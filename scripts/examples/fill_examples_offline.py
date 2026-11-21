import os
import re
import csv
import argparse
from pathlib import Path

import pyodbc
from dotenv import load_dotenv


# =========================================================
# 1. CẤU HÌNH
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

load_dotenv(ROOT / ".env")

DATA_DIR = (
    ROOT
    / "scripts"
    / "examples"
    / "data"
)


def get_output_path(level):
    """
    Mỗi HSK có một file riêng.

    Ví dụ:
    HSK2 -> offline_preview_hsk2.csv
    HSK3 -> offline_preview_hsk3.csv
    HSK4 -> offline_preview_hsk4.csv
    """
    return DATA_DIR / f"offline_preview_hsk{level}.csv"


# =========================================================
# 2. KẾT NỐI SQL SERVER
# =========================================================

def connect_db():
    server = os.getenv(
        "DB_SERVER",
        "localhost"
    )

    database = os.getenv(
        "DB_NAME",
        "HocTiengTrungDB"
    )

    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    drivers = [
        driver
        for driver in pyodbc.drivers()
        if "SQL Server" in driver
    ]

    if not drivers:
        raise RuntimeError(
            "Không tìm thấy ODBC Driver cho SQL Server."
        )

    # Lấy driver SQL Server mới nhất đang có
    driver = drivers[-1]

    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={database}",
        "TrustServerCertificate=yes"
    ]

    if username and password:
        parts.extend([
            f"UID={username}",
            f"PWD={password}"
        ])

    else:
        parts.append(
            "Trusted_Connection=yes"
        )

    connection_string = ";".join(parts)

    return pyodbc.connect(
        connection_string,
        autocommit=False
    )


# =========================================================
# 3. LẤY TỪ THIẾU VÍ DỤ THEO HSK
# =========================================================

def get_words(conn, level):
    """
    Chỉ lấy từ của đúng HSK được chọn
    và đang thiếu ít nhất một câu ví dụ.
    """

    sql = """
    SELECT
        tv.MaTuVung,
        MIN(kh.MaCapDo) AS HSK,
        tv.ChuHan,
        tv.NghiaTiengViet,
        tv.TuLoai,
        tv.ViDuTiengTrung,
        tv.ViDuTiengViet

    FROM dbo.TuVung AS tv

    INNER JOIN dbo.TuVungBaiHoc AS tvbh
        ON tvbh.MaTuVung = tv.MaTuVung

    INNER JOIN dbo.BaiHoc AS bh
        ON bh.MaBaiHoc = tvbh.MaBaiHoc

    INNER JOIN dbo.KhoaHoc AS kh
        ON kh.MaKhoaHoc = bh.MaKhoaHoc

    WHERE kh.MaCapDo BETWEEN 2 AND 4

      AND (
            NULLIF(
                LTRIM(RTRIM(tv.ViDuTiengTrung)),
                N''
            ) IS NULL

            OR

            NULLIF(
                LTRIM(RTRIM(tv.ViDuTiengViet)),
                N''
            ) IS NULL
      )

    GROUP BY
        tv.MaTuVung,
        tv.ChuHan,
        tv.NghiaTiengViet,
        tv.TuLoai,
        tv.ViDuTiengTrung,
        tv.ViDuTiengViet

    HAVING MIN(kh.MaCapDo) = ?

    ORDER BY
        tv.MaTuVung
    """

    cursor = conn.cursor()

    cursor.execute(
        sql,
        level
    )

    return cursor.fetchall()


# =========================================================
# 4. CHUẨN HÓA CHỮ HÁN
# =========================================================

def clean_word(value):
    """
    Xử lý các từ đặc biệt.

    Ví dụ:
    称1        -> 称
    面2        -> 面
    家（科学家） -> 科学家
    老（老王）   -> 老王
    """

    word = str(
        value or ""
    ).strip()

    # Lấy phần bên trong ngoặc Trung Quốc
    match = re.search(
        r"（([^（）]+)）",
        word
    )

    if match:
        return match.group(1).strip()

    # Xóa số ở cuối:
    # 称1 -> 称
    # 面2 -> 面

    word = re.sub(
        r"\d+$",
        "",
        word
    )

    return word.strip()


