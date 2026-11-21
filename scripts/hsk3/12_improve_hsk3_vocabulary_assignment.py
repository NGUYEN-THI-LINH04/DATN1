
# -*- coding: utf-8 -*-
"""
BUOC 47 - CAI THIEN PHAN BO TU VUNG HSK3

Nguon tham chieu:
- 772 tu HSK2 da phan bai
- 973 muc HSK3 da mapping
- Goi y HSK3 o buoc 46

Phuong phap:
- Giu goi y cu
- So sanh tu Trung va nghia Viet voi HSK2
- Chi chap nhan goi y khi co diem tuong dong ro
- Phan con lai cho ra soat

KHONG GHI SQL.
"""

import csv
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

H2 = (
    ROOT / "scripts" / "hsk2" / "data"
    / "processed" / "vocabulary_hsk2_final_by_lesson.csv"
)

D3 = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = D3 / "vocabulary_hsk3_lesson_suggestions.csv"
OUTPUT = D3 / "vocabulary_hsk3_assignment_improved.csv"

# Anh xa chu de HSK2 sang 20 chu de HSK3.
# Day la anh xa noi dung gan nhat, khong phai
# quan he cap do HSK chinh thuc.
TOPIC_MAP = {
    1: 4,     # Sinh hoat -> Thoi gian
    2: 2,     # Hoc tap -> Truong hoc
    3: 3,     # Cong viec
    4: 5,     # Gia dinh
    5: 15,    # Ngoai hinh/tinh cach
    6: 13,    # Thoi tiet
    7: 7,     # Suc khoe
    8: 9,     # An uong
    9: 10,    # Mua sam
    10: 11,   # Vi tri
    11: 11,   # Giao thong
    12: 12,   # Du lich
    13: 8,    # The thao
    14: 16,   # So thich
    15: 17,   # Le hoi
    16: 19,   # Hoan thanh hanh dong
    17: 4,    # Dang dien ra
    18: 15,   # So sanh
    19: 20,   # Thay doi
    20: 19,   # Nguyen nhan/dieu kien
    21: 6,    # Giao tiep
    22: 17,   # Van hoa
    23: None, # On tap / dung chung
}

STOPWORDS = {
    "của", "và", "hoặc", "với", "trong", "một",
    "các", "những", "người", "được", "dùng",
    "chỉ", "cho", "cái", "để", "là", "như",
    "khi", "về", "từ", "này", "đó",
    "biến", "thể", "tiếng", "trung", "nghĩa",
    "cũng", "có", "thể", "làm",
}


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay: {path}"
        )

    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        return list(csv.DictReader(f))


def vietnamese_tokens(value):
    text = clean(value).casefold()
    text = re.sub(r"[^a-zA-ZÀ-ỹ0-9]+", " ", text)

    return {
        word for word in text.split()
        if len(word) >= 3 and word not in STOPWORDS
    }


def chinese_tokens(value):
    chars = re.findall(r"[\u3400-\u9fff]", clean(value))
    tokens = set(chars)

    tokens.update(
        "".join(chars[i:i + 2])
        for i in range(len(chars) - 1)
    )

    return tokens


def similarity(a, b):
    a_vi = vietnamese_tokens(a["NghiaTiengViet"])
    b_vi = vietnamese_tokens(b["NghiaTiengViet"])

    common_vi = len(a_vi & b_vi)

    a_zh = chinese_tokens(a["ChuHan"])
    b_zh = chinese_tokens(b["ChuHan"])

    common_zh = len(a_zh & b_zh)

    same_word = (
        clean(a["ChuHan"]) == clean(b["ChuHan"])
    )

    # Uu tien nghia, sau do tu/cum chu Han.
    return (
        common_vi * 2.0
        + common_zh * 0.5
        + (4.0 if same_word else 0.0)
    )


def main():
    print("=" * 68)
    print("BUOC 47 - CAI THIEN PHAN BO TU VUNG HSK3")
    print("=" * 68)

    hsk2 = read_csv(H2)
    hsk3 = read_csv(SOURCE)

    if len(hsk2) != 772:
        raise ValueError(
            f"HSK2 can 772 muc, hien co {len(hsk2)}"
        )

    if len(hsk3) != 973:
        raise ValueError(
            f"HSK3 can 973 muc, hien co {len(hsk3)}"
        )

    if OUTPUT.exists():
        raise FileExistsError(
            f"File da ton tai: {OUTPUT}"
        )

    reference = defaultdict(list)

    for row in hsk2:
        lesson = int(row["SoThuTuBai"])
        target = TOPIC_MAP.get(lesson)

        if target is not None:
            reference[target].append(row)

    result = []
    counts = Counter()

    for word in hsk3:
        original = clean(
            word.get("SoThuTuBaiGoiY")
        )

        if original:
            # Giu lai goi y tu buoc 46.
            selected = int(original)
            method = "GOI_Y_BUOC_46"
            score = ""
            second_score = ""
        else:
            ranked = []

            for lesson, examples in reference.items():
                # Lay diem trung binh cua toi da 3
                # tu HSK2 tuong dong nhat.
                scores = sorted(
                    (
                        similarity(word, example)
                        for example in examples
                    ),
                    reverse=True,
                )

                best = scores[:3]

                if best:
                    ranked.append((
                        sum(best) / len(best),
                        lesson,
                    ))

            ranked.sort(
                key=lambda x: (-x[0], x[1])
            )

            best_score, best_lesson = ranked[0]
            next_score = ranked[1][0]

            score = round(best_score, 2)
            second_score = round(next_score, 2)

            # Can diem du manh va khoang cach
            # voi chu de tiep theo du ro rang.
            if (
                best_score >= 3.0
                and best_score - next_score >= 1.0
            ):
                selected = best_lesson
                method = "GOI_Y_TU_HSK2"
            else:
                selected = ""
                method = "CHO_RA_SOAT"

        new_row = dict(word)
        new_row["SoThuTuBaiDeXuat"] = selected
        new_row["PhuongPhapGoiY"] = method
        new_row["DiemTuongDong"] = score
        new_row["DiemChuDeThuHai"] = second_score
        new_row["DaDuyetPhanBai"] = "CHUA"

        result.append(new_row)
        counts[method] += 1

    fields = list(result[0].keys())

    with OUTPUT.open(
        "x", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=fields
        )
        writer.writeheader()
        writer.writerows(result)

    print("\nKET QUA:")
    print("Tong HSK3:", len(result))
    print("Giu goi y buoc 46:", counts["GOI_Y_BUOC_46"])
    print("Goi y them tu HSK2:", counts["GOI_Y_TU_HSK2"])
    print("Con cho ra soat:", counts["CHO_RA_SOAT"])

    print("\nFILE:")
    print(OUTPUT)

    print("\nCHUA GHI SQL")
    print("CHUA CHOT PHAN BO BAI HOC")


if __name__ == "__main__":
    main()
