from pathlib import Path
import csv
import hashlib
import sys
from datetime import datetime
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

BACKUP_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "review"
    / "db_backup"
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


def file_sha256(path):

    digest = hashlib.sha256()

    with open(path, "rb") as file:

        while True:

            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


# =========================================================
# DOC 501 MaTuVung TU FILE REVIEW
# =========================================================
def load_review_ids():

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

        if not reader.fieldnames:
            fail(
                "Khong doc duoc header file review."
            )

        required = {
            "MaTuVung",
            "ChuHan",
            "PhienAm",
            "MaNguon",
            "DaKiemDuyet",
        }

        missing = (
            required
            - set(reader.fieldnames)
        )

        if missing:
            fail(
                "File review thieu cot: "
                + ", ".join(
                    sorted(missing)
                )
            )

        rows = list(reader)

    if len(rows) != EXPECTED_ROWS:
        fail(
            "File review phai co 501 dong. "
            f"Thuc te: {len(rows)}"
        )

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

        if clean(
            row["DaKiemDuyet"]
        ) != "1":
            fail(
                "Van con dong review "
                "chua DaKiemDuyet=1."
            )

        ids.append(
            int(vocab_id)
        )

    if len(set(ids)) != EXPECTED_ROWS:
        fail(
            "File review khong co "
            "501 MaTuVung duy nhat."
        )

    return rows, ids


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 110)
    print(
        "09G28 - BACKUP 501 BAN GHI dbo.TuVung "
        "TRUOC KHI APPLY REVIEW"
    )
    print("=" * 110)

    print()
    print("CHE DO AN TOAN:")
    print("  CHI DOC FILE REVIEW")
    print("  CHI SELECT DATABASE")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")
    print("  CHI TAO FILE BACKUP CSV TREN O D")

    # =====================================================
    # 1. DOC FILE REVIEW
    # =====================================================
    print()
    print("[1] DOC DANH SACH 501 MaTuVung")
    print("-" * 110)

    review_rows, review_ids = (
        load_review_ids()
    )

    print(
        "Tong dong review:",
        len(review_rows),
    )

    print(
        "MaTuVung duy nhat:",
        len(set(review_ids)),
    )

    print("FILE REVIEW: OK")

    # =====================================================
    # 2. TAO THU MUC BACKUP
    # =====================================================
    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_file = (
        BACKUP_DIR
        / (
            "hsk1_tuvung_before_review_apply_"
            f"{timestamp}.csv"
        )
    )

    # =====================================================
    # 3. KET NOI DATABASE
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
                        f"Thuc te: {database_name}"
                    )

                print(
                    "KET NOI DATABASE: OK"
                )

                # =========================================
                # 4. KIEM TRA TABLE
                # =========================================
                print()
                print(
                    "[3] KIEM TRA dbo.TuVung"
                )
                print("-" * 110)

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.TuVung;
                    """
                )

                total_db = int(
                    cursor.fetchone()[0]
                )

                print(
                    "Tong dong dbo.TuVung:",
                    total_db,
                )

                if total_db != 501:
                    fail(
                        "dbo.TuVung hien khong co "
                        "dung 501 dong. "
                        f"Thuc te: {total_db}"
                    )

                # =========================================
                # 5. SELECT DUNG 501 ID
                # =========================================
                print()
                print(
                    "[4] DOC 501 BAN GHI "
                    "TU DATABASE"
                )
                print("-" * 110)

                placeholders = ",".join(
                    "?"
                    for _ in review_ids
                )

                sql = f"""
                    SELECT
                        MaTuVung,
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
                        NgayTao
                    FROM dbo.TuVung
                    WHERE MaTuVung IN ({placeholders})
                    ORDER BY MaTuVung;
                """

                cursor.execute(
                    sql,
                    review_ids,
                )

                db_rows = cursor.fetchall()

                if len(db_rows) != EXPECTED_ROWS:
                    fail(
                        "Phai SELECT duoc 501 dong. "
                        f"Thuc te: {len(db_rows)}"
                    )

                print(
                    "Dong tim thay:",
                    len(db_rows),
                )

                # =========================================
                # 6. KIEM TRA ID
                # =========================================
                db_ids = [
                    int(row[0])
                    for row in db_rows
                ]

                if set(db_ids) != set(
                    review_ids
                ):
                    fail(
                        "Danh sach MaTuVung trong DB "
                        "khong khop file review."
                    )

                if len(
                    set(db_ids)
                ) != 501:
                    fail(
                        "MaTuVung database "
                        "khong duy nhat."
                    )

                print(
                    "501/501 MaTuVung: OK"
                )

                # =========================================
                # 7. KIEM TRA DaDuyet VAN = 0
                # =========================================
                approved_count = sum(
                    1
                    for row in db_rows
                    if bool(row[10])
                )

                print(
                    "DaDuyet=1 hien tai:",
                    approved_count,
                )

                if approved_count != 0:
                    fail(
                        "Phat hien du lieu da "
                        "bi duyet truoc khi backup."
                    )

                print(
                    "Trang thai truoc apply: OK"
                )

                # =========================================
                # 8. DOI CHIEU LAI ChuHan / Pinyin
                # =========================================
                review_by_id = {
                    int(
                        clean(
                            row["MaTuVung"]
                        )
                    ): row
                    for row in review_rows
                }

                mismatches = []

                for row in db_rows:

                    vocab_id = int(
                        row[0]
                    )

                    csv_row = (
                        review_by_id[
                            vocab_id
                        ]
                    )

                    db_hanzi = clean(
                        row[1]
                    )

                    db_pinyin = clean(
                        row[3]
                    )

                    db_source = clean(
                        row[9]
                    )

                    if (
                        db_hanzi
                        != clean(
                            csv_row["ChuHan"]
                        )
                        or db_pinyin
                        != clean(
                            csv_row["PhienAm"]
                        )
                        or db_source
                        != clean(
                            csv_row["MaNguon"]
                        )
                    ):
                        mismatches.append(
                            vocab_id
                        )

                print(
                    "Ban ghi khong khop "
                    "ChuHan/PhienAm/MaNguon:",
                    len(mismatches),
                )

                if mismatches:
                    fail(
                        "Database da thay doi "
                        "so voi file review. "
                        "Khong tao backup apply."
                    )

                # =========================================
                # 9. GHI FILE BACKUP
                # =========================================
                print()
                print(
                    "[5] TAO FILE BACKUP CSV"
                )
                print("-" * 110)

                fieldnames = [
                    "MaTuVung",
                    "ChuHan",
                    "ChuPhonThe",
                    "PhienAm",
                    "NghiaTiengViet",
                    "TuLoai",
                    "ViDuTiengTrung",
                    "ViDuTiengViet",
                    "MaAmThanh",
                    "MaNguon",
                    "DaDuyet",
                    "NgayTao",
                ]

                with open(
                    backup_file,
                    "w",
                    encoding="utf-8-sig",
                    newline="",
                ) as file:

                    writer = csv.writer(
                        file
                    )

                    writer.writerow(
                        fieldnames
                    )

                    for row in db_rows:

                        writer.writerow([
                            ""
                            if value is None
                            else value
                            for value in row
                        ])

                print(
                    "Da tao:",
                    backup_file,
                )

        finally:

            # Khong co ghi DB.
            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 10. DOC LAI FILE BACKUP
    # =====================================================
    print()
    print("[6] VERIFY FILE BACKUP")
    print("-" * 110)

    if not backup_file.exists():
        fail(
            "File backup khong ton tai "
            "sau khi ghi."
        )

    with open(
        backup_file,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)
        backup_rows = list(reader)

    print(
        "Dong trong backup:",
        len(backup_rows),
    )

    if len(backup_rows) != 501:
        fail(
            "Backup khong co dung "
            "501 dong."
        )

    backup_ids = [
        int(
            clean(
                row["MaTuVung"]
            )
        )
        for row in backup_rows
    ]

    print(
        "MaTuVung duy nhat:",
        len(set(backup_ids)),
    )

    if len(
        set(backup_ids)
    ) != 501:
        fail(
            "Backup khong co "
            "501 MaTuVung duy nhat."
        )

    if set(
        backup_ids
    ) != set(
        review_ids
    ):
        fail(
            "MaTuVung trong backup "
            "khong khop file review."
        )

    # =====================================================
    # 11. SHA256
    # =====================================================
    sha256 = file_sha256(
        backup_file
    )

    print()
    print(
        "SHA256:"
    )

    print(
        sha256
    )

    print()
    print(
        "VERIFY FILE BACKUP: OK"
    )

    # =====================================================
    # 12. KET QUA
    # =====================================================
    print()
    print("=" * 110)
    print(
        "KET QUA BACKUP"
    )
    print("=" * 110)

    print(
        "Tong ban ghi backup:",
        len(backup_rows),
    )

    print(
        "MaTuVung duy nhat:",
        len(set(backup_ids)),
    )

    print(
        "Database da bi sua:",
        "KHONG",
    )

    print(
        "File backup:"
    )

    print(
        backup_file
    )

    print(
        "SHA256:"
    )

    print(
        sha256
    )

    print()
    print(
        "BACKUP THANH CONG."
    )

    print(
        "501 BAN GHI dbo.TuVung "
        "TRUOC APPLY DA DUOC LUU."
    )

    print()
    print(
        "DATABASE VAN CHUA BI SUA."
    )

    print()
    print("=" * 110)
    print("HOAN TAT")
    print("=" * 110)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print()
        print("=" * 110)
        print(
            "BACKUP THAT BAI"
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
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)