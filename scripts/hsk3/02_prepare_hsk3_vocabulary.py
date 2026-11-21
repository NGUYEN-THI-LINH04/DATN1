
# -*- coding: utf-8 -*-
"""
BUOC 37 - CHUAN BI TU VUNG HSK3

Du an: MOC HAN
Database: HocTiengTrungDB

Nguon:
data_sources/hsk/hsk1_4_vietnamese_source_complete.csv

Chuc nang:
1. Doc danh sach tu vung HSK3.
2. Lay chu Han gian the, Pinyin, tu loai.
3. Lay nghia tieng Viet tham khao.
4. Tach ghi chu luong tu.
5. Danh dau cac muc can ra soat.
6. Tao 2 file CSV.

KHONG INSERT, UPDATE HOAC DELETE SQL.
"""

import csv
import re

from pathlib import Path


# ==========================================================
# 1. CAU HINH DUONG DAN
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

SOURCE = (
    ROOT
    / "data_sources"
    / "hsk"
    / "hsk1_4_vietnamese_source_complete.csv"
)

OUT = (
    ROOT
    / "scripts"
    / "hsk3"
    / "data"
    / "processed"
)

MAIN = OUT / "vocabulary_hsk3_review.csv"

REVIEW = OUT / "vocabulary_hsk3_need_review.csv"


# ==========================================================
# 2. CAC COT CSV DAU RA
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
# 3. CHUAN HOA CHUOI
# ==========================================================

def tidy(value):

    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


# ==========================================================
# 4. TACH NGHIA VA GHI CHU LUONG TU
# ==========================================================

def split_notes(value):

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


# ==========================================================
# 5. CHUONG TRINH CHINH
# ==========================================================

def main():

    print("=" * 65)
    print("BUOC 37 - CHUAN BI TU VUNG HSK3")
    print("=" * 65)

    print(
        "CHE DO: CHI DOC NGUON - KHONG GHI SQL"
    )

    # ------------------------------------------------------
    # KIEM TRA FILE NGUON
    # ------------------------------------------------------

    if not SOURCE.is_file():

        raise SystemExit(
            "KHONG TIM THAY FILE NGUON:\n"
            + str(SOURCE)
        )

    print("\n[1] DOC FILE NGUON")

    print("Nguon:", SOURCE)

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        data = list(
            csv.DictReader(file)
        )

    print(
        "Tong dong du lieu nguon:",
        len(data),
    )

    # ------------------------------------------------------
    # LOC TU VUNG HSK3
    # ------------------------------------------------------

    print("\n[2] LOC DU LIEU HSK3")

    words = [
        row
        for row in data
        if tidy(
            row.get("CapDoHSK")
        ) == "3"
    ]

    if len(words) != 973:

        raise SystemExit(
            "DUNG LAI: HSK3 co "
            f"{len(words)} muc, "
            "trong khi du kien 973 muc."
        )

    print(
        "So muc tu HSK3:",
        len(words),
    )

    # ------------------------------------------------------
    # XU LY TUNG TU VUNG
    # ------------------------------------------------------

    print("\n[3] CHUAN BI DU LIEU")

    result = []

    seen = set()

    for index, row in enumerate(
        words,
        start=1,
    ):

        source_id = tidy(
            row.get("ID")
        )

        hanzi = tidy(
            row.get("TuChinh")
            or row.get("TuGoc")
        )

        pinyin = tidy(
            row.get("PinyinChuan")
        )

        meaning, notes = split_notes(
            row.get("NghiaTiengViet")
        )

        word_type = tidy(
            row.get("TuLoaiChuan")
            or row.get("TuLoaiMa")
        )

        issues = []

        # Kiem tra ma nguon.
        if (
            not source_id
            or source_id in seen
        ):

            issues.append(
                "MA_NGUON_THIEU_HOAC_TRUNG"
            )

        seen.add(source_id)

        # Kiem tra chu Han.
        if not hanzi:

            issues.append(
                "THIEU_CHU_HAN"
            )

        # Kiem tra Pinyin.
        if not pinyin:

            issues.append(
                "THIEU_PINYIN"
            )

        # Kiem tra nghia tieng Viet.
        if not meaning:

            issues.append(
                "THIEU_NGHIA"
            )

        # Kiem tra canh bao tu nguon.
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

        # Ghi chu luong tu.
        original_meaning = tidy(
            row.get("NghiaTiengViet")
        )

        if "LT:" in original_meaning.upper():

            issues.append(
                "CO_GHI_CHU_LUONG_TU"
            )

        # Nghia qua dai.
        if len(meaning) > 110:

            issues.append(
                "NGHIA_DAI_CAN_RUT_GON"
            )

        # Luu du lieu.
        result.append({

            "MaTuHSK": source_id,

            "SoThuTuNguon": index,

            "ChuHan": hanzi,

            "PhienAm": pinyin,

            "TuLoaiNguon": word_type,

            "NghiaTiengVietThamChieu":
                original_meaning,

            "NghiaTiengVietDeXuat":
                meaning,

            "GhiChuTuDien": notes,

            "NguonTuVung": tidy(
                row.get("NguonTuVung")
            ),

            "NguonNghiaViet": tidy(
                row.get("NguonNghiaViet")
            ),

            "TrangThaiKiemDuyet":
                "CHUA_DUYET",

            "VanDeCanKiemTra":
                "; ".join(issues),

        })

    # ------------------------------------------------------
    # 6. CHUAN BI DUONG DAN XUAT
    # ------------------------------------------------------

    OUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Khong ghi de CSV da ton tai.
    if MAIN.exists() or REVIEW.exists():

        raise SystemExit(
            "DA TON TAI FILE CSV DAU RA.\n"
            "Hay giu lai hoac doi ten file cu "
            "truoc khi chay lai.\n"
            f"{MAIN}\n"
            f"{REVIEW}"
        )

    # ------------------------------------------------------
    # 7. GHI FILE CSV DAY DU
    # ------------------------------------------------------

    print("\n[4] XUAT FILE CSV")

    with MAIN.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS,
        )

        writer.writeheader()

        writer.writerows(result)

    # ------------------------------------------------------
    # 8. GHI FILE CAN RA SOAT
    # ------------------------------------------------------

    need_review = [
        row
        for row in result
        if row["VanDeCanKiemTra"]
    ]

    with REVIEW.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS,
        )

        writer.writeheader()

        writer.writerows(
            need_review
        )

    # ------------------------------------------------------
    # 9. TONG KET
    # ------------------------------------------------------

    print("\n" + "=" * 65)

    print("CHUAN BI TU VUNG HSK3 THANH CONG")

    print("=" * 65)

    print(
        "Tong muc tu HSK3:",
        len(result),
    )

    print(
        "So muc can ra soat:",
        len(need_review),
    )

    print("\nFILE DAY DU:")

    print(MAIN)

    print("\nFILE CAN RA SOAT:")

    print(REVIEW)

    print(
        "\nCHUA INSERT / UPDATE / DELETE SQL."
    )

    print(
        "CHUA CHUYEN TRANG THAI KIEM DUYET."
    )


if __name__ == "__main__":

    main()
