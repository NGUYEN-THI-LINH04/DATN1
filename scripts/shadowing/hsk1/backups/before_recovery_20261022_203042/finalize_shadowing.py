
import json
import argparse
from pathlib import Path

BASE = Path(r"D:\DATN1\scripts\shadowing")


def finalize(input_path, output_path):
    data = json.loads(
        input_path.read_text(encoding="utf-8")
    )

    video_id = data["youtube_id"]
    sentences = data["sentences"]

    if not sentences:
        raise ValueError("Khong co cau nao de xu ly")

    result = []
    review = []

    for i, item in enumerate(sentences):
        start = item.get("start")
        end = item.get("end")

        if start is None or end is None:
            review.append(
                f"Cau {i + 1}: thieu timestamp"
            )
            continue

        start = float(start)
        end = float(end)

        if end <= start:
            review.append(
                f"Cau {i + 1}: thoi gian khong hop le"
            )
            continue

        # Dieu chinh end de khong chong cau tiep theo
        if i + 1 < len(sentences):
            next_start = sentences[i + 1].get("start")

            if next_start is not None:
                next_start = float(next_start)

                if next_start <= start:
                    review.append(
                        f"Cau {i + 1}: thu tu thoi gian sai"
                    )
                    continue

                end = min(end, next_start - 0.05)

        if end <= start:
            review.append(
                f"Cau {i + 1}: thoi luong qua ngan"
            )
            continue

        ratio = float(item.get("match_ratio", 0))

        if ratio < 0.95:
            review.append(
                f"Cau {i + 1}: noi dung chi khop {ratio:.0%}"
                f" | {item['hanzi']}"
            )

        if not item.get("vi", "").strip():
            review.append(
                f"Cau {i + 1}: chua co tieng Viet"
            )

        result.append({
            "start": round(start, 2),
            "end": round(end, 2),
            "hanzi": item["hanzi"],
            "pinyin": item["pinyin"],
            "vi": item["vi"]
        })

    output = {
        "module": "shadowing",
        "youtube_id": video_id,
        "sentences": result
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\n=== KET QUA ===")
    print("Video:", video_id)
    print("So cau ban dau:", len(sentences))
    print("So cau da xuat:", len(result))
    print("File:", output_path)

    print("\n=== CAC CAU CAN KIEM TRA ===")

    if review:
        for message in review:
            print("-", message)
    else:
        print("Khong phat hien loi tu dong")

    print("\n=== THOI GIAN HIEN THI ===")

    for i, item in enumerate(result, 1):
        print(
            f"{i:02d}. "
            f"{item['start']:.2f}s - "
            f"{item['end']:.2f}s | "
            f"{item['hanzi']}"
        )

    print("\nCHUA CAP NHAT SQL SERVER")
    print("FILE NAY LA BAN XEM TRUOC")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default=str(
            BASE / "previews" / "xiaozhang_review.json"
        )
    )

    parser.add_argument(
        "--output",
        default=str(
            BASE / "previews" / "xiaozhang_final_preview.json"
        )
    )

    args = parser.parse_args()

    finalize(
        Path(args.input),
        Path(args.output)
    )
