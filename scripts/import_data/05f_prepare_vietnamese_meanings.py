from pathlib import Path
import sys
import csv
import re
from collections import defaultdict
from urllib.request import Request, urlopen


# =========================================================
# THƯ MỤC GỐC D:\DATN1
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# THƯ MỤC
# =========================================================
HSK_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
)

CVDICT_DIR = (
    ROOT_DIR
    / "data_sources"
    / "cvdict"
)

CVDICT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# FILE ĐẦU VÀO
# =========================================================
INPUT_FILE = (
    HSK_DIR
    / "hsk1_4_final_base.csv"
)


# =========================================================
# FILE CVDICT
# =========================================================
CVDICT_FILE = (
    CVDICT_DIR
    / "CVDICT.u8"
)

CVDICT_URL = (
    "https://raw.githubusercontent.com/"
    "ph0ngp/CVDICT/main/CVDICT.u8"
)


# =========================================================
# FILE ĐẦU RA
# =========================================================
OUTPUT_FILE = (
    HSK_DIR
    / "hsk1_4_vietnamese_review.csv"
)

MANUAL_FILE = (
    HSK_DIR
    / "hsk1_4_vietnamese_manual.csv"
)


# =========================================================
# THÔNG TIN NGUỒN
# =========================================================
SOURCE_NAME = "CVDICT"

SOURCE_URL = (
    "https://github.com/ph0ngp/CVDICT"
)

SOURCE_LICENSE = (
    "CC BY-SA 4.0"
)

SOURCE_NOTE = (
    "Tu dien Trung-Viet CVDICT, "
    "duoc chuyen dich tu CC-CEDICT. "
    "Dung lam nguon nghia tieng Viet de xuat; "
    "khong tu dong coi la da kiem duyet."
)


# =========================================================
# ĐỊNH DẠNG CVDICT
#
# Traditional Simplified [Pinyin] /meaning/meaning/
# =========================================================
ENTRY_PATTERN = re.compile(
    r"^(\S+)\s+(\S+)\s+\[([^\]]+)\]\s+/(.*)/$"
)

CEDICT_KEY_PATTERN = re.compile(
    r"^([^|]+)\|(.+)\[([^\]]+)\]$"
)


# =========================================================
# DOWNLOAD CVDICT
# =========================================================
def download_cvdict():

    if CVDICT_FILE.exists():

        print(
            "Da co file CVDICT local:"
        )

        print(
            CVDICT_FILE
        )

        return

    print(
        "Chua co CVDICT."
    )

    print(
        "Dang tai tu dien Trung-Viet..."
    )

    request = Request(
        CVDICT_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "HocTiengTrungDB/1.0"
            )
        },
    )

    with urlopen(
        request,
        timeout=120,
    ) as response:

        content = response.read()

    CVDICT_FILE.write_bytes(
        content
    )

    print(
        "Da tai CVDICT:"
    )

    print(
        CVDICT_FILE
    )


# =========================================================
# CHUẨN HÓA PINYIN SỐ
#
# Chỉ chuẩn hóa cách trình bày.
# KHÔNG xóa thanh.
#
# Bei3 jing1
# vẫn khác
# bei3 jing1
#
# để tránh nhập nhầm tên riêng.
# =========================================================
def normalize_numbered_pinyin(value):

    if not value:
        return ""

    value = value.strip()

    value = value.replace(
        "ü",
        "u:",
    )

    value = value.replace(
        "Ü",
        "U:",
    )

    # Khoảng trắng liên tiếp -> 1 khoảng trắng
    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value


# =========================================================
# LOẠI TRÙNG NHƯNG GIỮ THỨ TỰ
# =========================================================
def unique_keep_order(values):

    result = []
    seen = set()

    for value in values:

        if not value:
            continue

        if value in seen:
            continue

        seen.add(value)
        result.append(value)

    return result


# =========================================================
# PARSE 1 DÒNG CVDICT
# =========================================================
def parse_cvdict_line(line):

    line = line.strip()

    if not line:
        return None

    if line.startswith("#"):
        return None

    match = ENTRY_PATTERN.match(
        line
    )

    if not match:
        return None

    traditional = (
        match.group(1)
        .strip()
    )

    simplified = (
        match.group(2)
        .strip()
    )

    pinyin = (
        match.group(3)
        .strip()
    )

    definition_block = (
        match.group(4)
        .strip()
    )

    meanings = [
        item.strip()
        for item
        in definition_block.split("/")
        if item.strip()
    ]

    if (
        not simplified
        or not pinyin
        or not meanings
    ):
        return None

    return {
        "traditional": traditional,
        "simplified": simplified,
        "pinyin": pinyin,
        "meaning": " / ".join(
            meanings
        ),
    }


