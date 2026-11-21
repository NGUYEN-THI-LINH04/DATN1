
from pathlib import Path
from collections import Counter
import csv
import re


# ==================================================
# 1. DUONG DAN
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "vocabulary_hsk2_review.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_FILE = (
    OUTPUT_DIR / "vocabulary_hsk2_clean.csv"
)

NEED_REVIEW_FILE = (
    OUTPUT_DIR / "vocabulary_hsk2_need_review.csv"
)

EXPECTED_TOTAL = 772


# ==================================================
# 2. CAC HAM CHUAN HOA
# ==================================================

def normalize_space(value):
    if value is None:
        return ""

    value = str(value).replace("\u00a0", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_hanzi(value):
    # Khong thay doi chu Han de tranh mat du lieu
    return normalize_space(value)


def normalize_pinyin(value):
    # Giu nguyen dau thanh va cach viet cua nguon
    return normalize_space(value)


def split_meaning_and_notes(raw_meaning):
    """
    Tach ghi chu LT:... neu la mot phan
    doc lap sau dau / hoac ||.

    Khong cat cac nghia khac.
    Khong tu dong chon nghia dau tien.
    """

    original = normalize_space(raw_meaning)

    if not original:
        return "", ""

    # Tach cac thanh phan theo dau phan cach
    parts = re.split(r"\s*(?:/|\|\|)\s*", original)

    meanings = []
    notes = []

    for part in parts:
        part = normalize_space(part)

        if not part:
            continue

        if re.match(r"^LT\s*:", part, re.IGNORECASE):
            notes.append(part)
        else:
            meanings.append(part)

    return " / ".join(meanings), " / ".join(notes)


def detect_issues(row):
    issues = []

    hanzi = row["ChuHan"]
    pinyin = row["PhienAm"]
    meaning = row["NghiaTiengVietDeXuat"]
    original = row["NghiaThamChieu"]

    if not hanzi:
        issues.append("THIEU_CHU_HAN")

    if not pinyin:
        issues.append("THIEU_PINYIN")

    if not meaning:
        issues.append("THIEU_NGHIA")

    if "\ufffd" in original or "\ufffd" in meaning:
        issues.append("KY_TU_LOI")

    if "LT:" in meaning.upper():
        issues.append("CON_CHU_THICH_LT")

    if "||" in original:
        issues.append("NHIEU_NHOM_NGHIA")

    if " / " in meaning or ";" in meaning:
        issues.append("NHIEU_NGHIA")

    if row["TrangThai"] == "CAN_KIEM_TRA_TRUNG":
        issues.append("TRUNG_MO_HO")

    return issues


# ==================================================
# 3. DOC CSV
# ==================================================

def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Khong tim thay file:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        required_columns = {
            "MaTuHSK",
            "MaMucNoiBo",
            "SoThuTuNguon",
            "ChuHan",
            "PhienAm",
            "TuLoaiNguon",
            "NghiaThamChieu",
            "NghiaTiengVietDeXuat",
            "MaTuVungDaCo",
            "TrangThai",
            "DaKiemTraNghia",
        }

        actual_columns = set(reader.fieldnames or [])

        missing_columns = required_columns - actual_columns

        if missing_columns:
            raise ValueError(
                "CSV thieu cot: "
                + ", ".join(sorted(missing_columns))
            )

        return list(reader)


# ==================================================
# 4. GHI CSV
# ==================================================

FIELDNAMES = [
    "MaTuHSK",
    "MaMucNoiBo",
    "SoThuTuNguon",
    "ChuHan",
    "PhienAm",
    "TuLoaiNguon",
    "NghiaThamChieu",
    "NghiaTiengVietDeXuat",
    "GhiChuLuongTu",
    "MaTuVungDaCo",
    "TrangThai",
    "VanDeCanKiemTra",
    "DaKiemTraNghia",
]


def write_csv(path, rows):
    with path.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES,
            extrasaction="ignore"
        )

        writer.writeheader()
        writer.writerows(rows)


# ==================================================
# 5. XU LY DU LIEU HSK2
# ==================================================

