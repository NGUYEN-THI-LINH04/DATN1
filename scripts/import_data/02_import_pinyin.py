from pathlib import Path
import sys

# =========================================================
# ĐƯA THƯ MỤC GỐC D:\DATN1 VÀO PYTHON PATH
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# THANH MẪU
# Theo bảng Hanyu Pinyin
# =========================================================
THANH_MAU = [
    "b", "p", "m", "f",
    "d", "t", "n", "l",
    "g", "k", "h",
    "j", "q", "x",
    "zh", "ch", "sh", "r",
    "z", "c", "s"
]


# =========================================================
# 35 VẬN MẪU
# Theo bảng Pinyin người dùng đã lưu trong data_sources/pinyin
# =========================================================
VAN_MAU = [
    "a", "o", "e",
    "ai", "ei", "ao", "ou",
    "an", "en", "ang", "eng", "ong",

    "u", "ua", "uo", "uai", "ui",
    "uan", "uang", "un", "ueng",

    "i", "ia", "ie", "iao", "iu",
    "ian", "iang", "in", "ing", "iong",

    "ü", "üe", "üan", "ün"
]


# =========================================================
# QUY TẮC PHÁT ÂM / CHÍNH TẢ PINYIN
#
# Chỉ đưa các nội dung có trong tài liệu
# 《汉语拼音方案》 đã lưu trong thư mục pinyin.
# =========================================================
QUY_TAC = [
    {
        "ten": "Thanh 1 - Âm bình (阴平)",
        "loai": "thanh_dieu",
        "noi_dung": (
            "Thanh thứ nhất sử dụng dấu ngang trên nguyên âm chính "
            "của âm tiết."
        ),
        "vi_du_trung": None,
        "vi_du_pinyin": "mā",
        "nghia_viet": "Thanh 1, giọng cao và tương đối bằng.",
        "thu_tu": 1,
    },

    {
        "ten": "Thanh 2 - Dương bình (阳平)",
        "loai": "thanh_dieu",
        "noi_dung": (
            "Thanh thứ hai sử dụng dấu sắc trên nguyên âm chính "
            "của âm tiết."
        ),
        "vi_du_trung": None,
        "vi_du_pinyin": "má",
        "nghia_viet": "Thanh 2, cao độ đi lên.",
        "thu_tu": 2,
    },

    {
        "ten": "Thanh 3 - Thượng thanh (上声)",
        "loai": "thanh_dieu",
        "noi_dung": (
            "Thanh thứ ba sử dụng dấu móc trên nguyên âm chính "
            "của âm tiết."
        ),
        "vi_du_trung": None,
        "vi_du_pinyin": "mǎ",
        "nghia_viet": "Thanh 3.",
        "thu_tu": 3,
    },

    {
        "ten": "Thanh 4 - Khứ thanh (去声)",
        "loai": "thanh_dieu",
        "noi_dung": (
            "Thanh thứ tư sử dụng dấu huyền ngược trên nguyên âm chính "
            "của âm tiết."
        ),
        "vi_du_trung": None,
        "vi_du_pinyin": "mà",
        "nghia_viet": "Thanh 4, cao độ đi xuống.",
        "thu_tu": 4,
    },

    {
        "ten": "Thanh nhẹ (轻声)",
        "loai": "thanh_dieu",
        "noi_dung": (
            "Âm tiết đọc thanh nhẹ không ghi ký hiệu thanh điệu."
        ),
        "vi_du_trung": None,
        "vi_du_pinyin": "ma",
        "nghia_viet": "Thanh nhẹ không có dấu thanh.",
        "thu_tu": 5,
    },

    {
        "ten": "Cách viết iou, uei, uen sau thanh mẫu",
        "loai": "chinh_ta",
        "noi_dung": (
            "Khi iou, uei và uen đứng sau một thanh mẫu, "
            "chúng được viết rút gọn lần lượt thành iu, ui và un."
        ),
        "vi_du_trung": None,
        "vi_du_pinyin": "liu, gui, lun",
        "nghia_viet": (
            "Quy tắc viết rút gọn một số vận mẫu khi có thanh mẫu đứng trước."
        ),
        "thu_tu": 6,
    },

    {
        "ten": "Cách viết âm tiết bắt đầu bằng i",
        "loai": "chinh_ta",
        "noi_dung": (
            "Khi âm tiết thuộc nhóm bắt đầu bằng i không có thanh mẫu đứng trước, "
            "chữ y được sử dụng theo quy tắc chính tả Hanyu Pinyin."
        ),
        "vi_du_trung": None,
        "vi_du_pinyin": "yi, ya, ye, yao, you, yan, yin, yang, ying, yong",
        "nghia_viet": (
            "Dùng y khi viết các âm tiết nhóm i không có thanh mẫu."
        ),
        "thu_tu": 7,
    },

    {
        "ten": "Cách viết âm tiết bắt đầu bằng u",
        "loai": "chinh_ta",
        "noi_dung": (
            "Khi âm tiết thuộc nhóm bắt đầu bằng u không có thanh mẫu đứng trước, "
            "chữ w được sử dụng theo quy tắc chính tả Hanyu Pinyin."
        ),
        "vi_du_trung": None,
        "vi_du_pinyin": "wu, wa, wo, wai, wei, wan, wang, wen, weng",
        "nghia_viet": (
            "Dùng w khi viết các âm tiết nhóm u không có thanh mẫu."
        ),
        "thu_tu": 8,
    },

    {
        "ten": "Cách viết nhóm ü khi không có thanh mẫu",
        "loai": "chinh_ta",
        "noi_dung": (
            "Khi các âm tiết thuộc nhóm ü không có thanh mẫu đứng trước, "
            "chữ y được thêm vào và hai chấm trên ü được bỏ."
        ),
        "vi_du_trung": None,
        "vi_du_pinyin": "yu, yue, yuan, yun",
        "nghia_viet": (
            "Quy tắc viết các âm tiết thuộc nhóm ü khi không có thanh mẫu."
        ),
        "thu_tu": 9,
    },

    {
        "ten": "Cách viết ü sau j, q, x",
        "loai": "chinh_ta",
        "noi_dung": (
            "Khi ü đứng sau j, q hoặc x, hai chấm phía trên ü được bỏ "
            "trong cách viết Hanyu Pinyin."
        ),
        "vi_du_trung": None,
        "vi_du_pinyin": "ju, qu, xu",
        "nghia_viet": (
            "Sau j, q, x, âm ü được viết bằng chữ u."
        ),
        "thu_tu": 10,
    },

    {
        "ten": "Dấu cách âm (隔音符号)",
        "loai": "chinh_ta",
        "noi_dung": (
            "Khi một âm tiết bắt đầu bằng a, o hoặc e đứng sau một âm tiết khác "
            "và ranh giới âm tiết có thể gây nhầm lẫn, dấu nháy đơn được dùng "
            "để phân cách."
        ),
        "vi_du_trung": None,
        "vi_du_pinyin": "pi'ao",
        "nghia_viet": "Dùng dấu nháy đơn để thể hiện rõ ranh giới âm tiết.",
        "thu_tu": 11,
    },
]


