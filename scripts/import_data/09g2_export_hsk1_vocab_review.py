from pathlib import Path
import csv
import sys


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

OUTPUT_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "review"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "hsk1_501_vocab_review.csv"
)


# =========================================================
# HELPER
# =========================================================
def clean(value):
    if value is None:
        return ""
    return str(value).strip()


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None
    cursor = None

    try:

        print("=" * 95)
        print(
            "09G2 - XUAT 501 TU HSK1 "
            "DE KIEM DUYET NOI DUNG"
        )
        print("=" * 95)

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        conn = get_connection()
        cursor = conn.cursor()

        # =================================================
        # 1. DOC 501 TU THEO THU TU BAI HOC
        # =================================================
        cursor.execute(
            """
            SELECT
                bh.SoThuTuBai,
                bh.TieuDe AS TieuDeBai,
                tvbh.ThuTu,

                tv.MaTuVung,
                tv.ChuHan,
                tv.PhienAm,
                tv.NghiaTiengViet,
                tv.TuLoai,
                tv.MaNguon,
                tv.DaDuyet,

                nd.Ten AS TenNguon

            FROM dbo.TuVungBaiHoc tvbh

            INNER JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc =
                   tvbh.MaBaiHoc

            INNER JOIN dbo.KhoaHoc kh
                ON kh.MaKhoaHoc =
                   bh.MaKhoaHoc

            INNER JOIN dbo.TuVung tv
                ON tv.MaTuVung =
                   tvbh.MaTuVung

            LEFT JOIN dbo.NguonDuLieu nd
                ON nd.MaNguon =
                   tv.MaNguon

            WHERE kh.MaKyHieu = ?

            ORDER BY
                bh.SoThuTuBai,
                tvbh.ThuTu
            """,
            COURSE_CODE,
        )

        rows = cursor.fetchall()

        if len(rows) != 501:

            raise RuntimeError(
                "HSK1 course phai co "
                "501 tu. "
                f"Thuc te: {len(rows)}"
            )

        # =================================================
        # 2. CAC COT REVIEW
        # =================================================
        fieldnames = [
            "SoThuTuBai",
            "TieuDeBai",
            "ThuTuTrongBai",

            "MaTuVung",
            "ChuHan",
            "PhienAm",

            "TuLoaiNguon",
            "NghiaNguon",

            "MaNguon",
            "TenNguon",

            "CanKiemTraTuLoai",
            "CanRutGonNghia",
            "CanKiemTraKyHieu",

            # CAC COT NAY DE SAU NAY REVIEW
            "TuLoaiHocTap",
            "NghiaHocTap",
            "GhiChuKiemDuyet",
            "DaKiemDuyet",
        ]

        # =================================================
        # 3. GHI CSV
        # =================================================
        missing_type_count = 0
        long_meaning_count = 0
        strange_symbol_count = 0

        suspicious_tokens = [
            "http://",
            "https://",
            "<",
            ">",
            "{",
            "}",
        ]

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

            for row in rows:

                word_type = clean(
                    row.TuLoai
                )

                meaning = clean(
                    row.NghiaTiengViet
                )

                missing_type = (
                    word_type == ""
                )

                long_meaning = (
                    len(meaning) > 120
                )

                strange_symbol = any(
                    token in meaning
                    for token
                    in suspicious_tokens
                )

                if missing_type:
                    missing_type_count += 1

                if long_meaning:
                    long_meaning_count += 1

                if strange_symbol:
                    strange_symbol_count += 1

                writer.writerow(
                    {
                        "SoThuTuBai":
                            row.SoThuTuBai,

                        "TieuDeBai":
                            row.TieuDeBai,

                        "ThuTuTrongBai":
                            row.ThuTu,

                        "MaTuVung":
                            row.MaTuVung,

                        "ChuHan":
                            row.ChuHan,

                        "PhienAm":
                            row.PhienAm,

                        "TuLoaiNguon":
                            word_type,

                        "NghiaNguon":
                            meaning,

                        "MaNguon":
                            row.MaNguon,

                        "TenNguon":
                            clean(
                                row.TenNguon
                            ),

                        "CanKiemTraTuLoai":
                            1 if missing_type else 0,

                        "CanRutGonNghia":
                            1 if long_meaning else 0,

                        "CanKiemTraKyHieu":
                            1 if strange_symbol else 0,

                        # Khong tu dong dien.
                        # Day la du lieu can review.
                        "TuLoaiHocTap":
                            "",

                        "NghiaHocTap":
                            "",

                        "GhiChuKiemDuyet":
                            "",

                        "DaKiemDuyet":
                            0,
                    }
                )

        # =================================================
        # 4. KIEM TRA FILE VUA XUAT
        # =================================================
        with open(
            OUTPUT_FILE,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            exported_rows = list(reader)

        if len(exported_rows) != 501:

            raise RuntimeError(
                "File review vua xuat "
                "khong co dung 501 dong."
            )

        # =================================================
        # 5. KET QUA
        # =================================================
        print()
        print("=" * 95)
        print("KET QUA")
        print("=" * 95)

        print(
            "Tong tu da xuat:",
            len(exported_rows),
        )

        print(
            "Thieu TuLoai:",
            missing_type_count,
        )

        print(
            "Nghia > 120 ky tu:",
            long_meaning_count,
        )

        print(
            "Nghia co ky hieu la:",
            strange_symbol_count,
        )

        print()
        print(
            "File review:"
        )

        print(
            OUTPUT_FILE
        )

        print()
        print(
            "KHONG SUA DATABASE."
        )

        print(
            "KHONG TU DONG DOI NGHIA."
        )

        print(
            "KHONG TU DONG CHUYEN "
            "DaDuyet = 1."
        )

        print()
        print("=" * 95)
        print("HOAN TAT")
        print("=" * 95)

    except Exception as e:

        print()
        print("=" * 95)
        print("THUC HIEN THAT BAI")
        print("=" * 95)

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