from pathlib import Path
import csv
import sys
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
LESSON_NO = 2
EXPECTED_VOCAB_COUNT = 29

STANDARD_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "hsk1_48_grammar_standard.csv"
)

OUTPUT_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "lesson_context"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "hsk1_lesson2_grammar_context.csv"
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


def line():

    print("-" * 115)


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


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 115)
    print(
        "09H10 - CHUAN BI DU LIEU "
        "XAY NGU PHAP BAI 2 HSK1"
    )
    print("=" * 115)

    print()
    print("CHE DO:")
    print("  CHI DOC FILE NGU PHAP CHUAN")
    print("  CHI SELECT DATABASE")
    print("  TAO FILE CONTEXT CSV")
    print("  KHONG INSERT NGUPHAP")
    print("  KHONG UPDATE NGUPHAP")
    print("  KHONG DELETE")

    # =====================================================
    # 1. VERIFY 48 GRAMMAR STANDARD
    # =====================================================
    print()
    print("[1] VERIFY 48 MUC NGU PHAP CHUAN")
    line()

    if not STANDARD_FILE.exists():

        fail(
            "Khong tim thay file:\n"
            f"{STANDARD_FILE}"
        )

    standard_fields, standard_rows = load_csv(
        STANDARD_FILE
    )

    required_standard_fields = {
        "MaMucNguPhapChuan",
        "CapDoHSK",
        "SoThuTuChuan",
        "NhomLonTrung",
        "NhomConTrung",
        "TenMucTrung",
        "NoiDungChuanTrung",
        "MaNguon",
    }

    missing_fields = (
        required_standard_fields
        - set(standard_fields)
    )

    if missing_fields:

        fail(
            "File ngu phap chuan thieu cot: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    if len(standard_rows) != 48:

        fail(
            "File ngu phap chuan "
            "khong co dung 48 dong."
        )

    wrong_source = [
        row
        for row in standard_rows
        if clean(
            row["MaNguon"]
        ) != "1004"
    ]

    if wrong_source:

        fail(
            "Co muc ngu phap chuan "
            "khong MaNguon=1004."
        )

    print(
        "Tong muc:",
        len(standard_rows),
    )

    print(
        "MaNguon=1004:",
        48,
    )

    print(
        "NGU PHAP CHUAN: OK"
    )

    # =====================================================
    # 2. CONNECT DB
    # =====================================================
    print()
    print("[2] KET NOI DATABASE")
    line()

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
                        CONVERT(
                            nvarchar(128),
                            SERVERPROPERTY('ServerName')
                        ),
                        DB_NAME(),
                        SUSER_SNAME();
                    """
                )

                (
                    server_name,
                    database_name,
                    login_name,
                ) = cursor.fetchone()

                print(
                    "Server:",
                    server_name,
                )

                print(
                    "Database:",
                    database_name,
                )

                print(
                    "Tai khoan:",
                    login_name,
                )

                if (
                    clean(
                        database_name
                    ).lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi nham database."
                    )

                print(
                    "KET NOI DATABASE: OK"
                )

                # =========================================
                # 3. FIND LESSON 2
                # =========================================
                print()
                print(
                    "[3] TIM BAI 2"
                )
                line()

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
                        AND bh.SoThuTuBai = ?;
                    """,
                    COURSE_CODE,
                    LESSON_NO,
                )

                lesson_rows = (
                    cursor.fetchall()
                )

                if len(lesson_rows) != 1:

                    fail(
                        "Phai tim thay dung "
                        "1 Bai 2."
                    )

                lesson_id = int(
                    lesson_rows[0][0]
                )

                lesson_title = clean(
                    lesson_rows[0][2]
                )

                print(
                    "MaBaiHoc:",
                    lesson_id,
                )

                print(
                    "SoThuTuBai:",
                    LESSON_NO,
                )

                print(
                    "TieuDe:",
                    lesson_title,
                )

                # =========================================
                # 4. CHECK EXISTING GRAMMAR
                # =========================================
                print()
                print(
                    "[4] KIEM TRA NGU PHAP "
                    "BAI 2 HIEN TAI"
                )
                line()

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.NguPhap
                    WHERE MaBaiHoc = ?;
                    """,
                    lesson_id,
                )

                current_grammar_count = int(
                    cursor.fetchone()[0]
                )

                print(
                    "Ngu phap hien tai:",
                    current_grammar_count,
                )

                if current_grammar_count != 0:

                    fail(
                        "Bai 2 da co ngu phap. "
                        "Khong tiep tuc tao context "
                        "tren gia dinh rong."
                    )

                print(
                    "BAI 2 CHUA CO NGU PHAP: OK"
                )

                # =========================================
                # 5. READ VOCABULARY
                # =========================================
                print()
                print(
                    "[5] DOC TU VUNG BAI 2"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        tvbh.ThuTu,
                        tv.MaTuVung,
                        tv.ChuHan,
                        tv.PhienAm,
                        tv.NghiaTiengViet,
                        tv.TuLoai,
                        tv.MaNguon,
                        tv.DaDuyet
                    FROM dbo.TuVungBaiHoc AS tvbh
                    INNER JOIN dbo.TuVung AS tv
                        ON tvbh.MaTuVung
                        = tv.MaTuVung
                    WHERE
                        tvbh.MaBaiHoc = ?
                    ORDER BY
                        tvbh.ThuTu,
                        tv.MaTuVung;
                    """,
                    lesson_id,
                )

                vocab_rows = (
                    cursor.fetchall()
                )

                if (
                    len(vocab_rows)
                    != EXPECTED_VOCAB_COUNT
                ):

                    fail(
                        "Bai 2 phai co dung "
                        f"{EXPECTED_VOCAB_COUNT} tu. "
                        f"Thuc te: "
                        f"{len(vocab_rows)}"
                    )

                vocabulary = []

                for row in vocab_rows:

                    item = {
                        "ThuTu": int(
                            row[0]
                        ),
                        "MaTuVung": int(
                            row[1]
                        ),
                        "ChuHan": clean(
                            row[2]
                        ),
                        "PhienAm": clean(
                            row[3]
                        ),
                        "NghiaTiengViet": clean(
                            row[4]
                        ),
                        "TuLoai": clean(
                            row[5]
                        ),
                        "MaNguon": (
                            ""
                            if row[6] is None
                            else str(
                                int(row[6])
                            )
                        ),
                        "DaDuyet": (
                            1
                            if bool(row[7])
                            else 0
                        ),
                    }

                    vocabulary.append(
                        item
                    )

                # =========================================
                # VERIFY ORDER
                # =========================================
                orders = [
                    item["ThuTu"]
                    for item in vocabulary
                ]

                expected_orders = list(
                    range(
                        1,
                        EXPECTED_VOCAB_COUNT + 1,
                    )
                )

                if orders != expected_orders:

                    fail(
                        "ThuTu TuVungBaiHoc "
                        "khong lien tuc 1 -> 29."
                    )

                unapproved = [
                    item
                    for item in vocabulary
                    if item["DaDuyet"] != 1
                ]

                if unapproved:

                    fail(
                        "Bai 2 van co tu "
                        "chua DaDuyet=1."
                    )

                print(
                    "Tong tu:",
                    len(vocabulary),
                )

                print(
                    "ThuTu 1 -> 29: OK"
                )

                print(
                    "DaDuyet=1:",
                    len(vocabulary),
                )

                print()
                print(
                    "DANH SACH TU VUNG BAI 2"
                )
                print("-" * 115)

                for item in vocabulary:

                    print(
                        f"{item['ThuTu']:>2}. "
                        f"{item['ChuHan']:<8} | "
                        f"{item['PhienAm']:<20} | "
                        f"{item['TuLoai']:<15} | "
                        f"{item['NghiaTiengViet']}"
                    )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 6. CREATE CONTEXT FILE
    # =====================================================
    print()
    print("[6] TAO FILE CONTEXT")
    line()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "LoaiDong",
        "SoThuTuBai",
        "TieuDeBai",
        "ThuTu",
        "MaThamChieu",
        "NoiDungChinh",
        "PhienAmHoacNhom",
        "ThongTinBoSung",
        "MaNguon",
    ]

    output_rows = []

    # -----------------------------------------------------
    # VOCAB ROWS
    # -----------------------------------------------------
    for item in vocabulary:

        output_rows.append(
            {
                "LoaiDong": "tu_vung",
                "SoThuTuBai": LESSON_NO,
                "TieuDeBai": lesson_title,
                "ThuTu": item["ThuTu"],
                "MaThamChieu": (
                    item["MaTuVung"]
                ),
                "NoiDungChinh": (
                    item["ChuHan"]
                ),
                "PhienAmHoacNhom": (
                    item["PhienAm"]
                ),
                "ThongTinBoSung": (
                    f"{item['TuLoai']} | "
                    f"{item['NghiaTiengViet']}"
                ),
                "MaNguon": (
                    item["MaNguon"]
                ),
            }
        )

    # -----------------------------------------------------
    # 48 GRAMMAR STANDARD ROWS
    # -----------------------------------------------------
    for row in standard_rows:

        output_rows.append(
            {
                "LoaiDong": (
                    "ngu_phap_chuan"
                ),
                "SoThuTuBai": (
                    LESSON_NO
                ),
                "TieuDeBai": (
                    lesson_title
                ),
                "ThuTu": clean(
                    row[
                        "SoThuTuChuan"
                    ]
                ),
                "MaThamChieu": clean(
                    row[
                        "MaMucNguPhapChuan"
                    ]
                ),
                "NoiDungChinh": clean(
                    row[
                        "TenMucTrung"
                    ]
                ),
                "PhienAmHoacNhom": (
                    clean(
                        row[
                            "NhomLonTrung"
                        ]
                    )
                    + " / "
                    + clean(
                        row[
                            "NhomConTrung"
                        ]
                    )
                ),
                "ThongTinBoSung": clean(
                    row[
                        "NoiDungChuanTrung"
                    ]
                ),
                "MaNguon": (
                    clean(
                        row["MaNguon"]
                    )
                ),
            }
        )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            output_rows
        )

    # =====================================================
    # 7. VERIFY FILE
    # =====================================================
    print()
    print("[7] VERIFY FILE CONTEXT")
    line()

    _, verify_rows = load_csv(
        OUTPUT_FILE
    )

    vocab_context = [
        row
        for row in verify_rows
        if clean(
            row["LoaiDong"]
        ) == "tu_vung"
    ]

    grammar_context = [
        row
        for row in verify_rows
        if clean(
            row["LoaiDong"]
        ) == "ngu_phap_chuan"
    ]

    print(
        "Tong dong:",
        len(verify_rows),
    )

    print(
        "Dong tu_vung:",
        len(vocab_context),
    )

    print(
        "Dong ngu_phap_chuan:",
        len(grammar_context),
    )

    if len(vocab_context) != 29:

        fail(
            "Context khong co "
            "dung 29 dong tu vung."
        )

    if len(grammar_context) != 48:

        fail(
            "Context khong co "
            "dung 48 muc ngu phap."
        )

    if len(verify_rows) != 77:

        fail(
            "Tong context phai "
            "co 77 dong."
        )

    print(
        "VERIFY FILE: OK"
    )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 115)
    print(
        "KET QUA 09H10"
    )
    print("=" * 115)

    print(
        "Bai:",
        LESSON_NO,
        "-",
        lesson_title,
    )

    print(
        "Tu vung:",
        len(vocabulary),
    )

    print(
        "Ngu phap hien tai:",
        current_grammar_count,
    )

    print(
        "Muc ngu phap chuan tham chieu:",
        len(standard_rows),
    )

    print()
    print(
        "FILE CONTEXT:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA TAO NOI DUNG NGU PHAP BAI 2."
    )

    print(
        "CHUA INSERT dbo.NguPhap."
    )

    print()
    print(
        "BUOC TIEP THEO:"
    )

    print(
        "CHON CAC MUC GF1 PHU HOP "
        "VOI CHU DE + TU VUNG BAI 2, "
        "SAU DO MOI BIEN SOAN "
        "NOI DUNG HOC TAP."
    )

    print()
    print("=" * 115)
    print("HOAN TAT")
    print("=" * 115)


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 115)
        print(
            "09H10 THAT BAI"
        )
        print("=" * 115)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)