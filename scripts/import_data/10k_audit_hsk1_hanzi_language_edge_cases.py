from pathlib import Path
import csv
import sys
from collections import Counter, defaultdict


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]


# =========================================================
# CONFIG
# =========================================================
EXPECTED_HANZI = 301

EXPECTED_WITH_SINGLE = 203
EXPECTED_WITHOUT_SINGLE = 98

EXPECTED_SINGLE_VOCAB_ROWS = 206

EXPECTED_MULTI_READING = 2

EXPECTED_EXISTING = 17
EXPECTED_EXISTING_PINYIN_MATCH = 16


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
    / "hsk1_301_hanzi_language_source_audit.csv"
)

MISSING_FILE = (
    REVIEW_DIR
    / "hsk1_98_hanzi_missing_vietnamese_source.csv"
)

SPECIAL_FILE = (
    REVIEW_DIR
    / "hsk1_hanzi_language_special_cases.csv"
)

LESSON_SUMMARY_FILE = (
    REVIEW_DIR
    / "hsk1_98_missing_vietnamese_by_lesson.csv"
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


def split_pipe(value):

    return [
        clean(item)
        for item
        in clean(value).split("|")
        if clean(item)
    ]


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10K - AUDIT CAC TRUONG HOP "
        "NGON NGU DAC BIET CUA 301 CHU HAN"
    )
    print("=" * 120)

    print()
    print("MUC TIEU:")
    print("  XAC DINH 2 CHU CO NHIEU CACH DOC")
    print("  XAC DINH CHU CO NHIEU TuVung DON")
    print("  XAC DINH 1/17 CHU HIEN CO LECH PINYIN")
    print("  XUAT CHINH XAC 98 CHU CHUA CO NGUON NGHIA VIET")
    print("  THONG KE 98 CHU THEO 23 BAI")
    print()
    print("CHE DO:")
    print("  CHI DOC FILE 10J")
    print("  KHONG SUA DATABASE")
    print("  KHONG SUA FILE 10J")
    print("  KHONG TU DONG CHON PINYIN")
    print("  KHONG TU DONG DICH NGHIA")

    # =====================================================
    # 1. READ 10J
    # =====================================================
    print()
    print("[1] DOC FILE 10J")
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

        "PinyinNguonRaw",
        "LoaiPinyinNguon",
        "DefinitionEnglishNguon",

        "MaBoThuChuan",
        "RadicalChuan",
        "SoNetNguon",

        "SoTuVungDonTimThay",
        "SoTuVungDonDaDuyet",

        "MaTuVungDon",
        "PinyinTuVungDon",
        "NghiaVietTuVungDon",
        "MaNguonTuVungDon",

        "MaTuVungDonDaDuyet",
        "PinyinDaDuyet",
        "NghiaVietDaDuyet",

        "TrangThaiNguonNghiaViet",

        "DaCoTrongChuHan",
        "PinyinChuHanHienTai",
        "NghiaChuHanHienTai",
        "KiemTraPinyinHienTai",
    }

    missing_fields = (
        required
        - set(fields)
    )

    if missing_fields:

        fail(
            "File 10J thieu cot: "
            + ", ".join(
                sorted(
                    missing_fields
                )
            )
        )

    if len(rows) != EXPECTED_HANZI:

        fail(
            "File 10J khong co dung "
            "301 dong."
        )

    characters = [
        clean(
            row["KyTu"]
        )
        for row in rows
    ]

    if len(set(characters)) != 301:

        fail(
            "KyTu trong 10J "
            "khong duy nhat."
        )

    print(
        "Tong Chu Han:",
        len(rows),
    )

    # =====================================================
    # 2. VERIFY SINGLE-VOCAB COVERAGE
    # =====================================================
    print()
    print(
        "[2] KIEM TRA COVERAGE TuVung DON"
    )
    print("-" * 120)

    with_single = [
        row
        for row in rows
        if int(
            clean(
                row[
                    "SoTuVungDonDaDuyet"
                ]
            )
            or 0
        ) > 0
    ]

    without_single = [
        row
        for row in rows
        if int(
            clean(
                row[
                    "SoTuVungDonDaDuyet"
                ]
            )
            or 0
        ) == 0
    ]

    total_single_rows = sum(
        int(
            clean(
                row[
                    "SoTuVungDonDaDuyet"
                ]
            )
            or 0
        )
        for row in rows
    )

    print(
        "Chu co TuVung don da duyet:",
        len(with_single),
    )

    print(
        "Chu khong co TuVung don:",
        len(without_single),
    )

    print(
        "Tong ban ghi TuVung don da duyet:",
        total_single_rows,
    )

    if (
        len(with_single)
        != EXPECTED_WITH_SINGLE
    ):

        fail(
            "So chu co TuVung don "
            "khong con bang 203."
        )

    if (
        len(without_single)
        != EXPECTED_WITHOUT_SINGLE
    ):

        fail(
            "So chu thieu TuVung don "
            "khong con bang 98."
        )

    if (
        total_single_rows
        != EXPECTED_SINGLE_VOCAB_ROWS
    ):

        fail(
            "Tong ban ghi TuVung don "
            "khong con bang 206."
        )

    print(
        "COVERAGE TuVung DON: OK"
    )

    # =====================================================
    # 3. MULTIPLE PINYIN IN SOURCE
    # =====================================================
    print()
    print(
        "[3] CHU CO NHIEU CACH DOC "
        "TRONG MAKE ME A HANZI"
    )
    print("-" * 120)

    multi_reading_rows = [
        row
        for row in rows
        if clean(
            row["LoaiPinyinNguon"]
        ) == "NHIEU_CACH_DOC"
    ]

    print(
        "So luong:",
        len(multi_reading_rows),
    )

    if (
        len(multi_reading_rows)
        != EXPECTED_MULTI_READING
    ):

        fail(
            "So chu da am khong con "
            "bang 2."
        )

    for row in multi_reading_rows:

        print(
            f"{clean(row['KyTu'])} "
            f"| PinyinNguon="
            f"{clean(row['PinyinNguonRaw'])} "
            f"| TuVungDauTien="
            f"{clean(row['TuVungDauTien'])} "
            f"| Bai="
            f"{clean(row['BaiXuatHienDau'])}"
        )

    # =====================================================
    # 4. MULTIPLE SINGLE-VOCAB ENTRIES
    # =====================================================
    print()
    print(
        "[4] CHU CO NHIEU HON "
        "1 TuVung DON DA DUYET"
    )
    print("-" * 120)

    multiple_vocab_rows = [
        row
        for row in rows
        if int(
            clean(
                row[
                    "SoTuVungDonDaDuyet"
                ]
            )
            or 0
        ) > 1
    ]

    extra_rows = sum(
        int(
            clean(
                row[
                    "SoTuVungDonDaDuyet"
                ]
            )
            or 0
        ) - 1
        for row in multiple_vocab_rows
    )

    print(
        "So Chu Han:",
        len(multiple_vocab_rows),
    )

    print(
        "So ban ghi du so voi "
        "moi chu 1 dong:",
        extra_rows,
    )

    for row in multiple_vocab_rows:

        print()
        print(
            "KyTu:",
            clean(row["KyTu"]),
        )

        print(
            "  SoTuVungDonDaDuyet:",
            clean(
                row[
                    "SoTuVungDonDaDuyet"
                ]
            ),
        )

        print(
            "  MaTuVung:",
            clean(
                row[
                    "MaTuVungDonDaDuyet"
                ]
            ),
        )

        print(
            "  Pinyin:",
            clean(
                row[
                    "PinyinDaDuyet"
                ]
            ),
        )

        print(
            "  Nghia:",
            clean(
                row[
                    "NghiaVietDaDuyet"
                ]
            ),
        )

    # =====================================================
    # 5. EXISTING 17 PINYIN
    # =====================================================
    print()
    print(
        "[5] DOI CHIEU PINYIN "
        "17 ChuHan HIEN CO"
    )
    print("-" * 120)

    existing_rows = [
        row
        for row in rows
        if clean(
            row["DaCoTrongChuHan"]
        ) == "1"
    ]

    if (
        len(existing_rows)
        != EXPECTED_EXISTING
    ):

        fail(
            "Khong con dung "
            "17 ChuHan hien co."
        )

    exact_existing = [
        row
        for row in existing_rows
        if clean(
            row[
                "KiemTraPinyinHienTai"
            ]
        ) == "EXACT_MATCH"
    ]

    mismatch_existing = [
        row
        for row in existing_rows
        if clean(
            row[
                "KiemTraPinyinHienTai"
            ]
        ) != "EXACT_MATCH"
    ]

    print(
        "Exact match:",
        len(exact_existing),
        "/17",
    )

    print(
        "Can review:",
        len(mismatch_existing),
        "/17",
    )

    if (
        len(exact_existing)
        != EXPECTED_EXISTING_PINYIN_MATCH
    ):

        fail(
            "Exact-match khong con "
            "16/17."
        )

    for row in mismatch_existing:

        print()
        print(
            "CHU CAN REVIEW:"
        )

        print(
            "  KyTu:",
            clean(row["KyTu"]),
        )

        print(
            "  Pinyin SQL:",
            clean(
                row[
                    "PinyinChuHanHienTai"
                ]
            ),
        )

        print(
            "  Pinyin MakeMeAHanzi:",
            clean(
                row[
                    "PinyinNguonRaw"
                ]
            ),
        )

        print(
            "  Pinyin TuVung da duyet:",
            clean(
                row[
                    "PinyinDaDuyet"
                ]
            ),
        )

        print(
            "  Nghia ChuHan hien tai:",
            clean(
                row[
                    "NghiaChuHanHienTai"
                ]
            ),
        )

        print(
            "  TuVung dau tien:",
            clean(
                row[
                    "TuVungDauTien"
                ]
            ),
        )

    # =====================================================
    # 6. 98 MISSING VIETNAMESE SOURCE
    # =====================================================
    print()
    print(
        "[6] 98 CHU CHUA CO NGUON "
        "NGHIA VIET TU TuVung DON"
    )
    print("-" * 120)

    missing_rows = []

    lesson_missing = defaultdict(
        list
    )

    for row in without_single:

        lesson_no = int(
            clean(
                row[
                    "BaiXuatHienDau"
                ]
            )
        )

        char = clean(
            row["KyTu"]
        )

        lesson_missing[
            lesson_no
        ].append(
            char
        )

        missing_rows.append(
            {
                "KyTu": char,

                "PhamVi": clean(
                    row["PhamVi"]
                ),

                "BaiXuatHienDau": (
                    lesson_no
                ),

                "TieuDeBai": clean(
                    row[
                        "TieuDeBai"
                    ]
                ),

                "TuVungDauTien": clean(
                    row[
                        "TuVungDauTien"
                    ]
                ),

                "PinyinNguonRaw": clean(
                    row[
                        "PinyinNguonRaw"
                    ]
                ),

                "DefinitionEnglishNguon": clean(
                    row[
                        "DefinitionEnglishNguon"
                    ]
                ),

                "RadicalChuan": clean(
                    row[
                        "RadicalChuan"
                    ]
                ),

                "MaBoThuChuan": clean(
                    row[
                        "MaBoThuChuan"
                    ]
                ),

                "SoNetNguon": clean(
                    row[
                        "SoNetNguon"
                    ]
                ),

                # De audit nguon tiep theo.
                "NguonNghiaVietDeXuat": "",

                "NghiaVietDeXuat": "",

                "DaKiemDuyetNguonNghia": 0,

                "GhiChu": "",
            }
        )

    for lesson_no in range(
        1,
        24,
    ):

        chars = (
            lesson_missing.get(
                lesson_no,
                [],
            )
        )

        print(
            f"Bai {lesson_no:>2}: "
            f"{len(chars):>2} chu"
            + (
                " | "
                + " ".join(chars)
                if chars
                else ""
            )
        )

    if len(missing_rows) != 98:

        fail(
            "Missing output "
            "khong bang 98."
        )

    # =====================================================
    # 7. BUILD SPECIAL CASE FILE
    # =====================================================
    special_rows = []

    for row in multi_reading_rows:

        special_rows.append(
            {
                "KyTu": clean(
                    row["KyTu"]
                ),

                "LoaiTruongHop": (
                    "NHIEU_CACH_DOC_NGUON"
                ),

                "PinyinNguon": clean(
                    row[
                        "PinyinNguonRaw"
                    ]
                ),

                "PinyinTuVung": clean(
                    row[
                        "PinyinDaDuyet"
                    ]
                ),

                "PinyinChuHanHienTai": clean(
                    row[
                        "PinyinChuHanHienTai"
                    ]
                ),

                "NghiaVietTuVung": clean(
                    row[
                        "NghiaVietDaDuyet"
                    ]
                ),

                "NghiaChuHanHienTai": clean(
                    row[
                        "NghiaChuHanHienTai"
                    ]
                ),

                "BaiXuatHienDau": clean(
                    row[
                        "BaiXuatHienDau"
                    ]
                ),

                "TuVungDauTien": clean(
                    row[
                        "TuVungDauTien"
                    ]
                ),

                "CanXuLy": (
                    "REVIEW_PINYIN"
                ),
            }
        )

    for row in multiple_vocab_rows:

        special_rows.append(
            {
                "KyTu": clean(
                    row["KyTu"]
                ),

                "LoaiTruongHop": (
                    "NHIEU_TUVUNG_DON"
                ),

                "PinyinNguon": clean(
                    row[
                        "PinyinNguonRaw"
                    ]
                ),

                "PinyinTuVung": clean(
                    row[
                        "PinyinDaDuyet"
                    ]
                ),

                "PinyinChuHanHienTai": clean(
                    row[
                        "PinyinChuHanHienTai"
                    ]
                ),

                "NghiaVietTuVung": clean(
                    row[
                        "NghiaVietDaDuyet"
                    ]
                ),

                "NghiaChuHanHienTai": clean(
                    row[
                        "NghiaChuHanHienTai"
                    ]
                ),

                "BaiXuatHienDau": clean(
                    row[
                        "BaiXuatHienDau"
                    ]
                ),

                "TuVungDauTien": clean(
                    row[
                        "TuVungDauTien"
                    ]
                ),

                "CanXuLy": (
                    "REVIEW_NHIEU_MUC"
                ),
            }
        )

    for row in mismatch_existing:

        special_rows.append(
            {
                "KyTu": clean(
                    row["KyTu"]
                ),

                "LoaiTruongHop": (
                    "PINYIN_CHUHAN_KHONG_EXACT"
                ),

                "PinyinNguon": clean(
                    row[
                        "PinyinNguonRaw"
                    ]
                ),

                "PinyinTuVung": clean(
                    row[
                        "PinyinDaDuyet"
                    ]
                ),

                "PinyinChuHanHienTai": clean(
                    row[
                        "PinyinChuHanHienTai"
                    ]
                ),

                "NghiaVietTuVung": clean(
                    row[
                        "NghiaVietDaDuyet"
                    ]
                ),

                "NghiaChuHanHienTai": clean(
                    row[
                        "NghiaChuHanHienTai"
                    ]
                ),

                "BaiXuatHienDau": clean(
                    row[
                        "BaiXuatHienDau"
                    ]
                ),

                "TuVungDauTien": clean(
                    row[
                        "TuVungDauTien"
                    ]
                ),

                "CanXuLy": (
                    "REVIEW_CHUHAN_HIEN_CO"
                ),
            }
        )

    # =====================================================
    # 8. LESSON SUMMARY
    # =====================================================
    lesson_summary_rows = []

    for lesson_no in range(
        1,
        24,
    ):

        chars = (
            lesson_missing.get(
                lesson_no,
                [],
            )
        )

        lesson_summary_rows.append(
            {
                "SoThuTuBai": (
                    lesson_no
                ),

                "SoChuThieuNguonNghiaViet": (
                    len(chars)
                ),

                "DanhSachChu": (
                    " ".join(chars)
                ),
            }
        )

    # =====================================================
    # 9. WRITE
    # =====================================================
    print()
    print(
        "[7] GHI FILE AUDIT"
    )
    print("-" * 120)

    write_csv(
        MISSING_FILE,
        [
            "KyTu",
            "PhamVi",
            "BaiXuatHienDau",
            "TieuDeBai",
            "TuVungDauTien",
            "PinyinNguonRaw",
            "DefinitionEnglishNguon",
            "RadicalChuan",
            "MaBoThuChuan",
            "SoNetNguon",
            "NguonNghiaVietDeXuat",
            "NghiaVietDeXuat",
            "DaKiemDuyetNguonNghia",
            "GhiChu",
        ],
        missing_rows,
    )

    write_csv(
        SPECIAL_FILE,
        [
            "KyTu",
            "LoaiTruongHop",
            "PinyinNguon",
            "PinyinTuVung",
            "PinyinChuHanHienTai",
            "NghiaVietTuVung",
            "NghiaChuHanHienTai",
            "BaiXuatHienDau",
            "TuVungDauTien",
            "CanXuLy",
        ],
        special_rows,
    )

    write_csv(
        LESSON_SUMMARY_FILE,
        [
            "SoThuTuBai",
            "SoChuThieuNguonNghiaViet",
            "DanhSachChu",
        ],
        lesson_summary_rows,
    )

    print(
        "98 missing source:"
    )

    print(
        MISSING_FILE
    )

    print()
    print(
        "Special cases:"
    )

    print(
        SPECIAL_FILE
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
    print()
    print("=" * 120)
    print(
        "KET QUA 10K"
    )
    print("=" * 120)

    print(
        "Tong Chu Han:",
        len(rows),
    )

    print(
        "Chu co TuVung don da duyet:",
        len(with_single),
    )

    print(
        "Chu chua co TuVung don:",
        len(without_single),
    )

    print(
        "Tong ban ghi TuVung don:",
        total_single_rows,
    )

    print()
    print(
        "Chu co nhieu Pinyin "
        "trong Make Me a Hanzi:",
        len(multi_reading_rows),
    )

    print(
        "Chu co nhieu hon "
        "1 TuVung don:",
        len(multiple_vocab_rows),
    )

    print(
        "So ban ghi TuVung don "
        "du ra:",
        extra_rows,
    )

    print()
    print(
        "17 ChuHan Pinyin exact:",
        len(exact_existing),
        "/17",
    )

    print(
        "17 ChuHan can review Pinyin:",
        len(mismatch_existing),
        "/17",
    )

    print()
    print(
        "98 chu thieu nguon nghia Viet:",
        len(missing_rows),
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "FILE 10J KHONG BI SUA."
    )

    print(
        "CHUA TU DONG CHON PINYIN."
    )

    print(
        "CHUA TU DONG DICH NGHIA."
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
        "AUDIT NGUON CVDICT/CC-CEDICT "
        "CHO DUNG 98 CHU CON THIEU, "
        "DONG THOI XU LY CAC TRUONG HOP "
        "PINYIN DAC BIET."
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
            "10K THAT BAI"
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