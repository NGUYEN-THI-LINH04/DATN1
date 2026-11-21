# -*- coding: utf-8 -*-
"""
BUOC 16 - AUDIT NGUON + SCHEMA CHU HAN HSK4

Muc dich:
1. Khoa file ngu phap HSK4 final.
2. Kiem tra cac nguon Hanzi hien co trong project:
   - Unicode / Unihan
   - CJKRadicals
   - Make Me a Hanzi
   - cac file hanzi/radical lien quan
3. Doc schema SQL THUC TE:
   - dbo.ChuHan
   - dbo.BoThu
   - dbo.NguonDuLieu
4. Thong ke du lieu ChuHan / BoThu hien co.
5. Kiem tra trang thai HSK4 hien tai.

CHI DOC FILE + CHI DOC SQL.
KHONG INSERT.
KHONG UPDATE.
KHONG DELETE.
"""

import hashlib
import json
import sys

from pathlib import Path
from contextlib import closing


# ==========================================================
# 1. ROOT / DATABASE
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT),
)

from database import get_connection


PROCESSED_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

GRAMMAR_FINAL = (
    PROCESSED_DIR
    / "grammar_hsk4_teaching_final_114.csv"
)

REPORT_FILE = (
    PROCESSED_DIR
    / "hsk4_hanzi_source_audit.json"
)


EXPECTED_GRAMMAR_SHA256 = (
    "9b3097dcc6e7a149e3d07fb07223226b"
    "5d15192aec6eb5a9ada77bfe8cd87e65"
)


# ==========================================================
# 2. HAM HO TRO
# ==========================================================

def clean(value):
    return (
        str(value).strip()
        if value is not None
        else ""
    )


def sha256_file(path):

    digest = hashlib.sha256()

    with path.open("rb") as file:

        while True:

            block = file.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


def fetch_all(
    cursor,
    sql,
    *params,
):

    cursor.execute(
        sql,
        *params,
    )

    columns = [
        item[0]
        for item in cursor.description
    ]

    return [
        dict(
            zip(
                columns,
                row,
            )
        )
        for row in cursor.fetchall()
    ]


def fetch_one(
    cursor,
    sql,
    *params,
):

    rows = fetch_all(
        cursor,
        sql,
        *params,
    )

    return (
        rows[0]
        if rows
        else None
    )


def table_exists(
    cursor,
    table_name,
):

    row = fetch_one(
        cursor,
        """
        SELECT COUNT(*) AS Tong
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = ?
        """,
        table_name,
    )

    return (
        row
        and row["Tong"] == 1
    )


def get_schema(
    cursor,
    table_name,
):

    return fetch_all(
        cursor,
        """
        SELECT
            c.ORDINAL_POSITION AS ThuTu,
            c.COLUMN_NAME AS TenCot,
            c.DATA_TYPE AS KieuDuLieu,
            c.CHARACTER_MAXIMUM_LENGTH AS DoDai,
            c.IS_NULLABLE AS ChoPhepNull,

            CASE
                WHEN COLUMNPROPERTY(
                    OBJECT_ID('dbo.' + c.TABLE_NAME),
                    c.COLUMN_NAME,
                    'IsIdentity'
                ) = 1
                THEN 1
                ELSE 0
            END AS LaIdentity

        FROM INFORMATION_SCHEMA.COLUMNS AS c

        WHERE c.TABLE_SCHEMA = 'dbo'
          AND c.TABLE_NAME = ?

        ORDER BY c.ORDINAL_POSITION
        """,
        table_name,
    )


def count_table(
    cursor,
    table_name,
):

    # table_name chi lay tu danh sach noi bo co dinh,
    # khong lay tu input nguoi dung.
    sql = (
        f"SELECT COUNT(*) AS Tong "
        f"FROM dbo.[{table_name}]"
    )

    row = fetch_one(
        cursor,
        sql,
    )

    return (
        row["Tong"]
        if row
        else None
    )


# ==========================================================
# 3. QUET SOURCE FILE
# ==========================================================

def scan_source_files():

    print(
        "\n[2] QUET NGUON CHU HAN TRONG PROJECT"
    )

    search_roots = [
        ROOT / "data_sources",
        ROOT / "data",
        ROOT / "scripts" / "hsk1",
        ROOT / "scripts" / "hsk2",
        ROOT / "scripts" / "hsk3",
    ]

    keywords = [
        "unihan",
        "cjkradical",
        "radical",
        "makemeahanzi",
        "make_me_a_hanzi",
        "hanzi",
        "chu_han",
        "chuhan",
        "dictionary.txt",
        "graphics.txt",
    ]

    ignored_parts = {
        ".git",
        "__pycache__",
        "venv",
        ".venv",
        "node_modules",
    }

    found = []

    seen = set()

    for search_root in search_roots:

        if not search_root.exists():
            continue

        for path in search_root.rglob("*"):

            if not path.is_file():
                continue

            if any(
                part.lower()
                in ignored_parts
                for part in path.parts
            ):
                continue

            lower_name = (
                path.name.lower()
            )

            relative_text = (
                str(
                    path.relative_to(ROOT)
                )
                .lower()
                .replace("\\", "/")
            )

            if not any(
                keyword
                in lower_name
                or keyword
                in relative_text
                for keyword in keywords
            ):
                continue

            key = str(
                path.resolve()
            ).lower()

            if key in seen:
                continue

            seen.add(key)

            try:
                size = path.stat().st_size
            except OSError:
                size = None

            found.append({
                "DuongDan":
                    str(path),

                "TenFile":
                    path.name,

                "PhanMoRong":
                    path.suffix.lower(),

                "KichThuocByte":
                    size,
            })

    found.sort(
        key=lambda item:
        item["DuongDan"].lower()
    )

    print(
        "Tong file ung vien:",
        len(found),
    )

    for item in found:

        print(
            " ",
            item["DuongDan"],
        )

    return found


