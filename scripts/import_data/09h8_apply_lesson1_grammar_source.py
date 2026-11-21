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
# CONFIG
# =========================================================
COURSE_CODE = "HSK1-CORE"
LESSON_NO = 1

EXPECTED_ROWS = 7
TARGET_SOURCE_ID = 1004
TARGET_SOURCE_NAME = "GF0025-2021 - Ngữ pháp HSK"


# =========================================================
# FILES
# =========================================================
REVIEW_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "hsk1_lesson1_grammar_mapping_review.csv"
)

BACKUP_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "db_backup"
)

SNAPSHOT_DIR = BACKUP_DIR


# =========================================================
# HELPERS
# =========================================================
def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def fail(message):

    raise RuntimeError(message)


def sha256_file(path):

    digest = hashlib.sha256()

    with open(path, "rb") as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def load_csv(path):

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:

            fail(
                f"Khong doc duoc header:\n{path}"
            )

        return reader.fieldnames, list(reader)


def normalize_nullable_int(value):

    text = clean(value)

    if text == "":
        return ""

    return str(
        int(text)
    )


def normalize_datetime(value):

    return clean(value)


def find_latest_backup():

    if not BACKUP_DIR.exists():

        fail(
            "Khong tim thay thu muc backup:\n"
            f"{BACKUP_DIR}"
        )

    backups = sorted(
        BACKUP_DIR.glob(
            "hsk1_lesson1_grammar_"
            "before_source_apply_*.csv"
        ),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not backups:

        fail(
            "Khong tim thay backup 09h7."
        )

    return backups[0]


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 115)
    print(
        "09H8 - APPLY MaNguon=1004 "
        "CHO 7 NGU PHAP BAI 1"
    )
    print("=" * 115)

    print()
    print("CANH BAO:")
    print(
        "  BUOC NAY SE THUC SU UPDATE dbo.NguPhap."
    )

    print(
        "  CHI DUOC SUA 1 COT: MaNguon."
    )

    print(
        "  MaNguon: NULL -> 1004."
    )

    print(
        "  Neu bat ky kiem tra nao sai truoc COMMIT,"
    )

    print(
        "  toan bo transaction se ROLLBACK."
    )

    # =====================================================
    # 1. VERIFY REVIEW
    # =====================================================
    print()
    print(
        "[1] VERIFY FILE REVIEW DA KIEM DUYET"
    )
    print("-" * 115)

    if not REVIEW_FILE.exists():

        fail(
            "Khong tim thay file review:\n"
            f"{REVIEW_FILE}"
        )

    review_fields, review_rows = load_csv(
        REVIEW_FILE
    )

    required_review_fields = {
        "MaNguPhap",
        "TenCauTruc",
        "MaNguonHienTai",
        "MaNguonDeXuat",
        "MaMucNguPhapChuan",
        "DaKiemDuyetMapping",
        "GhiChuKiemDuyet",
    }

    missing_review_fields = (
        required_review_fields
        - set(review_fields)
    )

    if missing_review_fields:

        fail(
            "File review thieu cot: "
            + ", ".join(
                sorted(
                    missing_review_fields
                )
            )
        )

    if len(review_rows) != EXPECTED_ROWS:

        fail(
            "File review phai co dung "
            f"{EXPECTED_ROWS} dong."
        )

    review_by_id = {}

    for row in review_rows:

        grammar_id_text = clean(
            row["MaNguPhap"]
        )

        if not grammar_id_text.isdigit():

            fail(
                "MaNguPhap khong hop le: "
                f"{grammar_id_text}"
            )

        grammar_id = int(
            grammar_id_text
        )

        if grammar_id in review_by_id:

            fail(
                "MaNguPhap bi trung: "
                f"{grammar_id}"
            )

        if (
            clean(
                row[
                    "DaKiemDuyetMapping"
                ]
            )
            != "1"
        ):

            fail(
                f"MaNguPhap={grammar_id} "
                "chua duoc kiem duyet."
            )

        if (
            clean(
                row["MaNguonDeXuat"]
            )
            != str(TARGET_SOURCE_ID)
        ):

            fail(
                f"MaNguPhap={grammar_id} "
                "khong de xuat MaNguon=1004."
            )

        if (
            clean(
                row["MaNguonHienTai"]
            )
            != ""
        ):

            fail(
                f"MaNguPhap={grammar_id} "
                "trong review khong con "
                "MaNguonHienTai=NULL."
            )

        if not clean(
            row["GhiChuKiemDuyet"]
        ):

            fail(
                f"MaNguPhap={grammar_id} "
                "thieu GhiChuKiemDuyet."
            )

        review_by_id[
            grammar_id
        ] = row

    if len(review_by_id) != 7:

        fail(
            "Khong co dung "
            "7 MaNguPhap duy nhat."
        )

    review_hash = sha256_file(
        REVIEW_FILE
    )

    print(
        "Tong mapping:",
        len(review_rows),
    )

    print(
        "DaKiemDuyetMapping=1:",
        7,
    )

    print(
        "MaNguonDeXuat=1004:",
        7,
    )

    print()
    print(
        "SHA256 review:"
    )

    print(
        review_hash
    )

    print(
        "FILE REVIEW: OK"
    )

    # =====================================================
    # 2. FIND + VERIFY BACKUP
    # =====================================================
    print()
    print(
        "[2] VERIFY BACKUP TRUOC APPLY"
    )
    print("-" * 115)

    backup_file = find_latest_backup()

    backup_fields, backup_rows = load_csv(
        backup_file
    )

    required_backup_fields = {
        "MaNguPhap",
        "MaBaiHoc",
        "SoThuTuBai",
        "TieuDeBai",
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
        "MaTep",
        "MaNguon",
        "ThuTu",
        "TrangThai",
        "NgayTao",
    }

    missing_backup_fields = (
        required_backup_fields
        - set(backup_fields)
    )

    if missing_backup_fields:

        fail(
            "Backup thieu cot: "
            + ", ".join(
                sorted(
                    missing_backup_fields
                )
            )
        )

    if len(backup_rows) != 7:

        fail(
            "Backup phai co dung 7 dong."
        )

    backup_by_id = {}

    for row in backup_rows:

        grammar_id = int(
            clean(
                row["MaNguPhap"]
            )
        )

        if grammar_id in backup_by_id:

            fail(
                "MaNguPhap bi trung "
                "trong backup: "
                f"{grammar_id}"
            )

        if (
            clean(
                row["MaNguon"]
            )
            != ""
        ):

            fail(
                f"Backup MaNguPhap="
                f"{grammar_id} "
                "khong co MaNguon=NULL."
            )

        backup_by_id[
            grammar_id
        ] = row

    if (
        set(backup_by_id)
        != set(review_by_id)
    ):

        fail(
            "Danh sach MaNguPhap "
            "backup va review "
            "khong khop nhau."
        )

    backup_hash = sha256_file(
        backup_file
    )

    print(
        "Backup:"
    )

    print(
        backup_file
    )

    print()
    print(
        "SHA256 backup:"
    )

    print(
        backup_hash
    )

    print()
    print(
        "Tong dong:",
        len(backup_rows),
    )

    print(
        "MaNguon=NULL:",
        7,
    )

    print(
        "BACKUP: OK"
    )

    # =====================================================
    # 3. FREEZE REVIEW SNAPSHOT
    # =====================================================
    print()
    print(
        "[3] DONG BANG REVIEW SE APPLY"
    )
    print("-" * 115)

    SNAPSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    snapshot_file = (
        SNAPSHOT_DIR
        / (
            "hsk1_lesson1_grammar_mapping_"
            f"applied_{timestamp}.csv"
        )
    )

    shutil.copy2(
        REVIEW_FILE,
        snapshot_file,
    )

    snapshot_hash = sha256_file(
        snapshot_file
    )

    if snapshot_hash != review_hash:

        fail(
            "Snapshot review "
            "khong trung SHA256 "
            "voi file review."
        )

    print(
        "Snapshot:"
    )

    print(
        snapshot_file
    )

    print()
    print(
        "SHA256 snapshot:"
    )

    print(
        snapshot_hash
    )

    # =====================================================
    # 4. CONFIRM
    # =====================================================
    print()
    print("=" * 115)
    print(
        "XAC NHAN APPLY"
    )
    print("=" * 115)

    print()
    print(
        "Neu tiep tuc, 7 dong dbo.NguPhap "
        "Bai 1 se duoc cap nhat:"
    )

    print(
        "MaNguon: NULL -> 1004"
    )

    confirmation = input(
        "Nhap chinh xac "
        "APPLY LESSON1 GRAMMAR SOURCE "
        "de tiep tuc: "
    ).strip()

    if (
        confirmation
        != "APPLY LESSON1 GRAMMAR SOURCE"
    ):

        print()
        print(
            "Khong nhan duoc xac nhan."
        )

        print(
            "DATABASE KHONG BI SUA."
        )

        return

    # =====================================================
    # 5. CONNECT DATABASE
    # =====================================================
    print()
    print(
        "[4] KET NOI DATABASE"
    )
    print("-" * 115)

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

                if (
                    clean(
                        database_name
                    ).lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi "
                        "nham database."
                    )

                print(
                    "KET NOI DATABASE: OK"
                )

                # =========================================
                # 6. VERIFY SOURCE
                # =========================================
                print()
                print(
                    "[5] VERIFY NGUON 1004"
                )
                print("-" * 115)

                cursor.execute(
                    """
                    SELECT
                        MaNguon,
                        Ten
                    FROM dbo.NguonDuLieu
                    WHERE MaNguon = ?;
                    """,
                    TARGET_SOURCE_ID,
                )

                source_row = (
                    cursor.fetchone()
                )

                if source_row is None:

                    fail(
                        "Khong tim thay "
                        "MaNguon=1004."
                    )

                if (
                    clean(
                        source_row[1]
                    )
                    != TARGET_SOURCE_NAME
                ):

                    fail(
                        "MaNguon=1004 "
                        "khong phai nguon "
                        "ngu phap mong doi."
                    )

                print(
                    "MaNguon:",
                    int(source_row[0]),
                )

                print(
                    "Ten:",
                    clean(source_row[1]),
                )

                print(
                    "NGUON: OK"
                )

                # =========================================
                # 7. PRE-CHECK DATABASE
                # =========================================
                print()
                print(
                    "[6] PRE-CHECK DATABASE "
                    "NGAY TRUOC UPDATE"
                )
                print("-" * 115)

                cursor.execute(
                    """
                    SELECT
                        np.MaNguPhap,
                        np.MaBaiHoc,
                        bh.SoThuTuBai,
                        bh.TieuDe,
                        np.TenCauTruc,
                        np.MoTa,
                        np.CachDung,
                        np.ViDuTiengTrung,
                        np.ViDuPinyin,
                        np.ViDuTiengViet,
                        np.MaTep,
                        np.MaNguon,
                        np.ThuTu,
                        np.TrangThai,
                        np.NgayTao
                    FROM dbo.NguPhap AS np
                    INNER JOIN dbo.BaiHoc AS bh
                        ON np.MaBaiHoc
                        = bh.MaBaiHoc
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc
                    WHERE
                        kh.MaKyHieu = ?
                        AND bh.SoThuTuBai = ?
                    ORDER BY
                        np.ThuTu,
                        np.MaNguPhap;
                    """,
                    COURSE_CODE,
                    LESSON_NO,
                )

                db_rows = (
                    cursor.fetchall()
                )

                if len(db_rows) != 7:

                    fail(
                        "Bai 1 khong con "
                        "dung 7 ngu phap."
                    )

                precheck_errors = []

                for row in db_rows:

                    grammar_id = int(
                        row[0]
                    )

                    if (
                        grammar_id
                        not in backup_by_id
                    ):

                        precheck_errors.append(
                            (
                                grammar_id,
                                "Khong co trong backup",
                            )
                        )

                        continue

                    backup = backup_by_id[
                        grammar_id
                    ]

                    checks = {
                        "MaBaiHoc": (
                            str(int(row[1])),
                            clean(
                                backup[
                                    "MaBaiHoc"
                                ]
                            ),
                        ),

                        "SoThuTuBai": (
                            str(int(row[2])),
                            clean(
                                backup[
                                    "SoThuTuBai"
                                ]
                            ),
                        ),

                        "TieuDeBai": (
                            clean(row[3]),
                            clean(
                                backup[
                                    "TieuDeBai"
                                ]
                            ),
                        ),

                        "TenCauTruc": (
                            clean(row[4]),
                            clean(
                                backup[
                                    "TenCauTruc"
                                ]
                            ),
                        ),

                        "MoTa": (
                            clean(row[5]),
                            clean(
                                backup["MoTa"]
                            ),
                        ),

                        "CachDung": (
                            clean(row[6]),
                            clean(
                                backup[
                                    "CachDung"
                                ]
                            ),
                        ),

                        "ViDuTiengTrung": (
                            clean(row[7]),
                            clean(
                                backup[
                                    "ViDuTiengTrung"
                                ]
                            ),
                        ),

                        "ViDuPinyin": (
                            clean(row[8]),
                            clean(
                                backup[
                                    "ViDuPinyin"
                                ]
                            ),
                        ),

                        "ViDuTiengViet": (
                            clean(row[9]),
                            clean(
                                backup[
                                    "ViDuTiengViet"
                                ]
                            ),
                        ),

                        "MaTep": (
                            (
                                ""
                                if row[10] is None
                                else str(
                                    int(row[10])
                                )
                            ),
                            normalize_nullable_int(
                                backup[
                                    "MaTep"
                                ]
                            ),
                        ),

                        "ThuTu": (
                            str(int(row[12])),
                            clean(
                                backup["ThuTu"]
                            ),
                        ),

                        "TrangThai": (
                            clean(row[13]),
                            clean(
                                backup[
                                    "TrangThai"
                                ]
                            ),
                        ),

                        "NgayTao": (
                            normalize_datetime(
                                row[14]
                            ),
                            normalize_datetime(
                                backup[
                                    "NgayTao"
                                ]
                            ),
                        ),
                    }

                    for (
                        column,
                        (
                            current_value,
                            backup_value,
                        ),
                    ) in checks.items():

                        if (
                            current_value
                            != backup_value
                        ):

                            precheck_errors.append(
                                (
                                    grammar_id,
                                    column,
                                    backup_value,
                                    current_value,
                                )
                            )

                    if row[11] is not None:

                        precheck_errors.append(
                            (
                                grammar_id,
                                "MaNguon",
                                "NULL",
                                row[11],
                            )
                        )

                print(
                    "Loi pre-check:",
                    len(precheck_errors),
                )

                if precheck_errors:

                    for error in (
                        precheck_errors[:30]
                    ):

                        print(
                            " ",
                            error,
                        )

                    fail(
                        "Database khong con "
                        "khop backup truoc apply."
                    )

                print(
                    "7/7 MaNguon hien tai: NULL"
                )

                print(
                    "PRE-CHECK: OK"
                )

                # =========================================
                # 8. UPDATE
                # =========================================
                print()
                print(
                    "[7] UPDATE TRONG TRANSACTION"
                )
                print("-" * 115)

                updated_ids = []

                for grammar_id in sorted(
                    review_by_id
                ):

                    backup = backup_by_id[
                        grammar_id
                    ]

                    cursor.execute(
                        """
                        UPDATE dbo.NguPhap
                        SET
                            MaNguon = ?
                        OUTPUT
                            INSERTED.MaNguPhap
                        WHERE
                            MaNguPhap = ?
                            AND MaNguon IS NULL
                            AND MaBaiHoc = ?
                            AND TenCauTruc = ?
                            AND ThuTu = ?
                            AND TrangThai = ?;
                        """,
                        TARGET_SOURCE_ID,
                        grammar_id,
                        int(
                            clean(
                                backup[
                                    "MaBaiHoc"
                                ]
                            )
                        ),
                        clean(
                            backup[
                                "TenCauTruc"
                            ]
                        ),
                        int(
                            clean(
                                backup[
                                    "ThuTu"
                                ]
                            )
                        ),
                        clean(
                            backup[
                                "TrangThai"
                            ]
                        ),
                    )

                    result = (
                        cursor.fetchone()
                    )

                    if result is None:

                        fail(
                            f"UPDATE that bai "
                            f"MaNguPhap="
                            f"{grammar_id}."
                        )

                    returned_id = int(
                        result[0]
                    )

                    if (
                        returned_id
                        != grammar_id
                    ):

                        fail(
                            "OUTPUT MaNguPhap "
                            "khong dung."
                        )

                    second_row = (
                        cursor.fetchone()
                    )

                    if (
                        second_row
                        is not None
                    ):

                        fail(
                            "UPDATE anh huong "
                            "nhieu hon 1 dong "
                            f"MaNguPhap="
                            f"{grammar_id}."
                        )

                    updated_ids.append(
                        grammar_id
                    )

                    print(
                        f"  Da update "
                        f"MaNguPhap="
                        f"{grammar_id}"
                    )

                if len(updated_ids) != 7:

                    fail(
                        "Khong UPDATE du "
                        "7 dong."
                    )

                print()
                print(
                    "UPDATE 7/7: OK"
                )

                # =========================================
                # 9. VERIFY BEFORE COMMIT
                # =========================================
                print()
                print(
                    "[8] VERIFY TRUOC COMMIT"
                )
                print("-" * 115)

                cursor.execute(
                    """
                    SELECT
                        np.MaNguPhap,
                        np.MaBaiHoc,
                        bh.SoThuTuBai,
                        bh.TieuDe,
                        np.TenCauTruc,
                        np.MoTa,
                        np.CachDung,
                        np.ViDuTiengTrung,
                        np.ViDuPinyin,
                        np.ViDuTiengViet,
                        np.MaTep,
                        np.MaNguon,
                        np.ThuTu,
                        np.TrangThai,
                        np.NgayTao
                    FROM dbo.NguPhap AS np
                    INNER JOIN dbo.BaiHoc AS bh
                        ON np.MaBaiHoc
                        = bh.MaBaiHoc
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc
                    WHERE
                        kh.MaKyHieu = ?
                        AND bh.SoThuTuBai = ?
                    ORDER BY
                        np.ThuTu,
                        np.MaNguPhap;
                    """,
                    COURSE_CODE,
                    LESSON_NO,
                )

                verify_rows = (
                    cursor.fetchall()
                )

                if len(verify_rows) != 7:

                    fail(
                        "Verify truoc COMMIT "
                        "khong co dung 7 dong."
                    )

                content_errors = []
                source_errors = []

                for row in verify_rows:

                    grammar_id = int(
                        row[0]
                    )

                    backup = backup_by_id[
                        grammar_id
                    ]

                    if (
                        row[11]
                        != TARGET_SOURCE_ID
                    ):

                        source_errors.append(
                            grammar_id
                        )

                    immutable_values = {
                        "MaBaiHoc": (
                            str(int(row[1])),
                            clean(
                                backup[
                                    "MaBaiHoc"
                                ]
                            ),
                        ),

                        "SoThuTuBai": (
                            str(int(row[2])),
                            clean(
                                backup[
                                    "SoThuTuBai"
                                ]
                            ),
                        ),

                        "TieuDeBai": (
                            clean(row[3]),
                            clean(
                                backup[
                                    "TieuDeBai"
                                ]
                            ),
                        ),

                        "TenCauTruc": (
                            clean(row[4]),
                            clean(
                                backup[
                                    "TenCauTruc"
                                ]
                            ),
                        ),

                        "MoTa": (
                            clean(row[5]),
                            clean(
                                backup["MoTa"]
                            ),
                        ),

                        "CachDung": (
                            clean(row[6]),
                            clean(
                                backup[
                                    "CachDung"
                                ]
                            ),
                        ),

                        "ViDuTiengTrung": (
                            clean(row[7]),
                            clean(
                                backup[
                                    "ViDuTiengTrung"
                                ]
                            ),
                        ),

                        "ViDuPinyin": (
                            clean(row[8]),
                            clean(
                                backup[
                                    "ViDuPinyin"
                                ]
                            ),
                        ),

                        "ViDuTiengViet": (
                            clean(row[9]),
                            clean(
                                backup[
                                    "ViDuTiengViet"
                                ]
                            ),
                        ),

                        "MaTep": (
                            (
                                ""
                                if row[10] is None
                                else str(
                                    int(row[10])
                                )
                            ),
                            normalize_nullable_int(
                                backup[
                                    "MaTep"
                                ]
                            ),
                        ),

                        "ThuTu": (
                            str(int(row[12])),
                            clean(
                                backup["ThuTu"]
                            ),
                        ),

                        "TrangThai": (
                            clean(row[13]),
                            clean(
                                backup[
                                    "TrangThai"
                                ]
                            ),
                        ),

                        "NgayTao": (
                            normalize_datetime(
                                row[14]
                            ),
                            normalize_datetime(
                                backup[
                                    "NgayTao"
                                ]
                            ),
                        ),
                    }

                    for (
                        column,
                        (
                            current_value,
                            backup_value,
                        ),
                    ) in immutable_values.items():

                        if (
                            current_value
                            != backup_value
                        ):

                            content_errors.append(
                                (
                                    grammar_id,
                                    column,
                                )
                            )

                print(
                    "Sai MaNguon:",
                    len(source_errors),
                )

                print(
                    "Cot khong duoc sua bi doi:",
                    len(content_errors),
                )

                if source_errors:

                    fail(
                        "Co dong chua "
                        "MaNguon=1004."
                    )

                if content_errors:

                    fail(
                        "Phat hien cot "
                        "khong duoc phep "
                        "bi thay doi."
                    )

                print(
                    "MaNguon=1004: 7/7"
                )

                print(
                    "VERIFY TRUOC COMMIT: OK"
                )

                # =========================================
                # 10. COMMIT
                # =========================================
                print()
                print(
                    "[9] COMMIT TRANSACTION"
                )
                print("-" * 115)

                connection.commit()

                committed = True

                print(
                    "COMMIT THANH CONG."
                )

                # =========================================
                # 11. VERIFY AFTER COMMIT
                # =========================================
                print()
                print(
                    "[10] VERIFY SAU COMMIT"
                )
                print("-" * 115)

                cursor.execute(
                    """
                    SELECT
                        COUNT(*)
                    FROM dbo.NguPhap AS np
                    INNER JOIN dbo.BaiHoc AS bh
                        ON np.MaBaiHoc
                        = bh.MaBaiHoc
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc
                    WHERE
                        kh.MaKyHieu = ?
                        AND bh.SoThuTuBai = ?
                        AND np.MaNguon = ?;
                    """,
                    COURSE_CODE,
                    LESSON_NO,
                    TARGET_SOURCE_ID,
                )

                source_count = int(
                    cursor.fetchone()[0]
                )

                cursor.execute(
                    """
                    SELECT
                        COUNT(*)
                    FROM dbo.NguPhap AS np
                    INNER JOIN dbo.BaiHoc AS bh
                        ON np.MaBaiHoc
                        = bh.MaBaiHoc
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc
                    WHERE
                        kh.MaKyHieu = ?
                        AND bh.SoThuTuBai = ?;
                    """,
                    COURSE_CODE,
                    LESSON_NO,
                )

                total_count = int(
                    cursor.fetchone()[0]
                )

                print(
                    "Tong ngu phap Bai 1:",
                    total_count,
                )

                print(
                    "MaNguon=1004:",
                    source_count,
                )

                if total_count != 7:

                    fail(
                        "Sau COMMIT Bai 1 "
                        "khong con dung 7 muc."
                    )

                if source_count != 7:

                    fail(
                        "Sau COMMIT khong co "
                        "du 7 MaNguon=1004."
                    )

                print(
                    "VERIFY SAU COMMIT: OK"
                )

                # =========================================
                # FINAL
                # =========================================
                print()
                print("=" * 115)
                print(
                    "KET QUA APPLY NGUON "
                    "NGU PHAP BAI 1"
                )
                print("=" * 115)

                print(
                    "Tong ngu phap Bai 1:",
                    7,
                )

                print(
                    "Da UPDATE:",
                    7,
                )

                print(
                    "MaNguon NULL -> 1004:",
                    7,
                )

                print(
                    "Cot khac bi thay doi:",
                    0,
                )

                print()
                print(
                    "DATABASE DA DUOC "
                    "CAP NHAT THANH CONG."
                )

                print()
                print(
                    "CHI 1 COT DA DUOC SUA:"
                )

                print(
                    "  MaNguon"
                )

                print()
                print(
                    "Backup truoc apply:"
                )

                print(
                    backup_file
                )

                print(
                    "SHA256 backup:"
                )

                print(
                    backup_hash
                )

                print()
                print(
                    "Snapshot review da apply:"
                )

                print(
                    snapshot_file
                )

                print(
                    "SHA256 snapshot:"
                )

                print(
                    snapshot_hash
                )

                print()
                print(
                    "CHUA INSERT NGU PHAP "
                    "BAI 2 -> 23."
                )

                print()
                print("=" * 115)
                print("HOAN TAT")
                print("=" * 115)

        except Exception:

            if not committed:

                try:

                    connection.rollback()

                    print()
                    print(
                        "TRANSACTION "
                        "DA ROLLBACK."
                    )

                    print(
                        "KHONG GIU LAI "
                        "UPDATE CHUA COMMIT."
                    )

                except Exception:
                    pass

            else:

                print()
                print(
                    "LUU Y:"
                )

                print(
                    "TRANSACTION DA COMMIT."
                )

                print(
                    "KHONG THE ROLLBACK "
                    "COMMIT CU BANG "
                    "TRANSACTION HIEN TAI."
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
        print("=" * 115)
        print(
            "09H8 APPLY THAT BAI"
        )
        print("=" * 115)

        print()
        print("Loi:")
        print(error)

        sys.exit(1)