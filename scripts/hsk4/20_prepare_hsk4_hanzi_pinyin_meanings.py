# -*- coding: utf-8 -*-
"""
BUOC 20 - DOI CHIEU PINYIN + NGHIA VIET 300 CHU HAN HSK4

INPUT:
    hanzi_hsk4_300_enriched_sources.csv

Nguon doi chieu:
1. Unicode Unihan                -> Pinyin tham khao
2. Make Me a Hanzi              -> Pinyin tham khao
3. GF0025 TuVungHSKChuan        -> cach doc/nghia khi KyTu la muc tu don
4. CC-CEDICT                    -> cach doc tham khao
5. CVDICT                       -> nghia Viet de xuat

NGUYEN TAC:
- KHONG lay Pinyin cua ca TU ghep de gan truc tiep cho tung KyTu.
- Chi uu tien muc tu DON co ChuHan == KyTu.
- Khong tu bia nghia neu khong co nguon.
- Chu da am / nhieu nghia / nguon mau thuan -> CAN_REVIEW.
- Khong ghi SQL.
"""

import csv
import hashlib
import json
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


DATA_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)


SOURCE = (
    DATA_DIR
    / "hanzi_hsk4_300_enriched_sources.csv"
)


OUTPUT = (
    DATA_DIR
    / "hanzi_hsk4_300_pinyin_meaning_draft.csv"
)


REVIEW_FILE = (
    DATA_DIR
    / "hanzi_hsk4_300_pinyin_meaning_review.csv"
)


SUMMARY_FILE = (
    DATA_DIR
    / "hanzi_hsk4_300_pinyin_meaning_summary.json"
)


EXPECTED_SOURCE_SHA256 = (
    "5f85c0e6c74693e7a411e5e8531cad824ff2742a70e2e4933a089847ada45c8d"
)

EXPECTED_TOTAL = 300


# ==========================================================
# 2. OUTPUT FIELDS
# ==========================================================

OUTPUT_FIELDS = [

    "MaChuHanTam",
    "KyTu",

    # ------------------------------------------------------
    # Ngu canh HSK4
    # ------------------------------------------------------

    "TuVungDaiDien",
    "PinyinTuDaiDien",
    "NghiaTuDaiDien",
    "CacTuHSK4ChuaKyTu",

    # ------------------------------------------------------
    # Nguon cau truc tu Buoc 19
    # ------------------------------------------------------

    "PinyinUnihanRaw",
    "PinyinMakeMeAHanzi",

    "SoNetUnihanRaw",
    "SoNetMakeMeAHanzi",
    "SoNetDeXuat",

    "MaBoThuSQL",
    "SoBoThuSQL",
    "KyHieuBoThuSQL",
    "TenBoThuSQL",

    "KiemTraSoNet",
    "KiemTraBoThu",

    # ------------------------------------------------------
    # GF0025 muc tu don
    # ------------------------------------------------------

    "SoMucGFDon",
    "PinyinGFDon",
    "NghiaGFDon",
    "CapDoGFDon",

    # ------------------------------------------------------
    # CC-CEDICT
    # ------------------------------------------------------

    "SoMucCEDICT",
    "CacCachDocCEDICT",
    "NghiaAnhCEDICT",

    # ------------------------------------------------------
    # CVDICT
    # ------------------------------------------------------

    "SoMucCVDICT",
    "CacCachDocCVDICT",
    "UngVienNghiaCVDICT",

    # ------------------------------------------------------
    # Pinyin
    # ------------------------------------------------------

    "ReadingsUnihanNormalized",
    "ReadingsMMAHNormalized",
    "ReadingsGFNormalized",
    "ReadingsCEDICTNormalized",

    "PinyinDeXuat",
    "NguonPinyinDeXuat",
    "TrangThaiPinyin",

    # ------------------------------------------------------
    # Nghia
    # ------------------------------------------------------

    "NghiaTiengVietDeXuat",
    "NguonNghiaDeXuat",
    "TrangThaiNghia",

    # ------------------------------------------------------
    # Tong review
    # ------------------------------------------------------

    "CanKiemTraPinyin",
    "CanKiemTraNghia",
    "CanKiemTraCauTruc",

    "TrangThaiKiemDuyet",
    "LyDoCanReview",
]


REVIEW_FIELDS = OUTPUT_FIELDS


# ==========================================================
# 3. HAM CO BAN
# ==========================================================

def clean(value):

    if value is None:
        return ""

    if isinstance(value, list):

        return " | ".join(
            clean(item)
            for item in value
            if clean(item)
        )

    return str(value).strip()


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


def read_csv(path):

    if not path.is_file():

        raise FileNotFoundError(
            f"Khong tim thay:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        fields = (
            reader.fieldnames
            or []
        )

        rows = list(reader)

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

        writer.writerows(rows)


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


