from pathlib import Path
import sys


# =========================================================
# THU MUC GOC DU AN
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# CAU HINH
# =========================================================
COURSE_CODE = "HSK1-CORE"


# =========================================================
# BAI 2 -> BAI 23
#
# BAI 1 DA TON TAI:
# 你好！ - Xin chào!
#
# Khong sua Bai 1 trong script nay.
# =========================================================
LESSONS = [
    {
        "order": 2,
        "title": "我是越南人 - Tôi là người Việt Nam",
        "summary": (
            "Học cách giới thiệu quốc tịch, quê hương, "
            "ngôn ngữ và những thông tin cơ bản về bản thân."
        ),
    },
    {
        "order": 3,
        "title": "这是我的家 - Đây là gia đình của tôi",
        "summary": (
            "Học từ vựng và mẫu câu cơ bản về gia đình, "
            "người thân và cách giới thiệu các thành viên."
        ),
    },
    {
        "order": 4,
        "title": "你今年几岁？ - Năm nay bạn bao nhiêu tuổi?",
        "summary": (
            "Học số đếm, tuổi, số lượng và các lượng từ "
            "cơ bản thường dùng."
        ),
    },
    {
        "order": 5,
        "title": "今天几月几号？ - Hôm nay là ngày mấy?",
        "summary": (
            "Học cách nói ngày, tháng, năm, thứ trong tuần "
            "và hỏi ngày tháng."
        ),
    },
    {
        "order": 6,
        "title": "现在几点？ - Bây giờ mấy giờ?",
        "summary": (
            "Học cách xem giờ, hỏi giờ và diễn đạt "
            "các thời điểm trong ngày."
        ),
    },
    {
        "order": 7,
        "title": "我在学校学习汉语 - Tôi học tiếng Trung ở trường",
        "summary": (
            "Học từ vựng về trường học, học sinh, giáo viên "
            "và hoạt động học tiếng Trung."
        ),
    },
    {
        "order": 8,
        "title": "请打开课本 - Mời mở sách giáo khoa",
        "summary": (
            "Học từ vựng lớp học, sách vở, kỹ năng học "
            "và các yêu cầu thường gặp trong lớp."
        ),
    },
    {
        "order": 9,
        "title": "我每天上班 - Tôi đi làm mỗi ngày",
        "summary": (
            "Học cách nói về công việc, thời gian biểu "
            "và sinh hoạt hằng ngày."
        ),
    },
    {
        "order": 10,
        "title": "你喜欢吃什么？ - Bạn thích ăn gì?",
        "summary": (
            "Học từ vựng về đồ ăn, thức uống, khẩu vị "
            "và cách hỏi sở thích ăn uống."
        ),
    },
    {
        "order": 11,
        "title": "我去商店买东西 - Tôi đi cửa hàng mua đồ",
        "summary": (
            "Học từ vựng mua sắm, giá tiền, đồ dùng "
            "và các mẫu câu mua hàng cơ bản."
        ),
    },
    {
        "order": 12,
        "title": "我家在这里 - Nhà tôi ở đây",
        "summary": (
            "Học từ vựng về nhà cửa, phòng và các đồ vật "
            "quen thuộc trong gia đình."
        ),
    },
    {
        "order": 13,
        "title": "桌子在左边 - Cái bàn ở bên trái",
        "summary": (
            "Học cách mô tả vị trí, phương hướng "
            "và quan hệ không gian giữa các đồ vật."
        ),
    },
    {
        "order": 14,
        "title": "请问，车站在哪儿？ - Cho hỏi, nhà ga ở đâu?",
        "summary": (
            "Học cách hỏi đường, chỉ đường và từ vựng "
            "giao thông cơ bản trong thành phố."
        ),
    },
    {
        "order": 15,
        "title": "今天天气怎么样？ - Thời tiết hôm nay thế nào?",
        "summary": (
            "Học từ vựng về thời tiết, mùa và "
            "một số hiện tượng tự nhiên quen thuộc."
        ),
    },
    {
        "order": 16,
        "title": "我生病了 - Tôi bị ốm rồi",
        "summary": (
            "Học từ vựng cơ bản về cơ thể, sức khỏe "
            "và cách diễn đạt tình trạng không khỏe."
        ),
    },
    {
        "order": 17,
        "title": "我喜欢唱歌和看电影 - Tôi thích hát và xem phim",
        "summary": (
            "Học cách nói về sở thích, giải trí, "
            "xem phim, nghe nhạc và hoạt động thư giãn."
        ),
    },
    {
        "order": 18,
        "title": "我们坐飞机去北京 - Chúng ta đi Bắc Kinh bằng máy bay",
        "summary": (
            "Học từ vựng về du lịch, phương tiện "
            "và việc di chuyển đến những nơi xa."
        ),
    },
    {
        "order": 19,
        "title": "你在做什么？ - Bạn đang làm gì?",
        "summary": (
            "Học cách diễn đạt hành động đang xảy ra "
            "và hỏi người khác đang làm gì."
        ),
    },
    {
        "order": 20,
        "title": "我会说中文 - Tôi biết nói tiếng Trung",
        "summary": (
            "Học cách diễn đạt khả năng, điều có thể làm, "
            "ý định và một số kết quả hành động."
        ),
    },
    {
        "order": 21,
        "title": "这个比那个好 - Cái này tốt hơn cái kia",
        "summary": (
            "Học cách miêu tả đặc điểm, mức độ "
            "và thực hiện những so sánh cơ bản."
        ),
    },
    {
        "order": 22,
        "title": "我给你打电话 - Tôi gọi điện cho bạn",
        "summary": (
            "Học từ vựng về liên lạc, điện thoại "
            "và những cách nói lịch sự cơ bản."
        ),
    },
    {
        "order": 23,
        "title": "明天见！ - Hẹn gặp ngày mai!",
        "summary": (
            "Ôn và mở rộng các từ chức năng, cách đáp lại "
            "và những mẫu giao tiếp thường ngày."
        ),
    },
]