def clean_text(value):
    if value is None:
        return ""

    return str(value).strip()


# =========================================================
# 5. CÁC CÂU ĐÃ VIẾT RIÊNG
# =========================================================

EXAMPLES = {

    "成绩": (
        "这次考试我的成绩很好。",
        "Kết quả kỳ thi lần này của tôi rất tốt."
    ),

    "成为": (
        "我想成为一名老师。",
        "Tôi muốn trở thành một giáo viên."
    ),

    "重复": (
        "请你再重复一遍。",
        "Bạn hãy lặp lại một lần nữa."
    ),

    "重新": (
        "请你重新做一次。",
        "Bạn hãy làm lại một lần nữa."
    ),

    "出发": (
        "我们明天早上七点出发。",
        "Chúng tôi khởi hành lúc bảy giờ sáng mai."
    ),

    "出国": (
        "他明年要出国学习。",
        "Năm sau anh ấy sẽ ra nước ngoài học tập."
    ),

    "出口": (
        "出口在前面。",
        "Lối ra ở phía trước."
    ),

    "出门": (
        "我每天八点出门。",
        "Hằng ngày tôi ra khỏi nhà lúc tám giờ."
    ),

    "出生": (
        "我出生在越南。",
        "Tôi sinh ra ở Việt Nam."
    ),

    "出现": (
        "他突然出现在门口。",
        "Anh ấy đột nhiên xuất hiện ở cửa."
    ),

    "出院": (
        "他明天可以出院了。",
        "Ngày mai anh ấy có thể xuất viện."
    ),

    "出租": (
        "这套房子可以出租。",
        "Căn nhà này có thể cho thuê."
    ),

    "出租车": (
        "我们坐出租车去学校。",
        "Chúng tôi đi taxi đến trường."
    ),

    "船": (
        "他们坐船去对岸。",
        "Họ đi thuyền sang bờ bên kia."
    ),

    "春节": (
        "春节我们全家一起吃饭。",
        "Tết Nguyên Đán cả gia đình tôi cùng ăn cơm."
    ),

    "春天": (
        "春天的天气很暖和。",
        "Thời tiết mùa xuân rất ấm áp."
    ),

    "词典": (
        "这个字我需要查词典。",
        "Chữ này tôi cần tra từ điển."
    ),

    "从小": (
        "我从小就喜欢中文。",
        "Từ nhỏ tôi đã thích tiếng Trung."
    ),

    "答应": (
        "妈妈答应带我去公园。",
        "Mẹ đồng ý đưa tôi đi công viên."
    ),

    "打工": (
        "他周末在饭馆打工。",
        "Cuối tuần anh ấy làm thêm tại nhà hàng."
    ),

    "打算": (
        "我打算明天去北京。",
        "Tôi dự định ngày mai đi Bắc Kinh."
    ),

    "打印": (
        "请帮我打印这份文件。",
        "Hãy giúp tôi in tài liệu này."
    ),

    "办公室": (
        "老师正在办公室工作。",
        "Giáo viên đang làm việc trong văn phòng."
    ),

    "半夜": (
        "昨天半夜突然下雨了。",
        "Nửa đêm hôm qua đột nhiên trời mưa."
    ),

    "动物园": (
        "周末我们一起去动物园。",
        "Cuối tuần chúng tôi cùng đi sở thú."
    ),

    "地铁": (
        "我每天坐地铁上班。",
        "Hằng ngày tôi đi tàu điện ngầm đi làm."
    ),

    "健康": (
        "每天运动对健康有好处。",
        "Vận động hằng ngày có lợi cho sức khỏe."
    ),

    "努力": (
        "我要努力学习中文。",
        "Tôi phải cố gắng học tiếng Trung."
    ),

    "旅行": (
        "我喜欢和朋友一起旅行。",
        "Tôi thích đi du lịch cùng bạn bè."
    ),

    "天气": (
        "今天天气很好。",
        "Hôm nay thời tiết rất đẹp."
    ),

    "学习": (
        "我每天晚上学习中文。",
        "Tôi học tiếng Trung mỗi tối."
    ),

    # Một số từ HSK2 đã phát hiện khi kiểm tra CSV

    "大部分": (
        "大部分学生都喜欢这门课。",
        "Phần lớn học sinh đều thích môn học này."
    ),

    "作业": (
        "我每天晚上做完作业再睡觉。",
        "Mỗi tối tôi làm xong bài tập rồi mới đi ngủ."
    ),

    "压力": (
        "最近工作太多，我觉得压力很大。",
        "Gần đây công việc quá nhiều, tôi cảm thấy áp lực rất lớn."
    ),

    "重量": (
        "这个箱子的重量是多少？",
        "Trọng lượng của chiếc thùng này là bao nhiêu?"
    ),

    "大海": (
        "我第一次看到了美丽的大海。",
        "Lần đầu tiên tôi nhìn thấy biển lớn xinh đẹp."
    ),

    "大家": (
        "大家都喜欢这个老师。",
        "Mọi người đều thích giáo viên này."
    ),

    "大门": (
        "学校的大门已经关了。",
        "Cổng lớn của trường đã đóng rồi."
    ),

    "字典": (
        "不知道这个字的时候可以查字典。",
        "Khi không biết chữ này có thể tra từ điển."
    ),

    "走进": (
        "老师走进了教室。",
        "Giáo viên bước vào lớp học."
    ),

    "走开": (
        "他生气地走开了。",
        "Anh ấy tức giận bỏ đi."
    ),

    "租": (
        "我想在学校附近租一个房间。",
        "Tôi muốn thuê một căn phòng gần trường."
    ),

    "组长": (
        "他是我们小组的组长。",
        "Anh ấy là trưởng nhóm của chúng tôi."
    ),

    "嘴": (
        "这个孩子的嘴很小。",
        "Miệng của đứa trẻ này rất nhỏ."
    ),

    "最近": (
        "我最近工作很忙。",
        "Gần đây tôi rất bận công việc."
    ),

    "作家": (
        "他是一位很有名的作家。",
        "Anh ấy là một nhà văn rất nổi tiếng."
    ),

    "作文": (
        "老师让我们写一篇作文。",
        "Giáo viên yêu cầu chúng tôi viết một bài văn."
    ),

    "座位": (
        "我的座位在教室前面。",
        "Chỗ ngồi của tôi ở phía trước lớp học."
    ),

    "做饭": (
        "妈妈正在厨房做饭。",
        "Mẹ đang nấu ăn trong bếp."
    ),
}


