from pathlib import Path
import sys
import zipfile
import json


# =========================================================
# THU MUC GOC
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# THU MUC DU LIEU HANZI
# =========================================================
HANZI_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hanzi"
)


# =========================================================
# 17 CHU CUA HSK1 - BAI 1
# =========================================================
LESSON_CHARS = [
    "你",
    "好",
    "我",
    "是",
    "叫",
    "什",
    "么",
    "名",
    "字",
    "很",
    "高",
    "兴",
    "认",
    "识",
    "吗",
    "呢",
    "也",
]


# =========================================================
# TIM FILE ZIP MAKE ME A HANZI
#
# Khong hard-code ten zip.
# Script se tim file zip nao co graphics.txt.
# =========================================================
def find_makemeahanzi_zip():

    if not HANZI_DIR.exists():

        raise FileNotFoundError(
            "Khong tim thay thu muc:\n"
            f"{HANZI_DIR}"
        )

    zip_files = list(
        HANZI_DIR.glob("*.zip")
    )

    if not zip_files:

        raise FileNotFoundError(
            "Khong tim thay file ZIP "
            "trong data_sources/hanzi."
        )

    candidates = []

    for zip_path in zip_files:

        try:

            with zipfile.ZipFile(
                zip_path,
                "r",
            ) as archive:

                names = (
                    archive.namelist()
                )

                graphics_files = [
                    name
                    for name in names
                    if name.endswith(
                        "graphics.txt"
                    )
                ]

                if graphics_files:

                    candidates.append(
                        (
                            zip_path,
                            graphics_files[0],
                        )
                    )

        except zipfile.BadZipFile:
            continue

    if len(candidates) == 0:

        raise RuntimeError(
            "Khong tim thay ZIP nao "
            "co graphics.txt."
        )

    if len(candidates) > 1:

        print(
            "Tim thay nhieu ZIP co graphics.txt:"
        )

        for path, _ in candidates:

            print(
                "-",
                path,
            )

        raise RuntimeError(
            "Co nhieu nguon Make Me a Hanzi. "
            "Can chon dung file truoc."
        )

    return candidates[0]


# =========================================================
# DOC graphics.txt
#
# Moi dong du kien la 1 JSON object:
#
# {
#   "character": "...",
#   "strokes": [...],
#   "medians": [...]
# }
# =========================================================
def load_graphics(
    zip_path,
    graphics_filename,
):

    target_chars = set(
        LESSON_CHARS
    )

    result = {}

    total_valid = 0

    with zipfile.ZipFile(
        zip_path,
        "r",
    ) as archive:

        with archive.open(
            graphics_filename,
            "r",
        ) as raw_file:

            for line_number, raw_line in enumerate(
                raw_file,
                start=1,
            ):

                try:

                    line = (
                        raw_line
                        .decode("utf-8")
                        .strip()
                    )

                except UnicodeDecodeError:

                    continue

                if not line:
                    continue

                try:

                    item = json.loads(
                        line
                    )

                except json.JSONDecodeError:

                    raise RuntimeError(
                        "JSON loi tai dong "
                        f"{line_number} "
                        "cua graphics.txt."
                    )

                character = (
                    item.get(
                        "character"
                    )
                )

                if not character:
                    continue

                total_valid += 1

                if (
                    character
                    not in target_chars
                ):
                    continue

                result[
                    character
                ] = {
                    "strokes":
                        item.get(
                            "strokes"
                        ),

                    "medians":
                        item.get(
                            "medians"
                        ),
                }

    return result, total_valid


