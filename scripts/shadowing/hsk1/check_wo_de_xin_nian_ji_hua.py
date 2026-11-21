
import json
from pathlib import Path

ROOT = Path(r"D:\DATN1\scripts\shadowing\hsk1\previews")
SOURCE = ROOT / "wo_de_xin_nian_ji_hua_final_preview.json"
REPORT = ROOT / "wo_de_xin_nian_ji_hua_check_report.txt"

with SOURCE.open("r", encoding="utf-8") as f:
    data = json.load(f)

errors = []
warnings = []
sentences = data.get("sentences", [])

# 1. Kiểm tra cấu trúc chung
if data.get("module") != "shadowing":
    errors.append("Module không đúng.")

if data.get("youtube_id") != "o6ilprwO6w0":
    errors.append("YouTube ID không đúng.")

if len(sentences) != 70:
    errors.append(f"Số câu không đúng: {len(sentences)}")

# 2. Kiểm tra từng câu
for i, s in enumerate(sentences, start=1):
    for key in ("start", "end", "hanzi", "pinyin", "vi"):
        if key not in s:
            errors.append(f"Câu {i}: thiếu {key}")

    if not all(k in s for k in
               ("start", "end", "hanzi", "pinyin", "vi")):
        continue

    start = s["start"]
    end = s["end"]

    if not isinstance(start, (int, float)) or \
       not isinstance(end, (int, float)):
        errors.append(f"Câu {i}: timestamp không hợp lệ")
        continue

    if start >= end:
        errors.append(f"Câu {i}: start >= end")

    if start < 0 or end > 425:
        errors.append(f"Câu {i}: thời gian vượt phạm vi video")

    for key in ("hanzi", "pinyin", "vi"):
        if not isinstance(s[key], str) or not s[key].strip():
            errors.append(f"Câu {i}: {key} đang trống")

    if i > 1:
        previous = sentences[i - 2]

        if "end" in previous and isinstance(
            previous["end"], (int, float)
        ):
            if start < previous["end"]:
                errors.append(
                    f"Câu {i}: thời gian chồng câu trước"
                )

            gap = start - previous["end"]
            if gap > 2:
                warnings.append(
                    f"Câu {i}: khoảng trống {gap:.2f} giây "
                    f"trước câu này"
                )

    duration = end - start
    if duration > 12:
        warnings.append(
            f"Câu {i}: thời lượng dài {duration:.2f} giây"
        )

# 3. Kiểm tra câu bị trùng hoàn toàn
seen = {}

for i, s in enumerate(sentences, start=1):
    text = s.get("hanzi", "").strip()

    if text in seen:
        warnings.append(
            f"Câu {i} trùng Hanzi với câu {seen[text]}"
        )
    else:
        seen[text] = i

# 4. Tạo báo cáo để kiểm tra thủ công
lines = [
    "KIEM TRA SHADOWING - WO DE XIN NIAN JI HUA",
    "=" * 60,
    f"YouTube ID: {data.get('youtube_id')}",
    f"Tong so cau: {len(sentences)}",
    "",
    f"SO LOI: {len(errors)}",
    *errors,
    "",
    f"SO CANH BAO: {len(warnings)}",
    *warnings,
    "",
    "DANH SACH 70 CAU",
    "=" * 60,
]

for i, s in enumerate(sentences, start=1):
    start = s.get("start", 0)
    end = s.get("end", 0)

    lines.extend([
        f"\nCAU {i:02d} [{start:.2f}s - {end:.2f}s]",
        f"ZH: {s.get('hanzi', '')}",
        f"PY: {s.get('pinyin', '')}",
        f"VI: {s.get('vi', '')}",
    ])

REPORT.write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print("===== KIEM TRA VIDEO 5 =====")
print("Tong so cau:", len(sentences))
print("So loi:", len(errors))
print("So canh bao:", len(warnings))
print("Bao cao:", REPORT)

if errors:
    print("KET QUA: CAN SUA LOI")
else:
    print("KET QUA: DAT KIEM TRA CAU TRUC")
    print("Van can doi chieu noi dung va audio")

print("Chua thay doi SQL Server")
