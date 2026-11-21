from pathlib import Path
import csv
import io
import json
import sys
import zipfile
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
COURSE_CODE = "HSK1-CORE"

STANDARD_SOURCE_ID = 1002
MAKEMEAHANZI_SOURCE_ID = 3

EXPECTED_STANDARD_VOCAB = 500
EXPECTED_RUNTIME_VOCAB = 501

EXPECTED_STANDARD_HANZI = 300
EXPECTED_RUNTIME_HANZI = 301

EXPECTED_RADICALS = 214
EXPECTED_CURRENT_HANZI = 17

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

REVIEW_FILE = (
    OUTPUT_DIR
    / "hsk1_301_hanzi_structure_review.csv"
)

ISSUES_FILE = (
    OUTPUT_DIR
    / "hsk1_301_hanzi_structure_issues.csv"
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


def extract_chars(text):

    return [
        char
        for char in clean(text)
        if is_hanzi(char)
    ]


def normalize_value(value):

    if value is None:
        return ""

    if isinstance(value, list):

        return " | ".join(
            clean(item)
            for item in value
            if clean(item)
        )

    if isinstance(value, dict):

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
# FIND MAKE ME A HANZI
# =========================================================
def find_source():

    # -----------------------------------------------------
    # Truong hop da giai nen
    # -----------------------------------------------------
    dictionary_files = list(
        DATA_ROOT.rglob("dictionary.txt")
    )

    graphics_files = list(
        DATA_ROOT.rglob("graphics.txt")
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

        fail(
            "Tim thay nhieu bo "
            "Make Me a Hanzi da giai nen."
        )

    # -----------------------------------------------------
    # Truong hop nam trong ZIP
    # -----------------------------------------------------
    zip_matches = []

    for zip_path in DATA_ROOT.rglob(
        "*.zip"
    ):

        try:

            with zipfile.ZipFile(
                zip_path,
                "r",
            ) as zip_file:

                names = zip_file.namelist()

                dictionaries = [
                    name
                    for name in names
                    if Path(name).name
                    == "dictionary.txt"
                ]

                graphics = [
                    name
                    for name in names
                    if Path(name).name
                    == "graphics.txt"
                ]

                for dictionary_name in dictionaries:

                    for graphics_name in graphics:

                        if (
                            Path(
                                dictionary_name
                            ).parent
                            ==
                            Path(
                                graphics_name
                            ).parent
                        ):

                            zip_matches.append(
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

    if len(zip_matches) == 1:

        return zip_matches[0]

    if len(zip_matches) > 1:

        fail(
            "Tim thay nhieu ZIP "
            "Make Me a Hanzi."
        )

    fail(
        "Khong tim thay dictionary.txt "
        "va graphics.txt."
    )


# =========================================================
# LOAD JSONL
# =========================================================
def parse_jsonl(stream):

    result = {}

    for line_number, line in enumerate(
        stream,
        start=1,
    ):

        line = line.strip()

        if not line:
            continue

        try:

            obj = json.loads(line)

        except Exception as error:

            fail(
                f"JSON loi dong "
                f"{line_number}: {error}"
            )

        character = clean(
            obj.get("character")
        )

        if not character:

            fail(
                f"Dong {line_number} "
                "khong co character."
            )

        if character in result:

            fail(
                "Trung character "
                f"trong nguon: {character}"
            )

        result[character] = obj

    return result


def load_source(source):

    if source["type"] == "folder":

        with open(
            source["dictionary"],
            "r",
            encoding="utf-8",
        ) as file:

            dictionary_data = (
                parse_jsonl(file)
            )

        with open(
            source["graphics"],
            "r",
            encoding="utf-8",
        ) as file:

            graphics_data = (
                parse_jsonl(file)
            )

        return (
            dictionary_data,
            graphics_data,
        )

    with zipfile.ZipFile(
        source["zip"],
        "r",
    ) as zip_file:

        with io.TextIOWrapper(
            zip_file.open(
                source["dictionary"]
            ),
            encoding="utf-8",
        ) as file:

            dictionary_data = (
                parse_jsonl(file)
            )

        with io.TextIOWrapper(
            zip_file.open(
                source["graphics"]
            ),
            encoding="utf-8",
        ) as file:

            graphics_data = (
                parse_jsonl(file)
            )

    return (
        dictionary_data,
        graphics_data,
    )


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10G - CHUAN HOA CAU TRUC "
        "301 CHU HAN HSK1"
    )
    print("=" * 120)

    print()
    print("MUC TIEU:")
    print("  DOI CHIEU PINYIN NGUON")
    print("  DOI CHIEU BO THU")
    print("  MAP VOI 214 BoThu TRONG SQL")
    print("  KIEM TRA SO NET")
    print("  KIEM TRA MEDIAN")
    print("  KIEM TRA 17 CHU HIEN CO")
    print()
    print("CHE DO:")
    print("  CHI SELECT DATABASE")
    print("  CHI TAO FILE REVIEW")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")

    # =====================================================
    # 1. SOURCE
    # =====================================================
    print()
    print(
        "[1] DOC MAKE ME A HANZI"
    )
    print("-" * 120)

    source = find_source()

    (
        dictionary_data,
        graphics_data,
    ) = load_source(source)

    print(
        "dictionary:",
        len(dictionary_data),
    )

    print(
        "graphics:",
        len(graphics_data),
    )

    # =====================================================
    # 2. DATABASE
    # =====================================================
    print()
    print(
        "[2] DOC DATABASE"
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

                db_name, server_name = (
                    cursor.fetchone()
                )

                print(
                    "Server:",
                    clean(server_name),
                )

                print(
                    "Database:",
                    clean(db_name),
                )

                if (
                    clean(db_name).lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi "
                        "nham database."
                    )

                # =========================================
                # BoThu
                # =========================================
                cursor.execute(
                    """
                    SELECT
                        MaBoThu,
                        KyHieu,
                        TenBoThu,
                        YNghia,
                        SoNet,
                        MaNguon,
                        TrangThai
                    FROM dbo.BoThu
                    ORDER BY MaBoThu;
                    """
                )

                radical_rows = (
                    cursor.fetchall()
                )

                if (
                    len(radical_rows)
                    != EXPECTED_RADICALS
                ):

                    fail(
                        "BoThu khong bang 214."
                    )

                radical_map = defaultdict(
                    list
                )

                for row in radical_rows:

                    radical_map[
                        clean(row[1])
                    ].append(
                        {
                            "MaBoThu": int(
                                row[0]
                            ),
                            "KyHieu": clean(
                                row[1]
                            ),
                            "TenBoThu": clean(
                                row[2]
                            ),
                            "YNghia": clean(
                                row[3]
                            ),
                            "SoNet": row[4],
                            "MaNguon": row[5],
                            "TrangThai": clean(
                                row[6]
                            ),
                        }
                    )

                print(
                    "BoThu:",
                    len(radical_rows),
                )

                print(
                    "KyHieu BoThu duy nhat:",
                    len(radical_map),
                )

                # =========================================
                # 501 vocab
                # =========================================
                cursor.execute(
                    """
                    SELECT
                        bh.SoThuTuBai,
                        bh.MaBaiHoc,
                        bh.TieuDe,
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
                        tvbh.ThuTu,
                        tv.MaTuVung;
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
                    if int(row[6])
                    == STANDARD_SOURCE_ID
                ]

                if (
                    len(standard_rows)
                    != EXPECTED_STANDARD_VOCAB
                ):

                    fail(
                        "Standard vocab "
                        "khong bang 500."
                    )

                # =========================================
                # Build character sets
                # =========================================
                standard_chars = set()
                runtime_chars = set()

                first_context = {}

                for row in vocab_rows:

                    lesson_no = int(row[0])
                    lesson_id = int(row[1])
                    lesson_title = clean(
                        row[2]
                    )
                    vocab_order = int(
                        row[3]
                    )
                    vocab_id = int(row[4])
                    word = clean(row[5])
                    source_id = int(row[6])

                    for position, char in enumerate(
                        extract_chars(word),
                        start=1,
                    ):

                        runtime_chars.add(
                            char
                        )

                        if (
                            source_id
                            == STANDARD_SOURCE_ID
                        ):

                            standard_chars.add(
                                char
                            )

                        key = (
                            lesson_no,
                            vocab_order,
                            position,
                            vocab_id,
                        )

                        if (
                            char not in first_context
                            or key
                            < first_context[
                                char
                            ]["_key"]
                        ):

                            first_context[
                                char
                            ] = {
                                "_key": key,
                                "Bai": lesson_no,
                                "MaBaiHoc": (
                                    lesson_id
                                ),
                                "TieuDe": (
                                    lesson_title
                                ),
                                "TuVung": word,
                            }

                if (
                    len(standard_chars)
                    != EXPECTED_STANDARD_HANZI
                ):

                    fail(
                        "Standard Hanzi "
                        "khong bang 300."
                    )

                if (
                    len(runtime_chars)
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
                    != {EXPECTED_EXTRA_CHAR}
                ):

                    fail(
                        "Chu bo sung "
                        "khong con la 越."
                    )

                # =========================================
                # Existing ChuHan
                # =========================================
                cursor.execute(
                    """
                    SELECT
                        ch.MaChuHan,
                        ch.KyTu,
                        ch.Pinyin,
                        ch.NghiaTiengViet,
                        ch.MaBoThu,
                        ch.SoNet,
                        ch.MaNguon,
                        ch.TrangThai,
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
                    clean(row[1]): {
                        "MaChuHan": (
                            int(row[0])
                        ),
                        "Pinyin": clean(
                            row[2]
                        ),
                        "Nghia": clean(
                            row[3]
                        ),
                        "MaBoThu": row[4],
                        "SoNet": row[5],
                        "MaNguon": row[6],
                        "TrangThai": clean(
                            row[7]
                        ),
                        "Bai": int(row[8]),
                    }

                    for row in current_rows
                }

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    print(
        "Standard Hanzi:",
        len(standard_chars),
    )

    print(
        "Runtime Hanzi:",
        len(runtime_chars),
    )

    print(
        "ChuHan hien co:",
        len(current_map),
    )

    # =====================================================
    # 3. STRUCTURE AUDIT
    # =====================================================
    print()
    print(
        "[3] CHUAN HOA CAU TRUC 301 CHU"
    )
    print("-" * 120)

    review_rows = []
    issues = []

    pinyin_present = 0
    radical_present = 0
    radical_matched = 0
    graphics_present = 0
    median_matched = 0
    ready_count = 0

    existing_radical_mismatch = 0
    existing_stroke_mismatch = 0

    ordered_chars = sorted(
        runtime_chars,
        key=lambda char: (
            first_context[
                char
            ]["_key"]
        ),
    )

    for char in ordered_chars:

        dictionary_entry = (
            dictionary_data.get(char)
        )

        graphics_entry = (
            graphics_data.get(char)
        )

        if not dictionary_entry:

            fail(
                f"10F da bao coverage "
                f"nhung 10G thieu dictionary: "
                f"{char}"
            )

        if not graphics_entry:

            fail(
                f"10F da bao coverage "
                f"nhung 10G thieu graphics: "
                f"{char}"
            )

        # -----------------------------------------
        # Pinyin raw
        # -----------------------------------------
        pinyin_raw = normalize_value(
            dictionary_entry.get(
                "pinyin"
            )
        )

        if pinyin_raw:

            pinyin_present += 1

        else:

            issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": (
                        "THIEU_PINYIN_NGUON"
                    ),
                    "ChiTiet": "",
                }
            )

        # -----------------------------------------
        # Radical raw
        # -----------------------------------------
        radical_raw = normalize_value(
            dictionary_entry.get(
                "radical"
            )
        )

        if radical_raw:

            radical_present += 1

        else:

            issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": (
                        "THIEU_RADICAL_NGUON"
                    ),
                    "ChiTiet": "",
                }
            )

        # -----------------------------------------
        # Radical -> dbo.BoThu
        # -----------------------------------------
        matches = (
            radical_map.get(
                radical_raw,
                [],
            )
            if radical_raw
            else []
        )

        ma_bo_thu = ""
        bo_thu_name = ""
        bo_thu_meaning = ""
        radical_status = ""

        if len(matches) == 1:

            radical_matched += 1

            ma_bo_thu = (
                matches[0][
                    "MaBoThu"
                ]
            )

            bo_thu_name = (
                matches[0][
                    "TenBoThu"
                ]
            )

            bo_thu_meaning = (
                matches[0][
                    "YNghia"
                ]
            )

            radical_status = (
                "OK"
            )

        elif len(matches) == 0:

            radical_status = (
                "KHONG_KHOP_BOTHU"
            )

            issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": (
                        "RADICAL_KHONG_KHOP_BOTHU"
                    ),
                    "ChiTiet": (
                        radical_raw
                    ),
                }
            )

        else:

            radical_status = (
                "TRUNG_KYHIEU_BOTHU"
            )

            issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": (
                        "RADICAL_TRUNG_KYHIEU_BOTHU"
                    ),
                    "ChiTiet": (
                        radical_raw
                    ),
                }
            )

        # -----------------------------------------
        # Graphics
        # -----------------------------------------
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

        stroke_count = len(
            strokes
        )

        median_count = len(
            medians
        )

        if stroke_count > 0:

            graphics_present += 1

        else:

            issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": (
                        "KHONG_CO_NET"
                    ),
                    "ChiTiet": "",
                }
            )

        if (
            stroke_count > 0
            and stroke_count
            == median_count
        ):

            median_matched += 1

            median_status = "OK"

        else:

            median_status = (
                "LECH_STROKE_MEDIAN"
            )

            issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": (
                        "LECH_STROKE_MEDIAN"
                    ),
                    "ChiTiet": (
                        f"strokes={stroke_count}; "
                        f"medians={median_count}"
                    ),
                }
            )

        # -----------------------------------------
        # Decomposition
        # -----------------------------------------
        decomposition = normalize_value(
            dictionary_entry.get(
                "decomposition"
            )
        )

        definition = normalize_value(
            dictionary_entry.get(
                "definition"
            )
        )

        # -----------------------------------------
        # Existing
        # -----------------------------------------
        current = (
            current_map.get(
                char
            )
        )

        existing_radical_status = ""
        existing_stroke_status = ""

        if current:

            if (
                ma_bo_thu
                and current[
                    "MaBoThu"
                ] == ma_bo_thu
            ):

                existing_radical_status = (
                    "OK"
                )

            elif ma_bo_thu:

                existing_radical_status = (
                    "LECH"
                )

                existing_radical_mismatch += 1

                issues.append(
                    {
                        "KyTu": char,
                        "LoaiLoi": (
                            "LECH_BOTHU_HIEN_CO"
                        ),
                        "ChiTiet": (
                            f"SQL="
                            f"{current['MaBoThu']}; "
                            f"Nguon={ma_bo_thu}"
                        ),
                    }
                )

            if (
                current[
                    "SoNet"
                ] is not None
                and int(
                    current[
                        "SoNet"
                    ]
                )
                == stroke_count
            ):

                existing_stroke_status = (
                    "OK"
                )

            else:

                existing_stroke_status = (
                    "LECH"
                )

                existing_stroke_mismatch += 1

                issues.append(
                    {
                        "KyTu": char,
                        "LoaiLoi": (
                            "LECH_SONET_HIEN_CO"
                        ),
                        "ChiTiet": (
                            f"SQL="
                            f"{current['SoNet']}; "
                            f"Nguon={stroke_count}"
                        ),
                    }
                )

        # -----------------------------------------
        # Ready structural data
        # -----------------------------------------
        ready = (
            bool(pinyin_raw)
            and len(matches) == 1
            and stroke_count > 0
            and stroke_count
            == median_count
        )

        if ready:

            ready_count += 1

        context = (
            first_context[
                char
            ]
        )

        review_rows.append(
            {
                "KyTu": char,

                "PhamVi": (
                    "HSK1_CHUAN_300"
                    if char
                    in standard_chars
                    else "BO_SUNG_VIET_NAM"
                ),

                "BaiXuatHienDau": (
                    context["Bai"]
                ),

                "MaBaiHoc": (
                    context[
                        "MaBaiHoc"
                    ]
                ),

                "TieuDeBai": (
                    context[
                        "TieuDe"
                    ]
                ),

                "TuVungDauTien": (
                    context[
                        "TuVung"
                    ]
                ),

                "PinyinNguonRaw": (
                    pinyin_raw
                ),

                "DefinitionEnglishNguon": (
                    definition
                ),

                "RadicalNguon": (
                    radical_raw
                ),

                "MaBoThuDeXuat": (
                    ma_bo_thu
                ),

                "TenBoThuSQL": (
                    bo_thu_name
                ),

                "YNghiaBoThuSQL": (
                    bo_thu_meaning
                ),

                "KiemTraBoThu": (
                    radical_status
                ),

                "DecompositionNguon": (
                    decomposition
                ),

                "SoNetNguon": (
                    stroke_count
                ),

                "SoMedianNguon": (
                    median_count
                ),

                "KiemTraStrokeMedian": (
                    median_status
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

                "PinyinSQLHienTai": (
                    current[
                        "Pinyin"
                    ]
                    if current
                    else ""
                ),

                "MaBoThuSQLHienTai": (
                    current[
                        "MaBoThu"
                    ]
                    if current
                    else ""
                ),

                "SoNetSQLHienTai": (
                    current[
                        "SoNet"
                    ]
                    if current
                    else ""
                ),

                "KiemTraBoThuHienTai": (
                    existing_radical_status
                ),

                "KiemTraSoNetHienTai": (
                    existing_stroke_status
                ),

                "SanSangCauTruc": (
                    1
                    if ready
                    else 0
                ),

                "DaKiemDuyetCauTruc": 0,

                "GhiChuKiemDuyet": "",
            }
        )

    # =====================================================
    # 4. WRITE
    # =====================================================
    print()
    print(
        "[4] TAO FILE REVIEW"
    )
    print("-" * 120)

    write_csv(
        REVIEW_FILE,
        [
            "KyTu",
            "PhamVi",
            "BaiXuatHienDau",
            "MaBaiHoc",
            "TieuDeBai",
            "TuVungDauTien",
            "PinyinNguonRaw",
            "DefinitionEnglishNguon",
            "RadicalNguon",
            "MaBoThuDeXuat",
            "TenBoThuSQL",
            "YNghiaBoThuSQL",
            "KiemTraBoThu",
            "DecompositionNguon",
            "SoNetNguon",
            "SoMedianNguon",
            "KiemTraStrokeMedian",
            "DaCoTrongChuHan",
            "MaChuHanHienTai",
            "PinyinSQLHienTai",
            "MaBoThuSQLHienTai",
            "SoNetSQLHienTai",
            "KiemTraBoThuHienTai",
            "KiemTraSoNetHienTai",
            "SanSangCauTruc",
            "DaKiemDuyetCauTruc",
            "GhiChuKiemDuyet",
        ],
        review_rows,
    )

    write_csv(
        ISSUES_FILE,
        [
            "KyTu",
            "LoaiLoi",
            "ChiTiet",
        ],
        issues,
    )

    print(
        "Structure review:"
    )

    print(
        REVIEW_FILE
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
        "KET QUA 10G"
    )
    print("=" * 120)

    print(
        "Tong Chu Han:",
        len(review_rows),
    )

    print(
        "Co Pinyin nguon:",
        pinyin_present,
        "/301",
    )

    print(
        "Co Radical nguon:",
        radical_present,
        "/301",
    )

    print(
        "Radical map dung vao BoThu:",
        radical_matched,
        "/301",
    )

    print(
        "Co net viet:",
        graphics_present,
        "/301",
    )

    print(
        "Stroke = Median:",
        median_matched,
        "/301",
    )

    print(
        "San sang cau truc:",
        ready_count,
        "/301",
    )

    print()
    print(
        "17 chu hien co lech BoThu:",
        existing_radical_mismatch,
    )

    print(
        "17 chu hien co lech SoNet:",
        existing_stroke_mismatch,
    )

    print(
        "Tong issue:",
        len(issues),
    )

    print()
    print(
        "DaKiemDuyetCauTruc=1:",
        0,
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA INSERT 284 CHU."
    )

    print(
        "CHUA INSERT NetChuHan."
    )

    print()
    print(
        "BUOC TIEP THEO:"
    )

    print(
        "XU LY CAC RADICAL KHONG MAP "
        "DUOC (NEU CO), SAU DO "
        "CHUAN HOA PINYIN VA NOI DUNG "
        "TIENG VIET CUA TUNG CHU."
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
            "10G THAT BAI"
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