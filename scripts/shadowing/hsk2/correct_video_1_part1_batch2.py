
import json
from pathlib import Path

# Tái sử dụng hàm tạo pinyin ở batch trước
from .correct_video_1_part1 import make_pinyin

ROOT = Path(__file__).resolve().parents[3]
HSK2 = ROOT / "scripts" / "shadowing" / "hsk2"

INPUT = (
    HSK2 / "previews"
    / "video_1_part1_corrected.json"
)

OUTPUT = (
    HSK2 / "previews"
    / "video_1_part1_corrected_20.json"
)

CORRECTIONS = {
    11: (
        "原来是这样。睡前故事，这是一个很有意思的话题。"
        "你很喜欢听故事吗？",
        "Ra là vậy. Chuyện kể trước giờ ngủ, đây là một "
        "chủ đề rất thú vị. Cậu rất thích nghe kể chuyện à?"
    ),
    12: (
        "非常喜欢，特别是小时候。",
        "Rất thích, đặc biệt là hồi còn nhỏ."
    ),
    13: (
        "我也是。那我们今天就聊一聊这个吧，聊一聊故事。",
        "Tôi cũng vậy. Thế hôm nay chúng ta nói về "
        "chủ đề này nhé, cùng trò chuyện về những câu chuyện."
    ),
    14: (
        "也许我们的听众朋友们今天晚上也可以听着我们的播客，"
        "安静地睡觉。",
        "Có lẽ tối nay các thính giả của chúng ta "
        "cũng có thể vừa nghe podcast vừa yên tâm "
        "đi vào giấc ngủ."
    ),
    15: (
        "这个主意太好了，我喜欢。",
        "Ý tưởng này hay quá, tôi thích đấy."
    ),
    16: (
        "王宇，你刚才说你小时候特别喜欢听故事，"
        "是你爸爸妈妈给你讲故事吗？",
        "Vương Vũ, vừa rồi cậu nói hồi nhỏ rất thích "
        "nghe kể chuyện. Có phải bố mẹ kể chuyện "
        "cho cậu không?"
    ),
    17: (
        "不是我爸爸妈妈，是我奶奶。你奶奶？",
        "Không phải bố mẹ tôi, mà là bà nội tôi. "
        "Bà nội cậu à?"
    ),
    18: (
        "对，我很小的时候，每天晚上，我奶奶都会坐在"
        "我的床边，给我讲故事。",
        "Đúng vậy. Khi tôi còn rất nhỏ, tối nào bà nội "
        "cũng ngồi bên giường và kể chuyện cho tôi nghe."
    ),
    19: (
        "她的声音特别温柔，特别好听。"
        "你还记得她给你讲了什么故事吗？",
        "Giọng bà rất dịu dàng, nghe rất hay. "
        "Cậu còn nhớ bà đã kể những câu chuyện gì "
        "cho cậu không?"
    ),
    20: (
        "嗯，我不记得所有的故事了，故事太多了，"
        "但是我记得那个感觉。感觉？是。",
        "Ừm, tôi không nhớ hết các câu chuyện nữa, "
        "vì có quá nhiều. Nhưng tôi vẫn nhớ cảm giác ấy. "
        "Cảm giác à? Đúng vậy."
    ),
}


def main():
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)

    if OUTPUT.exists():
        raise FileExistsError(
            f"File da ton tai, khong ghi de: {OUTPUT}"
        )

    with INPUT.open("r", encoding="utf-8-sig") as f:
        sentences = json.load(f)

    if not isinstance(sentences, list) or len(sentences) != 40:
        raise ValueError(
            "File dau vao phai co dung 40 cau."
        )

    for index, item in enumerate(sentences, 1):
        if index not in CORRECTIONS:
            continue

        hanzi, vi = CORRECTIONS[index]

        item["hanzi"] = hanzi
        item["pinyin"] = make_pinyin(hanzi)
        item["vi"] = vi
        item["_review_status"] = "can_doi_chieu_audio"

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(
            sentences,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("===== HSK2 - VIDEO 1 - BATCH 2 =====")
    print("Tong cau phan 1:", len(sentences))
    print("Da chinh so bo: 20")
    print("Chua ra soat: 20")
    print("File:", OUTPUT)
    print("Chua doi chieu audio.")
    print("Khong goi Supadata.")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
