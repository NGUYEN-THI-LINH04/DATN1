from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection


def main():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        print("=" * 75)
        print("BUOC 21 - KIEM TRA BAI TAP HSK1 VA HSK2")
        print("CHI DOC SQL - KHONG SUA DU LIEU")
        print("=" * 75)

        cursor.execute("""
            SELECT
                kh.MaKyHieu,
                COUNT(DISTINCT bh.MaBaiHoc) AS SoBaiHoc,
                COUNT(DISTINCT bt.MaBaiTap) AS SoBaiTap,
                COUNT(DISTINCT ch.MaCauHoi) AS SoCauHoi
            FROM dbo.KhoaHoc kh
            LEFT JOIN dbo.BaiHoc bh
                ON kh.MaKhoaHoc = bh.MaKhoaHoc
            LEFT JOIN dbo.BaiTap bt
                ON bh.MaBaiHoc = bt.MaBaiHoc
            LEFT JOIN dbo.CauHoi ch
                ON bt.MaBaiTap = ch.MaBaiTap
            WHERE kh.MaKyHieu IN ('HSK1-CORE', 'HSK2-CORE')
            GROUP BY kh.MaKyHieu
            ORDER BY kh.MaKyHieu
        """)

        print("\n1. TONG SO:")
        for row in cursor.fetchall():
            print(
                f"{row[0]} | "
                f"BaiHoc={row[1]} | "
                f"BaiTap={row[2]} | "
                f"CauHoi={row[3]}"
            )

        cursor.execute("""
            SELECT
                bh.SoThuTuBai,
                bt.MaBaiTap,
                bt.TieuDe,
                bt.HuongDan,
                bt.ThoiGianGioiHanGiay,
                bt.PhanTramDat,
                bt.TrangThai,
                COUNT(ch.MaCauHoi) AS SoCauHoi
            FROM dbo.BaiTap bt
            JOIN dbo.BaiHoc bh
                ON bt.MaBaiHoc = bh.MaBaiHoc
            JOIN dbo.KhoaHoc kh
                ON bh.MaKhoaHoc = kh.MaKhoaHoc
            LEFT JOIN dbo.CauHoi ch
                ON bt.MaBaiTap = ch.MaBaiTap
            WHERE kh.MaKyHieu = 'HSK1-CORE'
            GROUP BY
                bh.SoThuTuBai,
                bt.MaBaiTap,
                bt.TieuDe,
                bt.HuongDan,
                bt.ThoiGianGioiHanGiay,
                bt.PhanTramDat,
                bt.TrangThai
            ORDER BY bh.SoThuTuBai, bt.MaBaiTap
        """)

        print("\n2. MAU BAI TAP HSK1:")
        for row in cursor.fetchall()[:10]:
            print(tuple(row))

        cursor.execute("""
            SELECT
                ch.LoaiCauHoi,
                ch.KyNang,
                COUNT(*) AS SoLuong
            FROM dbo.CauHoi ch
            JOIN dbo.BaiTap bt
                ON ch.MaBaiTap = bt.MaBaiTap
            JOIN dbo.BaiHoc bh
                ON bt.MaBaiHoc = bh.MaBaiHoc
            JOIN dbo.KhoaHoc kh
                ON bh.MaKhoaHoc = kh.MaKhoaHoc
            WHERE kh.MaKyHieu = 'HSK1-CORE'
            GROUP BY ch.LoaiCauHoi, ch.KyNang
            ORDER BY SoLuong DESC
        """)

        print("\n3. LOAI CAU HOI HSK1:")
        for row in cursor.fetchall():
            print(tuple(row))

        cursor.execute("""
            SELECT TOP (5)
                ch.MaCauHoi,
                ch.LoaiCauHoi,
                ch.KyNang,
                ch.NoiDungCauHoi,
                ch.DapAnJson,
                ch.GiaiThich,
                ch.DiemToiDa,
                ch.ThuTu
            FROM dbo.CauHoi ch
            JOIN dbo.BaiTap bt
                ON ch.MaBaiTap = bt.MaBaiTap
            JOIN dbo.BaiHoc bh
                ON bt.MaBaiHoc = bh.MaBaiHoc
            JOIN dbo.KhoaHoc kh
                ON bh.MaKhoaHoc = kh.MaKhoaHoc
            WHERE kh.MaKyHieu = 'HSK1-CORE'
            ORDER BY bh.SoThuTuBai, ch.ThuTu
        """)

        questions = cursor.fetchall()

        print("\n4. NAM CAU HOI MAU HSK1:")

        for q in questions:
            print("\nCAU HOI:", tuple(q))

            cursor.execute("""
                SELECT
                    NoiDungLuaChon,
                    LaDapAnDung,
                    ThuTu
                FROM dbo.LuaChonCauHoi
                WHERE MaCauHoi = ?
                ORDER BY ThuTu
            """, q[0])

            for choice in cursor.fetchall():
                print("  Lua chon:", tuple(choice))

        print("\n" + "=" * 75)
        print("KIEM TRA HOAN TAT - KHONG GHI SQL")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()