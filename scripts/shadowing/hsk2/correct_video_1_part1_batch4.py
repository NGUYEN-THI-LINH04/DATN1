
import json
from pathlib import Path

from .correct_video_1_part1 import make_pinyin

ROOT = Path(__file__).resolve().parents[3]
HSK2 = ROOT / "scripts" / "shadowing" / "hsk2"

INPUT = (
    HSK2 / "previews"
    / "video_1_part1_corrected_30.json"
)

OUTPUT = (
    HSK2 / "previews"
    / "video_1_part1_batch4_review.json"
)

AUDIO_REVIEW = (
    HSK2 / "previews"
    / "video_1_part1_audio_check.txt"
)

# Những câu có thể chỉnh sơ bộ từ transcript hiện tại
CORRECTIONS = {
    37: (
        "一个非常非常有名的故事。",
        "Một câu chuyện vô cùng nổi tiếng."
    ),
    38: (
        "哦，我们想的是同一个吗？",
        "Ồ, có phải chúng ta đang nghĩ đến cùng một câu chuyện không?"
    ),
    39: (
        "这个故事里是不是有一个跑得很快的动物，"
        "还有一个跑得很慢的动物？",
        "Có phải trong câu chuyện này có một con vật chạy rất nhanh "
        "và một con vật khác chạy rất chậm không?"
    ),
    40: (
        "对，就是那个，龟兔赛跑。",
        "Đúng rồi, chính là câu chuyện Rùa và Thỏ chạy đua."
    ),
}

# Giữ nguyên câu 31-36 cho đến khi nghe lại.
PENDING = {
    31: "Lap chu; cau cuoi noi sang cau 32.",
    32: "Bat dau bang '道理'; ket thuc giua '记得'.",
    33: "Bat dau giua '记得'; ket thuc giua '聪明'.",
    34: "Bat dau giua '聪明'; ket thuc giua '故事'.",
    35: "Bat dau bang '事'; ket thuc giua y.",
    36: "Noi tiep cau 35; ket thuc giua y.",
}


def main():
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)

    if OUTPUT.exists() or AUDIO_REVIEW.exists():
        raise FileExistsError(
            "Da co file batch 4. Khong tu dong ghi de."
        )

    with INPUT.open("r", encoding="utf-8-sig") as f:
        sentences = json.load(f)

    if not isinstance(sentences, list) or len(sentences) != 40:
        raise ValueError("File dau vao phai co dung 40 cau.")

    for index in range(1, 31):
        if not sentences[index - 1].get("vi"):
            raise ValueError(
                f"Cau {index} chua duoc xu ly o batch truoc."
            )

    for number, (hanzi, vi) in CORRECTIONS.items():
        item = sentences[number - 1]
        item["hanzi"] = hanzi
        item["pinyin"] = make_pinyin(hanzi)
        item["vi"] = vi
        item["_review_status"] = "can_doi_chieu_audio"

    lines = [
        "HSK2 VIDEO 1 - CAN NGHE LAI CAU 31-36",
        "YouTube: https://www.youtube.com/watch?v=nxAfRmACtZs",
        "",
        "Day la transcript goc, KHONG phai loi thoai da xac minh.",
        "",
    ]

    for number, note in PENDING.items():
        item = sentences[number - 1]

        item["_review_status"] = "loi_asr_can_nghe_lai"
        item["_review_note"] = note

        lines.extend([
            f"CAU {number}",
            f"Time: {item['start']} - {item['end']}",
            f"Transcript: {item['hanzi']}",
            f"Loi: {note}",
            "Noi dung nghe lai:",
            "",
        ])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(
            sentences,
            f,
            ensure_ascii=False,
            indent=2
        )

    AUDIO_REVIEW.write_text(
        "\n".join(lines),
        encoding="utf-8-sig"
    )

    print("===== HSK2 - VIDEO 1 - BATCH 4 =====")
    print("Tong cau phan 1:", len(sentences))
    print("Da chinh so bo:", 34)
    print("Can nghe lai:", len(PENDING))
    print("JSON:", OUTPUT)
    print("Review:", AUDIO_REVIEW)
    print("Khong goi Supadata.")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
