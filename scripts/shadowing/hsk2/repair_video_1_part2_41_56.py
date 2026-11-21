
import json
from pathlib import Path

from .correct_video_1_part1 import make_pinyin

ROOT = Path(__file__).resolve().parents[3]
HSK2 = ROOT / "scripts" / "shadowing" / "hsk2"

INPUT = HSK2 / "previews" / "video_1_part2_corrected_80.json"

OUTPUT = HSK2 / "previews" / "video_1_part2_repaired_41_56.json"

# Mốc thời gian lấy từ các mảnh Supadata đã cache.
# Đây là mốc DỰ KIẾN, chưa xác minh trực tiếp bằng audio.
#
# Mỗi mục mới có một ý hoàn chỉnh, không cố giữ
# ranh giới của 16 câu nháp ban đầu.

REPAIRED = [
    (
        262.08, 265.06,
        "看来我们想的是同一个。",
        "Xem ra chúng ta đang nghĩ đến cùng một câu chuyện."
    ),
    (
        264.46, 270.16,
        "这个故事，我觉得在中国每个小孩子都听过。",
        "Tôi nghĩ ở Trung Quốc, đứa trẻ nào cũng từng nghe câu chuyện này."
    ),
    (
        268.90, 276.31,
        "那我们现在给我们的听众朋友们也讲一遍这个故事，好不好？",
        "Vậy bây giờ chúng ta kể lại câu chuyện này cho các thính giả nghe nhé?"
    ),
    (
        275.37, 278.91,
        "用最简单的中文。",
        "Bằng tiếng Trung đơn giản nhất."
    ),
    (
        278.47, 281.61,
        "好主意，我们可以一起讲。",
        "Ý hay đấy, chúng ta có thể cùng kể."
    ),
    (
        280.71, 283.07,
        "好的，那我开始。",
        "Được, vậy tôi bắt đầu nhé."
    ),
    (
        283.09, 285.87,
        "我们的故事开始了。",
        "Câu chuyện của chúng ta bắt đầu."
    ),
    (
        286.65, 292.97,
        "很久很久以前，森林里住着很多动物。",
        "Ngày xửa ngày xưa, trong rừng có rất nhiều loài động vật."
    ),
    (
        292.97, 295.25,
        "有一只兔子。",
        "Có một con thỏ."
    ),
    (
        295.07, 300.76,
        "这只兔子，它有一个特点，它跑得非常非常快。",
        "Con thỏ này có một đặc điểm là chạy vô cùng nhanh."
    ),
    (
        299.96, 307.74,
        "对，它是森林里跑得最快的动物，所以它有点骄傲。",
        "Đúng vậy, nó là con vật chạy nhanh nhất khu rừng nên hơi kiêu ngạo."
    ),
    (
        307.30, 314.86,
        "它常常对别的动物说：“你们看，我跑得多快呀！”",
        "Nó thường nói với các con vật khác: “Các bạn xem, tôi chạy nhanh biết bao!”"
    ),
    (
        314.62, 319.46,
        "森林里还有一只乌龟。这只乌龟呢，",
        "Trong rừng còn có một con rùa. Còn con rùa này thì..."
    ),
    (
        318.84, 324.68,
        "它也有一个特点，它走得非常非常慢。",
        "Nó cũng có một đặc điểm là đi rất, rất chậm."
    ),
    (
        323.64, 331.03,
        "对，它做什么事情都很慢，吃饭很慢，走路也很慢。",
        "Đúng vậy, nó làm việc gì cũng chậm, ăn chậm và đi lại cũng chậm."
    ),
    (
        330.77, 338.67,
        "有一天，兔子看见了正在走路的乌龟。兔子笑着对乌龟说：",
        "Một ngày nọ, thỏ nhìn thấy rùa đang đi. Thỏ cười và nói với rùa:"
    ),
    (
        337.69, 347.97,
        "“乌龟，乌龟，你太慢了！你看你走路的样子，真的太慢了！”",
        "“Rùa ơi, rùa ơi, cậu chậm quá! Nhìn dáng đi của cậu kìa, thật sự quá chậm!”"
    ),
    (
        347.31, 352.72,
        "乌龟听了，它不高兴。它对兔子说：",
        "Rùa nghe xong thì không vui. Nó nói với thỏ:"
    ),
    (
        351.67, 359.94,
        "“你很快，我知道，但是我们比赛，你可能不会赢。”",
        "“Tôi biết cậu chạy rất nhanh, nhưng nếu chúng ta thi đấu, chưa chắc cậu đã thắng.”"
    ),
    (
        359.24, 364.38,
        "兔子听了，哈哈大笑。它说：",
        "Thỏ nghe xong thì cười lớn. Nó nói:"
    ),
    (
        363.62, 369.28,
        "“什么？你说我不会赢？太有意思了！”",
        "“Cái gì? Cậu nói tôi sẽ không thắng à? Thú vị thật!”"
    ),
    (
        369.42, 375.92,
        "“好，我们明天就比赛，让森林里所有的动物都来看。”",
        "“Được, ngày mai chúng ta sẽ thi đấu, để tất cả các con vật trong rừng đến xem.”"
    ),
    (
        375.00, 380.08,
        "乌龟说：“好，明天见。”",
        "Rùa nói: “Được, hẹn gặp ngày mai.”"
    ),
    (
        379.81, 386.87,
        "第二天天气很好，森林里的动物都来了。",
        "Ngày hôm sau thời tiết rất đẹp, các con vật trong rừng đều đến."
    ),
    (
        386.51, 391.63,
        "小鸟来了，小狗来了，小猫也来了。",
        "Chim, chó và mèo cũng đến."
    ),
    (
        391.17, 395.99,
        "它们都想看兔子和乌龟的比赛。",
        "Tất cả đều muốn xem cuộc thi giữa thỏ và rùa."
    ),
]


