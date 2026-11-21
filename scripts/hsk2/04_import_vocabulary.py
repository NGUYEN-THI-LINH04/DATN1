from pathlib import Path
import csv
import os
import re
import sys
import pyodbc


# ============================================================
# 1. CAU HINH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_DIR / "vocabulary_hsk2_meaning_draft.csv"

RESULT_FILE = DATA_DIR / "vocabulary_hsk2_import_result.csv"

EXPECTED_TOTAL = 772

# Mac dinh CHI XEM THU.
# Chi khi bien moi truong = YES moi ghi vao SQL.
COMMIT_MODE = (
    os.getenv("HSK2_IMPORT_COMMIT", "")
    .strip()
    .upper()
    == "YES"
)


# ============================================================
# 2. KET NOI SQL SERVER
# ============================================================

def get_connection():
    connection_string = os.getenv(
        "HSK2_DB_CONNECTION_STRING",
        ""
    ).strip()

    if not connection_string:
        raise RuntimeError(
            "Chua co bien moi truong "
            "HSK2_DB_CONNECTION_STRING."
        )

    return pyodbc.connect(
        connection_string,
        timeout=15,
        autocommit=False
    )


# ============================================================
# 3. CHUAN HOA DU LIEU
# ============================================================

def clean_text(value):
    if value is None:
        return ""

    value = str(value).replace("\u00a0", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def match_key(hanzi, pinyin):
    return (
        clean_text(hanzi),
        clean_text(pinyin).casefold()
    )


def clean_meaning(value):
    """
    Lam sach nhe phan nghia truoc khi import.

    - Khong tu dong rut gon nghia.
    - Khong chon nghia dau tien.
    - Chi loai cac doan ghi chu LT:...
    - Giu lai cac nghia tham chieu con lai.
    """

    text = clean_text(value)

    if not text:
        return ""

    # Tach theo dau /
    parts = re.split(r"\s*/\s*", text)

    cleaned_parts = []

    for part in parts:
        part = clean_text(part)

        if not part:
            continue

        # Neu co LT: trong phan nay,
        # chi giu noi dung truoc LT:
        upper_part = part.upper()

        position = upper_part.find("LT:")

        if position >= 0:
            before_lt = clean_text(
                part[:position]
            )

            if before_lt:
                cleaned_parts.append(before_lt)

            continue

        cleaned_parts.append(part)

    # Loai trung lap
    unique_parts = []
    seen = set()

    for part in cleaned_parts:
        key = part.casefold()

        if key not in seen:
            seen.add(key)
            unique_parts.append(part)

    result = " / ".join(unique_parts)

    result = re.sub(
        r"\s+([,.;:])",
        r"\1",
        result
    )

    return clean_text(result)


# ============================================================
# 4. DOC CSV
# ============================================================

def read_source_rows():
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

        required_columns = {
            "MaTuHSK",
            "MaMucNoiBo",
            "ChuHan",
            "PhienAm",
            "TuLoaiNguon",
            "NghiaThamChieu",
            "NghiaTiengVietDeXuat",
            "MaTuVungDaCo",
            "TrangThai",
        }

        actual_columns = set(
            reader.fieldnames or []
        )

        missing = (
            required_columns
            - actual_columns
        )

        if missing:
            raise ValueError(
                "File CSV thieu cot: "
                + ", ".join(sorted(missing))
            )

        rows = list(reader)

    if len(rows) != EXPECTED_TOTAL:
        raise ValueError(
            f"Du kien {EXPECTED_TOTAL} dong, "
            f"nhung file co {len(rows)} dong."
        )

    return rows


# ============================================================
# 5. KIEM TRA DO DAI THEO SQL
# ============================================================

def validate_lengths(row):
    """
    TuVung:
    ChuHan            nvarchar(100)
    PhienAm           nvarchar(200)
    NghiaTiengViet    nvarchar(2000)
    TuLoai            nvarchar(100)

    SQL Server sys.columns tra max_length theo byte,
    nen nvarchar(200) => 100 ky tu.
    """

    hanzi = row["ChuHan"]
    pinyin = row["PhienAm"]
    meaning = row["NghiaTiengViet"]
    word_type = row["TuLoai"]

    errors = []

    if len(hanzi) > 100:
        errors.append(
            f"ChuHan qua dai ({len(hanzi)})"
        )

    if len(pinyin) > 200:
        errors.append(
            f"PhienAm qua dai ({len(pinyin)})"
        )

    if len(meaning) > 2000:
        errors.append(
            f"NghiaTiengViet qua dai "
            f"({len(meaning)})"
        )

    if len(word_type) > 100:
        errors.append(
            f"TuLoai qua dai ({len(word_type)})"
        )

    return errors


# ============================================================
# 6. DOC TU VUNG HIEN TAI TRONG SQL
# ============================================================

def load_existing_vocabulary(cursor):
    cursor.execute("""
        SELECT
            MaTuVung,
            ChuHan,
            PhienAm,
            NghiaTiengViet,
            TuLoai,
            DaDuyet
        FROM dbo.TuVung
        ORDER BY MaTuVung;
    """)

    index = {}

    for row in cursor.fetchall():
        key = match_key(
            row.ChuHan,
            row.PhienAm
        )

        index.setdefault(
            key,
            []
        ).append({
            "MaTuVung": row.MaTuVung,
            "ChuHan": row.ChuHan,
            "PhienAm": row.PhienAm,
            "NghiaTiengViet":
                row.NghiaTiengViet,
            "TuLoai": row.TuLoai,
            "DaDuyet": row.DaDuyet,
        })

    return index


# ============================================================
# 7. CHUAN BI 772 TU
# ============================================================

def prepare_rows(source_rows):
    prepared = []

    seen_codes = set()

    for source in source_rows:

        code = clean_text(
            source["MaMucNoiBo"]
        )

        if not re.fullmatch(
            r"L2-\d+",
            code
        ):
            raise ValueError(
                f"MaMucNoiBo khong hop le: "
                f"{code}"
            )

        if code in seen_codes:
            raise ValueError(
                f"Trung MaMucNoiBo: {code}"
            )

        seen_codes.add(code)

        hanzi = clean_text(
            source["ChuHan"]
        )

        pinyin = clean_text(
            source["PhienAm"]
        )

        word_type = clean_text(
            source["TuLoaiNguon"]
        )

        proposed_meaning = clean_text(
            source["NghiaTiengVietDeXuat"]
        )

        reference_meaning = clean_text(
            source["NghiaThamChieu"]
        )

        # Uu tien nghia da xu ly tu buoc 2/3.
        # Neu cot de xuat rong moi dung nghia tham chieu.
        meaning_source = (
            proposed_meaning
            if proposed_meaning
            else reference_meaning
        )

        meaning = clean_meaning(
            meaning_source
        )

        if not hanzi:
            raise ValueError(
                f"{code}: Thieu ChuHan"
            )

        if not pinyin:
            raise ValueError(
                f"{code}: Thieu PhienAm"
            )

        if not meaning:
            raise ValueError(
                f"{code}: Thieu NghiaTiengViet"
            )

        row = {
            "MaTuHSK": clean_text(
                source["MaTuHSK"]
            ),
            "MaMucNoiBo": code,
            "ChuHan": hanzi,
            "PhienAm": pinyin,
            "NghiaTiengViet": meaning,
            "TuLoai": word_type,
            "TrangThaiNguon": clean_text(
                source["TrangThai"]
            ),
        }

        length_errors = (
            validate_lengths(row)
        )

        if length_errors:
            raise ValueError(
                f"{code} - {hanzi}: "
                + "; ".join(length_errors)
            )

        prepared.append(row)

    return prepared


# ============================================================
# 8. DOI CHIEU VOI SQL
# ============================================================

def compare_with_database(
    prepared_rows,
    existing_index
):
    to_insert = []
    existing = []

    ambiguous = []

    for row in prepared_rows:

        key = match_key(
            row["ChuHan"],
            row["PhienAm"]
        )

        matches = existing_index.get(
            key,
            []
        )

        if len(matches) == 0:
            to_insert.append(row)

        elif len(matches) == 1:
            item = dict(row)

            item["MaTuVung"] = (
                matches[0]["MaTuVung"]
            )

            existing.append(item)

        else:
            ambiguous.append({
                "row": row,
                "matches": matches
            })

    return (
        to_insert,
        existing,
        ambiguous
    )


# ============================================================
# 9. INSERT
# ============================================================

def insert_one(cursor, row):
    """
    Chi insert cac cot can thiet.

    Khong insert MaTuVung:
    -> SQL tu tang.

    Khong insert NgayTao:
    -> default sysutcdatetime().

    DaDuyet = 0:
    -> du lieu moi chua duoc kiem duyet.
    """

    cursor.execute("""
        INSERT INTO dbo.TuVung
        (
            ChuHan,
            ChuPhonThe,
            PhienAm,
            NghiaTiengViet,
            TuLoai,
            ViDuTiengTrung,
            ViDuTiengViet,
            MaAmThanh,
            MaNguon,
            DaDuyet,
            MaQuanTriVienCapNhat,
            NgayCapNhat
        )
        OUTPUT INSERTED.MaTuVung
        VALUES
        (
            ?,
            NULL,
            ?,
            ?,
            ?,
            NULL,
            NULL,
            NULL,
            NULL,
            0,
            NULL,
            NULL
        );
    """,
        row["ChuHan"],
        row["PhienAm"],
        row["NghiaTiengViet"],
        row["TuLoai"] or None
    )

    inserted = cursor.fetchone()

    if inserted is None:
        raise RuntimeError(
            "INSERT thanh cong nhung "
            "khong lay duoc MaTuVung."
        )

    return int(inserted[0])


# ============================================================
# 10. XUAT KET QUA MAPPING
# ============================================================

RESULT_FIELDS = [
    "MaTuHSK",
    "MaMucNoiBo",
    "ChuHan",
    "PhienAm",
    "NghiaTiengViet",
    "TuLoai",
    "MaTuVung",
    "HanhDong",
]


def write_result(rows):
    with RESULT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=RESULT_FIELDS,
            extrasaction="ignore"
        )

        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# 11. MAIN
