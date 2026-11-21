
from pathlib import Path
import json
import re
from pypinyin import lazy_pinyin, Style

# ==================================================
# 1. CAU HINH
# ==================================================

ROOT = Path(r"D:\DATN1")
BASE = ROOT / "scripts" / "shadowing" / "hsk2"
DATA_DIR = BASE / "data" / "processed"

SOURCE = DATA_DIR / "video3_translated_full.json"
OUTPUT = DATA_DIR / "video3_ready_for_review.json"
REPORT = DATA_DIR / "video3_review_report.txt"

VIDEO_ID = "uv8KNcXpels"

# Cac nhom phu de can ghep lai.
MERGE_GROUPS = [
    [149, 150],
    [152, 153],
    [155, 156, 157],
    [159, 160],
    [201, 202],
    [225, 226],
]

# Ban dich hoan chinh cho nhung nhom bi cat giua tu.
VI_OVERRIDES = {
    155: (
        "Tôi chỉ vào hình trên thực đơn và nói: "
        "'Cái này... cỡ lớn... nóng.' "
        "Mặc dù tôi nói chưa tốt nhưng nhân viên "
        "vẫn hiểu. Anh ấy đưa cho tôi một cốc "
        "cà phê cỡ lớn và nóng."
    ),
    225: (
        "Hãy để việc viết trở thành một hoạt động "
        "nhẹ nhàng và vui vẻ."
    ),
}


# ==================================================
# 2. HAM CHUAN HOA
# ==================================================

def clean_hanzi(value):
    text = str(value or "").strip()

    # Loai bo khoang trang thua, xuong dong.
    text = re.sub(r"\s+", "", text)

    return text


def clean_vi(value):
    return re.sub(
        r"\s+", " ", str(value or "")
    ).strip()


def make_pinyin(hanzi):
    """
    Tao pinyin tu chu Han.
    Chi giu am tiet va dau thanh,
    khong chen dau cau vao dong pinyin.
    """

    tokens = re.findall(
        r"[\u3400-\u9fff]+|[A-Za-z0-9]+",
        hanzi
    )

    result = []

    for token in tokens:
        if re.fullmatch(
            r"[\u3400-\u9fff]+", token
        ):
            result.extend(
                lazy_pinyin(
                    token,
                    style=Style.TONE
                )
            )
        else:
            result.append(token)

    return " ".join(result).strip()


def merge_sentences(group):
    """
    Ghep cac doan lien tiep:
    - start: doan dau
    - end: doan cuoi
    - hanzi: noi truc tiep
    - vi: ghep ban dich
    """

    first = group[0]
    last = group[-1]

    hanzi = "".join(
        clean_hanzi(s["hanzi"])
        for s in group
    )

    vi = " ".join(
        clean_vi(s["vi"])
        for s in group
    )

    vi = clean_vi(vi)

    return {
        "start": float(first["start"]),
        "end": float(last["end"]),
        "hanzi": hanzi,
        "pinyin": make_pinyin(hanzi),
        "vi": vi,
    }


# ==================================================
# 3. DOC VA KIEM TRA DU LIEU GOC
# ==================================================

if not SOURCE.exists():
    raise FileNotFoundError(
        f"Khong tim thay: {SOURCE}"
    )

data = json.loads(
    SOURCE.read_text(encoding="utf-8")
)

if data.get("youtube_id") != VIDEO_ID:
    raise ValueError("YouTube ID khong khop!")

original = data.get("sentences", [])

if len(original) != 259:
    raise ValueError(
        f"Can 259 doan, hien co {len(original)}"
    )

for number, s in enumerate(original, 1):
    for key in (
        "start", "end", "hanzi", "pinyin", "vi"
    ):
        if key not in s or s[key] in ("", None):
            raise ValueError(
                f"Doan {number} thieu {key}"
            )


# ==================================================
# 4. XAC DINH NHOM GHEP
# ==================================================

merge_start = {}
covered_numbers = set()

for group in MERGE_GROUPS:
    if len(group) < 2:
        raise ValueError("Nhom ghep qua ngan!")

    if group != list(
        range(group[0], group[-1] + 1)
    ):
        raise ValueError(
            f"Nhom khong lien tiep: {group}"
        )

    for n in group:
        if n < 1 or n > len(original):
            raise ValueError(
                f"STT khong hop le: {n}"
            )

        if n in covered_numbers:
            raise ValueError(
                f"Doan {n} nam trong nhieu nhom!"
            )

        covered_numbers.add(n)

    merge_start[group[0]] = group


