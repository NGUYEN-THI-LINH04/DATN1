
# -*- coding: utf-8 -*-

"""
BUOC 22A - BIEN TAP LAI VI TRI GIANG DAY 114 NGU PHAP HSK4

Nguon:
    grammar_hsk4_by_lesson_draft_22.csv

Ket qua:
    grammar_hsk4_by_lesson_draft_22A.csv
    grammar_hsk4_by_lesson_changes_22A.csv
    hsk4_grammar_summary_22A.json

- Gan tung ma ngu phap bang bang phan bai tuong minh.
- Khong chia deu bang thuat toan.
- Khong thay doi noi dung ngu phap, vi du hay Pinyin.
- Giu nguyen sua loi 打（dá）.
- Khong ghi SQL, khong tao audio.
"""

import csv
import hashlib
import io
import json
import re

from collections import Counter
from pathlib import Path


BASE = Path(r"D:\DATN1\scripts\hsk4\data\processed")

SOURCE = BASE / "grammar_hsk4_by_lesson_draft_22.csv"

OUTPUT = BASE / "grammar_hsk4_by_lesson_draft_22A.csv"
CHANGES = BASE / "grammar_hsk4_by_lesson_changes_22A.csv"
SUMMARY = BASE / "hsk4_grammar_summary_22A.json"

EXPECTED_SHA256 = (
    "829575561fe1ffed9cd8616d24ce573767911b647a3e55e831b8732a644a1af2"
)


# ==========================================================
# BANG PHAN BAI 22A
#
# Ma rut gon:
#   002-01 = GF4-002-T01
#   038-02 = GF4-038-T02
#
# Moi ma xuat hien CHINH XAC MOT LAN.
# ==========================================================

LESSON_GROUPS = {

    # Bai 1: Con nguoi va quan he
    1: """
        002-01 016-01 041-02 021-01 011-02
    """,

    # Bai 2: Gia dinh va cuoc song
    2: """
        003-05 004-04 004-05 023-01 044-01
    """,

    # Bai 3: Hoc tap va giao duc
    3: """
        007-05 008-01 008-02
        028-01 045-01 026-01
    """,

    # Bai 4: Cong viec va nghe nghiep
    4: """
        018-01 032-01 017-01
        019-01 019-02 031-01
    """,

    # Bai 5: Kinh doanh va tai chinh
    5: """
        003-06 004-01 006-01
        061-01 062-04
    """,

    # Bai 6: Giao tiep va quan diem
    6: """
        014-01 015-01 012-01
        025-01 042-01 012-05
    """,

    # Bai 7: Cam xuc va tinh cach
    7: """
        011-01 012-02 012-03
        012-04 005-01 005-02
    """,

    # Bai 8: Suc khoe va y te
    8: """
        004-03 004-07 037-01
        035-01 065-01
    """,

    # Bai 9: Sinh hoat va dich vu
    9: """
        004-02 040-01 040-02
        036-01 038-02 039-01
    """,

    # Bai 10: An uong va mua sam
    10: """
        003-01 003-02 003-03
        003-04 004-06 005-03
    """,

    # Bai 11: Giao thong va du lich
    11: """
        007-02 007-03 024-01
        038-03 013-01
    """,

    # Bai 12: Dia diem va phuong huong
    12: """
        033-01 030-01 034-01
        068-01 070-01
    """,

    # Bai 13: Thoi gian va ke hoach
    13: """
        001-01 007-01 007-04
        046-01 058-01 056-01
    """,

    # Bai 14: Thien nhien va moi truong
    14: """
        020-01 020-02 047-01
        049-01 050-01
    """,

    # Bai 15: Cong nghe va Internet
    15: """
        020-06 020-07 027-01
        048-01 038-01
    """,

    # Bai 16: Van hoa va nghe thuat
    16: """
        020-05 020-08 043-01
        063-01 064-01 066-01
    """,

    # Bai 17: The thao va giai tri
    17: """
        041-01 075-01 067-01
        073-01 074-01
    """,

    # Bai 18: Xa hoi va phap luat
    18: """
        020-04 051-01 052-01
        053-01 054-01 057-01
    """,

    # Bai 19: So luong va so sanh
    19: """
        029-01 062-01 062-02
        062-03 009-01 010-01
    """,

    # Bai 20: Tong hop va dien dat nang cao
    20: """
        020-03 022-01 055-01
        059-01 060-01 069-01
        071-01 072-01 076-01
    """,
}


