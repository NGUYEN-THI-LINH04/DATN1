from pathlib import Path
import csv
import io
import re
import urllib.request
import zipfile
import pyodbc


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_DIR / "hanzi_hsk2_enriched.csv"
OUTPUT_FILE = DATA_DIR / "hanzi_hsk2_unihan.csv"

UNIHAN_URL = (
    "https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip"
)

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=HocTiengTrungDB;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
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


def clean_text(value):
    if value is None:
        return ""

    text = str(value).replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


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
        return list(csv.DictReader(file))


def download_unihan():
    print("Dang tai Unihan.zip tu Unicode...")

    with urllib.request.urlopen(
        UNIHAN_URL,
        timeout=60
    ) as response:
        data = response.read()

    print(
        f"Da tai Unihan.zip: "
        f"{len(data):,} bytes"
    )

    return data


def parse_unihan(data):
    """
    Lay:
    - kRSUnicode -> so bo thu Kangxi
    - kTotalStrokes -> tong so net
    """

    radicals = {}
    strokes = {}

    with zipfile.ZipFile(
        io.BytesIO(data)
    ) as archive:

        filename = "Unihan_IRGSources.txt"

        if filename not in archive.namelist():
            raise RuntimeError(
                f"Khong tim thay {filename}"
            )

        with archive.open(filename) as file:

            for raw_line in file:

                line = raw_line.decode(
                    "utf-8"
                ).strip()

                if (
                    not line
                    or line.startswith("#")
                ):
                    continue

                parts = line.split("\t")

                if len(parts) != 3:
                    continue

                codepoint = parts[0]
                field = parts[1]
                value = parts[2]

                if not codepoint.startswith(
                    "U+"
                ):
                    continue

                try:
                    char = chr(
                        int(
                            codepoint[2:],
                            16
                        )
                    )
                except ValueError:
                    continue

                if field == "kTotalStrokes":
                    # Co the co nhieu gia tri.
                    # Lay gia tri dau tien.
                    first = value.split()[0]

                    try:
                        strokes[char] = int(
                            first
                        )
                    except ValueError:
                        pass

                elif field == "kRSUnicode":
                    # Dang thuong gap:
                    # 85.5
                    # 85'.5
                    # 85.5 140.3
                    #
                    # Lay radical dau tien.

                    first = value.split()[0]

                    match = re.match(
                        r"^(\d+)",
                        first
                    )

                    if match:
                        radicals[char] = int(
                            match.group(1)
                        )

    return radicals, strokes


def load_radical_mapping(cursor):
    """
    Map SoBoThu Kangxi -> MaBoThu cua CSDL.
    """

    cursor.execute("""
        SELECT
            MaBoThu,
            SoBoThu,
            KyHieu,
            TenBoThu
        FROM dbo.BoThu
        ORDER BY SoBoThu;
    """)

    mapping = {}

    for row in cursor.fetchall():

        mapping[int(row.SoBoThu)] = {
            "MaBoThu":
                int(row.MaBoThu),

            "KyHieu":
                clean_text(row.KyHieu),

            "TenBoThu":
                clean_text(row.TenBoThu),
        }

    return mapping


def main():

    print("=" * 70)
    print("BUOC 8 - BO SUNG BO THU + SO NET CHU HAN HSK2")
    print("CHI DOC SQL - KHONG GHI SQL")
    print("=" * 70)

    rows = read_csv()

    if len(rows) != 299:
        raise ValueError(
            f"Du kien 299 chu, "
            f"nhung file co {len(rows)}."
        )

    unihan_data = download_unihan()

    radical_numbers, total_strokes = (
        parse_unihan(
            unihan_data
        )
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        radical_mapping = (
            load_radical_mapping(
                cursor
            )
        )

        output_rows = []

        missing_radical = 0
        missing_strokes = 0
        missing_meaning = 0

        for row in rows:

            char = clean_text(
                row["KyTu"]
            )

            # ==========================
            # SO NET
            # ==========================

            stroke_count = (
                total_strokes.get(
                    char
                )
            )

            if stroke_count is not None:
                row["SoNet"] = str(
                    stroke_count
                )

            # ==========================
            # BO THU
            # ==========================

            radical_no = (
                radical_numbers.get(
                    char
                )
            )

            radical_info = None

            if radical_no is not None:
                radical_info = (
                    radical_mapping.get(
                        radical_no
                    )
                )

            if radical_info:
                row["MaBoThu"] = str(
                    radical_info[
                        "MaBoThu"
                    ]
                )

            # ==========================
            # CACH GHI NHO
            # ==========================

            if (
                radical_info
                and not clean_text(
                    row["CachGhiNho"]
                )
            ):
                row["CachGhiNho"] = (
                    f"Nhận diện bộ "
                    f"{radical_info['KyHieu']} "
                    f"({radical_info['TenBoThu']}) "
                    f"trong chữ {char}; "
                    f"sau đó liên hệ toàn chữ "
                    f"với nghĩa để ghi nhớ mặt chữ."
                )

            # ==========================
            # CANH BAO
            # ==========================

            issues = []

            if not clean_text(
                row["Pinyin"]
            ):
                issues.append(
                    "THIEU_PINYIN"
                )

            if not clean_text(
                row["NghiaTiengViet"]
            ):
                issues.append(
                    "THIEU_NGHIA"
                )
                missing_meaning += 1

            if not clean_text(
                row["MaBoThu"]
            ):
                issues.append(
                    "THIEU_BO_THU"
                )
                missing_radical += 1

            if not clean_text(
                row["SoNet"]
            ):
                issues.append(
                    "THIEU_SO_NET"
                )
                missing_strokes += 1

            row["CanBoSung"] = (
                "; ".join(
                    issues
                )
            )

            # MaNguon:
            # de trong vi day la file draft.
            # Sau khi hoan thien moi gan
            # nguon tong hop.

            output_rows.append(
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
                output_rows
            )

        connection.rollback()

        print()
        print(
            f"Tong chu xu ly: "
            f"{len(output_rows)}"
        )

        print(
            f"Con thieu Pinyin: "
            f"{sum(1 for r in output_rows if not clean_text(r['Pinyin']))}"
        )

        print(
            f"Con thieu nghia Viet: "
            f"{missing_meaning}"
        )

        print(
            f"Con thieu bo thu: "
            f"{missing_radical}"
        )

        print(
            f"Con thieu so net: "
            f"{missing_strokes}"
        )

        print()
        print("Da tao:")
        print(OUTPUT_FILE)

        print()
        print(
            "CHUA GAN MaBaiHoc."
        )

        print(
            "CHUA INSERT/UPDATE/DELETE SQL."
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()