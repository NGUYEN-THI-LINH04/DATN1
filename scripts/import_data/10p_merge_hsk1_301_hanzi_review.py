from pathlib import Path
import csv
import sys
import unicodedata
from collections import defaultdict, Counter
from contextlib import closing


# =========================================================
# OPENPYXL
# =========================================================
try:
    from openpyxl import load_workbook
except ImportError:
    print()
    print("=" * 120)
    print("THIEU THU VIEN openpyxl")
    print("=" * 120)
    print()
    print("Chay lenh:")
    print()
    print('python -m pip install openpyxl')
    print()
    print("Sau do chay lai 10P.")
    sys.exit(1)


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

EXPECTED_TOTAL = 301
EXPECTED_STANDARD = 300
EXPECTED_SUPPLEMENT = 1

EXPECTED_FROM_TUVUNG = 203
EXPECTED_TUVUNG_ROWS = 206

EXPECTED_FROM_10O = 98

EXPECTED_CURRENT = 17

STRUCTURE_SOURCE_ID = 3

STATUS_DRAFT = "ban_nhap"


# =========================================================
# PATHS
# =========================================================
REVIEW_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
)

STRUCTURE_FILE = (
    REVIEW_DIR
    / "hsk1_301_hanzi_radical_mapped_review.csv"
)

REVIEW_10O_FILE = (
    REVIEW_DIR
    / "hsk1_98_hanzi_10o_nghia_viet_review.xlsx"
)

OUTPUT_FILE = (
    REVIEW_DIR
    / "hsk1_301_hanzi_merged_review.csv"
)

ISSUES_FILE = (
    REVIEW_DIR
    / "hsk1_301_hanzi_merged_issues.csv"
)

LESSON_SUMMARY_FILE = (
    REVIEW_DIR
    / "hsk1_301_hanzi_lesson_summary.csv"
)

PINYIN_REVIEW_FILE = (
    REVIEW_DIR
    / "hsk1_203_hanzi_pinyin_review.csv"
)


# =========================================================
# HELPERS
# =========================================================
def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def normalize_text(value):

    return unicodedata.normalize(
        "NFC",
        clean(value)
    ).lower()


def to_int(value, default=None):

    value = clean(value)

    if not value:
        return default

    return int(value)


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
                f"Khong doc duoc header:\n{path}"
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


