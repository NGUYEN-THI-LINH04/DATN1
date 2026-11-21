from pathlib import Path
import csv
import sys
import re
from collections import defaultdict, Counter
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

EXPECTED_MISSING = 98


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
    / "hsk1_98_hanzi_dictionary_source_summary.csv"
)

OUTPUT_FILE = (
    REVIEW_DIR
    / "hsk1_98_hanzi_cccedict_candidate_review.csv"
)

AMBIGUOUS_FILE = (
    REVIEW_DIR
    / "hsk1_98_hanzi_cccedict_ambiguous.csv"
)


# =========================================================
# HELPERS
# =========================================================
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


def normalize_numeric_pinyin(value):

    value = clean(value)

    if not value:
        return ""

    # chi normalize de so sanh:
    # - lower case
    # - bo khoang trang thua
    # KHONG chuyen sang dau thanh o buoc nay.
    value = value.lower()

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10M - AUDIT CHI TIET CC-CEDICT "
        "CHO 98 CHU HAN CON THIEU NGHIA VIET"
    )
    print("=" * 120)

    print()
    print("MUC TIEU:")
    print("  DOI CHIEU CHINH XAC 98 CHU")
    print("  DEM SO MUC CC-CEDICT TUNG CHU")
    print("  DEM SO CACH DOC TUNG CHU")
    print("  LIET KE NGHIA ANH DE REVIEW")
    print("  PHAT HIEN CAC CHU MO HO / DA AM")
    print()
    print("CHE DO:")
    print("  CHI SELECT DATABASE")
    print("  KHONG CHON NGHIA VIET")
    print("  KHONG CHON PINYIN CUOI")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")

    # =====================================================
    # 1. READ 10L
    # =====================================================
    print()
    print("[1] DOC FILE 10L")
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
        "DefinitionEnglishMakeMeAHanzi",
        "SoMucCCCEDICT",
        "PinyinCCCEDICT",
        "NghiaAnhCCCEDICT",
    }

    missing = (
        required
        - set(fields)
    )

    if missing:

        fail(
            "File 10L thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    if len(rows) != EXPECTED_MISSING:

        fail(
            "File 10L khong co "
            "dung 98 dong."
        )

    chars = [
        clean(row["KyTu"])
        for row in rows
    ]

    if len(set(chars)) != 98:

        fail(
            "98 dong nhung KyTu "
            "khong duy nhat."
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
    # 2. QUERY CC-CEDICT
    # =====================================================
    print()
    print(
        "[2] DOC CAC MUC CC-CEDICT"
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
                        NgonNguNghiaGoc,
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

                dictionary_rows = (
                    cursor.fetchall()
                )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    print(
        "Tong muc CC-CEDICT:",
        len(dictionary_rows),
    )

    # =====================================================
    # 3. GROUP BY CHARACTER
    # =====================================================
    entries_by_char = defaultdict(
        list
    )

    for row in dictionary_rows:

        entries_by_char[
            clean(row[1])
        ].append(
            {
                "MaMucTu": int(row[0]),
                "ChuHan": clean(row[1]),
                "PhienAm": clean(row[2]),
                "NghiaGoc": clean(row[3]),
                "NgonNgu": clean(row[4]),
                "MaNguonBenNgoai": clean(
                    row[5]
                ),
            }
        )

    missing_chars = [
        char
        for char in chars
        if char not in entries_by_char
    ]

    if missing_chars:

        print(
            "Khong co CC-CEDICT:",
            " ".join(missing_chars),
        )

        fail(
            "10L bao 98/98 co CC-CEDICT "
            "nhung 10M bi thieu."
        )

    # =====================================================
    # 4. ANALYZE
    # =====================================================
    print()
    print(
        "[3] PHAN TICH MUC TU / CACH DOC"
    )
    print("-" * 120)

    output_rows = []
    ambiguous_rows = []

    one_entry = 0
    multi_entry = 0

    one_reading = 0
    multi_reading = 0

    max_entries = 0

    entry_histogram = Counter()

    for char in chars:

        context = (
            context_map[char]
        )

        entries = (
            entries_by_char[char]
        )

        max_entries = max(
            max_entries,
            len(entries),
        )

        entry_histogram[
            len(entries)
        ] += 1

        if len(entries) == 1:

            one_entry += 1

        else:

            multi_entry += 1

        reading_groups = defaultdict(
            list
        )

        for item in entries:

            reading_key = (
                normalize_numeric_pinyin(
                    item["PhienAm"]
                )
            )

            reading_groups[
                reading_key
            ].append(
                item
            )

        reading_count = len(
            reading_groups
        )

        if reading_count == 1:

            one_reading += 1

        else:

            multi_reading += 1

        pinyins = []

        meanings = []

        ids = []

        for item in entries:

            ids.append(
                str(
                    item["MaMucTu"]
                )
            )

            if (
                item["PhienAm"]
                not in pinyins
            ):

                pinyins.append(
                    item["PhienAm"]
                )

            meanings.append(
                (
                    f"[{item['PhienAm']}] "
                    f"{item['NghiaGoc']}"
                )
            )

        if (
            len(entries) == 1
            and reading_count == 1
        ):

            complexity = (
                "DON_GIAN"
            )

        elif reading_count == 1:

            complexity = (
                "NHIEU_NGHIA_CUNG_CACH_DOC"
            )

        else:

            complexity = (
                "NHIEU_CACH_DOC"
            )

        output_row = {
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
                context["TieuDeBai"]
            ),

            "TuVungDauTien": clean(
                context[
                    "TuVungDauTien"
                ]
            ),

            "PinyinMakeMeAHanzi": clean(
                context[
                    "PinyinMakeMeAHanzi"
                ]
            ),

            "DefinitionMakeMeAHanzi": clean(
                context[
                    "DefinitionEnglishMakeMeAHanzi"
                ]
            ),

            "SoMucCCCEDICT": (
                len(entries)
            ),

            "SoCachDocCCCEDICT": (
                reading_count
            ),

            "DanhSachPinyinCCCEDICT": (
                " | ".join(
                    pinyins
                )
            ),

            "DanhSachMaMucTu": (
                " | ".join(
                    ids
                )
            ),

            "NghiaAnhTheoCachDoc": (
                " || ".join(
                    meanings
                )
            ),

            "MucDoPhucTap": (
                complexity
            ),

            # Chua chot.
            "PinyinChon": "",

            "NghiaTiengVietDeXuat": "",

            "NguonNghia": (
                "CC-CEDICT"
            ),

            "DaKiemDuyet": 0,

            "GhiChu": "",
        }

        output_rows.append(
            output_row
        )

        if (
            complexity
            != "DON_GIAN"
        ):

            ambiguous_rows.append(
                output_row.copy()
            )

    # =====================================================
    # 5. PRINT AMBIGUOUS
    # =====================================================
    print()
    print(
        "[4] CAC CHU CAN REVIEW KY"
    )
    print("-" * 120)

    print(
        "So chu phuc tap:",
        len(ambiguous_rows),
    )

    for row in ambiguous_rows:

        print()
        print(
            "KyTu:",
            row["KyTu"],
        )

        print(
            "  Bai:",
            row[
                "BaiXuatHienDau"
            ],
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
            "  So muc:",
            row[
                "SoMucCCCEDICT"
            ],
        )

        print(
            "  So cach doc:",
            row[
                "SoCachDocCCCEDICT"
            ],
        )

        print(
            "  Pinyin:",
            row[
                "DanhSachPinyinCCCEDICT"
            ],
        )

    # =====================================================
    # 6. WRITE
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
        "DefinitionMakeMeAHanzi",
        "SoMucCCCEDICT",
        "SoCachDocCCCEDICT",
        "DanhSachPinyinCCCEDICT",
        "DanhSachMaMucTu",
        "NghiaAnhTheoCachDoc",
        "MucDoPhucTap",
        "PinyinChon",
        "NghiaTiengVietDeXuat",
        "NguonNghia",
        "DaKiemDuyet",
        "GhiChu",
    ]

    write_csv(
        OUTPUT_FILE,
        fieldnames,
        output_rows,
    )

    write_csv(
        AMBIGUOUS_FILE,
        fieldnames,
        ambiguous_rows,
    )

    print(
        "98-char review:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "Ambiguous only:"
    )

    print(
        AMBIGUOUS_FILE
    )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 10M"
    )
    print("=" * 120)

    print(
        "Tong Chu Han:",
        len(output_rows),
    )

    print(
        "Chu co 1 muc CC-CEDICT:",
        one_entry,
    )

    print(
        "Chu co >1 muc CC-CEDICT:",
        multi_entry,
    )

    print()
    print(
        "Chu co 1 cach doc:",
        one_reading,
    )

    print(
        "Chu co >1 cach doc:",
        multi_reading,
    )

    print()
    print(
        "Chu don gian "
        "(1 muc + 1 cach doc):",
        sum(
            1
            for row in output_rows
            if row[
                "MucDoPhucTap"
            ] == "DON_GIAN"
        ),
    )

    print(
        "Chu nhieu nghia "
        "nhung cung cach doc:",
        sum(
            1
            for row in output_rows
            if row[
                "MucDoPhucTap"
            ]
            ==
            "NHIEU_NGHIA_CUNG_CACH_DOC"
        ),
    )

    print(
        "Chu co nhieu cach doc:",
        sum(
            1
            for row in output_rows
            if row[
                "MucDoPhucTap"
            ]
            ==
            "NHIEU_CACH_DOC"
        ),
    )

    print()
    print(
        "So muc CC-CEDICT lon nhat "
        "tren mot chu:",
        max_entries,
    )

    print()
    print(
        "PHAN BO SO MUC:"
    )

    for count in sorted(
        entry_histogram
    ):

        print(
            f"  {count} muc: "
            f"{entry_histogram[count]} chu"
        )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA CHON PINYIN CUOI."
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
            "10M THAT BAI"
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