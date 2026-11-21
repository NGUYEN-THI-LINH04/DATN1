
# -*- coding: utf-8 -*-
"""
BUOC 63 - GAN BO THU HSK3 TU UNIHAN VA SQL

Nguon:
- hanzi_hsk3_300_meanings_cleaned.csv
- hanzi_hsk3_unihan_enriched.csv
- dbo.BoThu

Ket qua:
- hanzi_hsk3_300_with_radicals.csv
- hanzi_hsk3_radicals_review.csv
- hanzi_hsk3_radicals_report.json

CHI DOC SQL.
KHONG INSERT/UPDATE/DELETE.
KHONG SUA NGHIA, PINYIN, SO NET.
"""

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = DATA / "hanzi_hsk3_300_meanings_cleaned.csv"
UNIHAN = DATA / "hanzi_hsk3_unihan_enriched.csv"

OUTPUT = DATA / "hanzi_hsk3_300_with_radicals.csv"
REVIEW = DATA / "hanzi_hsk3_radicals_review.csv"
REPORT = DATA / "hanzi_hsk3_radicals_report.json"


def clean(value):
    return str(value or "").strip()


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay file: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames or []
        rows = list(reader)

    if len(rows) != 300:
        raise ValueError(
            f"{path.name}: phai co 300 dong, "
            f"hien co {len(rows)}."
        )

    if "KyTu" not in fields:
        raise ValueError(
            f"{path.name}: thieu cot KyTu."
        )

    chars = [clean(r["KyTu"]) for r in rows]

    if len(set(chars)) != 300:
        raise ValueError(
            f"{path.name}: co chu Han trung."
        )

    if any(len(ch) != 1 for ch in chars):
        raise ValueError(
            f"{path.name}: co ky tu khong hop le."
        )

    return rows, fields


def load_sql_radicals(cursor):
    # Dung SoBoThu de tra MaBoThu.
    cursor.execute("""
        SELECT
            MaBoThu,
            SoBoThu,
            KyHieu,
            TenBoThu
        FROM dbo.BoThu
        WHERE SoBoThu IS NOT NULL
        ORDER BY SoBoThu, MaBoThu;
    """)

    mapping = defaultdict(list)

    for ma, so, ky_hieu, ten in cursor.fetchall():
        number = int(so)

        mapping[number].append({
            "id": int(ma),
            "symbol": clean(ky_hieu),
            "name": clean(ten),
        })

    return mapping


def parse_radical(value):
    """
    Unihan kRSUnicode vi du:
      85.4
      85.4 140.2

    Phan truoc dau cham la so bo thu Kangxi.
    Neu co nhieu so bo thu khac nhau:
    dung lai de kiem duyet.
    """
    value = clean(value)

    if not value:
        return [], "THIEU_BO_THU_UNIHAN"

    numbers = set()

    for token in value.split():
        match = re.fullmatch(
            r"(\d{1,3})'[.]([0-9]+)|"
            r"(\d{1,3})[.]([0-9]+)",
            token,
        )

        if not match:
            return [], "DINH_DANG_UNIHAN_KHONG_HOP_LE"

        number = int(match.group(1) or match.group(3))

        if not 1 <= number <= 214:
            return [], "SO_BO_THU_NGOAI_1_214"

        numbers.add(number)

    if len(numbers) != 1:
        return sorted(numbers), "NHIEU_BO_THU_UNIHAN"

    return sorted(numbers), ""


def write_csv(path, fields, rows):
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