# =========================================================
# ĐỌC CVDICT
#
# Tạo:
#
# 1. index exact:
#    (chữ giản thể, Pinyin)
#
# 2. index theo chữ:
#    chữ giản thể
# =========================================================
def load_cvdict():

    exact_index = defaultdict(
        list
    )

    word_index = defaultdict(
        list
    )

    total_lines = 0
    valid_entries = 0

    with open(
        CVDICT_FILE,
        "r",
        encoding="utf-8-sig",
        errors="replace",
    ) as file:

        for line in file:

            total_lines += 1

            entry = parse_cvdict_line(
                line
            )

            if entry is None:
                continue

            valid_entries += 1

            key = (
                entry["simplified"],
                normalize_numbered_pinyin(
                    entry["pinyin"]
                ),
            )

            exact_index[
                key
            ].append(
                entry
            )

            word_index[
                entry["simplified"]
            ].append(
                entry
            )

            if (
                valid_entries
                % 20000
                == 0
            ):

                print(
                    "Da doc CVDICT: "
                    f"{valid_entries} muc..."
                )

    return (
        exact_index,
        word_index,
        total_lines,
        valid_entries,
    )


# =========================================================
# PARSE CEDICT KEY
#
# Ví dụ:
#
# 愛|爱[ai4]
#
# =========================================================
def parse_cedict_key(value):

    value = (
        value or ""
    ).strip()

    match = (
        CEDICT_KEY_PATTERN.match(
            value
        )
    )

    if not match:
        return None

    return {
        "traditional":
            match.group(1).strip(),

        "simplified":
            match.group(2).strip(),

        "pinyin":
            match.group(3).strip(),
    }


# =========================================================
# TÁCH CÁC CEDICT KEY
# =========================================================
def get_cedict_keys(row):

    value = (
        row.get(
            "CEDICTKey",
            "",
        )
        or ""
    ).strip()

    if not value:
        return []

    return [
        item.strip()
        for item
        in value.split(" || ")
        if item.strip()
    ]


# =========================================================
# TÌM NGHĨA VIỆT CHO 1 DÒNG HSK
# =========================================================
def find_vietnamese_meaning(
    row,
    exact_index,
    word_index,
):

    # =====================================================
    # CÁCH 1:
    # Dùng CEDICTKey chính xác
    #
    # Đây là cách ưu tiên nhất.
    # =====================================================
    raw_keys = get_cedict_keys(
        row
    )

    exact_matches = []

    missing_keys = []

    for raw_key in raw_keys:

        parsed = parse_cedict_key(
            raw_key
        )

        if not parsed:
            missing_keys.append(
                raw_key
            )
            continue

        lookup_key = (
            parsed["simplified"],
            normalize_numbered_pinyin(
                parsed["pinyin"]
            ),
        )

        matches = (
            exact_index.get(
                lookup_key,
                [],
            )
        )

        if matches:
            exact_matches.extend(
                matches
            )
        else:
            missing_keys.append(
                raw_key
            )

    if exact_matches:

        meanings = (
            unique_keep_order(
                [
                    item["meaning"]
                    for item
                    in exact_matches
                ]
            )
        )

        pinyins = (
            unique_keep_order(
                [
                    item["pinyin"]
                    for item
                    in exact_matches
                ]
            )
        )

        words = (
            unique_keep_order(
                [
                    item["simplified"]
                    for item
                    in exact_matches
                ]
            )
        )

        if missing_keys:

            status = (
                "cvdict_khop_mot_phan"
            )

            manual = "1"

        else:

            status = (
                "cvdict_khop_chinh_xac"
            )

            manual = "0"

        return {
            "meaning":
                " || ".join(
                    meanings
                ),

            "words":
                " | ".join(
                    words
                ),

            "pinyins":
                " | ".join(
                    pinyins
                ),

            "status":
                status,

            "manual":
                manual,

            "missing":
                " || ".join(
                    missing_keys
                ),
        }

    # =====================================================
    # CÁCH 2:
    # Những mục HSK không có CEDICTKey.
    #
    # Tra trực tiếp bằng TuChinh.
    # =====================================================
    word = (
        row.get(
            "TuChinh",
            "",
        )
        or ""
    ).strip()

    if not word:

        return {
            "meaning": "",
            "words": "",
            "pinyins": "",
            "status":
                "khong_co_tu_tra",

            "manual": "1",
            "missing": "",
        }

    candidates = (
        word_index.get(
            word,
            [],
        )
    )

    # -----------------------------------------------------
    # Không có CVDICT
    # -----------------------------------------------------
    if not candidates:

        return {
            "meaning": "",
            "words": "",
            "pinyins": "",
            "status":
                "khong_tim_thay_cvdict",

            "manual": "1",
            "missing": word,
        }

    # -----------------------------------------------------
    # Chỉ có đúng 1 entry
    # -----------------------------------------------------
    if len(candidates) == 1:

        candidate = (
            candidates[0]
        )

        return {
            "meaning":
                candidate[
                    "meaning"
                ],

            "words":
                candidate[
                    "simplified"
                ],

            "pinyins":
                candidate[
                    "pinyin"
                ],

            "status":
                "cvdict_fallback_1",

            "manual":
                "1",

            "missing":
                "",
        }

    # =====================================================
    # CÁCH 3:
    # Nếu có nhiều entry,
    # thử dùng Pinyin CC-CEDICT đã đối chiếu.
    # =====================================================
    cedict_pinyin_text = (
        row.get(
            "PinyinCedictKhop",
            "",
        )
        or ""
    )

    target_pinyins = {
        normalize_numbered_pinyin(
            item.strip()
        )
        for item
        in cedict_pinyin_text.split(
            " | "
        )
        if item.strip()
    }

    if target_pinyins:

        matched = [
            candidate
            for candidate
            in candidates
            if (
                normalize_numbered_pinyin(
                    candidate[
                        "pinyin"
                    ]
                )
                in target_pinyins
            )
        ]

        if matched:

            meanings = (
                unique_keep_order(
                    [
                        item[
                            "meaning"
                        ]
                        for item
                        in matched
                    ]
                )
            )

            pinyins = (
                unique_keep_order(
                    [
                        item[
                            "pinyin"
                        ]
                        for item
                        in matched
                    ]
                )
            )

            return {
                "meaning":
                    " || ".join(
                        meanings
                    ),

                "words":
                    word,

                "pinyins":
                    " | ".join(
                        pinyins
                    ),

                "status":
                    "cvdict_fallback_pinyin",

                "manual":
                    "1",

                "missing":
                    "",
            }

    # -----------------------------------------------------
    # Còn mơ hồ -> không tự chọn
    # -----------------------------------------------------
    return {
        "meaning": "",
        "words": word,
        "pinyins": "",
        "status":
            "cvdict_nhieu_ket_qua",

        "manual": "1",
        "missing": word,
    }


