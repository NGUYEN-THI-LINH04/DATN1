
# -*- coding: utf-8 -*-
"""
BUOC 45 - RA SOAT NGU PHAP HSK3

- Doc 20 cau truc ngu phap HSK3 ban nhap.
- Doi chieu ten cau truc voi HSK2.
- Kiem tra thieu vi du / Pinyin / ban dich.
- Danh dau can xac minh cap do HSK3.
- Xuat CSV va bao cao JSON.

KHONG GHI SQL.
KHONG GHI DE FILE NGUON.
"""

import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

HSK3_DIR = ROOT / "scripts" / "hsk3" / "data" / "processed"
HSK2_DIR = ROOT / "scripts" / "hsk2" / "data" / "processed"

SOURCE = HSK3_DIR / "grammar_hsk3_draft.csv"
HSK2 = HSK2_DIR / "grammar_hsk2_draft.csv"

OUTPUT = HSK3_DIR / "grammar_hsk3_review.csv"
REPORT = HSK3_DIR / "grammar_hsk3_review_summary.json"


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize(value):
    value = unicodedata.normalize("NFKC", clean(value))
    value = value.casefold()
    value = re.sub(
        r"[\s…\.\-—–:：,，;；()（）]+",
        "",
        value,
    )
    return value


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay file: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        return list(csv.DictReader(f))


def main():
    print("=" * 68)
    print("BUOC 45 - RA SOAT NGU PHAP HSK3")
    print("=" * 68)

    hsk3 = read_csv(SOURCE)
    hsk2 = read_csv(HSK2)

    print("Ngu phap HSK3 ban nhap:", len(hsk3))
    print("Ngu phap HSK2 tham chieu:", len(hsk2))

    hsk2_titles = {}

    for item in hsk2:
        title = clean(item.get("TenCauTruc"))
        hsk2_titles.setdefault(
            normalize(title), []
        ).append(title)

    result = []
    duplicate_count = 0
    incomplete_count = 0
    seen = set()

    for item in hsk3:
        title = clean(item.get("TenCauTruc"))

        if not title:
            raise ValueError(
                "Phat hien cau truc khong co ten."
            )

        code = clean(item.get("MaNguPhapTam"))

        if not code or code in seen:
            raise ValueError(
                f"Ma ngu phap thieu hoac trung: {code}"
            )

        seen.add(code)

        issues = []

        if normalize(title) in hsk2_titles:
            issues.append("TRUNG_TEN_CAU_TRUC_HSK2")
            duplicate_count += 1

        required = [
            "MoTa",
            "CachDung",
            "ViDuTiengTrung",
            "ViDuPinyin",
            "ViDuTiengViet",
        ]

        missing = [
            field
            for field in required
            if not clean(item.get(field))
        ]

        if missing:
            issues.append(
                "THIEU_NOI_DUNG:" + ",".join(missing)
            )
            incomplete_count += 1

        # Chua co danh sach GF0025-2021 HSK3
        # de ket luan chinh xac cap do ngu phap.
        issues.append("CHUA_XAC_MINH_CHUAN_HSK3")

        row = dict(item)

        row["TrungTenVoiHSK2"] = (
            "CO"
            if normalize(title) in hsk2_titles
            else "KHONG"
        )

        row["GhiChuKiemTra"] = "; ".join(issues)
        row["DaXacMinhHSK3"] = "CHUA"
        row["QuyetDinh"] = "CHO_KIEM_DUYET"

        result.append(row)

    output_columns = list(result[0].keys()) if result else []

    # Khong ghi de file da co.
    for path in (OUTPUT, REPORT):
        if path.exists():
            raise FileExistsError(
                f"File da ton tai: {path}"
            )

    with OUTPUT.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=output_columns,
        )
        writer.writeheader()
        writer.writerows(result)

    summary = {
        "TongNguPhapHSK3BanNhap": len(hsk3),
        "TongNguPhapHSK2ThamChieu": len(hsk2),
        "TrungTenChinhXacVoiHSK2": duplicate_count,
        "ThieuNoiDung": incomplete_count,
        "DaXacMinhChuanHSK3": 0,
        "GhiChu": (
            "Doi chieu ten cau truc va tinh day du "
            "cua du lieu; chua phai kiem dinh "
            "cap do theo GF0025-2021."
        ),
        "DaGhiSQL": False,
    }

    with REPORT.open(
        "x",
        encoding="utf-8",
    ) as f:
        json.dump(
            summary,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("\nKET QUA")
    print("Tong ngu phap nhap:", len(hsk3))
    print("Trung ten voi HSK2:", duplicate_count)
    print("Thieu noi dung:", incomplete_count)
    print("Da xac minh chuan HSK3: 0")

    print("\nDa tao:")
    print(OUTPUT)
    print(REPORT)

    print("\nHOAN THANH - KHONG GHI SQL")


if __name__ == "__main__":
    main()
