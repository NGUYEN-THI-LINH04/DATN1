from pathlib import Path
import sys
import re
import zipfile


# =========================================================
# THƯ MỤC GỐC D:\DATN1
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# ĐƯỜNG DẪN NGUỒN
# =========================================================
CJK_RADICALS_FILE = (
    ROOT_DIR
    / "data_sources"
    / "unicode"
    / "CJKRadicals.txt"
)

UNIHAN_ZIP_FILE = (
    ROOT_DIR
    / "data_sources"
    / "unicode"
    / "Unihan.zip"
)


# =========================================================
# CHUYỂN HEX UNICODE THÀNH KÝ TỰ
# Ví dụ:
# 4E00 -> 一
# =========================================================
def codepoint_to_char(codepoint):
    if not codepoint:
        return None

    return chr(int(codepoint, 16))


# =========================================================
# ĐỌC CJKRadicals.txt
# =========================================================
def read_cjk_radicals():
    if not CJK_RADICALS_FILE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {CJK_RADICALS_FILE}"
        )

    radicals = []
    variant_count = 0

    with open(
        CJK_RADICALS_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:
            line = line.strip()

            # Bỏ dòng trống và comment
            if not line or line.startswith("#"):
                continue

            parts = [
                part.strip()
                for part in line.split(";")
            ]

            if len(parts) != 3:
                continue

            radical_number = parts[0]
            radical_codepoint = parts[1]
            ideograph_codepoint = parts[2]

            # ---------------------------------------------
            # Chỉ lấy 214 bộ chính.
            #
            # Ví dụ lấy:
            # 1
            # 2
            # ...
            # 214
            #
            # Không lấy:
            # 90'
            # 120'
            # 182''
            # ...
            # ---------------------------------------------
            if not radical_number.isdigit():
                variant_count += 1
                continue

            number = int(radical_number)

            if not 1 <= number <= 214:
                continue

            ky_hieu = codepoint_to_char(
                ideograph_codepoint
            )

            radical_symbol = codepoint_to_char(
                radical_codepoint
            )

            radicals.append(
                {
                    "so_bo": number,
                    "ky_hieu": ky_hieu,
                    "radical_symbol": radical_symbol,
                    "radical_codepoint": radical_codepoint,
                    "ideograph_codepoint": ideograph_codepoint,
                }
            )

    radicals.sort(
        key=lambda item: item["so_bo"]
    )

    return radicals, variant_count


# =========================================================
# ĐỌC kTotalStrokes TỪ Unihan.zip
#
# Không phụ thuộc kTotalStrokes nằm trong file txt nào.
# Script sẽ tìm trong toàn bộ các file .txt bên trong ZIP.
# =========================================================
def read_unihan_total_strokes():
    strokes = {}

    if not UNIHAN_ZIP_FILE.exists():
        print(
            "CANH BAO: Khong tim thay Unihan.zip."
        )
        print(
            "SoNet se duoc de NULL."
        )
        return strokes

    with zipfile.ZipFile(
        UNIHAN_ZIP_FILE,
        "r",
    ) as zip_file:

        txt_files = [
            name
            for name in zip_file.namelist()
            if name.lower().endswith(".txt")
        ]

        for file_name in txt_files:

            with zip_file.open(file_name) as f:

                for raw_line in f:

                    try:
                        line = raw_line.decode(
                            "utf-8"
                        ).strip()
                    except UnicodeDecodeError:
                        continue

                    if (
                        not line
                        or line.startswith("#")
                    ):
                        continue

                    parts = line.split("\t")

                    if len(parts) < 3:
                        continue

                    codepoint = parts[0]
                    property_name = parts[1]
                    value = parts[2]

                    if property_name != "kTotalStrokes":
                        continue

                    # U+4E00 -> 4E00
                    codepoint = codepoint.replace(
                        "U+",
                        "",
                    ).upper()

                    # Một số giá trị có thể chứa
                    # nhiều số. Lấy số đầu tiên.
                    match = re.search(
                        r"\d+",
                        value,
                    )

                    if match:
                        strokes[codepoint] = int(
                            match.group()
                        )

    return strokes


# =========================================================
# LẤY MÃ NGUỒN UNICODE
# =========================================================
def get_unicode_source_id(cursor):
    cursor.execute(
        """
        SELECT MaNguon
        FROM dbo.NguonDuLieu
        WHERE Ten = ?
        """,
        "Unicode Character Database",
    )

    row = cursor.fetchone()

    if not row:
        raise RuntimeError(
            "Khong tim thay nguon "
            "'Unicode Character Database'. "
            "Hay chay 01_import_sources.py truoc."
        )

    return row[0]


# =========================================================
# THÊM / CẬP NHẬT BỘ THỦ
# =========================================================
def upsert_radical(
    cursor,
    radical,
    so_net,
    ma_nguon,
):
    ky_hieu = radical["ky_hieu"]
    so_bo = radical["so_bo"]

    # Vì nguồn Unicode không chứa tên Hán-Việt,
    # đây chỉ là tên kỹ thuật tạm thời.
    ten_tam = f"Bộ thủ số {so_bo}"

    mo_ta_unicode = (
        f"Kangxi radical số {so_bo}; "
        f"radical symbol U+"
        f"{radical['radical_codepoint']}; "
        f"CJK unified ideograph U+"
        f"{radical['ideograph_codepoint']}."
    )

    cursor.execute(
        """
        SELECT
            MaBoThu,
            TenBoThu,
            YNghia,
            MoTa,
            SoNet
        FROM dbo.BoThu
        WHERE KyHieu = ?
        """,
        ky_hieu,
    )

    row = cursor.fetchone()

    # =====================================================
    # ĐÃ TỒN TẠI
    # =====================================================
    if row:

        ma_bo_thu = row[0]
        ten_hien_tai = row[1]
        y_nghia_hien_tai = row[2]
        mo_ta_hien_tai = row[3]
        so_net_hien_tai = row[4]

        # Nếu sau này đã nhập tên Hán-Việt thật
        # thì không ghi đè bằng tên tạm.
        if (
            ten_hien_tai
            and not ten_hien_tai.startswith(
                "Bộ thủ số "
            )
        ):
            ten_moi = ten_hien_tai
        else:
            ten_moi = ten_tam

        # Không ghi đè mô tả đã được biên tập.
        if mo_ta_hien_tai:
            mo_ta_moi = mo_ta_hien_tai
        else:
            mo_ta_moi = mo_ta_unicode

        # Ưu tiên số nét lấy từ Unihan.
        if so_net is not None:
            so_net_moi = so_net
        else:
            so_net_moi = so_net_hien_tai

        cursor.execute(
            """
            UPDATE dbo.BoThu
            SET TenBoThu = ?,
                SoNet = ?,
                MoTa = ?,
                MaNguon = ?
            WHERE MaBoThu = ?
            """,
            ten_moi,
            so_net_moi,
            mo_ta_moi,
            ma_nguon,
            ma_bo_thu,
        )

        return "cap_nhat"

    # =====================================================
    # CHƯA TỒN TẠI
    # =====================================================
    cursor.execute(
        """
        INSERT INTO dbo.BoThu
        (
            KyHieu,
            TenBoThu,
            YNghia,
            SoNet,
            MoTa,
            MaTep,
            MaNguon,
            TrangThai
        )
        VALUES
        (
            ?, ?, NULL, ?, ?,
            NULL, ?, 'ban_nhap'
        )
        """,
        ky_hieu,
        ten_tam,
        so_net,
        mo_ta_unicode,
        ma_nguon,
    )

    return "them"


# =========================================================
# MAIN
# =========================================================
def main():
    conn = None

    try:
        print("=" * 70)
        print("BAT DAU IMPORT 214 BO THU")
        print("=" * 70)

        # -------------------------------------------------
        # ĐỌC CJK RADICALS
        # -------------------------------------------------
        radicals, variant_count = (
            read_cjk_radicals()
        )

        print(
            f"So bo thu chinh doc duoc: "
            f"{len(radicals)}"
        )

        print(
            f"So bien the Unicode bo qua: "
            f"{variant_count}"
        )

        # Phải đúng 214 mới cho import
        if len(radicals) != 214:
            raise RuntimeError(
                "Du lieu bo thu chinh khong du 214. "
                f"Hien doc duoc {len(radicals)}."
            )

        # -------------------------------------------------
        # ĐỌC UNIHAN
        # -------------------------------------------------
        print(
            "\nDang doc SoNet tu Unihan.zip..."
        )

        stroke_map = (
            read_unihan_total_strokes()
        )

        print(
            "So ky tu co kTotalStrokes: "
            f"{len(stroke_map)}"
        )

        # -------------------------------------------------
        # SQL
        # -------------------------------------------------
        conn = get_connection()
        cursor = conn.cursor()

        ma_nguon = get_unicode_source_id(
            cursor
        )

        print(
            f"MaNguon Unicode: {ma_nguon}"
        )

        them = 0
        cap_nhat = 0
        co_so_net = 0
        thieu_so_net = 0

        for radical in radicals:

            codepoint = (
                radical[
                    "ideograph_codepoint"
                ].upper()
            )

            so_net = stroke_map.get(
                codepoint
            )

            if so_net is not None:
                co_so_net += 1
            else:
                thieu_so_net += 1

            result = upsert_radical(
                cursor=cursor,
                radical=radical,
                so_net=so_net,
                ma_nguon=ma_nguon,
            )

            if result == "them":
                them += 1
            else:
                cap_nhat += 1

        conn.commit()

        # -------------------------------------------------
        # KIỂM TRA
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.BoThu
            """
        )

        total_sql = cursor.fetchone()[0]

        print()
        print("-" * 70)
        print("IMPORT THANH CONG")
        print("-" * 70)

        print(
            f"Them moi: {them}"
        )

        print(
            f"Cap nhat: {cap_nhat}"
        )

        print(
            f"Co SoNet tu Unihan: "
            f"{co_so_net}"
        )

        print(
            f"Chua co SoNet: "
            f"{thieu_so_net}"
        )

        print(
            f"Tong so dong BoThu "
            f"trong SQL: {total_sql}"
        )

        print(
            "\n10 BO THU DAU TIEN:"
        )

        cursor.execute(
            """
            SELECT TOP 10
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
                f"SoNet={row.SoNet} | "
                f"{row.TrangThai}"
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
        print("IMPORT THAT BAI")
        print("Loi:", e)

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()