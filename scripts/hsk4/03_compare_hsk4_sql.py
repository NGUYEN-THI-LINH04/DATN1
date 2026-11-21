# -*- coding: utf-8 -*-
"""
BUOC 03 - DOI CHIEU TU VUNG HSK4 VOI SQL SERVER

Nguon:
scripts/hsk4/data/processed/vocabulary_hsk4_review.csv

Bang SQL:
- dbo.TuVungHSKChuan
- dbo.TuVung

Muc dich:
1. Doc dung 1000 muc HSK4.
2. Doi chieu MaTuHSK voi TuVungHSKChuan.
3. Doi chieu ChuHan + Pinyin voi dbo.TuVung.
4. Xac dinh:
   - tu co the tai su dung;
   - tu moi;
   - truong hop da am / trung / can kiem tra.
5. Bao ve cac muc cung ChuHan + Pinyin
   nhung khac tu loai/nghia, khong gop nham.
6. Xuat CSV cho buoc import sau.

CHI DOC SQL.
KHONG INSERT / UPDATE / DELETE.
"""

import csv
import re
import sys
import unicodedata

from collections import Counter, defaultdict
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
EXPECTED_TOTAL = 1000

DATA_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

SOURCE = (
    DATA_DIR
    / "vocabulary_hsk4_review.csv"
)

OUTPUT = (
    DATA_DIR
    / "vocabulary_hsk4_sql_comparison.csv"
)

NEW_WORDS = (
    DATA_DIR
    / "vocabulary_hsk4_new_words.csv"
)

NEED_REVIEW = (
    DATA_DIR
    / "vocabulary_hsk4_sql_need_review.csv"
)


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
    """
    Chuan hoa Pinyin de doi chieu.

    - Unicode NFC
    - chu thuong
    - bo khoang trang
    - bo dau '
    """

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


def word_key(hanzi, pinyin):
    return (
        clean(hanzi),
        normalize_pinyin(pinyin),
    )


def full_key(
    hanzi,
    pinyin,
    word_type,
    meaning,
):
    return (
        clean(hanzi),
        normalize_pinyin(pinyin),
        clean(word_type).casefold(),
        clean(meaning).casefold(),
    )


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

        return list(
            csv.DictReader(file)
        )


def write_csv(
    path,
    rows,
    fields,
):
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


# ==========================================================
# 3. DOC dbo.TuVung
# ==========================================================

def load_existing_vocabulary(cursor):

    cursor.execute(
        """
        SELECT
            MaTuVung,
            ChuHan,
            PhienAm,
            NghiaTiengViet,
            TuLoai
        FROM dbo.TuVung
        ORDER BY MaTuVung;
        """
    )

    by_key = defaultdict(list)
    by_hanzi = defaultdict(list)

    for row in cursor.fetchall():

        item = {
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
        }

        by_key[
            word_key(
                item["ChuHan"],
                item["PhienAm"],
            )
        ].append(item)

        by_hanzi[
            item["ChuHan"]
        ].append(item)

    return (
        by_key,
        by_hanzi,
    )


# ==========================================================
# 4. DOC dbo.TuVungHSKChuan HSK4
# ==========================================================

def load_hsk4_reference(cursor):

    cursor.execute(
        """
        SELECT
            MaTuHSK,
            MaMucNoiBo,
            MaCapDo,
            ChuHan,
            PhienAm,
            TuLoai,
            NghiaTiengVietThamChieu
        FROM dbo.TuVungHSKChuan
        WHERE MaCapDo = ?
        ORDER BY
            SoThuTuNguon,
            MaTuHSK;
        """,
        HSK_LEVEL,
    )

    by_source_id = defaultdict(list)

    total = 0

    for row in cursor.fetchall():

        total += 1

        source_id = clean(
            row[1]
        )

        by_source_id[
            source_id
        ].append({

            "MaTuHSK":
                int(row[0]),

            "MaMucNoiBo":
                source_id,

            "MaCapDo":
                int(row[2]),

            "ChuHan":
                clean(row[3]),

            "PhienAm":
                clean(row[4]),

            "TuLoai":
                clean(row[5]),

            "NghiaTiengViet":
                clean(row[6]),
        })

    return (
        by_source_id,
        total,
    )


