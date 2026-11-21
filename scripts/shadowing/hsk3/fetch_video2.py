
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

BASE = (
    ROOT
    / "scripts"
    / "shadowing"
    / "hsk3"
)

RAW_DIR = BASE / "data" / "raw"
PROCESSED_DIR = BASE / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. DOC SUPADATA API KEY TU .ENV
# ==================================================

load_dotenv(ROOT / ".env")

API_KEY = (
    os.getenv("SUPADATA_API_KEY")
    or os.getenv("SUPADATA_KEY")
    or os.getenv("SUPADATA_API_TOKEN")
)


# ==================================================
# 3. THONG TIN VIDEO HSK3 SO 2
# ==================================================

VIDEO_ID = "tQKsIFE-Y0g"

VIDEO_URL = (
    f"https://www.youtube.com/watch?v={VIDEO_ID}"
)

VIDEO_TITLE = (
    "中国餐桌礼仪 - "
    "Phép lịch sự trên bàn ăn Trung Quốc"
)

API_URL = "https://api.supadata.ai/v1/transcript"


# ==================================================
# 4. FILE DAU RA - CHI DANH CHO VIDEO 2
# ==================================================

RAW_FILE = (
    RAW_DIR / "video2_supadata_zh.json"
)

PREVIEW_FILE = (
    PROCESSED_DIR / "video2_zh_preview.json"
)

TRANSCRIPT_FILE = (
    PROCESSED_DIR / "video2_transcript.txt"
)

REPORT_FILE = (
    PROCESSED_DIR / "video2_fetch_report.txt"
)


# ==================================================
# 5. GOI SUPADATA API
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

    print("===== SHADOWING HSK3 - VIDEO 2 =====")

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
            "mode": "native",
        },
    )

    # Supadata co the xu ly bat dong bo
    # va tra ve jobId.
    if isinstance(data, dict) and data.get("jobId"):

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
# 7. CHUAN HOA PHU DE VA TIMESTAMP
# ==================================================

def normalize_transcript(data):

    content = data.get("content", [])

    if not isinstance(content, list):

        raise ValueError(
            "Khong tim thay danh sach phu de "
            "kem timestamp."
        )

    sentences = []

    for item in content:

        if not isinstance(item, dict):
            continue

        hanzi = str(
            item.get("text", "")
        ).strip()

        # Xoa xuong dong va khoang trang thua,
        # khong thay doi noi dung chu Han.
        hanzi = re.sub(
            r"\s+",
            " ",
            hanzi
        ).strip()

        if not hanzi:
            continue

        # Supadata tra ve mili giay.
        offset = float(
            item.get("offset", 0)
        )

        duration = float(
            item.get("duration", 0)
        )

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
        key=lambda s: (
            s["start"],
            s["end"]
        )
    )

    return sentences


# ==================================================
# 8. KIEM TRA CHAT LUONG PHU DE
# ==================================================

def inspect_transcript(data, sentences):

    print("\n===== KIEM TRA PHU DE =====")

    language = data.get("lang")
    available = data.get("availableLangs", [])

    print("Language:", language)
    print("Available:", available)

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

    chinese_ratio = (
        hanzi_count / max(letter_count, 1)
    )

    print(
        f"Ty le chu Han: {chinese_ratio:.1%}"
    )

    duplicates = []
    overlaps = []
    long_segments = []
    short_segments = []

    seen = set()

    for i, sentence in enumerate(sentences):

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
            duplicates.append(i + 1)

        seen.add(key)

        if duration > 10:

            long_segments.append({
                "number": i + 1,
                "duration": duration,
                "hanzi": sentence["hanzi"],
            })

        if duration < 0.8:

            short_segments.append({
                "number": i + 1,
                "duration": duration,
                "hanzi": sentence["hanzi"],
            })

        if i > 0:

            previous = sentences[i - 1]

            if start < previous["end"] - 0.001:
                overlaps.append(i + 1)

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

    # Kiem tra ngon ngu truoc khi tao preview.
    if language != "zh":

        raise RuntimeError(
            "Supadata khong tra ve ngon ngu zh."
        )

    if not sentences:

        raise RuntimeError(
            "Video khong co phu de hop le "
            "kem timestamp."
        )

    if chinese_ratio < 0.5:

        raise RuntimeError(
            "Phu de khong phai chu yeu "
            "tieng Trung."
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

    print("\n===== DANH GIA =====")

    if overlaps:

        print(
            "CAN KIEM TRA: Timestamp bi chong."
        )

    if duplicates:

        print(
            "CAN KIEM TRA: Co doan phu de trung."
        )

    if not overlaps and not duplicates:

        print(
            "Timestamp va doan trung: OK"
        )

    print(
        "Can doi chieu noi dung voi video goc."
    )

    return {
        "chinese_ratio": chinese_ratio,
        "duplicates": duplicates,
        "overlaps": overlaps,
        "long_segments": long_segments,
        "short_segments": short_segments,
    }


# ==================================================
# 9. LUU FILE JSON VA TRANSCRIPT
# ==================================================

def save_files(sentences, report):

    preview = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "title": VIDEO_TITLE,
        "sentences": sentences,
    }

    # File phu de de tao pinyin va ban dich.
    PREVIEW_FILE.write_text(
        json.dumps(
            preview,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # File text de doc va dich loi thoai.
    with TRANSCRIPT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        for i, sentence in enumerate(
            sentences,
            1
        ):

            file.write(
                f"{i:03d} "
                f"[{sentence['start']:.2f}-"
                f"{sentence['end']:.2f}] "
                f"{sentence['hanzi']}\n"
            )

    # Bao cao phuc vu kiem tra.
    lines = [
        "SHADOWING HSK3 - VIDEO 2",
        f"YouTube ID: {VIDEO_ID}",
        f"Tieu de: {VIDEO_TITLE}",
        f"So doan: {len(sentences)}",
        f"Ty le chu Han: {report['chinese_ratio']:.1%}",
        f"Doan trung: {len(report['duplicates'])}",
        f"Timestamp chong: {len(report['overlaps'])}",
        f"Doan > 10s: {len(report['long_segments'])}",
        f"Doan < 0.8s: {len(report['short_segments'])}",
        "",
        "===== DOAN QUA NGAN =====",
    ]

    for item in report["short_segments"]:

        lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    lines.extend([
        "",
        "===== DOAN QUA DAI =====",
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
        "CHUA CAP NHAT SQL SERVER.",
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
# 10. CHUONG TRINH CHINH
# ==================================================

def main():

    if not API_KEY:

        raise RuntimeError(
            "Khong tim thay SUPADATA_API_KEY "
            r"trong D:\DATN1\.env"
        )

    # Chan truong hop copy nham video khac.
    if VIDEO_ID != "tQKsIFE-Y0g":

        raise RuntimeError(
            "Sai YouTube ID cua video HSK3 so 2!"
        )

    data = fetch_transcript()

    # Luu du lieu Supadata goc truoc,
    # de co the kiem tra lai neu co loi.
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
