
# -*- coding: utf-8 -*-
"""
BUOC 46 - LAP KE HOACH BAI HOC HSK3

- Doc 973 tu HSK3 da co mapping.
- Tao 20 chu de bai hoc du kien.
- Goi y tu vung theo nghia tieng Viet.
- Khong chia deu, khong gan bua tu.
- Tu khong ro chu de se de CHO_PHAN_LOAI.
- Khong thay doi SQL.
"""

import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = DATA / "vocabulary_hsk3_import_result.csv"
LESSONS = DATA / "lessons_hsk3_draft.csv"
VOCAB = DATA / "vocabulary_hsk3_lesson_suggestions.csv"

# Moi chu de co: ten TQ, ten VN, tu khoa nghia VN.
# Chi la de xuat; KHONG phai ket qua phan loai chuan.
TOPICS = [
    ("我的学习计划", "Kế hoạch học tập",
     ["học tập", "bài học", "kiến thức", "ôn tập", "kỳ thi", "thi cử"]),
    ("校园生活", "Cuộc sống ở trường",
     ["trường học", "giáo viên", "học sinh", "lớp học", "giảng dạy"]),
    ("工作与职业", "Công việc và nghề nghiệp",
     ["công việc", "nghề nghiệp", "nhân viên", "công ty", "lương", "tuyển dụng"]),
    ("时间安排", "Sắp xếp thời gian",
     ["thời gian", "lịch trình", "đúng giờ", "trì hoãn", "hạn chót"]),
    ("家人与朋友", "Gia đình và bạn bè",
     ["gia đình", "bạn bè", "người thân", "cha mẹ", "họ hàng"]),
    ("认识新朋友", "Giao tiếp và kết bạn",
     ["giao tiếp", "quen biết", "giới thiệu", "trò chuyện", "kết bạn"]),
    ("健康与身体", "Sức khỏe và cơ thể",
     ["sức khỏe", "bệnh", "bác sĩ", "thuốc", "triệu chứng", "cơ thể"]),
    ("运动与生活", "Thể thao và sinh hoạt",
     ["thể thao", "vận động", "tập luyện", "bơi lội", "bóng đá"]),
    ("饮食与习惯", "Ăn uống và thói quen",
     ["thức ăn", "đồ ăn", "ăn uống", "nấu ăn", "bữa ăn", "thói quen"]),
    ("购物与消费", "Mua sắm và tiêu dùng",
     ["mua sắm", "giá cả", "thanh toán", "giảm giá", "cửa hàng", "khách hàng"]),
    ("城市与交通", "Thành phố và giao thông",
     ["giao thông", "xe buýt", "tàu điện", "đường phố", "ga tàu", "giao lộ"]),
    ("旅行与计划", "Du lịch và kế hoạch",
     ["du lịch", "khách sạn", "hành trình", "hộ chiếu", "tham quan"]),
    ("天气与季节", "Thời tiết và mùa",
     ["thời tiết", "nhiệt độ", "mùa xuân", "mùa hè", "mưa", "khí hậu"]),
    ("自然与环境", "Thiên nhiên và môi trường",
     ["thiên nhiên", "môi trường", "cây cối", "động vật", "ô nhiễm"]),
    ("情绪与感受", "Cảm xúc và cảm nhận",
     ["cảm xúc", "vui vẻ", "lo lắng", "buồn bã", "tức giận", "cảm thấy"]),
    ("兴趣与爱好", "Sở thích và giải trí",
     ["sở thích", "giải trí", "âm nhạc", "phim ảnh", "nghệ thuật"]),
    ("文化与节日", "Văn hóa và lễ hội",
     ["văn hóa", "lễ hội", "truyền thống", "phong tục", "ngày lễ"]),
    ("科技与交流", "Công nghệ và liên lạc",
     ["máy tính", "internet", "điện thoại", "phần mềm", "công nghệ", "tin nhắn"]),
    ("问题与解决", "Vấn đề và giải quyết",
     ["vấn đề", "giải quyết", "khó khăn", "sửa chữa", "xử lý"]),
    ("未来与梦想", "Tương lai và ước mơ",
     ["tương lai", "ước mơ", "mục tiêu", "thành công", "hy vọng"]),
]


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def write_csv(path, fields, rows):
    if path.exists():
        raise FileExistsError(
            f"File da ton tai: {path}\n"
            "Khong ghi de ket qua cu."
        )
    with path.open("x", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 65)
    print("BUOC 46 - KE HOACH BAI HOC HSK3")
    print("=" * 65)

    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        words = list(csv.DictReader(f))

    if len(words) != 973:
        raise ValueError(
            f"Phai co 973 muc HSK3, hien co {len(words)}."
        )

    ids = [clean(w.get("MaMucNoiBo")) for w in words]
    if (
        any(not item for item in ids)
        or len(ids) != len(set(ids))
        or any(not clean(w.get("MaTuVung")) for w in words)
    ):
        raise ValueError("Mapping HSK3 thieu ma hoac bi trung.")

    lessons = []
    for i, (zh, vi, keywords) in enumerate(TOPICS, 1):
        lessons.append({
            "SoThuTuBai": i,
            "TieuDeTiengTrung": zh,
            "TieuDeTiengViet": vi,
            "ChuDe": vi,
            "TrangThai": "ban_nhap",
        })

    suggestions = []
    counts = Counter()

    for word in words:
        meaning = clean(word.get("NghiaTiengViet")).casefold()
        scores = []

        for number, (_, _, keywords) in enumerate(TOPICS, 1):
            matched = [
                k for k in keywords
                if k.casefold() in meaning
            ]
            if matched:
                scores.append((number, len(matched), matched))

        scores.sort(key=lambda x: (-x[1], x[0]))

        # Chi tu dong goi y khi co 1 chu de ro rang
        # va khong dong diem voi chu de khac.
        if scores and (
            len(scores) == 1 or scores[0][1] > scores[1][1]
        ):
            lesson = scores[0][0]
            status = "GOI_Y_CAN_DUYET"
            matched_text = "; ".join(scores[0][2])
            counts[lesson] += 1
        else:
            lesson = ""
            status = "CHO_PHAN_LOAI"
            matched_text = ""

        suggestions.append({
            "MaMucNoiBo": word["MaMucNoiBo"],
            "MaTuHSK": word["MaTuHSK"],
            "MaTuVung": word["MaTuVung"],
            "ChuHan": word["ChuHan"],
            "PhienAm": word["PhienAm"],
            "TuLoai": word["TuLoai"],
            "NghiaTiengViet": word["NghiaTiengViet"],
            "SoThuTuBaiGoiY": lesson,
            "TuKhoaKhop": matched_text,
            "TrangThaiPhanLoai": status,
        })

    if LESSONS.exists() or VOCAB.exists():
        raise FileExistsError(
            "File dau ra da ton tai. Khong ghi de."
        )

    write_csv(
        LESSONS,
        ["SoThuTuBai", "TieuDeTiengTrung",
         "TieuDeTiengViet", "ChuDe", "TrangThai"],
        lessons,
    )

    write_csv(
        VOCAB,
        ["MaMucNoiBo", "MaTuHSK", "MaTuVung",
         "ChuHan", "PhienAm", "TuLoai",
         "NghiaTiengViet", "SoThuTuBaiGoiY",
         "TuKhoaKhop", "TrangThaiPhanLoai"],
        suggestions,
    )

    suggested = sum(counts.values())
    print("Tong muc HSK3:", len(words))
    print("So chu de du kien:", len(lessons))
    print("So muc co goi y chu de:", suggested)
    print("So muc cho phan loai:", len(words) - suggested)
    print("\nDanh sach chu de:")
    for number, (_, vi, _) in enumerate(TOPICS, 1):
        print(f"  Bai {number:02d}: {vi} ({counts[number]} goi y)")

    print("\nFile bai hoc:", LESSONS)
    print("File goi y tu vung:", VOCAB)
    print("\nCHUA GHI SQL - CHUA CHOT PHAN BO TU VUNG")


if __name__ == "__main__":
    main()
