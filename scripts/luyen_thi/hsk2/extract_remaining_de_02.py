
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 2 (H20902)

BUOC 2:
- Giu nguyen 10 anh dau tien.
- Tach anh cau 11-60.
- Tao 6 bang lua chon chung.
- Tao HTML kiem tra 60 cau.
- Tao JSON thong tin anh.

Khong thay doi SQL Server.
Khong sua HSK1 va HSK2 De 1.
"""

from pathlib import Path
import json
import re
import html
import unicodedata

import fitz


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

PDF_FILE = (
    ROOT
    / "source"
    / "De_HSK"
    / "HSK2"
    / "Đề HSK 2 số 2.pdf"
)

DATA_DIR = ROOT / "hsk2" / "data" / "de_02"
OUTPUT_DIR = ROOT / "hsk2" / "output" / "de_02"

QUESTION_DIR = OUTPUT_DIR / "questions"
GROUP_DIR = OUTPUT_DIR / "groups"

ANSWER_FILE = DATA_DIR / "de_02_dap_an.json"

MANIFEST_FILE = (
    DATA_DIR / "hinh_60_cau_ung_vien.json"
)

HTML_FILE = (
    OUTPUT_DIR / "kiem_tra_60_cau.html"
)


# =====================================================
# 2. DANH SACH CAU HOI
# =====================================================

# Cau 1-10 da tach o buoc truoc.
# Chi xu ly tiep cau 11-60.

PAGE_QUESTIONS = {
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


# 6 bang lua chon chung.

GROUP_PAGES = {
    "nghe_11_15": 4,
    "nghe_16_20": 5,
    "doc_36_40": 8,
    "doc_41_45": 9,
    "doc_51_55": 12,
    "doc_56_60": 13,
}


# =====================================================
# 3. NHAN DIEN SO CAU
# =====================================================

def parse_number(value):
    """
    Nhan dien ca:
        11.
        21．
        45．女：
        51．
    """

    text = unicodedata.normalize(
        "NFKC",
        str(value)
    ).strip()

    match = re.match(
        r"^(\d{1,2})(?=[.、):：]|$)",
        text
    )

    if match:
        return int(match.group(1))

    return None


def find_positions(page, numbers):
    """
    Tim so cau trong PDF.
    Uu tien cot trai.
    """

    candidates = {
        number: []
        for number in numbers
    }

    # Tim theo words.
    for word in page.get_text("words"):

        x0, y0, x1, y1, raw = word[:5]

        number = parse_number(raw)

        if number not in candidates:
            continue

        if x0 > page.rect.width * 0.35:
            continue

        if not (
            page.rect.height * 0.05
            < y0
            < page.rect.height * 0.94
        ):
            continue

        candidates[number].append(
            (x0, y0, x1, y1)
        )

    # Du phong neu so cau bi ghep voi chu Han.
    missing = [
        n for n in numbers
        if not candidates[n]
    ]

    if missing:

        data = page.get_text("dict")

        for block in data.get("blocks", []):

            for line in block.get("lines", []):

                spans = line.get("spans", [])

                text = "".join(
                    span.get("text", "")
                    for span in spans
                ).strip()

                number = parse_number(text)

                if number not in missing:
                    continue

                x0, y0, x1, y1 = line["bbox"]

                if x0 > page.rect.width * 0.35:
                    continue

                candidates[number].append(
                    (x0, y0, x1, y1)
                )

    result = {}

    for number in numbers:

        options = candidates[number]

        if not options:
            continue

        result[number] = sorted(
            options,
            key=lambda p: (p[0], p[1])
        )[0]

    missing = [
        n for n in numbers
        if n not in result
    ]

    if missing:
        raise RuntimeError(
            f"Khong tim thay cau: {missing}"
        )

    return result


# =====================================================
# 4. TIM NOI DUNG CUOI TRANG
# =====================================================

def last_content_bottom(page, top):
    """
    Tim diem ket thuc cau cuoi.
    Khong lay so trang H20902 - ...
    """

    limit = page.rect.height - 65

    words = [
        w for w in page.get_text("words")
        if (
            w[1] >= top
            and w[3] < limit
            and w[0] >= 15
        )
    ]

    if not words:
        return top + 45

    return max(
        w[3] for w in words
    ) + 9


# =====================================================
# 5. TINH VUNG CAT CAU HOI
# =====================================================

def question_rect(
    page,
    numbers,
    positions,
    index
):

    number = numbers[index]

    y = positions[number][1]

    # Nghe 11-20 chi co so cau va o trong.
    # Anh van duoc tao de du 60 file,
    # nhung HTML chi hien thi so cau.
    if 11 <= number <= 20:

        top = y - 9
        bottom = y + 23

    else:

        # Lay ca dong Pinyin phia tren chu Han.
        top = y - 17

        if index < len(numbers) - 1:

            next_number = numbers[index + 1]
            next_y = positions[next_number][1]

            bottom = next_y - 17

        else:

            bottom = last_content_bottom(
                page,
                top
            )

    top = max(15, top)

    bottom = min(
        page.rect.height - 55,
        bottom
    )

    if bottom <= top + 12:
        raise RuntimeError(
            f"Vung cat cau {number} khong hop le."
        )

    return fitz.Rect(
        30,
        top,
        page.rect.width - 24,
        bottom
    )


# =====================================================
# 6. TINH VUNG CAT BANG LUA CHON
# =====================================================

def group_rect(page, first_question_y):

    top = page.rect.height * 0.085

    # Tim dong "Vi du" neu co.
    examples = page.search_for("例如")

    valid = [
        rect.y0
        for rect in examples
        if top < rect.y0 < first_question_y
    ]

    if valid:
        bottom = min(valid) - 12
    else:
        bottom = first_question_y - 35

    if bottom <= top + 40:
        raise RuntimeError(
            "Vung bang lua chon qua hep."
        )

    return fitz.Rect(
        12,
        top,
        page.rect.width - 12,
        bottom
    )


# =====================================================
# 7. LUU ANH PNG
# =====================================================

def save_image(page, rect, destination):

    rect = rect & page.rect

    if rect.is_empty:
        raise RuntimeError(
            f"Anh rong: {destination}"
        )

    pix = page.get_pixmap(
        matrix=fitz.Matrix(3, 3),
        clip=rect,
        alpha=False
    )

    pix.save(str(destination))


# =====================================================
# 8. TAO HTML XEM TRUOC
# =====================================================

SECTIONS = [
    ("Nghe - Phần 1 (1–10)", 1, 10, None),
    ("Nghe - Phần 2 (11–15)", 11, 15, "nghe_11_15"),
    ("Nghe - Phần 2 (16–20)", 16, 20, "nghe_16_20"),
    ("Nghe - Phần 3 (21–30)", 21, 30, None),
    ("Nghe - Phần 4 (31–35)", 31, 35, None),
    ("Đọc - Phần 1 (36–40)", 36, 40, "doc_36_40"),
    ("Đọc - Phần 2 (41–45)", 41, 45, "doc_41_45"),
    ("Đọc - Phần 3 (46–50)", 46, 50, None),
    ("Đọc - Phần 4 (51–55)", 51, 55, "doc_51_55"),
    ("Đọc - Phần 4 (56–60)", 56, 60, "doc_56_60"),
]


def create_html():

    parts = [
        """<!DOCTYPE html>
