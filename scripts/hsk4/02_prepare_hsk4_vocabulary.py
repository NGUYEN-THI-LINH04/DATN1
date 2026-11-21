# -*- coding: utf-8 -*-
"""
BUOC 02 - CHUAN BI TU VUNG HSK4

Du an: MOC HAN
Database: HocTiengTrungDB

Nguon:
data_sources/hsk/hsk1_4_vietnamese_source_complete.csv

Chuc nang:
1. Doc danh sach 1000 tu HSK4.
2. Lay Chu Han, Pinyin, tu loai.
3. Lay nghia tieng Viet tham khao.
4. Tach ghi chu luong tu "LT:" ra khoi nghia chinh.
5. Danh dau cac muc can ra soat.
6. Tao file day du va file can review.

KHONG INSERT / UPDATE / DELETE SQL.
"""

import csv
import re
from collections import Counter
from pathlib import Path


# ==========================================================
# 1. CAU HINH
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

HSK_LEVEL = 4
EXPECTED_TOTAL = 1000

SOURCE = (
    ROOT
    / "data_sources"
    / "hsk"
    / "hsk1_4_vietnamese_source_complete.csv"
)

OUT = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

MAIN = OUT / "vocabulary_hsk4_review.csv"

REVIEW = OUT / "vocabulary_hsk4_need_review.csv"


# ==========================================================
# 2. COT DAU RA
# ==========================================================

FIELDS = [
    "MaTuHSK",
    "SoThuTuNguon",
    "ChuHan",
    "PhienAm",
    "TuLoaiNguon",
    "NghiaTiengVietThamChieu",
    "NghiaTiengVietDeXuat",
    "GhiChuTuDien",
    "NguonTuVung",
    "NguonNghiaViet",
    "TrangThaiKiemDuyet",
    "VanDeCanKiemTra",
]


# ==========================================================
# 3. HAM HO TRO
# ==========================================================

def tidy(value):
    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


def split_notes(value):
    """
    Tach cac phan kieu:

    nghia 1 / nghia 2 / LT:個|个[ge4]

    thanh:
    - nghia chinh
    - ghi chu luong tu
    """

    parts = [
        tidy(item)
        for item in re.split(
            r"\s*(?:/|\|\|)\s*",
            value or "",
        )
        if tidy(item)
    ]

    meanings = [
        item
        for item in parts
        if not re.match(
            r"^LT\s*:",
            item,
            re.I,
        )
    ]

    notes = [
        item
        for item in parts
        if re.match(
            r"^LT\s*:",
            item,
            re.I,
        )
    ]

    return (
        " / ".join(meanings),
        " / ".join(notes),
    )


def write_csv(path, rows):
    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS,
        )

        writer.writeheader()
        writer.writerows(rows)


# ==========================================================
# 4. MAIN
# ==========================================================

