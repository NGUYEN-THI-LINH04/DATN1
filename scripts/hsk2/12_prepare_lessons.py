from pathlib import Path
import csv


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

OUTPUT_FILE = DATA_DIR / "lessons_hsk2_draft.csv"


# ============================================================
# 23 BAI HOC HSK2
#
# HSK1 trong CSDL hien tai co 23 bai.
# HSK2 tiep tuc dung cung cach to chuc.
#
# Day la khung bai hoc cua he thong Moc Han,
# KHONG phai danh sach bai cua mot giao trinh cu the.
# ============================================================

LESSONS = [

    {
        "SoThuTuBai": 1,
        "TieuDe": "我的一天 - Một ngày của tôi",
        "TomTat":
            "Mở rộng cách nói về sinh hoạt hằng ngày, "
            "thời gian, các hoạt động thường xuyên và "
            "trình tự thực hiện công việc."
    },

    {
        "SoThuTuBai": 2,
        "TieuDe": "我的学习生活 - Cuộc sống học tập của tôi",
        "TomTat":
            "Học từ vựng về lớp học, học tập, bài tập, "
            "kết quả học tập và các hoạt động trong trường."
    },

    {
        "SoThuTuBai": 3,
        "TieuDe": "我的工作 - Công việc của tôi",
        "TomTat":
            "Học cách nói về nghề nghiệp, nơi làm việc, "
            "công ty, văn phòng và các hoạt động công việc."
    },

    {
        "SoThuTuBai": 4,
        "TieuDe": "我的家人和朋友 - Gia đình và bạn bè của tôi",
        "TomTat":
            "Mở rộng từ vựng về gia đình, bạn bè, "
            "các mối quan hệ và cách miêu tả một người."
    },

    {
        "SoThuTuBai": 5,
        "TieuDe": "他长得怎么样？ - Anh ấy trông thế nào?",
        "TomTat":
            "Học cách miêu tả ngoại hình, tính cách, "
            "đặc điểm và cảm nhận về người khác."
    },

    {
        "SoThuTuBai": 6,
        "TieuDe": "今天天气不错 - Thời tiết hôm nay khá đẹp",
        "TomTat":
            "Mở rộng từ vựng về thời tiết, nhiệt độ, "
            "các mùa và hiện tượng tự nhiên."
    },

    {
        "SoThuTuBai": 7,
        "TieuDe": "你身体怎么样？ - Sức khỏe của bạn thế nào?",
        "TomTat":
            "Học từ vựng về sức khỏe, cơ thể, "
            "cảm giác khó chịu, bệnh tật và chăm sóc sức khỏe."
    },

    {
        "SoThuTuBai": 8,
        "TieuDe": "我们去吃饭吧 - Chúng ta đi ăn nhé",
        "TomTat":
            "Mở rộng từ vựng về món ăn, nhà hàng, "
            "bữa ăn, khẩu vị và các tình huống ăn uống."
    },

    {
        "SoThuTuBai": 9,
        "TieuDe": "我想买这件衣服 - Tôi muốn mua bộ quần áo này",
        "TomTat":
            "Học cách mua sắm, hỏi giá, lựa chọn đồ vật, "
            "màu sắc, kích thước và đánh giá sản phẩm."
    },

    {
        "SoThuTuBai": 10,
        "TieuDe": "我家离学校很近 - Nhà tôi rất gần trường",
        "TomTat":
            "Học cách nói vị trí, khoảng cách, "
            "phương hướng và mô tả địa điểm."
    },

    {
        "SoThuTuBai": 11,
        "TieuDe": "请问，怎么走？ - Cho hỏi, đi thế nào?",
        "TomTat":
            "Mở rộng cách hỏi đường, chỉ đường, "
            "giao thông và các phương tiện đi lại."
    },

    {
        "SoThuTuBai": 12,
        "TieuDe": "我们去旅行吧 - Chúng ta đi du lịch nhé",
        "TomTat":
            "Học từ vựng về du lịch, khách sạn, "
            "hộ chiếu, hành trình và các hoạt động khi đi xa."
    },

    {
        "SoThuTuBai": 13,
        "TieuDe": "我喜欢运动 - Tôi thích vận động",
        "TomTat":
            "Học từ vựng về thể thao, vận động, "
            "sức khỏe và các hoạt động ngoài trời."
    },

    {
        "SoThuTuBai": 14,
        "TieuDe": "周末你做什么？ - Cuối tuần bạn làm gì?",
        "TomTat":
            "Học cách nói về sở thích, giải trí, "
            "âm nhạc, phim ảnh và các hoạt động cuối tuần."
    },

    {
        "SoThuTuBai": 15,
        "TieuDe": "春节快到了 - Tết sắp đến rồi",
        "TomTat":
            "Học từ vựng về ngày lễ, sự kiện, "
            "thời gian và các hoạt động trong dịp đặc biệt."
    },

    {
        "SoThuTuBai": 16,
        "TieuDe": "我已经做完了 - Tôi đã làm xong rồi",
        "TomTat":
            "Học cách diễn đạt hành động đã hoàn thành, "
            "kinh nghiệm và sự thay đổi trạng thái."
    },

    {
        "SoThuTuBai": 17,
        "TieuDe": "他正在学习呢 - Anh ấy đang học",
        "TomTat":
            "Học cách diễn đạt hành động đang diễn ra, "
            "trạng thái đang duy trì và hoạt động đồng thời."
    },

    {
        "SoThuTuBai": 18,
        "TieuDe": "这个比那个便宜 - Cái này rẻ hơn cái kia",
        "TomTat":
            "Mở rộng các cấu trúc so sánh, "
            "mức độ, sự giống nhau và khác nhau."
    },

    {
        "SoThuTuBai": 19,
        "TieuDe": "汉语越来越有意思 - Tiếng Trung ngày càng thú vị",
        "TomTat":
            "Học cách diễn đạt sự thay đổi mức độ, "
            "càng... càng..., ngày càng... và đánh giá."
    },

    {
        "SoThuTuBai": 20,
        "TieuDe": "因为下雨，所以我没去 - Vì trời mưa nên tôi không đi",
        "TomTat":
            "Học cách diễn đạt nguyên nhân, kết quả, "
            "điều kiện và quan hệ giữa các vế câu."
    },

    {
        "SoThuTuBai": 21,
        "TieuDe": "请给我打电话 - Hãy gọi điện cho tôi",
        "TomTat":
            "Học các mẫu câu giao tiếp, liên lạc, "
            "yêu cầu, đề nghị và cách hướng hành động tới người khác."
    },

    {
        "SoThuTuBai": 22,
        "TieuDe": "我对中国文化很感兴趣 - Tôi rất hứng thú với văn hóa Trung Quốc",
        "TomTat":
            "Học cách nói về sở thích, cảm xúc, "
            "quan điểm, văn hóa và những điều bản thân quan tâm."
    },

    {
        "SoThuTuBai": 23,
        "TieuDe": "一起复习吧！ - Cùng ôn tập nhé!",
        "TomTat":
            "Ôn tập và kết hợp từ vựng, chữ Hán và "
            "các cấu trúc ngữ pháp trọng tâm của HSK2."
    },
]