# =========================================================
# 6. CÂU DỰ PHÒNG
# =========================================================

TEMPLATES = [

    (
        "今天老师教我们“{word}”这个词。",
        'Hôm nay giáo viên dạy chúng tôi từ "{word}".'
    ),

    (
        "今天我们学习了“{word}”这个词。",
        'Hôm nay chúng tôi đã học từ "{word}".'
    ),

    (
        "我已经学会了“{word}”这个词。",
        'Tôi đã học được từ "{word}".'
    ),

    (
        "老师让我们读一读“{word}”这个词。",
        'Giáo viên yêu cầu chúng tôi đọc từ "{word}".'
    ),

    (
        "请用“{word}”造一个句子。",
        'Hãy dùng từ "{word}" để đặt một câu.'
    ),

    (
        "我把“{word}”写在了本子上。",
        'Tôi đã viết từ "{word}" vào vở.'
    ),

    (
        "我在课本里看到了“{word}”这个词。",
        'Tôi đã nhìn thấy từ "{word}" trong sách giáo khoa.'
    ),

    (
        "老师正在解释“{word}”这个词。",
        'Giáo viên đang giải thích từ "{word}".'
    ),

    (
        "请大家一起读“{word}”这个词。",
        'Mọi người hãy cùng đọc từ "{word}".'
    ),

    (
        "这个单元我们要学习“{word}”。",
        'Trong bài này chúng tôi sẽ học từ "{word}".'
    ),
]


