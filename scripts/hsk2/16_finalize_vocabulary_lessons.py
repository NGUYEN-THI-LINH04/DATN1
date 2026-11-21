from pathlib import Path
import csv


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

# 442 tu da phan o buoc 14
ASSIGNED_FILE = (
    DATA_DIR / "vocabulary_hsk2_reassigned.csv"
)

# 330 tu da xu ly o buoc 15
REVIEW_FILE = (
    DATA_DIR / "vocabulary_hsk2_review_assigned.csv"
)

# File cuoi 772 tu
OUTPUT_FILE = (
    DATA_DIR / "vocabulary_hsk2_final_by_lesson.csv"
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
# RA SOAT 93 TU DANG NAM O BAI 23
#
# DUNG MaTuHSK thay vi ChuHan de tranh trung tu / da nghia.
# ============================================================

FINAL_LESSON_23_REASSIGN = {

    # ========================================================
    # BAI 1 - THOI GIAN / SINH HOAT
    # ========================================================
    620: 1,     # 等 - doi
    664: 1,     # 分 - phut

    # ========================================================
    # BAI 2 - HOC TAP
    # ========================================================
    903: 2,     # 努力
    1002: 2,    # 数字
    1009: 2,    # 算
    1250: 2,    # 准确

    # ========================================================
    # BAI 3 - CONG VIEC
    # ========================================================
    749: 3,     # 机会
    1047: 3,    # 同事

    # ========================================================
    # BAI 4 - GIA DINH / BAN BE
    # ========================================================
    702: 4,     # 关心

    # ========================================================
    # BAI 5 - NGOAI HINH / TINH CACH / CAM XUC
    # ========================================================
    738: 5,     # 坏人
    752: 5,     # 急
    828: 5,     # 哭
    897: 5,     # 难听
    976: 5,     # 什么样
    1114: 5,    # 心情

    # ========================================================
    # BAI 6 - THOI TIET / TU NHIEN
    # ========================================================
    857: 6,     # 亮
    863: 6,     # 流

    # ========================================================
    # BAI 9 - MUA SAM / SO LUONG / TIEN
    # ========================================================
    823: 9,     # 克
    950: 9,     # 取
    1021: 9,    # 套
    1034: 9,    # 条
    1065: 9,    # 万
    1164: 9,    # 亿

    # ========================================================
    # BAI 10 - VI TRI / NHA CUA
    # ========================================================
    610: 10,    # 到处
    619: 10,    # 灯
    795: 10,    # 进入
    815: 10,    # 靠
    1087: 10,   # 洗衣机
    1212: 10,   # 占

    # ========================================================
    # BAI 12 - DU LICH
    # ========================================================
    505: 12,    # 安全
    743: 12,    # 回
    884: 12,    # 目的

    # ========================================================
    # BAI 14 - SO THICH / GIAI TRI
    # ========================================================
    587: 14,    # 打算
    695: 14,    # 公园
    735: 14,    # 画家
    1264: 14,   # 作家

    # ========================================================
    # BAI 15 - SU KIEN
    # ========================================================
    549: 15,    # 参加

    # ========================================================
    # BAI 16 - HOAN THANH / KET QUA
    # ========================================================
    615: 16,    # 得 de/nhan duoc
    629: 16,    # 掉 - bo/roi, bo ngu ket qua

    # ========================================================
    # BAI 17 - HANH DONG / TRINH TU / LAP LAI
    # ========================================================
    803: 17,    # 就要
    910: 17,    # 碰
    911: 17,    # 碰到
    912: 17,    # 碰见
    1188: 17,   # 又

    # ========================================================
    # BAI 18 - SO SANH / SO LUONG / PHAM VI
    # ========================================================
    545: 18,    # 部分
    889: 18,    # 那么
    891: 18,    # 那样
    952: 18,    # 全
    964: 18,    # 人数
    1014: 18,   # 所有
    1148: 18,   # 一共

    # ========================================================
    # BAI 19 - THAY DOI / MUC DO
    # ========================================================
    590: 19,    # 大大
    602: 19,    # 带来
    665: 19,    # 分开
    755: 19,    # 加
    1260: 19,   # 组成

    # ========================================================
    # BAI 20 - DIEU KIEN / LIEN KET Y
    # ========================================================
    1196: 20,   # 愿意

    # ========================================================
    # BAI 21 - GIAO TIEP
    # ========================================================
    501: 21,    # 啊
    512: 21,    # 帮助
    535: 21,    # 不要
    679: 21,    # 感谢
    701: 21,    # 关机
    739: 21,    # 欢迎
    784: 21,    # 接受
    830: 21,    # 快点儿
    946: 21,    # 求
    960: 21,    # 让
    1066: 21,   # 网
    1209: 21,   # 怎么办
    1210: 21,   # 怎么样
    1211: 21,   # 怎样
    1229: 21,   # 直接

    # ========================================================
    # BAI 22 - VAN HOA / QUAN DIEM / NGON NGU
    # ========================================================
    645: 22,    # 对
    835: 22,    # 来自
    849: 22,    # 例如
    864: 22,    # 流利
    1096: 22,   # 想到
    1098: 22,   # 想起
    1177: 22,   # 英语
}


# ============================================================
# 14 TU THUC SU GIU O BAI 23
# ============================================================

KEEP_IN_LESSON_23 = {

    528,    # 表
    618,    # 得 (tro tu)
    642,    # 段
    668,    # 份
    745,    # 会
    792,    # 借
    856,    # 两
    902,    # 弄
    926,    # 其他
    927,    # 其中
    990,    # 使用
    1015,   # 它
    1016,   # 它们
    1053,   # 推
}


def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def read_csv(path):

    if not path.exists():
        raise FileNotFoundError(
            f"Khong tim thay file:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        return (
            list(reader),
            reader.fieldnames
        )


def main():

    print("=" * 78)
    print("BUOC 16 - HOAN THIEN PHAN BAI TU VUNG HSK2")
    print("SUA BAI 23 + GHEP 442 + 330 = 772 TU")
    print("KHONG GHI SQL")
    print("=" * 78)

    assigned_rows, fields1 = read_csv(
        ASSIGNED_FILE
    )

    review_rows, fields2 = read_csv(
        REVIEW_FILE
    )

    if len(assigned_rows) != 442:
        raise ValueError(
            "File buoc 14 phai co 442 tu, "
            f"nhung hien co {len(assigned_rows)}."
        )

    if len(review_rows) != 330:
        raise ValueError(
            "File buoc 15 phai co 330 tu, "
            f"nhung hien co {len(review_rows)}."
        )

    if fields1 != fields2:
        raise ValueError(
            "Hai file co cau truc cot khac nhau."
        )

    fields = fields1

    # ========================================================
    # 1. LAY CAC DONG DANG O BAI 23
    # ========================================================

    lesson23_rows = [
        row
        for row in review_rows
        if int(row["SoThuTuBai"]) == 23
    ]

    if len(lesson23_rows) != 93:
        raise ValueError(
            "Du kien bai 23 cua buoc 15 co 93 tu, "
            f"nhung hien co {len(lesson23_rows)}."
        )

    lesson23_ids = {
        int(row["MaTuHSK"])
        for row in lesson23_rows
    }

    reviewed_ids = (
        set(FINAL_LESSON_23_REASSIGN.keys())
        | KEEP_IN_LESSON_23
    )

    missing_review = (
        lesson23_ids
        - reviewed_ids
    )

    extra_review = (
        reviewed_ids
        - lesson23_ids
    )

    if missing_review:
        raise ValueError(
            "Con MaTuHSK bai 23 chua duoc ra soat:\n"
            + ", ".join(
                map(str, sorted(missing_review))
            )
        )

    if extra_review:
        raise ValueError(
            "Bang ra soat co MaTuHSK "
            "khong nam trong bai 23:\n"
            + ", ".join(
                map(str, sorted(extra_review))
            )
        )

    # ========================================================
    # 2. SUA 93 TU BAI 23
    # ========================================================

    moved_count = 0
    kept_count = 0

    for row in review_rows:

        ma_hsk = int(
            row["MaTuHSK"]
        )

        old_lesson = int(
            row["SoThuTuBai"]
        )

        if old_lesson != 23:
            continue

        if ma_hsk in FINAL_LESSON_23_REASSIGN:

            new_lesson = (
                FINAL_LESSON_23_REASSIGN[
                    ma_hsk
                ]
            )

            row["SoThuTuBai"] = (
                new_lesson
            )

            row["MaBaiHocTam"] = (
                f"L2-{new_lesson:02d}"
            )

            row["TenBaiHoc"] = (
                LESSON_NAMES[
                    new_lesson
                ]
            )

            row["CachPhan"] = (
                "ra_soat_bai23"
            )

            row["DiemChuDe"] = 100

            row["TuKhoaKhop"] = (
                "ra_soat_bai23"
            )

            moved_count += 1

        elif ma_hsk in KEEP_IN_LESSON_23:

            row["CachPhan"] = (
                "giu_bai23"
            )

            row["DiemChuDe"] = 100

            row["TuKhoaKhop"] = (
                "tu_dung_chung"
            )

            kept_count += 1

    if moved_count + kept_count != 93:
        raise ValueError(
            "So tu bai 23 sau ra soat "
            "khong bang 93."
        )

    # ========================================================
    # 3. GHEP 442 + 330
    # ========================================================

    final_rows = (
        assigned_rows
        + review_rows
    )

    if len(final_rows) != 772:
        raise ValueError(
            "Tong sau ghep khong bang 772."
        )

    # ========================================================
    # 4. KIEM TRA MaTuHSK
    # ========================================================

    ma_hsk_list = [
        int(row["MaTuHSK"])
        for row in final_rows
    ]

    if len(set(ma_hsk_list)) != 772:

        duplicates = sorted({
            x
            for x in ma_hsk_list
            if ma_hsk_list.count(x) > 1
        })

        raise ValueError(
            "MaTuHSK bi trung:\n"
            + ", ".join(
                map(str, duplicates)
            )
        )

    # ========================================================
    # 5. KIEM TRA MaTuVung
    # ========================================================

    missing_ma_tu_vung = [
        row["MaTuHSK"]
        for row in final_rows
        if not clean(
            row["MaTuVung"]
        )
    ]

    if missing_ma_tu_vung:
        raise ValueError(
            "Con dong thieu MaTuVung:\n"
            + ", ".join(
                missing_ma_tu_vung
            )
        )

    # ========================================================
    # 6. KIEM TRA BAI HOC
    # ========================================================

    invalid_lessons = []

    for row in final_rows:

        value = clean(
            row["SoThuTuBai"]
        )

        if not value:
            invalid_lessons.append(
                row["MaTuHSK"]
            )
            continue

        lesson = int(value)

        if lesson < 1 or lesson > 23:
            invalid_lessons.append(
                row["MaTuHSK"]
            )

    if invalid_lessons:
        raise ValueError(
            "Co tu chua co bai hop le:\n"
            + ", ".join(
                invalid_lessons
            )
        )

    # ========================================================
    # 7. KHONG DUOC CON can_xem / can_bang
    # ========================================================

    invalid_methods = [
        (
            row["MaTuHSK"],
            row["CachPhan"]
        )
        for row in final_rows
        if clean(row["CachPhan"])
        in {
            "can_xem",
            "can_bang"
        }
    ]

    if invalid_methods:
        raise ValueError(
            "Van con CachPhan chua hoan tat."
        )

    # ========================================================
    # 8. SAP XEP VA DANH LAI THU TU TRONG BAI
    # ========================================================

    final_rows.sort(
        key=lambda row: (
            int(row["SoThuTuBai"]),
            int(row["SoThuTuNguon"]),
            int(row["MaTuHSK"])
        )
    )

    counters = {
        i: 0
        for i in range(
            1,
            24
        )
    }

    for row in final_rows:

        lesson = int(
            row["SoThuTuBai"]
        )

        counters[
            lesson
        ] += 1

        row[
            "ThuTuTrongBai"
        ] = counters[
            lesson
        ]

        row[
            "MaBaiHocTam"
        ] = (
            f"L2-{lesson:02d}"
        )

        row[
            "TenBaiHoc"
        ] = (
            LESSON_NAMES[
                lesson
            ]
        )

    # ========================================================
    # 9. GHI FILE CUOI
    # ========================================================

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
        writer.writerows(
            final_rows
        )

    # ========================================================
    # 10. THONG KE
    # ========================================================

    print()
    print(
        f"Tu bai 23 duoc chuyen sang bai khac: "
        f"{moved_count}"
    )

    print(
        f"Tu thuc su giu lai bai 23: "
        f"{kept_count}"
    )

    print()
    print(
        f"Tong tu sau ghep: "
        f"{len(final_rows)}"
    )

    print(
        f"MaTuHSK duy nhat: "
        f"{len(set(ma_hsk_list))}"
    )

    print(
        f"Thieu MaTuVung: "
        f"{len(missing_ma_tu_vung)}"
    )

    print()
    print("SO TU CUOI CUNG THEO BAI:")

    total_check = 0

    for lesson in range(
        1,
        24
    ):

        count = counters[
            lesson
        ]

        total_check += count

        print(
            f"  Bai {lesson:02d}: "
            f"{count} tu"
        )

    print()
    print(
        f"Tong kiem tra: "
        f"{total_check}/772"
    )

    print()
    print("DA TAO FILE CUOI:")
    print(OUTPUT_FILE)

    print()
    print(
        "CHUA GHI BaiHoc."
    )

    print(
        "CHUA GHI TuVungBaiHoc."
    )

    print(
        "CHUA INSERT/UPDATE/DELETE SQL."
    )


if __name__ == "__main__":
    main()