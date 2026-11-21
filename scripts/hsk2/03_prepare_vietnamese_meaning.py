
from pathlib import Path
from collections import Counter
import csv
import re


# =====================================================
# 1. CAU HINH DUONG DAN
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_DIR / "vocabulary_hsk2_clean.csv"

OUTPUT_FILE = (
    DATA_DIR / "vocabulary_hsk2_meaning_draft.csv"
)

REVIEW_FILE = (
    DATA_DIR / "vocabulary_hsk2_meaning_review.csv"
)

EXPECTED_TOTAL = 772


# =====================================================
# 2. CAC COT XUAT
# =====================================================

FIELDS = [
    "MaTuHSK",
    "MaMucNoiBo",
    "ChuHan",
    "PhienAm",
    "TuLoaiNguon",
    "NghiaThamChieu",
    "NghiaTiengVietDeXuat",
    "DanhSachNghia",
    "NghiaHocHSK2",
    "GhiChuLuongTu",
    "MaTuVungDaCo",
    "TrangThai",
    "VanDeCanKiemTra",
    "TrangThaiKiemDuyet",
]


# =====================================================
# 3. HAM CHUAN HOA
# =====================================================

def clean_text(value):
    if value is None:
        return ""

    text = str(value).replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_meanings(value):
    """
    Tach cac cum nghia de nguoi dung xem.

    KHONG tu dong chon nghia nao la nghia HSK2.
    KHONG thay doi cot nghia goc.
    """

    text = clean_text(value)

    if not text:
        return []

    parts = re.split(
        r"\s*(?:/|\|\|)\s*",
        text
    )

    result = []
    seen = set()

    for part in parts:
        part = clean_text(part)

        if not part:
            continue

        # Loai phan LT doc lap khoi danh sach nghia
        if re.match(
            r"^LT\s*:",
            part,
            flags=re.IGNORECASE
        ):
            continue

        key = part.casefold()

        if key not in seen:
            seen.add(key)
            result.append(part)

    return result


def detect_review_reasons(row, meanings):
    reasons = []

    if not clean_text(row.get("ChuHan")):
        reasons.append("THIEU_CHU_HAN")

    if not clean_text(row.get("PhienAm")):
        reasons.append("THIEU_PINYIN")

    if not meanings:
        reasons.append("THIEU_NGHIA")

    if len(meanings) > 1:
        reasons.append("NHIEU_CUM_NGHIA")

    if any(";" in meaning for meaning in meanings):
        reasons.append("NHIEU_NGHIA_TRONG_CUM")

    if any(len(meaning) > 100 for meaning in meanings):
        reasons.append("NGHIA_DAI")

    if "||" in clean_text(
        row.get("NghiaThamChieu")
    ):
        reasons.append("NHIEU_NHOM_NGHIA")

    if "LT:" in clean_text(
        row.get("NghiaTiengVietDeXuat")
    ).upper():
        reasons.append("CON_CHU_THICH_LT")

    if clean_text(
        row.get("TrangThai")
    ) == "CAN_KIEM_TRA_TRUNG":
        reasons.append("TRUNG_MO_HO")

    return reasons


# =====================================================
# 4. DOC FILE CSV
# =====================================================

def read_rows(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        required = {
            "MaTuHSK",
            "MaMucNoiBo",
            "ChuHan",
            "PhienAm",
            "TuLoaiNguon",
            "NghiaThamChieu",
            "NghiaTiengVietDeXuat",
            "GhiChuLuongTu",
            "MaTuVungDaCo",
            "TrangThai",
            "VanDeCanKiemTra",
        }

        missing = required - set(
            reader.fieldnames or []
        )

        if missing:
            raise ValueError(
                "Thieu cot CSV: "
                + ", ".join(sorted(missing))
            )

        return list(reader)


# =====================================================
# 5. GHI CSV
# =====================================================

def write_rows(path, rows):
    with path.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS,
            extrasaction="ignore"
        )

        writer.writeheader()
        writer.writerows(rows)


# =====================================================
# 6. CHUAN BI NGHIA TIENG VIET
# =====================================================