# =========================================================
# LẤY MÃ NGUỒN
# =========================================================
def get_source_id(cursor, ten_nguon):
    cursor.execute(
        """
        SELECT MaNguon
        FROM dbo.NguonDuLieu
        WHERE Ten = ?
        """,
        ten_nguon,
    )

    row = cursor.fetchone()

    if not row:
        raise RuntimeError(
            f"Khong tim thay nguon du lieu: {ten_nguon}. "
            "Hay chay 01_import_sources.py truoc."
        )

    return row[0]


# =========================================================
# THÊM / CẬP NHẬT BẢNG PINYIN
# =========================================================
def upsert_pinyin(
    cursor,
    loai_am,
    ky_hieu,
    cach_doc,
    vi_du,
    ma_nguon,
    thu_tu,
):
    cursor.execute(
        """
        SELECT MaPinyin
        FROM dbo.BangPinyin
        WHERE LoaiAm = ?
          AND KyHieu = ?
        """,
        loai_am,
        ky_hieu,
    )

    row = cursor.fetchone()

    if row:
        cursor.execute(
            """
            UPDATE dbo.BangPinyin
            SET CachDoc = ?,
                ViDu = ?,
                MaNguon = ?,
                ThuTu = ?,
                TrangThai = 'da_xuat_ban'
            WHERE MaPinyin = ?
            """,
            cach_doc,
            vi_du,
            ma_nguon,
            thu_tu,
            row[0],
        )

        return "cap_nhat"

    cursor.execute(
        """
        INSERT INTO dbo.BangPinyin
        (
            LoaiAm,
            KyHieu,
            CachDoc,
            ViDu,
            MaTep,
            MaNguon,
            ThuTu,
            TrangThai
        )
        VALUES (?, ?, ?, ?, NULL, ?, ?, 'da_xuat_ban')
        """,
        loai_am,
        ky_hieu,
        cach_doc,
        vi_du,
        ma_nguon,
        thu_tu,
    )

    return "them"


