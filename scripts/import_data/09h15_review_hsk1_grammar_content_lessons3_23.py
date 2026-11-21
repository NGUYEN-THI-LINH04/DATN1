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

EXPECTED_LESSONS = 21
EXPECTED_ROWS = 78

EXPECTED_INTRO = 38
EXPECTED_REVIEW = 40
EXPECTED_UNIQUE_GF1 = 44

SOURCE_ID = 1004
SOURCE_NAME = "GF0025-2021 - Ngữ pháp HSK"

EXPECTED_CONTENT_SHA256 = (
    "e9ca58e4c141835190ca9824704d3ab148e443f2ae98631534f30cfed31b4ae8"
)

EXPECTED_DISTRIBUTION_SHA256 = (
    "3129d9d2f35ce885a9bdb2f619ef1576f2da32b527e6cc0406275821656ef0b7"
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
DISTRIBUTION_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "hsk1_lessons3_23_grammar_distribution_review.csv"
)

CONTENT_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "hsk1_lessons3_23_grammar_content_review.csv"
)

BACKUP_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "backup"
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


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "09H15 - AUDIT + KIEM DUYET NOI DUNG "
        "NGU PHAP HSK1 BAI 3 -> 23"
    )
    print("=" * 120)

    print()
    print("CHE DO:")
    print("  AUDIT FILE CONTENT REVIEW")
    print("  DOI CHIEU FILE PHAN BO")
    print("  SELECT DATABASE DE KIEM TRA TRANG THAI")
    print("  BACKUP FILE TRUOC KIEM DUYET")
    print("  CAP NHAT DaKiemDuyetNoiDung TRONG CSV")
    print("  KHONG INSERT dbo.NguPhap")
    print("  KHONG UPDATE DATABASE")
    print("  KHONG DELETE DATABASE")

    # =====================================================
    # 1. VERIFY FILES
    # =====================================================
    print()
    print("[1] VERIFY FILE DAU VAO")
    line()

    for path in [
        DISTRIBUTION_FILE,
        CONTENT_FILE,
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

    distribution_hash = sha256_file(
        DISTRIBUTION_FILE
    )

    content_hash = sha256_file(
        CONTENT_FILE
    )

    print(
        "Distribution SHA256:"
    )
    print(
        distribution_hash
    )

    print()
    print(
        "Content SHA256:"
    )
    print(
        content_hash
    )

    if (
        distribution_hash
        != EXPECTED_DISTRIBUTION_SHA256
    ):

        fail(
            "File distribution da thay doi "
            "sau 09h13."
        )

    if (
        content_hash
        != EXPECTED_CONTENT_SHA256
    ):

        fail(
            "File content da thay doi "
            "sau 09h14."
        )

    print()
    print(
        "SHA256 2 FILE: OK"
    )

    # =====================================================
    # 3. READ DISTRIBUTION
    # =====================================================
    print()
    print(
        "[3] DOC 78 PHAN BO DA KIEM DUYET"
    )
    line()

    distribution_fields, distribution_rows = (
        load_csv(
            DISTRIBUTION_FILE
        )
    )

    if len(
        distribution_rows
    ) != EXPECTED_ROWS:

        fail(
            "Distribution khong co "
            "dung 78 dong."
        )

    approved_distribution = sum(
        1
        for row in distribution_rows
        if clean(
            row[
                "DaKiemDuyetPhanBo"
            ]
        ) == "1"
    )

    if approved_distribution != 78:

        fail(
            "Distribution chua "
            "duoc kiem duyet 78/78."
        )

    distribution_by_key = {}

    for row in distribution_rows:

        key = (
            int(
                clean(
                    row[
                        "SoThuTuBai"
                    ]
                )
            ),
            int(
                clean(
                    row[
                        "ThuTuNguPhapDeXuat"
                    ]
                )
            ),
        )

        if key in distribution_by_key:

            fail(
                "Distribution bi trung key: "
                f"{key}"
            )

        distribution_by_key[
            key
        ] = row

    print(
        "Tong phan bo:",
        len(distribution_rows),
    )

    print(
        "Da kiem duyet:",
        approved_distribution,
    )

    print(
        "DISTRIBUTION: OK"
    )

    # =====================================================
    # 4. READ CONTENT
    # =====================================================
    print()
    print(
        "[4] DOC 78 NOI DUNG NGU PHAP"
    )
    line()

    content_fields, rows = load_csv(
        CONTENT_FILE
    )

    required_fields = {
        "SoThuTuBai",
        "MaBaiHoc",
        "TieuDeBai",
        "ThuTuTrongBai",
        "MaMucNguPhapChuan",
        "TenMucChuan",
        "NoiDungChuan",
        "LoaiSuDung",
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
        "MaNguon",
        "MaTep",
        "TrangThai",
        "LyDoPhanBo",
        "GhiChuBienSoan",
        "DaKiemDuyetNoiDung",
        "GhiChuKiemDuyet",
    }

    missing_fields = (
        required_fields
        - set(content_fields)
    )

    if missing_fields:

        fail(
            "Content review thieu cot: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    if len(rows) != EXPECTED_ROWS:

        fail(
            "Content review phai "
            "co dung 78 dong."
        )

    print(
        "Tong noi dung:",
        len(rows),
    )

    # =====================================================
    # 5. AUDIT EACH ROW
    # =====================================================
    print()
    print(
        "[5] AUDIT 78/78 NOI DUNG"
    )
    line()

    errors = []

    content_by_key = {}

    required_nonblank = [
        "TieuDeBai",
        "MaMucNguPhapChuan",
        "TenMucChuan",
        "NoiDungChuan",
        "LoaiSuDung",
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
        "LyDoPhanBo",
        "GhiChuBienSoan",
    ]

    for row in rows:

        try:

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

        except Exception:

            errors.append(
                (
                    "?",
                    "?",
                    "SoThuTuBai/ThuTuTrongBai",
                )
            )

            continue

        key = (
            lesson_no,
            order_no,
        )

        if key in content_by_key:

            errors.append(
                (
                    lesson_no,
                    order_no,
                    "duplicate key",
                )
            )

            continue

        content_by_key[
            key
        ] = row

        if (
            lesson_no < 3
            or lesson_no > 23
        ):

            errors.append(
                (
                    lesson_no,
                    order_no,
                    "SoThuTuBai",
                )
            )

        for field in required_nonblank:

            if not clean(
                row[field]
            ):

                errors.append(
                    (
                        lesson_no,
                        order_no,
                        field,
                    )
                )

        if (
            clean(
                row["MaNguon"]
            )
            != "1004"
        ):

            errors.append(
                (
                    lesson_no,
                    order_no,
                    "MaNguon",
                )
            )

        if (
            clean(
                row["TrangThai"]
            )
            != "ban_nhap"
        ):

            errors.append(
                (
                    lesson_no,
                    order_no,
                    "TrangThai",
                )
            )

        if (
            clean(
                row["MaTep"]
            )
            != ""
        ):

            errors.append(
                (
                    lesson_no,
                    order_no,
                    "MaTep",
                )
            )

        if clean(
            row[
                "DaKiemDuyetNoiDung"
            ]
        ) not in {
            "0",
            "1",
        }:

            errors.append(
                (
                    lesson_no,
                    order_no,
                    "DaKiemDuyetNoiDung",
                )
            )

        if (
            clean(
                row["LoaiSuDung"]
            )
            not in {
                "gioi_thieu",
                "on_tap_mo_rong",
            }
        ):

            errors.append(
                (
                    lesson_no,
                    order_no,
                    "LoaiSuDung",
                )
            )

    print(
        "Loi noi dung:",
        len(errors),
    )

    if errors:

        for error in errors[:50]:

            print(
                " ",
                error,
            )

        fail(
            "Phat hien loi "
            "trong content review."
        )

    print(
        "78/78 NOI DUNG: OK"
    )

    # =====================================================
    # 6. COMPARE DISTRIBUTION
    # =====================================================
    print()
    print(
        "[6] DOI CHIEU CONTENT "
        "VOI DISTRIBUTION"
    )
    line()

    compare_errors = []

    if (
        set(content_by_key)
        != set(distribution_by_key)
    ):

        fail(
            "Key content khong khop "
            "distribution."
        )

    for key in sorted(
        content_by_key
    ):

        content = (
            content_by_key[
                key
            ]
        )

        distribution = (
            distribution_by_key[
                key
            ]
        )

        comparisons = {
            "MaBaiHoc": (
                clean(
                    content[
                        "MaBaiHoc"
                    ]
                ),
                clean(
                    distribution[
                        "MaBaiHoc"
                    ]
                ),
            ),

            "TieuDeBai": (
                clean(
                    content[
                        "TieuDeBai"
                    ]
                ),
                clean(
                    distribution[
                        "TieuDeBai"
                    ]
                ),
            ),

            "MaMucNguPhapChuan": (
                clean(
                    content[
                        "MaMucNguPhapChuan"
                    ]
                ),
                clean(
                    distribution[
                        "MaMucNguPhapChuan"
                    ]
                ),
            ),

            "TenMucChuan": (
                clean(
                    content[
                        "TenMucChuan"
                    ]
                ),
                clean(
                    distribution[
                        "TenMucChuan"
                    ]
                ),
            ),

            "NoiDungChuan": (
                clean(
                    content[
                        "NoiDungChuan"
                    ]
                ),
                clean(
                    distribution[
                        "NoiDungChuan"
                    ]
                ),
            ),

            "LoaiSuDung": (
                clean(
                    content[
                        "LoaiSuDung"
                    ]
                ),
                clean(
                    distribution[
                        "LoaiSuDung"
                    ]
                ),
            ),

            "LyDoPhanBo": (
                clean(
                    content[
                        "LyDoPhanBo"
                    ]
                ),
                clean(
                    distribution[
                        "LyDoPhanBo"
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

                compare_errors.append(
                    (
                        key,
                        field,
                    )
                )

    print(
        "Loi doi chieu:",
        len(
            compare_errors
        ),
    )

    if compare_errors:

        for error in (
            compare_errors[:50]
        ):

            print(
                " ",
                error,
            )

        fail(
            "Content khong khop "
            "distribution da duyet."
        )

    print(
        "CONTENT <-> DISTRIBUTION: OK"
    )

    # =====================================================
    # 7. PER-LESSON COUNTS
    # =====================================================
    print()
    print(
        "[7] KIEM TRA SO NGU PHAP TUNG BAI"
    )
    line()

    for lesson_no in range(
        3,
        24,
    ):

        lesson_rows = [
            row
            for row in rows
            if int(
                clean(
                    row[
                        "SoThuTuBai"
                    ]
                )
            ) == lesson_no
        ]

        actual_count = len(
            lesson_rows
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

            fail(
                f"Bai {lesson_no}: "
                f"du kien {expected_count}, "
                f"thuc te {actual_count}."
            )

        orders = [
            int(
                clean(
                    row[
                        "ThuTuTrongBai"
                    ]
                )
            )
            for row in lesson_rows
        ]

        expected_orders = list(
            range(
                1,
                expected_count + 1,
            )
        )

        if (
            orders
            != expected_orders
        ):

            fail(
                f"Bai {lesson_no}: "
                "ThuTuTrongBai sai."
            )

        print(
            f"Bai {lesson_no:>2}: "
            f"{actual_count} muc | OK"
        )

    # =====================================================
    # 8. STATISTICS
    # =====================================================
    print()
    print(
        "[8] KIEM TRA THONG KE"
    )
    line()

    intro_count = sum(
        1
        for row in rows
        if clean(
            row["LoaiSuDung"]
        ) == "gioi_thieu"
    )

    review_count = sum(
        1
        for row in rows
        if clean(
            row["LoaiSuDung"]
        ) == "on_tap_mo_rong"
    )

    unique_ids = {
        clean(
            row[
                "MaMucNguPhapChuan"
            ]
        )
        for row in rows
    }

    current_approved = sum(
        1
        for row in rows
        if clean(
            row[
                "DaKiemDuyetNoiDung"
            ]
        ) == "1"
    )

    print(
        "Gioi thieu:",
        intro_count,
    )

    print(
        "On tap/mo rong:",
        review_count,
    )

    print(
        "GF1 duy nhat:",
        len(unique_ids),
    )

    print(
        "DaKiemDuyetNoiDung=1:",
        current_approved,
    )

    if intro_count != 38:

        fail(
            "Gioi thieu khong bang 38."
        )

    if review_count != 40:

        fail(
            "On tap/mo rong "
            "khong bang 40."
        )

    if (
        len(unique_ids)
        != EXPECTED_UNIQUE_GF1
    ):

        fail(
            "GF1 duy nhat "
            "khong bang 44."
        )

    if current_approved != 0:

        fail(
            "File content da co "
            "noi dung duoc approve truoc. "
            "Khong ghi de."
        )

    print(
        "THONG KE: OK"
    )

    # =====================================================
    # 9. DATABASE READ-ONLY AUDIT
    # =====================================================
    print()
    print(
        "[9] DOI CHIEU DATABASE HIEN TAI"
    )
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

                # -----------------------------------------
                # Source
                # -----------------------------------------
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
                    clean(
                        source_row[0]
                    )
                    != SOURCE_NAME
                ):

                    fail(
                        "Sai MaNguon=1004."
                    )

                # -----------------------------------------
                # Grammar counts 1 -> 23
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        bh.SoThuTuBai,
                        COUNT(np.MaNguPhap)
                    FROM dbo.BaiHoc AS bh
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc
                    LEFT JOIN dbo.NguPhap AS np
                        ON bh.MaBaiHoc
                        = np.MaBaiHoc
                    WHERE
                        kh.MaKyHieu = ?
                        AND bh.SoThuTuBai
                            BETWEEN 1 AND 23
                    GROUP BY
                        bh.SoThuTuBai
                    ORDER BY
                        bh.SoThuTuBai;
                    """,
                    COURSE_CODE,
                )

                grammar_counts = {
                    int(row[0]): int(row[1])
                    for row in cursor.fetchall()
                }

                if len(
                    grammar_counts
                ) != 23:

                    fail(
                        "Database khong co "
                        "du 23 bai HSK1."
                    )

                print(
                    "Bai 1:",
                    grammar_counts[1],
                )

                print(
                    "Bai 2:",
                    grammar_counts[2],
                )

                if (
                    grammar_counts[1]
                    != 7
                ):

                    fail(
                        "Bai 1 khong con "
                        "7 ngu phap."
                    )

                if (
                    grammar_counts[2]
                    != 3
                ):

                    fail(
                        "Bai 2 khong con "
                        "3 ngu phap."
                    )

                later_total = sum(
                    grammar_counts[
                        lesson_no
                    ]
                    for lesson_no in range(
                        3,
                        24,
                    )
                )

                print(
                    "Tong ngu phap "
                    "Bai 3 -> 23 hien tai:",
                    later_total,
                )

                if later_total != 0:

                    fail(
                        "Bai 3 -> 23 "
                        "da co ngu phap trong DB. "
                        "Khong approve tren gia dinh rong."
                    )

                print(
                    "DATABASE STATE: OK"
                )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 10. BACKUP FILE BEFORE APPROVE
    # =====================================================
    print()
    print(
        "[10] BACKUP CONTENT REVIEW "
        "TRUOC KIEM DUYET"
    )
    line()

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
            "hsk1_lessons3_23_grammar_content_"
            f"before_approve_{timestamp}.csv"
        )
    )

    shutil.copy2(
        CONTENT_FILE,
        backup_file,
    )

    backup_hash = sha256_file(
        backup_file
    )

    if (
        backup_hash
        != EXPECTED_CONTENT_SHA256
    ):

        fail(
            "Backup hash khong khop "
            "content truoc approve."
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

    print(
        "BACKUP: OK"
    )

    # =====================================================
    # 11. CONFIRM
    # =====================================================
    print()
    print("=" * 120)
    print(
        "XAC NHAN KIEM DUYET NOI DUNG"
    )
    print("=" * 120)

    print()
    print(
        "Da audit:"
    )

    print(
        "  78/78 dong co day du noi dung"
    )

    print(
        "  78/78 khop distribution da duyet"
    )

    print(
        "  21/21 bai dung so luong va thu tu"
    )

    print(
        "  38 gioi thieu + 40 on tap/mo rong"
    )

    print(
        "  44 GF1 duy nhat trong Bai 3 -> 23"
    )

    print(
        "  MaNguon=1004"
    )

    print(
        "  TrangThai=ban_nhap"
    )

    print(
        "  Database Bai 3 -> 23 hien tai = 0 ngu phap"
    )

    print()
    print(
        "Buoc nay CHI approve CSV."
    )

    print(
        "CHUA INSERT DATABASE."
    )

    confirmation = input(
        "Nhap chinh xac "
        "APPROVE HSK1 GRAMMAR CONTENT "
        "de tiep tuc: "
    ).strip()

    if (
        confirmation
        != "APPROVE HSK1 GRAMMAR CONTENT"
    ):

        print()
        print(
            "KHONG NHAN DUOC XAC NHAN."
        )

        print(
            "CONTENT REVIEW KHONG BI SUA."
        )

        print(
            "DATABASE KHONG BI SUA."
        )

        return

    # =====================================================
    # 12. APPROVE
    # =====================================================
    print()
    print(
        "[11] CAP NHAT 78 DONG REVIEW"
    )
    line()

    for row in rows:

        lesson_no = clean(
            row[
                "SoThuTuBai"
            ]
        )

        standard_id = clean(
            row[
                "MaMucNguPhapChuan"
            ]
        )

        row[
            "DaKiemDuyetNoiDung"
        ] = "1"

        row[
            "GhiChuKiemDuyet"
        ] = (
            "Đã kiểm duyệt trước khi nhập SQL: "
            f"Bài {lesson_no}, {standard_id}; "
            "đã kiểm tra mapping đã duyệt, cấu trúc dữ liệu, "
            "mô tả, cách dùng, ví dụ Trung - Pinyin - Việt, "
            "nguồn và trạng thái bản nháp."
        )

    with open(
        CONTENT_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=content_fields,
        )

        writer.writeheader()

        writer.writerows(
            rows
        )

    # =====================================================
    # 13. VERIFY APPROVED FILE
    # =====================================================
    print()
    print(
        "[12] VERIFY FILE SAU KIEM DUYET"
    )
    line()

    verify_fields, verify_rows = load_csv(
        CONTENT_FILE
    )

    if len(verify_rows) != 78:

        fail(
            "File sau approve "
            "khong con dung 78 dong."
        )

    approved_after = sum(
        1
        for row in verify_rows
        if clean(
            row[
                "DaKiemDuyetNoiDung"
            ]
        ) == "1"
    )

    missing_notes = sum(
        1
        for row in verify_rows
        if not clean(
            row[
                "GhiChuKiemDuyet"
            ]
        )
    )

    if approved_after != 78:

        fail(
            "Khong approve du 78."
        )

    if missing_notes != 0:

        fail(
            "Co dong thieu "
            "GhiChuKiemDuyet."
        )

    # Verify immutable content fields did not change
    original_by_key = {
        (
            int(
                clean(
                    row[
                        "SoThuTuBai"
                    ]
                )
            ),
            int(
                clean(
                    row[
                        "ThuTuTrongBai"
                    ]
                )
            ),
        ): row
        for row in rows
    }

    immutable_fields = [
        "SoThuTuBai",
        "MaBaiHoc",
        "TieuDeBai",
        "ThuTuTrongBai",
        "MaMucNguPhapChuan",
        "TenMucChuan",
        "NoiDungChuan",
        "LoaiSuDung",
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
        "MaNguon",
        "MaTep",
        "TrangThai",
        "LyDoPhanBo",
        "GhiChuBienSoan",
    ]

    immutable_errors = []

    for row in verify_rows:

        key = (
            int(
                clean(
                    row[
                        "SoThuTuBai"
                    ]
                )
            ),
            int(
                clean(
                    row[
                        "ThuTuTrongBai"
                    ]
                )
            ),
        )

        original = (
            original_by_key[
                key
            ]
        )

        for field in immutable_fields:

            if (
                clean(
                    row[field]
                )
                != clean(
                    original[field]
                )
            ):

                immutable_errors.append(
                    (
                        key,
                        field,
                    )
                )

    if immutable_errors:

        print(
            immutable_errors[:30]
        )

        fail(
            "Co noi dung bi thay doi "
            "ngoai cot review."
        )

    approved_hash = sha256_file(
        CONTENT_FILE
    )

    print(
        "Tong dong:",
        len(verify_rows),
    )

    print(
        "DaKiemDuyetNoiDung=1:",
        approved_after,
    )

    print(
        "Thieu GhiChuKiemDuyet:",
        missing_notes,
    )

    print(
        "Cot noi dung bi thay doi:",
        len(
            immutable_errors
        ),
    )

    print()
    print(
        "SHA256 file da kiem duyet:"
    )

    print(
        approved_hash
    )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 09H15"
    )
    print("=" * 120)

    print(
        "Pham vi:",
        "Bai 3 -> Bai 23",
    )

    print(
        "So bai:",
        21,
    )

    print(
        "Tong noi dung:",
        78,
    )

    print(
        "Gioi thieu moi:",
        38,
    )

    print(
        "On tap / mo rong:",
        40,
    )

    print(
        "GF1 duy nhat:",
        44,
    )

    print(
        "Da kiem duyet noi dung:",
        approved_after,
    )

    print(
        "Chua kiem duyet:",
        0,
    )

    print()
    print(
        "78/78 NOI DUNG NGU PHAP "
        "DA DUOC KIEM DUYET."
    )

    print()
    print(
        "FILE CONTENT REVIEW:"
    )

    print(
        CONTENT_FILE
    )

    print()
    print(
        "Backup truoc kiem duyet:"
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
        "SHA256 file da kiem duyet:"
    )

    print(
        approved_hash
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "BAI 3 -> 23 VAN CHUA INSERT."
    )

    print()
    print(
        "BUOC TIEP THEO:"
    )

    print(
        "09H16 BACKUP + INSERT 78 NOI DUNG "
        "VAO dbo.NguPhap TRONG TRANSACTION, "
        "SAU DO AUDIT SAU COMMIT."
    )

    print()
    print("=" * 120)
    print("HOAN TAT")
    print("=" * 120)


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
            "09H15 THAT BAI"
        )
        print("=" * 120)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)