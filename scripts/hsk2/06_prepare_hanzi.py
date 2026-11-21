from pathlib import Path
from collections import OrderedDict
import csv
import re
import pyodbc


# ============================================================
# 1. CAU HINH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_FILE = OUTPUT_DIR / "hanzi_hsk2_draft.csv"

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=HocTiengTrungDB;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


# ============================================================
# 2. KET NOI SQL
# ============================================================

def get_connection():
    return pyodbc.connect(
        CONNECTION_STRING,
        timeout=15,
        autocommit=False
    )


# ============================================================
# 3. HAM HO TRO
# ============================================================

def clean_text(value):
    if value is None:
        return ""

    text = str(value).replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def is_hanzi(char):
    if not char:
        return False

    code = ord(char)

    return (
        0x3400 <= code <= 0x4DBF
        or 0x4E00 <= code <= 0x9FFF
        or 0xF900 <= code <= 0xFAFF
        or 0x20000 <= code <= 0x2FA1F
    )


def clean_dictionary_meaning(value):
    """
    Chi lam sach nhe cac ghi chu LT.
    Khong tu dong rut gon nghia thanh nghia cuoi cung.
    """

    text = clean_text(value)

    if not text:
        return ""

    parts = re.split(
        r"\s*/\s*",
        text
    )

    result = []

    for part in parts:
        part = clean_text(part)

        if not part:
            continue

        # Bo phan LT:...
        position = part.upper().find("LT:")

        if position >= 0:
            before = clean_text(
                part[:position]
            )

            if before:
                result.append(before)

            continue

        result.append(part)

    # Loai trung
    unique = []
    seen = set()

    for item in result:
        key = item.casefold()

        if key not in seen:
            seen.add(key)
            unique.append(item)

    return " / ".join(unique)


# ============================================================
# 4. DOC DANH SACH HSK2
# ============================================================

def load_hsk2_words(cursor):

    cursor.execute("""
        SELECT
            MaTuHSK,
            MaMucNoiBo,
            SoThuTuNguon,
            ChuHan,
            PhienAm,
            NghiaTiengVietThamChieu
        FROM dbo.TuVungHSKChuan
        WHERE MaCapDo = 2
        ORDER BY
            SoThuTuNguon,
            MaTuHSK;
    """)

    rows = []

    for row in cursor.fetchall():
        rows.append({
            "MaTuHSK": row.MaTuHSK,
            "MaMucNoiBo":
                clean_text(row.MaMucNoiBo),
            "SoThuTuNguon":
                row.SoThuTuNguon,
            "ChuHan":
                clean_text(row.ChuHan),
            "PhienAm":
                clean_text(row.PhienAm),
            "Nghia":
                clean_text(
                    row.NghiaTiengVietThamChieu
                ),
        })

    return rows


# ============================================================
# 5. DOC CHU HAN DA CO
# ============================================================

def load_existing_hanzi(cursor):

    cursor.execute("""
        SELECT DISTINCT KyTu
        FROM dbo.ChuHan
        WHERE KyTu IS NOT NULL;
    """)

    result = set()

    for row in cursor.fetchall():
        char = clean_text(row.KyTu)

        if char:
            result.add(char)

    return result


# ============================================================
# 6. DOC TU DON TRONG TUVUNG
# ============================================================

def load_single_character_vocabulary(cursor):

    cursor.execute("""
        SELECT
            MaTuVung,
            ChuHan,
            PhienAm,
            NghiaTiengViet
        FROM dbo.TuVung
        WHERE
            ChuHan IS NOT NULL
            AND LEN(ChuHan) = 1;
    """)

    result = {}

    for row in cursor.fetchall():

        char = clean_text(row.ChuHan)

        if not char or not is_hanzi(char):
            continue

        result.setdefault(
            char,
            {
                "Pinyin":
                    clean_text(row.PhienAm),

                "NghiaTiengViet":
                    clean_dictionary_meaning(
                        row.NghiaTiengViet
                    ),

                "Nguon":
                    "TuVung",
            }
        )

    return result


