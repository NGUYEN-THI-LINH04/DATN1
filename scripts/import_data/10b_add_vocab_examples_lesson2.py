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
# HSK1 - BÀI 2
# 我是越南人 - Tôi là người Việt Nam
#
# Chỉ bổ sung:
#   ViDuTiengTrung
#   ViDuTiengViet
#
# Không sửa:
#   ChuHan
#   PhienAm
#   NghiaTiengViet
#   TuLoai
#   MaNguon
# ============================================================

LESSON_ID = 2
EXPECTED_COUNT = 29


EXAMPLES = [

    (
        140,
        "国",
        "中国、越南都是国家。",
        "Trung Quốc và Việt Nam đều là các quốc gia.",
    ),

    (
        141,
        "国家",
        "越南是我的国家。",
        "Việt Nam là đất nước của tôi.",
    ),

    (
        142,
        "国外",
        "他在国外学习汉语。",
        "Anh ấy học tiếng Trung ở nước ngoài.",
    ),

    (
        148,
        "汉语",
        "我学习汉语。",
        "Tôi học tiếng Trung.",
    ),

    (
        149,
        "汉字",
        "我学习汉字。",
        "Tôi học chữ Hán.",
    ),

    (
        188,
        "介绍",
        "我介绍一下自己。",
        "Tôi xin giới thiệu một chút về bản thân.",
    ),

    (
        268,
        "男",
        "他是男的。",
        "Anh ấy là nam.",
    ),

    (
        271,
        "男人",
        "那个男人是我爸爸。",
        "Người đàn ông kia là bố tôi.",
    ),

    (
        272,
        "男生",
        "他是男生。",
        "Anh ấy là học sinh nam.",
    ),

    (
        277,
        "你们",
        "你们是学生吗？",
        "Các bạn là học sinh phải không?",
    ),

    (
        279,
        "您",
        "您好，老师！",
        "Em chào thầy/cô ạ!",
    ),

    (
        281,
        "女",
        "她是女的。",
        "Cô ấy là nữ.",
    ),

    (
        285,
        "女人",
        "那个女人是我妈妈。",
        "Người phụ nữ kia là mẹ tôi.",
    ),

    (
        286,
        "女生",
        "她是女生。",
        "Cô ấy là học sinh nữ.",
    ),

    (
        310,
        "人",
        "这里有很多人。",
        "Ở đây có rất nhiều người.",
    ),

    (
        329,
        "谁",
        "他是谁？",
        "Anh ấy là ai?",
    ),

    (
        356,
        "他",
        "他是我的朋友。",
        "Anh ấy là bạn của tôi.",
    ),

    (
        357,
        "他们",
        "他们都是学生。",
        "Họ đều là học sinh.",
    ),

    (
        358,
        "她",
        "她是我姐姐。",
        "Cô ấy là chị gái của tôi.",
    ),

    (
        359,
        "她们",
        "她们都是女生。",
        "Họ đều là học sinh nữ.",
    ),

    (
        371,
        "外国",
        "我喜欢外国电影。",
        "Tôi thích phim nước ngoài.",
    ),

    (
        372,
        "外语",
        "我学习外语。",
        "Tôi học ngoại ngữ.",
    ),

    (
        382,
        "我们",
        "我们是越南人。",
        "Chúng tôi là người Việt Nam.",
    ),

    (
        399,
        "先生",
        "王先生是老师。",
        "Ông Vương là giáo viên.",
    ),

    (
        404,
        "小姐",
        "李小姐，你好！",
        "Chào cô Lý!",
    ),

    (
        443,
        "有名",
        "北京很有名。",
        "Bắc Kinh rất nổi tiếng.",
    ),

    (
        477,
        "中国",
        "我想去中国。",
        "Tôi muốn đến Trung Quốc.",
    ),

    (
        479,
        "中文",
        "我会说中文。",
        "Tôi biết nói tiếng Trung.",
    ),

    (
        501,
        "越南",
        "我是越南人。",
        "Tôi là người Việt Nam.",
    ),
]


# ============================================================
# KIỂM TRA DANH SÁCH CODE
# ============================================================

