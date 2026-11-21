from pathlib import Path
import sys
import zipfile

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


UNIHAN_ZIP = (
    ROOT_DIR
    / "data_sources"
    / "unicode"
    / "Unihan.zip"
)


def read_vietnamese_readings():
    """
    Đọc trường kVietnamese từ Unihan.
    Trả về:
        {
            '4E00': 'nhất',
            ...
        }
    """
    readings = {}

    if not UNIHAN_ZIP.exists():
        raise FileNotFoundError(
            f"Khong tim thay: {UNIHAN_ZIP}"
        )

    with zipfile.ZipFile(UNIHAN_ZIP, "r") as z:

        # Tìm file Unihan_Readings.txt
        file_name = None

        for name in z.namelist():
            if name.endswith("Unihan_Readings.txt"):
                file_name = name
                break

        if not file_name:
            raise RuntimeError(
                "Khong tim thay Unihan_Readings.txt "
                "trong Unihan.zip."
            )

        with z.open(file_name) as f:

            for raw_line in f:

                line = raw_line.decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                if not line or line.startswith("#"):
                    continue

                parts = line.split("\t")

                if len(parts) < 3:
                    continue

                codepoint = parts[0]
                property_name = parts[1]
                value = parts[2].strip()

                if property_name != "kVietnamese":
                    continue

                codepoint = codepoint.replace(
                    "U+",
                    ""
                ).upper()

                readings[codepoint] = value

    return readings


def main():
    conn = None

    try:
        print("=" * 70)
        print("CAP NHAT TEN HAN-VIET CHO BO THU")
        print("=" * 70)

        readings = read_vietnamese_readings()

        print(
            f"So ky tu co kVietnamese trong Unihan: "
            f"{len(readings)}"
        )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                MaBoThu,
                KyHieu,
                TenBoThu
            FROM dbo.BoThu
            ORDER BY MaBoThu
            """
        )

        rows = cursor.fetchall()

        cap_nhat = 0
        khong_co = 0

        for row in rows:

            ma_bo_thu = row.MaBoThu
            ky_hieu = row.KyHieu

            codepoint = (
                f"{ord(ky_hieu):04X}"
            )

            ten_han_viet = readings.get(
                codepoint
            )

            if not ten_han_viet:
                khong_co += 1
                continue

            # Viết hoa chữ cái đầu
            ten_han_viet = (
                ten_han_viet[:1].upper()
                + ten_han_viet[1:]
            )

            cursor.execute(
                """
                UPDATE dbo.BoThu
                SET TenBoThu = ?
                WHERE MaBoThu = ?
                """,
                ten_han_viet,
                ma_bo_thu,
            )

            cap_nhat += 1

        conn.commit()

        print()
        print(f"Da cap nhat: {cap_nhat}")
        print(
            f"Khong tim thay kVietnamese: "
            f"{khong_co}"
        )

        print("\n20 BO THU DAU TIEN:\n")

        cursor.execute(
            """
            SELECT TOP 20
                MaBoThu,
                KyHieu,
                TenBoThu,
                YNghia,
                SoNet,
                TrangThai
            FROM dbo.BoThu
            ORDER BY MaBoThu
            """
        )

        for row in cursor.fetchall():

            print(
                f"{row.MaBoThu} | "
                f"{row.KyHieu} | "
                f"{row.TenBoThu} | "
                f"SoNet={row.SoNet}"
            )

        print()
        print("=" * 70)
        print("HOAN TAT")
        print("=" * 70)

        cursor.close()

    except Exception as e:

        if conn:
            conn.rollback()

        print()
        print("CAP NHAT THAT BAI")
        print("Loi:", e)

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()