# =========================================================
# THÊM / LẤY NGUỒN CVDICT
# =========================================================
def get_or_create_source(
    cursor,
):

    cursor.execute(
        """
        SELECT MaNguon
        FROM dbo.NguonDuLieu
        WHERE Ten = ?
        """,
        SOURCE_NAME,
    )

    row = cursor.fetchone()

    if row:

        ma_nguon = row[0]

        cursor.execute(
            """
            UPDATE dbo.NguonDuLieu

            SET
                LienKetNguon = ?,
                GiayPhep = ?,
                GhiChu = ?

            WHERE MaNguon = ?
            """,
            SOURCE_URL,
            SOURCE_LICENSE,
            SOURCE_NOTE,
            ma_nguon,
        )

        return ma_nguon

    cursor.execute(
        """
        INSERT INTO dbo.NguonDuLieu
        (
            Ten,
            LienKetNguon,
            GiayPhep,
            GhiChu,
            NgayLayDuLieu
        )

        OUTPUT INSERTED.MaNguon

        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            SYSDATETIME()
        )
        """,
        SOURCE_NAME,
        SOURCE_URL,
        SOURCE_LICENSE,
        SOURCE_NOTE,
    )

    return cursor.fetchone()[0]


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 72)
        print(
            "TAO NGHIA TIENG VIET "
            "DE XUAT CHO HSK 1-4"
        )
        print("=" * 72)

        if not INPUT_FILE.exists():

            raise FileNotFoundError(
                "Khong tim thay file:\n"
                f"{INPUT_FILE}\n"
                "Hay chay 05e truoc."
            )

        # -------------------------------------------------
        # Tải CVDICT
        # -------------------------------------------------
        download_cvdict()

        print()
        print(
            "Dang doc CVDICT..."
        )

        (
            exact_index,
            word_index,
            total_lines,
            valid_entries,
        ) = load_cvdict()

        print()
        print(
            "Tong dong CVDICT: "
            f"{total_lines}"
        )

        print(
            "So entry hop le: "
            f"{valid_entries}"
        )

        if valid_entries < 100000:

            raise RuntimeError(
                "CVDICT co qua it entry. "
                "Dung xu ly de tranh dung "
                "file khong day du."
            )

        # -------------------------------------------------
        # Đọc final base
        # -------------------------------------------------
        with open(
            INPUT_FILE,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            reader = csv.DictReader(
                file
            )

            rows = list(
                reader
            )

            fieldnames = list(
                reader.fieldnames
                or []
            )

        print()
        print(
            "So muc HSK dau vao: "
            f"{len(rows)}"
        )

        if len(rows) != 3245:

            raise RuntimeError(
                "File final khong co "
                "dung 3245 muc."
            )

        # -------------------------------------------------
        # Đăng ký nguồn
        # -------------------------------------------------
        conn = get_connection()
        cursor = conn.cursor()

        ma_nguon_cvdict = (
            get_or_create_source(
                cursor
            )
        )

        conn.commit()

        print(
            "MaNguon CVDICT: "
            f"{ma_nguon_cvdict}"
        )

        # -------------------------------------------------
        # Cột mới
        # -------------------------------------------------
        extra_fields = [
            "MaNguonNghiaViet",
            "NguonNghiaViet",
            "TuCvdictKhop",
            "PinyinCvdictKhop",
            "TrangThaiNghiaViet",
            "CanKiemTraNghia",
            "CedictKeyKhongKhopCvdict",
        ]

        for field in extra_fields:

            if field not in fieldnames:
                fieldnames.append(
                    field
                )

        # NghiaTiengViet và DaDuyet
        # đã tồn tại trong file base.
        if (
            "NghiaTiengViet"
            not in fieldnames
        ):
            fieldnames.append(
                "NghiaTiengViet"
            )

        if "DaDuyet" not in fieldnames:
            fieldnames.append(
                "DaDuyet"
            )

        # -------------------------------------------------
        # Thống kê
        # -------------------------------------------------
        stats = defaultdict(int)

        output_rows = []
        manual_rows = []

        # -------------------------------------------------
        # Ghép nghĩa Việt
        # -------------------------------------------------
        for row in rows:

            result = (
                find_vietnamese_meaning(
                    row,
                    exact_index,
                    word_index,
                )
            )

            row[
                "NghiaTiengViet"
            ] = result[
                "meaning"
            ]

            row[
                "MaNguonNghiaViet"
            ] = str(
                ma_nguon_cvdict
            )

            row[
                "NguonNghiaViet"
            ] = SOURCE_NAME

            row[
                "TuCvdictKhop"
            ] = result[
                "words"
            ]

            row[
                "PinyinCvdictKhop"
            ] = result[
                "pinyins"
            ]

            row[
                "TrangThaiNghiaViet"
            ] = result[
                "status"
            ]

            row[
                "CanKiemTraNghia"
            ] = result[
                "manual"
            ]

            row[
                "CedictKeyKhongKhopCvdict"
            ] = result[
                "missing"
            ]

            # TUYỆT ĐỐI chưa duyệt tự động
            row[
                "DaDuyet"
            ] = "0"

            stats[
                result["status"]
            ] += 1

            output_rows.append(
                row
            )

            if (
                result["manual"]
                == "1"
                or not result[
                    "meaning"
                ]
            ):

                manual_rows.append(
                    row
                )

        # -------------------------------------------------
        # Ghi file review
        # -------------------------------------------------
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
                output_rows
            )

        # -------------------------------------------------
        # Ghi file cần xem riêng
        # -------------------------------------------------
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

        # -------------------------------------------------
        # KẾT QUẢ
        # -------------------------------------------------
        print()
        print("-" * 72)
        print(
            "KET QUA NGHIA TIENG VIET"
        )
        print("-" * 72)

        print(
            "Khop chinh xac CVDICT: "
            f"{stats['cvdict_khop_chinh_xac']}"
        )

        print(
            "Khop mot phan CVDICT: "
            f"{stats['cvdict_khop_mot_phan']}"
        )

        print(
            "Fallback 1 entry: "
            f"{stats['cvdict_fallback_1']}"
        )

        print(
            "Fallback bang Pinyin: "
            f"{stats['cvdict_fallback_pinyin']}"
        )

        print(
            "Nhieu ket qua con mo ho: "
            f"{stats['cvdict_nhieu_ket_qua']}"
        )

        print(
            "Khong tim thay CVDICT: "
            f"{stats['khong_tim_thay_cvdict']}"
        )

        print(
            "Khong co tu tra: "
            f"{stats['khong_co_tu_tra']}"
        )

        print()
        print(
            "Tong file review: "
            f"{len(output_rows)}"
        )

        print(
            "Can xem rieng: "
            f"{len(manual_rows)}"
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
            "File can xem rieng:"
        )

        print(
            MANUAL_FILE
        )

        print()
        print(
            "TAT CA DaDuyet VAN = 0."
        )

        print(
            "CHUA INSERT VAO TuVung."
        )

        print()
        print("=" * 72)
        print("HOAN TAT")
        print("=" * 72)

        cursor.close()

    except Exception as e:

        if conn:
            conn.rollback()

        print()
        print("=" * 72)
        print("THUC HIEN THAT BAI")
        print("=" * 72)

        print(
            "Loi:",
            e,
        )

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()