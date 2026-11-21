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

INPUT_FILE = (
    HSK_DIR
    / "hsk1_4_review.csv"
)

OUTPUT_FILE = (
    HSK_DIR
    / "hsk1_4_review_refined.csv"
)


# =========================================================
# CHUẨN HÓA PINYIN ĐỂ SO SÁNH
#
# Ví dụ:
#
# àihào
# ai4 hao4
#
# đều trở thành:
#
# aihao
# =========================================================
def normalize_pinyin(value):
    if not value:
        return ""

    value = value.strip().lower()

    # -----------------------------------------------------
    # Xử lý ü trước khi bỏ dấu Unicode
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # Tách dấu thanh Unicode
    #
    # à -> a + dấu
    # ǎ -> a + dấu
    # é -> e + dấu
    # ...
    # -----------------------------------------------------
    value = unicodedata.normalize(
        "NFD",
        value,
    )

    value = "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )

    # -----------------------------------------------------
    # Xóa số thanh:
    #
    # ai4 hao4 -> ai hao
    # -----------------------------------------------------
    value = re.sub(
        r"[1-5]",
        "",
        value,
    )

    # -----------------------------------------------------
    # Chỉ giữ chữ cái
    #
    # ai hao -> aihao
    # -----------------------------------------------------
    value = re.sub(
        r"[^a-zv]",
        "",
        value,
    )

    return value


# =========================================================
# TÁCH DANH SÁCH THEO DẤU |
# =========================================================
def split_pipe(value):
    if not value:
        return []

    return [
        item.strip()
        for item in value.split(" | ")
    ]


# =========================================================
# TÁCH DANH SÁCH NGHĨA
# =========================================================
def split_definitions(value):
    if not value:
        return []

    return [
        item.strip()
        for item in value.split(" || ")
    ]


