# -*- coding: utf-8 -*-
"""
BUOC 09 - AUDIT NGUON NGU PHAP HSK4

Muc dich:
1. Kiem tra cac file nguon ngu phap hien co.
2. Kiem tra HSK2 / HSK3 da dung bao nhieu ngu phap.
3. Doc bao cao review ngu phap HSK3 neu co.
4. Kiem tra schema dbo.NguPhap.
5. Dem NguPhap hien co theo HSK1-4.
6. Xac dinh xem project da co nguon chuan HSK4 hay chua.

CHI DOC FILE + SQL.
KHONG INSERT / UPDATE / DELETE.
"""

import csv
import json
import sys

from contextlib import closing
from pathlib import Path


# ==========================================================
# 1. CAU HINH
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT),
)

from database import get_connection


GRAMMAR_SOURCE_DIR = (
    ROOT
    / "data_sources"
    / "hsk"
    / "grammar"
)

HSK2_GRAMMAR = (
    ROOT
    / "scripts"
    / "hsk2"
    / "data"
    / "processed"
    / "grammar_hsk2_draft.csv"
)

HSK3_GRAMMAR = (
    ROOT
    / "scripts"
    / "hsk3"
    / "data"
    / "processed"
    / "grammar_hsk3_draft.csv"
)

HSK3_REVIEW = (
    ROOT
    / "scripts"
    / "hsk3"
    / "data"
    / "processed"
    / "grammar_hsk3_review_summary.json"
)

REPORT = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
    / "hsk4_grammar_source_audit.json"
)


# ==========================================================
# 2. HAM HO TRO
# ==========================================================

def count_csv(path):

    if not path.is_file():
        return None

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        return sum(
            1
            for _ in csv.DictReader(file)
        )


def relative(path):

    try:
        return str(
            path.relative_to(ROOT)
        )

    except ValueError:
        return str(path)


# ==========================================================
# 3. MAIN
# ==========================================================

