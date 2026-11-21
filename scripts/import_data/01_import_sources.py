from pathlib import Path
import sys
from datetime import datetime

# ==========================================
# ĐƯA THƯ MỤC GỐC D:\DATN1 VÀO PYTHON PATH
# ==========================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Dùng lại kết nối SQL đang có của project
from database import get_connection


# ==========================================
# DANH SÁCH NGUỒN DỮ LIỆU
# ==========================================
NGUON_DU_LIEU = [
    {
        "ten": "Unicode Character Database",
        "lien_ket": "https://www.unicode.org/Public/UCD/latest/ucd/",
        "giay_phep": "Unicode Terms of Use",
        "ghi_chu": (
            "Nguồn Unicode dùng cho dữ liệu CJKRadicals và Unihan. "
            "Phục vụ xác định bộ thủ, chữ Hán, số nét và các thông tin Unicode."
        ),
    },

    {
        "ten": "CC-CEDICT",
        "lien_ket": "https://cc-cedict.org/editor/editor.php?handler=Download",
        "giay_phep": "CC BY-SA 4.0",
        "ghi_chu": (
            "Từ điển Trung - Anh. Hệ thống sử dụng chữ giản thể, "
            "Pinyin và nghĩa gốc để xây dựng dữ liệu từ điển."
        ),
    },

    {
        "ten": "Make Me a Hanzi",
        "lien_ket": "https://github.com/skishore/makemeahanzi",
        "giay_phep": "Theo giấy phép của từng tệp dữ liệu",
        "ghi_chu": (
            "Dùng dictionary.txt và graphics.txt để hỗ trợ dữ liệu chữ Hán "
            "và thông tin nét viết."
        ),
    },

    {
        "ten": "Tatoeba",
        "lien_ket": "https://tatoeba.org/en/downloads",
        "giay_phep": "Theo giấy phép của từng câu và audio",
        "ghi_chu": (
            "Nguồn câu tiếng Trung và audio. "
            "Chỉ sử dụng audio có thông tin giấy phép cho phép tái sử dụng."
        ),
    },

    {
        "ten": "Han Yu Pinyin Fang'an",
        "lien_ket": (
            "https://www.moe.gov.cn/jyb_sjzl/ziliao/"
            "A19/195802/t19580201_186000.html"
        ),
        "giay_phep": None,
        "ghi_chu": (
            "Tài liệu Han Yu Pinyin Fang'an của Bộ Giáo dục Trung Quốc. "
            "Dùng làm nguồn cho thanh mẫu, vận mẫu, thanh điệu "
            "và các quy tắc chính tả Pinyin."
        ),
    },
]


def luu_nguon(cursor, nguon):
    """
    Nếu nguồn đã tồn tại thì cập nhật.
    Nếu chưa có thì thêm mới.
    """

    cursor.execute(
        """
        SELECT MaNguon
        FROM dbo.NguonDuLieu
        WHERE Ten = ?
        """,
        nguon["ten"],
    )

    dong = cursor.fetchone()

    if dong:
        ma_nguon = dong[0]

        cursor.execute(
            """
            UPDATE dbo.NguonDuLieu
            SET LienKetNguon = ?,
                GiayPhep = ?,
                GhiChu = ?,
                NgayLayDuLieu = ?
            WHERE MaNguon = ?
            """,
            nguon["lien_ket"],
            nguon["giay_phep"],
            nguon["ghi_chu"],
            datetime.now(),
            ma_nguon,
        )

        print(f"[CAP NHAT] MaNguon={ma_nguon} - {nguon['ten']}")

    else:
        cursor.execute(
            """
            INSERT INTO dbo.NguonDuLieu
            (
                Ten,
                LienKetNguon,
                GiayPhep,
                GhiChu,
                NgayLayDuLieu
            )
            OUTPUT INSERTED.MaNguon
            VALUES (?, ?, ?, ?, ?)
            """,
            nguon["ten"],
            nguon["lien_ket"],
            nguon["giay_phep"],
            nguon["ghi_chu"],
            datetime.now(),
        )

        ma_nguon = cursor.fetchone()[0]

        print(f"[THEM MOI] MaNguon={ma_nguon} - {nguon['ten']}")


def main():
    conn = None

    try:
        print("=" * 60)
        print("BAT DAU IMPORT NGUON DU LIEU")
        print("=" * 60)

        conn = get_connection()
        cursor = conn.cursor()

        for nguon in NGUON_DU_LIEU:
            luu_nguon(cursor, nguon)

        conn.commit()

        print("=" * 60)
        print("IMPORT NGUON DU LIEU THANH CONG")
        print("=" * 60)

        # Kiểm tra lại dữ liệu
        cursor.execute(
            """
            SELECT
                MaNguon,
                Ten,
                LienKetNguon,
                GiayPhep,
                NgayLayDuLieu
            FROM dbo.NguonDuLieu
            ORDER BY MaNguon
            """
        )

        print("\nDANH SACH NGUON TRONG SQL:\n")

        for row in cursor.fetchall():
            print(
                f"{row.MaNguon} | "
                f"{row.Ten} | "
                f"{row.GiayPhep}"
            )

        cursor.close()

    except Exception as e:
        if conn:
            conn.rollback()

        print("\nIMPORT THAT BAI")
        print("Loi:", e)

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()