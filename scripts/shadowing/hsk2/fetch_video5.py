
from pathlib import Path
import os
import json
import re
import time
import requests

from dotenv import load_dotenv


# ==================================================
# 1. CAU HINH DU AN
# ==================================================

ROOT = Path(r"D:\DATN1")
BASE = ROOT / "scripts" / "shadowing" / "hsk2"

RAW_DIR = BASE / "data" / "raw"
PROCESSED_DIR = BASE / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT / ".env")

API_KEY = (
    os.getenv("SUPADATA_API_KEY")
    or os.getenv("SUPADATA_KEY")
    or os.getenv("SUPADATA_API_TOKEN")
)


# ==================================================
# 2. THONG TIN VIDEO 5
# ==================================================

VIDEO_ID = "MYQrQvbR8Vk"
VIDEO_URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"

VIDEO_TITLE = (
    "我的一天 - Sinh hoạt hằng ngày của tôi"
)

API_URL = "https://api.supadata.ai/v1/transcript"


# ==================================================
# 3. FILE DAU RA RIENG CHO VIDEO 5
# ==================================================

RAW_FILE = RAW_DIR / "video5_supadata_zh.json"

PREVIEW_FILE = (
    PROCESSED_DIR / "video5_zh_preview.json"
)

TRANSCRIPT_FILE = (
    PROCESSED_DIR / "video5_transcript.txt"
)


# ==================================================
# 4. GOI API SUPADATA
# ==================================================

def get_json(url, params=None):

    response = requests.get(
        url,
        params=params,
        headers={
            "x-api-key": API_KEY,
            "Accept": "application/json"
        },
        timeout=120
    )

    if not response.ok:
        raise RuntimeError(
            f"Supadata HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    return response.json()


# ==================================================
# 5. LAY PHU DE TIENG TRUNG
# ==================================================

def fetch_transcript():

    print("===== SHADOWING HSK2 - VIDEO 5 =====")
    print("YouTube ID:", VIDEO_ID)
    print("Link:", VIDEO_URL)
    print("Tieu de:", VIDEO_TITLE)
    print("\nDang lay phu de tieng Trung...")

    data = get_json(
        API_URL,
        params={
            "url": VIDEO_URL,
            "lang": "zh",
            "text": "false",
            "mode": "native"
        }
    )

    # Mot so video duoc Supadata xu ly bat dong bo.
    if isinstance(data, dict) and "jobId" in data:

        job_id = data["jobId"]
        print("Job ID:", job_id)

        for attempt in range(90):

            time.sleep(5)

            result = get_json(
                f"{API_URL}/{job_id}"
            )

            status = result.get("status")

            if status == "completed":
                data = result.get("result") or result
                break

            if status == "failed":
                raise RuntimeError(
                    f"Supadata that bai: {result}"
                )

            print(
                f"Dang xu ly: {attempt + 1}/90"
            )

        else:
            raise TimeoutError(
                "Supadata chua xu ly xong. "
                f"Job ID: {job_id}"
            )

    if not isinstance(data, dict):
        raise ValueError(
            "Du lieu Supadata khong hop le."
        )

    return data


# ==================================================
# 6. CHUAN HOA PHU DE
# ==================================================

def normalize_transcript(data):

    content = data.get("content", [])

    if not isinstance(content, list):
        raise ValueError(
            "Khong co danh sach phu de "
            "kem timestamp."
        )

    sentences = []

    for item in content:

        if not isinstance(item, dict):
            continue

        hanzi = re.sub(
            r"\s+",
            " ",
            str(item.get("text", ""))
        ).strip()

        if not hanzi:
            continue

        # Supadata tra timestamp bang mili giay.
        offset = float(item.get("offset", 0))
        duration = float(item.get("duration", 0))

        start = round(offset / 1000, 3)
        end = round((offset + duration) / 1000, 3)

        if start < 0 or end <= start:
            continue

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": "",
            "vi": ""
        })

    sentences.sort(
        key=lambda s: (s["start"], s["end"])
    )

    return sentences


