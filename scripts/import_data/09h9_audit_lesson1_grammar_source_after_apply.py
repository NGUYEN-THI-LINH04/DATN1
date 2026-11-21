from pathlib import Path
import csv
import hashlib
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
# CONFIG
# =========================================================
COURSE_CODE = "HSK1-CORE"
LESSON_NO = 1

EXPECTED_ROWS = 7
EXPECTED_SOURCE_ID = 1004
EXPECTED_SOURCE_NAME = "GF0025-2021 - Ngữ pháp HSK"


# =========================================================
# FILES
# =========================================================
BACKUP_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "db_backup"
    / "hsk1_lesson1_grammar_before_source_apply_20260929_143324.csv"
)

SNAPSHOT_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "db_backup"
    / "hsk1_lesson1_grammar_mapping_applied_20260929_143708.csv"
)


EXPECTED_BACKUP_SHA256 = (
    "954abc4d214ec66d032e20be737e88b3141bda53bb6efe4d03657d1f132218dc"
)

EXPECTED_SNAPSHOT_SHA256 = (
    "1b337dd158bb7f32b7ebe60b2e97ac1d4eb669fad017c2cec81c6980a674d3f3"
)


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


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 115)
    print(
        "09H9 - AUDIT NGU PHAP BAI 1 "
        "SAU KHI GAN MaNguon=1004"
    )
    print("=" * 115)

    print()
    print("CHE DO:")
    print("  CHI DOC FILE")
    print("  CHI SELECT DATABASE")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    # =====================================================
    # 1. VERIFY BACKUP
    # =====================================================
    print()
    print("[1] VERIFY BACKUP TRUOC APPLY")
    print("-" * 115)

    if not BACKUP_FILE.exists():

        fail(
            "Khong tim thay backup:\n"
            f"{BACKUP_FILE}"
        )

    backup_hash = sha256_file(
        BACKUP_FILE
    )

    print("Backup:")
    print(BACKUP_FILE)

    print()
    print("SHA256:")
    print(backup_hash)

    if (
        backup_hash
        != EXPECTED_BACKUP_SHA256
    ):

        fail(
            "SHA256 backup bi thay doi."
        )

    backup_fields, backup_rows = load_csv(
        BACKUP_FILE
    )

    if len(backup_rows) != EXPECTED_ROWS:

        fail(
            "Backup khong co dung 7 dong."
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

    print(
        "Tong dong backup:",
        len(backup_rows),
    )

    print(
        "MaNguon=NULL:",
        sum(
            1
            for row in backup_rows
            if clean(
                row["MaNguon"]
            ) == ""
        ),
    )

    print(
        "BACKUP: OK"
    )

    # =====================================================
    # 2. VERIFY SNAPSHOT
    # =====================================================
    print()
    print("[2] VERIFY SNAPSHOT REVIEW DA APPLY")
    print("-" * 115)

    if not SNAPSHOT_FILE.exists():

        fail(
            "Khong tim thay snapshot:\n"
            f"{SNAPSHOT_FILE}"
        )

    snapshot_hash = sha256_file(
        SNAPSHOT_FILE
    )

    print("Snapshot:")
    print(SNAPSHOT_FILE)

    print()
    print("SHA256:")
    print(snapshot_hash)

    if (
        snapshot_hash
        != EXPECTED_SNAPSHOT_SHA256
    ):

        fail(
            "SHA256 snapshot bi thay doi."
        )

    snapshot_fields, snapshot_rows = load_csv(
        SNAPSHOT_FILE
    )

    required_snapshot_fields = {
        "MaNguPhap",
        "TenCauTruc",
        "MaNguonHienTai",
        "MaNguonDeXuat",
        "MaMucNguPhapChuan",
        "DaKiemDuyetMapping",
        "GhiChuKiemDuyet",
    }

    missing_snapshot_fields = (
        required_snapshot_fields
        - set(snapshot_fields)
    )

    if missing_snapshot_fields:

        fail(
            "Snapshot thieu cot: "
            + ", ".join(
                sorted(
                    missing_snapshot_fields
                )
            )
        )

    if len(snapshot_rows) != EXPECTED_ROWS:

        fail(
            "Snapshot khong co dung 7 dong."
        )

    snapshot_by_id = {}

    for row in snapshot_rows:

        grammar_id = int(
            clean(
                row["MaNguPhap"]
            )
        )

        if grammar_id in snapshot_by_id:

            fail(
                "MaNguPhap bi trung "
                "trong snapshot."
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
            != "1004"
        ):

            fail(
                f"MaNguPhap={grammar_id} "
                "khong de xuat MaNguon=1004."
            )

        snapshot_by_id[
            grammar_id
        ] = row

    if (
        set(snapshot_by_id)
        != set(backup_by_id)
    ):

        fail(
            "MaNguPhap snapshot "
            "khong khop backup."
        )

    print(
        "Tong mapping:",
        len(snapshot_rows),
    )

    print(
        "DaKiemDuyetMapping=1:",
        sum(
            1
            for row in snapshot_rows
            if clean(
                row[
                    "DaKiemDuyetMapping"
                ]
            )
            == "1"
        ),
    )

    print(
        "MaNguonDeXuat=1004:",
        sum(
            1
            for row in snapshot_rows
            if clean(
                row[
                    "MaNguonDeXuat"
                ]
            )
            == "1004"
        ),
    )

    print(
        "SNAPSHOT: OK"
    )

    # =====================================================
    # 3. CONNECT DATABASE
    # =====================================================
    print()
    print("[3] KET NOI DATABASE")
    print("-" * 115)

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
                # 4. VERIFY SOURCE
                # =========================================
                print()
                print(
                    "[4] VERIFY MaNguon=1004"
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
                    EXPECTED_SOURCE_ID,
                )

                source_row = (
                    cursor.fetchone()
                )

                if source_row is None:

                    fail(
                        "Khong tim thay "
                        "MaNguon=1004."
                    )

                source_id = int(
                    source_row[0]
                )

                source_name = clean(
                    source_row[1]
                )

                print(
                    "MaNguon:",
                    source_id,
                )

                print(
                    "Ten:",
                    source_name,
                )

                if (
                    source_id
                    != EXPECTED_SOURCE_ID
                ):

                    fail(
                        "Sai MaNguon."
                    )

                if (
                    source_name
                    != EXPECTED_SOURCE_NAME
                ):

                    fail(
                        "Sai Ten nguon."
                    )

                print(
                    "NGUON: OK"
                )

                # =========================================
                # 5. READ DB
                # =========================================
                print()
                print(
                    "[5] DOC 7 NGU PHAP BAI 1"
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
                        "Bai 1 khong co "
                        "dung 7 ngu phap."
                    )

                print(
                    "Tong dong:",
                    len(db_rows),
                )

                # =========================================
                # 6. AUDIT MaNguon
                # =========================================
                print()
                print(
                    "[6] KIEM TRA MaNguon "
                    "SAU APPLY"
                )
                print("-" * 115)

                source_errors = []

                for row in db_rows:

                    grammar_id = int(
                        row[0]
                    )

                    if (
                        row[11]
                        != EXPECTED_SOURCE_ID
                    ):

                        source_errors.append(
                            grammar_id
                        )

                print(
                    "MaNguon=1004:",
                    (
                        len(db_rows)
                        - len(source_errors)
                    ),
                )

                print(
                    "Sai MaNguon:",
                    len(source_errors),
                )

                if source_errors:

                    print(
                        "ID sai:",
                        source_errors,
                    )

                    fail(
                        "Co ngu phap "
                        "khong MaNguon=1004."
                    )

                print(
                    "MaNguon: OK"
                )

                # =========================================
                # 7. AUDIT IMMUTABLE FIELDS
                # =========================================
                print()
                print(
                    "[7] KIEM TRA CAC COT "
                    "KHONG DUOC SUA"
                )
                print("-" * 115)

                immutable_errors = []

                for row in db_rows:

                    grammar_id = int(
                        row[0]
                    )

                    if (
                        grammar_id
                        not in backup_by_id
                    ):

                        immutable_errors.append(
                            (
                                grammar_id,
                                "Khong co backup",
                            )
                        )

                        continue

                    backup = backup_by_id[
                        grammar_id
                    ]

                    values = {
                        "MaNguPhap": (
                            str(grammar_id),
                            clean(
                                backup[
                                    "MaNguPhap"
                                ]
                            ),
                        ),

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
                                backup[
                                    "MoTa"
                                ]
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
                                backup[
                                    "ThuTu"
                                ]
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
                            clean(row[14]),
                            clean(
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
                    ) in values.items():

                        if (
                            current_value
                            != backup_value
                        ):

                            immutable_errors.append(
                                (
                                    grammar_id,
                                    column,
                                    backup_value,
                                    current_value,
                                )
                            )

                print(
                    "Cot khong duoc sua "
                    "bi thay doi:",
                    len(
                        immutable_errors
                    ),
                )

                if immutable_errors:

                    for error in (
                        immutable_errors[:30]
                    ):

                        print(
                            " ",
                            error,
                        )

                    fail(
                        "Phat hien du lieu "
                        "ngoai MaNguon bi thay doi."
                    )

                print(
                    "CAC COT BAT BIEN: OK"
                )

                # =========================================
                # 8. VERIFY WITH SNAPSHOT
                # =========================================
                print()
                print(
                    "[8] DOI CHIEU DATABASE "
                    "VOI SNAPSHOT REVIEW"
                )
                print("-" * 115)

                mapping_errors = []

                for row in db_rows:

                    grammar_id = int(
                        row[0]
                    )

                    snapshot = (
                        snapshot_by_id[
                            grammar_id
                        ]
                    )

                    if (
                        clean(row[4])
                        != clean(
                            snapshot[
                                "TenCauTruc"
                            ]
                        )
                    ):

                        mapping_errors.append(
                            (
                                grammar_id,
                                "TenCauTruc",
                            )
                        )

                    if (
                        clean(
                            snapshot[
                                "MaNguonDeXuat"
                            ]
                        )
                        != "1004"
                    ):

                        mapping_errors.append(
                            (
                                grammar_id,
                                "MaNguonDeXuat",
                            )
                        )

                    if (
                        clean(
                            snapshot[
                                "DaKiemDuyetMapping"
                            ]
                        )
                        != "1"
                    ):

                        mapping_errors.append(
                            (
                                grammar_id,
                                "DaKiemDuyetMapping",
                            )
                        )

                print(
                    "Loi doi chieu snapshot:",
                    len(
                        mapping_errors
                    ),
                )

                if mapping_errors:

                    fail(
                        "Database khong khop "
                        "snapshot review."
                    )

                print(
                    "DATABASE <-> SNAPSHOT: OK"
                )

                # =========================================
                # 9. PRINT 7 ITEMS
                # =========================================
                print()
                print(
                    "[9] DANH SACH 7 NGU PHAP "
                    "SAU APPLY"
                )
                print("-" * 115)

                for row in db_rows:

                    print(
                        f"[{int(row[12])}] "
                        f"MaNguPhap="
                        f"{int(row[0])} | "
                        f"{clean(row[4])} | "
                        f"MaNguon="
                        f"{int(row[11])}"
                    )

                # =========================================
                # FINAL
                # =========================================
                print()
                print("=" * 115)
                print(
                    "KET QUA AUDIT SAU APPLY"
                )
                print("=" * 115)

                print(
                    "Tong ngu phap Bai 1:",
                    len(db_rows),
                )

                print(
                    "MaNguon=1004:",
                    len(db_rows),
                )

                print(
                    "Sai MaNguon:",
                    len(source_errors),
                )

                print(
                    "Cot khac bi thay doi:",
                    len(
                        immutable_errors
                    ),
                )

                print(
                    "Loi snapshot:",
                    len(
                        mapping_errors
                    ),
                )

                print()
                print(
                    "AUDIT SAU APPLY "
                    "THANH CONG."
                )

                print(
                    "7/7 NGU PHAP BAI 1 "
                    "DA GAN MaNguon=1004."
                )

                print(
                    "KHONG CO COT NAO KHAC "
                    "BI THAY DOI."
                )

                print()
                print(
                    "SCRIPT NAY CHI SELECT."
                )

                print(
                    "DATABASE KHONG BI SUA."
                )

                print()
                print("=" * 115)
                print("HOAN TAT")
                print("=" * 115)

        finally:

            try:
                connection.rollback()
            except Exception:
                pass


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
            "09H9 AUDIT THAT BAI"
        )
        print("=" * 115)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "SCRIPT NAY CHI SELECT."
        )

        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)