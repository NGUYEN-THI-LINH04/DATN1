
# -*- coding: utf-8 -*-
"""
BUOC 60 - XU LY 55 CHU HAN CO NHIEU MUC NGHIA CVDICT

- Giu nguyen 245 chu da co nghia.
- Gop cac muc nghia CVDICT khop Pinyin cho 55 chu.
- Khong tu chon mot nghia khi co nhieu muc.
- Giu nguyen toan bo thong tin MaBaiHoc, Pinyin, SoNet.
- Tao du lieu nhap de kiem duyet.
- KHONG ghi SQL.
"""

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = DATA / "hanzi_hsk3_cvdict_rebuilt.csv"
OUTPUT = DATA / "hanzi_hsk3_300_meanings_draft.csv"
REVIEW = DATA / "hanzi_hsk3_55_multiple_meanings_review.csv"
REPORT = DATA / "hanzi_hsk3_meanings_final_report.json"

FIELDS_REQUIRED = {
    "KyTu",
    "MaBaiHoc",
    "Pinyin",
    "SoNet",
    "NghiaTiengViet",
    "TrangThaiDoiChieuCVDICT",
    "UngVienNghiaCVDICT",
}

def clean(value):
    return " ".join(str(value or "").split())


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        missing = FIELDS_REQUIRED - set(fields)

        if missing:
            raise ValueError(
                f"File thieu cot: {sorted(missing)}"
            )

        rows = list(reader)

    if len(rows) != 300:
        raise ValueError(
            f"Can 300 dong, thuc te {len(rows)}."
        )

    chars = [clean(r["KyTu"]) for r in rows]

    if len(set(chars)) != 300:
        raise ValueError("Co chu Han bi trung.")

    return rows, fields


def parse_candidates(value):
    """
    Dau vao:
    [pinyin] nghia A || [pinyin] nghia B

    Chi xoa nhan Pinyin dau moi muc.
    Giu nguyen noi dung nghia tieng Viet.
    """
    result = []
    seen = set()

    for raw in str(value or "").split(" || "):
        raw = clean(raw)

        if not raw:
            continue

        meaning = re.sub(
            r"^\[[^\]]+\]\s*",
            "",
            raw
        ).strip()

        if not meaning:
            continue

        key = meaning.casefold()

        if key not in seen:
            seen.add(key)
            result.append(meaning)

    return result


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
    print("BUOC 60 - HOAN THIEN NGHIA CHU HAN HSK3")
    print("=" * 68)
    print("CHE DO: KHONG GHI SQL")

    for path in (OUTPUT, REVIEW, REPORT):
        if path.exists():
            raise FileExistsError(
                f"Da ton tai: {path}\n"
                "Khong ghi de ket qua cu."
            )

    rows, fields = read_csv(SOURCE)

    additional = [
        "NghiaGopTuCVDICT",
        "TrangThaiKiemDuyet",
    ]

    out_fields = fields + [
        x for x in additional if x not in fields
    ]

    completed = []
    review = []
    stats = Counter()

    for original in rows:
        row = dict(original)
        char = clean(row["KyTu"])
        old_meaning = clean(row["NghiaTiengViet"])
        status = clean(
            row["TrangThaiDoiChieuCVDICT"]
        )

        for field in ("MaBaiHoc", "Pinyin", "SoNet"):
            if not clean(row[field]):
                raise ValueError(
                    f"{char}: thieu {field}"
                )

        if old_meaning:
            # Khong sua 245 nghia da co.
            row["NghiaGopTuCVDICT"] = ""
            row["TrangThaiKiemDuyet"] = (
                "GIU_NGUYEN_NGUON_CHUA_DUYET"
            )
            stats["giu_nguyen"] += 1

        elif status == "NHIEU_MUC_CUNG_PINYIN":
            meanings = parse_candidates(
                row["UngVienNghiaCVDICT"]
            )

            if len(meanings) < 2:
                raise ValueError(
                    f"{char}: du lieu nhieu muc "
                    "khong khop ung vien."
                )

            # Gop cac muc nghia, KHONG tu chon
            # mot nghia dai dien.
            proposed = "; ".join(meanings)

            row["NghiaTiengViet"] = proposed
            row["NghiaGopTuCVDICT"] = proposed
            row["TrangThaiKiemDuyet"] = (
                "CAN_DUYET_NGHIA_NHIEU_MUC"
            )

            review.append(row)
            stats["gop_nhieu_muc"] += 1

        else:
            raise ValueError(
                f"{char}: khong co nghia, "
                f"trang thai bat thuong: {status}"
            )

        for field in (
            "KyTu", "MaBaiHoc",
            "SoThuTuBai", "Pinyin",
            "SoNet", "MaChuHanTam"
        ):
            if field in original:
                if row[field] != original[field]:
                    raise RuntimeError(
                        f"{char}: thay doi {field}"
                    )

        completed.append(row)

    if stats["giu_nguyen"] != 245:
        raise RuntimeError(
            f"Du kien 245 chu da co nghia, "
            f"thuc te {stats['giu_nguyen']}."
        )

    if stats["gop_nhieu_muc"] != 55:
        raise RuntimeError(
            f"Du kien 55 chu can gop, "
            f"thuc te {stats['gop_nhieu_muc']}."
        )

    missing = sum(
        not clean(row["NghiaTiengViet"])
        for row in completed
    )

    if missing:
        raise RuntimeError(
            f"Van con {missing} chu thieu nghia."
        )

    report = {
        "tong_chu_hsk3_moi": 300,
        "giu_nguyen_nghia": 245,
        "gop_nghia_tu_cvdict": 55,
        "con_thieu_nghia": 0,
        "nghia_nhieu_muc_can_duyet": 55,
        "da_duyet_noi_dung": False,
        "ghi_sql": False,
    }

    write_csv(OUTPUT, out_fields, completed)
    write_csv(REVIEW, out_fields, review)

    with REPORT.open(
        "x", encoding="utf-8"
    ) as f:
        json.dump(
            report, f,
            ensure_ascii=False,
            indent=2
        )

    print("\nKET QUA")
    for key, value in report.items():
        print(f"{key}: {value}")

    print("\nFILE 300 CHU:")
    print(OUTPUT)

    print("\nFILE 55 CHU CAN DUYET:")
    print(REVIEW)

    print("\nHOAN THANH - CHUA GHI SQL")


if __name__ == "__main__":
    main()
