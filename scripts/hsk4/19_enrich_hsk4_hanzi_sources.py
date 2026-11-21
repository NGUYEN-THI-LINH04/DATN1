# -*- coding: utf-8 -*-
"""
BUOC 19 - ENRICH 300 CHU HAN MOI HSK4

Nguon:
1. hanzi_hsk4_new_candidates.csv
2. Unicode Unihan.zip
3. Unicode CJKRadicals.txt
4. Make Me a Hanzi:
   - dictionary.txt
   - graphics.txt
5. dbo.BoThu - CHI SELECT

Muc dich:
- Khoa snapshot 300 chu moi tu Buoc 18.
- Doc truc tiep Unihan.zip, KHONG can giai nen thu cong.
- Lay:
    + kMandarin
    + kTotalStrokes
    + kRSUnicode
- Lay Make Me a Hanzi:
    + pinyin
    + definition
    + radical
    + decomposition
    + strokes
    + medians
- Doi chieu so net Unihan <-> Make Me a Hanzi.
- Map SoBoThu Unicode -> dbo.BoThu.
- Xuat file review.

QUAN TRONG:
- CHUA chot Pinyin cuoi.
- CHUA chot nghia Viet.
- CHUA gan BaiHoc.
- KHONG INSERT SQL.
- KHONG UPDATE SQL.
- KHONG DELETE SQL.
"""

import csv
import hashlib
import json
import re
import sys
import zipfile

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


DATA_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)


SOURCE = (
    DATA_DIR
    / "hanzi_hsk4_new_candidates.csv"
)


OUTPUT = (
    DATA_DIR
    / "hanzi_hsk4_300_enriched_sources.csv"
)


ISSUES_FILE = (
    DATA_DIR
    / "hanzi_hsk4_300_source_issues.csv"
)


SUMMARY_FILE = (
    DATA_DIR
    / "hanzi_hsk4_300_enriched_sources_summary.json"
)


# ----------------------------------------------------------
# Unicode / Unihan
# ----------------------------------------------------------

UNICODE_DIR = (
    ROOT
    / "data_sources"
    / "unicode"
)


UNIHAN_ZIP_EXPECTED = (
    UNICODE_DIR
    / "Unihan.zip"
)


CJK_RADICALS_EXPECTED = (
    UNICODE_DIR
    / "CJKRadicals.txt"
)


# ----------------------------------------------------------
# Make Me a Hanzi
# ----------------------------------------------------------

HANZI_SOURCE_DIR = (
    ROOT
    / "data_sources"
    / "hanzi"
)


# ----------------------------------------------------------
# Snapshot Buoc 18
# ----------------------------------------------------------

EXPECTED_SOURCE_SHA256 = (
    "d274eceb4c1eb5f4609876b60cafaf"
    "7367039ffad7aba693fc858b715c2bf1ef"
)


EXPECTED_TOTAL = 300


# ==========================================================
# 2. COT OUTPUT
# ==========================================================

OUTPUT_FIELDS = [

    # ======================================================
    # Thong tin tu Buoc 18
    # ======================================================

    "MaChuHanTam",
    "KyTu",

    "ThuTuXuatHienDau",

    "MaTuHSKDauTien",
    "MaMucNoiBoDauTien",
    "SoThuTuNguonDauTien",

    "TuVungDaiDien",
    "PinyinTuDaiDien",
    "NghiaTuDaiDien",

    "SoTuHSK4ChuaKyTu",
    "CacMaMucNoiBo",
    "CacTuHSK4ChuaKyTu",

    # ======================================================
    # Unicode / Unihan
    # ======================================================

    "PinyinUnihanRaw",
    "SoNetUnihanRaw",
    "RSUnicodeRaw",

    "DanhSachSoBoThuUnicode",
    "SoBoThuUnicode",

    # ======================================================
    # Make Me a Hanzi
    # ======================================================

    "CoMakeMeAHanziDictionary",
    "CoMakeMeAHanziGraphics",

    "PinyinMakeMeAHanzi",
    "DefinitionEnglishMakeMeAHanzi",

    "RadicalMakeMeAHanzi",
    "DecompositionMakeMeAHanzi",

    "SoNetMakeMeAHanzi",
    "SoMedianMakeMeAHanzi",

    # ======================================================
    # Map bo thu SQL
    # ======================================================

    "MaBoThuSQL",
    "SoBoThuSQL",
    "KyHieuBoThuSQL",
    "TenBoThuSQL",
    "YNghiaBoThuSQL",

    # ======================================================
    # So net
    # ======================================================

    "KiemTraSoNet",
    "SoNetDeXuat",

    # ======================================================
    # Trang thai
    # ======================================================

    "CoDuLieuUnihan",
    "KiemTraBoThu",
    "TinhTrangDuLieu",

    # ======================================================
    # Chua duoc chot tai Buoc 19
    # ======================================================

    "PinyinFinal",
    "NghiaTiengVietFinal",

    "CanKiemTraPinyin",
    "CanKiemTraNghia",
    "CanKiemTraBoThu",
    "CanKiemTraSoNet",

    "GhiChu",
]


ISSUE_FIELDS = [
    "MaChuHanTam",
    "KyTu",
    "LoaiVanDe",
    "ChiTiet",
]


# ==========================================================
# 3. HAM CO BAN
# ==========================================================

def clean(value):

    if value is None:
        return ""

    if isinstance(
        value,
        list,
    ):

        return " | ".join(
            clean(item)
            for item in value
            if clean(item)
        )

    return str(
        value
    ).strip()


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

    if not path.is_file():

        raise FileNotFoundError(
            f"Khong tim thay file:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        fields = (
            reader.fieldnames
            or []
        )

        rows = list(
            reader
        )

    return fields, rows


