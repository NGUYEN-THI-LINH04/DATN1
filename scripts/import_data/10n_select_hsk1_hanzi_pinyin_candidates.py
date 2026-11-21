from pathlib import Path
import csv
import re
import sys
import unicodedata
from collections import defaultdict
from contextlib import closing


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# CONFIG
# =========================================================
CC_CEDICT_SOURCE_ID = 2
EXPECTED_HANZI = 98


# =========================================================
# FILES
# =========================================================
REVIEW_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
)

INPUT_FILE = (
    REVIEW_DIR
    / "hsk1_98_hanzi_cccedict_candidate_review.csv"
)

OUTPUT_FILE = (
    REVIEW_DIR
    / "hsk1_98_hanzi_pinyin_selected_review.csv"
)

REVIEW_FILE = (
    REVIEW_DIR
    / "hsk1_98_hanzi_pinyin_manual_review.csv"
)


# =========================================================
# PINYIN CONVERSION
# =========================================================
TONE_MAP = {
    "ā": ("a", "1"),
    "á": ("a", "2"),
    "ǎ": ("a", "3"),
    "à": ("a", "4"),

    "ē": ("e", "1"),
    "é": ("e", "2"),
    "ě": ("e", "3"),
    "è": ("e", "4"),

    "ī": ("i", "1"),
    "í": ("i", "2"),
    "ǐ": ("i", "3"),
    "ì": ("i", "4"),

    "ō": ("o", "1"),
    "ó": ("o", "2"),
    "ǒ": ("o", "3"),
    "ò": ("o", "4"),

    "ū": ("u", "1"),
    "ú": ("u", "2"),
    "ǔ": ("u", "3"),
    "ù": ("u", "4"),

    "ǖ": ("v", "1"),
    "ǘ": ("v", "2"),
    "ǚ": ("v", "3"),
    "ǜ": ("v", "4"),

    "ü": ("v", "5"),
}


def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def fail(message):

    raise RuntimeError(message)


