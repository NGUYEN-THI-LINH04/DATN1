from pathlib import Path
import csv
import re
import unicodedata


# =========================================================
# THƯ MỤC GỐC
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

HSK_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
)


# =========================================================
# FILE ĐẦU VÀO
# =========================================================
INPUT_FILE = (
    HSK_DIR
    / "hsk1_4_review_refined.csv"
)


# =========================================================
# FILE ĐẦU RA
# =========================================================

# Những từ đã xác định được dữ liệu gốc,
# sẵn sàng sang bước Việt hóa.
READY_FILE = (
    HSK_DIR
    / "hsk1_4_ready_for_vietnamese.csv"
)

# Những từ vẫn còn vấn đề,
# cần kiểm tra riêng.
MANUAL_FILE = (
    HSK_DIR
    / "hsk1_4_manual_review.csv"
)


# =========================================================
# CHUẨN HÓA PINYIN
#
# àihào     -> aihao
# ai4 hao4  -> aihao
# =========================================================
def normalize_pinyin(value):

    if not value:
        return ""

    value = value.strip().lower()

    replacements = {
        "ü": "v",
        "ǖ": "v",
        "ǘ": "v",
        "ǚ": "v",
        "ǜ": "v",
        "u:": "v",
    }

    for old, new in replacements.items():
        value = value.replace(
            old,
            new,
        )

    value = unicodedata.normalize(
        "NFD",
        value,
    )

    value = "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )

    # Bỏ số thanh
    value = re.sub(
        r"[1-5]",
        "",
        value,
    )

    # Bỏ khoảng trắng/ký tự khác
    value = re.sub(
        r"[^a-zv]",
        "",
        value,
    )

    return value


# =========================================================
# TÁCH CHUỖI THEO |
# =========================================================
def split_pipe(value):

    if not value:
        return []

    return [
        item.strip()
        for item in value.split(" | ")
        if item.strip()
    ]


# =========================================================
# TÁCH NGHĨA THEO ||
# =========================================================
def split_definitions(value):

    if not value:
        return []

    return [
        item.strip()
        for item in value.split(" || ")
        if item.strip()
    ]


# =========================================================
# LOẠI BỎ TRÙNG NHƯNG GIỮ THỨ TỰ
# =========================================================
def unique_keep_order(items):

    result = []
    seen = set()

    for item in items:

        if not item:
            continue

        if item in seen:
            continue

        seen.add(item)
        result.append(item)

    return result


