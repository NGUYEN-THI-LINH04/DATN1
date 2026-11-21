
# -*- coding: utf-8 -*-
"""
BUOC 40 - PREVIEW IMPORT TU VUNG HSK3

- Doc 973 muc da chuan bi o buoc 39.
- Kiem tra lai bang TuVung trong SQL.
- Tai su dung tu da co dung ChuHan + Pinyin.
- Cach ly tu trung ChuHan khac Pinyin.
- Kiem tra nhung tu moi co the INSERT.
- Xuat bao cao CSV de kiem tra.

CHI DOC SQL - KHONG GHI DU LIEU.
"""

import csv
import re
import sys
import unicodedata

from collections import Counter, defaultdict
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = DATA / "vocabulary_hsk3_import_draft.csv"
OUTPUT = DATA / "vocabulary_hsk3_import_preview.csv"

FIELDS = [
    "MaTuHSK",
    "ChuHan",
    "PhienAm",
    "NghiaTiengViet",
    "TuLoai",
    "MaTuVungDaCo",
    "HanhDongThucTe",
    "TrangThaiKiemDuyet",
    "VanDeCanKiemTra",
    "GhiChu",
]


def clean(value):
    return re.sub(
        r"\s+", " ", str(value or "")
    ).strip()


def key(hanzi, pinyin):
    return (
        clean(hanzi),
        unicodedata.normalize(
            "NFC", clean(pinyin)
        ).casefold().replace(" ", "").replace("'", ""),
    )


def read_source():
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {SOURCE}"
        )

    with SOURCE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        rows = list(csv.DictReader(file))

    if len(rows) != 973:
        raise ValueError(
            f"Can 973 muc, nhan duoc {len(rows)}"
        )

    ids = [clean(r.get("MaTuHSK")) for r in rows]

    if (
        any(not x for x in ids)
        or len(ids) != len(set(ids))
    ):
        raise ValueError(
            "MaTuHSK rong hoac trung nhau."
        )

    return rows


def load_sql(cursor):
    cursor.execute("""
        SELECT MaTuVung, ChuHan, PhienAm
        FROM dbo.TuVung;
    """)

    exact = defaultdict(list)
    by_hanzi = defaultdict(list)

    for ma, hanzi, pinyin in cursor.fetchall():
        ma = int(ma)
        hanzi = clean(hanzi)

        exact[key(hanzi, pinyin)].append(ma)
        by_hanzi[hanzi].append(ma)

    return exact, by_hanzi


def main():
    print("=" * 65)
    print("BUOC 40 - PREVIEW IMPORT TU VUNG HSK3")
    print("=" * 65)
    print("CHI DOC SQL - KHONG INSERT / UPDATE / DELETE")

    rows = read_source()

    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cursor:
            exact, by_hanzi = load_sql(cursor)

    result = []
    counts = Counter()

    for row in rows:
        hanzi = clean(row.get("ChuHan"))
        pinyin = clean(row.get("PhienAm"))
        meaning = clean(row.get("NghiaTiengViet"))
        word_type = clean(row.get("TuLoai"))
        warnings = clean(row.get("VanDeCanKiemTra"))

        if not hanzi or not pinyin or not meaning:
            raise ValueError(
                f"Du lieu thieu: {row.get('MaTuHSK')}"
            )

        if (
            len(hanzi) > 100
            or len(pinyin) > 200
            or len(meaning) > 2000
            or len(word_type) > 100
        ):
            raise ValueError(
                f"Du lieu qua dai: {row.get('MaTuHSK')}"
            )

        matches = exact.get(key(hanzi, pinyin), [])
        hanzi_matches = by_hanzi.get(hanzi, [])

        ma_existing = ""
        note = ""

        if len(matches) == 1:
            action = "TAI_SU_DUNG"
            ma_existing = matches[0]

        elif len(matches) > 1:
            action = "CAN_KIEM_TRA"
            note = "Nhieu ban ghi khop ChuHan + Pinyin"

        elif hanzi_matches:
            action = "CAN_KIEM_TRA"
            note = "Trung ChuHan nhung khac Pinyin"

        else:
            action = "INSERT_MOI_DU_KIEN"

        counts[action] += 1

        result.append({
            "MaTuHSK": clean(row.get("MaTuHSK")),
            "ChuHan": hanzi,
            "PhienAm": pinyin,
            "NghiaTiengViet": meaning,
            "TuLoai": word_type,
            "MaTuVungDaCo": ma_existing,
            "HanhDongThucTe": action,
            "TrangThaiKiemDuyet": clean(
                row.get("TrangThaiKiemDuyet")
            ),
            "VanDeCanKiemTra": warnings,
            "GhiChu": note,
        })

    # Phat hien trung trong chinh CSV.
    csv_keys = Counter(
        key(r["ChuHan"], r["PhienAm"])
        for r in result
    )

    duplicate_keys = {
        k for k, n in csv_keys.items()
        if n > 1
    }

    if duplicate_keys:
        for row in result:
            if key(row["ChuHan"], row["PhienAm"]) in duplicate_keys:
                row["HanhDongThucTe"] = "CAN_KIEM_TRA"
                row["GhiChu"] = (
                    clean(row["GhiChu"])
                    + "; Trung ChuHan + Pinyin trong CSV"
                ).strip("; ")

        counts = Counter(
            r["HanhDongThucTe"]
            for r in result
        )

    # Khong ghi de file preview truoc do.
    if OUTPUT.exists():
        raise FileExistsError(
            f"File da ton tai: {OUTPUT}\n"
            "Hay doi ten file cu truoc khi chay lai."
        )

    with OUTPUT.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=FIELDS
        )
        writer.writeheader()
        writer.writerows(result)

    print("\nKET QUA KIEM TRA THUC TE")
    print("Tong muc HSK3:", len(result))

    for action, count in sorted(counts.items()):
        print(f"{action}: {count}")

    warnings_count = sum(
        bool(r["VanDeCanKiemTra"])
        for r in result
    )

    print("Muc co canh bao nguon:", warnings_count)
    print("\nBao cao:", OUTPUT)
    print("\nPREVIEW THANH CONG - KHONG GHI SQL")


if __name__ == "__main__":
    main()
