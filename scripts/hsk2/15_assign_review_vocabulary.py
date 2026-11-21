from pathlib import Path
import csv
import re


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = (
    DATA_DIR
    / "vocabulary_hsk2_need_lesson_review.csv"
)

OUTPUT_FILE = (
    DATA_DIR
    / "vocabulary_hsk2_review_assigned.csv"
)


LESSON_NAMES = {
    1: "Một ngày của tôi",
    2: "Cuộc sống học tập",
    3: "Công việc",
    4: "Gia đình và bạn bè",
    5: "Ngoại hình và tính cách",
    6: "Thời tiết và các mùa",
    7: "Sức khỏe",
    8: "Ăn uống",
    9: "Mua sắm",
    10: "Vị trí và khoảng cách",
    11: "Hỏi đường và giao thông",
    12: "Du lịch",
    13: "Thể thao",
    14: "Sở thích và cuối tuần",
    15: "Ngày lễ và sự kiện",
    16: "Hành động đã hoàn thành",
    17: "Hành động đang diễn ra",
    18: "So sánh",
    19: "Thay đổi và mức độ",
    20: "Nguyên nhân và điều kiện",
    21: "Liên lạc và giao tiếp",
    22: "Văn hóa và quan điểm",
    23: "Ôn tập và từ dùng chung",
}


# ============================================================
# CAC TU DA RA SOAT VA CO CHU DE RO
# ============================================================

