
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
PREVIEWS = BASE / "previews"
PROCESSED = BASE / "data" / "processed"

PARTS = [
    PREVIEWS / "video_1_part1_corrected_40.json",
    PREVIEWS / "video_1_part2_verified_0933.json",
    PREVIEWS / "video_1_part3_0933_to_end.json",
]

OUTPUT = PROCESSED / "video_1_final.json"
REPORT = PREVIEWS / "video_1_final_report.txt"

YOUTUBE_ID = "nxAfRmACtZs"
LAST_TIME = 1147.55

def load(path):
    if not path.exists():
        raise FileNotFoundError(f"Thieu file: {path}")
    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"File phai la JSON array: {path}")
    return data

def main():
    all_items = []
    report = []
    errors = []
    warnings = []

    # Doc du lieu, khong sua file goc.
    for part_number, path in enumerate(PARTS, 1):
        data = load(path)
        report.append(f"Part {part_number}: {len(data)} muc")

        for index, item in enumerate(data, 1):
            if not isinstance(item, dict):
                errors.append(
                    f"Part {part_number}, muc {index}: khong phai object"
                )
                continue

            start = item.get("start")
            hanzi = str(item.get("hanzi") or "").strip()
            pinyin = str(item.get("pinyin") or "").strip()
            vi = str(item.get("vi") or "").strip()

            if not isinstance(start, (int, float)):
                errors.append(
                    f"Part {part_number}, muc {index}: start sai"
                )
                continue

            if not all([hanzi, pinyin, vi]):
                errors.append(
                    f"Part {part_number}, muc {index}: thieu noi dung"
                )
                continue

            all_items.append({
                "start": float(start),
                "end": item.get("end"),
                "hanzi": hanzi,
                "pinyin": pinyin,
                "vi": vi,
                "_source_part": part_number,
                "_original_index": index,
                "_timing_status": "chua_xac_minh_audio",
            })

    # Sap xep theo thoi gian; giu thu tu goc neu trung start.
    all_items.sort(key=lambda x: x["start"])

    # Loai ban trung khi cung thoi diem va cung Hanzi.
    unique = []
    seen = set()
    duplicate_count = 0

    for item in all_items:
        key = (
            round(item["start"], 2),
            "".join(item["hanzi"].split())
        )

        if key in seen:
            duplicate_count += 1
            continue

        seen.add(key)
        unique.append(item)

    # Xu ly cac moc trung start:
    # Phan chia tam khoang phu de cho cac cau,
    # KHONG coi la thoi gian audio da xac minh.
    i = 0
    while i < len(unique):
        j = i + 1

        while (
            j < len(unique)
            and unique[j]["start"] == unique[i]["start"]
        ):
            j += 1

        count = j - i

        if count > 1:
            next_start = (
                unique[j]["start"]
                if j < len(unique)
                else LAST_TIME
            )

            duration = next_start - unique[i]["start"]

            if duration <= 0:
                errors.append(
                    f"Khong du thoi gian tai {unique[i]['start']}s"
                )
            else:
                step = duration / count
                original_start = unique[i]["start"]

                for k in range(count):
                    unique[i + k]["start"] = round(
                        original_start + k * step, 3
                    )

                warnings.append(
                    f"Moc {original_start}s: "
                    f"tam chia {count} cau trong {duration:.2f}s"
                )

        i = j

    # Xu ly end theo start cua cau tiep theo.
    # Day la moc phu de du kien, khong phai audio alignment.
    for i, item in enumerate(unique):
        start = item["start"]

        if i + 1 < len(unique):
            next_start = unique[i + 1]["start"]
        else:
            next_start = LAST_TIME

        original_end = item["end"]

        if (
            isinstance(original_end, (int, float))
            and original_end > next_start + 0.15
        ):
            warnings.append(
                f"Muc {i+1}: end goc {original_end}s "
                f"chong start tiep theo {next_start}s"
            )

        if next_start <= start:
            errors.append(
                f"Muc {i+1}: thoi gian khong tang "
                f"({start} -> {next_start})"
            )
            continue

        item["end"] = round(next_start, 3)
        item["start"] = round(start, 3)

    # Kiem tra ket qua.
    for i, item in enumerate(unique, 1):
        if (
            not isinstance(item.get("end"), (int, float))
            or item["end"] <= item["start"]
        ):
            errors.append(f"Muc {i}: start/end khong hop le")

        if item["end"] - item["start"] > 15:
            warnings.append(
                f"Muc {i}: thoi luong dai "
                f"{item['end'] - item['start']:.2f}s"
            )

    report.append(f"Tong ban dau: {len(all_items)}")
    report.append(f"Da loai trung: {duplicate_count}")
    report.append(f"Tong sau ghep: {len(unique)}")
    report.append(f"So loi: {len(errors)}")
    report.append(f"So canh bao: {len(warnings)}")

    report.append("\n=== LOI ===")
    report.extend(errors or ["Khong co"])

    report.append("\n=== CANH BAO ===")
    report.extend(warnings or ["Khong co"])

    report.append(
        "\nTimestamp da chuan hoa theo moc phu de, "
        "CHUA xac minh audio."
    )

    PREVIEWS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("=== GHEP VIDEO HSK2 SO 1 ===")
    for line in report[:6]:
        print(line)

    if errors:
        print("CON LOI - KHONG XUAT FILE FINAL")
        print(f"Chi tiet: {REPORT}")
        return

    # Chi xuat cac truong ma website can.
    sentences = [
        {
            "start": item["start"],
            "end": item["end"],
            "hanzi": item["hanzi"],
            "pinyin": item["pinyin"],
            "vi": item["vi"],
        }
        for item in unique
    ]

    payload = {
        "module": "shadowing",
        "youtube_id": YOUTUBE_ID,
        "sentences": sentences
    }

    PROCESSED.mkdir(parents=True, exist_ok=True)

    # Khong ghi de ban final da ton tai.
    if OUTPUT.exists():
        print(f"FILE DA TON TAI: {OUTPUT}")
        print("Khong ghi de file cu.")
        return

    OUTPUT.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print(f"File: {OUTPUT}")
    print(f"Bao cao: {REPORT}")
    print("Da tao JSON du kien cho website.")
    print("Chua xac minh timestamp theo audio.")
    print("CHUA ghi SQL Server.")
    print("Khong thay doi HSK1.")

if __name__ == "__main__":
    main()
