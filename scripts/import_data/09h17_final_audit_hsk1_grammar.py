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

EXPECTED_TOTAL = 88
EXPECTED_SOURCE_ID = 1004
EXPECTED_SOURCE_NAME = "GF0025-2021 - Ngữ pháp HSK"

EXPECTED_COUNTS = {
    1: 7,
    2: 3,
    3: 4,
    4: 3,
    5: 3,
    6: 3,
    7: 4,
    8: 3,
    9: 3,
    10: 4,
    11: 4,
    12: 3,
    13: 4,
    14: 4,
    15: 4,
    16: 3,
    17: 4,
    18: 4,
    19: 4,
    20: 4,
    21: 4,
    22: 5,
    23: 4,
}


# =========================================================
# FILES
# =========================================================
BACKUP_BEFORE_INSERT = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "db_backup"
    / "hsk1_grammar_before_lessons3_23_insert_20260929_152919.csv"
)

CONTENT_APPLIED = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "db_backup"
    / "hsk1_lessons3_23_grammar_content_applied_20260929_152919.csv"
)

DB_AFTER_INSERT = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "db_backup"
    / "hsk1_lessons3_23_grammar_inserted_20260929_152919.csv"
)


EXPECTED_BACKUP_HASH = (
    "af25f3ccd6d6f6bf76251ac072a1a92659dda20b9d98717e9eca9fc51c93ce51"
)

EXPECTED_CONTENT_HASH = (
    "3323b989baec2aebae3c8cd1efa1ff38db8120762a89a6f5dcd4fae0cdc0babc"
)