# ============================================================
# 7. DOC TU DON TRONG TUVUNGHSKCHUAN HSK2
# ============================================================

def load_single_character_hsk2(cursor):

    cursor.execute("""
        SELECT
            ChuHan,
            PhienAm,
            NghiaTiengVietThamChieu
        FROM dbo.TuVungHSKChuan
        WHERE
            MaCapDo = 2
            AND ChuHan IS NOT NULL
            AND LEN(ChuHan) = 1
        ORDER BY MaTuHSK;
    """)

    result = {}

    for row in cursor.fetchall():

        char = clean_text(row.ChuHan)

        if not char or not is_hanzi(char):
            continue

        result.setdefault(
            char,
            {
                "Pinyin":
                    clean_text(row.PhienAm),

                "NghiaTiengViet":
                    clean_dictionary_meaning(
                        row.NghiaTiengVietThamChieu
                    ),

                "Nguon":
                    "TuVungHSKChuan",
            }
        )

    return result


# ============================================================
# 8. FALLBACK TU MUCTUDIEN
# ============================================================

def load_dictionary_characters(cursor):

    cursor.execute("""
        SELECT
            ChuHan,
            PhienAm,
            NghiaTiengViet,
            NghiaVietDaDuyet
        FROM dbo.MucTuDien
        WHERE
            ChuHan IS NOT NULL
            AND LEN(ChuHan) = 1;
    """)

    result = {}

    for row in cursor.fetchall():

        char = clean_text(row.ChuHan)

        if not char or not is_hanzi(char):
            continue

        meaning = clean_dictionary_meaning(
            row.NghiaTiengViet
        )

        # Chi uu tien dong co nghia Viet
        if not meaning:
            continue

        current = result.get(char)

        item = {
            "Pinyin":
                clean_text(row.PhienAm),

            "NghiaTiengViet":
                meaning,

            "Nguon":
                "MucTuDien",

            "DaDuyet":
                bool(row.NghiaVietDaDuyet),
        }

        # Neu co ban nghia da duyet thi uu tien
        if (
            current is None
            or item["DaDuyet"]
        ):
            result[char] = item

    return result


# ============================================================
# 9. TAO DANH SACH KY TU HSK2
# ============================================================

def collect_hsk2_characters(words):

    characters = OrderedDict()

    for word in words:

        hanzi_word = word["ChuHan"]

        for char in hanzi_word:

            if not is_hanzi(char):
                continue

            if char not in characters:
                characters[char] = {
                    "words": [],
                    "first_order":
                        word["SoThuTuNguon"],
                }

            if hanzi_word not in characters[
                char
            ]["words"]:

                characters[
                    char
                ]["words"].append(
                    hanzi_word
                )

    return characters


# ============================================================
# 10. CHON PINYIN + NGHIA TOT NHAT
# ============================================================

def choose_basic_data(
    char,
    hsk_single,
    vocabulary_single,
    dictionary_single
):

    # Uu tien tu don dung trong danh sach HSK2
    if char in hsk_single:
        return hsk_single[char]

    # Sau do dung TuVung cua he thong
    if char in vocabulary_single:
        return vocabulary_single[char]

    # Cuoi cung moi dung MucTuDien
    if char in dictionary_single:
        return dictionary_single[char]

    return {
        "Pinyin": "",
        "NghiaTiengViet": "",
        "Nguon": "",
    }


# ============================================================
# 11. GHI CSV
# ============================================================

FIELDS = [
    "MaChuHanTam",
    "MaBaiHoc",
    "MaBoThu",
    "KyTu",
    "Pinyin",
    "NghiaTiengViet",
    "SoNet",
    "CachGhiNho",
    "ViDuTiengTrung",
    "ViDuPinyin",
    "ViDuTiengViet",
    "MaTep",
    "MaNguon",
    "ThuTuTam",
    "TrangThai",
    "TuHSK2ChuaKyTu",
    "NguonPinyinNghia",
    "CanBoSung",
]


def write_csv(rows):

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS
        )

        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# 12. MAIN
# ============================================================

