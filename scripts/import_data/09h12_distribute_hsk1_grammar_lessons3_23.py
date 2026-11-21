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
# CONFIG
# =========================================================
COURSE_CODE = "HSK1-CORE"

START_LESSON = 3
END_LESSON = 23

EXPECTED_LESSON_COUNT = 21
EXPECTED_CONTEXT_ROWS = 459
EXPECTED_STANDARD_COUNT = 48
EXPECTED_DISTRIBUTION_ROWS = 78

SOURCE_ID = 1004
SOURCE_NAME = "GF0025-2021 - Ngữ pháp HSK"


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

CONTEXT_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "lesson_context"
    / "hsk1_lessons3_23_grammar_context.csv"
)

SUMMARY_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "lesson_context"
    / "hsk1_lessons3_23_grammar_summary.csv"
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

REVIEW_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
)

OUTPUT_FILE = (
    REVIEW_DIR
    / "hsk1_lessons3_23_grammar_distribution_review.csv"
)


# =========================================================
# PHAN BO NGU PHAP CUA DO AN
#
# Day la cach DO AN phan bo cac diem GF1 vao cac bai.
# KHONG khang dinh day la thu tu bai hoc chinh thuc
# cua GF0025.
#
# Mot diem GF1 co the xuat hien lai o bai sau
# de on tap / mo rong.
# =========================================================
DISTRIBUTION = {

    # Bai 3 - Gia dinh
    3: [
        "GF1-005",
        "GF1-020",
        "GF1-027",
        "GF1-037",
    ],

    # Bai 4 - Tuoi
    4: [
        "GF1-007",
        "GF1-023",
        "GF1-033",
    ],

    # Bai 5 - Ngay thang
    5: [
        "GF1-007",
        "GF1-044",
        "GF1-033",
    ],

    # Bai 6 - Gio giac
    6: [
        "GF1-044",
        "GF1-023",
        "GF1-025",
    ],

    # Bai 7 - Hoc o truong
    7: [
        "GF1-016",
        "GF1-028",
        "GF1-029",
        "GF1-032",
    ],

    # Bai 8 - Ngon ngu lop hoc
    8: [
        "GF1-034",
        "GF1-014",
        "GF1-026",
    ],

    # Bai 9 - Sinh hoat hang ngay
    9: [
        "GF1-012",
        "GF1-028",
        "GF1-029",
    ],

    # Bai 10 - An uong / so thich
    10: [
        "GF1-003",
        "GF1-047",
        "GF1-033",
        "GF1-026",
    ],

    # Bai 11 - Mua sam
    11: [
        "GF1-008",
        "GF1-043",
        "GF1-003",
        "GF1-021",
    ],

    # Bai 12 - Nha / noi chon
    12: [
        "GF1-006",
        "GF1-016",
        "GF1-037",
    ],

    # Bai 13 - Phuong vi
    13: [
        "GF1-001",
        "GF1-016",
        "GF1-020",
        "GF1-028",
    ],

    # Bai 14 - Hoi duong
    14: [
        "GF1-015",
        "GF1-001",
        "GF1-033",
        "GF1-046",
    ],

    # Bai 15 - Thoi tiet
    15: [
        "GF1-035",
        "GF1-030",
        "GF1-009",
        "GF1-040",
    ],

    # Bai 16 - Suc khoe
    16: [
        "GF1-040",
        "GF1-014",
        "GF1-041",
    ],

    # Bai 17 - So thich / giai tri
    17: [
        "GF1-017",
        "GF1-019",
        "GF1-039",
        "GF1-010",
    ],

    # Bai 18 - Di lai / du lich
    18: [
        "GF1-010",
        "GF1-015",
        "GF1-024",
        "GF1-025",
    ],

    # Bai 19 - Dang lam gi
    19: [
        "GF1-011",
        "GF1-042",
        "GF1-033",
        "GF1-046",
    ],

    # Bai 20 - Kha nang
    20: [
        "GF1-002",
        "GF1-048",
        "GF1-014",
        "GF1-029",
    ],

    # Bai 21 - So sanh
    21: [
        "GF1-018",
        "GF1-038",
        "GF1-006",
        "GF1-030",
    ],

    # Bai 22 - Goi dien
    22: [
        "GF1-005",
        "GF1-024",
        "GF1-025",
        "GF1-026",
        "GF1-041",
    ],

    # Bai 23 - Tong ket / hen gap
    23: [
        "GF1-031",
        "GF1-032",
        "GF1-012",
        "GF1-022",
    ],
}


