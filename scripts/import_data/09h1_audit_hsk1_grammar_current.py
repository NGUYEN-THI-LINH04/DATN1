from pathlib import Path
import sys
from collections import Counter, defaultdict
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

EXPECTED_LESSON_COUNT = 23

# Trang thai hop le theo constraint hien tai
VALID_STATUSES = {
    "ban_nhap",
    "da_xuat_ban",
    "luu_tru",
}

# Schema NguPhap theo database hien tai
EXPECTED_COLUMNS = [
    "MaNguPhap",
    "MaBaiHoc",
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


# =========================================================
# HELPERS
# =========================================================
def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def fail(message):

    raise RuntimeError(message)


def print_line():

    print("-" * 115)


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 115)
    print(
        "09H1 - AUDIT DU LIEU NGU PHAP HSK1 HIEN TAI"
    )
    print("=" * 115)

    print()
    print("CHE DO:")
    print("  CHI SELECT DATABASE")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    # =====================================================
    # 1. KET NOI DATABASE
    # =====================================================
    print()
    print("[1] KET NOI DATABASE")
    print_line()

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

                if clean(
                    database_name
                ).lower() != "hoctiengtrungdb":

                    fail(
                        "Dang ket noi nham database. "
                        f"Thuc te: {database_name}"
                    )

                print(
                    "KET NOI DATABASE: OK"
                )

                # =================================================
                # 2. KIEM TRA SCHEMA NGUPHAP
                # =================================================
                print()
                print(
                    "[2] KIEM TRA SCHEMA dbo.NguPhap"
                )
                print_line()

                cursor.execute(
                    """
                    SELECT
                        COLUMN_NAME,
                        DATA_TYPE,
                        CHARACTER_MAXIMUM_LENGTH,
                        IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE
                        TABLE_SCHEMA = 'dbo'
                        AND TABLE_NAME = 'NguPhap'
                    ORDER BY ORDINAL_POSITION;
                    """
                )

                schema_rows = cursor.fetchall()

                if not schema_rows:

                    fail(
                        "Khong tim thay bang dbo.NguPhap."
                    )

                actual_columns = [
                    clean(row[0])
                    for row in schema_rows
                ]

                print(
                    "Tong cot:",
                    len(actual_columns),
                )

                print()

                for index, row in enumerate(
                    schema_rows,
                    start=1,
                ):

                    column_name = clean(
                        row[0]
                    )

                    data_type = clean(
                        row[1]
                    )

                    max_length = row[2]

                    nullable = clean(
                        row[3]
                    )

                    if max_length is None:

                        type_text = data_type

                    elif int(max_length) == -1:

                        type_text = (
                            f"{data_type}(max)"
                        )

                    else:

                        type_text = (
                            f"{data_type}"
                            f"({max_length})"
                        )

                    print(
                        f"{index:>2}. "
                        f"{column_name:<20} "
                        f"{type_text:<20} "
                        f"NULL={nullable}"
                    )

                missing_columns = [
                    column
                    for column in EXPECTED_COLUMNS
                    if column not in actual_columns
                ]

                extra_columns = [
                    column
                    for column in actual_columns
                    if column not in EXPECTED_COLUMNS
                ]

                print()
                print(
                    "Cot thieu:",
                    len(missing_columns),
                )

                print(
                    "Cot ngoai schema mong doi:",
                    len(extra_columns),
                )

                if missing_columns:

                    print(
                        "Danh sach cot thieu:",
                        missing_columns,
                    )

                    fail(
                        "Schema dbo.NguPhap "
                        "khong dung nhu mong doi."
                    )

                if extra_columns:

                    print(
                        "Cot bo sung trong DB:",
                        extra_columns,
                    )

                print(
                    "SCHEMA NGUPHAP: OK"
                )

                # =================================================
                # 3. CONSTRAINTS
                # =================================================
                print()
                print(
                    "[3] KIEM TRA CONSTRAINT "
                    "VA FOREIGN KEY"
                )
                print_line()

                cursor.execute(
                    """
                    SELECT
                        cc.name,
                        cc.definition
                    FROM sys.check_constraints AS cc
                    INNER JOIN sys.tables AS t
                        ON cc.parent_object_id = t.object_id
                    INNER JOIN sys.schemas AS s
                        ON t.schema_id = s.schema_id
                    WHERE
                        s.name = 'dbo'
                        AND t.name = 'NguPhap'
                    ORDER BY cc.name;
                    """
                )

                check_constraints = (
                    cursor.fetchall()
                )

                print(
                    "CHECK constraints:",
                    len(check_constraints),
                )

                for row in check_constraints:

                    print(
                        " ",
                        clean(row[0]),
                        "=>",
                        clean(row[1]),
                    )

                cursor.execute(
                    """
                    SELECT
                        fk.name,
                        COL_NAME(
                            fkc.parent_object_id,
                            fkc.parent_column_id
                        ) AS CotNguon,
                        OBJECT_NAME(
                            fkc.referenced_object_id
                        ) AS BangDich,
                        COL_NAME(
                            fkc.referenced_object_id,
                            fkc.referenced_column_id
                        ) AS CotDich
                    FROM sys.foreign_keys AS fk
                    INNER JOIN
                        sys.foreign_key_columns AS fkc
                        ON fk.object_id
                        = fkc.constraint_object_id
                    WHERE
                        fk.parent_object_id
                        = OBJECT_ID('dbo.NguPhap')
                    ORDER BY fk.name;
                    """
                )

                foreign_keys = (
                    cursor.fetchall()
                )

                print()
                print(
                    "Foreign keys:",
                    len(foreign_keys),
                )

                for row in foreign_keys:

                    print(
                        " ",
                        clean(row[0]),
                        ":",
                        clean(row[1]),
                        "->",
                        clean(row[2]),
                        ".",
                        clean(row[3]),
                        sep="",
                    )

                # =================================================
                # 4. TIM KHOA HSK1
                # =================================================
                print()
                print(
                    "[4] TIM KHOA HOC HSK1"
                )
                print_line()

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
                        "Phai tim thay dung 1 khoa "
                        f"{COURSE_CODE}. "
                        f"Thuc te: {len(course_rows)}"
                    )

                (
                    course_id,
                    course_code,
                    course_title,
                ) = course_rows[0]

                course_id = int(
                    course_id
                )

                print(
                    "MaKhoaHoc:",
                    course_id,
                )

                print(
                    "MaKyHieu:",
                    clean(course_code),
                )

                print(
                    "TieuDe:",
                    clean(course_title),
                )

                print(
                    "KHOA HSK1: OK"
                )

                # =================================================
                # 5. KIEM TRA 23 BAI HOC
                # =================================================
                print()
                print(
                    "[5] KIEM TRA 23 BAI HOC HSK1"
                )
                print_line()

                cursor.execute(
                    """
                    SELECT
                        MaBaiHoc,
                        SoThuTuBai,
                        TieuDe,
                        TrangThai
                    FROM dbo.BaiHoc
                    WHERE MaKhoaHoc = ?
                    ORDER BY SoThuTuBai;
                    """,
                    course_id,
                )

                lesson_rows = (
                    cursor.fetchall()
                )

                print(
                    "Tong bai HSK1:",
                    len(lesson_rows),
                )

                if (
                    len(lesson_rows)
                    != EXPECTED_LESSON_COUNT
                ):

                    fail(
                        "HSK1 phai co dung "
                        f"{EXPECTED_LESSON_COUNT} bai. "
                        f"Thuc te: {len(lesson_rows)}"
                    )

                lessons_by_id = {}

                expected_order = 1

                for row in lesson_rows:

                    lesson_id = int(
                        row[0]
                    )

                    lesson_no = int(
                        row[1]
                    )

                    title = clean(
                        row[2]
                    )

                    status = clean(
                        row[3]
                    )

                    if lesson_no != expected_order:

                        fail(
                            "SoThuTuBai HSK1 "
                            "khong lien tuc.\n"
                            f"Mong doi: {expected_order}\n"
                            f"Thuc te: {lesson_no}"
                        )

                    lessons_by_id[
                        lesson_id
                    ] = {
                        "lesson_no": lesson_no,
                        "title": title,
                        "status": status,
                    }

                    print(
                        f"Bai {lesson_no:>2} | "
                        f"MaBaiHoc={lesson_id:<3} | "
                        f"{title}"
                    )

                    expected_order += 1

                print()
                print(
                    "23/23 BAI HSK1: OK"
                )

                # =================================================
                # 6. THONG KE TOAN BANG NGUPHAP
                # =================================================
                print()
                print(
                    "[6] THONG KE TOAN BO dbo.NguPhap"
                )
                print_line()

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.NguPhap;
                    """
                )

                total_grammar_db = int(
                    cursor.fetchone()[0]
                )

                print(
                    "Tong dong dbo.NguPhap:",
                    total_grammar_db,
                )

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.NguPhap AS np
                    INNER JOIN dbo.BaiHoc AS bh
                        ON np.MaBaiHoc = bh.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?;
                    """,
                    course_id,
                )

                total_hsk1_grammar = int(
                    cursor.fetchone()[0]
                )

                print(
                    "Ngu phap thuoc HSK1:",
                    total_hsk1_grammar,
                )

                print(
                    "Ngu phap ngoai HSK1:",
                    (
                        total_grammar_db
                        - total_hsk1_grammar
                    ),
                )

                # =================================================
                # 7. DOC NGU PHAP HSK1
                # =================================================
                print()
                print(
                    "[7] DOC CHI TIET NGU PHAP HSK1"
                )
                print_line()

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
                    WHERE bh.MaKhoaHoc = ?
                    ORDER BY
                        bh.SoThuTuBai,
                        np.ThuTu,
                        np.MaNguPhap;
                    """,
                    course_id,
                )

                grammar_rows = (
                    cursor.fetchall()
                )

                # Cau truc du lieu de audit
                grammar_by_lesson = (
                    defaultdict(list)
                )

                for row in grammar_rows:

                    item = {
                        "MaNguPhap": int(row[0]),
                        "MaBaiHoc": int(row[1]),
                        "SoThuTuBai": int(row[2]),
                        "TieuDeBai": clean(row[3]),
                        "TenCauTruc": clean(row[4]),
                        "MoTa": clean(row[5]),
                        "CachDung": clean(row[6]),
                        "ViDuTiengTrung": clean(row[7]),
                        "ViDuPinyin": clean(row[8]),
                        "ViDuTiengViet": clean(row[9]),
                        "MaTep": (
                            None
                            if row[10] is None
                            else int(row[10])
                        ),
                        "MaNguon": (
                            None
                            if row[11] is None
                            else int(row[11])
                        ),
                        "ThuTu": int(row[12]),
                        "TrangThai": clean(row[13]),
                        "NgayTao": row[14],
                    }

                    grammar_by_lesson[
                        item["SoThuTuBai"]
                    ].append(item)

                print(
                    "Tong ngu phap HSK1:",
                    len(grammar_rows),
                )

                print()

                for lesson_no in range(
                    1,
                    EXPECTED_LESSON_COUNT + 1,
                ):

                    lesson_id = None
                    lesson_title = ""

                    for (
                        current_lesson_id,
                        lesson_info,
                    ) in lessons_by_id.items():

                        if (
                            lesson_info[
                                "lesson_no"
                            ]
                            == lesson_no
                        ):

                            lesson_id = (
                                current_lesson_id
                            )

                            lesson_title = (
                                lesson_info[
                                    "title"
                                ]
                            )

                            break

                    grammar_count = len(
                        grammar_by_lesson[
                            lesson_no
                        ]
                    )

                    print(
                        f"Bai {lesson_no:>2}: "
                        f"{grammar_count:>2} muc "
                        f"| MaBaiHoc={lesson_id} "
                        f"| {lesson_title}"
                    )

                # =================================================
                # 8. IN CHI TIET CAC MUC HIEN CO
                # =================================================
                print()
                print(
                    "[8] CHI TIET NGU PHAP "
                    "HIEN DANG CO"
                )
                print_line()

                if not grammar_rows:

                    print(
                        "HIEN TAI HSK1 "
                        "CHUA CO DU LIEU NGU PHAP."
                    )

                else:

                    for lesson_no in range(
                        1,
                        EXPECTED_LESSON_COUNT + 1,
                    ):

                        items = (
                            grammar_by_lesson[
                                lesson_no
                            ]
                        )

                        if not items:
                            continue

                        print()
                        print(
                            "=" * 115
                        )

                        print(
                            f"BAI {lesson_no} - "
                            f"{items[0]['TieuDeBai']}"
                        )

                        print(
                            "=" * 115
                        )

                        for item in items:

                            print()
                            print(
                                f"[{item['ThuTu']}] "
                                f"MaNguPhap="
                                f"{item['MaNguPhap']} "
                                f"| "
                                f"{item['TenCauTruc']}"
                            )

                            print(
                                "  MoTa:",
                                (
                                    item["MoTa"]
                                    if item["MoTa"]
                                    else "<TRONG>"
                                ),
                            )

                            print(
                                "  CachDung:",
                                (
                                    item["CachDung"]
                                    if item["CachDung"]
                                    else "<TRONG>"
                                ),
                            )

                            print(
                                "  ViDuTiengTrung:",
                                (
                                    item[
                                        "ViDuTiengTrung"
                                    ]
                                    if item[
                                        "ViDuTiengTrung"
                                    ]
                                    else "<TRONG>"
                                ),
                            )

                            print(
                                "  ViDuPinyin:",
                                (
                                    item[
                                        "ViDuPinyin"
                                    ]
                                    if item[
                                        "ViDuPinyin"
                                    ]
                                    else "<TRONG>"
                                ),
                            )

                            print(
                                "  ViDuTiengViet:",
                                (
                                    item[
                                        "ViDuTiengViet"
                                    ]
                                    if item[
                                        "ViDuTiengViet"
                                    ]
                                    else "<TRONG>"
                                ),
                            )

                            print(
                                "  MaNguon:",
                                item["MaNguon"],
                            )

                            print(
                                "  MaTep:",
                                item["MaTep"],
                            )

                            print(
                                "  TrangThai:",
                                item["TrangThai"],
                            )

                # =================================================
                # 9. AUDIT THU TU
                # =================================================
                print()
                print(
                    "[9] KIEM TRA THU TU NGU PHAP"
                )
                print_line()

                order_errors = []

                duplicate_order_errors = []

                for lesson_no in range(
                    1,
                    EXPECTED_LESSON_COUNT + 1,
                ):

                    items = (
                        grammar_by_lesson[
                            lesson_no
                        ]
                    )

                    if not items:

                        continue

                    orders = [
                        item["ThuTu"]
                        for item in items
                    ]

                    if len(
                        orders
                    ) != len(
                        set(orders)
                    ):

                        duplicate_order_errors.append(
                            (
                                lesson_no,
                                orders,
                            )
                        )

                    expected_orders = list(
                        range(
                            1,
                            len(items) + 1,
                        )
                    )

                    if (
                        sorted(orders)
                        != expected_orders
                    ):

                        order_errors.append(
                            (
                                lesson_no,
                                sorted(orders),
                                expected_orders,
                            )
                        )

                print(
                    "Bai co ThuTu bi trung:",
                    len(
                        duplicate_order_errors
                    ),
                )

                print(
                    "Bai co ThuTu khong lien tuc:",
                    len(order_errors),
                )

                for (
                    lesson_no,
                    orders,
                ) in duplicate_order_errors:

                    print(
                        f"  Bai {lesson_no}: "
                        f"{orders}"
                    )

                for (
                    lesson_no,
                    actual,
                    expected,
                ) in order_errors:

                    print(
                        f"  Bai {lesson_no}: "
                        f"thuc te={actual} | "
                        f"mong doi={expected}"
                    )

                # =================================================
                # 10. AUDIT TRUONG NOI DUNG
                # =================================================
                print()
                print(
                    "[10] KIEM TRA NOI DUNG "
                    "NGU PHAP"
                )
                print_line()

                missing_ten = []
                missing_mota = []
                missing_cachdung = []
                missing_cn_example = []
                missing_pinyin_example = []
                missing_vi_example = []
                missing_source = []
                missing_media = []
                invalid_status = []

                for item in [
                    grammar
                    for lesson_items
                    in grammar_by_lesson.values()
                    for grammar in lesson_items
                ]:

                    grammar_id = item[
                        "MaNguPhap"
                    ]

                    if not item[
                        "TenCauTruc"
                    ]:
                        missing_ten.append(
                            grammar_id
                        )

                    if not item[
                        "MoTa"
                    ]:
                        missing_mota.append(
                            grammar_id
                        )

                    if not item[
                        "CachDung"
                    ]:
                        missing_cachdung.append(
                            grammar_id
                        )

                    if not item[
                        "ViDuTiengTrung"
                    ]:
                        missing_cn_example.append(
                            grammar_id
                        )

                    if not item[
                        "ViDuPinyin"
                    ]:
                        missing_pinyin_example.append(
                            grammar_id
                        )

                    if not item[
                        "ViDuTiengViet"
                    ]:
                        missing_vi_example.append(
                            grammar_id
                        )

                    if item[
                        "MaNguon"
                    ] is None:
                        missing_source.append(
                            grammar_id
                        )

                    if item[
                        "MaTep"
                    ] is None:
                        missing_media.append(
                            grammar_id
                        )

                    if (
                        item["TrangThai"]
                        not in VALID_STATUSES
                    ):

                        invalid_status.append(
                            grammar_id
                        )

                print(
                    "Thieu TenCauTruc:",
                    len(missing_ten),
                )

                print(
                    "Thieu MoTa:",
                    len(missing_mota),
                )

                print(
                    "Thieu CachDung:",
                    len(missing_cachdung),
                )

                print(
                    "Thieu ViDuTiengTrung:",
                    len(
                        missing_cn_example
                    ),
                )

                print(
                    "Thieu ViDuPinyin:",
                    len(
                        missing_pinyin_example
                    ),
                )

                print(
                    "Thieu ViDuTiengViet:",
                    len(
                        missing_vi_example
                    ),
                )

                print(
                    "Khong co MaNguon:",
                    len(missing_source),
                )

                print(
                    "Khong co MaTep:",
                    len(missing_media),
                )

                print(
                    "TrangThai khong hop le:",
                    len(invalid_status),
                )

                # MaTep co the NULL, day khong
                # duoc coi la loi bat buoc.
                print()
                print(
                    "Luu y: MaTep NULL "
                    "khong duoc coi la loi, "
                    "vi audio ngu phap co the "
                    "bo sung sau."
                )

                # =================================================
                # 11. DUPLICATE STRUCTURES
                # =================================================
                print()
                print(
                    "[11] KIEM TRA CAU TRUC TRUNG"
                )
                print_line()

                structure_counter = Counter(
                    (
                        item["SoThuTuBai"],
                        item["TenCauTruc"]
                        .casefold(),
                    )
                    for items
                    in grammar_by_lesson.values()
                    for item in items
                    if item["TenCauTruc"]
                )

                duplicate_structures = [
                    key
                    for key, count
                    in structure_counter.items()
                    if count > 1
                ]

                print(
                    "Cau truc trung "
                    "trong cung bai:",
                    len(
                        duplicate_structures
                    ),
                )

                for (
                    lesson_no,
                    structure_name,
                ) in duplicate_structures:

                    print(
                        f"  Bai {lesson_no}: "
                        f"{structure_name}"
                    )

                # =================================================
                # 12. TRANG THAI
                # =================================================
                print()
                print(
                    "[12] THONG KE TRANG THAI"
                )
                print_line()

                status_counter = Counter(
                    item["TrangThai"]
                    for items
                    in grammar_by_lesson.values()
                    for item in items
                )

                if not status_counter:

                    print(
                        "Khong co du lieu."
                    )

                else:

                    for (
                        status,
                        count,
                    ) in sorted(
                        status_counter.items()
                    ):

                        print(
                            f"{status}: {count}"
                        )

                # =================================================
                # 13. NGUON
                # =================================================
                print()
                print(
                    "[13] THONG KE MaNguon"
                )
                print_line()

                source_counter = Counter(
                    item["MaNguon"]
                    for items
                    in grammar_by_lesson.values()
                    for item in items
                )

                if not source_counter:

                    print(
                        "Khong co du lieu."
                    )

                else:

                    for (
                        source_id,
                        count,
                    ) in sorted(
                        source_counter.items(),
                        key=lambda x: (
                            x[0] is None,
                            x[0]
                            if x[0] is not None
                            else 0,
                        ),
                    ):

                        print(
                            f"MaNguon="
                            f"{source_id}: "
                            f"{count}"
                        )

                # =================================================
                # 14. RIENG BAI 1
                # =================================================
                print()
                print(
                    "[14] KIEM TRA RIENG BAI 1"
                )
                print_line()

                lesson1_items = (
                    grammar_by_lesson[1]
                )

                print(
                    "So muc ngu phap Bai 1:",
                    len(lesson1_items),
                )

                if lesson1_items:

                    for item in lesson1_items:

                        print(
                            f"  [{item['ThuTu']}] "
                            f"MaNguPhap="
                            f"{item['MaNguPhap']} "
                            f"| "
                            f"{item['TenCauTruc']}"
                        )

                else:

                    print(
                        "  Bai 1 hien chua "
                        "co ngu phap."
                    )

                # =================================================
                # 15. KET QUA
                # =================================================
                print()
                print("=" * 115)
                print(
                    "KET QUA AUDIT NGU PHAP HSK1"
                )
                print("=" * 115)

                print(
                    "Khoa:",
                    clean(course_code),
                )

                print(
                    "Tong bai HSK1:",
                    len(lesson_rows),
                )

                print(
                    "Tong ngu phap toan DB:",
                    total_grammar_db,
                )

                print(
                    "Tong ngu phap HSK1:",
                    total_hsk1_grammar,
                )

                print(
                    "Ngu phap Bai 1:",
                    len(lesson1_items),
                )

                lessons_with_grammar = sum(
                    1
                    for lesson_no
                    in range(
                        1,
                        EXPECTED_LESSON_COUNT + 1,
                    )
                    if grammar_by_lesson[
                        lesson_no
                    ]
                )

                lessons_without_grammar = (
                    EXPECTED_LESSON_COUNT
                    - lessons_with_grammar
                )

                print(
                    "Bai co ngu phap:",
                    lessons_with_grammar,
                )

                print(
                    "Bai chua co ngu phap:",
                    lessons_without_grammar,
                )

                print(
                    "ThuTu trung:",
                    len(
                        duplicate_order_errors
                    ),
                )

                print(
                    "ThuTu khong lien tuc:",
                    len(order_errors),
                )

                print(
                    "Cau truc trung cung bai:",
                    len(
                        duplicate_structures
                    ),
                )

                print(
                    "Thieu MoTa:",
                    len(missing_mota),
                )

                print(
                    "Thieu CachDung:",
                    len(
                        missing_cachdung
                    ),
                )

                print(
                    "Thieu vi du Trung:",
                    len(
                        missing_cn_example
                    ),
                )

                print(
                    "Thieu vi du Pinyin:",
                    len(
                        missing_pinyin_example
                    ),
                )

                print(
                    "Thieu vi du Viet:",
                    len(
                        missing_vi_example
                    ),
                )

                print(
                    "Thieu MaNguon:",
                    len(
                        missing_source
                    ),
                )

                print()
                print(
                    "AUDIT HOAN TAT."
                )

                print(
                    "DATABASE KHONG BI SUA."
                )

                print()
                print(
                    "DU LIEU TREN SE DUOC "
                    "DUNG DE QUYET DINH "
                    "CAC BUOC XAY DUNG "
                    "NGU PHAP HSK1 TIEP THEO."
                )

                print()
                print("=" * 115)
                print("HOAN TAT")
                print("=" * 115)

        finally:

            # Chi SELECT.
            # Rollback de dong transaction doc,
            # khong commit bat ky thay doi nao.
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
            "AUDIT NGU PHAP THAT BAI"
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