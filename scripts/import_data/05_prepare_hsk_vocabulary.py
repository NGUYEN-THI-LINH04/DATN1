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
# THƯ MỤC HSK
# Script tự tạo nếu chưa có
# =========================================================
HSK_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
)

HSK_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# FILE NGUỒN VÀ FILE KẾT QUẢ
# =========================================================
HSK_SOURCE_FILE = (
    HSK_DIR
    / "hsk_vocabulary_gf0025.csv"
)

HSK_REVIEW_FILE = (
    HSK_DIR
    / "hsk1_4_review.csv"
)


# =========================================================
# NGUỒN
#
# CSV máy đọc:
# HSK-official-Query-System
#
# README của repository ghi nguồn dữ liệu từ hệ thống
# tra cứu chuẩn HSK/ChineseTest và GF0025-2021.
# =========================================================
RAW_CSV_URL = (
    "https://raw.githubusercontent.com/"
    "shawkynasr/"
    "HSK-official-Query-System/"
    "main/"
    "%E8%AF%8D%E6%B1%87.csv"
)

SOURCE_NAME = (
    "GF0025-2021 - Tu vung HSK"
)

SOURCE_PAGE = (
    "https://www.chinesetest.cn/"
    "standardsAction.do?means=standardInfo"
)

SOURCE_NOTE = (
    "Danh sach tu vung phan cap theo "
    "《国际中文教育中文水平等级标准》 "
    "(GF0025-2021). "
    "Ban CSV may doc dung trong ETL duoc doi chieu "
    "tu HSK-official-Query-System. "
    "Nguon nay chi dung de xac dinh cap do, tu, "
    "pinyin va tu loai; khong phai nguon nghia tieng Viet."
)


# =========================================================
# MAP CẤP ĐỘ
# Chỉ lấy HSK 1 → HSK 4
# =========================================================
LEVEL_MAP = {
    "一级": 1,
    "二级": 2,
    "三级": 3,
    "四级": 4,
}


