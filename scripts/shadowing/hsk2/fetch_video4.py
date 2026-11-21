
from pathlib import Path
import os
import json
import time
import re
import requests

from dotenv import load_dotenv


# ==================================================
# 1. CAU HINH DU AN
# ==================================================

ROOT = Path(r"D:\DATN1")

BASE = (
    ROOT
    / "scripts"
    / "shadowing"
    / "hsk2"
)

RAW_DIR = BASE / "data" / "raw"
PROCESSED_DIR = BASE / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. DOC API KEY TU .ENV
# ==================================================

load_dotenv(ROOT / ".env")

API_KEY = (
    os.getenv("SUPADATA_API_KEY")
    or os.getenv("SUPADATA_KEY")
    or os.getenv("SUPADATA_API_TOKEN")
)


# ==================================================
# 3. THONG TIN VIDEO 4 - HSK2
# ==================================================

VIDEO_ID = "O_kkptuQPY8"

VIDEO_URL = (
    f"https://www.youtube.com/watch?v={VIDEO_ID}"
)

VIDEO_TITLE = (
    "中文口语练习 - "
    "Luyện nói về đồ ăn và cảm xúc"
)

API_URL = "https://api.supadata.ai/v1/transcript"


# ==================================================
# 4. FILE DAU RA - CHI DANH CHO VIDEO 4
# ==================================================

RAW_FILE = (
    RAW_DIR / "video4_supadata_zh.json"
)

PREVIEW_FILE = (
    PROCESSED_DIR / "video4_zh_preview.json"
)

TRANSCRIPT_FILE = (
    PROCESSED_DIR / "video4_transcript.txt"
)


# ==================================================
# 5. HAM GOI SUPADATA API
# ==================================================

def get_json(url, params=None):

    response = requests.get(
        url,
        params=params,
        headers={
            "x-api-key": API_KEY,
            "Accept": "application/json",
        },
        timeout=120,
    )

    if not response.ok:
        raise RuntimeError(
            f"Supadata HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    return response.json()


# ==================================================
# 6. LAY PHU DE TIENG TRUNG
# ==================================================

def fetch_transcript():

    print("===== SHADOWING HSK2 - VIDEO 4 =====")

    print("Video ID:", VIDEO_ID)
    print("YouTube:", VIDEO_URL)
    print("Tieu de:", VIDEO_TITLE)

    print("\nDang lay phu de tieng Trung...")

    data = get_json(
        API_URL,
        params={
            "url": VIDEO_URL,
            "lang": "zh",
            "text": "false",
            "mode": "native",
        },
    )

    # Truong hop Supadata tra ve jobId
    if "jobId" in data:

        job_id = data["jobId"]

        print("Supadata Job ID:", job_id)

        for attempt in range(90):

            time.sleep(5)

            result = get_json(
                f"{API_URL}/{job_id}"
            )

            status = result.get("status")

            if status == "completed":

                data = (
                    result.get("result")
                    or result
                )

                break

            if status == "failed":

                raise RuntimeError(
                    "Supadata xu ly that bai: "
                    + str(result)
                )

            print(
                f"Dang xu ly... {attempt + 1}/90"
            )

        else:
            raise TimeoutError(
                "Supadata chua hoan tat. "
                f"Job ID: {job_id}"
            )

    if not isinstance(data, dict):
        raise ValueError(
            "Supadata tra ve du lieu khong hop le."
        )

    return data


# ==================================================
# 7. CHUAN HOA TIMESTAMP VA CHU HAN
# ==================================================

def normalize_transcript(data):

    content = data.get("content", [])

    if not isinstance(content, list):
        raise ValueError(
            "Supadata khong tra ve phu de "
            "co timestamp."
        )

    sentences = []

    for item in content:

        if not isinstance(item, dict):
            continue

        hanzi = str(
            item.get("text", "")
        ).strip()

        if not hanzi:
            continue

        # Bo xuong dong va khoang trang thua
        hanzi = re.sub(
            r"\s+",
            " ",
            hanzi
        ).strip()

        offset = float(
            item.get("offset", 0)
        )

        duration = float(
            item.get("duration", 0)
        )

        # Supadata: mili giay -> giay
        start = round(
            offset / 1000,
            3
        )

        end = round(
            (offset + duration) / 1000,
            3
        )

        if start < 0 or end <= start:
            continue

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": "",
            "vi": "",
        })

    sentences.sort(
        key=lambda x: (
            x["start"],
            x["end"]
        )
    )

    return sentences


