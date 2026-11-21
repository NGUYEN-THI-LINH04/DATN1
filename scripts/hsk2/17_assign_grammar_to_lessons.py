from pathlib import Path
import csv
import re


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_DIR / "grammar_hsk2_draft.csv"
OUTPUT_FILE = DATA_DIR / "grammar_hsk2_by_lesson.csv"


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
# 48 CAU TRUC NGU PHAP -> BAI HOC
# ============================================================

GRAMMAR_TO_LESSON = {

    # Bai 1
    "每…都…": 1,
    "先…再…": 1,

    # Bai 2
    "只": 2,
    "才": 2,

    # Bai 3
    "就": 3,
    "还": 3,

    # Bai 4
    "跟/和…一样": 4,
    "又…又…": 4,

    # Bai 5
    "有点儿": 5,
    "一点儿": 5,

    # Bai 6
    "快要/就要…了": 6,
    "这么/那么": 6,

    # Bai 7
    "得补语": 7,
    "可能补语": 7,

    # Bai 8
    "一…就…": 8,
    "再": 8,

    # Bai 9
    "比": 9,
    "更": 9,

    # Bai 10
    "从…到…": 10,
    "离": 10,

    # Bai 11
    "往/向": 11,
    "给": 11,

    # Bai 12
    "过": 12,
    "趋向补语来/去": 12,

    # Bai 13
    "一边…一边…": 13,
    "越…越…": 13,

    # Bai 14
    "对…感兴趣": 14,
    "还是/或者": 14,

    # Bai 15
    "除了…以外还/也": 15,
    "是…的": 15,

    # Bai 16
    "已经…了": 16,
    "结果补语完": 16,
    "结果补语到": 16,

    # Bai 17
    "正在…呢": 17,
    "着": 17,

    # Bai 18
    "没有（比较）": 18,
    "最": 18,

    # Bai 19
    "越来越…": 19,
    "又": 19,

    # Bai 20
    "因为…所以…": 20,
    "虽然…但是…": 20,
    "如果…就…": 20,

    # Bai 21
    "让/叫": 21,
    "结果补语见": 21,

    # Bai 22
    "对…来说": 22,
    "结果补语懂": 22,

    # Bai 23
    "疑问词+都": 23,
    "结果补语好": 23,
}


def clean(value):
    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# CHUYEN TEN DAY DU TRONG CSV
# VE TEN CAU TRUC NGAN DUNG DE MAP
# ============================================================

