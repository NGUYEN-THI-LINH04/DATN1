
import json
import math
import re
from pathlib import Path

from pypinyin import lazy_pinyin, Style


# ==========================================
# 1. CAU HINH HSK4 VIDEO 4
# ==========================================

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk4")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video4_zh_preview.json"

OUTPUT = DATA / "video4_with_pinyin.json"
TRANSLATION_TEMPLATE = DATA / "video4_translation_template.txt"
REPORT = DATA / "video4_pinyin_report.txt"

VIDEO_ID = "xdULRJN_RZM"
EXPECTED_COUNT = 233


# ==========================================
# 2. HAM TAO PINYIN
# ==========================================

def make_pinyin(hanzi):

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
                    style=Style.TONE
                )
            )
        else:
            result.append(token)

    return " ".join(result).strip()


# ==========================================
# 3. XU LY DU LIEU
# ==========================================

def main():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if not isinstance(data, dict):
        raise ValueError("JSON khong hop le.")

    if data.get("module") != "shadowing":
        raise ValueError("Sai module.")

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError("Sai YouTube ID.")

    original = data.get("sentences")

    if not isinstance(original, list):
        raise ValueError("Khong co sentences.")

    if len(original) != EXPECTED_COUNT:
        raise ValueError(
            f"Can {EXPECTED_COUNT} doan, "
            f"hien co {len(original)}."
        )

    sentences = []
    short_segments = []
    long_segments = []
    previous_end = 0.0

    for i, item in enumerate(original, 1):

        if not isinstance(item, dict):
            raise ValueError(
                f"Du lieu doan {i} khong hop le."
            )

        try:
            start = float(item["start"])
            end = float(item["end"])
        except (KeyError, ValueError, TypeError):
            raise ValueError(
                f"Timestamp sai o doan {i}."
            )

        if not (
            math.isfinite(start)
            and math.isfinite(end)
        ):
            raise ValueError(
                f"Timestamp khong hop le o doan {i}."
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Thoi gian sai o doan {i}."
            )

        if (
            i > 1
            and start < previous_end - 0.001
        ):
            raise ValueError(
                f"Timestamp chong nhau o doan {i}."
            )

        hanzi = str(
            item.get("hanzi", "")
        ).strip()

        if not hanzi:
            raise ValueError(
                f"Thieu chu Han o doan {i}."
            )

        pinyin = make_pinyin(hanzi)

        if not pinyin:
            raise ValueError(
                f"Khong tao duoc pinyin doan {i}."
            )

        duration = end - start

        if duration < 0.8:
            short_segments.append(i)

        if duration > 10:
            long_segments.append(i)

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": ""
        })

        previous_end = end

    # ======================================
    # 4. LUU JSON
    # ======================================

    document = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "sentences": sentences
    }

    OUTPUT.write_text(
        json.dumps(
            document,
            ensure_ascii=False,
            indent=2,
            allow_nan=False
        ),
        encoding="utf-8"
    )

    # ======================================
    # 5. TAO FILE MAU DICH
    # ======================================

    lines = []

    for i, item in enumerate(sentences, 1):

        lines.append(
            f"{i:03d} "
            f"[{item['start']:.2f}-"
            f"{item['end']:.2f}] "
            f"{item['hanzi']}"
        )

        lines.append("VI: ")
        lines.append("")

    TRANSLATION_TEMPLATE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    # ======================================
    # 6. BAO CAO
    # ======================================

    report_lines = [
        "SHADOWING HSK4 - VIDEO 4",
        f"YouTube ID: {VIDEO_ID}",
        f"So doan: {len(sentences)}",
        f"Doan ngan < 0.8s: {len(short_segments)}",
        f"Doan dai > 10s: {len(long_segments)}",
        "",
        "CAC DOAN NGAN:",
        ", ".join(map(str, short_segments)) or "Khong co",
        "",
        "CAN KIEM TRA:",
        "Doan 039-043 co noi dung bat thuong.",
        "Can doi chieu voi am thanh video goc.",
        "Can kiem tra cach doc tu da am.",
        "",
        "CHUA DICH TIENG VIET.",
        "CHUA CAP NHAT SQL SERVER."
    ]

    REPORT.write_text(
        "\n".join(report_lines),
        encoding="utf-8"
    )

    # ======================================
    # 7. KIEM TRA FILE DA LUU
    # ======================================

    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    if len(saved["sentences"]) != EXPECTED_COUNT:
        raise RuntimeError(
            "So doan doc lai khong khop."
        )

    for old, new in zip(
        original,
        saved["sentences"]
    ):
        if (
            float(old["start"]) != new["start"]
            or float(old["end"]) != new["end"]
            or old["hanzi"].strip() != new["hanzi"]
        ):
            raise RuntimeError(
                "Du lieu goc bi thay doi."
            )

    # ======================================
    # 8. IN KET QUA
    # ======================================

    print(
        "===== HSK4 VIDEO 4 - TAO PINYIN ====="
    )

    print("YouTube:", VIDEO_ID)
    print("MaBaiHoc: 2050")
    print("So doan:", len(sentences))
    print("Doan < 0.8s:", len(short_segments))
    print("Doan > 10s:", len(long_segments))
    print("Timestamp chong nhau: 0")

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
    print("Mau dich:", TRANSLATION_TEMPLATE)
    print("Bao cao:", REPORT)

    print("\nKIEM TRA JSON: OK")
    print("CHUA DICH TIENG VIET.")
    print("CHUA CAP NHAT SQL SERVER.")


if __name__ == "__main__":
    main()