# ==================================================
# 8. KIEM TRA CHAT LUONG PHU DE
# ==================================================

def inspect_transcript(sentences, data):

    print("\n===== KIEM TRA PHU DE =====")

    print("Language:", data.get("lang"))

    print(
        "Available:",
        data.get("availableLangs")
    )

    print(
        "So doan phu de:",
        len(sentences)
    )

    full_text = "".join(
        s["hanzi"]
        for s in sentences
    )

    chinese_count = len(
        re.findall(
            r"[\u3400-\u9fff]",
            full_text
        )
    )

    letter_count = len(
        re.findall(
            r"[A-Za-z\u3400-\u9fff]",
            full_text
        )
    )

    chinese_ratio = (
        chinese_count / max(letter_count, 1)
    )

    print(
        f"Ty le chu Han: {chinese_ratio:.1%}"
    )

    overlaps = []

    duplicates = []

    seen = set()

    for i, sentence in enumerate(sentences):

        key = (
            sentence["start"],
            sentence["end"],
            sentence["hanzi"],
        )

        if key in seen:
            duplicates.append(i + 1)

        seen.add(key)

        if i > 0:

            previous = sentences[i - 1]

            if (
                sentence["start"]
                < previous["end"] - 0.001
            ):

                overlaps.append(i + 1)

    print(
        "So doan trung:",
        len(duplicates)
    )

    print(
        "So cap thoi gian chong nhau:",
        len(overlaps)
    )

    if sentences:

        print(
            "Thoi gian:",
            sentences[0]["start"],
            "->",
            sentences[-1]["end"],
            "giay"
        )

    if data.get("lang") != "zh":

        raise RuntimeError(
            "Supadata khong tra ve ngon ngu zh. "
            "Khong tao preview Shadowing."
        )

    if chinese_ratio < 0.5:

        raise RuntimeError(
            "Phu de khong phai chu yeu "
            "tieng Trung. Khong tao preview."
        )

    if not sentences:

        raise RuntimeError(
            "Khong co doan phu de hop le."
        )

    print("\n===== 15 DOAN DAU =====")

    for i, sentence in enumerate(
        sentences[:15],
        1
    ):

        print(
            f"{i:03d} "
            f"[{sentence['start']:.2f} - "
            f"{sentence['end']:.2f}] "
            f"{sentence['hanzi']}"
        )

    return {
        "chinese_ratio": round(
            chinese_ratio,
            4
        ),
        "duplicate_segments": duplicates,
        "overlap_segments": overlaps,
    }


# ==================================================
# 9. LUU FILE JSON VA TRANSCRIPT
# ==================================================

def save_results(data, sentences, report):

    preview = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "title": VIDEO_TITLE,
        "status": "needs_review",
        "sentences": sentences,
    }

    # Luu JSON cho video 4
    PREVIEW_FILE.write_text(
        json.dumps(
            preview,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # Luu transcript de xu ly pinyin,
    # dich tieng Viet o buoc tiep theo
    with TRANSCRIPT_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:

        for i, s in enumerate(sentences, 1):

            f.write(
                f"{i:03d} "
                f"[{s['start']:.2f}-{s['end']:.2f}] "
                f"{s['hanzi']}\n"
            )

    print("\n===== FILE DA LUU =====")

    print("Raw:", RAW_FILE)
    print("Preview:", PREVIEW_FILE)
    print("Transcript:", TRANSCRIPT_FILE)

    print("\nYouTube ID:", VIDEO_ID)
    print("So doan:", len(sentences))

    if report["overlap_segments"]:

        print(
            "CAN KIEM TRA CAC DOAN CHONG "
            "THOI GIAN TRUOC KHI XU LY TIEP."
        )

    print("\nCHUA CAP NHAT SQL SERVER.")


# ==================================================
# 10. CHUONG TRINH CHINH
# ==================================================

def main():

    if not API_KEY:

        raise RuntimeError(
            "Khong tim thay SUPADATA API key "
            r"trong D:\DATN1\.env"
        )

    # Kiem tra de tranh dung nham video 3
    if VIDEO_ID != "O_kkptuQPY8":

        raise RuntimeError(
            "Sai VIDEO_ID cua video 4!"
        )

    data = fetch_transcript()

    # Luu du lieu goc truoc khi xu ly
    RAW_FILE.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    sentences = normalize_transcript(data)

    report = inspect_transcript(
        sentences,
        data
    )

    save_results(
        data,
        sentences,
        report
    )


if __name__ == "__main__":
    main()