# ============================================================

def main():
    print("=" * 66)
    print("BUOC 4 - IMPORT TU VUNG HSK2 VAO SQL SERVER")
    print("=" * 66)

    if COMMIT_MODE:
        print(
            "CHE DO: GHI DU LIEU VAO SQL"
        )
    else:
        print(
            "CHE DO: PREVIEW - KHONG GHI SQL"
        )

    print("=" * 66)

    source_rows = read_source_rows()

    prepared_rows = prepare_rows(
        source_rows
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        existing_index = (
            load_existing_vocabulary(
                cursor
            )
        )

        (
            to_insert,
            already_exists,
            ambiguous
        ) = compare_with_database(
            prepared_rows,
            existing_index
        )

        print()
        print(
            f"Tong tu HSK2: "
            f"{len(prepared_rows)}"
        )

        print(
            f"Da ton tai trong TuVung: "
            f"{len(already_exists)}"
        )

        print(
            f"Can INSERT moi: "
            f"{len(to_insert)}"
        )

        print(
            f"Trung mo ho: "
            f"{len(ambiguous)}"
        )

        # Neu 1 tu trung nhieu dong
        # thi dung ngay.
        if ambiguous:
            print()
            print(
                "PHAT HIEN TU TRUNG MO HO."
            )

            for item in ambiguous[:20]:
                row = item["row"]

                print(
                    f"- {row['MaMucNoiBo']} "
                    f"{row['ChuHan']} "
                    f"{row['PhienAm']} "
                    f"=> {len(item['matches'])} "
                    f"dong trong TuVung"
                )

            raise RuntimeError(
                "Dung import vi co du lieu "
                "trung mo ho."
            )

        # ====================================================
        # PREVIEW
        # ====================================================

        if not COMMIT_MODE:
            connection.rollback()

            print()
            print(
                "PREVIEW THANH CONG."
            )

            print(
                "CHUA CO DU LIEU NAO "
                "DUOC GHI VAO SQL."
            )

            print()
            print(
                "Neu cac so lieu tren dung, "
                "chay lai voi:"
            )

            print()
            print(
                '$env:HSK2_IMPORT_COMMIT = "YES"'
            )

            print(
                "python "
                "scripts\\hsk2\\"
                "04_import_vocabulary.py"
            )

            return

        # ====================================================
        # COMMIT
        # ====================================================

        result_rows = []

        # Truoc het ghi mapping 14 tu
        # da ton tai.
        for row in already_exists:

            result_rows.append({
                "MaTuHSK":
                    row["MaTuHSK"],
                "MaMucNoiBo":
                    row["MaMucNoiBo"],
                "ChuHan":
                    row["ChuHan"],
                "PhienAm":
                    row["PhienAm"],
                "NghiaTiengViet":
                    row["NghiaTiengViet"],
                "TuLoai":
                    row["TuLoai"],
                "MaTuVung":
                    row["MaTuVung"],
                "HanhDong":
                    "DA_CO"
            })

        inserted_count = 0

        for index, row in enumerate(
            to_insert,
            start=1
        ):
            ma_tu_vung = insert_one(
                cursor,
                row
            )

            inserted_count += 1

            result_rows.append({
                "MaTuHSK":
                    row["MaTuHSK"],
                "MaMucNoiBo":
                    row["MaMucNoiBo"],
                "ChuHan":
                    row["ChuHan"],
                "PhienAm":
                    row["PhienAm"],
                "NghiaTiengViet":
                    row["NghiaTiengViet"],
                "TuLoai":
                    row["TuLoai"],
                "MaTuVung":
                    ma_tu_vung,
                "HanhDong":
                    "INSERT_MOI"
            })

            if (
                index % 100 == 0
                or index == len(to_insert)
            ):
                print(
                    f"Da chuan bi INSERT: "
                    f"{index}/"
                    f"{len(to_insert)}"
                )

        # Kiem tra mapping cuoi
        if len(result_rows) != EXPECTED_TOTAL:
            raise RuntimeError(
                "Mapping sau import khong du "
                "772 tu. Tu dong rollback."
            )

        connection.commit()

        # Sau khi commit moi ghi file ket qua.
        result_rows.sort(
            key=lambda x: int(
                x["MaTuHSK"]
            )
        )

        write_result(result_rows)

        print()
        print("=" * 66)
        print("IMPORT HSK2 THANH CONG")
        print("=" * 66)

        print(
            f"Da co san: "
            f"{len(already_exists)}"
        )

        print(
            f"Da INSERT moi: "
            f"{inserted_count}"
        )

        print(
            f"Tong mapping HSK2: "
            f"{len(result_rows)}"
        )

        print()
        print(
            "Tat ca tu INSERT moi co "
            "DaDuyet = 0."
        )

        print()
        print(
            "File mapping:"
        )

        print(RESULT_FILE)

    except Exception:
        connection.rollback()

        print()
        print(
            "CO LOI - DA ROLLBACK "
            "TRANSACTION."
        )

        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()