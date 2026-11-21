from pathlib import Path
import sys
import csv
import re
from collections import Counter


# =========================================================
# THU MUC GOC
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# FILE DA HOAN THIEN O BUOC 05g
#
# KHONG dung file 05h vi NghiaHocTapDeXuat
# cua 05h chi la ban thu nghiem.
# =========================================================
INPUT_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hsk1_4_vietnamese_source_complete.csv"
)


# =========================================================
# SO LUONG CHUAN HSK 1-4 TRONG PIPELINE HIEN TAI
# =========================================================
EXPECTED_COUNTS = {
    1: 500,
    2: 772,
    3: 973,
    4: 1000,
}

EXPECTED_TOTAL = sum(
    EXPECTED_COUNTS.values()
)


# =========================================================
# CAC COT BAT BUOC TRONG CSV
# =========================================================
REQUIRED_COLUMNS = {
    "ID",
    "WebNo",
    "CapDoHSK",
    "TuGoc",
    "TuChinh",
    "BienThe",
    "PinyinChuan",
    "PinyinGoc",
    "TuLoaiChuan",
    "MaMucTuCedict",
    "SoKetQuaCedict",
    "NghiaTiengViet",
    "TrangThaiDoiChieu",
    "NguonTuVung",
    "NguonNghiaViet",
    "TrangThaiNghiaViet",
    "CanKiemTraThuCong",
    "CanKiemTraNghia",
}


# =========================================================
# HAM TIEN ICH
# =========================================================
def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def nullable(value):
    value = clean(value)

    if value == "":
        return None

    return value


def parse_nullable_int(value, field_name, row_id):
    value = clean(value)

    if value == "":
        return None

    try:
        return int(value)

    except ValueError:
        raise RuntimeError(
            f"{row_id}: {field_name} khong phai so: {value}"
        )


# =========================================================
# PARSE DANH SACH MaMucTuCedict
#
# Vi du:
#
# 22337 | 75245
#
# ->
#
# [22337, 75245]
# =========================================================
def parse_dictionary_ids(value, row_id):
    value = clean(value)

    if not value:
        return []

    parts = re.split(
        r"\s*\|\s*",
        value,
    )

    result = []
    seen = set()

    for part in parts:
        part = clean(part)

        if not part:
            continue

        try:
            ma_muc_tu = int(part)

        except ValueError:
            raise RuntimeError(
                f"{row_id}: MaMucTuCedict khong hop le: {part}"
            )

        if ma_muc_tu not in seen:
            seen.add(ma_muc_tu)
            result.append(ma_muc_tu)

    return result


