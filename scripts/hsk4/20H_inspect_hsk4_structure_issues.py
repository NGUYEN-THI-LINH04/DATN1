# -*- coding: utf-8 -*-

import csv
import hashlib
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\DATN1")

SOURCE = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
    / "hanzi_hsk4_300_source_issues.csv"
)

EXPECTED_SHA256 = (
    "acebe2555ad0a8188aa7bf4b2f54dc5e219924ea63272975811ac1e0f697f943"
)


def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)

    return h.hexdigest()


def main():

    print("=" * 80)
    print("BUOC 20H - DOC 28 VAN DE CAU TRUC CHU HAN HSK4")
    print("=" * 80)
    print("CHI DOC CSV - KHONG GHI BAT KY FILE NAO")

    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"Khong tim thay:\n{SOURCE}"
        )

    print("\n[1] KIEM TRA SNAPSHOT")

    actual_hash = sha256_file(SOURCE)

    print("SHA256:")
    print(actual_hash)

    if actual_hash != EXPECTED_SHA256:
        raise RuntimeError(
            "FAIL: hash issue CSV khong khop.\n"
            f"Expected: {EXPECTED_SHA256}\n"
            f"Actual:   {actual_hash}"
        )

    print("PASS: snapshot issue CSV hop le.")

    print("\n[2] DOC CSV")

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        fields = list(reader.fieldnames or [])
        rows = list(reader)

    print("Tong dong:", len(rows))

    if len(rows) != 28:
        raise RuntimeError(
            f"FAIL: mong doi 28 dong, thuc te {len(rows)}"
        )

    print("PASS: dung 28 issue.")

    print("\n[3] HEADER")

    for i, field in enumerate(fields, start=1):
        print(f"{i:02d}. {field}")

    print("\n[4] PHAN LOAI ISSUE")

    # Tự tìm cột loại issue thay vì đoán schema.
    issue_field = None

    for candidate in [
        "LoaiVanDe",
        "LoaiIssue",
        "VanDe",
        "Issue",
        "TrangThaiReview",
    ]:
        if candidate in fields:
            issue_field = candidate
            break

    if issue_field:

        counts = Counter(
            (row.get(issue_field) or "").strip()
            for row in rows
        )

        print("Cot phan loai:", issue_field)

        for key, value in sorted(counts.items()):
            print(f"{key}: {value}")

    else:
        print(
            "Khong tim thay cot phan loai theo ten du kien; "
            "se in nguyen 28 dong de doi chieu."
        )

    print("\n[5] TOAN BO 28 ISSUE")

    for index, row in enumerate(rows, start=1):

        print("\n" + "-" * 80)
        print(f"ISSUE {index:02d}")
        print("-" * 80)

        for field in fields:

            value = (row.get(field) or "").strip()

            if value:
                print(f"{field}: {value}")

    print("\n" + "=" * 80)
    print("PASS: BUOC 20H HOAN THANH")
    print("CHI DOC - KHONG GHI FILE - KHONG GHI SQL")
    print("=" * 80)


if __name__ == "__main__":

    try:
        main()

    except Exception as exc:

        print("\nFAIL:", exc)
        raise SystemExit(1)