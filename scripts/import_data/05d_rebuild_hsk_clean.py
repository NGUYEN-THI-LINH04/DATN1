from pathlib import Path
import sys
import csv
import json
import re
from collections import defaultdict
from urllib.request import Request, urlopen


# =========================================================
# THƯ MỤC GỐC
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# THƯ MỤC DỮ LIỆU HSK
# =========================================================
HSK_DIR = ROOT_DIR / "data_sources" / "hsk"

HSK_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# FILE THAM CHIẾU HSK ĐÃ ĐƯỢC LÀM SẠCH
#
# Nguồn chính của chuẩn vẫn là:
# GF0025-2021 / ChineseTest.
#
# File hsk30 chỉ được dùng làm dữ liệu ETL trung gian
# để xử lý:
# - biến thể
# - Pinyin
# - từ loại
# - đối chiếu CC-CEDICT
# =========================================================
HSK30_URL = (
    "https://raw.githubusercontent.com/"
    "ivankra/hsk30/master/hsk30.csv"
)

HSK30_FILE = (
    HSK_DIR
    / "hsk30_clean_reference.csv"
)


# =========================================================
# FILE KẾT QUẢ
# =========================================================
READY_FILE = (
    HSK_DIR
    / "hsk1_4_clean_ready.csv"
)

MANUAL_FILE = (
    HSK_DIR
    / "hsk1_4_clean_manual.csv"
)


# =========================================================
# MAP TỪ LOẠI
# =========================================================
POS_MAP = {
    "N": "名",
    "V": "动",
    "Adj": "形",
    "Adv": "副",
    "Pron": "代",
    "Num": "数",
    "M": "量",
    "Prep": "介",
    "Conj": "连",
    "Aux": "助",
    "Int": "叹",
    "Prefix": "前缀",
    "Suffix": "后缀",
    "Phonetic": "拟声",
}


# =========================================================
# CHUYỂN POS VÍ DỤ:
#
# V/N     -> 动、名
# N/M/V   -> 名、量、动
# =========================================================
def convert_pos(value):
    if not value:
        return ""

    parts = [
        item.strip()
        for item in value.split("/")
        if item.strip()
    ]

    converted = []

    for part in parts:
        converted.append(
            POS_MAP.get(
                part,
                part,
            )
        )

    return "、".join(converted)


# =========================================================
# TẢI FILE HSK30 NẾU CHƯA CÓ
# =========================================================
def download_hsk30():

    if HSK30_FILE.exists():
        print(
            "Da co file HSK sach local:"
        )
        print(
            HSK30_FILE
        )
        return

    print(
        "Dang tai file HSK "
        "da duoc lam sach..."
    )

    request = Request(
        HSK30_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "HocTiengTrungDB/1.0"
            )
        },
    )

    with urlopen(
        request,
        timeout=60,
    ) as response:

        content = response.read()

    HSK30_FILE.write_bytes(
        content
    )

    print(
        "Da luu:"
    )

    print(
        HSK30_FILE
    )


# =========================================================
# CHUẨN HÓA PINYIN CC-CEDICT
#
# Không lowercase!
#
# Vì:
# an1  != An1
# bai2 != Bai2
#
# Chữ hoa trong CC-CEDICT có thể biểu thị
# tên riêng/họ/tên địa danh.
# =========================================================
def normalize_cedict_pinyin(value):

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

    value = value.replace(
        " ",
        "",
    )

    value = value.replace(
        "'",
        "",
    )

    value = value.replace(
        "’",
        "",
    )

    value = value.replace(
        "·",
        "",
    )

    value = value.replace(
        "-",
        "",
    )

    return value


# =========================================================
# PARSE 1 KHÓA CEDICT
#
# Ví dụ:
#
# 愛|爱[ai4]
#
# 匯率|汇率[hui4 lu:4]
# =========================================================
CEDICT_PATTERN = re.compile(
    r"^([^|]+)\|(.+)\[([^\]]+)\]$"
)


def parse_cedict_key(value):

    value = (
        value or ""
    ).strip()

    match = CEDICT_PATTERN.match(
        value
    )

    if not match:
        return None

    traditional = (
        match.group(1).strip()
    )

    simplified = (
        match.group(2).strip()
    )

    pinyin = (
        match.group(3).strip()
    )

    return {
        "traditional": traditional,
        "simplified": simplified,
        "pinyin": pinyin,
    }


# =========================================================
# TÁCH CÁC KHÓA CEDICT
#
# Ví dụ:
#
# A|A[...] / B|B[...]
# =========================================================
def split_cedict_keys(value):

    if not value:
        return []

    result = []

    for item in value.split("/"):

        item = item.strip()

        if item:
            result.append(item)

    return result


