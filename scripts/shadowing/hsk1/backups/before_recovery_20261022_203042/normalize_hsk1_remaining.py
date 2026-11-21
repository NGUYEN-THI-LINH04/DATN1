
import json
import re
from pathlib import Path

from difflib import SequenceMatcher
from pypinyin import pinyin, Style

ROOT = Path(__file__).resolve().parents[3]
PREVIEWS = ROOT / "scripts" / "shadowing" / "previews"

VIDEOS = [
    {
        "name": "一个下雨天",
        "id": "QwlhcsAMhT0",
        "input": "yi_ge_xia_yu_tian_generated_zh.json",
        "output": "yi_ge_xia_yu_tian_normalized.json",
        "review": "yi_ge_xia_yu_tian_review.txt",
    },
    {
        "name": "我的新年计划",
        "id": "o6ilprwO6w0",
        "input": "wo_de_xin_nian_ji_hua_generated_zh.json",
        "output": "wo_de_xin_nian_ji_hua_normalized.json",
        "review": "wo_de_xin_nian_ji_hua_review.txt",
    },
]

END_MARKS = "。！？?!"
PUNCTUATION = "，。！？；：、,.!?;:"

# Đây là bản chia câu sơ bộ.
# Các đoạn thiếu dấu câu vẫn cần kiểm tra thủ công.
MAX_CHARS = 38
MAX_SECONDS = 12.0
GAP_SECONDS = 2.5


