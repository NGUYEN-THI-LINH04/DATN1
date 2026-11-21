
from pathlib import Path
import json
import re
from pypinyin import lazy_pinyin, Style

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk2\data\processed")
SOURCE = BASE / "video_chabuduo_review_v2.json"
OUTPUT = BASE / "video_chabuduo_review_v3.json"

data = json.loads(SOURCE.read_text(encoding="utf-8"))
sentences = data["sentences"]

# STT cau -> phu de chu Han tren video
verified = {
    2: "她们两个差不多大。",
    6: "都有一双大大的眼睛，",
    16: "娜娜爱说话，爱笑，",
    18: "姐姐不爱说话，",
    19: "她比较喜欢一个人。",
    21: "也很爱姐姐，",
    22: "她对两个孩子的爱是一样的。",
    24: "但是看上去差不多像四十岁。",
}

def make_pinyin(text):
    result = " ".join(
        lazy_pinyin(text, style=Style.TONE)
    )
    return re.sub(
        r"\s+([，。！？；：、])",
        "",
        result
    ).strip()

for stt, hanzi in verified.items():
    sentence = sentences[stt - 1]
    sentence["hanzi"] = hanzi
    sentence["pinyin"] = make_pinyin(hanzi)
    sentence["verified_from_video_subtitle"] = True
    sentence["needs_audio_review"] = True

data["status"] = "partially_verified"
data["verified_sentence_numbers"] = sorted(verified)

OUTPUT.write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Da luu:", OUTPUT)
print("So cau:", len(sentences))
print("So cau da sua:", len(verified))
print("Chua cap nhat SQL Server.")
