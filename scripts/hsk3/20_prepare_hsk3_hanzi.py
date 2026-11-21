
# -*- coding: utf-8 -*-
"""
BUOC 56 - CHUAN BI CHU HAN HSK3
DU AN MOC HAN

Nguon:
- 973 muc HSK3 da lien ket voi bai hoc
- Bang TuVung, TuVungBaiHoc, BaiHoc
- Bang ChuHan hien co
- Bang TuVungHSKChuan

Chuc nang:
1. Trich cac ky tu Han tu 973 muc HSK3.
2. Xac dinh ky tu da co trong ChuHan.
3. Xac dinh ky tu moi can bo sung.
4. Lay Pinyin va nghia tu nguon co san
   neu co tu don phu hop.
5. Xac dinh bai dau tien ky tu xuat hien.
6. Xuat CSV chuan bi xu ly tiep.

CHI DOC SQL.
KHONG INSERT / UPDATE / DELETE.
"""

import csv
import re
import sys

from collections import OrderedDict, Counter
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

DATA = (
    ROOT / "scripts" / "hsk3"
    / "data" / "processed"
)

NEW_FILE = DATA / "hanzi_hsk3_new_draft.csv"
EXISTING_FILE = DATA / "hanzi_hsk3_existing.csv"
ALL_FILE = DATA / "hanzi_hsk3_all_characters.csv"

COURSE_ID = 3
EXPECTED_VOCAB = 973

FIELDS = [
    "MaChuHanTam",
    "KyTu",
    "MaBaiHoc",
    "SoThuTuBai",
    "ThuTuTam",
    "Pinyin",
    "NghiaTiengViet",
    "SoNet",
    "MaBoThu",
    "CachGhiNho",
    "ViDuTiengTrung",
    "ViDuPinyin",
    "ViDuTiengViet",
    "MaTep",
    "MaNguon",
    "TrangThai",
    "MaChuHanDaCo",
    "TuVungDaiDien",
    "CacBaiXuatHien",
    "NguonPinyinNghia",
    "CanBoSung",
]


def clean(value):
    return re.sub(
        r"\s+", " ", str(value or "")
    ).strip()


def is_hanzi(char):
    code = ord(char)

    return (
        0x3400 <= code <= 0x4DBF
        or 0x4E00 <= code <= 0x9FFF
        or 0xF900 <= code <= 0xFAFF
        or 0x20000 <= code <= 0x2FA1F
    )


