
# -*- coding: utf-8 -*-
"""
BUOC 52 - PHAN NGU PHAP HSK3 VAO BAI HOC

Nguon:
- grammar_hsk3_review.csv
- lessons_hsk3_sql_result.csv

Ket qua:
- grammar_hsk3_by_lesson_draft.csv

KHONG GHI SQL.
KHONG GHI DE NGUON.
CHUA XAC MINH CAP DO NGU PHAP.
"""

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

GRAMMAR = DATA / "grammar_hsk3_review.csv"
LESSONS = DATA / "lessons_hsk3_sql_result.csv"

OUTPUT = DATA / "grammar_hsk3_by_lesson_draft.csv"

# Mapping noi dung de xuat, chua kiem duyet
GRAMMAR_TO_LESSON = {
    "G3-001": 19,  # Cau chu Ba
    "G3-002": 19,  # Cau bi dong Bei
    "G3-003": 6,   # Khong nhung... ma con
    "G3-004": 1,   # Chi khi... moi
    "G3-005": 20,  # Chi can... thi
    "G3-006": 19,  # Du... van
    "G3-007": 19,  # Da... thi
    "G3-008": 20,  # Bat ke... deu
    "G3-009": 15,  # Ngay ca... cung
    "G3-010": 20,  # Tha... con hon
    "G3-011": 10,  # Dat vat vao vi tri
    "G3-012": 15,  # Bat dau hanh dong
    "G3-013": 19,  # Tiep tuc hanh dong
    "G3-014": 15,  # Trong co ve
    "G3-015": 4,   # Kip / khong kip
    "G3-016": 4,   # Suýt nua
    "G3-017": 20,  # Co le / co kha nang
    "G3-018": 15,  # E rang
    "G3-019": 14,  # Nguyen nhan / ket qua
    "G3-020": 20,  # Theo su thay doi
}


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay file: {path}"
        )

    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        return list(csv.DictReader(file))


def main():
    print("=" * 68)
    print("BUOC 52 - PHAN NGU PHAP HSK3 VAO BAI")
    print("=" * 68)

    grammar_rows = read_csv(GRAMMAR)
    lesson_rows = read_csv(LESSONS)

    if len(grammar_rows) != 20:
        raise ValueError(
            "Can dung 20 cau truc ngu phap nhap."
        )

    if len(lesson_rows) != 20:
        raise ValueError(
            "Can dung 20 bai hoc HSK3."
        )

    lessons = {}

    for row in lesson_rows:
        number = int(row["SoThuTuBai"])

        if int(row["MaKhoaHoc"]) != 3:
            raise ValueError(
                "Phat hien bai hoc khong thuoc HSK3."
            )

        if number in lessons:
            raise ValueError(
                f"Trung thu tu bai {number}"
            )

        lessons[number] = {
            "id": int(row["MaBaiHoc"]),
            "title": row["TieuDe"],
        }

    if set(lessons) != set(range(1, 21)):
        raise ValueError("Danh sach bai hoc khong day du.")

    source_codes = [
        str(r["MaNguPhapTam"]).strip()
        for r in grammar_rows
    ]

    if (
        len(set(source_codes)) != 20
        or set(source_codes) != set(GRAMMAR_TO_LESSON)
    ):
        raise ValueError(
            "Danh sach ma ngu phap khong khop."
        )

    result = []
    counts = Counter()

    for row in grammar_rows:
        code = row["MaNguPhapTam"].strip()
        lesson_number = GRAMMAR_TO_LESSON[code]

        if not all(
            str(row.get(field, "")).strip()
            for field in (
                "TenCauTruc",
                "MoTa",
                "CachDung",
                "ViDuTiengTrung",
                "ViDuPinyin",
                "ViDuTiengViet",
            )
        ):
            raise ValueError(
                f"{code}: thieu noi dung ngu phap."
            )

        counts[lesson_number] += 1

        item = dict(row)

        item["MaBaiHoc"] = lessons[
            lesson_number
        ]["id"]

        item["SoThuTuBai"] = lesson_number
        item["TieuDeBaiHoc"] = lessons[
            lesson_number
        ]["title"]

        item["ThuTu"] = counts[lesson_number]
        item["TrangThai"] = "ban_nhap"
        item["TrangThaiPhanBo"] = "DE_XUAT"
        item["DaXacMinhHSK3"] = "CHUA"

        result.append(item)

    if OUTPUT.exists():
        raise FileExistsError(
            f"File da ton tai: {OUTPUT}"
        )

    fields = list(result[0].keys())

    with OUTPUT.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )
        writer.writeheader()
        writer.writerows(result)

    print("\nKET QUA")
    print("Tong cau truc:", len(result))
    print("So bai co ngu phap de xuat:", len(counts))
    print("So bai chua co ngu phap:", 20 - len(counts))

    for number in range(1, 21):
        print(
            f"Bai {number:02d}: "
            f"{counts[number]} cau truc"
        )

    print("\nFILE KET QUA:")
    print(OUTPUT)

    print("\nCHUA GHI SQL")
    print("CHUA KIEM DUYET CAP DO HSK3")


if __name__ == "__main__":
    main()