MANUAL = {

    # --------------------------------------------------------
    # Bai 1 - sinh hoat / thoi gian
    # --------------------------------------------------------
    "从小": 1,
    "分钟": 1,
    "上周": 1,
    "下周": 1,
    "多久": 1,
    "不久": 1,
    "当时": 1,
    "那会儿": 1,
    "刚才": 1,
    "刚刚": 1,
    "好久": 1,
    "夜": 1,
    "随时": 1,
    "一会儿": 1,
    "周": 1,
    "习惯": 1,

    # --------------------------------------------------------
    # Bai 2 - hoc tap
    # --------------------------------------------------------
    "报名": 2,
    "级": 2,
    "院长": 2,
    "科": 2,
    "计算机": 2,
    "名单": 2,
    "生词": 2,
    "中级": 2,
    "背": 2,
    "重点": 2,
    "懂": 2,
    "懂得": 2,
    "举手": 2,
    "词": 2,
    "词语": 2,
    "句": 2,
    "音节": 2,
    "纸": 2,

    # --------------------------------------------------------
    # Bai 3 - cong viec
    # --------------------------------------------------------
    "办": 3,
    "商人": 3,
    "组": 3,
    "组长": 3,
    "小组": 3,
    "实习": 3,
    "作用": 3,
    "提出": 3,

    # --------------------------------------------------------
    # Bai 4 - gia dinh / con nguoi
    # --------------------------------------------------------
    "姓": 4,
    "姓名": 4,
    "一生": 4,
    "出生": 4,
    "大人": 4,
    "大家": 4,
    "人们": 4,
    "长大": 4,
    "主人": 4,
    "养": 4,

    # --------------------------------------------------------
    # Bai 5 - ngoai hinh / tinh cach / cam xuc
    # --------------------------------------------------------
    "好像": 5,
    "像": 5,
    "小（小王）": 5,
    "轻": 5,
    "怕": 5,
    "小心": 5,
    "熟": 5,
    "感到": 5,
    "感动": 5,
    "可怕": 5,
    "样子": 5,
    "不好意思": 5,
    "不满": 5,
    "心里": 5,
    "心中": 5,
    "放心": 5,
    "相信": 5,
    "信心": 5,
    "友好": 5,
    "个子": 5,
    "难看": 5,
    "难过": 5,

    # --------------------------------------------------------
    # Bai 6 - thoi tiet / tu nhien / dong vat
    # --------------------------------------------------------
    "狗": 6,
    "猫": 6,
    "鸟": 6,
    "动物": 6,
    "动物园": 6,
    "地球": 6,
    "天上": 6,
    "云": 6,
    "阴": 6,
    "凉快": 6,
    "零下": 6,
    "空气": 6,
    "星星": 6,
    "花": 6,
    "花园": 6,
    "草地": 6,
    "河": 6,
    "湖": 6,
    "海": 6,
    "大海": 6,
    "海边": 6,

    # --------------------------------------------------------
    # Bai 7 - suc khoe
    # --------------------------------------------------------
    "出院": 7,
    "全身": 7,
    "中医": 7,
    "平安": 7,

    # --------------------------------------------------------
    # Bai 8 - an uong
    # --------------------------------------------------------
    "蛋": 8,
    "请客": 8,
    "干杯": 8,
    "瓶": 8,
    "瓶子": 8,

    # --------------------------------------------------------
    # Bai 9 - mua sam / tien / ngan hang
    # --------------------------------------------------------
    "顾客": 9,
    "店": 9,
    "手表": 9,
    "千克": 9,
    "斤": 9,
    "选": 9,
    "银行": 9,
    "银行卡": 9,
    "信用卡": 9,
    "卡": 9,
    "取": 9,
    "省": 9,
    "出租": 9,

    # --------------------------------------------------------
    # Bai 10 - nha cua / vi tri
    # --------------------------------------------------------
    "墙": 10,
    "院子": 10,
    "大门": 10,
    "住房": 10,
    "椅子": 10,
    "座": 10,
    "座位": 10,
    "层": 10,

    # --------------------------------------------------------
    # Bai 11 - giao thong / phuong huong
    # --------------------------------------------------------
    "外地": 11,
    "站住": 11,

    # --------------------------------------------------------
    # Bai 12 - du lich
    # --------------------------------------------------------
    "参观": 12,
    "国际": 12,
    "船": 12,
    "出门": 12,
    "假期": 12,
    "来到": 12,

    # --------------------------------------------------------
    # Bai 13 - the thao
    # --------------------------------------------------------
    "爬": 13,
    "排球": 13,
    "球鞋": 13,
    "加油": 13,

    # --------------------------------------------------------
    # Bai 14 - giai tri / so thich
    # --------------------------------------------------------
    "故事": 14,
    "明星": 14,
    "画儿": 14,
    "影片": 14,
    "笑话": 14,
    "笑话儿": 14,
    "有空儿": 14,

    # --------------------------------------------------------
    # Bai 15 - su kien
    # --------------------------------------------------------
    "干杯": 15,
    "场": 15,

    # --------------------------------------------------------
    # Bai 16 - hoan thanh / ket qua
    # --------------------------------------------------------
    "收": 16,
    "收到": 16,
    "受到": 16,
    "重复": 16,
    "重新": 16,
    "拿到": 16,
    "拿出": 16,
    "得出": 16,
    "实现": 16,
    "找出": 16,
    "送到": 16,
    "见到": 16,

    # --------------------------------------------------------
    # Bai 17 - trinh tu / dang tiep dien
    # --------------------------------------------------------
    "接下来": 17,
    "留下": 17,
    "忽然": 17,
    "不一会儿": 17,
    "今后": 17,

    # --------------------------------------------------------
    # Bai 18 - so sanh
    # --------------------------------------------------------
    "等于": 18,
    "合适": 18,
    "低": 18,
    "平": 18,
    "平等": 18,
    "长": 18,
    "短": 18,
    "超过": 18,
    "多数": 18,
    "少数": 18,
    "大多数": 18,
    "大部分": 18,
    "一部分": 18,
    "全部": 18,
    "全": 18,
    "全体": 18,

    # --------------------------------------------------------
    # Bai 19 - muc do / thay doi
    # --------------------------------------------------------
    "一般": 19,
    "许多": 19,
    "十分": 19,
    "不少": 19,
    "大量": 19,
    "满": 19,
    "不够": 19,
    "不太": 19,
    "不错": 19,
    "挺好": 19,
    "越": 19,
    "长": 19,
    "主要": 19,
    "特点": 19,

    # --------------------------------------------------------
    # Bai 20 - nguyen nhan / dieu kien
    # --------------------------------------------------------
    "或者": 20,
    "为什么": 20,
    "只要": 20,
    "不但": 20,
    "应该": 20,
    "该": 20,
    "也许": 20,
    "只能": 20,
    "一定": 20,
    "不得": 20,

    # --------------------------------------------------------
    # Bai 21 - giao tiep / thong tin
    # --------------------------------------------------------
    "叫作": 21,
    "提到": 21,
    "网站": 21,
    "点头": 21,
    "清楚": 21,
    "打印": 21,
    "通知": 21,
    "声音": 21,
    "讲话": 21,
    "喊": 21,
    "常用": 21,
    "大声": 21,
    "信": 21,
    "信号": 21,
    "晚报": 21,
    "报纸": 21,
    "喂": 21,

    # --------------------------------------------------------
    # Bai 22 - y kien / xa hoi / van hoa
    # --------------------------------------------------------
    "自由": 22,
    "故意": 22,
    "道理": 22,
    "实际": 22,
    "公平": 22,
    "全国": 22,
    "人口": 22,
    "市": 22,
    "市长": 22,
    "以为": 22,
    "意思": 22,
    "行为": 22,
    "重视": 22,

    # --------------------------------------------------------
    # Bai 23 - tu chung / cong cu / luong tu
    # --------------------------------------------------------
    "分开": 23,
    "弄": 23,
    "人数": 23,
    "网": 23,
    "对": 23,
    "机会": 23,
    "努力": 23,
    "怎么办": 23,
    "带来": 23,
    "份": 23,
    "条": 23,
    "愿意": 23,
    "组成": 23,
    "求": 23,
    "什么样": 23,
    "数字": 23,
    "掉": 23,
    "目的": 23,
    "碰": 23,
    "碰到": 23,
    "碰见": 23,
    "直接": 23,
    "两": 23,
    "取": 23,
    "怎么样": 23,
    "表": 23,
    "亮": 23,
    "全": 23,
    "所有": 23,
    "一共": 23,
    "得": 23,
    "其他": 23,
    "其中": 23,
    "让": 23,
    "套": 23,
    "会": 23,
    "又": 23,
    "啊": 23,
    "帮助": 23,
    "部分": 23,
    "等": 23,
    "段": 23,
    "万": 23,
}