# =========================================================
# KIEM TRA COT CUA MOT BANG
# =========================================================
def get_columns(cursor, table_name):

    cursor.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """,
        table_name,
    )

    return {
        row.COLUMN_NAME
        for row in cursor.fetchall()
    }


# =========================================================
# KIEM TRA SCHEMA
# =========================================================
def check_schema(cursor):

    required_khoahoc = {
        "MaKhoaHoc",
        "MaCapDo",
        "MaKyHieu",
        "TieuDe",
        "MoTa",
        "PhienBanChuanHSK",
        "TrangThai",
        "NgayTao",
    }

    required_baihoc = {
        "MaBaiHoc",
        "MaKhoaHoc",
        "SoThuTuBai",
        "TieuDe",
        "TomTat",
        "TrangThai",
        "NgayTao",
    }

    actual_khoahoc = get_columns(
        cursor,
        "KhoaHoc",
    )

    actual_baihoc = get_columns(
        cursor,
        "BaiHoc",
    )

    missing_khoahoc = (
        required_khoahoc
        - actual_khoahoc
    )

    missing_baihoc = (
        required_baihoc
        - actual_baihoc
    )

    if missing_khoahoc:
        raise RuntimeError(
            "Bang KhoaHoc thieu cot: "
            + ", ".join(
                sorted(missing_khoahoc)
            )
        )

    if missing_baihoc:
        raise RuntimeError(
            "Bang BaiHoc thieu cot: "
            + ", ".join(
                sorted(missing_baihoc)
            )
        )

    print()
    print("Kiem tra schema:")
    print("  KhoaHoc : OK")
    print("  BaiHoc  : OK")


# =========================================================
# KIEM TRA DANH SACH BAI TRONG SCRIPT
# =========================================================
def check_lesson_config():

    if len(LESSONS) != 22:
        raise RuntimeError(
            "Script phai co dung 22 bai "
            "tu Bai 2 den Bai 23."
        )

    orders = [
        item["order"]
        for item in LESSONS
    ]

    expected = list(
        range(2, 24)
    )

    if orders != expected:
        raise RuntimeError(
            "SoThuTuBai trong script "
            "khong lien tuc 2 -> 23."
        )

    titles = [
        item["title"]
        for item in LESSONS
    ]

    if len(set(titles)) != 22:
        raise RuntimeError(
            "TieuDe trong script bi trung."
        )

    for item in LESSONS:

        if len(item["title"]) > 200:
            raise RuntimeError(
                f"Bai {item['order']} "
                "co TieuDe vuot 200 ky tu."
            )

        if len(item["summary"]) > 2000:
            raise RuntimeError(
                f"Bai {item['order']} "
                "co TomTat vuot 2000 ky tu."
            )


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None
    cursor = None

    try:

        print("=" * 90)
        print(
            "09B - TAO BAI 2 -> BAI 23 "
            "CHO HSK1"
        )
        print("=" * 90)

        conn = get_connection()
        conn.autocommit = False

        cursor = conn.cursor()

        # =================================================
        # 1. KIEM TRA SCHEMA LIVE DB
        # =================================================
        check_schema(
            cursor
        )

        # =================================================
        # 2. KIEM TRA DANH SACH TRONG SCRIPT
        # =================================================
        check_lesson_config()

        print()
        print(
            "Kiem tra danh sach 22 bai: OK"
        )

        # =================================================
        # 3. TIM DUNG KHOA HSK1-CORE
        # =================================================
        cursor.execute(
            """
            SELECT
                MaKhoaHoc,
                MaCapDo,
                MaKyHieu,
                TieuDe,
                MoTa,
                PhienBanChuanHSK,
                TrangThai
            FROM dbo.KhoaHoc
            WHERE MaKyHieu = ?
            """,
            COURSE_CODE,
        )

        courses = cursor.fetchall()

        if len(courses) != 1:
            raise RuntimeError(
                "Phai tim thay duy nhat 1 "
                f"khoa {COURSE_CODE}. "
                f"Thuc te: {len(courses)}"
            )

        course = courses[0]

        # =================================================
        # 4. KIEM TRA DUNG HSK1
        # =================================================
        if course.MaCapDo != 1:
            raise RuntimeError(
                f"{COURSE_CODE} co "
                f"MaCapDo={course.MaCapDo}, "
                "khong phai HSK1."
            )

        ma_khoa_hoc = (
            course.MaKhoaHoc
        )

        print()
        print("-" * 90)
        print("KHOA HOC")
        print("-" * 90)

        print(
            "MaKhoaHoc       :",
            course.MaKhoaHoc,
        )

        print(
            "MaCapDo         :",
            course.MaCapDo,
        )

        print(
            "MaKyHieu        :",
            course.MaKyHieu,
        )

        print(
            "TieuDe          :",
            course.TieuDe,
        )

        print(
            "PhienBanChuanHSK:",
            course.PhienBanChuanHSK,
        )

        print(
            "TrangThai       :",
            course.TrangThai,
        )

        # =================================================
        # 5. KIEM TRA TAT CA BAI HSK1 HIEN TAI
        # =================================================
        cursor.execute(
            """
            SELECT
                MaBaiHoc,
                MaKhoaHoc,
                SoThuTuBai,
                TieuDe,
                TomTat,
                TrangThai
            FROM dbo.BaiHoc
            WHERE MaKhoaHoc = ?
            ORDER BY SoThuTuBai
            """,
            ma_khoa_hoc,
        )

        current_lessons = (
            cursor.fetchall()
        )

        print()
        print("-" * 90)
        print("BAI HOC HIEN TAI")
        print("-" * 90)

        for row in current_lessons:

            print(
                f"Bai {row.SoThuTuBai:02d}"
                f" | MaBaiHoc={row.MaBaiHoc}"
                f" | {row.TieuDe}"
                f" | {row.TrangThai}"
            )

        # =================================================
        # 6. LIVE DB TRUOC KHI CHAY 09B
        #    PHAI CHI CO BAI 1
        # =================================================
        if len(current_lessons) != 1:
            raise RuntimeError(
                "Truoc khi chay 09b, "
                "HSK1 phai chi co dung Bai 1. "
                f"Thuc te co {len(current_lessons)} bai."
            )

        lesson1 = (
            current_lessons[0]
        )

        if lesson1.SoThuTuBai != 1:
            raise RuntimeError(
                "Bai duy nhat hien tai "
                "khong phai Bai 1."
            )

        if lesson1.MaBaiHoc != 1:
            print()
            print(
                "LUU Y: MaBaiHoc cua Bai 1 "
                f"la {lesson1.MaBaiHoc}, "
                "khong phai 1."
            )

        # Không bắt buộc title phải bằng tuyệt đối
        # để không lỗi chỉ vì khoảng trắng.
        if "你好" not in lesson1.TieuDe:
            raise RuntimeError(
                "Bai 1 hien tai khong phai "
                "bai 你好 nhu du kien."
            )

        print()
        print(
            "Bai 1 hop le, se giu nguyen."
        )

        # =================================================
        # 7. KIEM TRA KHONG CO THU TU 2 -> 23
        # =================================================
        cursor.execute(
            """
            SELECT
                MaBaiHoc,
                SoThuTuBai,
                TieuDe
            FROM dbo.BaiHoc
            WHERE MaKhoaHoc = ?
              AND SoThuTuBai BETWEEN 2 AND 23
            ORDER BY SoThuTuBai
            """,
            ma_khoa_hoc,
        )

        existing_new_lessons = (
            cursor.fetchall()
        )

        if existing_new_lessons:

            print()
            print(
                "Phat hien bai da ton tai:"
            )

            for row in existing_new_lessons:

                print(
                    f"  Bai {row.SoThuTuBai}: "
                    f"{row.TieuDe}"
                )

            raise RuntimeError(
                "Khong insert de tranh "
                "trung SoThuTuBai."
            )

        # =================================================
        # 8. IN TRUOC DU LIEU SE INSERT
        # =================================================
        print()
        print("-" * 90)
        print("DU LIEU SE INSERT")
        print("-" * 90)

        for item in LESSONS:

            print(
                f"{item['order']:02d}"
                f" | {item['title']}"
            )

        # =================================================
        # 9. INSERT BAI 2 -> 23
        # =================================================
        inserted = 0

        for item in LESSONS:

            cursor.execute(
                """
                INSERT INTO dbo.BaiHoc
                (
                    MaKhoaHoc,
                    SoThuTuBai,
                    TieuDe,
                    TomTat,
                    TrangThai
                )
                VALUES
                (
                    ?, ?, ?, ?, 'ban_nhap'
                )
                """,
                ma_khoa_hoc,
                item["order"],
                item["title"],
                item["summary"],
            )

            inserted += 1

        if inserted != 22:
            raise RuntimeError(
                "So bai insert khong dung 22."
            )

        # =================================================
        # 10. DOC LAI 23 BAI TRONG TRANSACTION
        # =================================================
        cursor.execute(
            """
            SELECT
                MaBaiHoc,
                MaKhoaHoc,
                SoThuTuBai,
                TieuDe,
                TomTat,
                TrangThai
            FROM dbo.BaiHoc
            WHERE MaKhoaHoc = ?
            ORDER BY SoThuTuBai
            """,
            ma_khoa_hoc,
        )

        final_lessons = (
            cursor.fetchall()
        )

        # =================================================
        # 11. VERIFY SO LUONG
        # =================================================
        if len(final_lessons) != 23:
            raise RuntimeError(
                "Sau insert phai co 23 bai. "
                f"Thuc te: {len(final_lessons)}"
            )

        actual_orders = [
            row.SoThuTuBai
            for row in final_lessons
        ]

        expected_orders = list(
            range(1, 24)
        )

        if actual_orders != expected_orders:
            raise RuntimeError(
                "SoThuTuBai sau insert "
                "khong dung 1 -> 23."
            )

        # =================================================
        # 12. KIEM TRA 22 BAI MOI O ban_nhap
        # =================================================
        invalid_status = [
            row
            for row in final_lessons
            if row.SoThuTuBai >= 2
            and row.TrangThai != "ban_nhap"
        ]

        if invalid_status:
            raise RuntimeError(
                "Co bai moi khong o "
                "TrangThai=ban_nhap."
            )

        # =================================================
        # 13. KIEM TRA BAI 2
        # =================================================
        lesson2 = next(
            row
            for row in final_lessons
            if row.SoThuTuBai == 2
        )

        if "我是越南人" not in lesson2.TieuDe:
            raise RuntimeError(
                "Bai 2 khong dung "
                "'我是越南人'."
            )

        # =================================================
        # 14. COMMIT
        # =================================================
        conn.commit()

        # =================================================
        # 15. KET QUA
        # =================================================
        print()
        print("=" * 90)
        print("KET QUA")
        print("=" * 90)

        for row in final_lessons:

            print(
                f"{row.SoThuTuBai:02d}"
                f" | MaBaiHoc={row.MaBaiHoc}"
                f" | {row.TieuDe}"
                f" | {row.TrangThai}"
            )

        print()
        print(
            "Tong bai HSK1:",
            len(final_lessons),
        )

        print(
            "Bai cu giu nguyen:",
            1,
        )

        print(
            "Bai moi da tao:",
            inserted,
        )

        print()
        print(
            "Bai 2:",
            lesson2.TieuDe,
        )

        print()
        print(
            "DA TAO BAI 2 -> BAI 23 "
            "THANH CONG."
        )

        print()
        print(
            "CHUA GAN TU VUNG VAO "
            "BAI 2 -> BAI 23."
        )

        print(
            "CHUA TAO NGU PHAP."
        )

        print(
            "CHUA TAO CHU HAN."
        )

        print(
            "CHUA TAO BAI TAP."
        )

        print()
        print("=" * 90)
        print("HOAN TAT")
        print("=" * 90)

    except Exception as e:

        if conn:
            conn.rollback()

        print()
        print("=" * 90)
        print(
            "THAT BAI - DA ROLLBACK"
        )
        print("=" * 90)

        print(
            "Loi:",
            e,
        )

        print()
        print(
            "KHONG GIU BAT KY BAI MOI "
            "NAO NEU CO LOI."
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


if __name__ == "__main__":
    main()