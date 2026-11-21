
import argparse
import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

from pypinyin import lazy_pinyin, Style


ROOT = Path(__file__).resolve().parents[2]
PREVIEWS = ROOT / "scripts" / "shadowing" / "previews"

DEFAULT_INPUT = PREVIEWS / "jian_dan_sheng_huo_native_zh.json"
DEFAULT_OUTPUT = PREVIEWS / "jian_dan_sheng_huo_normalized.json"

VIDEO_ID = "6YGJswSorYw"

# Bản câu đã biên tập từ transcript Supadata.
# Đây là nội dung để căn chỉnh, không phải phụ đề lấy từ website khác.
# Có thể chỉnh câu ở đây sau khi nghe lại video.
SENTENCES = [
    "大家好，今天我想和大家说说我一天的生活。",
    "我是一个在越南工作的办公室职员，今年30岁。",
    "我的生活很普通，但每天都有开心和难过的事情。",
    "早上六点，我的闹钟响了，我起来了。",
    "外面阳光很好，天气不冷也不热。",
    "我吃了简单的早餐，有面包和牛奶。",
    "吃完，我换好衣服，骑摩托车去公司。",
    "路上有很多车和人，交通很忙。",
    "骑车的时候要小心，看红绿灯和路人。",
    "我喜欢看街上的人们，他们都很努力工作。",
    "到了公司，很多同事已经开始工作。",
    "办公室里有电脑和文件。",
    "今天我有一个重要的会议，要给大家介绍我的工作计划。",
    "我有点紧张，但是同事们支持我，让我感觉好一点。",
    "领导听了我的报告，说你做得很好。",
    "我听了很高兴。",
    "工作中也有问题。",
    "下午的时候，电脑坏了，我打不开文件。",
    "我很着急，找了技术人员帮忙。",
    "最后我修好了电脑，完成了工作。",
    "虽然累，但是我很开心自己解决了问题。",
    "中午，我和同事去吃饭。",
    "我们吃了越南的牛肉粉和春卷。",
    "大家聊天，我告诉他们我和女朋友刚开始交往。",
    "她很温柔，我们喜欢一起喝咖啡和聊天。",
    "同事们笑着说，祝你们幸福。",
    "我也笑了。",
    "下午快下班时，女朋友发信息，今天想见你。",
    "我很想见她，但工作还没做完。",
    "只能说，等我下班，我去找你。",
    "她回了个笑脸，我心里很暖。",
    "下班后，我骑车去见她。",
    "在楼下等我。",
    "我们一起去吃晚饭，有很多好吃的越南菜。",
    "她问我，你今天累吗？",
    "我说，有点累，但是见到你就开心。",
    "她笑着说，我们一起努力好吗？",
    "我点头。",
    "晚上回家，我准备明天的工作。",
    "虽然累，但我很开心。",
    "生活有快乐，也有困难。",
    "有爱的人和朋友支持，我觉得很幸福。",
    "我希望以后和女朋友一起过更好的生活。",
    "也希望工作越来越好。",
    "有时候，我也会想起小时候的生活。",
    "那时候家里不富裕。",
    "父母每天努力工作，给我很好的教育。",
    "我很感谢他们。",
    "所以我现在也很努力工作，不想让他们失望。",
    "工作虽然有压力，但我知道这是为了更好的未来。",
    "周末的时候，我喜欢和女朋友去公园散步，或者看电影。",
    "我们也会一起做饭。",
    "虽然我厨艺不太好，但她总是鼓励我。",
    "这些小事让我觉得生活很美好。",
    "也让我有力量面对每天的挑战。",
    "谢谢大家听我的故事。",
    "希望你们每天都开心，生活越来越好。",
]


def normalize_text(text):
    """Bỏ khoảng trắng và dấu câu để so khớp nội dung."""
    text = unicodedata.normalize("NFKC", str(text))
    return re.sub(
        r"[\s，。！？、；：,.!?;:“”\"'（）()\[\]…]+",
        "",
        text,
    )


def get_pinyin(text):
    return " ".join(
        lazy_pinyin(text, style=Style.TONE, errors="default")
    )


def prepare_segments(content):
    """
    Sắp xếp và loại các đoạn trùng rõ ràng.

    Không dùng duration làm ranh giới câu vì nhiều
    đoạn Supadata có duration mặc định 1500 ms.
    """
    rows = []

    for item in content:
        text = normalize_text(item.get("text", ""))
        offset = int(item.get("offset", 0))
        duration = int(item.get("duration", 0))

        if not text or offset < 0:
            continue

        rows.append({
            "text": text,
            "start_ms": offset,
            "end_ms": offset + max(duration, 0),
        })

    rows.sort(key=lambda x: x["start_ms"])

    result = []

    for row in rows:
        # Loại đoạn trùng nguyên văn, gần cùng thời điểm.
        duplicate = any(
            old["text"] == row["text"]
            and abs(old["start_ms"] - row["start_ms"]) <= 100
            for old in result[-5:]
        )

        if not duplicate:
            result.append(row)

    return result