# ==================================================
# 7. KIEM TRA CHAT LUONG
# ==================================================

def inspect(data, sentences):

    print("\n===== KIEM TRA PHU DE =====")

    language = data.get("lang")
    available = data.get("availableLangs", [])

    print("Language:", language)
    print("Available:", available)
    print("So doan phu de:", len(sentences))

    full_text = "".join(
        s["hanzi"] for s in sentences
    )

    hanzi_count = len(
        re.findall(r"[\u3400-\u9fff]", full_text)
    )

    letter_count = len(
        re.findall(
            r"[A-Za-z\u3400-\u9fff]",
            full_text
        )
    )

    ratio = hanzi_count / max(letter_count, 1)

    print(f"Ty le chu Han: {ratio:.1%}")

    duplicates = 0
    overlaps = 0
    long_segments = 0

    seen = set()

    for index, sentence in enumerate(sentences):

        key = (
            sentence["start"],
            sentence["end"],
            sentence["hanzi"]
        )

        if key in seen:
            duplicates += 1

        seen.add(key)

        if sentence["end"] - sentence["start"] > 10:
            long_segments += 1

        if index > 0:

            previous = sentences[index - 1]

            if sentence["start"] < previous["end"] - 0.001:
                overlaps += 1

    print("So doan trung:", duplicates)
    print("So cap timestamp chong:", overlaps)
    print("So doan > 10 giay:", long_segments)

    if sentences:
        print(
            "Thoi gian:",
            sentences[0]["start"],
            "->",
            sentences[-1]["end"],
            "giay"
        )

    # Khong chap nhan phu de tieng Anh
    # hoac phu de khong co timestamp.
    if language != "zh":
        raise RuntimeError(
            "Supadata khong tra ve ngon ngu zh."
        )

    if not sentences:
        raise RuntimeError(
            "Khong lay duoc phu de co timestamp."
        )

    if ratio < 0.5:
        raise RuntimeError(
            "Phu de khong phai chu yeu tieng Trung."
        )

    print("\n===== 15 DOAN DAU =====")

    for i, item in enumerate(sentences[:15], 1):

        print(
            f"{i:03d} "
            f"[{item['start']:.2f} - "
            f"{item['end']:.2f}] "
            f"{item['hanzi']}"
        )

    print("\n===== KET LUAN =====")
    print("Da lay duoc phu de tieng Trung.")
    print("Can ra soat noi dung voi video goc.")


# ==================================================
# 8. LUU DU LIEU VIDEO 5
# ==================================================

def save_files(data, sentences):

    preview = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "title": VIDEO_TITLE,
        "sentences": sentences
    }

    PREVIEW_FILE.write_text(
        json.dumps(
            preview,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    with TRANSCRIPT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        for i, item in enumerate(sentences, 1):

            file.write(
                f"{i:03d} "
                f"[{item['start']:.2f}-"
                f"{item['end']:.2f}] "
                f"{item['hanzi']}\n"
            )

    print("\n===== FILE DA LUU =====")
    print("Raw:", RAW_FILE)
    print("Preview:", PREVIEW_FILE)
    print("Transcript:", TRANSCRIPT_FILE)

    print("\nCHUA CAP NHAT LOI THOAI VAO SQL.")


# ==================================================
# 9. CHUONG TRINH CHINH
# ==================================================

def main():

    if not API_KEY:
        raise RuntimeError(
            "Khong tim thay Supadata API key "
            "trong file .env"
        )

    if VIDEO_ID != "MYQrQvbR8Vk":
        raise RuntimeError("Sai video 5!")

    data = fetch_transcript()

    # Luu du lieu API vao file rieng,
    # khong anh huong video 1, 2, 3, 4.
    RAW_FILE.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    sentences = normalize_transcript(data)

    inspect(data, sentences)

    save_files(data, sentences)


if __name__ == "__main__":
    main()
