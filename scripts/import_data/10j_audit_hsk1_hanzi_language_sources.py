from pathlib import Path
import csv
import sys
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
COURSE_CODE = "HSK1-CORE"

EXPECTED_HANZI = 301
EXPECTED_EXISTING_HANZI = 17


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
    / "hsk1_301_hanzi_radical_mapped_review.csv"
)

OUTPUT_FILE = (
    REVIEW_DIR
    / "hsk1_301_hanzi_language_source_audit.csv"
)

ISSUES_FILE = (
    REVIEW_DIR
    / "hsk1_301_hanzi_language_source_issues.csv"
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
                "Khong doc duoc header."
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
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10J - AUDIT PINYIN VA NGUON "
        "NGHIA TIENG VIET CHO 301 CHU HAN"
    )
    print("=" * 120)

    print()
    print("MUC TIEU:")
    print("  KIEM TRA PINYIN MAKE ME A HANZI")
    print("  TIM TU VUNG DON TRUNG CHINH XAC VOI TUNG CHU")
    print("  KIEM TRA PINYIN + NGHIA VIET DA CO TRONG TuVung")
    print("  DOI CHIEU 17 ChuHan HIEN CO")
    print("  PHAT HIEN CHU CO NHIEU CACH DOC")
    print()
    print("CHE DO:")
    print("  CHI DOC FILE 10I")
    print("  CHI SELECT DATABASE")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")

    # =====================================================
    # 1. READ 10I
    # =====================================================
    print()
    print("[1] DOC FILE 10I")
    print("-" * 120)

    fields, rows = load_csv(
        INPUT_FILE
    )

    required = {
        "KyTu",
        "PhamVi",
        "BaiXuatHienDau",
        "MaBaiHoc",
        "TieuDeBai",
        "TuVungDauTien",
        "PinyinNguonRaw",
        "DefinitionEnglishNguon",
        "RadicalChuan",
        "MaBoThuChuan",
        "SoNetNguon",
        "KiemTraMappingBoThu",
        "DaCoTrongChuHan",
        "MaChuHanHienTai",
    }

    missing = (
        required
        - set(fields)
    )

    if missing:

        fail(
            "File 10I thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    if len(rows) != EXPECTED_HANZI:

        fail(
            "File 10I khong co "
            "dung 301 dong."
        )

    if any(
        clean(
            row["KiemTraMappingBoThu"]
        ) != "OK"
        for row in rows
    ):

        fail(
            "Van con Chu Han "
            "chua map BoThu."
        )

    characters = [
        clean(row["KyTu"])
        for row in rows
    ]

    if len(set(characters)) != 301:

        fail(
            "KyTu khong duy nhat."
        )

    print(
        "Tong Chu Han:",
        len(rows),
    )

    # =====================================================
    # 2. DATABASE
    # =====================================================
    print()
    print("[2] DOC DATABASE")
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
                        "Dang ket noi nham database."
                    )

                # =========================================
                # Tat ca TuVung co ChuHan trung dung 1 ky tu
                # =========================================
                cursor.execute(
                    """
                    SELECT
                        tv.MaTuVung,
                        tv.ChuHan,
                        tv.PhienAm,
                        tv.NghiaTiengViet,
                        tv.TuLoai,
                        tv.MaNguon,
                        tv.DaDuyet
                    FROM dbo.TuVung AS tv
                    WHERE LEN(tv.ChuHan) = 1
                    ORDER BY
                        tv.ChuHan,
                        tv.MaTuVung;
                    """
                )

                single_vocab_rows = (
                    cursor.fetchall()
                )

                single_vocab_map = defaultdict(
                    list
                )

                for row in single_vocab_rows:

                    char = clean(row[1])

                    if char not in set(characters):
                        continue

                    single_vocab_map[
                        char
                    ].append(
                        {
                            "MaTuVung": int(row[0]),
                            "ChuHan": char,
                            "PhienAm": clean(row[2]),
                            "NghiaTiengViet": clean(row[3]),
                            "TuLoai": clean(row[4]),
                            "MaNguon": clean(row[5]),
                            "DaDuyet": int(row[6]),
                        }
                    )

                # =========================================
                # 17 ChuHan hien co
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
                    != EXPECTED_EXISTING_HANZI
                ):

                    fail(
                        "ChuHan hien tai "
                        "khong con 17."
                    )

                current_map = {
                    clean(row[1]): {
                        "MaChuHan": int(row[0]),
                        "Pinyin": clean(row[2]),
                        "NghiaTiengViet": clean(row[3]),
                        "MaBoThu": row[4],
                        "SoNet": row[5],
                        "MaNguon": clean(row[6]),
                        "TrangThai": clean(row[7]),
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
        "TuVung don lien quan tim thay:",
        sum(
            len(items)
            for items
            in single_vocab_map.values()
        ),
    )

    print(
        "So Chu Han co it nhat "
        "1 TuVung don:",
        len(single_vocab_map),
    )

    # =====================================================
    # 3. AUDIT
    # =====================================================
    print()
    print(
        "[3] AUDIT 301 CHU"
    )
    print("-" * 120)

    output_rows = []
    issues = []

    with_single_vocab = 0
    with_approved_single_vocab = 0
    without_single_vocab = 0

    pinyin_source_ok = 0
    multiple_pinyin_source = 0

    existing_pinyin_match = 0
    existing_meaning_present = 0

    source_counter = Counter()

    for row in rows:

        char = clean(
            row["KyTu"]
        )

        source_pinyin = clean(
            row["PinyinNguonRaw"]
        )

        # -----------------------------------------
        # Pinyin source
        # -----------------------------------------
        if source_pinyin:

            pinyin_source_ok += 1

        else:

            issues.append(
                {
                    "KyTu": char,
                    "VanDe": (
                        "THIEU_PINYIN_NGUON"
                    ),
                    "ChiTiet": "",
                }
            )

        # normalize list marker created in 10G
        possible_readings = [
            clean(item)
            for item
            in source_pinyin.split("|")
            if clean(item)
        ]

        if (
            len(
                set(
                    possible_readings
                )
            )
            > 1
        ):

            multiple_pinyin_source += 1

            pinyin_type = (
                "NHIEU_CACH_DOC"
            )

        else:

            pinyin_type = (
                "MOT_CACH_DOC"
            )

        # -----------------------------------------
        # Exact single-character vocabulary
        # -----------------------------------------
        candidates = (
            single_vocab_map.get(
                char,
                [],
            )
        )

        approved = [
            item
            for item in candidates
            if item["DaDuyet"] == 1
        ]

        if candidates:

            with_single_vocab += 1

        else:

            without_single_vocab += 1

        if approved:

            with_approved_single_vocab += 1

        for item in approved:

            source_counter[
                str(
                    item["MaNguon"]
                )
            ] += 1

        # -----------------------------------------
        # Serialize candidates for review
        # -----------------------------------------
        candidate_ids = " | ".join(
            str(item["MaTuVung"])
            for item in candidates
        )

        candidate_pinyin = " | ".join(
            item["PhienAm"]
            for item in candidates
            if item["PhienAm"]
        )

        candidate_meanings = " || ".join(
            item["NghiaTiengViet"]
            for item in candidates
            if item["NghiaTiengViet"]
        )

        candidate_sources = " | ".join(
            str(item["MaNguon"])
            for item in candidates
        )

        approved_ids = " | ".join(
            str(item["MaTuVung"])
            for item in approved
        )

        approved_pinyin = " | ".join(
            item["PhienAm"]
            for item in approved
            if item["PhienAm"]
        )

        approved_meanings = " || ".join(
            item["NghiaTiengViet"]
            for item in approved
            if item["NghiaTiengViet"]
        )

        # -----------------------------------------
        # Existing ChuHan
        # -----------------------------------------
        current = (
            current_map.get(
                char
            )
        )

        current_pinyin = ""
        current_meaning = ""
        current_pinyin_check = ""

        if current:

            current_pinyin = (
                current["Pinyin"]
            )

            current_meaning = (
                current[
                    "NghiaTiengViet"
                ]
            )

            if current_meaning:

                existing_meaning_present += 1

            # Simple exact textual comparison only.
            # Khong sua tu dong neu format khac.
            source_reading_set = {
                item.lower()
                for item
                in possible_readings
            }

            if (
                current_pinyin.lower()
                in source_reading_set
            ):

                current_pinyin_check = (
                    "EXACT_MATCH"
                )

                existing_pinyin_match += 1

            else:

                current_pinyin_check = (
                    "CAN_REVIEW"
                )

        # -----------------------------------------
        # Determine available Vietnamese support
        # -----------------------------------------
        if approved:

            vietnamese_source_status = (
                "CO_TUVUNG_DON_DA_DUYET"
            )

        elif candidates:

            vietnamese_source_status = (
                "CHI_CO_TUVUNG_DON_CHUA_DUYET"
            )

        else:

            vietnamese_source_status = (
                "CHUA_CO_NGHIA_VIET_TU_TUVUNG_DON"
            )

        output_rows.append(
            {
                "KyTu": char,

                "PhamVi": clean(
                    row["PhamVi"]
                ),

                "BaiXuatHienDau": clean(
                    row[
                        "BaiXuatHienDau"
                    ]
                ),

                "TieuDeBai": clean(
                    row["TieuDeBai"]
                ),

                "TuVungDauTien": clean(
                    row[
                        "TuVungDauTien"
                    ]
                ),

                "PinyinNguonRaw": (
                    source_pinyin
                ),

                "LoaiPinyinNguon": (
                    pinyin_type
                ),

                "DefinitionEnglishNguon": clean(
                    row[
                        "DefinitionEnglishNguon"
                    ]
                ),

                "MaBoThuChuan": clean(
                    row[
                        "MaBoThuChuan"
                    ]
                ),

                "RadicalChuan": clean(
                    row[
                        "RadicalChuan"
                    ]
                ),

                "SoNetNguon": clean(
                    row[
                        "SoNetNguon"
                    ]
                ),

                "SoTuVungDonTimThay": (
                    len(candidates)
                ),

                "SoTuVungDonDaDuyet": (
                    len(approved)
                ),

                "MaTuVungDon": (
                    candidate_ids
                ),

                "PinyinTuVungDon": (
                    candidate_pinyin
                ),

                "NghiaVietTuVungDon": (
                    candidate_meanings
                ),

                "MaNguonTuVungDon": (
                    candidate_sources
                ),

                "MaTuVungDonDaDuyet": (
                    approved_ids
                ),

                "PinyinDaDuyet": (
                    approved_pinyin
                ),

                "NghiaVietDaDuyet": (
                    approved_meanings
                ),

                "TrangThaiNguonNghiaViet": (
                    vietnamese_source_status
                ),

                "DaCoTrongChuHan": (
                    1
                    if current
                    else 0
                ),

                "PinyinChuHanHienTai": (
                    current_pinyin
                ),

                "NghiaChuHanHienTai": (
                    current_meaning
                ),

                "KiemTraPinyinHienTai": (
                    current_pinyin_check
                ),

                # Chua chot noi dung.
                "PinyinChon": "",

                "NghiaTiengVietChon": "",

                "NguonNghiaTiengVietChon": "",

                "DaKiemDuyetNgonNgu": 0,

                "GhiChuKiemDuyet": "",
            }
        )

    # =====================================================
    # 4. WRITE
    # =====================================================
    print()
    print(
        "[4] GHI FILE AUDIT"
    )
    print("-" * 120)

    write_csv(
        OUTPUT_FILE,
        [
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
            "PinyinChon",
            "NghiaTiengVietChon",
            "NguonNghiaTiengVietChon",
            "DaKiemDuyetNgonNgu",
            "GhiChuKiemDuyet",
        ],
        output_rows,
    )

    write_csv(
        ISSUES_FILE,
        [
            "KyTu",
            "VanDe",
            "ChiTiet",
        ],
        issues,
    )

    print(
        "Language audit:"
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

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 10J"
    )
    print("=" * 120)

    print(
        "Tong Chu Han:",
        len(output_rows),
    )

    print(
        "Co Pinyin Make Me a Hanzi:",
        pinyin_source_ok,
        "/301",
    )

    print(
        "Chu co nhieu cach doc "
        "trong nguon:",
        multiple_pinyin_source,
    )

    print()
    print(
        "Chu co TuVung don "
        "trong database:",
        with_single_vocab,
        "/301",
    )

    print(
        "Chu co TuVung don DaDuyet=1:",
        with_approved_single_vocab,
        "/301",
    )

    print(
        "Chu khong co TuVung don:",
        without_single_vocab,
        "/301",
    )

    print()
    print(
        "Nguon cua cac TuVung don "
        "da duyet:"
    )

    if source_counter:

        for source_id, count in sorted(
            source_counter.items()
        ):

            print(
                f"  MaNguon={source_id}: "
                f"{count}"
            )

    else:

        print(
            "  <KHONG CO>"
        )

    print()
    print(
        "17 ChuHan hien co "
        "Pinyin exact-match nguon:",
        existing_pinyin_match,
        "/17",
    )

    print(
        "17 ChuHan hien co "
        "co nghia Viet:",
        existing_meaning_present,
        "/17",
    )

    print(
        "Tong issue ky thuat:",
        len(issues),
    )

    print()
    print(
        "DaKiemDuyetNgonNgu=1:",
        0,
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA TU DONG DICH "
        "DefinitionEnglishNguon."
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
        "DUA VAO COVERAGE TUVUNG DON "
        "DE QUYET DINH NGUON NGHIA VIET "
        "CHO CAC CHU CON THIEU."
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
            "10J THAT BAI"
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