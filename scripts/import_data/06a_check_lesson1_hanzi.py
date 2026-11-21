from pathlib import Path
import sys
import zipfile
import re


# =========================================================
# THU MUC GOC
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# FILE UNIHAN
# =========================================================
UNIHAN_ZIP = (
    ROOT_DIR
    / "data_sources"
    / "unicode"
    / "Unihan.zip"
)


# =========================================================
# 17 CHU HAN CUA HSK1 - BAI 1
#
# Pinyin o day la cach doc TRONG NGU CANH BAI HOC,
# khong phai tat ca am doc co the co cua tung chu.
# =========================================================
LESSON_CHARS = [
    ("你", "nǐ"),
    ("好", "hǎo"),
    ("我", "wǒ"),
    ("是", "shì"),
    ("叫", "jiào"),

    ("什", "shén"),
    ("么", "me"),
    ("名", "míng"),
    ("字", "zì"),
    ("很", "hěn"),

    ("高", "gāo"),
    ("兴", "xìng"),
    ("认", "rèn"),
    ("识", "shi"),
    ("吗", "ma"),

    ("呢", "ne"),
    ("也", "yě"),
]


# =========================================================
# CAC THUOC TINH UNIHAN CAN LAY
# =========================================================
TARGET_PROPERTIES = {
    "kRSUnicode",
    "kTotalStrokes",
}


# =========================================================
# PARSE U+XXXX -> KY TU
# =========================================================
def codepoint_to_char(value):

    value = value.strip()

    if not value.startswith("U+"):
        return None

    try:
        codepoint = int(
            value[2:],
            16,
        )
    except ValueError:
        return None

    return chr(codepoint)


# =========================================================
# LAY SO BO THU TU kRSUnicode
#
# Vi du:
#
# 9.5
# 149'.2
#
# -> 9
# -> 149
#
# Dau ' chi bieu thi dang bien the/gian hoa
# cua bo thu, nhung van thuoc bo chinh cung so.
# =========================================================
def parse_radical_number(value):

    if not value:
        return None

    # kRSUnicode co the co nhieu gia tri
    # cach nhau boi khoang trang.
    first_value = (
        value.strip()
        .split()[0]
    )

    match = re.match(
        r"^(\d+)'{0,3}\.",
        first_value,
    )

    if not match:
        return None

    return int(
        match.group(1)
    )


# =========================================================
# DOC UNIHAN
#
# Khong phu thuoc kRSUnicode/kTotalStrokes
# nam trong file nao.
# =========================================================
def load_unihan_properties():

    if not UNIHAN_ZIP.exists():

        raise FileNotFoundError(
            "Khong tim thay Unihan.zip:\n"
            f"{UNIHAN_ZIP}"
        )

    target_chars = {
        char
        for char, _
        in LESSON_CHARS
    }

    result = {
        char: {}
        for char in target_chars
    }

    with zipfile.ZipFile(
        UNIHAN_ZIP,
        "r",
    ) as archive:

        text_files = [
            name
            for name in archive.namelist()
            if (
                name.startswith("Unihan")
                and name.endswith(".txt")
            )
        ]

        if not text_files:
            raise RuntimeError(
                "Unihan.zip khong co file Unihan*.txt."
            )

        print(
            "So file Unihan se quet:",
            len(text_files),
        )

        for filename in text_files:

            with archive.open(
                filename,
                "r",
            ) as raw_file:

                for raw_line in raw_file:

                    try:
                        line = raw_line.decode(
                            "utf-8"
                        )
                    except UnicodeDecodeError:
                        continue

                    line = line.strip()

                    if (
                        not line
                        or line.startswith("#")
                    ):
                        continue

                    parts = line.split(
                        "\t"
                    )

                    if len(parts) < 3:
                        continue

                    codepoint = parts[0]
                    property_name = parts[1]
                    property_value = parts[2]

                    if (
                        property_name
                        not in TARGET_PROPERTIES
                    ):
                        continue

                    char = codepoint_to_char(
                        codepoint
                    )

                    if char not in target_chars:
                        continue

                    result[
                        char
                    ][
                        property_name
                    ] = property_value

    return result


