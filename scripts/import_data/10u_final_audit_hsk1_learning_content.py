from pathlib import Path
import csv
import sys
from collections import defaultdict
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

EXPECTED_LESSONS = 23

EXPECTED_VOCAB = 501
EXPECTED_GRAMMAR = 88
EXPECTED_HANZI = 301
EXPECTED_RADICALS = 214
EXPECTED_STROKES = 2162

VOCAB_STANDARD_SOURCE = 1002
VOCAB_SUPPLEMENT_SOURCE = 2

GRAMMAR_SOURCE = 1004

HANZI_SOURCE = 1005
STROKE_SOURCE = 3


# =========================================================
# EXPECTED VOCAB PER LESSON
# =========================================================
EXPECTED_VOCAB_COUNTS = {
    1: 13,
    2: 29,   # 28 standard + 越南
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


# =========================================================
# PATHS
# =========================================================
REVIEW_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "review"
)

OUTPUT_SUMMARY = (
    REVIEW_DIR
    / "hsk1_10u_final_lesson_audit.csv"
)

OUTPUT_ISSUES = (
    REVIEW_DIR
    / "hsk1_10u_final_issues.csv"
)

OUTPUT_OPTIONAL = (
    REVIEW_DIR
    / "hsk1_10u_optional_content_gaps.csv"
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


def write_csv(
    path,
    fieldnames,
    rows,
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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
        writer.writerows(rows)


def add_issue(
    issues,
    category,
    lesson,
    object_name,
    problem,
    detail="",
):

    issues.append(
        {
            "Nhom": category,
            "Bai": lesson,
            "DoiTuong": object_name,
            "VanDe": problem,
            "ChiTiet": detail,
        }
    )


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10U - FINAL AUDIT NOI DUNG HOC BAI HSK1"
    )
    print("=" * 120)

    print()
    print("MUC TIEU:")
    print("  KIEM TRA 23 BAI HSK1")
    print("  KIEM TRA 501 TU VUNG")
    print("  KIEM TRA 88 NGU PHAP")
    print("  KIEM TRA 301 CHU HAN")
    print("  KIEM TRA 214 BO THU")
    print("  KIEM TRA 2162 NET CHU HAN")
    print("  DOI CHIEU SO NET TUNG CHU")
    print("  PHAT HIEN TRUNG THU TU / THIEU DU LIEU")
    print()
    print("CHE DO:")
    print("  CHI SELECT DATABASE")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    issues = []
    optional_gaps = []

    # =====================================================
    # CONNECT
    # =====================================================
    print()
    print("[1] KET NOI DATABASE")
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
                        DB_NAME(),
                        CONVERT(
                            nvarchar(128),
                            SERVERPROPERTY('ServerName')
                        );
                    """
                )

                db_name, server_name = (
                    cursor.fetchone()
                )

                print(
                    "Server:",
                    clean(server_name),
                )

                print(
                    "Database:",
                    clean(db_name),
                )

                if (
                    clean(db_name).lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi nham database."
                    )

                # =================================================
                # 2. COURSE + LESSONS
                # =================================================
                print()
                print(
                    "[2] KIEM TRA KHOA HOC + 23 BAI"
                )
                print("-" * 120)

                cursor.execute(
                    """
                    SELECT
                        MaKhoaHoc,
                        MaKyHieu,
                        TieuDe
                    FROM dbo.KhoaHoc
                    WHERE MaKyHieu = ?;
                    """,
                    COURSE_CODE,
                )

                course_rows = (
                    cursor.fetchall()
                )

                if len(course_rows) != 1:

                    fail(
                        "Khong tim thay duy nhat "
                        "HSK1-CORE."
                    )

                ma_khoa_hoc = int(
                    course_rows[0][0]
                )

                print(
                    "MaKhoaHoc:",
                    ma_khoa_hoc,
                )

                print(
                    "MaKyHieu:",
                    clean(
                        course_rows[0][1]
                    ),
                )

                print(
                    "TieuDe:",
                    clean(
                        course_rows[0][2]
                    ),
                )

                cursor.execute(
                    """
                    SELECT
                        MaBaiHoc,
                        SoThuTuBai,
                        TieuDe
                    FROM dbo.BaiHoc
                    WHERE MaKhoaHoc = ?
                    ORDER BY SoThuTuBai;
                    """,
                    ma_khoa_hoc,
                )

                lesson_rows = (
                    cursor.fetchall()
                )

                lessons = {}

                for row in lesson_rows:

                    lesson_no = int(
                        row[1]
                    )

                    if lesson_no in lessons:

                        add_issue(
                            issues,
                            "BAI_HOC",
                            lesson_no,
                            "",
                            "TRUNG_SOTHUTUBAI",
                        )

                    lessons[
                        lesson_no
                    ] = {
                        "MaBaiHoc": int(
                            row[0]
                        ),
                        "TieuDe": clean(
                            row[2]
                        ),
                    }

                print(
                    "Tong bai:",
                    len(lesson_rows),
                    "/23",
                )

                expected_lesson_numbers = set(
                    range(
                        1,
                        EXPECTED_LESSONS + 1,
                    )
                )

                actual_lesson_numbers = set(
                    lessons
                )

                if (
                    actual_lesson_numbers
                    != expected_lesson_numbers
                ):

                    missing_lessons = (
                        expected_lesson_numbers
                        - actual_lesson_numbers
                    )

                    extra_lessons = (
                        actual_lesson_numbers
                        - expected_lesson_numbers
                    )

                    add_issue(
                        issues,
                        "BAI_HOC",
                        "",
                        "",
                        "DANH_SACH_BAI_KHONG_DUNG",
                        (
                            f"Thieu={sorted(missing_lessons)} "
                            f"| Thua={sorted(extra_lessons)}"
                        ),
                    )

                # =================================================
                # 3. VOCABULARY
                # =================================================
                print()
                print(
                    "[3] KIEM TRA TU VUNG"
                )
                print("-" * 120)

                cursor.execute(
                    """
                    SELECT
                        bh.SoThuTuBai,
                        COUNT(tvbh.MaTuVung) AS SoTu,

                        SUM(
                            CASE
                                WHEN tvbh.MaTuVung IS NOT NULL
                                     AND tv.DaDuyet = 1
                                THEN 1
                                ELSE 0
                            END
                        ) AS DaDuyet,

                        SUM(
                            CASE
                                WHEN tvbh.MaTuVung IS NOT NULL
                                     AND NULLIF(
                                         LTRIM(
                                             RTRIM(
                                                 tv.ChuHan
                                             )
                                         ),
                                         N''
                                     ) IS NULL
                                THEN 1
                                ELSE 0
                            END
                        ) AS ThieuChuHan,

                        SUM(
                            CASE
                                WHEN tvbh.MaTuVung IS NOT NULL
                                     AND NULLIF(
                                         LTRIM(
                                             RTRIM(
                                                 tv.PhienAm
                                             )
                                         ),
                                         N''
                                     ) IS NULL
                                THEN 1
                                ELSE 0
                            END
                        ) AS ThieuPinyin,

                        SUM(
                            CASE
                                WHEN tvbh.MaTuVung IS NOT NULL
                                     AND NULLIF(
                                         LTRIM(
                                             RTRIM(
                                                 tv.NghiaTiengViet
                                             )
                                         ),
                                         N''
                                     ) IS NULL
                                THEN 1
                                ELSE 0
                            END
                        ) AS ThieuNghia

                    FROM dbo.BaiHoc AS bh

                    LEFT JOIN dbo.TuVungBaiHoc AS tvbh
                        ON bh.MaBaiHoc
                        = tvbh.MaBaiHoc

                    LEFT JOIN dbo.TuVung AS tv
                        ON tvbh.MaTuVung
                        = tv.MaTuVung

                    WHERE
                        bh.MaKhoaHoc = ?

                    GROUP BY
                        bh.SoThuTuBai

                    ORDER BY
                        bh.SoThuTuBai;
                    """,
                    ma_khoa_hoc,
                )

                vocab_by_lesson = {}

                vocab_total = 0
                vocab_approved = 0
                vocab_missing_hanzi = 0
                vocab_missing_pinyin = 0
                vocab_missing_meaning = 0

                for row in cursor.fetchall():

                    lesson_no = int(
                        row[0]
                    )

                    count = int(
                        row[1] or 0
                    )

                    approved = int(
                        row[2] or 0
                    )

                    missing_hanzi = int(
                        row[3] or 0
                    )

                    missing_pinyin = int(
                        row[4] or 0
                    )

                    missing_meaning = int(
                        row[5] or 0
                    )

                    vocab_by_lesson[
                        lesson_no
                    ] = count

                    vocab_total += count
                    vocab_approved += approved

                    vocab_missing_hanzi += (
                        missing_hanzi
                    )

                    vocab_missing_pinyin += (
                        missing_pinyin
                    )

                    vocab_missing_meaning += (
                        missing_meaning
                    )

                    expected_count = (
                        EXPECTED_VOCAB_COUNTS[
                            lesson_no
                        ]
                    )

                    if count != expected_count:

                        add_issue(
                            issues,
                            "TU_VUNG",
                            lesson_no,
                            "",
                            "SAI_SO_LUONG",
                            (
                                f"SQL={count} "
                                f"| MongDoi={expected_count}"
                            ),
                        )

                print(
                    "Tong TuVung:",
                    vocab_total,
                    "/501",
                )

                print(
                    "DaDuyet=1:",
                    vocab_approved,
                    "/501",
                )

                print(
                    "Thieu ChuHan:",
                    vocab_missing_hanzi,
                )

                print(
                    "Thieu Pinyin:",
                    vocab_missing_pinyin,
                )

                print(
                    "Thieu nghia Viet:",
                    vocab_missing_meaning,
                )

                if vocab_total != EXPECTED_VOCAB:

                    add_issue(
                        issues,
                        "TU_VUNG",
                        "",
                        "",
                        "TONG_KHONG_BANG_501",
                        str(vocab_total),
                    )

                if (
                    vocab_approved
                    != EXPECTED_VOCAB
                ):

                    add_issue(
                        issues,
                        "TU_VUNG",
                        "",
                        "",
                        "CHUA_DUYET_DU_501",
                        str(vocab_approved),
                    )

                if (
                    vocab_missing_hanzi
                    + vocab_missing_pinyin
                    + vocab_missing_meaning
                    > 0
                ):

                    add_issue(
                        issues,
                        "TU_VUNG",
                        "",
                        "",
                        "THIEU_TRUONG_BAT_BUOC",
                        (
                            f"ChuHan={vocab_missing_hanzi} "
                            f"| Pinyin={vocab_missing_pinyin} "
                            f"| Nghia={vocab_missing_meaning}"
                        ),
                    )

                # -----------------------------------------
                # Vocabulary sources
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        tv.MaNguon,
                        COUNT(DISTINCT tv.MaTuVung)

                    FROM dbo.TuVung AS tv

                    INNER JOIN dbo.TuVungBaiHoc AS tvbh
                        ON tv.MaTuVung
                        = tvbh.MaTuVung

                    INNER JOIN dbo.BaiHoc AS bh
                        ON tvbh.MaBaiHoc
                        = bh.MaBaiHoc

                    WHERE
                        bh.MaKhoaHoc = ?

                    GROUP BY
                        tv.MaNguon

                    ORDER BY
                        tv.MaNguon;
                    """,
                    ma_khoa_hoc,
                )

                vocab_source_counts = {
                    int(row[0]): int(row[1])
                    for row in cursor.fetchall()
                }

                print(
                    "MaNguon=1002:",
                    vocab_source_counts.get(
                        VOCAB_STANDARD_SOURCE,
                        0,
                    ),
                )

                print(
                    "MaNguon=2:",
                    vocab_source_counts.get(
                        VOCAB_SUPPLEMENT_SOURCE,
                        0,
                    ),
                )

                if (
                    vocab_source_counts.get(
                        VOCAB_STANDARD_SOURCE,
                        0,
                    )
                    != 500
                ):

                    add_issue(
                        issues,
                        "TU_VUNG",
                        "",
                        "",
                        "NGUON_HSK_CHUAN_KHONG_BANG_500",
                        str(
                            vocab_source_counts.get(
                                VOCAB_STANDARD_SOURCE,
                                0,
                            )
                        ),
                    )

                if (
                    vocab_source_counts.get(
                        VOCAB_SUPPLEMENT_SOURCE,
                        0,
                    )
                    != 1
                ):

                    add_issue(
                        issues,
                        "TU_VUNG",
                        "",
                        "越南",
                        "TU_BO_SUNG_NGUON_2_KHONG_BANG_1",
                        str(
                            vocab_source_counts.get(
                                VOCAB_SUPPLEMENT_SOURCE,
                                0,
                            )
                        ),
                    )

                # -----------------------------------------
                # Duplicate vocabulary order
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        bh.SoThuTuBai,
                        tvbh.ThuTu,
                        COUNT(*)

                    FROM dbo.TuVungBaiHoc AS tvbh

                    INNER JOIN dbo.BaiHoc AS bh
                        ON tvbh.MaBaiHoc
                        = bh.MaBaiHoc

                    WHERE
                        bh.MaKhoaHoc = ?

                    GROUP BY
                        bh.SoThuTuBai,
                        tvbh.ThuTu

                    HAVING
                        COUNT(*) > 1;
                    """,
                    ma_khoa_hoc,
                )

                duplicate_vocab_order = (
                    cursor.fetchall()
                )

                print(
                    "Trung ThuTu TuVung:",
                    len(
                        duplicate_vocab_order
                    ),
                )

                for row in duplicate_vocab_order:

                    add_issue(
                        issues,
                        "TU_VUNG",
                        int(row[0]),
                        "",
                        "TRUNG_THUTU",
                        (
                            f"ThuTu={row[1]} "
                            f"| SoLuong={row[2]}"
                        ),
                    )

                # -----------------------------------------
                # Optional vocabulary examples
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        SUM(
                            CASE
                                WHEN NULLIF(
                                    LTRIM(
                                        RTRIM(
                                            tv.ViDuTiengTrung
                                        )
                                    ),
                                    N''
                                ) IS NULL
                                THEN 1
                                ELSE 0
                            END
                        ),
                        SUM(
                            CASE
                                WHEN NULLIF(
                                    LTRIM(
                                        RTRIM(
                                            tv.ViDuTiengViet
                                        )
                                    ),
                                    N''
                                ) IS NULL
                                THEN 1
                                ELSE 0
                            END
                        )

                    FROM dbo.TuVung AS tv

                    INNER JOIN dbo.TuVungBaiHoc AS tvbh
                        ON tv.MaTuVung
                        = tvbh.MaTuVung

                    INNER JOIN dbo.BaiHoc AS bh
                        ON tvbh.MaBaiHoc
                        = bh.MaBaiHoc

                    WHERE
                        bh.MaKhoaHoc = ?;
                    """,
                    ma_khoa_hoc,
                )

                row = cursor.fetchone()

                vocab_missing_example_cn = int(
                    row[0] or 0
                )

                vocab_missing_example_vi = int(
                    row[1] or 0
                )

                optional_gaps.append(
                    {
                        "Nhom": "TU_VUNG",
                        "Truong": "ViDuTiengTrung",
                        "SoLuongTrong": (
                            vocab_missing_example_cn
                        ),
                        "BatBuocDeKhoaNoiDungLoi": "KHONG",
                    }
                )

                optional_gaps.append(
                    {
                        "Nhom": "TU_VUNG",
                        "Truong": "ViDuTiengViet",
                        "SoLuongTrong": (
                            vocab_missing_example_vi
                        ),
                        "BatBuocDeKhoaNoiDungLoi": "KHONG",
                    }
                )

                # =================================================
                # 4. GRAMMAR
                # =================================================
                print()
                print(
                    "[4] KIEM TRA NGU PHAP"
                )
                print("-" * 120)

                cursor.execute(
                    """
                    SELECT
                        bh.SoThuTuBai,
                        COUNT(ng.MaNguPhap),

                        SUM(
                            CASE
                                WHEN ng.MaNguPhap IS NOT NULL
                                     AND NULLIF(
                                         LTRIM(
                                             RTRIM(
                                                 ng.TenCauTruc
                                             )
                                         ),
                                         N''
                                     ) IS NULL
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN ng.MaNguPhap IS NOT NULL
                                     AND NULLIF(
                                         LTRIM(
                                             RTRIM(
                                                 ng.MoTa
                                             )
                                         ),
                                         N''
                                     ) IS NULL
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN ng.MaNguPhap IS NOT NULL
                                     AND NULLIF(
                                         LTRIM(
                                             RTRIM(
                                                 ng.CachDung
                                             )
                                         ),
                                         N''
                                     ) IS NULL
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN ng.MaNguPhap IS NOT NULL
                                     AND NULLIF(
                                         LTRIM(
                                             RTRIM(
                                                 ng.ViDuTiengTrung
                                             )
                                         ),
                                         N''
                                     ) IS NULL
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN ng.MaNguPhap IS NOT NULL
                                     AND NULLIF(
                                         LTRIM(
                                             RTRIM(
                                                 ng.ViDuPinyin
                                             )
                                         ),
                                         N''
                                     ) IS NULL
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN ng.MaNguPhap IS NOT NULL
                                     AND NULLIF(
                                         LTRIM(
                                             RTRIM(
                                                 ng.ViDuTiengViet
                                             )
                                         ),
                                         N''
                                     ) IS NULL
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN ng.MaNguPhap IS NOT NULL
                                     AND ng.MaNguon = ?
                                THEN 1 ELSE 0
                            END
                        )

                    FROM dbo.BaiHoc AS bh

                    LEFT JOIN dbo.NguPhap AS ng
                        ON bh.MaBaiHoc
                        = ng.MaBaiHoc

                    WHERE
                        bh.MaKhoaHoc = ?

                    GROUP BY
                        bh.SoThuTuBai

                    ORDER BY
                        bh.SoThuTuBai;
                    """,
                    GRAMMAR_SOURCE,
                    ma_khoa_hoc,
                )

                grammar_by_lesson = {}

                grammar_total = 0

                grammar_missing = 0
                grammar_source_count = 0

                for row in cursor.fetchall():

                    lesson_no = int(
                        row[0]
                    )

                    count = int(
                        row[1] or 0
                    )

                    grammar_by_lesson[
                        lesson_no
                    ] = count

                    grammar_total += count

                    missing_fields = sum(
                        int(value or 0)
                        for value
                        in row[2:8]
                    )

                    grammar_missing += (
                        missing_fields
                    )

                    grammar_source_count += int(
                        row[8] or 0
                    )

                    if count <= 0:

                        add_issue(
                            issues,
                            "NGU_PHAP",
                            lesson_no,
                            "",
                            "BAI_KHONG_CO_NGU_PHAP",
                        )

                    if missing_fields > 0:

                        add_issue(
                            issues,
                            "NGU_PHAP",
                            lesson_no,
                            "",
                            "THIEU_NOI_DUNG_NGU_PHAP",
                            str(
                                missing_fields
                            ),
                        )

                print(
                    "Tong NguPhap:",
                    grammar_total,
                    "/88",
                )

                print(
                    "Bai co NguPhap:",
                    sum(
                        1
                        for value
                        in grammar_by_lesson.values()
                        if value > 0
                    ),
                    "/23",
                )

                print(
                    "Thieu truong noi dung:",
                    grammar_missing,
                )

                print(
                    "MaNguon=1004:",
                    grammar_source_count,
                    "/88",
                )

                if grammar_total != EXPECTED_GRAMMAR:

                    add_issue(
                        issues,
                        "NGU_PHAP",
                        "",
                        "",
                        "TONG_KHONG_BANG_88",
                        str(grammar_total),
                    )

                if (
                    grammar_source_count
                    != EXPECTED_GRAMMAR
                ):

                    add_issue(
                        issues,
                        "NGU_PHAP",
                        "",
                        "",
                        "NGUON_1004_KHONG_DU_88",
                        str(
                            grammar_source_count
                        ),
                    )

                # -----------------------------------------
                # Grammar duplicate order
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        bh.SoThuTuBai,
                        ng.ThuTu,
                        COUNT(*)

                    FROM dbo.NguPhap AS ng

                    INNER JOIN dbo.BaiHoc AS bh
                        ON ng.MaBaiHoc
                        = bh.MaBaiHoc

                    WHERE
                        bh.MaKhoaHoc = ?

                    GROUP BY
                        bh.SoThuTuBai,
                        ng.ThuTu

                    HAVING
                        COUNT(*) > 1;
                    """,
                    ma_khoa_hoc,
                )

                duplicate_grammar_order = (
                    cursor.fetchall()
                )

                print(
                    "Trung ThuTu NguPhap:",
                    len(
                        duplicate_grammar_order
                    ),
                )

                for row in duplicate_grammar_order:

                    add_issue(
                        issues,
                        "NGU_PHAP",
                        int(row[0]),
                        "",
                        "TRUNG_THUTU",
                        (
                            f"ThuTu={row[1]}"
                        ),
                    )

                # =================================================
                # 5. HANZI
                # =================================================
                print()
                print(
                    "[5] KIEM TRA CHU HAN"
                )
                print("-" * 120)

                cursor.execute(
                    """
                    SELECT
                        bh.SoThuTuBai,
                        COUNT(ch.MaChuHan),

                        SUM(
                            CASE
                                WHEN ch.MaChuHan IS NOT NULL
                                     AND NULLIF(
                                         LTRIM(
                                             RTRIM(
                                                 ch.Pinyin
                                             )
                                         ),
                                         N''
                                     ) IS NULL
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN ch.MaChuHan IS NOT NULL
                                     AND NULLIF(
                                         LTRIM(
                                             RTRIM(
                                                 ch.NghiaTiengViet
                                             )
                                         ),
                                         N''
                                     ) IS NULL
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN ch.MaChuHan IS NOT NULL
                                     AND ch.MaBoThu IS NULL
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN ch.MaChuHan IS NOT NULL
                                     AND (
                                         ch.SoNet IS NULL
                                         OR ch.SoNet <= 0
                                     )
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN ch.MaChuHan IS NOT NULL
                                     AND ch.MaNguon = ?
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN ch.MaChuHan IS NOT NULL
                                THEN ch.SoNet
                                ELSE 0
                            END
                        )

                    FROM dbo.BaiHoc AS bh

                    LEFT JOIN dbo.ChuHan AS ch
                        ON bh.MaBaiHoc
                        = ch.MaBaiHoc

                    WHERE
                        bh.MaKhoaHoc = ?

                    GROUP BY
                        bh.SoThuTuBai

                    ORDER BY
                        bh.SoThuTuBai;
                    """,
                    HANZI_SOURCE,
                    ma_khoa_hoc,
                )

                hanzi_by_lesson = {}
                expected_strokes_by_lesson = {}

                hanzi_total = 0
                hanzi_missing_pinyin = 0
                hanzi_missing_meaning = 0
                hanzi_missing_radical = 0
                hanzi_missing_strokes = 0
                hanzi_source_count = 0
                expected_stroke_total = 0

                for row in cursor.fetchall():

                    lesson_no = int(
                        row[0]
                    )

                    count = int(
                        row[1] or 0
                    )

                    hanzi_by_lesson[
                        lesson_no
                    ] = count

                    hanzi_total += count

                    hanzi_missing_pinyin += int(
                        row[2] or 0
                    )

                    hanzi_missing_meaning += int(
                        row[3] or 0
                    )

                    hanzi_missing_radical += int(
                        row[4] or 0
                    )

                    hanzi_missing_strokes += int(
                        row[5] or 0
                    )

                    hanzi_source_count += int(
                        row[6] or 0
                    )

                    expected_strokes = int(
                        row[7] or 0
                    )

                    expected_strokes_by_lesson[
                        lesson_no
                    ] = expected_strokes

                    expected_stroke_total += (
                        expected_strokes
                    )

                    if count <= 0:

                        add_issue(
                            issues,
                            "CHU_HAN",
                            lesson_no,
                            "",
                            "BAI_KHONG_CO_CHU_HAN",
                        )

                print(
                    "Tong ChuHan:",
                    hanzi_total,
                    "/301",
                )

                print(
                    "Bai co ChuHan:",
                    sum(
                        1
                        for value
                        in hanzi_by_lesson.values()
                        if value > 0
                    ),
                    "/23",
                )

                print(
                    "Thieu Pinyin:",
                    hanzi_missing_pinyin,
                )

                print(
                    "Thieu nghia Viet:",
                    hanzi_missing_meaning,
                )

                print(
                    "Thieu MaBoThu:",
                    hanzi_missing_radical,
                )

                print(
                    "Thieu/loi SoNet:",
                    hanzi_missing_strokes,
                )

                print(
                    "MaNguon=1005:",
                    hanzi_source_count,
                    "/301",
                )

                if hanzi_total != EXPECTED_HANZI:

                    add_issue(
                        issues,
                        "CHU_HAN",
                        "",
                        "",
                        "TONG_KHONG_BANG_301",
                        str(hanzi_total),
                    )

                if (
                    hanzi_source_count
                    != EXPECTED_HANZI
                ):

                    add_issue(
                        issues,
                        "CHU_HAN",
                        "",
                        "",
                        "NGUON_1005_KHONG_DU_301",
                        str(
                            hanzi_source_count
                        ),
                    )

                if (
                    hanzi_missing_pinyin
                    + hanzi_missing_meaning
                    + hanzi_missing_radical
                    + hanzi_missing_strokes
                    > 0
                ):

                    add_issue(
                        issues,
                        "CHU_HAN",
                        "",
                        "",
                        "THIEU_TRUONG_BAT_BUOC",
                        (
                            f"Pinyin={hanzi_missing_pinyin} "
                            f"| Nghia={hanzi_missing_meaning} "
                            f"| BoThu={hanzi_missing_radical} "
                            f"| SoNet={hanzi_missing_strokes}"
                        ),
                    )

                # -----------------------------------------
                # Duplicate KyTu
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        ch.KyTu,
                        COUNT(*)

                    FROM dbo.ChuHan AS ch

                    INNER JOIN dbo.BaiHoc AS bh
                        ON ch.MaBaiHoc
                        = bh.MaBaiHoc

                    WHERE
                        bh.MaKhoaHoc = ?

                    GROUP BY
                        ch.KyTu

                    HAVING
                        COUNT(*) > 1;
                    """,
                    ma_khoa_hoc,
                )

                duplicate_hanzi = (
                    cursor.fetchall()
                )

                print(
                    "Trung KyTu ChuHan:",
                    len(
                        duplicate_hanzi
                    ),
                )

                for row in duplicate_hanzi:

                    add_issue(
                        issues,
                        "CHU_HAN",
                        "",
                        clean(row[0]),
                        "TRUNG_KYTU",
                        str(row[1]),
                    )

                # -----------------------------------------
                # Duplicate order
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        bh.SoThuTuBai,
                        ch.ThuTu,
                        COUNT(*)

                    FROM dbo.ChuHan AS ch

                    INNER JOIN dbo.BaiHoc AS bh
                        ON ch.MaBaiHoc
                        = bh.MaBaiHoc

                    WHERE
                        bh.MaKhoaHoc = ?

                    GROUP BY
                        bh.SoThuTuBai,
                        ch.ThuTu

                    HAVING
                        COUNT(*) > 1;
                    """,
                    ma_khoa_hoc,
                )

                duplicate_hanzi_order = (
                    cursor.fetchall()
                )

                print(
                    "Trung ThuTu ChuHan:",
                    len(
                        duplicate_hanzi_order
                    ),
                )

                for row in duplicate_hanzi_order:

                    add_issue(
                        issues,
                        "CHU_HAN",
                        int(row[0]),
                        "",
                        "TRUNG_THUTU",
                        (
                            f"ThuTu={row[1]}"
                        ),
                    )

                # -----------------------------------------
                # Optional Hanzi teaching content
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        SUM(
                            CASE
                                WHEN NULLIF(
                                    LTRIM(
                                        RTRIM(
                                            ch.CachGhiNho
                                        )
                                    ),
                                    N''
                                ) IS NULL
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN NULLIF(
                                    LTRIM(
                                        RTRIM(
                                            ch.ViDuTiengTrung
                                        )
                                    ),
                                    N''
                                ) IS NULL
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN NULLIF(
                                    LTRIM(
                                        RTRIM(
                                            ch.ViDuPinyin
                                        )
                                    ),
                                    N''
                                ) IS NULL
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN NULLIF(
                                    LTRIM(
                                        RTRIM(
                                            ch.ViDuTiengViet
                                        )
                                    ),
                                    N''
                                ) IS NULL
                                THEN 1 ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN ch.MaTep IS NULL
                                THEN 1 ELSE 0
                            END
                        )

                    FROM dbo.ChuHan AS ch

                    INNER JOIN dbo.BaiHoc AS bh
                        ON ch.MaBaiHoc
                        = bh.MaBaiHoc

                    WHERE
                        bh.MaKhoaHoc = ?;
                    """,
                    ma_khoa_hoc,
                )

                optional_hanzi = (
                    cursor.fetchone()
                )

                optional_names = [
                    "CachGhiNho",
                    "ViDuTiengTrung",
                    "ViDuPinyin",
                    "ViDuTiengViet",
                    "MaTep",
                ]

                for index, name in enumerate(
                    optional_names
                ):

                    optional_gaps.append(
                        {
                            "Nhom": "CHU_HAN",
                            "Truong": name,
                            "SoLuongTrong": int(
                                optional_hanzi[
                                    index
                                ]
                                or 0
                            ),
                            "BatBuocDeKhoaNoiDungLoi": "KHONG",
                        }
                    )

                # =================================================
                # 6. RADICALS
                # =================================================
                print()
                print(
                    "[6] KIEM TRA 214 BO THU"
                )
                print("-" * 120)

                cursor.execute(
                    """
                    SELECT
                        COUNT(*),
                        COUNT(
                            DISTINCT KyHieu
                        ),
                        COUNT(
                            DISTINCT SoBoThu
                        ),
                        MIN(SoBoThu),
                        MAX(SoBoThu)
                    FROM dbo.BoThu;
                    """
                )

                radical_row = (
                    cursor.fetchone()
                )

                radical_total = int(
                    radical_row[0] or 0
                )

                radical_symbols = int(
                    radical_row[1] or 0
                )

                radical_numbers = int(
                    radical_row[2] or 0
                )

                radical_min = (
                    radical_row[3]
                )

                radical_max = (
                    radical_row[4]
                )

                print(
                    "BoThu:",
                    radical_total,
                    "/214",
                )

                print(
                    "KyHieu duy nhat:",
                    radical_symbols,
                )

                print(
                    "SoBoThu duy nhat:",
                    radical_numbers,
                )

                print(
                    "Khoang SoBoThu:",
                    radical_min,
                    "->",
                    radical_max,
                )

                if not (
                    radical_total == EXPECTED_RADICALS
                    and radical_symbols == EXPECTED_RADICALS
                    and radical_numbers == EXPECTED_RADICALS
                    and radical_min == 1
                    and radical_max == 214
                ):

                    add_issue(
                        issues,
                        "BO_THU",
                        "",
                        "",
                        "BO_THU_KHONG_DAY_DU_214",
                        (
                            f"Total={radical_total} "
                            f"| KyHieu={radical_symbols} "
                            f"| SoBoThu={radical_numbers} "
                            f"| Min={radical_min} "
                            f"| Max={radical_max}"
                        ),
                    )

                # =================================================
                # 7. STROKES
                # =================================================
                print()
                print(
                    "[7] KIEM TRA NetChuHan"
                )
                print("-" * 120)

                cursor.execute(
                    """
                    SELECT
                        bh.SoThuTuBai,
                        COUNT(n.MaNetChuHan)

                    FROM dbo.BaiHoc AS bh

                    LEFT JOIN dbo.ChuHan AS ch
                        ON bh.MaBaiHoc
                        = ch.MaBaiHoc

                    LEFT JOIN dbo.NetChuHan AS n
                        ON ch.MaChuHan
                        = n.MaChuHan

                    WHERE
                        bh.MaKhoaHoc = ?

                    GROUP BY
                        bh.SoThuTuBai

                    ORDER BY
                        bh.SoThuTuBai;
                    """,
                    ma_khoa_hoc,
                )

                strokes_by_lesson = {}

                stroke_total = 0

                for row in cursor.fetchall():

                    lesson_no = int(
                        row[0]
                    )

                    count = int(
                        row[1] or 0
                    )

                    strokes_by_lesson[
                        lesson_no
                    ] = count

                    stroke_total += count

                    expected = (
                        expected_strokes_by_lesson.get(
                            lesson_no,
                            0,
                        )
                    )

                    if count != expected:

                        add_issue(
                            issues,
                            "NET_CHU_HAN",
                            lesson_no,
                            "",
                            "SO_NET_KHONG_KHOP",
                            (
                                f"SQL={count} "
                                f"| TongSoNetChuHan={expected}"
                            ),
                        )

                print(
                    "Tong NetChuHan:",
                    stroke_total,
                    "/2162",
                )

                print(
                    "Tong ChuHan.SoNet:",
                    expected_stroke_total,
                )

                if (
                    stroke_total
                    != EXPECTED_STROKES
                ):

                    add_issue(
                        issues,
                        "NET_CHU_HAN",
                        "",
                        "",
                        "TONG_KHONG_BANG_2162",
                        str(
                            stroke_total
                        ),
                    )

                if (
                    expected_stroke_total
                    != EXPECTED_STROKES
                ):

                    add_issue(
                        issues,
                        "NET_CHU_HAN",
                        "",
                        "",
                        "TONG_CHUHAN_SONET_KHONG_BANG_2162",
                        str(
                            expected_stroke_total
                        ),
                    )

                # -----------------------------------------
                # Source + JSON + SVG
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        COUNT(*),

                        SUM(
                            CASE
                                WHEN n.MaNguon = ?
                                THEN 1
                                ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN NULLIF(
                                    LTRIM(
                                        RTRIM(
                                            n.DuongNetSVG
                                        )
                                    ),
                                    N''
                                ) IS NULL
                                THEN 1
                                ELSE 0
                            END
                        ),

                        SUM(
                            CASE
                                WHEN ISJSON(
                                    n.DuongTrungTamJson
                                ) = 1
                                THEN 0
                                ELSE 1
                            END
                        )

                    FROM dbo.NetChuHan AS n

                    INNER JOIN dbo.ChuHan AS ch
                        ON n.MaChuHan
                        = ch.MaChuHan

                    INNER JOIN dbo.BaiHoc AS bh
                        ON ch.MaBaiHoc
                        = bh.MaBaiHoc

                    WHERE
                        bh.MaKhoaHoc = ?;
                    """,
                    STROKE_SOURCE,
                    ma_khoa_hoc,
                )

                row = cursor.fetchone()

                net_count = int(
                    row[0] or 0
                )

                net_source3 = int(
                    row[1] or 0
                )

                net_empty_svg = int(
                    row[2] or 0
                )

                net_bad_json = int(
                    row[3] or 0
                )

                print(
                    "MaNguon=3:",
                    net_source3,
                    "/2162",
                )

                print(
                    "SVG trong:",
                    net_empty_svg,
                )

                print(
                    "Median JSON loi:",
                    net_bad_json,
                )

                if (
                    net_source3
                    != EXPECTED_STROKES
                ):

                    add_issue(
                        issues,
                        "NET_CHU_HAN",
                        "",
                        "",
                        "NGUON_3_KHONG_DU_2162",
                        str(net_source3),
                    )

                if (
                    net_empty_svg > 0
                    or net_bad_json > 0
                ):

                    add_issue(
                        issues,
                        "NET_CHU_HAN",
                        "",
                        "",
                        "DU_LIEU_NET_KHONG_HOP_LE",
                        (
                            f"SVGTrong={net_empty_svg} "
                            f"| JsonLoi={net_bad_json}"
                        ),
                    )

                # -----------------------------------------
                # Duplicate stroke key
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        n.MaChuHan,
                        n.ThuTuNet,
                        COUNT(*)

                    FROM dbo.NetChuHan AS n

                    INNER JOIN dbo.ChuHan AS ch
                        ON n.MaChuHan
                        = ch.MaChuHan

                    INNER JOIN dbo.BaiHoc AS bh
                        ON ch.MaBaiHoc
                        = bh.MaBaiHoc

                    WHERE
                        bh.MaKhoaHoc = ?

                    GROUP BY
                        n.MaChuHan,
                        n.ThuTuNet

                    HAVING
                        COUNT(*) > 1;
                    """,
                    ma_khoa_hoc,
                )

                duplicate_stroke = (
                    cursor.fetchall()
                )

                print(
                    "Trung MaChuHan + ThuTuNet:",
                    len(
                        duplicate_stroke
                    ),
                )

                for row in duplicate_stroke:

                    add_issue(
                        issues,
                        "NET_CHU_HAN",
                        "",
                        str(row[0]),
                        "TRUNG_THUTUNET",
                        str(row[1]),
                    )

                # -----------------------------------------
                # Verify every character has 1..SoNet
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        ch.MaChuHan,
                        ch.KyTu,
                        ch.SoNet,
                        COUNT(
                            n.MaNetChuHan
                        ) AS SoDongNet,
                        COUNT(
                            DISTINCT n.ThuTuNet
                        ) AS SoThuTuKhacNhau,
                        MIN(
                            n.ThuTuNet
                        ) AS NetDau,
                        MAX(
                            n.ThuTuNet
                        ) AS NetCuoi

                    FROM dbo.ChuHan AS ch

                    INNER JOIN dbo.BaiHoc AS bh
                        ON ch.MaBaiHoc
                        = bh.MaBaiHoc

                    LEFT JOIN dbo.NetChuHan AS n
                        ON ch.MaChuHan
                        = n.MaChuHan

                    WHERE
                        bh.MaKhoaHoc = ?

                    GROUP BY
                        ch.MaChuHan,
                        ch.KyTu,
                        ch.SoNet

                    HAVING
                        COUNT(
                            n.MaNetChuHan
                        ) <> ch.SoNet

                        OR COUNT(
                            DISTINCT n.ThuTuNet
                        ) <> ch.SoNet

                        OR MIN(
                            n.ThuTuNet
                        ) <> 1

                        OR MAX(
                            n.ThuTuNet
                        ) <> ch.SoNet;
                    """,
                    ma_khoa_hoc,
                )

                stroke_character_issues = (
                    cursor.fetchall()
                )

                print(
                    "Chu thieu/thua/sai ThuTuNet:",
                    len(
                        stroke_character_issues
                    ),
                )

                for row in (
                    stroke_character_issues
                ):

                    add_issue(
                        issues,
                        "NET_CHU_HAN",
                        "",
                        clean(row[1]),
                        "NET_KHONG_LIEN_TUC_HOAC_THIEU",
                        (
                            f"SoNet={row[2]} "
                            f"| SoDong={row[3]} "
                            f"| Distinct={row[4]} "
                            f"| Min={row[5]} "
                            f"| Max={row[6]}"
                        ),
                    )

                # =================================================
                # 8. BUILD LESSON SUMMARY
                # =================================================
                print()
                print(
                    "[8] TAO TONG KET 23 BAI"
                )
                print("-" * 120)

                summary_rows = []

                for lesson_no in range(
                    1,
                    EXPECTED_LESSONS + 1,
                ):

                    lesson = lessons.get(
                        lesson_no,
                        {
                            "MaBaiHoc": "",
                            "TieuDe": "",
                        },
                    )

                    vocab_count = (
                        vocab_by_lesson.get(
                            lesson_no,
                            0,
                        )
                    )

                    grammar_count = (
                        grammar_by_lesson.get(
                            lesson_no,
                            0,
                        )
                    )

                    hanzi_count = (
                        hanzi_by_lesson.get(
                            lesson_no,
                            0,
                        )
                    )

                    stroke_count = (
                        strokes_by_lesson.get(
                            lesson_no,
                            0,
                        )
                    )

                    expected_stroke_count = (
                        expected_strokes_by_lesson.get(
                            lesson_no,
                            0,
                        )
                    )

                    lesson_issues = [
                        issue
                        for issue in issues
                        if str(
                            issue["Bai"]
                        ) == str(
                            lesson_no
                        )
                    ]

                    status = (
                        "OK"
                        if not lesson_issues
                        else "CAN_KIEM_TRA"
                    )

                    summary_rows.append(
                        {
                            "SoThuTuBai": lesson_no,

                            "MaBaiHoc": (
                                lesson[
                                    "MaBaiHoc"
                                ]
                            ),

                            "TieuDe": (
                                lesson[
                                    "TieuDe"
                                ]
                            ),

                            "TuVung": (
                                vocab_count
                            ),

                            "TuVungMongDoi": (
                                EXPECTED_VOCAB_COUNTS[
                                    lesson_no
                                ]
                            ),

                            "NguPhap": (
                                grammar_count
                            ),

                            "ChuHan": (
                                hanzi_count
                            ),

                            "TongSoNetChuHan": (
                                expected_stroke_count
                            ),

                            "NetChuHanTrongSQL": (
                                stroke_count
                            ),

                            "TrangThai": (
                                status
                            ),
                        }
                    )

                    print(
                        f"Bai {lesson_no:>2}: "
                        f"TV={vocab_count:>2} "
                        f"| NP={grammar_count:>2} "
                        f"| Hanzi={hanzi_count:>2} "
                        f"| Net={stroke_count:>3} "
                        f"| {status}"
                    )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 9. WRITE FILES
    # =====================================================
    print()
    print(
        "[9] GHI FILE AUDIT"
    )
    print("-" * 120)

    write_csv(
        OUTPUT_SUMMARY,
        [
            "SoThuTuBai",
            "MaBaiHoc",
            "TieuDe",
            "TuVung",
            "TuVungMongDoi",
            "NguPhap",
            "ChuHan",
            "TongSoNetChuHan",
            "NetChuHanTrongSQL",
            "TrangThai",
        ],
        summary_rows,
    )

    write_csv(
        OUTPUT_ISSUES,
        [
            "Nhom",
            "Bai",
            "DoiTuong",
            "VanDe",
            "ChiTiet",
        ],
        issues,
    )

    write_csv(
        OUTPUT_OPTIONAL,
        [
            "Nhom",
            "Truong",
            "SoLuongTrong",
            "BatBuocDeKhoaNoiDungLoi",
        ],
        optional_gaps,
    )

    print(
        "Lesson audit:"
    )

    print(
        OUTPUT_SUMMARY
    )

    print()
    print(
        "Issues:"
    )

    print(
        OUTPUT_ISSUES
    )

    print()
    print(
        "Optional gaps:"
    )

    print(
        OUTPUT_OPTIONAL
    )

    # =====================================================
    # FINAL
    # =====================================================
    lessons_ok = sum(
        1
        for row in summary_rows
        if row[
            "TrangThai"
        ] == "OK"
    )

    print()
    print("=" * 120)
    print(
        "KET QUA 10U"
    )
    print("=" * 120)

    print(
        "BaiHoc HSK1:",
        len(lessons),
        "/23",
    )

    print(
        "Bai audit OK:",
        lessons_ok,
        "/23",
    )

    print()
    print(
        "TuVung:",
        vocab_total,
        "/501",
    )

    print(
        "TuVung DaDuyet:",
        vocab_approved,
        "/501",
    )

    print()
    print(
        "NguPhap:",
        grammar_total,
        "/88",
    )

    print(
        "NguPhap MaNguon=1004:",
        grammar_source_count,
        "/88",
    )

    print()
    print(
        "ChuHan:",
        hanzi_total,
        "/301",
    )

    print(
        "ChuHan MaNguon=1005:",
        hanzi_source_count,
        "/301",
    )

    print()
    print(
        "BoThu:",
        radical_total,
        "/214",
    )

    print()
    print(
        "NetChuHan:",
        stroke_total,
        "/2162",
    )

    print(
        "NetChuHan MaNguon=3:",
        net_source3,
        "/2162",
    )

    print()
    print(
        "Chu thieu/sai net:",
        len(
            stroke_character_issues
        ),
    )

    print(
        "Duplicate net:",
        len(
            duplicate_stroke
        ),
    )

    print()
    print(
        "TONG CRITICAL ISSUE:",
        len(
            issues
        ),
    )

    print()
    print(
        "LUU Y:"
    )

    print(
        "File optional_content_gaps "
        "chi thong ke cac truong bo sung "
        "nhu vi du, cach ghi nho, media."
    )

    print(
        "Cac truong do KHONG duoc tinh "
        "la critical issue cua bo du lieu loi."
    )

    print()

    if (
        len(issues) == 0
        and lessons_ok
        == EXPECTED_LESSONS
    ):

        print(
            "KET LUAN:"
        )

        print(
            "NOI DUNG LOI HOC BAI HSK1 "
            "DA DAT AUDIT."
        )

        print(
            "CO THE KHOA PHAN:"
        )

        print(
            "TU VUNG + NGU PHAP + "
            "CHU HAN + NET VIET HSK1."
        )

    else:

        print(
            "KET LUAN:"
        )

        print(
            "CHUA KHOA NOI DUNG HSK1."
        )

        print(
            "CAN XU LY CRITICAL ISSUE "
            "TRUOC."
        )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print()
    print("=" * 120)
    print("HOAN TAT")
    print("=" * 120)


# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 120)
        print(
            "10U THAT BAI"
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