def build_character_timeline(segments):
    """
    Mỗi ký tự được gắn mốc thời gian ước lượng
    từ offset của đoạn chứa ký tự.

    Đây không phải timestamp chính xác từng ký tự.
    """
    timeline = []

    for i, seg in enumerate(segments):
        start = seg["start_ms"]

        if i + 1 < len(segments):
            next_start = segments[i + 1]["start_ms"]
            end = max(start + 1, next_start)
        else:
            end = max(start + 1, seg["end_ms"])

        chars = list(seg["text"])
        count = len(chars)

        if not count:
            continue

        for j, char in enumerate(chars):
            char_start = start + (end - start) * j / count
            char_end = start + (end - start) * (j + 1) / count

            timeline.append({
                "char": char,
                "start_ms": char_start,
                "end_ms": char_end,
            })

    return timeline


def align_sentences(sentences, timeline):
    """
    Căn chỉnh bản câu biên tập với chuỗi ký tự Supadata.

    SequenceMatcher giúp tìm các vùng tương ứng.
    Những câu có tỷ lệ khớp thấp sẽ bị cảnh báo.
    """
    source = "".join(x["char"] for x in timeline)

    target_parts = [normalize_text(s) for s in sentences]
    target = "".join(target_parts)

    matcher = SequenceMatcher(
        None,
        target,
        source,
        autojunk=False,
    )

    positions = {}

    for block in matcher.get_matching_blocks():
        for j in range(block.size):
            positions[block.a + j] = block.b + j

    result = []
    warnings = []
    cursor = 0

    for index, (sentence, plain) in enumerate(
        zip(sentences, target_parts), 1
    ):
        start_index = cursor
        end_index = cursor + len(plain)
        cursor = end_index

        matched = [
            positions[p]
            for p in range(start_index, end_index)
            if p in positions
        ]

        ratio = len(matched) / max(1, len(plain))

        if not matched:
            warnings.append(
                f"Cau {index}: khong tim thay noi dung tuong ung"
            )
            continue

        first = min(matched)
        last = max(matched)

        start = timeline[first]["start_ms"] / 1000
        end = timeline[last]["end_ms"] / 1000

        result.append({
            "start": round(start, 2),
            "end": round(end, 2),
            "hanzi": sentence,
            "pinyin": get_pinyin(sentence),
            "vi": "",
            "_match_ratio": round(ratio, 3),
        })

        if ratio < 0.85:
            warnings.append(
                f"Cau {index}: khop thap ({ratio:.1%})"
            )

    return result, warnings


def fix_time_boundaries(items):
    """
    Không để các câu chồng lấn.

    Không tự kéo dài câu qua các khoảng im lặng.
    """
    for i, item in enumerate(items):
        if i + 1 < len(items):
            next_start = items[i + 1]["start"]

            if item["end"] > next_start:
                item["end"] = next_start

        if item["end"] <= item["start"]:
            item["end"] = round(item["start"] + 0.1, 2)

    return items


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )
    parser.add_argument(
        "--youtube-id",
        default=VIDEO_ID,
    )

    args = parser.parse_args()

    data = json.loads(
        args.input.read_text(encoding="utf-8-sig")
    )

    if not str(data.get("lang", "")).startswith("zh"):
        raise ValueError(
            "Transcript dau vao khong phai tieng Trung"
        )

    content = data.get("content", [])

    if not content:
        raise ValueError("Transcript khong co content")

    segments = prepare_segments(content)
    timeline = build_character_timeline(segments)

    items, warnings = align_sentences(
        SENTENCES,
        timeline,
    )

    items = fix_time_boundaries(items)

    # Các chỉ số kiểm tra chỉ in ra màn hình,
    # không lưu trong JSON dành cho ứng dụng.
    match_ratios = [
        x.pop("_match_ratio") for x in items
    ]

    result = {
        "module": "shadowing",
        "youtube_id": args.youtube_id,
        "sentences": items,
    }

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.output.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("===== CHUAN HOA SHADOWING =====")
    print("Video:", args.youtube_id)
    print("Doan Supadata:", len(content))
    print("Doan sau loc:", len(segments))
    print("So cau xuat:", len(items))
    print("Canh bao:", len(warnings))

    if match_ratios:
        print(
            "Do khop trung binh:",
            f"{sum(match_ratios) / len(match_ratios):.1%}"
        )

    print("File:", args.output)

    print("\n===== 5 CAU DAU =====")

    for i, item in enumerate(items[:5], 1):
        print(f"\nCau {i}")
        print("Time:", item["start"], "-", item["end"])
        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])

    if warnings:
        print("\n===== CANH BAO =====")
        for warning in warnings:
            print("-", warning)

    print("\nChua dich tieng Viet.")
    print("Chua thay doi SQL Server.")
    print("Can kiem tra lai noi dung va timestamp voi video.")


if __name__ == "__main__":
    main()
