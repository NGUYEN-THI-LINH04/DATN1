# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import re
import fitz

# ==========================================
# MOC HAN - FIX DOC PHAN 2 VA 3 - DE 8
# H11008 - CHI SUA CAU 26 DEN 35
# ==========================================

ROOT = Path(r"D:\DATN1")

PDF_PATH = (
    ROOT
    / "scripts/luyen_thi/source/De_HSK/HSK1/H11008.pdf"
)

OUTPUT_DIR = (
    ROOT
    / "scripts/luyen_thi/hsk1/output/de_08/questions"
)

BACKUP_DIR = (
    ROOT
    / "scripts/luyen_thi/hsk1/output/de_08/backup_doc_26_35"
)

# PDF page numbers start at 1
GROUPS = {
    8: [26, 27, 28, 29, 30],
    9: [31, 32, 33, 34, 35],
}


# ==========================================
# 1. TIM VI TRI SO CAU TREN PDF
# ==========================================

def find_question_positions(page, numbers):
    positions = {}

    for item in page.get_text("words"):
        x0, y0, x1, y1, raw = item[:5]

        word = str(raw).strip().replace("．", ".")
        word = word.rstrip(".")

        if not re.fullmatch(r"\d+", word):
            continue

        number = int(word)

        if number not in numbers:
            continue

        # Bo so cau trong tieu de va footer
        if not (65 <= x0 <= 180):
            continue

        if not (155 <= y0 <= 765):
            continue

        candidate = {
            "x": x0,
            "y": y0,
            "bottom": y1,
        }

        if number not in positions:
            positions[number] = candidate
        else:
            # Uu tien so cau nam gan cot x=90
            old = positions[number]

            if abs(x0 - 90) < abs(old["x"] - 90):
                positions[number] = candidate

    missing = [
        number
        for number in numbers
        if number not in positions
    ]

    if missing:
        raise RuntimeError(
            f"Khong tim thay so cau {missing} "
            f"tren trang PDF."
        )

    return positions


# ==========================================
# 2. TIM GIOI HAN PHAN DAP AN BEN PHAI
# ==========================================

def find_question_right_edge(page, positions):
    """
    Tim vi tri cac nhan dap an A-F o cot phai.
    Cat anh ngay truoc cot dap an.

    Neu khong tim thay, su dung moc du phong.
    """

    ys = [item["y"] for item in positions.values()]

    low = min(ys) - 30
    high = max(ys) + 75

    answer_x = []

    for item in page.get_text("words"):
        x0, y0, x1, y1, raw = item[:5]

        value = str(raw).strip().rstrip(".")

        if value not in {"A", "B", "C", "D", "E", "F"}:
            continue

        if not (295 <= x0 <= 530):
            continue

        if not (low <= y0 <= high):
            continue

        answer_x.append(x0)

    if answer_x:
        first_answer_x = min(answer_x)

        # Giu o tick, bo nhan va noi dung dap an
        right = first_answer_x - 12

        right = max(305, min(445, right))

        print(
            "Vi tri cot dap an: "
            f"x={first_answer_x:.1f}"
        )
    else:
        right = 350

        print(
            "Khong phat hien nhan A-F; "
            "dung gioi han du phong x=350."
        )

    return right


# ==========================================
# 3. TAO TOA DO CAT THEO TUNG CAU
# ==========================================

def build_crops(doc):
    crops = {}

    for page_number, numbers in GROUPS.items():
        page = doc[page_number - 1]

        positions = find_question_positions(
            page,
            numbers
        )

        print(
            f"\n===== TRANG PDF {page_number} ====="
        )

        for number in numbers:
            pos = positions[number]
            print(
                f"Cau {number}: "
                f"y={pos['y']:.1f}"
            )

        if page_number == 8:
            # Doc phan 2: lay ca cau va o tick
            left = 72
            right = 535

            # Khoang cach cac dong rat gan nhau
            offset = 18

        else:
            # Doc phan 3: bo cot dap an ben phai
            left = 72
            right = find_question_right_edge(
                page,
                positions
            )

            offset = 22

        for index, number in enumerate(numbers):
            y = positions[number]["y"]

            top = max(
                150,
                y - offset
            )

            if index < len(numbers) - 1:
                next_number = numbers[index + 1]
                next_y = positions[next_number]["y"]

                bottom = next_y - offset

            else:
                if page_number == 8:
                    bottom = y + 19
                else:
                    bottom = y + 70

                bottom = min(
                    bottom,
                    page.rect.height - 35
                )

            rect = fitz.Rect(
                left,
                top,
                right,
                bottom
            )

            if rect.is_empty:
                raise RuntimeError(
                    f"Toa do cau {number} khong hop le."
                )

            crops[number] = (
                page_number,
                rect
            )

    return crops


# ==========================================
# 4. SAO LUU VA CAT ANH
# ==========================================

def main():
    print("=" * 60)
    print("MOC HAN - SUA DOC 26-35 - HSK1 DE 8")
    print("=" * 60)

    if not PDF_PATH.is_file():
        raise FileNotFoundError(PDF_PATH)

    if not OUTPUT_DIR.is_dir():
        raise FileNotFoundError(OUTPUT_DIR)

    # Kiem tra du 10 anh truoc khi ghi de
    for number in range(26, 36):
        output_file = (
            OUTPUT_DIR / f"cau_{number:02d}.png"
        )

        if not output_file.is_file():
            raise FileNotFoundError(
                f"Thieu anh: {output_file}"
            )

    with fitz.open(PDF_PATH) as doc:
        # Tim tat ca toa do truoc khi sua anh
        crops = build_crops(doc)

        BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            "\n========== SAO LUU ANH CU =========="
        )

        for number in range(26, 36):
            name = f"cau_{number:02d}.png"

            old_file = OUTPUT_DIR / name
            backup_file = BACKUP_DIR / name

            if not backup_file.exists():
                shutil.copy2(
                    old_file,
                    backup_file
                )

            print(f"Da sao luu: {name}")

        print(
            "\n========== CAT LAI ANH =========="
        )

        for number in range(26, 36):
            page_number, rect = crops[number]

            page = doc[page_number - 1]

            pix = page.get_pixmap(
                matrix=fitz.Matrix(3, 3),
                clip=rect,
                alpha=False
            )

            output_file = (
                OUTPUT_DIR
                / f"cau_{number:02d}.png"
            )

            pix.save(str(output_file))

            print(
                f"Cau {number}: "
                f"trang {page_number}, "
                f"rect={tuple(round(v, 1) for v in rect)}"
            )

    print(
        "\n========== HOAN THANH =========="
    )

    print("Da cat lai 10 cau: 26-35")
    print(f"Anh: {OUTPUT_DIR}")
    print(f"Backup: {BACKUP_DIR}")
    print("Khong thay doi SQL Server.")
    print("Khong thay doi cac cau khac.")


if __name__ == "__main__":
    main()
