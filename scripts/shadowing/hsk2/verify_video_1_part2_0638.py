
import json
from pathlib import Path

from .correct_video_1_part1 import make_pinyin

HSK2 = Path(__file__).resolve().parent
PREVIEWS = HSK2 / "previews"

INPUT = PREVIEWS / "video_1_part2_subtitle_verified.json"
OUTPUT = PREVIEWS / "video_1_part2_verified_0638.json"

# Khóa là số thứ tự mục trong file 50 mục.
# Chữ Hán dựa trên phụ đề người dùng cung cấp.
# KHÔNG coi thời điểm phụ đề là timestamp chính xác.

UPDATES = {
    12: (
        "他常常对别的动物说：“你们看我，我跑得多快啊！”",
        "Nó thường nói với các con vật khác: "
        "“Các bạn nhìn tôi này, tôi chạy nhanh biết bao!”",
    ),
    13: (
        "森林里还有一只乌龟。",
        "Trong rừng còn có một con rùa.",
    ),
    14: (
        "这只乌龟呢，他也有一个特点。他走得非常非常慢。",
        "Còn con rùa này cũng có một đặc điểm. "
        "Nó đi rất, rất chậm.",
    ),
    15: (
        "对。他做什么事情都很慢。吃饭很慢，走路也很慢。",
        "Đúng vậy. Nó làm việc gì cũng chậm. "
        "Ăn chậm, đi lại cũng chậm.",
    ),
    16: (
        "有一天，兔子看见了正在走路的乌龟。"
        "兔子笑着对乌龟说：",
        "Một ngày nọ, thỏ nhìn thấy rùa đang đi. "
        "Thỏ cười và nói với rùa:",
    ),
    17: (
        "“乌龟，乌龟，你太慢了！"
        "你看你走路的样子，真的太慢了！”",
        "“Rùa ơi, rùa ơi, cậu chậm quá! "
        "Nhìn dáng đi của cậu kìa, thật sự quá chậm!”",
    ),
    18: (
        "乌龟听了，他不高兴。他对兔子说：",
        "Rùa nghe xong thì không vui. Nó nói với thỏ:",
    ),
    19: (
        "“你很快，我知道。但是，我们比赛，你可能不会赢。”",
        "“Tôi biết cậu rất nhanh. Nhưng nếu chúng ta thi đấu, "
        "cậu có thể sẽ không thắng.”",
    ),
    20: (
        "兔子听了，哈哈大笑。他说：",
        "Thỏ nghe xong liền cười lớn. Nó nói:",
    ),
    21: (
        "“什么？你说我不会赢？太有意思了！”",
        "“Cái gì? Cậu nói tôi sẽ không thắng à? "
        "Thú vị thật!”",
    ),
    22: (
        "“好！我们明天就比赛！"
        "让森林里所有的动物都来看！”",
        "“Được! Ngày mai chúng ta sẽ thi đấu! "
        "Để tất cả các con vật trong rừng đến xem!”",
    ),
    23: (
        "乌龟说：“好。明天见。”",
        "Rùa nói: “Được. Hẹn gặp ngày mai.”",
    ),
    24: (
        "第二天，天气很好。森林里的动物都来了。",
        "Ngày hôm sau, thời tiết rất đẹp. "
        "Các con vật trong rừng đều đến.",
    ),
    25: (
        "小鸟来了，小狗来了，小猫也来了。",
        "Chim đến, chó đến và mèo cũng đến.",
    ),
    26: (
        "他们都想看兔子和乌龟的比赛。",
        "Tất cả đều muốn xem cuộc thi giữa thỏ và rùa.",
    ),
    27: (
        "兔子和乌龟站在起点。"
        "一只小鸟说：“预备，开始！”",
        "Thỏ và rùa đứng ở vạch xuất phát. "
        "Một chú chim nói: “Chuẩn bị, bắt đầu!”",
    ),
}

# Mốc phụ đề để tiện kiểm tra.
# Đây là thời điểm dòng chữ xuất hiện, không phải
# thời gian phát âm chính xác của từng mục.
SUBTITLE_REFERENCES = {
    12: "05:07",
    13: "05:07",
    14: "05:17-05:20",
    15: "05:24-05:26",
    16: "05:30-05:35",
    17: "05:35-05:42",
    18: "05:42-05:50",
    19: "05:50-05:54",
    20: "05:54-06:02",
    21: "06:02-06:07",
    22: "06:08-06:11",
    23: "06:15",
    24: "06:15-06:23",
    25: "06:26",
    26: "06:30",
    27: "06:35-06:38",
}


def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Khong tim thay file dau vao: {INPUT}"
        )

    if OUTPUT.exists():
        raise FileExistsError(
            f"Khong ghi de file da ton tai: {OUTPUT}"
        )

    with INPUT.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if not isinstance(data, list) or len(data) != 50:
        raise ValueError(
            "File dau vao phai co dung 50 muc."
        )

    # Chỉ sửa 16 mục đã có phụ đề.
    for number, (hanzi, vi) in UPDATES.items():
        item = data[number - 1]

        item["hanzi"] = hanzi
        item["pinyin"] = make_pinyin(hanzi)
        item["vi"] = vi

        item["_review_status"] = "hanzi_da_doi_chieu_phu_de"
        item["_subtitle_reference"] = (
            SUBTITLE_REFERENCES[number]
        )
        item["_review_note"] = (
            "Noi dung da doi chieu phu de nguoi dung cung cap. "
            "Giu nguyen timestamp nhap, "
            "chua xac minh moc audio."
        )

    # Kiểm tra dữ liệu trước khi lưu.
    for index, item in enumerate(data, 1):
        for field in ("hanzi", "pinyin", "vi"):
            if not isinstance(item.get(field), str):
                raise ValueError(
                    f"Muc {index} thieu {field}"
                )

            if not item[field].strip():
                raise ValueError(
                    f"Muc {index} rong {field}"
                )

        if float(item["end"]) <= float(item["start"]):
            raise ValueError(
                f"Muc {index} co timestamp sai."
            )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("===== HSK2 VIDEO 1 - DOI CHIEU DEN 06:38 =====")
    print("Tong muc file:", len(data))
    print("Muc cap nhat:", len(UPDATES))
    print("File:", OUTPUT)

    print("\n===== CAC MUC DA CAP NHAT =====")

    for number in sorted(UPDATES):
        item = data[number - 1]

        print(f"\nMuc {number}")
        print(
            "Phu de:",
            item["_subtitle_reference"]
        )
        print(
            "Time nhap:",
            item["start"],
            "-",
            item["end"]
        )
        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])
        print("Viet:", item["vi"])

    print("\nTrang thai: CAN DOI CHIEU TIMESTAMP AUDIO")
    print("Khong goi Supadata.")
    print("Chua thay doi SQL Server.")
    print("Khong thay doi HSK1.")
    print("Khong ghi de file cu.")


if __name__ == "__main__":
    main()