# =========================================================
# DOC VA KIEM TRA CSV
# =========================================================
def load_and_validate_csv():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Khong tim thay file:\n"
            f"{INPUT_FILE}\n\n"
            "Can co file tu buoc 05g."
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        fieldnames = set(
            reader.fieldnames or []
        )

        missing = (
            REQUIRED_COLUMNS
            - fieldnames
        )

        if missing:
            raise RuntimeError(
                "File CSV thieu cac cot:\n"
                + "\n".join(
                    sorted(missing)
                )
            )

        rows = list(reader)

    # -----------------------------------------------------
    # Tong so dong
    # -----------------------------------------------------
    if len(rows) != EXPECTED_TOTAL:
        raise RuntimeError(
            "Tong so dong CSV khong dung.\n"
            f"Mong doi: {EXPECTED_TOTAL}\n"
            f"Thuc te: {len(rows)}"
        )

    # -----------------------------------------------------
    # Validate tung dong
    # -----------------------------------------------------
    ids = set()

    counts = Counter()

    prepared = []

    for row in rows:

        row_id = clean(
            row.get("ID")
        )

        if not row_id:
            raise RuntimeError(
                "Co dong khong co ID."
            )

        if row_id in ids:
            raise RuntimeError(
                f"Trung ID: {row_id}"
            )

        ids.add(row_id)

        # ---------------------------------------------
        # Cap do
        # ---------------------------------------------
        try:
            level = int(
                clean(
                    row.get(
                        "CapDoHSK"
                    )
                )
            )

        except ValueError:
            raise RuntimeError(
                f"{row_id}: CapDoHSK khong hop le."
            )

        if level not in EXPECTED_COUNTS:
            raise RuntimeError(
                f"{row_id}: Chi cho phep HSK 1-4."
            )

        counts[level] += 1

        # ---------------------------------------------
        # Truong bat buoc
        # ---------------------------------------------
        tu_goc = clean(
            row.get("TuGoc")
        )

        chu_han = clean(
            row.get("TuChinh")
        )

        pinyin_nguon = clean(
            row.get("PinyinGoc")
        )

        pinyin_chuan = clean(
            row.get("PinyinChuan")
        )

        nghia_viet = clean(
            row.get(
                "NghiaTiengViet"
            )
        )

        if not tu_goc:
            raise RuntimeError(
                f"{row_id}: TuGoc rong."
            )

        if not chu_han:
            raise RuntimeError(
                f"{row_id}: TuChinh rong."
            )

        if not pinyin_chuan:
            raise RuntimeError(
                f"{row_id}: PinyinChuan rong."
            )

        if not pinyin_nguon:
            # Neu khong co rieng PinyinGoc,
            # dung PinyinChuan.
            pinyin_nguon = pinyin_chuan

        if not nghia_viet:
            raise RuntimeError(
                f"{row_id}: NghiaTiengViet rong."
            )

        # ---------------------------------------------
        # Kiem tra do dai theo schema SQL
        # ---------------------------------------------
        if len(row_id) > 32:
            raise RuntimeError(
                f"{row_id}: ID dai qua varchar(32)."
            )

        if len(tu_goc) > 200:
            raise RuntimeError(
                f"{row_id}: TuGoc dai qua nvarchar(200)."
            )

        if len(chu_han) > 100:
            raise RuntimeError(
                f"{row_id}: TuChinh dai qua nvarchar(100)."
            )

        bien_the = nullable(
            row.get("BienThe")
        )

        if (
            bien_the
            and len(bien_the) > 200
        ):
            raise RuntimeError(
                f"{row_id}: BienThe dai qua nvarchar(200)."
            )

        if len(pinyin_nguon) > 200:
            raise RuntimeError(
                f"{row_id}: PinyinGoc dai qua nvarchar(200)."
            )

        if len(pinyin_chuan) > 200:
            raise RuntimeError(
                f"{row_id}: PinyinChuan dai qua nvarchar(200)."
            )

        tu_loai = nullable(
            row.get(
                "TuLoaiChuan"
            )
        )

        if (
            tu_loai
            and len(tu_loai) > 100
        ):
            raise RuntimeError(
                f"{row_id}: TuLoaiChuan dai qua nvarchar(100)."
            )

        web_no = parse_nullable_int(
            row.get("WebNo"),
            "WebNo",
            row_id,
        )

        dictionary_ids = (
            parse_dictionary_ids(
                row.get(
                    "MaMucTuCedict"
                ),
                row_id,
            )
        )

        # ---------------------------------------------
        # SoKetQuaCedict phai khop so ID
        # ---------------------------------------------
        so_ket_qua_text = clean(
            row.get(
                "SoKetQuaCedict"
            )
        )

        if so_ket_qua_text:
            try:
                so_ket_qua = int(
                    so_ket_qua_text
                )

            except ValueError:
                raise RuntimeError(
                    f"{row_id}: SoKetQuaCedict khong hop le."
                )

            if (
                so_ket_qua
                != len(dictionary_ids)
            ):
                raise RuntimeError(
                    f"{row_id}: SoKetQuaCedict={so_ket_qua} "
                    f"nhung co {len(dictionary_ids)} MaMucTu."
                )

        prepared.append(
            {
                "id": row_id,
                "level": level,
                "web_no": web_no,
                "tu_goc": tu_goc,
                "chu_han": chu_han,
                "bien_the": bien_the,
                "pinyin_nguon": pinyin_nguon,
                "pinyin": pinyin_chuan,
                "tu_loai": tu_loai,
                "nghia": nghia_viet,
                "nguon_nghia":
                    clean(
                        row.get(
                            "NguonNghiaViet"
                        )
                    ),
                "trang_thai_doi_chieu":
                    clean(
                        row.get(
                            "TrangThaiDoiChieu"
                        )
                    ),
                "trang_thai_nghia":
                    clean(
                        row.get(
                            "TrangThaiNghiaViet"
                        )
                    ),
                "can_kiem_tra_nguon":
                    clean(
                        row.get(
                            "CanKiemTraThuCong"
                        )
                    ),
                "can_kiem_tra_nghia":
                    clean(
                        row.get(
                            "CanKiemTraNghia"
                        )
                    ),
                "dictionary_ids":
                    dictionary_ids,
            }
        )

    # -----------------------------------------------------
    # Dem tung cap
    # -----------------------------------------------------
    for level, expected in (
        EXPECTED_COUNTS.items()
    ):

        actual = counts[level]

        if actual != expected:
            raise RuntimeError(
                f"HSK {level}: mong doi {expected}, "
                f"thuc te {actual}."
            )

    return prepared, counts