def write_csv(path, rows):
    if path.exists():
        raise FileExistsError(
            f"File da ton tai: {path}\n"
            "Khong ghi de file cu."
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


def load_hsk3_vocabulary(cursor):
    cursor.execute("""
        SELECT
            bh.MaBaiHoc,
            bh.SoThuTuBai,
            tvbh.ThuTu,
            tv.MaTuVung,
            tv.ChuHan,
            tv.PhienAm,
            tv.NghiaTiengViet
        FROM dbo.TuVungBaiHoc AS tvbh
        INNER JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc = tvbh.MaBaiHoc
        INNER JOIN dbo.TuVung AS tv
            ON tv.MaTuVung = tvbh.MaTuVung
        WHERE bh.MaKhoaHoc = ?
        ORDER BY
            bh.SoThuTuBai,
            tvbh.ThuTu,
            tv.MaTuVung;
    """, COURSE_ID)

    rows = cursor.fetchall()

    if len(rows) != EXPECTED_VOCAB:
        raise RuntimeError(
            f"HSK3 phai co {EXPECTED_VOCAB} "
            f"lien ket tu vung, hien co {len(rows)}."
        )

    return [
        {
            "lesson_id": int(r[0]),
            "lesson_number": int(r[1]),
            "word_order": int(r[2]),
            "word_id": int(r[3]),
            "hanzi": clean(r[4]),
            "pinyin": clean(r[5]),
            "meaning": clean(r[6]),
        }
        for r in rows
    ]


def load_existing_hanzi(cursor):
    cursor.execute("""
        SELECT
            MaChuHan,
            KyTu,
            Pinyin,
            NghiaTiengViet,
            MaBaiHoc
        FROM dbo.ChuHan
        WHERE KyTu IS NOT NULL;
    """)

    data = {}

    for row in cursor.fetchall():
        char = clean(row[1])

        if char and is_hanzi(char[0]) and len(char) == 1:
            data.setdefault(char, []).append({
                "id": int(row[0]),
                "pinyin": clean(row[2]),
                "meaning": clean(row[3]),
                "lesson_id": row[4],
            })

    return data


def load_single_character_sources(cursor):
    result = {}

    # Uu tien tu don trong nguon HSK3.
    cursor.execute("""
        SELECT
            ChuHan,
            PhienAm,
            NghiaTiengVietThamChieu
        FROM dbo.TuVungHSKChuan
        WHERE MaCapDo = 3
          AND LEN(ChuHan) = 1
        ORDER BY SoThuTuNguon, MaTuHSK;
    """)

    for char, pinyin, meaning in cursor.fetchall():
        char = clean(char)

        if len(char) != 1 or not is_hanzi(char):
            continue

        if char not in result:
            result[char] = {
                "pinyin": clean(pinyin),
                "meaning": clean(meaning),
                "source": "TuVungHSKChuan_HSK3",
            }

    # Bo sung tu don trong TuVung.
    cursor.execute("""
        SELECT
            ChuHan,
            PhienAm,
            NghiaTiengViet
        FROM dbo.TuVung
        WHERE LEN(ChuHan) = 1
        ORDER BY MaTuVung;
    """)

    for char, pinyin, meaning in cursor.fetchall():
        char = clean(char)

        if len(char) != 1 or not is_hanzi(char):
            continue

        result.setdefault(char, {
            "pinyin": clean(pinyin),
            "meaning": clean(meaning),
            "source": "TuVung",
        })

    return result


def collect_characters(words):
    characters = OrderedDict()

    for word in words:
        for char in word["hanzi"]:
            if not is_hanzi(char):
                continue

            if char not in characters:
                characters[char] = {
                    "occurrences": [],
                }

            characters[char]["occurrences"].append(
                word
            )

    return characters


def main():
    print("=" * 68)
    print("BUOC 56 - CHUAN BI CHU HAN HSK3")
    print("=" * 68)
    print("CHE DO: CHI DOC SQL")

    DATA.mkdir(parents=True, exist_ok=True)

    for path in (NEW_FILE, EXISTING_FILE, ALL_FILE):
        if path.exists():
            raise FileExistsError(
                f"Da co file: {path}\n"
                "Khong tu dong ghi de."
            )

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            words = load_hsk3_vocabulary(cursor)
            existing = load_existing_hanzi(cursor)
            single_sources = (
                load_single_character_sources(cursor)
            )

        connection.rollback()

    characters = collect_characters(words)

    all_rows = []
    new_rows = []
    existing_rows = []

    per_lesson = Counter()

    for index, (char, info) in enumerate(
        characters.items(),
        start=1,
    ):
        occurrences = sorted(
            info["occurrences"],
            key=lambda w: (
                w["lesson_number"],
                w["word_order"],
                w["word_id"],
            )
        )

        first = occurrences[0]

        lesson_numbers = sorted({
            w["lesson_number"]
            for w in occurrences
        })

        previous = existing.get(char, [])
        source = single_sources.get(char, {})

        # Neu da co chu Han, khong INSERT lai.
        if previous:
            pinyin = previous[0]["pinyin"]
            meaning = previous[0]["meaning"]
            source_name = "ChuHan_SQL"

        else:
            pinyin = source.get("pinyin", "")
            meaning = source.get("meaning", "")
            source_name = source.get("source", "")

        warnings = []

        if not pinyin:
            warnings.append("THIEU_PINYIN")

        if not meaning:
            warnings.append("THIEU_NGHIA")

        if len(previous) > 1:
            warnings.append("NHIEU_BAN_GHI_CHU_HAN_SQL")

        # Phan bo chu moi theo bai dau tien
        # ma ky tu xuat hien trong HSK3.
        per_lesson[first["lesson_number"]] += 1

        row = {
            "MaChuHanTam": f"H3-{index:04d}",
            "KyTu": char,
            "MaBaiHoc": first["lesson_id"],
            "SoThuTuBai": first["lesson_number"],
            "ThuTuTam": per_lesson[
                first["lesson_number"]
            ],
            "Pinyin": pinyin,
            "NghiaTiengViet": meaning,
            "SoNet": "",
            "MaBoThu": "",
            "CachGhiNho": "",
            "ViDuTiengTrung": first["hanzi"],
            "ViDuPinyin": "",
            "ViDuTiengViet": "",
            "MaTep": "",
            "MaNguon": "",
            "TrangThai": "ban_nhap",
            "MaChuHanDaCo": (
                previous[0]["id"] if previous else ""
            ),
            "TuVungDaiDien": first["hanzi"],
            "CacBaiXuatHien": ",".join(
                str(n) for n in lesson_numbers
            ),
            "NguonPinyinNghia": source_name,
            "CanBoSung": "; ".join(warnings),
        }

        all_rows.append(row)

        if previous:
            existing_rows.append(row)
        else:
            new_rows.append(row)

    if (
        len(all_rows)
        != len(new_rows) + len(existing_rows)
    ):
        raise RuntimeError(
            "Thong ke chu Han khong khop."
        )

    write_csv(NEW_FILE, new_rows)
    write_csv(EXISTING_FILE, existing_rows)
    write_csv(ALL_FILE, all_rows)

    print("\nKET QUA")
    print("Tong lien ket tu HSK3:", len(words))
    print("So ky tu Han khac nhau:", len(all_rows))
    print("Ky tu da co trong SQL:", len(existing_rows))
    print("Ky tu moi can bo sung:", len(new_rows))

    needs_review = sum(
        bool(row["CanBoSung"])
        for row in new_rows
    )

    print("Ky tu moi thieu Pinyin/nghia:", needs_review)

    print("\nFILE CHU MOI:")
    print(NEW_FILE)

    print("\nFILE CHU DA CO:")
    print(EXISTING_FILE)

    print("\nFILE TONG HOP:")
    print(ALL_FILE)

    print("\nHOAN THANH - KHONG GHI SQL")


if __name__ == "__main__":
    main()

