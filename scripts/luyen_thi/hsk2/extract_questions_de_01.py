# -*- coding: utf-8 -*-

"""
MOC HAN - TACH 60 CAU HSK2 DE 1
Ma de goc: H20901

Cau hoi: trang PDF 2-13
Loi thoai: trang 14-17 (bo qua)
Dap an: trang 18 (bo qua)

Output:
    60 anh cau hoi
    6 anh bang lua chon
    1 HTML kiem tra
    1 JSON manifest

Khong thay doi SQL Server.
"""

from pathlib import Path
import json
import re
import html
import unicodedata
import fitz


# ==========================================================
# 1. CAU HINH
# ==========================================================

ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

PDF_FILE = (
    ROOT
    / "source"
    / "De_HSK"
    / "HSK2"
    / "Đề HSK 2 số 1 file pdf.pdf"
)

DATA_DIR = ROOT / "hsk2" / "data" / "de_01"

OUTPUT_DIR = ROOT / "hsk2" / "output" / "de_01"

QUESTION_DIR = OUTPUT_DIR / "questions"

GROUP_DIR = OUTPUT_DIR / "groups"

HTML_FILE = OUTPUT_DIR / "kiem_tra_60_cau.html"

JSON_FILE = DATA_DIR / "hinh_60_cau_ung_vien.json"


# ==========================================================
# 2. SO CAU THEO TRANG PDF
# ==========================================================

PAGE_QUESTIONS = {
    2: list(range(1, 6)),
    3: list(range(6, 11)),
    4: list(range(11, 16)),
    5: list(range(16, 21)),
    6: list(range(21, 31)),
    7: list(range(31, 36)),
    8: list(range(36, 41)),
    9: list(range(41, 46)),
    10: [46, 47, 48],
    11: [49, 50],
    12: list(range(51, 56)),
    13: list(range(56, 61)),
}


# Bang lua chon chung
GROUPS = {
    "nghe_11_15": 4,
    "nghe_16_20": 5,
    "doc_36_40": 8,
    "doc_41_45": 9,
    "doc_51_55": 12,
    "doc_56_60": 13,
}


# ==========================================================
# 3. NHAN DIEN SO CAU
# ==========================================================

def parse_question_number(text):
    """
    Nhan dien:
        1.
        11．
        45．女：
        51．

    Chi lay so cau o dau chuoi.
    """

    value = unicodedata.normalize(
        "NFKC",
        str(text)
    ).strip()

    match = re.match(
        r"^(\d{1,2})(?=[.、):：]|$)",
        value
    )

    if not match:
        return None

    return int(match.group(1))


def valid_position(x, y, page):
    """
    So cau nam o le trai trang PDF.
    Bo so trong tieu de va footer.
    """

    return (
        0 <= x <= page.rect.width * 0.35
        and
        page.rect.height * 0.045
        <= y
        <= page.rect.height * 0.94
    )


def find_question_positions(page, numbers):
    """
    Tim toa do cua tung so cau.

    Co 2 cach:
    1. Doc PDF theo words
    2. Du phong doc theo text lines

    Neu khong du thi dung, khong cat sai anh.
    """

    candidates = {
        number: []
        for number in numbers
    }

    # ------------------------------------------------------
    # Cach 1: tim theo WORDS
    # ------------------------------------------------------

    for word in page.get_text("words"):

        x0, y0, x1, y1, raw = word[:5]

        number = parse_question_number(raw)

        if number not in candidates:
            continue

        if not valid_position(x0, y0, page):
            continue

        candidates[number].append(
            (x0, y0, x1, y1)
        )

    # ------------------------------------------------------
    # Cach 2: tim theo LINES neu con thieu
    # ------------------------------------------------------

    missing = [
        number
        for number in numbers
        if not candidates[number]
    ]

    if missing:

        data = page.get_text("dict")

        for block in data.get("blocks", []):

            if "lines" not in block:
                continue

            for line in block["lines"]:

                spans = line.get("spans", [])

                if not spans:
                    continue

                content = "".join(
                    span.get("text", "")
                    for span in spans
                ).strip()

                number = parse_question_number(content)

                if number not in missing:
                    continue

                x0, y0, x1, y1 = line["bbox"]

                if not valid_position(x0, y0, page):
                    continue

                candidates[number].append(
                    (x0, y0, x1, y1)
                )

    # ------------------------------------------------------
    # Chon vi tri
    # ------------------------------------------------------

    positions = {}

    for number in numbers:

        options = candidates[number]

        if not options:
            continue

        # Uu tien nhan so cau o le trai.
        selected = sorted(
            options,
            key=lambda item: (
                item[0],
                item[1]
            )
        )[0]

        positions[number] = selected

    missing = [
        number
        for number in numbers
        if number not in positions
    ]

    if missing:

        print("\nKHONG TIM THAY:", missing)

        print("\nCAC TU CHUA SO TREN TRANG:")

        for word in page.get_text("words"):

            raw = str(word[4])

            if re.search(r"\d", raw):
                print(
                    f"x={word[0]:.1f}, "
                    f"y={word[1]:.1f}, "
                    f"text={raw}"
                )

        raise RuntimeError(
            f"Khong tim thay so cau: {missing}"
        )

    return positions


