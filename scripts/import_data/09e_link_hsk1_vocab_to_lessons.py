from pathlib import Path
import csv
import sys
from collections import Counter, defaultdict


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# CAU HINH
# =========================================================
COURSE_CODE = "HSK1-CORE"
HSK_LEVEL = 1

ALLOCATION_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hsk1_500_phan_bo_23_bai.csv"
)

EXPECTED_WORDS = 500
EXPECTED_LESSONS = 23
EXPECTED_EXISTING_LINKS = 13
EXPECTED_NEW_LINKS = 487
EXPECTED_FINAL_LINKS = 500

# So tu trong tung bai theo file phan bo da chot.
EXPECTED_COUNTS = {
    1: 13,
    2: 28,
    3: 23,
    4: 26,
    5: 20,
    6: 24,
    7: 28,
    8: 25,
    9: 22,
    10: 24,
    11: 23,
    12: 22,
    13: 30,
    14: 22,
    15: 11,
    16: 12,
    17: 25,
    18: 22,
    19: 23,
    20: 23,
    21: 20,
    22: 18,
    23: 16,
}

REQUIRED_CSV_COLUMNS = {
    "MaTuHSK",
    "MaMucNoiBo",
    "ChuHan",
    "PhienAm",
    "DaDungTrongBai1",
    "BaiDeXuat",
    "TieuDeBaiTrung",
    "TieuDeBaiViet",
}


# =========================================================
# HELPERS
# =========================================================
def clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def make_key(chinese, pinyin):
    return (
        clean_text(chinese),
        clean_text(pinyin).lower(),
    )