def join_unique(
    values,
    separator=" | ",
):

    result = []

    seen = set()

    for value in values:

        value = clean(value)

        if not value:
            continue

        if value in seen:
            continue

        seen.add(value)

        result.append(value)

    return separator.join(result)


# ==========================================================
# 4. PINYIN NORMALIZATION
# ==========================================================

TONE_CHAR_MAP = {

    "ā": ("a", "1"),
    "á": ("a", "2"),
    "ǎ": ("a", "3"),
    "à": ("a", "4"),

    "ē": ("e", "1"),
    "é": ("e", "2"),
    "ě": ("e", "3"),
    "è": ("e", "4"),

    "ī": ("i", "1"),
    "í": ("i", "2"),
    "ǐ": ("i", "3"),
    "ì": ("i", "4"),

    "ō": ("o", "1"),
    "ó": ("o", "2"),
    "ǒ": ("o", "3"),
    "ò": ("o", "4"),

    "ū": ("u", "1"),
    "ú": ("u", "2"),
    "ǔ": ("u", "3"),
    "ù": ("u", "4"),

    "ǖ": ("v", "1"),
    "ǘ": ("v", "2"),
    "ǚ": ("v", "3"),
    "ǜ": ("v", "4"),

    "ü": ("v", ""),

    "ń": ("n", "2"),
    "ň": ("n", "3"),
    "ǹ": ("n", "4"),

    "ḿ": ("m", "2"),
}


def normalize_pinyin_syllable(value):
    """
    Chuyen:
        ā    -> a1
        ǎi   -> ai3
        shì  -> shi4
        shi4 -> shi4
        lü4  -> lv4

    Neu khong co tone:
        shi -> shi
    """

    text = clean(value).lower()

    if not text:
        return ""

    text = (
        text
        .replace("u:", "v")
        .replace("ü", "v")
    )

    # Loai dau nhay Pinyin.
    text = (
        text
        .replace("'", "")
        .replace("’", "")
    )

    # Neu da co tone number.
    match = re.fullmatch(
        r"([a-zv]+)([1-5])",
        text,
    )

    if match:

        return (
            match.group(1)
            + match.group(2)
        )

    tone = ""

    output = []

    for char in text:

        lower = char.lower()

        if lower in TONE_CHAR_MAP:

            base, found_tone = (
                TONE_CHAR_MAP[
                    lower
                ]
            )

            output.append(base)

            if found_tone:
                tone = found_tone

            continue

        # Unicode combining fallback.
        decomposed = unicodedata.normalize(
            "NFD",
            lower,
        )

        base_chars = [
            item
            for item in decomposed
            if unicodedata.category(item)
            != "Mn"
        ]

        base = "".join(base_chars)

        if (
            base
            and re.fullmatch(
                r"[a-zv]+",
                base,
            )
        ):

            output.append(base)

        elif lower.isalpha():

            output.append(lower)

    base_text = "".join(output)

    base_text = re.sub(
        r"[^a-zv]",
        "",
        base_text,
    )

    if not base_text:
        return ""

    return (
        base_text
        + tone
    )


def extract_pinyin_readings(raw):
    """
    Tach cac cach doc.

    Vi du:
        'shí | shén' -> {'shi2', 'shen2'}
        'shi2/shen2' -> {'shi2', 'shen2'}
    """

    text = clean(raw)

    if not text:
        return set()

    pieces = re.split(
        r"[\s,/;|、]+",
        text,
    )

    result = set()

    for piece in pieces:

        piece = clean(piece)

        if not piece:
            continue

        normalized = (
            normalize_pinyin_syllable(
                piece
            )
        )

        if normalized:

            result.add(normalized)

    return result


def readings_to_text(values):

    return ",".join(
        sorted(values)
    )


def choose_display_pinyin(
    normalized_reading,
    raw_sources,
):
    """
    Tim cach viet co dau thanh de hien thi,
    nhung khong tu tao Pinyin moi.

    Uu tien raw source nao map dung reading.
    """

    if not normalized_reading:
        return ""

    for raw in raw_sources:

        text = clean(raw)

        if not text:
            continue

        pieces = re.split(
            r"[\s,/;|、]+",
            text,
        )

        for piece in pieces:

            if (
                normalize_pinyin_syllable(
                    piece
                )
                == normalized_reading
            ):

                return clean(piece)

    # Khong tu chuyen number -> tone mark.
    # Neu khong co display source thi de reading number.
    return normalized_reading


# ==========================================================
# 5. MEANING HELPERS
# ==========================================================

