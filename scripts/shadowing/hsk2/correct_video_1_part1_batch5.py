
import json
from pathlib import Path

from .correct_video_1_part1 import make_pinyin

ROOT = Path(__file__).resolve().parents[3]
HSK2 = ROOT / "scripts" / "shadowing" / "hsk2"

INPUT = (
    HSK2 / "previews"
    / "video_1_part1_batch4_review.json"
)

OUTPUT = (
    HSK2 / "previews"
    / "video_1_part1_corrected_40.json"
)

# Nội dung đã đối chiếu với ảnh phụ đề YouTube.
# Timestamp vẫn cần kiểm tra lại khi phát video.
CORRECTIONS = {
    31: (
        "哈哈，你爸爸像一个老师。是啊，"
        "他觉得每个故事都有它的意思，有它的道理。",
        "Haha, bố cậu giống một thầy giáo thật đấy. "
        "Đúng vậy, bố tôi cho rằng mỗi câu chuyện "
        "đều có ý nghĩa và bài học riêng."
    ),
    32: (
        "所以我小时候听故事，不只是听，我还要想："
        "这个故事告诉了我什么？那也很好啊。",
        "Vì vậy, hồi nhỏ khi nghe kể chuyện, tôi không "
        "chỉ nghe mà còn phải suy nghĩ xem câu chuyện "
        "muốn nói với mình điều gì. Như thế cũng rất tốt mà."
    ),
    33: (
        "你还记得你爸爸给你讲过什么故事吗？"
        "记得，他给我讲了很多关于动物的故事。",
        "Cậu còn nhớ bố đã kể những câu chuyện gì không? "
        "Có chứ, bố đã kể cho tôi rất nhiều câu chuyện "
        "về động vật."
    ),
    34: (
        "故事里有聪明的动物，也有点儿笨的动物。"
        "有好人，也有坏人。"
        "我奶奶也喜欢讲动物的故事。",
        "Trong chuyện có những con vật thông minh, "
        "cũng có những con hơi ngốc nghếch. Có người tốt, "
        "cũng có người xấu. Bà nội tôi cũng thích kể "
        "chuyện về động vật."
    ),
    35: (
        "我觉得小孩子都喜欢听动物的故事，"
        "因为很简单，也很有意思。"
        "没错，简单的故事，有意思的故事，"
        "最适合在睡觉前听。",
        "Tôi nghĩ trẻ con đều thích nghe chuyện về "
        "động vật vì chúng đơn giản và thú vị. "
        "Đúng vậy, những câu chuyện đơn giản, thú vị "
        "rất thích hợp để nghe trước khi ngủ."
    ),
    36: (
        "它们不会让你的脑子太累。"
        "是的，说到动物故事，我马上就想到了一个。",
        "Chúng không khiến đầu óc cậu quá mệt mỏi. "
        "Đúng vậy, nhắc đến chuyện về động vật, "
        "tôi lập tức nghĩ ra một câu chuyện."
    ),
}

# Điều chỉnh ranh giới 35-36 theo mảnh ASR gốc.
# Các mốc này vẫn là sơ bộ, không phải xác nhận âm thanh.
TIME_ADJUSTMENTS = {
    35: {"end": 237.25},
    36: {"start": 237.47},
}


def main():
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)

    if OUTPUT.exists():
        raise FileExistsError(
            f"Khong ghi de file da co: {OUTPUT}"
        )

    with INPUT.open("r", encoding="utf-8-sig") as f:
        sentences = json.load(f)

    if not isinstance(sentences, list) or len(sentences) != 40:
        raise ValueError("Can dung 40 cau phan 1.")

    for number in range(31, 37):
        item = sentences[number - 1]

        hanzi, vi = CORRECTIONS[number]

        item["hanzi"] = hanzi
        item["pinyin"] = make_pinyin(hanzi)
        item["vi"] = vi

        # Chưa xác nhận timestamp theo âm thanh.
        item["_review_status"] = "can_doi_chieu_audio"
        item["_review_note"] = (
            "Da doi chieu noi dung voi anh phu de; "
            "timestamp can kiem tra lai."
        )

        if number in TIME_ADJUSTMENTS:
            item.update(TIME_ADJUSTMENTS[number])

    # Kiểm tra đủ Hanzi, pinyin, tiếng Việt
    incomplete = []

    for number, item in enumerate(sentences, 1):
        if not all(
            isinstance(item.get(field), str)
            and item[field].strip()
            for field in ("hanzi", "pinyin", "vi")
        ):
            incomplete.append(number)

        if item["end"] <= item["start"]:
            raise ValueError(
                f"Cau {number}: timestamp khong hop le."
            )

    if incomplete:
        raise ValueError(
            f"Nhung cau chua du noi dung: {incomplete}"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(
            sentences,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("===== HSK2 VIDEO 1 - PHAN 1 =====")
    print("Tong cau:", len(sentences))
    print("Da co Hanzi, pinyin, tieng Viet:", len(sentences))
    print("Da xu ly cau 31-36 tu anh phu de.")
    print("Trang thai: BAN NHAP - CAN KIEM TRA AUDIO")
    print("File:", OUTPUT)

    print("\n===== CAU 31-36 =====")
    for number in range(31, 37):
        item = sentences[number - 1]
        print(f"\nCau {number}")
        print("Time:", item["start"], "-", item["end"])
        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])
        print("Viet:", item["vi"])

    print("\nKhong goi Supadata.")
    print("Chua thay doi SQL Server.")
    print("Khong ghi de du lieu HSK1.")


if __name__ == "__main__":
    main()