def normalize_structure(value):

    text = clean(value)

    # --------------------------------------------
    # 1. Neu co " - nghia Viet"
    # chi lay phan cau truc o ben trai
    # --------------------------------------------

    if " - " in text:
        text = text.split(
            " - ",
            1
        )[0].strip()

    # --------------------------------------------
    # 2. Chuan hoa dau ba cham
    # --------------------------------------------

    text = text.replace(
        "......",
        "…"
    )

    text = text.replace(
        "……",
        "…"
    )

    text = text.replace(
        "...",
        "…"
    )

    # --------------------------------------------
    # 3. Chuan hoa ky tu
    # --------------------------------------------

    text = text.replace(
        "＋",
        "+"
    )

    text = text.replace(
        "／",
        "/"
    )

    text = text.replace(
        "(",
        "（"
    )

    text = text.replace(
        ")",
        "）"
    )

    # Bo khoang trang
    text = re.sub(
        r"\s+",
        "",
        text
    )

    lower = text.lower()

    # ========================================================
    # NHOM THOI / TRANG THAI
    # ========================================================

    if text.startswith(
        "已经…了"
    ):
        return "已经…了"

    if text.startswith(
        "正在…呢"
    ):
        return "正在…呢"

    if lower.startswith(
        "độngtừ+过"
    ):
        return "过"

    if lower.startswith(
        "độngtừ+着"
    ):
        return "着"

    if text.startswith(
        "快要/就要…了"
    ):
        return "快要/就要…了"

    # ========================================================
    # TRINH TU / SONG SONG
    # ========================================================

    if text.startswith(
        "一…就…"
    ):
        return "一…就…"

    if text.startswith(
        "先…再…"
    ):
        return "先…再…"

    if text.startswith(
        "又…又…"
    ):
        return "又…又…"

    if text.startswith(
        "一边…一边…"
    ):
        return "一边…一边…"

    # ========================================================
    # MUC DO
    # ========================================================

    if text.startswith(
        "越来越…"
    ):
        return "越来越…"

    if text.startswith(
        "越…越…"
    ):
        return "越…越…"

    # ========================================================
    # SO SANH
    # ========================================================

    if lower.startswith(
        "a+比+b+"
    ):
        return "比"

    if lower.startswith(
        "a+没有+b+"
    ):
        return "没有（比较）"

    if lower.startswith(
        "a+跟/和+b+一样"
    ):
        return "跟/和…一样"

    if text.startswith(
        "更+"
    ):
        return "更"

    if text.startswith(
        "最+"
    ):
        return "最"

    if text.startswith(
        "有点儿+"
    ):
        return "有点儿"

    if lower.startswith(
        "tínhtừ+一点儿"
    ):
        return "一点儿"

    if text.startswith(
        "这么/那么+"
    ):
        return "这么/那么"

    # ========================================================
    # PHAM VI / TAN SUAT
    # ========================================================

    if text.startswith(
        "每…都…"
    ):
        return "每…都…"

    if (
        "谁/什么/哪儿" in text
        and "+都" in text
    ):
        return "疑问词+都"

    # ========================================================
    # PHO TU
    # ========================================================

    if lower.startswith(
        "只+độngtừ"
    ):
        return "只"

    if text == "才":
        return "才"

    if text == "就":
        return "就"

    if lower.startswith(
        "再+độngtừ"
    ):
        return "再"

    if lower.startswith(
        "又+độngtừ"
    ):
        return "又"

    if text == "还":
        return "还"

    # ========================================================
    # LUA CHON / LIEN TU
    # ========================================================

    if text.startswith(
        "还是/或者"
    ):
        return "还是/或者"

    if text.startswith(
        "因为…所以…"
    ):
        return "因为…所以…"

    if text.startswith(
        "虽然…但是…"
    ):
        return "虽然…但是…"

    if text.startswith(
        "如果…就…"
    ):
        return "如果…就…"

    if text.startswith(
        "除了…以外"
    ):
        return "除了…以外还/也"

    # ========================================================
    # GIOI TU / PHUONG HUONG
    # ========================================================

    if text.startswith(
        "从…到…"
    ):
        return "从…到…"

    if lower.startswith(
        "a+离+b+"
    ):
        return "离"

    if lower.startswith(
        "往/向+phươnghướng+"
    ):
        return "往/向"

    if lower.startswith(
        "给+người+"
    ):
        return "给"

    if lower.startswith(
        "让/叫+người+"
    ):
        return "让/叫"

    # ========================================================
    # 对
    # ========================================================

    if text.startswith(
        "对…感兴趣"
    ):
        return "对…感兴趣"

    if text.startswith(
        "对…来说"
    ):
        return "对…来说"

    # ========================================================
    # BO NGU
    # ========================================================

    if lower.startswith(
        "độngtừ+得+bổngữ"
    ):
        return "得补语"

    if lower.startswith(
        "độngtừ+不+bổngữ"
    ):
        return "可能补语"

    if lower.startswith(
        "độngtừ+完"
    ):
        return "结果补语完"

    if lower.startswith(
        "độngtừ+到"
    ):
        return "结果补语到"

    if lower.startswith(
        "độngtừ+见"
    ):
        return "结果补语见"

    if lower.startswith(
        "độngtừ+懂"
    ):
        return "结果补语懂"

    if lower.startswith(
        "độngtừ+好"
    ):
        return "结果补语好"

    if lower.startswith(
        "độngtừ+来/去"
    ):
        return "趋向补语来/去"

    # ========================================================
    # 是……的
    # ========================================================

    if text.startswith(
        "是…的"
    ):
        return "是…的"

    # Khong nhan dien duoc
    return text


