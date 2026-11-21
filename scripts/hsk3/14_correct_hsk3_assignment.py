
# -*- coding: utf-8 -*-
"""
BUOC 49 - SUA PHAN BO TU VUNG HSK3

- Doc 973 muc tu o buoc 48.
- Sua nhung truong hop phan sai chu de da xac dinh.
- Bao toan MaMucNoiBo, MaTuHSK, MaTuVung.
- Giu lai trang thai CHUA_DUYET cho toan bo phan bo.
- Tao file moi, khong ghi de file cu.
- KHONG GHI SQL.
"""

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = DATA / "vocabulary_hsk3_assignment_complete.csv"
OUTPUT = DATA / "vocabulary_hsk3_assignment_corrected.csv"

# Ma nguon HSK3 -> (Chu Han kiem tra, bai hoc moi)
# Chi sua nhung tu da xac dinh ro chu de.
CORRECTIONS = {
    "L3-0001": ("爱心", 15),
    "L3-0003": ("安装", 18),
    "L3-0010": ("白菜", 9),
    "L3-0076": ("长城", 17),
    "L3-0097": ("城市", 11),
    "L3-0149": ("电视剧", 16),
    "L3-0150": ("电视台", 18),
    "L3-0421": ("空调", 18),
}

LESSON_NAMES = {
    1: "Kế hoạch học tập",
    2: "Cuộc sống ở trường",
    3: "Công việc và nghề nghiệp",
    4: "Sắp xếp thời gian",
    5: "Gia đình và bạn bè",
    6: "Giao tiếp và kết bạn",
    7: "Sức khỏe và cơ thể",
    8: "Thể thao và sinh hoạt",
    9: "Ăn uống và thói quen",
    10: "Mua sắm và tiêu dùng",
    11: "Thành phố và giao thông",
    12: "Du lịch và kế hoạch",
    13: "Thời tiết và mùa",
    14: "Thiên nhiên và môi trường",
    15: "Cảm xúc và cảm nhận",
    16: "Sở thích và giải trí",
    17: "Văn hóa và lễ hội",
    18: "Công nghệ và liên lạc",
    19: "Vấn đề và giải quyết",
    20: "Tương lai và ước mơ",
}


def main():
    print("=" * 65)
    print("BUOC 49 - SUA PHAN BO TU VUNG HSK3")
    print("=" * 65)

    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)

    if OUTPUT.exists():
        raise FileExistsError(
            f"File da ton tai: {OUTPUT}\n"
            "Khong ghi de ket qua truoc do."
        )

    with SOURCE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)

    if len(rows) != 973:
        raise ValueError("Du lieu HSK3 khong du 973 muc.")

    codes = [r["MaMucNoiBo"].strip() for r in rows]

    if len(set(codes)) != 973:
        raise ValueError("MaMucNoiBo bi trung.")

    if any(not r["MaTuVung"].strip() for r in rows):
        raise ValueError("Co muc chua co MaTuVung.")

    found = set()
    changed = []

    extra_fields = [
        "BaiHocTruocKhiSua",
        "TrangThaiChotPhanBo",
        "GhiChuChinhSua",
    ]

    for name in extra_fields:
        if name not in fields:
            fields.append(name)

    for row in rows:
        code = row["MaMucNoiBo"].strip()
        old = row["SoThuTuBaiDuKien"].strip()

        row["BaiHocTruocKhiSua"] = old
        row["TrangThaiChotPhanBo"] = "CHUA_DUYET"
        row["GhiChuChinhSua"] = ""

        if code not in CORRECTIONS:
            continue

        expected_hanzi, new_lesson = CORRECTIONS[code]

        if row["ChuHan"].strip() != expected_hanzi:
            raise ValueError(
                f"{code}: ChuHan khong khop du lieu nguon."
            )

        row["SoThuTuBaiDuKien"] = str(new_lesson)
        row["TenBaiDuKien"] = LESSON_NAMES[new_lesson]
        row["PhuongPhapPhanBo"] = "SUA_THU_CONG"
        row["MucCanKiemTra"] = "DA_DIEU_CHINH_CHO_DUYET"
        row["GhiChuChinhSua"] = (
            "Chuyen sang chu de phu hop voi nghia tu; "
            "can kiem duyet truoc khi import bai hoc."
        )

        found.add(code)

        if old != str(new_lesson):
            changed.append(
                (code, expected_hanzi, old, new_lesson)
            )

    if found != set(CORRECTIONS):
        raise RuntimeError(
            "Co ma can sua khong ton tai trong CSV."
        )

    counts = Counter()

    for row in rows:
        lesson = int(row["SoThuTuBaiDuKien"])

        if lesson not in LESSON_NAMES:
            raise ValueError("Bai hoc khong hop le.")

        counts[lesson] += 1

    if sum(counts.values()) != 973:
        raise RuntimeError("Phan bo bi thieu du lieu.")

    with OUTPUT.open(
        "x", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=fields
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\nKET QUA")
    print("Tong muc HSK3:", len(rows))
    print("So muc dieu chinh:", len(changed))

    print("\nCHI TIET:")
    for code, hanzi, old, new in changed:
        print(
            f"{code} | {hanzi} | Bai {old} -> Bai {new}"
        )

    print("\nSO TU THEO BAI SAU KHI SUA:")

    for number in range(1, 21):
        print(
            f"Bai {number:02}: "
            f"{counts[number]} muc"
        )

    print("\nFILE KET QUA:")
    print(OUTPUT)

    print("\nTOAN BO PHAN BO VAN CHUA DUYET")
    print("KHONG GHI SQL")


if __name__ == "__main__":
    main()