# =========================================================
# 7. TẠO CÂU
# =========================================================

def create_example(word_id, raw_word):
    word = clean_word(
        raw_word
    )

    if not word:
        return None

    # Ưu tiên câu riêng
    if word in EXAMPLES:

        chinese, vietnamese = EXAMPLES[word]

        return (
            chinese,
            vietnamese,
            "REAL"
        )

    # Nếu chưa có câu riêng thì dùng câu dự phòng.
    index = (
        int(word_id)
        % len(TEMPLATES)
    )

    cn_template, vi_template = (
        TEMPLATES[index]
    )

    chinese = cn_template.format(
        word=word
    )

    vietnamese = vi_template.format(
        word=word
    )

    return (
        chinese,
        vietnamese,
        "TEMPLATE"
    )


# =========================================================
# 8. TẠO FILE PREVIEW
# =========================================================

def generate_preview(level):
    conn = connect_db()

    output = get_output_path(
        level
    )

    try:
        rows = get_words(
            conn,
            level
        )

        DATA_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        total = 0
        real_count = 0
        template_count = 0
        partial_count = 0

        with output.open(
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "MaTuVung",
                "HSK",
                "ChuHan",
                "NghiaTiengViet",
                "TuLoai",
                "ViDuTiengTrung",
                "ViDuTiengViet",
                "LoaiCau",
                "TrangThaiImport"
            ])

            for row in rows:

                (
                    word_id,
                    hsk,
                    raw_word,
                    meaning,
                    word_type,
                    old_chinese,
                    old_vietnamese
                ) = row

                old_chinese = clean_text(
                    old_chinese
                )

                old_vietnamese = clean_text(
                    old_vietnamese
                )

                result = create_example(
                    word_id,
                    raw_word
                )

                if result is None:
                    continue

                (
                    chinese,
                    vietnamese,
                    sentence_type
                ) = result

                # -----------------------------------------
                # Nếu một nửa đã có dữ liệu:
                # KHÔNG tự động import.
                # Vì câu cũ và câu mới có thể không khớp.
                # -----------------------------------------

                if (
                    bool(old_chinese)
                    != bool(old_vietnamese)
                ):

                    import_status = (
                        "PARTIAL_REVIEW"
                    )

                    partial_count += 1

                else:
                  if sentence_type == "REAL":
                        import_status = "READY"
                  else:
                    import_status = "NEED_REVIEW"

                # Nếu cả hai trường cũ đều trống
                # thì dùng cặp câu mới.
                #
                # Nếu cả hai đã có thì bình thường
                # query sẽ không lấy dòng đó.

                writer.writerow([
                    word_id,
                    hsk,
                    raw_word,
                    meaning or "",
                    word_type or "",
                    chinese,
                    vietnamese,
                    sentence_type,
                    import_status
                ])

                total += 1

                if sentence_type == "REAL":
                    real_count += 1
                else:
                    template_count += 1

        print()
        print("=" * 55)

        print(
            f"HSK{level}"
        )

        print(
            f"Tổng từ thiếu ví dụ: {total}"
        )

        print(
            f"Câu dùng từ trong ngữ cảnh: {real_count}"
        )

        print(
            f"Câu mẫu dự phòng: {template_count}"
        )

        print(
            f"Câu có dữ liệu một nửa cần kiểm tra: "
            f"{partial_count}"
        )

        print()
        print(
            f"File: {output}"
        )

        print(
            "CHƯA THAY ĐỔI SQL SERVER."
        )

        print("=" * 55)

    finally:
        conn.rollback()
        conn.close()


# =========================================================
# 9. IMPORT PREVIEW
# =========================================================

