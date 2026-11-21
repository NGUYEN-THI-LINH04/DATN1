from pathlib import Path
import csv
import hashlib
import shutil
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
# FILES
# =========================================================
REVIEW_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "review"
    / "hsk1_501_vocab_review.csv"
)

BACKUP_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "review"
    / "db_backup"
    / "hsk1_tuvung_before_review_apply_20260929_025148.csv"
)

EXPECTED_BACKUP_SHA256 = (
    "ca0e3fc574c53d51a35e70007bc2a707"
    "1563edc3a64a01eae869fc6446175512"
)

SNAPSHOT_DIR = (
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


def nullable(value):
    value = clean(value)

    if value == "":
        return None

    return value


def fail(message):
    raise RuntimeError(message)


def sha256_file(path):

    digest = hashlib.sha256()

    with open(path, "rb") as file:

        while True:

            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


# =========================================================
# DOC FILE REVIEW
# =========================================================
def load_review():

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
                "Khong doc duoc header CSV."
            )

        fieldnames = reader.fieldnames
        rows = list(reader)

    required = {
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

    missing = (
        required
        - set(fieldnames)
    )

    if missing:
        fail(
            "File review thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

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
                f"MaTuVung={vocab_id} "
                "chua DaKiemDuyet=1."
            )

        if not clean(
            row["TuLoaiHocTap"]
        ):
            fail(
                f"MaTuVung={vocab_id} "
                "thieu TuLoaiHocTap."
            )

        if not clean(
            row["NghiaHocTap"]
        ):
            fail(
                f"MaTuVung={vocab_id} "
                "thieu NghiaHocTap."
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
# LOAD DATABASE
# =========================================================
def load_db_rows(cursor, ids):

    placeholders = ",".join(
        "?"
        for _ in ids
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
        ids,
    )

    result = {}

    for row in cursor.fetchall():

        result[int(row[0])] = {
            "ChuHan": clean(
                row[1]
            ),

            "PhienAm": clean(
                row[2]
            ),

            "NghiaTiengViet": clean(
                row[3]
            ),

            "TuLoai": clean(
                row[4]
            ),

            "MaNguon": (
                ""
                if row[5] is None
                else str(
                    int(row[5])
                )
            ),

            "DaDuyet": (
                1
                if bool(row[6])
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
        "09G29 - APPLY 501 TU VUNG HSK1 "
        "DA KIEM DUYET VAO DATABASE"
    )
    print("=" * 110)

    print()
    print("CANH BAO:")
    print(
        "  BUOC NAY SE THUC SU UPDATE "
        "dbo.TuVung."
    )

    print(
        "  Chi sua:"
    )

    print(
        "    - NghiaTiengViet"
    )

    print(
        "    - TuLoai"
    )

    print(
        "    - DaDuyet"
    )

    print(
        "  KHONG sua ChuHan, PhienAm, "
        "MaNguon, vi du, audio..."
    )

    print(
        "  Neu bat ky kiem tra nao sai "
        "truoc COMMIT,"
    )

    print(
        "  toan bo transaction se ROLLBACK."
    )

    # =====================================================
    # 1. VERIFY BACKUP
    # =====================================================
    print()
    print("[1] VERIFY BACKUP TRUOC APPLY")
    print("-" * 110)

    if not BACKUP_FILE.exists():
        fail(
            "Khong tim thay file backup:\n"
            f"{BACKUP_FILE}"
        )

    actual_backup_hash = sha256_file(
        BACKUP_FILE
    )

    print("Backup:")
    print(BACKUP_FILE)

    print("SHA256:")
    print(actual_backup_hash)

    if (
        actual_backup_hash
        != EXPECTED_BACKUP_SHA256
    ):
        fail(
            "SHA256 backup khong khop.\n"
            "KHONG DUOC APPLY."
        )

    print("BACKUP: OK")

    # =====================================================
    # 2. LOAD REVIEW
    # =====================================================
    print()
    print("[2] DOC FILE REVIEW")
    print("-" * 110)

    review_rows, review_ids = (
        load_review()
    )

    print(
        "Tong dong:",
        len(review_rows),
    )

    print(
        "MaTuVung duy nhat:",
        len(set(review_ids)),
    )

    reviewed_count = sum(
        1
        for row in review_rows
        if clean(
            row["DaKiemDuyet"]
        ) == "1"
    )

    print(
        "DaKiemDuyet=1:",
        reviewed_count,
    )

    if reviewed_count != 501:
        fail(
            "File review khong co "
            "501 dong DaKiemDuyet=1."
        )

    print(
        "FILE REVIEW: OK"
    )

    # =====================================================
    # 3. SNAPSHOT REVIEW SE APPLY
    # =====================================================
    print()
    print(
        "[3] DONG BANG FILE REVIEW SE APPLY"
    )
    print("-" * 110)

    SNAPSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    review_snapshot = (
        SNAPSHOT_DIR
        / (
            "hsk1_review_applied_"
            f"{timestamp}.csv"
        )
    )

    shutil.copy2(
        REVIEW_FILE,
        review_snapshot,
    )

    review_hash = sha256_file(
        review_snapshot
    )

    print("Snapshot:")
    print(review_snapshot)

    print("SHA256:")
    print(review_hash)

    # =====================================================
    # 4. USER CONFIRMATION
    # =====================================================
    print()
    print("=" * 110)
    print("XAC NHAN APPLY")
    print("=" * 110)

    print(
        "Neu tiep tuc, 501 ban ghi "
        "dbo.TuVung se duoc cap nhat."
    )

    confirmation = input(
        "Nhap chinh xac APPLY HSK1 501 "
        "de tiep tuc: "
    ).strip()

    if confirmation != "APPLY HSK1 501":

        print()
        print(
            "KHONG NHAN DUOC XAC NHAN."
        )

        print(
            "DATABASE KHONG BI SUA."
        )

        return

    # =====================================================
    # 5. CONNECT DATABASE
    # =====================================================
    print()
    print("[4] KET NOI DATABASE")
    print("-" * 110)

    with closing(
        get_connection()
    ) as connection:

        committed = False

        try:

            try:
                connection.autocommit = False
            except Exception:
                pass

            with closing(
                connection.cursor()
            ) as cursor:

                # =========================================
                # Database identity
                # =========================================
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
                        "Dang ket noi nham database.\n"
                        f"Thuc te: {database_name}"
                    )

                print(
                    "KET NOI DATABASE: OK"
                )

                # =========================================
                # 6. PRE-CHECK
                # =========================================
                print()
                print(
                    "[5] PRE-CHECK DATABASE "
                    "NGAY TRUOC UPDATE"
                )
                print("-" * 110)

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.TuVung;
                    """
                )

                total_table = int(
                    cursor.fetchone()[0]
                )

                print(
                    "Tong dong dbo.TuVung:",
                    total_table,
                )

                if total_table != 501:
                    fail(
                        "dbo.TuVung khong con "
                        "dung 501 dong."
                    )

                db_before = load_db_rows(
                    cursor,
                    review_ids,
                )

                if len(db_before) != 501:
                    fail(
                        "Khong tim thay du "
                        "501 MaTuVung."
                    )

                mismatch_count = 0
                meaning_changes = 0
                pos_changes = 0

                for csv_row in review_rows:

                    vocab_id = int(
                        clean(
                            csv_row["MaTuVung"]
                        )
                    )

                    db = db_before[
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
                        csv_row["NghiaNguon"]
                    )

                    csv_source_pos = clean(
                        csv_row["TuLoaiNguon"]
                    )

                    csv_learning_meaning = clean(
                        csv_row["NghiaHocTap"]
                    )

                    csv_learning_pos = clean(
                        csv_row["TuLoaiHocTap"]
                    )

                    if (
                        db["ChuHan"] != csv_hanzi
                        or
                        db["PhienAm"] != csv_pinyin
                        or
                        db["MaNguon"] != csv_source
                        or
                        db["NghiaTiengViet"]
                        != csv_source_meaning
                        or
                        db["TuLoai"]
                        != csv_source_pos
                        or
                        db["DaDuyet"] != 0
                    ):
                        mismatch_count += 1

                    if (
                        db["NghiaTiengViet"]
                        != csv_learning_meaning
                    ):
                        meaning_changes += 1

                    if (
                        db["TuLoai"]
                        != csv_learning_pos
                    ):
                        pos_changes += 1

                print(
                    "Ban ghi khong con khop "
                    "du lieu nguon:",
                    mismatch_count,
                )

                print(
                    "NghiaTiengViet du kien doi:",
                    meaning_changes,
                )

                print(
                    "TuLoai du kien doi:",
                    pos_changes,
                )

                if mismatch_count != 0:
                    fail(
                        "Database da thay doi "
                        "sau buoc 09g27.\n"
                        "KHONG DUOC UPDATE."
                    )

                if meaning_changes != 450:
                    fail(
                        "So NghiaTiengViet du kien "
                        "thay doi khong con la 450.\n"
                        f"Thuc te: {meaning_changes}"
                    )

                if pos_changes != 501:
                    fail(
                        "So TuLoai du kien "
                        "thay doi khong con la 501.\n"
                        f"Thuc te: {pos_changes}"
                    )

                print(
                    "PRE-CHECK: OK"
                )

                # =========================================
                # 7. UPDATE
                #
                # SUA LOI O DAY:
                # KHONG DUNG SELECT @@ROWCOUNT.
                # DUNG cursor.rowcount.
                # =========================================
                print()
                print(
                    "[6] UPDATE TRONG TRANSACTION"
                )
                print("-" * 110)

                updated = 0

                for index, csv_row in enumerate(
                    review_rows,
                    start=1,
                ):

                    vocab_id = int(
                        clean(
                            csv_row["MaTuVung"]
                        )
                    )

                    hanzi = clean(
                        csv_row["ChuHan"]
                    )

                    pinyin = clean(
                        csv_row["PhienAm"]
                    )

                    source_id = int(
                        clean(
                            csv_row["MaNguon"]
                        )
                    )

                    source_meaning = clean(
                        csv_row["NghiaNguon"]
                    )

                    source_pos = nullable(
                        csv_row["TuLoaiNguon"]
                    )

                    learning_meaning = clean(
                        csv_row["NghiaHocTap"]
                    )

                    learning_pos = clean(
                        csv_row["TuLoaiHocTap"]
                    )

                    # -------------------------------------
                    # Optimistic locking:
                    #
                    # Chi UPDATE neu ban ghi van
                    # dung trang thai NGUON ban dau.
                    #
                    # Neu 1 dong da bi thay doi,
                    # rowcount se khong bang 1
                    # va toan bo transaction rollback.
                    # -------------------------------------
                    cursor.execute(
                        """
                        UPDATE dbo.TuVung
                        SET
                            NghiaTiengViet = ?,
                            TuLoai = ?,
                            DaDuyet = 1
                        WHERE
                            MaTuVung = ?
                            AND ChuHan = ?
                            AND PhienAm = ?
                            AND MaNguon = ?
                            AND NghiaTiengViet = ?
                            AND DaDuyet = 0
                            AND (
                                TuLoai = ?
                                OR (
                                    TuLoai IS NULL
                                    AND ? IS NULL
                                )
                            );
                        """,

                        learning_meaning,
                        learning_pos,

                        vocab_id,
                        hanzi,
                        pinyin,
                        source_id,
                        source_meaning,

                        source_pos,
                        source_pos,
                    )

                    # =====================================
                    # DAY LA PHAN DA SUA
                    # =====================================
                    affected = cursor.rowcount

                    if affected != 1:

                        fail(
                            "UPDATE that bai tai:\n"
                            f"MaTuVung={vocab_id}\n"
                            f"ChuHan={hanzi}\n"
                            f"PhienAm={pinyin}\n"
                            f"rowcount={affected}\n"
                            "ROLLBACK TOAN BO."
                        )

                    updated += 1

                    if (
                        index % 50 == 0
                        or index == 501
                    ):
                        print(
                            f"  Da update: "
                            f"{index}/501"
                        )

                if updated != 501:
                    fail(
                        "So dong UPDATE "
                        "khong bang 501."
                    )

                print()
                print(
                    "UPDATE 501/501: OK"
                )

                # =========================================
                # 8. VERIFY TRUOC COMMIT
                # =========================================
                print()
                print(
                    "[7] VERIFY TRUOC COMMIT"
                )
                print("-" * 110)

                db_after = load_db_rows(
                    cursor,
                    review_ids,
                )

                if len(db_after) != 501:
                    fail(
                        "Sau UPDATE khong doc "
                        "duoc dung 501 dong."
                    )

                after_errors = []

                immutable_errors = []

                for csv_row in review_rows:

                    vocab_id = int(
                        clean(
                            csv_row["MaTuVung"]
                        )
                    )

                    db = db_after[
                        vocab_id
                    ]

                    expected_hanzi = clean(
                        csv_row["ChuHan"]
                    )

                    expected_pinyin = clean(
                        csv_row["PhienAm"]
                    )

                    expected_source = clean(
                        csv_row["MaNguon"]
                    )

                    expected_meaning = clean(
                        csv_row["NghiaHocTap"]
                    )

                    expected_pos = clean(
                        csv_row["TuLoaiHocTap"]
                    )

                    # -------------------------------------
                    # Cac cot DUOC PHEP thay doi
                    # -------------------------------------
                    if (
                        db["NghiaTiengViet"]
                        != expected_meaning
                        or
                        db["TuLoai"]
                        != expected_pos
                        or
                        db["DaDuyet"] != 1
                    ):
                        after_errors.append(
                            vocab_id
                        )

                    # -------------------------------------
                    # Cac cot KHONG DUOC thay doi
                    # -------------------------------------
                    if (
                        db["ChuHan"]
                        != expected_hanzi
                        or
                        db["PhienAm"]
                        != expected_pinyin
                        or
                        db["MaNguon"]
                        != expected_source
                    ):
                        immutable_errors.append(
                            vocab_id
                        )

                print(
                    "Ban ghi sai noi dung "
                    "sau UPDATE:",
                    len(after_errors),
                )

                print(
                    "Ban ghi bi doi "
                    "ChuHan/PhienAm/MaNguon:",
                    len(immutable_errors),
                )

                if after_errors:
                    print(
                        "ID loi:",
                        after_errors[:20],
                    )

                    fail(
                        "VERIFY noi dung "
                        "truoc COMMIT that bai."
                    )

                if immutable_errors:
                    print(
                        "ID loi:",
                        immutable_errors[:20],
                    )

                    fail(
                        "Phat hien cot khong duoc "
                        "phep bi thay doi."
                    )

                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS TongDong,
                        SUM(
                            CASE
                                WHEN DaDuyet = 1
                                THEN 1
                                ELSE 0
                            END
                        ) AS TongDaDuyet
                    FROM dbo.TuVung;
                    """
                )

                (
                    total_after,
                    approved_after,
                ) = cursor.fetchone()

                total_after = int(
                    total_after
                )

                approved_after = int(
                    approved_after or 0
                )

                print(
                    "Tong dong:",
                    total_after,
                )

                print(
                    "DaDuyet=1:",
                    approved_after,
                )

                if total_after != 501:
                    fail(
                        "Tong dong sau UPDATE "
                        "khong con la 501."
                    )

                if approved_after != 501:
                    fail(
                        "DaDuyet=1 sau UPDATE "
                        "khong bang 501."
                    )

                print(
                    "VERIFY TRUOC COMMIT: OK"
                )

                # =========================================
                # 9. COMMIT
                # =========================================
                print()
                print(
                    "[8] COMMIT TRANSACTION"
                )
                print("-" * 110)

                connection.commit()

                committed = True

                print(
                    "COMMIT THANH CONG."
                )

                # =========================================
                # 10. VERIFY SAU COMMIT
                # =========================================
                print()
                print(
                    "[9] VERIFY SAU COMMIT"
                )
                print("-" * 110)

                db_committed = load_db_rows(
                    cursor,
                    review_ids,
                )

                if len(db_committed) != 501:
                    fail(
                        "Sau COMMIT khong doc "
                        "duoc dung 501 dong."
                    )

                final_errors = []

                final_immutable_errors = []

                for csv_row in review_rows:

                    vocab_id = int(
                        clean(
                            csv_row["MaTuVung"]
                        )
                    )

                    db = db_committed[
                        vocab_id
                    ]

                    expected_hanzi = clean(
                        csv_row["ChuHan"]
                    )

                    expected_pinyin = clean(
                        csv_row["PhienAm"]
                    )

                    expected_source = clean(
                        csv_row["MaNguon"]
                    )

                    expected_meaning = clean(
                        csv_row["NghiaHocTap"]
                    )

                    expected_pos = clean(
                        csv_row["TuLoaiHocTap"]
                    )

                    if (
                        db["NghiaTiengViet"]
                        != expected_meaning
                        or
                        db["TuLoai"]
                        != expected_pos
                        or
                        db["DaDuyet"] != 1
                    ):
                        final_errors.append(
                            vocab_id
                        )

                    if (
                        db["ChuHan"]
                        != expected_hanzi
                        or
                        db["PhienAm"]
                        != expected_pinyin
                        or
                        db["MaNguon"]
                        != expected_source
                    ):
                        final_immutable_errors.append(
                            vocab_id
                        )

                print(
                    "Loi noi dung sau COMMIT:",
                    len(final_errors),
                )

                print(
                    "Loi cot khong duoc sua:",
                    len(
                        final_immutable_errors
                    ),
                )

                if final_errors:

                    print(
                        "ID loi:",
                        final_errors[:20],
                    )

                    fail(
                        "Du lieu sau COMMIT "
                        "khong dung file review."
                    )

                if final_immutable_errors:

                    print(
                        "ID loi:",
                        final_immutable_errors[:20],
                    )

                    fail(
                        "Phat hien ChuHan / "
                        "PhienAm / MaNguon "
                        "bi thay doi sau COMMIT."
                    )

                cursor.execute(
                    """
                    SELECT
                        COUNT(*),
                        SUM(
                            CASE
                                WHEN DaDuyet = 1
                                THEN 1
                                ELSE 0
                            END
                        )
                    FROM dbo.TuVung;
                    """
                )

                (
                    final_total,
                    final_approved,
                ) = cursor.fetchone()

                final_total = int(
                    final_total
                )

                final_approved = int(
                    final_approved or 0
                )

                print(
                    "Tong dong sau COMMIT:",
                    final_total,
                )

                print(
                    "DaDuyet=1 sau COMMIT:",
                    final_approved,
                )

                if final_total != 501:
                    fail(
                        "Tong dong sau COMMIT "
                        "khong bang 501."
                    )

                if final_approved != 501:
                    fail(
                        "DaDuyet=1 sau COMMIT "
                        "khong bang 501."
                    )

                print(
                    "VERIFY SAU COMMIT: OK"
                )

                # =========================================
                # 11. RESULT
                # =========================================
                print()
                print("=" * 110)
                print(
                    "KET QUA APPLY HSK1"
                )
                print("=" * 110)

                print(
                    "Tong MaTuVung:",
                    501,
                )

                print(
                    "Da UPDATE:",
                    updated,
                )

                print(
                    "NghiaTiengViet thay doi:",
                    meaning_changes,
                )

                print(
                    "TuLoai thay doi:",
                    pos_changes,
                )

                print(
                    "DaDuyet=1:",
                    final_approved,
                )

                print(
                    "Loi verify:",
                    len(final_errors),
                )

                print()
                print(
                    "DATABASE DA DUOC CAP NHAT "
                    "THANH CONG."
                )

                print(
                    "501/501 TU VUNG HSK1 "
                    "DA AP DUNG NOI DUNG "
                    "DA KIEM DUYET."
                )

                print()
                print(
                    "CHI 3 TRUONG DA DUOC SUA:"
                )

                print(
                    "  NghiaTiengViet"
                )

                print(
                    "  TuLoai"
                )

                print(
                    "  DaDuyet"
                )

                print()
                print(
                    "Backup truoc apply:"
                )

                print(
                    BACKUP_FILE
                )

                print(
                    "SHA256 backup:"
                )

                print(
                    EXPECTED_BACKUP_SHA256
                )

                print()
                print(
                    "Snapshot review da apply:"
                )

                print(
                    review_snapshot
                )

                print(
                    "SHA256 snapshot:"
                )

                print(
                    review_hash
                )

                print()
                print("=" * 110)
                print("HOAN TAT")
                print("=" * 110)

        except Exception:

            # =================================================
            # Neu chua COMMIT:
            # rollback toan bo.
            #
            # Neu da COMMIT:
            # khong duoc noi la rollback thanh cong,
            # vi COMMIT da ghi xuong DB.
            # =================================================
            if not committed:

                try:

                    connection.rollback()

                    print()
                    print(
                        "TRANSACTION DA ROLLBACK."
                    )

                    print(
                        "KHONG GIU LAI UPDATE "
                        "CHUA COMMIT."
                    )

                except Exception as rollback_error:

                    print()
                    print(
                        "LOI KHI ROLLBACK:"
                    )

                    print(
                        rollback_error
                    )

            else:

                print()
                print(
                    "LUU Y: LOI XAY RA "
                    "SAU KHI COMMIT."
                )

                print(
                    "DATABASE DA DUOC COMMIT, "
                    "KHONG THE ROLLBACK "
                    "BANG TRANSACTION CU."
                )

                print(
                    "FILE BACKUP VAN CO SAN "
                    "DE PHUC HOI NEU CAN."
                )

            raise


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 110)
        print(
            "APPLY THAT BAI"
        )
        print("=" * 110)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "Backup truoc apply:"
        )

        print(
            BACKUP_FILE
        )

        print()
        print(
            "KIEM TRA LOI TRUOC KHI "
            "CHAY LAI."
        )

        sys.exit(1)