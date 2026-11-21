from pathlib import Path
import csv
import sys
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

STANDARD_VOCAB_SOURCE_ID = 1002
SUPPLEMENT_WORD = "越南"

EXPECTED_STANDARD_VOCAB = 500
EXPECTED_RUNTIME_VOCAB = 501

EXPECTED_STANDARD_HANZI = 300
EXPECTED_RUNTIME_HANZI = 301

EXPECTED_CURRENT_HANZI = 17


# =========================================================
# OUTPUT
# =========================================================
OUTPUT_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
)

STANDARD_FILE = (
    OUTPUT_DIR
    / "hsk1_300_standard_hanzi_from_vocab_review.csv"
)

SUPPLEMENT_FILE = (
    OUTPUT_DIR
    / "hsk1_hanzi_supplement_diff_review.csv"
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


def extract_chars(word):

    return [
        char
        for char in word
        if is_hanzi(char)
    ]


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10E - XAC MINH 300 CHU HAN CHUAN HSK1 "
        "VA 1 CHU BO SUNG"
    )
    print("=" * 120)

    print()
    print("MUC TIEU:")
    print("  500 TU MaNguon=1002 -> KIEM TRA 300 CHU HAN")
    print("  501 TU RUNTIME       -> KIEM TRA 301 CHU HAN")
    print("  XAC DINH CHU PHAT SINH BOI TU 越南")
    print("  DOI CHIEU 17 ChuHan HIEN CO")
    print()
    print("CHE DO:")
    print("  CHI SELECT DATABASE")
    print("  TAO CSV REVIEW")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    # =====================================================
    # 1. CONNECT
    # =====================================================
    print()
    print("[1] KET NOI DATABASE")
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
                        ),
                        SUSER_SNAME();
                    """
                )

                database_name, server_name, login_name = (
                    cursor.fetchone()
                )

                print(
                    "Server:",
                    clean(server_name),
                )

                print(
                    "Database:",
                    clean(database_name),
                )

                print(
                    "Tai khoan:",
                    clean(login_name),
                )

                if (
                    clean(database_name).lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi nham database."
                    )

                print(
                    "KET NOI: OK"
                )

                # =================================================
                # 2. READ ALL 501
                # =================================================
                print()
                print("[2] DOC 501 TU VUNG RUNTIME")
                print("-" * 120)

                cursor.execute(
                    """
                    SELECT
                        bh.SoThuTuBai,
                        bh.MaBaiHoc,
                        bh.TieuDe,
                        tvbh.ThuTu,
                        tv.MaTuVung,
                        tv.ChuHan,
                        tv.PhienAm,
                        tv.NghiaTiengViet,
                        tv.MaNguon

                    FROM dbo.TuVungBaiHoc AS tvbh

                    INNER JOIN dbo.BaiHoc AS bh
                        ON tvbh.MaBaiHoc = bh.MaBaiHoc

                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc = kh.MaKhoaHoc

                    INNER JOIN dbo.TuVung AS tv
                        ON tvbh.MaTuVung = tv.MaTuVung

                    WHERE
                        kh.MaKyHieu = ?

                    ORDER BY
                        bh.SoThuTuBai,
                        tvbh.ThuTu,
                        tv.MaTuVung;
                    """,
                    COURSE_CODE,
                )

                runtime_rows = (
                    cursor.fetchall()
                )

                if (
                    len(runtime_rows)
                    != EXPECTED_RUNTIME_VOCAB
                ):

                    fail(
                        "Runtime vocab khong bang 501. "
                        f"Thuc te: {len(runtime_rows)}"
                    )

                print(
                    "Runtime vocab:",
                    len(runtime_rows),
                )

                # =================================================
                # 3. SPLIT STANDARD VS SUPPLEMENT
                # =================================================
                print()
                print(
                    "[3] TACH 500 TU CHUAN "
                    "VA TU BO SUNG"
                )
                print("-" * 120)

                standard_rows = [
                    row
                    for row in runtime_rows
                    if int(row[8])
                    == STANDARD_VOCAB_SOURCE_ID
                ]

                nonstandard_rows = [
                    row
                    for row in runtime_rows
                    if int(row[8])
                    != STANDARD_VOCAB_SOURCE_ID
                ]

                print(
                    "MaNguon=1002:",
                    len(standard_rows),
                )

                print(
                    "Khac MaNguon=1002:",
                    len(nonstandard_rows),
                )

                if (
                    len(standard_rows)
                    != EXPECTED_STANDARD_VOCAB
                ):

                    fail(
                        "Tu chuan MaNguon=1002 "
                        "khong bang 500."
                    )

                if len(nonstandard_rows) != 1:

                    fail(
                        "Du kien chi co "
                        "1 tu bo sung."
                    )

                supplement_row = (
                    nonstandard_rows[0]
                )

                supplement_word = clean(
                    supplement_row[5]
                )

                print(
                    "Tu bo sung:",
                    supplement_word,
                )

                print(
                    "MaTuVung:",
                    supplement_row[4],
                )

                print(
                    "MaNguon:",
                    supplement_row[8],
                )

                if (
                    supplement_word
                    != SUPPLEMENT_WORD
                ):

                    fail(
                        "Tu bo sung khong phai 越南."
                    )

                # =================================================
                # 4. STANDARD CHARACTER SET
                # =================================================
                print()
                print(
                    "[4] TACH CHU HAN "
                    "TU 500 TU CHUAN"
                )
                print("-" * 120)

                standard_chars = set()

                first_context = {}

                word_ids_by_char = defaultdict(
                    set
                )

                for row in standard_rows:

                    lesson_no = int(row[0])
                    lesson_id = int(row[1])
                    lesson_title = clean(row[2])
                    vocab_order = int(row[3])

                    vocab_id = int(row[4])
                    word = clean(row[5])
                    pinyin = clean(row[6])
                    meaning = clean(row[7])

                    for position, char in enumerate(
                        extract_chars(word),
                        start=1,
                    ):

                        standard_chars.add(
                            char
                        )

                        word_ids_by_char[
                            char
                        ].add(
                            vocab_id
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
                            ][
                                "_key"
                            ]
                        ):

                            first_context[
                                char
                            ] = {
                                "_key": key,
                                "KyTu": char,
                                "BaiXuatHienDau": (
                                    lesson_no
                                ),
                                "MaBaiHocDauTien": (
                                    lesson_id
                                ),
                                "TieuDeBaiDauTien": (
                                    lesson_title
                                ),
                                "ThuTuTuVungDauTien": (
                                    vocab_order
                                ),
                                "MaTuVungDauTien": (
                                    vocab_id
                                ),
                                "TuVungDauTien": (
                                    word
                                ),
                                "PinyinTuDauTien": (
                                    pinyin
                                ),
                                "NghiaTuDauTien": (
                                    meaning
                                ),
                            }

                print(
                    "Chu Han khac nhau "
                    "trong 500 tu chuan:",
                    len(
                        standard_chars
                    ),
                )

                if (
                    len(standard_chars)
                    != EXPECTED_STANDARD_HANZI
                ):

                    fail(
                        "500 tu chuan khong tao ra "
                        "dung 300 Chu Han. "
                        f"Thuc te: "
                        f"{len(standard_chars)}"
                    )

                print(
                    "300 CHU HAN CHUAN: OK"
                )

                # =================================================
                # 5. RUNTIME CHARACTER SET
                # =================================================
                print()
                print(
                    "[5] TACH CHU HAN "
                    "TU TOAN BO 501 TU"
                )
                print("-" * 120)

                runtime_chars = set()

                for row in runtime_rows:

                    word = clean(row[5])

                    runtime_chars.update(
                        extract_chars(word)
                    )

                print(
                    "Chu Han khac nhau "
                    "trong 501 tu:",
                    len(runtime_chars),
                )

                if (
                    len(runtime_chars)
                    != EXPECTED_RUNTIME_HANZI
                ):

                    fail(
                        "501 tu khong tao ra "
                        "dung 301 Chu Han."
                    )

                # =================================================
                # 6. DIFF
                # =================================================
                print()
                print(
                    "[6] XAC DINH CHU BO SUNG"
                )
                print("-" * 120)

                extra_chars = sorted(
                    runtime_chars
                    - standard_chars
                )

                missing_runtime = sorted(
                    standard_chars
                    - runtime_chars
                )

                print(
                    "Chu ngoai bo 300:",
                    len(extra_chars),
                )

                print(
                    "Danh sach:",
                    (
                        " ".join(extra_chars)
                        if extra_chars
                        else "<KHONG>"
                    ),
                )

                print(
                    "Chu chuan bi thieu "
                    "khoi runtime:",
                    len(
                        missing_runtime
                    ),
                )

                if missing_runtime:

                    print(
                        "Danh sach:",
                        " ".join(
                            missing_runtime
                        ),
                    )

                if len(extra_chars) != 1:

                    fail(
                        "Du kien chi co 1 chu "
                        "bo sung ngoai bo 300."
                    )

                if missing_runtime:

                    fail(
                        "Runtime bi thieu "
                        "chu chuan."
                    )

                supplement_chars = set(
                    extract_chars(
                        supplement_word
                    )
                )

                extra_char = (
                    extra_chars[0]
                )

                if (
                    extra_char
                    not in supplement_chars
                ):

                    fail(
                        "Chu ngoai bo 300 "
                        "khong nam trong 越南."
                    )

                print(
                    "Chu bo sung xac dinh:",
                    extra_char,
                )

                # =================================================
                # 7. CURRENT 17
                # =================================================
                print()
                print(
                    "[7] DOI CHIEU 17 ChuHan "
                    "HIEN CO"
                )
                print("-" * 120)

                cursor.execute(
                    """
                    SELECT
                        ch.MaChuHan,
                        ch.KyTu,
                        bh.SoThuTuBai,
                        ch.ThuTu

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

                if (
                    len(current_rows)
                    != EXPECTED_CURRENT_HANZI
                ):

                    fail(
                        "ChuHan hien tai "
                        "khong bang 17."
                    )

                current_chars = {
                    clean(row[1])
                    for row in current_rows
                }

                current_standard = (
                    current_chars
                    & standard_chars
                )

                current_extra = (
                    current_chars
                    - standard_chars
                )

                print(
                    "17 chu hien co:",
                    len(current_chars),
                )

                print(
                    "Nam trong bo 300 chuan:",
                    len(current_standard),
                )

                print(
                    "Ngoai bo 300:",
                    len(current_extra),
                )

                if current_extra:

                    print(
                        "Danh sach ngoai chuan:",
                        " ".join(
                            sorted(
                                current_extra
                            )
                        ),
                    )

                if len(current_standard) != 17:

                    fail(
                        "17 ChuHan Bai 1 "
                        "khong nam day du "
                        "trong bo 300 chuan."
                    )

                print(
                    "17/17 HIEN CO "
                    "NAM TRONG BO 300: OK"
                )

                # =================================================
                # 8. EXPORT STANDARD 300
                # =================================================
                print()
                print(
                    "[8] TAO FILE REVIEW "
                    "BO 300 CHU CHUAN"
                )
                print("-" * 120)

                standard_output = []

                ordered_standard = sorted(
                    standard_chars,
                    key=lambda char: (
                        first_context[
                            char
                        ][
                            "_key"
                        ]
                    ),
                )

                for index, char in enumerate(
                    ordered_standard,
                    start=1,
                ):

                    context = (
                        first_context[
                            char
                        ]
                    )

                    standard_output.append(
                        {
                            "STTChuanNoiBo": (
                                index
                            ),

                            "KyTu": char,

                            "BaiXuatHienDau": (
                                context[
                                    "BaiXuatHienDau"
                                ]
                            ),

                            "MaBaiHocDauTien": (
                                context[
                                    "MaBaiHocDauTien"
                                ]
                            ),

                            "TieuDeBaiDauTien": (
                                context[
                                    "TieuDeBaiDauTien"
                                ]
                            ),

                            "ThuTuTuVungDauTien": (
                                context[
                                    "ThuTuTuVungDauTien"
                                ]
                            ),

                            "MaTuVungDauTien": (
                                context[
                                    "MaTuVungDauTien"
                                ]
                            ),

                            "TuVungDauTien": (
                                context[
                                    "TuVungDauTien"
                                ]
                            ),

                            "PinyinTuDauTien": (
                                context[
                                    "PinyinTuDauTien"
                                ]
                            ),

                            "NghiaTuDauTien": (
                                context[
                                    "NghiaTuDauTien"
                                ]
                            ),

                            "SoTuChuanChuaChu": (
                                len(
                                    word_ids_by_char[
                                        char
                                    ]
                                )
                            ),

                            "DaCoTrongChuHan": (
                                1
                                if char
                                in current_chars
                                else 0
                            ),

                            "PhamVi": (
                                "HSK1_CHUAN_300"
                            ),

                            "DaKiemDuyet": 0,

                            "GhiChu": "",
                        }
                    )

                write_csv(
                    STANDARD_FILE,
                    [
                        "STTChuanNoiBo",
                        "KyTu",
                        "BaiXuatHienDau",
                        "MaBaiHocDauTien",
                        "TieuDeBaiDauTien",
                        "ThuTuTuVungDauTien",
                        "MaTuVungDauTien",
                        "TuVungDauTien",
                        "PinyinTuDauTien",
                        "NghiaTuDauTien",
                        "SoTuChuanChuaChu",
                        "DaCoTrongChuHan",
                        "PhamVi",
                        "DaKiemDuyet",
                        "GhiChu",
                    ],
                    standard_output,
                )

                # =================================================
                # 9. EXPORT SUPPLEMENT DIFF
                # =================================================
                supplement_output = []

                for char in sorted(
                    supplement_chars
                ):

                    supplement_output.append(
                        {
                            "KyTu": char,

                            "NamTrongBo300": (
                                1
                                if char
                                in standard_chars
                                else 0
                            ),

                            "LaChuBoSungNgoai300": (
                                1
                                if char
                                in extra_chars
                                else 0
                            ),

                            "TuBoSung": (
                                supplement_word
                            ),

                            "MaTuVung": (
                                supplement_row[4]
                            ),

                            "PinyinTu": clean(
                                supplement_row[6]
                            ),

                            "NghiaTiengViet": clean(
                                supplement_row[7]
                            ),

                            "MaNguonTu": (
                                supplement_row[8]
                            ),

                            "GhiChu": "",
                        }
                    )

                write_csv(
                    SUPPLEMENT_FILE,
                    [
                        "KyTu",
                        "NamTrongBo300",
                        "LaChuBoSungNgoai300",
                        "TuBoSung",
                        "MaTuVung",
                        "PinyinTu",
                        "NghiaTiengViet",
                        "MaNguonTu",
                        "GhiChu",
                    ],
                    supplement_output,
                )

                print(
                    "Bo 300:"
                )

                print(
                    STANDARD_FILE
                )

                print()
                print(
                    "Supplement diff:"
                )

                print(
                    SUPPLEMENT_FILE
                )

                # =================================================
                # FINAL
                # =================================================
                print()
                print("=" * 120)
                print(
                    "KET QUA 10E"
                )
                print("=" * 120)

                print(
                    "Tu vung chuan MaNguon=1002:",
                    len(standard_rows),
                )

                print(
                    "Chu Han tu 500 tu chuan:",
                    len(standard_chars),
                )

                print(
                    "Tu vung runtime:",
                    len(runtime_rows),
                )

                print(
                    "Chu Han runtime:",
                    len(runtime_chars),
                )

                print(
                    "Tu bo sung:",
                    supplement_word,
                )

                print(
                    "Chu trong tu bo sung:",
                    " ".join(
                        sorted(
                            supplement_chars
                        )
                    ),
                )

                print(
                    "Chu bo sung ngoai bo 300:",
                    extra_char,
                )

                print(
                    "17 ChuHan hien co "
                    "nam trong bo 300:",
                    len(current_standard),
                    "/17",
                )

                print()
                print(
                    "KET LUAN DU LIEU:"
                )

                print(
                    "HSK1 CHUAN = "
                    "500 TU + 300 CHU HAN."
                )

                print(
                    "DU AN HIEN CO "
                    "1 TU BO SUNG: 越南."
                )

                print(
                    "VI VAY TAP RUNTIME "
                    "CO 301 CHU KHAC NHAU."
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
                print("=" * 120)
                print("HOAN TAT")
                print("=" * 120)

        finally:

            try:
                connection.rollback()
            except Exception:
                pass


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
            "10E THAT BAI"
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