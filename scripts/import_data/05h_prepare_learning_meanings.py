from pathlib import Path
import csv
import re


# =========================================================
# THƯ MỤC
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

HSK_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
)


# =========================================================
# FILE INPUT
# =========================================================
INPUT_FILE = (
    HSK_DIR
    / "hsk1_4_vietnamese_source_complete.csv"
)


# =========================================================
# FILE OUTPUT
# =========================================================
OUTPUT_FILE = (
    HSK_DIR
    / "hsk1_4_learning_meanings_review.csv"
)

MANUAL_FILE = (
    HSK_DIR
    / "hsk1_4_learning_meanings_manual.csv"
)


# =========================================================
# NHỮNG CỤM KHÔNG ƯU TIÊN CHO NGHĨA HỌC TẬP
#
# Chú ý:
# KHÔNG xóa khỏi NghiaTiengViet nguồn.
#
# Chỉ không ưu tiên khi tạo NghiaHocTapDeXuat.
# =========================================================
LOW_PRIORITY_PATTERNS = [

    "biến thể của",
    "biến thể cũ",
    "dạng cũ",

    "họ ",
    "họ của",

    "văn cổ",
    "cổ văn",

    "phát âm ở đài loan",
    "đài loan phát âm",

    "phản động",
    "chống cộng",

    "dân tộc",

    "viết tắt của",

    "tên khoa học",

    "tên riêng",
]


# =========================================================
# XÓA KHOẢNG TRẮNG THỪA
# =========================================================
def normalize_space(text):

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# =========================================================
# TÁCH NGHĨA
#
# Ví dụ:
#
# yêu; thích / tình cảm / ...
#
# hoặc:
#
# nghĩa A || nghĩa B
# =========================================================
def split_meanings(text):

    if not text:
        return []

    # Tách theo:
    #   /
    #   ||
    #
    # Chỉ tách khi có khoảng trắng
    # để hạn chế phá nội dung khác.
    parts = re.split(
        r"\s+\|\|\s+|\s+/\s+",
        text,
    )

    result = []

    for part in parts:

        part = normalize_space(
            part
        )

        if part:
            result.append(
                part
            )

    return result


# =========================================================
# LOẠI TRÙNG NHƯNG GIỮ THỨ TỰ
# =========================================================
def unique_keep_order(values):

    result = []
    seen = set()

    for value in values:

        key = (
            value
            .strip()
            .lower()
        )

        if not key:
            continue

        if key in seen:
            continue

        seen.add(key)

        result.append(
            value.strip()
        )

    return result


# =========================================================
# KIỂM TRA NGHĨA CÓ PHẢI CHỈ LÀ LƯỢNG TỪ
# =========================================================
def is_classifier_note(text):

    value = (
        text
        .strip()
        .lower()
    )

    return (
        value.startswith("lt:")
        or
        value.startswith("lượng từ:")
        or
        value.startswith("lượng từ cho")
    )


# =========================================================
# KIỂM TRA NGHĨA ÍT ƯU TIÊN
# =========================================================
def is_low_priority(text):

    value = (
        text
        .strip()
        .lower()
    )

    for pattern in LOW_PRIORITY_PATTERNS:

        if pattern in value:
            return True

    return False


# =========================================================
# TÍNH ĐỘ DÀI TƯƠNG ĐỐI
# =========================================================
def is_too_long(text):

    if len(text) > 180:
        return True

    return False


# =========================================================
# XỬ LÝ MỘT NGHĨA
# =========================================================
def clean_meaning(text):

    value = normalize_space(
        text
    )

    # ---------------------------------------------
    # Xóa dấu chấm cuối cho thống nhất
    # ---------------------------------------------
    value = value.rstrip(
        " .;"
    )

    return value


# =========================================================
# LẤY SỐ NGHĨA TỐI ĐA THEO CẤP HSK
#
# Cấp thấp: ngắn gọn hơn.
# =========================================================
def get_max_meanings(level):

    if level <= 2:
        return 2

    return 3