# =========================================================
# TẢI FILE HSK NẾU CHƯA CÓ
# =========================================================
def download_hsk_file():

    if HSK_SOURCE_FILE.exists():
        print(
            f"Da co file nguon: "
            f"{HSK_SOURCE_FILE.name}"
        )
        return

    print(
        "Chua co file HSK local."
    )

    print(
        "Dang tai danh sach tu vung HSK..."
    )

    request = Request(
        RAW_CSV_URL,
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

    HSK_SOURCE_FILE.write_bytes(
        content
    )

    print(
        f"Da luu file: "
        f"{HSK_SOURCE_FILE}"
    )


# =========================================================
# CHUẨN HÓA TỪ TRA CỨU
#
# Một số mục chuẩn có thể có dạng:
#
# 爸爸∣爸
#
# Ta giữ nguyên TuGoc nhưng tách các dạng
# để đối chiếu CC-CEDICT.
# =========================================================
def get_word_variants(word):
    if not word:
        return []

    parts = re.split(
        r"[∣|]",
        word,
    )

    result = []

    for part in parts:
        part = part.strip()

        if (
            part
            and part not in result
        ):
            result.append(part)

    return result


# =========================================================
# ĐỌC FILE HSK
# =========================================================
def read_hsk_vocabulary():

    items = []

    with open(
        HSK_SOURCE_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        required_columns = {
            "No.",
            "级别",
            "词语",
            "拼音",
            "词性",
        }

        if not reader.fieldnames:
            raise RuntimeError(
                "File HSK khong co header."
            )

        missing_columns = (
            required_columns
            - set(reader.fieldnames)
        )

        if missing_columns:
            raise RuntimeError(
                "File HSK thieu cot: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )

        for row in reader:

            level_text = (
                row.get("级别") or ""
            ).strip()

            # Chỉ HSK 1 → 4
            if level_text not in LEVEL_MAP:
                continue

            word = (
                row.get("词语") or ""
            ).strip()

            pinyin = (
                row.get("拼音") or ""
            ).strip()

            part_of_speech = (
                row.get("词性") or ""
            ).strip()

            number = (
                row.get("No.") or ""
            ).strip()

            if not word:
                continue

            variants = (
                get_word_variants(
                    word
                )
            )

            items.append(
                {
                    "number": number,
                    "level": LEVEL_MAP[
                        level_text
                    ],
                    "level_text": level_text,
                    "word_original": word,
                    "variants": variants,
                    "pinyin": pinyin,
                    "part_of_speech": (
                        part_of_speech
                    ),
                }
            )

    return items


# =========================================================
# LẤY MaNguon CỦA CC-CEDICT
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
            "Khong tim thay nguon CC-CEDICT. "
            "Hay chay 01 va 04 truoc."
        )

    return row[0]


# =========================================================
# THÊM / CẬP NHẬT NGUỒN HSK
# =========================================================
def get_or_create_hsk_source(
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

        cursor.execute(
            """
            UPDATE dbo.NguonDuLieu
            SET
                LienKetNguon = ?,
                GhiChu = ?
            WHERE MaNguon = ?
            """,
            SOURCE_PAGE,
            SOURCE_NOTE,
            row[0],
        )

        return row[0]

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
            NULL,
            ?,
            SYSDATETIME()
        )
        """,
        SOURCE_NAME,
        SOURCE_PAGE,
        SOURCE_NOTE,
    )

    return cursor.fetchone()[0]


# =========================================================
# LẤY TOÀN BỘ CÁC BIẾN THỂ CẦN TRA
# =========================================================
def collect_lookup_words(
    hsk_items,
):

    words = set()

    for item in hsk_items:

        for variant in item[
            "variants"
        ]:
            words.add(variant)

    return sorted(words)


# =========================================================
# TRA MucTuDien THEO TỪ
#
# Chia chunk để không vượt giới hạn số parameter
# của SQL Server.
# =========================================================
def load_cedict_matches(
    cursor,
    ma_nguon_cedict,
    words,
):
    result = defaultdict(list)

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
            ORDER BY
                ChuHan,
                MaMucTu
        """

        params = [
            ma_nguon_cedict,
            *chunk,
        ]

        cursor.execute(
            sql,
            params,
        )

        for row in cursor.fetchall():

            result[
                row.ChuHan
            ].append(
                {
                    "ma_muc_tu": (
                        row.MaMucTu
                    ),
                    "pinyin": (
                        row.PhienAm
                        or ""
                    ),
                    "definition": (
                        row.NghiaGoc
                        or ""
                    ),
                }
            )

    return result


# =========================================================
# TẠO FILE REVIEW
# =========================================================
def create_review_file(
    hsk_items,
    cedict_matches,
):

    fieldnames = [
        "SoThuTuChuan",
        "CapDoHSK",
        "CapDoGoc",
        "TuGoc",
        "TuTraCuu",
        "PinyinChuan",
        "TuLoaiChuan",

        "SoKetQuaCedict",
        "MaMucTuCedict",
        "PinyinCedict",
        "NghiaAnhCedict",

        "TrangThaiDoiChieu",

        # Để trống cho bước Việt hóa
        "NghiaTiengViet",
        "DaDuyet",
    ]

    stats = {
        "khop_1": 0,
        "nhieu_ket_qua": 0,
        "khong_tim_thay": 0,
    }

    with open(
        HSK_REVIEW_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for item in hsk_items:

            all_matches = []

            matched_variants = []

            for variant in item[
                "variants"
            ]:

                matches = (
                    cedict_matches.get(
                        variant,
                        [],
                    )
                )

                if matches:

                    matched_variants.append(
                        variant
                    )

                    for match in matches:

                        all_matches.append(
                            {
                                "variant": variant,
                                **match,
                            }
                        )

            # ---------------------------------------------
            # XÁC ĐỊNH TRẠNG THÁI
            # ---------------------------------------------
            if len(all_matches) == 0:

                status = (
                    "khong_tim_thay"
                )

            elif len(all_matches) == 1:

                status = "khop_1"

            else:

                status = (
                    "nhieu_ket_qua"
                )

            stats[status] += 1

            # ---------------------------------------------
            # GHÉP THÔNG TIN CC-CEDICT
            # ---------------------------------------------
            if all_matches:

                ma_muc_tu = " | ".join(
                    str(
                        match[
                            "ma_muc_tu"
                        ]
                    )
                    for match
                    in all_matches
                )

                pinyin_cedict = " | ".join(
                    match["pinyin"]
                    for match
                    in all_matches
                )

                definitions = " || ".join(
                    match[
                        "definition"
                    ]
                    for match
                    in all_matches
                )

                search_word = " | ".join(
                    matched_variants
                )

            else:

                ma_muc_tu = ""
                pinyin_cedict = ""
                definitions = ""

                if item["variants"]:
                    search_word = (
                        item["variants"][0]
                    )
                else:
                    search_word = (
                        item[
                            "word_original"
                        ]
                    )

            writer.writerow(
                {
                    "SoThuTuChuan":
                        item["number"],

                    "CapDoHSK":
                        item["level"],

                    "CapDoGoc":
                        item["level_text"],

                    "TuGoc":
                        item[
                            "word_original"
                        ],

                    "TuTraCuu":
                        search_word,

                    "PinyinChuan":
                        item["pinyin"],

                    "TuLoaiChuan":
                        item[
                            "part_of_speech"
                        ],

                    "SoKetQuaCedict":
                        len(all_matches),

                    "MaMucTuCedict":
                        ma_muc_tu,

                    "PinyinCedict":
                        pinyin_cedict,

                    "NghiaAnhCedict":
                        definitions,

                    "TrangThaiDoiChieu":
                        status,

                    "NghiaTiengViet":
                        "",

                    "DaDuyet":
                        0,
                }
            )

    return stats


# =========================================================
# ĐẾM THEO CẤP
# =========================================================
def count_by_level(
    items,
):
    counts = defaultdict(int)

    for item in items:
        counts[
            item["level"]
        ] += 1

    return counts


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 72)
        print(
            "CHUAN BI TU VUNG HSK 1-4 "
            "VA DOI CHIEU CC-CEDICT"
        )
        print("=" * 72)

        # -------------------------------------------------
        # 1. TẢI FILE
        # -------------------------------------------------
        download_hsk_file()

        # -------------------------------------------------
        # 2. ĐỌC DANH SÁCH HSK
        # -------------------------------------------------
        print()
        print(
            "Dang doc danh sach HSK..."
        )

        hsk_items = (
            read_hsk_vocabulary()
        )

        if not hsk_items:
            raise RuntimeError(
                "Khong doc duoc tu vung "
                "HSK 1-4."
            )

        counts = count_by_level(
            hsk_items
        )

        print()
        print("SO LUONG THEO CAP:")

        for level in range(1, 5):

            print(
                f"HSK {level}: "
                f"{counts[level]}"
            )

        print(
            f"Tong HSK 1-4: "
            f"{len(hsk_items)}"
        )

        # -------------------------------------------------
        # 3. KẾT NỐI SQL
        # -------------------------------------------------
        conn = get_connection()
        cursor = conn.cursor()

        ma_nguon_cedict = (
            get_cedict_source_id(
                cursor
            )
        )

        ma_nguon_hsk = (
            get_or_create_hsk_source(
                cursor
            )
        )

        print()
        print(
            f"MaNguon CC-CEDICT: "
            f"{ma_nguon_cedict}"
        )

        print(
            f"MaNguon HSK: "
            f"{ma_nguon_hsk}"
        )

        # -------------------------------------------------
        # 4. LẤY TỪ CẦN TRA
        # -------------------------------------------------
        lookup_words = (
            collect_lookup_words(
                hsk_items
            )
        )

        print(
            "So tu/bien the can doi chieu: "
            f"{len(lookup_words)}"
        )

        # -------------------------------------------------
        # 5. ĐỐI CHIẾU CC-CEDICT
        # -------------------------------------------------
        print()
        print(
            "Dang doi chieu voi "
            "125115 muc CC-CEDICT..."
        )

        cedict_matches = (
            load_cedict_matches(
                cursor,
                ma_nguon_cedict,
                lookup_words,
            )
        )

        # -------------------------------------------------
        # 6. TẠO FILE REVIEW
        # -------------------------------------------------
        stats = create_review_file(
            hsk_items,
            cedict_matches,
        )

        # Lưu nguồn HSK
        conn.commit()

        print()
        print("-" * 72)
        print("HOAN TAT DOI CHIEU")
        print("-" * 72)

        print(
            "Khop dung 1 entry CC-CEDICT: "
            f"{stats['khop_1']}"
        )

        print(
            "Co nhieu entry CC-CEDICT: "
            f"{stats['nhieu_ket_qua']}"
        )

        print(
            "Khong tim thay CC-CEDICT: "
            f"{stats['khong_tim_thay']}"
        )

        print()
        print(
            "File ket qua:"
        )

        print(
            HSK_REVIEW_FILE
        )

        print()
        print(
            "CHUA INSERT VAO TuVung."
        )

        print(
            "NghiaTiengViet van de trong "
            "de cho buoc kiem duyet."
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