# ==========================================================
# 4. TIM DUONG KE NGANG CUA BANG
# ==========================================================

def get_horizontal_lines(page):

    lines = []

    for drawing in page.get_drawings():

        for item in drawing.get("items", []):

            if not item:
                continue

            # Duong ke thang
            if item[0] == "l":

                p1 = item[1]
                p2 = item[2]

                if abs(p1.y - p2.y) > 1.5:
                    continue

                length = abs(p2.x - p1.x)

                if length < page.rect.width * 0.45:
                    continue

                lines.append(
                    (p1.y + p2.y) / 2
                )

            # Hinh chu nhat
            elif item[0] == "re":

                rect = item[1]

                if rect.width < page.rect.width * 0.45:
                    continue

                lines.append(rect.y0)
                lines.append(rect.y1)

    return sorted(
        set(round(y, 2) for y in lines)
    )


# ==========================================================
# 5. CAT CAU NGHE PHAN 1 (1-10)
# ==========================================================

def crop_listening_image(
    page,
    numbers,
    positions,
    index
):

    number = numbers[index]

    y = positions[number][1]

    lines = get_horizontal_lines(page)

    above = [
        line
        for line in lines
        if line < y - 7
    ]

    below = [
        line
        for line in lines
        if line > y + 7
    ]

    top = None
    bottom = None

    # Uu tien duong ke bang that
    if above and below:

        t = max(above)
        b = min(below)

        height = b - t

        if 40 <= height <= 190:
            top = t + 2
            bottom = b - 2

    # Neu khong co duong ke thi dung khoang cach
    # giua cac so cau.
    if top is None:

        ys = [
            positions[n][1]
            for n in numbers
        ]

        if index == 0:

            step = ys[1] - ys[0]
            top = y - step * 0.5

        else:

            prev_y = ys[index - 1]
            top = (prev_y + y) / 2

        if index == len(numbers) - 1:

            step = y - ys[index - 1]
            bottom = y + step * 0.5

        else:

            next_y = ys[index + 1]
            bottom = (y + next_y) / 2

    return fitz.Rect(
        8,
        max(8, top),
        page.rect.width * 0.72,
        min(
            page.rect.height - 25,
            bottom
        )
    )


# ==========================================================
# 6. CAT CAU DANG VAN BAN (11-60)
# ==========================================================

def crop_text_question(
    page,
    numbers,
    positions,
    index
):

    number = numbers[index]

    y = positions[number][1]

    # Lay ca dong Pinyin o phia tren
    top = y - 25

    if index < len(numbers) - 1:

        next_number = numbers[index + 1]

        next_y = positions[next_number][1]

        # Ket thuc truoc dong Pinyin cau sau
        bottom = next_y - 22

    else:

        # Cau cuoi trang co the co nhieu dong.
        words = [
            w
            for w in page.get_text("words")
            if (
                w[1] >= y - 3
                and
                w[1] < page.rect.height - 55
            )
        ]

        if words:
            last_y = max(w[3] for w in words)
        else:
            last_y = y + 20

        bottom = max(
            y + 35,
            last_y + 13
        )

    top = max(10, top)

    bottom = min(
        page.rect.height - 40,
        bottom
    )

    if bottom <= top + 12:
        raise RuntimeError(
            f"Toa do cau {number} khong hop le."
        )

    return fitz.Rect(
        12,
        top,
        page.rect.width - 12,
        bottom
    )