EXPECTED_DB_AFTER_HASH = (
    "8c5b0517913dcded63a2d9b095857fa716a3a361c3073f6af16b226ce194432b"
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


def line():

    print("-" * 120)


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


def db_text(value):

    if value is None:
        return ""

    if hasattr(value, "isoformat"):

        return value.isoformat(
            sep=" "
        )

    return str(value)


def db_row_to_dict(row):

    return {
        "MaNguPhap": db_text(row[0]),
        "MaBaiHoc": db_text(row[1]),
        "SoThuTuBai": db_text(row[2]),
        "TieuDeBai": db_text(row[3]),
        "TenCauTruc": db_text(row[4]),
        "MoTa": db_text(row[5]),
        "CachDung": db_text(row[6]),
        "ViDuTiengTrung": db_text(row[7]),
        "ViDuPinyin": db_text(row[8]),
        "ViDuTiengViet": db_text(row[9]),
        "MaTep": db_text(row[10]),
        "MaNguon": db_text(row[11]),
        "ThuTu": db_text(row[12]),
        "TrangThai": db_text(row[13]),
        "NgayTao": db_text(row[14]),
    }


def select_grammar(
    cursor,
    start_lesson,
    end_lesson,
):

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
            ON np.MaBaiHoc = bh.MaBaiHoc
        INNER JOIN dbo.KhoaHoc AS kh
            ON bh.MaKhoaHoc = kh.MaKhoaHoc
        WHERE
            kh.MaKyHieu = ?
            AND bh.SoThuTuBai
                BETWEEN ? AND ?
        ORDER BY
            bh.SoThuTuBai,
            np.ThuTu,
            np.MaNguPhap;
        """,
        COURSE_CODE,
        start_lesson,
        end_lesson,
    )

    return cursor.fetchall()


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "09H17 - FINAL AUDIT TOAN BO "
        "NGU PHAP HSK1 BAI 1 -> 23"
    )
    print("=" * 120)

    print()
    print("CHE DO:")
    print("  CHI DOC FILE BACKUP / SNAPSHOT")
    print("  CHI SELECT DATABASE")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    # =====================================================
    # 1. VERIFY FILE EXISTS
    # =====================================================
    print()
    print("[1] VERIFY 3 FILE DOI CHUNG")
    line()

    for path in [
        BACKUP_BEFORE_INSERT,
        CONTENT_APPLIED,
        DB_AFTER_INSERT,
    ]:

        if not path.exists():

            fail(
                "Khong tim thay file:\n"
                f"{path}"
            )

        print(
            "OK:",
            path,
        )

    # =====================================================
    # 2. VERIFY HASH
    # =====================================================
    print()
    print("[2] VERIFY SHA256")
    line()

    backup_hash = sha256_file(
        BACKUP_BEFORE_INSERT
    )

    content_hash = sha256_file(
        CONTENT_APPLIED
    )

    db_after_hash = sha256_file(
        DB_AFTER_INSERT
    )

    print(
        "Backup before INSERT:"
    )
    print(
        backup_hash
    )

    print()
    print(
        "Content applied:"
    )
    print(
        content_hash
    )

    print()
    print(
        "DB after INSERT:"
    )
    print(
        db_after_hash
    )

    if (
        backup_hash
        != EXPECTED_BACKUP_HASH
    ):

        fail(
            "SHA256 backup truoc INSERT "
            "bi thay doi."
        )

    if (
        content_hash
        != EXPECTED_CONTENT_HASH
    ):

        fail(
            "SHA256 content applied "
            "bi thay doi."
        )

    if (
        db_after_hash
        != EXPECTED_DB_AFTER_HASH
    ):

        fail(
            "SHA256 snapshot DB sau INSERT "
            "bi thay doi."
        )

    print()
    print(
        "3/3 SHA256: OK"
    )

    # =====================================================
    # 3. READ BACKUP OLD 10
    # =====================================================
    print()
    print(
        "[3] DOC BACKUP 10 NGU PHAP "
        "BAI 1 + 2"
    )
    line()

    backup_fields, backup_rows = load_csv(
        BACKUP_BEFORE_INSERT
    )

    if len(backup_rows) != 10:

        fail(
            "Backup truoc INSERT "
            "phai co dung 10 dong."
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
                "Backup bi trung MaNguPhap."
            )

        backup_by_id[
            grammar_id
        ] = row

    print(
        "Tong backup:",
        len(backup_rows),
    )

    print(
        "Bai 1 + 2 backup: OK"
    )

    # =====================================================
    # 4. READ APPROVED CONTENT 78
    # =====================================================
    print()
    print(
        "[4] DOC CONTENT DA APPLY 78 DONG"
    )
    line()

    content_fields, content_rows = load_csv(
        CONTENT_APPLIED
    )

    if len(content_rows) != 78:

        fail(
            "Content applied "
            "phai co dung 78 dong."
        )

    content_by_key = {}

    for row in content_rows:

        lesson_no = int(
            clean(
                row[
                    "SoThuTuBai"
                ]
            )
        )

        order_no = int(
            clean(
                row[
                    "ThuTuTrongBai"
                ]
            )
        )

        key = (
            lesson_no,
            order_no,
        )

        if key in content_by_key:

            fail(
                f"Content trung key: {key}"
            )

        if (
            clean(
                row[
                    "DaKiemDuyetNoiDung"
                ]
            )
            != "1"
        ):

            fail(
                f"{key} chua duoc "
                "kiem duyet."
            )

        content_by_key[
            key
        ] = row

    print(
        "Tong content:",
        len(content_rows),
    )

    print(
        "DaKiemDuyetNoiDung=1:",
        len(content_rows),
    )

    # =====================================================
    # 5. READ DB SNAPSHOT 78
    # =====================================================
    print()
    print(
        "[5] DOC SNAPSHOT DB SAU INSERT"
    )
    line()

    snapshot_fields, snapshot_rows = load_csv(
        DB_AFTER_INSERT
    )

    if len(snapshot_rows) != 78:

        fail(
            "Snapshot DB sau INSERT "
            "phai co dung 78 dong."
        )

    snapshot_by_id = {}

    snapshot_by_key = {}

    for row in snapshot_rows:

        grammar_id = int(
            clean(
                row["MaNguPhap"]
            )
        )

        lesson_no = int(
            clean(
                row[
                    "SoThuTuBai"
                ]
            )
        )

        order_no = int(
            clean(
                row["ThuTu"]
            )
        )

        key = (
            lesson_no,
            order_no,
        )

        if grammar_id in snapshot_by_id:

            fail(
                "Snapshot DB "
                "trung MaNguPhap."
            )

        if key in snapshot_by_key:

            fail(
                f"Snapshot DB trung key: {key}"
            )

        snapshot_by_id[
            grammar_id
        ] = row

        snapshot_by_key[
            key
        ] = row

    print(
        "Tong snapshot:",
        len(snapshot_rows),
    )

    print(
        "Snapshot 78 dong: OK"
    )

    # =====================================================
    # 6. CONTENT <-> DB SNAPSHOT
    # =====================================================
    print()
    print(
        "[6] DOI CHIEU CONTENT "
        "VOI SNAPSHOT DB"
    )
    line()

    if (
        set(content_by_key)
        != set(snapshot_by_key)
    ):

        fail(
            "Key content khong khop "
            "snapshot DB."
        )

    snapshot_content_errors = []

    for key in sorted(
        content_by_key
    ):

        content = (
            content_by_key[
                key
            ]
        )

        snapshot = (
            snapshot_by_key[
                key
            ]
        )

        comparisons = {
            "MaBaiHoc": (
                clean(
                    snapshot[
                        "MaBaiHoc"
                    ]
                ),
                clean(
                    content[
                        "MaBaiHoc"
                    ]
                ),
            ),

            "TieuDeBai": (
                clean(
                    snapshot[
                        "TieuDeBai"
                    ]
                ),
                clean(
                    content[
                        "TieuDeBai"
                    ]
                ),
            ),

            "TenCauTruc": (
                clean(
                    snapshot[
                        "TenCauTruc"
                    ]
                ),
                clean(
                    content[
                        "TenCauTruc"
                    ]
                ),
            ),

            "MoTa": (
                clean(
                    snapshot["MoTa"]
                ),
                clean(
                    content["MoTa"]
                ),
            ),

            "CachDung": (
                clean(
                    snapshot[
                        "CachDung"
                    ]
                ),
                clean(
                    content[
                        "CachDung"
                    ]
                ),
            ),

            "ViDuTiengTrung": (
                clean(
                    snapshot[
                        "ViDuTiengTrung"
                    ]
                ),
                clean(
                    content[
                        "ViDuTiengTrung"
                    ]
                ),
            ),

            "ViDuPinyin": (
                clean(
                    snapshot[
                        "ViDuPinyin"
                    ]
                ),
                clean(
                    content[
                        "ViDuPinyin"
                    ]
                ),
            ),

            "ViDuTiengViet": (
                clean(
                    snapshot[
                        "ViDuTiengViet"
                    ]
                ),
                clean(
                    content[
                        "ViDuTiengViet"
                    ]
                ),
            ),

            "MaNguon": (
                clean(
                    snapshot[
                        "MaNguon"
                    ]
                ),
                "1004",
            ),

            "TrangThai": (
                clean(
                    snapshot[
                        "TrangThai"
                    ]
                ),
                "ban_nhap",
            ),
        }

        for (
            field,
            (
                actual,
                expected,
            ),
        ) in comparisons.items():

            if actual != expected:

                snapshot_content_errors.append(
                    (
                        key,
                        field,
                    )
                )

        if (
            clean(
                snapshot["MaTep"]
            )
            != ""
        ):

            snapshot_content_errors.append(
                (
                    key,
                    "MaTep",
                )
            )

    print(
        "Loi content <-> snapshot:",
        len(
            snapshot_content_errors
        ),
    )

    if snapshot_content_errors:

        for error in (
            snapshot_content_errors[:50]
        ):

            print(
                " ",
                error,
            )

        fail(
            "Snapshot DB khong khop "
            "content da duyet."
        )

    print(
        "78/78 CONTENT KHOP SNAPSHOT DB."
    )

    # =====================================================
    # 7. CONNECT DATABASE
    # =====================================================
    print()
    print("[7] KET NOI DATABASE")
    line()

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

                # =========================================
                # SOURCE
                # =========================================
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

                if (
                    clean(
                        source_row[1]
                    )
                    != EXPECTED_SOURCE_NAME
                ):

                    fail(
                        "Sai Ten MaNguon=1004."
                    )

                # =========================================
                # CURRENT ALL 88
                # =========================================
                print()
                print(
                    "[8] DOC TOAN BO "
                    "NGU PHAP HSK1"
                )
                line()

                current_rows = (
                    select_grammar(
                        cursor,
                        1,
                        23,
                    )
                )

                if (
                    len(current_rows)
                    != EXPECTED_TOTAL
                ):

                    fail(
                        "Tong ngu phap HSK1 "
                        "khong bang 88. "
                        f"Thuc te: "
                        f"{len(current_rows)}"
                    )

                counts = {}

                for row in current_rows:

                    lesson_no = int(
                        row[2]
                    )

                    counts[
                        lesson_no
                    ] = (
                        counts.get(
                            lesson_no,
                            0,
                        )
                        + 1
                    )

                count_errors = []

                for lesson_no in range(
                    1,
                    24,
                ):

                    actual = (
                        counts.get(
                            lesson_no,
                            0,
                        )
                    )

                    expected = (
                        EXPECTED_COUNTS[
                            lesson_no
                        ]
                    )

                    if actual != expected:

                        count_errors.append(
                            (
                                lesson_no,
                                actual,
                                expected,
                            )
                        )

                    print(
                        f"Bai {lesson_no:>2}: "
                        f"{actual} muc"
                    )

                if count_errors:

                    fail(
                        "Sai so luong ngu phap "
                        "theo bai."
                    )

                print()
                print(
                    "23/23 BAI DUNG SO LUONG."
                )

                # =========================================
                # 9. VERIFY OLD 10 UNCHANGED
                # =========================================
                print()
                print(
                    "[9] VERIFY BAI 1 + 2 "
                    "KHONG BI THAY DOI"
                )
                line()

                current_old = (
                    select_grammar(
                        cursor,
                        1,
                        2,
                    )
                )

                if len(current_old) != 10:

                    fail(
                        "Bai 1 + 2 "
                        "khong con 10 dong."
                    )

                old_errors = []

                for row in current_old:

                    current = (
                        db_row_to_dict(
                            row
                        )
                    )

                    grammar_id = int(
                        current[
                            "MaNguPhap"
                        ]
                    )

                    before = (
                        backup_by_id.get(
                            grammar_id
                        )
                    )

                    if before is None:

                        old_errors.append(
                            (
                                grammar_id,
                                "khong co backup",
                            )
                        )

                        continue

                    for field in [
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
                    ]:

                        if (
                            clean(
                                current[
                                    field
                                ]
                            )
                            != clean(
                                before[
                                    field
                                ]
                            )
                        ):

                            old_errors.append(
                                (
                                    grammar_id,
                                    field,
                                )
                            )

                print(
                    "Loi Bai 1 + 2:",
                    len(old_errors),
                )

                if old_errors:

                    for error in (
                        old_errors[:50]
                    ):

                        print(
                            " ",
                            error,
                        )

                    fail(
                        "Bai 1 + 2 "
                        "bi thay doi."
                    )

                print(
                    "10/10 DONG CU KHONG DOI."
                )

                # =========================================
                # 10. VERIFY CURRENT NEW 78
                # =========================================
                print()
                print(
                    "[10] VERIFY 78 DONG "
                    "BAI 3 -> 23 VOI SNAPSHOT"
                )
                line()

                current_new = (
                    select_grammar(
                        cursor,
                        3,
                        23,
                    )
                )

                if len(current_new) != 78:

                    fail(
                        "Bai 3 -> 23 "
                        "khong con 78 dong."
                    )

                current_by_id = {
                    int(
                        row[0]
                    ): db_row_to_dict(
                        row
                    )
                    for row in current_new
                }

                if (
                    set(current_by_id)
                    != set(snapshot_by_id)
                ):

                    fail(
                        "Tap MaNguPhap hien tai "
                        "khong khop snapshot."
                    )

                current_snapshot_errors = []

                for grammar_id in sorted(
                    current_by_id
                ):

                    current = (
                        current_by_id[
                            grammar_id
                        ]
                    )

                    snapshot = (
                        snapshot_by_id[
                            grammar_id
                        ]
                    )

                    for field in [
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
                    ]:

                        if (
                            clean(
                                current[
                                    field
                                ]
                            )
                            != clean(
                                snapshot[
                                    field
                                ]
                            )
                        ):

                            current_snapshot_errors.append(
                                (
                                    grammar_id,
                                    field,
                                )
                            )

                print(
                    "Loi current <-> snapshot:",
                    len(
                        current_snapshot_errors
                    ),
                )

                if current_snapshot_errors:

                    for error in (
                        current_snapshot_errors[:50]
                    ):

                        print(
                            " ",
                            error,
                        )

                    fail(
                        "78 dong hien tai "
                        "khong khop snapshot "
                        "sau INSERT."
                    )

                print(
                    "78/78 DONG MOI "
                    "KHOP SNAPSHOT."
                )

                # =========================================
                # 11. GLOBAL SOURCE / STATUS
                # =========================================
                print()
                print(
                    "[11] KIEM TRA NGUON "
                    "VA TRANG THAI"
                )
                line()

                source_1004_count = sum(
                    1
                    for row in current_rows
                    if row[11] == 1004
                )

                draft_count = sum(
                    1
                    for row in current_rows
                    if clean(
                        row[13]
                    ) == "ban_nhap"
                )

                null_media_count = sum(
                    1
                    for row in current_rows
                    if row[10] is None
                )

                print(
                    "Tong HSK1:",
                    len(current_rows),
                )

                print(
                    "MaNguon=1004:",
                    source_1004_count,
                )

                print(
                    "TrangThai=ban_nhap:",
                    draft_count,
                )

                print(
                    "MaTep=NULL:",
                    null_media_count,
                )

                if (
                    source_1004_count
                    != 88
                ):

                    fail(
                        "Khong phai 88/88 "
                        "MaNguon=1004."
                    )

                if draft_count != 88:

                    fail(
                        "Khong phai 88/88 "
                        "TrangThai=ban_nhap."
                    )

                if (
                    null_media_count
                    != 88
                ):

                    fail(
                        "Khong phai 88/88 "
                        "MaTep=NULL."
                    )

                # =========================================
                # FINAL
                # =========================================
                print()
                print("=" * 120)
                print(
                    "KET QUA 09H17"
                )
                print("=" * 120)

                print(
                    "Tong ngu phap HSK1:",
                    88,
                )

                print(
                    "So bai:",
                    23,
                )

                print(
                    "Bai 1:",
                    7,
                )

                print(
                    "Bai 2:",
                    3,
                )

                print(
                    "Bai 3 -> 23:",
                    78,
                )

                print(
                    "23/23 bai dung so luong:",
                    "YES",
                )

                print(
                    "Bai 1 + 2 bi thay doi:",
                    0,
                )

                print(
                    "78 dong moi sai snapshot:",
                    0,
                )

                print(
                    "78 dong moi sai content da duyet:",
                    0,
                )

                print(
                    "MaNguon=1004:",
                    88,
                )

                print(
                    "TrangThai=ban_nhap:",
                    88,
                )

                print(
                    "MaTep=NULL:",
                    88,
                )

                print()
                print(
                    "FINAL AUDIT NGU PHAP "
                    "HSK1 THANH CONG."
                )

                print(
                    "TOAN BO NGU PHAP "
                    "BAI 1 -> 23 DA DUOC "
                    "DOI CHIEU VA KHOA LAI."
                )

                print()
                print(
                    "SCRIPT NAY CHI SELECT."
                )

                print(
                    "DATABASE KHONG BI SUA."
                )

                print()
                print("=" * 120)
                print("HOAN TAT")
                print("=" * 120)

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
        print("=" * 120)
        print(
            "09H17 FINAL AUDIT THAT BAI"
        )
        print("=" * 120)

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