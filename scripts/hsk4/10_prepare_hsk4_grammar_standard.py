# -*- coding: utf-8 -*-
"""
BUOC 10 - TAO NGUON CHUAN 76 NGU PHAP HSK4

Nguon chinh:
GF0025-2021
《国际中文教育中文水平等级标准》
Phu luc A - 语法等级大纲

Nguon machine-readable:
ivankra/hsk30/hsk30-grammar.csv

Muc dich:
1. Kiem tra MaNguon GF0025-2021 trong SQL.
2. Tai/luu ban machine-readable neu chua co.
3. Loc chinh xac Level = 4.
4. Bat buoc phai co dung 76 muc.
5. Tao ma on dinh GF4-001 ... GF4-076.
6. Tao file nguon chuan HSK4.

KHONG INSERT / UPDATE / DELETE SQL.
"""

import csv
import hashlib
import sys
import urllib.request

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


HSK_LEVEL = 4

EXPECTED_COUNT = 76

SOURCE_NAME = (
    "GF0025-2021 - Ngữ pháp HSK"
)

# File raw machine-readable.
RAW_DIR = (
    ROOT
    / "data_sources"
    / "hsk"
    / "grammar"
)

RAW_FILE = (
    RAW_DIR
    / "hsk30_grammar_gf0025.csv"
)

OUTPUT_FILE = (
    RAW_DIR
    / "hsk4_76_grammar_standard.csv"
)


RAW_URL = (
    "https://raw.githubusercontent.com/"
    "ivankra/hsk30/master/"
    "hsk30-grammar.csv"
)


# ==========================================================
# 2. HAM HO TRO
# ==========================================================

def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def fail(message):

    raise RuntimeError(
        message
    )


def sha256_file(path):

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:

        while True:

            block = file.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(
                block
            )

    return digest.hexdigest()


def read_csv(path):

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        rows = list(
            reader
        )

        fields = (
            reader.fieldnames
            or []
        )

    return fields, rows


# ==========================================================
# 3. KIEM TRA NGUON TRONG SQL
# ==========================================================

