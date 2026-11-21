
# -*- coding: utf-8 -*-
"""
BUOC 39 - CHUAN BI IMPORT TU VUNG HSK3

Nguon: Ket qua doi chieu o buoc 38.

- Giu du 973 muc HSK3
- Tach tu moi can INSERT
- Giu tu da co de tai su dung
- Cach ly tu trung chu Han khac Pinyin
- Bao toan nghia va canh bao nguon
- KHONG thay doi SQL Server
"""

import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = DATA / "vocabulary_hsk3_sql_comparison.csv"

OUTPUT = DATA / "vocabulary_hsk3_import_draft.csv"
NEW = DATA / "vocabulary_hsk3_insert_candidates.csv"
AMBIGUOUS = DATA / "vocabulary_hsk3_pinyin_conflicts.csv"

EXPECTED_TOTAL = 973

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


def clean(value):
    return re.sub(
        r"\s+", " ", str(value or "")
    ).strip()


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay file: {path}"
        )

    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    if path.exists():
        raise FileExistsError(
            f"File da ton tai: {path}\n"
            "Khong ghi de du lieu da xu ly."
        )

    with path.open(
        "w", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 65)
    print("BUOC 39 - CHUAN BI IMPORT TU VUNG HSK3")
    print("=" * 65)
    print("KHONG GHI SQL SERVER")

    rows = read_csv(SOURCE)

    if len(rows) != EXPECTED_TOTAL:
        raise ValueError(
            f"Du kien {EXPECTED_TOTAL} muc, "
            f"nhan duoc {len(rows)} muc."
        )

    result = []
    counts = Counter()

    for source in rows:
        status = clean(
            source.get("TrangThaiDoiChieuSQL")
        )

        source_id = clean(source.get("MaTuHSK"))
        hanzi = clean(source.get("ChuHan"))
        pinyin = clean(source.get("PhienAm"))

        meaning = clean(
            source.get("NghiaTiengVietDeXuat")
            or source.get("NghiaTiengVietThamChieu")
        )

        word_type = clean(source.get("TuLoaiNguon"))

        existing_id = clean(
            source.get("MaTuVungDaCo")
        )

        warnings = clean(
            source.get("GhiChuDoiChieuSQL")
        )

        if status == "TU_MOI_CHUA_CO_TRONG_SQL":
            action = "INSERT_MOI"

        elif status == "DA_CO_DUNG_CHU_HAN_PINYIN":
            action = "TAI_SU_DUNG"

        else:
            action = "CAN_KIEM_TRA"

        if action == "TAI_SU_DUNG" and not existing_id:
            raise ValueError(
                f"{source_id}: thieu MaTuVungDaCo."
            )

        if not source_id or not hanzi or not pinyin:
            raise ValueError(
                f"{source_id}: thieu ma, ChuHan hoac Pinyin."
            )

        if not meaning:
            raise ValueError(
                f"{source_id}: thieu nghia tieng Viet."
            )

        if len(hanzi) > 100:
            raise ValueError(
                f"{source_id}: ChuHan qua dai."
            )

        if len(pinyin) > 200:
            raise ValueError(
                f"{source_id}: PhienAm qua dai."
            )

        if len(meaning) > 2000:
            raise ValueError(
                f"{source_id}: NghiaTiengViet qua dai."
            )

        if len(word_type) > 100:
            raise ValueError(
                f"{source_id}: TuLoai qua dai."
            )

        result.append({
            "MaTuHSK": source_id,
            "ChuHan": hanzi,
            "PhienAm": pinyin,
            "NghiaTiengViet": meaning,
            "TuLoai": word_type,
            "MaTuVungDaCo": existing_id,
            "HanhDongDeXuat": action,
            "TrangThaiKiemDuyet": "CHUA_DUYET",
            "VanDeCanKiemTra": warnings,
            "NghiaGoc": clean(
                source.get("NghiaTiengVietThamChieu")
            ),
            "GhiChuTuDien": clean(
                source.get("GhiChuTuDien")
            ),
        })

        counts[action] += 1

    ids = [r["MaTuHSK"] for r in result]

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Phat hien MaTuHSK trung nhau."
        )

    if (
        counts["INSERT_MOI"] != 954
        or counts["TAI_SU_DUNG"] != 12
        or counts["CAN_KIEM_TRA"] != 7
    ):
        raise ValueError(
            "So luong phan loai khac buoc 38. "
            "Dung lai de kiem tra."
        )

    # Kiem tra duong dan truoc khi tao bat ky file nao.
    for path in (OUTPUT, NEW, AMBIGUOUS):
        if path.exists():
            raise FileExistsError(
                f"Da co file: {path}\n"
                "Khong tu dong ghi de."
            )

    write_csv(OUTPUT, result)

    write_csv(
        NEW,
        [
            r for r in result
            if r["HanhDongDeXuat"] == "INSERT_MOI"
        ],
    )

    write_csv(
        AMBIGUOUS,
        [
            r for r in result
            if r["HanhDongDeXuat"] == "CAN_KIEM_TRA"
        ],
    )

    print("\nKET QUA CHUAN BI")
    print("Tong muc HSK3:", len(result))
    print("Tu moi can import:", counts["INSERT_MOI"])
    print("Tu da co - tai su dung:", counts["TAI_SU_DUNG"])
    print("Tu can kiem tra Pinyin:", counts["CAN_KIEM_TRA"])

    print("\nFILE DA TAO:")
    print(OUTPUT)
    print(NEW)
    print(AMBIGUOUS)

    print("\nCHUA GHI SQL")
    print("CHUA TU DONG DUYET NGHIA")
    print("HOAN THANH BUOC 39")


if __name__ == "__main__":
    main()
