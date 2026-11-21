# -*- coding: utf-8 -*-
"""
BUOC 04 - RA SOAT CAC TRUONG HOP CAU TRUC HSK4

Chi tap trung:
1. 12 muc du kien tai su dung TuVung cu.
2. 10 muc trung ChuHan nhung khac Pinyin.
3. Nhom nguon HSK4 co cung ChuHan + Pinyin nhung nhieu muc.

CHI DOC SQL.
KHONG INSERT / UPDATE / DELETE.
"""

import csv
import re
import sys
import unicodedata

from collections import defaultdict
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


SOURCE = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
    / "vocabulary_hsk4_sql_comparison.csv"
)

EXPECTED_TOTAL = 1000


# ==========================================================
# 2. HAM HO TRO
# ==========================================================

def clean(value):
    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


def normalize_pinyin(value):

    text = unicodedata.normalize(
        "NFC",
        clean(value).lower(),
    )

    return (
        text
        .replace(" ", "")
        .replace("'", "")
        .replace("’", "")
    )


def print_separator():
    print("-" * 90)


def print_source(row):

    print(
        f"MaTuHSK={clean(row.get('MaTuHSK'))}"
        f" | {clean(row.get('ChuHan'))}"
        f" | {clean(row.get('PhienAm'))}"
    )

    print(
        "  TuLoai nguon :",
        clean(row.get("TuLoaiNguon"))
        or "(rong)",
    )

    print(
        "  Nghia nguon  :",
        clean(
            row.get("NghiaTiengVietDeXuat")
        ),
    )


# ==========================================================
# 3. DOC CSV
# ==========================================================

def read_source():

    if not SOURCE.is_file():

        raise FileNotFoundError(
            f"Khong tim thay:\n{SOURCE}"
        )

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        rows = list(
            csv.DictReader(file)
        )

    if len(rows) != EXPECTED_TOTAL:

        raise RuntimeError(
            f"File phai co {EXPECTED_TOTAL} dong, "
            f"hien co {len(rows)}."
        )

    return rows


# ==========================================================
# 4. DOC CAC BAN GHI TuVung THEO CHU HAN
# ==========================================================

def load_sql_by_hanzi(cursor, hanzi_values):

    result = defaultdict(list)

    for hanzi in sorted(hanzi_values):

        cursor.execute(
            """
            SELECT
                MaTuVung,
                ChuHan,
                PhienAm,
                NghiaTiengViet,
                TuLoai
            FROM dbo.TuVung
            WHERE ChuHan = ?
            ORDER BY
                MaTuVung;
            """,
            hanzi,
        )

        for row in cursor.fetchall():

            result[hanzi].append({

                "MaTuVung":
                    int(row[0]),

                "ChuHan":
                    clean(row[1]),

                "PhienAm":
                    clean(row[2]),

                "NghiaTiengViet":
                    clean(row[3]),

                "TuLoai":
                    clean(row[4]),
            })

    return result


# ==========================================================
# 5. MAIN
# ==========================================================

