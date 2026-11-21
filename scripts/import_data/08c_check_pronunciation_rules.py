from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


def show_value(value):
    if value is None:
        return "NULL"

    return str(value)


def main():

    conn = None

    try:

        print("=" * 90)
        print("KIEM TRA DAY DU QUY TAC PHAT AM")
        print("=" * 90)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                MaQuyTac,
                TenQuyTac,
                LoaiQuyTac,
                NoiDung,
                ViDuTiengTrung,
                ViDuPinyin,
                NghiaTiengViet,
                MaTep,
                MaNguon,
                ThuTu,
                TrangThai
            FROM dbo.QuyTacPhatAm
            ORDER BY ThuTu, MaQuyTac
            """
        )

        rows = cursor.fetchall()

        print()
        print("Tong quy tac:", len(rows))

        if len(rows) != 11:
            print(
                "CANH BAO: du kien 11 quy tac "
                f"nhung thuc te co {len(rows)}."
            )

        for row in rows:

            print()
            print("-" * 90)

            print(
                f"MaQuyTac : {row.MaQuyTac}"
            )

            print(
                f"ThuTu     : {row.ThuTu}"
            )

            print(
                f"Loai      : {row.LoaiQuyTac}"
            )

            print(
                f"Ten       : {show_value(row.TenQuyTac)}"
            )

            print(
                f"NoiDung   : {show_value(row.NoiDung)}"
            )

            print(
                f"ViDuTrung : {show_value(row.ViDuTiengTrung)}"
            )

            print(
                f"ViDuPinyin: {show_value(row.ViDuPinyin)}"
            )

            print(
                f"NghiaViet : {show_value(row.NghiaTiengViet)}"
            )

            print(
                f"MaTep     : {show_value(row.MaTep)}"
            )

            print(
                f"MaNguon   : {show_value(row.MaNguon)}"
            )

            print(
                f"TrangThai : {row.TrangThai}"
            )

        # ================================================
        # TONG KET THIEU DU LIEU
        # ================================================
        cursor.execute(
            """
            SELECT
                COUNT(*) AS Tong,

                SUM(
                    CASE
                        WHEN ViDuTiengTrung IS NULL
                          OR LTRIM(RTRIM(ViDuTiengTrung)) = N''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuViDuTrung,

                SUM(
                    CASE
                        WHEN ViDuPinyin IS NULL
                          OR LTRIM(RTRIM(ViDuPinyin)) = N''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuViDuPinyin,

                SUM(
                    CASE
                        WHEN NghiaTiengViet IS NULL
                          OR LTRIM(RTRIM(NghiaTiengViet)) = N''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuNghiaViet,

                SUM(
                    CASE
                        WHEN MaTep IS NULL
                        THEN 1
                        ELSE 0
                    END
                ) AS ChuaCoAudio

            FROM dbo.QuyTacPhatAm
            """
        )

        summary = cursor.fetchone()

        print()
        print("=" * 90)
        print("TONG KET")
        print("=" * 90)

        print(
            "Tong quy tac:",
            summary.Tong
        )

        print(
            "Thieu ViDuTiengTrung:",
            summary.ThieuViDuTrung
        )

        print(
            "Thieu ViDuPinyin:",
            summary.ThieuViDuPinyin
        )

        print(
            "Thieu NghiaTiengViet:",
            summary.ThieuNghiaViet
        )

        print(
            "Chua co audio:",
            summary.ChuaCoAudio
        )

        print()
        print(
            "CHI KIEM TRA - KHONG SUA DATABASE."
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

        print("Loi:", e)

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()