def clean_text(text):
    text = str(text).strip()
    text = re.sub(r"\s+", "", text)

    replacements = {
        ",": "，",
        ".": "。",
        "?": "？",
        "!": "！",
        ";": "；",
        ":": "：",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def only_hanzi(text):
    return re.sub(
        r"[^\u3400-\u9fff0-9]",
        "",
        text,
    )


def similarity(a, b):
    return SequenceMatcher(
        None,
        only_hanzi(a),
        only_hanzi(b),
    ).ratio()


def make_pinyin(hanzi):
    result = pinyin(
        hanzi,
        style=Style.TONE,
        heteronym=False,
        errors=lambda x: list(x),
    )

    return " ".join(item[0] for item in result)


def remove_duplicate_segments(content):
    """
    Loại các đoạn ASR lặp gần nhau theo timestamp.
    Không loại câu giống nhau ở các thời điểm xa nhau.
    """
    items = []

    for raw in content:
        text = clean_text(raw.get("text", ""))

        if not text:
            continue

        start = float(raw["offset"]) / 1000
        duration = float(raw["duration"]) / 1000

        if start < 0 or duration <= 0:
            continue

        items.append({
            "start": start,
            "end": start + duration,
            "text": text,
        })

    items.sort(key=lambda x: (x["start"], x["end"]))

    cleaned = []
    duplicates = []

    for item in items:
        is_duplicate = False

        for old in reversed(cleaned[-12:]):
            if item["start"] - old["start"] > 1.0:
                break

            close_time = (
                abs(item["start"] - old["start"]) <= 0.25
            )

            similar_text = (
                similarity(item["text"], old["text"])
                >= 0.90
            )

            if close_time and similar_text:
                is_duplicate = True
                duplicates.append(item)
                break

        if not is_duplicate:
            cleaned.append(item)

    return cleaned, duplicates


def split_into_drafts(items):
    """
    Ghép các mảnh ASR theo thứ tự thời gian.
    Ưu tiên dấu kết thúc câu và khoảng ngắt.
    Giới hạn độ dài để dễ kiểm tra.
    """
    drafts = []

    current_text = ""
    current_start = None
    current_end = None
    warnings = []

    def flush(reason):
        nonlocal current_text, current_start, current_end

        text = current_text.strip("，、； ")

        if text:
            if text[-1] not in END_MARKS:
                text += "。"

            drafts.append({
                "start": round(current_start, 2),
                "end": round(current_end, 2),
                "hanzi": text,
                "pinyin": make_pinyin(text),
                "vi": "",
                "_reason": reason,
            })

        current_text = ""
        current_start = None
        current_end = None

    for item in items:
        text = item["text"]

        if current_start is None:
            current_start = item["start"]
            current_end = item["end"]

        elif (
            item["start"] - current_end
            > GAP_SECONDS
        ):
            flush("khoang_ngat")
            current_start = item["start"]
            current_end = item["end"]

        current_text += text
        current_end = max(
            current_end,
            item["end"],
        )

        # Một mảnh có thể chứa dấu câu ở giữa.
        # Chưa tự chia tại đó vì timestamp
        # của từng chữ không đủ chính xác.
        ends_sentence = (
            text[-1] in END_MARKS
        )

        char_count = len(
            only_hanzi(current_text)
        )

        duration = current_end - current_start

        if ends_sentence:
            flush("dau_cau")

        elif (
            char_count >= MAX_CHARS
            or duration >= MAX_SECONDS
        ):
            warnings.append(
                f"Can xem lai doan tai "
                f"{current_start:.2f}s: "
                f"cat theo gioi han do dai"
            )
            flush("gioi_han")

    if current_text:
        flush("cuoi_video")

    return drafts, warnings


def validate_drafts(drafts):
    warnings = []
    previous_start = -1

    for index, item in enumerate(drafts, 1):
        start = item["start"]
        end = item["end"]

        if start < previous_start:
            warnings.append(
                f"Cau {index}: timestamp dao thu tu"
            )

        if end <= start:
            warnings.append(
                f"Cau {index}: thoi gian khong hop le"
            )

        if index > 1:
            previous_end = drafts[index - 2]["end"]

            if start < previous_end:
                warnings.append(
                    f"Cau {index}: chong lan "
                    f"{previous_end - start:.2f}s"
                )

        previous_start = start

    return warnings


def process_video(video):
    input_file = PREVIEWS / video["input"]
    output_file = PREVIEWS / video["output"]
    review_file = PREVIEWS / video["review"]

    if not input_file.exists():
        raise FileNotFoundError(input_file)

    with input_file.open(
        "r", encoding="utf-8-sig"
    ) as f:
        raw = json.load(f)

    content = raw.get("content")

    if not isinstance(content, list) or not content:
        raise ValueError(
            f"Transcript rong: {video['name']}"
        )

    items, duplicates = remove_duplicate_segments(
        content
    )

    drafts, warnings = split_into_drafts(items)

    warnings.extend(
        validate_drafts(drafts)
    )

    # Bản JSON chỉ để xem trước.
    # Chưa phải bản cuối cùng để nhập SQL.
    payload = {
        "module": "shadowing",
        "youtube_id": video["id"],
        "sentences": [
            {
                "start": item["start"],
                "end": item["end"],
                "hanzi": item["hanzi"],
                "pinyin": item["pinyin"],
                "vi": "",
            }
            for item in drafts
        ],
    }

    with output_file.open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(
            payload,
            f,
            ensure_ascii=False,
            indent=2,
        )

    lines = [
        f"VIDEO: {video['name']}",
        f"YOUTUBE ID: {video['id']}",
        "BAN NHAP - CHUA DOI CHIEU AUDIO",
        "",
    ]

    for index, item in enumerate(drafts, 1):
        lines.extend([
            f"CAU {index}",
            f"Time: {item['start']} - {item['end']}",
            f"Hanzi: {item['hanzi']}",
            f"Pinyin: {item['pinyin']}",
            f"Ly do tach: {item['_reason']}",
            "",
        ])

    lines.append("===== CANH BAO =====")

    if not warnings:
        lines.append(
            "Khong phat hien loi timestamp co ban."
        )
    else:
        lines.extend(warnings)

    lines.extend([
        "",
        f"So manh lap nghi ngo: {len(duplicates)}",
        "Can doi chieu cau voi video truoc khi dich.",
        "Chua thay doi SQL Server.",
    ])

    review_file.write_text(
        "\n".join(lines),
        encoding="utf-8-sig",
    )

    print("\n============================")
    print("Video:", video["name"])
    print("So doan goc:", len(content))
    print("So doan sau loc:", len(items))
    print("So cau nhap:", len(drafts))
    print("Canh bao:", len(warnings))
    print("JSON:", output_file)
    print("Review:", review_file)

    print("\n===== 5 CAU DAU =====")

    for index, item in enumerate(drafts[:5], 1):
        print(f"\nCau {index}")
        print(
            "Time:",
            item["start"],
            "-",
            item["end"],
        )
        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])


def main():
    PREVIEWS.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("===== CHUAN HOA HSK1 =====")

    for video in VIDEOS:
        process_video(video)

    print("\n===== HOAN THANH BAN NHAP =====")
    print("Da xu ly ca 2 video.")
    print("Chua dich tieng Viet.")
    print("Chua doi chieu het loi thoai.")
    print("Chua thay doi SQL Server.")
    print("Khong goi Supadata.")


if __name__ == "__main__":
    main()