def get_columns(cursor, table_name):
    cursor.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = ?
        """,
        table_name,
    )

    return {
        row.COLUMN_NAME
        for row in cursor.fetchall()
    }


def check_schema(cursor):
    required = {
        "KhoaHoc": {
            "MaKhoaHoc",
            "MaCapDo",
            "MaKyHieu",
            "TieuDe",
            "TrangThai",
        },
        "BaiHoc": {
            "MaBaiHoc",
            "MaKhoaHoc",
            "SoThuTuBai",
            "TieuDe",
            "TrangThai",
        },
        "TuVungHSKChuan": {
            "MaTuHSK",
            "MaCapDo",
            "ChuHan",
            "PhienAm",
        },
        "TuVung": {
            "MaTuVung",
            "ChuHan",
            "PhienAm",
            "MaNguon",
            "DaDuyet",
        },
        "TuVungBaiHoc": {
            "MaBaiHoc",
            "MaTuVung",
            "ThuTu",
        },
    }

    print()
    print("Kiem tra schema live DB:")

    for table_name, required_columns in required.items():
        actual = get_columns(cursor, table_name)
        missing = required_columns - actual

        if missing:
            raise RuntimeError(
                f"Bang {table_name} thieu cot: "
                + ", ".join(sorted(missing))
            )

        print(f"  {table_name:<18}: OK")


def load_allocation_file():
    if not ALLOCATION_FILE.exists():
        raise RuntimeError(
            "Khong tim thay file phan bo:\n"
            f"{ALLOCATION_FILE}\n"
            "Hay dat file hsk1_500_phan_bo_23_bai.csv vao dung thu muc."
        )

    with open(
        ALLOCATION_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        headers = set(reader.fieldnames or [])

        missing_columns = REQUIRED_CSV_COLUMNS - headers

        if missing_columns:
            raise RuntimeError(
                "File CSV thieu cot: "
                + ", ".join(sorted(missing_columns))
            )

        rows = []

        for file_order, raw in enumerate(reader, start=1):
            try:
                ma_tu_hsk = int(raw["MaTuHSK"])
                bai = int(raw["BaiDeXuat"])
            except Exception as exc:
                raise RuntimeError(
                    f"Dong CSV {file_order + 1} co "
                    "MaTuHSK/BaiDeXuat khong hop le."
                ) from exc

            rows.append(
                {
                    "file_order": file_order,
                    "MaTuHSK": ma_tu_hsk,
                    "ChuHan": clean_text(raw["ChuHan"]),
                    "PhienAm": clean_text(raw["PhienAm"]),
                    "DaDungTrongBai1": clean_text(
                        raw["DaDungTrongBai1"]
                    ),
                    "BaiDeXuat": bai,
                    "TieuDeBaiTrung": clean_text(
                        raw["TieuDeBaiTrung"]
                    ),
                    "TieuDeBaiViet": clean_text(
                        raw["TieuDeBaiViet"]
                    ),
                }
            )

    if len(rows) != EXPECTED_WORDS:
        raise RuntimeError(
            f"File phan bo phai co 500 dong. "
            f"Thuc te: {len(rows)}"
        )

    ma_ids = [
        row["MaTuHSK"]
        for row in rows
    ]

    if len(set(ma_ids)) != EXPECTED_WORDS:
        duplicates = [
            ma
            for ma, count in Counter(ma_ids).items()
            if count > 1
        ]

        raise RuntimeError(
            "MaTuHSK bi trung trong CSV: "
            + ", ".join(
                map(str, sorted(duplicates))
            )
        )

    invalid_lessons = sorted(
        {
            row["BaiDeXuat"]
            for row in rows
            if row["BaiDeXuat"]
            not in range(1, 24)
        }
    )

    if invalid_lessons:
        raise RuntimeError(
            "CSV co BaiDeXuat ngoai 1..23: "
            + ", ".join(
                map(str, invalid_lessons)
            )
        )

    counts = Counter(
        row["BaiDeXuat"]
        for row in rows
    )

    if dict(
        sorted(counts.items())
    ) != EXPECTED_COUNTS:

        raise RuntimeError(
            "So luong tu theo bai trong CSV "
            "khong khop file phan bo da chot.\n"
            f"Thuc te: {dict(sorted(counts.items()))}"
        )

    lesson1_rows = [
        row
        for row in rows
        if row["BaiDeXuat"] == 1
    ]

    if len(lesson1_rows) != 13:
        raise RuntimeError(
            "Bai 1 trong CSV "
            "khong co dung 13 tu."
        )

    if any(
        row["DaDungTrongBai1"] != "1"
        for row in lesson1_rows
    ):
        raise RuntimeError(
            "Co tu Bai 1 trong CSV "
            "khong duoc danh dau "
            "DaDungTrongBai1=1."
        )

    wrong_flags = [
        row
        for row in rows
        if row["DaDungTrongBai1"] == "1"
        and row["BaiDeXuat"] != 1
    ]

    if wrong_flags:
        raise RuntimeError(
            "Co tu danh dau "
            "DaDungTrongBai1=1 "
            "nhung khong thuoc Bai 1."
        )

    return rows, counts


# =========================================================
# MAIN
# =========================================================
def main():
    conn = None
    cursor = None

    try:
        print("=" * 96)
        print(
            "09E - GAN DU 500 TU HSK1 "
            "VAO 23 BAI HOC"
        )
        print("=" * 96)

        # -------------------------------------------------
        # 1. DOC FILE PHAN BO
        # -------------------------------------------------
        allocation_rows, expected_counts = (
            load_allocation_file()
        )

        print()
        print("File phan bo:")
        print(ALLOCATION_FILE)

        print(
            "Tong dong CSV:",
            len(allocation_rows),
        )

        print(
            "Bai 1 trong CSV:",
            expected_counts[1],
        )

        print(
            "Bai 2 -> 23:",
            len(allocation_rows)
            - expected_counts[1],
        )

        # -------------------------------------------------
        # 2. CONNECT
        # -------------------------------------------------
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        check_schema(cursor)

        # -------------------------------------------------
        # 3. TIM KHOA HSK1-CORE
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                MaKhoaHoc,
                MaCapDo,
                MaKyHieu,
                TieuDe,
                TrangThai
            FROM dbo.KhoaHoc
            WHERE MaKyHieu = ?
            """,
            COURSE_CODE,
        )

        courses = cursor.fetchall()

        if len(courses) != 1:
            raise RuntimeError(
                f"Khong tim thay duy nhat "
                f"khoa {COURSE_CODE}."
            )

        course = courses[0]

        if course.MaCapDo != HSK_LEVEL:
            raise RuntimeError(
                f"{COURSE_CODE} co "
                f"MaCapDo={course.MaCapDo}, "
                "khong phai HSK1."
            )

        ma_khoa_hoc = (
            course.MaKhoaHoc
        )

        # -------------------------------------------------
        # 4. DOC 23 BAI LIVE DB
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                MaBaiHoc,
                SoThuTuBai,
                TieuDe,
                TrangThai
            FROM dbo.BaiHoc
            WHERE MaKhoaHoc = ?
            ORDER BY SoThuTuBai
            """,
            ma_khoa_hoc,
        )

        lessons = cursor.fetchall()

        if len(lessons) != EXPECTED_LESSONS:
            raise RuntimeError(
                "HSK1 phai co 23 bai. "
                f"Thuc te: {len(lessons)}"
            )

        actual_orders = [
            row.SoThuTuBai
            for row in lessons
        ]

        if actual_orders != list(
            range(1, 24)
        ):
            raise RuntimeError(
                "SoThuTuBai trong DB "
                "khong lien tuc 1 -> 23."
            )

        lesson_by_order = {
            row.SoThuTuBai: row
            for row in lessons
        }

        print()
        print(
            "Khoa HSK1:",
            course.TieuDe,
        )

        print(
            "Tong bai live DB:",
            len(lessons),
        )

        # -------------------------------------------------
        # 5. DOI CHIEU CSV VOI TuVungHSKChuan
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                MaTuHSK,
                ChuHan,
                PhienAm
            FROM dbo.TuVungHSKChuan
            WHERE MaCapDo = ?
            ORDER BY MaTuHSK
            """,
            HSK_LEVEL,
        )

        hsk_rows = cursor.fetchall()

        if len(hsk_rows) != EXPECTED_WORDS:
            raise RuntimeError(
                "TuVungHSKChuan HSK1 "
                "phai co 500 dong. "
                f"Thuc te: {len(hsk_rows)}"
            )

        hsk_by_id = {
            row.MaTuHSK: row
            for row in hsk_rows
        }

        allocation_ids = {
            row["MaTuHSK"]
            for row in allocation_rows
        }

        if allocation_ids != set(
            hsk_by_id.keys()
        ):
            raise RuntimeError(
                "Tap MaTuHSK trong CSV "
                "khong khop 500 MaTuHSK "
                "live DB."
            )

        csv_hsk_mismatches = []

        for row in allocation_rows:
            hsk = hsk_by_id[
                row["MaTuHSK"]
            ]

            if (
                make_key(
                    row["ChuHan"],
                    row["PhienAm"],
                )
                !=
                make_key(
                    hsk.ChuHan,
                    hsk.PhienAm,
                )
            ):
                csv_hsk_mismatches.append(
                    (
                        row["MaTuHSK"],
                        row["ChuHan"],
                        row["PhienAm"],
                        hsk.ChuHan,
                        hsk.PhienAm,
                    )
                )

        if csv_hsk_mismatches:
            print()
            print(
                "CSV KHONG KHOP "
                "TuVungHSKChuan:"
            )

            for item in (
                csv_hsk_mismatches[:20]
            ):
                print(item)

            raise RuntimeError(
                "Co dong CSV khong khop "
                "ChuHan/PhienAm live DB."
            )

        # -------------------------------------------------
        # 6. MAP 500 HSK -> 500 TuVung
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                MaTuVung,
                ChuHan,
                PhienAm
            FROM dbo.TuVung
            ORDER BY MaTuVung
            """
        )

        runtime_rows = (
            cursor.fetchall()
        )

        if len(
            runtime_rows
        ) != EXPECTED_WORDS:

            raise RuntimeError(
                "Truoc 09e TuVung "
                "phai co dung 500 dong. "
                f"Thuc te: {len(runtime_rows)}"
            )

        runtime_by_key = (
            defaultdict(list)
        )

        for row in runtime_rows:

            runtime_by_key[
                make_key(
                    row.ChuHan,
                    row.PhienAm,
                )
            ].append(row)

        duplicate_runtime_keys = {
            key: rows
            for key, rows
            in runtime_by_key.items()
            if len(rows) > 1
        }

        if duplicate_runtime_keys:

            raise RuntimeError(
                "TuVung runtime co "
                "ChuHan+PhienAm trung; "
                "khong the gan bai an toan."
            )

        allocation_with_runtime = []

        for row in allocation_rows:

            candidates = runtime_by_key.get(
                make_key(
                    row["ChuHan"],
                    row["PhienAm"],
                ),
                [],
            )

            if len(candidates) != 1:

                raise RuntimeError(
                    f"MaTuHSK="
                    f"{row['MaTuHSK']} "
                    f"({row['ChuHan']} "
                    f"| {row['PhienAm']}) "
                    f"khop "
                    f"{len(candidates)} "
                    "TuVung runtime."
                )

            new_row = dict(row)

            new_row["MaTuVung"] = (
                candidates[0].MaTuVung
            )

            new_row["MaBaiHoc"] = (
                lesson_by_order[
                    row["BaiDeXuat"]
                ].MaBaiHoc
            )

            allocation_with_runtime.append(
                new_row
            )

        # -------------------------------------------------
        # 7. TAO ThuTu CHO BAI 2 -> 23
        # Bai 1 giu nguyen ThuTu cu
        # -------------------------------------------------
        next_order = Counter()

        for row in allocation_with_runtime:

            bai = row["BaiDeXuat"]

            if bai == 1:
                row["ThuTu"] = None
                continue

            next_order[bai] += 1
            row["ThuTu"] = (
                next_order[bai]
            )

        for bai in range(2, 24):

            if (
                next_order[bai]
                != expected_counts[bai]
            ):
                raise RuntimeError(
                    f"ThuTu sinh cho Bai "
                    f"{bai} khong du "
                    f"{expected_counts[bai]} tu."
                )

        # -------------------------------------------------
        # 8. KIEM TRA LIEN KET HIEN TAI
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                tvbh.MaBaiHoc,
                bh.SoThuTuBai,
                tvbh.MaTuVung,
                tvbh.ThuTu,
                tv.ChuHan,
                tv.PhienAm
            FROM dbo.TuVungBaiHoc tvbh

            INNER JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc =
                   tvbh.MaBaiHoc

            INNER JOIN dbo.TuVung tv
                ON tv.MaTuVung =
                   tvbh.MaTuVung

            WHERE bh.MaKhoaHoc = ?

            ORDER BY
                bh.SoThuTuBai,
                tvbh.ThuTu
            """,
            ma_khoa_hoc,
        )

        existing_links = (
            cursor.fetchall()
        )

        print()
        print(
            "Lien ket HSK1 hien tai:",
            len(existing_links),
        )

        if (
            len(existing_links)
            != EXPECTED_EXISTING_LINKS
        ):
            raise RuntimeError(
                "Truoc 09e HSK1 phai "
                "co dung 13 lien ket "
                "TuVungBaiHoc cua Bai 1. "
                f"Thuc te: "
                f"{len(existing_links)}"
            )

        if any(
            row.SoThuTuBai != 1
            for row in existing_links
        ):
            raise RuntimeError(
                "Da co TuVungBaiHoc "
                "o Bai 2 -> 23; "
                "khong insert de tranh trung."
            )

        # -------------------------------------------------
        # 9. DOI CHIEU 13 TU BAI 1
        # -------------------------------------------------
        expected_lesson1_runtime_ids = {
            row["MaTuVung"]
            for row
            in allocation_with_runtime
            if row["BaiDeXuat"] == 1
        }

        actual_lesson1_runtime_ids = {
            row.MaTuVung
            for row in existing_links
        }

        if (
            actual_lesson1_runtime_ids
            != expected_lesson1_runtime_ids
        ):
            raise RuntimeError(
                "13 tu dang gan Bai 1 "
                "khong khop 13 tu Bai 1 "
                "trong file phan bo."
            )

        # -------------------------------------------------
        # 10. IN TOM TAT TRUOC INSERT
        # -------------------------------------------------
        print()
        print("-" * 96)
        print("PHAN BO SE AP DUNG")
        print("-" * 96)

        for bai in range(1, 24):

            lesson = (
                lesson_by_order[bai]
            )

            count = (
                expected_counts[bai]
            )

            action = (
                "GIU NGUYEN"
                if bai == 1
                else "INSERT"
            )

            print(
                f"Bai {bai:02d}"
                f" | MaBaiHoc="
                f"{lesson.MaBaiHoc:<3}"
                f" | {count:>2} tu"
                f" | {action}"
                f" | {lesson.TieuDe}"
            )

        # -------------------------------------------------
        # 11. INSERT 487 LIEN KET
        # -------------------------------------------------
        rows_to_insert = [
            row
            for row
            in allocation_with_runtime
            if row["BaiDeXuat"] != 1
        ]

        if (
            len(rows_to_insert)
            != EXPECTED_NEW_LINKS
        ):
            raise RuntimeError(
                "Phai insert 487 lien ket. "
                f"Thuc te: "
                f"{len(rows_to_insert)}"
            )

        inserted = 0

        for row in rows_to_insert:

            cursor.execute(
                """
                INSERT INTO dbo.TuVungBaiHoc
                (
                    MaBaiHoc,
                    MaTuVung,
                    ThuTu
                )
                VALUES (?, ?, ?)
                """,
                row["MaBaiHoc"],
                row["MaTuVung"],
                row["ThuTu"],
            )

            inserted += 1

        if (
            inserted
            != EXPECTED_NEW_LINKS
        ):
            raise RuntimeError(
                "So lien ket da insert "
                "khong bang 487. "
                f"Thuc te: {inserted}"
            )

        # -------------------------------------------------
        # 12. VERIFY SO TU TUNG BAI
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                bh.SoThuTuBai,
                COUNT(*) AS SoTu
            FROM dbo.TuVungBaiHoc tvbh

            INNER JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc =
                   tvbh.MaBaiHoc

            WHERE bh.MaKhoaHoc = ?

            GROUP BY
                bh.SoThuTuBai

            ORDER BY
                bh.SoThuTuBai
            """,
            ma_khoa_hoc,
        )

        count_rows = (
            cursor.fetchall()
        )

        actual_counts = {
            row.SoThuTuBai:
                row.SoTu
            for row in count_rows
        }

        if (
            actual_counts
            != EXPECTED_COUNTS
        ):
            raise RuntimeError(
                "So tu theo bai sau "
                "insert khong khop "
                "file phan bo.\n"
                f"Thuc te: "
                f"{actual_counts}"
            )

        # -------------------------------------------------
        # 13. VERIFY TONG 500 LIEN KET
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.TuVungBaiHoc tvbh

            INNER JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc =
                   tvbh.MaBaiHoc

            WHERE bh.MaKhoaHoc = ?
            """,
            ma_khoa_hoc,
        )

        final_links = (
            cursor.fetchone()[0]
        )

        if (
            final_links
            != EXPECTED_FINAL_LINKS
        ):
            raise RuntimeError(
                "Tong lien ket HSK1 "
                "sau insert phai la 500. "
                f"Thuc te: {final_links}"
            )

        # -------------------------------------------------
        # 14. MOI TU CHI NAM 1 BAI
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                tvbh.MaTuVung,
                COUNT(*) AS SoBai
            FROM dbo.TuVungBaiHoc tvbh

            INNER JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc =
                   tvbh.MaBaiHoc

            WHERE bh.MaKhoaHoc = ?

            GROUP BY
                tvbh.MaTuVung

            HAVING COUNT(*) <> 1
            """,
            ma_khoa_hoc,
        )

        invalid_word_links = (
            cursor.fetchall()
        )

        if invalid_word_links:

            raise RuntimeError(
                "Co TuVung duoc gan "
                "0/nhieu hon 1 bai "
                "trong HSK1."
            )

        # -------------------------------------------------
        # 15. DEM TU KHAC NHAU
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                COUNT(
                    DISTINCT tvbh.MaTuVung
                )
            FROM dbo.TuVungBaiHoc tvbh

            INNER JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc =
                   tvbh.MaBaiHoc

            WHERE bh.MaKhoaHoc = ?
            """,
            ma_khoa_hoc,
        )

        distinct_words = (
            cursor.fetchone()[0]
        )

        if (
            distinct_words
            != EXPECTED_WORDS
        ):
            raise RuntimeError(
                "So TuVung khac nhau "
                "duoc gan bai phai la 500. "
                f"Thuc te: {distinct_words}"
            )

        # -------------------------------------------------
        # 16. COMMIT
        # -------------------------------------------------
        conn.commit()

        # -------------------------------------------------
        # 17. KET QUA
        # -------------------------------------------------
        print()
        print("=" * 96)
        print("KET QUA")
        print("=" * 96)

        print(
            "Lien ket truoc 09e :",
            EXPECTED_EXISTING_LINKS,
        )

        print(
            "Da insert           :",
            inserted,
        )

        print(
            "Tong lien ket HSK1  :",
            final_links,
        )

        print(
            "Tu vung khac nhau   :",
            distinct_words,
        )

        print()
        print("SO TU TUNG BAI")
        print("-" * 50)

        for bai in range(1, 24):

            print(
                f"Bai {bai:02d}: "
                f"{actual_counts[bai]:>2} tu"
            )

        print()
        print(
            "Chua phan bai : 0"
        )

        print(
            "Trung bai     : 0"
        )

        print(
            "Bai 1         : "
            "13 tu (giu nguyen)"
        )

        print(
            "Bai 2 -> 23   : "
            "487 tu moi duoc gan"
        )

        print()
        print(
            "DA GAN DU 500/500 TU HSK1 "
            "VAO 23 BAI THANH CONG."
        )

        print()
        print("LUU Y:")

        print(
            "- Chua them tu bo sung "
            "越南 vao Bai 2."
        )

        print(
            "- Chua duyet nghia 500 tu "
            "(DaDuyet van = 0)."
        )

        print(
            "- Chua tao vi du "
            "cho 487 tu moi."
        )

        print(
            "- Chua tao ngu phap / "
            "Chu Han / bai tap "
            "cho Bai 2 -> 23."
        )

        print()
        print("=" * 96)
        print("HOAN TAT")
        print("=" * 96)

    except Exception as e:

        if conn:
            conn.rollback()

        print()
        print("=" * 96)
        print(
            "THAT BAI - DA ROLLBACK"
        )
        print("=" * 96)

        print(
            "Loi:",
            e,
        )

        print()
        print(
            "KHONG GIU BAT KY "
            "LIEN KET TuVungBaiHoc "
            "MOI NAO NEU CO LOI."
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


if __name__ == "__main__":
    main()