<html lang="vi">

<head>
<meta charset="UTF-8">
<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>HSK2 - Đề 2 | Kiểm tra 60 câu</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #f5f7fb;
    font-family: Arial, sans-serif;
    color: #26344a;
}

.container {
    width: min(1080px, 100%);
    margin: 0 auto;
    padding: 26px 18px 60px;
}

.header {
    padding: 22px;
    background: white;
    border: 1px solid #dce5f1;
    border-radius: 14px;
}

.header h1 {
    font-size: 24px;
    margin: 0 0 10px;
}

.header p {
    color: #64748b;
    line-height: 1.6;
    margin: 0;
}

.section {
    margin-top: 30px;
}

.section-title {
    font-size: 19px;
    padding-bottom: 12px;
    border-bottom: 1px solid #dce5f1;
}

.grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
}

.grid.two {
    grid-template-columns:
        repeat(2, minmax(0, 1fr));
}

.grid.compact {
    grid-template-columns:
        repeat(5, minmax(0, 1fr));
}

.card {
    background: white;
    border: 1px solid #dce5f1;
    border-radius: 12px;
    padding: 15px;
    min-width: 0;
}

.card-title {
    font-size: 16px;
    font-weight: bold;
    color: #2056a3;
    margin-bottom: 10px;
}

