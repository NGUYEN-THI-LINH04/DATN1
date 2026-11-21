
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HSK2 = ROOT / "scripts" / "shadowing" / "hsk2"

INPUT = (
    HSK2 / "previews"
    / "video_1_part2_corrected_80.json"
)

OUTPUT = (
    HSK2 / "previews"
    / "video_1_part2_timestamp_review.txt"
)


def main():
    with INPUT.open("r", encoding="utf-8-sig") as f:
        sentences = json.load(f)

    if len(sentences) != 40:
        raise ValueError("Phan 2 phai co 40 cau.")

    lines = [
        "HSK2 VIDEO 1 - KIEM TRA PHAN 2",
        "Video: nxAfRmACtZs",
        "Cau: 41-80",
        "",
        "BAN NHAP - CHUA XAC MINH AUDIO",
        "=" * 60,
    ]

    warnings = []

    for i, item in enumerate(sentences):
        number = i + 41
        start = float(item["start"])
        end = float(item["end"])
        hanzi = item["hanzi"]

        lines.extend([
            "",
            f"CAU {number}",
            f"Time: {start:.2f} - {end:.2f}",
            f"Hanzi: {hanzi}",
            f"Viet: {item['vi']}",
        ])

        if end <= start:
            warnings.append(
                f"Cau {number}: timestamp khong hop le"
            )

        if end - start > 12:
            warnings.append(
                f"Cau {number}: dai {end-start:.2f}s"
            )

        if i > 0:
            prev = sentences[i - 1]
            prev_end = float(prev["end"])

            if start < prev_end:
                overlap = prev_end - start
                warnings.append(
                    f"Cau {number-1}-{number}: "
                    f"chong {overlap:.2f}s"
                )

        if "……" in hanzi or "…" in hanzi:
            warnings.append(
                f"Cau {number}: co noi dung cat ngang"
            )

        status = item.get(
            "_review_status",
            "chua_co_trang_thai"
        )

        lines.append(f"Trang thai: {status}")

        if item.get("_review_note"):
            lines.append(
                f"Ghi chu: {item['_review_note']}"
            )

    lines.extend([
        "",
        "=" * 60,
        "DANH SACH CAN KIEM TRA",
        f"Tong canh bao: {len(warnings)}",
        "",
    ])

    lines.extend(warnings)

    lines.extend([
        "",
        "Khong tu dong sua timestamp.",
        "Khong goi Supadata.",
        "Khong thay doi SQL Server.",
    ])

    if OUTPUT.exists():
        raise FileExistsError(
            f"Khong ghi de file da co: {OUTPUT}"
        )

    OUTPUT.write_text(
        "\n".join(lines),
        encoding="utf-8-sig"
    )

    print("===== KIEM TRA HSK2 - PHAN 2 =====")
    print("Tong cau:", len(sentences))
    print("So canh bao:", len(warnings))
    print("File:", OUTPUT)

    print("\n===== CANH BAO =====")
    for warning in warnings:
        print("-", warning)

    print("\nKhong goi Supadata.")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