# =========================================================
# TẠO NGHĨA HỌC TẬP ĐỀ XUẤT
# =========================================================
def create_learning_meaning(row):

    source_meaning = (
        row.get(
            "NghiaTiengViet",
            "",
        )
        or ""
    ).strip()

    if not source_meaning:

        return {
            "meaning": "",
            "status":
                "khong_co_nghia_nguon",
            "manual": "1",
            "note":
                "Khong co nghia tieng Viet nguon.",
        }

    try:

        level = int(
            row.get(
                "CapDoHSK",
                "0",
            )
            or 0
        )

    except ValueError:

        level = 0

    pos_code = (
        row.get(
            "TuLoaiMa",
            "",
        )
        or ""
    ).strip()

    parts = split_meanings(
        source_meaning
    )

    parts = unique_keep_order(
        parts
    )

    if not parts:

        return {
            "meaning": source_meaning,
            "status":
                "giu_nguyen_vi_khong_tach_duoc",
            "manual": "1",
            "note":
                "Khong tach duoc cac nghia.",
        }

    # =====================================================
    # CHIA NHÓM
    # =====================================================
    normal_parts = []

    classifier_parts = []

    low_priority_parts = []

    long_parts = []

    for part in parts:

        cleaned = clean_meaning(
            part
        )

        if not cleaned:
            continue

        if is_classifier_note(
            cleaned
        ):

            classifier_parts.append(
                cleaned
            )

            continue

        if is_low_priority(
            cleaned
        ):

            low_priority_parts.append(
                cleaned
            )

            continue

        if is_too_long(
            cleaned
        ):

            long_parts.append(
                cleaned
            )

            continue

        normal_parts.append(
            cleaned
        )

    # =====================================================
    # SỐ NGHĨA TỐI ĐA
    # =====================================================
    max_meanings = (
        get_max_meanings(
            level
        )
    )

    selected = []

    # =====================================================
    # TRƯỜNG HỢP LƯỢNG TỪ
    #
    # Nếu POS có M thì ưu tiên ghi nhận
    # chức năng lượng từ.
    # =====================================================
    if (
        "M" in pos_code.split("/")
        and classifier_parts
    ):

        # Vẫn ưu tiên nghĩa thông thường trước
        if normal_parts:

            selected.append(
                normal_parts[0]
            )

        selected.append(
            classifier_parts[0]
        )

    else:

        selected.extend(
            normal_parts[
                :max_meanings
            ]
        )

    # =====================================================
    # Nếu không còn nghĩa bình thường,
    # dùng nghĩa dài trước khi dùng nghĩa ít ưu tiên.
    # =====================================================
    if not selected:

        if long_parts:

            selected.append(
                long_parts[0]
            )

        elif low_priority_parts:

            selected.append(
                low_priority_parts[0]
            )

        elif classifier_parts:

            selected.append(
                classifier_parts[0]
            )

    selected = unique_keep_order(
        selected
    )

    # Giới hạn lần cuối
    selected = selected[
        :max_meanings
    ]

    learning_meaning = (
        "; ".join(
            selected
        )
    )

    # =====================================================
    # XÁC ĐỊNH CÓ CẦN REVIEW KHÔNG
    # =====================================================
    manual = "0"

    reasons = []

    if (
        row.get(
            "CanKiemTraNghia",
            "",
        )
        == "1"
    ):

        manual = "1"

        reasons.append(
            "nghia nguon tung can kiem tra"
        )

    if len(parts) >= 5:

        manual = "1"

        reasons.append(
            "tu co nhieu nghia"
        )

    if low_priority_parts:

        manual = "1"

        reasons.append(
            "co nghia phu/it dung"
        )

    if long_parts:

        manual = "1"

        reasons.append(
            "co nghia nguon dai"
        )

    if not learning_meaning:

        manual = "1"

        reasons.append(
            "khong tao duoc nghia hoc tap"
        )

    if manual == "1":

        status = (
            "de_xuat_can_kiem_tra"
        )

    else:

        status = (
            "de_xuat_tu_dong"
        )

    note = "; ".join(
        reasons
    )

    return {
        "meaning":
            learning_meaning,

        "status":
            status,

        "manual":
            manual,

        "note":
            note,
    }


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 72)
    print(
        "TAO NGHIA HOC TAP DE XUAT "
        "CHO HSK 1-4"
    )
    print("=" * 72)

    # -----------------------------------------------------
    # Kiểm tra file
    # -----------------------------------------------------
    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "Khong tim thay:\n"
            f"{INPUT_FILE}\n\n"
            "Hay chay 05g truoc."
        )

    # -----------------------------------------------------
    # Đọc CSV
    # -----------------------------------------------------
    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        rows = list(reader)

        fieldnames = list(
            reader.fieldnames
            or []
        )

    print(
        f"So muc dau vao: "
        f"{len(rows)}"
    )

    if len(rows) != 3245:

        raise RuntimeError(
            "File khong co dung 3245 muc."
        )

    # -----------------------------------------------------
    # Cột mới
    # -----------------------------------------------------
    new_fields = [
        "NghiaHocTapDeXuat",
        "TrangThaiNghiaHocTap",
        "CanKiemTraNghiaHocTap",
        "GhiChuNghiaHocTap",
        "NghiaHocTapDaDuyet",
    ]

    for field in new_fields:

        if field not in fieldnames:

            fieldnames.append(
                field
            )

    # -----------------------------------------------------
    # Thống kê
    # -----------------------------------------------------
    auto_count = 0

    manual_count = 0

    empty_count = 0

    manual_rows = []

    # -----------------------------------------------------
    # Xử lý
    # -----------------------------------------------------
    for row in rows:

        result = (
            create_learning_meaning(
                row
            )
        )

        row[
            "NghiaHocTapDeXuat"
        ] = result[
            "meaning"
        ]

        row[
            "TrangThaiNghiaHocTap"
        ] = result[
            "status"
        ]

        row[
            "CanKiemTraNghiaHocTap"
        ] = result[
            "manual"
        ]

        row[
            "GhiChuNghiaHocTap"
        ] = result[
            "note"
        ]

        # Chưa duyệt
        row[
            "NghiaHocTapDaDuyet"
        ] = "0"

        # DaDuyet của TuVung cũng chưa đổi
        row[
            "DaDuyet"
        ] = "0"

        if not result[
            "meaning"
        ]:

            empty_count += 1

        if result[
            "manual"
        ] == "1":

            manual_count += 1

            manual_rows.append(
                row.copy()
            )

        else:

            auto_count += 1

    # -----------------------------------------------------
    # Ghi file đầy đủ
    # -----------------------------------------------------
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        writer.writerows(
            rows
        )

    # -----------------------------------------------------
    # Ghi file cần xem riêng
    # -----------------------------------------------------
    with open(
        MANUAL_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        writer.writerows(
            manual_rows
        )

    # -----------------------------------------------------
    # IN 20 MẪU ĐẦU
    # -----------------------------------------------------
    print()
    print("-" * 72)
    print(
        "20 MAU NGHIA HOC TAP"
    )
    print("-" * 72)

    for row in rows[:20]:

        print()

        print(
            f"{row.get('TuChinh', '')}"
            f" | "
            f"{row.get('PinyinChuan', '')}"
            f" | "
            f"HSK {row.get('CapDoHSK', '')}"
        )

        print(
            "Nguon : "
            f"{row.get('NghiaTiengViet', '')}"
        )

        print(
            "Hoc   : "
            f"{row.get('NghiaHocTapDeXuat', '')}"
        )

    # -----------------------------------------------------
    # KẾT QUẢ
    # -----------------------------------------------------
    print()
    print("=" * 72)
    print("KET QUA")
    print("=" * 72)

    print(
        "Tong HSK 1-4: "
        f"{len(rows)}"
    )

    print(
        "Tao duoc tu dong: "
        f"{auto_count}"
    )

    print(
        "Can xem lai: "
        f"{manual_count}"
    )

    print(
        "Nghia hoc tap trong: "
        f"{empty_count}"
    )

    print()
    print(
        "File review:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "File can xem lai:"
    )

    print(
        MANUAL_FILE
    )

    print()
    print(
        "TAT CA NghiaHocTapDaDuyet = 0."
    )

    print(
        "TAT CA DaDuyet = 0."
    )

    print(
        "CHUA INSERT VAO TuVung."
    )

    print()
    print("=" * 72)
    print("HOAN TAT")
    print("=" * 72)


if __name__ == "__main__":
    main()