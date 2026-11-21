
import json
from pathlib import Path

# Sử dụng lại hàm tạo pinyin của batch 1
from .correct_video_1_part1 import make_pinyin

ROOT = Path(__file__).resolve().parents[3]
HSK2 = ROOT / "scripts" / "shadowing" / "hsk2"

INPUT = (
    HSK2 / "previews"
    / "video_1_part1_corrected_20.json"
)

OUTPUT = (
    HSK2 / "previews"
    / "video_1_part1_corrected_30.json"
)

# Chỉnh sơ bộ câu 21-30 theo transcript Supadata.
CORRECTIONS = {
    21: (
        "什么样的感觉？",
        "Cảm giác như thế nào?"
    ),
    22: (
        "安全，很暖和的感觉。外面可能很冷，"
        "但是在房间里听着奶奶的声音，我觉得……",
        "Cảm giác an toàn, rất ấm áp. Bên ngoài có thể "
        "rất lạnh, nhưng khi ở trong phòng nghe giọng bà, "
        "tôi cảm thấy…"
    ),
    23: (
        "非常非常舒服。有时候，故事还没有讲完，"
        "我就已经睡着了。",
        "Vô cùng dễ chịu. Đôi khi bà còn chưa kể hết "
        "câu chuyện thì tôi đã ngủ thiếp đi rồi."
    ),
    24: (
        "我完全明白，那个感觉比故事本身更重要。",
        "Tôi hoàn toàn hiểu, cảm giác ấy còn quan trọng "
        "hơn chính câu chuyện."
    ),
    25: (
        "李明，你小时候有人给你讲故事吗？",
        "Lý Minh, hồi nhỏ có ai kể chuyện cho cậu nghe không?"
    ),
    26: (
        "有，是我爸爸，但是我爸爸和你奶奶不太一样。",
        "Có, là bố tôi. Nhưng bố tôi hơi khác bà nội của cậu."
    ),
    27: (
        "哦，怎么不一样？",
        "Ồ, khác như thế nào?"
    ),
    28: (
        "我爸爸也给我讲故事，但是他每次讲完一个故事"
        "都会问我一个问题。",
        "Bố tôi cũng kể chuyện cho tôi nghe, nhưng mỗi "
        "lần kể xong một câu chuyện, ông đều hỏi tôi một câu."
    ),
    29: (
        "什么问题？",
        "Câu hỏi gì vậy?"
    ),
    30: (
        "他会问：“李明，听完这个故事，你学到了什么？”",
        "Bố sẽ hỏi: “Lý Minh, sau khi nghe câu chuyện "
        "này, con học được điều gì?”"
    ),
}

# Các câu cần đặc biệt nghe lại khi rà soát audio.
AUDIO_NOTES = {
    22: "Cau tiep tuc sang cau 23; can xem lai ranh gioi.",
    23: "Noi tiep cau 22; timestamp chua xac minh.",
    25: "Da bo chu '呢' dau cau; can nghe lai.",
    30: "Da them dau cau cho loi thoai; can nghe lai.",
}


def main():
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)

    # Không ghi đè nếu đã chỉnh file này.
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

    # Đảm bảo batch trước đã được xử lý.
    for index in range(20):
        if not sentences[index].get("vi"):
            raise ValueError(
                f"Cau {index + 1} chua duoc dich o batch truoc."
            )

    for index in range(21, 31):
        item = sentences[index - 1]

        hanzi, vi = CORRECTIONS[index]

        item["hanzi"] = hanzi
        item["pinyin"] = make_pinyin(hanzi)
        item["vi"] = vi

        # Vẫn là bản sơ bộ, chưa nghe đối chiếu.
        item["_review_status"] = "can_doi_chieu_audio"

        if index in AUDIO_NOTES:
            item["_review_note"] = AUDIO_NOTES[index]

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

    print("===== HSK2 - VIDEO 1 - BATCH 3 =====")
    print("Tong cau phan 1:", len(sentences))
    print("Da chinh so bo: 30")
    print("Chua ra soat: 10")
    print("Can doi chieu audio: Co")
    print("File:", OUTPUT)
    print("Khong goi Supadata.")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