# ==========================================================
# 7. CAT BANG LUA CHON CHUNG
# ==========================================================

def crop_group(page, first_question_y):

    top = page.rect.height * 0.085

    # Tim dong "Vi du"
    examples = page.search_for("例如")

    example_y = [
        rect.y0
        for rect in examples
        if (
            top < rect.y0 < first_question_y
        )
    ]

    if example_y:

        bottom = min(example_y) - 12

    else:

        bottom = first_question_y - 35

    if bottom <= top + 40:
        raise RuntimeError(
            "Vung cat bang lua chon qua hep."
        )

    return fitz.Rect(
        12,
        top,
        page.rect.width - 12,
        bottom
    )


# ==========================================================
# 8. LUU ANH
# ==========================================================

def save_image(page, rect, output_file):

    rect = rect & page.rect

    if rect.is_empty:
        raise RuntimeError(
            f"Vung cat rong: {output_file}"
        )

    pix = page.get_pixmap(
        matrix=fitz.Matrix(2.5, 2.5),
        clip=rect,
        alpha=False
    )

    pix.save(str(output_file))


# ==========================================================
# 9. CAU TRUC HTML KIEM TRA
# ==========================================================

SECTIONS = [
    ("Nghe - Phan 1 (1-10)", 1, 10, None),

    (
        "Nghe - Phan 2 (11-15)",
        11, 15, "nghe_11_15"
    ),

    (
        "Nghe - Phan 2 (16-20)",
        16, 20, "nghe_16_20"
    ),

    ("Nghe - Phan 3 (21-30)", 21, 30, None),

    ("Nghe - Phan 4 (31-35)", 31, 35, None),

    (
        "Doc - Phan 1 (36-40)",
        36, 40, "doc_36_40"
    ),

    (
        "Doc - Phan 2 (41-45)",
        41, 45, "doc_41_45"
    ),

    ("Doc - Phan 3 (46-50)", 46, 50, None),

    (
        "Doc - Phan 4 (51-55)",
        51, 55, "doc_51_55"
    ),

    (
        "Doc - Phan 4 (56-60)",
        56, 60, "doc_56_60"
    ),
]


def create_html():

    parts = [
        """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>HSK2 - De 1 - Kiem tra 60 cau</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 24px;
    background: #f3f5f9;
    font-family: Arial, sans-serif;
    color: #26344a;
}

main {
    max-width: 1100px;
    margin: auto;
}

h1 {
    font-size: 24px;
}

h2 {
    margin-top: 30px;
    font-size: 19px;
}

.note {
    color: #526174;
    line-height: 1.6;
}

.grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}

.card,
.group {
    background: #fff;
    border: 1px solid #dbe2ef;
    border-radius: 10px;
    padding: 12px;
}

.card strong {
    display: block;
    margin-bottom: 10px;
    color: #1657a7;
}

.card img,
.group img {
    width: 100%;
    height: auto;
    display: block;
}

.group {
    max-width: 850px;
    margin: 12px 0 18px;
}

.group strong {
    display: block;
    margin-bottom: 10px;
}

@media(max-width:700px) {
    body { padding: 12px; }
    .grid { grid-template-columns: 1fr; }
}
</style>
</head>

<body>
<main>

<h1>HSK2 - De 1 (H20901)</h1>

<p class="note">
60 cau hoi, lay tu trang PDF 2-13.
Khong hien thi loi thoai va dap an.
</p>
"""
    ]

    for title, start, end, group in SECTIONS:

        parts.append(
            f"<h2>{html.escape(title)}</h2>"
        )

        if group:

            parts.append(
                '<div class="group">'
                '<strong>Bang lua chon chung</strong>'
                f'<img src="groups/{group}.png" '
                'alt="Bang lua chon">'
                '</div>'
            )

        parts.append('<div class="grid">')

        for number in range(start, end + 1):

            parts.append(
                '<div class="card">'
                f'<strong>Cau {number:02d}</strong>'
                f'<img src="questions/cau_{number:02d}.png" '
                f'alt="Cau {number}">'
                '</div>'
            )

        parts.append('</div>')

    parts.append('</main></body></html>')

    HTML_FILE.write_text(
        "\n".join(parts),
        encoding="utf-8"
    )


