# -*- coding: utf-8 -*-
"""
BUOC 05 - CHUAN BI IMPORT TU VUNG HSK4

Ket qua da xac minh:
- Tong HSK4: 1000 muc
- Tai su dung TuVung cu: 12
- INSERT moi: 988
  + 978 muc chua co ChuHan trong SQL
  + 10 muc cung ChuHan nhung khac Pinyin
- 1 nhom trung ChuHan + Pinyin: 批 pī
  nhung la 2 MaTuHSK / 2 TuLoai khac nhau
  => giu thanh 2 muc TuVung rieng.

KHONG GHI SQL.
"""

import csv
import re
import unicodedata

from collections import Counter, defaultdict
from pathlib import Path


# ==========================================================
# 1. CAU HINH
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

DATA = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

SOURCE = (
    DATA
    / "vocabulary_hsk4_sql_comparison.csv"
)

OUTPUT = (
    DATA
    / "vocabulary_hsk4_import_draft.csv"
)

NEW = (
    DATA
    / "vocabulary_hsk4_insert_candidates.csv"
)

REUSE = (
    DATA
    / "vocabulary_hsk4_reuse_candidates.csv"
)


EXPECTED_TOTAL = 1000
EXPECTED_REUSE = 12
EXPECTED_INSERT = 988


FIELDS = [
    "MaTuHSK",
    "ChuHan",
    "PhienAm",
    "NghiaTiengViet",
    "TuLoai",
    "MaTuVungDaCo",
    "HanhDongDeXuat",
    "TrangThaiKiemDuyet",
    "VanDeCanKiemTra",
    "NghiaGoc",
    "GhiChuTuDien",
]


# ==========================================================
# 2. HAM HO TRO
# ==========================================================

def clean(value):
    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


def pinyin_key(value):
    return (
        unicodedata.normalize(
            "NFC",
            clean(value).casefold(),
        )
        .replace(" ", "")
        .replace("'", "")
        .replace("’", "")
    )


def basic_key(row):
    return (
        clean(row.get("ChuHan")),
        pinyin_key(
            row.get("PhienAm")
        ),
    )