# =========================================================
# XỬ LÝ TRƯỜNG HỢP NHIỀU ENTRY CÙNG PINYIN
# =========================================================
def merge_same_pinyin(row):

    standard_pinyin = (
        row.get(
            "PinyinChuan",
            "",
        )
        .strip()
    )

    normalized_standard = normalize_pinyin(
        standard_pinyin
    )

    ids = split_pipe(
        row.get(
            "MaMucTuCedict",
            "",
        )
    )

    pinyins = split_pipe(
        row.get(
            "PinyinCedict",
            "",
        )
    )

    definitions = split_definitions(
        row.get(
            "NghiaAnhCedict",
            "",
        )
    )

    candidate_count = min(
        len(ids),
        len(pinyins),
    )

    matched_ids = []
    matched_pinyins = []
    matched_definitions = []

    for index in range(
        candidate_count
    ):

        pinyin = pinyins[index]

        normalized_candidate = (
            normalize_pinyin(
                pinyin
            )
        )

        if (
            normalized_candidate
            != normalized_standard
        ):
            continue

        matched_ids.append(
            ids[index]
        )

        matched_pinyins.append(
            pinyin
        )

        if index < len(definitions):

            definition = (
                definitions[index]
            )

            if definition:
                matched_definitions.append(
                    definition
                )

    # Loại trùng
    matched_ids = unique_keep_order(
        matched_ids
    )

    matched_pinyins = unique_keep_order(
        matched_pinyins
    )

    matched_definitions = (
        unique_keep_order(
            matched_definitions
        )
    )

    if not matched_ids:
        return False

    row[
        "MaMucTuDuocChon"
    ] = " | ".join(
        matched_ids
    )

    row[
        "PinyinDuocChon"
    ] = " | ".join(
        matched_pinyins
    )

    # Giữ toàn bộ nghĩa của các entry
    # cùng từ + cùng Pinyin.
    row[
        "NghiaAnhDuocChon"
    ] = " / ".join(
        matched_definitions
    )

    row[
        "TrangThaiSauDoiChieu"
    ] = "gop_nghia_cung_pinyin"

    row[
        "LyDoLuaChon"
    ] = (
        "Co nhieu entry CC-CEDICT "
        "cung tu va cung Pinyin chuan HSK; "
        "giu va gop toan bo nghia Anh."
    )

    return True


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 72)
    print(
        "HOAN THIEN DOI CHIEU TU VUNG HSK 1-4"
    )
    print("=" * 72)

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "Khong tim thay file:\n"
            f"{INPUT_FILE}\n\n"
            "Hay chay "
            "05b_refine_hsk_matches.py "
            "truoc."
        )

    # =====================================================
    # ĐỌC FILE
    # =====================================================
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
            reader.fieldnames or []
        )

    print(
        f"So dong dau vao: "
        f"{len(rows)}"
    )

    if len(rows) != 3245:

        print(
            "CANH BAO: "
            "So dong khong phai 3245."
        )

    # =====================================================
    # ĐẢM BẢO CÁC CỘT CẦN THIẾT
    # =====================================================
    required_extra_fields = [
        "MaMucTuDuocChon",
        "PinyinDuocChon",
        "NghiaAnhDuocChon",
        "TrangThaiSauDoiChieu",
        "LyDoLuaChon",
        "NghiaTiengViet",
        "DaDuyet",
    ]

    for field in required_extra_fields:

        if field not in fieldnames:
            fieldnames.append(
                field
            )

    # =====================================================
    # DANH SÁCH KẾT QUẢ
    # =====================================================
    ready_rows = []
    manual_rows = []

    stats = {
        "khop_1": 0,
        "khop_pinyin": 0,
        "gop_nghia_cung_pinyin": 0,
        "khong_khop_pinyin": 0,
        "khong_tim_thay": 0,
        "khac": 0,
    }

    # =====================================================
    # XỬ LÝ
    # =====================================================
    for row in rows:

        status = (
            row.get(
                "TrangThaiSauDoiChieu",
                "",
            )
            .strip()
        )

        # -------------------------------------------------
        # ĐÃ KHỚP 1 ENTRY
        # -------------------------------------------------
        if status == "khop_1":

            stats[
                "khop_1"
            ] += 1

            row[
                "NghiaTiengViet"
            ] = ""

            row[
                "DaDuyet"
            ] = "0"

            ready_rows.append(
                row
            )

            continue

        # -------------------------------------------------
        # ĐÃ CHỌN ĐƯỢC BẰNG PINYIN
        # -------------------------------------------------
        if status == "khop_pinyin":

            stats[
                "khop_pinyin"
            ] += 1

            row[
                "NghiaTiengViet"
            ] = ""

            row[
                "DaDuyet"
            ] = "0"

            ready_rows.append(
                row
            )

            continue

        # -------------------------------------------------
        # NHIỀU ENTRY NHƯNG CÙNG PINYIN
        #
        # Không chọn 1 entry.
        # Gộp toàn bộ nghĩa phù hợp.
        # -------------------------------------------------
        if (
            status
            == "nhieu_entry_cung_pinyin"
        ):

            success = merge_same_pinyin(
                row
            )

            if success:

                stats[
                    "gop_nghia_cung_pinyin"
                ] += 1

                row[
                    "NghiaTiengViet"
                ] = ""

                row[
                    "DaDuyet"
                ] = "0"

                ready_rows.append(
                    row
                )

            else:

                stats[
                    "khac"
                ] += 1

                row[
                    "TrangThaiSauDoiChieu"
                ] = (
                    "loi_gop_pinyin"
                )

                manual_rows.append(
                    row
                )

            continue

        # -------------------------------------------------
        # PINYIN KHÔNG KHỚP
        # -------------------------------------------------
        if status == "khong_khop_pinyin":

            stats[
                "khong_khop_pinyin"
            ] += 1

            manual_rows.append(
                row
            )

            continue

        # -------------------------------------------------
        # KHÔNG TÌM THẤY
        # -------------------------------------------------
        if status == "khong_tim_thay":

            stats[
                "khong_tim_thay"
            ] += 1

            manual_rows.append(
                row
            )

            continue

        # -------------------------------------------------
        # TRẠNG THÁI KHÁC
        # -------------------------------------------------
        stats[
            "khac"
        ] += 1

        manual_rows.append(
            row
        )

    # =====================================================
    # GHI FILE ĐỦ ĐIỀU KIỆN VIỆT HÓA
    # =====================================================
    with open(
        READY_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            ready_rows
        )

    # =====================================================
    # GHI FILE CẦN KIỂM TRA
    # =====================================================
    with open(
        MANUAL_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            manual_rows
        )

    # =====================================================
    # IN KẾT QUẢ
    # =====================================================
    print()
    print("-" * 72)
    print("KET QUA CUOI DOI CHIEU")
    print("-" * 72)

    print(
        "Khop 1 entry: "
        f"{stats['khop_1']}"
    )

    print(
        "Chon bang Pinyin: "
        f"{stats['khop_pinyin']}"
    )

    print(
        "Gop nhieu nghia cung Pinyin: "
        f"{stats['gop_nghia_cung_pinyin']}"
    )

    print(
        "Pinyin khong khop: "
        f"{stats['khong_khop_pinyin']}"
    )

    print(
        "Khong tim thay: "
        f"{stats['khong_tim_thay']}"
    )

    print(
        "Trang thai khac/loi: "
        f"{stats['khac']}"
    )

    print()
    print(
        "SO TU SAN SANG VIET HOA: "
        f"{len(ready_rows)}"
    )

    print(
        "SO TU CAN KIEM TRA RIENG: "
        f"{len(manual_rows)}"
    )

    print()
    print(
        "File san sang Viet hoa:"
    )

    print(
        READY_FILE
    )

    print()
    print(
        "File can kiem tra rieng:"
    )

    print(
        MANUAL_FILE
    )

    print()
    print(
        "CHUA INSERT VAO TuVung."
    )

    print(
        "NghiaTiengViet van dang trong."
    )

    print()
    print("=" * 72)
    print("HOAN TAT")
    print("=" * 72)


if __name__ == "__main__":
    main()