# =========================================================
# XỬ LÝ MỘT DÒNG
# =========================================================
def refine_row(row):

    status = (
        row.get(
            "TrangThaiDoiChieu",
            "",
        )
        .strip()
    )

    so_ket_qua_text = (
        row.get(
            "SoKetQuaCedict",
            "0",
        )
        .strip()
    )

    try:
        so_ket_qua = int(
            so_ket_qua_text
            or 0
        )
    except ValueError:
        so_ket_qua = 0

    # =====================================================
    # CÁC CỘT MỚI
    # =====================================================
    row[
        "MaMucTuDuocChon"
    ] = ""

    row[
        "PinyinDuocChon"
    ] = ""

    row[
        "NghiaAnhDuocChon"
    ] = ""

    row[
        "LyDoLuaChon"
    ] = ""

    row[
        "TrangThaiSauDoiChieu"
    ] = status

    # =====================================================
    # KHÔNG TÌM THẤY
    # =====================================================
    if (
        status == "khong_tim_thay"
        or so_ket_qua == 0
    ):

        row[
            "TrangThaiSauDoiChieu"
        ] = "khong_tim_thay"

        row[
            "LyDoLuaChon"
        ] = (
            "Khong co entry CC-CEDICT "
            "de doi chieu."
        )

        return row

    # =====================================================
    # ĐÃ CÓ ĐÚNG 1 ENTRY
    # =====================================================
    if so_ket_qua == 1:

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

        definitions = (
            split_definitions(
                row.get(
                    "NghiaAnhCedict",
                    "",
                )
            )
        )

        if ids:
            row[
                "MaMucTuDuocChon"
            ] = ids[0]

        if pinyins:
            row[
                "PinyinDuocChon"
            ] = pinyins[0]

        if definitions:
            row[
                "NghiaAnhDuocChon"
            ] = definitions[0]

        row[
            "TrangThaiSauDoiChieu"
        ] = "khop_1"

        row[
            "LyDoLuaChon"
        ] = (
            "Chi co mot entry "
            "CC-CEDICT."
        )

        return row

    # =====================================================
    # CÓ NHIỀU ENTRY
    # DÙNG PINYIN HSK ĐỂ LỌC
    # =====================================================
    pinyin_chuan = (
        row.get(
            "PinyinChuan",
            "",
        )
        .strip()
    )

    normalized_standard = (
        normalize_pinyin(
            pinyin_chuan
        )
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

    # -----------------------------------------------------
    # Đảm bảo danh sách cùng kích thước
    # -----------------------------------------------------
    candidate_count = min(
        len(ids),
        len(pinyins),
    )

    candidates = []

    for index in range(
        candidate_count
    ):

        definition = ""

        if index < len(definitions):
            definition = (
                definitions[index]
            )

        candidates.append(
            {
                "id": ids[index],
                "pinyin": (
                    pinyins[index]
                ),
                "definition": (
                    definition
                ),
                "normalized": (
                    normalize_pinyin(
                        pinyins[index]
                    )
                ),
            }
        )

    # -----------------------------------------------------
    # Lấy những candidate có Pinyin giống chuẩn HSK
    # -----------------------------------------------------
    matched = [
        candidate
        for candidate in candidates
        if (
            candidate[
                "normalized"
            ]
            == normalized_standard
        )
    ]

    # =====================================================
    # CHỈ 1 KẾT QUẢ KHỚP PINYIN
    # =====================================================
    if len(matched) == 1:

        selected = matched[0]

        row[
            "MaMucTuDuocChon"
        ] = selected["id"]

        row[
            "PinyinDuocChon"
        ] = selected[
            "pinyin"
        ]

        row[
            "NghiaAnhDuocChon"
        ] = selected[
            "definition"
        ]

        row[
            "TrangThaiSauDoiChieu"
        ] = "khop_pinyin"

        row[
            "LyDoLuaChon"
        ] = (
            "Trong nhieu entry "
            "CC-CEDICT, chi co mot entry "
            "co Pinyin khop voi "
            "Pinyin chuan HSK."
        )

        return row

    # =====================================================
    # NHIỀU ENTRY CÙNG PINYIN
    # =====================================================
    if len(matched) > 1:

        row[
            "TrangThaiSauDoiChieu"
        ] = (
            "nhieu_entry_cung_pinyin"
        )

        row[
            "LyDoLuaChon"
        ] = (
            "Co nhieu entry CC-CEDICT "
            "cung khop Pinyin; "
            "can kiem tra nghia."
        )

        return row

    # =====================================================
    # KHÔNG ENTRY NÀO KHỚP PINYIN
    # =====================================================
    row[
        "TrangThaiSauDoiChieu"
    ] = "khong_khop_pinyin"

    row[
        "LyDoLuaChon"
    ] = (
        "Tim thay tu trong CC-CEDICT "
        "nhung khong co Pinyin nao "
        "khop voi Pinyin chuan HSK."
    )

    return row


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 72)
    print(
        "LOC LAI KET QUA HSK BANG PINYIN"
    )
    print("=" * 72)

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "Khong tim thay file:\n"
            f"{INPUT_FILE}\n"
            "Hay chay "
            "05_prepare_hsk_vocabulary.py "
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

        original_fields = list(
            reader.fieldnames or []
        )

    print(
        f"So dong doc duoc: "
        f"{len(rows)}"
    )

    # =====================================================
    # THÊM CỘT
    # =====================================================
    new_fields = [
        "MaMucTuDuocChon",
        "PinyinDuocChon",
        "NghiaAnhDuocChon",
        "TrangThaiSauDoiChieu",
        "LyDoLuaChon",
    ]

    fieldnames = (
        original_fields
        + [
            field
            for field in new_fields
            if field not in original_fields
        ]
    )

    # =====================================================
    # THỐNG KÊ
    # =====================================================
    stats = {
        "khop_1": 0,
        "khop_pinyin": 0,
        "nhieu_entry_cung_pinyin": 0,
        "khong_khop_pinyin": 0,
        "khong_tim_thay": 0,
    }

    refined_rows = []

    for row in rows:

        refined = refine_row(
            row
        )

        status = refined.get(
            "TrangThaiSauDoiChieu",
            "",
        )

        if status in stats:
            stats[status] += 1

        refined_rows.append(
            refined
        )

    # =====================================================
    # GHI FILE MỚI
    # =====================================================
    with open(
        OUTPUT_FILE,
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
            refined_rows
        )

    # =====================================================
    # KẾT QUẢ
    # =====================================================
    print()
    print("-" * 72)
    print("KET QUA SAU KHI LOC PINYIN")
    print("-" * 72)

    print(
        "Khop san 1 entry: "
        f"{stats['khop_1']}"
    )

    print(
        "Tu nhieu entry -> chon duoc "
        "bang Pinyin: "
        f"{stats['khop_pinyin']}"
    )

    print(
        "Van con nhieu entry cung Pinyin: "
        f"{stats['nhieu_entry_cung_pinyin']}"
    )

    print(
        "Co tu nhung Pinyin khong khop: "
        f"{stats['khong_khop_pinyin']}"
    )

    print(
        "Khong tim thay CC-CEDICT: "
        f"{stats['khong_tim_thay']}"
    )

    da_chon_duoc = (
        stats["khop_1"]
        + stats["khop_pinyin"]
    )

    can_kiem_tra = (
        stats[
            "nhieu_entry_cung_pinyin"
        ]
        + stats[
            "khong_khop_pinyin"
        ]
        + stats[
            "khong_tim_thay"
        ]
    )

    print()
    print(
        "Tong da chon duoc entry: "
        f"{da_chon_duoc}"
    )

    print(
        "Tong con can kiem tra: "
        f"{can_kiem_tra}"
    )

    print()
    print(
        "File ket qua:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "CHUA INSERT VAO TuVung."
    )

    print(
        "CHUA GAN NghiaTiengViet."
    )

    print()
    print("=" * 72)
    print("HOAN TAT")
    print("=" * 72)


if __name__ == "__main__":
    main()