def get_source_info():

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    MaNguon,
                    Ten,
                    LienKetNguon,
                    GiayPhep,
                    GhiChu
                FROM dbo.NguonDuLieu
                WHERE Ten = ?;
                """,
                SOURCE_NAME,
            )

            rows = (
                cursor.fetchall()
            )

            connection.rollback()

    if len(rows) == 0:

        fail(
            "Khong tim thay nguon SQL:\n"
            f"{SOURCE_NAME}\n\n"
            "KHONG tu dong tao MaNguon moi."
        )

    if len(rows) > 1:

        fail(
            "Co nhieu hon 1 NguonDuLieu "
            "cung ten GF0025 grammar."
        )

    row = rows[0]

    return {
        "MaNguon":
            int(row[0]),

        "Ten":
            clean(row[1]),

        "LienKetNguon":
            clean(row[2]),

        "GiayPhep":
            clean(row[3]),

        "GhiChu":
            clean(row[4]),
    }


# ==========================================================
# 4. TAI MACHINE-READABLE SOURCE
# ==========================================================

def ensure_raw_source():

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if RAW_FILE.is_file():

        print(
            "File raw da ton tai:"
        )

        print(
            " ",
            RAW_FILE,
        )

        print(
            "Khong tai lai."
        )

        return

    print(
        "Dang tai machine-readable source..."
    )

    request = urllib.request.Request(
        RAW_URL,
        headers={
            "User-Agent":
                "Moc-Han-Graduation-Project/1.0"
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=30,
        ) as response:

            data = response.read()

    except Exception as error:

        raise RuntimeError(
            "Khong tai duoc source.\n"
            f"URL: {RAW_URL}\n"
            f"Loi: {error}"
        )

    if len(data) < 10000:

        fail(
            "File tai ve qua nho, "
            "co the khong phai CSV mong doi."
        )

    # Ghi file mot lan.
    with RAW_FILE.open(
        "xb"
    ) as file:

        file.write(
            data
        )

    print(
        "Da tai:"
    )

    print(
        " ",
        RAW_FILE,
    )


# ==========================================================
# 5. XAC DINH TEN MUC
# ==========================================================

def choose_item_name(
    group,
    category,
    details,
    content,
):
    """
    Ten muc dung cho file nguon.

    Khong bien soan nghia tieng Viet.
    Chi chon nhan Trung van de de xem.
    """

    group = clean(group)
    category = clean(category)
    details = clean(details)
    content = clean(content)

    # Uu tien muc chi tiet.
    if details:

        # Mot so Details chi la nhom chung.
        generic = {
            "单句",
            "复句",
            "特殊句型",
            "其他",
            "其他结构类型",
            "结构类型",
            "句型",
            "句类",
            "动作的态",
        }

        if (
            details not in generic
            or not content
        ):
            return details

    if content:
        return content

    if category:
        return category

    return group


# ==========================================================
# 6. MAIN
# ==========================================================

def main():

    print("=" * 78)

    print(
        "BUOC 10 - TAO NGUON CHUAN "
        "76 NGU PHAP HSK4"
    )

    print("=" * 78)

    print(
        "CHI DOC SQL + TAO CSV"
    )

    print(
        "KHONG INSERT / UPDATE / DELETE SQL"
    )

    # ======================================================
    # 1. KIEM TRA SOURCE SQL
    # ======================================================

    print(
        "\n[1] KIEM TRA NGUON GF0025-2021"
    )

    source = get_source_info()

    print(
        "MaNguon:",
        source["MaNguon"],
    )

    print(
        "Ten:",
        source["Ten"],
    )

    print(
        "LienKetNguon:",
        source["LienKetNguon"]
        or "(rong)",
    )

    print(
        "PASS: Nguon grammar GF0025 "
        "da duoc dang ky."
    )

    # ======================================================
    # 2. RAW SOURCE
    # ======================================================

    print(
        "\n[2] KIEM TRA MACHINE-READABLE SOURCE"
    )

    ensure_raw_source()

    raw_hash = sha256_file(
        RAW_FILE
    )

    print(
        "RAW SHA256:"
    )

    print(
        raw_hash
    )

    # ======================================================
    # 3. DOC CSV
    # ======================================================

    print(
        "\n[3] DOC DU LIEU NGU PHAP"
    )

    fields, all_rows = read_csv(
        RAW_FILE
    )

    print(
        "Tong dong:",
        len(all_rows),
    )

    print(
        "Cot:",
        fields,
    )

    required = {
        "No",
        "Level",
        "Group",
        "Category",
        "Details",
        "Content",
    }

    missing = (
        required
        - set(fields)
    )

    if missing:

        fail(
            "Source thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    # ======================================================
    # 4. DEM THEO LEVEL
    # ======================================================

    print(
        "\n[4] THONG KE THEO LEVEL"
    )

    counts = {}

    for row in all_rows:

        level = clean(
            row.get("Level")
        )

        counts[level] = (
            counts.get(
                level,
                0,
            )
            + 1
        )

    for level in sorted(
        counts,
        key=lambda x: (
            int(x)
            if x.isdigit()
            else 999
        ),
    ):

        print(
            f"  Level {level}: "
            f"{counts[level]}"
        )

    # ======================================================
    # 5. LOC LEVEL 4
    # ======================================================

    print(
        "\n[5] LOC HSK4"
    )

    hsk4 = [
        row
        for row in all_rows
        if clean(
            row.get("Level")
        ) == str(HSK_LEVEL)
    ]

    print(
        "So muc HSK4:",
        len(hsk4),
    )

    if (
        len(hsk4)
        != EXPECTED_COUNT
    ):

        fail(
            "HSK4 GF0025 phai co "
            f"{EXPECTED_COUNT} muc moi. "
            f"Source hien co {len(hsk4)}."
        )

    print(
        "PASS: HSK4 co dung "
        "76 muc ngu phap moi."
    )

    # ======================================================
    # 6. KIEM TRA SOURCE NO
    # ======================================================

    source_numbers = []

    for row in hsk4:

        raw_no = clean(
            row.get("No")
        )

        try:

            number = int(
                raw_no
            )

        except ValueError:

            fail(
                "No khong phai so: "
                f"{raw_no}"
            )

        source_numbers.append(
            number
        )

    if (
        len(set(source_numbers))
        != EXPECTED_COUNT
    ):

        fail(
            "Cot No cua 76 muc "
            "bi trung."
        )

    print(
        "Source No:",
        min(source_numbers),
        "->",
        max(source_numbers),
    )

    # ======================================================
    # 7. TAO RECORD CHUAN
    # ======================================================

    print(
        "\n[6] CHUAN HOA FILE HSK4"
    )

    records = []

    for index, row in enumerate(
        hsk4,
        start=1,
    ):

        group = clean(
            row.get("Group")
        )

        category = clean(
            row.get("Category")
        )

        details = clean(
            row.get("Details")
        )

        content = clean(
            row.get("Content")
        )

        if not group:

            fail(
                f"GF4-{index:03d}: "
                "thieu Group."
            )

        item_name = (
            choose_item_name(
                group,
                category,
                details,
                content,
            )
        )

        # NoiDungChuanTrung:
        # giu nguyen Content neu co.
        # Neu source khong co Content,
        # dung Details/Category de khong mat muc.
        official_content = (
            content
            or details
            or category
            or group
        )

        if not official_content:

            fail(
                f"GF4-{index:03d}: "
                "khong co noi dung."
            )

        records.append({

            "MaMucNguPhapChuan":
                f"GF4-{index:03d}",

            "CapDoHSK":
                HSK_LEVEL,

            "SoThuTuChuan":
                index,

            "SoThuTuNguon":
                clean(
                    row.get("No")
                ),

            "NhomLonTrung":
                group,

            "NhomConTrung":
                category,

            "TenMucTrung":
                item_name,

            "ChiTietTrung":
                details,

            "NoiDungChuanTrung":
                official_content,

            "MaNguon":
                source["MaNguon"],

            "TrangThaiReview":
                "nguon_chuan",

            "GhiChu":
                (
                    "GF0025-2021 cap 4; "
                    "machine-readable cross-check "
                    "tu ivankra/hsk30. "
                    "Chua phai noi dung giang day "
                    "tieng Viet."
                ),
        })

    # ======================================================
    # 8. VALIDATE RECORD
    # ======================================================

    ids = [
        row[
            "MaMucNguPhapChuan"
        ]
        for row in records
    ]

    orders = [
        int(
            row[
                "SoThuTuChuan"
            ]
        )
        for row in records
    ]

    if (
        len(set(ids))
        != EXPECTED_COUNT
    ):

        fail(
            "MaMucNguPhapChuan bi trung."
        )

    if orders != list(
        range(
            1,
            EXPECTED_COUNT + 1,
        )
    ):

        fail(
            "SoThuTuChuan "
            "khong lien tuc 1 -> 76."
        )

    print(
        "PASS: GF4-001 -> GF4-076"
    )

    # ======================================================
    # 9. KHONG GHI DE FILE CU
    # ======================================================

    if OUTPUT_FILE.exists():

        raise FileExistsError(
            "Da ton tai file:\n"
            f"{OUTPUT_FILE}\n\n"
            "Khong tu dong ghi de."
        )

    # ======================================================
    # 10. WRITE CSV
    # ======================================================

    fieldnames = [
        "MaMucNguPhapChuan",
        "CapDoHSK",
        "SoThuTuChuan",
        "SoThuTuNguon",
        "NhomLonTrung",
        "NhomConTrung",
        "TenMucTrung",
        "ChiTietTrung",
        "NoiDungChuanTrung",
        "MaNguon",
        "TrangThaiReview",
        "GhiChu",
    ]

    with OUTPUT_FILE.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            records
        )

    # ======================================================
    # 11. THONG KE NHOM
    # ======================================================

    groups = {}

    for row in records:

        name = row[
            "NhomLonTrung"
        ]

        groups[name] = (
            groups.get(
                name,
                0,
            )
            + 1
        )

    print(
        "\n[7] THONG KE NHOM HSK4"
    )

    for name, count in groups.items():

        print(
            f"  {name}: {count}"
        )

    # ======================================================
    # 12. KET QUA
    # ======================================================

    output_hash = sha256_file(
        OUTPUT_FILE
    )

    print(
        "\n" + "=" * 78
    )

    print(
        "TAO NGUON CHUAN "
        "NGU PHAP HSK4 THANH CONG"
    )

    print("=" * 78)

    print(
        "Tong:",
        len(records),
        "/ 76",
    )

    print(
        "Ma:",
        ids[0],
        "->",
        ids[-1],
    )

    print(
        "MaNguon:",
        source["MaNguon"],
    )

    print(
        "\nRAW:"
    )

    print(
        " ",
        RAW_FILE,
    )

    print(
        "\nOUTPUT:"
    )

    print(
        " ",
        OUTPUT_FILE,
    )

    print(
        "\nOUTPUT SHA256:"
    )

    print(
        output_hash
    )

    print(
        "\nKHONG THAY DOI SQL."
    )

    print("=" * 78)


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