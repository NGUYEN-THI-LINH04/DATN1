
import os
import re
import json
import time
import math
from pathlib import Path

import requests
from dotenv import load_dotenv


# ==================================================
# 1. CAU HINH DU AN
# ==================================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "shadowing" / "hsk4"

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
# 2. THONG TIN VIDEO HSK4 SO 3
# ==================================================

VIDEO_ID = "KIMnS86vgPE"

VIDEO_URL = (
    f"https://www.youtube.com/watch?v={VIDEO_ID}"
)

VIDEO_TITLE = (
    "为什么你用的吸引力法则总失效？ - "
    "Tại sao luật hấp dẫn bạn áp dụng "
    "luôn không hiệu quả?"
)

MA_BAI_HOC = 2057

API_URL = "https://api.supadata.ai/v1/transcript"


# ==================================================
# 3. DUONG DAN FILE VIDEO 3
# ==================================================

RAW_FILE = (
    RAW_DIR / "video3_supadata_zh.json"
)

PREVIEW_FILE = (
    PROCESSED_DIR / "video3_zh_preview.json"
)

TRANSCRIPT_FILE = (
    PROCESSED_DIR / "video3_transcript.txt"
)

REPORT_FILE = (
    PROCESSED_DIR / "video3_fetch_report.txt"
)


# ==================================================
# 4. GOI API SUPADATA
# ==================================================

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


# ==================================================
# 5. LAY PHU DE TIENG TRUNG
# ==================================================

def fetch_transcript():

    print(
        "===== SHADOWING HSK4 - VIDEO 3 ====="
    )

    print("YouTube ID:", VIDEO_ID)
    print("Video:", VIDEO_URL)
    print("MaBaiHoc:", MA_BAI_HOC)
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

    # Supadata co the tra ve jobId
    # neu du lieu dang duoc xu ly.

    if isinstance(data, dict) and data.get("jobId"):

        job_id = data["jobId"]

        print("Supadata Job ID:", job_id)

        for attempt in range(90):

            time.sleep(5)

            result = api_get(
                f"{API_URL}/{job_id}"
            )

            status = str(
                result.get("status", "")
            ).lower()

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
                f"Dang xu ly: {attempt + 1}/90"
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
# 6. CHUAN HOA PHU DE VA TIMESTAMP
# ==================================================

def normalize_transcript(data):

    content = data.get("content", [])

    if not isinstance(content, list):

        raise ValueError(
            "Khong tim thay danh sach phu de "
            "kem timestamp."
        )

    sentences = []

    for index, item in enumerate(content, 1):

        if not isinstance(item, dict):
            continue

        hanzi = re.sub(
            r"\s+",
            " ",
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
                f"Timestamp khong hop le "
                f"o doan {index}"
            )

        # Supadata tra ve mili giay.
        start = round(
            offset / 1000,
            3
        )

        end = round(
            (offset + duration) / 1000,
            3
        )

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
        key=lambda s: (
            s["start"],
            s["end"]
        )
    )

    return sentences


# ==================================================
# 7. KIEM TRA CHAT LUONG PHU DE
# ==================================================

def inspect_transcript(data, sentences):

    language = data.get("lang")
    available = data.get("availableLangs", [])

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

    duplicates = []
    overlaps = []
    short_segments = []
    long_segments = []

    seen = set()

    for i, sentence in enumerate(
        sentences, 1
    ):

        start = sentence["start"]
        end = sentence["end"]

        duration = round(
            end - start,
            3
        )

        key = (
            start,
            end,
            sentence["hanzi"]
        )

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

    print(
        "So doan trung:",
        len(duplicates)
    )

    print(
        "Timestamp chong nhau:",
        len(overlaps)
    )

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

    # Bat buoc phai la tieng Trung.
    if language != "zh":

        raise RuntimeError(
            "Supadata khong tra ve phu de zh. "
            f"Ngon ngu thuc te: {language}"
        )

    if not sentences:

        raise RuntimeError(
            "Video khong co phu de tieng Trung "
            "kem timestamp."
        )

    if ratio < 0.5:

        raise RuntimeError(
            "Phu de khong chu yeu la chu Han."
        )

    print("\n===== 15 DOAN DAU =====")

    for i, sentence in enumerate(
        sentences[:15], 1
    ):

        print(
            f"{i:03d} "
            f"[{sentence['start']:.2f} - "
            f"{sentence['end']:.2f}] "
            f"{sentence['hanzi']}"
        )

    print("\n===== DANH GIA =====")

    if duplicates or overlaps:

        print(
            "CAN KIEM TRA: Co doan trung "
            "hoac timestamp chong nhau."
        )

    else:

        print(
            "Timestamp va doan trung: OK"
        )

    print(
        "Can doi chieu noi dung phu de "
        "voi am thanh video goc."
    )

    return {
        "ratio": ratio,
        "duplicates": duplicates,
        "overlaps": overlaps,
        "short_segments": short_segments,
        "long_segments": long_segments
    }


# ==================================================
# 8. LUU JSON, TRANSCRIPT VA BAO CAO
# ==================================================

def save_files(sentences, report):

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

    # Transcript dung de dich tieng Viet.
    with TRANSCRIPT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        for i, sentence in enumerate(
            sentences, 1
        ):

            file.write(
                f"{i:03d} "
                f"[{sentence['start']:.2f}-"
                f"{sentence['end']:.2f}] "
                f"{sentence['hanzi']}\n"
            )

    # Tao bao cao kiem tra.
    lines = [
        "SHADOWING HSK4 - VIDEO 3",
        f"YouTube ID: {VIDEO_ID}",
        f"MaBaiHoc: {MA_BAI_HOC}",
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


# ==================================================
# 9. CHUONG TRINH CHINH
# ==================================================

def main():

    if not API_KEY:

        raise RuntimeError(
            "Khong tim thay SUPADATA_API_KEY "
            "trong D:\\DATN1\\.env"
        )

    data = fetch_transcript()

    # Luu phan hoi goc cua Supadata.
    # Khong ghi vao SQL Server.
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
        data,
        sentences
    )

    save_files(
        sentences,
        report
    )


if __name__ == "__main__":
    main()
