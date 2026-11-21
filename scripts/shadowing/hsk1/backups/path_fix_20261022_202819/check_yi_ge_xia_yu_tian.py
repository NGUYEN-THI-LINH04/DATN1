
import json
from pathlib import Path

path = Path(
    r"D:\DATN1\scripts\shadowing\previews"
    r"\yi_ge_xia_yu_tian_final_preview.json"
)

with path.open("r", encoding="utf-8") as f:
    data = json.load(f)

sentences = data["sentences"]

assert len(sentences) == 54
assert data["youtube_id"] == "QwlhcsAMhT0"

# Câu 24
s = sentences[23]
assert s["hanzi"] == "听朋友的声音让我觉得好一点。"

s["hanzi"] = "听她的声音让我觉得好一点。"
s["pinyin"] = (
    "tīng tā de shēng yīn "
    "ràng wǒ jué de hǎo yì diǎn 。"
)
s["vi"] = (
    "Nghe giọng nói của cô bạn "
    "khiến tôi cảm thấy khá hơn một chút."
)

# Câu 16: dùng dấu phẩy vì còn mệnh đề 但是
s = sentences[14]
assert s["hanzi"] == "虽然在家工作很方便。"
s["hanzi"] = "虽然在家工作很方便，"
s["pinyin"] = s["pinyin"].replace("。", "，")
s["vi"] = "Mặc dù làm việc ở nhà rất thuận tiện,"

# Câu 53: sửa pinyin 和
s = sentences[51]
assert "温暖和快乐" in s["hanzi"]
s["pinyin"] = s["pinyin"].replace(
    "wēn nuǎn huo kuài lè",
    "wēn nuǎn hé kuài lè"
)

# Kiểm tra lại thời gian
for i, s in enumerate(sentences):
    assert s["start"] < s["end"]

    if i > 0:
        assert (
            s["start"] >= sentences[i - 1]["end"]
        ), f"Chong thoi gian tai cau {i + 1}"

output = path.with_name(
    "yi_ge_xia_yu_tian_checked_preview.json"
)

with output.open("w", encoding="utf-8") as f:
    json.dump(
        data,
        f,
        ensure_ascii=False,
        indent=2
    )

print("===== KIEM TRA THANH CONG =====")
print("Video:", data["youtube_id"])
print("So cau:", len(sentences))
print("File:", output)
print("Chua thay doi SQL Server")