def main():
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)

    if OUTPUT.exists():
        raise FileExistsError(
            f"File da ton tai, khong ghi de: {OUTPUT}"
        )

    with INPUT.open("r", encoding="utf-8-sig") as f:
        original = json.load(f)

    if not isinstance(original, list) or len(original) != 40:
        raise ValueError("File phan 2 phai co 40 cau nhap.")

    # Giữ lại các câu 57-80, không sửa nội dung.
    remaining = [dict(item) for item in original[16:]]

    repaired = []

    for index, (start, end, hanzi, vi) in enumerate(REPAIRED, 1):
        if end <= start:
            raise ValueError(f"Moc thoi gian sai: {index}")

        repaired.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": make_pinyin(hanzi),
            "vi": vi,
            "_review_status": "can_doi_chieu_audio",
            "_review_note": (
                "Chia lai tu transcript Supadata goc. "
                "Timestamp du kien, chua xac minh audio."
            ),
            "_source_draft_range": "41-56"
        })

    result = repaired + remaining

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("===== HSK2 VIDEO 1 - SUA CAU 41-56 =====")
    print("So cau nhap cu:", 16)
    print("So muc sau khi chia lai:", len(repaired))
    print("So muc 57-80 giu nguyen:", len(remaining))
    print("Tong muc file moi:", len(result))
    print("Trang thai: CAN DOI CHIEU AUDIO")
    print("File:", OUTPUT)

    print("\n===== 5 MUC DAU =====")

    for index, item in enumerate(repaired[:5], 1):
        print(f"\nMuc {index}")
        print("Time:", item["start"], "-", item["end"])
        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])
        print("Viet:", item["vi"])

    print("\nKhong goi Supadata.")
    print("Chua thay doi SQL Server.")
    print("Khong thay doi HSK1.")
    print("Khong ghi de file goc.")


if __name__ == "__main__":
    main()
