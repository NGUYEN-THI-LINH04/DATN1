# -*- coding: utf-8 -*-

"""
BUOC 20I - DOI CHIEU NGUON CAU TRUC CHO 28 CHU HAN HSK4

Chi doc:
- hanzi_hsk4_300_enriched_sources.csv
- hanzi_hsk4_300_source_issues.csv

Muc tieu:
- Xac minh dung snapshot Step19.
- Lay dung 28 chu co issue.
- In cac cot lien quan:
    + so net
    + radical / bo thu
    + kRSUnicode
    + Make Me a Hanzi
    + Unihan
    + decomposition / structure neu co
- KHONG ghi file.
- KHONG ghi SQL.
"""

import csv
import hashlib
from pathlib import Path


ROOT = Path(r"D:\DATN1")

PROCESSED = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

SOURCE_ENRICHED = (
    PROCESSED
    / "hanzi_hsk4_300_enriched_sources.csv"
)

SOURCE_ISSUES = (
    PROCESSED
    / "hanzi_hsk4_300_source_issues.csv"
)


EXPECTED_ENRICHED_SHA256 = (
    "5f85c0e6c74693e7a411e5e8531cad824ff2742a70e2e4933a089847ada45c8d"
)

EXPECTED_ISSUES_SHA256 = (
    "acebe2555ad0a8188aa7bf4b2f54dc5e219924ea63272975811ac1e0f697f943"
)


def clean(value):
    return (value or "").strip()


def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        fields = list(reader.fieldnames or [])
        rows = list(reader)

    return fields, rows


def is_structure_field(field):
    """
    Khong doan schema cu the.
    Tu dong chon cac cot co ten lien quan cau truc Hanzi.
    """

    key = field.lower()

    keywords = [
        "machuhantam",
        "kytu",

        "sonet",
        "stroke",

        "radical",
        "bothu",
        "mabothu",

        "rsunicode",
        "krs",

        "unihan",

        "makeme",
        "mmah",

        "decomp",
        "decomposition",

        "structure",
        "cautruc",

        "ids",

        "kangxi",
    ]

    return any(
        keyword in key
        for keyword in keywords
    )


