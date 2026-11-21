
from pathlib import Path
import os
import json
import time
import requests
from dotenv import load_dotenv

# ==================================================
# 1. CAU HINH DUONG DAN
# ==================================================

ROOT = Path(r"D:\DATN1")

BASE_DIR = ROOT / "scripts" / "shadowing" / "hsk2"
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT / ".env")

API_KEY = (
    os.getenv("SUPADATA_API_KEY")
    or os.getenv("SUPADATA_KEY")
    or os.getenv("SUPADATA_API_TOKEN")
)

VIDEO_ID = "VkEYoXw7jD0"
VIDEO_URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"

API_URL = "https://api.supadata.ai/v1/transcript"

RAW_FILE = RAW_DIR / "video_chabuduo_supadata.json"
PREVIEW_FILE = PROCESSED_DIR / "video_chabuduo_preview.json"


# ==================================================
# 2. HAM GOI API
# ==================================================

def get_json(url, params=None):
    response = requests.get(
        url,
        params=params,
        headers={
            "x-api-key": API_KEY,
            "Accept": "application/json",
        },
        timeout=90,
    )

    if not response.ok:
        # Khong in API key ra man hinh.
        raise RuntimeError(
            f"Supadata HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    return response.json()


def fetch_transcript():
    print("Dang lay phu de tu Supadata...")
    print("Video:", VIDEO_ID)

    data = get_json(
        API_URL,
        params={
            "url": VIDEO_URL,
            "lang": "zh",
            "text": "false",
            "mode": "native",
        },
    )

    # Mot so video tra ve jobId thay vi phu de ngay.
    if "jobId" in data:
        job_id = data["jobId"]

        print("Supadata dang xu ly job:", job_id)

        for attempt in range(60):
            time.sleep(5)

            data = get_json(
                f"{API_URL}/{job_id}"
            )

            status = data.get("status")

            if status == "completed":
                break

            if status == "failed":
                raise RuntimeError(
                    "Supadata xu ly that bai: "
                    + str(data.get("message", data))
                )

            print(
                f"Dang cho ket qua... "
                f"{attempt + 1}/60"
            )
        else:
            raise TimeoutError(
                "Job chua hoan tat. "
                f"Job ID: {job_id}"
            )

    return data


# ==================================================
# 3. CHUAN HOA PHU DE
# ==================================================

def normalize_segments(data):
    content = data.get("content", [])

    if not isinstance(content, list):
        raise ValueError(
            "Supadata khong tra ve timestamped chunks. "
            "Khong the tao Shadowing tu plain text."
        )

    segments = []

    for item in content:
        text = str(item.get("text", "")).strip()

        if not text:
            continue

        # Supadata tra offset/duration bang mili giay.
        offset = float(item.get("offset", 0))
        duration = float(item.get("duration", 0))

        start = round(offset / 1000, 3)
        end = round((offset + duration) / 1000, 3)

        if end <= start:
            continue

        segments.append({
            "start": start,
            "end": end,
            "hanzi": text,
            "pinyin": "",
            "vi": "",
        })

    segments.sort(
        key=lambda x: (x["start"], x["end"])
    )

    return segments


# ==================================================
# 4. KIEM TRA DU LIEU
# ==================================================

def inspect_segments(segments):
    overlaps = []
    duplicates = []

    seen = set()

    for i, segment in enumerate(segments):
        key = (
            segment["start"],
            segment["end"],
            segment["hanzi"],
        )

        if key in seen:
            duplicates.append(i + 1)

        seen.add(key)

        if i > 0:
            previous = segments[i - 1]

            if segment["start"] < previous["end"]:
                overlaps.append({
                    "previous": i,
                    "current": i + 1,
                    "overlap_seconds": round(
                        previous["end"] - segment["start"],
                        3,
                    ),
                })

    print("\n===== KET QUA KIEM TRA =====")
    print("So doan phu de:", len(segments))
    print("So doan trung hoan toan:", len(duplicates))
    print("So cap moc thoi gian chong nhau:", len(overlaps))

    if segments:
        print(
            "Thoi gian:",
            segments[0]["start"],
            "->",
            segments[-1]["end"],
            "giay",
        )

    print("\n===== 10 DOAN DAU =====")

    for i, segment in enumerate(segments[:10], 1):
        print(
            f"{i:03d} "
            f"[{segment['start']:.2f} - "
            f"{segment['end']:.2f}] "
            f"{segment['hanzi']}"
        )

    return {
        "duplicates": duplicates,
        "overlaps": overlaps,
    }


# ==================================================
# 5. CHUONG TRINH CHINH
# ==================================================

def main():
    if not API_KEY:
        raise RuntimeError(
            "Khong tim thay SUPADATA_API_KEY trong "
            r"D:\DATN1\.env. "
            "Hay kiem tra ten bien API key dang dung."
        )

    data = fetch_transcript()

    # Luu nguyen ban de co the xu ly lai
    # ma khong can goi API lan nua.
    RAW_FILE.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nDa luu raw:", RAW_FILE)

    segments = normalize_segments(data)

    if not segments:
        raise RuntimeError(
            "Khong lay duoc doan phu de nao."
        )

    report = inspect_segments(segments)

    preview = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "title": "差不多 - Gần giống nhau",
        "source_language": data.get("lang"),
        "status": "needs_review",
        "sentences": segments,
        "validation": report,
    }

    PREVIEW_FILE.write_text(
        json.dumps(
            preview,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nDa luu preview:", PREVIEW_FILE)
    print("\nCHUA CAP NHAT SQL SERVER.")
    print(
        "Can chia lai cau, bo sung pinyin "
        "va ban dich truoc khi luu SQL."
    )


if __name__ == "__main__":
    main()
