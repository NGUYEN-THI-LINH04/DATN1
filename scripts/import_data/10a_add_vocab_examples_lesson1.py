from pathlib import Path
import sys


# ============================================================
# ROOT PROJECT
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from database import get_connection


# ============================================================
# DỮ LIỆU VÍ DỤ BÀI 1
# ============================================================

EXAMPLES = [
    (8, "你", "你好吗？", "Bạn khỏe không?"),
    (2, "好", "我很好。", "Tôi rất khỏe."),
    (12, "我", "我是学生。", "Tôi là học sinh."),
    (11, "是", "他是老师。", "Anh ấy là giáo viên."),
    (4, "叫", "我叫安娜。", "Tôi tên là Anna."),
    (10, "什么", "你叫什么名字？", "Bạn tên là gì?"),
    (6, "名字", "我的名字是安娜。", "Tên của tôi là Anna."),
    (3, "很", "我很高兴。", "Tôi rất vui."),
    (
        1,
        "高兴",
        "认识你很高兴。",
        "Rất vui được làm quen với bạn.",
    ),
    (9, "认识", "我认识他。", "Tôi biết anh ấy."),
    (
        5,
        "吗",
        "你是学生吗？",
        "Bạn là học sinh phải không?",
    ),
    (
        7,
        "呢",
        "我很好，你呢？",
        "Tôi khỏe, còn bạn thì sao?",
    ),
    (13, "也", "我也是学生。", "Tôi cũng là học sinh."),
]


def main():

    conn = None

    try:

        print("=" * 70)
        print("BỔ SUNG VÍ DỤ TỪ VỰNG HSK1 - BÀI 1")
        print("=" * 70)

        # ====================================================
        # 1. KẾT NỐI DATABASE
        # ====================================================

        conn = get_connection()

        conn.autocommit = False

        cursor = conn.cursor()

        print()
        print("[1] Kết nối database: OK")


        # ====================================================
        # 2. KIỂM TRA 13 TỪ CÓ ĐÚNG TRONG BÀI 1 KHÔNG
        # ====================================================

        print()
        print("[2] Kiểm tra dữ liệu trước khi cập nhật")

        for ma_tu_vung, chu_han, vi_du_trung, vi_du_viet in EXAMPLES:

            cursor.execute(
                """
                SELECT
                    tv.MaTuVung,
                    tv.ChuHan

                FROM TuVung tv

                INNER JOIN TuVungBaiHoc tvbh
                    ON tvbh.MaTuVung = tv.MaTuVung

                WHERE tv.MaTuVung = ?
                  AND tv.ChuHan = ?
                  AND tvbh.MaBaiHoc = 1
                """,
                ma_tu_vung,
                chu_han,
            )

            row = cursor.fetchone()

            if row is None:

                raise RuntimeError(
                    f"Không tìm thấy đúng từ: "
                    f"{ma_tu_vung} - {chu_han}"
                )

            print(
                f"OK | MaTuVung={ma_tu_vung:<3} | {chu_han}"
            )


        # ====================================================
        # 3. UPDATE VÍ DỤ
        # ====================================================

        print()
        print("[3] Cập nhật ví dụ")

        updated = 0

        for ma_tu_vung, chu_han, vi_du_trung, vi_du_viet in EXAMPLES:

            cursor.execute(
                """
                UPDATE TuVung

                SET
                    ViDuTiengTrung = ?,
                    ViDuTiengViet = ?

                WHERE MaTuVung = ?
                  AND ChuHan = ?
                """,
                vi_du_trung,
                vi_du_viet,
                ma_tu_vung,
                chu_han,
            )

            if cursor.rowcount != 1:

                raise RuntimeError(
                    f"Update lỗi: "
                    f"{ma_tu_vung} - {chu_han}"
                )

            updated += 1

            print(
                f"Đã cập nhật | {chu_han} | {vi_du_trung}"
            )


        # ====================================================
        # 4. AUDIT LẠI BÀI 1
        # ====================================================

        cursor.execute(
            """
            SELECT
                COUNT(*) AS TongTu,

                SUM(
                    CASE
                        WHEN ViDuTiengTrung IS NULL
                          OR LTRIM(RTRIM(ViDuTiengTrung)) = ''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuTrung,

                SUM(
                    CASE
                        WHEN ViDuTiengViet IS NULL
                          OR LTRIM(RTRIM(ViDuTiengViet)) = ''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuViet

            FROM TuVung tv

            INNER JOIN TuVungBaiHoc tvbh
                ON tvbh.MaTuVung = tv.MaTuVung

            WHERE tvbh.MaBaiHoc = 1
            """
        )

        result = cursor.fetchone()

        tong_tu = result.TongTu
        thieu_trung = result.ThieuTrung
        thieu_viet = result.ThieuViet


        print()
        print("[4] Kết quả audit")

        print(
            "Tổng từ:",
            tong_tu,
        )

        print(
            "Thiếu ví dụ Trung:",
            thieu_trung,
        )

        print(
            "Thiếu ví dụ Việt:",
            thieu_viet,
        )


        # ====================================================
        # 5. CHỈ COMMIT KHI ĐÚNG
        # ====================================================

        if (
            tong_tu == 13
            and thieu_trung == 0
            and thieu_viet == 0
        ):

            conn.commit()

            print()
            print(
                "✅ BÀI 1 ĐÃ CẬP NHẬT VÍ DỤ THÀNH CÔNG."
            )

        else:

            conn.rollback()

            print()
            print(
                "❌ Kết quả chưa đúng."
            )

            print(
                "Đã rollback, database không bị thay đổi."
            )


    except Exception as error:

        if conn is not None:

            conn.rollback()

        print()
        print("❌ CÓ LỖI:")
        print(error)

        print()
        print(
            "Database đã rollback."
        )


    finally:

        if conn is not None:

            conn.close()

        print()
        print("Đã đóng kết nối.")


if __name__ == "__main__":
    main()