
# -*- coding: utf-8 -*-
"""
BUOC 58 - DOI CHIEU NGHIA TIENG VIET CHU HAN HSK3

- Chi lay nghia cua tu DON 1 chu Han.
- Khong suy nghia tu tu ghep.
- Khong dich may tu dong.
- Khong ghi SQL, khong ghi de file nguon.
- Neu nhieu nghia mau thuan: de kiem duyet.
"""

import csv
import json
import sys
import unicodedata
from collections import defaultdict
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"
SOURCE = DATA / "hanzi_hsk3_unihan_enriched.csv"
OUTPUT = DATA / "hanzi_hsk3_meanings_completed.csv"
REVIEW = DATA / "hanzi_hsk3_meanings_review.csv"
REPORT = DATA / "hanzi_hsk3_meanings_report.json"

EXPECTED = 300

HANZI_NAMES = (
    "KyTu", "ChuHan", "ChuGianThe",
    "GianThe", "TuTiengTrung",
)
MEANING_NAMES = (
    "NghiaTiengViet", "NghiaViet",
    "NghiaTV", "DinhNghiaTiengViet",
)
PINYIN_NAMES = ("Pinyin", "PhienAm")


def clean(value):
    return " ".join(str(value or "").split())


def quote(name):
    return "[" + name.replace("]", "]]") + "]"


def normalized_pinyin(value):
    value = unicodedata.normalize(
        "NFKC", clean(value).lower()
    )
    return "".join(value.split()).replace("u:", "ü")


def read_source():
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)

    with SOURCE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        rows = list(reader)

    required = {
        "KyTu", "Pinyin", "NghiaTiengViet"
    }
    if not required.issubset(fields):
        raise ValueError(
            f"Thieu cot: {sorted(required - set(fields))}"
        )

    chars = [clean(r["KyTu"]) for r in rows]
    if len(rows) != EXPECTED or len(set(chars)) != EXPECTED:
        raise ValueError(
            "File nguon phai co dung 300 chu khong trung."
        )

    if any(len(c) != 1 for c in chars):
        raise ValueError("Phat hien ky tu khong hop le.")

    return rows, fields


def choose_column(columns, names):
    lookup = {c.lower(): c for c in columns}
    for name in names:
        if name.lower() in lookup:
            return lookup[name.lower()]
    return None


def find_table_columns(cursor, table):
    cursor.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
    """, table)
    return [r[0] for r in cursor.fetchall()]


def collect_dictionary(cursor, table, chars, candidates):
    columns = find_table_columns(cursor, table)

    if not columns:
        print(f"[BO QUA] {table}: khong co bang.")
        return

    h = choose_column(columns, HANZI_NAMES)
    m = choose_column(columns, MEANING_NAMES)
    p = choose_column(columns, PINYIN_NAMES)

    if not h or not m:
        print(
            f"[BO QUA] {table}: "
            "khong xac dinh duoc cot chu Han / nghia Viet."
        )
        print("  Cac cot:", ", ".join(columns))
        return

    print(
        f"[NGUON] {table}: "
        f"chu={h}, nghia={m}, pinyin={p or 'khong co'}"
    )

    selected = (
        f"{quote(h)}, {quote(m)}, "
        + (quote(p) if p else "NULL")
    )

    # Chi truy van 300 ky tu can doi chieu.
    char_list = sorted(chars)
    placeholders = ",".join("?" for _ in char_list)

    sql = f"""
        SELECT {selected}
        FROM {quote('dbo')}.{quote(table)}
        WHERE {quote(h)} IN ({placeholders})
          AND {quote(m)} IS NOT NULL
    """

    cursor.execute(sql, *char_list)

    for hanzi, meaning, pinyin in cursor.fetchall():
        char = clean(hanzi)
        meaning = clean(meaning)
        reading = clean(pinyin)

        if len(char) != 1 or char not in chars or not meaning:
            continue

        candidates[char].append({
            "meaning": meaning,
            "pinyin": reading,
            "source": table,
        })


def choose_meaning(row, candidates):
    existing = clean(row["NghiaTiengViet"])

    if existing:
        return existing, "GIU_NGUYEN_CSV", ""

    reading = normalized_pinyin(row["Pinyin"])
    matches = []
    unmatched = 0

    for item in candidates:
        source_reading = normalized_pinyin(item["pinyin"])

        # Khong gan nghia neu cach doc nguon mau thuan.
        if source_reading and reading and source_reading != reading:
            unmatched += 1
            continue

        matches.append(item)

    if not matches:
        return "", "", (
            "KHONG_TIM_THAY_NGHIA_PHU_HOP"
            if not unmatched
            else "PINYIN_KHONG_KHOP_NGUON"
        )

    meanings = {
        item["meaning"].casefold(): item["meaning"]
        for item in matches
    }

    if len(meanings) != 1:
        return "", "", "NHIEU_NGHIA_CAN_DOI_CHIEU"

    meaning = next(iter(meanings.values()))
    sources = sorted({item["source"] for item in matches})

    return meaning, "+".join(sources), ""


def write_csv(path, fields, rows):
    with path.open(
        "x", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=fields, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 68)
    print("BUOC 58 - DOI CHIEU NGHIA CHU HAN HSK3")
    print("=" * 68)
    print("CHE DO: KHONG GHI SQL")

    for path in (OUTPUT, REVIEW, REPORT):
        if path.exists():
            raise FileExistsError(
                f"File da ton tai, khong ghi de: {path}"
            )

    rows, fields = read_source()
    chars = {r["KyTu"] for r in rows}
    candidates = defaultdict(list)

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            collect_dictionary(
                cursor, "MucTuDien", chars, candidates
            )
            collect_dictionary(
                cursor, "TuVung", chars, candidates
            )
        connection.rollback()

    extra = [
        "NguonNghiaBoSung",
        "CanKiemTraNghia",
        "SoNghiaUngVien",
    ]
    out_fields = fields + [
        c for c in extra if c not in fields
    ]

    original_missing = 0
    filled = 0
    completed = []
    review = []

    for original in rows:
        row = dict(original)
        char = clean(row["KyTu"])

        if not clean(row["NghiaTiengViet"]):
            original_missing += 1

        meaning, source, warning = choose_meaning(
            row, candidates[char]
        )

        if (
            not clean(original["NghiaTiengViet"])
            and meaning
        ):
            filled += 1

        row["NghiaTiengViet"] = meaning
        row["NguonNghiaBoSung"] = source
        row["CanKiemTraNghia"] = warning
        row["SoNghiaUngVien"] = len(candidates[char])

        completed.append(row)

        if warning or not meaning:
            review.append(row)

    report = {
        "tong_chu": len(rows),
        "thieu_nghia_ban_dau": original_missing,
        "bo_sung_tu_sql": filled,
        "con_thieu_nghia": sum(
            not clean(r["NghiaTiengViet"])
            for r in completed
        ),
        "can_kiem_tra_nghia": len(review),
        "ghi_sql": False,
    }

    write_csv(OUTPUT, out_fields, completed)
    write_csv(REVIEW, out_fields, review)

    with REPORT.open("x", encoding="utf-8") as f:
        json.dump(
            report, f, ensure_ascii=False, indent=2
        )

    print("\nKET QUA")
    for key, value in report.items():
        print(f"{key}: {value}")

    print("\nFILE DA DOI CHIEU:", OUTPUT)
    print("FILE CAN KIEM TRA:", REVIEW)
    print("BAO CAO:", REPORT)
    print("\nCHUA GHI SQL - CHUA XUAT BAN")


if __name__ == "__main__":
    main()
