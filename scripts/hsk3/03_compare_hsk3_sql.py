
# -*- coding: utf-8 -*-
"""
BUOC 38 - DOI CHIEU TU VUNG HSK3 VOI SQL SERVER

Nguon:
scripts/hsk3/data/processed/vocabulary_hsk3_review.csv

Bang SQL:
- TuVungHSKChuan
- TuVung

Chuc nang:
1. Doc 973 muc tu HSK3.
2. Doi chieu ma nguon voi TuVungHSKChuan.
3. Doi chieu ChuHan + Pinyin voi TuVung.
4. Phan loai tu da co, tu moi, tu can kiem tra.
5. Xuat CSV phuc vu import o buoc sau.

CHI DOC SQL - KHONG INSERT / UPDATE / DELETE.
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
sys.path.insert(0, str(ROOT))

from database import get_connection

DATA_DIR = (
    ROOT / "scripts" / "hsk3" / "data" / "processed"
)

SOURCE = DATA_DIR / "vocabulary_hsk3_review.csv"

OUTPUT = DATA_DIR / "vocabulary_hsk3_sql_comparison.csv"

NEW_WORDS = DATA_DIR / "vocabulary_hsk3_new_words.csv"

NEED_REVIEW = DATA_DIR / "vocabulary_hsk3_sql_need_review.csv"

HSK_LEVEL = 3


# ==========================================================
# 2. HAM CHUAN HOA
# ==========================================================

def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_pinyin(value):
    text = unicodedata.normalize(
        "NFC", clean(value).lower()
    )
    return text.replace(" ", "").replace("'", "")


def make_key(hanzi, pinyin):
    return (
        clean(hanzi),
        normalize_pinyin(pinyin),
    )


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay file:\n{path}"
        )

    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    with path.open(
        "w", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fields,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


# ==========================================================
# 3. DOC TU VUNG TRONG SQL
# ==========================================================

def load_existing_vocabulary(cursor):
    cursor.execute("""
        SELECT
            MaTuVung,
            ChuHan,
            PhienAm,
            NghiaTiengViet,
            TuLoai
        FROM dbo.TuVung;
    """)

    by_key = defaultdict(list)
    by_hanzi = defaultdict(list)

    for row in cursor.fetchall():
        item = {
            "MaTuVung": int(row[0]),
            "ChuHan": clean(row[1]),
            "PhienAm": clean(row[2]),
            "NghiaTiengViet": clean(row[3]),
            "TuLoai": clean(row[4]),
        }

        by_key[
            make_key(item["ChuHan"], item["PhienAm"])
        ].append(item)

        by_hanzi[item["ChuHan"]].append(item)

    return by_key, by_hanzi


def load_existing_hsk(cursor):
    cursor.execute("""
        SELECT
            MaTuHSK,
            MaMucNoiBo,
            MaCapDo,
            ChuHan,
            PhienAm
        FROM dbo.TuVungHSKChuan;
    """)

    by_source_id = defaultdict(list)

    for row in cursor.fetchall():
        source_id = clean(row[1])

        by_source_id[source_id].append({
            "MaTuHSK": int(row[0]),
            "MaMucNoiBo": source_id,
            "MaCapDo": int(row[2]),
            "ChuHan": clean(row[3]),
            "PhienAm": clean(row[4]),
        })

    return by_source_id


# ==========================================================
# 4. DOI CHIEU
# ==========================================================

def compare_word(
    row,
    vocabulary_by_key,
    vocabulary_by_hanzi,
    hsk_by_source_id,
):
    source_id = clean(row["MaTuHSK"])
    hanzi = clean(row["ChuHan"])
    pinyin = clean(row["PhienAm"])

    key = make_key(hanzi, pinyin)

    exact_matches = vocabulary_by_key.get(key, [])
    hanzi_matches = vocabulary_by_hanzi.get(hanzi, [])
    hsk_matches = hsk_by_source_id.get(source_id, [])

    issues = []

    existing_warning = clean(
        row.get("VanDeCanKiemTra")
    )

    if existing_warning:
        issues.append(existing_warning)

    # -----------------------------------------
    # Kiem tra danh sach HSK chuan
    # -----------------------------------------

    hsk_id = ""

    if len(hsk_matches) == 1:
        hsk_row = hsk_matches[0]
        hsk_id = hsk_row["MaTuHSK"]

        if hsk_row["MaCapDo"] != HSK_LEVEL:
            issues.append("MA_NGUON_SAI_CAP_HSK")

        if hsk_row["ChuHan"] != hanzi:
            issues.append("MA_NGUON_KHAC_CHU_HAN")

        if (
            normalize_pinyin(hsk_row["PhienAm"])
            != normalize_pinyin(pinyin)
        ):
            issues.append("MA_NGUON_KHAC_PINYIN")

    elif len(hsk_matches) > 1:
        issues.append("MA_NGUON_TRUNG_TRONG_SQL")

    else:
        issues.append("CHUA_CO_MA_HSK_TRONG_SQL")

    # -----------------------------------------
    # Phan loai tu vung
    # -----------------------------------------

    matched_vocab_id = ""
    matched_meaning = ""

    if len(exact_matches) == 1:
        matched = exact_matches[0]

        matched_vocab_id = matched["MaTuVung"]
        matched_meaning = matched["NghiaTiengViet"]

        status = "DA_CO_DUNG_CHU_HAN_PINYIN"

    elif len(exact_matches) > 1:
        status = "TRUNG_NHIEU_BAN_GHI_SQL"
        issues.append("CAN_XAC_DINH_MA_TU_VUNG")

    elif hanzi_matches:
        status = "TRUNG_CHU_HAN_KHAC_PINYIN"
        issues.append("CAN_KIEM_TRA_TU_DA_AM")

    else:
        status = "TU_MOI_CHUA_CO_TRONG_SQL"

    # -----------------------------------------
    # Tao ket qua
    # -----------------------------------------

    result = dict(row)

    result.update({
        "TrangThaiDoiChieuSQL": status,
        "MaTuVungDaCo": matched_vocab_id,
        "MaTuHSKDaCo": hsk_id,
        "NghiaTrongSQL": matched_meaning,
        "SoBanGhiTrungChuHan": len(hanzi_matches),
        "SoBanGhiTrungChuHanPinyin": len(exact_matches),
        "GhiChuDoiChieuSQL": "; ".join(
            dict.fromkeys(issues)
        ),
    })

    return result


# ==========================================================
# 5. CHUONG TRINH CHINH
# ==========================================================

def main():
    print("=" * 68)
    print("BUOC 38 - DOI CHIEU TU VUNG HSK3 VOI SQL")
    print("=" * 68)
    print("CHE DO: CHI DOC - KHONG GHI SQL")

    print("\n[1] DOC DU LIEU HSK3")

    words = read_csv(SOURCE)

    print("Tong muc tu:", len(words))

    if len(words) != 973:
        raise RuntimeError(
            "So luong tu HSK3 khong phai 973. "
            "Dung lai de tranh doi chieu sai."
        )

    source_ids = [clean(r["MaTuHSK"]) for r in words]

    if len(set(source_ids)) != len(source_ids):
        raise RuntimeError(
            "Co MaTuHSK trung trong CSV nguon."
        )

    print("\n[2] DOC DU LIEU SQL SERVER")

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:

            vocabulary_by_key, vocabulary_by_hanzi = (
                load_existing_vocabulary(cursor)
            )

            hsk_by_source_id = load_existing_hsk(cursor)

    print(
        "Tong cap ChuHan + Pinyin trong SQL:",
        len(vocabulary_by_key),
    )

    print(
        "Tong ma nguon HSK trong SQL:",
        len(hsk_by_source_id),
    )

    print("\n[3] DOI CHIEU 973 MUC TU")

    result = [
        compare_word(
            word,
            vocabulary_by_key,
            vocabulary_by_hanzi,
            hsk_by_source_id,
        )
        for word in words
    ]

    counts = Counter(
        row["TrangThaiDoiChieuSQL"]
        for row in result
    )

    # Chi nhung tu hoan toan chua co trong SQL
    new_words = [
        row for row in result
        if row["TrangThaiDoiChieuSQL"]
        == "TU_MOI_CHUA_CO_TRONG_SQL"
    ]

    # Gom tu can ra soat nghia hoac doi chieu
    review_rows = [
        row for row in result
        if row["GhiChuDoiChieuSQL"]
        or row["TrangThaiDoiChieuSQL"] in (
            "TRUNG_NHIEU_BAN_GHI_SQL",
            "TRUNG_CHU_HAN_KHAC_PINYIN",
        )
    ]

    print("\n[4] XUAT BAO CAO CSV")

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = list(result[0].keys())

    write_csv(OUTPUT, result, fields)
    write_csv(NEW_WORDS, new_words, fields)
    write_csv(NEED_REVIEW, review_rows, fields)

    print("\n" + "=" * 68)
    print("KET QUA DOI CHIEU HSK3")
    print("=" * 68)

    for name, count in sorted(counts.items()):
        print(f"{name}: {count}")

    print("\nTong muc HSK3:", len(result))
    print("Tu moi chua co trong SQL:", len(new_words))
    print("Muc can ra soat:", len(review_rows))

    print("\nFILE DOI CHIEU:")
    print(OUTPUT)

    print("\nFILE TU MOI:")
    print(NEW_WORDS)

    print("\nFILE CAN RA SOAT:")
    print(NEED_REVIEW)

    print("\nHOAN THANH - CHUA THAY DOI SQL")


if __name__ == "__main__":
    main()
