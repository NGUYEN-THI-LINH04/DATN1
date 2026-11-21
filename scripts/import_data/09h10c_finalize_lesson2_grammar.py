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
LESSON_NO = 2
EXPECTED_ROWS = 3

SOURCE_ID = 1004
SOURCE_NAME = "GF0025-2021 - Ngữ pháp HSK"


# =========================================================
# FILES
# =========================================================
REVIEW_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "hsk1_lesson2_grammar_review.csv"
)

BACKUP_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "db_backup"
)


# =========================================================
# EXPECTED CONTENT
# =========================================================
EXPECTED = {

    1: {
        "TenCauTruc": (
            "Đại từ nhân xưng: "
            "我 / 你 / 您 / 他 / 她 / "
            "我们 / 你们 / 他们 / 她们"
        ),
        "MaMucNguPhapChuan": "GF1-005",
        "LoaiSuDung": "gioi_thieu",
    },

    2: {
        "TenCauTruc": (
            "A + 是 + B - giới thiệu quốc tịch hoặc thân phận"
        ),
        "MaMucNguPhapChuan": "GF1-036",
        "LoaiSuDung": "on_tap_mo_rong",
    },

    3: {
        "TenCauTruc": "谁 - hỏi 'ai'",
        "MaMucNguPhapChuan": "GF1-004;GF1-046",
        "LoaiSuDung": "gioi_thieu",
    },
}


