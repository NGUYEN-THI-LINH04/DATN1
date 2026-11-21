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

# So tu vung da phan bo truoc do cho tung bai.
EXPECTED_VOCAB_COUNTS = {
    3: 23,
    4: 26,
    5: 20,
    6: 24,
    7: 28,
    8: 25,
    9: 22,
    10: 24,
    11: 23,
    12: 22,
    13: 30,
    14: 22,
    15: 11,
    16: 12,
    17: 25,
    18: 22,
    19: 23,
    20: 23,
    21: 20,
    22: 18,
    23: 16,
}

EXPECTED_TOTAL_VOCAB = sum(
    EXPECTED_VOCAB_COUNTS.values()
)

STANDARD_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "hsk1_48_grammar_standard.csv"
)

OUTPUT_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "lesson_context"
)

CONTEXT_FILE = (
    OUTPUT_DIR
    / "hsk1_lessons3_23_grammar_context.csv"
)

SUMMARY_FILE = (
    OUTPUT_DIR
    / "hsk1_lessons3_23_grammar_summary.csv"
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


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "09H11 - CHUAN BI CONTEXT NGU PHAP "
        "HSK1 BAI 3 -> BAI 23"
    )
    print("=" * 120)

    print()
    print("CHE DO:")
    print("  CHI DOC FILE NGU PHAP CHUAN")
    print("  CHI SELECT DATABASE")
    print("  TAO FILE CONTEXT")
    print("  TAO FILE SUMMARY")
    print("  KHONG INSERT dbo.NguPhap")
    print("  KHONG UPDATE dbo.NguPhap")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    # =====================================================
    # 1. VERIFY 48 STANDARD GRAMMAR ITEMS
    # =====================================================
    print()
    print("[1] VERIFY 48 MUC NGU PHAP HSK1 CHUAN")
    line()

    if not STANDARD_FILE.exists():

        fail(
            "Khong tim thay file:\n"
            f"{STANDARD_FILE}"
        )

    standard_fields, standard_rows = load_csv(
        STANDARD_FILE
    )

    required_standard_fields = {
        "MaMucNguPhapChuan",
        "CapDoHSK",
        "SoThuTuChuan",
        "NhomLonTrung",
        "NhomConTrung",
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
            "File ngu phap chuan thieu cot: "
            + ", ".join(
                sorted(
                    missing_standard_fields
                )
            )
        )

    if len(standard_rows) != 48:

        fail(
            "File ngu phap chuan "
            "khong co dung 48 dong."
        )

    standard_ids = [
        clean(
            row["MaMucNguPhapChuan"]
        )
        for row in standard_rows
    ]

    if len(set(standard_ids)) != 48:

        fail(
            "MaMucNguPhapChuan bi trung."
        )

    wrong_source = [
        row
        for row in standard_rows
        if clean(
            row["MaNguon"]
        ) != "1004"
    ]

    if wrong_source:

        fail(
            "Co muc ngu phap chuan "
            "khong co MaNguon=1004."
        )

    print(
        "Tong muc:",
        len(standard_rows),
    )

    print(
        "ID duy nhat:",
        len(set(standard_ids)),
    )

    print(
        "MaNguon=1004: 48/48"
    )

    print(
        "NGU PHAP CHUAN: OK"
    )

    # =====================================================
    # 2. VERIFY EXPECTED COUNTS
    # =====================================================
    print()
    print(
        "[2] VERIFY CAU HINH BAI 3 -> 23"
    )
    line()

    expected_lessons = list(
        range(
            START_LESSON,
            END_LESSON + 1,
        )
    )

    if (
        sorted(EXPECTED_VOCAB_COUNTS.keys())
        != expected_lessons
    ):

        fail(
            "EXPECTED_VOCAB_COUNTS "
            "khong du Bai 3 -> 23."
        )

    if len(
        EXPECTED_VOCAB_COUNTS
    ) != EXPECTED_LESSON_COUNT:

        fail(
            "Phai co dung 21 bai."
        )

    print(
        "So bai:",
        len(EXPECTED_VOCAB_COUNTS),
    )

    print(
        "Tong tu du kien:",
        EXPECTED_TOTAL_VOCAB,
    )

    if EXPECTED_TOTAL_VOCAB != 459:

        fail(
            "Tong tu du kien "
            "khong bang 459."
        )

    print(
        "CAU HINH: OK"
    )

    # =====================================================
    # 3. CONNECT DATABASE
    # =====================================================
    print()
    print("[3] KET NOI DATABASE")
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
                        "Dang ket noi nham database."
                    )

                print(
                    "KET NOI DATABASE: OK"
                )

                # =========================================
                # 4. READ LESSONS 3 -> 23
                # =========================================
                print()
                print(
                    "[4] DOC BAI 3 -> 23"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        bh.MaBaiHoc,
                        bh.SoThuTuBai,
                        bh.TieuDe,
                        bh.TrangThai
                    FROM dbo.BaiHoc AS bh
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc
                    WHERE
                        kh.MaKyHieu = ?
                        AND bh.SoThuTuBai
                            BETWEEN ? AND ?
                    ORDER BY
                        bh.SoThuTuBai;
                    """,
                    COURSE_CODE,
                    START_LESSON,
                    END_LESSON,
                )

                lesson_rows = (
                    cursor.fetchall()
                )

                if (
                    len(lesson_rows)
                    != EXPECTED_LESSON_COUNT
                ):

                    fail(
                        "Phai co dung "
                        "21 bai tu Bai 3 -> 23. "
                        f"Thuc te: "
                        f"{len(lesson_rows)}"
                    )

                lessons = []

                for row in lesson_rows:

                    lesson = {
                        "MaBaiHoc": int(
                            row[0]
                        ),
                        "SoThuTuBai": int(
                            row[1]
                        ),
                        "TieuDe": clean(
                            row[2]
                        ),
                        "TrangThai": clean(
                            row[3]
                        ),
                    }

                    lessons.append(
                        lesson
                    )

                actual_lesson_numbers = [
                    lesson[
                        "SoThuTuBai"
                    ]
                    for lesson in lessons
                ]

                if (
                    actual_lesson_numbers
                    != expected_lessons
                ):

                    fail(
                        "SoThuTuBai khong lien tuc "
                        "3 -> 23."
                    )

                print(
                    "Tong bai:",
                    len(lessons),
                )

                print(
                    "Bai 3 -> 23: OK"
                )

                # =========================================
                # 5. CHECK EXISTING GRAMMAR
                # =========================================
                print()
                print(
                    "[5] KIEM TRA NGU PHAP "
                    "HIEN TAI BAI 3 -> 23"
                )
                line()

                grammar_count_errors = []

                current_grammar_counts = {}

                for lesson in lessons:

                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM dbo.NguPhap
                        WHERE MaBaiHoc = ?;
                        """,
                        lesson[
                            "MaBaiHoc"
                        ],
                    )

                    grammar_count = int(
                        cursor.fetchone()[0]
                    )

                    current_grammar_counts[
                        lesson[
                            "SoThuTuBai"
                        ]
                    ] = grammar_count

                    print(
                        f"Bai "
                        f"{lesson['SoThuTuBai']:>2}: "
                        f"{grammar_count} muc"
                    )

                    if grammar_count != 0:

                        grammar_count_errors.append(
                            (
                                lesson[
                                    "SoThuTuBai"
                                ],
                                grammar_count,
                            )
                        )

                if grammar_count_errors:

                    print()
                    print(
                        "Phat hien bai "
                        "da co ngu phap:"
                    )

                    for (
                        lesson_no,
                        count,
                    ) in grammar_count_errors:

                        print(
                            f"  Bai {lesson_no}: "
                            f"{count} muc"
                        )

                    fail(
                        "Khong tiep tuc "
                        "de tranh ghi de "
                        "du lieu da co."
                    )

                print()
                print(
                    "21/21 BAI CHUA CO NGU PHAP: OK"
                )

                # =========================================
                # 6. READ VOCAB FOR EACH LESSON
                # =========================================
                print()
                print(
                    "[6] DOC TU VUNG "
                    "BAI 3 -> 23"
                )
                line()

                all_vocab = []

                summary_rows = []

                for lesson in lessons:

                    lesson_id = (
                        lesson[
                            "MaBaiHoc"
                        ]
                    )

                    lesson_no = (
                        lesson[
                            "SoThuTuBai"
                        ]
                    )

                    lesson_title = (
                        lesson[
                            "TieuDe"
                        ]
                    )

                    cursor.execute(
                        """
                        SELECT
                            tvbh.ThuTu,
                            tv.MaTuVung,
                            tv.ChuHan,
                            tv.PhienAm,
                            tv.NghiaTiengViet,
                            tv.TuLoai,
                            tv.MaNguon,
                            tv.DaDuyet
                        FROM dbo.TuVungBaiHoc
                            AS tvbh
                        INNER JOIN dbo.TuVung
                            AS tv
                            ON tvbh.MaTuVung
                            = tv.MaTuVung
                        WHERE
                            tvbh.MaBaiHoc = ?
                        ORDER BY
                            tvbh.ThuTu,
                            tv.MaTuVung;
                        """,
                        lesson_id,
                    )

                    vocab_rows = (
                        cursor.fetchall()
                    )

                    expected_count = (
                        EXPECTED_VOCAB_COUNTS[
                            lesson_no
                        ]
                    )

                    actual_count = len(
                        vocab_rows
                    )

                    if (
                        actual_count
                        != expected_count
                    ):

                        fail(
                            f"Bai {lesson_no} "
                            f"phai co "
                            f"{expected_count} tu. "
                            f"Thuc te: "
                            f"{actual_count}"
                        )

                    orders = [
                        int(row[0])
                        for row in vocab_rows
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
                            "ThuTu tu vung "
                            "khong lien tuc."
                        )

                    lesson_vocab = []

                    for row in vocab_rows:

                        item = {
                            "SoThuTuBai": (
                                lesson_no
                            ),

                            "MaBaiHoc": (
                                lesson_id
                            ),

                            "TieuDeBai": (
                                lesson_title
                            ),

                            "ThuTuTrongBai": int(
                                row[0]
                            ),

                            "MaTuVung": int(
                                row[1]
                            ),

                            "ChuHan": clean(
                                row[2]
                            ),

                            "PhienAm": clean(
                                row[3]
                            ),

                            "NghiaTiengViet": clean(
                                row[4]
                            ),

                            "TuLoai": clean(
                                row[5]
                            ),

                            "MaNguonTuVung": (
                                ""
                                if row[6] is None
                                else str(
                                    int(row[6])
                                )
                            ),

                            "DaDuyet": (
                                1
                                if bool(
                                    row[7]
                                )
                                else 0
                            ),
                        }

                        lesson_vocab.append(
                            item
                        )

                    unapproved = [
                        item
                        for item in lesson_vocab
                        if (
                            item["DaDuyet"]
                            != 1
                        )
                    ]

                    if unapproved:

                        fail(
                            f"Bai {lesson_no} "
                            "co tu chua "
                            "DaDuyet=1."
                        )

                    all_vocab.extend(
                        lesson_vocab
                    )

                    summary_rows.append(
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

                            "SoTuVung": (
                                actual_count
                            ),

                            "SoNguPhapHienTai": (
                                current_grammar_counts[
                                    lesson_no
                                ]
                            ),

                            "TrangThaiBaiHoc": (
                                lesson[
                                    "TrangThai"
                                ]
                            ),
                        }
                    )

                    print(
                        f"Bai "
                        f"{lesson_no:>2}: "
                        f"{actual_count:>2} tu "
                        f"| {lesson_title}"
                    )

                # =========================================
                # TOTAL CHECK
                # =========================================
                print()
                print(
                    "Tong tu Bai 3 -> 23:",
                    len(all_vocab),
                )

                if (
                    len(all_vocab)
                    != EXPECTED_TOTAL_VOCAB
                ):

                    fail(
                        "Tong tu Bai 3 -> 23 "
                        "khong bang 459."
                    )

                unique_vocab_ids = {
                    item[
                        "MaTuVung"
                    ]
                    for item in all_vocab
                }

                print(
                    "MaTuVung duy nhat:",
                    len(
                        unique_vocab_ids
                    ),
                )

                print(
                    "DaDuyet=1:",
                    sum(
                        1
                        for item in all_vocab
                        if (
                            item[
                                "DaDuyet"
                            ]
                            == 1
                        )
                    ),
                )

                print(
                    "DOC DU LIEU: OK"
                )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 7. CREATE OUTPUT DIRECTORY
    # =====================================================
    print()
    print(
        "[7] TAO FILE CONTEXT TONG"
    )
    line()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    context_fields = [
        "SoThuTuBai",
        "MaBaiHoc",
        "TieuDeBai",
        "ThuTuTrongBai",
        "MaTuVung",
        "ChuHan",
        "PhienAm",
        "TuLoai",
        "NghiaTiengViet",
        "MaNguonTuVung",
        "DaDuyet",
    ]

    with open(
        CONTEXT_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=context_fields,
        )

        writer.writeheader()

        writer.writerows(
            all_vocab
        )

    print(
        "Context:"
    )

    print(
        CONTEXT_FILE
    )

    # =====================================================
    # 8. CREATE SUMMARY FILE
    # =====================================================
    print()
    print(
        "[8] TAO FILE SUMMARY 21 BAI"
    )
    line()

    summary_fields = [
        "SoThuTuBai",
        "MaBaiHoc",
        "TieuDeBai",
        "SoTuVung",
        "SoNguPhapHienTai",
        "TrangThaiBaiHoc",
    ]

    with open(
        SUMMARY_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=summary_fields,
        )

        writer.writeheader()

        writer.writerows(
            summary_rows
        )

    print(
        "Summary:"
    )

    print(
        SUMMARY_FILE
    )

    # =====================================================
    # 9. VERIFY OUTPUT FILES
    # =====================================================
    print()
    print(
        "[9] VERIFY FILE OUTPUT"
    )
    line()

    _, verify_context = load_csv(
        CONTEXT_FILE
    )

    _, verify_summary = load_csv(
        SUMMARY_FILE
    )

    if (
        len(verify_context)
        != 459
    ):

        fail(
            "Context phai co "
            "459 dong tu vung."
        )

    if (
        len(verify_summary)
        != 21
    ):

        fail(
            "Summary phai co "
            "21 dong."
        )

    lessons_in_context = {
        int(
            clean(
                row["SoThuTuBai"]
            )
        )
        for row in verify_context
    }

    if (
        lessons_in_context
        != set(
            range(3, 24)
        )
    ):

        fail(
            "Context khong du "
            "Bai 3 -> 23."
        )

    print(
        "Context rows:",
        len(verify_context),
    )

    print(
        "Summary rows:",
        len(verify_summary),
    )

    print(
        "Bai 3 -> 23:",
        len(
            lessons_in_context
        ),
    )

    print(
        "VERIFY OUTPUT: OK"
    )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 09H11"
    )
    print("=" * 120)

    print(
        "Bai da doc:",
        21,
    )

    print(
        "Pham vi:",
        "Bai 3 -> Bai 23",
    )

    print(
        "Tong tu vung:",
        len(all_vocab),
    )

    print(
        "Tong ngu phap hien tai:",
        sum(
            row[
                "SoNguPhapHienTai"
            ]
            for row in summary_rows
        ),
    )

    print(
        "Muc ngu phap chuan tham chieu:",
        len(standard_rows),
    )

    print()
    print(
        "CONTEXT FILE:"
    )

    print(
        CONTEXT_FILE
    )

    print()
    print(
        "SUMMARY FILE:"
    )

    print(
        SUMMARY_FILE
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
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
        "PHAN BO CAC DIEM NGU PHAP "
        "CHO TOAN BO BAI 3 -> 23 "
        "TRONG MOT LAN."
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
            "09H11 THAT BAI"
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