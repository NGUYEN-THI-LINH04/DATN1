
import os
import json
import re
import time

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

API_KEY = os.getenv("SUPADATA_API_KEY", "").strip()

API_URL = "https://api.supadata.ai/v1/transcript"


# ==================================================
# 2. THONG TIN VIDEO HSK4 SO 5
# ==================================================

VIDEO_ID = "Q1FO6dr5T_Y"

VIDEO_URL = (
    f"https://www.youtube.com/watch?v={VIDEO_ID}"
)

VIDEO_TITLE = (
    "社交媒体是好是坏 - "
    "Mạng xã hội tốt hay xấu?"
)

MA_KHOA_HOC = 4
MA_BAI_HOC = 2059

RAW_FILE = RAW_DIR / "video5_supadata_zh.json"

PREVIEW_FILE = (
    PROCESSED_DIR / "video5_zh_preview.json"
)

TRANSCRIPT_FILE = (
    PROCESSED_DIR / "video5_transcript.txt"
)

REPORT_FILE = (
    PROCESSED_DIR / "video5_fetch_report.txt"
)


# ==================================================
# 3. GOI SUPADATA API
# ==================================================

def api_get(url, params=None):

    headers = {
        "x-api-key": API_KEY,
        "Accept": "application/json"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=90
    )

    if not response.ok:
        raise RuntimeError(
            f"Supadata HTTP {response.status_code}\n"
            f"{response.text[:1500]}"
        )

    try:
        data = response.json()

    except ValueError:
        raise RuntimeError(
            "Supadata khong tra ve JSON hop le."
        )

    if not isinstance(data, dict):
        raise RuntimeError(
            "Cau truc JSON cua Supadata khong hop le."
        )

    return data


def get_transcript():

    if not API_KEY:
        raise RuntimeError(
            "Chua co SUPADATA_API_KEY trong D:\\DATN1\\.env"
        )

    params = {
        "url": VIDEO_URL,
        "lang": "zh",
        "text": "false",
        "mode": "native"
    }

    print("\nDang lay phu de tieng Trung...")

    data = api_get(
        API_URL,
        params=params
    )

    # Truong hop API tra ket qua bat dong bo
    if "jobId" in data:

        job_id = data["jobId"]

        print("Supadata job ID:", job_id)

        job_url = f"{API_URL}/{job_id}"

        for attempt in range(1, 31):

            print(
                f"Dang kiem tra job: {attempt}/30"
            )

            time.sleep(5)

            job = api_get(job_url)

            status = str(
                job.get("status", "")
            ).lower()

            if status == "failed":
                raise RuntimeError(
                    "Supadata xu ly that bai:\n"
                    + json.dumps(
                        job.get("error", job),
                        ensure_ascii=False
                    )
                )

            if status == "completed":

                # Supadata co the boc transcript
                # trong truong result
                result = job.get("result")

                if isinstance(result, dict):
                    data = result

                elif isinstance(
                    job.get("content"), list
                ):
                    data = job

                else:
                    raise RuntimeError(
                        "Job completed nhung "
                        "khong co transcript."
                    )

                break

        else:
            raise RuntimeError(
                "Supadata job chua hoan thanh "
                "sau 30 lan kiem tra."
            )

    return data


# ==================================================
# 4. CHUAN HOA PHU DE THANH SENTENCES
# ==================================================

def clean_text(value):

    value = str(value or "")

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def normalize_transcript(data):

    lang = str(
        data.get("lang", "")
    ).strip()

    if not lang.lower().startswith("zh"):
        raise ValueError(
            f"Ngon ngu khong phai tieng Trung: {lang}"
        )

    content = data.get("content")

    if not isinstance(content, list):
        raise ValueError(
            "Supadata khong tra ve "
            "danh sach phu de co timestamp."
        )

    if not content:
        raise ValueError(
            "Danh sach phu de rong."
        )

    sentences = []

    for index, item in enumerate(content, 1):

        if not isinstance(item, dict):
            raise ValueError(
                f"Doan {index} khong phai object."
            )

        text = clean_text(
            item.get("text", "")
        )

        if not text:
            continue

        offset = item.get("offset")
        duration = item.get("duration")

        try:
            offset_ms = float(offset)
            duration_ms = float(duration)

        except (TypeError, ValueError):
            raise ValueError(
                f"Timestamp khong hop le "
                f"tai doan {index}."
            )

        if offset_ms < 0 or duration_ms <= 0:
            raise ValueError(
                f"Thoi gian sai o doan {index}."
            )

        start = round(
            offset_ms / 1000,
            3
        )

        end = round(
            (offset_ms + duration_ms) / 1000,
            3
        )

        if end <= start:
            raise ValueError(
                f"Doan {index} co end <= start."
            )

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": text,
            "pinyin": "",
            "vi": ""
        })

    if not sentences:
        raise ValueError(
            "Khong lay duoc doan phu de nao."
        )

    return sentences


# ==================================================
# 5. KIEM TRA CHAT LUONG PHU DE
# ==================================================