# ==========================================================
# 5. TIM BAN GHI SQL CO THE TAI SU DUNG
# ==========================================================

def select_existing(
    matches,
    source_row,
    source_variants,
):
    """
    Cach chon duoc dua tren pipeline HSK3.

    Uu tien:
    1. Trung ChuHan + Pinyin + TuLoai + Nghia.
    2. Cung TuLoai neu nhom nguon chi co 1 bien the.
    3. Chi co duy nhat 1 ban ghi ChuHan + Pinyin
       va nguon khong co nhieu nghia/tu loai.

    Neu khong chac chan:
    -> khong tu dong chon MaTuVung.
    """

    if not matches:
        return None, ""

    word_type = clean(
        source_row.get("TuLoaiNguon")
    )

    meaning = clean(
        source_row.get(
            "NghiaTiengVietDeXuat"
        )
        or source_row.get(
            "NghiaTiengVietThamChieu"
        )
    )

    # ------------------------------------------------------
    # 1. Khop day du
    # ------------------------------------------------------

    full_matches = [
        item
        for item in matches
        if (
            clean(
                item["TuLoai"]
            ).casefold()
            ==
            word_type.casefold()
        )
        and (
            clean(
                item["NghiaTiengViet"]
            ).casefold()
            ==
            meaning.casefold()
        )
    ]

    if len(full_matches) == 1:
        return (
            full_matches[0],
            "KHOP_DAY_DU",
        )

    if len(full_matches) > 1:
        return (
            None,
            "TRUNG_DAY_DU_NHIEU_BAN_GHI",
        )

    # ------------------------------------------------------
    # 2. Cung tu loai
    # ------------------------------------------------------

    same_type = [
        item
        for item in matches
        if (
            clean(
                item["TuLoai"]
            ).casefold()
            ==
            word_type.casefold()
        )
    ]

    if (
        len(same_type) == 1
        and len(source_variants) == 1
    ):
        return (
            same_type[0],
            "KHOP_TU_LOAI",
        )

    # ------------------------------------------------------
    # 3. Chi co duy nhat 1 tu trong SQL
    # ------------------------------------------------------

    if (
        len(matches) == 1
        and len(source_variants) == 1
    ):
        return (
            matches[0],
            "DUY_NHAT_CHUHAN_PINYIN",
        )

    return (
        None,
        "KHONG_THE_TU_DONG_CHON",
    )


# ==========================================================
# 6. DOI CHIEU MOT MUC HSK4
# ==========================================================

