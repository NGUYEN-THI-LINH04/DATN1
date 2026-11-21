
import json
import re
from pathlib import Path
from difflib import SequenceMatcher

from pypinyin import lazy_pinyin, Style


# ==================================================
# CAU HINH VIDEO
# ==================================================

BASE = Path(r"D:\DATN1\scripts\shadowing")

VIDEO_ID = "-hVHRNgDdNE"

INPUT_FILE = BASE / "previews" / "xiaozhang_generated_zh.json"

OUTPUT_FILE = BASE / "previews" / "xiaozhang_review.json"


# ==================================================
# NOI DUNG CAU CHUYEN TIEU TRUONG
# Bien tap tu transcript Supadata
# Can doi chieu voi video truoc khi nhap SQL
# ==================================================

STORY = [
    (
        "小张今年二十八岁。",
        "Năm nay Tiểu Trương 28 tuổi."
    ),
    (
        "他不是北京人，但是住在北京。",
        "Anh ấy không phải người Bắc Kinh, nhưng sống ở Bắc Kinh."
    ),
    (
        "他在北京的一家大公司工作。",
        "Anh ấy làm việc tại một công ty lớn ở Bắc Kinh."
    ),
    (
        "六年前，小张第一次来北京旅游。",
        "Sáu năm trước, Tiểu Trương lần đầu đến Bắc Kinh du lịch."
    ),
    (
        "北京有很多好吃的、好玩的。",
        "Bắc Kinh có nhiều món ngon và nhiều nơi vui chơi."
    ),
    (
        "他第一次来就喜欢上了北京。",
        "Ngay lần đầu đến đây, anh ấy đã thích Bắc Kinh."
    ),
    (
        "回到家，他想去北京找工作。",
        "Sau khi trở về nhà, anh ấy muốn đến Bắc Kinh tìm việc."
    ),
    (
        "他姐姐的同学住在北京。",
        "Bạn học của chị gái anh ấy sống ở Bắc Kinh."
    ),
    (
        "他姓张，在北京的一家大公司工作。",
        "Người đó họ Trương và làm việc tại một công ty lớn ở Bắc Kinh."
    ),
    (
        "他告诉小张，公司需要一个会说英语的人。",
        "Người đó nói với Tiểu Trương rằng công ty cần một người biết nói tiếng Anh."
    ),
    (
        "因为小张的英语很好，所以他可以去那儿工作。",
        "Vì tiếng Anh của Tiểu Trương rất tốt nên anh ấy có thể đến đó làm việc."
    ),
    (
        "一个星期后，小张买了一张飞北京的机票。",
        "Một tuần sau, Tiểu Trương mua một vé máy bay đến Bắc Kinh."
    ),
    (
        "就这样，他开始了北京的生活。",
        "Cứ như vậy, anh ấy bắt đầu cuộc sống ở Bắc Kinh."
    ),
    (
        "他在这儿认识了很多新朋友。",
        "Ở đây, anh ấy quen được nhiều người bạn mới."
    ),
    (
        "每天都过得很开心。",
        "Ngày nào anh ấy cũng sống rất vui vẻ."
    ),
    (
        "北京太大了，而且房租很贵。",
        "Bắc Kinh rất rộng lớn, hơn nữa tiền thuê nhà rất đắt."
    ),
    (
        "他住得离公司很远，每天都要花很长时间上下班。",
        "Anh ấy sống rất xa công ty, mỗi ngày phải mất nhiều thời gian đi làm và về nhà."
    ),
    (
    "小张正在和同事一起找房子。",
    "Tiểu Trương đang cùng đồng nghiệp tìm nhà."
    ),
    (
        "他们希望住得离公司近一些。",
        "Họ hy vọng có thể sống gần công ty hơn một chút."
    ),
    (
        "这样每天早上可以多睡一个小时。",
        "Như vậy, mỗi sáng họ có thể ngủ thêm một tiếng."
    ),
    (
        "他们的新房子不大，离公司很近。",
        "Ngôi nhà mới của họ không lớn nhưng rất gần công ty."
    ),
    (
        "他们每个人都有一个房间。",
        "Mỗi người đều có một phòng riêng."
    ),
    (
        "每人每月付一半房租。",
        "Mỗi người trả một nửa tiền thuê nhà mỗi tháng."
    ),
    (
        "现在他每天早上七点起床，下午六点回家。",
        "Bây giờ mỗi sáng anh ấy thức dậy lúc 7 giờ và về nhà lúc 6 giờ chiều."
    ),
    (
        "因为有了更多的休息时间，他可以看书、踢足球，做很多喜欢的事情。",
        "Vì có nhiều thời gian nghỉ ngơi hơn, anh ấy có thể đọc sách, đá bóng và làm nhiều việc mình thích."
    ),
    (
        "因为他每天都运动，所以他的身体更好了。",
        "Vì ngày nào anh ấy cũng vận động nên sức khỏe đã tốt hơn."
    )
]


