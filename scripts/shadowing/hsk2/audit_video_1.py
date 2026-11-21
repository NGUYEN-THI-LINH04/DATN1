
import json
import re
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw" / "video_1_native_zh.json"
PART1 = BASE / "previews" / "video_1_part1_corrected_40.json"
PART2 = BASE / "previews" / "video_1_part2_verified_0933.json"
REPORT = BASE / "previews" / "video_1_audit_report.txt"

def load(path):
    if not path.exists():
        return None
    with path.open(encoding="utf-8-sig") as f:
        return json.load(f)

def main():
    messages = []
    errors = []
    warnings = []

    def log(s):
        messages.append(s)

    raw = load(RAW)
    p1 = load(PART1)
    p2 = load(PART2)

    if raw is None:
        errors.append("Thieu transcript Supadata goc")
    if p1 is None:
        errors.append("Thieu file part1")
    if p2 is None:
        errors.append("Thieu file part2")

    if isinstance(raw, dict):
        fragments = raw.get("content", [])
    elif isinstance(raw, list):
        fragments = raw
    else:
        fragments = []

    if not isinstance(fragments, list):
        fragments = []

    log("=== KIEM TRA VIDEO HSK2 SO 1 ===")
    log(f"Supadata fragments: {len(fragments)}")

    if fragments:
        offsets = [
            (x["offset"] + x.get("duration", 0)) / 1000
            for x in fragments
            if isinstance(x, dict)
            and isinstance(x.get("offset"), (int, float))
        ]
        if offsets:
            log(f"Supadata moc cuoi: {max(offsets):.2f}s")

    if not isinstance(p1, list):
        p1 = []
    if not isinstance(p2, list):
        p2 = []

    log(f"Part1: {len(p1)} muc")
    log(f"Part2: {len(p2)} muc")

    items = p1 + p2
    log(f"Tong hien tai: {len(items)} muc")

    previous = None
    hanzi_count = Counter()

    for i, item in enumerate(items, 1):
        if not isinstance(item, dict):
            errors.append(f"Muc {i}: khong phai object")
            continue

        start = item.get("start")
        end = item.get("end")
        hanzi = str(item.get("hanzi") or "").strip()
        pinyin = str(item.get("pinyin") or "").strip()
        vi = str(item.get("vi") or "").strip()

        if not hanzi:
            errors.append(f"Muc {i}: thieu Hanzi")
        if not pinyin:
            errors.append(f"Muc {i}: thieu Pinyin")
        if not vi:
            errors.append(f"Muc {i}: thieu tieng Viet")

        if hanzi:
            hanzi_count[hanzi] += 1

        if not isinstance(start, (int, float)):
            errors.append(f"Muc {i}: start khong hop le")
            continue

        if not isinstance(end, (int, float)):
            errors.append(f"Muc {i}: end null/khong hop le")
            continue

        if end <= start:
            errors.append(f"Muc {i}: end <= start")

        duration = end - start
        if duration > 12:
            warnings.append(
                f"Muc {i}: cau dai {duration:.2f}s"
            )

        if previous is not None:
            prev_i, prev_start, prev_end = previous

            if start < prev_start:
                errors.append(
                    f"Muc {i}: start khong tang"
                )

            if start < prev_end - 0.15:
                warnings.append(
                    f"Muc {prev_i} -> {i}: "
                    f"chong {prev_end - start:.2f}s"
                )

            if start > prev_end + 3:
                warnings.append(
                    f"Muc {prev_i} -> {i}: "
                    f"khoang trong {start - prev_end:.2f}s"
                )

        previous = (i, start, end)

    for hanzi, count in hanzi_count.items():
        if count > 1:
            warnings.append(
                f"Trung Hanzi {count} lan: {hanzi}"
            )

    if items:
        starts = [
            x.get("start") for x in items
            if isinstance(x, dict)
            and isinstance(x.get("start"), (int, float))
        ]
        ends = [
            x.get("end") for x in items
            if isinstance(x, dict)
            and isinstance(x.get("end"), (int, float))
        ]
        if starts and ends:
            log(
                f"Pham vi JSON: "
                f"{min(starts):.2f}s - {max(ends):.2f}s"
            )

    log("")
    log(f"SO LOI: {len(errors)}")
    log(f"SO CANH BAO: {len(warnings)}")
    log("")
    log("=== LOI ===")
    log("\n".join(errors) if errors else "Khong co")
    log("")
    log("=== CANH BAO ===")
    log("\n".join(warnings) if warnings else "Khong co")
    log("")
    log("KET LUAN:")
    log(
        "CHUA SAN SANG GHI SQL - "
        "CAN HOAN THIEN PHU DE 09:33-19:05 "
        "VA XAC MINH TIMESTAMP."
    )

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "\n".join(messages),
        encoding="utf-8"
    )

    print("\n".join(messages[:9]))
    print(f"\nBao cao chi tiet: {REPORT}")
    print("Khong thay doi SQL Server.")
    print("Khong goi Supadata.")

if __name__ == "__main__":
    main()
