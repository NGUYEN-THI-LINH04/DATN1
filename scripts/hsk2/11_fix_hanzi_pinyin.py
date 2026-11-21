from pathlib import Path
import csv
import re


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_DIR / "hanzi_hsk2_meanings_completed.csv"
OUTPUT_FILE = DATA_DIR / "hanzi_hsk2_final.csv"


# ============================================================
# CAC TRUONG HOP DA XAC NHAN SAI CACH DOC THEO NGU CANH HSK2
# ============================================================

PINYIN_OVERRIDES = {
    "色": "sè",       # 白色 báisè
    "单": "dān",      # 菜单 càidān
    "观": "guān",     # 参观 cānguān
    "处": "chù",      # 到处 dàochù
    "便": "biàn",     # 方便 fāngbiàn
    "板": "bǎn",      # 黑板 hēibǎn
    "结": "jié",      # 结果 jiéguǒ
    "可": "kě",       # 可爱 kě'ài
    "乐": "lè",       # 快乐 kuàilè
    "漂": "piào",     # 漂亮 piàoliang
    "末": "mò",       # 周末 zhōumò
}


# ============================================================
# CHUYEN PINYIN SO -> PINYIN DAU
#
# vi du:
# qing2 -> qíng
# fa3   -> fǎ
# lu:3  -> lǚ
# Shi4  -> shì
# ============================================================

TONE_TABLE = {
    "a": ["a", "ā", "á", "ǎ", "à"],
    "e": ["e", "ē", "é", "ě", "è"],
    "i": ["i", "ī", "í", "ǐ", "ì"],
    "o": ["o", "ō", "ó", "ǒ", "ò"],
    "u": ["u", "ū", "ú", "ǔ", "ù"],
    "ü": ["ü", "ǖ", "ǘ", "ǚ", "ǜ"],
}


def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def numbered_to_tone_mark(pinyin):
    """
    Chuyen mot am tiet Pinyin dang:
        qing2 -> qíng
        lu:3  -> lǚ
        lv3   -> lǚ

    Neu da co dau thanh thi giu nguyen.
    """

    pinyin = clean(pinyin)

    if not pinyin:
        return ""

    # Chuan hoa chu hoa do MucTuDien sinh ra
    pinyin = pinyin.lower()

    # Chuan hoa u: / v
    pinyin = pinyin.replace("u:", "ü")
    pinyin = pinyin.replace("v", "ü")

    match = re.fullmatch(
        r"([a-zü]+)([0-5])",
        pinyin
    )

    if not match:
        return pinyin

    syllable = match.group(1)
    tone = int(match.group(2))

    # Thanh nhe
    if tone in (0, 5):
        return syllable

    # Quy tac dat dau Hanyu Pinyin:
    # 1. co a -> danh dau a
    # 2. co e -> danh dau e
    # 3. co ou -> danh dau o
    # 4. con lai danh dau nguyen am cuoi

    position = -1

    if "a" in syllable:
        position = syllable.index("a")

    elif "e" in syllable:
        position = syllable.index("e")

    elif "ou" in syllable:
        position = syllable.index("o")

    else:
        for index in range(
            len(syllable) - 1,
            -1,
            -1
        ):
            if syllable[index] in "aeiouü":
                position = index
                break

    if position == -1:
        return syllable

    vowel = syllable[position]

    marked = TONE_TABLE[
        vowel
    ][tone]

    return (
        syllable[:position]
        + marked
        + syllable[position + 1:]
    )


