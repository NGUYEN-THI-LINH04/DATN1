from pathlib import Path
import csv
import io
import json
import sys
import zipfile
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
COURSE_CODE = "HSK1-CORE"

STANDARD_SOURCE_ID = 1002
MAKEMEAHANZI_SOURCE_ID = 3

EXPECTED_STANDARD_VOCAB = 500
EXPECTED_RUNTIME_VOCAB = 501

EXPECTED_STANDARD_HANZI = 300
EXPECTED_RUNTIME_HANZI = 301

EXPECTED_CURRENT_HANZI = 17

SUPPLEMENT_WORD = "越南"
EXPECTED_EXTRA_CHAR = "越"


# =========================================================
# PATH
# =========================================================
DATA_ROOT = (
    ROOT_DIR
    / "data_sources"
)

OUTPUT_DIR = (
    DATA_ROOT
    / "hsk"
    / "hanzi"
    / "review"
)

COVERAGE_FILE = (
    OUTPUT_DIR
    / "hsk1_301_makemeahanzi_coverage_review.csv"
)

ISSUES_FILE = (
    OUTPUT_DIR
    / "hsk1_301_makemeahanzi_issues.csv"
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


def is_hanzi(char):

    if not char:
        return False

    code = ord(char)

    return (
        0x3400 <= code <= 0x4DBF
        or 0x4E00 <= code <= 0x9FFF
        or 0xF900 <= code <= 0xFAFF
        or 0x20000 <= code <= 0x2A6DF
        or 0x2A700 <= code <= 0x2B73F
        or 0x2B740 <= code <= 0x2B81F
        or 0x2B820 <= code <= 0x2CEAF
        or 0x30000 <= code <= 0x3134F
    )


def extract_chars(word):

    return {
        char
        for char in clean(word)
        if is_hanzi(char)
    }


def normalize_value(value):

    if value is None:
        return ""

    if isinstance(
        value,
        (list, tuple),
    ):

        return " | ".join(
            clean(item)
            for item in value
            if clean(item)
        )

    if isinstance(
        value,
        dict,
    ):

        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
        )

    return clean(value)


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


# =========================================================
# FIND SOURCE
# =========================================================
def find_extracted_pair():

    dictionary_files = list(
        DATA_ROOT.rglob(
            "dictionary.txt"
        )
    )

    graphics_files = list(
        DATA_ROOT.rglob(
            "graphics.txt"
        )
    )

    pairs = []

    for dictionary_path in dictionary_files:

        for graphics_path in graphics_files:

            if (
                dictionary_path.parent
                == graphics_path.parent
            ):

                pairs.append(
                    (
                        dictionary_path,
                        graphics_path,
                    )
                )

    if len(pairs) == 1:

        return {
            "type": "folder",
            "dictionary": pairs[0][0],
            "graphics": pairs[0][1],
        }

    if len(pairs) > 1:

        print()
        print(
            "Tim thay nhieu cap "
            "dictionary.txt + graphics.txt:"
        )

        for pair in pairs:

            print(
                "  ",
                pair[0].parent,
            )

        fail(
            "Co nhieu bo Make Me a Hanzi. "
            "Can xac dinh bo nao se dung."
        )

    return None


def find_zip_pair():

    found = []

    for zip_path in DATA_ROOT.rglob(
        "*.zip"
    ):

        try:

            with zipfile.ZipFile(
                zip_path,
                "r",
            ) as zip_file:

                names = (
                    zip_file.namelist()
                )

                dictionaries = [
                    name
                    for name in names
                    if (
                        Path(name).name
                        == "dictionary.txt"
                    )
                ]

                graphics = [
                    name
                    for name in names
                    if (
                        Path(name).name
                        == "graphics.txt"
                    )
                ]

                for dictionary_name in dictionaries:

                    for graphics_name in graphics:

                        if (
                            Path(dictionary_name).parent
                            ==
                            Path(graphics_name).parent
                        ):

                            found.append(
                                {
                                    "type": "zip",
                                    "zip": zip_path,
                                    "dictionary": (
                                        dictionary_name
                                    ),
                                    "graphics": (
                                        graphics_name
                                    ),
                                }
                            )

        except zipfile.BadZipFile:

            continue

    if len(found) == 1:

        return found[0]

    if len(found) > 1:

        print()
        print(
            "Tim thay nhieu ZIP "
            "co Make Me a Hanzi:"
        )

        for item in found:

            print(
                "  ",
                item["zip"],
            )

        fail(
            "Co nhieu bo Make Me a Hanzi "
            "trong ZIP."
        )

    return None


