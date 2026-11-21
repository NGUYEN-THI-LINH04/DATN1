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

EXPECTED_VOCAB = 501
EXPECTED_CANDIDATES = 301
EXPECTED_EXISTING = 17
EXPECTED_MISSING = 284


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

OUTPUT_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
    / "hsk1_hanzi_priority_review.csv"
)

SUMMARY_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
    / "hsk1_hanzi_priority_summary.csv"
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
        "10D - XEP NHOM UU TIEN "
        "301 CHU HAN HSK1"
    )
    print("=" * 120)

    print()
    print("MUC DICH:")
    print("  KHONG TU DONG CHON 301 CHU DE DAY")
    print("  CHI XEP NHOM UU TIEN DE REVIEW")
    print()
    print("NGUYEN TAC:")
    print("  HIEN_CO : 17 chu dang co trong SQL -> giu nguyen")
    print("  NHOM_A  : chu co gia tri hoc tap cao")
    print("  NHOM_B  : muc uu tien trung binh")
    print("  NHOM_C  : chu chi xuat hien han che")
    print()
    print("DATABASE:")
    print("  CHI SELECT")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")

    # =====================================================
    # 1. FILE
    # =====================================================
    print()
    print("[1] DOC FILE 10B")
    print("-" * 120)

    if not CANDIDATE_FILE.exists():

        fail(
            "Khong tim thay:\n"
            f"{CANDIDATE_FILE}"
        )

    fields, candidates = load_csv(
        CANDIDATE_FILE
    )

    if len(candidates) != EXPECTED_CANDIDATES:

        fail(
            "Candidate file phai co "
            f"{EXPECTED_CANDIDATES} dong."
        )

    required_fields = {
        "KyTu",
        "BaiXuatHienDau",
        "MaBaiHocDauTien",
        "TieuDeBaiDauTien",
        "TuVungDauTien",
        "SoTuVungChuaChu",
        "TongLanXuatHien",
        "TrangThaiDoiChieu",
        "MaChuHanHienTai",
    }

    missing = (
        required_fields
        - set(fields)
    )

    if missing:

        fail(
            "File 10B thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    chars = [
        clean(row["KyTu"])
        for row in candidates
    ]

    if len(set(chars)) != 301:

        fail(
            "KyTu trong file 10B "
            "khong duy nhat."
        )

    print(
        "Tong candidate:",
        len(candidates),
    )

    # =====================================================
    # 2. DATABASE
    # =====================================================
    print()
    print("[2] DOC 501 TU VUNG + 23 BAI")
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
                    WHERE kh.MaKyHieu = ?
                    ORDER BY bh.SoThuTuBai;
                    """,
                    COURSE_CODE,
                )

                lesson_rows = (
                    cursor.fetchall()
                )

                if len(lesson_rows) != 23:

                    fail(
                        "Khong co du 23 bai."
                    )

                lesson_map = {
                    int(row[1]): {
                        "MaBaiHoc": int(row[0]),
                        "TieuDe": clean(row[2]),
                    }
                    for row in lesson_rows
                }

                # -----------------------------------------
                # Vocabulary
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        bh.SoThuTuBai,
                        tv.MaTuVung,
                        tv.ChuHan,
                        tv.PhienAm,
                        tv.NghiaTiengViet
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
                    WHERE kh.MaKyHieu = ?
                    ORDER BY
                        bh.SoThuTuBai,
                        tvbh.ThuTu;
                    """,
                    COURSE_CODE,
                )

                vocab_rows = (
                    cursor.fetchall()
                )

                if len(vocab_rows) != EXPECTED_VOCAB:

                    fail(
                        "Khong co dung "
                        "501 tu vung."
                    )

                # -----------------------------------------
                # Current Hanzi
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        ch.KyTu,
                        ch.MaChuHan,
                        bh.SoThuTuBai
                    FROM dbo.ChuHan AS ch
                    INNER JOIN dbo.BaiHoc AS bh
                        ON ch.MaBaiHoc
                        = bh.MaBaiHoc
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc
                    WHERE kh.MaKyHieu = ?;
                    """,
                    COURSE_CODE,
                )

                current_hanzi_rows = (
                    cursor.fetchall()
                )

                if (
                    len(current_hanzi_rows)
                    != EXPECTED_EXISTING
                ):

                    fail(
                        "ChuHan hien tai "
                        "khong con 17."
                    )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 3. BUILD VOCAB INDEX
    # =====================================================
    print()
    print(
        "[3] PHAN TICH NGU CANH HOC TAP"
    )
    print("-" * 120)

    single_character_words = set()

    word_count_by_char = defaultdict(
        set
    )

    occurrence_count_by_char = Counter()

    lesson_occurrence_by_char = defaultdict(
        set
    )

    for row in vocab_rows:

        lesson_no = int(row[0])
        vocab_id = int(row[1])
        word = clean(row[2])

        if len(word) == 1:

            single_character_words.add(
                word
            )

        for char in word:

            if char in chars:

                word_count_by_char[
                    char
                ].add(
                    vocab_id
                )

                occurrence_count_by_char[
                    char
                ] += 1

                lesson_occurrence_by_char[
                    char
                ].add(
                    lesson_no
                )

    print(
        "Chu dong thoi la tu don:",
        len(
            single_character_words
            & set(chars)
        ),
    )

    # =====================================================
    # 4. PRIORITY
    # =====================================================
    print()
    print(
        "[4] XEP NHOM UU TIEN"
    )
    print("-" * 120)

    output_rows = []

    priority_counts = Counter()

    lesson_priority_counts = defaultdict(
        Counter
    )

    existing_count = 0
    missing_count = 0

    for row in candidates:

        char = clean(
            row["KyTu"]
        )

        lesson_no = int(
            clean(
                row[
                    "BaiXuatHienDau"
                ]
            )
        )

        lesson_title = (
            lesson_map[
                lesson_no
            ][
                "TieuDe"
            ]
        )

        status = clean(
            row[
                "TrangThaiDoiChieu"
            ]
        )

        distinct_words = len(
            word_count_by_char[
                char
            ]
        )

        occurrences = (
            occurrence_count_by_char[
                char
            ]
        )

        lesson_occurrences = len(
            lesson_occurrence_by_char[
                char
            ]
        )

        is_single_word = (
            1
            if char in single_character_words
            else 0
        )

        appears_in_title = (
            1
            if char in lesson_title
            else 0
        )

        # ================================================
        # Day chi la DIEM REVIEW,
        # khong phai diem nguon chinh thuc.
        # ================================================
        score = 0

        if is_single_word:
            score += 100

        if appears_in_title:
            score += 60

        score += (
            distinct_words * 10
        )

        score += min(
            occurrences,
            20,
        )

        score += (
            lesson_occurrences * 3
        )

        # -----------------------------------------------
        # Existing 17 are retained
        # -----------------------------------------------
        if (
            status
            == "DA_CO_DUNG_BAI"
        ):

            priority = "HIEN_CO"

            existing_count += 1

        else:

            missing_count += 1

            # -------------------------------------------
            # A:
            # - la tu don
            # - hoac nam trong tieu de bai
            # - hoac xuat hien trong >= 3 tu khac nhau
            # -------------------------------------------
            if (
                is_single_word == 1
                or appears_in_title == 1
                or distinct_words >= 3
            ):

                priority = "NHOM_A"

            # -------------------------------------------
            # B:
            # xuat hien trong 2 tu vung
            # -------------------------------------------
            elif distinct_words == 2:

                priority = "NHOM_B"

            # -------------------------------------------
            # C:
            # chi xuat hien trong 1 tu
            # -------------------------------------------
            else:

                priority = "NHOM_C"

        priority_counts[
            priority
        ] += 1

        lesson_priority_counts[
            lesson_no
        ][
            priority
        ] += 1

        reasons = []

        if status == "DA_CO_DUNG_BAI":

            reasons.append(
                "Đã tồn tại đúng bài trong SQL"
            )

        if is_single_word:

            reasons.append(
                "Bản thân chữ là một từ vựng HSK1"
            )

        if appears_in_title:

            reasons.append(
                "Xuất hiện trong tiêu đề bài"
            )

        if distinct_words >= 3:

            reasons.append(
                (
                    f"Xuất hiện trong "
                    f"{distinct_words} từ HSK1"
                )
            )

        elif distinct_words == 2:

            reasons.append(
                "Xuất hiện trong 2 từ HSK1"
            )

        else:

            reasons.append(
                "Chỉ xuất hiện trong 1 từ HSK1"
            )

        output_rows.append(
            {
                "KyTu": char,

                "BaiXuatHienDau": (
                    lesson_no
                ),

                "MaBaiHocDauTien": clean(
                    row[
                        "MaBaiHocDauTien"
                    ]
                ),

                "TieuDeBaiDauTien": (
                    lesson_title
                ),

                "TuVungDauTien": clean(
                    row[
                        "TuVungDauTien"
                    ]
                ),

                "SoTuVungChuaChu": (
                    distinct_words
                ),

                "TongLanXuatHien": (
                    occurrences
                ),

                "SoBaiCoXuatHien": (
                    lesson_occurrences
                ),

                "LaTuDonHSK1": (
                    is_single_word
                ),

                "XuatHienTrongTieuDeBai": (
                    appears_in_title
                ),

                "TrangThaiDoiChieu": (
                    status
                ),

                "MaChuHanHienTai": clean(
                    row[
                        "MaChuHanHienTai"
                    ]
                ),

                "DiemUuTienReview": (
                    score
                ),

                "NhomUuTien": (
                    priority
                ),

                "LyDoXepNhom": (
                    "; ".join(
                        reasons
                    )
                ),

                # Chua phe duyet.
                "QuyetDinhCuoi": "",

                "DaKiemDuyetPhamVi": 0,

                "GhiChuKiemDuyet": "",
            }
        )

    if existing_count != 17:

        fail(
            "So HIEN_CO khong bang 17."
        )

    if missing_count != 284:

        fail(
            "So chu chua co "
            "khong bang 284."
        )

    # =====================================================
    # 5. SORT
    # =====================================================
    priority_order = {
        "HIEN_CO": 0,
        "NHOM_A": 1,
        "NHOM_B": 2,
        "NHOM_C": 3,
    }

    output_rows.sort(
        key=lambda row: (
            int(
                row[
                    "BaiXuatHienDau"
                ]
            ),
            priority_order[
                row[
                    "NhomUuTien"
                ]
            ],
            -int(
                row[
                    "DiemUuTienReview"
                ]
            ),
            row["KyTu"],
        )
    )

    # =====================================================
    # 6. SUMMARY
    # =====================================================
    print()
    print(
        "[5] THONG KE 23 BAI"
    )
    print("-" * 120)

    summary_rows = []

    for lesson_no in range(
        1,
        24,
    ):

        counts = (
            lesson_priority_counts[
                lesson_no
            ]
        )

        total = sum(
            counts.values()
        )

        summary_rows.append(
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
                    lesson_map[
                        lesson_no
                    ][
                        "TieuDe"
                    ]
                ),

                "TongChuUngVien": (
                    total
                ),

                "HienCo": (
                    counts[
                        "HIEN_CO"
                    ]
                ),

                "NhomA": (
                    counts[
                        "NHOM_A"
                    ]
                ),

                "NhomB": (
                    counts[
                        "NHOM_B"
                    ]
                ),

                "NhomC": (
                    counts[
                        "NHOM_C"
                    ]
                ),

                "TongTrongTamTamThoi": (
                    counts[
                        "HIEN_CO"
                    ]
                    +
                    counts[
                        "NHOM_A"
                    ]
                ),
            }
        )

        print(
            f"Bai {lesson_no:>2} | "
            f"Tong={total:>2} | "
            f"HienCo="
            f"{counts['HIEN_CO']:>2} | "
            f"A={counts['NHOM_A']:>2} | "
            f"B={counts['NHOM_B']:>2} | "
            f"C={counts['NHOM_C']:>2} | "
            f"Tam thoi trong tam="
            f"{counts['HIEN_CO'] + counts['NHOM_A']:>2}"
        )

    # =====================================================
    # 7. WRITE
    # =====================================================
    print()
    print(
        "[6] GHI FILE REVIEW"
    )
    print("-" * 120)

    write_csv(
        OUTPUT_FILE,
        [
            "KyTu",
            "BaiXuatHienDau",
            "MaBaiHocDauTien",
            "TieuDeBaiDauTien",
            "TuVungDauTien",
            "SoTuVungChuaChu",
            "TongLanXuatHien",
            "SoBaiCoXuatHien",
            "LaTuDonHSK1",
            "XuatHienTrongTieuDeBai",
            "TrangThaiDoiChieu",
            "MaChuHanHienTai",
            "DiemUuTienReview",
            "NhomUuTien",
            "LyDoXepNhom",
            "QuyetDinhCuoi",
            "DaKiemDuyetPhamVi",
            "GhiChuKiemDuyet",
        ],
        output_rows,
    )

    write_csv(
        SUMMARY_FILE,
        [
            "SoThuTuBai",
            "MaBaiHoc",
            "TieuDeBai",
            "TongChuUngVien",
            "HienCo",
            "NhomA",
            "NhomB",
            "NhomC",
            "TongTrongTamTamThoi",
        ],
        summary_rows,
    )

    print(
        "Priority review:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "Summary:"
    )

    print(
        SUMMARY_FILE
    )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 10D"
    )
    print("=" * 120)

    print(
        "Tong ung vien:",
        len(output_rows),
    )

    print(
        "HIEN_CO:",
        priority_counts[
            "HIEN_CO"
        ],
    )

    print(
        "NHOM_A:",
        priority_counts[
            "NHOM_A"
        ],
    )

    print(
        "NHOM_B:",
        priority_counts[
            "NHOM_B"
        ],
    )

    print(
        "NHOM_C:",
        priority_counts[
            "NHOM_C"
        ],
    )

    print()

    print(
        "Tong tam thoi neu giu "
        "HIEN_CO + NHOM_A:",
        (
            priority_counts[
                "HIEN_CO"
            ]
            +
            priority_counts[
                "NHOM_A"
            ]
        ),
    )

    print()
    print(
        "LUU Y:"
    )

    print(
        "NHOM_A/B/C CHI LA "
        "PHAN LOAI UU TIEN DE REVIEW."
    )

    print(
        "CHUA CO CHU NAO DUOC "
        "TU DONG PHE DUYET HOAC LOAI."
    )

    print()
    print(
        "DaKiemDuyetPhamVi=1:",
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
            "10D THAT BAI"
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