def validate_python_data():

    print()
    print("[1] Kiểm tra dữ liệu Python")

    if len(EXAMPLES) != EXPECTED_COUNT:

        raise RuntimeError(
            f"Bài 2 phải có {EXPECTED_COUNT} từ. "
            f"Code hiện có {len(EXAMPLES)} từ."
        )


    ids = [
        row[0]
        for row in EXAMPLES
    ]


    if len(ids) != len(set(ids)):

        raise RuntimeError(
            "Có MaTuVung bị trùng trong EXAMPLES."
        )


    hanzi = [
        row[1]
        for row in EXAMPLES
    ]


    if len(hanzi) != len(set(hanzi)):

        raise RuntimeError(
            "Có ChuHan bị trùng trong EXAMPLES."
        )


    for (
        ma_tu_vung,
        chu_han,
        vi_du_trung,
        vi_du_viet,
    ) in EXAMPLES:

        if not chu_han.strip():

            raise RuntimeError(
                f"MaTuVung={ma_tu_vung} thiếu ChuHan."
            )


        if not vi_du_trung.strip():

            raise RuntimeError(
                f"{chu_han} thiếu ví dụ tiếng Trung."
            )


        if not vi_du_viet.strip():

            raise RuntimeError(
                f"{chu_han} thiếu ví dụ tiếng Việt."
            )


    print(
        f"Dữ liệu Python: OK ({len(EXAMPLES)} từ)"
    )


# ============================================================
# KIỂM TRA LIVE DATABASE
# ============================================================

def validate_database(cursor):

    print()
    print("[2] Kiểm tra 29 từ trong live database")

    cursor.execute(
        """
        SELECT
            COUNT(*)

        FROM dbo.TuVungBaiHoc

        WHERE MaBaiHoc = ?
        """,
        LESSON_ID,
    )


    actual_count = cursor.fetchone()[0]


    print(
        "Số từ Bài 2 trong DB:",
        actual_count,
    )


    if actual_count != EXPECTED_COUNT:

        raise RuntimeError(
            f"Bài 2 trong DB phải có {EXPECTED_COUNT} từ. "
            f"Thực tế: {actual_count}"
        )


    for (
        ma_tu_vung,
        chu_han,
        vi_du_trung,
        vi_du_viet,
    ) in EXAMPLES:

        cursor.execute(
            """
            SELECT
                tv.MaTuVung,
                tv.ChuHan,
                tvbh.ThuTu

            FROM dbo.TuVung tv

            INNER JOIN dbo.TuVungBaiHoc tvbh
                ON tvbh.MaTuVung = tv.MaTuVung

            WHERE tv.MaTuVung = ?
              AND tv.ChuHan = ?
              AND tvbh.MaBaiHoc = ?
            """,
            ma_tu_vung,
            chu_han,
            LESSON_ID,
        )


        row = cursor.fetchone()


        if row is None:

            raise RuntimeError(
                "Không khớp database: "
                f"MaTuVung={ma_tu_vung} | "
                f"ChuHan={chu_han}"
            )


        print(
            f"OK | "
            f"ThuTu={row.ThuTu:>2} | "
            f"MaTuVung={row.MaTuVung:<3} | "
            f"{row.ChuHan}"
        )


# ============================================================
# UPDATE
# ============================================================

