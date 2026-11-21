from pathlib import Path
import sys
from collections import defaultdict


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


HSK_LEVEL = 1
EXPECTED_HSK1 = 500
EXPECTED_EXISTING = 13
EXPECTED_MISSING = 487


# =========================================================
# CHUAN HOA NHE DE SO SANH
# Khong thay doi du lieu DB
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


# =========================================================
# KIEM TRA COT BAT BUOC
# =========================================================
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

    required_hsk = {
        "MaTuHSK",
        "MaCapDo",
        "ChuHan",
        "PhienAm",
        "NghiaTiengVietThamChieu",
        "TuLoai",
        "MaNguonDanhSach",
    }

    required_runtime = {
        "MaTuVung",
        "ChuHan",
        "PhienAm",
        "NghiaTiengViet",
        "TuLoai",
        "MaNguon",
        "DaDuyet",
    }

    hsk_columns = get_columns(
        cursor,
        "TuVungHSKChuan",
    )

    runtime_columns = get_columns(
        cursor,
        "TuVung",
    )

    missing_hsk = (
        required_hsk
        - hsk_columns
    )

    missing_runtime = (
        required_runtime
        - runtime_columns
    )

    if missing_hsk:
        raise RuntimeError(
            "TuVungHSKChuan thieu cot: "
            + ", ".join(
                sorted(missing_hsk)
            )
        )

    if missing_runtime:
        raise RuntimeError(
            "TuVung thieu cot: "
            + ", ".join(
                sorted(missing_runtime)
            )
        )

    print()
    print("Schema:")
    print("  TuVungHSKChuan : OK")
    print("  TuVung         : OK")


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None
    cursor = None

    try:

        print("=" * 90)
        print(
            "09C2 - KIEM TRA KHOP "
            "TU VUNG HSK1 -> TuVung"
        )
        print("=" * 90)

        conn = get_connection()
        cursor = conn.cursor()

        # -------------------------------------------------
        # 1. SCHEMA
        # -------------------------------------------------
        check_schema(cursor)

        # -------------------------------------------------
        # 2. DOC 500 TU HSK1
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                MaTuHSK,
                MaMucNoiBo,
                SoThuTuNguon,
                ChuHan,
                PhienAm,
                TuLoai,
                NghiaTiengVietThamChieu,
                MaNguonDanhSach
            FROM dbo.TuVungHSKChuan
            WHERE MaCapDo = ?
            ORDER BY MaTuHSK
            """,
            HSK_LEVEL,
        )

        hsk_rows = cursor.fetchall()

        print()
        print(
            "Tong TuVungHSKChuan HSK1:",
            len(hsk_rows),
        )

        if len(hsk_rows) != EXPECTED_HSK1:
            raise RuntimeError(
                "HSK1 khong co dung 500 muc. "
                f"Thuc te: {len(hsk_rows)}"
            )

        # -------------------------------------------------
        # 3. DOC TOAN BO TuVung RUNTIME
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                MaTuVung,
                ChuHan,
                PhienAm,
                NghiaTiengViet,
                TuLoai,
                MaNguon,
                DaDuyet
            FROM dbo.TuVung
            ORDER BY MaTuVung
            """
        )

        runtime_rows = cursor.fetchall()

        print(
            "Tong TuVung runtime:",
            len(runtime_rows),
        )

        # -------------------------------------------------
        # 4. LAP INDEX THEO ChuHan + PhienAm
        # -------------------------------------------------
        runtime_by_key = defaultdict(list)

        for row in runtime_rows:

            key = make_key(
                row.ChuHan,
                row.PhienAm,
            )

            runtime_by_key[key].append(
                row
            )

        # -------------------------------------------------
        # 5. KIEM TRA RUNTIME CO KEY TRUNG KHONG
        # -------------------------------------------------
        duplicate_runtime_keys = {
            key: rows
            for key, rows
            in runtime_by_key.items()
            if len(rows) > 1
        }

        if duplicate_runtime_keys:

            print()
            print("-" * 90)
            print(
                "CANH BAO: TRUNG "
                "ChuHan + PhienAm TRONG TuVung"
            )
            print("-" * 90)

            for key, rows in duplicate_runtime_keys.items():

                print(
                    key,
                    "=>",
                    [
                        row.MaTuVung
                        for row in rows
                    ],
                )

        # -------------------------------------------------
        # 6. SO KHOP 500 HSK
        # -------------------------------------------------
        matched = []
        missing = []
        ambiguous = []

        for hsk in hsk_rows:

            key = make_key(
                hsk.ChuHan,
                hsk.PhienAm,
            )

            candidates = (
                runtime_by_key.get(
                    key,
                    [],
                )
            )

            if len(candidates) == 0:

                missing.append(
                    hsk
                )

            elif len(candidates) == 1:

                matched.append(
                    (
                        hsk,
                        candidates[0],
                    )
                )

            else:

                ambiguous.append(
                    (
                        hsk,
                        candidates,
                    )
                )

        # -------------------------------------------------
        # 7. IN CAC TU DA KHOP
        # -------------------------------------------------
        print()
        print("-" * 90)
        print("CAC TU DA CO TRONG TuVung")
        print("-" * 90)

        for hsk, runtime in matched:

            print(
                f"MaTuHSK={hsk.MaTuHSK:<4}"
                f" | MaTuVung={runtime.MaTuVung:<4}"
                f" | {hsk.ChuHan}"
                f" | {hsk.PhienAm}"
                f" | Nguon={runtime.MaNguon}"
            )

        # -------------------------------------------------
        # 8. KIEM TRA NGUON 13 TU
        # -------------------------------------------------
        wrong_source = [
            (hsk, runtime)
            for hsk, runtime in matched
            if runtime.MaNguon
            != hsk.MaNguonDanhSach
        ]

        # -------------------------------------------------
        # 9. KIEM TRA 13 TU BAI 1
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                tvbh.ThuTu,
                tv.MaTuVung,
                tv.ChuHan,
                tv.PhienAm
            FROM dbo.TuVungBaiHoc tvbh

            INNER JOIN dbo.TuVung tv
                ON tv.MaTuVung =
                   tvbh.MaTuVung

            WHERE tvbh.MaBaiHoc = 1

            ORDER BY tvbh.ThuTu
            """
        )

        lesson1_rows = (
            cursor.fetchall()
        )

        # -------------------------------------------------
        # 10. KET QUA
        # -------------------------------------------------
        print()
        print("=" * 90)
        print("KET QUA")
        print("=" * 90)

        print(
            "Tong HSK1:",
            len(hsk_rows),
        )

        print(
            "Da co trong TuVung:",
            len(matched),
        )

        print(
            "Con thieu:",
            len(missing),
        )

        print(
            "Mo ho / khop nhieu:",
            len(ambiguous),
        )

        print(
            "Runtime key bi trung:",
            len(duplicate_runtime_keys),
        )

        print(
            "Sai MaNguon:",
            len(wrong_source),
        )

        print(
            "TuVungBaiHoc Bai 1:",
            len(lesson1_rows),
        )

        # -------------------------------------------------
        # 11. EXPECTED CHECK
        # -------------------------------------------------
        problems = []

        if len(matched) != EXPECTED_EXISTING:
            problems.append(
                "So tu da co != 13"
            )

        if len(missing) != EXPECTED_MISSING:
            problems.append(
                "So tu thieu != 487"
            )

        if ambiguous:
            problems.append(
                "Co tu HSK khop nhieu "
                "TuVung runtime"
            )

        if duplicate_runtime_keys:
            problems.append(
                "TuVung co ChuHan+PhienAm trung"
            )

        if wrong_source:
            problems.append(
                "Co tu runtime sai MaNguon"
            )

        if len(lesson1_rows) != 13:
            problems.append(
                "Bai 1 khong co dung 13 tu"
            )

        if problems:

            print()
            print("-" * 90)
            print(
                "CHUA DU DIEU KIEN INSERT 487 TU"
            )
            print("-" * 90)

            for problem in problems:
                print(
                    "-",
                    problem,
                )

            print()
            print(
                "KHONG SUA DATABASE."
            )

            return

        # -------------------------------------------------
        # 12. THANH CONG
        # -------------------------------------------------
        print()
        print(
            "DU DIEU KIEN DE CHUAN BI "
            "INSERT 487 TU CON LAI."
        )

        print()
        print(
            "SCRIPT NAY KHONG SUA DATABASE."
        )

        print()
        print("=" * 90)
        print("HOAN TAT")
        print("=" * 90)

    except Exception as e:

        print()
        print("=" * 90)
        print("THUC HIEN THAT BAI")
        print("=" * 90)

        print(
            "Loi:",
            e,
        )

        print()
        print(
            "KHONG SUA DATABASE."
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


if __name__ == "__main__":
    main()