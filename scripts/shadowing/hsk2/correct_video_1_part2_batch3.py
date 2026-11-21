
import json
from pathlib import Path

from .correct_video_1_part1 import make_pinyin

ROOT = Path(__file__).resolve().parents[3]
HSK2 = ROOT / "scripts" / "shadowing" / "hsk2"

INPUT = (
    HSK2 / "previews"
    / "video_1_part2_corrected_60.json"
)

OUTPUT = (
    HSK2 / "previews"
    / "video_1_part2_corrected_70.json"
)

CORRECTIONS = {
    61: (
        "兔子想：“乌龟太慢了，它可能明天早上才能到这里。"
        "天气这么好，我想在这里睡一会儿。”",
        "Thỏ nghĩ: “Rùa chậm quá, có lẽ phải đến sáng mai "
        "nó mới tới đây. Thời tiết đẹp thế này, "
        "mình muốn ngủ một lát ở đây.”"
    ),
    62: (
        "我睡醒了，再跑也来得及。",
        "Khi mình ngủ dậy rồi chạy tiếp thì vẫn còn kịp."
    ),
    63: (
        "于是，兔子就在一棵大树下面开始睡觉了。"
        "它睡得很香。",
        "Thế là thỏ bắt đầu ngủ dưới một gốc cây lớn. "
        "Nó ngủ rất ngon."
    ),
    64: (
        "这个时候，乌龟在哪里呢？",
        "Lúc này, rùa đang ở đâu nhỉ?"
    ),
    65: (
        "乌龟还在路上。它很累，也很热，但是它没有休息。"
        "它心里想：“我一定要坚持。”",
        "Rùa vẫn đang trên đường. Nó rất mệt và nóng, "
        "nhưng không nghỉ ngơi. Trong lòng nó nghĩ: "
        "“Mình nhất định phải kiên trì.”"
    ),
    66: (
        "我不能停。",
        "Mình không thể dừng lại."
    ),
    67: (
        "所以，乌龟一直走，一直走。"
        "它走得很慢，但是它没有停。",
        "Vì vậy, rùa cứ đi mãi, đi mãi. "
        "Nó đi rất chậm nhưng không dừng lại."
    ),
    68: (
        "走到了那棵大树下面，它看到了谁？",
        "Khi đến dưới gốc cây lớn ấy, "
        "nó đã nhìn thấy ai?"
    ),
    69: (
        "它看到了正在睡觉的兔子。",
        "Nó nhìn thấy thỏ đang ngủ."
    ),
    70: (
        "对，兔子睡得正香呢。",
        "Đúng vậy, thỏ đang ngủ rất ngon."
    ),
}

AUDIO_NOTES = {
    61: "Loi thoai noi tiep sang cau 62.",
    62: "Noi tiep suy nghi cua tho o cau 61.",
    65: "Loi thoai noi tiep sang cau 66.",
    66: "Noi tiep suy nghi cua rua o cau 65.",
    68: "Can kiem tra moc bat dau cau voi phu de.",
    70: "Can kiem tra dau cau va nguoi noi.",
}


def main():
    print("===== HSK2 VIDEO 1 - PHAN 2 - BATCH 3 =====")

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

    # Kiểm tra câu 41-60 đã có bản dịch
    for number in range(41, 61):
        item = sentences[number - 41]

        if not item.get("vi"):
            raise ValueError(
                f"Cau {number} chua duoc xu ly."
            )

    # Chỉnh câu 61-70
    for number in range(61, 71):
        item = sentences[number - 41]

        hanzi, vi = CORRECTIONS[number]

        item["hanzi"] = hanzi
        item["pinyin"] = make_pinyin(hanzi)
        item["vi"] = vi
        item["_review_status"] = "can_doi_chieu_audio"

        if number in AUDIO_NOTES:
            item["_review_note"] = AUDIO_NOTES[number]

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
    print("Da chinh so bo: 30")
    print("Chua ra soat: 10")
    print("File:", OUTPUT)

    print("\n===== CAU 61-63 =====")

    for number in range(61, 64):
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