def main():
    print("=" * 68)
    print("BUOC 63 - GAN BO THU HSK3")
    print("=" * 68)
    print("CHE DO: CHI DOC SQL")

    for path in (OUTPUT, REVIEW, REPORT):
        if path.exists():
            raise FileExistsError(
                f"Da co file ket qua: {path}\n"
                "Khong ghi de file cu."
            )

    source_rows, source_fields = read_csv(SOURCE)
    unihan_rows, unihan_fields = read_csv(UNIHAN)

    if "BoThuUnicode" not in unihan_fields:
        raise ValueError(
            "File Unihan thieu cot BoThuUnicode."
        )

    source_chars = {
        clean(r["KyTu"]) for r in source_rows
    }

    unihan_by_char = {
        clean(r["KyTu"]): r for r in unihan_rows
    }

    if source_chars != set(unihan_by_char):
        raise ValueError(
            "300 chu trong hai file khong khop."
        )

    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cursor:
            sql_radicals = load_sql_radicals(cursor)

        if not getattr(conn, "autocommit", False):
            conn.rollback()

    print("\nSo bo thu khac nhau trong SQL:",
          len(sql_radicals))

    extra_fields = [
        "SoBoThuUnicode",
        "MaBoThuSQL",
        "KyHieuBoThuSQL",
        "TenBoThuSQL",
        "TrangThaiGanBoThu",
    ]

    output_fields = list(source_fields)

    for field in extra_fields:
        if field not in output_fields:
            output_fields.append(field)

    completed = []
    review = []
    counts = Counter()

    for original in source_rows:
        row = dict(original)
        char = clean(row["KyTu"])

        uni = unihan_by_char[char]
        unicode_value = clean(
            uni.get("BoThuUnicode")
        )

        numbers, warning = parse_radical(
            unicode_value
        )

        ma_bo_thu = ""
        ky_hieu = ""
        ten_bo_thu = ""

        if not warning:
            number = numbers[0]
            matches = sql_radicals.get(number, [])

            if len(matches) == 1:
                ma_bo_thu = matches[0]["id"]
                ky_hieu = matches[0]["symbol"]
                ten_bo_thu = matches[0]["name"]

                warning = "KHOP_SQL"
                counts["khop_sql"] += 1

            elif not matches:
                warning = "CHUA_CO_BO_THU_TRONG_SQL"
                counts["khong_co_sql"] += 1

            else:
                warning = "TRUNG_SO_BO_THU_TRONG_SQL"
                counts["trung_sql"] += 1

        if warning != "KHOP_SQL":
            counts["can_kiem_tra"] += 1

        # Bao ve cot MaBoThu neu file nguon
        # da co ma bo thu truoc do.
        old_id = clean(row.get("MaBoThu", ""))

        if old_id and ma_bo_thu:
            if old_id != str(ma_bo_thu):
                raise RuntimeError(
                    f"{char}: MaBoThu cu={old_id} "
                    f"khac MaBoThu SQL={ma_bo_thu}."
                )

        row["SoBoThuUnicode"] = (
            numbers[0]
            if len(numbers) == 1
            else unicode_value
        )

        row["MaBoThuSQL"] = ma_bo_thu
        row["KyHieuBoThuSQL"] = ky_hieu
        row["TenBoThuSQL"] = ten_bo_thu
        row["TrangThaiGanBoThu"] = warning

        # Giu nguyen tat ca thong tin goc.
        for field in source_fields:
            if row.get(field) != original.get(field):
                raise RuntimeError(
                    f"{char}: da thay doi cot {field}"
                )

        completed.append(row)

        if warning != "KHOP_SQL":
            review.append(row)

    if len(completed) != 300:
        raise RuntimeError(
            "Tong so chu sau xu ly khong khop."
        )

    report = {
        "tong_chu_han": 300,
        "gan_duoc_ma_bo_thu_sql": counts["khop_sql"],
        "chua_co_bo_thu_sql": counts["khong_co_sql"],
        "trung_so_bo_thu_sql": counts["trung_sql"],
        "can_kiem_tra": counts["can_kiem_tra"],
        "ghi_sql": False,
    }

    write_csv(OUTPUT, output_fields, completed)
    write_csv(REVIEW, output_fields, review)

    with REPORT.open("x", encoding="utf-8") as f:
        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("\nKET QUA")
    for key, value in report.items():
        print(f"{key}: {value}")

    print("\nFILE TONG HOP:")
    print(OUTPUT)

    print("\nFILE CAN KIEM TRA:")
    print(REVIEW)

    print("\nHOAN THANH - KHONG GHI SQL")


if __name__ == "__main__":
    main()
