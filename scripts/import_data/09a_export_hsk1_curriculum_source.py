from pathlib import Path
import sys
import csv


# =========================================================
# THU MUC GOC
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# FILE OUTPUT
# =========================================================
OUTPUT_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "hsk1_500_curriculum_source.csv"
)


# =========================================================
# 13 TU DA DUNG TRONG BAI 1
# =========================================================
LESSON1_WORDS = {
    "你",
    "好",
    "我",
    "是",
    "叫",
    "什么",
    "名字",
    "很",
    "高兴",
    "认识",
    "吗",
    "呢",
    "也",
}


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 90)
        print(
            "XUAT 500 TU HSK1 DE THIET KE "
            "CHUONG TRINH HOC"
        )
        print("=" * 90)

        conn = get_connection()
        cursor = conn.cursor()

        # -------------------------------------------------
        # 1. KIEM TRA HSK1
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.TuVungHSKChuan
            WHERE MaCapDo = 1
            """
        )

        total = cursor.fetchone()[0]

        print()
        print(
            "Tong TuVungHSKChuan HSK1:",
            total
        )

        if total != 500:

            raise RuntimeError(
                "HSK1 phai co dung 500 muc. "
                f"Thuc te: {total}"
            )

        # -------------------------------------------------
        # 2. DOC DAY DU 500 TU
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                h.MaTuHSK,
                h.MaMucNoiBo,
                h.SoThuTuNguon,
                h.TuGoc,
                h.ChuHan,
                h.BienThe,
                h.PhienAmNguon,
                h.PhienAm,
                h.TuLoai,
                h.NghiaTiengVietThamChieu,
                h.MaNguonDanhSach,
                nd1.Ten AS NguonDanhSach,
                h.MaNguonNghiaViet,
                nd2.Ten AS NguonNghiaViet,
                h.DaKiemTraNguon,
                h.GhiChu,

                (
                    SELECT COUNT(*)
                    FROM dbo.TuVungHSKMucTuDien map
                    WHERE map.MaTuHSK = h.MaTuHSK
                ) AS SoMucTuDienLienKet

            FROM dbo.TuVungHSKChuan h

            LEFT JOIN dbo.NguonDuLieu nd1
                ON nd1.MaNguon =
                   h.MaNguonDanhSach

            LEFT JOIN dbo.NguonDuLieu nd2
                ON nd2.MaNguon =
                   h.MaNguonNghiaViet

            WHERE h.MaCapDo = 1

            ORDER BY
                CASE
                    WHEN h.SoThuTuNguon IS NULL
                    THEN 1
                    ELSE 0
                END,
                h.SoThuTuNguon,
                h.MaTuHSK
            """
        )

        rows = cursor.fetchall()

        if len(rows) != 500:

            raise RuntimeError(
                "SELECT khong tra ve dung 500 dong."
            )

        # -------------------------------------------------
        # 3. KIEM TRA MA NOI BO
        # -------------------------------------------------
        internal_codes = [
            row.MaMucNoiBo
            for row in rows
        ]

        if len(
            set(internal_codes)
        ) != 500:

            raise RuntimeError(
                "MaMucNoiBo bi trung."
            )

        # -------------------------------------------------
        # 4. DANH DAU BAI 1
        # -------------------------------------------------
        lesson1_count = sum(
            1
            for row in rows
            if row.ChuHan
            in LESSON1_WORDS
        )

        print(
            "So muc trung 13 tu Bai 1:",
            lesson1_count
        )

        if lesson1_count != 13:

            print()
            print(
                "CANH BAO: khong tim du "
                "13 tu Bai 1 trong HSK1."
            )

        # -------------------------------------------------
        # 5. TAO THU MUC OUTPUT
        # -------------------------------------------------
        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        # -------------------------------------------------
        # 6. GHI CSV
        # -------------------------------------------------
        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            fieldnames = [
                "MaTuHSK",
                "MaMucNoiBo",
                "SoThuTuNguon",
                "TuGoc",
                "ChuHan",
                "BienThe",
                "PhienAmNguon",
                "PhienAm",
                "TuLoai",
                "NghiaTiengVietThamChieu",
                "MaNguonDanhSach",
                "NguonDanhSach",
                "MaNguonNghiaViet",
                "NguonNghiaViet",
                "SoMucTuDienLienKet",
                "DaKiemTraNguon",
                "GhiChu",
                "DaDungTrongBai1",
                "BaiDeXuat",
                "ChuDeDeXuat",
                "GhiChuPhanBo",
            ]

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for row in rows:

                writer.writerow(
                    {
                        "MaTuHSK":
                            row.MaTuHSK,

                        "MaMucNoiBo":
                            row.MaMucNoiBo,

                        "SoThuTuNguon":
                            row.SoThuTuNguon,

                        "TuGoc":
                            row.TuGoc,

                        "ChuHan":
                            row.ChuHan,

                        "BienThe":
                            row.BienThe,

                        "PhienAmNguon":
                            row.PhienAmNguon,

                        "PhienAm":
                            row.PhienAm,

                        "TuLoai":
                            row.TuLoai,

                        "NghiaTiengVietThamChieu":
                            row.NghiaTiengVietThamChieu,

                        "MaNguonDanhSach":
                            row.MaNguonDanhSach,

                        "NguonDanhSach":
                            row.NguonDanhSach,

                        "MaNguonNghiaViet":
                            row.MaNguonNghiaViet,

                        "NguonNghiaViet":
                            row.NguonNghiaViet,

                        "SoMucTuDienLienKet":
                            row.SoMucTuDienLienKet,

                        "DaKiemTraNguon":
                            row.DaKiemTraNguon,

                        "GhiChu":
                            row.GhiChu,

                        "DaDungTrongBai1":
                            (
                                1
                                if row.ChuHan
                                in LESSON1_WORDS
                                else 0
                            ),

                        # De trong.
                        # Buoc sau moi chia chuong trinh.
                        "BaiDeXuat":
                            "",

                        "ChuDeDeXuat":
                            "",

                        "GhiChuPhanBo":
                            "",
                    }
                )

        # -------------------------------------------------
        # 7. THONG KE TU LOAI
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                TuLoai,
                COUNT(*) AS SoLuong
            FROM dbo.TuVungHSKChuan
            WHERE MaCapDo = 1
            GROUP BY TuLoai
            ORDER BY COUNT(*) DESC, TuLoai
            """
        )

        pos_rows = cursor.fetchall()

        print()
        print("-" * 90)
        print("THONG KE TU LOAI")
        print("-" * 90)

        for row in pos_rows:

            print(
                f"{str(row.TuLoai):<20}"
                f" : {row.SoLuong}"
            )

        # -------------------------------------------------
        # 8. KIEM TRA DONG THIEU DU LIEU
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                SUM(
                    CASE
                        WHEN ChuHan IS NULL
                          OR LTRIM(
                              RTRIM(ChuHan)
                          ) = N''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuChuHan,

                SUM(
                    CASE
                        WHEN PhienAm IS NULL
                          OR LTRIM(
                              RTRIM(PhienAm)
                          ) = N''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuPhienAm,

                SUM(
                    CASE
                        WHEN NghiaTiengVietThamChieu
                             IS NULL
                          OR LTRIM(
                              RTRIM(
                                  NghiaTiengVietThamChieu
                              )
                          ) = N''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuNghiaViet

            FROM dbo.TuVungHSKChuan
            WHERE MaCapDo = 1
            """
        )

        check = cursor.fetchone()

        print()
        print("=" * 90)
        print("KET QUA")
        print("=" * 90)

        print(
            "Tong HSK1:",
            total
        )

        print(
            "Tu Bai 1:",
            lesson1_count
        )

        print(
            "Thieu ChuHan:",
            check.ThieuChuHan
        )

        print(
            "Thieu PhienAm:",
            check.ThieuPhienAm
        )

        print(
            "Thieu NghiaViet:",
            check.ThieuNghiaViet
        )

        print()
        print(
            "File:"
        )

        print(
            OUTPUT_FILE
        )

        print()
        print(
            "CHUA TAO THEM BAI HOC."
        )

        print(
            "CHUA GAN 487 TU CON LAI "
            "VAO BAI."
        )

        print(
            "CHUA SUA DATABASE."
        )

        print()
        print("=" * 90)
        print("HOAN TAT")
        print("=" * 90)

        cursor.close()

    except Exception as e:

        print()
        print("=" * 90)
        print("THUC HIEN THAT BAI")
        print("=" * 90)

        print(
            "Loi:",
            e
        )

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()