
import json
from pathlib import Path
from .correct_video_1_part1 import make_pinyin

HSK2 = Path(__file__).resolve().parent
PREVIEWS = HSK2 / "previews"

INPUT = PREVIEWS / "video_1_part2_subtitle_verified.json"
OUTPUT = PREVIEWS / "video_1_part2_verified_0509.json"

def main():
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)

    if OUTPUT.exists():
        raise FileExistsError(f"Khong ghi de: {OUTPUT}")

    with INPUT.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if len(data) != 50:
        raise ValueError("File dau vao phai co 50 muc.")

    item = data[11]  # Mục 12

    if "你们看，我跑得多快啊！" not in item["hanzi"]:
        raise ValueError(
            "Noi dung muc 12 khong khop ban da kiem tra."
        )

    item["hanzi"] = item["hanzi"].replace(
        "你们看，我跑得多快啊！",
        "你们看我，我跑得多快啊！"
    )
    item["pinyin"] = make_pinyin(item["hanzi"])
    item["vi"] = (
        "Nó thường nói với các con vật khác: "
        "“Các bạn nhìn tôi này, tôi chạy nhanh biết bao!”"
    )
    item["_review_status"] = "hanzi_da_doi_chieu_anh"
    item["_review_note"] = (
        "Da kiem tra anh phu de 05:09. "
        "Timestamp chua xac minh audio."
    )

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("===== SUA PHU DE HSK2 VIDEO 1 =====")
    print("Tong muc:", len(data))
    print("Muc da sua: 12")
    print("Hanzi:", item["hanzi"])
    print("Pinyin:", item["pinyin"])
    print("Viet:", item["vi"])
    print("File:", OUTPUT)

    print("\nKhong goi Supadata.")
    print("Chua thay doi SQL Server.")
    print("Khong thay doi HSK1.")

if __name__ == "__main__":
    main()
