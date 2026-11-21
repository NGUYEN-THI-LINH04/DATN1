
from pathlib import Path
import json
from pypinyin import lazy_pinyin, Style

ROOT = Path(r"D:\DATN1\scripts\shadowing\hsk2")
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# Cac cau DU KIEN khoi phuc tu ASR.
# Timestamp va loi thoai can duoc doi chieu voi video.
draft_rows = [
    (28.01, 34.37,
     "她们都有一双大大的眼睛。",
     "Cả hai đều có đôi mắt to."),

    (34.37, 40.50,
     "她们的头发差不多一样长。",
     "Tóc của hai chị em dài gần bằng nhau."),

    (41.24, 46.20,
     "她们的身高也差不多。",
     "Chiều cao của hai chị em cũng gần bằng nhau."),

    (46.43, 50.50,
     "姐姐一米六五。",
     "Chị gái cao 1 mét 65."),

    (50.89, 54.60,
     "娜娜一米六二。",
     "Na Na cao 1 mét 62."),

    (55.69, 64.70,
     "她们都在上初中，在同一所学校上学。",
     "Hai chị em đều học cấp hai, cùng một trường."),

    (65.49, 71.00,
     "成绩差不多一样好。",
     "Thành tích học tập của cả hai đều tốt gần như nhau."),

    (72.71, 82.00,
     "虽然她们长得差不多，但是性格差很多。",
     "Tuy ngoại hình hai chị em khá giống nhau, "
     "nhưng tính cách lại khác nhau rất nhiều."),

    (106.50, 109.50,
     "妈妈很爱娜娜。",
     "Mẹ rất yêu Na Na."),

    (136.30, 143.80,
     "妈妈和爸爸的生日差不多在同一天。",
     "Sinh nhật bố và mẹ rất gần nhau."),

    (146.12, 151.20,
     "妈妈的生日是五月五日。",
     "Sinh nhật của mẹ là ngày 5 tháng 5."),

    (151.62, 157.00,
     "爸爸的生日是五月六日。",
     "Sinh nhật của bố là ngày 6 tháng 5."),

    (159.79, 163.30,
     "他们都一起过生日。",
     "Họ cùng nhau tổ chức sinh nhật."),

    (165.75, 171.50,
     "妈妈每年的生日愿望都差不多。",
     "Điều ước sinh nhật mỗi năm của mẹ đều gần giống nhau."),

    (172.33, 180.00,
     "她希望自己的女儿们健康快乐。",
     "Mẹ mong các con gái luôn khỏe mạnh và vui vẻ."),

    (181.05, 189.10,
     "爸爸每年的生日愿望也差不多，都一样。",
     "Điều ước sinh nhật hằng năm của bố cũng tương tự."),

    (189.38, 198.50,
     "他希望一家人永远开心幸福。",
     "Bố mong cả gia đình mãi vui vẻ, hạnh phúc."),
]

sentences = []

for start, end, hanzi, vi in draft_rows:
    pinyin = " ".join(
        lazy_pinyin(hanzi, style=Style.TONE)
    )

    sentences.append({
        "start": start,
        "end": end,
        "hanzi": hanzi,
        "pinyin": pinyin,
        "vi": vi,
        "needs_review": True
    })

data = {
    "module": "shadowing",
    "youtube_id": "VkEYoXw7jD0",
    "title": "差不多 - Gần giống nhau",
    "status": "draft_needs_audio_review",
    "source": "reconstructed_from_noisy_asr",
    "missing_ranges": [
        [0, 28.01],
        [82.0, 106.5],
        [109.5, 136.3],
        [143.8, 146.12]
    ],
    "sentences": sentences
}

output_file = OUT / "video_chabuduo_draft_review.json"

output_file.write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Da tao ban nhap:", output_file)
print("So cau:", len(sentences))
print("CHUA CAP NHAT SQL SERVER.")
print("Can kiem tra voi am thanh truoc khi su dung.")