# ==========================================================
# 10. HAM MAIN
# ==========================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK2 DE 1 - H20901")
    print("TACH 60 CAU HOI")
    print("=" * 60)

    if not PDF_FILE.is_file():
        raise FileNotFoundError(PDF_FILE)

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    QUESTION_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    GROUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    manifest_questions = {}
    manifest_groups = {}

    page_positions = {}

    with fitz.open(PDF_FILE) as doc:

        if len(doc) != 18:
            raise RuntimeError(
                f"PDF co {len(doc)} trang, "
                "khac H20901 da kiem tra."
            )

        print("\n===== KIEM TRA VI TRI 60 CAU =====")

        # Tim du 60 cau truoc khi bat dau cat
        for page_number, numbers in PAGE_QUESTIONS.items():

            page = doc[page_number - 1]

            positions = find_question_positions(
                page,
                numbers
            )

            page_positions[page_number] = positions

            print(
                f"Trang {page_number:02d}: "
                f"{len(positions)}/{len(numbers)} cau"
            )

        all_numbers = sorted(
            number
            for numbers in PAGE_QUESTIONS.values()
            for number in numbers
        )

        if all_numbers != list(range(1, 61)):
            raise RuntimeError(
                "Danh sach cau khong du 1-60."
            )

        print("\n===== CAT 60 CAU =====")

        for page_number, numbers in PAGE_QUESTIONS.items():

            page = doc[page_number - 1]

            positions = page_positions[page_number]

            for index, number in enumerate(numbers):

                if number <= 10:

                    rect = crop_listening_image(
                        page,
                        numbers,
                        positions,
                        index
                    )

                else:

                    rect = crop_text_question(
                        page,
                        numbers,
                        positions,
                        index
                    )

                name = f"cau_{number:02d}.png"

                output = QUESTION_DIR / name

                save_image(
                    page,
                    rect,
                    output
                )

                manifest_questions[str(number)] = {
                    "trang_pdf": page_number,
                    "anh": f"questions/{name}",
                    "toa_do": [
                        round(value, 2)
                        for value in rect
                    ],
                }

                print(
                    f"Cau {number:02d}: "
                    f"trang {page_number}, "
                    f"y={rect.y0:.1f}-{rect.y1:.1f}"
                )

        print("\n===== CAT BANG LUA CHON =====")

        for group_name, page_number in GROUPS.items():

            page = doc[page_number - 1]

            first_number = PAGE_QUESTIONS[
                page_number
            ][0]

            first_y = page_positions[
                page_number
            ][first_number][1]

            rect = crop_group(
                page,
                first_y
            )

            filename = f"{group_name}.png"

            save_image(
                page,
                rect,
                GROUP_DIR / filename
            )

            manifest_groups[group_name] = {
                "trang_pdf": page_number,
                "anh": f"groups/{filename}",
                "toa_do": [
                    round(value, 2)
                    for value in rect
                ],
            }

            print(
                f"{group_name}: trang {page_number}"
            )

    # ------------------------------------------------------
    # LUU JSON
    # ------------------------------------------------------

    result = {
        "cap_hsk": 2,
        "so_de": 1,
        "ma_de_goc": "H20901",
        "tong_cau": 60,
        "nghe": 35,
        "doc": 25,
        "trang_cau_hoi": list(range(2, 14)),
        "trang_bo_qua": [1, 14, 15, 16, 17, 18],
        "cau_hoi": manifest_questions,
        "bang_lua_chon": manifest_groups,
    }

    JSON_FILE.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # ------------------------------------------------------
    # TAO HTML
    # ------------------------------------------------------

    create_html()

    print("\n" + "=" * 60)
    print("HOAN THANH")
    print("=" * 60)

    print(
        f"So anh cau hoi: {len(manifest_questions)}"
    )

    print(
        f"So bang lua chon: {len(manifest_groups)}"
    )

    print(f"HTML: {HTML_FILE}")
    print(f"JSON: {JSON_FILE}")

    print("\nChua thay doi SQL Server.")
    print("Chua duyet hoac xuat ban de.")


if __name__ == "__main__":
    main()