# =========================================================
# TIM NGUON CVDICT
# =========================================================
def get_cvdict_source(cursor):

    cursor.execute(
        """
        SELECT
            MaNguon,
            Ten
        FROM dbo.NguonDuLieu
        WHERE Ten = ?
        """,
        "CVDICT",
    )

    rows = cursor.fetchall()

    if len(rows) != 1:
        raise RuntimeError(
            "Khong tim thay duy nhat 1 nguon CVDICT "
            "trong NguonDuLieu."
        )

    return rows[0].MaNguon


# =========================================================
# TIM NGUON CC-CEDICT
# =========================================================
def get_cedict_source(cursor):

    cursor.execute(
        """
        SELECT
            MaNguon,
            Ten
        FROM dbo.NguonDuLieu
        WHERE Ten = ?
        """,
        "CC-CEDICT",
    )

    rows = cursor.fetchall()

    if len(rows) != 1:
        raise RuntimeError(
            "Khong tim thay duy nhat 1 nguon CC-CEDICT."
        )

    return rows[0].MaNguon


# =========================================================
# TIM NGUON DANH SACH HSK
#
# Khong mac dinh MaNguon=1002 ngay.
# Tim bang Ten/LienKet/GhiChu truoc.
#
# 1002 chi dung lam fallback cho dung DB hien tai
# neu ban ghi do thuc su co noi dung HSK/GF0025.
# =========================================================
def get_hsk_source(cursor):

    cursor.execute(
        """
        SELECT
            MaNguon,
            Ten,
            LienKetNguon,
            GhiChu
        FROM dbo.NguonDuLieu
        WHERE
            Ten LIKE N'%GF0025%'
            OR Ten LIKE N'%HSK%'
            OR LienKetNguon LIKE N'%GF0025%'
            OR GhiChu LIKE N'%GF0025%'
        ORDER BY MaNguon
        """
    )

    candidates = cursor.fetchall()

    # -----------------------------------------------------
    # Uu tien candidate co GF0025
    # -----------------------------------------------------
    strong = []

    for row in candidates:

        combined = " ".join(
            [
                clean(row.Ten),
                clean(row.LienKetNguon),
                clean(row.GhiChu),
            ]
        ).lower()

        if "gf0025" in combined:
            strong.append(row)

    if len(strong) == 1:
        return strong[0].MaNguon

    # -----------------------------------------------------
    # Neu chi co 1 candidate HSK
    # -----------------------------------------------------
    if len(candidates) == 1:
        return candidates[0].MaNguon

    # -----------------------------------------------------
    # Fallback cho DB hien tai:
    # output buoc truoc cua ban cho thay MaNguon HSK=1002.
    #
    # Van kiem tra noi dung truoc khi dung.
    # -----------------------------------------------------
    for row in candidates:

        if row.MaNguon != 1002:
            continue

        combined = " ".join(
            [
                clean(row.Ten),
                clean(row.LienKetNguon),
                clean(row.GhiChu),
            ]
        ).lower()

        if (
            "hsk" in combined
            or "gf0025" in combined
        ):
            return row.MaNguon

    # -----------------------------------------------------
    # Khong tu chon neu mo ho
    # -----------------------------------------------------
    details = []

    for row in candidates:

        details.append(
            f"MaNguon={row.MaNguon}, Ten={row.Ten}"
        )

    raise RuntimeError(
        "Khong xac dinh duoc duy nhat nguon HSK.\n"
        + "\n".join(details)
    )


