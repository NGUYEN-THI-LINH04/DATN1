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

START_LESSON = 3
END_LESSON = 23

EXPECTED_NEW_ROWS = 78
EXPECTED_OLD_ROWS = 10
EXPECTED_TOTAL_AFTER = 88

SOURCE_ID = 1004
SOURCE_NAME = "GF0025-2021 - Ngữ pháp HSK"

EXPECTED_CONTENT_SHA256 = (
    "3323b989baec2aebae3c8cd1efa1ff38db8120762a89a6f5dcd4fae0cdc0babc"
)

EXPECTED_COUNTS = {
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
CONTENT_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "hsk1_lessons3_23_grammar_content_review.csv"
)

DB_BACKUP_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "db_backup"
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


def db_text(value):

    if value is None:
        return ""

    if hasattr(value, "isoformat"):

        return value.isoformat(
            sep=" "
        )

    return str(value)


def grammar_row_to_dict(row):

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


def write_db_snapshot(
    path,
    rows,
):

    fieldnames = [
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
    ]

    with open(
        path,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in rows:

            writer.writerow(
                grammar_row_to_dict(
                    row
                )
            )


def select_hsk1_grammar(
    cursor,
    start_lesson=1,
    end_lesson=23,
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
        "09H16 - BACKUP + INSERT "
        "NGU PHAP HSK1 BAI 3 -> 23"
    )
    print("=" * 120)

    print()
    print("BUOC NAY SE:")
    print("  1. VERIFY FILE NOI DUNG DA KIEM DUYET")
    print("  2. VERIFY DATABASE HIEN TAI")
    print("  3. BACKUP 10 NGU PHAP BAI 1 + 2")
    print("  4. DONG BANG FILE NOI DUNG 78 DONG")
    print("  5. INSERT 78 DONG TRONG 1 TRANSACTION")
    print("  6. VERIFY TRUOC COMMIT")
    print("  7. COMMIT")
    print("  8. AUDIT SAU COMMIT")
    print("  9. TAO SNAPSHOT DATABASE SAU INSERT")

    # =====================================================
    # 1. VERIFY CONTENT FILE
    # =====================================================
    print()
    print("[1] VERIFY FILE CONTENT REVIEW")
    line()

    if not CONTENT_FILE.exists():

        fail(
            "Khong tim thay file:\n"
            f"{CONTENT_FILE}"
        )

    content_hash = sha256_file(
        CONTENT_FILE
    )

    print(
        "SHA256 hien tai:"
    )

    print(
        content_hash
    )

    print()
    print(
        "SHA256 mong doi:"
    )

    print(
        EXPECTED_CONTENT_SHA256
    )

    if (
        content_hash
        != EXPECTED_CONTENT_SHA256
    ):

        fail(
            "File content da thay doi "
            "sau 09h15."
        )

    fields, rows = load_csv(
        CONTENT_FILE
    )

    if len(rows) != EXPECTED_NEW_ROWS:

        fail(
            "Content phai co dung "
            "78 dong."
        )

    required_fields = {
        "SoThuTuBai",
        "MaBaiHoc",
        "TieuDeBai",
        "ThuTuTrongBai",
        "MaMucNguPhapChuan",
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
        "MaNguon",
        "MaTep",
        "TrangThai",
        "DaKiemDuyetNoiDung",
        "GhiChuKiemDuyet",
    }

    missing_fields = (
        required_fields
        - set(fields)
    )

    if missing_fields:

        fail(
            "Content thieu cot: "
            + ", ".join(
                sorted(
                    missing_fields
                )
            )
        )

    content_by_key = {}

    for row in rows:

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
                f"Trung key content: {key}"
            )

        if (
            lesson_no < 3
            or lesson_no > 23
        ):

            fail(
                f"Bai ngoai pham vi: "
                f"{lesson_no}"
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
                f"{key} chua "
                "DaKiemDuyetNoiDung=1."
            )

        if (
            clean(
                row["MaNguon"]
            )
            != "1004"
        ):

            fail(
                f"{key} "
                "khong MaNguon=1004."
            )

        if (
            clean(
                row["TrangThai"]
            )
            != "ban_nhap"
        ):

            fail(
                f"{key} "
                "khong ban_nhap."
            )

        if (
            clean(
                row["MaTep"]
            )
            != ""
        ):

            fail(
                f"{key} "
                "MaTep phai rong."
            )

        for field in [
            "TenCauTruc",
            "MoTa",
            "CachDung",
            "ViDuTiengTrung",
            "ViDuPinyin",
            "ViDuTiengViet",
        ]:

            if not clean(
                row[field]
            ):

                fail(
                    f"{key} "
                    f"thieu {field}."
                )

        content_by_key[
            key
        ] = row

    # =====================================================
    # VERIFY COUNTS PER LESSON
    # =====================================================
    for lesson_no in range(
        3,
        24,
    ):

        lesson_rows = [
            row
            for row in rows
            if int(
                row[
                    "SoThuTuBai"
                ]
            ) == lesson_no
        ]

        expected_count = (
            EXPECTED_COUNTS[
                lesson_no
            ]
        )

        if (
            len(lesson_rows)
            != expected_count
        ):

            fail(
                f"Bai {lesson_no}: "
                f"du kien {expected_count}, "
                f"thuc te "
                f"{len(lesson_rows)}."
            )

    print(
        "Tong content:",
        len(rows),
    )

    print(
        "DaKiemDuyetNoiDung=1:",
        len(rows),
    )

    print(
        "SHA256: OK"
    )

    print(
        "CONTENT: OK"
    )

    # =====================================================
    # 2. PREPARE BACKUP DIR
    # =====================================================
    DB_BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    # =====================================================
    # 3. FREEZE APPROVED CONTENT
    # =====================================================
    print()
    print(
        "[2] DONG BANG FILE NOI DUNG DA DUYET"
    )
    line()

    content_snapshot = (
        DB_BACKUP_DIR
        / (
            "hsk1_lessons3_23_grammar_content_"
            f"applied_{timestamp}.csv"
        )
    )

    shutil.copy2(
        CONTENT_FILE,
        content_snapshot,
    )

    content_snapshot_hash = (
        sha256_file(
            content_snapshot
        )
    )

    if (
        content_snapshot_hash
        != EXPECTED_CONTENT_SHA256
    ):

        fail(
            "Snapshot content "
            "khong khop file da duyet."
        )

    print(
        "Snapshot:"
    )

    print(
        content_snapshot
    )

    print(
        "SHA256:"
    )

    print(
        content_snapshot_hash
    )

    # =====================================================
    # 4. CONFIRM
    # =====================================================
    print()
    print("=" * 120)
    print(
        "XAC NHAN INSERT DATABASE"
    )
    print("=" * 120)

    print()
    print(
        "Sap INSERT 78 ngu phap "
        "cho Bai 3 -> 23."
    )

    print(
        "Bai 1 va Bai 2 se KHONG bi UPDATE."
    )

    print()
    print(
        "Nhap dung cau xac nhan moi tiep tuc."
    )

    confirmation = input(
        "Nhap chinh xac "
        "INSERT HSK1 GRAMMAR LESSONS3-23 "
        "de tiep tuc: "
    ).strip()

    if (
        confirmation
        != "INSERT HSK1 GRAMMAR LESSONS3-23"
    ):

        print()
        print(
            "KHONG NHAN DUOC XAC NHAN."
        )

        print(
            "DATABASE KHONG BI SUA."
        )

        return

    # =====================================================
    # 5. CONNECT
    # =====================================================
    print()
    print("[3] KET NOI DATABASE")
    line()

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

                # =================================================
                # 6. VERIFY SOURCE
                # =================================================
                print()
                print(
                    "[4] VERIFY MaNguon=1004"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        MaNguon,
                        Ten
                    FROM dbo.NguonDuLieu
                    WHERE MaNguon = ?;
                    """,
                    SOURCE_ID,
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
                    != SOURCE_NAME
                ):

                    fail(
                        "Sai Ten nguon "
                        "MaNguon=1004."
                    )

                print(
                    "MaNguon:",
                    int(
                        source_row[0]
                    ),
                )

                print(
                    "Ten:",
                    clean(
                        source_row[1]
                    ),
                )

                print(
                    "NGUON: OK"
                )

                # =================================================
                # 7. VERIFY LESSON MAP
                # =================================================
                print()
                print(
                    "[5] VERIFY BAI 3 -> 23"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        bh.MaBaiHoc,
                        bh.SoThuTuBai,
                        bh.TieuDe
                    FROM dbo.BaiHoc AS bh
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc
                    WHERE
                        kh.MaKyHieu = ?
                        AND bh.SoThuTuBai
                            BETWEEN 3 AND 23
                    ORDER BY
                        bh.SoThuTuBai;
                    """,
                    COURSE_CODE,
                )

                lesson_rows_db = (
                    cursor.fetchall()
                )

                if (
                    len(lesson_rows_db)
                    != 21
                ):

                    fail(
                        "Khong tim thay "
                        "du 21 bai."
                    )

                db_lesson_map = {}

                for item in (
                    lesson_rows_db
                ):

                    lesson_id = int(
                        item[0]
                    )

                    lesson_no = int(
                        item[1]
                    )

                    title = clean(
                        item[2]
                    )

                    db_lesson_map[
                        lesson_no
                    ] = {
                        "MaBaiHoc": (
                            lesson_id
                        ),
                        "TieuDe": (
                            title
                        ),
                    }

                for row in rows:

                    lesson_no = int(
                        row[
                            "SoThuTuBai"
                        ]
                    )

                    expected_lesson = (
                        db_lesson_map[
                            lesson_no
                        ]
                    )

                    if (
                        int(
                            clean(
                                row[
                                    "MaBaiHoc"
                                ]
                            )
                        )
                        != expected_lesson[
                            "MaBaiHoc"
                        ]
                    ):

                        fail(
                            f"Bai {lesson_no}: "
                            "MaBaiHoc trong CSV "
                            "khong khop DB."
                        )

                    if (
                        clean(
                            row[
                                "TieuDeBai"
                            ]
                        )
                        != expected_lesson[
                            "TieuDe"
                        ]
                    ):

                        fail(
                            f"Bai {lesson_no}: "
                            "TieuDe khong khop DB."
                        )

                print(
                    "21/21 BAI: OK"
                )

                # =================================================
                # 8. PRE-INSERT STATE
                # =================================================
                print()
                print(
                    "[6] KIEM TRA TRANG THAI "
                    "TRUOC INSERT"
                )
                line()

                old_rows = (
                    select_hsk1_grammar(
                        cursor,
                        1,
                        23,
                    )
                )

                if (
                    len(old_rows)
                    != EXPECTED_OLD_ROWS
                ):

                    fail(
                        "Truoc INSERT HSK1 "
                        "phai co dung 10 ngu phap. "
                        f"Thuc te: "
                        f"{len(old_rows)}"
                    )

                old_counts = {}

                for row in old_rows:

                    lesson_no = int(
                        row[2]
                    )

                    old_counts[
                        lesson_no
                    ] = (
                        old_counts.get(
                            lesson_no,
                            0,
                        )
                        + 1
                    )

                if (
                    old_counts.get(
                        1,
                        0,
                    )
                    != 7
                ):

                    fail(
                        "Bai 1 khong con "
                        "7 ngu phap."
                    )

                if (
                    old_counts.get(
                        2,
                        0,
                    )
                    != 3
                ):

                    fail(
                        "Bai 2 khong con "
                        "3 ngu phap."
                    )

                for lesson_no in range(
                    3,
                    24,
                ):

                    if (
                        old_counts.get(
                            lesson_no,
                            0,
                        )
                        != 0
                    ):

                        fail(
                            f"Bai {lesson_no} "
                            "da co ngu phap. "
                            "KHONG INSERT TRUNG."
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
                    0,
                )

                print(
                    "Tong hien tai:",
                    len(old_rows),
                )

                # =================================================
                # 9. BACKUP DB
                # =================================================
                print()
                print(
                    "[7] BACKUP DATABASE "
                    "TRUOC INSERT"
                )
                line()

                db_backup_file = (
                    DB_BACKUP_DIR
                    / (
                        "hsk1_grammar_before_"
                        f"lessons3_23_insert_"
                        f"{timestamp}.csv"
                    )
                )

                write_db_snapshot(
                    db_backup_file,
                    old_rows,
                )

                db_backup_hash = (
                    sha256_file(
                        db_backup_file
                    )
                )

                print(
                    "Backup:"
                )

                print(
                    db_backup_file
                )

                print(
                    "SHA256:"
                )

                print(
                    db_backup_hash
                )

                old_rows_by_id = {
                    int(
                        row[0]
                    ): grammar_row_to_dict(
                        row
                    )
                    for row in old_rows
                }

                # =================================================
                # 10. INSERT
                # =================================================
                print()
                print(
                    "[8] INSERT 78 DONG "
                    "TRONG TRANSACTION"
                )
                line()

                inserted_ids = []

                ordered_content = sorted(
                    rows,
                    key=lambda row: (
                        int(
                            row[
                                "SoThuTuBai"
                            ]
                        ),
                        int(
                            row[
                                "ThuTuTrongBai"
                            ]
                        ),
                    ),
                )

                for index, row in enumerate(
                    ordered_content,
                    start=1,
                ):

                    lesson_no = int(
                        row[
                            "SoThuTuBai"
                        ]
                    )

                    lesson_id = int(
                        row[
                            "MaBaiHoc"
                        ]
                    )

                    order_no = int(
                        row[
                            "ThuTuTrongBai"
                        ]
                    )

                    cursor.execute(
                        """
                        INSERT INTO dbo.NguPhap
                        (
                            MaBaiHoc,
                            TenCauTruc,
                            MoTa,
                            CachDung,
                            ViDuTiengTrung,
                            ViDuPinyin,
                            ViDuTiengViet,
                            MaTep,
                            MaNguon,
                            ThuTu,
                            TrangThai,
                            NgayTao
                        )
                        OUTPUT
                            INSERTED.MaNguPhap
                        VALUES
                        (
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            NULL,
                            ?,
                            ?,
                            ?,
                            SYSDATETIME()
                        );
                        """,
                        lesson_id,
                        clean(
                            row[
                                "TenCauTruc"
                            ]
                        ),
                        clean(
                            row["MoTa"]
                        ),
                        clean(
                            row[
                                "CachDung"
                            ]
                        ),
                        clean(
                            row[
                                "ViDuTiengTrung"
                            ]
                        ),
                        clean(
                            row[
                                "ViDuPinyin"
                            ]
                        ),
                        clean(
                            row[
                                "ViDuTiengViet"
                            ]
                        ),
                        SOURCE_ID,
                        order_no,
                        "ban_nhap",
                    )

                    result = (
                        cursor.fetchone()
                    )

                    if result is None:

                        fail(
                            f"INSERT Bai "
                            f"{lesson_no}, "
                            f"ThuTu {order_no} "
                            "khong tra MaNguPhap."
                        )

                    grammar_id = int(
                        result[0]
                    )

                    inserted_ids.append(
                        grammar_id
                    )

                    print(
                        f"{index:>2}/78 | "
                        f"Bai {lesson_no:>2} | "
                        f"ThuTu={order_no} | "
                        f"MaNguPhap="
                        f"{grammar_id}"
                    )

                if (
                    len(inserted_ids)
                    != EXPECTED_NEW_ROWS
                ):

                    fail(
                        "Khong INSERT du "
                        "78 dong."
                    )

                if (
                    len(set(inserted_ids))
                    != EXPECTED_NEW_ROWS
                ):

                    fail(
                        "MaNguPhap INSERT "
                        "bi trung."
                    )

                # =================================================
                # 11. VERIFY BEFORE COMMIT
                # =================================================
                print()
                print(
                    "[9] VERIFY TRUOC COMMIT"
                )
                line()

                new_db_rows = (
                    select_hsk1_grammar(
                        cursor,
                        3,
                        23,
                    )
                )

                if (
                    len(new_db_rows)
                    != 78
                ):

                    fail(
                        "Truoc COMMIT "
                        "Bai 3 -> 23 "
                        "khong co dung 78."
                    )

                verify_errors = []

                count_by_lesson = {}

                db_inserted_ids = set()

                for db_row in new_db_rows:

                    grammar_id = int(
                        db_row[0]
                    )

                    lesson_no = int(
                        db_row[2]
                    )

                    order_no = int(
                        db_row[12]
                    )

                    db_inserted_ids.add(
                        grammar_id
                    )

                    count_by_lesson[
                        lesson_no
                    ] = (
                        count_by_lesson.get(
                            lesson_no,
                            0,
                        )
                        + 1
                    )

                    key = (
                        lesson_no,
                        order_no,
                    )

                    if key not in (
                        content_by_key
                    ):

                        verify_errors.append(
                            (
                                key,
                                "khong co trong content",
                            )
                        )

                        continue

                    content = (
                        content_by_key[
                            key
                        ]
                    )

                    comparisons = {
                        "MaBaiHoc": (
                            clean(
                                db_row[1]
                            ),
                            clean(
                                content[
                                    "MaBaiHoc"
                                ]
                            ),
                        ),

                        "TieuDeBai": (
                            clean(
                                db_row[3]
                            ),
                            clean(
                                content[
                                    "TieuDeBai"
                                ]
                            ),
                        ),

                        "TenCauTruc": (
                            clean(
                                db_row[4]
                            ),
                            clean(
                                content[
                                    "TenCauTruc"
                                ]
                            ),
                        ),

                        "MoTa": (
                            clean(
                                db_row[5]
                            ),
                            clean(
                                content[
                                    "MoTa"
                                ]
                            ),
                        ),

                        "CachDung": (
                            clean(
                                db_row[6]
                            ),
                            clean(
                                content[
                                    "CachDung"
                                ]
                            ),
                        ),

                        "ViDuTiengTrung": (
                            clean(
                                db_row[7]
                            ),
                            clean(
                                content[
                                    "ViDuTiengTrung"
                                ]
                            ),
                        ),

                        "ViDuPinyin": (
                            clean(
                                db_row[8]
                            ),
                            clean(
                                content[
                                    "ViDuPinyin"
                                ]
                            ),
                        ),

                        "ViDuTiengViet": (
                            clean(
                                db_row[9]
                            ),
                            clean(
                                content[
                                    "ViDuTiengViet"
                                ]
                            ),
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

                            verify_errors.append(
                                (
                                    key,
                                    field,
                                )
                            )

                    if db_row[10] is not None:

                        verify_errors.append(
                            (
                                key,
                                "MaTep",
                            )
                        )

                    if (
                        int(db_row[11])
                        != SOURCE_ID
                    ):

                        verify_errors.append(
                            (
                                key,
                                "MaNguon",
                            )
                        )

                    if (
                        clean(
                            db_row[13]
                        )
                        != "ban_nhap"
                    ):

                        verify_errors.append(
                            (
                                key,
                                "TrangThai",
                            )
                        )

                if (
                    db_inserted_ids
                    != set(inserted_ids)
                ):

                    fail(
                        "Tap MaNguPhap "
                        "trong DB khong khop "
                        "OUTPUT INSERT."
                    )

                for lesson_no in range(
                    3,
                    24,
                ):

                    actual_count = (
                        count_by_lesson.get(
                            lesson_no,
                            0,
                        )
                    )

                    expected_count = (
                        EXPECTED_COUNTS[
                            lesson_no
                        ]
                    )

                    if (
                        actual_count
                        != expected_count
                    ):

                        verify_errors.append(
                            (
                                lesson_no,
                                "SoLuong",
                                actual_count,
                                expected_count,
                            )
                        )

                print(
                    "Loi verify content:",
                    len(
                        verify_errors
                    ),
                )

                if verify_errors:

                    for error in (
                        verify_errors[:50]
                    ):

                        print(
                            " ",
                            error,
                        )

                    fail(
                        "Du lieu truoc COMMIT "
                        "khong khop content."
                    )

                # =================================================
                # VERIFY OLD 10 UNCHANGED
                # =================================================
                current_old_rows = (
                    select_hsk1_grammar(
                        cursor,
                        1,
                        2,
                    )
                )

                if (
                    len(current_old_rows)
                    != 10
                ):

                    fail(
                        "Bai 1 + 2 "
                        "khong con dung "
                        "10 dong."
                    )

                old_change_errors = []

                for db_row in (
                    current_old_rows
                ):

                    grammar_id = int(
                        db_row[0]
                    )

                    current_dict = (
                        grammar_row_to_dict(
                            db_row
                        )
                    )

                    before_dict = (
                        old_rows_by_id.get(
                            grammar_id
                        )
                    )

                    if before_dict is None:

                        old_change_errors.append(
                            (
                                grammar_id,
                                "new old-row",
                            )
                        )

                        continue

                    for field in (
                        before_dict
                    ):

                        if (
                            current_dict[
                                field
                            ]
                            != before_dict[
                                field
                            ]
                        ):

                            old_change_errors.append(
                                (
                                    grammar_id,
                                    field,
                                )
                            )

                print(
                    "Bai 1 + 2 bi thay doi:",
                    len(
                        old_change_errors
                    ),
                )

                if old_change_errors:

                    fail(
                        "Phat hien Bai 1/2 "
                        "bi thay doi."
                    )

                print(
                    "78/78 NOI DUNG KHOP REVIEW."
                )

                print(
                    "Bai 1 + 2 KHONG BI SUA."
                )

                print(
                    "VERIFY TRUOC COMMIT: OK"
                )

                # =================================================
                # 12. COMMIT
                # =================================================
                print()
                print("[10] COMMIT")
                line()

                connection.commit()

                committed = True

                print(
                    "COMMIT THANH CONG."
                )

                # =================================================
                # 13. AUDIT AFTER COMMIT
                # =================================================
                print()
                print(
                    "[11] AUDIT SAU COMMIT"
                )
                line()

                all_after = (
                    select_hsk1_grammar(
                        cursor,
                        1,
                        23,
                    )
                )

                if (
                    len(all_after)
                    != EXPECTED_TOTAL_AFTER
                ):

                    fail(
                        "Sau COMMIT "
                        "tong HSK1 khong "
                        "bang 88."
                    )

                after_counts = {}

                for db_row in all_after:

                    lesson_no = int(
                        db_row[2]
                    )

                    after_counts[
                        lesson_no
                    ] = (
                        after_counts.get(
                            lesson_no,
                            0,
                        )
                        + 1
                    )

                if (
                    after_counts.get(
                        1,
                        0,
                    )
                    != 7
                ):

                    fail(
                        "Sau COMMIT "
                        "Bai 1 != 7."
                    )

                if (
                    after_counts.get(
                        2,
                        0,
                    )
                    != 3
                ):

                    fail(
                        "Sau COMMIT "
                        "Bai 2 != 3."
                    )

                for lesson_no in range(
                    3,
                    24,
                ):

                    if (
                        after_counts.get(
                            lesson_no,
                            0,
                        )
                        != EXPECTED_COUNTS[
                            lesson_no
                        ]
                    ):

                        fail(
                            f"Sau COMMIT "
                            f"Bai {lesson_no} "
                            "sai so luong."
                        )

                after_new_rows = (
                    select_hsk1_grammar(
                        cursor,
                        3,
                        23,
                    )
                )

                if (
                    len(after_new_rows)
                    != 78
                ):

                    fail(
                        "Sau COMMIT "
                        "Bai 3 -> 23 "
                        "khong bang 78."
                    )

                source_count = sum(
                    1
                    for db_row in (
                        after_new_rows
                    )
                    if (
                        db_row[11]
                        == SOURCE_ID
                    )
                )

                draft_count = sum(
                    1
                    for db_row in (
                        after_new_rows
                    )
                    if clean(
                        db_row[13]
                    ) == "ban_nhap"
                )

                null_media_count = sum(
                    1
                    for db_row in (
                        after_new_rows
                    )
                    if (
                        db_row[10]
                        is None
                    )
                )

                print(
                    "Tong ngu phap HSK1:",
                    len(all_after),
                )

                print(
                    "Bai 1:",
                    after_counts[1],
                )

                print(
                    "Bai 2:",
                    after_counts[2],
                )

                print(
                    "Bai 3 -> 23:",
                    len(
                        after_new_rows
                    ),
                )

                print(
                    "MaNguon=1004 "
                    "trong 78 moi:",
                    source_count,
                )

                print(
                    "TrangThai=ban_nhap "
                    "trong 78 moi:",
                    draft_count,
                )

                print(
                    "MaTep=NULL "
                    "trong 78 moi:",
                    null_media_count,
                )

                if source_count != 78:

                    fail(
                        "Sau COMMIT "
                        "MaNguon sai."
                    )

                if draft_count != 78:

                    fail(
                        "Sau COMMIT "
                        "TrangThai sai."
                    )

                if (
                    null_media_count
                    != 78
                ):

                    fail(
                        "Sau COMMIT "
                        "MaTep sai."
                    )

                print(
                    "AUDIT SAU COMMIT: OK"
                )

                # =================================================
                # 14. CREATE AFTER SNAPSHOT
                # =================================================
                print()
                print(
                    "[12] TAO SNAPSHOT "
                    "78 DONG SAU COMMIT"
                )
                line()

                after_file = (
                    DB_BACKUP_DIR
                    / (
                        "hsk1_lessons3_23_"
                        f"grammar_inserted_"
                        f"{timestamp}.csv"
                    )
                )

                write_db_snapshot(
                    after_file,
                    after_new_rows,
                )

                after_hash = (
                    sha256_file(
                        after_file
                    )
                )

                print(
                    "Snapshot:"
                )

                print(
                    after_file
                )

                print(
                    "SHA256:"
                )

                print(
                    after_hash
                )

                # =================================================
                # FINAL
                # =================================================
                print()
                print("=" * 120)
                print(
                    "KET QUA 09H16"
                )
                print("=" * 120)

                print(
                    "Bai 1:",
                    "7 ngu phap",
                )

                print(
                    "Bai 2:",
                    "3 ngu phap",
                )

                print(
                    "Bai 3 -> 23 "
                    "da INSERT:",
                    78,
                )

                print(
                    "Tong ngu phap "
                    "HSK1 hien tai:",
                    88,
                )

                print(
                    "MaNguon=1004 "
                    "cua 78 dong moi:",
                    78,
                )

                print(
                    "TrangThai=ban_nhap "
                    "cua 78 dong moi:",
                    78,
                )

                print(
                    "MaTep=NULL "
                    "cua 78 dong moi:",
                    78,
                )

                print(
                    "Bai 1 + 2 bi thay doi:",
                    0,
                )

                print(
                    "Loi verify:",
                    0,
                )

                print()
                print(
                    "78 NGU PHAP BAI 3 -> 23 "
                    "DA DUOC CAP NHAT "
                    "VAO DATABASE THANH CONG."
                )

                print()
                print(
                    "Backup DB truoc INSERT:"
                )

                print(
                    db_backup_file
                )

                print(
                    "SHA256 backup:"
                )

                print(
                    db_backup_hash
                )

                print()
                print(
                    "Snapshot content da apply:"
                )

                print(
                    content_snapshot
                )

                print(
                    "SHA256 content:"
                )

                print(
                    content_snapshot_hash
                )

                print()
                print(
                    "Snapshot DB sau INSERT:"
                )

                print(
                    after_file
                )

                print(
                    "SHA256 snapshot DB:"
                )

                print(
                    after_hash
                )

                print()
                print("=" * 120)
                print("HOAN TAT")
                print("=" * 120)

        except Exception:

            if not committed:

                try:

                    connection.rollback()

                    print()
                    print(
                        "TRANSACTION DA ROLLBACK."
                    )

                    print(
                        "KHONG GIU LAI "
                        "78 INSERT CHUA COMMIT."
                    )

                except Exception:
                    pass

            else:

                print()
                print(
                    "LUU Y:"
                )

                print(
                    "DATABASE DA COMMIT."
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
        print("=" * 120)
        print(
            "09H16 THAT BAI"
        )
        print("=" * 120)

        print()
        print("Loi:")
        print(error)

        sys.exit(1)