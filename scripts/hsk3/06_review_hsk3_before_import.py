
# -*- coding: utf-8 -*-
"""
BUOC 41 - PHAN LOAI TU VUNG HSK3 TRUOC IMPORT

Dau vao:
vocabulary_hsk3_import_preview.csv

Ket qua:
1. Tu moi khong co canh bao.
2. Tu moi co canh bao can xem lai.
3. Tu trung / khac Pinyin can kiem tra.
4. Bao cao thong ke.

KHONG GHI SQL.
KHONG TU Y SUA NGHIA TIENG VIET.
"""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = DATA / "vocabulary_hsk3_import_preview.csv"

CLEAN_OUTPUT = DATA / "hsk3_new_without_warnings.csv"
REVIEW_OUTPUT = DATA / "hsk3_new_need_meaning_review.csv"
CONFLICT_OUTPUT = DATA / "hsk3_11_conflicts_detail.csv"
SUMMARY_OUTPUT = DATA / "hsk3_review_summary.json"

REQUIRED_COLUMNS = [
    "MaTuHSK",
    "ChuHan",
    "PhienAm",
    "NghiaTiengViet",
    "TuLoai",
    "HanhDongThucTe",
    "VanDeCanKiemTra",
    "GhiChu",
]


def clean(value):
    return str(value or "").strip()


def read_source():
    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"Khong tim thay: {SOURCE}"
        )

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []

        missing = [
            col for col in REQUIRED_COLUMNS
            if col not in columns
        ]

        if missing:
            raise ValueError(
                f"CSV thieu cac cot: {missing}"
            )

        rows = list(reader)

    if len(rows) != 973:
        raise ValueError(
            f"Can 973 muc, thuc te co {len(rows)}"
        )

    return rows, columns


def write_csv(path, rows, columns):
    with path.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=columns,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 65)
    print("BUOC 41 - PHAN LOAI TU VUNG HSK3")
    print("=" * 65)

    rows, columns = read_source()

    clean_words = []
    review_words = []
    conflicts = []
    reused = []

    for row in rows:
        action = clean(
            row["HanhDongThucTe"]
        )

        warning = clean(
            row["VanDeCanKiemTra"]
        )

        note = clean(
            row["GhiChu"]
        )

        if action == "INSERT_MOI_DU_KIEN":
            if warning or note:
                review_words.append(row)
            else:
                clean_words.append(row)

        elif action == "CAN_KIEM_TRA":
            conflicts.append(row)

        elif action == "TAI_SU_DUNG":
            reused.append(row)

        else:
            raise ValueError(
                "Hanh dong khong hop le: "
                f"{action}"
            )

    # Khong duoc bo sot bat ky muc tu nao.
    total = (
        len(clean_words)
        + len(review_words)
        + len(conflicts)
        + len(reused)
    )

    if total != len(rows):
        raise RuntimeError(
            "Phan loai bi thieu du lieu."
        )

    if len(clean_words) + len(review_words) != 950:
        raise RuntimeError(
            "So tu moi khong dung PREVIEW buoc 40."
        )

    if len(conflicts) != 11 or len(reused) != 12:
        raise RuntimeError(
            "So muc trung/da co khong dung buoc 40."
        )

    # Kiem tra truoc de khong ghi de file cu.
    outputs = [
        CLEAN_OUTPUT,
        REVIEW_OUTPUT,
        CONFLICT_OUTPUT,
        SUMMARY_OUTPUT,
    ]

    existing = [
        str(p) for p in outputs if p.exists()
    ]

    if existing:
        raise FileExistsError(
            "Da ton tai file dau ra:\n"
            + "\n".join(existing)
            + "\nHay doi ten file cu truoc khi chay lai."
        )

    write_csv(
        CLEAN_OUTPUT,
        clean_words,
        columns,
    )

    write_csv(
        REVIEW_OUTPUT,
        review_words,
        columns,
    )

    write_csv(
        CONFLICT_OUTPUT,
        conflicts,
        columns,
    )

    warning_counter = Counter()

    for row in rows:
        warnings = clean(
            row["VanDeCanKiemTra"]
        )

        for warning in warnings.split(";"):
            warning = warning.strip()
            if warning:
                warning_counter[warning] += 1

    summary = {
        "HSK": 3,
        "TongMuc": len(rows),
        "TuMoiKhongCanhBao": len(clean_words),
        "TuMoiCanRaSoat": len(review_words),
        "TuCanKiemTraTrungPinyin": len(conflicts),
        "TuTaiSuDung": len(reused),
        "SoMucCoCanhBaoNguon": sum(
            bool(clean(r["VanDeCanKiemTra"]))
            for r in rows
        ),
        "ThongKeCanhBao": dict(warning_counter),
        "DaGhiSQL": False,
    }

    with SUMMARY_OUTPUT.open(
        "x",
        encoding="utf-8",
    ) as f:
        json.dump(
            summary,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("\nKET QUA PHAN LOAI")
    print("Tong muc:", len(rows))
    print(
        "Tu moi khong canh bao:",
        len(clean_words),
    )
    print(
        "Tu moi can ra soat:",
        len(review_words),
    )
    print(
        "Tu trung/khac Pinyin:",
        len(conflicts),
    )
    print(
        "Tu tai su dung:",
        len(reused),
    )

    print("\nCHI TIET 11 MUC CAN KIEM TRA:")

    for row in conflicts:
        print(
            f"- {row['MaTuHSK']} | "
            f"{row['ChuHan']} | "
            f"{row['PhienAm']} | "
            f"{row['GhiChu']}"
        )

    print("\nCAC FILE DA TAO:")

    for path in outputs:
        print(path)

    print("\nHOAN THANH - KHONG GHI SQL")


if __name__ == "__main__":
    main()