def main():
    print("=" * 60)
    print("BUOC 2 - CHUAN HOA TU VUNG HSK2")
    print("KHONG GHI DU LIEU VAO SQL SERVER")
    print("=" * 60)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    source_rows = read_csv(INPUT_FILE)

    if len(source_rows) != EXPECTED_TOTAL:
        raise ValueError(
            f"Du kien {EXPECTED_TOTAL} tu, "
            f"nhung CSV co {len(source_rows)} dong. "
            "Dung lai de kiem tra."
        )

    # Kiem tra trung ma nguon
    codes = [
        normalize_space(row["MaMucNoiBo"])
        for row in source_rows
    ]

    if len(codes) != len(set(codes)):
        raise ValueError(
            "Phat hien MaMucNoiBo trung nhau."
        )

    cleaned_rows = []
    need_review_rows = []

    status_counter = Counter()
    issue_counter = Counter()

    for source in source_rows:

        code = normalize_space(
            source["MaMucNoiBo"]
        )

        if not re.fullmatch(r"L2-\d+", code):
            raise ValueError(
                f"Ma HSK2 khong hop le: {code}"
            )

        hanzi = normalize_hanzi(
            source["ChuHan"]
        )

        pinyin = normalize_pinyin(
            source["PhienAm"]
        )

        original_meaning = normalize_space(
            source["NghiaThamChieu"]
        )

        suggested_meaning = normalize_space(
            source["NghiaTiengVietDeXuat"]
        )

        # Neu da co nghia trong TuVung:
        # giu nguyen nghia da su dung.
        #
        # Neu chua co:
        # tach ghi chu LT khoi nghia tham chieu.
        # Day van la NGHIA DE XUAT,
        # chua phai nghia da duyet.

        if suggested_meaning:
            final_suggestion = suggested_meaning
            _, notes = split_meaning_and_notes(
                original_meaning
            )
        else:
            final_suggestion, notes = (
                split_meaning_and_notes(
                    original_meaning
                )
            )

        status = normalize_space(
            source["TrangThai"]
        )

        row = {
            "MaTuHSK": normalize_space(
                source["MaTuHSK"]
            ),
            "MaMucNoiBo": code,
            "SoThuTuNguon": normalize_space(
                source["SoThuTuNguon"]
            ),
            "ChuHan": hanzi,
            "PhienAm": pinyin,
            "TuLoaiNguon": normalize_space(
                source["TuLoaiNguon"]
            ),
            "NghiaThamChieu": original_meaning,
            "NghiaTiengVietDeXuat": final_suggestion,
            "GhiChuLuongTu": notes,
            "MaTuVungDaCo": normalize_space(
                source["MaTuVungDaCo"]
            ),
            "TrangThai": status,
            "VanDeCanKiemTra": "",
            "DaKiemTraNghia": "CHUA",
        }

        issues = detect_issues(row)

        # Moi nghia lay tu nguon tham chieu
        # deu can duoc kiem duyet truoc import.
        #
        # Khong tu dong danh dau DA_DUYET.

        row["VanDeCanKiemTra"] = (
            "; ".join(issues)
        )

        cleaned_rows.append(row)
        status_counter[status] += 1

        for issue in issues:
            issue_counter[issue] += 1

        if status != "DA_CO" or issues:
            need_review_rows.append(row)

    # Kiem tra truoc khi xuat
    if len(cleaned_rows) != EXPECTED_TOTAL:
        raise RuntimeError(
            "So luong du lieu sau xu ly khong khop."
        )

    write_csv(
        OUTPUT_FILE,
        cleaned_rows
    )

    write_csv(
        NEED_REVIEW_FILE,
        need_review_rows
    )

    print()
    print(f"Tong so tu: {len(cleaned_rows)}")

    print()
    print("PHAN LOAI:")
    for status, count in sorted(
        status_counter.items()
    ):
        print(f"  {status}: {count}")

    print()
    print("CAC VAN DE CAN KIEM TRA:")

    if issue_counter:
        for issue, count in sorted(
            issue_counter.items()
        ):
            print(f"  {issue}: {count}")
    else:
        print("  Khong phat hien loi co ban")

    print()
    print("FILE DA TAO:")
    print(OUTPUT_FILE)
    print(NEED_REVIEW_FILE)

    print()
    print("LUU Y:")
    print("- Chua import vao SQL.")
    print("- Nghia tieng Viet chua duoc duyet.")
    print("- Giu nguyen nghia tham chieu.")
    print("- Khong sua du lieu HSK1.")
    print("- Khong tu dong xoa nghia nhieu cach dung.")


if __name__ == "__main__":
    main()
