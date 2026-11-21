from pathlib import Path
import sys
import re
from urllib.request import Request, urlopen
from html.parser import HTMLParser


# =========================================================
# THƯ MỤC GỐC D:\DATN1
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# NGUỒN TÊN HÁN-VIỆT
# =========================================================
SOURCE_NAME = "Từ điển Hán Nôm - Thi Viện"
SOURCE_URL = "https://hvdic.thivien.net/rad-hv"

SOURCE_NOTE = (
    "Nguồn tham khảo tên Hán-Việt của hệ thống "
    "214 bộ thủ Khang Hy."
)


# =========================================================
# HTML PARSER
# LẤY NỘI DUNG TRONG CÁC THẺ <a>
# =========================================================
class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_anchor = False
        self.current_text = []
        self.anchor_texts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self.in_anchor = True
            self.current_text = []

    def handle_data(self, data):
        if self.in_anchor:
            self.current_text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self.in_anchor:
            text = "".join(self.current_text).strip()

            if text:
                self.anchor_texts.append(text)

            self.in_anchor = False
            self.current_text = []


# =========================================================
# THÊM NGUỒN HÁN-VIỆT NẾU CHƯA CÓ
# =========================================================
def get_or_create_source(cursor):
    cursor.execute(
        """
        SELECT MaNguon
        FROM dbo.NguonDuLieu
        WHERE Ten = ?
        """,
        SOURCE_NAME,
    )

    row = cursor.fetchone()

    if row:
        return row[0]

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
        VALUES
        (
            ?,
            ?,
            NULL,
            ?,
            SYSDATETIME()
        )
        """,
        SOURCE_NAME,
        SOURCE_URL,
        SOURCE_NOTE,
    )

    return cursor.fetchone()[0]


# =========================================================
# TẢI DANH SÁCH TÊN HÁN-VIỆT CỦA 214 BỘ
# =========================================================
def download_radical_names(valid_characters):
    print("Dang tai danh sach ten Han-Viet...")

    request = Request(
        SOURCE_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "HocTiengTrungDB/1.0"
            )
        },
    )

    with urlopen(
        request,
        timeout=30,
    ) as response:

        html = response.read().decode(
            "utf-8",
            errors="ignore",
        )

    parser = AnchorParser()
    parser.feed(html)

    mapping = {}

    # -----------------------------------------------------
    # Trang nguồn có dạng:
    #
    # 一 nhất
    # 丨 cổn
    # 丶 chủ
    # ...
    #
    # Ta chỉ lấy các ký tự nằm trong bảng BoThu.
    #
    # Riêng 青 được cho phép vì Unicode CJKRadicals
    # dùng dị thể 靑 cho bộ 174.
    # -----------------------------------------------------
    for text in parser.anchor_texts:

        text = " ".join(text.split())

        match = re.match(
            r"^(\S)\s+(.+)$",
            text,
        )

        if not match:
            continue

        character = match.group(1)
        reading = match.group(2).strip()

        if (
            character not in valid_characters
            and character != "青"
        ):
            continue

        if not reading:
            continue

        mapping[character] = reading

    # -----------------------------------------------------
    # XỬ LÝ RIÊNG BỘ 174
    #
    # Unicode CJKRadicals dùng:
    # 靑 U+9751
    #
    # Nguồn Hán-Việt dùng:
    # 青 U+9752
    #
    # Hai ký tự là dị thể.
    # -----------------------------------------------------
    if "青" in mapping and "靑" not in mapping:
        mapping["靑"] = mapping["青"]

    return mapping


# =========================================================
# VIẾT HOA CHỮ CÁI ĐẦU
# =========================================================
def capitalize_name(value):
    value = value.strip()

    if not value:
        return value

    return value[0].upper() + value[1:]


# =========================================================
# MAIN
# =========================================================
def main():
    conn = None

    try:
        print("=" * 72)
        print("CHUAN HOA TEN HAN-VIET CHO 214 BO THU")
        print("=" * 72)

        conn = get_connection()
        cursor = conn.cursor()

        # -------------------------------------------------
        # ĐỌC 214 BỘ ĐANG CÓ TRONG SQL
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                MaBoThu,
                KyHieu,
                TenBoThu,
                MoTa,
                MaNguon
            FROM dbo.BoThu
            ORDER BY MaBoThu
            """
        )

        rows = cursor.fetchall()

        if len(rows) != 214:
            raise RuntimeError(
                "Bang BoThu hien khong co dung 214 dong. "
                f"Hien tai co {len(rows)} dong."
            )

        valid_characters = {
            row.KyHieu
            for row in rows
        }

        print(
            f"So bo thu trong SQL: "
            f"{len(valid_characters)}"
        )

        # -------------------------------------------------
        # TẠO / LẤY NGUỒN HÁN-VIỆT
        # -------------------------------------------------
        ma_nguon_han_viet = (
            get_or_create_source(cursor)
        )

        print(
            "MaNguon ten Han-Viet: "
            f"{ma_nguon_han_viet}"
        )

        # -------------------------------------------------
        # TẢI TÊN HÁN-VIỆT
        # -------------------------------------------------
        name_map = download_radical_names(
            valid_characters
        )

        print(
            "So ten Han-Viet tim duoc: "
            f"{len(name_map)}"
        )

        # -------------------------------------------------
        # KIỂM TRA:
        # KHÔNG CẦN mapping = 214 CHÍNH XÁC
        #
        # Vì mapping có thể có cả 青 và 靑.
        # Quan trọng là 214 ký tự trong SQL
        # đều phải tìm được tên.
        # -------------------------------------------------
        missing = (
            valid_characters
            - set(name_map.keys())
        )

        if missing:

            print()
            print(
                "Khong du ten cho 214 bo thu."
            )

            print(
                "Cac ky tu con thieu:"
            )

            print(
                " ".join(
                    sorted(missing)
                )
            )

            raise RuntimeError(
                "Dung cap nhat de tranh ghi "
                "du lieu khong day du."
            )

        # -------------------------------------------------
        # CẬP NHẬT SQL
        # -------------------------------------------------
        updated = 0

        source_note = (
            f"Nguồn tên Hán-Việt: "
            f"MaNguon={ma_nguon_han_viet} - "
            f"{SOURCE_NAME} - "
            f"{SOURCE_URL}"
        )

        for row in rows:

            ky_hieu = row.KyHieu

            new_name = capitalize_name(
                name_map[ky_hieu]
            )

            old_description = (
                row.MoTa or ""
            ).strip()

            # Không thêm ghi chú nguồn trùng
            # nếu chạy script nhiều lần.
            if SOURCE_URL not in old_description:

                if old_description:
                    new_description = (
                        old_description
                        + " "
                        + source_note
                    )
                else:
                    new_description = (
                        source_note
                    )

            else:
                new_description = (
                    old_description
                )

            # -------------------------------------------------
            # KHÔNG đổi MaNguon của BoThu.
            #
            # Vì nguồn chính của:
            # - KyHieu
            # - SoNet
            #
            # vẫn là Unicode.
            #
            # Nguồn tên Hán-Việt được ghi trong MoTa.
            # -------------------------------------------------
            cursor.execute(
                """
                UPDATE dbo.BoThu
                SET
                    TenBoThu = ?,
                    MoTa = ?
                WHERE MaBoThu = ?
                """,
                new_name,
                new_description,
                row.MaBoThu,
            )

            updated += 1

        conn.commit()

        # -------------------------------------------------
        # KIỂM TRA KẾT QUẢ
        # -------------------------------------------------
        print()
        print("-" * 72)
        print("CAP NHAT THANH CONG")
        print("-" * 72)

        print(
            f"So bo thu da chuan hoa: "
            f"{updated}"
        )

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.BoThu
            WHERE TenBoThu LIKE N'Bộ thủ số %'
            """
        )

        temporary_names = (
            cursor.fetchone()[0]
        )

        print(
            "So ten tam con lai: "
            f"{temporary_names}"
        )

        # -------------------------------------------------
        # KIỂM TRA RIÊNG BỘ 174
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                MaBoThu,
                KyHieu,
                TenBoThu,
                SoNet
            FROM dbo.BoThu
            WHERE KyHieu = N'靑'
            """
        )

        radical_174 = cursor.fetchone()

        if radical_174:

            print()
            print("KIEM TRA BO 174:")

            print(
                f"{radical_174.MaBoThu} | "
                f"{radical_174.KyHieu} | "
                f"{radical_174.TenBoThu} | "
                f"SoNet={radical_174.SoNet}"
            )

        # -------------------------------------------------
        # HIỂN THỊ 20 BỘ ĐẦU
        # -------------------------------------------------
        print()
        print("20 BO THU DAU TIEN:")
        print()

        cursor.execute(
            """
            SELECT TOP 20
                MaBoThu,
                KyHieu,
                TenBoThu,
                YNghia,
                SoNet,
                MaNguon,
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
                f"Nguon={row.MaNguon} | "
                f"{row.TrangThai}"
            )

        print()
        print("=" * 72)
        print("HOAN TAT")
        print("=" * 72)

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