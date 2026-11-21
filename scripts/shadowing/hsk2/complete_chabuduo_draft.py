
from pathlib import Path
import json
from pypinyin import lazy_pinyin, Style

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk2")
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

SOURCE = RAW / "video_chabuduo_supadata.json"
OUTPUT = PROCESSED / "video_chabuduo_full_draft.json"

# Cac cau tieng Trung duoc de xuat tu ban dich tieng Anh,
# doi chieu voi cac manh ASR tieng Trung khi co.
# CHUA DUOC XAC MINH LA LOI THOAI GOC.

hanzi_rows = [
    "娜娜有一个姐姐。",
    "她们的年龄差不多。",
    "姐姐十六岁。",
    "娜娜十五岁。",
    "她们长得差不多一样漂亮。",
    "她们都有一双大大的眼睛，",
    "头发差不多一样长。",
    "她们的身高也差不多。",
    "姐姐一米六五。",
    "娜娜一米六二。",
    "她们都在上初中，",
    "在同一所学校上学。",
    "她们的成绩差不多一样好。",
    "虽然她们长得差不多，",
    "但是性格差很多。",
    "娜娜很喜欢说话和笑。",
    "她喜欢和朋友们在一起。",
    "姐姐不太喜欢说话。",
    "她更喜欢一个人待着。",
    "妈妈很爱娜娜。",
    "她也很爱姐姐。",
    "她对两个女儿的爱是一样的。",
    "妈妈差不多五十岁了，",
    "但是看起来只有四十岁左右。",
    "妈妈和爸爸的生日差不多在同一天。",
    "妈妈的生日是五月五日。",
    "爸爸的生日是五月六日。",
    "每年，",
    "他们都一起过生日。",
    "妈妈每年的生日愿望都差不多。",
    "她希望",
    "自己的女儿们健康快乐。",
    "爸爸每年的生日愿望",
    "也差不多，都一样。",
    "他希望一家人",
    "永远开心幸福。"
]

vi_rows = [
    "Na Na có một người chị gái.",
    "Hai chị em gần bằng tuổi nhau.",
    "Chị gái 16 tuổi.",
    "Na Na 15 tuổi.",
    "Hai chị em có ngoại hình xinh đẹp gần giống nhau.",
    "Cả hai đều có đôi mắt to,",
    "tóc dài gần bằng nhau.",
    "Chiều cao của hai chị em cũng gần bằng nhau.",
    "Chị gái cao 1 mét 65.",
    "Na Na cao 1 mét 62.",
    "Cả hai đều đang học cấp hai,",
    "học cùng một trường.",
    "Thành tích học tập của hai chị em đều tốt gần như nhau.",
    "Tuy ngoại hình hai chị em khá giống nhau,",
    "nhưng tính cách lại khác nhau rất nhiều.",
    "Na Na rất thích nói chuyện và cười.",
    "Cô ấy thích ở bên bạn bè.",
    "Chị gái không thích nói chuyện lắm.",
    "Chị ấy thích ở một mình hơn.",
    "Mẹ rất yêu Na Na.",
    "Mẹ cũng rất yêu chị gái.",
    "Tình yêu mẹ dành cho hai con gái là như nhau.",
    "Mẹ khoảng 50 tuổi,",
    "nhưng trông chỉ khoảng 40 tuổi.",
    "Sinh nhật bố và mẹ rất gần nhau.",
    "Sinh nhật mẹ là ngày 5 tháng 5.",
    "Sinh nhật bố là ngày 6 tháng 5.",
    "Hằng năm,",
    "họ đều tổ chức sinh nhật cùng nhau.",
    "Điều ước sinh nhật mỗi năm của mẹ gần như giống nhau.",
    "Mẹ mong",
    "các con gái luôn khỏe mạnh, vui vẻ.",
    "Điều ước sinh nhật mỗi năm của bố",
    "cũng gần giống như vậy.",
    "Bố mong cả gia đình",
    "mãi mãi vui vẻ và hạnh phúc."
]

data = json.loads(SOURCE.read_text(encoding="utf-8"))
content = data["content"]

if len(content) != len(hanzi_rows) or len(content) != len(vi_rows):
    raise ValueError(
        f"So luong khong khop: "
        f"English={len(content)}, "
        f"Hanzi={len(hanzi_rows)}, "
        f"Vietnamese={len(vi_rows)}"
    )

sentences = []

for i, item in enumerate(content):
    start = round(item["offset"] / 1000, 3)
    end = round(
        (item["offset"] + item["duration"]) / 1000,
        3
    )

    hanzi = hanzi_rows[i]

    sentences.append({
        "start": start,
        "end": end,
        "hanzi": hanzi,
        "pinyin": " ".join(
            lazy_pinyin(hanzi, style=Style.TONE)
        ),
        "vi": vi_rows[i],
        "english_reference": item["text"],
        "needs_audio_review": True
    })

result = {
    "module": "shadowing",
    "youtube_id": "VkEYoXw7jD0",
    "title": "差不多 - Gần giống nhau",
    "status": "draft_needs_audio_review",
    "sentences": sentences
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

OUTPUT.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Da tao:", OUTPUT)
print("So cau:", len(sentences))
print("Khoang thoi gian:", sentences[0]["start"],
      "->", sentences[-1]["end"])
print("Tat ca cau deu can doi chieu am thanh.")
print("CHUA CAP NHAT SQL SERVER.")