# =========================================================
# READ EXCEL 10O
# =========================================================
def load_10o_excel(path):

    if not path.exists():

        fail(
            "Khong tim thay file 10O:\n"
            f"{path}"
        )

    workbook = load_workbook(
        path,
        data_only=True,
    )

    if "Review_98" not in workbook.sheetnames:

        fail(
            "File 10O khong co sheet Review_98."
        )

    sheet = workbook["Review_98"]

    headers = [
        clean(cell.value)
        for cell in sheet[1]
    ]

    required = {
        "KyTu",
        "BaiXuatHienDau",
        "TieuDeBai",
        "TuVungDauTien",

        "PinyinDeXuat",
        "PinyinTheoNguCanhDeXuat",
        "CanReviewPinyinNguCanh",

        "NghiaTiengVietDeXuat",

        "NguonNghia",

        "DaKiemDuyetPinyin",
        "DaKiemDuyetNghiaViet",

        "GhiChu",
    }

    missing = (
        required
        - set(headers)
    )

    if missing:

        fail(
            "Excel 10O thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    index = {
        name: position
        for position, name
        in enumerate(headers)
    }

    rows = []

    for excel_row in sheet.iter_rows(
        min_row=2,
        values_only=True,
    ):

        if not any(
            value is not None
            for value in excel_row
        ):
            continue

        record = {
            header: (
                excel_row[
                    index[header]
                ]
                if index[header]
                < len(excel_row)
                else None
            )
            for header in headers
        }

        rows.append(
            record
        )

    return rows


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10P - GHEP 301 CHU HAN HSK1 "
        "THANH BAN REVIEW TONG"
    )
    print("=" * 120)

    print()
    print("MUC TIEU:")
    print("  203 CHU -> TuVung DA DUYET")
    print("   98 CHU -> FILE 10O DA KIEM DUYET")
    print("  CAU TRUC -> FILE 10I")
    print("  TONG -> 301 CHU")
    print()
    print("CHE DO:")
    print("  CHI SELECT DATABASE")
    print("  CHI DOC FILE REVIEW")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    # =====================================================
    # 1. READ STRUCTURE 10I
    # =====================================================
    print()
    print("[1] DOC CAU TRUC 301 CHU TU 10I")
    print("-" * 120)

    structure_fields, structure_rows = load_csv(
        STRUCTURE_FILE
    )

    required_structure = {
        "KyTu",
        "PhamVi",
        "BaiXuatHienDau",
        "MaBaiHoc",
        "TieuDeBai",
        "TuVungDauTien",

        "PinyinNguonRaw",

        "RadicalChuan",
        "MaBoThuChuan",
        "SoBoThuChuan",
        "TenBoThuChuan",

        "SoNetNguon",
        "SoMedianNguon",

        "KiemTraMappingBoThu",
        "KiemTraStrokeMedian",

        "DaCoTrongChuHan",
        "MaChuHanHienTai",
    }

    missing_structure = (
        required_structure
        - set(structure_fields)
    )

    if missing_structure:

        fail(
            "File 10I thieu cot: "
            + ", ".join(
                sorted(missing_structure)
            )
        )

    if len(structure_rows) != EXPECTED_TOTAL:

        fail(
            "File 10I khong co dung "
            "301 dong."
        )

    structure_map = {}

    structure_order = {}

    for position, row in enumerate(
        structure_rows,
        start=1,
    ):

        char = clean(
            row["KyTu"]
        )

        if char in structure_map:

            fail(
                f"Trung KyTu trong 10I: {char}"
            )

        if clean(
            row[
                "KiemTraMappingBoThu"
            ]
        ) != "OK":

            fail(
                f"{char}: mapping BoThu "
                "chua OK."
            )

        if clean(
            row[
                "KiemTraStrokeMedian"
            ]
        ) != "OK":

            fail(
                f"{char}: Stroke/Median "
                "chua OK."
            )

        structure_map[
            char
        ] = row

        structure_order[
            char
        ] = position

    standard_chars = {
        char
        for char, row
        in structure_map.items()
        if clean(
            row["PhamVi"]
        ) == "HSK1_CHUAN_300"
    }

    supplement_chars = (
        set(structure_map)
        - standard_chars
    )

    if (
        len(standard_chars)
        != EXPECTED_STANDARD
    ):

        fail(
            "Bo HSK1 chuan "
            "khong bang 300."
        )

    if (
        len(supplement_chars)
        != EXPECTED_SUPPLEMENT
    ):

        fail(
            "Bo chu bo sung "
            "khong bang 1."
        )

    if supplement_chars != {"越"}:

        fail(
            "Chu bo sung khong phai 越."
        )

    print(
        "Tong structure:",
        len(structure_rows),
    )

    print(
        "HSK1 chuan:",
        len(standard_chars),
    )

    print(
        "Bo sung:",
        " ".join(
            sorted(supplement_chars)
        ),
    )

    # =====================================================
    # 2. READ 10O
    # =====================================================
    print()
    print(
        "[2] DOC 98 CHU DA DUYET TU 10O"
    )
    print("-" * 120)

    review_10o_rows = load_10o_excel(
        REVIEW_10O_FILE
    )

    if (
        len(review_10o_rows)
        != EXPECTED_FROM_10O
    ):

        fail(
            "Excel 10O khong co "
            "dung 98 dong. "
            f"Thuc te: "
            f"{len(review_10o_rows)}"
        )

    review_10o_map = {}

    pinyin_approved = 0
    meaning_approved = 0

    context_pinyin_rows = []

    for row in review_10o_rows:

        char = clean(
            row["KyTu"]
        )

        if char in review_10o_map:

            fail(
                f"10O trung KyTu: {char}"
            )

        pinyin_flag = clean(
            row[
                "DaKiemDuyetPinyin"
            ]
        )

        meaning_flag = clean(
            row[
                "DaKiemDuyetNghiaViet"
            ]
        )

        if pinyin_flag == "1":

            pinyin_approved += 1

        if meaning_flag == "1":

            meaning_approved += 1

        if (
            pinyin_flag != "1"
            or meaning_flag != "1"
        ):

            fail(
                f"{char}: 10O chua duyet du "
                "Pinyin/NghiaViet."
            )

        pinyin_context = clean(
            row[
                "PinyinTheoNguCanhDeXuat"
            ]
        )

        pinyin_base = clean(
            row[
                "PinyinDeXuat"
            ]
        )

        if not pinyin_context:

            pinyin_context = (
                pinyin_base
            )

        if not pinyin_context:

            fail(
                f"{char}: thieu Pinyin trong 10O."
            )

        meaning = clean(
            row[
                "NghiaTiengVietDeXuat"
            ]
        )

        if not meaning:

            fail(
                f"{char}: thieu nghia Viet "
                "trong 10O."
            )

        if normalize_text(
            pinyin_context
        ) != normalize_text(
            pinyin_base
        ):

            context_pinyin_rows.append(
                {
                    "KyTu": char,
                    "PinyinGoc": (
                        pinyin_base
                    ),
                    "PinyinTheoNguCanh": (
                        pinyin_context
                    ),
                    "TuVungDauTien": clean(
                        row[
                            "TuVungDauTien"
                        ]
                    ),
                    "GhiChu": clean(
                        row["GhiChu"]
                    ),
                }
            )

        review_10o_map[
            char
        ] = {
            "PinyinFinal": (
                pinyin_context
            ),

            "NghiaFinal": (
                meaning
            ),

            "NguonNgonNgu": (
                "10O_CC-CEDICT_"
                "BIEN_SOAN_DO_AN"
            ),

            "GhiChu": clean(
                row["GhiChu"]
            ),
        }

    print(
        "Dong 10O:",
        len(review_10o_map),
    )

    print(
        "Da duyet Pinyin:",
        pinyin_approved,
        "/98",
    )

    print(
        "Da duyet Nghia Viet:",
        meaning_approved,
        "/98",
    )

    print(
        "Pinyin thay doi theo "
        "ngu canh:",
        len(
            context_pinyin_rows
        ),
    )

    for item in context_pinyin_rows:

        print(
            f"  {item['KyTu']}: "
            f"{item['PinyinGoc']} "
            f"-> "
            f"{item['PinyinTheoNguCanh']} "
            f"| {item['TuVungDauTien']}"
        )

    # =====================================================
    # 3. DATABASE
    # =====================================================
    print()
    print(
        "[3] DOC 203 CHU TU TuVung "
        "DA DUYET"
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
                # 23 lessons
                # =========================================
                cursor.execute(
                    """
                    SELECT
                        bh.MaBaiHoc,
                        bh.SoThuTuBai,
                        bh.TieuDe
                    FROM dbo.BaiHoc AS bh
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc
                    WHERE
                        kh.MaKyHieu = ?
                    ORDER BY
                        bh.SoThuTuBai;
                    """,
                    COURSE_CODE,
                )

                lesson_rows = (
                    cursor.fetchall()
                )

                if len(lesson_rows) != 23:

                    fail(
                        "Khong co du 23 bai HSK1."
                    )

                lesson_map = {
                    int(row[0]): {
                        "SoThuTuBai": int(
                            row[1]
                        ),
                        "TieuDe": clean(
                            row[2]
                        ),
                    }
                    for row in lesson_rows
                }

                # =========================================
                # Approved single-char vocabulary
                # =========================================
                cursor.execute(
                    """
                    SELECT
                        tv.MaTuVung,
                        tv.ChuHan,
                        tv.PhienAm,
                        tv.NghiaTiengViet,
                        tv.MaNguon,
                        tv.DaDuyet,

                        bh.MaBaiHoc,
                        bh.SoThuTuBai,
                        tvbh.ThuTu

                    FROM dbo.TuVung AS tv

                    INNER JOIN dbo.TuVungBaiHoc AS tvbh
                        ON tv.MaTuVung
                        = tvbh.MaTuVung

                    INNER JOIN dbo.BaiHoc AS bh
                        ON tvbh.MaBaiHoc
                        = bh.MaBaiHoc

                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc

                    WHERE
                        kh.MaKyHieu = ?
                        AND LEN(tv.ChuHan) = 1
                        AND tv.DaDuyet = 1

                    ORDER BY
                        tv.ChuHan,
                        bh.SoThuTuBai,
                        tvbh.ThuTu,
                        tv.MaTuVung;
                    """,
                    COURSE_CODE,
                )

                vocab_link_rows = (
                    cursor.fetchall()
                )

                # =========================================
                # Current 17 ChuHan
                # =========================================
                cursor.execute(
                    """
                    SELECT
                        ch.MaChuHan,
                        ch.MaBaiHoc,
                        ch.KyTu,
                        ch.Pinyin,
                        ch.NghiaTiengViet,
                        ch.MaBoThu,
                        ch.SoNet,
                        ch.ThuTu,
                        ch.MaNguon,
                        ch.TrangThai

                    FROM dbo.ChuHan AS ch

                    INNER JOIN dbo.BaiHoc AS bh
                        ON ch.MaBaiHoc
                        = bh.MaBaiHoc

                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc

                    WHERE
                        kh.MaKyHieu = ?

                    ORDER BY
                        bh.SoThuTuBai,
                        ch.ThuTu;
                    """,
                    COURSE_CODE,
                )

                current_rows = (
                    cursor.fetchall()
                )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    if len(current_rows) != EXPECTED_CURRENT:

        fail(
            "ChuHan hien tai "
            "khong con 17."
        )

    # =====================================================
    # 4. BUILD UNIQUE SINGLE VOCAB ENTRIES
    # =====================================================
    print()
    print(
        "[4] CHUAN HOA 203 CHU "
        "TU TuVung"
    )
    print("-" * 120)

    vocab_by_id = {}

    for row in vocab_link_rows:

        vocab_id = int(row[0])

        placement_key = (
            int(row[7]),
            int(row[8]),
            vocab_id,
        )

        if vocab_id not in vocab_by_id:

            vocab_by_id[
                vocab_id
            ] = {
                "MaTuVung": (
                    vocab_id
                ),

                "KyTu": clean(
                    row[1]
                ),

                "Pinyin": clean(
                    row[2]
                ),

                "NghiaTiengViet": clean(
                    row[3]
                ),

                "MaNguon": row[4],

                "DaDuyet": int(
                    row[5]
                ),

                "MaBaiHocDauTien": int(
                    row[6]
                ),

                "BaiDauTien": int(
                    row[7]
                ),

                "ThuTuDauTien": int(
                    row[8]
                ),

                "_key": (
                    placement_key
                ),
            }

        else:

            if (
                placement_key
                <
                vocab_by_id[
                    vocab_id
                ][
                    "_key"
                ]
            ):

                vocab_by_id[
                    vocab_id
                ][
                    "MaBaiHocDauTien"
                ] = int(
                    row[6]
                )

                vocab_by_id[
                    vocab_id
                ][
                    "BaiDauTien"
                ] = int(
                    row[7]
                )

                vocab_by_id[
                    vocab_id
                ][
                    "ThuTuDauTien"
                ] = int(
                    row[8]
                )

                vocab_by_id[
                    vocab_id
                ][
                    "_key"
                ] = (
                    placement_key
                )

    candidates_by_char = defaultdict(
        list
    )

    for item in vocab_by_id.values():

        char = (
            item["KyTu"]
        )

        if char in structure_map:

            candidates_by_char[
                char
            ].append(
                item
            )

    if (
        len(vocab_by_id)
        != EXPECTED_TUVUNG_ROWS
    ):

        fail(
            "So TuVung don da duyet "
            "khong con bang 206. "
            f"Thuc te: "
            f"{len(vocab_by_id)}"
        )

    if (
        len(candidates_by_char)
        != EXPECTED_FROM_TUVUNG
    ):

        fail(
            "So Chu Han co TuVung don "
            "khong con bang 203. "
            f"Thuc te: "
            f"{len(candidates_by_char)}"
        )

    print(
        "TuVung don da duyet:",
        len(vocab_by_id),
    )

    print(
        "Chu Han co TuVung don:",
        len(candidates_by_char),
    )

    # =====================================================
    # 5. VERIFY 203 + 98 = 301
    # =====================================================
    chars_from_vocab = set(
        candidates_by_char
    )

    chars_from_10o = set(
        review_10o_map
    )

    overlap = (
        chars_from_vocab
        & chars_from_10o
    )

    if overlap:

        fail(
            "Co chu vua nam trong 203 "
            "vua nam trong 98: "
            + " ".join(
                sorted(overlap)
            )
        )

    combined_chars = (
        chars_from_vocab
        | chars_from_10o
    )

    structure_chars = set(
        structure_map
    )

    if (
        combined_chars
        != structure_chars
    ):

        missing_combined = (
            structure_chars
            - combined_chars
        )

        extra_combined = (
            combined_chars
            - structure_chars
        )

        fail(
            "203 + 98 khong khop "
            "301 structure.\n"
            f"Thieu: "
            f"{' '.join(sorted(missing_combined))}\n"
            f"Thua: "
            f"{' '.join(sorted(extra_combined))}"
        )

    print()
    print(
        "203 + 98 = 301: OK"
    )

    # =====================================================
    # 6. CHOOSE 203 LANGUAGE CANDIDATES
    # =====================================================
    print()
    print(
        "[5] DOI CHIEU PINYIN "
        "CHO 203 CHU TuVung"
    )
    print("-" * 120)

    language_203 = {}

    pinyin_review_rows = []

    multiple_candidate_chars = []

    for char in sorted(
        chars_from_vocab,
        key=lambda c: (
            structure_order[c]
        ),
    ):

        structure = (
            structure_map[
                char
            ]
        )

        source_pinyin = clean(
            structure[
                "PinyinNguonRaw"
            ]
        )

        candidates = sorted(
            candidates_by_char[
                char
            ],
            key=lambda item: (
                item["_key"]
            ),
        )

        if len(candidates) > 1:

            multiple_candidate_chars.append(
                char
            )

        matching = [
            item
            for item in candidates
            if normalize_text(
                item["Pinyin"]
            )
            ==
            normalize_text(
                source_pinyin
            )
        ]

        # -----------------------------------------
        # Prefer exact Pinyin match with structure source
        # -----------------------------------------
        if len(matching) == 1:

            chosen = (
                matching[0]
            )

            pinyin_status = (
                "MATCH_NGUON"
            )

        elif len(matching) > 1:

            chosen = sorted(
                matching,
                key=lambda item: (
                    item["_key"]
                ),
            )[0]

            pinyin_status = (
                "NHIEU_MUC_CUNG_PINYIN"
            )

        else:

            # Chua tu dong ket luan.
            # Lay candidate som nhat de review,
            # nhung danh dau can kiem tra.
            chosen = (
                candidates[0]
            )

            pinyin_status = (
                "CAN_REVIEW_PINYIN"
            )

            pinyin_review_rows.append(
                {
                    "KyTu": char,

                    "BaiXuatHienDau": clean(
                        structure[
                            "BaiXuatHienDau"
                        ]
                    ),

                    "TuVungDauTien": clean(
                        structure[
                            "TuVungDauTien"
                        ]
                    ),

                    "PinyinNguon": (
                        source_pinyin
                    ),

                    "PinyinTuVungChon": (
                        chosen[
                            "Pinyin"
                        ]
                    ),

                    "TatCaPinyinTuVung": (
                        " | ".join(
                            item["Pinyin"]
                            for item
                            in candidates
                        )
                    ),

                    "TatCaMaTuVung": (
                        " | ".join(
                            str(
                                item[
                                    "MaTuVung"
                                ]
                            )
                            for item
                            in candidates
                        )
                    ),

                    "TrangThai": (
                        pinyin_status
                    ),
                }
            )

        language_203[
            char
        ] = {
            "PinyinFinal": (
                chosen[
                    "Pinyin"
                ]
            ),

            "NghiaFinal": (
                chosen[
                    "NghiaTiengViet"
                ]
            ),

            "MaTuVungNguon": (
                chosen[
                    "MaTuVung"
                ]
            ),

            "MaNguonNgonNgu": (
                chosen[
                    "MaNguon"
                ]
            ),

            "TrangThaiPinyin": (
                pinyin_status
            ),

            "TatCaPinyin": (
                " | ".join(
                    item["Pinyin"]
                    for item
                    in candidates
                )
            ),

            "TatCaNghia": (
                " || ".join(
                    item[
                        "NghiaTiengViet"
                    ]
                    for item
                    in candidates
                )
            ),
        }

    print(
        "Chu co >1 TuVung don:",
        len(
            multiple_candidate_chars
        ),
    )

    if multiple_candidate_chars:

        print(
            "  ",
            " ".join(
                multiple_candidate_chars
            ),
        )

    print(
        "Chu can review Pinyin:",
        len(
            pinyin_review_rows
        ),
    )

    for item in pinyin_review_rows:

        print(
            f"  {item['KyTu']} "
            f"| Nguon="
            f"{item['PinyinNguon']} "
            f"| TuVung="
            f"{item['TatCaPinyinTuVung']}"
        )

    # =====================================================
    # 7. THUTU PER LESSON
    # =====================================================
    lesson_sequence = defaultdict(
        list
    )

    for char in sorted(
        structure_chars,
        key=lambda c: (
            structure_order[c]
        ),
    ):

        lesson_no = int(
            clean(
                structure_map[
                    char
                ][
                    "BaiXuatHienDau"
                ]
            )
        )

        lesson_sequence[
            lesson_no
        ].append(
            char
        )

    proposed_order = {}

    for lesson_no in range(
        1,
        24,
    ):

        for order, char in enumerate(
            lesson_sequence.get(
                lesson_no,
                [],
            ),
            start=1,
        ):

            proposed_order[
                char
            ] = (
                order
            )

    # =====================================================
    # 8. CURRENT SQL MAP
    # =====================================================
    current_map = {}

    for row in current_rows:

        char = clean(
            row[2]
        )

        current_map[
            char
        ] = {
            "MaChuHan": int(
                row[0]
            ),

            "MaBaiHoc": int(
                row[1]
            ),

            "Pinyin": clean(
                row[3]
            ),

            "Nghia": clean(
                row[4]
            ),

            "MaBoThu": row[5],

            "SoNet": row[6],

            "ThuTu": row[7],

            "MaNguon": row[8],

            "TrangThai": clean(
                row[9]
            ),
        }

    # =====================================================
    # 9. BUILD FINAL MERGED REVIEW
    # =====================================================
    print()
    print(
        "[6] TAO BAN REVIEW TONG 301 CHU"
    )
    print("-" * 120)

    output_rows = []

    critical_issues = []

    existing_exact = 0
    existing_need_review = 0

    source_counts = Counter()

    for char in sorted(
        structure_chars,
        key=lambda c: (
            structure_order[c]
        ),
    ):

        structure = (
            structure_map[
                char
            ]
        )

        lesson_no = int(
            clean(
                structure[
                    "BaiXuatHienDau"
                ]
            )
        )

        ma_bai_hoc = int(
            clean(
                structure[
                    "MaBaiHoc"
                ]
            )
        )

        if char in language_203:

            language = (
                language_203[
                    char
                ]
            )

            pinyin_final = (
                language[
                    "PinyinFinal"
                ]
            )

            meaning_final = (
                language[
                    "NghiaFinal"
                ]
            )

            source_language = (
                "TuVung_DaDuyet"
            )

            source_language_id = (
                language[
                    "MaNguonNgonNgu"
                ]
            )

            source_reference = (
                language[
                    "MaTuVungNguon"
                ]
            )

            pinyin_status = (
                language[
                    "TrangThaiPinyin"
                ]
            )

            language_reviewed = (
                1
                if pinyin_status
                != "CAN_REVIEW_PINYIN"
                else 0
            )

        else:

            language = (
                review_10o_map[
                    char
                ]
            )

            pinyin_final = (
                language[
                    "PinyinFinal"
                ]
            )

            meaning_final = (
                language[
                    "NghiaFinal"
                ]
            )

            source_language = (
                "10O_CC-CEDICT_"
                "BIEN_SOAN_DO_AN"
            )

            source_language_id = (
                2
            )

            source_reference = ""

            pinyin_status = (
                "10O_DA_DUYET"
            )

            language_reviewed = 1

        source_counts[
            source_language
        ] += 1

        radical_id = to_int(
            structure[
                "MaBoThuChuan"
            ]
        )

        stroke_count = to_int(
            structure[
                "SoNetNguon"
            ]
        )

        order_in_lesson = (
            proposed_order[
                char
            ]
        )

        # -----------------------------------------
        # Critical completeness
        # -----------------------------------------
        if not pinyin_final:

            critical_issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": (
                        "THIEU_PINYIN"
                    ),
                    "ChiTiet": "",
                }
            )

        if not meaning_final:

            critical_issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": (
                        "THIEU_NGHIA_VIET"
                    ),
                    "ChiTiet": "",
                }
            )

        if radical_id is None:

            critical_issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": (
                        "THIEU_MABOTHU"
                    ),
                    "ChiTiet": "",
                }
            )

        if stroke_count is None:

            critical_issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": (
                        "THIEU_SONET"
                    ),
                    "ChiTiet": "",
                }
            )

        # -----------------------------------------
        # Compare existing 17
        # -----------------------------------------
        current = (
            current_map.get(
                char
            )
        )

        current_status = (
            "CHUA_CO_TRONG_SQL"
        )

        current_diff = []

        ma_chu_han_current = ""

        if current:

            ma_chu_han_current = (
                current[
                    "MaChuHan"
                ]
            )

            if (
                current[
                    "MaBaiHoc"
                ]
                != ma_bai_hoc
            ):

                current_diff.append(
                    "MaBaiHoc"
                )

            if (
                normalize_text(
                    current[
                        "Pinyin"
                    ]
                )
                !=
                normalize_text(
                    pinyin_final
                )
            ):

                current_diff.append(
                    "Pinyin"
                )

            if (
                normalize_text(
                    current[
                        "Nghia"
                    ]
                )
                !=
                normalize_text(
                    meaning_final
                )
            ):

                current_diff.append(
                    "NghiaTiengViet"
                )

            if (
                current[
                    "MaBoThu"
                ]
                != radical_id
            ):

                current_diff.append(
                    "MaBoThu"
                )

            if (
                current[
                    "SoNet"
                ]
                != stroke_count
            ):

                current_diff.append(
                    "SoNet"
                )

            if (
                current[
                    "ThuTu"
                ]
                != order_in_lesson
            ):

                current_diff.append(
                    "ThuTu"
                )

            if current_diff:

                current_status = (
                    "CAN_REVIEW_CAP_NHAT"
                )

                existing_need_review += 1

            else:

                current_status = (
                    "KHOP_NOI_DUNG"
                )

                existing_exact += 1

        output_rows.append(
            {
                "KyTu": char,

                "PhamVi": clean(
                    structure[
                        "PhamVi"
                    ]
                ),

                "BaiXuatHienDau": (
                    lesson_no
                ),

                "MaBaiHoc": (
                    ma_bai_hoc
                ),

                "TieuDeBai": clean(
                    structure[
                        "TieuDeBai"
                    ]
                ),

                "TuVungDauTien": clean(
                    structure[
                        "TuVungDauTien"
                    ]
                ),

                "ThuTuDeXuat": (
                    order_in_lesson
                ),

                "PinyinFinalDeXuat": (
                    pinyin_final
                ),

                "NghiaTiengVietFinalDeXuat": (
                    meaning_final
                ),

                "RadicalChuan": clean(
                    structure[
                        "RadicalChuan"
                    ]
                ),

                "MaBoThu": (
                    radical_id
                ),

                "SoBoThu": clean(
                    structure[
                        "SoBoThuChuan"
                    ]
                ),

                "TenBoThu": clean(
                    structure[
                        "TenBoThuChuan"
                    ]
                ),

                "SoNet": (
                    stroke_count
                ),

                "SoMedian": clean(
                    structure[
                        "SoMedianNguon"
                    ]
                ),

                "MaNguonCauTruc": (
                    STRUCTURE_SOURCE_ID
                ),

                "NguonNgonNgu": (
                    source_language
                ),

                "MaNguonNgonNgu": (
                    source_language_id
                ),

                "MaThamChieuNgonNgu": (
                    source_reference
                ),

                "TrangThaiPinyin": (
                    pinyin_status
                ),

                "NgonNguDaKiemDuyet": (
                    language_reviewed
                ),

                # Chua chot MaNguon duy nhat
                # cho dbo.ChuHan o buoc nay.
                "MaNguonChuHanDeXuat": "",

                "TrangThaiDeXuat": (
                    STATUS_DRAFT
                ),

                "DaCoTrongChuHan": (
                    1
                    if current
                    else 0
                ),

                "MaChuHanHienTai": (
                    ma_chu_han_current
                ),

                "KiemTraChuHanHienTai": (
                    current_status
                ),

                "CotKhacHienTai": (
                    " | ".join(
                        current_diff
                    )
                ),

                "SanSangNoiDung": (
                    1
                    if (
                        pinyin_final
                        and meaning_final
                        and radical_id
                        is not None
                        and stroke_count
                        is not None
                        and language_reviewed
                        == 1
                    )
                    else 0
                ),

                "GhiChu": (
                    clean(
                        review_10o_map[
                            char
                        ][
                            "GhiChu"
                        ]
                    )
                    if char
                    in review_10o_map
                    else ""
                ),
            }
        )

    # =====================================================
    # 10. LESSON SUMMARY
    # =====================================================
    lesson_summary = []

    for lesson_no in range(
        1,
        24,
    ):

        lesson_chars = [
            row
            for row in output_rows
            if row[
                "BaiXuatHienDau"
            ] == lesson_no
        ]

        lesson_summary.append(
            {
                "SoThuTuBai": (
                    lesson_no
                ),

                "MaBaiHoc": (
                    lesson_chars[
                        0
                    ][
                        "MaBaiHoc"
                    ]
                    if lesson_chars
                    else ""
                ),

                "TieuDeBai": (
                    lesson_chars[
                        0
                    ][
                        "TieuDeBai"
                    ]
                    if lesson_chars
                    else ""
                ),

                "SoChuHan": (
                    len(
                        lesson_chars
                    )
                ),

                "SoChuSanSangNoiDung": (
                    sum(
                        int(
                            row[
                                "SanSangNoiDung"
                            ]
                        )
                        for row
                        in lesson_chars
                    )
                ),

                "DanhSachChu": (
                    " ".join(
                        row[
                            "KyTu"
                        ]
                        for row
                        in lesson_chars
                    )
                ),
            }
        )

    # =====================================================
    # 11. WRITE
    # =====================================================
    print()
    print(
        "[7] GHI FILE REVIEW"
    )
    print("-" * 120)

    output_fields = [
        "KyTu",
        "PhamVi",
        "BaiXuatHienDau",
        "MaBaiHoc",
        "TieuDeBai",
        "TuVungDauTien",
        "ThuTuDeXuat",

        "PinyinFinalDeXuat",
        "NghiaTiengVietFinalDeXuat",

        "RadicalChuan",
        "MaBoThu",
        "SoBoThu",
        "TenBoThu",

        "SoNet",
        "SoMedian",

        "MaNguonCauTruc",

        "NguonNgonNgu",
        "MaNguonNgonNgu",
        "MaThamChieuNgonNgu",

        "TrangThaiPinyin",
        "NgonNguDaKiemDuyet",

        "MaNguonChuHanDeXuat",
        "TrangThaiDeXuat",

        "DaCoTrongChuHan",
        "MaChuHanHienTai",
        "KiemTraChuHanHienTai",
        "CotKhacHienTai",

        "SanSangNoiDung",

        "GhiChu",
    ]

    write_csv(
        OUTPUT_FILE,
        output_fields,
        output_rows,
    )

    write_csv(
        ISSUES_FILE,
        [
            "KyTu",
            "LoaiLoi",
            "ChiTiet",
        ],
        critical_issues,
    )

    write_csv(
        PINYIN_REVIEW_FILE,
        [
            "KyTu",
            "BaiXuatHienDau",
            "TuVungDauTien",
            "PinyinNguon",
            "PinyinTuVungChon",
            "TatCaPinyinTuVung",
            "TatCaMaTuVung",
            "TrangThai",
        ],
        pinyin_review_rows,
    )

    write_csv(
        LESSON_SUMMARY_FILE,
        [
            "SoThuTuBai",
            "MaBaiHoc",
            "TieuDeBai",
            "SoChuHan",
            "SoChuSanSangNoiDung",
            "DanhSachChu",
        ],
        lesson_summary,
    )

    print(
        "Merged review:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "Issues:"
    )

    print(
        ISSUES_FILE
    )

    print()
    print(
        "Pinyin review:"
    )

    print(
        PINYIN_REVIEW_FILE
    )

    print()
    print(
        "Lesson summary:"
    )

    print(
        LESSON_SUMMARY_FILE
    )

    # =====================================================
    # FINAL
    # =====================================================
    ready_count = sum(
        int(
            row[
                "SanSangNoiDung"
            ]
        )
        for row
        in output_rows
    )

    print()
    print("=" * 120)
    print(
        "KET QUA 10P"
    )
    print("=" * 120)

    print(
        "Tong Chu Han:",
        len(output_rows),
    )

    print(
        "HSK1 chuan:",
        len(standard_chars),
    )

    print(
        "Chu bo sung:",
        len(supplement_chars),
    )

    print()
    print(
        "Nguon ngon ngu:"
    )

    print(
        "  TuVung da duyet:",
        source_counts[
            "TuVung_DaDuyet"
        ],
    )

    print(
        "  10O da duyet:",
        source_counts[
            "10O_CC-CEDICT_"
            "BIEN_SOAN_DO_AN"
        ],
    )

    print()
    print(
        "301 chu SanSangNoiDung:",
        ready_count,
        "/301",
    )

    print(
        "Critical issue:",
        len(
            critical_issues
        ),
    )

    print(
        "203 chu can review Pinyin:",
        len(
            pinyin_review_rows
        ),
    )

    print()
    print(
        "17 ChuHan hien co "
        "khop noi dung:",
        existing_exact,
        "/17",
    )

    print(
        "17 ChuHan hien co "
        "can review cap nhat:",
        existing_need_review,
        "/17",
    )

    print()
    print(
        "CHUA CHOT MaNguon "
        "DUY NHAT CHO dbo.ChuHan."
    )

    print(
        "CHUA INSERT ChuHan."
    )

    print(
        "CHUA UPDATE 17 ChuHan CU."
    )

    print(
        "CHUA INSERT NetChuHan."
    )

    print(
        "DATABASE KHONG BI SUA."
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
            "10P THAT BAI"
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