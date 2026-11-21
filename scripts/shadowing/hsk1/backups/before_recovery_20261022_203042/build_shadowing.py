
import json
import argparse
from pathlib import Path
from pypinyin import lazy_pinyin, Style

ROOT = Path(r"D:\DATN1")
BASE = ROOT / "scripts" / "shadowing"


def make_pinyin(hanzi):
    return " ".join(
        lazy_pinyin(hanzi, style=Style.TONE)
    )


def build(video_id, raw_file, edited_file):
    raw = json.loads(
        Path(raw_file).read_text(encoding="utf-8")
    )

    edited = json.loads(
        Path(edited_file).read_text(encoding="utf-8")
    )

    source = raw.get("content", [])
    if not source:
        raise ValueError("File Supadata khong co content")

    sentences = []

    for index, item in enumerate(edited, start=1):
        start = float(item["start"])
        end = float(item["end"])
        hanzi = item["hanzi"].strip()
        vi = item.get("vi", "").strip()

        if end <= start:
            raise ValueError(f"Cau {index}: thoi gian sai")

        if not hanzi:
            raise ValueError(f"Cau {index}: thieu Hanzi")

        if sentences and start < sentences[-1]["end"]:
            raise ValueError(
                f"Cau {index}: timestamp chong len cau truoc"
            )

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": make_pinyin(hanzi),
            "vi": vi
        })

    result = {
        "module": "shadowing",
        "youtube_id": video_id,
        "sentences": sentences
    }

    output = BASE / "previews" / f"{video_id}_ready.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Tong doan Supadata: {len(source)}")
    print(f"Tong cau da chuan hoa: {len(sentences)}")
    print(f"File ket qua: {output}")
    print("CHUA CAP NHAT SQL SERVER")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-id", required=True)
    parser.add_argument("--raw", required=True)
    parser.add_argument("--edited", required=True)
    args = parser.parse_args()

    build(args.video_id, args.raw, args.edited)
