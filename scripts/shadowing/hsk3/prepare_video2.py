
import json
import re
from pathlib import Path

from pypinyin import lazy_pinyin, Style


# ==========================================
# 1. CAU HINH VIDEO HSK3 SO 2
# ==========================================

BASE = Path(
    r"D:\DATN1\scripts\shadowing\hsk3"
)

DATA = BASE / "data" / "processed"

SOURCE = DATA / "video2_zh_preview.json"
OUTPUT = DATA / "video2_with_pinyin.json"
REPORT = DATA / "video2_pinyin_report.txt"

VIDEO_ID = "tQKsIFE-Y0g"
EXPECTED_COUNT = 216


# ==========================================
# 2. TAO PINYIN CO DAU THANH
# ==========================================

def make_pinyin(hanzi):

    # Tach cum chu Han va chu/so Latin.
    # Bo dau cau, giu nguyen chu Han goc.
    tokens = re.findall(
        r"[\u3400-\u9fff]+|[A-Za-z0-9]+",
        hanzi
    )

    result = []

    for token in tokens:

        if re.fullmatch(
            r"[\u3400-\u9fff]+",
            token
        ):
            result.extend(
                lazy_pinyin(
                    token,
                    style=Style.TONE,
                    neutral_tone_with_five=False
                )
            )

        else:
            result.append(token)

    return " ".join(result).strip()


# ==========================================
# 3. DOC VA KIEM TRA PHU DE
# ==========================================

def main():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if not isinstance(data, dict):
        raise ValueError("JSON khong hop le.")

    if data.get("module") != "shadowing":
        raise ValueError("Sai module Shadowing.")

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError(
            "Sai YouTube ID cua video 2!"
        )

    original = data.get("sentences", [])

    if not isinstance(original, list):
        raise ValueError(
            "sentences phai la danh sach."
        )

    if len(original) != EXPECTED_COUNT:
        raise ValueError(
            f"Can {EXPECTED_COUNT} doan, "
            f"hien co {len(original)}."
        )

    sentences = []
    short_segments = []
    long_segments = []
    overlaps = []

    previous_end = 0.0

    # ======================================
    # 4. XU LY TUNG DOAN
    # ======================================

    for i, item in enumerate(original, 1):

        start = round(float(item["start"]), 3)
        end = round(float(item["end"]), 3)

        hanzi = re.sub(
            r"\s+",
            " ",
            str(item["hanzi"])
        ).strip()

        if not hanzi:
            raise ValueError(
                f"Doan {i} khong co chu Han."
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Timestamp sai o doan {i}."
            )

        if i > 1 and start < previous_end - 0.001:
            overlaps.append(i)

        duration = round(end - start, 3)

        if duration < 0.8:
            short_segments.append({
                "number": i,
                "duration": duration,
                "hanzi": hanzi
            })

        if duration > 10:
            long_segments.append({
                "number": i,
                "duration": duration,
                "hanzi": hanzi
            })

        pinyin = make_pinyin(hanzi)

        if not pinyin:
            raise ValueError(
                f"Khong tao duoc pinyin doan {i}."
            )

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": ""
        })

        previous_end = end

    if overlaps:
        raise ValueError(
            f"Timestamp chong nhau: {overlaps}"
        )

    # ======================================
    # 5. LUU FILE PINYIN
    # ======================================

    result = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "sentences": sentences
    }

    OUTPUT.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # ======================================
    # 6. TAO BAO CAO KIEM TRA
    # ======================================

    lines = [
        "SHADOWING HSK3 - VIDEO 2",
        "",
        f"YouTube ID: {VIDEO_ID}",
        f"So doan: {len(sentences)}",
        f"Doan < 0.8 giay: {len(short_segments)}",
        f"Doan > 10 giay: {len(long_segments)}",
        "Timestamp chong nhau: 0",
        "",
        "===== DOAN QUA NGAN ====="
    ]

    for item in short_segments:
        lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    lines.extend([
        "",
        "===== DOAN QUA DAI ====="
    ])

    for item in long_segments:
        lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    lines.extend([
        "",
        "===== NOI DUNG CAN RA SOAT =====",
        "Doan 014: Co ky hieu (笑).",
        "Kiem tra cac tu da am trong pinyin.",
        "Kiem tra doan ngan voi video goc.",
        "",
        "CHUA DICH TIENG VIET.",
        "CHUA CAP NHAT SQL SERVER."
    ])

    REPORT.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    # ======================================
    # 7. KIEM TRA FILE DA LUU
    # ======================================

    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    assert saved["youtube_id"] == VIDEO_ID
    assert len(saved["sentences"]) == EXPECTED_COUNT

    assert all(
        item["hanzi"] and item["pinyin"]
        for item in saved["sentences"]
    )

    print(
        "===== HSK3 VIDEO 2 - TAO PINYIN ====="
    )
    print("YouTube:", VIDEO_ID)
    print("So doan:", len(sentences))
    print("Doan < 0.8s:", len(short_segments))
    print("Doan > 10s:", len(long_segments))
    print("Timestamp chong nhau:", len(overlaps))

    print("\n===== 5 DOAN DAU =====")

    for i, item in enumerate(sentences[:5], 1):
        print(
            f"\n{i:03d} "
            f"[{item['start']:.2f} - "
            f"{item['end']:.2f}]"
        )
        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])

    print("\n===== FILE DA LUU =====")
    print("JSON:", OUTPUT)
    print("Bao cao:", REPORT)

    print("\nKIEM TRA JSON: OK")
    print("CHUA DICH TIENG VIET.")
    print("CHUA CAP NHAT SQL SERVER.")


if __name__ == "__main__":
    main()