def main():

    print("=" * 90)
    print("BUOC 04 - RA SOAT CAU TRUC TU VUNG HSK4")
    print("=" * 90)

    print(
        "CHI DOC SQL - KHONG INSERT / UPDATE / DELETE"
    )

    rows = read_source()

    # ======================================================
    # A. 12 MUC DU KIEN TAI SU DUNG
    # ======================================================

    reusable = [
        row
        for row in rows
        if clean(
            row.get(
                "TrangThaiDoiChieuSQL"
            )
        )
        ==
        "DA_CO_CO_THE_TAI_SU_DUNG"
    ]

    # ======================================================
    # B. 10 MUC CUNG CHU HAN NHUNG KHAC PINYIN
    # ======================================================

    different_pinyin = [
        row
        for row in rows
        if clean(
            row.get(
                "TrangThaiDoiChieuSQL"
            )
        )
        ==
        "TRUNG_CHU_HAN_KHAC_PINYIN"
    ]

    # ======================================================
    # C. NHOM NGUON CUNG CHUHAN + PINYIN
    # ======================================================

    source_groups = defaultdict(list)

    for row in rows:

        key = (
            clean(
                row.get("ChuHan")
            ),

            normalize_pinyin(
                row.get("PhienAm")
            ),
        )

        source_groups[
            key
        ].append(row)

    duplicate_groups = {
        key: group
        for key, group
        in source_groups.items()
        if len(group) > 1
    }

    # ======================================================
    # DOC SQL CHO CAC TRUONG HOP DAC BIET
    # ======================================================

    hanzi_values = {
        clean(row.get("ChuHan"))
        for row in (
            reusable
            + different_pinyin
        )
        if clean(row.get("ChuHan"))
    }

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            sql_by_hanzi = (
                load_sql_by_hanzi(
                    cursor,
                    hanzi_values,
                )
            )

            connection.rollback()

    # ======================================================
    # 1. IN 12 MUC DU KIEN TAI SU DUNG
    # ======================================================

    print("\n")
    print("=" * 90)
    print(
        f"[1] UNG VIEN TAI SU DUNG: "
        f"{len(reusable)}"
    )
    print("=" * 90)

    for index, row in enumerate(
        reusable,
        start=1,
    ):

        print(
            f"\n[{index}]"
        )

        print_source(row)

        print(
            "  MaTuVung SQL :",
            clean(
                row.get(
                    "MaTuVungDaCo"
                )
            ),
        )

        print(
            "  Pinyin SQL   :",
            clean(
                row.get(
                    "PinyinTrongSQL"
                )
            ),
        )

        print(
            "  TuLoai SQL   :",
            clean(
                row.get(
                    "TuLoaiTrongSQL"
                )
            )
            or "(rong)",
        )

        print(
            "  Nghia SQL    :",
            clean(
                row.get(
                    "NghiaTrongSQL"
                )
            ),
        )

        print(
            "  Cach khop    :",
            clean(
                row.get(
                    "PhuongPhapKhopSQL"
                )
            ),
        )

        print_separator()

    # ======================================================
    # 2. IN 10 MUC TRUNG CHU HAN / KHAC PINYIN
    # ======================================================

    print("\n")
    print("=" * 90)

    print(
        "[2] CUNG CHU HAN NHUNG KHAC PINYIN: "
        f"{len(different_pinyin)}"
    )

    print("=" * 90)

    for index, row in enumerate(
        different_pinyin,
        start=1,
    ):

        hanzi = clean(
            row.get("ChuHan")
        )

        print(
            f"\n[{index}] NGUON HSK4"
        )

        print_source(row)

        sql_rows = (
            sql_by_hanzi.get(
                hanzi,
                [],
            )
        )

        print(
            f"  SQL hien co {len(sql_rows)} "
            "ban ghi cung ChuHan:"
        )

        for sql_row in sql_rows:

            print(
                "    -> "
                f"MaTuVung="
                f"{sql_row['MaTuVung']}"
                f" | Pinyin="
                f"{sql_row['PhienAm']}"
                f" | TuLoai="
                f"{sql_row['TuLoai'] or '(rong)'}"
                f" | Nghia="
                f"{sql_row['NghiaTiengViet']}"
            )

        print_separator()

    # ======================================================
    # 3. IN NHOM NGUON TRUNG CHU HAN + PINYIN
    # ======================================================

    print("\n")
    print("=" * 90)

    print(
        "[3] NHOM NGUON HSK4 CO CUNG "
        "CHUHAN + PINYIN: "
        f"{len(duplicate_groups)}"
    )

    print("=" * 90)

    for (
        hanzi,
        normalized_pinyin,
    ), group in sorted(
        duplicate_groups.items()
    ):

        print(
            "\n"
            f"ChuHan={hanzi}"
            f" | Pinyin="
            f"{clean(group[0].get('PhienAm'))}"
            f" | SoMuc={len(group)}"
        )

        for row in group:

            print(
                "  -> "
                f"MaTuHSK="
                f"{clean(row.get('MaTuHSK'))}"
                f" | TuLoai="
                f"{clean(row.get('TuLoaiNguon')) or '(rong)'}"
                f" | Nghia="
                f"{clean(row.get('NghiaTiengVietDeXuat'))}"
                f" | TrangThaiSQL="
                f"{clean(row.get('TrangThaiDoiChieuSQL'))}"
            )

        print_separator()

    # ======================================================
    # 4. TONG KET
    # ======================================================

    print("\n")
    print("=" * 90)
    print("TONG KET BUOC 04")
    print("=" * 90)

    print(
        "Tong HSK4:",
        len(rows),
    )

    print(
        "Ung vien tai su dung:",
        len(reusable),
    )

    print(
        "Cung ChuHan nhung khac Pinyin:",
        len(different_pinyin),
    )

    print(
        "Nhom nguon trung ChuHan + Pinyin:",
        len(duplicate_groups),
    )

    print(
        "\nCHUA THAY DOI SQL."
    )

    print("=" * 90)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print("\nLOI:")
        print(error)

        raise SystemExit(1)