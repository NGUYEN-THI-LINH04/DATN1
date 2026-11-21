
from pathlib import Path
import json
import re

from pypinyin import lazy_pinyin, Style


# ==========================================
# 1. DUONG DAN
# ==========================================

BASE = Path(
    r"D:\DATN1\scripts\shadowing\hsk2"
)

DATA_DIR = BASE / "data" / "processed"

SOURCE = DATA_DIR / "video4_zh_preview.json"

OUTPUT = DATA_DIR / "video4_with_pinyin.json"

REPORT = DATA_DIR / "video4_pinyin_report.txt"

VIDEO_ID = "O_kkptuQPY8"


# ==========================================
# 2. TAO PINYIN
# ==========================================

def make_pinyin(hanzi):

    # Chi lay cac tu chu Han va ky tu Latin/so.
    # Khong dua dau cau vao dong pinyin.
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
# 3. DOC FILE PHU DE
# ==========================================

def main():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError(
            "Sai YouTube ID. Khong xu ly."
        )

    original = data.get("sentences", [])

    if len(original) != 171:
        raise ValueError(
            f"Du kien 171 doan, nhung co {len(original)}."
        )

    sentences = []
    long_segments = []
    previous_end = 0.0

    # ======================================
    # 4. XU LY TUNG DOAN
    # ======================================

    for index, item in enumerate(original, 1):

        start = float(item["start"])
        end = float(item["end"])

        # Chi chuan hoa khoang trang.
        # Giu nguyen noi dung chu Han.
        hanzi = re.sub(
            r"\s+",
            " ",
            str(item["hanzi"])
        ).strip()

        if not hanzi:
            raise ValueError(
                f"Doan {index} khong co chu Han."
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Timestamp sai o doan {index}."
            )

        if index > 1 and start < previous_end - 0.001:
            raise ValueError(
                f"Chong timestamp o doan {index}."
            )

        duration = round(end - start, 3)

        if duration > 10:
            long_segments.append({
                "number": index,
                "duration": duration,
                "hanzi": hanzi
            })

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": make_pinyin(hanzi),
            "vi": ""
        })

        previous_end = end

    # ======================================
    # 5. LUU JSON
    # ======================================

    result = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "title": (
            "中文口语练习 - "
            "Luyện nói về đồ ăn và cảm xúc"
        ),
        "status": "needs_translation",
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
    # 6. BAO CAO DOAN DAI
    # ======================================

    lines = [
        "VIDEO 4 - KIEM TRA PHU DE",
        f"YouTube ID: {VIDEO_ID}",
        f"So doan: {len(sentences)}",
        f"So doan dai hon 10 giay: {len(long_segments)}",
        "",
        "DANH SACH DOAN DAI:"
    ]

    for item in long_segments:
        lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.2f}s | "
            f"{item['hanzi']}"
        )

    REPORT.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    # ======================================
    # 7. IN KET QUA
    # ======================================

    print("===== VIDEO 4 - TAO PINYIN =====")
    print("Video:", VIDEO_ID)
    print("So doan:", len(sentences))
    print("JSON:", OUTPUT)
    print("Bao cao:", REPORT)

    print("\n===== 5 DOAN DAU =====")

    for i, sentence in enumerate(sentences[:5], 1):

        print(f"\n{i}. [{sentence['start']:.2f} - "
              f"{sentence['end']:.2f}]")

        print("Hanzi:", sentence["hanzi"])
        print("Pinyin:", sentence["pinyin"])

    print(
        "\nDoan dai hon 10 giay:",
        len(long_segments)
    )

    print("\nChua dich tieng Viet.")
    print("Chua cap nhat SQL Server.")


if __name__ == "__main__":
    main()