# =========================================================
# LY DO PHAN BO
# =========================================================
RATIONALES = {

    3: (
        "Chủ đề gia đình phù hợp với đại từ nhân xưng, "
        "định ngữ sở hữu với 的 và cấu trúc 有."
    ),

    4: (
        "Chủ đề tuổi cần số đếm, cụm số lượng "
        "và câu nghi vấn."
    ),

    5: (
        "Chủ đề ngày tháng cần số đếm, "
        "cách biểu đạt thời gian và câu hỏi."
    ),

    6: (
        "Chủ đề giờ giấc tập trung vào biểu đạt thời gian "
        "và cấu trúc vị ngữ cơ bản."
    ),

    7: (
        "Chủ đề học tập tại trường phù hợp với 在 chỉ nơi chốn, "
        "trạng ngữ và câu vị ngữ động từ."
    ),

    8: (
        "Ngôn ngữ lớp học cần câu cầu khiến, "
        "phủ định với 别 và tân ngữ."
    ),

    9: (
        "Sinh hoạt hằng ngày phù hợp với phó từ tần suất "
        "và trạng ngữ."
    ),

    10: (
        "Chủ đề ăn uống phù hợp với 想/要, "
        "câu lựa chọn 还是 và câu nghi vấn."
    ),

    11: (
        "Mua sắm cần lượng từ, cách nói tiền, "
        "想/要 và trợ từ động thái 了."
    ),

    12: (
        "Chủ đề nhà ở phù hợp với đại từ chỉ thị, "
        "在 chỉ vị trí và câu 有."
    ),

    13: (
        "Chủ đề vị trí cần danh từ phương vị, "
        "在 và trạng ngữ nơi chốn."
    ),

    14: (
        "Hỏi đường cần 从, từ phương vị "
        "và phương pháp đặt câu hỏi."
    ),

    15: (
        "Thời tiết phù hợp với vị ngữ tính từ, "
        "phó từ mức độ, cảm thán và thay đổi trạng thái."
    ),

    16: (
        "Sức khỏe cần biểu đạt thay đổi trạng thái, "
        "phủ định và hành động hoàn thành."
    ),

    17: (
        "Sở thích và giải trí có nhiều thành phần song song, "
        "phù hợp với 和/跟 và câu ghép song song."
    ),

    18: (
        "Đi lại và du lịch phù hợp với 一起, 从 "
        "và củng cố thành phần chủ ngữ - vị ngữ."
    ),

    19: (
        "Chủ đề đang làm gì trực tiếp liên quan đến "
        "在/正/正在 và thể tiếp diễn."
    ),

    20: (
        "Chủ đề khả năng trực tiếp sử dụng 会/能, "
        "phủ định và dạng hỏi chính-phản."
    ),

    21: (
        "Chủ đề so sánh trực tiếp sử dụng 比, "
        "câu so sánh và vị ngữ tính từ."
    ),

    22: (
        "Gọi điện giúp củng cố cấu trúc "
        "chủ ngữ - vị ngữ - tân ngữ "
        "và hành động hoàn thành."
    ),

    23: (
        "Bài cuối phù hợp để củng cố câu không chủ-vị, "
        "câu trần thuật, 再 và trợ từ ngữ khí."
    ),
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
        "09H12 - PHAN BO NGU PHAP "
        "HSK1 BAI 3 -> BAI 23"
    )
    print("=" * 120)

    print()
    print("CHE DO:")
    print("  CHI DOC FILE")
    print("  CHI SELECT DATABASE DE DOI CHIEU")
    print("  TAO FILE REVIEW PHAN BO")
    print("  KHONG INSERT dbo.NguPhap")
    print("  KHONG UPDATE dbo.NguPhap")
    print("  KHONG DELETE")

    # =====================================================
    # 1. VERIFY INPUT FILES
    # =====================================================
    print()
    print("[1] VERIFY FILE DAU VAO")
    print("-" * 120)

    required_files = [
        STANDARD_FILE,
        CONTEXT_FILE,
        SUMMARY_FILE,
        LESSON1_REVIEW_FILE,
        LESSON2_REVIEW_FILE,
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
    # 2. READ 48 STANDARD ITEMS
    # =====================================================
    print()
    print("[2] DOC 48 MUC NGU PHAP CHUAN")
    print("-" * 120)

    standard_fields, standard_rows = (
        load_csv(
            STANDARD_FILE
        )
    )

    required_standard_fields = {
        "MaMucNguPhapChuan",
        "SoThuTuChuan",
        "NhomLonTrung",
        "NhomConTrung",
        "TenMucTrung",
        "NoiDungChuanTrung",
        "MaNguon",
    }

    missing_standard = (
        required_standard_fields
        - set(standard_fields)
    )

    if missing_standard:

        fail(
            "File chuan thieu cot: "
            + ", ".join(
                sorted(missing_standard)
            )
        )

    if len(
        standard_rows
    ) != EXPECTED_STANDARD_COUNT:

        fail(
            "File chuan phai co "
            "dung 48 dong."
        )

    standard_by_id = {}

    for row in standard_rows:

        standard_id = clean(
            row[
                "MaMucNguPhapChuan"
            ]
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
    # 3. READ LESSON 1 REVIEW
    # =====================================================
    print()
    print(
        "[3] DOC CAC GF1 DA DUNG O BAI 1"
    )
    print("-" * 120)

    lesson1_fields, lesson1_rows = (
        load_csv(
            LESSON1_REVIEW_FILE
        )
    )

    if len(lesson1_rows) != 7:

        fail(
            "Review Bai 1 "
            "khong co dung 7 dong."
        )

    if (
        "MaMucNguPhapChuan"
        not in lesson1_fields
        or
        "DaKiemDuyetMapping"
        not in lesson1_fields
    ):

        fail(
            "Review Bai 1 "
            "thieu cot can thiet."
        )

    lesson1_standard_ids = set()

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
                "Bai 1 van co mapping "
                "chua kiem duyet."
            )

        for standard_id in split_ids(
            row[
                "MaMucNguPhapChuan"
            ]
        ):

            if (
                standard_id
                not in standard_by_id
            ):

                fail(
                    "Bai 1 tham chieu "
                    "ID khong ton tai: "
                    f"{standard_id}"
                )

            lesson1_standard_ids.add(
                standard_id
            )

    print(
        "So GF1 duy nhat Bai 1:",
        len(
            lesson1_standard_ids
        ),
    )

    print(
        "Danh sach:",
        ";".join(
            sorted(
                lesson1_standard_ids
            )
        ),
    )

    # =====================================================
    # 4. READ LESSON 2 REVIEW
    # =====================================================
    print()
    print(
        "[4] DOC CAC GF1 DA DUNG O BAI 2"
    )
    print("-" * 120)

    lesson2_fields, lesson2_rows = (
        load_csv(
            LESSON2_REVIEW_FILE
        )
    )

    if len(lesson2_rows) != 3:

        fail(
            "Review Bai 2 "
            "khong co dung 3 dong."
        )

    if (
        "MaMucNguPhapChuan"
        not in lesson2_fields
        or
        "DaKiemDuyetNoiDung"
        not in lesson2_fields
    ):

        fail(
            "Review Bai 2 "
            "thieu cot can thiet."
        )

    lesson2_standard_ids = set()

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
                "Bai 2 van co noi dung "
                "chua kiem duyet."
            )

        for standard_id in split_ids(
            row[
                "MaMucNguPhapChuan"
            ]
        ):

            if (
                standard_id
                not in standard_by_id
            ):

                fail(
                    "Bai 2 tham chieu "
                    "ID khong ton tai: "
                    f"{standard_id}"
                )

            lesson2_standard_ids.add(
                standard_id
            )

    print(
        "So GF1 duy nhat Bai 2:",
        len(
            lesson2_standard_ids
        ),
    )

    print(
        "Danh sach:",
        ";".join(
            sorted(
                lesson2_standard_ids
            )
        ),
    )

    # =====================================================
    # 5. PREVIOUS COVERAGE
    # =====================================================
    print()
    print(
        "[5] PHAM VI DA HOC "
        "SAU BAI 1 + BAI 2"
    )
    print("-" * 120)

    already_introduced = (
        lesson1_standard_ids
        | lesson2_standard_ids
    )

    print(
        "GF1 duy nhat "
        "da xuat hien:",
        len(
            already_introduced
        ),
    )

    print(
        "Danh sach:",
        ";".join(
            sorted(
                already_introduced
            )
        ),
    )

    # =====================================================
    # 6. VERIFY CONTEXT 3 -> 23
    # =====================================================
    print()
    print(
        "[6] VERIFY CONTEXT BAI 3 -> 23"
    )
    print("-" * 120)

    _, context_rows = load_csv(
        CONTEXT_FILE
    )

    if (
        len(context_rows)
        != EXPECTED_CONTEXT_ROWS
    ):

        fail(
            "Context phai co "
            "459 dong."
        )

    context_lessons = {
        int(
            clean(
                row[
                    "SoThuTuBai"
                ]
            )
        )
        for row in context_rows
    }

    if (
        context_lessons
        != set(
            range(
                START_LESSON,
                END_LESSON + 1,
            )
        )
    ):

        fail(
            "Context khong du "
            "Bai 3 -> 23."
        )

    print(
        "Tong tu:",
        len(context_rows),
    )

    print(
        "So bai:",
        len(context_lessons),
    )

    print(
        "CONTEXT: OK"
    )

    # =====================================================
    # 7. VERIFY SUMMARY
    # =====================================================
    print()
    print(
        "[7] VERIFY SUMMARY BAI 3 -> 23"
    )
    print("-" * 120)

    _, summary_rows = load_csv(
        SUMMARY_FILE
    )

    if (
        len(summary_rows)
        != EXPECTED_LESSON_COUNT
    ):

        fail(
            "Summary phai co "
            "21 dong."
        )

    summary_by_lesson = {}

    for row in summary_rows:

        lesson_no = int(
            clean(
                row[
                    "SoThuTuBai"
                ]
            )
        )

        if lesson_no in summary_by_lesson:

            fail(
                "Bai bi trung "
                "trong summary: "
                f"{lesson_no}"
            )

        if (
            clean(
                row[
                    "SoNguPhapHienTai"
                ]
            )
            != "0"
        ):

            fail(
                f"Bai {lesson_no} "
                "trong summary "
                "khong con 0 ngu phap."
            )

        summary_by_lesson[
            lesson_no
        ] = row

    if (
        set(summary_by_lesson)
        != set(range(3, 24))
    ):

        fail(
            "Summary khong du "
            "Bai 3 -> 23."
        )

    print(
        "21/21 bai: OK"
    )

    # =====================================================
    # 8. VERIFY DATABASE CURRENT STATE
    # =====================================================
    print()
    print(
        "[8] DOI CHIEU DATABASE HIEN TAI"
    )
    print("-" * 120)

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
                        DB_NAME()
                    """
                )

                database_name = clean(
                    cursor.fetchone()[0]
                )

                if (
                    database_name.lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi "
                        "nham database."
                    )

                # -----------------------------------------
                # Lesson 1 = 7
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

                counts = {
                    int(row[0]): int(row[1])
                    for row in cursor.fetchall()
                }

                if len(counts) != 23:

                    fail(
                        "Khong doc duoc "
                        "du 23 bai HSK1."
                    )

                print(
                    "Bai 1:",
                    counts[1],
                    "ngu phap",
                )

                print(
                    "Bai 2:",
                    counts[2],
                    "ngu phap",
                )

                if counts[1] != 7:

                    fail(
                        "Bai 1 khong con "
                        "dung 7 ngu phap."
                    )

                if counts[2] != 3:

                    fail(
                        "Bai 2 khong con "
                        "dung 3 ngu phap."
                    )

                nonempty_later = []

                for lesson_no in range(
                    3,
                    24,
                ):

                    if counts[
                        lesson_no
                    ] != 0:

                        nonempty_later.append(
                            (
                                lesson_no,
                                counts[
                                    lesson_no
                                ],
                            )
                        )

                if nonempty_later:

                    print(
                        "Phat hien bai "
                        "3 -> 23 da co ngu phap:"
                    )

                    for item in (
                        nonempty_later
                    ):

                        print(
                            item
                        )

                    fail(
                        "Khong tiep tuc "
                        "de tranh trung du lieu."
                    )

                print(
                    "Bai 3 -> 23:",
                    "0 ngu phap",
                )

                print(
                    "DATABASE STATE: OK"
                )

                # -----------------------------------------
                # Verify source
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
                        "Sai nguon 1004."
                    )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 9. VERIFY DISTRIBUTION
    # =====================================================
    print()
    print(
        "[9] VERIFY PHAN BO BAI 3 -> 23"
    )
    print("-" * 120)

    if (
        set(DISTRIBUTION)
        != set(range(3, 24))
    ):

        fail(
            "DISTRIBUTION "
            "khong du Bai 3 -> 23."
        )

    if (
        set(RATIONALES)
        != set(range(3, 24))
    ):

        fail(
            "RATIONALES "
            "khong du Bai 3 -> 23."
        )

    total_rows = 0

    for lesson_no in range(
        3,
        24,
    ):

        ids = (
            DISTRIBUTION[
                lesson_no
            ]
        )

        if not ids:

            fail(
                f"Bai {lesson_no} "
                "khong co ngu phap."
            )

        if (
            len(ids)
            != len(set(ids))
        ):

            fail(
                f"Bai {lesson_no} "
                "co GF1 bi trung."
            )

        for standard_id in ids:

            if (
                standard_id
                not in standard_by_id
            ):

                fail(
                    f"Bai {lesson_no}: "
                    f"{standard_id} "
                    "khong ton tai."
                )

        total_rows += len(
            ids
        )

        print(
            f"Bai "
            f"{lesson_no:>2}: "
            f"{len(ids)} muc"
        )

    print()
    print(
        "Tong dong phan bo:",
        total_rows,
    )

    if (
        total_rows
        != EXPECTED_DISTRIBUTION_ROWS
    ):

        fail(
            "Tong dong phan bo "
            "khong bang 78."
        )

    # =====================================================
    # 10. CREATE REVIEW
    # =====================================================
    print()
    print(
        "[10] TAO FILE REVIEW PHAN BO"
    )
    print("-" * 120)

    REVIEW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    introduced_ids = set(
        already_introduced
    )

    output_rows = []

    for lesson_no in range(
        3,
        24,
    ):

        summary = (
            summary_by_lesson[
                lesson_no
            ]
        )

        lesson_id = int(
            clean(
                summary[
                    "MaBaiHoc"
                ]
            )
        )

        lesson_title = clean(
            summary[
                "TieuDeBai"
            ]
        )

        for order_no, standard_id in enumerate(
            DISTRIBUTION[
                lesson_no
            ],
            start=1,
        ):

            standard = (
                standard_by_id[
                    standard_id
                ]
            )

            # ---------------------------------------------
            # Xac dinh day la bai gioi thieu hay on tap.
            # ---------------------------------------------
            if (
                standard_id
                in introduced_ids
            ):

                usage_type = (
                    "on_tap_mo_rong"
                )

            else:

                usage_type = (
                    "gioi_thieu"
                )

            output_rows.append(
                {
                    "SoThuTuBai": (
                        lesson_no
                    ),

                    "MaBaiHoc": (
                        lesson_id
                    ),

                    "TieuDeBai": (
                        lesson_title
                    ),

                    "ThuTuNguPhapDeXuat": (
                        order_no
                    ),

                    "MaMucNguPhapChuan": (
                        standard_id
                    ),

                    "SoThuTuChuan": clean(
                        standard[
                            "SoThuTuChuan"
                        ]
                    ),

                    "NhomLonTrung": clean(
                        standard[
                            "NhomLonTrung"
                        ]
                    ),

                    "NhomConTrung": clean(
                        standard[
                            "NhomConTrung"
                        ]
                    ),

                    "TenMucChuan": clean(
                        standard[
                            "TenMucTrung"
                        ]
                    ),

                    "NoiDungChuan": clean(
                        standard[
                            "NoiDungChuanTrung"
                        ]
                    ),

                    "LoaiSuDung": (
                        usage_type
                    ),

                    "LyDoPhanBo": (
                        RATIONALES[
                            lesson_no
                        ]
                    ),

                    "MaNguon": (
                        SOURCE_ID
                    ),

                    "DaKiemDuyetPhanBo": (
                        0
                    ),

                    "GhiChuKiemDuyet": "",
                }
            )

            # Sau lan dau, lan xuat hien sau
            # se la on_tap_mo_rong.
            introduced_ids.add(
                standard_id
            )

    fieldnames = [
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
    ]

    with open(
        OUTPUT_FILE,
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
            output_rows
        )

    print(
        "Da tao:"
    )

    print(
        OUTPUT_FILE
    )

    # =====================================================
    # 11. VERIFY OUTPUT
    # =====================================================
    print()
    print(
        "[11] VERIFY FILE REVIEW"
    )
    print("-" * 120)

    _, verify_rows = load_csv(
        OUTPUT_FILE
    )

    if (
        len(verify_rows)
        != EXPECTED_DISTRIBUTION_ROWS
    ):

        fail(
            "Review phai co "
            "dung 78 dong."
        )

    output_lessons = {
        int(
            clean(
                row[
                    "SoThuTuBai"
                ]
            )
        )
        for row in verify_rows
    }

    if (
        output_lessons
        != set(range(3, 24))
    ):

        fail(
            "Review khong du "
            "Bai 3 -> 23."
        )

    approved_count = sum(
        1
        for row in verify_rows
        if clean(
            row[
                "DaKiemDuyetPhanBo"
            ]
        ) == "1"
    )

    if approved_count != 0:

        fail(
            "File moi tao "
            "khong duoc tu dong "
            "kiem duyet."
        )

    wrong_sources = [
        row
        for row in verify_rows
        if clean(
            row["MaNguon"]
        ) != "1004"
    ]

    if wrong_sources:

        fail(
            "Co dong khong "
            "MaNguon=1004."
        )

    print(
        "Tong dong:",
        len(verify_rows),
    )

    print(
        "So bai:",
        len(output_lessons),
    )

    print(
        "DaKiemDuyetPhanBo=1:",
        approved_count,
    )

    print(
        "Cho kiem duyet:",
        len(verify_rows),
    )

    # =====================================================
    # 12. CHECK COVERAGE 48 / 48
    # =====================================================
    print()
    print(
        "[12] KIEM TRA BAO PHU 48 MUC GF1"
    )
    print("-" * 120)

    distributed_ids = {
        clean(
            row[
                "MaMucNguPhapChuan"
            ]
        )
        for row in verify_rows
    }

    all_covered = (
        already_introduced
        | distributed_ids
    )

    missing_ids = sorted(
        expected_standard_ids
        - all_covered
    )

    print(
        "GF1 da co Bai 1 + 2:",
        len(
            already_introduced
        ),
    )

    print(
        "GF1 xuat hien "
        "Bai 3 -> 23:",
        len(
            distributed_ids
        ),
    )

    print(
        "Tong GF1 bao phu:",
        len(
            all_covered
        ),
    )

    print(
        "GF1 con thieu:",
        len(
            missing_ids
        ),
    )

    if missing_ids:

        print(
            "Danh sach thieu:",
            ";".join(
                missing_ids
            ),
        )

        fail(
            "Chua bao phu "
            "du 48 muc GF1."
        )

    if len(
        all_covered
    ) != 48:

        fail(
            "Tong bao phu "
            "khong bang 48."
        )

    print(
        "48/48 GF1: OK"
    )

    # =====================================================
    # 13. STATISTICS
    # =====================================================
    print()
    print(
        "[13] THONG KE PHAN BO"
    )
    print("-" * 120)

    intro_count = sum(
        1
        for row in verify_rows
        if clean(
            row["LoaiSuDung"]
        ) == "gioi_thieu"
    )

    review_count = sum(
        1
        for row in verify_rows
        if clean(
            row["LoaiSuDung"]
        ) == "on_tap_mo_rong"
    )

    print(
        "Gioi thieu moi:",
        intro_count,
    )

    print(
        "On tap / mo rong:",
        review_count,
    )

    if (
        intro_count
        + review_count
        != 78
    ):

        fail(
            "Thong ke LoaiSuDung "
            "khong bang 78."
        )

    # =====================================================
    # 14. PRINT SUMMARY PER LESSON
    # =====================================================
    print()
    print(
        "[14] TOM TAT TUNG BAI"
    )
    print("-" * 120)

    for lesson_no in range(
        3,
        24,
    ):

        lesson_rows = [
            row
            for row in verify_rows
            if int(
                clean(
                    row[
                        "SoThuTuBai"
                    ]
                )
            ) == lesson_no
        ]

        ids = [
            clean(
                row[
                    "MaMucNguPhapChuan"
                ]
            )
            for row in lesson_rows
        ]

        title = clean(
            lesson_rows[0][
                "TieuDeBai"
            ]
        )

        print(
            f"Bai {lesson_no:>2} | "
            f"{len(lesson_rows)} muc | "
            f"{';'.join(ids)} | "
            f"{title}"
        )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 09H12"
    )
    print("=" * 120)

    print(
        "Bai 1 hien tai:",
        "7 ngu phap",
    )

    print(
        "Bai 2 hien tai:",
        "3 ngu phap",
    )

    print(
        "Pham vi phan bo:",
        "Bai 3 -> Bai 23",
    )

    print(
        "So bai:",
        21,
    )

    print(
        "Tong dong phan bo:",
        len(verify_rows),
    )

    print(
        "Gioi thieu moi:",
        intro_count,
    )

    print(
        "On tap / mo rong:",
        review_count,
    )

    print(
        "GF1 bao phu toan HSK1:",
        "48/48",
    )

    print(
        "Da kiem duyet phan bo:",
        0,
    )

    print(
        "Cho kiem duyet:",
        len(verify_rows),
    )

    print()
    print(
        "FILE REVIEW:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA TAO MoTa / CachDung / VI DU "
        "CHO BAI 3 -> 23."
    )

    print(
        "CHUA INSERT dbo.NguPhap "
        "BAI 3 -> 23."
    )

    print()
    print(
        "LUU Y:"
    )

    print(
        "DAY LA PHAN BO BAI HOC "
        "DO DO AN TU THIET KE "
        "DUA TREN 48 MUC THAM CHIEU GF0025."
    )

    print(
        "KHONG CO NGHIA GF0025 "
        "QUY DINH CAC MUC PHAI NAM "
        "O DUNG NHUNG BAI NAY."
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
            "09H12 THAT BAI"
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