
import json
from pathlib import Path

folder = Path(r"D:\DATN1\scripts\shadowing\previews")
source = folder / "3G9eT9c2bP8.json"
output = folder / "emily_shadowing_cau_chuyen.json"

translations = [
    "Cô Vương sống ở Thượng Hải.",
    "Cô ấy là người Thượng Hải.",
    "Năm nay cô ấy 24 tuổi.",
    "Gia đình cô ấy có ba người.",
    "Bố, mẹ và cô ấy.",
    "Cô ấy sống một mình.",
    "Buổi sáng cô ấy lái xe đến công ty làm việc.",
    "Cô ấy rất thích công việc của mình.",
    "Đồng nghiệp của cô ấy có người Mỹ.",
    "Cũng có người Anh.",
    "Buổi chiều, cô Vương cùng đồng nghiệp đến quán cà phê.",
    "Cô ấy thích uống cà phê.",
    "Cô ấy và các đồng nghiệp uống cà phê ở quán.",
    "Ăn bánh sandwich và salad trái cây.",
    "Thứ Bảy và Chủ nhật,",
    "Cô Vương không đến công ty.",
    "Cô ấy đến cửa hàng mua đồ.",
    "Xem phim cùng bạn bè.",
    "Đến hiệu sách đọc sách.",
    "Khi ở nhà,",
    "Cô ấy thích xem tivi và đọc sách.",
    "Cô ấy cũng thích gọi điện cho bạn bè khi trời mưa.",
    "Tháng Ba, tháng Tư và tháng Năm,",
    "Thượng Hải rất đẹp.",
    "Vào tháng Sáu,",
    "Ngày nào ở Thượng Hải cũng mưa.",
    "Tháng Bảy và tháng Tám, thời tiết rất nóng.",
    "Tháng Mười Một và tháng Mười Hai, thời tiết rất lạnh.",
    "Nhà cô Vương có một con mèo.",
    "Con mèo nhỏ tên là Tiểu Tiểu.",
    "Khi trời mưa,",
    "Tiểu Tiểu thích ngủ trên ghế sofa.",
    "Khi thời tiết đẹp,",
    "Tiểu Tiểu thích chơi ở bên ngoài.",
    "Cô Vương chưa có bạn trai.",
    "Cô ấy rất muốn có một người bạn trai.",
    "Cùng anh ấy uống cà phê.",
    "Xem phim.",
    "Đến cửa hàng mua đồ.",
    "Cô ấy không thích cuộc sống một mình.",
    "Cô Vương rất thích Thượng Hải.",
    "Thích cuộc sống ở đây.",
    "Thích thời tiết ở đây.",
    "Ngày nào cô ấy cũng rất vui."
]

data = json.loads(source.read_text(encoding="utf-8-sig"))

# Chỉ chọn phần câu chuyện, bỏ giới thiệu và giảng từ vựng.
sentences = [
    s for s in data["sentences"]
    if s["start"] >= 18.9 and s["end"] <= 245.366
]

if len(sentences) != len(translations):
    raise ValueError(
        f"So cau khong khop: {len(sentences)} / {len(translations)}"
    )

for sentence, translation in zip(sentences, translations):
    sentence["vi"] = translation

data["sentences"] = sentences

output.write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("DA TAO JSON SHADOWING")
print("So cau:", len(sentences))
print("File:", output)
