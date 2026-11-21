from pathlib import Path
import csv
import sys
from contextlib import closing


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# FILE REVIEW
# =========================================================
REVIEW_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "review"
    / "hsk1_501_vocab_review.csv"
)

EXPECTED_ROWS = 501


# =========================================================
# HELPERS
# =========================================================
def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def fail(message):
    raise RuntimeError(message)


def print_mismatches(title, items, limit=20):

    if not items:
        return

    print()
    print("-" * 110)
    print(title)
    print("-" * 110)

    for item in items[:limit]:
        print(item)

    if len(items) > limit:
        print(
            f"... con {len(items) - limit} loi "
            "khong hien thi."
        )


# =========================================================
# DOC FILE REVIEW
# =========================================================
def load_review_file():

    if not REVIEW_FILE.exists():
        fail(
            "Khong tim thay file review:\n"
            f"{REVIEW_FILE}"
        )

    with open(
        REVIEW_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        fieldnames = reader.fieldnames

        if not fieldnames:
            fail(
                "Khong doc duoc header CSV."
            )

        rows = list(reader)

    required_columns = {
        "SoThuTuBai",
        "ThuTuTrongBai",
        "MaTuVung",
        "ChuHan",
        "PhienAm",
        "TuLoaiNguon",
        "NghiaNguon",
        "MaNguon",
        "TuLoaiHocTap",
        "NghiaHocTap",
        "GhiChuKiemDuyet",
        "DaKiemDuyet",
    }

    missing_columns = (
        required_columns
        - set(fieldnames)
    )

    if missing_columns:
        fail(
            "File review thieu cot:\n"
            + ", ".join(
                sorted(missing_columns)
            )
        )

    if len(rows) != EXPECTED_ROWS:
        fail(
            "File review phai co dung 501 dong. "
            f"Thuc te: {len(rows)}"
        )

    # Tat ca phai da review
    not_reviewed = [
        row
        for row in rows
        if clean(
            row["DaKiemDuyet"]
        ) != "1"
    ]

    if not_reviewed:
        fail(
            "File review van con "
            f"{len(not_reviewed)} dong "
            "DaKiemDuyet != 1."
        )

    # MaTuVung phai hop le
    ids = []

    for row in rows:

        vocab_id = clean(
            row["MaTuVung"]
        )

        if not vocab_id.isdigit():
            fail(
                "MaTuVung khong hop le: "
                f"{vocab_id}"
            )

        ids.append(
            int(vocab_id)
        )

    if len(set(ids)) != EXPECTED_ROWS:
        fail(
            "501 dong review khong co "
            "501 MaTuVung duy nhat."
        )

    return rows, ids


# =========================================================
# KIEM TRA SCHEMA DATABASE
# =========================================================
def check_database_schema(cursor):

    required_columns = {
        "MaTuVung",
        "ChuHan",
        "PhienAm",
        "NghiaTiengViet",
        "TuLoai",
        "MaNguon",
        "DaDuyet",
    }

    cursor.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = 'TuVung';
        """
    )

    actual_columns = {
        row[0]
        for row in cursor.fetchall()
    }

    missing = (
        required_columns
        - actual_columns
    )

    if missing:
        fail(
            "Bang dbo.TuVung thieu cot:\n"
            + ", ".join(
                sorted(missing)
            )
        )

    return actual_columns


# =========================================================
# LAY 501 TU TU DATABASE
# =========================================================
def load_database_rows(cursor, vocab_ids):

    placeholders = ",".join(
        "?"
        for _ in vocab_ids
    )

    sql = f"""
        SELECT
            MaTuVung,
            ChuHan,
            PhienAm,
            NghiaTiengViet,
            TuLoai,
            MaNguon,
            DaDuyet
        FROM dbo.TuVung
        WHERE MaTuVung IN ({placeholders})
        ORDER BY MaTuVung;
    """

    cursor.execute(
        sql,
        vocab_ids,
    )

    result = {}

    for row in cursor.fetchall():

        (
            ma_tu_vung,
            chu_han,
            phien_am,
            nghia_tieng_viet,
            tu_loai,
            ma_nguon,
            da_duyet,
        ) = row

        result[int(ma_tu_vung)] = {
            "MaTuVung": int(
                ma_tu_vung
            ),
            "ChuHan": clean(
                chu_han
            ),
            "PhienAm": clean(
                phien_am
            ),
            "NghiaTiengViet": clean(
                nghia_tieng_viet
            ),
            "TuLoai": clean(
                tu_loai
            ),
            "MaNguon": (
                ""
                if ma_nguon is None
                else str(
                    int(ma_nguon)
                )
            ),
            "DaDuyet": (
                1
                if bool(da_duyet)
                else 0
            ),
        }

    return result


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 110)
    print(
        "09G27 - DOI CHIEU FILE REVIEW HSK1 "
        "VOI DATABASE"
    )
    print("=" * 110)

    print()
    print("CHE DO AN TOAN:")
    print("  CHI DOC CSV")
    print("  CHI SELECT DATABASE")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    # =====================================================
    # 1. DOC FILE REVIEW
    # =====================================================
    print()
    print("[1] DOC FILE REVIEW")
    print("-" * 110)

    review_rows, review_ids = (
        load_review_file()
    )

    print(
        "File:",
        REVIEW_FILE,
    )

    print(
        "Tong dong:",
        len(review_rows),
    )

    print(
        "MaTuVung duy nhat:",
        len(set(review_ids)),
    )

    print(
        "DaKiemDuyet=1:",
        sum(
            1
            for row in review_rows
            if clean(
                row["DaKiemDuyet"]
            ) == "1"
        ),
    )

    print("FILE REVIEW: OK")

    # =====================================================
    # 2. KET NOI DATABASE
    # =====================================================
    print()
    print("[2] KET NOI DATABASE")
    print("-" * 110)

    with closing(
        get_connection()
    ) as connection:

        try:

            with closing(
                connection.cursor()
            ) as cursor:

                # -----------------------------------------
                # Thong tin ket noi
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        CONVERT(
                            nvarchar(128),
                            SERVERPROPERTY('ServerName')
                        ),
                        DB_NAME(),
                        SUSER_SNAME();
                    """
                )

                (
                    server_name,
                    database_name,
                    login_name,
                ) = cursor.fetchone()

                print(
                    "Server:",
                    server_name,
                )

                print(
                    "Database:",
                    database_name,
                )

                print(
                    "Tai khoan:",
                    login_name,
                )

                if clean(
                    database_name
                ).lower() != (
                    "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi nham database. "
                        "Mong doi HocTiengTrungDB, "
                        f"thuc te: {database_name}"
                    )

                print(
                    "KET NOI DATABASE: OK"
                )

                # =========================================
                # 3. KIEM TRA SCHEMA
                # =========================================
                print()
                print(
                    "[3] KIEM TRA SCHEMA dbo.TuVung"
                )
                print("-" * 110)

                actual_columns = (
                    check_database_schema(
                        cursor
                    )
                )

                print(
                    "So cot hien tai cua TuVung:",
                    len(actual_columns),
                )

                print(
                    "Cac cot can doi chieu: OK"
                )

                # =========================================
                # 4. THONG KE DATABASE
                # =========================================
                print()
                print(
                    "[4] THONG KE BANG dbo.TuVung"
                )
                print("-" * 110)

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.TuVung;
                    """
                )

                total_db_vocab = int(
                    cursor.fetchone()[0]
                )

                print(
                    "Tong dong hien co "
                    "trong dbo.TuVung:",
                    total_db_vocab,
                )

                # =========================================
                # 5. LOAD 501 MA TU VUNG
                # =========================================
                print()
                print(
                    "[5] LAY 501 MaTuVung "
                    "TU DATABASE"
                )
                print("-" * 110)

                db_rows = (
                    load_database_rows(
                        cursor,
                        review_ids,
                    )
                )

                print(
                    "So MaTuVung tim thay:",
                    len(db_rows),
                )

                review_id_set = set(
                    review_ids
                )

                db_id_set = set(
                    db_rows.keys()
                )

                missing_ids = sorted(
                    review_id_set
                    - db_id_set
                )

                unexpected_ids = sorted(
                    db_id_set
                    - review_id_set
                )

                print(
                    "MaTuVung thieu trong DB:",
                    len(missing_ids),
                )

                print(
                    "MaTuVung du:",
                    len(unexpected_ids),
                )

                if missing_ids:

                    print(
                        "Danh sach ID thieu:",
                        missing_ids[:50],
                    )

                    fail(
                        "Co MaTuVung trong CSV "
                        "khong ton tai trong database."
                    )

                if unexpected_ids:
                    fail(
                        "Ket qua SELECT co "
                        "MaTuVung ngoai danh sach CSV."
                    )

                if len(db_rows) != 501:
                    fail(
                        "Phai tim thay dung "
                        "501 MaTuVung trong database."
                    )

                print(
                    "501/501 MaTuVung: OK"
                )

                # =========================================
                # 6. DOI CHIEU TUNG DONG
                # =========================================
                print()
                print(
                    "[6] DOI CHIEU TUNG BAN GHI"
                )
                print("-" * 110)

                hanzi_mismatches = []
                pinyin_mismatches = []
                source_mismatches = []

                source_meaning_mismatches = []
                source_pos_mismatches = []

                approved_rows = []

                learning_meaning_changes = []
                learning_pos_changes = []

                rows_need_update = set()

                for csv_row in review_rows:

                    vocab_id = int(
                        clean(
                            csv_row[
                                "MaTuVung"
                            ]
                        )
                    )

                    db_row = db_rows[
                        vocab_id
                    ]

                    csv_hanzi = clean(
                        csv_row["ChuHan"]
                    )

                    csv_pinyin = clean(
                        csv_row["PhienAm"]
                    )

                    csv_source = clean(
                        csv_row["MaNguon"]
                    )

                    csv_source_meaning = clean(
                        csv_row[
                            "NghiaNguon"
                        ]
                    )

                    csv_source_pos = clean(
                        csv_row[
                            "TuLoaiNguon"
                        ]
                    )

                    csv_learning_meaning = clean(
                        csv_row[
                            "NghiaHocTap"
                        ]
                    )

                    csv_learning_pos = clean(
                        csv_row[
                            "TuLoaiHocTap"
                        ]
                    )

                    # -------------------------------------
                    # ChuHan
                    # -------------------------------------
                    if (
                        db_row["ChuHan"]
                        != csv_hanzi
                    ):

                        hanzi_mismatches.append(
                            (
                                f"MaTuVung={vocab_id} | "
                                f"CSV='{csv_hanzi}' | "
                                f"DB='{db_row['ChuHan']}'"
                            )
                        )

                    # -------------------------------------
                    # Pinyin
                    #
                    # So sanh EXACT sau khi trim.
                    # Khong tu dong bo dau / bo khoang trang.
                    # -------------------------------------
                    if (
                        db_row["PhienAm"]
                        != csv_pinyin
                    ):

                        pinyin_mismatches.append(
                            (
                                f"MaTuVung={vocab_id} "
                                f"{csv_hanzi} | "
                                f"CSV='{csv_pinyin}' | "
                                f"DB='{db_row['PhienAm']}'"
                            )
                        )

                    # -------------------------------------
                    # Nguon
                    # -------------------------------------
                    if (
                        db_row["MaNguon"]
                        != csv_source
                    ):

                        source_mismatches.append(
                            (
                                f"MaTuVung={vocab_id} "
                                f"{csv_hanzi} | "
                                f"CSV MaNguon="
                                f"'{csv_source}' | "
                                f"DB MaNguon="
                                f"'{db_row['MaNguon']}'"
                            )
                        )

                    # -------------------------------------
                    # Nghia nguon
                    #
                    # DB chua update, nen
                    # NghiaTiengViet hien tai phai
                    # van giong NghiaNguon da export.
                    # -------------------------------------
                    if (
                        db_row[
                            "NghiaTiengViet"
                        ]
                        != csv_source_meaning
                    ):

                        source_meaning_mismatches.append(
                            (
                                f"MaTuVung={vocab_id} "
                                f"{csv_hanzi} "
                                f"[{csv_pinyin}]\n"
                                f"  CSV NghiaNguon: "
                                f"{csv_source_meaning}\n"
                                f"  DB NghiaTiengViet: "
                                f"{db_row['NghiaTiengViet']}"
                            )
                        )

                    # -------------------------------------
                    # Tu loai nguon
                    # -------------------------------------
                    if (
                        db_row["TuLoai"]
                        != csv_source_pos
                    ):

                        source_pos_mismatches.append(
                            (
                                f"MaTuVung={vocab_id} "
                                f"{csv_hanzi} "
                                f"[{csv_pinyin}] | "
                                f"CSV TuLoaiNguon="
                                f"'{csv_source_pos}' | "
                                f"DB TuLoai="
                                f"'{db_row['TuLoai']}'"
                            )
                        )

                    # -------------------------------------
                    # DaDuyet hien tai
                    #
                    # Truoc buoc apply review,
                    # 501 tu van phai DaDuyet=0.
                    # -------------------------------------
                    if (
                        db_row["DaDuyet"]
                        != 0
                    ):

                        approved_rows.append(
                            (
                                f"MaTuVung={vocab_id} "
                                f"{csv_hanzi} "
                                f"[{csv_pinyin}] "
                                f"DaDuyet="
                                f"{db_row['DaDuyet']}"
                            )
                        )

                    # -------------------------------------
                    # THONG KE NHUNG GI SE DOI
                    #
                    # CHI THONG KE.
                    # KHONG UPDATE.
                    # -------------------------------------
                    if (
                        db_row[
                            "NghiaTiengViet"
                        ]
                        != csv_learning_meaning
                    ):

                        learning_meaning_changes.append(
                            vocab_id
                        )

                        rows_need_update.add(
                            vocab_id
                        )

                    if (
                        db_row["TuLoai"]
                        != csv_learning_pos
                    ):

                        learning_pos_changes.append(
                            vocab_id
                        )

                        rows_need_update.add(
                            vocab_id
                        )

                # =========================================
                # 7. IN KET QUA DOI CHIEU
                # =========================================
                print(
                    "Sai ChuHan:",
                    len(hanzi_mismatches),
                )

                print(
                    "Sai PhienAm:",
                    len(pinyin_mismatches),
                )

                print(
                    "Sai MaNguon:",
                    len(source_mismatches),
                )

                print(
                    "DB NghiaTiengViet "
                    "khac NghiaNguon:",
                    len(
                        source_meaning_mismatches
                    ),
                )

                print(
                    "DB TuLoai "
                    "khac TuLoaiNguon:",
                    len(
                        source_pos_mismatches
                    ),
                )

                print(
                    "DaDuyet != 0:",
                    len(approved_rows),
                )

                # =========================================
                # 8. NEU CO LOI THI IN RA
                # =========================================
                print_mismatches(
                    "SAI ChuHan",
                    hanzi_mismatches,
                )

                print_mismatches(
                    "SAI PhienAm",
                    pinyin_mismatches,
                )

                print_mismatches(
                    "SAI MaNguon",
                    source_mismatches,
                )

                print_mismatches(
                    "DB NghiaTiengViet "
                    "KHONG CON KHOP NghiaNguon",
                    source_meaning_mismatches,
                )

                print_mismatches(
                    "DB TuLoai "
                    "KHONG CON KHOP TuLoaiNguon",
                    source_pos_mismatches,
                )

                print_mismatches(
                    "PHAT HIEN DaDuyet != 0",
                    approved_rows,
                )

                # =========================================
                # 9. FAIL NEU DATABASE DA BI THAY DOI
                # =========================================
                total_mismatches = (
                    len(
                        hanzi_mismatches
                    )
                    + len(
                        pinyin_mismatches
                    )
                    + len(
                        source_mismatches
                    )
                    + len(
                        source_meaning_mismatches
                    )
                    + len(
                        source_pos_mismatches
                    )
                    + len(
                        approved_rows
                    )
                )

                if total_mismatches != 0:
                    fail(
                        "CSV review va database "
                        "KHONG con dong bo. "
                        "KHONG duoc UPDATE database."
                    )

                print()
                print(
                    "501/501 BAN GHI "
                    "KHOP DATABASE: OK"
                )

                # =========================================
                # 10. THONG KE NHUNG GI SE THAY DOI
                # =========================================
                print()
                print(
                    "[7] THONG KE DU KIEN "
                    "CHO BUOC UPDATE SAU"
                )
                print("-" * 110)

                print(
                    "NghiaTiengViet se thay doi:",
                    len(
                        learning_meaning_changes
                    ),
                )

                print(
                    "TuLoai se thay doi:",
                    len(
                        learning_pos_changes
                    ),
                )

                print(
                    "Tong MaTuVung co it nhat "
                    "1 truong can cap nhat:",
                    len(
                        rows_need_update
                    ),
                )

                print(
                    "DaDuyet se chuyen "
                    "0 -> 1:",
                    501,
                )

                print()
                print(
                    "LUU Y: DAY CHI LA THONG KE."
                )

                print(
                    "KHONG CO LENH UPDATE "
                    "NAO DUOC CHAY."
                )

                # =========================================
                # 11. KET QUA CUOI
                # =========================================
                print()
                print("=" * 110)
                print(
                    "KET QUA DOI CHIEU CUOI CUNG"
                )
                print("=" * 110)

                print(
                    "CSV review:",
                    len(review_rows),
                )

                print(
                    "MaTuVung trong DB tim thay:",
                    len(db_rows),
                )

                print(
                    "Khong khop ChuHan:",
                    len(hanzi_mismatches),
                )

                print(
                    "Khong khop PhienAm:",
                    len(pinyin_mismatches),
                )

                print(
                    "Khong khop MaNguon:",
                    len(source_mismatches),
                )

                print(
                    "Nghia nguon bi thay doi:",
                    len(
                        source_meaning_mismatches
                    ),
                )

                print(
                    "Tu loai nguon bi thay doi:",
                    len(
                        source_pos_mismatches
                    ),
                )

                print(
                    "DaDuyet != 0:",
                    len(approved_rows),
                )

                print()
                print(
                    "DOI CHIEU CSV <-> DATABASE "
                    "THANH CONG."
                )

                print(
                    "501/501 BAN GHI KHOP "
                    "MaTuVung + ChuHan + PhienAm "
                    "+ MaNguon."
                )

                print(
                    "DATABASE VAN GIU "
                    "DU LIEU NGUON BAN DAU."
                )

                print()
                print(
                    "SAN SANG CHO BUOC "
                    "TAO BACKUP DATABASE "
                    "VA APPLY NOI DUNG "
                    "DA KIEM DUYET."
                )

                print()
                print(
                    "SCRIPT NAY CHI SELECT."
                )

                print(
                    "DATABASE KHONG BI SUA."
                )

                print()
                print("=" * 110)
                print("HOAN TAT")
                print("=" * 110)

        finally:

            # Khong co thao tac ghi.
            # Rollback de dam bao transaction
            # duoc dong ma khong commit bat cu thu gi.
            try:
                connection.rollback()
            except Exception:
                pass


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print()
        print("=" * 110)
        print(
            "DOI CHIEU THAT BAI"
        )
        print("=" * 110)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "KHONG DUOC CHAY BUOC UPDATE."
        )

        print(
            "SCRIPT NAY KHONG SUA DATABASE."
        )

        sys.exit(1)