def find_source():

    extracted = (
        find_extracted_pair()
    )

    if extracted:

        return extracted

    zipped = (
        find_zip_pair()
    )

    if zipped:

        return zipped

    fail(
        "Khong tim thay dictionary.txt "
        "va graphics.txt cua Make Me a Hanzi "
        f"trong:\n{DATA_ROOT}"
    )


# =========================================================
# JSONL LOAD
# =========================================================
def parse_jsonl_stream(stream):

    result = {}

    duplicates = []

    invalid_lines = []

    for line_number, line in enumerate(
        stream,
        start=1,
    ):

        line = line.strip()

        if not line:
            continue

        try:

            obj = json.loads(
                line
            )

        except Exception as error:

            invalid_lines.append(
                (
                    line_number,
                    str(error),
                )
            )

            continue

        character = clean(
            obj.get(
                "character"
            )
        )

        if not character:

            invalid_lines.append(
                (
                    line_number,
                    "Thieu field character",
                )
            )

            continue

        if character in result:

            duplicates.append(
                character
            )

        result[
            character
        ] = obj

    return (
        result,
        duplicates,
        invalid_lines,
    )


def load_sources(source):

    if (
        source["type"]
        == "folder"
    ):

        with open(
            source["dictionary"],
            "r",
            encoding="utf-8",
        ) as file:

            (
                dictionary_data,
                dictionary_duplicates,
                dictionary_invalid,
            ) = parse_jsonl_stream(
                file
            )

        with open(
            source["graphics"],
            "r",
            encoding="utf-8",
        ) as file:

            (
                graphics_data,
                graphics_duplicates,
                graphics_invalid,
            ) = parse_jsonl_stream(
                file
            )

        return (
            dictionary_data,
            graphics_data,
            dictionary_duplicates,
            graphics_duplicates,
            dictionary_invalid,
            graphics_invalid,
        )

    with zipfile.ZipFile(
        source["zip"],
        "r",
    ) as zip_file:

        with io.TextIOWrapper(
            zip_file.open(
                source[
                    "dictionary"
                ]
            ),
            encoding="utf-8",
        ) as file:

            (
                dictionary_data,
                dictionary_duplicates,
                dictionary_invalid,
            ) = parse_jsonl_stream(
                file
            )

        with io.TextIOWrapper(
            zip_file.open(
                source[
                    "graphics"
                ]
            ),
            encoding="utf-8",
        ) as file:

            (
                graphics_data,
                graphics_duplicates,
                graphics_invalid,
            ) = parse_jsonl_stream(
                file
            )

    return (
        dictionary_data,
        graphics_data,
        dictionary_duplicates,
        graphics_duplicates,
        dictionary_invalid,
        graphics_invalid,
    )


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10F - AUDIT MAKE ME A HANZI "
        "CHO 301 CHU HAN HSK1"
    )
    print("=" * 120)

    print()
    print("CHE DO:")
    print("  DOC DATABASE")
    print("  DOC dictionary.txt")
    print("  DOC graphics.txt")
    print("  KIEM TRA COVERAGE 301 CHU")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    # =====================================================
    # 1. FIND SOURCE
    # =====================================================
    print()
    print(
        "[1] TIM NGUON MAKE ME A HANZI"
    )
    print("-" * 120)

    source = (
        find_source()
    )

    print(
        "Loai nguon:",
        source["type"],
    )

    if (
        source["type"]
        == "folder"
    ):

        print(
            "dictionary:",
            source[
                "dictionary"
            ],
        )

        print(
            "graphics:",
            source[
                "graphics"
            ],
        )

    else:

        print(
            "ZIP:",
            source[
                "zip"
            ],
        )

        print(
            "dictionary:",
            source[
                "dictionary"
            ],
        )

        print(
            "graphics:",
            source[
                "graphics"
            ],
        )

    # =====================================================
    # 2. LOAD SOURCE
    # =====================================================
    print()
    print(
        "[2] DOC MAKE ME A HANZI"
    )
    print("-" * 120)

    (
        dictionary_data,
        graphics_data,
        dictionary_duplicates,
        graphics_duplicates,
        dictionary_invalid,
        graphics_invalid,
    ) = load_sources(
        source
    )

    print(
        "dictionary entries:",
        len(dictionary_data),
    )

    print(
        "graphics entries:",
        len(graphics_data),
    )

    print(
        "dictionary duplicate character:",
        len(
            dictionary_duplicates
        ),
    )

    print(
        "graphics duplicate character:",
        len(
            graphics_duplicates
        ),
    )

    print(
        "dictionary invalid lines:",
        len(
            dictionary_invalid
        ),
    )

    print(
        "graphics invalid lines:",
        len(
            graphics_invalid
        ),
    )

    # =====================================================
    # 3. DATABASE
    # =====================================================
    print()
    print(
        "[3] DOI CHIEU DATABASE"
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
                    """
                    SELECT
                        DB_NAME(),
                        CONVERT(
                            nvarchar(128),
                            SERVERPROPERTY('ServerName')
                        );
                    """
                )

                (
                    database_name,
                    server_name,
                ) = cursor.fetchone()

                print(
                    "Server:",
                    clean(
                        server_name
                    ),
                )

                print(
                    "Database:",
                    clean(
                        database_name
                    ),
                )

                if (
                    clean(
                        database_name
                    ).lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi "
                        "nham database."
                    )

                # -----------------------------------------
                # Source 3
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        MaNguon,
                        Ten,
                        LienKetNguon,
                        GiayPhep,
                        GhiChu
                    FROM dbo.NguonDuLieu
                    WHERE MaNguon = ?;
                    """,
                    MAKEMEAHANZI_SOURCE_ID,
                )

                source_row = (
                    cursor.fetchone()
                )

                if not source_row:

                    fail(
                        "Khong co MaNguon=3 "
                        "trong NguonDuLieu."
                    )

                print()
                print(
                    "MaNguon:",
                    source_row[0],
                )

                print(
                    "Ten:",
                    clean(
                        source_row[1]
                    ),
                )

                if (
                    "make me a hanzi"
                    not in clean(
                        source_row[1]
                    ).lower()
                ):

                    fail(
                        "MaNguon=3 "
                        "khong phai Make Me a Hanzi."
                    )

                # -----------------------------------------
                # Vocab
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        bh.SoThuTuBai,
                        tvbh.ThuTu,
                        tv.MaTuVung,
                        tv.ChuHan,
                        tv.MaNguon

                    FROM dbo.TuVungBaiHoc AS tvbh

                    INNER JOIN dbo.BaiHoc AS bh
                        ON tvbh.MaBaiHoc
                        = bh.MaBaiHoc

                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc

                    INNER JOIN dbo.TuVung AS tv
                        ON tvbh.MaTuVung
                        = tv.MaTuVung

                    WHERE
                        kh.MaKyHieu = ?

                    ORDER BY
                        bh.SoThuTuBai,
                        tvbh.ThuTu;
                    """,
                    COURSE_CODE,
                )

                vocab_rows = (
                    cursor.fetchall()
                )

                if (
                    len(vocab_rows)
                    != EXPECTED_RUNTIME_VOCAB
                ):

                    fail(
                        "Runtime vocab "
                        "khong bang 501."
                    )

                standard_rows = [
                    row
                    for row in vocab_rows
                    if int(
                        row[4]
                    )
                    == STANDARD_SOURCE_ID
                ]

                supplement_rows = [
                    row
                    for row in vocab_rows
                    if int(
                        row[4]
                    )
                    != STANDARD_SOURCE_ID
                ]

                if (
                    len(standard_rows)
                    != EXPECTED_STANDARD_VOCAB
                ):

                    fail(
                        "Standard vocab "
                        "khong bang 500."
                    )

                if (
                    len(supplement_rows)
                    != 1
                ):

                    fail(
                        "Khong con dung "
                        "1 tu bo sung."
                    )

                if clean(
                    supplement_rows[
                        0
                    ][
                        3
                    ]
                ) != SUPPLEMENT_WORD:

                    fail(
                        "Tu bo sung "
                        "khong phai 越南."
                    )

                standard_chars = set()

                runtime_chars = set()

                first_lesson = {}

                first_order = {}

                for row in vocab_rows:

                    lesson_no = int(
                        row[0]
                    )

                    vocab_order = int(
                        row[1]
                    )

                    word = clean(
                        row[3]
                    )

                    chars_in_word = (
                        extract_chars(
                            word
                        )
                    )

                    runtime_chars.update(
                        chars_in_word
                    )

                    if (
                        int(row[4])
                        == STANDARD_SOURCE_ID
                    ):

                        standard_chars.update(
                            chars_in_word
                        )

                    for char in chars_in_word:

                        key = (
                            lesson_no,
                            vocab_order,
                        )

                        if (
                            char
                            not in first_lesson
                            or key
                            <
                            (
                                first_lesson[
                                    char
                                ],
                                first_order[
                                    char
                                ],
                            )
                        ):

                            first_lesson[
                                char
                            ] = lesson_no

                            first_order[
                                char
                            ] = vocab_order

                if (
                    len(
                        standard_chars
                    )
                    != EXPECTED_STANDARD_HANZI
                ):

                    fail(
                        "Standard Hanzi "
                        "khong bang 300."
                    )

                if (
                    len(
                        runtime_chars
                    )
                    != EXPECTED_RUNTIME_HANZI
                ):

                    fail(
                        "Runtime Hanzi "
                        "khong bang 301."
                    )

                extra_chars = (
                    runtime_chars
                    - standard_chars
                )

                if (
                    extra_chars
                    != {
                        EXPECTED_EXTRA_CHAR
                    }
                ):

                    fail(
                        "Chu bo sung "
                        "khong con la 越."
                    )

                # -----------------------------------------
                # Current Hanzi
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        ch.MaChuHan,
                        ch.KyTu,
                        ch.SoNet,
                        bh.SoThuTuBai

                    FROM dbo.ChuHan AS ch

                    INNER JOIN dbo.BaiHoc AS bh
                        ON ch.MaBaiHoc
                        = bh.MaBaiHoc

                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc

                    WHERE
                        kh.MaKyHieu = ?;
                    """,
                    COURSE_CODE,
                )

                current_rows = (
                    cursor.fetchall()
                )

                if (
                    len(current_rows)
                    != EXPECTED_CURRENT_HANZI
                ):

                    fail(
                        "ChuHan hien tai "
                        "khong bang 17."
                    )

                current_map = {
                    clean(
                        row[1]
                    ): {
                        "MaChuHan": (
                            int(
                                row[0]
                            )
                        ),

                        "SoNet": (
                            row[2]
                        ),

                        "Bai": (
                            int(
                                row[3]
                            )
                        ),
                    }

                    for row
                    in current_rows
                }

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    print(
        "Standard Hanzi:",
        len(
            standard_chars
        ),
    )

    print(
        "Runtime Hanzi:",
        len(
            runtime_chars
        ),
    )

    print(
        "Chu bo sung:",
        EXPECTED_EXTRA_CHAR,
    )

    # =====================================================
    # 4. COVERAGE
    # =====================================================
    print()
    print(
        "[4] KIEM TRA COVERAGE 301 CHU"
    )
    print("-" * 120)

    coverage_rows = []

    issues = []

    dictionary_covered = 0

    graphics_covered = 0

    both_covered = 0

    stroke_mismatch_current = 0

    ordered_chars = sorted(
        runtime_chars,
        key=lambda char: (
            first_lesson.get(
                char,
                999,
            ),
            first_order.get(
                char,
                999,
            ),
            char,
        ),
    )

    for char in ordered_chars:

        dictionary_entry = (
            dictionary_data.get(
                char
            )
        )

        graphics_entry = (
            graphics_data.get(
                char
            )
        )

        has_dictionary = (
            dictionary_entry
            is not None
        )

        has_graphics = (
            graphics_entry
            is not None
        )

        if has_dictionary:

            dictionary_covered += 1

        if has_graphics:

            graphics_covered += 1

        if (
            has_dictionary
            and has_graphics
        ):

            both_covered += 1

        pinyin = ""

        definition = ""

        decomposition = ""

        radical = ""

        if dictionary_entry:

            pinyin = normalize_value(
                dictionary_entry.get(
                    "pinyin"
                )
            )

            definition = normalize_value(
                dictionary_entry.get(
                    "definition"
                )
            )

            decomposition = normalize_value(
                dictionary_entry.get(
                    "decomposition"
                )
            )

            radical = normalize_value(
                dictionary_entry.get(
                    "radical"
                )
            )

        strokes = []

        medians = []

        if graphics_entry:

            strokes = (
                graphics_entry.get(
                    "strokes"
                )
                or []
            )

            medians = (
                graphics_entry.get(
                    "medians"
                )
                or []
            )

        stroke_count_graphics = (
            len(strokes)
        )

        median_count = (
            len(medians)
        )

        current = (
            current_map.get(
                char
            )
        )

        sql_stroke_count = ""

        stroke_check = ""

        if current:

            sql_stroke_count = (
                current[
                    "SoNet"
                ]
            )

            if (
                sql_stroke_count
                is None
            ):

                stroke_check = (
                    "SQL_SONET_NULL"
                )

            elif not has_graphics:

                stroke_check = (
                    "THIEU_GRAPHICS"
                )

            elif (
                int(
                    sql_stroke_count
                )
                ==
                stroke_count_graphics
            ):

                stroke_check = (
                    "OK"
                )

            else:

                stroke_check = (
                    "LECH_SO_NET"
                )

                stroke_mismatch_current += 1

        scope = (
            "HSK1_CHUAN_300"
            if char
            in standard_chars
            else "BO_SUNG_VIET_NAM"
        )

        if not has_dictionary:

            issues.append(
                {
                    "KyTu": char,
                    "PhamVi": scope,
                    "VanDe": (
                        "THIEU_DICTIONARY"
                    ),
                    "ChiTiet": "",
                }
            )

        if not has_graphics:

            issues.append(
                {
                    "KyTu": char,
                    "PhamVi": scope,
                    "VanDe": (
                        "THIEU_GRAPHICS"
                    ),
                    "ChiTiet": "",
                }
            )

        if (
            current
            and stroke_check
            == "LECH_SO_NET"
        ):

            issues.append(
                {
                    "KyTu": char,
                    "PhamVi": scope,
                    "VanDe": (
                        "LECH_SO_NET_HIEN_CO"
                    ),
                    "ChiTiet": (
                        f"SQL={sql_stroke_count}; "
                        f"Graphics={stroke_count_graphics}"
                    ),
                }
            )

        coverage_rows.append(
            {
                "KyTu": char,

                "PhamVi": scope,

                "BaiXuatHienDau": (
                    first_lesson.get(
                        char,
                        "",
                    )
                ),

                "CoDictionary": (
                    1
                    if has_dictionary
                    else 0
                ),

                "CoGraphics": (
                    1
                    if has_graphics
                    else 0
                ),

                "PinyinMakeMeAHanzi": (
                    pinyin
                ),

                "DefinitionEnglish": (
                    definition
                ),

                "RadicalField": (
                    radical
                ),

                "Decomposition": (
                    decomposition
                ),

                "SoNetGraphics": (
                    stroke_count_graphics
                    if has_graphics
                    else ""
                ),

                "SoMedian": (
                    median_count
                    if has_graphics
                    else ""
                ),

                "DaCoTrongChuHan": (
                    1
                    if current
                    else 0
                ),

                "MaChuHanHienTai": (
                    current[
                        "MaChuHan"
                    ]
                    if current
                    else ""
                ),

                "SoNetSQLHienTai": (
                    sql_stroke_count
                ),

                "KiemTraSoNetHienTai": (
                    stroke_check
                ),

                "DaKiemDuyetNguon": 0,

                "GhiChuKiemDuyet": "",
            }
        )

    # =====================================================
    # 5. WRITE
    # =====================================================
    print()
    print(
        "[5] TAO FILE REVIEW"
    )
    print("-" * 120)

    write_csv(
        COVERAGE_FILE,
        [
            "KyTu",
            "PhamVi",
            "BaiXuatHienDau",
            "CoDictionary",
            "CoGraphics",
            "PinyinMakeMeAHanzi",
            "DefinitionEnglish",
            "RadicalField",
            "Decomposition",
            "SoNetGraphics",
            "SoMedian",
            "DaCoTrongChuHan",
            "MaChuHanHienTai",
            "SoNetSQLHienTai",
            "KiemTraSoNetHienTai",
            "DaKiemDuyetNguon",
            "GhiChuKiemDuyet",
        ],
        coverage_rows,
    )

    write_csv(
        ISSUES_FILE,
        [
            "KyTu",
            "PhamVi",
            "VanDe",
            "ChiTiet",
        ],
        issues,
    )

    print(
        "Coverage:"
    )

    print(
        COVERAGE_FILE
    )

    print()
    print(
        "Issues:"
    )

    print(
        ISSUES_FILE
    )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 10F"
    )
    print("=" * 120)

    print(
        "Chu HSK1 chuan:",
        len(
            standard_chars
        ),
    )

    print(
        "Chu bo sung:",
        len(
            runtime_chars
            - standard_chars
        ),
    )

    print(
        "Tong runtime:",
        len(
            runtime_chars
        ),
    )

    print()
    print(
        "dictionary coverage:",
        dictionary_covered,
        "/301",
    )

    print(
        "graphics coverage:",
        graphics_covered,
        "/301",
    )

    print(
        "Co ca dictionary + graphics:",
        both_covered,
        "/301",
    )

    print()
    print(
        "Thieu dictionary:",
        (
            EXPECTED_RUNTIME_HANZI
            -
            dictionary_covered
        ),
    )

    print(
        "Thieu graphics:",
        (
            EXPECTED_RUNTIME_HANZI
            -
            graphics_covered
        ),
    )

    print(
        "17 chu hien co lech SoNet "
        "voi graphics:",
        stroke_mismatch_current,
    )

    print(
        "Tong issue:",
        len(
            issues
        ),
    )

    print()
    print(
        "DaKiemDuyetNguon=1:",
        0,
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA INSERT ChuHan."
    )

    print(
        "CHUA INSERT NetChuHan."
    )

    print()
    print(
        "BUOC TIEP THEO:"
    )

    print(
        "NEU COVERAGE DAT, "
        "MOI BAT DAU CHUAN HOA "
        "PINYIN + BO THU + SO NET "
        "+ DU LIEU NET VIET."
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
            "10F THAT BAI"
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