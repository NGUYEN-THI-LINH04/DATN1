
# -*- coding: utf-8 -*-

"""
BUOC 22 - SUA 1 LOI PINYIN VA PHAN 114 NGU PHAP HSK4

Input:
  grammar_hsk4_teaching_final_114.csv
  lessons_hsk4_draft_20_21B.csv

Output:
  grammar_hsk4_corrected_22.csv
  grammar_hsk4_by_lesson_draft_22.csv
  grammar_hsk4_by_lesson_review_22.csv
  hsk4_grammar_summary_22.json

KHONG ghi SQL.
KHONG tao audio.
KHONG sua file goc.
"""

import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(r"D:\DATN1\scripts\hsk4\data\processed")

GRAMMAR_SOURCE = BASE / "grammar_hsk4_teaching_final_114.csv"
LESSON_SOURCE = BASE / "lessons_hsk4_draft_20_21B.csv"

CORRECTED = BASE / "grammar_hsk4_corrected_22.csv"
ASSIGNED = BASE / "grammar_hsk4_by_lesson_draft_22.csv"
REVIEW = BASE / "grammar_hsk4_by_lesson_review_22.csv"
SUMMARY = BASE / "hsk4_grammar_summary_22.json"

EXPECTED_GRAMMAR_HASH = (
    "9b3097dcc6e7a149e3d07fb07223226b5d15192aec6eb5a9ada77bfe8cd87e65"
)
EXPECTED_LESSON_HASH = (
    "32fb32a40a5aa8b60fd64556734e8a0be9b9a6902be865bf5cd5c11a244aa3ab"
)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def csv_content(fields, rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=fields,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig")


def safe_write(path, content):
    if path.exists():
        if path.read_bytes() == content:
            print("PASS: file da ton tai, noi dung giong:", path.name)
            return
        raise RuntimeError(
            "FAIL: file da ton tai va noi dung khac, "
            "khong ghi de: " + str(path)
        )
    with path.open("xb") as f:
        f.write(content)
    print("PASS: da tao", path.name)


# ==========================================================
# BANG GAN CHU DE CHO 76 MUC NGU PHAP CHUAN
#
# Day la PHUONG AN GIANG DAY, khong phai phan loai
# chinh thuc cua tieu chuan GF0025.
#
# Nhung cau truc tong hop duoc gan bai 20.
# Khong ep moi bai co so ngu phap bang nhau.
# ==========================================================

GROUPS = {
    1: [2, 16],
    2: [],
    3: [],
    4: [18, 58],
    5: [],
    6: [9, 10, 12, 14, 15, 17, 19, 20, 25, 27, 28, 32,
        42, 45, 56, 75],
    7: [11, 21, 23, 41],
    8: [],
    9: [],
    10: [],
    11: [],
    12: [13, 33],
    13: [1, 7, 8, 24, 26, 30, 46],
    14: [],
    15: [31],
    16: [],
    17: [],
    18: [],
    19: [3, 4, 5, 6, 29, 61, 62],
    20: [
        22, 34, 35, 36, 37, 38, 39, 40, 43, 44, 47,
        48, 49, 50, 51, 52, 53, 54, 55, 57, 59, 60,
        63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73,
        74, 76,
    ],
}

# Bai 20 gom cac mau cau, cau phuc va cach nhan manh.
# Bai 19 gom luong tu, pho tu muc do va bieu dat so.
# Bai 6 gom lien tu, giao tiep, dien dat quan diem.
# Bai 13 gom thoi gian, ke hoach, trinh tu hanh dong.


def make_mapping():
    mapping = {}
    for lesson, numbers in GROUPS.items():
        for number in numbers:
            if number in mapping:
                raise RuntimeError(
                    f"FAIL: muc GF4-{number:03d} bi gan trung."
                )
            mapping[number] = lesson

    missing = sorted(set(range(1, 77)) - set(mapping))
    extra = sorted(set(mapping) - set(range(1, 77)))

    if missing or extra:
        raise RuntimeError(
            f"FAIL: mapping 76 muc. Thieu={missing}, thua={extra}"
        )
    return mapping


def main():
    print("=" * 82)
    print("BUOC 22 - SUA DA VA CHIA 114 NGU PHAP HSK4")
    print("CHI XUAT CSV - KHONG GHI SQL - KHONG TAO AUDIO")
    print("=" * 82)

    print("\n[1] KIEM TRA SNAPSHOT")

    for path, expected in [
        (GRAMMAR_SOURCE, EXPECTED_GRAMMAR_HASH),
        (LESSON_SOURCE, EXPECTED_LESSON_HASH),
    ]:
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = sha256(path)
        print(path.name, actual)
        if actual != expected:
            raise RuntimeError("FAIL: SHA256 khong khop: " + path.name)

    print("PASS: hai file dau vao khop snapshot.")

    print("\n[2] DOC VA KIEM TRA NGU PHAP")

    grammar_fields, grammar = read_csv(GRAMMAR_SOURCE)
    lesson_fields, lessons = read_csv(LESSON_SOURCE)

    if len(grammar) != 114:
        raise RuntimeError(f"FAIL: can 114 ngu phap, co {len(grammar)}.")

    if len(lessons) != 20:
        raise RuntimeError(f"FAIL: can 20 bai, co {len(lessons)}.")

    grammar_ids = [r["MaDonViGiangDay"] for r in grammar]

    if len(set(grammar_ids)) != 114:
        raise RuntimeError("FAIL: trung MaDonViGiangDay.")

    lesson_map = {}

    for row in lessons:
        number = int(row["SoThuTuBai"])
        if number in lesson_map:
            raise RuntimeError("FAIL: trung so bai.")
        if row["MaKhoaHoc"] != "4":
            raise RuntimeError("FAIL: bai khong thuoc khoa HSK4.")
        if row["TrangThai"] != "ban_nhap":
            raise RuntimeError("FAIL: bai khong o trang thai ban_nhap.")
        lesson_map[number] = row

    if set(lesson_map) != set(range(1, 21)):
        raise RuntimeError("FAIL: bai hoc khong du 1-20.")

    mapping = make_mapping()

    print("PASS: 114 don vi duy nhat.")
    print("PASS: 20 bai HSK4 hop le.")
    print("PASS: 76/76 muc ngu phap da co phuong an gan bai.")

    print("\n[3] SUA DUY NHAT GF4-003-T01")

    corrected = [dict(r) for r in grammar]
    targets = [
        r for r in corrected
        if r["MaDonViGiangDay"] == "GF4-003-T01"
    ]

    if len(targets) != 1:
        raise RuntimeError("FAIL: khong tim thay dung 1 GF4-003-T01.")

    target = targets[0]

    if target["TenCauTruc"] != "打（dǎ）— lượng từ":
        raise RuntimeError("FAIL: tieu de goc khong dung du kien.")

    if target["ViDuPinyin"] != "Wǒ mǎi le yì dǎ qiānbǐ.":
        raise RuntimeError("FAIL: Pinyin vi du goc khong dung du kien.")

    if target["ViDuTiengTrung"] != "我买了一打铅笔。":
        raise RuntimeError("FAIL: vi du Hanzi khong dung du kien.")

    target["TenCauTruc"] = "打（dá）— lượng từ"
    target["ViDuPinyin"] = "Wǒ mǎi le yì dá qiānbǐ."

    # Khong thay doi trang thai duyet cua file goc.
    # Ghi chu ro day la hieu chinh phat am.
    print("PASS: 打（dǎ） -> 打（dá）")
    print("PASS: yì dǎ -> yì dá")
    print("PASS: chi sua 2 o cua 1 dong.")

    print("\n[4] GAN 114 NGU PHAP VAO 20 BAI")

    assigned = []
    counts = Counter()

    for row in corrected:
        item = dict(row)
        code = item["MaDonViGiangDay"]

        match = re.fullmatch(r"GF4-(\d{3})-T(\d{2})", code)
        if not match:
            raise RuntimeError("FAIL: ma khong dung mau: " + code)

        standard_number = int(match.group(1))

        if standard_number not in mapping:
            raise RuntimeError("FAIL: muc chua duoc gan: " + code)

        lesson_number = mapping[standard_number]
        lesson = lesson_map[lesson_number]

        item["SoThuTuBai"] = lesson_number
        item["MaBaiHocTam"] = lesson["MaBaiHocTam"]
        item["TieuDeBaiHoc"] = lesson["TieuDe"]

        item["LyDoGanBai22"] = (
            "GAN_THEO_NHOM_NGU_PHAP_VA_MUC_TIEU_BAI"
        )

        # Phan bo ngữ phap la de xuat su pham.
        # Can kiem tra tinh lien mach khi hoan thien giao trinh.
        item["CanReviewPhanBai22"] = "CO"

        item["GhiChuBuoc22"] = (
            "De xuat vi tri giang day; chua ghi SQL."
        )

        if code == "GF4-003-T01":
            item["GhiChuBuoc22"] = (
                "Da sua Pinyin luong tu 打 thanh da (thanh 2); "
                "de xuat vi tri giang day; chua ghi SQL."
            )

        assigned.append(item)
        counts[lesson_number] += 1

    # Giu cac muc tach lien nhau trong cung bai, va
    # theo thu tu chuan truoc khi gan ThuTuTrongBai.
    assigned.sort(
        key=lambda r: (
            int(r["SoThuTuBai"]),
            int(r["SoThuTuChuan"]),
            int(r["ThuTuTrongDiemChuan"]),
            r["MaDonViGiangDay"],
        )
    )

    for lesson_number in range(1, 21):
        order = 0
        for item in assigned:
            if item["SoThuTuBai"] == lesson_number:
                order += 1
                item["ThuTuTrongBai"] = order

    print("PASS: da gan 114/114 don vi.")

    print("\n[5] KIEM TRA KHONG MAT / KHONG TRUNG")

    if len(assigned) != 114:
        raise RuntimeError("FAIL: sai tong so dong.")

    if set(r["MaDonViGiangDay"] for r in assigned) != set(grammar_ids):
        raise RuntimeError("FAIL: mat/them MaDonViGiangDay.")

    # Kiem tra sau sua: chi dung 2 truong cua 1 dong khac.
    original_by_id = {
        r["MaDonViGiangDay"]: r for r in grammar
    }

    allowed_changes = {
        ("GF4-003-T01", "TenCauTruc"),
        ("GF4-003-T01", "ViDuPinyin"),
    }

    actual_changes = set()

    for item in corrected:
        code = item["MaDonViGiangDay"]
        original = original_by_id[code]

        for field in grammar_fields:
            if item[field] != original[field]:
                actual_changes.add((code, field))

    if actual_changes != allowed_changes:
        raise RuntimeError(
            f"FAIL: sua khac du kien: {sorted(actual_changes)}"
        )

    # Kiem tra thu tu trong bai lien tuc.
    for number in range(1, 21):
        orders = sorted(
            r["ThuTuTrongBai"]
            for r in assigned
            if r["SoThuTuBai"] == number
        )
        if orders != list(range(1, len(orders) + 1)):
            raise RuntimeError(f"FAIL: ThuTuTrongBai bai {number}.")

    print("PASS: 114/114 ma duoc bao toan.")
    print("PASS: chi sua dung 2 o Pinyin/tieu de.")
    print("PASS: ThuTuTrongBai lien tuc.")

    print("\n[6] THONG KE PHAN BAI")

    for number in range(1, 21):
        print(
            f"Bai {number:02d} | {counts[number]:3d} ngu phap | "
            f"{lesson_map[number]['TieuDe']}"
        )

    print("Tong ngu phap:", sum(counts.values()))

    # Mot so bai co the khong co ngu phap rieng.
    # Bai 20 nhieu cau truc vi la bai tong hop cu phap.
    if counts[20] > 30:
        print(
            "CANH BAO: Bai 20 tap trung nhieu ngu phap; "
            "can danh gia tai hoc truoc khi xuat ban."
        )

    print("\n[7] XUAT FILE")

    extra_fields = [
        "SoThuTuBai",
        "MaBaiHocTam",
        "TieuDeBaiHoc",
        "ThuTuTrongBai",
        "LyDoGanBai22",
        "CanReviewPhanBai22",
        "GhiChuBuoc22",
    ]

    output_fields = grammar_fields + [
        f for f in extra_fields if f not in grammar_fields
    ]

    summary = {
        "buoc": 22,
        "trang_thai": "BAN_NHAP_CAN_REVIEW_SU_PHAM",
        "tong_ngu_phap": 114,
        "so_muc_ngu_phap_chuan": 76,
        "so_bai": 20,
        "so_dong_sua_noi_dung": 1,
        "so_o_sua_noi_dung": 2,
        "ma_sua": "GF4-003-T01",
        "phan_bo": {str(n): counts[n] for n in range(1, 21)},
        "grammar_source_sha256": EXPECTED_GRAMMAR_HASH,
        "lessons_source_sha256": EXPECTED_LESSON_HASH,
        "ghi_sql": False,
        "tao_audio": False,
        "ghi_chu": (
            "Phan bai ngu phap la phuong an du thao; "
            "chua xac nhan tinh phu hop su pham."
        ),
    }

    safe_write(
        CORRECTED,
        csv_content(grammar_fields, corrected),
    )
    safe_write(
        ASSIGNED,
        csv_content(output_fields, assigned),
    )
    safe_write(
        REVIEW,
        csv_content(output_fields, assigned),
    )
    safe_write(
        SUMMARY,
        (json.dumps(
            summary, ensure_ascii=False, indent=2
        ) + "\n").encode("utf-8"),
    )

    print("\n" + "=" * 82)
    print("PASS: BUOC 22 HOAN THANH VE MAT KY THUAT")
    print("=" * 82)
    print("114/114 ngu phap da co bai tam.")
    print("76/76 muc ngu phap chuan da duoc bao phu.")
    print("Da sua dung GF4-003-T01: 打 da (thanh 2).")
    print("CORRECTED:", CORRECTED)
    print("ASSIGNED:", ASSIGNED)
    print("SHA256:", sha256(ASSIGNED))
    print("REVIEW:", REVIEW)
    print("SUMMARY:", SUMMARY)
    print("KHONG GHI SQL.")
    print("KHONG TAO AUDIO.")
    print("CHUA DUYET PHAN BAI DE XUAT BAN.")
    print("=" * 82)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nFAIL:", exc)
        raise SystemExit(1)