.question-image {
    display: block;
    width: 100%;
    height: auto;
    object-fit: contain;
}

.picture-card .question-image {
    max-height: 270px;
}

.simple-card {
    min-height: 76px;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.simple-card .card-title {
    margin: 0;
}

.group {
    background: white;
    border: 1px solid #dce5f1;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 16px;
}

.group-title {
    font-size: 14px;
    font-weight: bold;
    color: #2056a3;
    margin-bottom: 14px;
}

.group img {
    display: block;
    width: 100%;
    max-width: 850px;
    height: auto;
    margin: auto;
}

@media(max-width:750px) {
    .container {
        padding: 12px;
    }

    .grid.two,
    .grid.compact {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }
}

@media(max-width:450px) {
    .grid.two {
        grid-template-columns: 1fr;
    }
}
</style>
</head>

<body>
<div class="container">

<div class="header">
    <h1>HSK2 – Đề 2 (H20902)</h1>

    <p>
        60 câu hỏi • 35 câu Nghe • 25 câu Đọc.
        Không hiển thị đáp án.
    </p>
</div>
"""
    ]

    for title, start, end, group in SECTIONS:

        parts.append(
            '<section class="section">'
        )

        parts.append(
            '<h2 class="section-title">'
            + html.escape(title)
            + '</h2>'
        )

        if group:

            parts.append(
                '<div class="group">'
                '<div class="group-title">'
                'Bảng lựa chọn chung'
                '</div>'
                f'<img src="groups/{group}.png" '
                'alt="Bảng lựa chọn">'
                '</div>'
            )

        is_simple = 11 <= start <= 20

        if start <= 10:
            grid_class = "grid two"

        elif is_simple:
            grid_class = "grid compact"

        else:
            grid_class = "grid"

        parts.append(
            f'<div class="{grid_class}">'
        )

        for number in range(start, end + 1):

            if is_simple:

                # Chi hien thi so cau.
                parts.append(
                    '<div class="card simple-card">'
                    f'<div class="card-title">'
                    f'Câu {number:02d}'
                    '</div>'
                    '</div>'
                )

            else:

                picture_class = (
                    "picture-card"
                    if number <= 10
                    else ""
                )

                parts.append(
                    f'<div class="card {picture_class}">'
                    f'<div class="card-title">'
                    f'Câu {number:02d}'
                    '</div>'
                    f'<img class="question-image" '
                    f'src="questions/cau_{number:02d}.png" '
                    f'alt="Câu {number}">'
                    '</div>'
                )

        parts.append("</div>")
        parts.append("</section>")

    parts.append(
        "</div></body></html>"
    )

    HTML_FILE.write_text(
        "\n".join(parts),
        encoding="utf-8"
    )


# =====================================================
# 9. KIEM TRA FILE NGUON
# =====================================================

def check_sources():

    if not PDF_FILE.is_file():
        raise FileNotFoundError(PDF_FILE)

    if not ANSWER_FILE.is_file():
        raise FileNotFoundError(ANSWER_FILE)

    with ANSWER_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as f:
        answer_data = json.load(f)

    if answer_data.get("ma_de_goc") != "H20902":
        raise RuntimeError(
            "JSON dap an khong phai H20902."
        )

    answers = answer_data.get("dap_an", {})

    if set(answers) != {
        str(n) for n in range(1, 61)
    }:
        raise RuntimeError(
            "Dap an chua du 60 cau."
        )

    # Kiem tra 10 anh da tach o buoc 1.
    for number in range(1, 11):

        image_path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if not image_path.is_file():
            raise FileNotFoundError(
                f"Thieu anh cau {number}: {image_path}"
            )

    print("Da kiem tra 60 dap an.")
    print("Da co 10 anh cau hoi dau tien.")


# =====================================================
# 10. MAIN
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK2 DE 2 - H20902")
    print("TACH CAU 11-60")
    print("=" * 60)

    check_sources()

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

    # Giu nguyen anh cau 1-10.
    for number in range(1, 11):

        page_number = (
            2 if number <= 5 else 3
        )

        manifest_questions[str(number)] = {
            "trang_pdf": page_number,
            "anh": (
                f"questions/cau_{number:02d}.png"
            ),
            "toa_do": None,
        }

    with fitz.open(PDF_FILE) as doc:

        if len(doc) != 18:
            raise RuntimeError(
                "PDF khong dung 18 trang."
            )

        if "H20902" not in doc[0].get_text():
            raise RuntimeError(
                "PDF khong phai H20902."
            )

        print("\n===== KIEM TRA CAU 11-60 =====")

        # Nhan dien du so cau truoc khi cat.
        for page_no, numbers in PAGE_QUESTIONS.items():

            page = doc[page_no - 1]

            positions = find_positions(
                page,
                numbers
            )

            page_positions[page_no] = positions

            print(
                f"Trang {page_no:02d}: "
                f"{len(positions)}/{len(numbers)} cau"
            )

        remaining = sorted(
            number
            for numbers in PAGE_QUESTIONS.values()
            for number in numbers
        )

        if remaining != list(range(11, 61)):
            raise RuntimeError(
                "Danh sach cau 11-60 khong du."
            )

        print("\n===== TACH ANH CAU 11-60 =====")

        for page_no, numbers in PAGE_QUESTIONS.items():

            page = doc[page_no - 1]

            positions = page_positions[page_no]

            for index, number in enumerate(numbers):

                rect = question_rect(
                    page,
                    numbers,
                    positions,
                    index
                )

                filename = (
                    f"cau_{number:02d}.png"
                )

                destination = (
                    QUESTION_DIR / filename
                )

                save_image(
                    page,
                    rect,
                    destination
                )

                manifest_questions[str(number)] = {
                    "trang_pdf": page_no,
                    "anh": (
                        f"questions/{filename}"
                    ),
                    "toa_do": [
                        round(value, 2)
                        for value in rect
                    ],
                }

                print(
                    f"Cau {number:02d}: "
                    f"trang {page_no}, "
                    f"y={rect.y0:.1f}-{rect.y1:.1f}"
                )

        print("\n===== TACH 6 BANG LUA CHON =====")

        for group_name, page_no in GROUP_PAGES.items():

            page = doc[page_no - 1]

            first_number = (
                PAGE_QUESTIONS[page_no][0]
            )

            first_y = (
                page_positions[page_no]
                [first_number][1]
            )

            rect = group_rect(
                page,
                first_y
            )

            filename = (
                f"{group_name}.png"
            )

            save_image(
                page,
                rect,
                GROUP_DIR / filename
            )

            manifest_groups[group_name] = {
                "trang_pdf": page_no,
                "anh": (
                    f"groups/{filename}"
                ),
                "toa_do": [
                    round(value, 2)
                    for value in rect
                ],
            }

            print(
                f"{group_name}: trang {page_no}"
            )

    # ================================================
    # KIEM TRA KET QUA
    # ================================================

    if len(manifest_questions) != 60:
        raise RuntimeError(
            "Chua du 60 cau hoi."
        )

    if len(manifest_groups) != 6:
        raise RuntimeError(
            "Chua du 6 bang lua chon."
        )

    for number in range(1, 61):

        image_path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if not image_path.is_file():
            raise RuntimeError(
                f"Thieu anh cau {number}"
            )

    # ================================================
    # TAO JSON
    # ================================================

    result = {
        "cap_hsk": 2,
        "so_de": 2,
        "ma_de_goc": "H20902",
        "tong_cau": 60,
        "nghe": 35,
        "doc": 25,
        "trang_cau_hoi": list(range(2, 14)),
        "trang_bo_qua": [1, 14, 15, 16, 17, 18],
        "cau_hoi": manifest_questions,
        "bang_lua_chon": manifest_groups,
    }

    MANIFEST_FILE.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # ================================================
    # TAO HTML
    # ================================================

    create_html()

    print("\n" + "=" * 60)
    print("HOAN THANH HSK2 DE 2")
    print("=" * 60)

    print("Ma de: H20902")
    print("Anh cau hoi: 60/60")
    print("Bang lua chon: 6/6")
    print("Dap an: 60/60")
    print("Nghe: 35")
    print("Doc: 25")

    print(f"\nJSON: {MANIFEST_FILE}")
    print(f"HTML: {HTML_FILE}")

    print("\nChua chuan hoa de.")
    print("Chua thay doi SQL Server.")
    print("Khong sua HSK1 va HSK2 De 1.")


if __name__ == "__main__":
    main()
