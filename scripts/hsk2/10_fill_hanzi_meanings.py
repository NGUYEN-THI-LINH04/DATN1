from pathlib import Path
import csv


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

# Dùng file 299 chữ đã có đủ bộ thủ + số nét
INPUT_FILE = DATA_DIR / "hanzi_hsk2_unihan.csv"

# File hoàn thiện nghĩa
OUTPUT_FILE = DATA_DIR / "hanzi_hsk2_meanings_completed.csv"


# ============================================================
# NGHIA TIENG VIET CHO 141 CHU CON THIEU
# Nghia duoc rut gon theo huong hoc tap, khong lay nguyen
# nghia dai cua tu dien.
# ============================================================

MEANINGS = {
    "情": "tình cảm; tình; cảm xúc",
    "安": "yên; yên ổn; an toàn",
    "静": "yên tĩnh; tĩnh lặng",
    "色": "màu; màu sắc; sắc",
    "法": "phương pháp; cách; pháp luật",
    "公": "công; chung; công cộng",
    "室": "phòng; căn phòng",
    "助": "giúp; trợ giúp; hỗ trợ",
    "报": "báo; báo cáo; thông báo",
    "如": "như; giống như",
    "必": "nhất định; ắt; phải",
    "须": "cần; phải",
    "示": "biểu thị; chỉ ra; cho thấy",
    "意": "ý; ý nghĩa; ý định",
    "思": "nghĩ; suy nghĩ",
    "久": "lâu; lâu dài",
    "定": "định; xác định; nhất định",
    "部": "bộ; phần; bộ phận",
    "单": "đơn; đơn lẻ; phiếu",
    "参": "tham gia; tham dự",
    "观": "xem; quan sát; quan điểm",
    "超": "vượt; vượt quá",
    "称": "gọi; gọi là; xưng; cân",
    "绩": "thành tích; kết quả",
    "复": "lặp lại; trở lại; ôn lại",
    "春": "mùa xuân",
    "典": "điển; sách chuẩn; sách tra cứu",
    "应": "nên; cần; đáp ứng",
    "印": "in; dấu; ấn",
    "量": "lượng; số lượng; đo lường",
    "声": "âm thanh; tiếng; giọng",
    "自": "tự; bản thân",
    "然": "như vậy; thế; đúng",
    "处": "nơi; chỗ; xử lý",
    "理": "lý; lý lẽ; xử lý",
    "于": "ở; tại; đối với",
    "铁": "sắt",
    "冬": "mùa đông",
    "物": "vật; sự vật",
    "园": "vườn; khuôn viên",
    "音": "âm; âm thanh",
    "而": "mà; và; còn",
    "且": "và; lại; hơn nữa",
    "便": "tiện; thuận tiện",
    "心": "tim; lòng; tâm",
    "钟": "chuông; đồng hồ",
    "务": "việc; công việc; phục vụ",
    "感": "cảm; cảm giác; cảm nhận",
    "活": "sống; hoạt động",
    "共": "cùng; chung; tổng cộng",
    "司": "quản lý; cơ quan; công ty",
    "故": "cố; nguyên nhân; sự việc",
    "顾": "quan tâm; chăm nom; ngoảnh nhìn",
    "广": "rộng; rộng lớn",
    "际": "ranh giới; khoảng; quốc tế",
    "合": "hợp; phù hợp; kết hợp",
    "适": "thích hợp; phù hợp",
    "板": "tấm; bảng",
    "忽": "bỗng; chợt; lơ là",
    "护": "bảo vệ; che chở",
    "照": "chiếu; chụp; theo; chăm sóc",
    "迎": "đón; chào đón",
    "者": "người; người mà...",
    "计": "tính; kế; kế hoạch",
    "划": "vạch; phân chia; hoạch định",
    "庭": "sân; gia đình",
    "检": "kiểm tra; kiểm nghiệm",
    "健": "khỏe; khỏe mạnh",
    "康": "khỏe mạnh; an khang",
    "饺": "sủi cảo; bánh chẻo",
    "育": "nuôi dưỡng; giáo dục",
    "受": "nhận; chịu; chịu đựng",
    "目": "mắt; mục; mục tiêu",
    "结": "kết; nối; kết quả",
    "入": "vào; gia nhập",
    "经": "qua; kinh qua; thường",
    "可": "có thể; được; đáng",
    "以": "dùng; lấy; để; bằng",
    "堂": "phòng lớn; sảnh; lớp",
    "空": "trống; không; bầu trời",
    "餐": "bữa ăn; ăn",
    "乐": "vui; vui vẻ; âm nhạc",
    "筷": "đũa",
    "篮": "giỏ; rổ",
    "王": "vua; họ Vương",
    "礼": "lễ; lễ phép; quà",
    "例": "ví dụ; trường hợp",
    "利": "lợi; lợi ích; thuận lợi",
    "旅": "du lịch; chuyến đi",
    "游": "đi chơi; du lịch; bơi",
    "努": "cố gắng; nỗ lực",
    "力": "sức; lực; sức lực",
    "宜": "thích hợp; phù hợp",
    "漂": "trôi; nổi; đẹp trong từ 漂亮",
    "普": "phổ biến; phổ thông",
    "其": "nó; của nó; đó; trong đó",
    "温": "ấm; nhiệt độ",
    "青": "xanh; trẻ; thanh niên",
    "清": "trong; sạch; rõ",
    "楚": "rõ; rõ ràng",
    "秋": "mùa thu",
    "实": "thật; thực; thực tế",
    "食": "ăn; thức ăn",
    "使": "khiến; làm cho; sử dụng",
    "舒": "thoải mái; thư giãn",
    "顺": "thuận; thuận lợi; theo",
    "虽": "mặc dù; tuy",
    "随": "theo; tùy; cùng",
    "所": "nơi; chỗ; sở",
    "阳": "mặt trời; dương",
    "态": "trạng thái; thái độ",
    "讨": "thảo luận; đòi; xin",
    "论": "bàn luận; luận",
    "特": "đặc biệt; riêng",
    "味": "vị; mùi vị",
    "惯": "quen; thói quen",
    "澡": "tắm",
    "夏": "mùa hè",
    "相": "lẫn nhau; nhau; xem",
    "许": "cho phép; có lẽ",
    "颜": "mặt; sắc; màu",
    "睛": "con ngươi; mắt",
    "已": "đã; rồi",
    "椅": "ghế",
    "般": "loại; dạng; như",
    "直": "thẳng; trực tiếp; luôn",
    "因": "nguyên nhân; vì",
    "银": "bạc; màu bạc",
    "英": "Anh; ưu tú; hoa",
    "永": "vĩnh viễn; lâu dài",
    "言": "lời nói; nói; ngôn ngữ",
    "原": "ban đầu; nguyên; nguồn gốc",
    "愿": "mong muốn; nguyện; sẵn lòng",
    "运": "vận chuyển; vận động; vận hành",
    "晨": "sáng sớm; buổi sáng",
    "确": "chính xác; chắc chắn",
    "末": "cuối; cuối cùng",
    "主": "chủ; chính; chủ yếu",
    "己": "bản thân; mình",
    "由": "do; bởi; từ",
    "业": "nghề; nghiệp; công việc",
}


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def main():

    print("=" * 70)
    print("BUOC 10 - DIEN NGHIA TIENG VIET CHO CHU HAN HSK2")
    print("KHONG GHI SQL")
    print("=" * 70)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file:\n{INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        fieldnames = reader.fieldnames
        rows = list(reader)

    if len(rows) != 299:
        raise ValueError(
            f"Du kien 299 chu HSK2, "
            f"nhung file co {len(rows)}."
        )

    missing_before = []
    filled = 0

    for row in rows:

        char = clean(
            row.get("KyTu")
        )

        meaning = clean(
            row.get("NghiaTiengViet")
        )

        if not meaning:
            missing_before.append(char)

            if char in MEANINGS:

                row["NghiaTiengViet"] = (
                    MEANINGS[char]
                )

                filled += 1

                # Xoa co THIEU_NGHIA
                flags = [
                    item.strip()
                    for item in clean(
                        row.get("CanBoSung")
                    ).split(";")
                    if item.strip()
                ]

                flags = [
                    item
                    for item in flags
                    if item != "THIEU_NGHIA"
                ]

                row["CanBoSung"] = (
                    "; ".join(flags)
                )

    still_missing = [
        clean(row.get("KyTu"))
        for row in rows
        if not clean(
            row.get("NghiaTiengViet")
        )
    ]

    # Bat buoc khong duoc con chu nao thieu nghia
    if still_missing:
        raise ValueError(
            "Van con chu chua co nghia:\n"
            + ", ".join(still_missing)
        )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print()
    print(
        f"Tong chu HSK2: "
        f"{len(rows)}"
    )

    print(
        f"Chu thieu nghia truoc khi xu ly: "
        f"{len(missing_before)}"
    )

    print(
        f"Da dien nghia: "
        f"{filled}"
    )

    print(
        f"Con thieu nghia: "
        f"{len(still_missing)}"
    )

    print()
    print("Da tao:")
    print(OUTPUT_FILE)

    print()
    print("KHONG INSERT/UPDATE/DELETE SQL.")


if __name__ == "__main__":
    main()