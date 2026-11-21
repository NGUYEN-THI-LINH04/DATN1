
import os
import re
import json
import time
import math
from pathlib import Path

import requests
from dotenv import load_dotenv


# ==========================================
# 1. CAU HINH
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

VIDEO_ID = "yaeECV1JRjM"
VIDEO_URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"
VIDEO_TITLE = "周末野餐对话 - Hội thoại về buổi dã ngoại cuối tuần"

API_URL = "https://api.supadata.ai/v1/transcript"

RAW_FILE = RAW_DIR / "video4_supadata_zh.json"
PREVIEW_FILE = PROCESSED_DIR / "video4_zh_preview.json"
TRANSCRIPT_FILE = PROCESSED_DIR / "video4_transcript.txt"
REPORT_FILE = PROCESSED_DIR / "video4_fetch_report.txt"


# ==========================================
# 2. GOI SUPADATA
# ==========================================

def api_get(url, params=None):
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


def fetch_transcript():
    print("===== SHADOWING HSK3 - VIDEO 4 =====")
    print("YouTube ID:", VIDEO_ID)
    print("Video:", VIDEO_URL)
    print("Tieu de:", VIDEO_TITLE)
    print("\nDang lay phu de tieng Trung...")

    data = api_get(
        API_URL,
        params={
            "url": VIDEO_URL,
            "lang": "zh",
            "text": "false",
            "mode": "native"
        }
    )

    if isinstance(data, dict) and data.get("jobId"):
        job_id = data["jobId"]
        print("Supadata Job ID:", job_id)

        for attempt in range(90):
            time.sleep(5)

            result = api_get(f"{API_URL}/{job_id}")
            status = result.get("status")

            if status == "completed":
                data = result.get("result") or result
                break

            if status == "failed":
                raise RuntimeError(
                    "Supadata xu ly that bai: "
                    + str(result)
                )

            print(f"Dang xu ly: {attempt + 1}/90")
        else:
            raise TimeoutError(
                f"Supadata chua hoan tat: {job_id}"
            )

    if not isinstance(data, dict):
        raise ValueError("Du lieu Supadata khong hop le.")

    return data


# ==========================================
# 3. CHUAN HOA PHU DE
# ==========================================

def normalize(data):
    content = data.get("content", [])

    if not isinstance(content, list):
        raise ValueError(
            "Khong co phu de kem timestamp."
        )

    sentences = []

    for index, item in enumerate(content, 1):
        if not isinstance(item, dict):
            continue

        hanzi = re.sub(
            r"\s+", " ",
            str(item.get("text", ""))
        ).strip()

        if not hanzi:
            continue

        try:
            offset = float(item["offset"])
            duration = float(item["duration"])
        except (KeyError, TypeError, ValueError):
            raise ValueError(
                f"Timestamp sai o doan {index}"
            )

        if not (
            math.isfinite(offset)
            and math.isfinite(duration)
        ):
            raise ValueError(
                f"Timestamp khong hop le o doan {index}"
            )

        start = round(offset / 1000, 3)
        end = round((offset + duration) / 1000, 3)

        if start < 0 or end <= start:
            raise ValueError(
                f"Thoi gian sai o doan {index}"
            )

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


# ==========================================
# 4. KIEM TRA CHAT LUONG
# ==========================================

