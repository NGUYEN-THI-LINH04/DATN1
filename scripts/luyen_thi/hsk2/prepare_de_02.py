# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 2 - H20902

BUOC 1:
- Lay 60 dap an tu PDF.
- Tach anh 10 cau nghe dau tien.
- Tao HTML kiem tra.

Chua tach cau 11-60.
Chua thay doi SQL Server.
"""

from pathlib import Path
import json
import re
import unicodedata
import fitz


# ======================================================
# 1. DUONG DAN
# ======================================================

ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

SOURCE = ROOT / "source" / "De_HSK" / "HSK2"

PDF_FILE = SOURCE / "Đề HSK 2 số 2.pdf"

MP3_FILE = SOURCE / "Đề HSK 2 số 2 file nghe.mp3"

DATA = ROOT / "hsk2" / "data" / "de_02"

OUTPUT = ROOT / "hsk2" / "output" / "de_02"

QUESTIONS = OUTPUT / "questions"

ANSWER_JSON = DATA / "de_02_dap_an.json"

PREVIEW_HTML = OUTPUT / "kiem_tra_10_cau.html"


# ======================================================
# 2. LAY DAP AN
# ======================================================

def extract_answers(page):

    text = unicodedata.normalize(
        "NFKC",
        page.get_text("text")
    )

    if "H20902" not in text or "答案" not in text:
        raise RuntimeError(
            "Trang 18 khong phai dap an H20902."
        )

    pattern = re.compile(
        r"(?<!\d)(\d{1,2})\s*[.、]\s*([A-F√×])"
    )

    answers = {}

    for match in pattern.finditer(text):

        number = int(match.group(1))
        answer = match.group(2)

        if not 1 <= number <= 60:
            continue

        if number in answers:
            raise RuntimeError(
                f"Trung dap an cau {number}"
            )

        answers[number] = answer

    missing = [
        n for n in range(1, 61)
        if n not in answers
    ]

    if missing:
        raise RuntimeError(
            f"Thieu dap an: {missing}"
        )

    for number, answer in answers.items():

        if number <= 10 or 46 <= number <= 50:
            allowed = set("√×")

        elif 21 <= number <= 35:
            allowed = set("ABC")

        elif 16 <= number <= 20 or 56 <= number <= 60:
            allowed = set("ABCDE")

        else:
            allowed = set("ABCDEF")

        if answer not in allowed:
            raise RuntimeError(
                f"Dap an cau {number} sai dang: {answer}"
            )

    return answers


# ======================================================
# 3. TIM VI TRI CAU 1-10
# ======================================================

def parse_number(text):

    text = unicodedata.normalize(
        "NFKC",
        str(text)
    ).strip()

    match = re.match(
        r"^(\d{1,2})(?=[.、):：]|$)",
        text
    )

    return int(match.group(1)) if match else None


def get_question_positions(page, numbers):

    result = {}

    for word in page.get_text("words"):

        x0, y0, x1, y1, raw = word[:5]

        number = parse_number(raw)

        if number not in numbers:
            continue

        if x0 > page.rect.width * 0.3:
            continue

        if not (
            25 < y0 < page.rect.height - 35
        ):
            continue

        if number not in result:
            result[number] = (x0, y0, x1, y1)

    missing = [
        number for number in numbers
        if number not in result
    ]

    if missing:
        raise RuntimeError(
            f"Khong nhan dien du so cau: {missing}"
        )

    return result


# ======================================================
# 4. TIM DUONG KE CUA BANG HINH
# ======================================================

def get_horizontal_lines(page):

    lines = []
    min_width = page.rect.width * 0.45

    for drawing in page.get_drawings():

        for item in drawing.get("items", []):

            if item[0] == "l":

                p1, p2 = item[1], item[2]

                if abs(p1.y - p2.y) > 1.5:
                    continue

                if abs(p1.x - p2.x) < min_width:
                    continue

                lines.append((p1.y + p2.y) / 2)

            elif item[0] == "re":

                rect = item[1]

                if rect.width >= min_width:
                    lines.extend([rect.y0, rect.y1])

    return sorted(set(round(y, 2) for y in lines))


# ======================================================
# 5. XAC DINH VUNG CAT
# ======================================================

def get_crop_rect(page, numbers, positions, index):

    number = numbers[index]
    y = positions[number][1]

    lines = get_horizontal_lines(page)

    above = [
        line for line in lines
        if line < y - 7
    ]

    below = [
        line for line in lines
        if line > y + 7
    ]

    top = None
    bottom = None

    # Uu tien duong ke bang trong PDF.
    if above and below:

        candidate_top = max(above)
        candidate_bottom = min(below)

        height = candidate_bottom - candidate_top

        if 40 <= height <= 180:
            top = candidate_top + 2
            bottom = candidate_bottom - 2

    # Du phong neu PDF khong co duong ke vector.
    if top is None:

        ys = [
            positions[n][1]
            for n in numbers
        ]

        if index == 0:
            step = ys[1] - ys[0]
            top = y - step / 2
        else:
            top = (ys[index - 1] + y) / 2

        if index == len(numbers) - 1:
            step = y - ys[index - 1]
            bottom = y + step / 2
        else:
            bottom = (y + ys[index + 1]) / 2

    rect = fitz.Rect(
        page.rect.width * 0.02,
        max(10, top),
        page.rect.width * 0.98,
        min(page.rect.height - 25, bottom)
    )

    if rect.height < 30:
        raise RuntimeError(
            f"Vung cat cau {number} qua nho."
        )

    return rect


# ======================================================
# 6. HTML KIEM TRA
# ======================================================

def create_preview():

    parts = [
        """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>HSK2 - De 2 - Kiem tra 10 cau</title>

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    padding: 24px;
    font-family: Arial, sans-serif;
    background: #f5f7fb;
    color: #24344c;
}