def clean(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def semantic_fallback(row):
    """
    Fallback chi dung khi tu khong nam trong MANUAL.

    Khong chia de can bang.
    Dua vao bai theo nghia ro rang.
    Neu van chung chung -> bai 23.
    """

    hanzi = clean(row["ChuHan"])
    meaning = clean(row["NghiaTiengViet"]).lower()
    pos = clean(row["TuLoai"])

    # Suc khoe
    if any(x in meaning for x in [
        "bệnh", "bác sĩ", "y học", "cơ thể",
        "đau", "khỏe", "viện"
    ]):
        return 7, "nghia_suc_khoe"

    # Hoc tap
    if any(x in meaning for x in [
        "học", "giáo dục", "bài học",
        "bài thi", "trường", "từ mới"
    ]):
        return 2, "nghia_hoc_tap"

    # An uong
    if any(x in meaning for x in [
        "ăn", "uống", "thức ăn", "món ăn",
        "chai", "bình"
    ]):
        return 8, "nghia_an_uong"

    # Mua sam / tien
    if any(x in meaning for x in [
        "tiền", "khách hàng", "ngân hàng",
        "thẻ", "mua", "bán", "cửa hàng"
    ]):
        return 9, "nghia_mua_sam"

    # Giao thong / du lich
    if any(x in meaning for x in [
        "tàu", "thuyền", "du lịch",
        "khách sạn", "đi xa", "kỳ nghỉ"
    ]):
        return 12, "nghia_du_lich"

    # The thao
    if any(x in meaning for x in [
        "bóng", "thể thao", "thi đấu"
    ]):
        return 13, "nghia_the_thao"

    # Thoi tiet / tu nhien
    if any(x in meaning for x in [
        "mây", "biển", "hồ", "sông",
        "động vật", "chim", "mèo", "chó",
        "nhiệt độ", "không khí"
    ]):
        return 6, "nghia_tu_nhien"

    # Giao tiep
    if any(x in meaning for x in [
        "nói", "thông báo", "tin tức",
        "tin nhắn", "giọng", "âm thanh",
        "câu", "thư"
    ]):
        return 21, "nghia_giao_tiep"

    # Quan diem / xa hoi
    if any(x in meaning for x in [
        "quan điểm", "ý kiến", "thái độ",
        "xã hội", "dân số", "công bằng"
    ]):
        return 22, "nghia_quan_diem"

    # Tu noi / lien tu / pho tu:
    # uu tien bai ngu phap/tong hop
    if any(x in pos for x in [
        "连", "副", "助", "介", "代"
    ]):
        return 23, "tu_chuc_nang"

    return 23, "tu_dung_chung"


def main():

    print("=" * 76)
    print("BUOC 15 - GAN 330 TU CAN XEM VAO BAI HSK2")
    print("DA RA SOAT NOI DUNG - KHONG CAN BANG SO LUONG")
    print("KHONG GHI SQL")
    print("=" * 76)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file:\n{INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)
        rows = list(reader)
        fields = reader.fieldnames

    if len(rows) != 330:
        raise ValueError(
            f"Du kien 330 tu can xem, "
            f"nhung file co {len(rows)}."
        )

    counts = {
        i: 0
        for i in range(1, 24)
    }

    manual_count = 0
    fallback_count = 0

    output = []

    for row in rows:

        word = clean(
            row["ChuHan"]
        )

        if word in MANUAL:

            lesson = MANUAL[word]
            reason = "ra_soat_thu_cong"

            manual_count += 1

        else:

            lesson, reason = (
                semantic_fallback(row)
            )

            fallback_count += 1

        row["MaBaiHocTam"] = (
            f"L2-{lesson:02d}"
        )

        row["SoThuTuBai"] = lesson

        row["TenBaiHoc"] = (
            LESSON_NAMES[lesson]
        )

        row["CachPhan"] = reason

        row["DiemChuDe"] = (
            100
            if reason == "ra_soat_thu_cong"
            else 50
        )

        row["TuKhoaKhop"] = reason

        counts[lesson] += 1

        output.append(row)

    # Sap theo bai va thu tu nguon
    output.sort(
        key=lambda r: (
            int(r["SoThuTuBai"]),
            int(r["SoThuTuNguon"])
        )
    )

    # Danh lai ThuTuTrongBai rieng cho file 330
    current = {
        i: 0
        for i in range(1, 24)
    }

    for row in output:

        lesson = int(
            row["SoThuTuBai"]
        )

        current[lesson] += 1

        row["ThuTuTrongBai"] = (
            current[lesson]
        )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(output)

    print()
    print(f"Tong tu xu ly: {len(output)}")
    print(
        f"Gan theo bang ra soat: "
        f"{manual_count}"
    )
    print(
        f"Gan theo nghia/fallback: "
        f"{fallback_count}"
    )

    print()
    print("PHAN BO 330 TU:")

    for lesson in range(1, 24):
        print(
            f"  Bai {lesson:02d}: "
            f"{counts[lesson]} tu"
        )

    print()
    print("Da tao:")
    print(OUTPUT_FILE)

    print()
    print(
        "Tat ca 330 tu da co bai tam."
    )
    print(
        "KHONG INSERT/UPDATE/DELETE SQL."
    )


if __name__ == "__main__":
    main()