def write_csv(
    path,
    rows,
    fields,
):

    if path.exists():

        raise FileExistsError(
            f"File da ton tai:\n"
            f"{path}\n"
            "Khong tu dong ghi de."
        )

    with path.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields,
            extrasaction="ignore",
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


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
        for item
        in cursor.description
    ]

    return [
        dict(
            zip(
                columns,
                row,
            )
        )
        for row
        in cursor.fetchall()
    ]


def get_table_columns(
    cursor,
    table_name,
):

    rows = fetch_all(
        cursor,
        """
        SELECT
            COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """,
        table_name,
    )

    return {
        row[
            "COLUMN_NAME"
        ]
        for row in rows
    }


def join_unique(
    values,
    separator=" | ",
):

    result = []

    seen = set()

    for value in values:

        value = clean(
            value
        )

        if not value:
            continue

        if value in seen:
            continue

        seen.add(
            value
        )

        result.append(
            value
        )

    return separator.join(
        result
    )


# ==========================================================
# 4. TIM UNIHAN.ZIP
# ==========================================================

def find_unihan_zip():

    # ------------------------------------------------------
    # Duong dan dung cua project hien tai.
    # ------------------------------------------------------

    if UNIHAN_ZIP_EXPECTED.is_file():

        return (
            UNIHAN_ZIP_EXPECTED
        )

    # ------------------------------------------------------
    # Fallback neu sau nay user di chuyen file.
    # Tim tren toan bo data_sources.
    # ------------------------------------------------------

    data_sources = (
        ROOT
        / "data_sources"
    )

    if not data_sources.exists():

        return None

    matches = []

    for path in data_sources.rglob(
        "*"
    ):

        if not path.is_file():
            continue

        if (
            path.name.lower()
            == "unihan.zip"
        ):

            matches.append(
                path
            )

    if not matches:

        return None

    matches.sort(
        key=lambda p:
        len(
            str(p)
        )
    )

    return matches[0]


# ==========================================================
# 5. DOC UNIHAN.ZIP
# ==========================================================

def load_unihan_from_zip(
    zip_path,
    wanted_chars,
):

    """
    Doc TRUC TIEP cac member Unihan_*.txt trong Unihan.zip.

    Khong can user giai nen.

    Chi thu thap:
    - kMandarin
    - kTotalStrokes
    - kRSUnicode
    """

    result = {
        char: defaultdict(list)
        for char
        in wanted_chars
    }

    useful_fields = {
        "kMandarin",
        "kTotalStrokes",
        "kRSUnicode",
    }

    parsed_members = []

    with zipfile.ZipFile(
        zip_path,
        "r",
    ) as archive:

        members = (
            archive.namelist()
        )

        # --------------------------------------------------
        # Khong hard-code 3 file.
        # Doc tat ca Unihan_*.txt trong ZIP.
        # Neu Unicode thay doi vi tri field,
        # script van tim duoc.
        # --------------------------------------------------

        unihan_members = [
            member
            for member in members
            if (
                Path(
                    member
                ).name.startswith(
                    "Unihan_"
                )
                and Path(
                    member
                ).suffix.lower()
                == ".txt"
            )
        ]

        if not unihan_members:

            raise RuntimeError(
                "Unihan.zip khong chua "
                "file Unihan_*.txt."
            )

        for member in sorted(
            unihan_members
        ):

            found_useful_field = False

            with archive.open(
                member,
                "r",
            ) as raw_file:

                for raw_line in raw_file:

                    try:

                        line = (
                            raw_line
                            .decode(
                                "utf-8",
                                errors="replace",
                            )
                            .strip()
                        )

                    except Exception:

                        continue

                    if not line:
                        continue

                    if line.startswith(
                        "#"
                    ):
                        continue

                    if not line.startswith(
                        "U+"
                    ):
                        continue

                    parts = line.split(
                        "\t",
                        2,
                    )

                    if len(parts) != 3:
                        continue

                    codepoint_text = (
                        parts[0]
                    )

                    field = (
                        parts[1]
                    )

                    value = (
                        parts[2]
                    )

                    if (
                        field
                        not in useful_fields
                    ):
                        continue

                    found_useful_field = True

                    try:

                        codepoint = int(
                            codepoint_text[
                                2:
                            ],
                            16,
                        )

                        char = chr(
                            codepoint
                        )

                    except Exception:

                        continue

                    if (
                        char
                        not in wanted_chars
                    ):
                        continue

                    if (
                        value
                        not in result[
                            char
                        ][field]
                    ):

                        result[
                            char
                        ][field].append(
                            value
                        )

            if found_useful_field:

                parsed_members.append(
                    Path(
                        member
                    ).name
                )

    return (
        result,
        sorted(
            set(
                parsed_members
            )
        ),
    )


# ==========================================================
# 6. TIM MAKE ME A HANZI
# ==========================================================

def find_files_by_name(
    root,
    target_name,
):

    result = []

    if not root.exists():

        return result

    target_name = (
        target_name.lower()
    )

    for path in root.rglob(
        "*"
    ):

        if not path.is_file():
            continue

        if (
            path.name.lower()
            == target_name
        ):

            result.append(
                path
            )

    return result


def choose_makemeahanzi_file(
    paths,
):

    if not paths:

        return None

    preferred = [
        path
        for path in paths
        if "makemeahanzi"
        in str(
            path
        ).lower()
    ]

    candidates = (
        preferred
        if preferred
        else paths
    )

    candidates.sort(
        key=lambda path:
        len(
            str(path)
        )
    )

    return candidates[0]


