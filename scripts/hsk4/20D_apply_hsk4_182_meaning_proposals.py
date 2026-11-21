
# -*- coding: utf-8 -*-

"""
BUOC 20D - KIEM TRA VA AP DUNG 182 NGHIA DE XUAT HSK4

- Doc CSV review goc tu Buoc 20C
- Doc CSV de xuat nghia da bien tap
- Kiem tra 182 ID va KyTu
- Kiem tra SHA256 cua ca hai file
- Tao CSV ket qua trong data/processed

KHONG GHI SQL.
KHONG GAN BAI HOC.
KHONG TAO AUDIO.
"""

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(r"D:\DATN1")

PROCESSED = ROOT / "scripts" / "hsk4" / "data" / "processed"
REVIEW = ROOT / "scripts" / "hsk4" / "data" / "processed"

SOURCE_20C = PROCESSED / "hanzi_hsk4_182_meaning_review_pack.csv"

SOURCE_PROPOSAL = REVIEW / "hanzi_hsk4_182_meaning_review_proposed.csv"

OUTPUT = PROCESSED / "hanzi_hsk4_182_meaning_review_proposed.csv"

SUMMARY = PROCESSED / "hanzi_hsk4_182_meaning_review_proposed_summary.json"


EXPECTED_20C_HASH = (
    "3100eaa9b0e192fb3a174fb00e39803157dde58f518d7e01b03472c974211fe7"
)

EXPECTED_PROPOSAL_HASH = (
    "846848de877623616df2c956e8671e1834dbeb2dd4f35ff14be0ef00f1c9244e"
)


def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)

    return h.hexdigest()


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(f"Khong tim thay: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def main():
    print("=" * 70)
    print("BUOC 20D - AP DUNG DE XUAT NGHIA 182 CHU HSK4")
    print("=" * 70)

    print("\n[1] KIEM TRA HASH")

    h20c = sha256_file(SOURCE_20C)
    hproposal = sha256_file(SOURCE_PROPOSAL)

    print("20C:", h20c)
    print("PROPOSAL:", hproposal)

    if h20c != EXPECTED_20C_HASH:
        raise RuntimeError("FAIL: hash 20C khong khop")

    if hproposal != EXPECTED_PROPOSAL_HASH:
        raise RuntimeError("FAIL: hash proposal khong khop")

    print("PASS: hash hop le")

    print("\n[2] DOC CSV")

    _, original = read_csv(SOURCE_20C)
    fields, proposals = read_csv(SOURCE_PROPOSAL)

    if len(original) != 182 or len(proposals) != 182:
        raise RuntimeError("FAIL: so dong khong bang 182")

    required = {
        "MaChuHanTam",
        "KyTu",
        "NghiaDeXuatBienTap",
        "MucDoCanReview",
        "LyDoCanReview",
        "NguonDoiChieuBienTap",
    }

    if not required.issubset(fields):
        raise RuntimeError(
            f"FAIL: thieu cot {sorted(required - set(fields))}"
        )

    original_map = {}

    for row in original:
        mid = row["MaChuHanTam"].strip()

        if mid in original_map:
            raise RuntimeError(f"FAIL: trung ID 20C {mid}")

        original_map[mid] = row["KyTu"].strip()

    counts = Counter()
    seen = set()

    for row in proposals:
        mid = row["MaChuHanTam"].strip()
        char = row["KyTu"].strip()

        if mid in seen:
            raise RuntimeError(f"FAIL: trung ID proposal {mid}")

        seen.add(mid)

        if original_map.get(mid) != char:
            raise RuntimeError(f"FAIL: ID/KyTu khong khop {mid}")

        if not row["NghiaDeXuatBienTap"].strip():
            raise RuntimeError(f"FAIL: thieu nghia {mid}")

        counts[row["MucDoCanReview"].strip()] += 1

    if len(seen) != 182:
        raise RuntimeError("FAIL: mapping khong du 182")

    if counts["UU_TIEN"] != 37 or counts["THUONG"] != 145:
        raise RuntimeError(f"FAIL: phan loai sai {dict(counts)}")

    print("PASS: 182/182 ID va KyTu khop")
    print("UU_TIEN:", counts["UU_TIEN"])
    print("THUONG:", counts["THUONG"])

    print("\n[3] TAO OUTPUT")

    if OUTPUT.exists():
        existing_hash = sha256_file(OUTPUT)

        if existing_hash != EXPECTED_PROPOSAL_HASH:
            raise RuntimeError(
                "FAIL: output da ton tai nhung hash khac. "
                "Khong ghi de."
            )

        print("PASS: output da co va dung hash, khong ghi lai")

    else:
        OUTPUT.write_bytes(SOURCE_PROPOSAL.read_bytes())
        print("PASS: da tao output")

    result_hash = sha256_file(OUTPUT)

    if result_hash != EXPECTED_PROPOSAL_HASH:
        raise RuntimeError("FAIL: output hash khong khop")

    summary = {
        "buoc": "20D",
        "status": "PASS",
        "total": 182,
        "uu_tien": 37,
        "thuong": 145,
        "output": str(OUTPUT),
        "sha256": result_hash,
        "ghi_sql": False,
        "gan_bai_hoc": False,
        "tao_audio": False,
    }

    if not SUMMARY.exists():
        SUMMARY.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print("\n" + "=" * 70)
    print("PASS: BUOC 20D HOAN THANH")
    print("OUTPUT:", OUTPUT)
    print("SHA256:", result_hash)
    print("KHONG GHI SQL")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nFAIL:", exc)
        raise SystemExit(1)
