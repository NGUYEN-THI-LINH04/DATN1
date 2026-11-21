
import json
from pathlib import Path

# Tận dụng hàm tạo pinyin như các batch HSK2 trước
from .correct_video_1_part1 import make_pinyin

ROOT = Path(__file__).resolve().parents[3]
HSK2 = ROOT / "scripts" / "shadowing" / "hsk2"

INPUT = HSK2 / "previews" / "video_1_part2_review.json"

OUTPUT = (
    HSK2 / "previews"
    / "video_1_part2_corrected_50.json"
)

CORRECTIONS = {
    41: (
        "看来我们想的是同一个。",
        "Xem ra chúng ta đang nghĩ đến cùng một câu chuyện."
    ),
    42: (
        "这个故事，我觉得在中国每个小孩子都听过。"
        "那我们现在给我们的……",
        "Tôi nghĩ ở Trung Quốc, đứa trẻ nào cũng từng "
        "nghe câu chuyện này. Vậy bây giờ chúng ta "
        "hãy kể cho…"
    ),
    43: (
        "听众朋友们也讲一遍这个故事，好不好？"
        "用最简单的中文。好主意，我们可以一起讲。"
        "好的，那我开始。",
        "…các thính giả nghe lại câu chuyện này nhé? "
        "Bằng tiếng Trung đơn giản nhất. Ý hay đấy, "
        "chúng ta cùng kể. Được, vậy tôi bắt đầu."
    ),
    44: (
        "我们的故事开始了。很久很久以前，"
        "森林里住着很多动物。有一只兔子，这……",
        "Câu chuyện của chúng ta bắt đầu. Ngày xửa "
        "ngày xưa, trong rừng có rất nhiều loài "
        "động vật. Có một con thỏ, con thỏ này…"
    ),
    45: (
        "只兔子，它有一个特点，它跑得非常非常快。"
        "对，它是森林里跑得最快的动物，所以它有点……",
        "…có một đặc điểm là chạy cực kỳ nhanh. "
        "Đúng vậy, nó là con vật chạy nhanh nhất "
        "khu rừng, vì vậy nó hơi…"
    ),
    46: (
        "骄傲。",
        "Kiêu ngạo."
    ),
    47: (
        "它常常对别的动物说：“你们看，我跑得多快呀！”"
        "森林里还有一只乌龟。这只乌龟呢……",
        "Nó thường khoe với những con vật khác: "
        "“Các bạn xem, tôi chạy nhanh biết bao!” "
        "Trong rừng còn có một con rùa. "
        "Còn con rùa này thì…"
    ),
    48: (
        "它也有一个特点，它走得非常非常慢，非常慢。",
        "Nó cũng có một đặc điểm, đó là đi rất, rất chậm."
    ),
    49: (
        "对，它做什么事情都是……",
        "Đúng vậy, nó làm việc gì cũng đều…"
    ),
    50: (
        "很慢，吃饭很慢，走路也很慢。"
        "有一天，兔子看见了正在走路的乌龟。"
        "兔子笑着对……",
        "…rất chậm. Ăn cũng chậm, đi lại cũng chậm. "
        "Một ngày nọ, thỏ nhìn thấy rùa đang đi "
        "trên đường. Thỏ cười và nói với…"
    ),
}

# Những vị trí cần nghe và xem lại phụ đề
AUDIO_NOTES = {
    42: "Noi tiep sang cau 43, co ASR lap chu.",
    43: "Co nhieu nguoi noi; can xac minh dau cau.",
    44: "Ket thuc giua cum '这只兔子'.",
    45: "Bat dau giua '这只兔子', ket thuc truoc '骄傲'.",
    46: "Noi tiep cau 45.",
    47: "Ket thuc giua y.",
    49: "Noi tiep sang cau 50; ASR sai.",
    50: "Ket thuc giua y, noi sang cau 51.",
}


def main():
    print("===== HSK2 VIDEO 1 - PHAN 2 - BATCH 1 =====")

    if not INPUT.exists():
        raise FileNotFoundError(INPUT)

    if OUTPUT.exists():
        raise FileExistsError(
            f"Da co file, khong ghi de: {OUTPUT}"
        )

    with INPUT.open("r", encoding="utf-8-sig") as f:
        sentences = json.load(f)

    if not isinstance(sentences, list) or len(sentences) != 40:
        raise ValueError(
            "File phan 2 phai co dung 40 cau."
        )

    # Phần 2 gồm câu gốc số 41-80.
    # index 0 tương ứng câu 41.
    for number in range(41, 51):
        item = sentences[number - 41]

        hanzi, vi = CORRECTIONS[number]

        item["hanzi"] = hanzi
        item["pinyin"] = make_pinyin(hanzi)
        item["vi"] = vi

        # Chưa xác minh bằng audio
        item["_review_status"] = "can_doi_chieu_audio"

        if number in AUDIO_NOTES:
            item["_review_note"] = AUDIO_NOTES[number]

    # Giữ câu 51-80 ở trạng thái chưa xử lý
    for number in range(51, 81):
        item = sentences[number - 41]
        item["_review_status"] = "chua_ra_soat"

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
    print("Da chinh so bo: 10")
    print("Chua ra soat: 30")
    print("File:", OUTPUT)

    print("\n===== 3 CAU DAU =====")

    for number in range(41, 44):
        item = sentences[number - 41]
        print(f"\nCau {number}")
        print("Time:", item["start"], "-", item["end"])
        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])
        print("Viet:", item["vi"])

    print("\nCan doi chieu audio: Co")
    print("Khong goi Supadata.")
    print("Chua thay doi SQL Server.")
    print("Khong thay doi HSK1.")


if __name__ == "__main__":
    main()