# =========================================================
# DOC BO THU TU SQL
# =========================================================
def load_radicals_from_db(cursor):

    cursor.execute(
        """
        SELECT
            MaBoThu,
            KyHieu,
            TenBoThu,
            SoNet
        FROM dbo.BoThu
        ORDER BY MaBoThu
        """
    )

    result = {}

    for row in cursor.fetchall():

        result[
            row.MaBoThu
        ] = {
            "KyHieu": row.KyHieu,
            "TenBoThu": row.TenBoThu,
            "SoNet": row.SoNet,
        }

    return result


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 78)
        print(
            "KIEM TRA UNIHAN CHO HSK1 - BAI 1"
        )
        print("=" * 78)

        # -------------------------------------------------
        # 1. DOC UNIHAN
        # -------------------------------------------------
        properties = (
            load_unihan_properties()
        )

        # -------------------------------------------------
        # 2. DOC BO THU SQL
        # -------------------------------------------------
        conn = get_connection()
        cursor = conn.cursor()

        radicals = (
            load_radicals_from_db(
                cursor
            )
        )

        if len(radicals) != 214:

            raise RuntimeError(
                "Bang BoThu khong co dung 214 dong. "
                f"Thuc te: {len(radicals)}"
            )

        # -------------------------------------------------
        # 3. KIEM TRA TUNG CHU
        # -------------------------------------------------
        valid_rows = []

        errors = []

        print()
        print("-" * 78)
        print(
            "KET QUA 17 CHU"
        )
        print("-" * 78)

        for order, (
            char,
            lesson_pinyin,
        ) in enumerate(
            LESSON_CHARS,
            start=1,
        ):

            data = properties.get(
                char,
                {}
            )

            rs_value = data.get(
                "kRSUnicode"
            )

            total_strokes_text = data.get(
                "kTotalStrokes"
            )

            radical_number = (
                parse_radical_number(
                    rs_value
                )
            )

            if not rs_value:

                errors.append(
                    f"{char}: thieu kRSUnicode"
                )

                continue

            if not total_strokes_text:

                errors.append(
                    f"{char}: thieu kTotalStrokes"
                )

                continue

            if radical_number is None:

                errors.append(
                    f"{char}: khong parse duoc "
                    f"kRSUnicode={rs_value}"
                )

                continue

            radical = radicals.get(
                radical_number
            )

            if not radical:

                errors.append(
                    f"{char}: bo thu {radical_number} "
                    "khong co trong SQL"
                )

                continue

            try:

                total_strokes = int(
                    total_strokes_text
                )

            except ValueError:

                errors.append(
                    f"{char}: kTotalStrokes khong phai so: "
                    f"{total_strokes_text}"
                )

                continue

            valid_rows.append(
                {
                    "ThuTu": order,
                    "KyTu": char,
                    "Pinyin": lesson_pinyin,
                    "MaBoThu": radical_number,
                    "KyHieuBoThu":
                        radical["KyHieu"],
                    "TenBoThu":
                        radical["TenBoThu"],
                    "RSUnicode":
                        rs_value,
                    "SoNet":
                        total_strokes,
                }
            )

            print(
                f"{order:02d}"
                f" | {char}"
                f" | {lesson_pinyin:<6}"
                f" | Bo {radical_number:>3}"
                f" {radical['KyHieu']}"
                f" ({radical['TenBoThu']})"
                f" | kRSUnicode={rs_value}"
                f" | SoNet={total_strokes}"
            )

        # -------------------------------------------------
        # 4. TONG KET
        # -------------------------------------------------
        print()
        print("=" * 78)
        print("TONG KET")
        print("=" * 78)

        print(
            "Tong chu can kiem tra:",
            len(LESSON_CHARS),
        )

        print(
            "Hop le:",
            len(valid_rows),
        )

        print(
            "Loi:",
            len(errors),
        )

        if errors:

            print()
            print(
                "CAC LOI:"
            )

            for error in errors:

                print(
                    "-",
                    error,
                )

            raise RuntimeError(
                "Du lieu Unihan chua du "
                "cho 17 chu. CHUA DUOC INSERT ChuHan."
            )

        if len(valid_rows) != 17:

            raise RuntimeError(
                "Khong du 17 chu."
            )

        print()
        print(
            "DU 17/17 CHU."
        )

        print(
            "CHUA INSERT VAO dbo.ChuHan."
        )

        print()
        print("=" * 78)
        print("HOAN TAT")
        print("=" * 78)

        cursor.close()

    except Exception as e:

        print()
        print("=" * 78)
        print("THUC HIEN THAT BAI")
        print("=" * 78)

        print(
            "Loi:",
            e,
        )

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()