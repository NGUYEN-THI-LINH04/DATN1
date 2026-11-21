
import json
from pathlib import Path

from .correct_video_1_part1 import make_pinyin

ROOT = Path(__file__).resolve().parents[3]
HSK2 = ROOT / "scripts" / "shadowing" / "hsk2"

INPUT = (
    HSK2 / "previews"
    / "video_1_part2_corrected_50.json"
)

OUTPUT = (
    HSK2 / "previews"
    / "video_1_part2_corrected_60.json"
)

CORRECTIONS = {
    51: (
        "乌龟，乌龟，你太慢了！你看你走路的样子，"
        "真的太慢了！乌龟听了……",
        "Rùa ơi, cậu chậm quá! Nhìn dáng đi của cậu kìa, "
        "thật sự quá chậm! Rùa nghe xong…"
    ),
    52: (
        "它不高兴。它对兔子说：“你很快，我知道，"
        "但是我们比赛，你可能不会赢。”兔子……",
        "Nó không vui. Nó nói với thỏ: "
        "“Tôi biết cậu chạy rất nhanh, nhưng nếu chúng ta "
        "thi đấu, chưa chắc cậu đã thắng.” Thỏ…"
    ),
    53: (
        "听了，哈哈大笑。它说：“什么？你说我不会赢？"
        "太有意思了！好，我们明天就……”",
        "…nghe xong liền cười lớn: “Cái gì? "
        "Cậu nói tôi không thắng được à? Thú vị thật! "
        "Được, ngày mai chúng ta sẽ…”"
    ),
    54: (
        "比赛，让森林里所有的动物都来看。"
        "乌龟说：“好，明天见。”",
        "…thi chạy, để tất cả động vật trong rừng đến xem. "
        "Rùa nói: “Được, hẹn gặp ngày mai.”"
    ),
    55: (
        "第二天天气很好，森林里的动物都来了。"
        "小鸟来了，小狗来了，小猫也来了，它们都……",
        "Ngày hôm sau thời tiết rất đẹp. "
        "Các con vật trong rừng đều đến. "
        "Chim, chó và mèo cũng đến. Tất cả đều…"
    ),
    56: (
        "想看兔子和乌龟的比赛。",
        "…muốn xem cuộc thi giữa thỏ và rùa."
    ),
    57: (
        "兔子和乌龟站在起点。"
        "一只小鸟说：“预备，开始！”",
        "Thỏ và rùa đứng ở vạch xuất phát. "
        "Một chú chim nói: “Chuẩn bị, bắt đầu!”"
    ),
    58: (
        "兔子像风一样跑了出去，非常快，"
        "一转眼就看不见了。乌龟呢？"
        "它也在努力地跑。",
        "Thỏ phóng đi nhanh như gió, chỉ chớp mắt "
        "đã không thấy đâu. Còn rùa thì sao? "
        "Nó cũng đang cố gắng chạy."
    ),
    59: (
        "但是我们知道，它跑得很慢，"
        "它一步一步慢慢地向前走。",
        "Nhưng chúng ta biết rùa chạy rất chậm. "
        "Nó từng bước, từng bước tiến về phía trước."
    ),
    60: (
        "兔子跑了很远，它回头看，看不到乌龟，"
        "一点儿也看不到。",
        "Thỏ đã chạy rất xa. Nó quay đầu nhìn lại "
        "nhưng không thấy rùa, hoàn toàn không thấy đâu cả."
    ),
}

AUDIO_NOTES = {
    51: "Noi tiep cau 50, ASR nhan nham nguoi noi.",
    52: "ASR lap chu va cuoi cau noi sang cau 53.",
    53: "Noi tiep cau 52 va 54.",
    54: "Bat dau giua cau tu cau 53.",
    55: "Noi tiep sang cau 56.",
    56: "Noi tiep cau 55.",
    57: "Can kiem tra dau cau va loi thoai.",
    58: "ASR lap chu; can doi chieu phu de.",
    60: "ASR lap hoac nhan sai '一点也'.",
}


def main():
    print("===== HSK2 VIDEO 1 - PHAN 2 - BATCH 2 =====")

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

    # Kiểm tra batch trước đã có dữ liệu.
    for number in range(41, 51):
        item = sentences[number - 41]

        if not item.get("vi"):
            raise ValueError(
                f"Cau {number} chua duoc xu ly."
            )

    # Chỉnh câu 51-60.
    for number in range(51, 61):
        item = sentences[number - 41]

        hanzi, vi = CORRECTIONS[number]

        item["hanzi"] = hanzi
        item["pinyin"] = make_pinyin(hanzi)
        item["vi"] = vi
        item["_review_status"] = "can_doi_chieu_audio"

        if number in AUDIO_NOTES:
            item["_review_note"] = AUDIO_NOTES[number]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(
            sentences,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("Tong cau phan 2:", len(sentences))
    print("Da chinh so bo: 20")
    print("Chua ra soat: 20")
    print("File:", OUTPUT)

    print("\n===== CAU 51-53 =====")

    for number in range(51, 54):
        item = sentences[number - 41]

        print(f"\nCau {number}")
        print("Time:", item["start"], "-", item["end"])
        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])
        print("Viet:", item["vi"])

    print("\nTrang thai: CAN DOI CHIEU AUDIO")
    print("Khong goi Supadata.")
    print("Chua thay doi SQL Server.")
    print("Khong thay doi HSK1.")


if __name__ == "__main__":
    main()
