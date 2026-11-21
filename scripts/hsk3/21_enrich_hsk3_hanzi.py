
# -*- coding: utf-8 -*-
"""
BUOC 57 - BO SUNG DU LIEU CHU HAN HSK3 TU UNIHAN

CHI DOC FILE, KHONG GHI SQL.
KHONG GHI DE CSV CU.
KHONG TU DONG DOAN NGHIA TIENG VIET.

Nguon:
- hanzi_hsk3_new_draft.csv
- Unihan.zip

Ket qua:
- hanzi_hsk3_unihan_enriched.csv
- hanzi_hsk3_need_review.csv
- hanzi_hsk3_unihan_report.json
"""

import csv
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = DATA / "hanzi_hsk3_new_draft.csv"

OUTPUT = DATA / "hanzi_hsk3_unihan_enriched.csv"
REVIEW = DATA / "hanzi_hsk3_need_review.csv"
REPORT = DATA / "hanzi_hsk3_unihan_report.json"

EXPECTED = 300


def clean(value):
    return str(value or "").strip()


def find_unihan():
    # Uu tien cac duong dan thuong su dung.
    candidates = [
        ROOT / "Unihan.zip",
        ROOT / "data_sources" / "Unihan.zip",
        ROOT / "data_sources" / "unihan" / "Unihan.zip",
        ROOT / "data_sources" / "unicode" / "Unihan.zip",
        ROOT / "data" / "Unihan.zip",
    ]

    found = [
        p for p in candidates if p.is_file()
    ]

    if not found:
        found = [
            p for p in ROOT.rglob("Unihan.zip")
            if ".venv" not in p.parts
            and "venv" not in p.parts
            and ".git" not in p.parts
        ]

    found = sorted(
        set(found),
        key=lambda p: str(p).lower(),
    )

    if not found:
        raise FileNotFoundError(
            "Khong tim thay Unihan.zip trong D:\\DATN1.\n"
            "Can su dung dung bo du lieu Unicode Unihan."
        )

    if len(found) > 1:
        print("Tim thay nhieu tep Unihan.zip:")
        for path in found:
            print(" -", path)

        raise RuntimeError(
            "Co nhieu nguon Unihan. "
            "Can chon mot nguon de tranh khac phien ban."
        )

    return found[0]


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        rows = list(reader)

    required = {
        "KyTu",
        "MaBaiHoc",
        "Pinyin",
        "NghiaTiengViet",
        "SoNet",
    }

    missing = required - set(fields)

    if missing:
        raise ValueError(
            f"CSV thieu cot: {sorted(missing)}"
        )

    if len(rows) != EXPECTED:
        raise ValueError(
            f"Can dung {EXPECTED} chu, "
            f"nhung file co {len(rows)}."
        )

    chars = [clean(r["KyTu"]) for r in rows]

    if any(len(char) != 1 for char in chars):
        raise ValueError(
            "Co dong khong chua dung mot ky tu Han."
        )

    if len(set(chars)) != EXPECTED:
        raise ValueError(
            "Co ky tu Han bi trung trong CSV."
        )

    return rows, fields


def read_unihan(path, target_chars):
    result = {
        char: {} for char in target_chars
    }

    code_to_char = {
        f"U+{ord(char):04X}": char
        for char in target_chars
    }

    wanted = {
        "kMandarin",
        "kTotalStrokes",
        "kRSUnicode",
    }

    with zipfile.ZipFile(path) as z:
        members = [
            name for name in z.namelist()
            if name.endswith(".txt")
            and (
                "Unihan_Readings" in name
                or "Unihan_DictionaryLikeData" in name
                or "Unihan_IRGSources" in name
            )
        ]

        if not members:
            raise RuntimeError(
                "Unihan.zip khong co cac tep du lieu can thiet."
            )

        for name in members:
            with z.open(name) as raw:
                for line in raw:
                    line = line.decode(
                        "utf-8-sig",
                        errors="replace",
                    ).strip()

                    if not line or line.startswith("#"):
                        continue

                    parts = line.split("\t", 2)

                    if len(parts) != 3:
                        continue

                    code, field, value = parts

                    if field not in wanted:
                        continue

                    char = code_to_char.get(code.upper())

                    if char:
                        result[char][field] = value.strip()

    return result


def normalize_pinyin(value):
    # Unihan kMandarin co the co dau thanh
    # hoac nhieu cach doc.
    return clean(value).lower()


def parse_strokes(value):
    values = clean(value).split()

    if (
        len(values) == 1
        and values[0].isdigit()
        and int(values[0]) > 0
    ):
        return values[0]

    return ""


