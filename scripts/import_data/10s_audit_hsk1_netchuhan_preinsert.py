from pathlib import Path
import csv
import json
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

EXPECTED_HANZI = 301

# 10R da xac nhan truoc/sau deu co 106 dong.
EXPECTED_EXISTING_NET = 106

MAKE_ME_A_HANZI_SOURCE_ID = 3


# =========================================================
# PATHS
# =========================================================
DATA_DIR = (
    ROOT_DIR
    / "data_sources"
)

REVIEW_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
)

OUTPUT_STROKES = (
    REVIEW_DIR
    / "hsk1_301_netchuhan_preinsert_review.csv"
)

OUTPUT_SUMMARY = (
    REVIEW_DIR
    / "hsk1_301_netchuhan_character_summary.csv"
)

OUTPUT_ISSUES = (
    REVIEW_DIR
    / "hsk1_301_netchuhan_10s_issues.csv"
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


def normalize_json_text(value):

    value = clean(value)

    if not value:
        return ""

    try:

        data = json.loads(
            value
        )

        return json.dumps(
            data,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    except Exception:

        # Neu du lieu cu khong parse duoc JSON,
        # giu nguyen de bao mismatch thay vi doan.
        return value


def median_to_json(value):

    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
    )


def quote_sql_identifier(name):

    return (
        "["
        + str(name).replace(
            "]",
            "]]",
        )
        + "]"
    )


# =========================================================
# FIND graphics.txt
# =========================================================
def find_graphics_file():

    if not DATA_DIR.exists():

        fail(
            "Khong ton tai thu muc:\n"
            f"{DATA_DIR}"
        )

    candidates = list(
        DATA_DIR.rglob(
            "graphics.txt"
        )
    )

    if not candidates:

        fail(
            "Khong tim thay graphics.txt "
            "trong data_sources."
        )

    if len(candidates) == 1:

        return candidates[0]

    # Neu co nhieu graphics.txt,
    # uu tien duong dan co Make Me a Hanzi.
    preferred = []

    for path in candidates:

        normalized = (
            str(path)
            .lower()
            .replace("-", "")
            .replace("_", "")
            .replace(" ", "")
        )

        if (
            "makemeahanzi"
            in normalized
        ):

            preferred.append(
                path
            )

    if len(preferred) == 1:

        return preferred[0]

    print()
    print(
        "Tim thay nhieu graphics.txt:"
    )

    for path in candidates:

        print(
            "  ",
            path,
        )

    fail(
        "Khong the tu dong xac dinh "
        "graphics.txt nao la Make Me a Hanzi."
    )


# =========================================================
# READ Make Me a Hanzi
# =========================================================
def read_graphics(
    path,
    target_chars,
):

    result = {}

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1,
        ):

            line = line.strip()

            if not line:
                continue

            try:

                item = json.loads(
                    line
                )

            except Exception as error:

                fail(
                    f"graphics.txt loi JSON "
                    f"dong {line_number}: "
                    f"{error}"
                )

            char = clean(
                item.get(
                    "character"
                )
            )

            if (
                char
                not in target_chars
            ):

                continue

            if char in result:

                fail(
                    f"graphics.txt trung KyTu: "
                    f"{char}"
                )

            strokes = item.get(
                "strokes"
            )

            medians = item.get(
                "medians"
            )

            if not isinstance(
                strokes,
                list,
            ):

                fail(
                    f"{char}: strokes "
                    "khong phai list."
                )

            if not isinstance(
                medians,
                list,
            ):

                fail(
                    f"{char}: medians "
                    "khong phai list."
                )

            if (
                len(strokes)
                != len(medians)
            ):

                fail(
                    f"{char}: strokes="
                    f"{len(strokes)} "
                    f"nhung medians="
                    f"{len(medians)}."
                )

            if len(strokes) <= 0:

                fail(
                    f"{char}: khong co net."
                )

            result[
                char
            ] = {
                "strokes": strokes,
                "medians": medians,
            }

            if (
                len(result)
                == len(
                    target_chars
                )
            ):

                break

    return result


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10S - AUDIT NetChuHan HSK1 "
        "TRUOC KHI INSERT NET VIET"
    )
    print("=" * 120)

    print()
    print("MUC TIEU:")
    print("  KIEM TRA SCHEMA LIVE dbo.NetChuHan")
    print("  TU DONG XAC DINH TEN COT DuongTrung...")
    print("  DOC 301 ChuHan HSK1 TRONG SQL")
    print("  DOC graphics.txt MAKE ME A HANZI")
    print("  DOI CHIEU SoNet")
    print("  DOI CHIEU 106 NetChuHan HIEN CO")
    print("  TAO PLAN KEEP / INSERT / REVIEW")
    print()
    print("CHE DO:")
    print("  CHI SELECT DATABASE")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    # =====================================================
    # 1. CONNECT + SCHEMA
    # =====================================================
    print()
    print(
        "[1] KIEM TRA SCHEMA dbo.NetChuHan"
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
                        "Dang ket noi "
                        "nham database."
                    )

                # -----------------------------------------
                # Schema NetChuHan
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        ORDINAL_POSITION,
                        COLUMN_NAME,
                        DATA_TYPE,
                        CHARACTER_MAXIMUM_LENGTH,
                        IS_NULLABLE

                    FROM INFORMATION_SCHEMA.COLUMNS

                    WHERE
                        TABLE_SCHEMA = 'dbo'
                        AND TABLE_NAME = 'NetChuHan'

                    ORDER BY
                        ORDINAL_POSITION;
                    """
                )

                schema_rows = (
                    cursor.fetchall()
                )

                if not schema_rows:

                    fail(
                        "Khong ton tai "
                        "dbo.NetChuHan."
                    )

                columns = []

                for row in schema_rows:

                    column = {
                        "ordinal": int(
                            row[0]
                        ),
                        "name": clean(
                            row[1]
                        ),
                        "type": clean(
                            row[2]
                        ),
                        "max_length": (
                            row[3]
                        ),
                        "nullable": clean(
                            row[4]
                        ),
                    }

                    columns.append(
                        column
                    )

                    print(
                        f"{column['ordinal']:>2}. "
                        f"{column['name']:<30} "
                        f"{column['type']:<15} "
                        f"NULL={column['nullable']}"
                    )

                column_names = {
                    item["name"]
                    for item in columns
                }

                required_fixed = {
                    "MaNetChuHan",
                    "MaChuHan",
                    "ThuTuNet",
                    "DuongNetSVG",
                    "MaNguon",
                    "NgayTao",
                }

                missing_fixed = (
                    required_fixed
                    - column_names
                )

                if missing_fixed:

                    fail(
                        "NetChuHan thieu cot: "
                        + ", ".join(
                            sorted(
                                missing_fixed
                            )
                        )
                    )

                # -----------------------------------------
                # Tim cot median dua tren schema that.
                # KHONG doan ten cot.
                # -----------------------------------------
                median_candidates = [
                    item["name"]
                    for item in columns
                    if item["name"].lower().startswith(
                        "duongtrung"
                    )
                ]

                if (
                    len(
                        median_candidates
                    )
                    != 1
                ):

                    fail(
                        "Khong xac dinh duoc "
                        "duy nhat cot DuongTrung... "
                        "trong NetChuHan. "
                        f"Tim thay: "
                        f"{median_candidates}"
                    )

                median_column = (
                    median_candidates[0]
                )

                print()
                print(
                    "Cot duong trung tam thuc te:",
                    median_column,
                )

                median_sql = (
                    quote_sql_identifier(
                        median_column
                    )
                )

                # =================================================
                # 2. READ 301 ChuHan
                # =================================================
                print()
                print(
                    "[2] DOC 301 ChuHan HSK1"
                )
                print("-" * 120)

                cursor.execute(
                    """
                    SELECT
                        ch.MaChuHan,
                        ch.KyTu,
                        ch.SoNet,
                        ch.MaBaiHoc,
                        bh.SoThuTuBai,
                        ch.ThuTu

                    FROM dbo.ChuHan AS ch

                    INNER JOIN dbo.BaiHoc AS bh
                        ON ch.MaBaiHoc
                        = bh.MaBaiHoc

                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc

                    WHERE
                        kh.MaKyHieu = ?

                    ORDER BY
                        bh.SoThuTuBai,
                        ch.ThuTu,
                        ch.MaChuHan;
                    """,
                    COURSE_CODE,
                )

                hanzi_rows = (
                    cursor.fetchall()
                )

                if (
                    len(hanzi_rows)
                    != EXPECTED_HANZI
                ):

                    fail(
                        "ChuHan HSK1 khong co "
                        "dung 301 dong. "
                        f"Thuc te: "
                        f"{len(hanzi_rows)}"
                    )

                hanzi_map = {}

                for row in hanzi_rows:

                    char = clean(
                        row[1]
                    )

                    if char in hanzi_map:

                        fail(
                            f"Trung KyTu trong ChuHan: "
                            f"{char}"
                        )

                    hanzi_map[
                        char
                    ] = {
                        "MaChuHan": int(
                            row[0]
                        ),
                        "SoNet": (
                            int(row[2])
                            if row[2]
                            is not None
                            else None
                        ),
                        "MaBaiHoc": int(
                            row[3]
                        ),
                        "SoThuTuBai": int(
                            row[4]
                        ),
                        "ThuTuChuHan": int(
                            row[5]
                        ),
                    }

                print(
                    "ChuHan HSK1:",
                    len(
                        hanzi_map
                    ),
                )

                # =================================================
                # 3. READ EXISTING NetChuHan
                # =================================================
                print()
                print(
                    "[3] DOC NetChuHan HIEN CO"
                )
                print("-" * 120)

                query_existing = f"""
                    SELECT
                        n.MaNetChuHan,
                        n.MaChuHan,
                        n.ThuTuNet,
                        n.DuongNetSVG,
                        n.{median_sql},
                        n.MaNguon,
                        ch.KyTu

                    FROM dbo.NetChuHan AS n

                    INNER JOIN dbo.ChuHan AS ch
                        ON n.MaChuHan
                        = ch.MaChuHan

                    INNER JOIN dbo.BaiHoc AS bh
                        ON ch.MaBaiHoc
                        = bh.MaBaiHoc

                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc

                    WHERE
                        kh.MaKyHieu = ?

                    ORDER BY
                        ch.MaChuHan,
                        n.ThuTuNet,
                        n.MaNetChuHan;
                """

                cursor.execute(
                    query_existing,
                    COURSE_CODE,
                )

                existing_rows = (
                    cursor.fetchall()
                )

                print(
                    "NetChuHan HSK1 hien co:",
                    len(existing_rows),
                )

                if (
                    len(existing_rows)
                    != EXPECTED_EXISTING_NET
                ):

                    fail(
                        "NetChuHan hien co "
                        "khong con bang 106. "
                        f"Thuc te: "
                        f"{len(existing_rows)}"
                    )

                existing_by_key = {}

                duplicate_existing = []

                chars_with_existing = set()

                for row in existing_rows:

                    record = {
                        "MaNetChuHan": int(
                            row[0]
                        ),
                        "MaChuHan": int(
                            row[1]
                        ),
                        "ThuTuNet": int(
                            row[2]
                        ),
                        "DuongNetSVG": clean(
                            row[3]
                        ),
                        "DuongTrungTam": clean(
                            row[4]
                        ),
                        "MaNguon": int(
                            row[5]
                        ),
                        "KyTu": clean(
                            row[6]
                        ),
                    }

                    key = (
                        record[
                            "KyTu"
                        ],
                        record[
                            "ThuTuNet"
                        ],
                    )

                    if key in existing_by_key:

                        duplicate_existing.append(
                            key
                        )

                    else:

                        existing_by_key[
                            key
                        ] = record

                    chars_with_existing.add(
                        record["KyTu"]
                    )

                print(
                    "Chu co NetChuHan hien co:",
                    len(
                        chars_with_existing
                    ),
                )

                print(
                    "Duplicate KyTu + ThuTuNet:",
                    len(
                        duplicate_existing
                    ),
                )

                if duplicate_existing:

                    fail(
                        "NetChuHan hien tai "
                        "co duplicate."
                    )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 4. FIND + READ graphics.txt
    # =====================================================
    print()
    print(
        "[4] DOC Make Me a Hanzi graphics.txt"
    )
    print("-" * 120)

    graphics_file = (
        find_graphics_file()
    )

    print(
        "graphics.txt:"
    )

    print(
        graphics_file
    )

    graphics_map = read_graphics(
        graphics_file,
        set(
            hanzi_map.keys()
        ),
    )

    print(
        "Coverage graphics:",
        len(graphics_map),
        "/301",
    )

    if (
        len(graphics_map)
        != EXPECTED_HANZI
    ):

        missing_graphics = (
            set(hanzi_map)
            - set(graphics_map)
        )

        fail(
            "graphics.txt thieu Chu Han: "
            + " ".join(
                sorted(
                    missing_graphics
                )
            )
        )

    # =====================================================
    # 5. BUILD EXPECTED STROKES
    # =====================================================
    print()
    print(
        "[5] DOI CHIEU SO NET + 106 DONG CU"
    )
    print("-" * 120)

    review_rows = []

    summary_rows = []

    issues = []

    expected_total_strokes = 0

    keep_count = 0
    insert_count = 0
    mismatch_count = 0

    stroke_count_match = 0

    complete_existing_chars = 0
    new_chars = 0
    partial_chars = 0

    for char, hanzi in sorted(
        hanzi_map.items(),
        key=lambda item: (
            item[1][
                "SoThuTuBai"
            ],
            item[1][
                "ThuTuChuHan"
            ],
        ),
    ):

        source = (
            graphics_map[
                char
            ]
        )

        strokes = (
            source[
                "strokes"
            ]
        )

        medians = (
            source[
                "medians"
            ]
        )

        source_count = len(
            strokes
        )

        expected_total_strokes += (
            source_count
        )

        if (
            hanzi["SoNet"]
            ==
            source_count
        ):

            stroke_count_status = "OK"

            stroke_count_match += 1

        else:

            stroke_count_status = (
                "MISMATCH"
            )

            issues.append(
                {
                    "KyTu": char,
                    "ThuTuNet": "",
                    "LoaiLoi": (
                        "SONET_CHUHAN_KHONG_KHOP_GRAPHICS"
                    ),
                    "ChiTiet": (
                        f"ChuHan.SoNet="
                        f"{hanzi['SoNet']} "
                        f"| graphics="
                        f"{source_count}"
                    ),
                }
            )

        char_keep = 0
        char_insert = 0
        char_mismatch = 0

        for index, (
            svg_path,
            median,
        ) in enumerate(
            zip(
                strokes,
                medians,
            ),
            start=1,
        ):

            source_svg = clean(
                svg_path
            )

            source_median = (
                median_to_json(
                    median
                )
            )

            key = (
                char,
                index,
            )

            existing = (
                existing_by_key.get(
                    key
                )
            )

            existing_id = ""
            existing_svg = ""
            existing_median = ""
            existing_source = ""

            if existing is None:

                action = "INSERT"

                char_insert += 1
                insert_count += 1

            else:

                existing_id = (
                    existing[
                        "MaNetChuHan"
                    ]
                )

                existing_svg = (
                    existing[
                        "DuongNetSVG"
                    ]
                )

                existing_median = (
                    existing[
                        "DuongTrungTam"
                    ]
                )

                existing_source = (
                    existing[
                        "MaNguon"
                    ]
                )

                svg_match = (
                    clean(
                        existing_svg
                    )
                    ==
                    source_svg
                )

                median_match = (
                    normalize_json_text(
                        existing_median
                    )
                    ==
                    source_median
                )

                source_match = (
                    existing_source
                    ==
                    MAKE_ME_A_HANZI_SOURCE_ID
                )

                if (
                    svg_match
                    and median_match
                    and source_match
                ):

                    action = "KEEP"

                    char_keep += 1
                    keep_count += 1

                else:

                    action = (
                        "REVIEW_MISMATCH"
                    )

                    char_mismatch += 1
                    mismatch_count += 1

                    differences = []

                    if not svg_match:

                        differences.append(
                            "DuongNetSVG"
                        )

                    if not median_match:

                        differences.append(
                            median_column
                        )

                    if not source_match:

                        differences.append(
                            "MaNguon"
                        )

                    issues.append(
                        {
                            "KyTu": char,
                            "ThuTuNet": index,
                            "LoaiLoi": (
                                "NET_HIEN_CO_KHONG_KHOP_NGUON"
                            ),
                            "ChiTiet": (
                                " | ".join(
                                    differences
                                )
                            ),
                        }
                    )

            review_rows.append(
                {
                    "KyTu": char,

                    "MaChuHan": (
                        hanzi[
                            "MaChuHan"
                        ]
                    ),

                    "SoThuTuBai": (
                        hanzi[
                            "SoThuTuBai"
                        ]
                    ),

                    "ThuTuChuHan": (
                        hanzi[
                            "ThuTuChuHan"
                        ]
                    ),

                    "SoNetChuHan": (
                        hanzi[
                            "SoNet"
                        ]
                    ),

                    "SoNetGraphics": (
                        source_count
                    ),

                    "KiemTraSoNet": (
                        stroke_count_status
                    ),

                    "ThuTuNet": index,

                    "DuongNetSVGNguon": (
                        source_svg
                    ),

                    "DuongTrungTamNguon": (
                        source_median
                    ),

                    "MaNguonDeXuat": (
                        MAKE_ME_A_HANZI_SOURCE_ID
                    ),

                    "MaNetChuHanHienTai": (
                        existing_id
                    ),

                    "MaNguonHienTai": (
                        existing_source
                    ),

                    "HanhDongDeXuat": (
                        action
                    ),
                }
            )

        # -----------------------------------------
        # Check existing extra strokes
        # -----------------------------------------
        char_existing_rows = [
            item
            for key, item
            in existing_by_key.items()
            if key[0] == char
        ]

        extra_existing = [
            item
            for item in char_existing_rows
            if item[
                "ThuTuNet"
            ] > source_count
        ]

        for item in extra_existing:

            issues.append(
                {
                    "KyTu": char,
                    "ThuTuNet": (
                        item[
                            "ThuTuNet"
                        ]
                    ),
                    "LoaiLoi": (
                        "NET_SQL_THUA_SO_VOI_GRAPHICS"
                    ),
                    "ChiTiet": (
                        f"MaNetChuHan="
                        f"{item['MaNetChuHan']}"
                    ),
                }
            )

        # -----------------------------------------
        # Character status
        # -----------------------------------------
        if (
            char_keep == source_count
            and char_insert == 0
            and char_mismatch == 0
        ):

            char_status = (
                "DA_CO_DAY_DU_KHOP_NGUON"
            )

            complete_existing_chars += 1

        elif (
            char_keep == 0
            and char_insert == source_count
            and char_mismatch == 0
        ):

            char_status = (
                "CHUA_CO_NET_CAN_INSERT"
            )

            new_chars += 1

        else:

            char_status = (
                "CAN_REVIEW"
            )

            partial_chars += 1

        summary_rows.append(
            {
                "KyTu": char,

                "MaChuHan": (
                    hanzi[
                        "MaChuHan"
                    ]
                ),

                "SoThuTuBai": (
                    hanzi[
                        "SoThuTuBai"
                    ]
                ),

                "ThuTuChuHan": (
                    hanzi[
                        "ThuTuChuHan"
                    ]
                ),

                "SoNetChuHan": (
                    hanzi[
                        "SoNet"
                    ]
                ),

                "SoNetGraphics": (
                    source_count
                ),

                "SoNetKEEP": (
                    char_keep
                ),

                "SoNetINSERT": (
                    char_insert
                ),

                "SoNetMismatch": (
                    char_mismatch
                ),

                "TrangThaiNet": (
                    char_status
                ),
            }
        )

    # =====================================================
    # 6. VERIFY ALL EXISTING ROWS ACCOUNTED FOR
    # =====================================================
    expected_keys = {
        (
            row["KyTu"],
            int(
                row["ThuTuNet"]
            ),
        )
        for row in review_rows
    }

    existing_keys = set(
        existing_by_key
    )

    extra_keys = (
        existing_keys
        - expected_keys
    )

    for char, stroke_order in sorted(
        extra_keys
    ):

        item = (
            existing_by_key[
                (
                    char,
                    stroke_order,
                )
            ]
        )

        issues.append(
            {
                "KyTu": char,
                "ThuTuNet": (
                    stroke_order
                ),
                "LoaiLoi": (
                    "NET_SQL_KHONG_CO_TRONG_KE_HOACH_NGUON"
                ),
                "ChiTiet": (
                    f"MaNetChuHan="
                    f"{item['MaNetChuHan']}"
                ),
            }
        )

    # =====================================================
    # 7. WRITE REVIEW
    # =====================================================
    print()
    print(
        "[6] GHI FILE REVIEW"
    )
    print("-" * 120)

    write_csv(
        OUTPUT_STROKES,
        [
            "KyTu",
            "MaChuHan",
            "SoThuTuBai",
            "ThuTuChuHan",
            "SoNetChuHan",
            "SoNetGraphics",
            "KiemTraSoNet",
            "ThuTuNet",
            "DuongNetSVGNguon",
            "DuongTrungTamNguon",
            "MaNguonDeXuat",
            "MaNetChuHanHienTai",
            "MaNguonHienTai",
            "HanhDongDeXuat",
        ],
        review_rows,
    )

    write_csv(
        OUTPUT_SUMMARY,
        [
            "KyTu",
            "MaChuHan",
            "SoThuTuBai",
            "ThuTuChuHan",
            "SoNetChuHan",
            "SoNetGraphics",
            "SoNetKEEP",
            "SoNetINSERT",
            "SoNetMismatch",
            "TrangThaiNet",
        ],
        summary_rows,
    )

    write_csv(
        OUTPUT_ISSUES,
        [
            "KyTu",
            "ThuTuNet",
            "LoaiLoi",
            "ChiTiet",
        ],
        issues,
    )

    print(
        "Stroke review:"
    )

    print(
        OUTPUT_STROKES
    )

    print()
    print(
        "Character summary:"
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

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 10S"
    )
    print("=" * 120)

    print(
        "ChuHan HSK1:",
        len(
            hanzi_map
        ),
    )

    print(
        "Graphics coverage:",
        len(
            graphics_map
        ),
        "/301",
    )

    print(
        "ChuHan.SoNet khop graphics:",
        stroke_count_match,
        "/301",
    )

    print()
    print(
        "Tong net mong doi:",
        expected_total_strokes,
    )

    print(
        "NetChuHan hien co:",
        len(
            existing_rows
        ),
    )

    print(
        "KEEP:",
        keep_count,
    )

    print(
        "CAN INSERT:",
        insert_count,
    )

    print(
        "MISMATCH:",
        mismatch_count,
    )

    print()
    print(
        "Chu da co net day du:",
        complete_existing_chars,
    )

    print(
        "Chu chua co net:",
        new_chars,
    )

    print(
        "Chu can review:",
        partial_chars,
    )

    print()
    print(
        "Tong issue:",
        len(
            issues
        ),
    )

    print()
    print(
        "Cot DuongTrung... thuc te:",
        median_column,
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA INSERT NetChuHan."
    )

    print(
        "CHUA UPDATE NetChuHan."
    )

    print(
        "CHUA DELETE NetChuHan."
    )

    print()
    print(
        "NEU MISMATCH=0 VA ISSUE=0:"
    )

    print(
        "10T SE GIU NGUYEN CAC NET CU "
        "DA KHOP VA CHI INSERT CAC NET CON THIEU."
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
            "10S THAT BAI"
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