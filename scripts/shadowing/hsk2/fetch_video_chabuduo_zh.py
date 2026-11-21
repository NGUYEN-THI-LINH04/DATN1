
from pathlib import Path
import os
import json
import time
import re
import requests
from dotenv import load_dotenv

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

VIDEO_ID = "VkEYoXw7jD0"
VIDEO_URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"

API_URL = "https://api.supadata.ai/v1/transcript"

RAW_FILE = RAW_DIR / "video_chabuduo_zh_generated.json"
PREVIEW_FILE = (
    PROCESSED_DIR / "video_chabuduo_zh_preview.json"
)


def request_json(url, params=None):
    response = requests.get(
        url,
        params=params,
        headers={"x-api-key": API_KEY},
        timeout=120
    )

    if not response.ok:
        raise RuntimeError(
            f"HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    return response.json()


def fetch_chinese_transcript():
    print("Dang nhan dang loi noi tieng Trung...")

    data = request_json(
        API_URL,
        params={
            "url": VIDEO_URL,
            "lang": "zh",
            "text": "false",
            "mode": "generate"
        }
    )

    if "jobId" in data:
        job_id = data["jobId"]
        print("Job ID:", job_id)

        for i in range(90):
            time.sleep(5)

            result = request_json(
                f"{API_URL}/{job_id}"
            )

            status = result.get("status")

            if status == "completed":
                data = result.get("result") or result
                break

            if status == "failed":
                raise RuntimeError(
                    "Supadata that bai: "
                    + str(result.get("error", result))
                )

            print(f"Dang xu ly... {i + 1}/90")
        else:
            raise TimeoutError(
                f"Het thoi gian cho. Job ID: {job_id}"
            )

    return data


def normalize(data):
    content = data.get("content", [])

    if not isinstance(content, list):
        raise RuntimeError(
            "API khong tra ve phu de co timestamp."
        )

    result = []

    for chunk in content:
        hanzi = str(chunk.get("text", "")).strip()

        if not hanzi:
            continue

        offset = float(chunk.get("offset", 0))
        duration = float(chunk.get("duration", 0))

        start = round(offset / 1000, 3)
        end = round((offset + duration) / 1000, 3)

        if end <= start:
            continue

        result.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": "",
            "vi": ""
        })

    result.sort(key=lambda s: s["start"])
    return result


def check_chinese(segments):
    full_text = "".join(
        s["hanzi"] for s in segments
    )

    chinese_chars = len(re.findall(
        r"[\u3400-\u9fff]",
        full_text
    ))

    letters = len(re.findall(
        r"[A-Za-z\u3400-\u9fff]",
        full_text
    ))

    ratio = chinese_chars / max(letters, 1)

    print(f"Ty le chu Han: {ratio:.1%}")

    if ratio < 0.5:
        raise RuntimeError(
            "Ket qua van khong phai chu yeu tieng Trung. "
            "Chua tao file preview."
        )


def main():
    if not API_KEY:
        raise RuntimeError(
            "Khong tim thay Supadata API key trong .env"
        )

    data = fetch_chinese_transcript()

    print("Ngon ngu API:", data.get("lang"))
    print("Available:", data.get("availableLangs"))

    # Luu ket qua tho, khong ghi de file cu.
    RAW_FILE.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    segments = normalize(data)

    if not segments:
        raise RuntimeError(
            "Khong co doan phu de nao."
        )

    check_chinese(segments)

    # Chua phai du lieu hoan chinh.
    # Can ra soat, chia cau va bo sung pinyin/vi.
    preview = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "title": "差不多 - Gần giống nhau",
        "status": "needs_review",
        "sentences": segments
    }

    PREVIEW_FILE.write_text(
        json.dumps(
            preview,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\n===== KET QUA =====")
    print("So doan:", len(segments))
    print("File JSON:", PREVIEW_FILE)

    print("\n===== 15 DOAN DAU =====")

    for i, s in enumerate(segments[:15], 1):
        print(
            f"{i:03d} "
            f"[{s['start']:.2f} - {s['end']:.2f}] "
            f"{s['hanzi']}"
        )

    print("\nCHUA CAP NHAT SQL SERVER.")


if __name__ == "__main__":
    main()
