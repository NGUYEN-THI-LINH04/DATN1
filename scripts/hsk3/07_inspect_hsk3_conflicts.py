
# -*- coding: utf-8 -*-
"""
BUOC 42 - KIEM TRA CHI TIET 11 MUC HSK3

Chuc nang:
- Doc 11 muc bi cach ly.
- Lay nghia, Pinyin, tu loai trong SQL.
- Nhom cac muc trung ChuHan + Pinyin.
- Xuat bao cao de xac dinh cach xu ly.

KHONG INSERT / UPDATE / DELETE SQL.
"""

import csv
import sys
import re
import unicodedata

from pathlib import Path
from collections import defaultdict
from contextlib import closing

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = DATA / "hsk3_11_conflicts_detail.csv"
OUTPUT = DATA / "hsk3_conflicts_full_review.csv"

FIELDS = [
    "MaTuHSK",
    "ChuHan",
    "PhienAmHSK3",
    "TuLoaiHSK3",
    "NghiaHSK3",
    "LyDoCachLy",
    "MaTuVungSQL",
    "PhienAmSQL",
    "TuLoaiSQL",
    "NghiaSQL",
    "SoMucTrungTrongCSV",
    "MaNguonTrungTrongCSV",
    "HuongXuLyDeXuat",
    "QuyetDinhCuoi",
    "GhiChuKiemDuyet",
]


def clean(value):
    return re.sub(
        r"\s+", " ", str(value or "")
    ).strip()


def pinyin_key(value):
    return unicodedata.normalize(
        "NFC", clean(value).casefold()
    ).replace(" ", "").replace("'", "")


def read_source():
    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"Khong tim thay: {SOURCE}"
        )

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    if len(rows) != 11:
        raise ValueError(
            f"Can dung 11 muc, tim thay {len(rows)}."
        )

    return rows


def main():
    print("=" * 68)
    print("BUOC 42 - KIEM TRA 11 MUC TU HSK3")
    print("=" * 68)
    print("CHE DO: CHI DOC SQL")

    source_rows = read_source()

    # Gom cac ma nguon co cung ChuHan + Pinyin.
    groups = defaultdict(list)

    for row in source_rows:
        group_key = (
            clean(row["ChuHan"]),
            pinyin_key(row["PhienAm"]),
        )
        groups[group_key].append(
            clean(row["MaTuHSK"])
        )

    hanzi_list = sorted({
        clean(row["ChuHan"])
        for row in source_rows
    })

    placeholders = ",".join(
        "?" for _ in hanzi_list
    )

    sql = f"""
        SELECT
            MaTuVung,
            ChuHan,
            PhienAm,
            TuLoai,
            NghiaTiengViet
        FROM dbo.TuVung
        WHERE ChuHan IN ({placeholders})
        ORDER BY ChuHan, MaTuVung;
    """

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql, *hanzi_list)
            sql_rows = cursor.fetchall()

    sql_by_hanzi = defaultdict(list)

    for row in sql_rows:
        sql_by_hanzi[clean(row[1])].append({
            "MaTuVung": str(row[0]),
            "PhienAm": clean(row[2]),
            "TuLoai": clean(row[3]),
            "Nghia": clean(row[4]),
        })

    result = []

    for source in source_rows:
        hanzi = clean(source["ChuHan"])
        pinyin = clean(source["PhienAm"])

        group_key = (hanzi, pinyin_key(pinyin))
        source_codes = groups[group_key]

        existing = sql_by_hanzi.get(hanzi, [])

        # Neu khong tim thay trong SQL, van giu 1 dong.
        candidates = existing or [None]

        for item in candidates:
            sql_pinyin = (
                item["PhienAm"] if item else ""
            )

            same_pinyin = bool(
                item and
                pinyin_key(sql_pinyin) == pinyin_key(pinyin)
            )

            if same_pinyin:
                suggestion = (
                    "KIEM_TRA_NGHIA_TRUOC_KHI_TAI_SU_DUNG"
                )
            elif item:
                suggestion = (
                    "KHAC_PINYIN_CAN_XAC_MINH"
                )
            elif len(source_codes) > 1:
                suggestion = (
                    "TRUNG_NGUON_CAN_SO_SANH_NGHIA_TU_LOAI"
                )
            else:
                suggestion = (
                    "CHUA_CO_SQL_CAN_KIEM_TRA"
                )

            result.append({
                "MaTuHSK": clean(
                    source["MaTuHSK"]
                ),
                "ChuHan": hanzi,
                "PhienAmHSK3": pinyin,
                "TuLoaiHSK3": clean(
                    source["TuLoai"]
                ),
                "NghiaHSK3": clean(
                    source["NghiaTiengViet"]
                ),
                "LyDoCachLy": clean(
                    source.get("GhiChu")
                ),
                "MaTuVungSQL": (
                    item["MaTuVung"] if item else ""
                ),
                "PhienAmSQL": sql_pinyin,
                "TuLoaiSQL": (
                    item["TuLoai"] if item else ""
                ),
                "NghiaSQL": (
                    item["Nghia"] if item else ""
                ),
                "SoMucTrungTrongCSV": len(
                    source_codes
                ),
                "MaNguonTrungTrongCSV": (
                    " | ".join(source_codes)
                ),
                "HuongXuLyDeXuat": suggestion,
                "QuyetDinhCuoi": "",
                "GhiChuKiemDuyet": "",
            })

    if OUTPUT.exists():
        raise FileExistsError(
            f"Da ton tai file: {OUTPUT}\n"
            "Khong ghi de ket qua cu."
        )

    with OUTPUT.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS,
        )
        writer.writeheader()
        writer.writerows(result)

    print("\nKET QUA")
    print("So muc HSK3 duoc kiem tra:", len(source_rows))
    print("So ban ghi SQL lien quan:", len(sql_rows))
    print("So dong bao cao:", len(result))

    print("\nCHI TIET:")
    for row in source_rows:
        hanzi = clean(row["ChuHan"])
        print(
            f"  {row['MaTuHSK']} | "
            f"{hanzi} | {row['PhienAm']} | "
            f"{row['NghiaTiengViet']}"
        )

    print("\nBAO CAO:")
    print(OUTPUT)

    print("\nHOAN THANH - KHONG GHI SQL")


if __name__ == "__main__":
    main()