# =========================================================
# HELPERS
# =========================================================
def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def fail(message):

    raise RuntimeError(message)


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


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 115)
    print(
        "09H10C - FINALIZE NGU PHAP BAI 2"
    )
    print("=" * 115)

    print()
    print("BUOC NAY SE:")
    print("  1. KIEM TRA 3 MUC NGU PHAP")
    print("  2. KIEM DUYET FILE REVIEW")
    print("  3. BACKUP TRANG THAI TRUOC INSERT")
    print("  4. INSERT 3 MUC VAO dbo.NguPhap")
    print("  5. VERIFY TRUOC COMMIT")
    print("  6. COMMIT")
    print("  7. AUDIT SAU COMMIT")

    # =====================================================
    # 1. READ REVIEW
    # =====================================================
    print()
    print("[1] DOC FILE REVIEW")
    print("-" * 115)

    if not REVIEW_FILE.exists():

        fail(
            "Khong tim thay file:\n"
            f"{REVIEW_FILE}"
        )

    fieldnames, rows = load_csv(
        REVIEW_FILE
    )

    required_fields = {
        "SoThuTuBai",
        "MaBaiHoc",
        "TieuDeBai",
        "ThuTuTrongBai",
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
        "MaMucNguPhapChuan",
        "LoaiSuDung",
        "MaNguon",
        "MaTep",
        "TrangThai",
        "GhiChuNguon",
        "DaKiemDuyetNoiDung",
        "GhiChuKiemDuyet",
    }

    missing_fields = (
        required_fields
        - set(fieldnames)
    )

    if missing_fields:

        fail(
            "File review thieu cot: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    if len(rows) != EXPECTED_ROWS:

        fail(
            "File review phai co dung 3 dong."
        )

    review_by_order = {}

    for row in rows:

        order_no = int(
            clean(
                row["ThuTuTrongBai"]
            )
        )

        if order_no in review_by_order:

            fail(
                f"ThuTuTrongBai bi trung: {order_no}"
            )

        if order_no not in EXPECTED:

            fail(
                f"ThuTu khong mong doi: {order_no}"
            )

        expected = EXPECTED[
            order_no
        ]

        if (
            clean(
                row["TenCauTruc"]
            )
            != expected[
                "TenCauTruc"
            ]
        ):

            fail(
                f"Sai TenCauTruc "
                f"o ThuTu={order_no}"
            )

        if (
            clean(
                row[
                    "MaMucNguPhapChuan"
                ]
            )
            != expected[
                "MaMucNguPhapChuan"
            ]
        ):

            fail(
                f"Sai MaMucNguPhapChuan "
                f"o ThuTu={order_no}"
            )

        if (
            clean(
                row["LoaiSuDung"]
            )
            != expected[
                "LoaiSuDung"
            ]
        ):

            fail(
                f"Sai LoaiSuDung "
                f"o ThuTu={order_no}"
            )

        if (
            clean(
                row["MaNguon"]
            )
            != "1004"
        ):

            fail(
                f"ThuTu={order_no} "
                "khong MaNguon=1004."
            )

        if (
            clean(
                row["TrangThai"]
            )
            != "ban_nhap"
        ):

            fail(
                f"ThuTu={order_no} "
                "khong TrangThai=ban_nhap."
            )

        for content_field in [
            "MoTa",
            "CachDung",
            "ViDuTiengTrung",
            "ViDuPinyin",
            "ViDuTiengViet",
            "GhiChuNguon",
        ]:

            if not clean(
                row[content_field]
            ):

                fail(
                    f"ThuTu={order_no} "
                    f"thieu {content_field}."
                )

        review_by_order[
            order_no
        ] = row

    if set(
        review_by_order
    ) != {
        1,
        2,
        3,
    }:

        fail(
            "ThuTu phai dung 1,2,3."
        )

    print(
        "Tong muc:",
        len(rows),
    )

    print(
        "3/3 noi dung: OK"
    )

    # =====================================================
    # 2. SHOW CONTENT
    # =====================================================
    print()
    print("[2] NOI DUNG SE KIEM DUYET")
    print("-" * 115)

    for order_no in [
        1,
        2,
        3,
    ]:

        row = review_by_order[
            order_no
        ]

        print()
        print(
            f"[{order_no}] "
            f"{row['TenCauTruc']}"
        )

        print(
            "  MoTa:",
            row["MoTa"],
        )

        print(
            "  CachDung:",
            row["CachDung"],
        )

        print(
            "  ViDu:",
            row["ViDuTiengTrung"],
        )

        print(
            "  Pinyin:",
            row["ViDuPinyin"],
        )

        print(
            "  Nghia:",
            row["ViDuTiengViet"],
        )

        print(
            "  GF1:",
            row[
                "MaMucNguPhapChuan"
            ],
        )

    # =====================================================
    # 3. CONFIRM REVIEW
    # =====================================================
    print()
    print("=" * 115)
    print(
        "XAC NHAN KIEM DUYET + INSERT"
    )
    print("=" * 115)

    print()
    print(
        "Neu tiep tuc, 3 muc tren se duoc "
        "danh dau da kiem duyet va INSERT vao SQL."
    )

    confirmation = input(
        "Nhap chinh xac "
        "APPROVE AND INSERT LESSON2 GRAMMAR "
        "de tiep tuc: "
    ).strip()

    if (
        confirmation
        != "APPROVE AND INSERT LESSON2 GRAMMAR"
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
    # 4. UPDATE REVIEW FILE
    # =====================================================
    print()
    print(
        "[3] KIEM DUYET FILE REVIEW"
    )
    print("-" * 115)

    for row in rows:

        row[
            "DaKiemDuyetNoiDung"
        ] = "1"

        row[
            "GhiChuKiemDuyet"
        ] = (
            "Đã kiểm duyệt nội dung, "
            "mapping GF0025, ví dụ Trung - Pinyin - Việt "
            "và phạm vi Bài 2 trước khi INSERT SQL."
        )

    with open(
        REVIEW_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            rows
        )

    _, verify_review = load_csv(
        REVIEW_FILE
    )

    approved_count = sum(
        1
        for row in verify_review
        if clean(
            row[
                "DaKiemDuyetNoiDung"
            ]
        ) == "1"
    )

    if approved_count != 3:

        fail(
            "Khong kiem duyet du 3 muc."
        )

    print(
        "DaKiemDuyetNoiDung=1:",
        approved_count,
    )

    print(
        "REVIEW: OK"
    )

    # =====================================================
    # 5. CREATE SNAPSHOT
    # =====================================================
    print()
    print(
        "[4] DONG BANG REVIEW SE INSERT"
    )
    print("-" * 115)

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    snapshot_file = (
        BACKUP_DIR
        / (
            "hsk1_lesson2_grammar_"
            f"review_applied_{timestamp}.csv"
        )
    )

    shutil.copy2(
        REVIEW_FILE,
        snapshot_file,
    )

    snapshot_hash = sha256_file(
        snapshot_file
    )

    print(
        "Snapshot:"
    )

    print(
        snapshot_file
    )

    print(
        "SHA256:"
    )

    print(
        snapshot_hash
    )

    # =====================================================
    # 6. CONNECT DATABASE
    # =====================================================
    print()
    print("[5] KET NOI DATABASE")
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
                        "Dang ket noi nham database."
                    )

                print(
                    "KET NOI DATABASE: OK"
                )

                # =========================================
                # 7. FIND LESSON 2
                # =========================================
                print()
                print(
                    "[6] PRE-CHECK BAI 2"
                )
                print("-" * 115)

                cursor.execute(
                    """
                    SELECT
                        bh.MaBaiHoc,
                        bh.TieuDe
                    FROM dbo.BaiHoc AS bh
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

                lesson_rows = (
                    cursor.fetchall()
                )

                if len(lesson_rows) != 1:

                    fail(
                        "Khong tim thay dung "
                        "1 Bai 2."
                    )

                lesson_id = int(
                    lesson_rows[0][0]
                )

                lesson_title = clean(
                    lesson_rows[0][1]
                )

                if (
                    lesson_title
                    != "我是越南人 - Tôi là người Việt Nam"
                ):

                    fail(
                        "Sai tieu de Bai 2."
                    )

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.NguPhap
                    WHERE MaBaiHoc = ?;
                    """,
                    lesson_id,
                )

                current_count = int(
                    cursor.fetchone()[0]
                )

                print(
                    "MaBaiHoc:",
                    lesson_id,
                )

                print(
                    "TieuDe:",
                    lesson_title,
                )

                print(
                    "Ngu phap hien tai:",
                    current_count,
                )

                if current_count != 0:

                    fail(
                        "Bai 2 da co ngu phap. "
                        "KHONG INSERT TRUNG."
                    )

                # =========================================
                # VERIFY SOURCE
                # =========================================
                cursor.execute(
                    """
                    SELECT Ten
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
                    clean(source_row[0])
                    != SOURCE_NAME
                ):

                    fail(
                        "Sai nguon 1004."
                    )

                print(
                    "PRE-CHECK: OK"
                )

                # =========================================
                # 8. BACKUP PRE-INSERT STATE
                # =========================================
                print()
                print(
                    "[7] BACKUP TRANG THAI "
                    "TRUOC INSERT"
                )
                print("-" * 115)

                preinsert_file = (
                    BACKUP_DIR
                    / (
                        "hsk1_lesson2_grammar_"
                        f"before_insert_{timestamp}.csv"
                    )
                )

                preinsert_fields = [
                    "MaBaiHoc",
                    "SoThuTuBai",
                    "TieuDeBai",
                    "SoNguPhapTruocInsert",
                ]

                with open(
                    preinsert_file,
                    "w",
                    encoding="utf-8-sig",
                    newline="",
                ) as file:

                    writer = csv.DictWriter(
                        file,
                        fieldnames=preinsert_fields,
                    )

                    writer.writeheader()

                    writer.writerow(
                        {
                            "MaBaiHoc": (
                                lesson_id
                            ),
                            "SoThuTuBai": 2,
                            "TieuDeBai": (
                                lesson_title
                            ),
                            "SoNguPhapTruocInsert": (
                                current_count
                            ),
                        }
                    )

                preinsert_hash = (
                    sha256_file(
                        preinsert_file
                    )
                )

                print(
                    "Backup:"
                )

                print(
                    preinsert_file
                )

                print(
                    "SHA256:"
                )

                print(
                    preinsert_hash
                )

                # =========================================
                # 9. INSERT
                # =========================================
                print()
                print(
                    "[8] INSERT 3 NGU PHAP "
                    "TRONG TRANSACTION"
                )
                print("-" * 115)

                inserted_ids = []

                for order_no in [
                    1,
                    2,
                    3,
                ]:

                    row = review_by_order[
                        order_no
                    ]

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
                            f"INSERT ThuTu="
                            f"{order_no} "
                            "khong tra ve "
                            "MaNguPhap."
                        )

                    grammar_id = int(
                        result[0]
                    )

                    inserted_ids.append(
                        grammar_id
                    )

                    print(
                        f"  ThuTu={order_no} "
                        f"-> MaNguPhap="
                        f"{grammar_id}"
                    )

                if (
                    len(inserted_ids)
                    != 3
                ):

                    fail(
                        "Khong INSERT du 3 muc."
                    )

                # =========================================
                # 10. VERIFY BEFORE COMMIT
                # =========================================
                print()
                print(
                    "[9] VERIFY TRUOC COMMIT"
                )
                print("-" * 115)

                cursor.execute(
                    """
                    SELECT
                        MaNguPhap,
                        TenCauTruc,
                        MoTa,
                        CachDung,
                        ViDuTiengTrung,
                        ViDuPinyin,
                        ViDuTiengViet,
                        MaTep,
                        MaNguon,
                        ThuTu,
                        TrangThai
                    FROM dbo.NguPhap
                    WHERE MaBaiHoc = ?
                    ORDER BY ThuTu;
                    """,
                    lesson_id,
                )

                db_rows = (
                    cursor.fetchall()
                )

                if len(db_rows) != 3:

                    fail(
                        "Truoc COMMIT "
                        "Bai 2 khong co "
                        "dung 3 muc."
                    )

                verify_errors = []

                for row in db_rows:

                    order_no = int(
                        row[9]
                    )

                    if (
                        order_no
                        not in review_by_order
                    ):

                        verify_errors.append(
                            (
                                order_no,
                                "ThuTu",
                            )
                        )

                        continue

                    review = (
                        review_by_order[
                            order_no
                        ]
                    )

                    comparisons = {
                        "TenCauTruc": (
                            clean(row[1]),
                            clean(
                                review[
                                    "TenCauTruc"
                                ]
                            ),
                        ),
                        "MoTa": (
                            clean(row[2]),
                            clean(
                                review[
                                    "MoTa"
                                ]
                            ),
                        ),
                        "CachDung": (
                            clean(row[3]),
                            clean(
                                review[
                                    "CachDung"
                                ]
                            ),
                        ),
                        "ViDuTiengTrung": (
                            clean(row[4]),
                            clean(
                                review[
                                    "ViDuTiengTrung"
                                ]
                            ),
                        ),
                        "ViDuPinyin": (
                            clean(row[5]),
                            clean(
                                review[
                                    "ViDuPinyin"
                                ]
                            ),
                        ),
                        "ViDuTiengViet": (
                            clean(row[6]),
                            clean(
                                review[
                                    "ViDuTiengViet"
                                ]
                            ),
                        ),
                    }

                    for (
                        column,
                        (
                            actual,
                            expected,
                        ),
                    ) in comparisons.items():

                        if actual != expected:

                            verify_errors.append(
                                (
                                    order_no,
                                    column,
                                )
                            )

                    if row[7] is not None:

                        verify_errors.append(
                            (
                                order_no,
                                "MaTep",
                            )
                        )

                    if (
                        int(row[8])
                        != SOURCE_ID
                    ):

                        verify_errors.append(
                            (
                                order_no,
                                "MaNguon",
                            )
                        )

                    if (
                        clean(row[10])
                        != "ban_nhap"
                    ):

                        verify_errors.append(
                            (
                                order_no,
                                "TrangThai",
                            )
                        )

                print(
                    "Loi verify:",
                    len(
                        verify_errors
                    ),
                )

                if verify_errors:

                    print(
                        verify_errors
                    )

                    fail(
                        "Du lieu INSERT "
                        "khong khop review."
                    )

                print(
                    "3/3 NOI DUNG KHOP REVIEW."
                )

                print(
                    "VERIFY TRUOC COMMIT: OK"
                )

                # =========================================
                # 11. COMMIT
                # =========================================
                print()
                print(
                    "[10] COMMIT"
                )
                print("-" * 115)

                connection.commit()
                committed = True

                print(
                    "COMMIT THANH CONG."
                )

                # =========================================
                # 12. AUDIT AFTER COMMIT
                # =========================================
                print()
                print(
                    "[11] AUDIT SAU COMMIT"
                )
                print("-" * 115)

                cursor.execute(
                    """
                    SELECT
                        MaNguPhap,
                        TenCauTruc,
                        MaNguon,
                        ThuTu,
                        TrangThai,
                        MaTep
                    FROM dbo.NguPhap
                    WHERE MaBaiHoc = ?
                    ORDER BY ThuTu;
                    """,
                    lesson_id,
                )

                after_rows = (
                    cursor.fetchall()
                )

                total_after = len(
                    after_rows
                )

                source_count = sum(
                    1
                    for row in after_rows
                    if (
                        row[2]
                        == SOURCE_ID
                    )
                )

                valid_orders = [
                    int(row[3])
                    for row in after_rows
                ]

                draft_count = sum(
                    1
                    for row in after_rows
                    if (
                        clean(row[4])
                        == "ban_nhap"
                    )
                )

                null_media_count = sum(
                    1
                    for row in after_rows
                    if row[5] is None
                )

                print(
                    "Tong ngu phap Bai 2:",
                    total_after,
                )

                print(
                    "MaNguon=1004:",
                    source_count,
                )

                print(
                    "ThuTu:",
                    valid_orders,
                )

                print(
                    "TrangThai=ban_nhap:",
                    draft_count,
                )

                print(
                    "MaTep=NULL:",
                    null_media_count,
                )

                if total_after != 3:
                    fail(
                        "Sau COMMIT "
                        "khong co dung 3 muc."
                    )

                if source_count != 3:
                    fail(
                        "Sau COMMIT "
                        "khong du MaNguon=1004."
                    )

                if (
                    valid_orders
                    != [
                        1,
                        2,
                        3,
                    ]
                ):

                    fail(
                        "ThuTu sau COMMIT sai."
                    )

                if draft_count != 3:
                    fail(
                        "TrangThai sau COMMIT sai."
                    )

                if null_media_count != 3:
                    fail(
                        "MaTep sau COMMIT sai."
                    )

                print(
                    "AUDIT SAU COMMIT: OK"
                )

                # =========================================
                # FINAL
                # =========================================
                print()
                print("=" * 115)
                print(
                    "KET QUA FINALIZE BAI 2"
                )
                print("=" * 115)

                print(
                    "Bai:",
                    "2 -",
                    lesson_title,
                )

                print(
                    "Ngu phap da kiem duyet:",
                    3,
                )

                print(
                    "Ngu phap da INSERT:",
                    3,
                )

                print(
                    "MaNguon=1004:",
                    3,
                )

                print(
                    "TrangThai=ban_nhap:",
                    3,
                )

                print(
                    "Loi verify:",
                    0,
                )

                print()
                print(
                    "NGU PHAP BAI 2 "
                    "DA DUOC CAP NHAT "
                    "VAO DATABASE THANH CONG."
                )

                print()
                print(
                    "3 MUC:"
                )

                for row in after_rows:

                    print(
                        f"  [{int(row[3])}] "
                        f"MaNguPhap="
                        f"{int(row[0])} | "
                        f"{clean(row[1])}"
                    )

                print()
                print(
                    "Snapshot review:"
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
                    "Backup truoc INSERT:"
                )

                print(
                    preinsert_file
                )

                print(
                    "SHA256 backup:"
                )

                print(
                    preinsert_hash
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
                        "TRANSACTION DA ROLLBACK."
                    )

                    print(
                        "KHONG GIU LAI "
                        "INSERT CHUA COMMIT."
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
        print("=" * 115)
        print(
            "09H10C THAT BAI"
        )
        print("=" * 115)

        print()
        print("Loi:")
        print(error)

        sys.exit(1)