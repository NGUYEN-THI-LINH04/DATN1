from pathlib import Path
import csv


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_DIR / "hanzi_hsk2_unihan.csv"
OUTPUT_FILE = DATA_DIR / "hanzi_hsk2_missing_meanings.csv"


def clean_text(value):
    if value is None:
        return ""

    return str(value).strip()


def main():

    print("=" * 66)
    print("BUOC 9 - XUAT CHU HAN HSK2 CON THIEU NGHIA")
    print("=" * 66)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file:\n{INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames

    missing = []

    for row in rows:

        if not clean_text(
            row.get("NghiaTiengViet")
        ):
            missing.append(row)

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(missing)

    print()
    print(
        f"Tong chu trong file: "
        f"{len(rows)}"
    )

    print(
        f"Chu con thieu nghia: "
        f"{len(missing)}"
    )

    print()
    print("Da tao:")
    print(OUTPUT_FILE)

    print()
    print("KHONG GHI SQL.")


if __name__ == "__main__":
    main()