# ==========================================================
# 4. KIEM TRA CAC TEN SOURCE QUAN TRONG
# ==========================================================

def classify_sources(files):

    result = {
        "Unihan": [],
        "CJKRadicals": [],
        "MakeMeAHanzi": [],
        "HanziKhac": [],
    }

    for item in files:

        text = (
            item["DuongDan"]
            .lower()
            .replace("\\", "/")
        )

        name = (
            item["TenFile"]
            .lower()
        )

        if "unihan" in text:

            result[
                "Unihan"
            ].append(
                item["DuongDan"]
            )

        elif (
            "cjkradical"
            in text
            or "cjk_radical"
            in text
        ):

            result[
                "CJKRadicals"
            ].append(
                item["DuongDan"]
            )

        elif (
            "makemeahanzi"
            in text
            or "make_me_a_hanzi"
            in text
            or (
                name
                in {
                    "dictionary.txt",
                    "graphics.txt",
                }
                and "hanzi" in text
            )
        ):

            result[
                "MakeMeAHanzi"
            ].append(
                item["DuongDan"]
            )

        else:

            result[
                "HanziKhac"
            ].append(
                item["DuongDan"]
            )

    print(
        "\n[3] PHAN LOAI NGUON"
    )

    for key, values in (
        result.items()
    ):

        print(
            f"{key}: {len(values)}"
        )

        for value in values:

            print(
                "  ",
                value,
            )

    return result


# ==========================================================
# 5. MAIN
# ==========================================================

