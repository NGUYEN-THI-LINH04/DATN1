
import json
import math
import re
from pathlib import Path

from pypinyin import lazy_pinyin, Style


# ==================================================
# 1. CAU HINH SHADOWING HSK4 - VIDEO 5
# ==================================================

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk4")

DATA = BASE / "data" / "processed"

SOURCE = DATA / "video5_zh_preview.json"

OUTPUT = DATA / "video5_with_pinyin.json"

TRANSLATION_TEMPLATE = (
    DATA / "video5_translation_template.txt"
)

REPORT = DATA / "video5_pinyin_report.txt"

VIDEO_ID = "Q1FO6dr5T_Y"

MA_KHOA_HOC = 4
MA_BAI_HOC = 2059

EXPECTED_COUNT = 313


# ==================================================
# 2. HAM TAO PINYIN
# ==================================================

def make_pinyin(hanzi):

    # Lay cac cum chu Han hoac chu cai, chu so.
    # Bo qua dau cau vi phan noi dung goc
    # da giu nguyen trong truong hanzi.

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

            pinyin_tokens = lazy_pinyin(
                token,
                style=Style.TONE
            )

            result.extend(pinyin_tokens)

        else:
            result.append(token)

    return " ".join(result).strip()


# ==================================================
# 3. DOC VA KIEM TRA JSON NGUON
# ==================================================

def load_source():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if not isinstance(data, dict):
        raise ValueError(
            "JSON nguon khong hop le."
        )

    if data.get("module") != "shadowing":
        raise ValueError(
            "Sai module, yeu cau shadowing."
        )

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError(
            "YouTube ID khong khop video 5."
        )

    sentences = data.get("sentences")

    if not isinstance(sentences, list):
        raise ValueError(
            "Khong co danh sach sentences."
        )

    if len(sentences) != EXPECTED_COUNT:
        raise ValueError(
            f"Can {EXPECTED_COUNT} doan, "
            f"hien co {len(sentences)}."
        )

    return data


# ==================================================
# 4. TAO PINYIN CHO TUNG DOAN
# ==================================================

def prepare_sentences(original):

    sentences = []

    previous_end = 0.0

    short_segments = []
    long_segments = []

    for i, item in enumerate(original, 1):

        if not isinstance(item, dict):
            raise ValueError(
                f"Du lieu doan {i} khong hop le."
            )

        # Kiem tra timestamp
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
                f"Thoi gian khong hop le o doan {i}."
            )

        if (
            i > 1
            and start < previous_end - 0.001
        ):
            raise ValueError(
                f"Timestamp chong nhau o doan {i}."
            )

        # Lay chu Han
        hanzi = str(
            item.get("hanzi", "")
        ).strip()

        if not hanzi:
            raise ValueError(
                f"Thieu chu Han o doan {i}."
            )

        # Tao pinyin
        pinyin = make_pinyin(hanzi)

        if not pinyin:
            raise ValueError(
                f"Khong tao duoc pinyin o doan {i}."
            )

        duration = end - start

        if duration < 0.8:
            short_segments.append(i)

        if duration > 10:
            long_segments.append(i)

        # Giu nguyen timestamp va chu Han
        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": ""
        })

        previous_end = end

    return sentences, short_segments, long_segments


# ==================================================
# 5. LUU JSON CO PINYIN
# ==================================================

def save_json(sentences):

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

    return document


# ==================================================
# 6. TAO FILE MAU DICH TIENG VIET
# ==================================================

def create_translation_template(sentences):

    lines = []

    for i, item in enumerate(sentences, 1):

        lines.append(
            f"{i:03d} "
            f"[{item['start']:.2f}-"
            f"{item['end']:.2f}] "
            f"{item['hanzi']}"
        )

        lines.append(
            f"Pinyin: {item['pinyin']}"
        )

        lines.append("VI: ")
        lines.append("")

    TRANSLATION_TEMPLATE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )


# ==================================================
# 7. TAO BAO CAO
# ==================================================

def save_report(
    sentences,
    short_segments,
    long_segments
):

    report_lines = [
        "SHADOWING HSK4 - VIDEO 5",
        "",
        f"YouTube ID: {VIDEO_ID}",
        f"MaKhoaHoc: {MA_KHOA_HOC}",
        f"MaBaiHoc: {MA_BAI_HOC}",
        f"So doan: {len(sentences)}",
        "",
        f"So doan < 0.8s: {len(short_segments)}",
        f"So doan > 10s: {len(long_segments)}",
        "",
        "DANH SACH DOAN NGAN:",
        ", ".join(
            map(str, short_segments)
        ) or "Khong co",
        "",
        "DANH SACH DOAN DAI:",
        ", ".join(
            map(str, long_segments)
        ) or "Khong co",
        "",
        "CAC DOAN CAN RA SOAT:",
        "072-073: Tu bi ngat giua hai doan.",
        "134-135: Tu bi ngat giua hai doan.",
        "277-279: Tu bi ngat giua cac doan.",
        "Can kiem tra pinyin cua cac tu da am.",
        "Can doi chieu voi am thanh video goc.",
        "",
        "CHUA DICH TIENG VIET.",
        "CHUA CAP NHAT SQL SERVER."
    ]

    REPORT.write_text(
        "\n".join(report_lines),
        encoding="utf-8"
    )


# ==================================================
# 8. KIEM TRA DU LIEU SAU KHI LUU
# ==================================================

def verify_output(original, document):

    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    if saved != document:
        raise RuntimeError(
            "JSON doc lai khong khop."
        )

    if len(saved["sentences"]) != EXPECTED_COUNT:
        raise RuntimeError(
            "So doan sau khi luu khong bang 313."
        )

    for i, (old, new) in enumerate(
        zip(original, saved["sentences"]), 1
    ):

        if (
            float(old["start"]) != new["start"]
            or float(old["end"]) != new["end"]
            or old["hanzi"].strip() != new["hanzi"]
        ):
            raise RuntimeError(
                f"Du lieu goc bi thay doi tai doan {i}."
            )

        if not new["pinyin"].strip():
            raise RuntimeError(
                f"Thieu pinyin doan {i}."
            )


# ==================================================
# 9. MAIN
# ==================================================

def main():

    print(
        "===== HSK4 VIDEO 5 - TAO PINYIN ====="
    )

    data = load_source()

    original = data["sentences"]

    sentences, short_segments, long_segments = (
        prepare_sentences(original)
    )

    document = save_json(sentences)

    create_translation_template(sentences)

    save_report(
        sentences,
        short_segments,
        long_segments
    )

    verify_output(original, document)

    print("YouTube:", VIDEO_ID)
    print("MaKhoaHoc:", MA_KHOA_HOC)
    print("MaBaiHoc:", MA_BAI_HOC)

    print("So doan:", len(sentences))

    print(
        "Doan < 0.8s:",
        len(short_segments)
    )

    print(
        "Doan > 10s:",
        len(long_segments)
    )

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