def main():

    print("=" * 76)
    print("BUOC 09 - AUDIT NGUON NGU PHAP HSK4")
    print("=" * 76)

    print(
        "CHI DOC FILE + SQL - "
        "KHONG INSERT / UPDATE / DELETE"
    )

    report = {
        "grammar_source_files": [],
        "hsk2_grammar_draft_count": None,
        "hsk3_grammar_draft_count": None,
        "hsk3_review_summary": None,
        "sql_grammar_counts": {},
        "ngu_phap_schema": [],
        "hsk4_source_candidates": [],
    }

    # ======================================================
    # 1. QUET THU MUC NGUON
    # ======================================================

    print(
        "\n[1] KIEM TRA THU MUC NGUON NGU PHAP"
    )

    print(
        "Thu muc:",
        GRAMMAR_SOURCE_DIR,
    )

    if not GRAMMAR_SOURCE_DIR.is_dir():

        print(
            "  THIEU thu muc nguon ngu phap."
        )

    else:

        files = sorted(
            path
            for path in GRAMMAR_SOURCE_DIR.rglob("*")
            if path.is_file()
        )

        print(
            "Tong file:",
            len(files),
        )

        for path in files:

            item = {
                "path":
                    relative(path),

                "suffix":
                    path.suffix.lower(),

                "csv_rows":
                    (
                        count_csv(path)
                        if path.suffix.lower()
                        == ".csv"
                        else None
                    ),
            }

            report[
                "grammar_source_files"
            ].append(item)

            if (
                "hsk4"
                in path.name.lower()
                or
                "level4"
                in path.name.lower()
                or
                "level_4"
                in path.name.lower()
            ):

                report[
                    "hsk4_source_candidates"
                ].append(
                    relative(path)
                )

        print(
            "\nCSV nguon chinh:"
        )

        for item in report[
            "grammar_source_files"
        ]:

            if item[
                "suffix"
            ] != ".csv":
                continue

            print(
                " ",
                item["path"],
                "| rows =",
                item["csv_rows"],
            )

    # ======================================================
    # 2. KIEM TRA HSK2 / HSK3 DRAFT
    # ======================================================

    print(
        "\n[2] KIEM TRA DU LIEU NGU PHAP "
        "HSK2 / HSK3 CU"
    )

    hsk2_count = count_csv(
        HSK2_GRAMMAR
    )

    hsk3_count = count_csv(
        HSK3_GRAMMAR
    )

    report[
        "hsk2_grammar_draft_count"
    ] = hsk2_count

    report[
        "hsk3_grammar_draft_count"
    ] = hsk3_count

    print(
        "HSK2 grammar draft:",
        (
            hsk2_count
            if hsk2_count is not None
            else "KHONG CO FILE"
        ),
    )

    print(
        "HSK3 grammar draft:",
        (
            hsk3_count
            if hsk3_count is not None
            else "KHONG CO FILE"
        ),
    )

    # ======================================================
    # 3. DOC REVIEW HSK3
    # ======================================================

    print(
        "\n[3] KIEM TRA REVIEW NGU PHAP HSK3"
    )

    if HSK3_REVIEW.is_file():

        data = json.loads(
            HSK3_REVIEW.read_text(
                encoding="utf-8-sig"
            )
        )

        report[
            "hsk3_review_summary"
        ] = data

        for key, value in data.items():

            print(
                f"  {key}: {value}"
            )

    else:

        print(
            "  Khong tim thay review summary HSK3."
        )

    # ======================================================
    # 4. KIEM TRA SQL
    # ======================================================

    print(
        "\n[4] KIEM TRA dbo.NguPhap"
    )

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'dbo'
                  AND TABLE_NAME = 'NguPhap'
                ORDER BY ORDINAL_POSITION;
                """
            )

            schema = []

            for row in cursor.fetchall():

                item = {
                    "COLUMN_NAME":
                        row[0],

                    "DATA_TYPE":
                        row[1],

                    "CHARACTER_MAXIMUM_LENGTH":
                        row[2],

                    "IS_NULLABLE":
                        row[3],
                }

                schema.append(
                    item
                )

            report[
                "ngu_phap_schema"
            ] = schema

            print(
                "So cot dbo.NguPhap:",
                len(schema),
            )

            for column in schema:

                print(
                    " ",
                    column[
                        "COLUMN_NAME"
                    ],
                    "|",
                    column[
                        "DATA_TYPE"
                    ],
                    "| nullable=",
                    column[
                        "IS_NULLABLE"
                    ],
                )

            # ----------------------------------------------
            # Dem ngu phap theo khoa
            # ----------------------------------------------

            cursor.execute(
                """
                SELECT
                    kh.MaKhoaHoc,
                    kh.MaCapDo,
                    COUNT(ng.MaNguPhap) AS SoNguPhap
                FROM dbo.KhoaHoc AS kh
                LEFT JOIN dbo.BaiHoc AS bh
                    ON bh.MaKhoaHoc =
                       kh.MaKhoaHoc
                LEFT JOIN dbo.NguPhap AS ng
                    ON ng.MaBaiHoc =
                       bh.MaBaiHoc
                WHERE kh.MaCapDo
                    IN (1, 2, 3, 4)
                GROUP BY
                    kh.MaKhoaHoc,
                    kh.MaCapDo
                ORDER BY
                    kh.MaCapDo,
                    kh.MaKhoaHoc;
                """
            )

            print(
                "\nNgu phap hien co theo khoa:"
            )

            for row in cursor.fetchall():

                course_id = int(
                    row[0]
                )

                level = int(
                    row[1]
                )

                count = int(
                    row[2]
                )

                report[
                    "sql_grammar_counts"
                ][str(level)] = count

                print(
                    f"  HSK{level}"
                    f" | MaKhoaHoc={course_id}"
                    f" | NguPhap={count}"
                )

            # ----------------------------------------------
            # HSK4 hien trang
            # ----------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dbo.BaiHoc
                WHERE MaKhoaHoc = 4;
                """
            )

            hsk4_lessons = int(
                cursor.fetchone()[0]
            )

            print(
                "\nBaiHoc HSK4:",
                hsk4_lessons,
            )

            connection.rollback()

    # ======================================================
    # 5. DANH GIA NGUON HSK4
    # ======================================================

    print(
        "\n[5] DANH GIA NGUON NGU PHAP HSK4"
    )

    candidates = report[
        "hsk4_source_candidates"
    ]

    if candidates:

        print(
            "Tim thay file co ten lien quan HSK4:"
        )

        for path in candidates:
            print(
                " ",
                path,
            )

    else:

        print(
            "CHUA tim thay file nguon "
            "co ten HSK4/Level4."
        )

        print(
            "KHONG nen tu dong bien soan "
            "ngu phap HSK4 roi coi la "
            "'nguon chuan'."
        )

    # ======================================================
    # 6. XUAT REPORT
    # ======================================================

    REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if REPORT.exists():

        raise FileExistsError(
            "Da ton tai report:\n"
            + str(REPORT)
        )

    REPORT.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # ======================================================
    # 7. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 76
    )

    print(
        "AUDIT NGUON NGU PHAP HSK4 HOAN THANH"
    )

    print("=" * 76)

    print(
        "HSK2 draft:",
        hsk2_count,
    )

    print(
        "HSK3 draft:",
        hsk3_count,
    )

    print(
        "File nguon HSK4 tim thay:",
        len(candidates),
    )

    print(
        "\nBao cao:"
    )

    print(
        " ",
        REPORT,
    )

    print(
        "\nKHONG THAY DOI SQL."
    )

    print("=" * 76)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print("\nLOI:")
        print(error)

        raise SystemExit(1)