# ==================================================
# HAM XU LY
# ==================================================

def normalize(text):
    """Chi giu chu Han de so khop."""
    return "".join(
        re.findall(r"[\u3400-\u9fff]", text)
    )


def make_pinyin(hanzi):
    """Tao pinyin co dau, khong goi AI."""
    return " ".join(
        lazy_pinyin(hanzi, style=Style.TONE)
    )


def read_supadata(path):
    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    content = data.get("content", [])

    if not content:
        raise ValueError("Khong tim thay content trong JSON")

    return sorted(
        content,
        key=lambda x: x["offset"]
    )


def build_source(segments):
    """
    Tao chuoi chu Han va moc thoi gian.
    Chua tu y xoa cac doan trung, vi co the
    lam mat noi dung dung.
    """
    chars = []
    timestamps = []
    ends = []

    for segment in segments:
        text = normalize(segment.get("text", ""))

        if not text:
            continue

        start = segment["offset"] / 1000
        duration = segment["duration"] / 1000
        end = start + duration

        for i, char in enumerate(text):
            chars.append(char)

            # Uoc luong thoi gian tung chu
            position = i / len(text)

            timestamps.append(
                start + duration * position
            )

            ends.append(end)

    return "".join(chars), timestamps, ends


def align_sentences(story, source, timestamps, ends):
    """
    So khop van ban chuan voi Supadata.
    Ket qua thoi gian la uoc luong can kiem tra.
    """
    target = "".join(
        normalize(hanzi) for hanzi, _ in story
    )

    matcher = SequenceMatcher(
        None,
        target,
        source,
        autojunk=False
    )

    mapping = {}

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for i in range(i2 - i1):
                mapping[i1 + i] = j1 + i

    result = []
    cursor = 0
    previous_end = 0.0

    for hanzi, vi in story:
        plain = normalize(hanzi)
        length = len(plain)

        matches = [
            mapping[i]
            for i in range(cursor, cursor + length)
            if i in mapping
        ]

        ratio = len(matches) / length if length else 0

        start = None
        end = None
        problem = []

        if matches:
            first = min(matches)
            last = max(matches)

            start = round(timestamps[first], 2)
            end = round(ends[last], 2)

            if start < previous_end - 0.15:
                problem.append("Thoi gian chong len cau truoc")

            if end <= start:
                problem.append("Thoi gian khong hop le")

            previous_end = max(previous_end, end)

        else:
            problem.append("Khong tim thay vi tri cau")

        if ratio < 0.9:
            problem.append("Noi dung khop thap")

        result.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": make_pinyin(hanzi),
            "vi": vi,
            "match_ratio": round(ratio, 3),
            "needs_review": True,
            "issues": problem
        })

        cursor += length

    return result


# ==================================================
# CHUONG TRINH CHINH
# ==================================================

def main():
    print("=== CHUAN BI DU LIEU SHADOWING ===")
    print("Video:", VIDEO_ID)

    segments = read_supadata(INPUT_FILE)

    source, timestamps, ends = build_source(segments)

    sentences = align_sentences(
        STORY,
        source,
        timestamps,
        ends
    )

    result = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "sentences": sentences
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\nDoan Supadata:", len(segments))
    print("So cau duoc tao:", len(sentences))
    print("File:", OUTPUT_FILE)

    print("\n=== DANH SACH CAU ===")

    for index, item in enumerate(sentences, 1):
        start = item["start"]

        time_text = (
            f"{start:.2f}s"
            if start is not None
            else "CHUA KHOP"
        )

        print(
            f"{index:02d}. "
            f"{time_text} | "
            f"{item['match_ratio']:.0%} | "
            f"{item['hanzi']}"
        )

        if item["issues"]:
            print("    CAN KIEM TRA:", ", ".join(item["issues"]))

    print("\nCHUA CAP NHAT SQL SERVER")
    print("CAN KIEM TRA NOI DUNG VA TIMESTAMP")


if __name__ == "__main__":
    main()
