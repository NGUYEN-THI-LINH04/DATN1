
# -*- coding: utf-8 -*-
"""
BUOC 59 - LAM LAI NGHIA CHU HAN HSK3 TU CVDICT

Nguon:
- hanzi_hsk3_meanings_completed.csv (300 chu)
- data_sources/cvdict/CVDICT.u8

Ket qua:
- hanzi_hsk3_cvdict_rebuilt.csv
- hanzi_hsk3_cvdict_review.csv
- hanzi_hsk3_cvdict_report.json

KHONG SUA SQL.
KHONG GHI DE FILE NGUON.
KHONG LAY NGHIA TU GHEP CHO CHU DON.
KHONG TU CHON KHI NGUON MO HO.
"""

import csv
import json
import re
import unicodedata
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = DATA / "hanzi_hsk3_meanings_completed.csv"
CVDICT = ROOT / "data_sources" / "cvdict" / "CVDICT.u8"

OUTPUT = DATA / "hanzi_hsk3_cvdict_rebuilt.csv"
REVIEW = DATA / "hanzi_hsk3_cvdict_review.csv"
REPORT = DATA / "hanzi_hsk3_cvdict_report.json"

EXPECTED = 300

# Chuan hoa thanh Pinyin so thanh:
# biāo -> biao1, lǜ -> lv4.
TONE_MARKS = {
    "ā": ("a", "1"), "á": ("a", "2"),
    "ǎ": ("a", "3"), "à": ("a", "4"),
    "ē": ("e", "1"), "é": ("e", "2"),
    "ě": ("e", "3"), "è": ("e", "4"),
    "ī": ("i", "1"), "í": ("i", "2"),
    "ǐ": ("i", "3"), "ì": ("i", "4"),
    "ō": ("o", "1"), "ó": ("o", "2"),
    "ǒ": ("o", "3"), "ò": ("o", "4"),
    "ū": ("u", "1"), "ú": ("u", "2"),
    "ǔ": ("u", "3"), "ù": ("u", "4"),
    "ǖ": ("v", "1"), "ǘ": ("v", "2"),
    "ǚ": ("v", "3"), "ǜ": ("v", "4"),
    "ń": ("n", "2"), "ň": ("n", "3"),
    "ǹ": ("n", "4"), "ḿ": ("m", "2"),
}


def clean(value):
    return " ".join(str(value or "").split())


def normalize_pinyin(value):
    s = unicodedata.normalize(
        "NFC", clean(value).lower()
    )
    s = s.replace("u:", "v").replace("ü", "v")

    tone = ""
    letters = []

    for char in s:
        if char in TONE_MARKS:
            base, number = TONE_MARKS[char]
            letters.append(base)
            tone = number
        elif char.isascii() and char.isalpha():
            letters.append(char)
        elif char in "12345":
            tone = char

    if not letters:
        return ""

    if not tone:
        tone = "5"

    return "".join(letters) + tone


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
        "KyTu", "Pinyin", "NghiaTiengViet",
        "SoNet", "MaBaiHoc",
    }

    if not required.issubset(fields):
        raise ValueError(
            f"CSV thieu cot: {sorted(required - set(fields))}"
        )

    chars = [clean(r["KyTu"]) for r in rows]

    if len(rows) != EXPECTED:
        raise ValueError(
            f"Phai co 300 dong, hien co {len(rows)}."
        )

    if len(set(chars)) != EXPECTED:
        raise ValueError("Co chu Han bi trung.")

    if any(len(c) != 1 for c in chars):
        raise ValueError("Co dong khong phai mot chu Han.")

    for row in rows:
        if not clean(row["Pinyin"]):
            raise ValueError(
                f"Thieu Pinyin: {row['KyTu']}"
            )
        if not clean(row["SoNet"]):
            raise ValueError(
                f"Thieu SoNet: {row['KyTu']}"
            )
        if not clean(row["MaBaiHoc"]):
            raise ValueError(
                f"Thieu MaBaiHoc: {row['KyTu']}"
            )

    return rows, fields


def read_cvdict(target_chars):
    if not CVDICT.is_file():
        raise FileNotFoundError(
            "Khong tim thay CVDICT.u8 trong du an:\n"
            + str(CVDICT)
        )

    # CVDICT la tep dinh dang CEDICT:
    # PHON_THE GIAN_THE [pin1 yin1] /nghia/
    pattern = re.compile(
        r"^(\S+)\s+(\S+)\s+"
        r"\[([^\]]+)\]\s+/(.*)/$"
    )

    dictionary = defaultdict(list)

    with CVDICT.open(
        "r", encoding="utf-8-sig"
    ) as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            match = pattern.match(line)
            if not match:
                continue

            traditional, simplified, py, meaning = (
                match.groups()
            )

            # Bat buoc la mot CHU DON gian the.
            if len(simplified) != 1:
                continue

            if simplified not in target_chars:
                continue

            meaning = clean(
                meaning.replace("/", "; ")
            )

            if not meaning:
                continue

            dictionary[simplified].append({
                "pinyin": clean(py),
                "pinyin_key": normalize_pinyin(py),
                "meaning": meaning,
                "traditional": traditional,
            })

    return dictionary