FIELDS = [
    "MaBaiHocTam",
    "MaKhoaHoc",
    "SoThuTuBai",
    "TieuDe",
    "TomTat",
    "TrangThai",
]


def main():

    print("=" * 70)
    print("BUOC 12 - TAO KHUNG BAI HOC HSK2")
    print("KHONG GHI SQL")
    print("=" * 70)

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if OUTPUT_FILE.exists():
        raise FileExistsError(
            f"File da ton tai:\n{OUTPUT_FILE}\n"
            "Khong tu dong ghi de."
        )

    rows = []

    for lesson in LESSONS:

        order = lesson[
            "SoThuTuBai"
        ]

        rows.append({
            "MaBaiHocTam":
                f"L2-{order:02d}",

            # KhoaHoc HSK2 trong SQL
            "MaKhoaHoc":
                2,

            "SoThuTuBai":
                order,

            "TieuDe":
                lesson["TieuDe"],

            "TomTat":
                lesson["TomTat"],

            # Chua xuat ban
            "TrangThai":
                "ban_nhap",
        })

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS
        )

        writer.writeheader()
        writer.writerows(rows)

    print()
    print(
        f"Tong so bai HSK2: "
        f"{len(rows)}"
    )

    print(
        "MaKhoaHoc HSK2: 2"
    )

    print(
        "Trang thai: ban_nhap"
    )

    print()
    print("Da tao:")
    print(OUTPUT_FILE)

    print()
    print(
        "CHUA INSERT/UPDATE/DELETE SQL."
    )


if __name__ == "__main__":
    main()