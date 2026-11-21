
from pathlib import Path
import os
import json
import re
import time

import requests
from dotenv import load_dotenv


# ==========================================
# 1. CAU HINH THU MUC HSK3
# ==========================================

ROOT = Path(r"D:\DATN1")
BASE = ROOT / "scripts" / "shadowing" / "hsk3"

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


# ==========================================
# 2. VIDEO 1 - HSK3
# ==========================================

VIDEO_ID = "wZDej3Logc4"

VIDEO_URL = (
    f"https://www.youtube.com/watch?v={VIDEO_ID}"
)

VIDEO_TITLE = (
    "慢慢吃，对身体好！- Ăn chậm tốt cho sức khỏe"
)

API_URL = "https://api.supadata.ai/v1/transcript"


# ==========================================
# 3. FILE DAU RA RIENG CUA HSK3
# ==========================================

RAW_FILE = (
    RAW_DIR / "video1_supadata_zh.json"
)

PREVIEW_FILE = (
    PROCESSED_DIR / "video1_zh_preview.json"
)

TRANSCRIPT_FILE = (
    PROCESSED_DIR / "video1_transcript.txt"
)


# ==========================================
# 4. GOI API SUPADATA
# ==========================================

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


# ==========================================
# 5. LAY PHU DE TIENG TRUNG
# ==========================================

def fetch_transcript():

    print("===== SHADOWING HSK3 - VIDEO 1 =====")
    print("YouTube ID:", VIDEO_ID)
    print("Video:", VIDEO_URL)
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

    # Xu ly neu Supadata tra ve job ID
    if isinstance(data, dict) and data.get("jobId"):

        job_id = data["jobId"]

        print("Job ID:", job_id)

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
                    f"Supadata that bai: {result}"
                )

            print(
                f"Dang xu ly... {attempt + 1}/90"
            )

        else:
            raise TimeoutError(
                f"Job chua hoan tat: {job_id}"
            )

    if not isinstance(data, dict):
        raise ValueError(
            "Supadata tra ve du lieu khong hop le."
        )

    return data


# ==========================================
# 6. CHUAN HOA TIMESTAMP
# ==========================================

def normalize_transcript(data):

    content = data.get("content", [])

    if not isinstance(content, list):
        raise ValueError(
            "Khong co phu de kem timestamp."
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

        # Supadata dung mili giay
        offset = float(
            item.get("offset", 0)
        )

        duration = float(
            item.get("duration", 0)
        )

        start = round(
            offset / 1000, 3
        )

        end = round(
            (offset + duration) / 1000, 3
        )

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
        key=lambda s: (
            s["start"],
            s["end"]
        )
    )

    return sentences


# ==========================================
# 7. KIEM TRA CHAT LUONG PHU DE
# ==========================================

def inspect(data, sentences):

    print("\n===== KIEM TRA PHU DE =====")

    print(
        "Language:",
        data.get("lang")
    )

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

    hanzi_count = len(
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

    ratio = (
        hanzi_count / max(letter_count, 1)
    )

    print(
        f"Ty le chu Han: {ratio:.1%}"
    )

    duplicates = 0
    overlaps = 0
    long_segments = []
    short_segments = []

    seen = set()

    for index, s in enumerate(sentences):

        key = (
            s["start"],
            s["end"],
            s["hanzi"]
        )

        if key in seen:
            duplicates += 1

        seen.add(key)

        duration = s["end"] - s["start"]

        if duration > 10:
            long_segments.append(index + 1)

        if duration < 0.8:
            short_segments.append(index + 1)

        if index > 0:

            previous = sentences[index - 1]

            if (
                s["start"]
                < previous["end"] - 0.001
            ):
                overlaps += 1

    print("So doan trung:", duplicates)
    print("Timestamp chong nhau:", overlaps)

    print(
        "So doan > 10 giay:",
        len(long_segments)
    )

    print(
        "So doan < 0.8 giay:",
        len(short_segments)
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
            "Supadata khong tra ve ngon ngu zh."
        )

    if ratio < 0.5:
        raise RuntimeError(
            "Phu de khong phai chu yeu tieng Trung."
        )

    if not sentences:
        raise RuntimeError(
            "Khong tim thay phu de hop le."
        )

    print("\n===== 15 DOAN DAU =====")

    for i, s in enumerate(
        sentences[:15], 1
    ):

        print(
            f"{i:03d} "
            f"[{s['start']:.2f} - "
            f"{s['end']:.2f}] "
            f"{s['hanzi']}"
        )

    print("\nCAN KIEM TRA NOI DUNG VOI VIDEO GOC.")


# ==========================================
# 8. LUU KET QUA
# ==========================================

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
    ) as f:

        for i, s in enumerate(
            sentences, 1
        ):

            f.write(
                f"{i:03d} "
                f"[{s['start']:.2f}-"
                f"{s['end']:.2f}] "
                f"{s['hanzi']}\n"
            )

    print("\n===== FILE DA LUU =====")

    print("Raw:", RAW_FILE)
    print("Preview:", PREVIEW_FILE)
    print("Transcript:", TRANSCRIPT_FILE)

    print("\nCHUA CAP NHAT LOI THOAI VAO SQL SERVER.")


# ==========================================
# 9. MAIN
# ==========================================

def main():

    if not API_KEY:
        raise RuntimeError(
            "Khong tim thay Supadata API key "
            "trong D:\\DATN1\\.env"
        )

    if VIDEO_ID != "wZDej3Logc4":
        raise RuntimeError(
            "Sai YouTube ID cua video HSK3!"
        )

    data = fetch_transcript()

    # Luu phan hoi Supadata truoc,
    # ke ca khi phu de chua dat yeu cau.
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