def compare_word(
    source_row,
    vocabulary_by_key,
    vocabulary_by_hanzi,
    hsk_by_source_id,
    source_groups,
):

    source_id = clean(
        source_row.get("MaTuHSK")
    )

    hanzi = clean(
        source_row.get("ChuHan")
    )

    pinyin = clean(
        source_row.get("PhienAm")
    )

    word_type = clean(
        source_row.get("TuLoaiNguon")
    )

    meaning = clean(
        source_row.get(
            "NghiaTiengVietDeXuat"
        )
        or source_row.get(
            "NghiaTiengVietThamChieu"
        )
    )

    key = word_key(
        hanzi,
        pinyin,
    )

    exact_matches = (
        vocabulary_by_key.get(
            key,
            [],
        )
    )

    hanzi_matches = (
        vocabulary_by_hanzi.get(
            hanzi,
            [],
        )
    )

    hsk_matches = (
        hsk_by_source_id.get(
            source_id,
            [],
        )
    )

    source_variants = {
        (
            clean(
                item.get("TuLoaiNguon")
            ).casefold(),

            clean(
                item.get(
                    "NghiaTiengVietDeXuat"
                )
                or item.get(
                    "NghiaTiengVietThamChieu"
                )
            ).casefold(),
        )
        for item
        in source_groups[key]
    }

    issues = []

    # ------------------------------------------------------
    # Giu canh bao tu buoc 02
    # ------------------------------------------------------

    old_warning = clean(
        source_row.get(
            "VanDeCanKiemTra"
        )
    )

    if old_warning:
        issues.append(
            old_warning
        )

    # ------------------------------------------------------
    # Bao ve cac muc nhu cung ChuHan + Pinyin
    # nhung khac TuLoai/Nghia
    # ------------------------------------------------------

    if len(source_variants) > 1:
        issues.append(
            "NGUON_CUNG_CHUHAN_PINYIN_NHIEU_MUC"
        )

    # ------------------------------------------------------
    # Kiem tra MaTuHSK
    # ------------------------------------------------------

    hsk_sql_id = ""

    if len(hsk_matches) == 1:

        hsk_row = hsk_matches[0]

        hsk_sql_id = (
            hsk_row["MaTuHSK"]
        )

        if (
            hsk_row["MaCapDo"]
            != HSK_LEVEL
        ):
            issues.append(
                "MA_NGUON_SAI_CAP_HSK"
            )

        if (
            clean(
                hsk_row["ChuHan"]
            )
            != hanzi
        ):
            issues.append(
                "MA_NGUON_KHAC_CHU_HAN"
            )

        if (
            normalize_pinyin(
                hsk_row["PhienAm"]
            )
            !=
            normalize_pinyin(
                pinyin
            )
        ):
            issues.append(
                "MA_NGUON_KHAC_PINYIN"
            )

    elif len(hsk_matches) > 1:

        issues.append(
            "MA_NGUON_TRUNG_TRONG_SQL"
        )

    else:

        issues.append(
            "CHUA_CO_MA_HSK_TRONG_SQL"
        )

    # ------------------------------------------------------
    # Kiem tra dbo.TuVung
    # ------------------------------------------------------

    matched_vocab = None
    match_method = ""

    if exact_matches:

        matched_vocab, match_method = (
            select_existing(
                exact_matches,
                source_row,
                source_variants,
            )
        )

        if matched_vocab is not None:

            status = (
                "DA_CO_CO_THE_TAI_SU_DUNG"
            )

            if (
                match_method
                == "KHOP_TU_LOAI"
            ):
                issues.append(
                    "TAI_SU_DUNG_CUNG_TU_LOAI_NHUNG_NGHIA_KHAC"
                )

            elif (
                match_method
                == "DUY_NHAT_CHUHAN_PINYIN"
            ):
                issues.append(
                    "TAI_SU_DUNG_DUY_NHAT_CAN_SO_SANH_NGHIA_TULOAI"
                )

        else:

            if (
                match_method
                ==
                "TRUNG_DAY_DU_NHIEU_BAN_GHI"
            ):
                status = (
                    "TRUNG_NHIEU_BAN_GHI_SQL"
                )

                issues.append(
                    "CAN_XAC_DINH_MA_TU_VUNG"
                )

            else:
                status = (
                    "CUNG_CHUHAN_PINYIN_CAN_KIEM_TRA"
                )

                issues.append(
                    "KHONG_THE_TU_DONG_XAC_DINH_MA_TU_VUNG"
                )

    elif hanzi_matches:

        status = (
            "TRUNG_CHU_HAN_KHAC_PINYIN"
        )

        match_method = (
            "CHU_HAN_CO_NHUNG_PINYIN_KHAC"
        )

        issues.append(
            "CAN_KIEM_TRA_TU_DA_AM"
        )

    else:

        status = (
            "TU_MOI_CHUA_CO_TRONG_SQL"
        )

        match_method = (
            "CHUA_CO_CHU_HAN"
        )

    # ------------------------------------------------------
    # Gia tri SQL duoc chon neu an toan
    # ------------------------------------------------------

    vocab_id = ""
    sql_meaning = ""
    sql_word_type = ""
    sql_pinyin = ""

    if matched_vocab:

        vocab_id = (
            matched_vocab["MaTuVung"]
        )

        sql_meaning = clean(
            matched_vocab[
                "NghiaTiengViet"
            ]
        )

        sql_word_type = clean(
            matched_vocab[
                "TuLoai"
            ]
        )

        sql_pinyin = clean(
            matched_vocab[
                "PhienAm"
            ]
        )

    # ------------------------------------------------------
    # Ket qua
    # ------------------------------------------------------

    result = dict(
        source_row
    )

    result.update({

        "TrangThaiDoiChieuSQL":
            status,

        "PhuongPhapKhopSQL":
            match_method,

        "MaTuVungDaCo":
            vocab_id,

        "MaTuHSKTrongSQL":
            hsk_sql_id,

        "PinyinTrongSQL":
            sql_pinyin,

        "TuLoaiTrongSQL":
            sql_word_type,

        "NghiaTrongSQL":
            sql_meaning,

        "SoBanGhiTrungChuHan":
            len(
                hanzi_matches
            ),

        "SoBanGhiTrungChuHanPinyin":
            len(
                exact_matches
            ),

        "SoBienTheNguonCungChuHanPinyin":
            len(
                source_variants
            ),

        "GhiChuDoiChieuSQL":
            "; ".join(
                dict.fromkeys(
                    issues
                )
            ),
    })

    return result