def full_key(row):
    return (
        clean(row.get("ChuHan")),
        pinyin_key(
            row.get("PhienAm")
        ),
        clean(
            row.get("TuLoaiNguon")
        ).casefold(),
        clean(
            row.get(
                "NghiaTiengVietDeXuat"
            )
            or row.get(
                "NghiaTiengVietThamChieu"
            )
        ).casefold(),
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


def write_csv(path, rows):

    if path.exists():
        raise FileExistsError(
            f"Da ton tai file:\n{path}\n"
            "Khong tu dong ghi de."
        )

    with path.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


# ==========================================================
# 3. MAIN
# ==========================================================

def main():

    print("=" * 72)
    print("BUOC 05 - CHUAN BI IMPORT TU VUNG HSK4")
    print("=" * 72)

    print(
        "CHI TAO FILE KE HOACH - KHONG GHI SQL"
    )

    # ======================================================
    # 1. DOC KET QUA BUOC 03
    # ======================================================

    print(
        "\n[1] DOC KET QUA DOI CHIEU"
    )

    rows = read_csv(
        SOURCE
    )

    print(
        "Tong muc:",
        len(rows),
    )

    if len(rows) != EXPECTED_TOTAL:
        raise RuntimeError(
            f"Can {EXPECTED_TOTAL} muc, "
            f"nhan duoc {len(rows)}."
        )

    # ======================================================
    # 2. KIEM TRA MaTuHSK
    # ======================================================

    ids = [
        clean(
            row.get("MaTuHSK")
        )
        for row in rows
    ]

    if any(
        not value
        for value in ids
    ):
        raise RuntimeError(
            "Co MaTuHSK rong."
        )

    if len(set(ids)) != EXPECTED_TOTAL:
        raise RuntimeError(
            "MaTuHSK bi trung."
        )

    for code in ids:

        if not re.fullmatch(
            r"L4-\d{4}",
            code,
        ):
            raise RuntimeError(
                f"Ma HSK4 khong hop le: {code}"
            )

    print(
        "PASS: 1000 MaTuHSK duy nhat."
    )

    # ======================================================
    # 3. KIEM TRA NHOM CUNG CHUHAN + PINYIN
    # ======================================================

    groups = defaultdict(list)

    for row in rows:
        groups[
            basic_key(row)
        ].append(row)

    duplicate_groups = {
        key: group
        for key, group
        in groups.items()
        if len(group) > 1
    }

    print(
        "\n[2] NHOM CUNG CHUHAN + PINYIN"
    )

    print(
        "So nhom co nhieu MaTuHSK:",
        len(duplicate_groups),
    )

    # Theo ket qua buoc 04,
    # HSK4 hien tai chi co nhom 批 pī.
    if len(duplicate_groups) != 1:
        raise RuntimeError(
            "So nhom trung ChuHan + Pinyin "
            "khac ket qua Buoc 04."
        )

    for key, group in duplicate_groups.items():

        print(
            " ",
            key[0],
            "|",
            clean(
                group[0].get("PhienAm")
            ),
            "|",
            len(group),
            "muc",
        )

        # Hai muc trung basic key chi duoc phep
        # neu full key khac nhau.
        full_keys = {
            full_key(row)
            for row in group
        }

        if len(full_keys) != len(group):
            raise RuntimeError(
                f"{key[0]}: "
                "co MaTuHSK trung hoan toan "
                "ChuHan/Pinyin/TuLoai/Nghia."
            )

        print(
            "  PASS: cac muc co TuLoai/Nghia "
            "phan biet -> giu rieng."
        )

    # ======================================================
    # 4. LAP KE HOACH IMPORT
    # ======================================================

    print(
        "\n[3] LAP KE HOACH IMPORT"
    )

    result = []
    counts = Counter()

    allowed_statuses = {
        "DA_CO_CO_THE_TAI_SU_DUNG",
        "TU_MOI_CHUA_CO_TRONG_SQL",
        "TRUNG_CHU_HAN_KHAC_PINYIN",
    }

    for source in rows:

        code = clean(
            source.get("MaTuHSK")
        )

        hanzi = clean(
            source.get("ChuHan")
        )

        pinyin = clean(
            source.get("PhienAm")
        )

        meaning = clean(
            source.get(
                "NghiaTiengVietDeXuat"
            )
            or source.get(
                "NghiaTiengVietThamChieu"
            )
        )

        word_type = clean(
            source.get(
                "TuLoaiNguon"
            )
        )

        existing_id = clean(
            source.get(
                "MaTuVungDaCo"
            )
        )

        status = clean(
            source.get(
                "TrangThaiDoiChieuSQL"
            )
        )

        warnings = clean(
            source.get(
                "GhiChuDoiChieuSQL"
            )
        )

        # --------------------------------------------------
        # Du lieu bat buoc
        # --------------------------------------------------

        if not code:
            raise RuntimeError(
                "Co MaTuHSK rong."
            )

        if not hanzi:
            raise RuntimeError(
                f"{code}: thieu ChuHan."
            )

        if not pinyin:
            raise RuntimeError(
                f"{code}: thieu Pinyin."
            )

        if not meaning:
            raise RuntimeError(
                f"{code}: thieu nghia Viet."
            )

        if status not in allowed_statuses:
            raise RuntimeError(
                f"{code}: con trang thai "
                f"chua duoc xu ly: {status}"
            )

        # --------------------------------------------------
        # Quyet dinh
        # --------------------------------------------------

        if (
            status
            ==
            "DA_CO_CO_THE_TAI_SU_DUNG"
        ):

            action = "TAI_SU_DUNG"

            if not existing_id:
                raise RuntimeError(
                    f"{code}: TAI_SU_DUNG "
                    "nhung thieu MaTuVungDaCo."
                )

        elif (
            status
            ==
            "TU_MOI_CHUA_CO_TRONG_SQL"
        ):

            action = "INSERT_MOI"

            if existing_id:
                raise RuntimeError(
                    f"{code}: tu moi "
                    "nhung lai co MaTuVungDaCo."
                )

        elif (
            status
            ==
            "TRUNG_CHU_HAN_KHAC_PINYIN"
        ):

            # Cung ChuHan voi SQL nhung
            # Pinyin la mot cach doc khac.
            # Khong tai su dung MaTuVung cu.
            action = "INSERT_MOI"

            if existing_id:
                raise RuntimeError(
                    f"{code}: khac Pinyin "
                    "nhung lai duoc gan MaTuVung cu."
                )

            extra = (
                "CACH_DOC_MOI_INSERT_RIENG"
            )

            warnings = (
                f"{warnings}; {extra}"
                if warnings
                else extra
            )

        else:
            raise RuntimeError(
                f"{code}: trang thai khong hop le."
            )

        # --------------------------------------------------
        # Gioi han cot
        # --------------------------------------------------

        if len(hanzi) > 100:
            raise RuntimeError(
                f"{code}: ChuHan qua dai."
            )

        if len(pinyin) > 200:
            raise RuntimeError(
                f"{code}: Pinyin qua dai."
            )

        if len(meaning) > 2000:
            raise RuntimeError(
                f"{code}: Nghia qua dai."
            )

        if len(word_type) > 100:
            raise RuntimeError(
                f"{code}: TuLoai qua dai."
            )

        # --------------------------------------------------
        # Luu ke hoach
        # --------------------------------------------------

        item = {

            "MaTuHSK":
                code,

            "ChuHan":
                hanzi,

            "PhienAm":
                pinyin,

            "NghiaTiengViet":
                meaning,

            "TuLoai":
                word_type,

            "MaTuVungDaCo":
                existing_id,

            "HanhDongDeXuat":
                action,

            "TrangThaiKiemDuyet":
                "CHUA_DUYET",

            "VanDeCanKiemTra":
                warnings,

            "NghiaGoc":
                clean(
                    source.get(
                        "NghiaTiengVietThamChieu"
                    )
                ),

            "GhiChuTuDien":
                clean(
                    source.get(
                        "GhiChuTuDien"
                    )
                ),
        }

        result.append(
            item
        )

        counts[
            action
        ] += 1

    # ======================================================
    # 5. KIEM TRA SO LUONG CUOI
    # ======================================================

    print(
        "\n[4] KIEM TRA KE HOACH"
    )

    print(
        "TAI_SU_DUNG:",
        counts["TAI_SU_DUNG"],
    )

    print(
        "INSERT_MOI:",
        counts["INSERT_MOI"],
    )

    if (
        counts["TAI_SU_DUNG"]
        != EXPECTED_REUSE
    ):
        raise RuntimeError(
            "So muc TAI_SU_DUNG "
            "khac ket qua Buoc 04."
        )

    if (
        counts["INSERT_MOI"]
        != EXPECTED_INSERT
    ):
        raise RuntimeError(
            "So muc INSERT_MOI "
            "khac ket qua Buoc 04."
        )

    if (
        counts["TAI_SU_DUNG"]
        + counts["INSERT_MOI"]
        != EXPECTED_TOTAL
    ):
        raise RuntimeError(
            "Tong ke hoach khong bang 1000."
        )

    # ======================================================
    # 6. KIEM TRA NHOM 批
    # ======================================================

    pi_group = [
        row
        for row in result
        if (
            row["ChuHan"] == "批"
            and
            pinyin_key(
                row["PhienAm"]
            )
            ==
            pinyin_key("pī")
        )
    ]

    if len(pi_group) != 2:
        raise RuntimeError(
            "Khong tim thay dung 2 muc 批 pī."
        )

    if any(
        row["HanhDongDeXuat"]
        != "INSERT_MOI"
        for row in pi_group
    ):
        raise RuntimeError(
            "Hai muc 批 pī "
            "phai duoc INSERT rieng."
        )

    if len({
        clean(row["TuLoai"])
        for row in pi_group
    }) != 2:
        raise RuntimeError(
            "Hai muc 批 pī "
            "khong con phan biet TuLoai."
        )

    print(
        "PASS: 批 pī co 2 muc "
        "va se INSERT rieng."
    )

    # ======================================================
    # 7. THONG KE CANH BAO
    # ======================================================

    missing_type = sum(
        not clean(
            row["TuLoai"]
        )
        for row in result
    )

    warning_count = sum(
        bool(
            clean(
                row["VanDeCanKiemTra"]
            )
        )
        for row in result
    )

    print(
        "Muc thieu TuLoai:",
        missing_type,
    )

    print(
        "Muc co canh bao:",
        warning_count,
    )

    # 78 muc thieu TuLoai da duoc
    # xac nhan tu nguon o Buoc 01-02.
    if missing_type != 78:
        raise RuntimeError(
            "So muc thieu TuLoai "
            "khac ket qua Buoc 01-02."
        )

    # ======================================================
    # 8. BAO VE FILE CU
    # ======================================================

    for path in (
        OUTPUT,
        NEW,
        REUSE,
    ):
        if path.exists():
            raise FileExistsError(
                f"Da ton tai file:\n{path}\n"
                "Khong tu dong ghi de."
            )

    # ======================================================
    # 9. XUAT FILE
    # ======================================================

    write_csv(
        OUTPUT,
        result,
    )

    write_csv(
        NEW,
        [
            row
            for row in result
            if (
                row[
                    "HanhDongDeXuat"
                ]
                ==
                "INSERT_MOI"
            )
        ],
    )

    write_csv(
        REUSE,
        [
            row
            for row in result
            if (
                row[
                    "HanhDongDeXuat"
                ]
                ==
                "TAI_SU_DUNG"
            )
        ],
    )

    # ======================================================
    # 10. TONG KET
    # ======================================================

    print(
        "\n" + "=" * 72
    )

    print(
        "CHUAN BI IMPORT HSK4 THANH CONG"
    )

    print("=" * 72)

    print(
        "Tong mapping:",
        len(result),
    )

    print(
        "Tai su dung:",
        counts["TAI_SU_DUNG"],
    )

    print(
        "INSERT moi:",
        counts["INSERT_MOI"],
    )

    print(
        "Chua xac dinh:",
        0,
    )

    print(
        "Thieu TuLoai:",
        missing_type,
    )

    print(
        "\nFILE KE HOACH:"
    )
    print(
        " ",
        OUTPUT,
    )

    print(
        "\nFILE INSERT:"
    )
    print(
        " ",
        NEW,
    )

    print(
        "\nFILE TAI SU DUNG:"
    )
    print(
        " ",
        REUSE,
    )

    print(
        "\nCHUA GHI SQL."
    )

    print("=" * 72)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print("\nLOI:")
        print(error)

        raise SystemExit(1)