# =========================================================
# KIEM TRA CapDoHSK 1-4 TON TAI
# =========================================================
def validate_hsk_levels(cursor):

    cursor.execute(
        """
        SELECT
            MaCapDo,
            MaKyHieu
        FROM dbo.CapDoHSK
        WHERE MaCapDo IN (1, 2, 3, 4)
        ORDER BY MaCapDo
        """
    )

    rows = cursor.fetchall()

    found = {
        row.MaCapDo
        for row in rows
    }

    if found != {1, 2, 3, 4}:
        raise RuntimeError(
            "CapDoHSK chua co du MaCapDo 1,2,3,4."
        )


# =========================================================
# KIEM TRA CAC MaMucTu THUC SU TON TAI
# VA THUOC NGUON CC-CEDICT
# =========================================================
def validate_dictionary_ids(
    cursor,
    prepared_rows,
    ma_nguon_cedict,
):

    all_ids = sorted(
        {
            ma_muc_tu
            for row in prepared_rows
            for ma_muc_tu
            in row["dictionary_ids"]
        }
    )

    print(
        "So MaMucTu CC-CEDICT can kiem tra: "
        f"{len(all_ids)}"
    )

    if not all_ids:
        raise RuntimeError(
            "Khong co MaMucTu nao de doi chieu."
        )

    found = set()

    wrong_source = []

    CHUNK_SIZE = 500

    for start in range(
        0,
        len(all_ids),
        CHUNK_SIZE,
    ):

        chunk = all_ids[
            start:
            start + CHUNK_SIZE
        ]

        placeholders = ",".join(
            "?"
            for _ in chunk
        )

        sql = f"""
            SELECT
                MaMucTu,
                MaNguon
            FROM dbo.MucTuDien
            WHERE MaMucTu IN ({placeholders})
        """

        cursor.execute(
            sql,
            chunk,
        )

        for db_row in cursor.fetchall():

            found.add(
                db_row.MaMucTu
            )

            if (
                db_row.MaNguon
                != ma_nguon_cedict
            ):
                wrong_source.append(
                    (
                        db_row.MaMucTu,
                        db_row.MaNguon,
                    )
                )

    missing = (
        set(all_ids)
        - found
    )

    if missing:
        sample = sorted(
            missing
        )[:20]

        raise RuntimeError(
            "Co MaMucTu khong ton tai trong MucTuDien:\n"
            + ", ".join(
                str(x)
                for x in sample
            )
        )

    if wrong_source:
        sample = wrong_source[:20]

        raise RuntimeError(
            "Co MaMucTu khong thuoc nguon CC-CEDICT:\n"
            + "\n".join(
                f"{x[0]} -> MaNguon {x[1]}"
                for x in sample
            )
        )

    return len(all_ids)


# =========================================================
# TAO GHI CHU
# =========================================================
def build_note(row):

    notes = [
        "Nhap tu pipeline ETL HSK 1-4.",
    ]

    if row[
        "trang_thai_doi_chieu"
    ]:
        notes.append(
            "DoiChieu="
            + row[
                "trang_thai_doi_chieu"
            ]
        )

    if row[
        "trang_thai_nghia"
    ]:
        notes.append(
            "NghiaViet="
            + row[
                "trang_thai_nghia"
            ]
        )

    if (
        row[
            "can_kiem_tra_nguon"
        ] == "1"
    ):
        notes.append(
            "CanKiemTraNguon=1"
        )

    if (
        row[
            "can_kiem_tra_nghia"
        ] == "1"
    ):
        notes.append(
            "CanKiemTraNghia=1"
        )

    note = "; ".join(
        notes
    )

    if len(note) > 2000:
        raise RuntimeError(
            f"{row['id']}: GhiChu vuot 2000 ky tu."
        )

    return note


