
import json
from pathlib import Path

ROOT = Path(r"D:\DATN1\scripts\shadowing\previews")
SOURCE = ROOT / "wo_de_xin_nian_ji_hua_generated_zh.json"
OUTPUT = ROOT / "wo_de_xin_nian_ji_hua_review.txt"

with SOURCE.open("r", encoding="utf-8") as f:
    data = json.load(f)

content = data["content"]

def format_time(ms):
    seconds = ms // 1000
    return f"{seconds // 60:02d}:{seconds % 60:02d}"

with OUTPUT.open("w", encoding="utf-8") as f:
    f.write("我的新年计划 - Transcript Supadata\n")
    f.write(f"So doan: {len(content)}\n\n")

    current_group = None
    fragments = []

    for item in content:
        offset = int(item["offset"])
        group = offset // 10000  # Mỗi nhóm 10 giây

        if current_group is not None and group != current_group:
            f.write(
                f"[{format_time(current_group * 10000)}] "
                + " ".join(fragments)
                + "\n"
            )
            fragments = []

        current_group = group
        fragments.append(item["text"].strip())

    if fragments:
        f.write(
            f"[{format_time(current_group * 10000)}] "
            + " ".join(fragments)
            + "\n"
        )

print("===== CHUAN BI THANH CONG =====")
print("So doan transcript:", len(content))
print("File kiem tra:", OUTPUT)
print("Khong goi Supadata")
print("Chua thay doi SQL Server")