def main():
    print("=" * 68)
    print("BUOC 57 - BO SUNG CHU HAN HSK3 TU UNIHAN")
    print("=" * 68)
    print("CHE DO: CHI DOC NGUON, KHONG GHI SQL")

    # Khong ghi de file da xu ly.
    for path in [OUTPUT, REVIEW, REPORT]:
        if path.exists():
            raise FileExistsError(
                f"File ket qua da ton tai: {path}\n"
                "Dung lai de tranh ghi de du lieu cu."
            )

    rows, original_fields = read_csv(SOURCE)

    unihan_path = find_unihan()

    print("\nNguon Unihan:")
    print(unihan_path)

    unihan = read_unihan(
        unihan_path,
        {clean(row["KyTu"]) for row in rows},
    )

    extra_fields = [
        "PinyinUnihan",
        "SoNetUnihan",
        "BoThuUnicode",
        "CanKiemTraPinyin",
        "TinhTrangDuLieu",
    ]

    fields = original_fields + [
        f for f in extra_fields
        if f not in original_fields
    ]

    enriched = []
    need_review = []

    statistics = {
        "tong_chu_moi": len(rows),
        "pinyin_bo_sung_tu_unihan": 0,
        "so_net_bo_sung_tu_unihan": 0,
        "con_thieu_pinyin": 0,
        "con_thieu_nghia_tieng_viet": 0,
        "con_thieu_so_net": 0,
        "can_kiem_tra": 0,
    }

    for original in rows:
        row = dict(original)
        char = clean(row["KyTu"])

        info = unihan.get(char, {})

        pinyin_unihan = normalize_pinyin(
            info.get("kMandarin", "")
        )

        strokes_unihan = parse_strokes(
            info.get("kTotalStrokes", "")
        )

        radical = clean(
            info.get("kRSUnicode", "")
        )

        row["PinyinUnihan"] = pinyin_unihan
        row["SoNetUnihan"] = strokes_unihan
        row["BoThuUnicode"] = radical

        old_pinyin = clean(row["Pinyin"])
        old_strokes = clean(row["SoNet"])

        # Chi dien Pinyin neu truoc do rong.
        # Neu nhieu cach doc, khong tu chon.
        if not old_pinyin and pinyin_unihan:
            if len(pinyin_unihan.split()) == 1:
                row["Pinyin"] = pinyin_unihan
                statistics[
                    "pinyin_bo_sung_tu_unihan"
                ] += 1

        # Chi dien so net neu chua co va Unihan
        # co duy nhat mot gia tri.
        if not old_strokes and strokes_unihan:
            row["SoNet"] = strokes_unihan
            statistics[
                "so_net_bo_sung_tu_unihan"
            ] += 1

        warnings = []

        if not clean(row["Pinyin"]):
            warnings.append("THIEU_PINYIN")
            statistics["con_thieu_pinyin"] += 1

        if not clean(row["NghiaTiengViet"]):
            warnings.append("THIEU_NGHIA_TIENG_VIET")
            statistics[
                "con_thieu_nghia_tieng_viet"
            ] += 1

        if not clean(row["SoNet"]):
            warnings.append("THIEU_SO_NET")
            statistics["con_thieu_so_net"] += 1

        # Chua khang dinh Pinyin cua tu ghep
        # la Pinyin dung cho chu don.
        if old_pinyin and pinyin_unihan:
            if old_pinyin.casefold() != pinyin_unihan.casefold():
                warnings.append(
                    "DOI_CHIEU_PINYIN"
                )

        if len(pinyin_unihan.split()) > 1:
            warnings.append("NHIEU_CACH_DOC")

        if radical and len(radical.split()) > 1:
            warnings.append("NHIEU_BO_THU_UNICODE")

        row["CanKiemTraPinyin"] = (
            "CO"
            if any(
                x in warnings
                for x in (
                    "DOI_CHIEU_PINYIN",
                    "NHIEU_CACH_DOC",
                    "THIEU_PINYIN",
                )
            )
            else "KHONG"
        )

        row["TinhTrangDuLieu"] = (
            ";".join(warnings)
            if warnings
            else "DU_TRUONG_CO_BAN"
        )

        enriched.append(row)

        if warnings:
            need_review.append(row)

    statistics["can_kiem_tra"] = len(need_review)
    statistics["nguon_unihan"] = str(unihan_path)

    # Hoan tat xu ly moi bat dau ghi file.
    for path, content in [
        (OUTPUT, enriched),
        (REVIEW, need_review),
    ]:
        with path.open(
            "x",
            encoding="utf-8-sig",
            newline="",
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=fields,
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(content)

    REPORT.write_text(
        json.dumps(
            statistics,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nKET QUA")
    for key, value in statistics.items():
        if key != "nguon_unihan":
            print(f"{key}: {value}")

    print("\nFILE DA DOI CHIEU:")
    print(OUTPUT)

    print("\nFILE CAN KIEM TRA:")
    print(REVIEW)

    print("\nBAO CAO:")
    print(REPORT)

    print("\nHOAN THANH")
    print("CHUA INSERT VAO SQL SERVER")
    print("CHUA XUAT BAN CHU HAN HSK3")


if __name__ == "__main__":
    main()