def sha256(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)

    return h.hexdigest()


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def csv_bytes(fields, rows):
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
            "FAIL: file da ton tai nhung noi dung khac. "
            "Khong ghi de: " + str(path)
        )

    with path.open("xb") as f:
        f.write(content)

    print("PASS: da tao", path.name)


def build_mapping():
    mapping = {}

    for lesson_number, raw_codes in LESSON_GROUPS.items():

        if lesson_number not in range(1, 21):
            raise RuntimeError("FAIL: so bai ngoai 1-20.")

        for short_code in raw_codes.split():

            if not re.fullmatch(r"\d{3}-\d{2}", short_code):
                raise RuntimeError(
                    "FAIL: ma rut gon sai: " + short_code
                )

            standard, teaching = short_code.split("-")

            full_code = (
                f"GF4-{standard}-T{teaching}"
            )

            if full_code in mapping:
                raise RuntimeError(
                    "FAIL: trung mapping: " + full_code
                )

            mapping[full_code] = lesson_number

    return mapping


def main():
    print("=" * 80)
    print("BUOC 22A - PHAN LAI 114 NGU PHAP HSK4")
    print("KHONG GHI SQL - KHONG TAO AUDIO")
    print("=" * 80)

    # ------------------------------------------------------
    # 1. Snapshot
    # ------------------------------------------------------

    print("\n[1] KIEM TRA SNAPSHOT")

    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)

    actual_hash = sha256(SOURCE)
    print("SHA256:", actual_hash)

    if actual_hash != EXPECTED_SHA256:
        raise RuntimeError(
            "FAIL: file Step22 khong khop snapshot."
        )

    print("PASS: snapshot Step22 hop le.")

    # ------------------------------------------------------
    # 2. Read
    # ------------------------------------------------------

    print("\n[2] DOC DU LIEU")

    fields, source_rows = read_csv(SOURCE)

    if len(source_rows) != 114:
        raise RuntimeError(
            f"FAIL: can 114 dong, co {len(source_rows)}."
        )

    ids = [
        row["MaDonViGiangDay"]
        for row in source_rows
    ]

    if len(set(ids)) != 114:
        raise RuntimeError("FAIL: trung ma ngu phap.")

    print("PASS: 114 ma ngu phap duy nhat.")

    # ------------------------------------------------------
    # 3. Mapping validation
    # ------------------------------------------------------

    print("\n[3] KIEM TRA BANG PHAN BAI")

    mapping = build_mapping()

    missing = sorted(set(ids) - set(mapping))
    extra = sorted(set(mapping) - set(ids))

    if missing or extra:
        raise RuntimeError(
            "FAIL: mapping khong khop 114 ma.\n"
            f"Thieu: {missing}\n"
            f"Thua: {extra}"
        )

    if len(mapping) != 114:
        raise RuntimeError("FAIL: mapping khong du 114.")

    print("PASS: mapping 114/114, khong thieu, khong trung.")

    # ------------------------------------------------------
    # 4. Lay ten bai tu chinh file Step22
    # ------------------------------------------------------

    print("\n[4] KIEM TRA TEN 20 BAI")

    titles = {}

    for row in source_rows:
        number = int(row["SoThuTuBai"])
        title = row["TieuDeBaiHoc"]

        if number in titles and titles[number] != title:
            raise RuntimeError(
                f"FAIL: tieu de bai {number} khong nhat quan."
            )

        titles[number] = title

    # Step22 co 11 bai trong, nen khong the lay du
    # ten 20 bai tu file ngu phap.
    # Khai bao dung bo ten bai cua HSK4.
    official_titles = {
        1: "人与关系 - Con người và các mối quan hệ",
        2: "家庭与生活 - Gia đình và cuộc sống",
        3: "学习让我们进步 - Học tập và giáo dục",
        4: "工作与职业 - Công việc và nghề nghiệp",
        5: "商业与金钱 - Kinh doanh và tài chính",
        6: "表达自己的看法 - Giao tiếp và quan điểm",
        7: "心情与性格 - Cảm xúc, tính cách và thái độ",
        8: "健康最重要 - Sức khỏe và y tế",
        9: "日常生活与服务 - Sinh hoạt hằng ngày và dịch vụ",
        10: "吃饭与购物 - Ăn uống, mua sắm và tiêu dùng",
        11: "出发吧！ - Giao thông và du lịch",
        12: "城市、地点与方向 - Thành phố, địa điểm và phương hướng",
        13: "时间、计划与变化 - Thời gian, kế hoạch và thay đổi",
        14: "天气、自然与环境 - Thời tiết, thiên nhiên và môi trường",
        15: "科技改变生活 - Khoa học, công nghệ và Internet",
        16: "文化、艺术与媒体 - Văn hóa, nghệ thuật và truyền thông",
        17: "运动与休闲 - Thể thao và giải trí",
        18: "社会、法律与安全 - Xã hội, pháp luật và an toàn",
        19: "数量、程度与比较 - Số lượng, mức độ và so sánh",
        20: "把话说清楚 - Từ chức năng và diễn đạt tổng hợp",
    }

    for number, title in titles.items():
        if official_titles[number] != title:
            raise RuntimeError(
                f"FAIL: tieu de bai {number} khong khop Step22."
            )

    print("PASS: tieu de cac bai da co ngu phap khop.")

    # ------------------------------------------------------
    # 5. Assign
    # ------------------------------------------------------

    print("\n[5] PHAN BAI 22A")

    rows = []
    changes = []

    for source_row in source_rows:
        row = dict(source_row)

        code = row["MaDonViGiangDay"]
        old_lesson = int(row["SoThuTuBai"])
        new_lesson = mapping[code]

        row["SoThuTuBai22"] = old_lesson
        row["SoThuTuBai22A"] = new_lesson

        row["SoThuTuBai"] = new_lesson
        row["MaBaiHocTam"] = f"H4-L{new_lesson:02d}"
        row["TieuDeBaiHoc"] = official_titles[new_lesson]

        row["LyDoGanBai22A"] = (
            "BIEN_TAP_THEO_TINH_HUONG_VA_TIEN_TRINH_HOC"
        )

        row["CanReviewPhanBai22A"] = "CO"

        row["GhiChuBuoc22A"] = (
            "Phuong an giang day tam; "
            "can duyet tinh phu hop truoc SQL."
        )

        rows.append(row)

        if old_lesson != new_lesson:
            changes.append(row)

    rows.sort(
        key=lambda r: (
            int(r["SoThuTuBai"]),
            int(r["SoThuTuChuan"]),
            int(r["ThuTuTrongDiemChuan"]),
            r["MaDonViGiangDay"],
        )
    )

    counts = Counter()

    for row in rows:
        lesson_number = int(row["SoThuTuBai"])
        counts[lesson_number] += 1
        row["ThuTuTrongBai"] = counts[lesson_number]

    print("PASS: da gan lai 114/114 ngu phap.")

    # ------------------------------------------------------
    # 6. Validate
    # ------------------------------------------------------

    print("\n[6] VALIDATE")

    if len(rows) != 114:
        raise RuntimeError("FAIL: khong du 114 dong.")

    if set(r["MaDonViGiangDay"] for r in rows) != set(ids):
        raise RuntimeError("FAIL: mat hoac them ma.")

    if set(counts) != set(range(1, 21)):
        raise RuntimeError("FAIL: co bai chua co ngu phap.")

    if not all(4 <= counts[n] <= 9 for n in range(1, 21)):
        raise RuntimeError(
            "FAIL: phan bo ngoai pham vi 4-9 ngu phap/bai."
        )

    # Dam bao KHONG sua noi dung ngu phap.
    content_fields = [
        "MaDonViGiangDay",
        "MaMucNguPhapChuan",
        "SoThuTuChuan",
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
        "MaNguon",
        "TrangThai",
        "TrangThaiKiemDuyet",
    ]

    original_by_id = {
        r["MaDonViGiangDay"]: r
        for r in source_rows
    }

    for row in rows:
        original = original_by_id[row["MaDonViGiangDay"]]

        for field in content_fields:
            if row[field] != original[field]:
                raise RuntimeError(
                    f"FAIL: thay doi noi dung {field} "
                    f"cua {row['MaDonViGiangDay']}"
                )

    target = [
        r for r in rows
        if r["MaDonViGiangDay"] == "GF4-003-T01"
    ]

    if len(target) != 1:
        raise RuntimeError("FAIL: thieu GF4-003-T01.")

    if target[0]["TenCauTruc"] != "打（dá）— lượng từ":
        raise RuntimeError("FAIL: mat ban sua 打（dá）.")

    if target[0]["ViDuPinyin"] != "Wǒ mǎi le yì dá qiānbǐ.":
        raise RuntimeError("FAIL: mat ban sua Pinyin yì dá.")

    print("PASS: 114/114 ma, khong trung, khong mat.")
    print("PASS: 20/20 bai co ngu phap.")
    print("PASS: noi dung va vi du khong doi.")
    print("PASS: giu nguyen 打（dá）.")

    # ------------------------------------------------------
    # 7. Distribution
    # ------------------------------------------------------

    print("\n[7] PHAN BO NGU PHAP 22A")

    for number in range(1, 21):
        print(
            f"Bai {number:02d} | "
            f"{counts[number]:2d} ngu phap | "
            f"{official_titles[number]}"
        )

    print("Tong:", sum(counts.values()))
    print("So ngu phap doi bai so voi 22:", len(changes))

    # ------------------------------------------------------
    # 8. Export
    # ------------------------------------------------------

    print("\n[8] XUAT FILE")

    extra_fields = [
        "SoThuTuBai22",
        "SoThuTuBai22A",
        "LyDoGanBai22A",
        "CanReviewPhanBai22A",
        "GhiChuBuoc22A",
    ]

    output_fields = fields + [
        f for f in extra_fields
        if f not in fields
    ]

    safe_write(
        OUTPUT,
        csv_bytes(output_fields, rows),
    )

    safe_write(
        CHANGES,
        csv_bytes(output_fields, changes),
    )

    summary = {
        "buoc": "22A",
        "trang_thai": "BAN_NHAP",
        "source_sha256": EXPECTED_SHA256,
        "tong_ngu_phap": len(rows),
        "so_bai": 20,
        "so_ngu_phap_doi_bai": len(changes),
        "phan_bo": {
            str(n): counts[n]
            for n in range(1, 21)
        },
        "output": str(OUTPUT),
        "output_sha256": sha256(OUTPUT),
        "changes": str(CHANGES),
        "changes_sha256": sha256(CHANGES),
        "ghi_sql": False,
        "tao_audio": False,
        "can_duyet_su_pham": True,
    }

    safe_write(
        SUMMARY,
        (
            json.dumps(
                summary,
                ensure_ascii=False,
                indent=2,
            ) + "\n"
        ).encode("utf-8"),
    )

    print("\n" + "=" * 80)
    print("PASS: BUOC 22A HOAN THANH VE MAT KY THUAT")
    print("=" * 80)
    print("114/114 ngu phap.")
    print("20/20 bai co ngu phap.")
    print("Giu nguyen sua loi 打（dá）.")
    print("OUTPUT:", OUTPUT)
    print("SHA256:", sha256(OUTPUT))
    print("CHANGES:", CHANGES)
    print("SUMMARY:", SUMMARY)
    print("KHONG GHI SQL.")
    print("KHONG TAO AUDIO.")
    print("PHAN BAI VAN LA BAN NHAP.")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nFAIL:", exc)
        raise SystemExit(1)
