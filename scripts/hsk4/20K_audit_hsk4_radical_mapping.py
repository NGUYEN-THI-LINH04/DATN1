
# -*- coding: utf-8 -*-

import csv
import hashlib
from pathlib import Path

BASE = Path(r"D:\DATN1\scripts\hsk4\data\processed")

SOURCE = BASE / "hanzi_hsk4_300_enriched_sources.csv"
REVIEW = BASE / "hanzi_hsk4_28_structure_review_20J.csv"

HASH_SOURCE = "5f85c0e6c74693e7a411e5e8531cad824ff2742a70e2e4933a089847ada45c8d"
HASH_REVIEW = "edb9cee3f84ada35ca5996394969aa4ab3ebfc60e8f9269c3b8260096e98cf5a"

RADICALS = {
    57: "弓",
    61: "心",
    75: "木",
    81: "比",
    116: "穴",
    117: "立",
    135: "舌",
}

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def get(row, key):
    return (row.get(key) or "").strip()

def main():
    print("=" * 72)
    print("BUOC 20K - AUDIT ANH XA BO THU HSK4")
    print("CHI DOC - KHONG GHI FILE - KHONG GHI SQL")
    print("=" * 72)

    if sha256(SOURCE) != HASH_SOURCE:
        raise RuntimeError("FAIL: hash Step19 khong khop")

    if sha256(REVIEW) != HASH_REVIEW:
        raise RuntimeError("FAIL: hash Step20J khong khop")

    print("PASS: hai snapshot hop le")

    source = load(SOURCE)
    review = load(REVIEW)

    if len(source) != 300 or len(review) != 28:
        raise RuntimeError("FAIL: so dong khong dung 300/28")

    by_id = {get(r, "MaChuHanTam"): r for r in source}

    if len(by_id) != 300:
        raise RuntimeError("FAIL: ID Step19 khong duy nhat")

    print("\n[1] KIEM TRA RIENG CHU 巨")

    giant = by_id.get("H4-0468")

    if not giant or get(giant, "KyTu") != "巨":
        raise RuntimeError("FAIL: khong tim thay H4-0468 | 巨")

    for field in [
        "MaChuHanTam",
        "KyTu",
        "RSUnicodeRaw",
        "SoBoThuUnicode",
        "RadicalMakeMeAHanzi",
        "MaBoThuSQL",
        "SoBoThuSQL",
        "KyHieuBoThuSQL",
        "TenBoThuSQL",
        "DecompositionMakeMeAHanzi",
    ]:
        print(f"{field}: {get(giant, field)}")

    print("\n[2] DOI CHIEU 7 BO THU DE XUAT")

    ambiguous = [
        r for r in review
        if get(r, "LoaiVanDe") == "NHIEU_RSUNICODE"
    ]

    if len(ambiguous) != 7:
        raise RuntimeError("FAIL: khong du 7 truong hop")

    for item in ambiguous:
        mid = get(item, "MaChuHanTam")
        row = by_id[mid]

        if get(item, "KyTu") != get(row, "KyTu"):
            raise RuntimeError(f"FAIL: KyTu lech tai {mid}")

        number = int(get(item, "SoBoThuDeXuat"))
        expected_symbol = RADICALS.get(number)
        actual_symbol = get(row, "RadicalMakeMeAHanzi")

        if expected_symbol != actual_symbol:
            raise RuntimeError(
                f"FAIL: bo thu khong khop tai {mid}"
            )

        print(
            f"{mid} | {get(row, 'KyTu')} | "
            f"Bo {number} ({expected_symbol}) | "
            f"RS={get(row, 'RSUnicodeRaw')} | "
            "DOI_CHIEU_NGUON_OK"
        )

    print("\n[3] TIM CAC DONG STEP19 DUNG MA BO THU 48")

    matches = [
        r for r in source
        if get(r, "MaBoThuSQL") == "48"
        or get(r, "SoBoThuSQL") == "48"
    ]

    print("So dong:", len(matches))

    for row in matches:
        print(
            f"{get(row, 'MaChuHanTam')} | "
            f"{get(row, 'KyTu')} | "
            f"Unihan={get(row, 'RSUnicodeRaw')} | "
            f"MMAH={get(row, 'RadicalMakeMeAHanzi')} | "
            f"SQL={get(row, 'KyHieuBoThuSQL')} | "
            f"MaBoThuSQL={get(row, 'MaBoThuSQL')}"
        )

    print("\n" + "=" * 72)
    print("PASS: BUOC 20K HOAN THANH")
    print("7 BO THU DA DOI CHIEU NGUON, CHUA CHOT SQL")
    print("21 LECH SO NET CHUA CHOT")
    print("KHONG GHI FILE - KHONG GHI SQL")
    print("=" * 72)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("FAIL:", exc)
        raise SystemExit(1)