# ==========================================================
# 7. DOC JSON LINES MAKE ME A HANZI
# ==========================================================

def load_json_lines_by_character(
    path,
    wanted_chars,
):

    result = {}

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
    ) as file:

        for line_number, raw_line in enumerate(
            file,
            start=1,
        ):

            text = (
                raw_line.strip()
            )

            if not text:
                continue

            try:

                obj = json.loads(
                    text
                )

            except json.JSONDecodeError:

                # Source MMAH la JSON Lines.
                # Neu co mot dong khong doc duoc,
                # khong dung toan pipeline.
                continue

            character = clean(
                obj.get(
                    "character"
                )
            )

            if not character:
                continue

            if (
                character
                not in wanted_chars
            ):
                continue

            if (
                character
                not in result
            ):

                result[
                    character
                ] = obj

    return result


# ==========================================================
# 8. PARSE UNIHAN
# ==========================================================

def extract_integers(text):

    return [
        int(item)
        for item in re.findall(
            r"\d+",
            clean(
                text
            ),
        )
    ]


def parse_total_strokes(raw):

    """
    kTotalStrokes co the co mot hoac nhieu gia tri.
    Tra ve danh sach int unique.
    """

    numbers = (
        extract_integers(
            raw
        )
    )

    return sorted(
        set(
            numbers
        )
    )


def parse_rs_unicode_radicals(
    raw,
):

    """
    Vi du kRSUnicode:
        85.8
        85'.8
        140.4 85.8

    Can lay phan radical number truoc dau cham.
    """

    result = set()

    text = clean(
        raw
    )

    for match in re.finditer(
        r"(?:^|\s)(\d{1,3})'?\.",
        text,
    ):

        number = int(
            match.group(1)
        )

        if (
            1
            <= number
            <= 214
        ):

            result.add(
                number
            )

    return sorted(
        result
    )


# ==========================================================
# 9. MAIN
# ==========================================================

