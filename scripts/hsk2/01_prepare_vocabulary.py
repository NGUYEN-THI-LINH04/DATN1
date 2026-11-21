
from pathlib import Path
import csv
import os
import re
import pyodbc


# ==========================================
# 1. CAU HINH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "vocabulary_hsk2_review.csv"

HSK_LEVEL = 2


# ==========================================
# 2. KET NOI SQL SERVER
# ==========================================

def get_connection():
    connection_string = os.getenv("HSK2_DB_CONNECTION_STRING")

    if not connection_string:
        raise RuntimeError(
            "Chua cau hinh HSK2_DB_CONNECTION_STRING. "
            "Hay dung chuoi ket noi SQL Server hien tai cua du an."
        )

    return pyodbc.connect(connection_string, timeout=15)


# ==========================================
# 3. CHUAN HOA DU LIEU
# ==========================================

def clean_text(value):
    if value is None:
        return ""

    return re.sub(r"\s+", " ", str(value)).strip()


def match_key(hanzi, pinyin):
    return (
        clean_text(hanzi),
        clean_text(pinyin).casefold()
    )


def prepare_reference_meaning(value):
    """
    Chi lam sach khoang trang.
    Khong tu dong xoa nghia, luong tu
    hoac chon mot nghia duy nhat.
    """
    return clean_text(value)


# ==========================================
# 4. DOC DU LIEU TU SQL
# ==========================================

def load_hsk2_words(cursor):
    cursor.execute(
        """
        SELECT
            MaTuHSK,
            MaMucNoiBo,
            SoThuTuNguon,
            ChuHan,
            PhienAm,
            TuLoai,
            NghiaTiengVietThamChieu
        FROM dbo.TuVungHSKChuan
        WHERE MaCapDo = ?
        ORDER BY
            SoThuTuNguon,
            MaTuHSK
        """,
        HSK_LEVEL
    )

    return cursor.fetchall()


def load_existing_words(cursor):
    cursor.execute(
        """
        SELECT
            MaTuVung,
            ChuHan,
            PhienAm,
            NghiaTiengViet,
            TuLoai
        FROM dbo.TuVung
        """
    )

    return cursor.fetchall()


# ==========================================
# 5. DOI CHIEU VA XUAT CSV
# ==========================================

def main():
    print("=" * 55)
    print("CHUAN BI TU VUNG HSK2")
    print("CHE DO: CHI DOC SQL - KHONG INSERT/UPDATE/DELETE")
    print("=" * 55)

    with get_connection() as conn:
        cursor = conn.cursor()

        source_words = load_hsk2_words(cursor)
        existing_words = load_existing_words(cursor)

        existing_index = {}

        for word in existing_words:
            key = match_key(word.ChuHan, word.PhienAm)
            existing_index.setdefault(key, []).append(word)

        output_rows = []

        count_existing = 0
        count_missing = 0
        count_ambiguous = 0

        for word in source_words:
            hanzi = clean_text(word.ChuHan)
            pinyin = clean_text(word.PhienAm)
            key = match_key(hanzi, pinyin)

            matches = existing_index.get(key, [])

            if len(matches) == 1:
                status = "DA_CO"
                existing_id = matches[0].MaTuVung
                existing_meaning = clean_text(
                    matches[0].NghiaTiengViet
                )
                count_existing += 1

            elif len(matches) == 0:
                status = "CHUA_CO"
                existing_id = ""
                existing_meaning = ""
                count_missing += 1

            else:
                status = "CAN_KIEM_TRA_TRUNG"
                existing_id = ""
                existing_meaning = ""
                count_ambiguous += 1

            output_rows.append({
                "MaTuHSK": word.MaTuHSK,
                "MaMucNoiBo": word.MaMucNoiBo,
                "SoThuTuNguon": word.SoThuTuNguon,
                "ChuHan": hanzi,
                "PhienAm": pinyin,
                "TuLoaiNguon": clean_text(word.TuLoai),
                "NghiaThamChieu": prepare_reference_meaning(
                    word.NghiaTiengVietThamChieu
                ),
                "NghiaTiengVietDeXuat": existing_meaning,
                "MaTuVungDaCo": existing_id,
                "TrangThai": status,
                "DaKiemTraNghia": "CHUA"
            })

        fieldnames = [
            "MaTuHSK",
            "MaMucNoiBo",
            "SoThuTuNguon",
            "ChuHan",
            "PhienAm",
            "TuLoaiNguon",
            "NghiaThamChieu",
            "NghiaTiengVietDeXuat",
            "MaTuVungDaCo",
            "TrangThai",
            "DaKiemTraNghia"
        ]

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
            writer.writerows(output_rows)

        print(f"Tong tu HSK2: {len(source_words)}")
        print(f"Da co trong TuVung: {count_existing}")
        print(f"Chua co: {count_missing}")
        print(f"Can kiem tra trung: {count_ambiguous}")

        if len(source_words) != 772:
            print(
                "CANH BAO: So luong nguon khac 772. "
                "Can kiem tra truoc khi import."
            )

        print()
        print("Da xuat CSV:")
        print(OUTPUT_FILE)
        print()
        print("CHUA CO DU LIEU NAO BI GHI VAO SQL.")


if __name__ == "__main__":
    main()