# =========================================================
# LOẠI TRÙNG GIỮ NGUYÊN THỨ TỰ
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
# LẤY CEDICT KEY TỪ MỘT DÒNG HSK
#
# Ngoài trường CEDICT chính,
# ta đọc cả Variants.
#
# Ví dụ:
#
# 爸爸|爸
#
# Variants chứa:
# 爸爸 -> CC-CEDICT
# 爸   -> CC-CEDICT
#
# Với Prefix/Suffix:
# 第（第二）
#
# 第二 chỉ là Example,
# không được coi là một mục HSK độc lập.
# =========================================================
def collect_cedict_keys(row):

    keys = []

    main_cedict = (
        row.get("CEDICT")
        or ""
    ).strip()

    keys.extend(
        split_cedict_keys(
            main_cedict
        )
    )

    variants_text = (
        row.get("Variants")
        or ""
    ).strip()

    if variants_text:

        try:
            variants = json.loads(
                variants_text
            )

            for variant in variants:

                # Example=1 nghĩa là chỉ là
                # ví dụ minh họa cho prefix/suffix.
                if str(
                    variant.get(
                        "Example",
                        "",
                    )
                ) == "1":
                    continue

                cedict_value = (
                    variant.get(
                        "CEDICT"
                    )
                    or ""
                ).strip()

                keys.extend(
                    split_cedict_keys(
                        cedict_value
                    )
                )

        except json.JSONDecodeError:

            # Không dừng toàn bộ chương trình.
            # Dòng đó sẽ được đưa sang manual
            # nếu không có CEDICT hợp lệ.
            pass

    return unique_keep_order(
        keys
    )