def main():

    print(
        "=" * 80
    )

    print(
        "BUOC 19 - ENRICH 300 CHU HAN MOI HSK4"
    )

    print(
        "=" * 80
    )

    print(
        "UNIHAN.ZIP + MAKE ME A HANZI + dbo.BoThu"
    )

    print(
        "KHONG GHI SQL"
    )

    # ======================================================
    # [1] KHOA SNAPSHOT BUOC 18
    # ======================================================

    print(
        "\n[1] KIEM TRA SNAPSHOT BUOC 18"
    )

    source_hash = (
        sha256_file(
            SOURCE
        )
    )

    print(
        "SOURCE SHA256:"
    )

    print(
        source_hash
    )

    if (
        source_hash
        != EXPECTED_SOURCE_SHA256
    ):

        raise RuntimeError(
            "hanzi_hsk4_new_candidates.csv "
            "da thay doi sau Buoc 18."
        )

    fields, source_rows = (
        read_csv(
            SOURCE
        )
    )

    required_fields = {
        "MaChuHanTam",
        "KyTu",
        "ThuTuXuatHienDau",
        "MaTuHSKDauTien",
        "MaMucNoiBoDauTien",
        "SoThuTuNguonDauTien",
        "TuVungDaiDien",
        "PinyinTuDaiDien",
        "NghiaTuDaiDien",
        "SoTuHSK4ChuaKyTu",
        "CacMaMucNoiBo",
        "CacTuHSK4ChuaKyTu",
        "DaCoTrongSQL",
        "TrangThai",
    }

    missing = (
        required_fields
        - set(
            fields
        )
    )

    if missing:

        raise RuntimeError(
            "File Buoc 18 thieu cot: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )

    print(
        "Tong:",
        len(
            source_rows
        ),
    )

    if (
        len(
            source_rows
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "File Buoc 18 khong con "
            "dung 300 chu."
        )

    chars = [
        clean(
            row[
                "KyTu"
            ]
        )
        for row
        in source_rows
    ]

    if (
        len(
            set(
                chars
            )
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "KyTu trong Buoc 18 bi trung."
        )

    for row in source_rows:

        char = clean(
            row[
                "KyTu"
            ]
        )

        if (
            clean(
                row[
                    "TrangThai"
                ]
            )
            != "MOI_HSK4"
        ):

            raise RuntimeError(
                f"{char}: "
                "TrangThai != MOI_HSK4."
            )

        if (
            clean(
                row[
                    "DaCoTrongSQL"
                ]
            )
            != "KHONG"
        ):

            raise RuntimeError(
                f"{char}: "
                "DaCoTrongSQL != KHONG."
            )

    print(
        "PASS: 300 KyTu moi duy nhat."
    )

    wanted_chars = set(
        chars
    )

    # ======================================================
    # [2] TIM SOURCE
    # ======================================================

    print(
        "\n[2] TIM SOURCE TREN MAY"
    )

    # ------------------------------------------------------
    # Unihan.zip
    # ------------------------------------------------------

    unihan_zip = (
        find_unihan_zip()
    )

    print(
        "Unihan ZIP:"
    )

    print(
        " ",
        unihan_zip,
    )

    if unihan_zip is None:

        raise RuntimeError(
            "Khong tim thay Unihan.zip."
        )

    if not zipfile.is_zipfile(
        unihan_zip
    ):

        raise RuntimeError(
            f"File khong phai ZIP hop le:\n"
            f"{unihan_zip}"
        )

    # ------------------------------------------------------
    # CJKRadicals
    # ------------------------------------------------------

    cjk_radicals_file = (
        CJK_RADICALS_EXPECTED
        if CJK_RADICALS_EXPECTED.is_file()
        else None
    )

    print(
        "CJKRadicals:"
    )

    print(
        " ",
        cjk_radicals_file,
    )

    # CJKRadicals khong bat buoc de Buoc 19 chay,
    # vi radical number se map voi dbo.BoThu.
    # Tuy nhien ghi nhan neu file co san.

    # ------------------------------------------------------
    # Make Me a Hanzi
    # ------------------------------------------------------

    dictionary_candidates = (
        find_files_by_name(
            HANZI_SOURCE_DIR,
            "dictionary.txt",
        )
    )

    graphics_candidates = (
        find_files_by_name(
            HANZI_SOURCE_DIR,
            "graphics.txt",
        )
    )

    dictionary_file = (
        choose_makemeahanzi_file(
            dictionary_candidates
        )
    )

    graphics_file = (
        choose_makemeahanzi_file(
            graphics_candidates
        )
    )

    print(
        "MakeMeAHanzi dictionary:"
    )

    print(
        " ",
        dictionary_file,
    )

    print(
        "MakeMeAHanzi graphics:"
    )

    print(
        " ",
        graphics_file,
    )

    if dictionary_file is None:

        raise RuntimeError(
            "Khong tim thay "
            "Make Me a Hanzi dictionary.txt."
        )

    if graphics_file is None:

        raise RuntimeError(
            "Khong tim thay "
            "Make Me a Hanzi graphics.txt."
        )

    # ======================================================
    # [3] DOC UNIHAN.ZIP
    # ======================================================

    print(
        "\n[3] DOC UNIHAN.ZIP"
    )

    (
        unihan,
        unihan_members,
    ) = load_unihan_from_zip(
        unihan_zip,
        wanted_chars,
    )

    print(
        "PASS: da doc truc tiep Unihan.zip."
    )

    print(
        "Members chua field can dung:",
        len(
            unihan_members
        ),
    )

    for member in unihan_members:

        print(
            " ",
            member,
        )

    # ======================================================
    # [4] DOC MAKE ME A HANZI
    # ======================================================

    print(
        "\n[4] DOC MAKE ME A HANZI"
    )

    mmah_dictionary = (
        load_json_lines_by_character(
            dictionary_file,
            wanted_chars,
        )
    )

    mmah_graphics = (
        load_json_lines_by_character(
            graphics_file,
            wanted_chars,
        )
    )

    print(
        "Dictionary coverage:",
        len(
            mmah_dictionary
        ),
        "/ 300",
    )

    print(
        "Graphics coverage:",
        len(
            mmah_graphics
        ),
        "/ 300",
    )

    # ======================================================
    # [5] DOC dbo.BoThu
    # ======================================================

    print(
        "\n[5] DOC dbo.BoThu"
    )

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            bo_thu_columns = (
                get_table_columns(
                    cursor,
                    "BoThu",
                )
            )

            required_bo_thu = {
                "MaBoThu",
                "SoBoThu",
                "KyHieu",
                "TenBoThu",
                "YNghia",
                "SoNet",
                "TrangThai",
            }

            missing_bo_thu = (
                required_bo_thu
                - bo_thu_columns
            )

            if missing_bo_thu:

                raise RuntimeError(
                    "dbo.BoThu thieu cot: "
                    + ", ".join(
                        sorted(
                            missing_bo_thu
                        )
                    )
                )

            radicals = fetch_all(
                cursor,
                """
                SELECT
                    MaBoThu,
                    SoBoThu,
                    KyHieu,
                    TenBoThu,
                    YNghia,
                    SoNet,
                    TrangThai

                FROM dbo.BoThu

                ORDER BY
                    SoBoThu,
                    MaBoThu
                """
            )

    print(
        "Tong dbo.BoThu:",
        len(
            radicals
        ),
    )

    radical_by_number = (
        defaultdict(
            list
        )
    )

    for radical in radicals:

        so_bo_thu = (
            radical.get(
                "SoBoThu"
            )
        )

        if so_bo_thu is None:
            continue

        try:

            number = int(
                so_bo_thu
            )

        except Exception:
            continue

        radical_by_number[
            number
        ].append(
            radical
        )

    # ======================================================
    # [6] ENRICH
    # ======================================================

    print(
        "\n[6] ENRICH 300 CHU"
    )

    output_rows = []

    issues = []

    coverage_unihan = 0
    coverage_mmah_dictionary = 0
    coverage_mmah_graphics = 0

    stroke_ready = 0
    stroke_review = 0

    radical_ready = 0
    radical_review = 0

    # ------------------------------------------------------
    # Coverage tung field Unihan
    # ------------------------------------------------------

    coverage_kmandarin = 0
    coverage_kstrokes = 0
    coverage_krs = 0

    for source_row in source_rows:

        char = clean(
            source_row[
                "KyTu"
            ]
        )

        temp_id = clean(
            source_row[
                "MaChuHanTam"
            ]
        )

        # ==================================================
        # A. UNIHAN
        # ==================================================

        unihan_data = (
            unihan.get(
                char,
                {}
            )
        )

        mandarin_raw = (
            join_unique(
                unihan_data.get(
                    "kMandarin",
                    [],
                )
            )
        )

        strokes_raw = (
            join_unique(
                unihan_data.get(
                    "kTotalStrokes",
                    [],
                )
            )
        )

        rs_unicode_raw = (
            join_unique(
                unihan_data.get(
                    "kRSUnicode",
                    [],
                )
            )
        )

        if mandarin_raw:

            coverage_kmandarin += 1

        if strokes_raw:

            coverage_kstrokes += 1

        if rs_unicode_raw:

            coverage_krs += 1

        has_unihan = bool(
            mandarin_raw
            or strokes_raw
            or rs_unicode_raw
        )

        if has_unihan:

            coverage_unihan += 1

        # ==================================================
        # B. RADICAL UNICODE
        # ==================================================

        radical_numbers = (
            parse_rs_unicode_radicals(
                rs_unicode_raw
            )
        )

        radical_numbers_text = (
            ",".join(
                str(value)
                for value
                in radical_numbers
            )
        )

        single_radical_number = ""

        if (
            len(
                radical_numbers
            )
            == 1
        ):

            single_radical_number = (
                radical_numbers[0]
            )

        # ==================================================
        # C. MAKE ME A HANZI DICTIONARY
        # ==================================================

        dict_obj = (
            mmah_dictionary.get(
                char
            )
        )

        graphics_obj = (
            mmah_graphics.get(
                char
            )
        )

        if dict_obj:

            coverage_mmah_dictionary += 1

        if graphics_obj:

            coverage_mmah_graphics += 1

        pinyin_mmah = ""

        definition_mmah = ""

        radical_mmah = ""

        decomposition_mmah = ""

        if dict_obj:

            pinyin_mmah = clean(
                dict_obj.get(
                    "pinyin"
                )
            )

            definition_mmah = clean(
                dict_obj.get(
                    "definition"
                )
            )

            radical_mmah = clean(
                dict_obj.get(
                    "radical"
                )
            )

            decomposition_mmah = clean(
                dict_obj.get(
                    "decomposition"
                )
            )

        # ==================================================
        # D. MAKE ME A HANZI GRAPHICS
        # ==================================================

        strokes_list = None
        medians_list = None

        if graphics_obj:

            strokes_list = (
                graphics_obj.get(
                    "strokes"
                )
            )

            medians_list = (
                graphics_obj.get(
                    "medians"
                )
            )

        if isinstance(
            strokes_list,
            list,
        ):

            so_net_mmah = len(
                strokes_list
            )

        else:

            so_net_mmah = ""

        if isinstance(
            medians_list,
            list,
        ):

            so_median_mmah = len(
                medians_list
            )

        else:

            so_median_mmah = ""

        # ==================================================
        # E. DOI CHIEU SO NET
        # ==================================================

        unihan_strokes = (
            parse_total_strokes(
                strokes_raw
            )
        )

        stroke_status = ""
        stroke_proposed = ""

        need_review_stroke = (
            "KHONG"
        )

        if (
            so_net_mmah != ""
            and unihan_strokes
        ):

            if (
                int(
                    so_net_mmah
                )
                in unihan_strokes
            ):

                stroke_status = (
                    "KHOP_MMAH_UNIHAN"
                )

                stroke_proposed = (
                    so_net_mmah
                )

                stroke_ready += 1

            else:

                stroke_status = (
                    "LECH_MMAH_UNIHAN"
                )

                need_review_stroke = (
                    "CO"
                )

                stroke_review += 1

                issues.append({
                    "MaChuHanTam":
                        temp_id,

                    "KyTu":
                        char,

                    "LoaiVanDe":
                        "LECH_SO_NET",

                    "ChiTiet":
                        (
                            f"MMAH={so_net_mmah}; "
                            f"Unihan={strokes_raw}"
                        ),
                })

        elif (
            so_net_mmah != ""
        ):

            stroke_status = (
                "CHI_CO_MMAH"
            )

            stroke_proposed = (
                so_net_mmah
            )

            stroke_ready += 1

        elif unihan_strokes:

            if (
                len(
                    unihan_strokes
                )
                == 1
            ):

                stroke_status = (
                    "CHI_CO_UNIHAN"
                )

                stroke_proposed = (
                    unihan_strokes[0]
                )

                stroke_ready += 1

            else:

                stroke_status = (
                    "UNIHAN_NHIEU_GIA_TRI"
                )

                need_review_stroke = (
                    "CO"
                )

                stroke_review += 1

                issues.append({
                    "MaChuHanTam":
                        temp_id,

                    "KyTu":
                        char,

                    "LoaiVanDe":
                        "NHIEU_SO_NET_UNIHAN",

                    "ChiTiet":
                        strokes_raw,
                })

        else:

            stroke_status = (
                "THIEU_SO_NET"
            )

            need_review_stroke = (
                "CO"
            )

            stroke_review += 1

            issues.append({
                "MaChuHanTam":
                    temp_id,

                "KyTu":
                    char,

                "LoaiVanDe":
                    "THIEU_SO_NET",

                "ChiTiet":
                    (
                        "Khong co strokes MMAH "
                        "va khong co kTotalStrokes."
                    ),
            })

        # ==================================================
        # F. MAP BO THU SQL
        # ==================================================

        ma_bo_thu_sql = ""
        so_bo_thu_sql = ""

        ky_hieu_bo_thu_sql = ""
        ten_bo_thu_sql = ""
        y_nghia_bo_thu_sql = ""

        radical_status = ""

        need_review_radical = (
            "KHONG"
        )

        if (
            len(
                radical_numbers
            )
            == 1
        ):

            radical_number = (
                radical_numbers[0]
            )

            matches = (
                radical_by_number.get(
                    radical_number,
                    [],
                )
            )

            if (
                len(
                    matches
                )
                == 1
            ):

                match = (
                    matches[0]
                )

                ma_bo_thu_sql = (
                    match[
                        "MaBoThu"
                    ]
                )

                so_bo_thu_sql = (
                    match[
                        "SoBoThu"
                    ]
                )

                ky_hieu_bo_thu_sql = (
                    clean(
                        match[
                            "KyHieu"
                        ]
                    )
                )

                ten_bo_thu_sql = (
                    clean(
                        match[
                            "TenBoThu"
                        ]
                    )
                )

                y_nghia_bo_thu_sql = (
                    clean(
                        match[
                            "YNghia"
                        ]
                    )
                )

                radical_status = (
                    "MAP_SO_BO_THU_OK"
                )

                radical_ready += 1

            elif (
                len(
                    matches
                )
                == 0
            ):

                radical_status = (
                    "KHONG_TIM_THAY_BO_THU_SQL"
                )

                need_review_radical = (
                    "CO"
                )

                radical_review += 1

                issues.append({
                    "MaChuHanTam":
                        temp_id,

                    "KyTu":
                        char,

                    "LoaiVanDe":
                        "KHONG_MAP_DUOC_BO_THU",

                    "ChiTiet":
                        (
                            "SoBoThuUnicode="
                            f"{radical_number}"
                        ),
                })

            else:

                radical_status = (
                    "TRUNG_SO_BO_THU_SQL"
                )

                need_review_radical = (
                    "CO"
                )

                radical_review += 1

                issues.append({
                    "MaChuHanTam":
                        temp_id,

                    "KyTu":
                        char,

                    "LoaiVanDe":
                        "NHIEU_BO_THU_SQL",

                    "ChiTiet":
                        (
                            "SoBoThuUnicode="
                            f"{radical_number}; "
                            f"SQL matches="
                            f"{len(matches)}"
                        ),
                })

        elif (
            len(
                radical_numbers
            )
            > 1
        ):

            radical_status = (
                "NHIEU_RSUNICODE"
            )

            need_review_radical = (
                "CO"
            )

            radical_review += 1

            issues.append({
                "MaChuHanTam":
                    temp_id,

                "KyTu":
                    char,

                "LoaiVanDe":
                    "NHIEU_RSUNICODE",

                "ChiTiet":
                    (
                        f"kRSUnicode="
                        f"{rs_unicode_raw}; "
                        f"radicals="
                        f"{radical_numbers_text}"
                    ),
            })

        else:

            radical_status = (
                "THIEU_RSUNICODE"
            )

            need_review_radical = (
                "CO"
            )

            radical_review += 1

            issues.append({
                "MaChuHanTam":
                    temp_id,

                "KyTu":
                    char,

                "LoaiVanDe":
                    "THIEU_RSUNICODE",

                "ChiTiet":
                    (
                        f"kRSUnicode="
                        f"{rs_unicode_raw!r}; "
                        f"MMAH radical="
                        f"{radical_mmah!r}"
                    ),
            })

        # ==================================================
        # G. COVERAGE ISSUES
        # ==================================================

        if not dict_obj:

            issues.append({
                "MaChuHanTam":
                    temp_id,

                "KyTu":
                    char,

                "LoaiVanDe":
                    "THIEU_MMAH_DICTIONARY",

                "ChiTiet":
                    (
                        "Khong tim thay KyTu "
                        "trong dictionary.txt."
                    ),
            })

        if not graphics_obj:

            issues.append({
                "MaChuHanTam":
                    temp_id,

                "KyTu":
                    char,

                "LoaiVanDe":
                    "THIEU_MMAH_GRAPHICS",

                "ChiTiet":
                    (
                        "Khong tim thay KyTu "
                        "trong graphics.txt."
                    ),
            })

        if not has_unihan:

            issues.append({
                "MaChuHanTam":
                    temp_id,

                "KyTu":
                    char,

                "LoaiVanDe":
                    "THIEU_UNIHAN",

                "ChiTiet":
                    (
                        "Khong tim thay "
                        "kMandarin/kTotalStrokes/"
                        "kRSUnicode."
                    ),
            })

        # ==================================================
        # H. PINYIN + NGHIA
        # ==================================================
        #
        # Chua duoc chot o Buoc 19.
        #
        # Pinyin cua TU HSK4 khong tu dong
        # bang Pinyin cua KY TU.
        #
        # Vi du:
        # 阿姨 -> ayí
        # khong the tu dong gan ayí cho rieng 阿.
        #
        # ==================================================

        need_review_pinyin = (
            "CO"
        )

        need_review_meaning = (
            "CO"
        )

        # ==================================================
        # I. TINH TRANG TONG
        # ==================================================

        if (
            has_unihan
            and dict_obj
            and graphics_obj
            and need_review_radical
            == "KHONG"
            and need_review_stroke
            == "KHONG"
        ):

            data_status = (
                "DU_NGUON_CAU_TRUC"
            )

        else:

            data_status = (
                "CAN_REVIEW_NGUON"
            )

        notes = []

        if mandarin_raw:

            notes.append(
                "Co kMandarin."
            )

        if pinyin_mmah:

            notes.append(
                "Co Pinyin MakeMeAHanzi."
            )

        notes.append(
            "Chua chot Pinyin/Nghia Viet."
        )

        # ==================================================
        # J. OUTPUT ROW
        # ==================================================

        output_rows.append({

            # ----------------------------------------------
            # Buoc 18
            # ----------------------------------------------

            "MaChuHanTam":
                temp_id,

            "KyTu":
                char,

            "ThuTuXuatHienDau":
                source_row[
                    "ThuTuXuatHienDau"
                ],

            "MaTuHSKDauTien":
                source_row[
                    "MaTuHSKDauTien"
                ],

            "MaMucNoiBoDauTien":
                source_row[
                    "MaMucNoiBoDauTien"
                ],

            "SoThuTuNguonDauTien":
                source_row[
                    "SoThuTuNguonDauTien"
                ],

            "TuVungDaiDien":
                source_row[
                    "TuVungDaiDien"
                ],

            "PinyinTuDaiDien":
                source_row[
                    "PinyinTuDaiDien"
                ],

            "NghiaTuDaiDien":
                source_row[
                    "NghiaTuDaiDien"
                ],

            "SoTuHSK4ChuaKyTu":
                source_row[
                    "SoTuHSK4ChuaKyTu"
                ],

            "CacMaMucNoiBo":
                source_row[
                    "CacMaMucNoiBo"
                ],

            "CacTuHSK4ChuaKyTu":
                source_row[
                    "CacTuHSK4ChuaKyTu"
                ],

            # ----------------------------------------------
            # Unihan
            # ----------------------------------------------

            "PinyinUnihanRaw":
                mandarin_raw,

            "SoNetUnihanRaw":
                strokes_raw,

            "RSUnicodeRaw":
                rs_unicode_raw,

            "DanhSachSoBoThuUnicode":
                radical_numbers_text,

            "SoBoThuUnicode":
                single_radical_number,

            # ----------------------------------------------
            # MMAH
            # ----------------------------------------------

            "CoMakeMeAHanziDictionary":
                (
                    "CO"
                    if dict_obj
                    else "KHONG"
                ),

            "CoMakeMeAHanziGraphics":
                (
                    "CO"
                    if graphics_obj
                    else "KHONG"
                ),

            "PinyinMakeMeAHanzi":
                pinyin_mmah,

            "DefinitionEnglishMakeMeAHanzi":
                definition_mmah,

            "RadicalMakeMeAHanzi":
                radical_mmah,

            "DecompositionMakeMeAHanzi":
                decomposition_mmah,

            "SoNetMakeMeAHanzi":
                so_net_mmah,

            "SoMedianMakeMeAHanzi":
                so_median_mmah,

            # ----------------------------------------------
            # SQL radical
            # ----------------------------------------------

            "MaBoThuSQL":
                ma_bo_thu_sql,

            "SoBoThuSQL":
                so_bo_thu_sql,

            "KyHieuBoThuSQL":
                ky_hieu_bo_thu_sql,

            "TenBoThuSQL":
                ten_bo_thu_sql,

            "YNghiaBoThuSQL":
                y_nghia_bo_thu_sql,

            # ----------------------------------------------
            # Stroke
            # ----------------------------------------------

            "KiemTraSoNet":
                stroke_status,

            "SoNetDeXuat":
                stroke_proposed,

            # ----------------------------------------------
            # Source state
            # ----------------------------------------------

            "CoDuLieuUnihan":
                (
                    "CO"
                    if has_unihan
                    else "KHONG"
                ),

            "KiemTraBoThu":
                radical_status,

            "TinhTrangDuLieu":
                data_status,

            # ----------------------------------------------
            # Chua chot
            # ----------------------------------------------

            "PinyinFinal":
                "",

            "NghiaTiengVietFinal":
                "",

            "CanKiemTraPinyin":
                need_review_pinyin,

            "CanKiemTraNghia":
                need_review_meaning,

            "CanKiemTraBoThu":
                need_review_radical,

            "CanKiemTraSoNet":
                need_review_stroke,

            "GhiChu":
                " ".join(
                    notes
                ),
        })

    # ======================================================
    # [7] VALIDATE OUTPUT
    # ======================================================

    print(
        "\n[7] KIEM TRA KET QUA"
    )

    if (
        len(
            output_rows
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Output khong dung 300 dong."
        )

    output_chars = [
        row[
            "KyTu"
        ]
        for row
        in output_rows
    ]

    if (
        len(
            set(
                output_chars
            )
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Output bi trung KyTu."
        )

    output_ids = [
        row[
            "MaChuHanTam"
        ]
        for row
        in output_rows
    ]

    if (
        len(
            set(
                output_ids
            )
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Output bi trung MaChuHanTam."
        )

    print(
        "PASS: 300/300 KyTu duy nhat."
    )

    print(
        "Unihan any coverage:",
        coverage_unihan,
        "/ 300",
    )

    print(
        "  kMandarin:",
        coverage_kmandarin,
        "/ 300",
    )

    print(
        "  kTotalStrokes:",
        coverage_kstrokes,
        "/ 300",
    )

    print(
        "  kRSUnicode:",
        coverage_krs,
        "/ 300",
    )

    print(
        "MakeMeAHanzi dictionary:",
        coverage_mmah_dictionary,
        "/ 300",
    )

    print(
        "MakeMeAHanzi graphics:",
        coverage_mmah_graphics,
        "/ 300",
    )

    print(
        "SoNet san sang:",
        stroke_ready,
    )

    print(
        "SoNet can review:",
        stroke_review,
    )

    print(
        "BoThu map OK:",
        radical_ready,
    )

    print(
        "BoThu can review:",
        radical_review,
    )

    print(
        "Tong issue records:",
        len(
            issues
        ),
    )

    # ======================================================
    # [8] GHI FILE
    # ======================================================

    print(
        "\n[8] GHI FILE"
    )

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_csv(
        OUTPUT,
        output_rows,
        OUTPUT_FIELDS,
    )

    write_csv(
        ISSUES_FILE,
        issues,
        ISSUE_FIELDS,
    )

    output_hash = (
        sha256_file(
            OUTPUT
        )
    )

    issues_hash = (
        sha256_file(
            ISSUES_FILE
        )
    )

    # ======================================================
    # [9] SUMMARY
    # ======================================================

    status_counts = defaultdict(
        int
    )

    for row in output_rows:

        status_counts[
            row[
                "TinhTrangDuLieu"
            ]
        ] += 1

    issue_counts = defaultdict(
        int
    )

    for issue in issues:

        issue_counts[
            issue[
                "LoaiVanDe"
            ]
        ] += 1

    summary = {

        "status":
            "PASS",

        "buoc":
            19,

        "tong_chu_moi_hsk4":
            len(
                output_rows
            ),

        # ----------------------------------------------
        # Source paths
        # ----------------------------------------------

        "unihan_zip":
            str(
                unihan_zip
            ),

        "unihan_members_da_doc":
            unihan_members,

        "cjk_radicals":
            (
                str(
                    cjk_radicals_file
                )
                if cjk_radicals_file
                else None
            ),

        "makemeahanzi_dictionary":
            str(
                dictionary_file
            ),

        "makemeahanzi_graphics":
            str(
                graphics_file
            ),

        # ----------------------------------------------
        # Coverage
        # ----------------------------------------------

        "unihan_any_coverage":
            coverage_unihan,

        "unihan_kMandarin_coverage":
            coverage_kmandarin,

        "unihan_kTotalStrokes_coverage":
            coverage_kstrokes,

        "unihan_kRSUnicode_coverage":
            coverage_krs,

        "makemeahanzi_dictionary_coverage":
            coverage_mmah_dictionary,

        "makemeahanzi_graphics_coverage":
            coverage_mmah_graphics,

        # ----------------------------------------------
        # Review
        # ----------------------------------------------

        "sonet_san_sang":
            stroke_ready,

        "sonet_can_review":
            stroke_review,

        "bothu_map_ok":
            radical_ready,

        "bothu_can_review":
            radical_review,

        "tinh_trang_du_lieu":
            dict(
                status_counts
            ),

        "issue_counts":
            dict(
                issue_counts
            ),

        # ----------------------------------------------
        # Hash
        # ----------------------------------------------

        "source_sha256":
            source_hash,

        "output_sha256":
            output_hash,

        "issues_sha256":
            issues_hash,

        # ----------------------------------------------
        # Chua lam
        # ----------------------------------------------

        "da_chot_pinyin":
            False,

        "da_chot_nghia_viet":
            False,

        "da_gan_bai_hoc":
            False,

        "da_ghi_sql":
            False,
    }

    if SUMMARY_FILE.exists():

        raise FileExistsError(
            f"Summary da ton tai:\n"
            f"{SUMMARY_FILE}"
        )

    SUMMARY_FILE.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # ======================================================
    # [10] PREVIEW REVIEW
    # ======================================================

    print(
        "\n[9] PREVIEW CAC MUC CAN REVIEW"
    )

    review_rows = [
        row
        for row in output_rows
        if (
            row[
                "TinhTrangDuLieu"
            ]
            == "CAN_REVIEW_NGUON"
        )
    ]

    print(
        "So chu can review nguon:",
        len(
            review_rows
        ),
    )

    for row in review_rows[
        :30
    ]:

        print(
            row[
                "MaChuHanTam"
            ],
            "|",
            row[
                "KyTu"
            ],
            "| stroke:",
            row[
                "KiemTraSoNet"
            ],
            "| radical:",
            row[
                "KiemTraBoThu"
            ],
        )

    # ======================================================
    # [11] KET QUA CUOI
    # ======================================================

    print(
        "\n"
        + "=" * 80
    )

    print(
        "ENRICH NGUON CHU HAN HSK4 HOAN THANH"
    )

    print(
        "=" * 80
    )

    print(
        "Tong chu moi:",
        len(
            output_rows
        ),
        "/ 300",
    )

    print(
        "Unihan any:",
        coverage_unihan,
        "/ 300",
    )

    print(
        "kMandarin:",
        coverage_kmandarin,
        "/ 300",
    )

    print(
        "kTotalStrokes:",
        coverage_kstrokes,
        "/ 300",
    )

    print(
        "kRSUnicode:",
        coverage_krs,
        "/ 300",
    )

    print(
        "MakeMeAHanzi dictionary:",
        coverage_mmah_dictionary,
        "/ 300",
    )

    print(
        "MakeMeAHanzi graphics:",
        coverage_mmah_graphics,
        "/ 300",
    )

    print(
        "BoThu map OK:",
        radical_ready,
    )

    print(
        "BoThu can review:",
        radical_review,
    )

    print(
        "SoNet san sang:",
        stroke_ready,
    )

    print(
        "SoNet can review:",
        stroke_review,
    )

    print(
        "\nOUTPUT:"
    )

    print(
        " ",
        OUTPUT,
    )

    print(
        "SHA256:"
    )

    print(
        output_hash
    )

    print(
        "\nISSUES:"
    )

    print(
        " ",
        ISSUES_FILE,
    )

    print(
        "SHA256:"
    )

    print(
        issues_hash
    )

    print(
        "\nSUMMARY:"
    )

    print(
        " ",
        SUMMARY_FILE,
    )

    print(
        "\nCHUA CHOT PINYIN."
    )

    print(
        "CHUA CHOT NGHIA TIENG VIET."
    )

    print(
        "CHUA GAN BAI HOC."
    )

    print(
        "KHONG THAY DOI SQL."
    )

    print(
        "=" * 80
    )


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