def main():

    print("=" * 66)
    print("BUOC 6 - CHUAN BI CHU HAN HSK2")
    print("CHE DO: CHI DOC SQL - KHONG GHI SQL")
    print("=" * 66)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if OUTPUT_FILE.exists():
        raise FileExistsError(
            f"File da ton tai:\n"
            f"{OUTPUT_FILE}\n"
            "Khong tu dong ghi de."
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        words = load_hsk2_words(
            cursor
        )

        if len(words) != 772:
            raise ValueError(
                "Du kien 772 tu HSK2, "
                f"nhung SQL co {len(words)}."
            )

        existing_hanzi = (
            load_existing_hanzi(
                cursor
            )
        )

        hsk_single = (
            load_single_character_hsk2(
                cursor
            )
        )

        vocabulary_single = (
            load_single_character_vocabulary(
                cursor
            )
        )

        dictionary_single = (
            load_dictionary_characters(
                cursor
            )
        )

        characters = (
            collect_hsk2_characters(
                words
            )
        )

        total_unique = len(
            characters
        )

        new_chars = [
            char
            for char in characters
            if char not in existing_hanzi
        ]

        result_rows = []

        missing_pinyin = 0
        missing_meaning = 0

        for index, char in enumerate(
            new_chars,
            start=1
        ):

            basic = choose_basic_data(
                char,
                hsk_single,
                vocabulary_single,
                dictionary_single
            )

            pinyin = clean_text(
                basic.get("Pinyin")
            )

            meaning = clean_text(
                basic.get(
                    "NghiaTiengViet"
                )
            )

            issues = []

            if not pinyin:
                issues.append(
                    "THIEU_PINYIN"
                )
                missing_pinyin += 1

            if not meaning:
                issues.append(
                    "THIEU_NGHIA"
                )
                missing_meaning += 1

            # Bo thu + so net chua lay o buoc nay
            issues.append(
                "CHUA_BO_SUNG_UNIHAN"
            )

            result_rows.append({
                "MaChuHanTam":
                    f"H2-{index:04d}",

                # Sau nay moi gan bai hoc
                "MaBaiHoc":
                    "",

                # Buoc tiep theo moi map BoThu
                "MaBoThu":
                    "",

                "KyTu":
                    char,

                "Pinyin":
                    pinyin,

                "NghiaTiengViet":
                    meaning,

                # Buoc tiep theo lay Unihan/
                # Make Me a Hanzi
                "SoNet":
                    "",

                "CachGhiNho":
                    "",

                "ViDuTiengTrung":
                    "",

                "ViDuPinyin":
                    "",

                "ViDuTiengViet":
                    "",

                "MaTep":
                    "",

                "MaNguon":
                    "",

                "ThuTuTam":
                    index,

                "TrangThai":
                    "ban_nhap",

                "TuHSK2ChuaKyTu":
                    " | ".join(
                        characters[
                            char
                        ]["words"][:10]
                    ),

                "NguonPinyinNghia":
                    basic.get(
                        "Nguon",
                        ""
                    ),

                "CanBoSung":
                    "; ".join(
                        issues
                    ),
            })

        write_csv(
            result_rows
        )

        # Day chi la script doc
        connection.rollback()

        print()
        print(
            f"Tong tu HSK2: "
            f"{len(words)}"
        )

        print(
            f"Tong ky tu Han khac nhau "
            f"xuat hien trong HSK2: "
            f"{total_unique}"
        )

        print(
            f"Ky tu da co trong ChuHan: "
            f"{total_unique - len(new_chars)}"
        )

        print(
            f"Ky tu moi can chuan bi "
            f"cho HSK2: "
            f"{len(new_chars)}"
        )

        print()
        print(
            f"Thieu Pinyin: "
            f"{missing_pinyin}"
        )

        print(
            f"Thieu nghia Viet: "
            f"{missing_meaning}"
        )

        print()
        print("Da tao:")
        print(OUTPUT_FILE)

        print()
        print(
            "MaBaiHoc: CHUA GAN"
        )

        print(
            "MaBoThu/SoNet: CHUA BO SUNG"
        )

        print(
            "KHONG INSERT/UPDATE/DELETE SQL."
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()