def main():

    print("=" * 80)

    print(
        "BUOC 16 - AUDIT NGUON + "
        "SCHEMA CHU HAN HSK4"
    )

    print("=" * 80)

    print(
        "CHI DOC FILE + CHI DOC SQL"
    )

    print(
        "KHONG INSERT / UPDATE / DELETE"
    )

    # ======================================================
    # 1. KHOA NGU PHAP FINAL
    # ======================================================

    print(
        "\n[1] KIEM TRA NGU PHAP HSK4 FINAL"
    )

    if not GRAMMAR_FINAL.is_file():

        raise FileNotFoundError(
            "Khong tim thay:\n"
            f"{GRAMMAR_FINAL}"
        )

    grammar_hash = sha256_file(
        GRAMMAR_FINAL
    )

    print(
        "FINAL GRAMMAR SHA256:"
    )

    print(
        grammar_hash
    )

    if (
        grammar_hash
        != EXPECTED_GRAMMAR_SHA256
    ):

        raise RuntimeError(
            "File grammar final HSK4 "
            "da thay doi sau Buoc 15E."
        )

    print(
        "PASS: grammar HSK4 final "
        "khong thay doi."
    )

    # ======================================================
    # 2-3. QUET SOURCE
    # ======================================================

    source_files = scan_source_files()

    source_groups = classify_sources(
        source_files
    )

    # ======================================================
    # 4. DOC SQL
    # ======================================================

    print(
        "\n[4] KIEM TRA SQL"
    )

    tables = [
        "ChuHan",
        "BoThu",
        "NguonDuLieu",
        "KhoaHoc",
        "BaiHoc",
    ]

    schemas = {}
    counts = {}

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            for table_name in tables:

                exists = table_exists(
                    cursor,
                    table_name,
                )

                print(
                    f"\nTABLE dbo.{table_name}:",
                    (
                        "CO"
                        if exists
                        else "KHONG"
                    ),
                )

                if not exists:

                    schemas[
                        table_name
                    ] = []

                    counts[
                        table_name
                    ] = None

                    continue

                schema = get_schema(
                    cursor,
                    table_name,
                )

                schemas[
                    table_name
                ] = schema

                total = count_table(
                    cursor,
                    table_name,
                )

                counts[
                    table_name
                ] = total

                print(
                    "Tong dong:",
                    total,
                )

                print(
                    "Schema:"
                )

                for column in schema:

                    length = (
                        ""
                        if column[
                            "DoDai"
                        ] is None
                        else (
                            f"({column['DoDai']})"
                        )
                    )

                    print(
                        " ",
                        f"{column['ThuTu']:>2}.",
                        column["TenCot"],
                        column["KieuDuLieu"]
                        + length,
                        "NULL="
                        + column[
                            "ChoPhepNull"
                        ],
                        "IDENTITY="
                        + str(
                            column[
                                "LaIdentity"
                            ]
                        ),
                    )

            # ==================================================
            # 5. KHOA HSK4
            # ==================================================

            print(
                "\n[5] KIEM TRA KHOA HSK4"
            )

            course_schema_names = {
                item["TenCot"]
                for item
                in schemas.get(
                    "KhoaHoc",
                    []
                )
            }

            hsk4_course = None

            # Chi truy van bang cac cot neu
            # schema THUC TE xac nhan co.
            if {
                "MaKhoaHoc",
                "MaCapDo",
            }.issubset(
                course_schema_names
            ):

                selected_columns = [
                    "MaKhoaHoc",
                    "MaCapDo",
                ]

                for optional in [
                    "TenKhoaHoc",
                    "TrangThai",
                    "MaKyHieu",
                ]:

                    if (
                        optional
                        in course_schema_names
                    ):

                        selected_columns.append(
                            optional
                        )

                sql = (
                    "SELECT "
                    + ", ".join(
                        f"[{name}]"
                        for name
                        in selected_columns
                    )
                    + """
                    FROM dbo.KhoaHoc
                    WHERE MaKhoaHoc = 4
                    """
                )

                hsk4_course = fetch_one(
                    cursor,
                    sql,
                )

                print(
                    "HSK4:",
                    hsk4_course,
                )

            else:

                print(
                    "Khong du cot schema "
                    "de truy van HSK4 an toan."
                )

            # ==================================================
            # 6. DEM BAI HSK4 NEU SCHEMA CHO PHEP
            # ==================================================

            print(
                "\n[6] KIEM TRA BAI HOC HSK4"
            )

            lesson_schema_names = {
                item["TenCot"]
                for item
                in schemas.get(
                    "BaiHoc",
                    []
                )
            }

            hsk4_lessons = None

            if (
                "MaKhoaHoc"
                in lesson_schema_names
            ):

                row = fetch_one(
                    cursor,
                    """
                    SELECT COUNT(*) AS Tong
                    FROM dbo.BaiHoc
                    WHERE MaKhoaHoc = 4
                    """,
                )

                hsk4_lessons = (
                    row["Tong"]
                    if row
                    else 0
                )

                print(
                    "So BaiHoc HSK4:",
                    hsk4_lessons,
                )

            else:

                print(
                    "dbo.BaiHoc khong co "
                    "cot MaKhoaHoc theo schema."
                )

    # ======================================================
    # 7. BAO CAO
    # ======================================================

    print(
        "\n[7] TAO REPORT AUDIT"
    )

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if REPORT_FILE.exists():

        raise FileExistsError(
            "Da ton tai report:\n"
            f"{REPORT_FILE}\n"
            "Khong tu dong ghi de."
        )

    report = {
        "status":
            "PASS",

        "buoc":
            16,

        "grammar_final_sha256":
            grammar_hash,

        "tong_file_nguon_ung_vien":
            len(
                source_files
            ),

        "phan_loai_nguon":
            source_groups,

        "sql_table_counts":
            counts,

        "sql_schemas":
            schemas,

        "hsk4_course":
            hsk4_course,

        "hsk4_lessons":
            hsk4_lessons,

        "da_tao_danh_sach_chu_hsk4":
            False,

        "da_them_chu_han":
            False,

        "da_ghi_sql":
            False,

        "ghi_chu":
            (
                "Buoc 16 chi audit nguon "
                "Unicode/Unihan/Make Me a Hanzi "
                "va schema ChuHan/BoThu. "
                "Chua xac dinh tap chu HSK4."
            ),
    }

    REPORT_FILE.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    # ======================================================
    # 8. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "AUDIT CHU HAN HSK4 HOAN THANH"
    )

    print("=" * 80)

    print(
        "Grammar final: PASS"
    )

    print(
        "File nguon ung vien:",
        len(
            source_files
        ),
    )

    print(
        "Unihan:",
        len(
            source_groups[
                "Unihan"
            ]
        ),
    )

    print(
        "CJKRadicals:",
        len(
            source_groups[
                "CJKRadicals"
            ]
        ),
    )

    print(
        "MakeMeAHanzi:",
        len(
            source_groups[
                "MakeMeAHanzi"
            ]
        ),
    )

    print(
        "\ndbo.ChuHan:",
        counts.get(
            "ChuHan"
        ),
    )

    print(
        "dbo.BoThu:",
        counts.get(
            "BoThu"
        ),
    )

    print(
        "BaiHoc HSK4:",
        hsk4_lessons,
    )

    print(
        "\nREPORT:"
    )

    print(
        " ",
        REPORT_FILE,
    )

    print(
        "\nCHUA TAO DANH SACH CHU HSK4."
    )

    print(
        "KHONG THAY DOI SQL."
    )

    print("=" * 80)


if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print(
            "\nLOI:"
        )

        print(
            error
        )

        raise SystemExit(1)