main {
    max-width: 1000px;
    margin: auto;
}

h1 {
    font-size: 24px;
}

.subtitle {
    color: #64748b;
    margin-bottom: 22px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}

.card {
    background: white;
    border: 1px solid #dce5f1;
    border-radius: 12px;
    padding: 16px;
}

.card h2 {
    color: #2056a3;
    margin: 0 0 12px;
    font-size: 17px;
}

.card img {
    display: block;
    width: 100%;
    height: auto;
}

@media(max-width:650px) {
    .grid {
        grid-template-columns: 1fr;
    }
    body { padding: 12px; }
}
</style>
</head>

<body>
<main>
<h1>HSK2 – Đề 2 (H20902)</h1>
<p class="subtitle">
Kiểm tra hình ảnh câu 1–10.
Không hiển thị đáp án.
</p>

<div class="grid">
"""
    ]

    for number in range(1, 11):

        parts.append(
            '<div class="card">'
            f'<h2>Câu {number:02d}</h2>'
            f'<img src="questions/cau_{number:02d}.png" '
            f'alt="Câu {number}">'
            '</div>'
        )

    parts.append(
        "</div></main></body></html>"
    )

    PREVIEW_HTML.write_text(
        "\n".join(parts),
        encoding="utf-8"
    )


# ======================================================
# 7. MAIN
# ======================================================

def main():

    print("=" * 60)
    print("MOC HAN - CHUAN BI HSK2 DE 2")
    print("H20902")
    print("=" * 60)

    if not PDF_FILE.is_file():
        raise FileNotFoundError(PDF_FILE)

    if not MP3_FILE.is_file():
        raise FileNotFoundError(MP3_FILE)

    DATA.mkdir(parents=True, exist_ok=True)
    QUESTIONS.mkdir(parents=True, exist_ok=True)

    with fitz.open(PDF_FILE) as doc:

        print(f"\nPDF co {len(doc)} trang")

        if len(doc) != 18:
            raise RuntimeError(
                "PDF khong co 18 trang."
            )

        if "H20902" not in doc[0].get_text():
            raise RuntimeError(
                "Khong dung PDF H20902."
            )

        answers = extract_answers(doc[17])

        print("\n===== 60 DAP AN =====")

        for start in range(1, 61, 5):

            values = [
                answers[n]
                for n in range(start, start + 5)
            ]

            print(
                f"{start:02d}-{start+4:02d}: "
                + " ".join(values)
            )

        print("\n===== TACH ANH CAU 1-10 =====")

        for page_no, numbers in [
            (2, list(range(1, 6))),
            (3, list(range(6, 11))),
        ]:

            page = doc[page_no - 1]

            positions = get_question_positions(
                page,
                numbers
            )

            for index, number in enumerate(numbers):

                rect = get_crop_rect(
                    page,
                    numbers,
                    positions,
                    index
                )

                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2.5, 2.5),
                    clip=rect,
                    alpha=False
                )

                filename = f"cau_{number:02d}.png"

                pix.save(str(QUESTIONS / filename))

                print(
                    f"Cau {number:02d}: "
                    f"trang {page_no}, "
                    f"y={rect.y0:.1f}-{rect.y1:.1f}"
                )

    answer_data = {
        "cap_hsk": 2,
        "so_de": 2,
        "ma_de_goc": "H20902",
        "file_pdf": str(PDF_FILE),
        "file_mp3": str(MP3_FILE),
        "tong_cau": 60,
        "so_cau_nghe": 35,
        "so_cau_doc": 25,
        "trang_cau_hoi": list(range(2, 14)),
        "trang_bo_qua": [1, 14, 15, 16, 17],
        "trang_dap_an": 18,
        "dap_an": {
            str(n): answers[n]
            for n in range(1, 61)
        }
    }

    ANSWER_JSON.write_text(
        json.dumps(
            answer_data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    create_preview()

    print("\n" + "=" * 60)
    print("HOAN THANH BUOC 1")
    print("=" * 60)

    print("Ma de: H20902")
    print("HSK: 2")
    print("Dap an: 60/60")
    print("Anh cau hoi: 10/60")
    print("Trang cau hoi: 2-13")
    print("Trang 14-17: bo qua")
    print("Trang 18: chi lay dap an")

    print(f"\nJSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nChua tach cau 11-60.")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