def main():

    print("=" * 72)
    print("BUOC 11 - KIEM TRA VA CHUAN HOA PINYIN CHU HAN HSK2")
    print("KHONG GHI SQL")
    print("=" * 72)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file:\n{INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        fieldnames = reader.fieldnames
        rows = list(reader)

    if len(rows) != 299:
        raise ValueError(
            f"Du kien 299 chu, "
            f"nhung file co {len(rows)}."
        )

    normalized_count = 0
    override_count = 0
    changes = []

    for row in rows:

        char = clean(
            row.get("KyTu")
        )

        old_pinyin = clean(
            row.get("Pinyin")
        )

        # --------------------------------------------
        # 1. Chuan hoa tone-number -> tone-mark
        # --------------------------------------------

        new_pinyin = numbered_to_tone_mark(
            old_pinyin
        )

        # --------------------------------------------
        # 2. Sua cac chu da xac nhan sai doc
        # --------------------------------------------

        if char in PINYIN_OVERRIDES:

            corrected = PINYIN_OVERRIDES[
                char
            ]

            if new_pinyin != corrected:
                new_pinyin = corrected
                override_count += 1

        if old_pinyin != new_pinyin:

            normalized_count += 1

            changes.append({
                "KyTu": char,
                "PinyinCu": old_pinyin,
                "PinyinMoi": new_pinyin,
                "ViDu": clean(
                    row.get(
                        "ViDuTiengTrung"
                    )
                ),
                "ViDuPinyin": clean(
                    row.get(
                        "ViDuPinyin"
                    )
                ),
            })

        row["Pinyin"] = new_pinyin

    # ========================================================
    # KIEM TRA CUOI
    # ========================================================

    missing_pinyin = []
    missing_meaning = []
    missing_radical = []
    missing_strokes = []

    numeric_pinyin = []

    for row in rows:

        char = clean(
            row.get("KyTu")
        )

        pinyin = clean(
            row.get("Pinyin")
        )

        if not pinyin:
            missing_pinyin.append(
                char
            )

        if not clean(
            row.get(
                "NghiaTiengViet"
            )
        ):
            missing_meaning.append(
                char
            )

        if not clean(
            row.get("MaBoThu")
        ):
            missing_radical.append(
                char
            )

        if not clean(
            row.get("SoNet")
        ):
            missing_strokes.append(
                char
            )

        if re.search(
            r"[0-9]",
            pinyin
        ):
            numeric_pinyin.append(
                f"{char}:{pinyin}"
            )

    # Khong cho tao file final neu con thieu du lieu quan trong

    if missing_pinyin:
        raise ValueError(
            "Con thieu Pinyin: "
            + ", ".join(
                missing_pinyin
            )
        )

    if missing_meaning:
        raise ValueError(
            "Con thieu nghia: "
            + ", ".join(
                missing_meaning
            )
        )

    if missing_radical:
        raise ValueError(
            "Con thieu MaBoThu: "
            + ", ".join(
                missing_radical
            )
        )

    if missing_strokes:
        raise ValueError(
            "Con thieu SoNet: "
            + ", ".join(
                missing_strokes
            )
        )

    if numeric_pinyin:
        raise ValueError(
            "Van con Pinyin dang so: "
            + ", ".join(
                numeric_pinyin
            )
        )

    # ========================================================
    # GHI FILE FINAL
    # ========================================================

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(
            rows
        )

    print()
    print(
        f"Tong chu HSK2: "
        f"{len(rows)}"
    )

    print(
        f"So dong Pinyin duoc chuan hoa/sua: "
        f"{normalized_count}"
    )

    print(
        f"So chu sai cach doc duoc sua theo HSK2: "
        f"{override_count}"
    )

    print()
    print("KIEM TRA CUOI:")

    print(
        f"  Thieu Pinyin: "
        f"{len(missing_pinyin)}"
    )

    print(
        f"  Thieu nghia Viet: "
        f"{len(missing_meaning)}"
    )

    print(
        f"  Thieu MaBoThu: "
        f"{len(missing_radical)}"
    )

    print(
        f"  Thieu SoNet: "
        f"{len(missing_strokes)}"
    )

    print(
        f"  Pinyin con dang so: "
        f"{len(numeric_pinyin)}"
    )

    print()
    print("CAC DONG DA DOI PINYIN:")

    for item in changes:

        print(
            f"  {item['KyTu']}: "
            f"{item['PinyinCu']} "
            f"-> {item['PinyinMoi']}"
        )

    print()
    print("DA TAO FILE CUOI:")
    print(OUTPUT_FILE)

    print()
    print(
        "KHONG INSERT/UPDATE/DELETE SQL."
    )


if __name__ == "__main__":
    main()