def update_examples(cursor):

    print()
    print("[3] Cập nhật ví dụ Bài 2")

    updated = 0


    for (
        ma_tu_vung,
        chu_han,
        vi_du_trung,
        vi_du_viet,
    ) in EXAMPLES:

        cursor.execute(
            """
            UPDATE dbo.TuVung

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
                "UPDATE không đúng 1 dòng: "
                f"{ma_tu_vung} | {chu_han}"
            )


        updated += 1


        print(
            f"Đã cập nhật | "
            f"{chu_han} | "
            f"{vi_du_trung}"
        )


    return updated


# ============================================================
# AUDIT BÀI 2
# ============================================================

def audit_lesson(cursor):

    cursor.execute(
        """
        SELECT
            COUNT(*) AS TongTu,

            SUM(
                CASE
                    WHEN
                        tv.ViDuTiengTrung IS NULL
                        OR LTRIM(
                            RTRIM(
                                tv.ViDuTiengTrung
                            )
                        ) = ''
                    THEN 1
                    ELSE 0
                END
            ) AS ThieuViDuTrung,

            SUM(
                CASE
                    WHEN
                        tv.ViDuTiengViet IS NULL
                        OR LTRIM(
                            RTRIM(
                                tv.ViDuTiengViet
                            )
                        ) = ''
                    THEN 1
                    ELSE 0
                END
            ) AS ThieuViDuViet

        FROM dbo.TuVung tv

        INNER JOIN dbo.TuVungBaiHoc tvbh
            ON tvbh.MaTuVung = tv.MaTuVung

        WHERE tvbh.MaBaiHoc = ?
        """,
        LESSON_ID,
    )


    return cursor.fetchone()


# ============================================================
# HIỂN THỊ DỮ LIỆU SAU UPDATE
# ============================================================

def show_result(cursor):

    print()
    print("[5] Dữ liệu Bài 2 sau cập nhật")
    print("-" * 100)


    cursor.execute(
        """
        SELECT
            tvbh.ThuTu,
            tv.MaTuVung,
            tv.ChuHan,
            tv.PhienAm,
            tv.ViDuTiengTrung,
            tv.ViDuTiengViet

        FROM dbo.TuVungBaiHoc tvbh

        INNER JOIN dbo.TuVung tv
            ON tv.MaTuVung = tvbh.MaTuVung

        WHERE tvbh.MaBaiHoc = ?

        ORDER BY
            tvbh.ThuTu
        """,
        LESSON_ID,
    )


    rows = cursor.fetchall()


    for row in rows:

        print(
            f"{row.ThuTu:02} | "
            f"{row.ChuHan} | "
            f"{row.PhienAm} | "
            f"{row.ViDuTiengTrung} | "
            f"{row.ViDuTiengViet}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    conn = None


    try:

        print("=" * 100)
        print(
            "HSK1 - BÀI 2 - BỔ SUNG VÍ DỤ TỪ VỰNG"
        )
        print("=" * 100)


        # ----------------------------------------------------
        # 1. CHECK CODE
        # ----------------------------------------------------

        validate_python_data()


        # ----------------------------------------------------
        # 2. CONNECT
        # ----------------------------------------------------

        print()
        print("Đang kết nối database...")


        conn = get_connection()

        conn.autocommit = False

        cursor = conn.cursor()


        print(
            "Kết nối database: OK"
        )


        # ----------------------------------------------------
        # 3. CHECK DATABASE
        # ----------------------------------------------------

        validate_database(
            cursor
        )


        # ----------------------------------------------------
        # 4. UPDATE
        # ----------------------------------------------------

        updated = update_examples(
            cursor
        )


        # ----------------------------------------------------
        # 5. AUDIT TRƯỚC COMMIT
        # ----------------------------------------------------

        result = audit_lesson(
            cursor
        )


        tong_tu = result.TongTu

        thieu_trung = (
            result.ThieuViDuTrung
            or 0
        )

        thieu_viet = (
            result.ThieuViDuViet
            or 0
        )


        print()
        print("[4] Kết quả audit")
        print("-" * 70)


        print(
            "Tổng từ:",
            tong_tu,
        )

        print(
            "Đã cập nhật:",
            updated,
        )

        print(
            "Thiếu ví dụ Trung:",
            thieu_trung,
        )

        print(
            "Thiếu ví dụ Việt:",
            thieu_viet,
        )


        # ----------------------------------------------------
        # 6. COMMIT / ROLLBACK
        # ----------------------------------------------------

        if (
            tong_tu == EXPECTED_COUNT
            and updated == EXPECTED_COUNT
            and thieu_trung == 0
            and thieu_viet == 0
        ):

            conn.commit()


            print()
            print(
                "✅ BÀI 2 ĐÃ CẬP NHẬT "
                "VÍ DỤ THÀNH CÔNG."
            )

        else:

            conn.rollback()


            raise RuntimeError(
                "Kết quả audit không đạt. "
                "Database đã rollback."
            )


        # ----------------------------------------------------
        # 7. SHOW RESULT
        # ----------------------------------------------------

        show_result(
            cursor
        )


    except Exception as error:

        if conn is not None:

            try:

                conn.rollback()

            except Exception:

                pass


        print()
        print("=" * 100)
        print("❌ CÓ LỖI")
        print("=" * 100)

        print(error)

        print()
        print(
            "Database không giữ "
            "thay đổi của lần chạy lỗi."
        )


    finally:

        if conn is not None:

            conn.close()


        print()
        print(
            "Đã đóng kết nối database."
        )


if __name__ == "__main__":
    main()