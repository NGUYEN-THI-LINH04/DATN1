
from pathlib import Path
import json

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk2\data\processed")
SOURCE = BASE / "video3_with_pinyin.json"
OUTPUT = BASE / "video3_translated_draft.json"

# Ban dich tieng Viet, theo dung thu tu phu de.
translations = {
    1: "Xin chào mọi người! Chào mừng đến với 'Tiếng Trung mỗi ngày'. Tôi là Lý Minh.",
    2: "Xin chào mọi người! Tôi là Vương Vũ.",
    3: "Lý Minh, chào bạn!",
    4: "Vương Vũ, chào bạn!",
    5: "Hôm nay trông bạn rất vui. Có chuyện gì vui sao?",
    6: "Ừ! Đúng là có một chuyện.",
    7: "Tôi có một người bạn Việt Nam, cô ấy tên là Tiểu Nguyệt.",
    8: "Cô ấy mới học tiếng Trung được ba tháng, nhưng bây giờ đã có thể nói được khá nhiều tiếng Trung rồi.",
    9: "Thật sao? Ba tháng thôi à?",
    10: "Như vậy là rất khá đấy!",
    11: "Đúng vậy! Tôi thấy cô ấy rất giỏi.",
    12: "Ngày nào cô ấy cũng tiến bộ.",
    13: "Vì thế, hôm nay tôi chợt nghĩ rằng, khi học một ngôn ngữ mới,",
    14: "chẳng hạn như tiếng Trung, liệu có những phương pháp rất đơn giản nhưng lại hữu ích,",
    15: "có thể giúp chúng ta tiến bộ từng chút một mỗi ngày không?",
    16: "Câu hỏi hay đấy!",
    17: "Đây thực sự là một câu hỏi rất hay.",
    18: "Có lẽ nhiều bạn đang học tiếng Trung đều từng nghĩ rằng:",
    19: "Ngày nào tôi cũng bận, không có nhiều thời gian, vậy phải học thế nào?",
    20: "Thực ra có rất nhiều việc nhỏ mà chúng ta có thể làm mỗi ngày.",
    21: "Đúng, đúng, đúng!",
    22: "Chính là ý đó!",
    23: "Không phải ngày nào cũng phải học năm tiếng, mà là chúng ta có thể làm những việc nhỏ nào,",
    24: "chỉ cần mười hoặc hai mươi phút mỗi ngày cũng có ích.",
    25: "Chính xác.",
    26: "Vậy hôm nay, chúng ta cùng trò chuyện về chủ đề này nhé:",
    27: "Những phương pháp học tiếng Trung đơn giản giúp chúng ta tiến bộ từng chút một mỗi ngày.",
    28: "Tuyệt quá!",
    29: "Chủ đề này rất hữu ích.",
    30: "Các bạn thính giả, mọi người đã sẵn sàng chưa?",
    31: "Chúng ta bắt đầu nhé!",
    32: "Được rồi, Vương Vũ, nếu chọn phương pháp đầu tiên, bạn sẽ nói gì?",
    33: "Ừm... Để tôi nghĩ xem. Tôi thấy phương pháp đầu tiên, cũng là đơn giản nhất,",
    34: "là đưa tiếng Trung vào cuộc sống, để ngày nào bạn cũng nhìn thấy và nghe thấy nó.",
    35: "Ồ? Ý bạn là sao? Bạn có thể giải thích rõ hơn một chút không?",
    36: "Được chứ. Ví dụ, tất cả chúng ta đều có điện thoại, đúng không?",
    37: "Chúng ta có thể đổi ngôn ngữ trên điện thoại từ tiếng mẹ đẻ sang tiếng Trung.",
    38: "À, tôi từng nghe phương pháp này rồi! Bạn đã thử chưa?",
    39: "Tôi thử rồi! Khi học tiếng Anh, tôi cũng làm như vậy.",
    40: "Ban đầu, tôi chẳng hiểu gì cả và cảm thấy rất khó.",
    41: "Những từ như 'Cài đặt', 'Tin nhắn', 'Điện thoại' trên điện thoại, tôi đều không biết.",
    42: "Vậy bạn đã làm thế nào?",
    43: "Tôi đoán nghĩa! Hoặc hỏi bạn bè xem từ đó có nghĩa là gì.",
    44: "Sau một, hai tuần, tôi đã biết hết những từ đó.",
    45: "Bởi vì ngày nào bạn cũng phải dùng điện thoại,",
    46: "nên bạn nhìn thấy những từ này rất nhiều lần và nhanh chóng ghi nhớ chúng.",
    47: "Tôi hiểu rồi. Đây là một phương pháp rất hay.",
    48: "Ngày nào cũng nhìn, ngày nào cũng dùng, giống như ăn cơm uống nước, dần dần sẽ thành thói quen.",
    49: "Những bạn đang học tiếng Trung cũng có thể làm như vậy.",
    50: "Trên điện thoại của bạn có 'WeChat', 'Máy ảnh', 'Thời tiết',"
}

data = json.loads(SOURCE.read_text(encoding="utf-8"))

if len(data["sentences"]) != 259:
    raise ValueError("So luong cau khong phai 259!")

for i, sentence in enumerate(data["sentences"], 1):
    if i in translations:
        sentence["vi"] = translations[i]

data["status"] = "translation_in_progress"

OUTPUT.write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

translated_count = sum(
    bool(s.get("vi")) for s in data["sentences"]
)

print("Da dich:", translated_count, "/ 259 cau")
print("Da luu:", OUTPUT)
print("CHUA CAP NHAT SQL SERVER.")
