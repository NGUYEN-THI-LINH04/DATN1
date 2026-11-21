
from pathlib import Path
import os
import json
import time
import re
import requests
from dotenv import load_dotenv

# ======================================
# 1. CAU HINH
# ======================================

ROOT = Path(r"D:\DATN1")
BASE = ROOT / "scripts" / "shadowing" / "hsk2"

RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

RAW.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT / ".env")

API_KEY = (
    os.getenv("SUPADATA_API_KEY")
    or os.getenv("SUPADATA_KEY")
    or os.getenv("SUPADATA_API_TOKEN")
)

VIDEO_ID = "uv8KNcXpels"
VIDEO_URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"

API_URL = "https://api.supadata.ai/v1/transcript"

RAW_FILE = RAW / "video3_supadata_zh.json"
PREVIEW_FILE = PROCESSED / "video3_zh_preview.json"


# ======================================
# 2. GOI SUPADATA
# ======================================

def get_json(url, params=None):
    response = requests.get(
        url,
        params=params,
        headers={"x-api-key": API_KEY},
        timeout=90
    )

    if not response.ok:
        raise RuntimeError(
            f"HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    return response.json()


def fetch_transcript():
    print("Dang lay phu de tieng Trung...")

    data = get_json(
        API_URL,
        params={
            "url": VIDEO_URL,
            "lang": "zh",
            "text": "false",
            "mode": "native"
        }
    )

    if "jobId" in data:
        job_id = data["jobId"]

        for i in range(60):
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
        else:
            raise TimeoutError(
                f"Job chua hoan tat: {job_id}"
            )

    return data


# ======================================
# 3. KIEM TRA VA CHUAN HOA
# ======================================

def normalize(data):
    content = data.get("content", [])

    if not isinstance(content, list):
        raise RuntimeError(
            "Khong co phu de kem timestamp."
        )

    sentences = []

    for item in content:
        hanzi = str(item.get("text", "")).strip()

        if not hanzi:
            continue

        start = round(
            float(item.get("offset", 0)) / 1000,
            3
        )

        duration = float(item.get("duration", 0))
        end = round(start + duration / 1000, 3)

        if end <= start:
            continue

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": "",
            "vi": ""
        })

    sentences.sort(
        key=lambda x: (x["start"], x["end"])
    )

    return sentences


def main():
    if not API_KEY:
        raise RuntimeError(
            "Khong tim thay API key trong .env"
        )

    data = fetch_transcript()

    print("Language:", data.get("lang"))
    print("Available:", data.get("availableLangs"))

    # Luu raw de su dung lai,
    # khong can goi Supadata them.
    RAW_FILE.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    sentences = normalize(data)

    if not sentences:
        raise RuntimeError(
            "Khong lay duoc phu de."
        )

    all_text = "".join(
        s["hanzi"] for s in sentences
    )

    chinese = len(
        re.findall(r"[\u3400-\u9fff]", all_text)
    )

    letters = len(
        re.findall(
            r"[A-Za-z\u3400-\u9fff]",
            all_text
        )
    )

    ratio = chinese / max(letters, 1)

    print(f"Ty le chu Han: {ratio:.1%}")

    # Khong tao preview neu API tra sai ngon ngu.
    if ratio < 0.5:
        raise RuntimeError(
            "Phu de khong phai chu yeu tieng Trung. "
            "Da luu raw, chua tao preview."
        )

    preview = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "title": "每日学习法 - Phuong phap hoc moi ngay",
        "status": "needs_review",
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

    overlaps = sum(
        sentences[i]["start"] < sentences[i-1]["end"]
        for i in range(1, len(sentences))
    )

    print("\n===== KET QUA =====")
    print("So doan phu de:", len(sentences))
    print("So cap thoi gian chong nhau:", overlaps)
    print("File:", PREVIEW_FILE)

    print("\n===== 15 DOAN DAU =====")

    for i, s in enumerate(sentences[:15], 1):
        print(
            f"{i:03d} "
            f"[{s['start']:.2f} - {s['end']:.2f}] "
            f"{s['hanzi']}"
        )

    print("\nCHUA CAP NHAT SQL SERVER.")


if __name__ == "__main__":
    main()
