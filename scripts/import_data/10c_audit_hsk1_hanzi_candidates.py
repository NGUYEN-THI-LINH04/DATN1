from pathlib import Path
import csv
import sys
from collections import Counter, defaultdict
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

EXPECTED_LESSONS = 23
EXPECTED_VOCAB = 501
EXPECTED_UNIQUE_HANZI = 301
EXPECTED_EXISTING_HANZI = 17
EXPECTED_MISSING_HANZI = 284


# =========================================================
# FILES
# =========================================================
CANDIDATE_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
    / "hsk1_hanzi_candidate_review.csv"
)

SUMMARY_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
    / "hsk1_hanzi_candidate_summary.csv"
)

AUDIT_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
    / "hsk1_hanzi_candidate_audit.csv"
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

        return reader.fieldnames, list(reader)


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
        "10C - AUDIT 301 UNG VIEN CHU HAN HSK1"
    )
    print("=" * 120)

    print()
    print("CHE DO:")
    print("  DOC FILE 10B")
    print("  DOI CHIEU DATABASE")
    print("  THONG KE SO CHU TUNG BAI")
    print("  KIEM TRA 17 CHU HIEN CO")
    print("  KIEM TRA 284 CHU CHUA CO")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")

    # =====================================================
    # 1. VERIFY FILES
    # =====================================================
    print()
    print("[1] VERIFY FILE 10B")
    print("-" * 120)

    for path in [
        CANDIDATE_FILE,
        SUMMARY_FILE,
    ]:

        if not path.exists():

            fail(
                "Khong tim thay file:\n"
                f"{path}"
            )

        print(
            "OK:",
            path,
        )

    # =====================================================
    # 2. READ CANDIDATES
    # =====================================================
    print()
    print("[2] DOC 301 UNG VIEN")
    print("-" * 120)

    fields, rows = load_csv(
        CANDIDATE_FILE
    )

    required_fields = {
        "KyTu",
        "BaiXuatHienDau",
        "MaBaiHocDauTien",
        "TieuDeBaiDauTien",
        "ThuTuTuVungDauTien",
        "ViTriTrongTuDauTien",
        "MaTuVungDauTien",
        "TuVungDauTien",
        "PinyinTuDauTien",
        "NghiaTuDauTien",
        "SoTuVungChuaChu",
        "TongLanXuatHien",
        "CacTuVungChuaChu",
        "TrangThaiDoiChieu",
        "MaChuHanHienTai",
        "BaiHienTai",
        "DaKiemDuyetUngVien",
    }

    missing_fields = (
        required_fields
        - set(fields)
    )

    if missing_fields:

        fail(
            "Candidate file thieu cot: "
            + ", ".join(
                sorted(
                    missing_fields
                )
            )
        )

    if len(rows) != EXPECTED_UNIQUE_HANZI:

        fail(
            "Candidate file phai co "
            "301 dong. "
            f"Thuc te: {len(rows)}"
        )

    characters = [
        clean(
            row["KyTu"]
        )
        for row in rows
    ]

    if len(set(characters)) != 301:

        fail(
            "301 dong nhung KyTu "
            "khong duy nhat."
        )

    print(
        "Tong ung vien:",
        len(rows),
    )

    print(
        "KyTu duy nhat:",
        len(
            set(characters)
        ),
    )

    # =====================================================
    # 3. STATUS COUNTS
    # =====================================================
    print()
    print(
        "[3] KIEM TRA TRANG THAI DOI CHIEU"
    )
    print("-" * 120)

    status_counts = Counter(
        clean(
            row[
                "TrangThaiDoiChieu"
            ]
        )
        for row in rows
    )

    for status, count in sorted(
        status_counts.items()
    ):

        print(
            f"{status}: {count}"
        )

    if (
        status_counts[
            "DA_CO_DUNG_BAI"
        ]
        != EXPECTED_EXISTING_HANZI
    ):

        fail(
            "DA_CO_DUNG_BAI "
            "khong bang 17."
        )

    if (
        status_counts[
            "CHUA_CO_TRONG_CHUHAN"
        ]
        != EXPECTED_MISSING_HANZI
    ):

        fail(
            "CHUA_CO_TRONG_CHUHAN "
            "khong bang 284."
        )

    if (
        status_counts[
            "DA_CO_KHAC_BAI"
        ]
        != 0
    ):

        fail(
            "Co ChuHan dang nam sai bai."
        )

    if (
        status_counts[
            "TRUNG_KYTU_TRONG_CHUHAN"
        ]
        != 0
    ):

        fail(
            "Co KyTu bi trung "
            "trong dbo.ChuHan."
        )

    print(
        "TRANG THAI DOI CHIEU: OK"
    )

    # =====================================================
    # 4. FIRST APPEARANCE COUNTS
    # =====================================================
    print()
    print(
        "[4] THONG KE CHU XUAT HIEN DAU "
        "THEO 23 BAI"
    )
    print("-" * 120)

    lesson_counts = Counter()

    existing_counts = Counter()

    missing_counts = Counter()

    for row in rows:

        lesson_no = int(
            clean(
                row[
                    "BaiXuatHienDau"
                ]
            )
        )

        if (
            lesson_no < 1
            or lesson_no > 23
        ):

            fail(
                f"KyTu {row['KyTu']} "
                f"co BaiXuatHienDau "
                f"khong hop le: "
                f"{lesson_no}"
            )

        lesson_counts[
            lesson_no
        ] += 1

        status = clean(
            row[
                "TrangThaiDoiChieu"
            ]
        )

        if (
            status
            == "DA_CO_DUNG_BAI"
        ):

            existing_counts[
                lesson_no
            ] += 1

        elif (
            status
            == "CHUA_CO_TRONG_CHUHAN"
        ):

            missing_counts[
                lesson_no
            ] += 1

    if (
        sum(
            lesson_counts.values()
        )
        != 301
    ):

        fail(
            "Tong phan bo theo bai "
            "khong bang 301."
        )

    if (
        sum(
            missing_counts.values()
        )
        != 284
    ):

        fail(
            "Tong chu thieu "
            "khong bang 284."
        )

    # =====================================================
    # 5. DATABASE AUDIT
    # =====================================================
    print()
    print(
        "[5] DOI CHIEU DATABASE HIEN TAI"
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
                        DB_NAME()
                    """
                )

                database_name = clean(
                    cursor.fetchone()[0]
                )

                if (
                    database_name.lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi "
                        "nham database."
                    )

                # -----------------------------------------
                # Lessons
                # -----------------------------------------
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

                if len(
                    lesson_rows
                ) != EXPECTED_LESSONS:

                    fail(
                        "Database khong co "
                        "du 23 bai."
                    )

                lesson_map = {
                    int(
                        row[1]
                    ): {
                        "MaBaiHoc": (
                            int(
                                row[0]
                            )
                        ),
                        "TieuDe": (
                            clean(
                                row[2]
                            )
                        ),
                    }
                    for row in lesson_rows
                }

                # -----------------------------------------
                # Current Hanzi
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        ch.MaChuHan,
                        ch.KyTu,
                        bh.SoThuTuBai,
                        ch.ThuTu,
                        ch.Pinyin,
                        ch.NghiaTiengViet,
                        ch.MaBoThu,
                        ch.SoNet,
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

                print(
                    "ChuHan trong DB:",
                    len(
                        current_rows
                    ),
                )

                if (
                    len(
                        current_rows
                    )
                    != 17
                ):

                    fail(
                        "Database khong con "
                        "dung 17 ChuHan."
                    )

                current_chars = {
                    clean(
                        row[1]
                    )
                    for row in current_rows
                }

                expected_existing_chars = {
                    clean(
                        row[
                            "KyTu"
                        ]
                    )
                    for row in rows
                    if clean(
                        row[
                            "TrangThaiDoiChieu"
                        ]
                    )
                    == "DA_CO_DUNG_BAI"
                }

                if (
                    current_chars
                    != expected_existing_chars
                ):

                    fail(
                        "17 KyTu trong SQL "
                        "khong khop file 10B."
                    )

                print(
                    "17/17 CHU HIEN CO: OK"
                )

                # -----------------------------------------
                # BoThu
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.BoThu;
                    """
                )

                radical_count = int(
                    cursor.fetchone()[0]
                )

                print(
                    "BoThu:",
                    radical_count,
                )

                if radical_count != 214:

                    fail(
                        "BoThu khong con "
                        "dung 214."
                    )

                # -----------------------------------------
                # NetChuHan
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.NetChuHan;
                    """
                )

                stroke_rows = int(
                    cursor.fetchone()[0]
                )

                print(
                    "NetChuHan hien tai:",
                    stroke_rows,
                )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 6. BUILD AUDIT TABLE
    # =====================================================
    print()
    print(
        "[6] TAO BANG AUDIT 23 BAI"
    )
    print("-" * 120)

    audit_rows = []

    high_load_lessons = []

    for lesson_no in range(
        1,
        24,
    ):

        total_new = (
            lesson_counts.get(
                lesson_no,
                0,
            )
        )

        existing = (
            existing_counts.get(
                lesson_no,
                0,
            )
        )

        missing = (
            missing_counts.get(
                lesson_no,
                0,
            )
        )

        # Chi la canh bao tai hoc,
        # KHONG phai tu dong loai bo.
        if total_new <= 12:

            load_level = "NHE"

        elif total_new <= 16:

            load_level = "VUA"

        elif total_new <= 20:

            load_level = "CAO"

        else:

            load_level = (
                "RAT_CAO"
            )

            high_load_lessons.append(
                lesson_no
            )

        lesson_title = (
            lesson_map[
                lesson_no
            ][
                "TieuDe"
            ]
        )

        audit_rows.append(
            {
                "SoThuTuBai": (
                    lesson_no
                ),

                "MaBaiHoc": (
                    lesson_map[
                        lesson_no
                    ][
                        "MaBaiHoc"
                    ]
                ),

                "TieuDeBai": (
                    lesson_title
                ),

                "SoChuXuatHienDau": (
                    total_new
                ),

                "SoChuDaCoDungBai": (
                    existing
                ),

                "SoChuChuaCo": (
                    missing
                ),

                "MucTaiChuHan": (
                    load_level
                ),

                "CanKiemTraPhanBo": (
                    1
                    if load_level
                    in {
                        "CAO",
                        "RAT_CAO",
                    }
                    else 0
                ),
            }
        )

        print(
            f"Bai {lesson_no:>2} | "
            f"Chu moi={total_new:>2} | "
            f"Da co={existing:>2} | "
            f"Chua co={missing:>2} | "
            f"{load_level}"
        )

    write_csv(
        AUDIT_FILE,
        [
            "SoThuTuBai",
            "MaBaiHoc",
            "TieuDeBai",
            "SoChuXuatHienDau",
            "SoChuDaCoDungBai",
            "SoChuChuaCo",
            "MucTaiChuHan",
            "CanKiemTraPhanBo",
        ],
        audit_rows,
    )

    # =====================================================
    # 7. MORE CANDIDATE CHECKS
    # =====================================================
    print()
    print(
        "[7] KIEM TRA CHAT LUONG UNG VIEN"
    )
    print("-" * 120)

    blank_first_word = []

    blank_pinyin_word = []

    blank_meaning_word = []

    no_occurrence = []

    for row in rows:

        char = clean(
            row[
                "KyTu"
            ]
        )

        if not clean(
            row[
                "TuVungDauTien"
            ]
        ):

            blank_first_word.append(
                char
            )

        if not clean(
            row[
                "PinyinTuDauTien"
            ]
        ):

            blank_pinyin_word.append(
                char
            )

        if not clean(
            row[
                "NghiaTuDauTien"
            ]
        ):

            blank_meaning_word.append(
                char
            )

        try:

            occurrences = int(
                clean(
                    row[
                        "TongLanXuatHien"
                    ]
                )
            )

        except Exception:

            occurrences = 0

        if occurrences <= 0:

            no_occurrence.append(
                char
            )

    print(
        "Thieu TuVungDauTien:",
        len(
            blank_first_word
        ),
    )

    print(
        "Thieu PinyinTuDauTien:",
        len(
            blank_pinyin_word
        ),
    )

    print(
        "Thieu NghiaTuDauTien:",
        len(
            blank_meaning_word
        ),
    )

    print(
        "TongLanXuatHien <= 0:",
        len(
            no_occurrence
        ),
    )

    if (
        blank_first_word
        or blank_pinyin_word
        or blank_meaning_word
        or no_occurrence
    ):

        fail(
            "Candidate file co "
            "du lieu ngu canh bi thieu."
        )

    print(
        "301/301 UNG VIEN "
        "CO NGU CANH TU VUNG: OK"
    )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 10C"
    )
    print("=" * 120)

    print(
        "Tong Chu Han khac nhau:",
        301,
    )

    print(
        "Da co dung bai:",
        17,
    )

    print(
        "Chua co trong dbo.ChuHan:",
        284,
    )

    print(
        "Da co khac bai:",
        0,
    )

    print(
        "KyTu bi trung:",
        0,
    )

    print(
        "BoThu hien co:",
        214,
    )

    print()
    print(
        "FILE AUDIT:"
    )

    print(
        AUDIT_FILE
    )

    print()
    print(
        "CAC BAI CO >20 CHU XUAT HIEN DAU:"
    )

    if high_load_lessons:

        print(
            ", ".join(
                str(x)
                for x in high_load_lessons
            )
        )

    else:

        print(
            "KHONG CO"
        )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA QUYET DINH "
        "301 CHU DEU LA NOI DUNG "
        "BAT BUOC PHAI DAY."
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
        "DUA VAO PHAN BO THUC TE "
        "DE CHOT PHAM VI CHU HAN HSK1, "
        "SAU DO MOI LAY DU LIEU "
        "UNICODE / MAKE ME A HANZI."
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
            "10C THAT BAI"
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