
from pathlib import Path
import json
import re
from pypinyin import lazy_pinyin, Style

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk2\data\processed")

SOURCE = BASE / "video3_zh_preview.json"
OUTPUT = BASE / "video3_with_pinyin.json"
TXT_OUTPUT = BASE / "video3_transcript.txt"

data = json.loads(SOURCE.read_text(encoding="utf-8"))

sentences = []

for i, item in enumerate(data["sentences"], 1):
    hanzi = re.sub(r"\s+", "", item["hanzi"]).strip()

    pinyin = " ".join(
        lazy_pinyin(hanzi, style=Style.TONE)
    )

    pinyin = re.sub(
        r"[，。！？；：、,.!?;:]+",
        "",
        pinyin
    )

    pinyin = re.sub(r"\s+", " ", pinyin).strip()

    sentences.append({
        "start": item["start"],
        "end": item["end"],
        "hanzi": hanzi,
        "pinyin": pinyin,
        "vi": ""
    })

result = {
    "module": "shadowing",
    "youtube_id": data["youtube_id"],
    "title": data["title"],
    "status": "needs_translation",
    "sentences": sentences
}

OUTPUT.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

with TXT_OUTPUT.open("w", encoding="utf-8") as f:
    for i, s in enumerate(sentences, 1):
        f.write(
            f"{i:03d} [{s['start']:.2f}-{s['end']:.2f}] "
            f"{s['hanzi']}\n"
        )

print("===== KET QUA =====")
print("So cau:", len(sentences))
print("JSON:", OUTPUT)
print("Transcript:", TXT_OUTPUT)

print("\n===== 5 CAU DAU =====")
for i, s in enumerate(sentences[:5], 1):
    print(i, s["hanzi"])
    print("Pinyin:", s["pinyin"])

print("\nCHUA CAP NHAT SQL SERVER.")