# =========================================================
# THÊM / CẬP NHẬT QUY TẮC PHÁT ÂM
# =========================================================
def upsert_rule(cursor, rule, ma_nguon):
    cursor.execute(
        """
        SELECT MaQuyTac
        FROM dbo.QuyTacPhatAm
        WHERE TenQuyTac = ?
        """,
        rule["ten"],
    )

    row = cursor.fetchone()

    if row:
        cursor.execute(
            """
            UPDATE dbo.QuyTacPhatAm
            SET LoaiQuyTac = ?,
                NoiDung = ?,
                ViDuTiengTrung = ?,
                ViDuPinyin = ?,
                NghiaTiengViet = ?,
                MaNguon = ?,
                ThuTu = ?,
                TrangThai = 'da_xuat_ban'
            WHERE MaQuyTac = ?
            """,
            rule["loai"],
            rule["noi_dung"],
            rule["vi_du_trung"],
            rule["vi_du_pinyin"],
            rule["nghia_viet"],
            ma_nguon,
            rule["thu_tu"],
            row[0],
        )

        return "cap_nhat"

    cursor.execute(
        """
        INSERT INTO dbo.QuyTacPhatAm
        (
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
        )
        VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, 'da_xuat_ban')
        """,
        rule["ten"],
        rule["loai"],
        rule["noi_dung"],
        rule["vi_du_trung"],
        rule["vi_du_pinyin"],
        rule["nghia_viet"],
        ma_nguon,
        rule["thu_tu"],
    )

    return "them"


# =========================================================
# MAIN
# =========================================================
def main():
    conn = None

    try:
        print("=" * 65)
        print("BAT DAU IMPORT PINYIN")
        print("=" * 65)

        conn = get_connection()
        cursor = conn.cursor()

        ma_nguon = get_source_id(
            cursor,
            "Han Yu Pinyin Fang'an"
        )

        print(f"MaNguon Pinyin: {ma_nguon}")
        print()

        them_pinyin = 0
        cap_nhat_pinyin = 0

        # -------------------------------------------------
        # THANH MẪU
        # -------------------------------------------------
        for index, ky_hieu in enumerate(THANH_MAU, start=1):
            result = upsert_pinyin(
                cursor=cursor,
                loai_am="thanh_mau",
                ky_hieu=ky_hieu,
                cach_doc=None,
                vi_du=None,
                ma_nguon=ma_nguon,
                thu_tu=index,
            )

            if result == "them":
                them_pinyin += 1
            else:
                cap_nhat_pinyin += 1

        # -------------------------------------------------
        # VẬN MẪU
        # -------------------------------------------------
        for index, ky_hieu in enumerate(VAN_MAU, start=1):
            result = upsert_pinyin(
                cursor=cursor,
                loai_am="van_mau",
                ky_hieu=ky_hieu,
                cach_doc=None,
                vi_du=None,
                ma_nguon=ma_nguon,
                thu_tu=index,
            )

            if result == "them":
                them_pinyin += 1
            else:
                cap_nhat_pinyin += 1

        # -------------------------------------------------
        # QUY TẮC
        # -------------------------------------------------
        them_quy_tac = 0
        cap_nhat_quy_tac = 0

        for rule in QUY_TAC:
            result = upsert_rule(
                cursor,
                rule,
                ma_nguon,
            )

            if result == "them":
                them_quy_tac += 1
            else:
                cap_nhat_quy_tac += 1

        conn.commit()

        print("IMPORT THANH CONG")
        print("-" * 65)

        print(
            f"BangPinyin: them {them_pinyin}, "
            f"cap nhat {cap_nhat_pinyin}"
        )

        print(
            f"QuyTacPhatAm: them {them_quy_tac}, "
            f"cap nhat {cap_nhat_quy_tac}"
        )

        # -------------------------------------------------
        # KIỂM TRA KẾT QUẢ
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT LoaiAm, COUNT(*) AS SoLuong
            FROM dbo.BangPinyin
            GROUP BY LoaiAm
            ORDER BY LoaiAm
            """
        )

        print("\nSO LUONG PINYIN TRONG SQL:")

        for row in cursor.fetchall():
            print(
                f"{row.LoaiAm}: {row.SoLuong}"
            )

        cursor.execute(
            """
            SELECT COUNT(*) AS SoLuong
            FROM dbo.QuyTacPhatAm
            """
        )

        so_quy_tac = cursor.fetchone()[0]

        print(
            f"\nTong so quy tac phat am: {so_quy_tac}"
        )

        print("=" * 65)
        print("HOAN TAT")
        print("=" * 65)

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