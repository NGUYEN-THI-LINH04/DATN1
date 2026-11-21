
import json
from pathlib import Path

from .correct_video_1_part1 import make_pinyin

ROOT = Path(__file__).resolve().parents[3]
HSK2 = ROOT / "scripts" / "shadowing" / "hsk2"

INPUT = (
    HSK2 / "previews"
    / "video_1_part2_corrected_70.json"
)

OUTPUT = (
    HSK2 / "previews"
    / "video_1_part2_corrected_80.json"
)

CORRECTIONS = {
    71: (
        "乌龟看了看兔子，它什么也没说，"
        "继续一步一步慢慢地向前走。又过了很久。",
        "Rùa nhìn thỏ nhưng không nói gì, tiếp tục "
        "từng bước chậm rãi đi về phía trước. "
        "Một thời gian dài nữa trôi qua."
    ),
    72: (
        "兔子醒了，它睁开眼睛，伸了一个懒腰。"
        "它说：“啊，我睡得真好！现在乌龟到哪里了？”",
        "Thỏ tỉnh dậy, mở mắt và vươn vai. Nó nói: "
        "“A, mình ngủ ngon quá! Bây giờ rùa đến đâu rồi nhỉ?”"
    ),
    73: (
        "它向后看，没有乌龟。它又向前看。",
        "Nó nhìn về phía sau, không thấy rùa đâu. "
        "Sau đó nó lại nhìn về phía trước."
    ),
    74: (
        "它看到了什么？",
        "Nó đã nhìn thấy gì?"
    ),
    75: (
        "它看到乌龟已经快要到终点了。"
        "兔子非常着急，它马上开始跑，跑得很快很快。",
        "Nó nhìn thấy rùa đã gần đến đích. "
        "Thỏ vô cùng sốt ruột, lập tức chạy thật nhanh."
    ),
    76: (
        "比以前更快。",
        "Còn nhanh hơn trước nữa."
    ),
    77: (
        "是的，太晚了。就在兔子快要追上的时候，"
        "乌龟慢慢地走过了终点线。",
        "Đúng vậy, đã quá muộn rồi. "
        "Ngay khi thỏ sắp đuổi kịp, "
        "rùa đã từ từ bước qua vạch đích."
    ),
    78: (
        "所以，比赛结束了。谁是第一名？"
        "是那只走得很慢，但是一直没有放弃的乌龟。",
        "Vậy là cuộc đua kết thúc. "
        "Ai giành vị trí thứ nhất? "
        "Chính là chú rùa tuy đi rất chậm "
        "nhưng chưa từng bỏ cuộc."
    ),
    79: (
        "这个故事讲完了。",
        "Câu chuyện đến đây là kết thúc."
    ),
    80: (
        "虽然我们都知道这个故事，"
        "但是现在再说一遍，还是觉得很有意思。",
        "Mặc dù chúng ta đều biết câu chuyện này, "
        "nhưng kể lại một lần nữa vẫn thấy rất thú vị."
    ),
}

AUDIO_NOTES = {
    71: "Can kiem tra doan chuyen sang cau 72.",
    72: (
        "ASR lap chu, cat giua '到哪里了'. "
        "Da ghep cum tu vao cau 72, "
        "can xac minh timestamp."
    ),
    73: (
        "Da chuyen '了' sang cau 72 cho dung ngu nghia. "
        "Can kiem tra moc bat dau."
    ),
    75: "Can kiem tra thoi diem chuyen y.",
    76: "Noi tiep cau 75.",
    77: "Can kiem tra dau cau va nguoi noi.",
    78: "Co cau hoi va cau tra loi trong cung mot muc.",
}


def main():
    print("===== HSK2 VIDEO 1 - PHAN 2 - BATCH 4 =====")

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
            "File phan 2 phai co dung 40 cau."
        )

    # Xác nhận các câu 41-70 đã có nội dung
    for number in range(41, 71):
        item = sentences[number - 41]

        if not item.get("vi"):
            raise ValueError(
                f"Cau {number} chua co ban dich."
            )

    # Chỉnh câu 71-80
    for number in range(71, 81):
        item = sentences[number - 41]

        hanzi, vi = CORRECTIONS[number]

        item["hanzi"] = hanzi
        item["pinyin"] = make_pinyin(hanzi)
        item["vi"] = vi
        item["_review_status"] = "can_doi_chieu_audio"

        if number in AUDIO_NOTES:
            item["_review_note"] = AUDIO_NOTES[number]

    # Kiểm tra dữ liệu toàn bộ phần 2
    for number, item in enumerate(sentences, 41):
        for field in ("hanzi", "pinyin", "vi"):
            value = item.get(field)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Cau {number} thieu {field}"
                )

        if item["end"] <= item["start"]:
            raise ValueError(
                f"Cau {number} co timestamp khong hop le."
            )

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

    print("Tong cau phan 2:", len(sentences))
    print("Da co Hanzi, pinyin, tieng Viet:", len(sentences))
    print("Trang thai: BAN NHAP - CAN DOI CHIEU AUDIO")
    print("File:", OUTPUT)

    print("\n===== CAU 71-73 =====")

    for number in range(71, 74):
        item = sentences[number - 41]

        print(f"\nCau {number}")
        print("Time:", item["start"], "-", item["end"])
        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])
        print("Viet:", item["vi"])

    print("\nKhong goi Supadata.")
    print("Chua thay doi SQL Server.")
    print("Khong thay doi HSK1.")


if __name__ == "__main__":
    main()
