from pathlib import Path
import sys


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


TARGET_WORD = "越南"
LESSON_ORDER = 2
COURSE_CODE = "HSK1-CORE"


def main():

    conn = None
    cursor = None

    try:

        print("=" * 90)
        print("09F1 - KIEM TRA TU BO SUNG 越南")
        print("=" * 90)

        conn = get_connection()
        cursor = conn.cursor()

        # =================================================
        # 1. KIEM TRA BAI 2
        # =================================================
        cursor.execute(
            """
            SELECT
                bh.MaBaiHoc,
                bh.SoThuTuBai,
                bh.TieuDe,
                bh.TrangThai
            FROM dbo.BaiHoc bh

            INNER JOIN dbo.KhoaHoc kh
                ON kh.MaKhoaHoc = bh.MaKhoaHoc

            WHERE kh.MaKyHieu = ?
              AND bh.SoThuTuBai = ?
            """,
            COURSE_CODE,
            LESSON_ORDER,
        )

        lesson_rows = cursor.fetchall()

        if len(lesson_rows) != 1:
            raise RuntimeError(
                "Khong tim thay duy nhat Bai 2 "
                "cua HSK1-CORE."
            )

        lesson = lesson_rows[0]

        print()
        print("-" * 90)
        print("BAI 2")
        print("-" * 90)

        print(
            "MaBaiHoc :",
            lesson.MaBaiHoc,
        )

        print(
            "TieuDe    :",
            lesson.TieuDe,
        )

        print(
            "TrangThai :",
            lesson.TrangThai,
        )

        # =================================================
        # 2. KIEM TRA 越南 CO NAM TRONG 500 HSK1 KHONG
        # =================================================
        cursor.execute(
            """
            SELECT
                MaTuHSK,
                MaCapDo,
                ChuHan,
                PhienAm
            FROM dbo.TuVungHSKChuan
            WHERE MaCapDo = 1
              AND ChuHan = ?
            """,
            TARGET_WORD,
        )

        hsk_rows = cursor.fetchall()

        print()
        print("-" * 90)
        print("KIEM TRA TRONG 500 HSK1")
        print("-" * 90)

        print(
            "So dong:",
            len(hsk_rows),
        )

        if hsk_rows:

            for row in hsk_rows:

                print(
                    f"MaTuHSK={row.MaTuHSK}"
                    f" | {row.ChuHan}"
                    f" | {row.PhienAm}"
                )

        else:

            print(
                "越南 KHONG nam trong "
                "500 tu HSK1 hien tai."
            )

        # =================================================
        # 3. KIEM TRA DA CO TRONG TuVung RUNTIME CHUA
        # =================================================
        cursor.execute(
            """
            SELECT
                MaTuVung,
                ChuHan,
                ChuPhonThe,
                PhienAm,
                NghiaTiengViet,
                TuLoai,
                MaNguon,
                DaDuyet
            FROM dbo.TuVung
            WHERE ChuHan = ?
            ORDER BY MaTuVung
            """,
            TARGET_WORD,
        )

        runtime_rows = cursor.fetchall()

        print()
        print("-" * 90)
        print("KIEM TRA dbo.TuVung")
        print("-" * 90)

        print(
            "So dong:",
            len(runtime_rows),
        )

        for row in runtime_rows:

            print(
                f"MaTuVung={row.MaTuVung}"
                f" | {row.ChuHan}"
                f" | {row.PhienAm}"
                f" | {row.NghiaTiengViet}"
                f" | MaNguon={row.MaNguon}"
                f" | DaDuyet={row.DaDuyet}"
            )

        # =================================================
        # 4. TIM TRONG MucTuDien
        # =================================================
        cursor.execute(
            """
            SELECT
                m.MaMucTu,
                m.MaNguon,
                nd.Ten AS TenNguon,
                m.MaNguonBenNgoai,
                m.ChuHan,
                m.ChuPhonThe,
                m.PhienAm,
                m.NghiaGoc,
                m.NgonNguNghiaGoc,
                m.NghiaTiengViet,
                m.NghiaVietDaDuyet
            FROM dbo.MucTuDien m

            INNER JOIN dbo.NguonDuLieu nd
                ON nd.MaNguon = m.MaNguon

            WHERE m.ChuHan = ?

            ORDER BY
                m.MaNguon,
                m.MaMucTu
            """,
            TARGET_WORD,
        )

        dictionary_rows = cursor.fetchall()

        print()
        print("-" * 90)
        print("KET QUA TRONG MucTuDien")
        print("-" * 90)

        print(
            "So muc tim thay:",
            len(dictionary_rows),
        )

        for row in dictionary_rows:

            print()
            print(
                "MaMucTu       :",
                row.MaMucTu,
            )

            print(
                "MaNguon       :",
                row.MaNguon,
            )

            print(
                "TenNguon      :",
                row.TenNguon,
            )

            print(
                "MaNgoai       :",
                row.MaNguonBenNgoai,
            )

            print(
                "ChuHan        :",
                row.ChuHan,
            )

            print(
                "ChuPhonThe    :",
                row.ChuPhonThe,
            )

            print(
                "PhienAm       :",
                row.PhienAm,
            )

            print(
                "NghiaGoc      :",
                row.NghiaGoc,
            )

            print(
                "NgonNguGoc    :",
                row.NgonNguNghiaGoc,
            )

            print(
                "NghiaViet     :",
                row.NghiaTiengViet,
            )

            print(
                "NghiaVietDuyet:",
                row.NghiaVietDaDuyet,
            )

        # =================================================
        # 5. KIEM TRA 越南 DA GAN BAI 2 CHUA
        # =================================================
        cursor.execute(
            """
            SELECT
                tvbh.MaBaiHoc,
                tvbh.MaTuVung,
                tvbh.ThuTu,
                tv.ChuHan,
                tv.PhienAm
            FROM dbo.TuVungBaiHoc tvbh

            INNER JOIN dbo.TuVung tv
                ON tv.MaTuVung = tvbh.MaTuVung

            WHERE tvbh.MaBaiHoc = ?
              AND tv.ChuHan = ?
            """,
            lesson.MaBaiHoc,
            TARGET_WORD,
        )

        linked_rows = cursor.fetchall()

        print()
        print("-" * 90)
        print("KIEM TRA LIEN KET BAI 2")
        print("-" * 90)

        print(
            "越南 da gan Bai 2:",
            len(linked_rows),
        )

        for row in linked_rows:

            print(
                f"MaTuVung={row.MaTuVung}"
                f" | ThuTu={row.ThuTu}"
                f" | {row.ChuHan}"
                f" | {row.PhienAm}"
            )

        # =================================================
        # 6. SO TU BAI 2 HIEN TAI
        # =================================================
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.TuVungBaiHoc
            WHERE MaBaiHoc = ?
            """,
            lesson.MaBaiHoc,
        )

        lesson2_count = cursor.fetchone()[0]

        print()
        print("=" * 90)
        print("TONG KET")
        print("=" * 90)

        print(
            "越南 trong HSK1:",
            len(hsk_rows),
        )

        print(
            "越南 trong TuVung:",
            len(runtime_rows),
        )

        print(
            "越南 trong MucTuDien:",
            len(dictionary_rows),
        )

        print(
            "越南 da gan Bai 2:",
            len(linked_rows),
        )

        print(
            "So tu Bai 2 hien tai:",
            lesson2_count,
        )

        print()
        print(
            "SCRIPT NAY CHI KIEM TRA."
        )

        print(
            "KHONG INSERT / UPDATE DATABASE."
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