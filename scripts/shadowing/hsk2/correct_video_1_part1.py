
import json
from pathlib import Path
from pypinyin import pinyin, Style

ROOT = Path(__file__).resolve().parents[3]
HSK2 = ROOT / "scripts" / "shadowing" / "hsk2"

INPUT = HSK2 / "previews" / "video_1_part1_review.json"
OUTPUT = HSK2 / "previews" / "video_1_part1_corrected.json"

# Chỉ sửa những câu đã rà soát.
# Các câu 11-40 được giữ nguyên, chưa đánh dấu hoàn tất.
CORRECTIONS = {
    1: (
        "嗯，我有点困了。李明，困了？",
        "Ừm, tôi hơi buồn ngủ rồi. Lý Minh, buồn ngủ à?"
    ),
    2: (
        "王宇，你看，现在时间还早呢，天还没黑。我知道，但是我昨天晚上睡得不太好。是吗？",
        "Vương Vũ, cậu xem, bây giờ vẫn còn sớm, trời còn chưa tối. "
        "Tôi biết, nhưng tối qua tôi ngủ không được ngon lắm. Vậy à?"
    ),
    3: (
        "为什么？",
        "Tại sao vậy?"
    ),
    4: (
        "工作太忙了？",
        "Công việc quá bận à?"
    ),
    5: (
        "也不是，是我昨天晚上睡觉以前想找一个故事来听。",
        "Cũng không phải. Chỉ là tối qua trước khi ngủ, "
        "tôi muốn tìm một câu chuyện để nghe."
    ),
    6: (
        "你知道吗？",
        "Cậu biết không?"
    ),
    7: (
        "就是那种让人很放松的，可以帮助睡觉的故事。",
        "Chính là loại chuyện khiến người ta thư giãn, "
        "có thể giúp dễ ngủ ấy."
    ),
    8: (
        "我明白，你说的是睡前故事。",
        "Tôi hiểu rồi, ý cậu là chuyện kể trước giờ ngủ."
    ),
    9: (
        "对，就是睡前故事，但是我找了很久，都没有找到一个我喜欢的。",
        "Đúng vậy, chính là chuyện kể trước giờ ngủ. "
        "Nhưng tôi tìm rất lâu mà vẫn không tìm được "
        "câu chuyện nào mình thích."
    ),
    10: (
        "所以我睡得很晚。",
        "Vì vậy tôi đã đi ngủ rất muộn."
    ),
}


def make_pinyin(text):
    result = pinyin(
        text,
        style=Style.TONE,
        heteronym=False,
        errors=lambda x: list(x),
    )
    return " ".join(item[0] for item in result)


def main():
    if OUTPUT.exists():
        raise FileExistsError(
            f"File da ton tai, khong ghi de: {OUTPUT}"
        )

    with INPUT.open("r", encoding="utf-8-sig") as f:
        sentences = json.load(f)

    if len(sentences) != 40:
        raise ValueError(
            f"Can 40 cau, nhan duoc {len(sentences)}"
        )

    corrected = []

    for index, original in enumerate(sentences, 1):
        item = original.copy()

        if index in CORRECTIONS:
            hanzi, vi = CORRECTIONS[index]

            item["hanzi"] = hanzi
            item["pinyin"] = make_pinyin(hanzi)
            item["vi"] = vi

            # Đánh dấu chưa đối chiếu audio.
            item["_review_status"] = "can_doi_chieu_audio"
        else:
            item["_review_status"] = "chua_ra_soat"

        corrected.append(item)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(
            corrected,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("===== CHINH SUA HSK2 - PHAN 1 =====")
    print("Tong cau:", len(corrected))
    print("Da chinh so bo:", len(CORRECTIONS))
    print("Chua ra soat:", len(corrected) - len(CORRECTIONS))
    print("File:", OUTPUT)
    print("Chua thay doi SQL Server.")
    print("Khong goi Supadata.")


if __name__ == "__main__":
    main()