# ==================================================
# 5. GHEP VA CHUAN HOA
# ==================================================

result_sentences = []
index = 1

while index <= len(original):

    if index in merge_start:
        group_numbers = merge_start[index]

        selected = [
            original[n - 1]
            for n in group_numbers
        ]

        item = merge_sentences(selected)

        if index in VI_OVERRIDES:
            item["vi"] = VI_OVERRIDES[index]

        result_sentences.append(item)

        index = group_numbers[-1] + 1

    else:
        original_item = original[index - 1]

        hanzi = clean_hanzi(
            original_item["hanzi"]
        )

        result_sentences.append({
            "start": float(
                original_item["start"]
            ),
            "end": float(
                original_item["end"]
            ),
            "hanzi": hanzi,
            "pinyin": make_pinyin(hanzi),
            "vi": clean_vi(
                original_item["vi"]
            ),
        })

        index += 1


# ==================================================
# 6. KIEM TRA DU LIEU SAU KHI GHEP
# ==================================================

expected_count = 259 - sum(
    len(group) - 1
    for group in MERGE_GROUPS
)

if len(result_sentences) != expected_count:
    raise ValueError(
        "So luong sau ghep khong dung!"
    )

long_sentences = []
overlaps = []

for i, s in enumerate(result_sentences, 1):

    if not all([
        s["hanzi"],
        s["pinyin"],
        s["vi"]
    ]):
        raise ValueError(
            f"Thieu noi dung o cau {i}"
        )

    if s["start"] < 0:
        raise ValueError(
            f"Thoi gian am o cau {i}"
        )

    if s["end"] <= s["start"]:
        raise ValueError(
            f"Timestamp sai o cau {i}"
        )

    duration = s["end"] - s["start"]

    # Cac cau dai can duoc nghe kiem tra.
    if duration > 10:
        long_sentences.append(
            (i, round(duration, 2))
        )

    if i > 1:
        previous = result_sentences[i - 2]

        if s["start"] < previous["end"] - 0.001:
            overlaps.append(i)

if overlaps:
    raise ValueError(
        f"Timestamp chong nhau: {overlaps}"
    )


# ==================================================
# 7. LUU JSON DE KIEM TRA
# ==================================================

final_data = {
    "module": "shadowing",
    "youtube_id": VIDEO_ID,
    "title": (
        "每日学习法 - "
        "Phương pháp học tiếng Trung mỗi ngày"
    ),
    "sentences": result_sentences
}

OUTPUT.write_text(
    json.dumps(
        final_data,
        ensure_ascii=False,
        indent=2
    ),
    encoding="utf-8"
)

# Bao cao giu rieng, khong dua vao SQL.
report_lines = [
    "BAO CAO CHUAN HOA SHADOWING VIDEO 3",
    f"YouTube ID: {VIDEO_ID}",
    f"So doan ban dau: {len(original)}",
    f"So cau sau ghep: {len(result_sentences)}",
    f"So nhom da ghep: {len(MERGE_GROUPS)}",
    "",
    "NHOM DA GHEP:",
]

for group in MERGE_GROUPS:
    report_lines.append(str(group))

report_lines += [
    "",
    "CAU DAI HON 10 GIAY CAN KIEM TRA:",
]

for number, duration in long_sentences:
    report_lines.append(
        f"Cau {number}: {duration} giay"
    )

if not long_sentences:
    report_lines.append("Khong co.")

REPORT.write_text(
    "\n".join(report_lines),
    encoding="utf-8"
)


# ==================================================
# 8. IN KET QUA
# ==================================================

print("===== CHUAN HOA HOAN THANH =====")
print("Video:", VIDEO_ID)
print("So doan ban dau:", len(original))
print("So nhom da ghep:", len(MERGE_GROUPS))
print("So cau sau ghep:", len(result_sentences))

print("\nJSON:", OUTPUT)
print("Bao cao:", REPORT)

print("\n===== 5 CAU DAU =====")

for i, s in enumerate(result_sentences[:5], 1):
    print(f"\n{i}. [{s['start']:.2f} - {s['end']:.2f}]")
    print("Hanzi:", s["hanzi"])
    print("Pinyin:", s["pinyin"])
    print("VI:", s["vi"])

print("\nSo cau dai hon 10 giay:", len(long_sentences))
print("Timestamp chong nhau:", len(overlaps))

print("\nCHUA CAP NHAT SQL SERVER.")