def unique_candidates(items):
    result = []
    seen = set()

    for item in items:
        key = (
            item["pinyin_key"],
            item["meaning"].casefold(),
        )

        if key not in seen:
            seen.add(key)
            result.append(item)

    return result


def process(rows, dictionary):
    completed = []
    review = []
    stats = Counter()

    for original in rows:
        row = dict(original)
        char = clean(row["KyTu"])
        target_py = normalize_pinyin(row["Pinyin"])

        all_candidates = dictionary.get(char, [])

        exact = unique_candidates([
            item for item in all_candidates
            if item["pinyin_key"] == target_py
        ])

        old_meaning = clean(
            row["NghiaTiengViet"]
        )

        if old_meaning:
            # Khong sua 118 nghia goc.
            status = "GIU_NGUYEN_NGHIA_CU"
            source_name = clean(
                row.get("NguonNghiaBoSung", "")
            ) or "CSV_HSK3"

            stats["giu_nguyen"] += 1

        elif len(exact) == 1:
            # Chi tu dong dien khi Pinyin khop
            # va chi co mot muc nghia duy nhat.
            row["NghiaTiengViet"] = exact[0]["meaning"]
            status = "CVDICT_KHOP_PINYIN_CAN_DUYET"
            source_name = "CVDICT.u8"

            stats["bo_sung"] += 1

        elif len(exact) > 1:
            status = "NHIEU_MUC_CUNG_PINYIN"
            source_name = "CVDICT.u8"
            stats["nhieu_muc"] += 1

        elif all_candidates:
            status = "KHONG_KHOP_PINYIN"
            source_name = "CVDICT.u8"
            stats["sai_khac_pinyin"] += 1

        else:
            status = "KHONG_TIM_THAY_CHU"
            source_name = ""
            stats["khong_tim_thay"] += 1

        row["NguonNghiaHienTai"] = source_name
        row["TrangThaiDoiChieuCVDICT"] = status
        row["SoMucCVDICT"] = len(all_candidates)
        row["SoMucCVDICTKhopPinyin"] = len(exact)

        # Giu de nguoi kiem duyet xem duoc
        # cac lua chon goc cua tu dien.
        row["UngVienNghiaCVDICT"] = " || ".join(
            f"[{item['pinyin']}] {item['meaning']}"
            for item in exact
        )

        row["CacCachDocCVDICT"] = " | ".join(
            sorted({
                item["pinyin"]
                for item in all_candidates
            })
        )

        if not clean(row["NghiaTiengViet"]):
            stats["con_thieu"] += 1

        # Dam bao cac cot goc khong bi sua.
        for field in (
            "KyTu", "Pinyin", "SoNet",
            "MaBaiHoc", "SoThuTuBai",
            "MaChuHanTam",
        ):
            if field in original:
                if row[field] != original[field]:
                    raise RuntimeError(
                        f"{char}: bi sua cot {field}"
                    )

        completed.append(row)

        if status != "GIU_NGUYEN_NGHIA_CU":
            review.append(row)

    return completed, review, stats


def write_csv(path, fields, rows):
    with path.open(
        "x", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fields,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 68)
    print("BUOC 59 - LAM LAI CHU HAN HSK3 TU CVDICT")
    print("=" * 68)
    print("CHI DOC NGUON - KHONG GHI SQL")

    for path in (OUTPUT, REVIEW, REPORT):
        if path.exists():
            raise FileExistsError(
                f"Da co file: {path}\n"
                "Khong ghi de file cu."
            )

    rows, fields = read_source()
    target = {clean(r["KyTu"]) for r in rows}

    dictionary = read_cvdict(target)

    completed, review, stats = process(
        rows, dictionary
    )

    additional = [
        "NguonNghiaHienTai",
        "TrangThaiDoiChieuCVDICT",
        "SoMucCVDICT",
        "SoMucCVDICTKhopPinyin",
        "UngVienNghiaCVDICT",
        "CacCachDocCVDICT",
    ]

    output_fields = fields + [
        name for name in additional
        if name not in fields
    ]

    report = {
        "tong_chu_moi": 300,
        "giu_nguyen_nghia_cu": stats["giu_nguyen"],
        "bo_sung_tu_cvdict": stats["bo_sung"],
        "nhieu_muc_cung_pinyin": stats["nhieu_muc"],
        "khong_khop_pinyin": stats["sai_khac_pinyin"],
        "khong_tim_thay_chu": stats["khong_tim_thay"],
        "con_thieu_nghia": stats["con_thieu"],
        "so_chu_can_duyet": len(review),
        "ghi_sql": False,
        "nguon": str(CVDICT),
    }

    write_csv(OUTPUT, output_fields, completed)
    write_csv(REVIEW, output_fields, review)

    with REPORT.open(
        "x", encoding="utf-8"
    ) as f:
        json.dump(
            report, f, ensure_ascii=False, indent=2
        )

    print("\nKET QUA:")
    for key, value in report.items():
        if key != "nguon":
            print(f"{key}: {value}")

    print("\nFILE TONG HOP:")
    print(OUTPUT)

    print("\nFILE DOI CHIEU:")
    print(REVIEW)

    print("\nHOAN THANH - CHUA GHI SQL")
    print("TOAN BO NOI DUNG MOI VAN CAN KIEM DUYET")


if __name__ == "__main__":
    main()