# =========================================================
# IMPORT / UPDATE
#
# Script co the chay lai:
# - Neu MaMucNoiBo chua co -> INSERT
# - Neu da co -> UPDATE
# - Mapping MucTuDien duoc tao lai
#
# Toan bo nam trong 1 transaction.
# Neu loi -> ROLLBACK.
# =========================================================
def import_rows(
    cursor,
    prepared_rows,
    ma_nguon_hsk,
    ma_nguon_cvdict,
):

    inserted = 0
    updated = 0
    mapping_count = 0
    manual_meaning_count = 0

    for index, row in enumerate(
        prepared_rows,
        start=1,
    ):

        # -------------------------------------------------
        # Xac dinh nguon nghia
        # -------------------------------------------------
        source_name = (
            row["nguon_nghia"]
            .strip()
        )

        if source_name == "CVDICT":

            ma_nguon_nghia = (
                ma_nguon_cvdict
            )

        elif source_name == "":

            # 9 muc bo sung thu cong
            ma_nguon_nghia = None

            manual_meaning_count += 1

        else:

            raise RuntimeError(
                f"{row['id']}: "
                f"NguonNghiaViet khong duoc ho tro: "
                f"{source_name}"
            )

        note = build_note(row)

        # -------------------------------------------------
        # Tim theo MaMucNoiBo
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT MaTuHSK
            FROM dbo.TuVungHSKChuan
            WHERE MaMucNoiBo = ?
            """,
            row["id"],
        )

        existing = cursor.fetchone()

        if existing:

            ma_tu_hsk = (
                existing.MaTuHSK
            )

            cursor.execute(
                """
                UPDATE dbo.TuVungHSKChuan
                SET
                    MaCapDo = ?,
                    SoThuTuNguon = ?,
                    TuGoc = ?,
                    ChuHan = ?,
                    BienThe = ?,
                    PhienAmNguon = ?,
                    PhienAm = ?,
                    TuLoai = ?,
                    NghiaTiengVietThamChieu = ?,
                    MaNguonDanhSach = ?,
                    MaNguonNghiaViet = ?,
                    DaKiemTraNguon = 0,
                    GhiChu = ?,
                    NgayCapNhat = SYSDATETIME()
                WHERE MaTuHSK = ?
                """,
                row["level"],
                row["web_no"],
                row["tu_goc"],
                row["chu_han"],
                row["bien_the"],
                row["pinyin_nguon"],
                row["pinyin"],
                row["tu_loai"],
                row["nghia"],
                ma_nguon_hsk,
                ma_nguon_nghia,
                note,
                ma_tu_hsk,
            )

            # Xoa mapping cu de tao lai
            cursor.execute(
                """
                DELETE FROM dbo.TuVungHSKMucTuDien
                WHERE MaTuHSK = ?
                """,
                ma_tu_hsk,
            )

            updated += 1

        else:

            cursor.execute(
                """
                INSERT INTO dbo.TuVungHSKChuan
                (
                    MaMucNoiBo,
                    MaCapDo,
                    SoThuTuNguon,
                    TuGoc,
                    ChuHan,
                    BienThe,
                    PhienAmNguon,
                    PhienAm,
                    TuLoai,
                    NghiaTiengVietThamChieu,
                    MaNguonDanhSach,
                    MaNguonNghiaViet,
                    DaKiemTraNguon,
                    GhiChu
                )
                OUTPUT INSERTED.MaTuHSK
                VALUES
                (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?,
                    0,
                    ?
                )
                """,
                row["id"],
                row["level"],
                row["web_no"],
                row["tu_goc"],
                row["chu_han"],
                row["bien_the"],
                row["pinyin_nguon"],
                row["pinyin"],
                row["tu_loai"],
                row["nghia"],
                ma_nguon_hsk,
                ma_nguon_nghia,
                note,
            )

            result = cursor.fetchone()

            if not result:
                raise RuntimeError(
                    f"{row['id']}: Khong lay duoc MaTuHSK sau INSERT."
                )

            ma_tu_hsk = (
                result[0]
            )

            inserted += 1

        # -------------------------------------------------
        # Tao mapping HSK <-> MucTuDien
        # -------------------------------------------------
        for order, ma_muc_tu in enumerate(
            row["dictionary_ids"],
            start=1,
        ):

            cursor.execute(
                """
                INSERT INTO dbo.TuVungHSKMucTuDien
                (
                    MaTuHSK,
                    MaMucTu,
                    ThuTu
                )
                VALUES (?, ?, ?)
                """,
                ma_tu_hsk,
                ma_muc_tu,
                order,
            )

            mapping_count += 1

        if index % 500 == 0:
            print(
                f"Da xu ly {index}/{len(prepared_rows)} muc..."
            )

    return (
        inserted,
        updated,
        mapping_count,
        manual_meaning_count,
    )


# =========================================================
# KIEM TRA SAU IMPORT
# =========================================================
def verify_database(cursor):

    cursor.execute(
        """
        SELECT
            MaCapDo,
            COUNT(*) AS SoLuong
        FROM dbo.TuVungHSKChuan
        WHERE MaCapDo IN (1, 2, 3, 4)
        GROUP BY MaCapDo
        ORDER BY MaCapDo
        """
    )

    counts = {
        row.MaCapDo: row.SoLuong
        for row in cursor.fetchall()
    }

    for level, expected in (
        EXPECTED_COUNTS.items()
    ):

        actual = counts.get(
            level,
            0,
        )

        if actual != expected:

            raise RuntimeError(
                "Kiem tra DB that bai: "
                f"HSK {level} co {actual}, "
                f"mong doi {expected}."
            )

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM dbo.TuVungHSKChuan
        WHERE MaCapDo IN (1,2,3,4)
        """
    )

    total = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM dbo.TuVungHSKMucTuDien
        """
    )

    mappings = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM dbo.TuVungHSKChuan
        WHERE MaCapDo IN (1,2,3,4)
          AND MaNguonNghiaViet IS NULL
        """
    )

    no_vietnamese_source = (
        cursor.fetchone()[0]
    )

    return (
        counts,
        total,
        mappings,
        no_vietnamese_source,
    )