def main():
    print("=" * 60)
    print("BUOC 3 - CHUAN BI NGHIA TIENG VIET HSK2")
    print("KHONG GHI VAO SQL SERVER")
    print("=" * 60)

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    source_rows = read_rows(INPUT_FILE)

    if len(source_rows) != EXPECTED_TOTAL:
        raise ValueError(
            f"Du kien {EXPECTED_TOTAL} tu, "
            f"nhung co {len(source_rows)} dong."
        )

    all_rows = []
    review_rows = []
    counters = Counter()
    seen_codes = set()

    for source in source_rows:

        code = clean_text(
            source["MaMucNoiBo"]
        )

        if not re.fullmatch(r"L2-\d+", code):
            raise ValueError(
                f"Ma tu HSK2 khong hop le: {code}"
            )

        if code in seen_codes:
            raise ValueError(
                f"Trung ma tu HSK2: {code}"
            )

        seen_codes.add(code)

        meaning = clean_text(
            source["NghiaTiengVietDeXuat"]
        )

        meanings = split_meanings(meaning)

        reasons = detect_review_reasons(
            source,
            meanings
        )

        previous_issues = clean_text(
            source["VanDeCanKiemTra"]
        )

        if previous_issues:
            reasons.append(
                "CO_CANH_BAO_TU_BUOC_2"
            )

        # Khong tu dong phe duyet bat ky tu nao.
        # Cot NghiaHocHSK2 de trong de chon
        # nghia phu hop voi nguoi hoc.

        row = {
            "MaTuHSK": clean_text(
                source["MaTuHSK"]
            ),
            "MaMucNoiBo": code,
            "ChuHan": clean_text(
                source["ChuHan"]
            ),
            "PhienAm": clean_text(
                source["PhienAm"]
            ),
            "TuLoaiNguon": clean_text(
                source["TuLoaiNguon"]
            ),
            "NghiaThamChieu": clean_text(
                source["NghiaThamChieu"]
            ),
            "NghiaTiengVietDeXuat": meaning,
            "DanhSachNghia": " | ".join(meanings),
            "NghiaHocHSK2": "",
            "GhiChuLuongTu": clean_text(
                source["GhiChuLuongTu"]
            ),
            "MaTuVungDaCo": clean_text(
                source["MaTuVungDaCo"]
            ),
            "TrangThai": clean_text(
                source["TrangThai"]
            ),
            "VanDeCanKiemTra": (
                "; ".join(dict.fromkeys(reasons))
            ),
            "TrangThaiKiemDuyet": "CHUA_DUYET",
        }

        all_rows.append(row)

        counters[row["TrangThai"]] += 1

        for reason in set(reasons):
            counters[reason] += 1

        # Chua duyet nghia nao, nen dua tat ca
        # 772 tu vao file kiem duyet.
        review_rows.append(row)

    if len(all_rows) != EXPECTED_TOTAL:
        raise RuntimeError(
            "So luong tu sau xu ly khong khop."
        )

    # Bao ve ket qua duyet thu cong:
    # khong ghi de file neu da ton tai.
    for path in (OUTPUT_FILE, REVIEW_FILE):
        if path.exists():
            raise FileExistsError(
                f"File da ton tai: {path}\n"
                "Khong tu dong ghi de de tranh mat "
                "du lieu da chinh sua."
            )

    write_rows(OUTPUT_FILE, all_rows)
    write_rows(REVIEW_FILE, review_rows)

    print()
    print(f"Tong so tu: {len(all_rows)}")
    print(f"Can kiem duyet: {len(review_rows)}")

    print()
    print("PHAN LOAI:")
    print(
        "  DA_CO:",
        counters["DA_CO"]
    )
    print(
        "  CHUA_CO:",
        counters["CHUA_CO"]
    )

    print()
    print("CAC CANH BAO:")

    for key, count in sorted(counters.items()):
        if key not in {"DA_CO", "CHUA_CO"}:
            print(f"  {key}: {count}")

    print()
    print("DA TAO:")
    print(OUTPUT_FILE)
    print(REVIEW_FILE)

    print()
    print("CHUA INSERT/UPDATE/DELETE SQL.")
    print("CHUA CO NGHIA NAO DUOC TU DONG DUYET.")


if __name__ == "__main__":
    main()