def import_preview(
    level,
    commit=False
):
    output = get_output_path(
        level
    )

    if not output.exists():

        print(
            f"Không tìm thấy file:"
        )

        print(output)

        print()
        print(
            f"Hãy chạy:"
        )

        print(
            f"python scripts\\examples\\"
            f"fill_examples_offline.py "
            f"--generate --level {level}"
        )

        return

    conn = connect_db()

    try:
        cursor = conn.cursor()

        updated = 0
        skipped_partial = 0

        with output.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(
                file
            )

            for row in reader:

                # -----------------------------------------
                # Không tự import trường hợp đã có 1 nửa.
                # -----------------------------------------

                if (
                    row["TrangThaiImport"]
                    != "READY"
                ):

                    skipped_partial += 1
                    continue

                word_id = int(
                    row["MaTuVung"]
                )

                chinese = clean_text(
                    row["ViDuTiengTrung"]
                )

                vietnamese = clean_text(
                    row["ViDuTiengViet"]
                )

                if (
                    not chinese
                    or not vietnamese
                ):
                    continue

                # -----------------------------------------
                # Chỉ update khi CẢ HAI trường đang trống.
                #
                # Như vậy tránh:
                # câu Trung cũ + dịch Việt mới không khớp.
                # -----------------------------------------

                cursor.execute(
                    """
                    UPDATE dbo.TuVung

                    SET
                        ViDuTiengTrung = ?,
                        ViDuTiengViet = ?

                    WHERE
                        MaTuVung = ?

                    AND
                        NULLIF(
                            LTRIM(
                                RTRIM(
                                    ViDuTiengTrung
                                )
                            ),
                            N''
                        ) IS NULL

                    AND
                        NULLIF(
                            LTRIM(
                                RTRIM(
                                    ViDuTiengViet
                                )
                            ),
                            N''
                        ) IS NULL
                    """,

                    chinese,
                    vietnamese,
                    word_id
                )

                updated += (
                    cursor.rowcount
                )

        print()
        print("=" * 55)

        print(
            f"HSK{level}"
        )

        print(
            f"Số từ có thể cập nhật an toàn: "
            f"{updated}"
        )

        print(
            f"PARTIAL_REVIEW bỏ qua: "
            f"{skipped_partial}"
        )

        if commit:

            conn.commit()

            print()
            print(
                "COMMIT PASS"
            )

            print(
                "ĐÃ LƯU VÀO SQL SERVER."
            )

        else:

            conn.rollback()

            print()
            print(
                "DRY RUN PASS"
            )

            print(
                "DATABASE CHƯA THAY ĐỔI."
            )

        print("=" * 55)

    except Exception:

        conn.rollback()

        print(
            "IMPORT FAIL."
        )

        raise

    finally:

        conn.close()


# =========================================================
# 10. MAIN
# =========================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Tạo câu ví dụ HSK2/3/4 "
            "không dùng AI"
        )
    )

    action_group = (
        parser
        .add_mutually_exclusive_group(
            required=True
        )
    )

    action_group.add_argument(
        "--generate",
        action="store_true",
        help="Tạo CSV xem trước"
    )

    action_group.add_argument(
        "--import-preview",
        action="store_true",
        help="Kiểm tra/import CSV vào SQL"
    )

    # Bắt buộc chọn HSK
    parser.add_argument(
        "--level",
        type=int,
        choices=[2, 3, 4],
        required=True,
        help="Chọn HSK 2, 3 hoặc 4"
    )

    parser.add_argument(
        "--commit",
        action="store_true",
        help="Ghi thật vào SQL"
    )

    args = parser.parse_args()

    if (
        args.commit
        and not args.import_preview
    ):

        parser.error(
            "--commit chỉ dùng với "
            "--import-preview"
        )

    if args.generate:

        generate_preview(
            args.level
        )

    else:

        import_preview(
            args.level,
            commit=args.commit
        )


if __name__ == "__main__":
    main()