def load_csv(path):

    if not path.exists():

        fail(
            "Khong tim thay file:\n"
            f"{path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:

            fail(
                "Khong doc duoc header CSV."
            )

        return (
            reader.fieldnames,
            list(reader),
        )


def write_csv(
    path,
    fieldnames,
    rows,
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


def tone_mark_to_numbered(pinyin):

    """
    Chuyen:
        shí -> shi2
        yǔ -> yu3
        me -> me5
        nü -> nv5

    Chi dung cho 1 am tiet.
    """

    pinyin = clean(
        pinyin
    ).lower()

    if not pinyin:

        return ""

    # Already numbered
    if re.search(
        r"[1-5]$",
        pinyin,
    ):

        return (
            pinyin
            .replace("ü", "v")
            .replace("u:", "v")
        )

    tone = "5"

    chars = []

    for char in pinyin:

        if char in TONE_MAP:

            base, found_tone = (
                TONE_MAP[char]
            )

            chars.append(base)

            if found_tone != "5":

                tone = found_tone

        else:

            chars.append(char)

    result = "".join(
        chars
    )

    result = (
        result
        .replace("ü", "v")
        .replace("u:", "v")
    )

    # Remove stray punctuation/spaces
    result = re.sub(
        r"[^a-zv]",
        "",
        result,
    )

    if not result:

        return ""

    return (
        result + tone
    )


def normalize_cccedict_pinyin(pinyin):

    value = clean(
        pinyin
    ).lower()

    value = (
        value
        .replace("ü", "v")
        .replace("u:", "v")
    )

    value = re.sub(
        r"\s+",
        "",
        value,
    )

    # CC-CEDICT capitalization for surnames
    # was already lowered above.
    return value


def split_make_me_a_hanzi_readings(value):

    readings = []

    for item in clean(
        value
    ).split("|"):

        item = clean(item)

        if item:

            readings.append(
                item
            )

    return readings


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10N - CHON UNG VIEN PINYIN "
        "CHO 98 CHU HAN HSK1"
    )
    print("=" * 120)

    print()
    print("NGUYEN TAC:")
    print("  Make Me a Hanzi = cach doc ung vien")
    print("  CC-CEDICT = nguon doi chieu")
    print("  CHI AUTO_MATCH KHI TIM THAY CACH DOC KHOP")
    print("  KHONG AUTO DICH NGHIA VIET")
    print("  KHONG UPDATE DATABASE")

    # =====================================================
    # 1. READ INPUT
    # =====================================================
    print()
    print("[1] DOC FILE 10M")
    print("-" * 120)

    fields, rows = load_csv(
        INPUT_FILE
    )

    required = {
        "KyTu",
        "PhamVi",
        "BaiXuatHienDau",
        "TieuDeBai",
        "TuVungDauTien",
        "PinyinMakeMeAHanzi",
        "DefinitionMakeMeAHanzi",
        "SoMucCCCEDICT",
        "SoCachDocCCCEDICT",
        "DanhSachPinyinCCCEDICT",
        "MucDoPhucTap",
    }

    missing = (
        required
        - set(fields)
    )

    if missing:

        fail(
            "File 10M thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    if len(rows) != EXPECTED_HANZI:

        fail(
            "File 10M khong co dung "
            "98 dong."
        )

    chars = [
        clean(row["KyTu"])
        for row in rows
    ]

    if len(set(chars)) != 98:

        fail(
            "KyTu khong duy nhat."
        )

    context_map = {
        clean(row["KyTu"]): row
        for row in rows
    }

    print(
        "Tong Chu Han:",
        len(rows),
    )

    # =====================================================
    # 2. LOAD RAW CC-CEDICT ENTRIES
    # =====================================================
    print()
    print(
        "[2] DOC CHI TIET CC-CEDICT"
    )
    print("-" * 120)

    with closing(
        get_connection()
    ) as connection:

        try:

            with closing(
                connection.cursor()
            ) as cursor:

                cursor.execute(
                    "SELECT DB_NAME();"
                )

                db_name = clean(
                    cursor.fetchone()[0]
                )

                if (
                    db_name.lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi "
                        "nham database."
                    )

                placeholders = ",".join(
                    "?"
                    for _ in chars
                )

                sql = f"""
                    SELECT
                        MaMucTu,
                        ChuHan,
                        PhienAm,
                        NghiaGoc,
                        MaNguonBenNgoai
                    FROM dbo.MucTuDien
                    WHERE
                        MaNguon = ?
                        AND LEN(ChuHan) = 1
                        AND ChuHan IN (
                            {placeholders}
                        )
                    ORDER BY
                        ChuHan,
                        MaMucTu;
                """

                params = (
                    [CC_CEDICT_SOURCE_ID]
                    + chars
                )

                cursor.execute(
                    sql,
                    *params,
                )

                raw_rows = (
                    cursor.fetchall()
                )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    entries_by_char = defaultdict(
        list
    )

    for row in raw_rows:

        char = clean(row[1])

        entries_by_char[
            char
        ].append(
            {
                "MaMucTu": int(row[0]),

                "PinyinRaw": clean(
                    row[2]
                ),

                "PinyinNormalized": (
                    normalize_cccedict_pinyin(
                        row[2]
                    )
                ),

                "NghiaGoc": clean(
                    row[3]
                ),

                "MaNguonBenNgoai": clean(
                    row[4]
                ),
            }
        )

    print(
        "Tong muc CC-CEDICT:",
        len(raw_rows),
    )

    # =====================================================
    # 3. MATCH
    # =====================================================
    print()
    print(
        "[3] DOI CHIEU PINYIN"
    )
    print("-" * 120)

    output_rows = []
    manual_rows = []

    auto_match = 0
    manual_review = 0

    one_matching_reading = 0
    multiple_matching_readings = 0

    for char in chars:

        context = (
            context_map[char]
        )

        mmah_raw = clean(
            context[
                "PinyinMakeMeAHanzi"
            ]
        )

        mmah_readings = (
            split_make_me_a_hanzi_readings(
                mmah_raw
            )
        )

        mmah_numbered = []

        for reading in mmah_readings:

            numeric = (
                tone_mark_to_numbered(
                    reading
                )
            )

            if (
                numeric
                and numeric
                not in mmah_numbered
            ):

                mmah_numbered.append(
                    numeric
                )

        entries = (
            entries_by_char[
                char
            ]
        )

        cc_readings = sorted(
            {
                item[
                    "PinyinNormalized"
                ]
                for item in entries
                if item[
                    "PinyinNormalized"
                ]
            }
        )

        matching_readings = [
            reading
            for reading
            in mmah_numbered
            if reading
            in cc_readings
        ]

        matching_entries = [
            item
            for item in entries
            if item[
                "PinyinNormalized"
            ]
            in matching_readings
        ]

        # -----------------------------------------
        # Decide status
        # -----------------------------------------
        if (
            len(matching_readings)
            == 1
        ):

            status = (
                "AUTO_MATCH"
            )

            chosen_numeric = (
                matching_readings[0]
            )

            auto_match += 1
            one_matching_reading += 1

        elif (
            len(matching_readings)
            > 1
        ):

            status = (
                "NHIEU_CACH_DOC_DEU_KHOP"
            )

            chosen_numeric = ""

            manual_review += 1
            multiple_matching_readings += 1

        else:

            status = (
                "KHONG_KHOP_CCCEDICT"
            )

            chosen_numeric = ""

            manual_review += 1

        matching_ids = (
            " | ".join(
                str(
                    item["MaMucTu"]
                )
                for item
                in matching_entries
            )
        )

        matching_meanings = (
            " || ".join(
                (
                    f"[{item['PinyinRaw']}] "
                    f"{item['NghiaGoc']}"
                )
                for item
                in matching_entries
            )
        )

        output = {
            "KyTu": char,

            "PhamVi": clean(
                context["PhamVi"]
            ),

            "BaiXuatHienDau": clean(
                context[
                    "BaiXuatHienDau"
                ]
            ),

            "TieuDeBai": clean(
                context[
                    "TieuDeBai"
                ]
            ),

            "TuVungDauTien": clean(
                context[
                    "TuVungDauTien"
                ]
            ),

            "PinyinMakeMeAHanzi": (
                mmah_raw
            ),

            "PinyinMakeMeAHanziSo": (
                " | ".join(
                    mmah_numbered
                )
            ),

            "PinyinCCCEDICTTatCa": (
                " | ".join(
                    cc_readings
                )
            ),

            "PinyinCCCEDICTKhop": (
                " | ".join(
                    matching_readings
                )
            ),

            "SoMucCCCEDICTKhop": (
                len(
                    matching_entries
                )
            ),

            "MaMucTuKhop": (
                matching_ids
            ),

            "NghiaAnhDungCachDoc": (
                matching_meanings
            ),

            "TrangThaiMatchPinyin": (
                status
            ),

            # Tone-mark Pinyin cua MMAH duoc
            # giu de review, chua commit.
            "PinyinDeXuat": (
                mmah_raw
                if status
                == "AUTO_MATCH"
                else ""
            ),

            "NghiaTiengVietDeXuat": "",

            "NguonNghia": (
                "CC-CEDICT_MaNguon_2"
            ),

            "DaKiemDuyetPinyin": 0,

            "DaKiemDuyetNghiaViet": 0,

            "GhiChu": "",
        }

        output_rows.append(
            output
        )

        if status != "AUTO_MATCH":

            manual_rows.append(
                output.copy()
            )

    # =====================================================
    # 4. PRINT MANUAL CASES
    # =====================================================
    print()
    print(
        "[4] CAC CHU CHUA AUTO MATCH"
    )
    print("-" * 120)

    print(
        "So luong:",
        len(manual_rows),
    )

    for row in manual_rows:

        print()
        print(
            "KyTu:",
            row["KyTu"],
        )

        print(
            "  Tu dau tien:",
            row[
                "TuVungDauTien"
            ],
        )

        print(
            "  MakeMeAHanzi:",
            row[
                "PinyinMakeMeAHanzi"
            ],
        )

        print(
            "  MakeMeAHanzi so:",
            row[
                "PinyinMakeMeAHanziSo"
            ],
        )

        print(
            "  CC-CEDICT:",
            row[
                "PinyinCCCEDICTTatCa"
            ],
        )

        print(
            "  Trang thai:",
            row[
                "TrangThaiMatchPinyin"
            ],
        )

    # =====================================================
    # 5. WRITE
    # =====================================================
    print()
    print(
        "[5] GHI FILE REVIEW"
    )
    print("-" * 120)

    fieldnames = [
        "KyTu",
        "PhamVi",
        "BaiXuatHienDau",
        "TieuDeBai",
        "TuVungDauTien",
        "PinyinMakeMeAHanzi",
        "PinyinMakeMeAHanziSo",
        "PinyinCCCEDICTTatCa",
        "PinyinCCCEDICTKhop",
        "SoMucCCCEDICTKhop",
        "MaMucTuKhop",
        "NghiaAnhDungCachDoc",
        "TrangThaiMatchPinyin",
        "PinyinDeXuat",
        "NghiaTiengVietDeXuat",
        "NguonNghia",
        "DaKiemDuyetPinyin",
        "DaKiemDuyetNghiaViet",
        "GhiChu",
    ]

    write_csv(
        OUTPUT_FILE,
        fieldnames,
        output_rows,
    )

    write_csv(
        REVIEW_FILE,
        fieldnames,
        manual_rows,
    )

    print(
        "All:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "Manual only:"
    )

    print(
        REVIEW_FILE
    )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 10N"
    )
    print("=" * 120)

    print(
        "Tong Chu Han:",
        len(output_rows),
    )

    print(
        "AUTO_MATCH Pinyin:",
        auto_match,
    )

    print(
        "Can review thu cong:",
        manual_review,
    )

    print(
        "Nhieu cach doc MMAH "
        "cung khop CC-CEDICT:",
        multiple_matching_readings,
    )

    print()
    print(
        "AUTO_MATCH KHONG CO NGHIA "
        "LA DA KIEM DUYET."
    )

    print(
        "DaKiemDuyetPinyin=1:",
        0,
    )

    print(
        "DaKiemDuyetNghiaViet=1:",
        0,
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA DICH NGHIA VIET."
    )

    print(
        "CHUA SUA 识."
    )

    print(
        "CHUA INSERT ChuHan."
    )

    print(
        "CHUA INSERT NetChuHan."
    )

    print()
    print("=" * 120)
    print("HOAN TAT")
    print("=" * 120)


# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 120)
        print(
            "10N THAT BAI"
        )
        print("=" * 120)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)