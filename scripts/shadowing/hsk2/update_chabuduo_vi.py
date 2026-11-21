
from pathlib import Path
import json

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk2")
PROCESSED = BASE / "data" / "processed"

SOURCE = PROCESSED / "video_chabuduo_full_draft.json"
OUTPUT = PROCESSED / "video_chabuduo_review_v2.json"

# Ban dich dua tren 36 dong phu de ban cung cap.
# Chi chinh sua dau cau va cach dien dat cho tu nhien.

vi_rows = [
    "Na Na có một người chị gái.",
    "Hai chị em gần bằng tuổi nhau.",
    "Chị gái 16 tuổi.",
    "Na Na 15 tuổi.",
    "Cả hai đều xinh đẹp.",
    "Cả hai đều có đôi mắt to.",
    "Và mái tóc dài gần bằng nhau.",
    "Chiều cao của hai chị em cũng gần giống nhau.",
    "Chị gái cao 1,65 mét.",
    "Na Na cao 1,62 mét.",
    "Cả hai đều đang học trung học.",
    "Và học cùng một trường.",
    "Kết quả học tập cũng tốt như nhau.",
    "Mặc dù trông hai chị em khá giống nhau,",
    "Nhưng tính cách lại rất khác nhau.",
    "Na Na thích nói chuyện và thích cười.",
    "Cô ấy thích ở cùng bạn bè.",
    "Chị gái của Na Na không thích nói chuyện.",
    "Chị ấy thích ở một mình.",
    "Mẹ rất yêu Na Na.",
    "Mẹ cũng rất yêu chị gái của Na Na.",
    "Mẹ yêu thương hai chị em như nhau.",
    "Mẹ khoảng 50 tuổi.",
    "Nhưng trông mẹ chỉ như 40 tuổi.",
    "Sinh nhật của bố và mẹ rất gần nhau.",
    "Sinh nhật mẹ là ngày 5 tháng 5.",
    "Sinh nhật bố là ngày 6 tháng 5.",
    "Mỗi năm,",
    "Họ đều tổ chức sinh nhật cùng nhau.",
    "Điều ước sinh nhật mỗi năm của mẹ đều giống nhau.",
    "Mẹ ước rằng",
    "Hai con gái luôn khỏe mạnh và vui vẻ.",
    "Điều ước sinh nhật mỗi năm của bố",
    "Cũng giống như những năm trước.",
    "Bố mong cả gia đình",
    "Mãi mãi vui vẻ và hạnh phúc."
]

if not SOURCE.exists():
    raise FileNotFoundError(
        "Chua co file full draft. "
        "Hay chay complete_chabuduo_draft.py truoc."
    )

data = json.loads(SOURCE.read_text(encoding="utf-8"))
sentences = data["sentences"]

if len(sentences) != 36 or len(vi_rows) != 36:
    raise ValueError(
        f"So cau khong khop: "
        f"{len(sentences)} vs {len(vi_rows)}"
    )

for i, sentence in enumerate(sentences):
    sentence["vi"] = vi_rows[i]
    sentence["needs_audio_review"] = True

data["status"] = "draft_needs_audio_review"
data["translation_source"] = "user_provided_vietnamese_subtitles"

OUTPUT.write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("===== KET QUA =====")
print("Da tao:", OUTPUT)
print("So cau:", len(sentences))

print("\n===== 5 CAU DAU =====")

for i, s in enumerate(sentences[:5], 1):
    print(f"\n{i}. [{s['start']} - {s['end']}]")
    print("Hanzi:", s["hanzi"])
    print("Pinyin:", s["pinyin"])
    print("Tieng Viet:", s["vi"])

print("\nCHUA CAP NHAT SQL SERVER.")