def analyze_sentences(sentences):

    duplicates = []
    overlaps = []
    short_segments = []
    long_segments = []

    previous = None

    hanzi_count = 0
    character_count = 0

    for index, item in enumerate(sentences, 1):

        text = item["hanzi"]

        start = item["start"]
        end = item["end"]

        duration = end - start

        if duration < 0.8:
            short_segments.append(index)

        if duration > 10:
            long_segments.append(index)

        if previous is not None:

            if (
                text == previous["hanzi"]
            ):
                duplicates.append(index)

            if start < previous["end"] - 0.001:
                overlaps.append(index)

        previous = item

        for char in text:

            # Dem chu Han
            if (
                "\u3400" <= char <= "\u9fff"
            ):
                hanzi_count += 1
                character_count += 1

            # Dem chu cai va chu so khac
            elif char.isalnum():
                character_count += 1

    ratio = (
        hanzi_count / character_count * 100
        if character_count else 0
    )

    return {
        "duplicates": duplicates,
        "overlaps": overlaps,
        "short_segments": short_segments,
        "long_segments": long_segments,
        "hanzi_ratio": round(ratio, 1)
    }


# ==================================================
# 6. LUU FILE JSON, TRANSCRIPT VA BAO CAO
# ==================================================

def save_results(
    raw_data,
    sentences,
    analysis
):

    # Luu JSON goc Supadata
    RAW_FILE.write_text(
        json.dumps(
            raw_data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # JSON preview dung cho buoc tao pinyin
    preview = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
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

    # File transcript de kiem tra va dich
    transcript_lines = []

    for index, item in enumerate(
        sentences, 1
    ):

        transcript_lines.append(
            f"{index:03d} "
            f"[{item['start']:.2f}-"
            f"{item['end']:.2f}] "
            f"{item['hanzi']}"
        )

    TRANSCRIPT_FILE.write_text(
        "\n".join(transcript_lines),
        encoding="utf-8"
    )

    # Bao cao chat luong phu de
    report_lines = [
        "SHADOWING HSK4 - VIDEO 5",
        "",
        f"YouTube ID: {VIDEO_ID}",
        f"Video: {VIDEO_URL}",
        f"MaKhoaHoc: {MA_KHOA_HOC}",
        f"MaBaiHoc: {MA_BAI_HOC}",
        f"Tieu de: {VIDEO_TITLE}",
        "",
        f"So doan: {len(sentences)}",
        f"Ty le chu Han: {analysis['hanzi_ratio']}%",
        "",
        f"So doan trung lien tiep: "
        f"{len(analysis['duplicates'])}",
        f"Timestamp chong nhau: "
        f"{len(analysis['overlaps'])}",
        f"So doan > 10s: "
        f"{len(analysis['long_segments'])}",
        f"So doan < 0.8s: "
        f"{len(analysis['short_segments'])}",
        "",
        "DANH SACH DOAN TRUNG:",
        str(analysis["duplicates"]),
        "",
        "DANH SACH TIMESTAMP CHONG:",
        str(analysis["overlaps"]),
        "",
        "DANH SACH DOAN NGAN:",
        str(analysis["short_segments"]),
        "",
        "DANH SACH DOAN DAI:",
        str(analysis["long_segments"]),
        "",
        "CAN DOI CHIEU VOI AM THANH VIDEO GOC.",
        "CHUA TAO PINYIN.",
        "CHUA DICH TIENG VIET.",
        "CHUA CAP NHAT SQL SERVER."
    ]

    REPORT_FILE.write_text(
        "\n".join(report_lines),
        encoding="utf-8"
    )


# ==================================================
# 7. HAM MAIN
# ==================================================

def main():

    print(
        "===== SHADOWING HSK4 - VIDEO 5 ====="
    )

    print("YouTube ID:", VIDEO_ID)
    print("Video:", VIDEO_URL)
    print("MaKhoaHoc:", MA_KHOA_HOC)
    print("MaBaiHoc:", MA_BAI_HOC)
    print("Tieu de:", VIDEO_TITLE)

    # Lay transcript
    data = get_transcript()

    # Chuan hoa
    sentences = normalize_transcript(data)

    # Phan tich
    analysis = analyze_sentences(sentences)

    print("\n===== KIEM TRA PHU DE =====")

    print(
        "Language:",
        data.get("lang")
    )

    print(
        "Available:",
        data.get("availableLangs", [])
    )

    print(
        "So doan phu de:",
        len(sentences)
    )

    print(
        "Ty le chu Han:",
        f"{analysis['hanzi_ratio']}%"
    )

    print(
        "So doan trung:",
        len(analysis["duplicates"])
    )

    print(
        "Timestamp chong nhau:",
        len(analysis["overlaps"])
    )

    print(
        "So doan > 10 giay:",
        len(analysis["long_segments"])
    )

    print(
        "So doan < 0.8 giay:",
        len(analysis["short_segments"])
    )

    print(
        "Thoi gian:",
        sentences[0]["start"],
        "->",
        sentences[-1]["end"],
        "giay"
    )

    print("\n===== 15 DOAN DAU =====")

    for index, item in enumerate(
        sentences[:15], 1
    ):

        print(
            f"{index:03d} "
            f"[{item['start']:.2f} - "
            f"{item['end']:.2f}] "
            f"{item['hanzi']}"
        )

    # Luu file
    save_results(
        data,
        sentences,
        analysis
    )

    print("\n===== DANH GIA =====")

    if (
        not analysis["overlaps"]
        and not analysis["duplicates"]
    ):
        print(
            "Timestamp va doan trung: OK"
        )

    else:
        print(
            "Can kiem tra timestamp "
            "hoac doan trung."
        )

    print(
        "Can doi chieu phu de "
        "voi am thanh video goc."
    )

    print("\n===== FILE DA LUU =====")

    print("Raw:", RAW_FILE)
    print("Preview:", PREVIEW_FILE)
    print("Transcript:", TRANSCRIPT_FILE)
    print("Bao cao:", REPORT_FILE)

    print("\nCHUA CAP NHAT SQL SERVER.")


if __name__ == "__main__":
    main()
