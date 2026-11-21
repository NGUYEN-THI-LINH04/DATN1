
import json
from pathlib import Path

from .correct_video_1_part1 import make_pinyin

ROOT = Path(__file__).resolve().parents[3]
HSK2 = ROOT / "scripts" / "shadowing" / "hsk2"

INPUT = HSK2 / "previews" / "video_1_part2_repaired_41_56.json"
OUTPUT = HSK2 / "previews" / "video_1_part2_subtitle_verified.json"

# Chỉ cập nhật những mục có ảnh phụ đề xác nhận.
# Khóa là vị trí 1-based trong danh sách đã chia lại.
UPDATES = {
    2: (
        "这个故事，我觉得，在中国，每个小孩子都听过。",
        "Tôi nghĩ rằng ở Trung Quốc, đứa trẻ nào cũng đã từng nghe câu chuyện này."
    ),
    5: (
        "好主意。我们可以一起讲。",
        "Ý hay đấy. Chúng ta có thể cùng kể."
    ),
    7: (
        "我们的故事，开始了。",
        "Câu chuyện của chúng ta bắt đầu."
    ),
    10: (
        "这只兔子，它有一个特点。它跑得非常非常快。",
        "Con thỏ này có một đặc điểm. Nó chạy vô cùng nhanh."
    ),
    11: (
        "对，它是森林里跑得最快的动物。所以，它有点儿骄傲。",
        "Đúng vậy, nó là con vật chạy nhanh nhất khu rừng. Vì thế, nó hơi kiêu ngạo."
    ),
    12: (
        "它常常对别的动物说：“你们看，我跑得多快啊！”",
        "Nó thường nói với các con vật khác: “Các bạn xem, tôi chạy nhanh biết bao!”"
    ),
}


def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Chua co file dau vao: {INPUT}"
        )

    if OUTPUT.exists():
        raise FileExistsError(
            f"Khong ghi de file da co: {OUTPUT}"
        )

    with INPUT.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if not isinstance(data, list) or len(data) != 50:
        raise ValueError(
            "File dau vao phai co 50 muc. "
            "Hay chay repair_video_1_part2_41_56 truoc."
        )

    for number, (hanzi, vi) in UPDATES.items():
        item = data[number - 1]

        item["hanzi"] = hanzi
        item["pinyin"] = make_pinyin(hanzi)
        item["vi"] = vi

        # Ảnh xác nhận chữ Hán, không xác nhận chính xác
        # điểm bắt đầu/kết thúc của từng câu.
        item["_review_status"] = "hanzi_da_doi_chieu_anh"
        item["_review_note"] = (
            "Hanzi da doi chieu voi anh phu de YouTube. "
            "Timestamp van can kiem tra audio."
        )

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("===== HSK2 VIDEO 1 - DOI CHIEU PHU DE =====")
    print("Tong muc:", len(data))
    print("So muc cap nhat:", len(UPDATES))
    print("File:", OUTPUT)

    for number in sorted(UPDATES):
        item = data[number - 1]
        print(f"\nMuc {number}")
        print("Time:", item["start"], "-", item["end"])
        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])
        print("Viet:", item["vi"])

    print("\nKhong goi Supadata.")
    print("Chua thay doi SQL Server.")
    print("Khong thay doi HSK1.")
    print("Khong ghi de du lieu cu.")


if __name__ == "__main__":
    main()
