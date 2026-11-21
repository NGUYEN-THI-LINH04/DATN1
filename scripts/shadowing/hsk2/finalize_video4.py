
from pathlib import Path
import json
import re

# ==========================================
# 1. CAU HINH
# ==========================================

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk2")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video4_translated_full.json"
OUTPUT = DATA / "video4_ready_for_review.json"
REPORT = DATA / "video4_review_report.txt"

VIDEO_ID = "O_kkptuQPY8"
EXPECTED_COUNT = 171


# ==========================================
# 2. CHUAN HOA NOI DUNG
# ==========================================

def clean_text(value):
    return re.sub(
        r"\s+", " ", str(value or "")
    ).strip()


def clean_pinyin(value):
    text = clean_text(value)

    # Loai bo dau cau, khong thay doi thanh dieu.
    text = re.sub(
        r"[，。！？；：、,.!?;:“”\"'（）()\[\]…]+",
        " ",
        text
    )

    return clean_text(text)


# ==========================================
# 3. KIEM TRA DU LIEU
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
        raise ValueError("Sai YouTube ID!")

    original = data.get("sentences", [])

    if len(original) != EXPECTED_COUNT:
        raise ValueError(
            f"Can {EXPECTED_COUNT} doan, "
            f"hien co {len(original)}"
        )

    sentences = []
    long_segments = []
    review_items = []

    for i, item in enumerate(original, 1):

        start = round(float(item["start"]), 3)
        end = round(float(item["end"]), 3)

        hanzi = clean_text(item["hanzi"])
        pinyin = clean_pinyin(item["pinyin"])
        vi = clean_text(item["vi"])

        if not all([hanzi, pinyin, vi]):
            raise ValueError(
                f"Doan {i} thieu noi dung."
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Timestamp khong hop le o doan {i}"
            )

        if sentences:
            previous_end = sentences[-1]["end"]

            if start < previous_end - 0.001:
                raise ValueError(
                    f"Timestamp chong nhau o doan {i}"
                )

        duration = round(end - start, 3)

        if duration > 10:
            long_segments.append({
                "number": i,
                "duration": duration,
                "hanzi": hanzi
            })

        # Phat hien cac cho can doi chieu.
        reasons = []

        if "[" in hanzi or "]" in hanzi:
            reasons.append("Co dau ngoac vuong")

        if hanzi.startswith(("”", "“")):
            reasons.append("Can kiem tra dau ngoac kep")

        if hanzi.endswith(("“", "”")):
            reasons.append("Can kiem tra dau ngoac kep")

        if len(hanzi) > 95:
            reasons.append("Doan rat dai")

        if reasons:
            review_items.append({
                "number": i,
                "reasons": reasons,
                "hanzi": hanzi
            })

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": vi
        })

    # ======================================
    # 4. TAO JSON CHUAN
    # ======================================

    result = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "description": (
            "Hoi thoai tieng Trung ve do an, "
            "huong vi va cam xuc."
        ),
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
    # 5. BAO CAO KIEM TRA
    # ======================================

    lines = [
        "BAO CAO SHADOWING HSK2 - VIDEO 4",
        "",
        f"YouTube ID: {VIDEO_ID}",
        f"So doan: {len(sentences)}",
        f"So doan > 10 giay: {len(long_segments)}",
        f"So doan can xem lai: {len(review_items)}",
        "",
        "===== DOAN DAI HON 10 GIAY =====",
    ]

    for item in long_segments:
        lines.extend([
            "",
            f"Doan {item['number']}: "
            f"{item['duration']:.2f} giay",
            item["hanzi"]
        ])

    lines.extend([
        "",
        "===== NOI DUNG CAN DOI CHIEU =====",
    ])

    for item in review_items:
        lines.extend([
            "",
            f"Doan {item['number']}: "
            + ", ".join(item["reasons"]),
            item["hanzi"]
        ])

    # Mot so cho trong transcript goc
    # co cau hoi va dau ngoac keo qua 2 doan.
    lines.extend([
        "",
        "===== VI TRI NEN NGHE KIEM TRA =====",
        "Doan 100-101: Cau hoi bi cat giua hai doan",
        "Doan 104-105: Loi thoai va dau ngoac kep",
        "Doan 120: Co ky hieu [味道]",
        "",
        "Pinyin tao tu dong can ra soat tu da am.",
    ])

    REPORT.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    # ======================================
    # 6. IN KET QUA
    # ======================================

    print("===== VIDEO 4 - CHUAN HOA =====")
    print("YouTube:", VIDEO_ID)
    print("So doan:", len(sentences))
    print("Doan > 10 giay:", len(long_segments))
    print("Doan can xem lai:", len(review_items))
    print("Timestamp chong nhau: 0")

    print("\nJSON:", OUTPUT)
    print("Bao cao:", REPORT)

    print("\n===== CAC DOAN DAI =====")

    for item in long_segments:
        print(
            f"Doan {item['number']}: "
            f"{item['duration']:.2f}s"
        )

    # Doc lai file de xac minh.
    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    assert saved["youtube_id"] == VIDEO_ID
    assert len(saved["sentences"]) == 171

    print("\nKIEM TRA JSON: OK")
    print("CHUA CAP NHAT SQL SERVER.")


if __name__ == "__main__":
    main()