# ==========================================================
# 7. MAIN
# ==========================================================

def main():

    print("=" * 72)

    print(
        "BUOC 03 - DOI CHIEU TU VUNG HSK4 VOI SQL"
    )

    print("=" * 72)

    print(
        "CHE DO: CHI DOC SQL - "
        "KHONG INSERT / UPDATE / DELETE"
    )

    # ======================================================
    # 1. DOC FILE BUOC 02
    # ======================================================

    print(
        "\n[1] DOC DU LIEU HSK4 TU BUOC 02"
    )

    words = read_csv(
        SOURCE
    )

    print(
        "Tong muc tu:",
        len(words),
    )

    if len(words) != EXPECTED_TOTAL:

        raise RuntimeError(
            f"HSK4 phai co "
            f"{EXPECTED_TOTAL} muc, "
            f"nhung file co {len(words)}."
        )

    source_ids = [
        clean(
            row.get("MaTuHSK")
        )
        for row in words
    ]

    if any(
        not item
        for item in source_ids
    ):
        raise RuntimeError(
            "Co MaTuHSK rong."
        )

    if (
        len(set(source_ids))
        != EXPECTED_TOTAL
    ):
        raise RuntimeError(
            "MaTuHSK trong CSV bi trung."
        )

    # ======================================================
    # 2. NHOM NGUON THEO CHUHAN + PINYIN
    # ======================================================

    source_groups = (
        defaultdict(list)
    )

    for row in words:

        key = word_key(
            row.get("ChuHan"),
            row.get("PhienAm"),
        )

        source_groups[
            key
        ].append(row)

    duplicate_source_groups = {
        key: rows
        for key, rows
        in source_groups.items()
        if len(rows) > 1
    }

    print(
        "Nhom ChuHan + Pinyin khac nhau:",
        len(source_groups),
    )

    print(
        "Nhom nguon co nhieu hon 1 muc:",
        len(
            duplicate_source_groups
        ),
    )

    # ======================================================
    # 3. DOC SQL
    # ======================================================

    print(
        "\n[2] DOC SQL SERVER"
    )

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            (
                vocabulary_by_key,
                vocabulary_by_hanzi,
            ) = load_existing_vocabulary(
                cursor
            )

            (
                hsk_by_source_id,
                hsk_total,
            ) = load_hsk4_reference(
                cursor
            )

            # Chi doc, khong commit.
            connection.rollback()

    print(
        "Tong cap ChuHan + Pinyin "
        "trong dbo.TuVung:",
        len(
            vocabulary_by_key
        ),
    )

    print(
        "Tong muc HSK4 "
        "trong TuVungHSKChuan:",
        hsk_total,
    )

    if hsk_total != EXPECTED_TOTAL:

        raise RuntimeError(
            "TuVungHSKChuan HSK4 "
            f"phai co {EXPECTED_TOTAL} muc."
        )

    if (
        len(hsk_by_source_id)
        != EXPECTED_TOTAL
    ):
        raise RuntimeError(
            "MaMucNoiBo HSK4 trong SQL "
            "bi trung hoac thieu."
        )

    for source_id, rows in (
        hsk_by_source_id.items()
    ):
        if len(rows) != 1:
            raise RuntimeError(
                f"{source_id}: "
                "khong co dung 1 dong "
                "TuVungHSKChuan."
            )

    # ======================================================
    # 4. DOI CHIEU
    # ======================================================

    print(
        "\n[3] DOI CHIEU 1000 MUC HSK4"
    )

    result = [
        compare_word(
            source_row=row,
            vocabulary_by_key=
                vocabulary_by_key,
            vocabulary_by_hanzi=
                vocabulary_by_hanzi,
            hsk_by_source_id=
                hsk_by_source_id,
            source_groups=
                source_groups,
        )
        for row in words
    ]

    counts = Counter(
        row[
            "TrangThaiDoiChieuSQL"
        ]
        for row in result
    )

    methods = Counter(
        row[
            "PhuongPhapKhopSQL"
        ]
        for row in result
    )

    # ======================================================
    # 5. TU MOI
    # ======================================================

    new_words = [
        row
        for row in result
        if (
            row[
                "TrangThaiDoiChieuSQL"
            ]
            ==
            "TU_MOI_CHUA_CO_TRONG_SQL"
        )
    ]

    # ======================================================
    # 6. CAN REVIEW
    # ======================================================

    structural_review_statuses = {
        "TRUNG_NHIEU_BAN_GHI_SQL",
        "CUNG_CHUHAN_PINYIN_CAN_KIEM_TRA",
        "TRUNG_CHU_HAN_KHAC_PINYIN",
    }

    review_rows = [
        row
        for row in result
        if (
            clean(
                row.get(
                    "GhiChuDoiChieuSQL"
                )
            )
            or
            row[
                "TrangThaiDoiChieuSQL"
            ]
            in structural_review_statuses
        )
    ]

    # ======================================================
    # 7. KIEM TRA FILE DAU RA
    # ======================================================

    print(
        "\n[4] KIEM TRA FILE DAU RA"
    )

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for path in (
        OUTPUT,
        NEW_WORDS,
        NEED_REVIEW,
    ):
        if path.exists():

            raise FileExistsError(
                "DA TON TAI FILE:\n"
                f"{path}\n\n"
                "Khong tu dong ghi de."
            )

    # ======================================================
    # 8. XUAT CSV
    # ======================================================

    fields = list(
        result[0].keys()
    )

    write_csv(
        OUTPUT,
        result,
        fields,
    )

    write_csv(
        NEW_WORDS,
        new_words,
        fields,
    )

    write_csv(
        NEED_REVIEW,
        review_rows,
        fields,
    )

    # ======================================================
    # 9. TONG KET
    # ======================================================

    print(
        "\n" + "=" * 72
    )

    print(
        "KET QUA DOI CHIEU HSK4"
    )

    print("=" * 72)

    print(
        "\nPHAN LOAI:"
    )

    for name, count in sorted(
        counts.items()
    ):
        print(
            f"  {name}: {count}"
        )

    print(
        "\nPHUONG PHAP KHOP:"
    )

    for name, count in sorted(
        methods.items()
    ):
        print(
            f"  {name}: {count}"
        )

    print(
        "\nTong muc HSK4:",
        len(result),
    )

    print(
        "Tu moi chua co trong SQL:",
        len(new_words),
    )

    print(
        "Muc co canh bao/can ra soat:",
        len(review_rows),
    )

    print(
        "\nNhom nguon trung "
        "ChuHan + Pinyin:",
        len(
            duplicate_source_groups
        ),
    )

    print(
        "\nFILE DOI CHIEU:"
    )

    print(
        " ",
        OUTPUT,
    )

    print(
        "\nFILE TU MOI:"
    )

    print(
        " ",
        NEW_WORDS,
    )

    print(
        "\nFILE CAN RA SOAT:"
    )

    print(
        " ",
        NEED_REVIEW,
    )

    print(
        "\nHOAN THANH - "
        "CHUA THAY DOI SQL"
    )

    print("=" * 72)


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