def meaning_candidates_from_cvdict(rows):

    values = []

    for row in rows:

        # CVDICT co the luu nghia Viet o
        # NghiaTiengViet hoac NghiaGoc tuy pipeline import.
        meaning_vi = clean(
            row.get(
                "NghiaTiengViet"
            )
        )

        meaning_original = clean(
            row.get(
                "NghiaGoc"
            )
        )

        language = clean(
            row.get(
                "NgonNguNghiaGoc"
            )
        ).lower()

        if meaning_vi:

            values.append(
                meaning_vi
            )

        elif (
            language == "vi"
            and meaning_original
        ):

            values.append(
                meaning_original
            )

        elif meaning_original:

            # CVDICT la nguon Trung-Viet cua project.
            # Van chi de xuat, khong tu coi da duyet.
            values.append(
                meaning_original
            )

    return list(
        dict.fromkeys(
            values
        )
    )


def meaning_candidates_from_gf(rows):

    values = []

    for row in rows:

        meaning = clean(
            row.get(
                "NghiaTiengVietThamChieu"
            )
        )

        if meaning:

            values.append(
                meaning
            )

    return list(
        dict.fromkeys(
            values
        )
    )


# ==========================================================
# 6. MAIN
# ==========================================================

def main():

    print("=" * 80)

    print(
        "BUOC 20 - DOI CHIEU PINYIN + "
        "NGHIA VIET 300 CHU HAN HSK4"
    )

    print("=" * 80)

    print(
        "CHI SELECT SQL + TAO CSV"
    )

    print(
        "KHONG INSERT / UPDATE / DELETE"
    )

    # ======================================================
    # [1] LOCK INPUT BUOC 19
    # ======================================================

    print(
        "\n[1] KIEM TRA INPUT BUOC 19"
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
            "File Buoc 19 da thay doi."
        )

    fields, source_rows = (
        read_csv(
            SOURCE
        )
    )

    required_fields = {

        "MaChuHanTam",
        "KyTu",

        "TuVungDaiDien",
        "PinyinTuDaiDien",
        "NghiaTuDaiDien",
        "CacTuHSK4ChuaKyTu",

        "PinyinUnihanRaw",
        "PinyinMakeMeAHanzi",

        "SoNetUnihanRaw",
        "SoNetMakeMeAHanzi",
        "SoNetDeXuat",

        "MaBoThuSQL",
        "SoBoThuSQL",
        "KyHieuBoThuSQL",
        "TenBoThuSQL",

        "KiemTraSoNet",
        "KiemTraBoThu",
    }

    missing = (
        required_fields
        - set(fields)
    )

    if missing:

        raise RuntimeError(
            "Input thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    if (
        len(source_rows)
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Input khong dung 300 dong."
        )

    chars = [
        clean(
            row[
                "KyTu"
            ]
        )
        for row in source_rows
    ]

    if (
        len(
            set(chars)
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Input bi trung KyTu."
        )

    print(
        "PASS: 300/300 KyTu."
    )

    # ======================================================
    # [2] DOC NGUON SQL
    # ======================================================

    print(
        "\n[2] XAC DINH MaNguon THUC TE"
    )

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            source_db_rows = fetch_all(
                cursor,
                """
                SELECT
                    MaNguon,
                    Ten,
                    LienKetNguon,
                    GiayPhep
                FROM dbo.NguonDuLieu
                ORDER BY MaNguon
                """
            )

            source_by_name = {
                clean(
                    row[
                        "Ten"
                    ]
                ).casefold():
                    row
                for row in source_db_rows
            }

            required_sources = [
                "CC-CEDICT",
                "CVDICT",
                "GF0025-2021 - Tu vung HSK",
            ]

            resolved_sources = {}

            for source_name in required_sources:

                row = source_by_name.get(
                    source_name.casefold()
                )

                if row is None:

                    raise RuntimeError(
                        "Khong tim thay NguonDuLieu: "
                        f"{source_name}"
                    )

                resolved_sources[
                    source_name
                ] = row

                print(
                    f"  {source_name}: "
                    f"MaNguon={row['MaNguon']}"
                )

            ma_nguon_cedict = int(
                resolved_sources[
                    "CC-CEDICT"
                ][
                    "MaNguon"
                ]
            )

            ma_nguon_cvdict = int(
                resolved_sources[
                    "CVDICT"
                ][
                    "MaNguon"
                ]
            )

            ma_nguon_gf = int(
                resolved_sources[
                    "GF0025-2021 - Tu vung HSK"
                ][
                    "MaNguon"
                ]
            )

            # ==================================================
            # [3] GF0025 MUC TU DON
            # ==================================================

            print(
                "\n[3] DOC GF0025 MUC TU DON"
            )

            placeholders = ",".join(
                "?"
                for _ in chars
            )

            gf_rows = fetch_all(
                cursor,
                f"""
                SELECT
                    MaTuHSK,
                    MaMucNoiBo,
                    MaCapDo,
                    ChuHan,
                    PhienAm,
                    NghiaTiengVietThamChieu,
                    MaNguonDanhSach,
                    MaNguonNghiaViet

                FROM dbo.TuVungHSKChuan

                WHERE
                    MaCapDo BETWEEN 1 AND 4
                    AND ChuHan IN ({placeholders})

                ORDER BY
                    MaCapDo,
                    SoThuTuNguon,
                    MaTuHSK
                """,
                *chars,
            )

            gf_by_char = defaultdict(
                list
            )

            for row in gf_rows:

                char = clean(
                    row[
                        "ChuHan"
                    ]
                )

                # KyTu phai chinh xac la 1 character.
                if (
                    char
                    in set(chars)
                ):

                    gf_by_char[
                        char
                    ].append(
                        row
                    )

            print(
                "KyTu co muc GF don:",
                len(
                    gf_by_char
                ),
                "/ 300",
            )

            # ==================================================
            # [4] MucTuDien - CVDICT / CC-CEDICT
            # ==================================================

            print(
                "\n[4] DOC MucTuDien "
                "CVDICT + CC-CEDICT"
            )

            dictionary_rows = fetch_all(
                cursor,
                f"""
                SELECT
                    MaMucTu,
                    MaNguon,
                    MaNguonBenNgoai,
                    ChuHan,
                    ChuPhonThe,
                    PhienAm,
                    NghiaGoc,
                    NgonNguNghiaGoc,
                    NghiaTiengViet,
                    NghiaVietDaDuyet

                FROM dbo.MucTuDien

                WHERE
                    MaNguon IN (?, ?)
                    AND (
                        ChuHan IN ({placeholders})
                        OR ChuPhonThe IN ({placeholders})
                    )

                ORDER BY
                    MaNguon,
                    ChuHan,
                    PhienAm,
                    MaMucTu
                """,
                ma_nguon_cedict,
                ma_nguon_cvdict,
                *chars,
                *chars,
            )

    cvdict_by_char = defaultdict(
        list
    )

    cedict_by_char = defaultdict(
        list
    )

    for row in dictionary_rows:

        possible_chars = {
            clean(
                row.get(
                    "ChuHan"
                )
            ),
            clean(
                row.get(
                    "ChuPhonThe"
                )
            ),
        }

        matched_chars = (
            possible_chars
            & set(chars)
        )

        for char in matched_chars:

            if (
                int(
                    row[
                        "MaNguon"
                    ]
                )
                == ma_nguon_cvdict
            ):

                cvdict_by_char[
                    char
                ].append(
                    row
                )

            elif (
                int(
                    row[
                        "MaNguon"
                    ]
                )
                == ma_nguon_cedict
            ):

                cedict_by_char[
                    char
                ].append(
                    row
                )

    print(
        "CVDICT exact-char coverage:",
        len(
            cvdict_by_char
        ),
        "/ 300",
    )

    print(
        "CC-CEDICT exact-char coverage:",
        len(
            cedict_by_char
        ),
        "/ 300",
    )

    # ======================================================
    # [5] BUILD 300 ROWS
    # ======================================================

    print(
        "\n[5] DOI CHIEU 300 CHU"
    )

    output_rows = []

    review_rows = []

    pinyin_ready = 0
    pinyin_review = 0

    meaning_ready = 0
    meaning_review = 0

    structure_review = 0

    for source_row in source_rows:

        char = clean(
            source_row[
                "KyTu"
            ]
        )

        # ==================================================
        # A. NGUON PINYIN
        # ==================================================

        unihan_raw = clean(
            source_row[
                "PinyinUnihanRaw"
            ]
        )

        mmah_raw = clean(
            source_row[
                "PinyinMakeMeAHanzi"
            ]
        )

        unihan_readings = (
            extract_pinyin_readings(
                unihan_raw
            )
        )

        mmah_readings = (
            extract_pinyin_readings(
                mmah_raw
            )
        )

        # --------------------------------------------------
        # GF exact single-character rows
        # --------------------------------------------------

        gf_char_rows = (
            gf_by_char.get(
                char,
                []
            )
        )

        gf_pinyin_raw_values = [
            clean(
                row.get(
                    "PhienAm"
                )
            )
            for row in gf_char_rows
            if clean(
                row.get(
                    "PhienAm"
                )
            )
        ]

        gf_readings = set()

        for value in gf_pinyin_raw_values:

            gf_readings.update(
                extract_pinyin_readings(
                    value
                )
            )

        gf_meanings = (
            meaning_candidates_from_gf(
                gf_char_rows
            )
        )

        gf_levels = join_unique(
            [
                f"HSK{row['MaCapDo']}"
                for row
                in gf_char_rows
            ],
            ",",
        )

        # --------------------------------------------------
        # CC-CEDICT
        # --------------------------------------------------

        cedict_rows = (
            cedict_by_char.get(
                char,
                []
            )
        )

        cedict_pinyin_values = [
            clean(
                row.get(
                    "PhienAm"
                )
            )
            for row in cedict_rows
            if clean(
                row.get(
                    "PhienAm"
                )
            )
        ]

        cedict_readings = set()

        for value in cedict_pinyin_values:

            cedict_readings.update(
                extract_pinyin_readings(
                    value
                )
            )

        cedict_meanings_en = (
            join_unique(
                [
                    row.get(
                        "NghiaGoc"
                    )
                    for row in cedict_rows
                ]
            )
        )

        # --------------------------------------------------
        # CVDICT
        # --------------------------------------------------

        cvdict_rows = (
            cvdict_by_char.get(
                char,
                []
            )
        )

        cvdict_pinyin_values = [
            clean(
                row.get(
                    "PhienAm"
                )
            )
            for row in cvdict_rows
            if clean(
                row.get(
                    "PhienAm"
                )
            )
        ]

        cvdict_readings = set()

        for value in cvdict_pinyin_values:

            cvdict_readings.update(
                extract_pinyin_readings(
                    value
                )
            )

        cvdict_meanings = (
            meaning_candidates_from_cvdict(
                cvdict_rows
            )
        )

        # ==================================================
        # B. CHON PINYIN DE XUAT
        # ==================================================

        pinyin_proposed = ""

        pinyin_source = ""

        pinyin_status = ""

        need_review_pinyin = "KHONG"

        selected_reading = ""

        # --------------------------------------------------
        # Uu tien 1:
        # GF co dung 1 reading cho muc tu don.
        # --------------------------------------------------

        if (
            len(
                gf_readings
            )
            == 1
        ):

            selected_reading = next(
                iter(
                    gf_readings
                )
            )

            pinyin_proposed = (
                choose_display_pinyin(
                    selected_reading,
                    (
                        gf_pinyin_raw_values
                        + [mmah_raw]
                        + [unihan_raw]
                        + cedict_pinyin_values
                    ),
                )
            )

            pinyin_source = (
                "GF0025_MUC_TU_DON"
            )

            # Neu nguon cau truc co reading
            # nhung khong chua reading GF -> review.
            conflicts = []

            if (
                unihan_readings
                and selected_reading
                not in unihan_readings
            ):

                conflicts.append(
                    "UNIHAN"
                )

            if (
                mmah_readings
                and selected_reading
                not in mmah_readings
            ):

                conflicts.append(
                    "MMAH"
                )

            if (
                cedict_readings
                and selected_reading
                not in cedict_readings
            ):

                conflicts.append(
                    "CEDICT"
                )

            if conflicts:

                pinyin_status = (
                    "GF_CO_1_NHUNG_NGUON_KHAC_LECH"
                )

                need_review_pinyin = "CO"

            else:

                pinyin_status = (
                    "GF_DON_KHOP_NGUON"
                )

        # --------------------------------------------------
        # GF co nhieu reading -> khong tu chot.
        # --------------------------------------------------

        elif (
            len(
                gf_readings
            )
            > 1
        ):

            pinyin_status = (
                "GF_DON_NHIEU_CACH_DOC"
            )

            need_review_pinyin = "CO"

        else:

            # ----------------------------------------------
            # Khong co GF muc don.
            # Tim giao cua Unihan + MMAH.
            # ----------------------------------------------

            structural_sets = [
                values
                for values in [
                    unihan_readings,
                    mmah_readings,
                ]
                if values
            ]

            common = set()

            if structural_sets:

                common = set(
                    structural_sets[0]
                )

                for values in (
                    structural_sets[1:]
                ):

                    common &= values

            # Neu co dung 1 reading giao nhau.
            if (
                len(common)
                == 1
            ):

                selected_reading = next(
                    iter(common)
                )

                # Neu CEDICT co du lieu,
                # reading nay phai ton tai trong CEDICT.
                if (
                    cedict_readings
                    and selected_reading
                    not in cedict_readings
                ):

                    pinyin_proposed = (
                        choose_display_pinyin(
                            selected_reading,
                            [
                                mmah_raw,
                                unihan_raw,
                            ],
                        )
                    )

                    pinyin_source = (
                        "UNIHAN_MMAH"
                    )

                    pinyin_status = (
                        "UNIHAN_MMAH_KHOP_NHUNG_CEDICT_LECH"
                    )

                    need_review_pinyin = (
                        "CO"
                    )

                else:

                    pinyin_proposed = (
                        choose_display_pinyin(
                            selected_reading,
                            [
                                mmah_raw,
                                unihan_raw,
                            ]
                            + cedict_pinyin_values,
                        )
                    )

                    pinyin_source = (
                        "UNIHAN_MMAH"
                    )

                    pinyin_status = (
                        "UNIHAN_MMAH_KHOP"
                    )

            # ----------------------------------------------
            # Neu Unihan/MMAH khong giao,
            # thu CEDICT chi khi CEDICT chi co 1 reading
            # VA reading nam trong mot nguon cau truc.
            # ----------------------------------------------

            elif (
                len(
                    cedict_readings
                )
                == 1
            ):

                only_cedict = next(
                    iter(
                        cedict_readings
                    )
                )

                if (
                    only_cedict
                    in unihan_readings
                    or only_cedict
                    in mmah_readings
                ):

                    selected_reading = (
                        only_cedict
                    )

                    pinyin_proposed = (
                        choose_display_pinyin(
                            selected_reading,
                            cedict_pinyin_values
                            + [mmah_raw]
                            + [unihan_raw],
                        )
                    )

                    pinyin_source = (
                        "CEDICT_KHOP_1_NGUON_CAU_TRUC"
                    )

                    pinyin_status = (
                        "DE_XUAT_CO_DOI_CHIEU"
                    )

                else:

                    pinyin_status = (
                        "NGUON_PINYIN_MAU_THUAN"
                    )

                    need_review_pinyin = (
                        "CO"
                    )

            else:

                pinyin_status = (
                    "CHUA_CHOT_DUOC_PINYIN"
                )

                need_review_pinyin = (
                    "CO"
                )

        if (
            pinyin_proposed
            and need_review_pinyin
            == "KHONG"
        ):

            pinyin_ready += 1

        else:

            pinyin_review += 1

        # ==================================================
        # C. CHON NGHIA VIET DE XUAT
        # ==================================================

        meaning_proposed = ""

        meaning_source = ""

        meaning_status = ""

        need_review_meaning = (
            "KHONG"
        )

        # --------------------------------------------------
        # Uu tien CVDICT exact KyTu.
        # --------------------------------------------------

        if (
            len(
                cvdict_meanings
            )
            == 1
        ):

            meaning_proposed = (
                cvdict_meanings[0]
            )

            meaning_source = (
                "CVDICT_EXACT_CHAR"
            )

            meaning_status = (
                "CVDICT_1_UNG_VIEN"
            )

        elif (
            len(
                cvdict_meanings
            )
            > 1
        ):

            meaning_status = (
                "CVDICT_NHIEU_NGHIA"
            )

            need_review_meaning = (
                "CO"
            )

        # --------------------------------------------------
        # Neu DB khong co exact CVDICT,
        # dung nghia GF muc tu don chi khi
        # co dung mot nghia tham chieu.
        # --------------------------------------------------

        elif (
            len(
                gf_meanings
            )
            == 1
        ):

            meaning_proposed = (
                gf_meanings[0]
            )

            meaning_source = (
                "GF0025_MUC_TU_DON_NGHIA_THAM_CHIEU"
            )

            meaning_status = (
                "GF_DON_1_UNG_VIEN"
            )

        elif (
            len(
                gf_meanings
            )
            > 1
        ):

            meaning_status = (
                "GF_DON_NHIEU_NGHIA"
            )

            need_review_meaning = (
                "CO"
            )

        else:

            meaning_status = (
                "KHONG_CO_NGHIA_EXACT_CHAR"
            )

            need_review_meaning = (
                "CO"
            )

        if (
            meaning_proposed
            and need_review_meaning
            == "KHONG"
        ):

            meaning_ready += 1

        else:

            meaning_review += 1

        # ==================================================
        # D. CAU TRUC - GIU 28 ISSUE BUOC 19
        # ==================================================

        structure_reasons = []

        if (
            clean(
                source_row[
                    "KiemTraSoNet"
                ]
            )
            == "LECH_MMAH_UNIHAN"
        ):

            structure_reasons.append(
                "LECH_SO_NET"
            )

        if (
            clean(
                source_row[
                    "KiemTraBoThu"
                ]
            )
            != "MAP_SO_BO_THU_OK"
        ):

            structure_reasons.append(
                "CAN_REVIEW_BO_THU"
            )

        need_review_structure = (
            "CO"
            if structure_reasons
            else "KHONG"
        )

        if (
            need_review_structure
            == "CO"
        ):

            structure_review += 1

        # ==================================================
        # E. TONG TRANG THAI
        # ==================================================

        reasons = []

        if (
            need_review_pinyin
            == "CO"
        ):

            reasons.append(
                "PINYIN:"
                + pinyin_status
            )

        if (
            need_review_meaning
            == "CO"
        ):

            reasons.append(
                "NGHIA:"
                + meaning_status
            )

        reasons.extend(
            structure_reasons
        )

        if reasons:

            overall_status = (
                "CAN_REVIEW"
            )

        else:

            overall_status = (
                "SAN_SANG_KIEM_DUYET_CUOI"
            )

        # ==================================================
        # F. OUTPUT
        # ==================================================

        output_row = {

            "MaChuHanTam":
                source_row[
                    "MaChuHanTam"
                ],

            "KyTu":
                char,

            # ----------------------------------------------
            # Context
            # ----------------------------------------------

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

            "CacTuHSK4ChuaKyTu":
                source_row[
                    "CacTuHSK4ChuaKyTu"
                ],

            # ----------------------------------------------
            # Structural sources
            # ----------------------------------------------

            "PinyinUnihanRaw":
                unihan_raw,

            "PinyinMakeMeAHanzi":
                mmah_raw,

            "SoNetUnihanRaw":
                source_row[
                    "SoNetUnihanRaw"
                ],

            "SoNetMakeMeAHanzi":
                source_row[
                    "SoNetMakeMeAHanzi"
                ],

            "SoNetDeXuat":
                source_row[
                    "SoNetDeXuat"
                ],

            "MaBoThuSQL":
                source_row[
                    "MaBoThuSQL"
                ],

            "SoBoThuSQL":
                source_row[
                    "SoBoThuSQL"
                ],

            "KyHieuBoThuSQL":
                source_row[
                    "KyHieuBoThuSQL"
                ],

            "TenBoThuSQL":
                source_row[
                    "TenBoThuSQL"
                ],

            "KiemTraSoNet":
                source_row[
                    "KiemTraSoNet"
                ],

            "KiemTraBoThu":
                source_row[
                    "KiemTraBoThu"
                ],

            # ----------------------------------------------
            # GF
            # ----------------------------------------------

            "SoMucGFDon":
                len(
                    gf_char_rows
                ),

            "PinyinGFDon":
                join_unique(
                    gf_pinyin_raw_values
                ),

            "NghiaGFDon":
                join_unique(
                    gf_meanings
                ),

            "CapDoGFDon":
                gf_levels,

            # ----------------------------------------------
            # CEDICT
            # ----------------------------------------------

            "SoMucCEDICT":
                len(
                    cedict_rows
                ),

            "CacCachDocCEDICT":
                join_unique(
                    cedict_pinyin_values
                ),

            "NghiaAnhCEDICT":
                cedict_meanings_en,

            # ----------------------------------------------
            # CVDICT
            # ----------------------------------------------

            "SoMucCVDICT":
                len(
                    cvdict_rows
                ),

            "CacCachDocCVDICT":
                join_unique(
                    cvdict_pinyin_values
                ),

            "UngVienNghiaCVDICT":
                join_unique(
                    cvdict_meanings
                ),

            # ----------------------------------------------
            # Normalized readings
            # ----------------------------------------------

            "ReadingsUnihanNormalized":
                readings_to_text(
                    unihan_readings
                ),

            "ReadingsMMAHNormalized":
                readings_to_text(
                    mmah_readings
                ),

            "ReadingsGFNormalized":
                readings_to_text(
                    gf_readings
                ),

            "ReadingsCEDICTNormalized":
                readings_to_text(
                    cedict_readings
                ),

            # ----------------------------------------------
            # Proposed Pinyin
            # ----------------------------------------------

            "PinyinDeXuat":
                pinyin_proposed,

            "NguonPinyinDeXuat":
                pinyin_source,

            "TrangThaiPinyin":
                pinyin_status,

            # ----------------------------------------------
            # Proposed meaning
            # ----------------------------------------------

            "NghiaTiengVietDeXuat":
                meaning_proposed,

            "NguonNghiaDeXuat":
                meaning_source,

            "TrangThaiNghia":
                meaning_status,

            # ----------------------------------------------
            # Review
            # ----------------------------------------------

            "CanKiemTraPinyin":
                need_review_pinyin,

            "CanKiemTraNghia":
                need_review_meaning,

            "CanKiemTraCauTruc":
                need_review_structure,

            "TrangThaiKiemDuyet":
                overall_status,

            "LyDoCanReview":
                " | ".join(
                    reasons
                ),
        }

        output_rows.append(
            output_row
        )

        if (
            overall_status
            == "CAN_REVIEW"
        ):

            review_rows.append(
                output_row
            )

    # ======================================================
    # [6] VALIDATE
    # ======================================================

    print(
        "\n[6] KIEM TRA OUTPUT"
    )

    if (
        len(
            output_rows
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Output khong dung 300."
        )

    if (
        len({
            row[
                "KyTu"
            ]
            for row
            in output_rows
        })
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Output bi trung KyTu."
        )

    if (
        pinyin_ready
        + pinyin_review
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Thong ke Pinyin khong khop."
        )

    if (
        meaning_ready
        + meaning_review
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Thong ke nghia khong khop."
        )

    print(
        "PASS: 300/300 KyTu."
    )

    print(
        "Pinyin de xuat san sang:",
        pinyin_ready,
    )

    print(
        "Pinyin can review:",
        pinyin_review,
    )

    print(
        "Nghia de xuat san sang:",
        meaning_ready,
    )

    print(
        "Nghia can review:",
        meaning_review,
    )

    print(
        "Cau truc can review:",
        structure_review,
    )

    print(
        "Tong KyTu can review bat ky muc nao:",
        len(
            review_rows
        ),
    )

    # ======================================================
    # [7] GHI FILE
    # ======================================================

    print(
        "\n[7] GHI FILE"
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
        REVIEW_FILE,
        review_rows,
        REVIEW_FIELDS,
    )

    output_hash = (
        sha256_file(
            OUTPUT
        )
    )

    review_hash = (
        sha256_file(
            REVIEW_FILE
        )
    )

    # ======================================================
    # [8] SUMMARY
    # ======================================================

    pinyin_status_counts = (
        defaultdict(int)
    )

    meaning_status_counts = (
        defaultdict(int)
    )

    for row in output_rows:

        pinyin_status_counts[
            row[
                "TrangThaiPinyin"
            ]
        ] += 1

        meaning_status_counts[
            row[
                "TrangThaiNghia"
            ]
        ] += 1

    summary = {

        "status":
            "PASS",

        "buoc":
            20,

        "tong_chu":
            len(
                output_rows
            ),

        "nguon_sql": {

            "GF0025":
                ma_nguon_gf,

            "CC_CEDICT":
                ma_nguon_cedict,

            "CVDICT":
                ma_nguon_cvdict,
        },

        "coverage": {

            "GF_exact_single_char":
                len(
                    gf_by_char
                ),

            "CVDICT_exact_char":
                len(
                    cvdict_by_char
                ),

            "CEDICT_exact_char":
                len(
                    cedict_by_char
                ),
        },

        "pinyin": {

            "san_sang":
                pinyin_ready,

            "can_review":
                pinyin_review,

            "status_counts":
                dict(
                    pinyin_status_counts
                ),
        },

        "nghia": {

            "san_sang":
                meaning_ready,

            "can_review":
                meaning_review,

            "status_counts":
                dict(
                    meaning_status_counts
                ),
        },

        "cau_truc_can_review":
            structure_review,

        "tong_ky_tu_can_review":
            len(
                review_rows
            ),

        "source_sha256":
            source_hash,

        "output_sha256":
            output_hash,

        "review_sha256":
            review_hash,

        "da_chot_final":
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
    # [9] PREVIEW REVIEW
    # ======================================================

    print(
        "\n[8] PREVIEW CAN REVIEW"
    )

    for row in review_rows[:40]:

        print(
            row[
                "MaChuHanTam"
            ],
            "|",
            row[
                "KyTu"
            ],
            "| Pinyin:",
            row[
                "TrangThaiPinyin"
            ],
            "| Nghia:",
            row[
                "TrangThaiNghia"
            ],
            "| CauTruc:",
            row[
                "CanKiemTraCauTruc"
            ],
        )

    # ======================================================
    # [10] FINAL
    # ======================================================

    print(
        "\n"
        + "=" * 80
    )

    print(
        "BUOC 20 HOAN THANH"
    )

    print(
        "=" * 80
    )

    print(
        "Tong chu:",
        len(
            output_rows
        ),
        "/ 300",
    )

    print(
        "GF muc tu don coverage:",
        len(
            gf_by_char
        ),
        "/ 300",
    )

    print(
        "CVDICT exact-char coverage:",
        len(
            cvdict_by_char
        ),
        "/ 300",
    )

    print(
        "CC-CEDICT exact-char coverage:",
        len(
            cedict_by_char
        ),
        "/ 300",
    )

    print(
        "\nPinyin san sang:",
        pinyin_ready,
    )

    print(
        "Pinyin can review:",
        pinyin_review,
    )

    print(
        "\nNghia san sang:",
        meaning_ready,
    )

    print(
        "Nghia can review:",
        meaning_review,
    )

    print(
        "\nCau truc can review:",
        structure_review,
    )

    print(
        "Tong KyTu can review:",
        len(
            review_rows
        ),
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
        "\nREVIEW:"
    )

    print(
        " ",
        REVIEW_FILE,
    )

    print(
        "SHA256:"
    )

    print(
        review_hash
    )

    print(
        "\nSUMMARY:"
    )

    print(
        " ",
        SUMMARY_FILE,
    )

    print(
        "\nCHUA GHI SQL."
    )

    print(
        "CHUA GAN BAI HOC."
    )

    print(
        "CHUA TAO AUDIO."
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