# =========================================================
# ĐỌC HSK 1 → 4
# =========================================================
def read_hsk_rows():

    rows = []

    counts = defaultdict(int)

    with open(
        HSK30_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        required = {
            "ID",
            "Simplified",
            "Pinyin",
            "POS",
            "Level",
            "WebNo",
            "WebPinyin",
            "Variants",
            "CEDICT",
        }

        missing = (
            required
            - set(
                reader.fieldnames
                or []
            )
        )

        if missing:
            raise RuntimeError(
                "File HSK30 thieu cot: "
                + ", ".join(
                    sorted(missing)
                )
            )

        for row in reader:

            level_text = (
                row.get("Level")
                or ""
            ).strip()

            if level_text not in {
                "1",
                "2",
                "3",
                "4",
            }:
                continue

            level = int(
                level_text
            )

            simplified = (
                row.get(
                    "Simplified"
                )
                or ""
            ).strip()

            if not simplified:
                continue

            # ---------------------------------------------
            # Dạng chính để hiển thị.
            #
            # 爸爸|爸 -> 爸爸
            # 零|〇   -> 零
            # ---------------------------------------------
            main_word = (
                simplified.split("|")[0]
                .strip()
            )

            variants = [
                item.strip()
                for item
                in simplified.split("|")[1:]
                if item.strip()
            ]

            pinyin = (
                row.get("Pinyin")
                or ""
            ).strip()

            main_pinyin = (
                pinyin.split("|")[0]
                .strip()
            )

            cedict_keys = (
                collect_cedict_keys(
                    row
                )
            )

            rows.append(
                {
                    "ID":
                        row.get(
                            "ID",
                            "",
                        ),

                    "WebNo":
                        row.get(
                            "WebNo",
                            "",
                        ),

                    "CapDoHSK":
                        level,

                    "TuGoc":
                        simplified,

                    "TuChinh":
                        main_word,

                    "BienThe":
                        " | ".join(
                            variants
                        ),

                    "PinyinChuan":
                        main_pinyin,

                    "PinyinGoc":
                        pinyin,

                    "WebPinyin":
                        row.get(
                            "WebPinyin",
                            "",
                        ),

                    "TuLoaiMa":
                        row.get(
                            "POS",
                            "",
                        ),

                    "TuLoaiChuan":
                        convert_pos(
                            row.get(
                                "POS",
                                "",
                            )
                        ),

                    "CEDICTKeys":
                        cedict_keys,
                }
            )

            counts[level] += 1

    return rows, counts


# =========================================================
# LẤY MaNguon CC-CEDICT
# =========================================================
def get_cedict_source_id(cursor):

    cursor.execute(
        """
        SELECT MaNguon
        FROM dbo.NguonDuLieu
        WHERE Ten = ?
        """,
        "CC-CEDICT",
    )

    row = cursor.fetchone()

    if not row:
        raise RuntimeError(
            "Khong tim thay CC-CEDICT "
            "trong NguonDuLieu."
        )

    return row[0]


# =========================================================
# LẤY CÁC TỪ GIẢN THỂ CẦN TRA TRONG SQL
# =========================================================
def collect_lookup_words(
    hsk_rows,
):

    words = set()

    for row in hsk_rows:

        for key in row[
            "CEDICTKeys"
        ]:

            parsed = (
                parse_cedict_key(
                    key
                )
            )

            if parsed:
                words.add(
                    parsed[
                        "simplified"
                    ]
                )

    return sorted(words)


# =========================================================
# ĐỌC CÁC ENTRY CC-CEDICT CẦN THIẾT TỪ SQL
# =========================================================
def load_cedict_from_sql(
    cursor,
    ma_nguon,
    words,
):

    index = defaultdict(list)

    CHUNK_SIZE = 500

    for start in range(
        0,
        len(words),
        CHUNK_SIZE,
    ):

        chunk = words[
            start:
            start + CHUNK_SIZE
        ]

        if not chunk:
            continue

        placeholders = ",".join(
            "?"
            for _ in chunk
        )

        sql = f"""
            SELECT
                MaMucTu,
                ChuHan,
                PhienAm,
                NghiaGoc
            FROM dbo.MucTuDien
            WHERE MaNguon = ?
              AND ChuHan IN
              ({placeholders})
        """

        params = [
            ma_nguon,
            *chunk,
        ]

        cursor.execute(
            sql,
            params,
        )

        for db_row in cursor.fetchall():

            key = (
                db_row.ChuHan,
                normalize_cedict_pinyin(
                    db_row.PhienAm
                ),
            )

            index[key].append(
                {
                    "MaMucTu":
                        db_row.MaMucTu,

                    "ChuHan":
                        db_row.ChuHan,

                    "PhienAm":
                        db_row.PhienAm,

                    "NghiaGoc":
                        db_row.NghiaGoc
                        or "",
                }
            )

    return index


# =========================================================
# ĐỐI CHIẾU 1 DÒNG HSK
# =========================================================
def match_hsk_row(
    row,
    cedict_index,
):

    matches = []

    parsed_keys = []

    for raw_key in row[
        "CEDICTKeys"
    ]:

        parsed = (
            parse_cedict_key(
                raw_key
            )
        )

        if not parsed:
            continue

        parsed_keys.append(
            parsed
        )

        lookup_key = (
            parsed["simplified"],
            normalize_cedict_pinyin(
                parsed["pinyin"]
            ),
        )

        found = (
            cedict_index.get(
                lookup_key,
                [],
            )
        )

        matches.extend(
            found
        )

    # ---------------------------------------------
    # Loại entry trùng theo MaMucTu
    # ---------------------------------------------
    unique_matches = []

    seen_ids = set()

    for match in matches:

        ma_muc_tu = (
            match["MaMucTu"]
        )

        if ma_muc_tu in seen_ids:
            continue

        seen_ids.add(
            ma_muc_tu
        )

        unique_matches.append(
            match
        )

    return (
        parsed_keys,
        unique_matches,
    )


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 72)
        print(
            "XAY DUNG LAI DANH SACH "
            "HSK 1-4 SACH"
        )
        print("=" * 72)

        # -------------------------------------------------
        # 1. TẢI FILE SẠCH
        # -------------------------------------------------
        download_hsk30()

        # -------------------------------------------------
        # 2. ĐỌC HSK
        # -------------------------------------------------
        print()
        print(
            "Dang doc HSK 1-4..."
        )

        hsk_rows, counts = (
            read_hsk_rows()
        )

        print()
        print("SO LUONG:")

        for level in range(
            1,
            5,
        ):
            print(
                f"HSK {level}: "
                f"{counts[level]}"
            )

        print(
            "Tong: "
            f"{len(hsk_rows)}"
        )

        # Kiểm tra chuẩn số lượng
        expected = {
            1: 500,
            2: 772,
            3: 973,
            4: 1000,
        }

        for level, expected_count in (
            expected.items()
        ):

            if (
                counts[level]
                != expected_count
            ):
                raise RuntimeError(
                    f"HSK {level} co "
                    f"{counts[level]} muc, "
                    f"khong dung "
                    f"{expected_count}."
                )

        # -------------------------------------------------
        # 3. SQL
        # -------------------------------------------------
        conn = get_connection()
        cursor = conn.cursor()

        ma_nguon = (
            get_cedict_source_id(
                cursor
            )
        )

        print()
        print(
            "MaNguon CC-CEDICT: "
            f"{ma_nguon}"
        )

        # -------------------------------------------------
        # 4. LẤY CÁC TỪ CẦN TRA
        # -------------------------------------------------
        lookup_words = (
            collect_lookup_words(
                hsk_rows
            )
        )

        print(
            "So tu can tra "
            "trong MucTuDien: "
            f"{len(lookup_words)}"
        )

        # -------------------------------------------------
        # 5. ĐỌC CC-CEDICT TỪ SQL
        # -------------------------------------------------
        print()
        print(
            "Dang doi chieu voi "
            "MucTuDien..."
        )

        cedict_index = (
            load_cedict_from_sql(
                cursor,
                ma_nguon,
                lookup_words,
            )
        )

        # -------------------------------------------------
        # 6. CỘT FILE OUTPUT
        # -------------------------------------------------
        fields = [
            "ID",
            "WebNo",
            "CapDoHSK",

            "TuGoc",
            "TuChinh",
            "BienThe",

            "PinyinChuan",
            "PinyinGoc",
            "WebPinyin",

            "TuLoaiMa",
            "TuLoaiChuan",

            "CEDICTKey",

            "SoKetQuaCedict",
            "MaMucTuCedict",
            "TuCedictKhop",
            "PinyinCedictKhop",
            "NghiaAnhCedict",

            "TrangThaiDoiChieu",

            "NghiaTiengViet",
            "DaDuyet",
        ]

        ready_rows = []
        manual_rows = []

        # -------------------------------------------------
        # 7. ĐỐI CHIẾU
        # -------------------------------------------------
        for row in hsk_rows:

            (
                parsed_keys,
                matches,
            ) = match_hsk_row(
                row,
                cedict_index,
            )

            cedict_key_text = (
                " || ".join(
                    row[
                        "CEDICTKeys"
                    ]
                )
            )

            if matches:

                ma_muc_tu = (
                    " | ".join(
                        str(
                            item[
                                "MaMucTu"
                            ]
                        )
                        for item
                        in matches
                    )
                )

                matched_words = (
                    unique_keep_order(
                        [
                            item["ChuHan"]
                            for item
                            in matches
                        ]
                    )
                )

                matched_pinyin = (
                    unique_keep_order(
                        [
                            item["PhienAm"]
                            for item
                            in matches
                        ]
                    )
                )

                meanings = (
                    unique_keep_order(
                        [
                            item["NghiaGoc"]
                            for item
                            in matches
                            if item[
                                "NghiaGoc"
                            ]
                        ]
                    )
                )

                output = {
                    **row,

                    "CEDICTKey":
                        cedict_key_text,

                    "SoKetQuaCedict":
                        len(matches),

                    "MaMucTuCedict":
                        ma_muc_tu,

                    "TuCedictKhop":
                        " | ".join(
                            matched_words
                        ),

                    "PinyinCedictKhop":
                        " | ".join(
                            matched_pinyin
                        ),

                    "NghiaAnhCedict":
                        " || ".join(
                            meanings
                        ),

                    "TrangThaiDoiChieu":
                        "san_sang_viet_hoa",

                    "NghiaTiengViet":
                        "",

                    "DaDuyet":
                        0,
                }

                # Xóa field chỉ dùng nội bộ
                output.pop(
                    "CEDICTKeys",
                    None,
                )

                ready_rows.append(
                    output
                )

            else:

                if row[
                    "CEDICTKeys"
                ]:

                    status = (
                        "cedict_key_"
                        "khong_khop_sql"
                    )

                else:

                    status = (
                        "khong_co_"
                        "cedict_mapping"
                    )

                output = {
                    **row,

                    "CEDICTKey":
                        cedict_key_text,

                    "SoKetQuaCedict":
                        0,

                    "MaMucTuCedict":
                        "",

                    "TuCedictKhop":
                        "",

                    "PinyinCedictKhop":
                        "",

                    "NghiaAnhCedict":
                        "",

                    "TrangThaiDoiChieu":
                        status,

                    "NghiaTiengViet":
                        "",

                    "DaDuyet":
                        0,
                }

                output.pop(
                    "CEDICTKeys",
                    None,
                )

                manual_rows.append(
                    output
                )

        # -------------------------------------------------
        # 8. GHI FILE SẠCH
        # -------------------------------------------------
        with open(
            READY_FILE,
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fields,
            )

            writer.writeheader()

            writer.writerows(
                ready_rows
            )

        # -------------------------------------------------
        # 9. GHI FILE MANUAL
        # -------------------------------------------------
        with open(
            MANUAL_FILE,
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fields,
            )

            writer.writeheader()

            writer.writerows(
                manual_rows
            )

        # -------------------------------------------------
        # 10. KẾT QUẢ
        # -------------------------------------------------
        print()
        print("-" * 72)
        print("KET QUA")
        print("-" * 72)

        print(
            "Tong HSK 1-4: "
            f"{len(hsk_rows)}"
        )

        print(
            "San sang Viet hoa: "
            f"{len(ready_rows)}"
        )

        print(
            "Can kiem tra them: "
            f"{len(manual_rows)}"
        )

        print()

        print(
            "File sach:"
        )

        print(
            READY_FILE
        )

        print()

        print(
            "File can kiem tra:"
        )

        print(
            MANUAL_FILE
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