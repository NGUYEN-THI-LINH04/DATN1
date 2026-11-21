
import json
from pathlib import Path

# Tái sử dụng chính các hàm chuẩn hóa của HSK1
from scripts.shadowing.normalize_hsk1_remaining import (
    remove_duplicate_segments,
    split_into_drafts,
    validate_drafts,
)

ROOT = Path(__file__).resolve().parents[3]

HSK2 = ROOT / "scripts" / "shadowing" / "hsk2"

INPUT = HSK2 / "data" / "raw" / "video_1_native_zh.json"

OUTPUT = (
    HSK2 / "data" / "processed"
    / "video_1_normalized.json"
)

REVIEW = (
    HSK2 / "previews"
    / "video_1_review.txt"
)

VIDEO_ID = "nxAfRmACtZs"
VIDEO_NAME = "用中文讲故事"


def main():
    print("===== CHUAN HOA HSK2 - VIDEO 1 =====")

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Khong tim thay transcript: {INPUT}"
        )

    # Không ghi đè bản đã chỉnh sửa thủ công.
    if OUTPUT.exists() or REVIEW.exists():
        raise FileExistsError(
            "Da co file normalized hoac review. "
            "Khong tu dong ghi de du lieu cu."
        )

    # 1. Đọc transcript đã cache từ Supadata
    with INPUT.open("r", encoding="utf-8-sig") as f:
        raw = json.load(f)

    content = raw.get("content")

    if not isinstance(content, list) or not content:
        raise ValueError("Transcript rong hoac khong hop le")

    print("Video:", VIDEO_NAME)
    print("YouTube ID:", VIDEO_ID)
    print("So doan goc:", len(content))

    # 2. Loại mảnh trùng bằng hàm HSK1
    items, duplicates = remove_duplicate_segments(
        content
    )

    # 3. Ghép các mảnh thành câu nháp
    drafts, warnings = split_into_drafts(items)

    # 4. Kiểm tra timestamp
    warnings.extend(validate_drafts(drafts))

    if not drafts:
        raise ValueError("Khong tao duoc cau nhap")

    # 5. Tạo JSON đúng cấu trúc Shadowing HSK1
    data = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "sentences": [
            {
                "start": item["start"],
                "end": item["end"],
                "hanzi": item["hanzi"],
                "pinyin": item["pinyin"],
                "vi": "",
            }
            for item in drafts
        ],
    }

    # 6. Lưu bản nháp vào HSK2/data/processed
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    # 7. Tạo file TXT để rà soát từng câu
    lines = [
        "SHADOWING HSK2 - VIDEO 1",
        f"Video: {VIDEO_NAME}",
        f"YouTube ID: {VIDEO_ID}",
        f"So doan goc: {len(content)}",
        f"So doan sau loc: {len(items)}",
        f"So doan trung nghi ngo: {len(duplicates)}",
        f"So cau nhap: {len(drafts)}",
        "",
        "BAN NHAP - CHUA DOI CHIEU AUDIO",
        "=" * 60,
    ]

    for index, item in enumerate(drafts, start=1):
        lines.extend([
            "",
            f"CAU {index:03d}",
            (
                f"Time: {item['start']:.2f} "
                f"- {item['end']:.2f}"
            ),
            f"Hanzi: {item['hanzi']}",
            f"Pinyin: {item['pinyin']}",
            f"Ly do tach: {item['_reason']}",
        ])

    lines.extend([
        "",
        "=" * 60,
        "CANH BAO",
        f"So canh bao: {len(warnings)}",
    ])

    if warnings:
        lines.extend(warnings)
    else:
        lines.append(
            "Khong phat hien loi timestamp co ban."
        )

    lines.extend([
        "",
        "Chua dich tieng Viet.",
        "Chua xac minh noi dung va timestamp voi audio.",
        "Chua thay doi SQL Server.",
        "Khong goi Supadata.",
    ])

    REVIEW.parent.mkdir(parents=True, exist_ok=True)

    REVIEW.write_text(
        "\n".join(lines),
        encoding="utf-8-sig"
    )

    # 8. In kết quả
    print("\n===== KET QUA CHUAN HOA =====")
    print("So doan goc:", len(content))
    print("So doan sau loc:", len(items))
    print("So doan trung nghi ngo:", len(duplicates))
    print("So cau nhap:", len(drafts))
    print("So canh bao:", len(warnings))
    print("JSON:", OUTPUT)
    print("Review:", REVIEW)

    print("\n===== 5 CAU DAU =====")

    for index, item in enumerate(drafts[:5], start=1):
        print(f"\nCau {index}")
        print(
            "Time:",
            item["start"],
            "-",
            item["end"]
        )
        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])

    print("\nKhong goi Supadata.")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
