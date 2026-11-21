from pathlib import Path
import csv
import hashlib
import shutil
import sys
from datetime import datetime


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]


# =========================================================
# CONFIG
# =========================================================
START_LESSON = 3
END_LESSON = 23

EXPECTED_LESSONS = 21
EXPECTED_ROWS = 78

EXPECTED_INTRO_COUNT = 38
EXPECTED_REVIEW_COUNT = 40

EXPECTED_SOURCE_ID = 1004


# =========================================================
# FILES
# =========================================================
STANDARD_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "hsk1_48_grammar_standard.csv"
)

LESSON1_REVIEW_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "hsk1_lesson1_grammar_mapping_review.csv"
)

LESSON2_REVIEW_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "hsk1_lesson2_grammar_review.csv"
)

DISTRIBUTION_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "hsk1_lessons3_23_grammar_distribution_review.csv"
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


def split_ids(value):

    return [
        item.strip()
        for item in clean(value).split(";")
        if item.strip()
    ]


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "09H13 - AUDIT + KIEM DUYET "
        "PHAN BO NGU PHAP HSK1 BAI 3 -> 23"
    )
    print("=" * 120)

    print()
    print("CHE DO:")
    print("  CHI DOC CAC FILE NGUON / REVIEW")
    print("  BACKUP FILE PHAN BO")
    print("  CAP NHAT DaKiemDuyetPhanBo TRONG CSV")
    print("  KHONG KET NOI DATABASE")
    print("  KHONG INSERT dbo.NguPhap")
    print("  KHONG UPDATE dbo.NguPhap")

    # =====================================================
    # 1. VERIFY FILES
    # =====================================================
    print()
    print("[1] VERIFY FILE DAU VAO")
    line()

    required_files = [
        STANDARD_FILE,
        LESSON1_REVIEW_FILE,
        LESSON2_REVIEW_FILE,
        DISTRIBUTION_FILE,
    ]

    for path in required_files:

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
    # 2. STANDARD 48
    # =====================================================
    print()
    print("[2] VERIFY 48 MUC GF1")
    line()

    standard_fields, standard_rows = load_csv(
        STANDARD_FILE
    )

    required_standard_fields = {
        "MaMucNguPhapChuan",
        "SoThuTuChuan",
        "TenMucTrung",
        "NoiDungChuanTrung",
        "MaNguon",
    }

    missing_standard_fields = (
        required_standard_fields
        - set(standard_fields)
    )

    if missing_standard_fields:

        fail(
            "File chuan thieu cot: "
            + ", ".join(
                sorted(
                    missing_standard_fields
                )
            )
        )

    if len(standard_rows) != 48:

        fail(
            "File chuan phai co dung 48 dong."
        )

    standard_by_id = {}

    for row in standard_rows:

        standard_id = clean(
            row["MaMucNguPhapChuan"]
        )

        if standard_id in standard_by_id:

            fail(
                "MaMucNguPhapChuan bi trung: "
                f"{standard_id}"
            )

        if clean(
            row["MaNguon"]
        ) != "1004":

            fail(
                f"{standard_id} "
                "khong MaNguon=1004."
            )

        standard_by_id[
            standard_id
        ] = row

    expected_standard_ids = {
        f"GF1-{number:03d}"
        for number in range(
            1,
            49,
        )
    }

    if (
        set(standard_by_id)
        != expected_standard_ids
    ):

        fail(
            "Danh sach GF1 "
            "khong dung 001 -> 048."
        )

    print(
        "Tong muc:",
        len(standard_rows),
    )

    print(
        "GF1-001 -> GF1-048: OK"
    )

    # =====================================================
    # 3. PREVIOUS COVERAGE - LESSON 1
    # =====================================================
    print()
    print(
        "[3] DOC CAC GF1 DA HOC O BAI 1"
    )
    line()

    _, lesson1_rows = load_csv(
        LESSON1_REVIEW_FILE
    )

    if len(lesson1_rows) != 7:

        fail(
            "Bai 1 khong co dung 7 mapping."
        )

    introduced_before = set()

    for row in lesson1_rows:

        if (
            clean(
                row[
                    "DaKiemDuyetMapping"
                ]
            )
            != "1"
        ):

            fail(
                "Bai 1 co mapping "
                "chua kiem duyet."
            )

        for standard_id in split_ids(
            row[
                "MaMucNguPhapChuan"
            ]
        ):

            if standard_id not in standard_by_id:

                fail(
                    "Bai 1 tham chieu "
                    "ID khong ton tai: "
                    f"{standard_id}"
                )

            introduced_before.add(
                standard_id
            )

    print(
        "GF1 duy nhat sau Bai 1:",
        len(introduced_before),
    )

    # =====================================================
    # 4. PREVIOUS COVERAGE - LESSON 2
    # =====================================================
    print()
    print(
        "[4] DOC CAC GF1 DA HOC O BAI 2"
    )
    line()

    _, lesson2_rows = load_csv(
        LESSON2_REVIEW_FILE
    )

    if len(lesson2_rows) != 3:

        fail(
            "Bai 2 khong co dung "
            "3 ngu phap review."
        )

    for row in lesson2_rows:

        if (
            clean(
                row[
                    "DaKiemDuyetNoiDung"
                ]
            )
            != "1"
        ):

            fail(
                "Bai 2 co noi dung "
                "chua kiem duyet."
            )

        for standard_id in split_ids(
            row[
                "MaMucNguPhapChuan"
            ]
        ):

            if standard_id not in standard_by_id:

                fail(
                    "Bai 2 tham chieu "
                    "ID khong ton tai: "
                    f"{standard_id}"
                )

            introduced_before.add(
                standard_id
            )

    print(
        "GF1 duy nhat sau Bai 1 + 2:",
        len(introduced_before),
    )

    if len(introduced_before) != 10:

        fail(
            "Sau Bai 1 + Bai 2 "
            "du kien phai co 10 GF1 duy nhat. "
            f"Thuc te: {len(introduced_before)}"
        )

    print(
        "10 GF1 DA DUOC GIOI THIEU: OK"
    )

    # =====================================================
    # 5. READ DISTRIBUTION
    # =====================================================
    print()
    print(
        "[5] DOC FILE PHAN BO 78 DONG"
    )
    line()

    distribution_fields, rows = load_csv(
        DISTRIBUTION_FILE
    )

    required_distribution_fields = {
        "SoThuTuBai",
        "MaBaiHoc",
        "TieuDeBai",
        "ThuTuNguPhapDeXuat",
        "MaMucNguPhapChuan",
        "SoThuTuChuan",
        "NhomLonTrung",
        "NhomConTrung",
        "TenMucChuan",
        "NoiDungChuan",
        "LoaiSuDung",
        "LyDoPhanBo",
        "MaNguon",
        "DaKiemDuyetPhanBo",
        "GhiChuKiemDuyet",
    }

    missing_distribution_fields = (
        required_distribution_fields
        - set(distribution_fields)
    )

    if missing_distribution_fields:

        fail(
            "File phan bo thieu cot: "
            + ", ".join(
                sorted(
                    missing_distribution_fields
                )
            )
        )

    if len(rows) != EXPECTED_ROWS:

        fail(
            "File phan bo phai co "
            "dung 78 dong. "
            f"Thuc te: {len(rows)}"
        )

    print(
        "Tong dong:",
        len(rows),
    )

    # =====================================================
    # 6. AUDIT PER LESSON / ORDER
    # =====================================================
    print()
    print(
        "[6] KIEM TRA TUNG BAI + THU TU"
    )
    line()

    rows_by_lesson = {}

    for row in rows:

        lesson_no = int(
            clean(
                row["SoThuTuBai"]
            )
        )

        if lesson_no < 3 or lesson_no > 23:

            fail(
                "SoThuTuBai ngoai pham vi: "
                f"{lesson_no}"
            )

        rows_by_lesson.setdefault(
            lesson_no,
            [],
        ).append(
            row
        )

    if (
        set(rows_by_lesson)
        != set(range(3, 24))
    ):

        fail(
            "File phan bo khong du "
            "Bai 3 -> 23."
        )

    for lesson_no in range(
        3,
        24,
    ):

        lesson_rows = rows_by_lesson[
            lesson_no
        ]

        actual_orders = [
            int(
                clean(
                    row[
                        "ThuTuNguPhapDeXuat"
                    ]
                )
            )
            for row in lesson_rows
        ]

        expected_orders = list(
            range(
                1,
                len(lesson_rows) + 1,
            )
        )

        if actual_orders != expected_orders:

            fail(
                f"Bai {lesson_no}: "
                "ThuTuNguPhapDeXuat "
                "khong lien tuc.\n"
                f"Thuc te: {actual_orders}\n"
                f"Mong doi: {expected_orders}"
            )

        standard_ids = [
            clean(
                row[
                    "MaMucNguPhapChuan"
                ]
            )
            for row in lesson_rows
        ]

        if (
            len(standard_ids)
            != len(set(standard_ids))
        ):

            fail(
                f"Bai {lesson_no} "
                "co GF1 bi trung."
            )

        print(
            f"Bai {lesson_no:>2}: "
            f"{len(lesson_rows)} muc | OK"
        )

    print()
    print(
        "21/21 BAI: OK"
    )

    # =====================================================
    # 7. VERIFY STANDARD CONTENT
    # =====================================================
    print()
    print(
        "[7] DOI CHIEU TUNG DONG VOI FILE 48 GF1"
    )
    line()

    standard_errors = []

    for row in rows:

        standard_id = clean(
            row[
                "MaMucNguPhapChuan"
            ]
        )

        if standard_id not in standard_by_id:

            standard_errors.append(
                (
                    row["SoThuTuBai"],
                    standard_id,
                    "ID khong ton tai",
                )
            )

            continue

        standard = standard_by_id[
            standard_id
        ]

        comparisons = {
            "SoThuTuChuan": (
                clean(
                    row[
                        "SoThuTuChuan"
                    ]
                ),
                clean(
                    standard[
                        "SoThuTuChuan"
                    ]
                ),
            ),

            "NhomLonTrung": (
                clean(
                    row[
                        "NhomLonTrung"
                    ]
                ),
                clean(
                    standard[
                        "NhomLonTrung"
                    ]
                ),
            ),

            "NhomConTrung": (
                clean(
                    row[
                        "NhomConTrung"
                    ]
                ),
                clean(
                    standard[
                        "NhomConTrung"
                    ]
                ),
            ),

            "TenMucChuan": (
                clean(
                    row[
                        "TenMucChuan"
                    ]
                ),
                clean(
                    standard[
                        "TenMucTrung"
                    ]
                ),
            ),

            "NoiDungChuan": (
                clean(
                    row[
                        "NoiDungChuan"
                    ]
                ),
                clean(
                    standard[
                        "NoiDungChuanTrung"
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

                standard_errors.append(
                    (
                        row[
                            "SoThuTuBai"
                        ],
                        standard_id,
                        field,
                    )
                )

        if (
            clean(
                row["MaNguon"]
            )
            != str(
                EXPECTED_SOURCE_ID
            )
        ):

            standard_errors.append(
                (
                    row[
                        "SoThuTuBai"
                    ],
                    standard_id,
                    "MaNguon",
                )
            )

        if not clean(
            row["LyDoPhanBo"]
        ):

            standard_errors.append(
                (
                    row[
                        "SoThuTuBai"
                    ],
                    standard_id,
                    "LyDoPhanBo trong",
                )
            )

    print(
        "Loi doi chieu:",
        len(standard_errors),
    )

    if standard_errors:

        for error in (
            standard_errors[:30]
        ):

            print(
                " ",
                error,
            )

        fail(
            "File phan bo khong khop "
            "48 muc GF1."
        )

    print(
        "78/78 DONG DOI CHIEU GF1: OK"
    )

    # =====================================================
    # 8. VERIFY INTRO / REVIEW LOGIC
    # =====================================================
    print()
    print(
        "[8] KIEM TRA LOGIC "
        "GIOI THIEU / ON TAP"
    )
    line()

    introduced = set(
        introduced_before
    )

    classification_errors = []

    expected_intro_count = 0
    expected_review_count = 0

    # Phai xu ly dung thu tu bai va thu tu trong bai.
    ordered_rows = sorted(
        rows,
        key=lambda row: (
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
        ),
    )

    for row in ordered_rows:

        standard_id = clean(
            row[
                "MaMucNguPhapChuan"
            ]
        )

        actual_type = clean(
            row["LoaiSuDung"]
        )

        if standard_id in introduced:

            expected_type = (
                "on_tap_mo_rong"
            )

            expected_review_count += 1

        else:

            expected_type = (
                "gioi_thieu"
            )

            expected_intro_count += 1

        if actual_type != expected_type:

            classification_errors.append(
                (
                    row[
                        "SoThuTuBai"
                    ],
                    standard_id,
                    actual_type,
                    expected_type,
                )
            )

        introduced.add(
            standard_id
        )

    print(
        "Gioi thieu tinh lai:",
        expected_intro_count,
    )

    print(
        "On tap/mo rong tinh lai:",
        expected_review_count,
    )

    print(
        "Loi phan loai:",
        len(
            classification_errors
        ),
    )

    if classification_errors:

        for error in (
            classification_errors[:30]
        ):

            print(
                " ",
                error,
            )

        fail(
            "LoaiSuDung khong dung "
            "logic lan xuat hien dau."
        )

    if (
        expected_intro_count
        != EXPECTED_INTRO_COUNT
    ):

        fail(
            "So gioi_thieu "
            "khong bang 38."
        )

    if (
        expected_review_count
        != EXPECTED_REVIEW_COUNT
    ):

        fail(
            "So on_tap_mo_rong "
            "khong bang 40."
        )

    print(
        "38 gioi_thieu + "
        "40 on_tap_mo_rong: OK"
    )

    # =====================================================
    # 9. VERIFY 48 COVERAGE
    # =====================================================
    print()
    print(
        "[9] KIEM TRA BAO PHU GF1"
    )
    line()

    distributed_ids = {
        clean(
            row[
                "MaMucNguPhapChuan"
            ]
        )
        for row in rows
    }

    all_covered = (
        introduced_before
        | distributed_ids
    )

    missing_ids = sorted(
        expected_standard_ids
        - all_covered
    )

    print(
        "GF1 truoc Bai 3:",
        len(
            introduced_before
        ),
    )

    print(
        "GF1 trong Bai 3 -> 23:",
        len(
            distributed_ids
        ),
    )

    print(
        "Tong bao phu:",
        len(
            all_covered
        ),
    )

    print(
        "Con thieu:",
        len(
            missing_ids
        ),
    )

    if missing_ids:

        print(
            "ID thieu:",
            ";".join(
                missing_ids
            ),
        )

        fail(
            "Chua bao phu 48/48."
        )

    if len(all_covered) != 48:

        fail(
            "Tong bao phu "
            "khong bang 48."
        )

    print(
        "48/48 GF1: OK"
    )

    # =====================================================
    # 10. CURRENT REVIEW STATE
    # =====================================================
    print()
    print(
        "[10] KIEM TRA TRANG THAI REVIEW"
    )
    line()

    current_approved = sum(
        1
        for row in rows
        if clean(
            row[
                "DaKiemDuyetPhanBo"
            ]
        ) == "1"
    )

    current_pending = (
        len(rows)
        - current_approved
    )

    invalid_review_values = [
        row
        for row in rows
        if clean(
            row[
                "DaKiemDuyetPhanBo"
            ]
        )
        not in {
            "0",
            "1",
        }
    ]

    if invalid_review_values:

        fail(
            "Co gia tri "
            "DaKiemDuyetPhanBo "
            "khong hop le."
        )

    print(
        "Da kiem duyet hien tai:",
        current_approved,
    )

    print(
        "Cho kiem duyet:",
        current_pending,
    )

    if current_approved != 0:

        fail(
            "File phan bo da co dong "
            "duoc kiem duyet truoc do. "
            "Khong tu dong ghi de."
        )

    # =====================================================
    # 11. BACKUP
    # =====================================================
    print()
    print(
        "[11] BACKUP FILE PHAN BO "
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
            "hsk1_lessons3_23_grammar_distribution_"
            f"before_approve_{timestamp}.csv"
        )
    )

    shutil.copy2(
        DISTRIBUTION_FILE,
        backup_file,
    )

    backup_hash = sha256_file(
        backup_file
    )

    current_hash = sha256_file(
        DISTRIBUTION_FILE
    )

    if backup_hash != current_hash:

        fail(
            "SHA256 backup "
            "khong trung file goc."
        )

    print(
        "Backup:"
    )

    print(
        backup_file
    )

    print()
    print(
        "SHA256:"
    )

    print(
        backup_hash
    )

    print(
        "BACKUP: OK"
    )

    # =====================================================
    # 12. CONFIRM
    # =====================================================
    print()
    print("=" * 120)
    print(
        "XAC NHAN KIEM DUYET 78 DONG"
    )
    print("=" * 120)

    print()
    print(
        "78 dong da qua audit ky thuat:"
    )

    print(
        "  - 21/21 bai hop le"
    )

    print(
        "  - 78/78 mapping GF1 hop le"
    )

    print(
        "  - 38 diem gioi thieu moi"
    )

    print(
        "  - 40 diem on tap/mo rong"
    )

    print(
        "  - Bao phu 48/48 GF1"
    )

    print()
    print(
        "Buoc nay CHI cap nhat file CSV review."
    )

    print(
        "DATABASE KHONG BI SUA."
    )

    confirmation = input(
        "Nhap chinh xac "
        "APPROVE HSK1 GRAMMAR DISTRIBUTION "
        "de tiep tuc: "
    ).strip()

    if (
        confirmation
        != "APPROVE HSK1 GRAMMAR DISTRIBUTION"
    ):

        print()
        print(
            "KHONG NHAN DUOC XAC NHAN."
        )

        print(
            "FILE REVIEW KHONG BI SUA."
        )

        print(
            "DATABASE KHONG BI SUA."
        )

        return

    # =====================================================
    # 13. APPROVE FILE
    # =====================================================
    print()
    print(
        "[12] CAP NHAT FILE REVIEW"
    )
    line()

    for row in rows:

        lesson_no = int(
            clean(
                row[
                    "SoThuTuBai"
                ]
            )
        )

        standard_id = clean(
            row[
                "MaMucNguPhapChuan"
            ]
        )

        usage_type = clean(
            row["LoaiSuDung"]
        )

        row[
            "DaKiemDuyetPhanBo"
        ] = "1"

        if (
            usage_type
            == "gioi_thieu"
        ):

            row[
                "GhiChuKiemDuyet"
            ] = (
                f"Đã kiểm duyệt phân bổ. "
                f"{standard_id} được giới thiệu lần đầu "
                f"ở Bài {lesson_no} trong lộ trình "
                f"do đồ án thiết kế."
            )

        else:

            row[
                "GhiChuKiemDuyet"
            ] = (
                f"Đã kiểm duyệt phân bổ. "
                f"{standard_id} đã xuất hiện trước đó; "
                f"Bài {lesson_no} dùng để ôn tập "
                f"hoặc mở rộng theo chủ đề."
            )

    with open(
        DISTRIBUTION_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=distribution_fields,
        )

        writer.writeheader()

        writer.writerows(
            rows
        )

    # =====================================================
    # 14. VERIFY AFTER WRITE
    # =====================================================
    print()
    print(
        "[13] VERIFY SAU KIEM DUYET"
    )
    line()

    _, verify_rows = load_csv(
        DISTRIBUTION_FILE
    )

    if len(verify_rows) != 78:

        fail(
            "File sau kiem duyet "
            "khong con dung 78 dong."
        )

    approved_after = sum(
        1
        for row in verify_rows
        if clean(
            row[
                "DaKiemDuyetPhanBo"
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

    intro_after = sum(
        1
        for row in verify_rows
        if clean(
            row[
                "LoaiSuDung"
            ]
        ) == "gioi_thieu"
    )

    review_after = sum(
        1
        for row in verify_rows
        if clean(
            row[
                "LoaiSuDung"
            ]
        ) == "on_tap_mo_rong"
    )

    print(
        "Tong dong:",
        len(verify_rows),
    )

    print(
        "DaKiemDuyetPhanBo=1:",
        approved_after,
    )

    print(
        "Thieu GhiChuKiemDuyet:",
        missing_notes,
    )

    print(
        "Gioi thieu:",
        intro_after,
    )

    print(
        "On tap/mo rong:",
        review_after,
    )

    if approved_after != 78:

        fail(
            "Khong kiem duyet du 78 dong."
        )

    if missing_notes != 0:

        fail(
            "Co dong thieu "
            "GhiChuKiemDuyet."
        )

    if intro_after != 38:

        fail(
            "Gioi thieu sau review "
            "khong bang 38."
        )

    if review_after != 40:

        fail(
            "On tap sau review "
            "khong bang 40."
        )

    approved_hash = sha256_file(
        DISTRIBUTION_FILE
    )

    print()
    print(
        "SHA256 file da kiem duyet:"
    )

    print(
        approved_hash
    )

    print(
        "VERIFY SAU KIEM DUYET: OK"
    )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 09H13"
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
        "Tong dong phan bo:",
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
        "GF1 bao phu toan HSK1:",
        "48/48",
    )

    print(
        "Da kiem duyet:",
        approved_after,
    )

    print(
        "Chua kiem duyet:",
        0,
    )

    print()
    print(
        "78/78 PHAN BO NGU PHAP "
        "DA DUOC KIEM DUYET."
    )

    print()
    print(
        "FILE REVIEW:"
    )

    print(
        DISTRIBUTION_FILE
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
        "CHUA TAO NOI DUNG CHI TIET "
        "MoTa / CachDung / VI DU "
        "CHO 78 MUC."
    )

    print(
        "CHUA INSERT NGU PHAP "
        "BAI 3 -> 23."
    )

    print()
    print(
        "BUOC TIEP THEO:"
    )

    print(
        "TU 78 PHAN BO DA KIEM DUYET, "
        "SINH NOI DUNG HOC TAP HOAN CHINH "
        "CHO BAI 3 -> 23 THEO LO."
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
            "09H13 THAT BAI"
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