# =========================================================
# DOC 17 CHU TRONG SQL
# =========================================================
def load_lesson_chars_from_db(
    cursor,
):

    placeholders = ",".join(
        "?"
        for _ in LESSON_CHARS
    )

    sql = f"""
        SELECT
            MaChuHan,
            KyTu,
            SoNet,
            ThuTu
        FROM dbo.ChuHan
        WHERE MaBaiHoc = 1
          AND KyTu IN ({placeholders})
        ORDER BY ThuTu
    """

    cursor.execute(
        sql,
        LESSON_CHARS,
    )

    rows = cursor.fetchall()

    return {
        row.KyTu: {
            "MaChuHan":
                row.MaChuHan,

            "SoNet":
                row.SoNet,

            "ThuTu":
                row.ThuTu,
        }
        for row in rows
    }


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 80)
        print(
            "KIEM TRA MAKE ME A HANZI "
            "CHO HSK1 - BAI 1"
        )
        print("=" * 80)

        # -------------------------------------------------
        # 1. TIM FILE
        # -------------------------------------------------
        (
            zip_path,
            graphics_filename,
        ) = find_makemeahanzi_zip()

        print()
        print(
            "ZIP:"
        )

        print(
            zip_path
        )

        print()

        print(
            "graphics.txt:"
        )

        print(
            graphics_filename
        )

        # -------------------------------------------------
        # 2. DOC MAKE ME A HANZI
        # -------------------------------------------------
        graphics, total_valid = (
            load_graphics(
                zip_path,
                graphics_filename,
            )
        )

        print()
        print(
            "Tong entry graphics doc duoc:",
            total_valid,
        )

        # -------------------------------------------------
        # 3. DOC SQL
        # -------------------------------------------------
        conn = get_connection()

        cursor = conn.cursor()

        db_chars = (
            load_lesson_chars_from_db(
                cursor
            )
        )

        if len(db_chars) != 17:

            raise RuntimeError(
                "SQL khong co dung 17 ChuHan "
                f"cua Bai 1. Thuc te: "
                f"{len(db_chars)}"
            )

        # -------------------------------------------------
        # 4. KIEM TRA TUNG CHU
        # -------------------------------------------------
        errors = []

        valid_count = 0

        print()
        print("-" * 80)
        print(
            "KET QUA 17 CHU"
        )
        print("-" * 80)

        ordered_chars = sorted(
            db_chars.items(),
            key=lambda item:
                item[1]["ThuTu"],
        )

        for character, db_data in (
            ordered_chars
        ):

            source_data = (
                graphics.get(
                    character
                )
            )

            if source_data is None:

                errors.append(
                    f"{character}: "
                    "khong tim thay trong graphics.txt"
                )

                print(
                    f"{db_data['ThuTu']:02d}"
                    f" | {character}"
                    " | KHONG TIM THAY"
                )

                continue

            strokes = (
                source_data.get(
                    "strokes"
                )
            )

            medians = (
                source_data.get(
                    "medians"
                )
            )

            if not isinstance(
                strokes,
                list,
            ):

                errors.append(
                    f"{character}: strokes "
                    "khong phai danh sach"
                )

                continue

            if not isinstance(
                medians,
                list,
            ):

                errors.append(
                    f"{character}: medians "
                    "khong phai danh sach"
                )

                continue

            stroke_count = len(
                strokes
            )

            median_count = len(
                medians
            )

            db_stroke_count = (
                db_data["SoNet"]
            )

            status = "OK"

            if (
                stroke_count
                != db_stroke_count
            ):

                status = "LECH SO NET"

                errors.append(
                    f"{character}: "
                    f"Unihan/SQL={db_stroke_count}, "
                    f"MakeMeAHanzi={stroke_count}"
                )

            if (
                median_count
                != stroke_count
            ):

                status = (
                    "LECH STROKES/MEDIANS"
                )

                errors.append(
                    f"{character}: "
                    f"strokes={stroke_count}, "
                    f"medians={median_count}"
                )

            if status == "OK":
                valid_count += 1

            print(
                f"{db_data['ThuTu']:02d}"
                f" | {character}"
                f" | SQL={db_stroke_count}"
                f" | strokes={stroke_count}"
                f" | medians={median_count}"
                f" | {status}"
            )

        # -------------------------------------------------
        # 5. TONG KET
        # -------------------------------------------------
        print()
        print("=" * 80)
        print("TONG KET")
        print("=" * 80)

        print(
            "Tong ChuHan Bai 1:",
            len(db_chars),
        )

        print(
            "Tim thay trong Make Me a Hanzi:",
            sum(
                1
                for char in db_chars
                if char in graphics
            ),
        )

        print(
            "Khop hoan toan:",
            valid_count,
        )

        print(
            "So loi:",
            len(errors),
        )

        if errors:

            print()
            print(
                "CHI TIET LOI:"
            )

            for error in errors:

                print(
                    "-",
                    error,
                )

            print()
            print(
                "CHUA DUOC IMPORT NET CHU HAN."
            )

        else:

            print()
            print(
                "DU LIEU 17/17 CHU KHOP."
            )

            print(
                "CHUA INSERT DU LIEU NET VIET."
            )

        print()
        print("=" * 80)
        print("HOAN TAT")
        print("=" * 80)

        cursor.close()

    except Exception as e:

        print()
        print("=" * 80)
        print("THUC HIEN THAT BAI")
        print("=" * 80)

        print(
            "Loi:",
            e,
        )

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()