def main():

    print("=" * 70)
    print("BUOC 02 - CHUAN BI TU VUNG HSK4")
    print("=" * 70)

    print(
        "CHE DO: CHI DOC NGUON - KHONG GHI SQL"
    )

    # ======================================================
    # 1. KIEM TRA FILE NGUON
    # ======================================================

    print("\n[1] KIEM TRA FILE NGUON")

    if not SOURCE.is_file():
        raise FileNotFoundError(
            "KHONG TIM THAY FILE NGUON:\n"
            + str(SOURCE)
        )

    print("Nguon:")
    print(" ", SOURCE)

    # ======================================================
    # 2. DOC FILE CSV
    # ======================================================

    print("\n[2] DOC FILE NGUON")

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        all_rows = list(
            csv.DictReader(file)
        )

    print(
        "Tong dong HSK1-HSK4 trong nguon:",
        len(all_rows),
    )

    # ======================================================
    # 3. LOC HSK4
    # ======================================================

    print("\n[3] LOC DU LIEU HSK4")

    words = [
        row
        for row in all_rows
        if tidy(
            row.get("CapDoHSK")
        ) == str(HSK_LEVEL)
    ]

    print(
        "So muc tim thay:",
        len(words),
    )

    if len(words) != EXPECTED_TOTAL:
        raise RuntimeError(
            f"HSK4 phai co {EXPECTED_TOTAL} muc, "
            f"nhung file nguon co {len(words)} muc."
        )

    # ======================================================
    # 4. CHUAN BI 1000 MUC TU
    # ======================================================

    print("\n[4] CHUAN BI 1000 MUC TU")

    result = []

    seen_ids = set()

    issue_counter = Counter()

    for index, row in enumerate(
        words,
        start=1,
    ):

        # --------------------------------------------------
        # Ma muc HSK
        # --------------------------------------------------

        source_id = tidy(
            row.get("ID")
        )

        # --------------------------------------------------
        # Chu Han
        # --------------------------------------------------

        hanzi = tidy(
            row.get("TuChinh")
            or row.get("TuGoc")
        )

        # --------------------------------------------------
        # Pinyin
        # --------------------------------------------------

        pinyin = tidy(
            row.get("PinyinChuan")
        )

        # --------------------------------------------------
        # Nghia Viet
        # --------------------------------------------------

        original_meaning = tidy(
            row.get("NghiaTiengViet")
        )

        meaning, notes = split_notes(
            original_meaning
        )

        # --------------------------------------------------
        # Tu loai
        # --------------------------------------------------

        word_type = tidy(
            row.get("TuLoaiChuan")
            or row.get("TuLoaiMa")
        )

        issues = []

        # --------------------------------------------------
        # Kiem tra ma nguon
        # --------------------------------------------------

        if not source_id:
            issues.append(
                "THIEU_MA_NGUON"
            )

        elif source_id in seen_ids:
            issues.append(
                "TRUNG_MA_NGUON"
            )

        seen_ids.add(source_id)

        # --------------------------------------------------
        # Kiem tra du lieu bat buoc
        # --------------------------------------------------

        if not hanzi:
            issues.append(
                "THIEU_CHU_HAN"
            )

        if not pinyin:
            issues.append(
                "THIEU_PINYIN"
            )

        if not meaning:
            issues.append(
                "THIEU_NGHIA"
            )

        # Tu loai khong bat buoc de dung pipeline,
        # nhung phai danh dau de xu ly sau.
        if not word_type:
            issues.append(
                "THIEU_TU_LOAI"
            )

        # --------------------------------------------------
        # Nguon yeu cau ra soat thu cong
        # --------------------------------------------------

        if (
            tidy(
                row.get("CanKiemTraNghia")
            ) == "1"
            or tidy(
                row.get("CanKiemTraThuCong")
            ) == "1"
        ):
            issues.append(
                "NGUON_YEU_CAU_RA_SOAT"
            )

        # --------------------------------------------------
        # Ghi chu luong tu
        # --------------------------------------------------

        if "LT:" in original_meaning.upper():
            issues.append(
                "CO_GHI_CHU_LUONG_TU"
            )

        # --------------------------------------------------
        # Nghia qua dai
        # --------------------------------------------------

        if len(meaning) > 110:
            issues.append(
                "NGHIA_DAI_CAN_RUT_GON"
            )

        # --------------------------------------------------
        # Dem tung loai canh bao
        # --------------------------------------------------

        for issue in issues:
            issue_counter[issue] += 1

        # --------------------------------------------------
        # Luu dong ket qua
        # --------------------------------------------------

        result.append({

            "MaTuHSK":
                source_id,

            "SoThuTuNguon":
                index,

            "ChuHan":
                hanzi,

            "PhienAm":
                pinyin,

            "TuLoaiNguon":
                word_type,

            "NghiaTiengVietThamChieu":
                original_meaning,

            "NghiaTiengVietDeXuat":
                meaning,

            "GhiChuTuDien":
                notes,

            "NguonTuVung":
                tidy(
                    row.get("NguonTuVung")
                ),

            "NguonNghiaViet":
                tidy(
                    row.get("NguonNghiaViet")
                ),

            "TrangThaiKiemDuyet":
                "CHUA_DUYET",

            "VanDeCanKiemTra":
                "; ".join(issues),

        })

    # ======================================================
    # 5. KIEM TRA SAU XU LY
    # ======================================================

    print("\n[5] KIEM TRA SAU XU LY")

    if len(result) != EXPECTED_TOTAL:
        raise RuntimeError(
            "So luong sau xu ly khong con 1000."
        )

    ids = [
        row["MaTuHSK"]
        for row in result
    ]

    if len(set(ids)) != EXPECTED_TOTAL:
        raise RuntimeError(
            "MaTuHSK bi trung hoac thieu."
        )

    missing_hanzi = sum(
        not row["ChuHan"]
        for row in result
    )

    missing_pinyin = sum(
        not row["PhienAm"]
        for row in result
    )

    missing_meaning = sum(
        not row["NghiaTiengVietDeXuat"]
        for row in result
    )

    print(
        "Tong:",
        len(result),
    )

    print(
        "MaTuHSK khac nhau:",
        len(set(ids)),
    )

    print(
        "Thieu ChuHan:",
        missing_hanzi,
    )

    print(
        "Thieu Pinyin:",
        missing_pinyin,
    )

    print(
        "Thieu nghia:",
        missing_meaning,
    )

    if (
        missing_hanzi
        or missing_pinyin
        or missing_meaning
    ):
        raise RuntimeError(
            "Co muc HSK4 thieu du lieu bat buoc."
        )

    # ======================================================
    # 6. CAC MUC CAN REVIEW
    # ======================================================

    need_review = [
        row
        for row in result
        if row["VanDeCanKiemTra"]
    ]

    print("\n[6] THONG KE CAN RA SOAT")

    if issue_counter:
        for issue, count in sorted(
            issue_counter.items()
        ):
            print(
                f"  {issue}: {count}"
            )

    else:
        print(
            "  Khong co canh bao."
        )

    print(
        "\nTong dong co it nhat 1 canh bao:",
        len(need_review),
    )

    # ======================================================
    # 7. BAO VE FILE CU
    # ======================================================

    OUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    for path in (
        MAIN,
        REVIEW,
    ):
        if path.exists():
            raise FileExistsError(
                "DA TON TAI FILE DAU RA:\n"
                f"{path}\n\n"
                "Khong tu dong ghi de. "
                "Hay doi ten/xoa file cu "
                "neu ban thuc su muon chay lai."
            )

    # ======================================================
    # 8. XUAT CSV
    # ======================================================

    print("\n[7] XUAT FILE")

    write_csv(
        MAIN,
        result,
    )

    write_csv(
        REVIEW,
        need_review,
    )

    # ======================================================
    # 9. TONG KET
    # ======================================================

    print("\n" + "=" * 70)

    print(
        "CHUAN BI TU VUNG HSK4 THANH CONG"
    )

    print("=" * 70)

    print(
        "Tong muc HSK4:",
        len(result),
    )

    print(
        "So muc can ra soat:",
        len(need_review),
    )

    print("\nFILE DAY DU:")
    print(" ", MAIN)

    print("\nFILE CAN RA SOAT:")
    print(" ", REVIEW)

    print(
        "\nCHUA INSERT / UPDATE / DELETE SQL."
    )

    print(
        "CHUA TU DONG DUYET NGHIA."
    )

    print("=" * 70)


if __name__ == "__main__":
    try:
        main()

    except Exception as error:
        print("\nLOI:")
        print(error)
        raise SystemExit(1)