# =========================================================
# IN MOT SO TU DA NGHIA / KHAC TU LOAI
# DE CHUNG MINH DU LIEU KHONG BI GOP
# =========================================================
def show_special_samples(cursor):

    print()
    print("-" * 72)
    print(
        "KIEM TRA CAC TU KHONG DUOC GOP NHAM"
    )
    print("-" * 72)

    cursor.execute(
        """
        SELECT
            MaMucNoiBo,
            MaCapDo,
            ChuHan,
            PhienAm,
            TuLoai
        FROM dbo.TuVungHSKChuan
        WHERE ChuHan IN
        (
            N'白',
            N'把',
            N'会'
        )
        ORDER BY
            ChuHan,
            MaCapDo,
            MaMucNoiBo
        """
    )

    rows = cursor.fetchall()

    for row in rows:

        print(
            f"{row.MaMucNoiBo}"
            f" | HSK {row.MaCapDo}"
            f" | {row.ChuHan}"
            f" | {row.PhienAm}"
            f" | {row.TuLoai or ''}"
        )


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 72)
        print(
            "IMPORT KHO THAM CHIEU HSK 1-4"
        )
        print("=" * 72)

        # -------------------------------------------------
        # 1. DOC VA KIEM TRA CSV TRUOC
        # -------------------------------------------------
        print()
        print(
            "Dang kiem tra file CSV..."
        )

        (
            prepared_rows,
            csv_counts,
        ) = load_and_validate_csv()

        print(
            "CSV hop le."
        )

        for level in range(
            1,
            5,
        ):

            print(
                f"HSK {level}: "
                f"{csv_counts[level]}"
            )

        print(
            f"Tong: {len(prepared_rows)}"
        )

        # -------------------------------------------------
        # 2. MO KET NOI
        # -------------------------------------------------
        conn = get_connection()

        # Tu quan ly transaction
        conn.autocommit = False

        cursor = conn.cursor()

        # -------------------------------------------------
        # 3. KIEM TRA SCHEMA
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                OBJECT_ID(N'dbo.TuVungHSKChuan', N'U'),
                OBJECT_ID(N'dbo.TuVungHSKMucTuDien', N'U')
            """
        )

        schema_check = (
            cursor.fetchone()
        )

        if (
            not schema_check[0]
            or not schema_check[1]
        ):
            raise RuntimeError(
                "Chua co du 2 bang "
                "TuVungHSKChuan va TuVungHSKMucTuDien."
            )

        validate_hsk_levels(
            cursor
        )

        # -------------------------------------------------
        # 4. LAY NGUON
        # -------------------------------------------------
        ma_nguon_hsk = (
            get_hsk_source(
                cursor
            )
        )

        ma_nguon_cvdict = (
            get_cvdict_source(
                cursor
            )
        )

        ma_nguon_cedict = (
            get_cedict_source(
                cursor
            )
        )

        print()
        print(
            "MaNguon danh sach HSK: "
            f"{ma_nguon_hsk}"
        )

        print(
            "MaNguon CVDICT: "
            f"{ma_nguon_cvdict}"
        )

        print(
            "MaNguon CC-CEDICT: "
            f"{ma_nguon_cedict}"
        )

        # -------------------------------------------------
        # 5. KIEM TRA CAC MaMucTu CEDICT
        # -------------------------------------------------
        unique_dictionary_count = (
            validate_dictionary_ids(
                cursor,
                prepared_rows,
                ma_nguon_cedict,
            )
        )

        print(
            "Tat ca MaMucTu deu ton tai "
            "va thuoc CC-CEDICT."
        )

        # -------------------------------------------------
        # 6. IMPORT
        # -------------------------------------------------
        print()
        print(
            "Dang import vao TuVungHSKChuan..."
        )

        (
            inserted,
            updated,
            mapping_count,
            manual_meaning_count,
        ) = import_rows(
            cursor,
            prepared_rows,
            ma_nguon_hsk,
            ma_nguon_cvdict,
        )

        # -------------------------------------------------
        # 7. KIEM TRA TRUOC COMMIT
        # -------------------------------------------------
        (
            db_counts,
            db_total,
            db_mappings,
            db_no_vietnamese_source,
        ) = verify_database(
            cursor
        )

        if db_total != EXPECTED_TOTAL:
            raise RuntimeError(
                f"DB co {db_total} muc HSK 1-4, "
                f"khong dung {EXPECTED_TOTAL}."
            )

        # -------------------------------------------------
        # 8. COMMIT
        # -------------------------------------------------
        conn.commit()

        # -------------------------------------------------
        # 9. KET QUA
        # -------------------------------------------------
        print()
        print("=" * 72)
        print("KET QUA")
        print("=" * 72)

        print(
            f"INSERT moi: {inserted}"
        )

        print(
            f"UPDATE: {updated}"
        )

        print()

        for level in range(
            1,
            5,
        ):

            print(
                f"HSK {level}: "
                f"{db_counts[level]}"
            )

        print()

        print(
            "Tong HSK 1-4: "
            f"{db_total}"
        )

        print(
            "Tong mapping HSK -> MucTuDien: "
            f"{db_mappings}"
        )

        print(
            "So MaMucTu CC-CEDICT duy nhat: "
            f"{unique_dictionary_count}"
        )

        print(
            "Nghia bo sung khong co "
            "nguon CVDICT: "
            f"{db_no_vietnamese_source}"
        )

        print()

        print(
            "DaKiemTraNguon van = 0."
        )

        print(
            "CHUA INSERT VAO dbo.TuVung."
        )

        show_special_samples(
            cursor
        )

        print()
        print("=" * 72)
        print("HOAN TAT")
        print("=" * 72)

        cursor.close()

    except Exception as e:

        if conn:
            conn.rollback()

        print()
        print("=" * 72)
        print("IMPORT THAT BAI - DA ROLLBACK")
        print("=" * 72)

        print(
            "Loi:",
            e,
        )

        print()
        print(
            "Khong co du lieu dang do "
            "duoc giu lai neu transaction that bai."
        )

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()