def main():

    print("=" * 88)
    print("BUOC 20I - DOI CHIEU NGUON CAU TRUC 28 CHU HAN HSK4")
    print("=" * 88)
    print("CHI DOC CSV - KHONG GHI FILE - KHONG GHI SQL")

    # ============================================================
    # 1. KIEM TRA SNAPSHOT
    # ============================================================

    print("\n[1] KIEM TRA SNAPSHOT")

    hash_enriched = sha256_file(
        SOURCE_ENRICHED
    )

    hash_issues = sha256_file(
        SOURCE_ISSUES
    )

    print("STEP19 ENRICHED SHA256:")
    print(hash_enriched)

    print("STEP19 ISSUES SHA256:")
    print(hash_issues)

    if hash_enriched != EXPECTED_ENRICHED_SHA256:
        raise RuntimeError(
            "FAIL: hash enriched Step19 khong khop.\n"
            f"Expected: {EXPECTED_ENRICHED_SHA256}\n"
            f"Actual:   {hash_enriched}"
        )

    if hash_issues != EXPECTED_ISSUES_SHA256:
        raise RuntimeError(
            "FAIL: hash issues Step19 khong khop.\n"
            f"Expected: {EXPECTED_ISSUES_SHA256}\n"
            f"Actual:   {hash_issues}"
        )

    print("PASS: snapshot Step19 hop le.")

    # ============================================================
    # 2. DOC DU LIEU
    # ============================================================

    print("\n[2] DOC DU LIEU")

    enriched_fields, enriched_rows = read_csv(
        SOURCE_ENRICHED
    )

    issue_fields, issue_rows = read_csv(
        SOURCE_ISSUES
    )

    print("Enriched rows:", len(enriched_rows))
    print("Issue rows:", len(issue_rows))

    if len(enriched_rows) != 300:
        raise RuntimeError(
            f"FAIL: enriched phai co 300 dong, "
            f"thuc te {len(enriched_rows)}"
        )

    if len(issue_rows) != 28:
        raise RuntimeError(
            f"FAIL: issues phai co 28 dong, "
            f"thuc te {len(issue_rows)}"
        )

    required_enriched = {
        "MaChuHanTam",
        "KyTu",
    }

    required_issues = {
        "MaChuHanTam",
        "KyTu",
        "LoaiVanDe",
        "ChiTiet",
    }

    missing_enriched = (
        required_enriched
        - set(enriched_fields)
    )

    missing_issues = (
        required_issues
        - set(issue_fields)
    )

    if missing_enriched:
        raise RuntimeError(
            "FAIL: enriched thieu cot:\n"
            + "\n".join(
                sorted(missing_enriched)
            )
        )

    if missing_issues:
        raise RuntimeError(
            "FAIL: issues thieu cot:\n"
            + "\n".join(
                sorted(missing_issues)
            )
        )

    print("PASS: header co cac cot khoa can thiet.")

    # ============================================================
    # 3. CAC COT CAU TRUC TIM DUOC
    # ============================================================

    print("\n[3] CAC COT CAU TRUC TIM DUOC TRONG STEP19")

    structure_fields = [
        field
        for field in enriched_fields
        if is_structure_field(field)
    ]

    if not structure_fields:
        raise RuntimeError(
            "FAIL: khong tim thay cot cau truc nao "
            "trong enriched CSV."
        )

    for index, field in enumerate(
        structure_fields,
        start=1,
    ):
        print(
            f"{index:02d}. {field}"
        )

    # ============================================================
    # 4. TAO MAP 300 CHU
    # ============================================================

    print("\n[4] TAO MAP ENRICHED")

    enriched_map = {}

    for row in enriched_rows:

        mid = clean(
            row["MaChuHanTam"]
        )

        if not mid:
            raise RuntimeError(
                "FAIL: MaChuHanTam rong "
                "trong enriched."
            )

        if mid in enriched_map:
            raise RuntimeError(
                f"FAIL: trung MaChuHanTam: {mid}"
            )

        enriched_map[mid] = row

    if len(enriched_map) != 300:
        raise RuntimeError(
            "FAIL: enriched khong co "
            "300 ID duy nhat."
        )

    print("PASS: 300 ID duy nhat.")

    # ============================================================
    # 5. DOI CHIEU 28 ISSUE
    # ============================================================

    print("\n[5] DOI CHIEU 28 ISSUE")

    found = 0

    for issue_index, issue in enumerate(
        issue_rows,
        start=1,
    ):

        mid = clean(
            issue["MaChuHanTam"]
        )

        char = clean(
            issue["KyTu"]
        )

        issue_type = clean(
            issue["LoaiVanDe"]
        )

        detail = clean(
            issue["ChiTiet"]
        )

        if mid not in enriched_map:
            raise RuntimeError(
                f"FAIL: {mid} khong co "
                "trong enriched."
            )

        source = enriched_map[mid]

        source_char = clean(
            source["KyTu"]
        )

        if source_char != char:
            raise RuntimeError(
                f"FAIL: KyTu khong khop tai {mid}: "
                f"issue={char}, enriched={source_char}"
            )

        found += 1

        print("\n" + "=" * 88)

        print(
            f"ISSUE {issue_index:02d}/28"
        )

        print("=" * 88)

        print("MaChuHanTam:", mid)
        print("KyTu:", char)
        print("LoaiVanDe:", issue_type)
        print("ChiTiet:", detail)

        print("\n--- NGUON STEP19 ---")

        nonempty_count = 0

        for field in structure_fields:

            value = clean(
                source.get(field)
            )

            if not value:
                continue

            print(
                f"{field}: {value}"
            )

            nonempty_count += 1

        if nonempty_count == 0:
            print(
                "(Khong co gia tri cau truc "
                "khac rong cho dong nay)"
            )

    if found != 28:
        raise RuntimeError(
            f"FAIL: chi doi chieu duoc {found}/28."
        )

    print("\n" + "=" * 88)
    print("PASS: BUOC 20I HOAN THANH")
    print("=" * 88)

    print("Doi chieu:", found, "/ 28")

    print(
        "CHI DOC - KHONG GHI FILE - "
        "KHONG GHI SQL"
    )

    print("=" * 88)


if __name__ == "__main__":

    try:
        main()

    except Exception as exc:

        print("\nFAIL:", exc)

        raise SystemExit(1)