def inspect(data, sentences):
    language = data.get("lang")
    available = data.get("availableLangs", [])

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

    duplicates = []
    overlaps = []
    short_segments = []
    long_segments = []

    seen = set()

    for i, sentence in enumerate(sentences, 1):
        start = sentence["start"]
        end = sentence["end"]
        duration = round(end - start, 3)

        key = (start, end, sentence["hanzi"])

        if key in seen:
            duplicates.append(i)

        seen.add(key)

        if i > 1:
            previous = sentences[i - 2]
            if start < previous["end"] - 0.001:
                overlaps.append(i)

        if duration < 0.8:
            short_segments.append({
                "number": i,
                "duration": duration,
                "hanzi": sentence["hanzi"]
            })

        if duration > 10:
            long_segments.append({
                "number": i,
                "duration": duration,
                "hanzi": sentence["hanzi"]
            })

    print("\n===== KIEM TRA PHU DE =====")
    print("Language:", language)
    print("Available:", available)
    print("So doan phu de:", len(sentences))
    print(f"Ty le chu Han: {ratio:.1%}")
    print("So doan trung:", len(duplicates))
    print("Timestamp chong nhau:", len(overlaps))
    print("So doan > 10 giay:", len(long_segments))
    print("So doan < 0.8 giay:", len(short_segments))

    if sentences:
        print(
            "Thoi gian:",
            sentences[0]["start"],
            "->",
            sentences[-1]["end"],
            "giay"
        )

    if language != "zh":
        raise RuntimeError(
            "Supadata khong tra phu de zh."
        )

    if not sentences:
        raise RuntimeError(
            "Khong lay duoc phu de."
        )

    if ratio < 0.5:
        raise RuntimeError(
            "Phu de khong chu yeu la chu Han."
        )

    print("\n===== 15 DOAN DAU =====")

    for i, sentence in enumerate(sentences[:15], 1):
        print(
            f"{i:03d} "
            f"[{sentence['start']:.2f} - "
            f"{sentence['end']:.2f}] "
            f"{sentence['hanzi']}"
        )

    print("\n===== DANH GIA =====")
    if duplicates or overlaps:
        print(
            "CAN KIEM TRA DOAN TRUNG "
            "HOAC TIMESTAMP CHONG NHAU."
        )
    else:
        print("Timestamp va doan trung: OK")

    print("Can doi chieu noi dung voi video goc.")

    return {
        "ratio": ratio,
        "duplicates": duplicates,
        "overlaps": overlaps,
        "short_segments": short_segments,
        "long_segments": long_segments
    }


# ==========================================
# 5. LUU FILE
# ==========================================

def save_files(data, sentences, report):
    RAW_FILE.write_text(
        json.dumps(
            data, ensure_ascii=False, indent=2
        ),
        encoding="utf-8"
    )

    preview = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "title": VIDEO_TITLE,
        "sentences": sentences
    }

    PREVIEW_FILE.write_text(
        json.dumps(
            preview, ensure_ascii=False, indent=2
        ),
        encoding="utf-8"
    )

    with TRANSCRIPT_FILE.open(
        "w", encoding="utf-8"
    ) as file:
        for i, s in enumerate(sentences, 1):
            file.write(
                f"{i:03d} "
                f"[{s['start']:.2f}-{s['end']:.2f}] "
                f"{s['hanzi']}\n"
            )

    lines = [
        "SHADOWING HSK3 - VIDEO 4",
        f"YouTube ID: {VIDEO_ID}",
        f"Tieu de: {VIDEO_TITLE}",
        f"So doan: {len(sentences)}",
        f"Ty le chu Han: {report['ratio']:.1%}",
        f"Doan trung: {len(report['duplicates'])}",
        f"Timestamp chong: {len(report['overlaps'])}",
        f"Doan < 0.8s: {len(report['short_segments'])}",
        f"Doan > 10s: {len(report['long_segments'])}",
        "",
        "===== DOAN QUA NGAN ====="
    ]

    for item in report["short_segments"]:
        lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    lines.extend([
        "",
        "===== DOAN QUA DAI ====="
    ])

    for item in report["long_segments"]:
        lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    lines.extend([
        "",
        "CHUA TAO PINYIN.",
        "CHUA DICH TIENG VIET.",
        "CHUA CAP NHAT SQL SERVER."
    ])

    REPORT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print("\n===== FILE DA LUU =====")
    print("Raw:", RAW_FILE)
    print("Preview:", PREVIEW_FILE)
    print("Transcript:", TRANSCRIPT_FILE)
    print("Bao cao:", REPORT_FILE)
    print("\nCHUA CAP NHAT SQL SERVER.")


# ==========================================
# 6. MAIN
# ==========================================

def main():
    if not API_KEY:
        raise RuntimeError(
            "Thieu SUPADATA_API_KEY trong .env"
        )

    data = fetch_transcript()
    sentences = normalize(data)
    report = inspect(data, sentences)
    save_files(data, sentences, report)


if __name__ == "__main__":
    main()
