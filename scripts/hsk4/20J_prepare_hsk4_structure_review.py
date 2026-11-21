
# -*- coding: utf-8 -*-

import csv
import hashlib
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\DATN1\scripts\hsk4\data\processed")

SOURCE = ROOT / "hanzi_hsk4_300_enriched_sources.csv"
ISSUES = ROOT / "hanzi_hsk4_300_source_issues.csv"
OUTPUT = ROOT / "hanzi_hsk4_28_structure_review_20J.csv"

EXPECTED_SOURCE = (
    "5f85c0e6c74693e7a411e5e8531cad824ff2742a70e2e4933a089847ada45c8d"
)
EXPECTED_ISSUES = (
    "acebe2555ad0a8188aa7bf4b2f54dc5e219924ea63272975811ac1e0f697f943"
)

# Kangxi radical numbers, for the seven ambiguous cases only.
RADICALS = {
    8: "亠",
    19: "力",
    24: "十",
    36: "夕",
    57: "弓",
    61: "心",
    66: "攴",
    75: "木",
    81: "比",
    116: "穴",
    117: "立",
    135: "舌",
    141: "虍",
    180: "音",
}

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()

def read(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def val(row, key):
    return (row.get(key) or "").strip()

def main():
    print("=" * 72)
    print("BUOC 20J - LAP BANG REVIEW CAU TRUC HSK4")
    print("KHONG GHI SQL - KHONG SUA DU LIEU GOC")
    print("=" * 72)

    print("\n[1] KIEM TRA HASH")
    if sha(SOURCE) != EXPECTED_SOURCE:
        raise ValueError("FAIL: hash enriched Step19 khong khop")
    if sha(ISSUES) != EXPECTED_ISSUES:
        raise ValueError("FAIL: hash issues Step19 khong khop")
    print("PASS: 2 snapshot hop le")

    source = read(SOURCE)
    issues = read(ISSUES)

    if len(source) != 300 or len(issues) != 28:
        raise ValueError("FAIL: so dong khong khop 300/28")

    by_id = {val(r, "MaChuHanTam"): r for r in source}
    if len(by_id) != 300:
        raise ValueError("FAIL: trung ID trong source")

    result = []
    counts = Counter()

    print("\n[2] LAP DE XUAT")

    for issue in issues:
        mid = val(issue, "MaChuHanTam")
        char = val(issue, "KyTu")
        typ = val(issue, "LoaiVanDe")
        r = by_id.get(mid)

        if not r or val(r, "KyTu") != char:
            raise ValueError(f"FAIL: mapping {mid} {char}")

        counts[typ] += 1

        mmah = val(r, "SoNetMakeMeAHanzi")
        unihan = val(r, "SoNetUnihanRaw")
        rs = val(r, "RSUnicodeRaw")
        radical = val(r, "RadicalMakeMeAHanzi")

        candidate = ""
        note = ""

        if typ == "NHIEU_RSUNICODE":
            numbers = [
                int(x.split(".")[0])
                for x in rs.split()
            ]
            matches = [
                n for n in numbers
                if RADICALS.get(n) == radical
            ]

            if len(matches) == 1:
                candidate = str(matches[0])
                note = "DE_XUAT_MMAH_KHOP_UNIHAN_CAN_DUYET"
            else:
                note = "CHUA_XAC_DINH_CAN_DUYET_THU_CONG"

        elif typ == "LECH_SO_NET":
            note = "GIU_HAI_NGUON_CHUA_CHOT_SO_NET"
        else:
            raise ValueError(f"FAIL: loai issue la {typ}")

        result.append({
            "MaChuHanTam": mid,
            "KyTu": char,
            "LoaiVanDe": typ,
            "SoNetMMAH": mmah,
            "SoNetUnihan": unihan,
            "RSUnicodeRaw": rs,
            "RadicalMMAH": radical,
            "SoBoThuDeXuat": candidate,
            "SoBoThuSQLHienTai": val(r, "SoBoThuSQL"),
            "KyHieuBoThuSQL": val(r, "KyHieuBoThuSQL"),
            "TrangThaiDeXuat": note,
            "SoNetChot": "",
            "SoBoThuChot": "",
        })

        print(
            f"{mid} | {char} | {typ} | "
            f"net MMAH={mmah}, Unihan={unihan} | "
            f"bo thu de xuat={candidate or '-'} | {note}"
        )

    if counts != Counter({
        "LECH_SO_NET": 21,
        "NHIEU_RSUNICODE": 7,
    }):
        raise ValueError(f"FAIL: phan loai khong khop: {counts}")

    print("\n[3] GHI BAO CAO")

    fields = list(result[0].keys())

    if OUTPUT.exists():
        raise FileExistsError(
            f"FAIL: output da ton tai, khong ghi de: {OUTPUT}"
        )

    with OUTPUT.open("x", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result)

    print("\nPASS: BUOC 20J HOAN THANH")
    print("LECH_SO_NET:", counts["LECH_SO_NET"])
    print("NHIEU_RSUNICODE:", counts["NHIEU_RSUNICODE"])
    print("OUTPUT:", OUTPUT)
    print("SHA256:", sha(OUTPUT))
    print("CHUA CHOT SO NET / BO THU")
    print("KHONG GHI SQL")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\nFAIL:", e)
        raise SystemExit(1)
