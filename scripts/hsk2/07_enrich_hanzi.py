from pathlib import Path
import csv
import re
import pyodbc


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_DIR / "hanzi_hsk2_draft.csv"
OUTPUT_FILE = DATA_DIR / "hanzi_hsk2_enriched.csv"

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=HocTiengTrungDB;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


def clean_text(value):
    if value is None:
        return ""

    value = str(value).replace("\u00a0", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def get_connection():
    return pyodbc.connect(
        CONNECTION_STRING,
        timeout=15,
        autocommit=False
    )


def read_csv():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file:\n{INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        return list(
            csv.DictReader(file)
        )


def load_hsk_words(cursor):
    """
    Lay tat ca tu HSK2 de tim cac tu co chua ky tu can bo sung.
    """

    cursor.execute("""
        SELECT
            ChuHan,
            PhienAm,
            NghiaTiengVietThamChieu
        FROM dbo.TuVungHSKChuan
        WHERE MaCapDo = 2
        ORDER BY MaTuHSK;
    """)

    result = []

    for row in cursor.fetchall():

        result.append({
            "ChuHan":
                clean_text(row.ChuHan),

            "PhienAm":
                clean_text(row.PhienAm),

            "Nghia":
                clean_text(
                    row.NghiaTiengVietThamChieu
                )
        })

    return result


def load_dictionary(cursor):
    """
    Lay cac muc tu don tu MucTuDien.
    """

    cursor.execute("""
        SELECT
            ChuHan,
            PhienAm,
            NghiaTiengViet,
            NghiaGoc
        FROM dbo.MucTuDien
        WHERE
            ChuHan IS NOT NULL
            AND LEN(ChuHan) = 1;
    """)

    result = {}

    for row in cursor.fetchall():

        char = clean_text(
            row.ChuHan
        )

        if not char:
            continue

        pinyin = clean_text(
            row.PhienAm
        )

        vietnamese = clean_text(
            row.NghiaTiengViet
        )

        original = clean_text(
            row.NghiaGoc
        )

        if char not in result:
            result[char] = {
                "Pinyin": pinyin,
                "NghiaTiengViet":
                    vietnamese,
                "NghiaGoc":
                    original
            }

        else:

            current = result[char]

            if (
                not current["Pinyin"]
                and pinyin
            ):
                current["Pinyin"] = (
                    pinyin
                )

            if (
                not current[
                    "NghiaTiengViet"
                ]
                and vietnamese
            ):
                current[
                    "NghiaTiengViet"
                ] = vietnamese

            if (
                not current[
                    "NghiaGoc"
                ]
                and original
            ):
                current[
                    "NghiaGoc"
                ] = original

    return result


def find_examples(char, words):
    """
    Tim toi da 5 tu HSK2 co chua chu nay.
    """

    matches = []

    for word in words:

        if char in word["ChuHan"]:

            matches.append(
                word
            )

            if len(matches) >= 5:
                break

    return matches


def choose_example(matches):

    if not matches:
        return "", "", ""

    # Uu tien tu ngan hon
    matches = sorted(
        matches,
        key=lambda x: len(
            x["ChuHan"]
        )
    )

    word = matches[0]

    return (
        word["ChuHan"],
        word["PhienAm"],
        word["Nghia"]
    )


FIELDS = [
    "MaChuHanTam",
    "MaBaiHoc",
    "MaBoThu",
    "KyTu",
    "Pinyin",
    "NghiaTiengViet",
    "SoNet",
    "CachGhiNho",
    "ViDuTiengTrung",
    "ViDuPinyin",
    "ViDuTiengViet",
    "MaTep",
    "MaNguon",
    "ThuTuTam",
    "TrangThai",
    "TuHSK2ChuaKyTu",
    "NguonPinyinNghia",
    "CanBoSung",
]


def main():

    print("=" * 68)
    print("BUOC 7 - BO SUNG DU LIEU CHU HAN HSK2")
    print("CHE DO: CHI DOC SQL - KHONG GHI SQL")
    print("=" * 68)

    rows = read_csv()

    if len(rows) != 299:
        print(
            "LUU Y: file hien co "
            f"{len(rows)} chu, khong phai 299."
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        words = load_hsk_words(
            cursor
        )

        dictionary = load_dictionary(
            cursor
        )

        enriched = []

        missing_pinyin = 0
        missing_meaning = 0

        for row in rows:

            char = clean_text(
                row["KyTu"]
            )

            pinyin = clean_text(
                row["Pinyin"]
            )

            meaning = clean_text(
                row["NghiaTiengViet"]
            )

            source = clean_text(
                row["NguonPinyinNghia"]
            )

            # ==========================
            # FALLBACK MucTuDien
            # ==========================

            if char in dictionary:

                item = dictionary[
                    char
                ]

                if not pinyin:
                    pinyin = clean_text(
                        item["Pinyin"]
                    )

                    if pinyin:
                        source = (
                            "MucTuDien"
                        )

                if not meaning:
                    meaning = clean_text(
                        item[
                            "NghiaTiengViet"
                        ]
                    )

                    if meaning:
                        source = (
                            "MucTuDien"
                        )

            # ==========================
            # TIM TU VI DU HSK2
            # ==========================

            examples = find_examples(
                char,
                words
            )

            (
                example_word,
                example_pinyin,
                example_meaning
            ) = choose_example(
                examples
            )

            # Khong cat pinyin cua tu ghep
            # thanh pinyin tung chu,
            # vi co the sai voi chu da am.

            if not pinyin:
                missing_pinyin += 1

            if not meaning:
                missing_meaning += 1

            issues = []

            if not pinyin:
                issues.append(
                    "THIEU_PINYIN"
                )

            if not meaning:
                issues.append(
                    "THIEU_NGHIA"
                )

            if not clean_text(
                row["MaBoThu"]
            ):
                issues.append(
                    "CHUA_BO_THU"
                )

            if not clean_text(
                row["SoNet"]
            ):
                issues.append(
                    "CHUA_SO_NET"
                )

            row["Pinyin"] = pinyin
            row[
                "NghiaTiengViet"
            ] = meaning

            row[
                "ViDuTiengTrung"
            ] = example_word

            row[
                "ViDuPinyin"
            ] = example_pinyin

            row[
                "ViDuTiengViet"
            ] = example_meaning

            row[
                "NguonPinyinNghia"
            ] = source

            row[
                "CanBoSung"
            ] = "; ".join(
                issues
            )

            enriched.append(
                row
            )

        with OUTPUT_FILE.open(
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=FIELDS
            )

            writer.writeheader()
            writer.writerows(
                enriched
            )

        connection.rollback()

        print()
        print(
            f"Tong chu HSK2 can chuan bi: "
            f"{len(enriched)}"
        )

        print(
            f"Con thieu Pinyin: "
            f"{missing_pinyin}"
        )

        print(
            f"Con thieu nghia Viet: "
            f"{missing_meaning}"
        )

        print()
        print("Da tao:")
        print(OUTPUT_FILE)

        print()
        print(
            "Van chua gan MaBaiHoc."
        )

        print(
            "Van chua ghi vao ChuHan."
        )

        print(
            "MaBoThu va SoNet se "
            "bo sung o buoc tiep."
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()