def main():

    print("=" * 78)
    print("BUOC 17 - PHAN 48 NGU PHAP HSK2 VAO 23 BAI")
    print("PHIEN BAN SUA THEO TEN CAU TRUC THUC TE")
    print("KHONG GHI SQL")
    print("=" * 78)

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Khong tim thay:\n"
            f"{INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(
            file
        )

        rows = list(
            reader
        )

        original_fields = (
            reader.fieldnames
        )

    if not original_fields:

        raise ValueError(
            "File khong co header."
        )

    print()
    print(
        "Cot trong file grammar:"
    )

    print(
        ", ".join(
            original_fields
        )
    )

    if "TenCauTruc" not in original_fields:

        raise ValueError(
            "Khong co cot TenCauTruc."
        )

    if len(rows) != 48:

        raise ValueError(
            f"Du kien 48 dong, "
            f"nhung file co "
            f"{len(rows)}."
        )

    fields = list(
        original_fields
    )

    extra_fields = [
        "MaBaiHocTam",
        "SoThuTuBai",
        "TenBaiHoc",
        "ThuTuTrongBai",
        "CachPhan",
        "CauTrucChuan",
    ]

    for field in extra_fields:

        if field not in fields:
            fields.append(
                field
            )

    assigned = []
    unmatched = []

    # ========================================================
    # GAN BAI
    # ========================================================

    for row in rows:

        original = clean(
            row["TenCauTruc"]
        )

        canonical = (
            normalize_structure(
                original
            )
        )

        lesson = (
            GRAMMAR_TO_LESSON.get(
                canonical
            )
        )

        if lesson is None:

            unmatched.append(
                (
                    original,
                    canonical
                )
            )

            continue

        row[
            "CauTrucChuan"
        ] = canonical

        row[
            "MaBaiHocTam"
        ] = (
            f"L2-{lesson:02d}"
        )

        row[
            "SoThuTuBai"
        ] = lesson

        row[
            "TenBaiHoc"
        ] = (
            LESSON_NAMES[
                lesson
            ]
        )

        row[
            "CachPhan"
        ] = (
            "gan_theo_noi_dung"
        )

        # MaBaiHoc that chua duoc tao
        row[
            "MaBaiHoc"
        ] = ""

        # Van la du lieu nhap
        row[
            "TrangThai"
        ] = "ban_nhap"

        assigned.append(
            row
        )

    # ========================================================
    # NEU CON LOI -> DUNG
    # ========================================================

    if unmatched:

        print()
        print(
            "CON CAU TRUC CHUA GAN:"
        )

        for original, canonical in unmatched:

            print(
                f"  {original}"
            )

            print(
                f"    -> {canonical}"
            )

        raise ValueError(
            f"Con {len(unmatched)} "
            f"cau truc chua gan."
        )

    if len(assigned) != 48:

        raise ValueError(
            "Khong du 48 cau truc."
        )

    # ========================================================
    # KIEM TRA 48 CAU TRUC CHUAN KHONG TRUNG
    # ========================================================

    canonical_values = [
        row["CauTrucChuan"]
        for row in assigned
    ]

    duplicates = sorted({
        value
        for value in canonical_values
        if canonical_values.count(
            value
        ) > 1
    })

    if duplicates:

        raise ValueError(
            "Co CauTrucChuan bi trung:\n"
            + ", ".join(
                duplicates
            )
        )

    # ========================================================
    # SAP THEO BAI
    # ========================================================

    assigned.sort(
    key=lambda row: (
        int(
            row[
                "SoThuTuBai"
            ]
        ),
        row[
            "MaNguPhapTam"
        ]
    )
)

    counters = {
        i: 0
        for i in range(
            1,
            24
        )
    }

    for row in assigned:

        lesson = int(
            row[
                "SoThuTuBai"
            ]
        )

        counters[
            lesson
        ] += 1

        order = counters[
            lesson
        ]

        row[
            "ThuTuTrongBai"
        ] = order

        # File hien tai dung ThuTuTam
        if "ThuTuTam" in row:

            row[
                "ThuTuTam"
            ] = order

    # ========================================================
    # GHI FILE
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
            assigned
        )

    # ========================================================
    # THONG KE
    # ========================================================

    print()
    print(
        f"Tong ngu phap HSK2: "
        f"{len(assigned)}"
    )

    print(
        "Cau truc chua gan: 0"
    )

    print()
    print(
        "NGU PHAP THEO BAI:"
    )

    total = 0

    for lesson in range(
        1,
        24
    ):

        count = counters[
            lesson
        ]

        total += count

        print(
            f"  Bai "
            f"{lesson:02d}: "
            f"{count} cau truc"
        )

    print()
    print(
        f"Tong kiem tra: "
        f"{total}/48"
    )

    print()
    print(
        "Da tao:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "MaBaiHoc van de trong."
    )

    print(
        "TrangThai = ban_nhap."
    )

    print(
        "CHUA INSERT/UPDATE/DELETE SQL."
    )


if __name__ == "__main__":
    main()