# -*- coding: utf-8 -*-

"""
MOC HAN - LAM DEP HSK2 DE 1 (H20901)

- Giu nguyen anh 1-10 va 6 bang lua chon chung
- Cat lai anh 11-60 cho gon hon
- Bo dong thua va chan trang
- Tang kich thuoc hien thi cau hoi
- An anh PDF khong can thiet cua Nghe 11-20
- Cap nhat HTML va toa do JSON

Khong sua dap an.
Khong thay doi SQL Server.
"""

from pathlib import Path
import json
import re
import shutil
import unicodedata
import fitz


ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

PDF_PATH = (
    ROOT / "source" / "De_HSK" / "HSK2"
    / "Đề HSK 2 số 1 file pdf.pdf"
)

OUT = ROOT / "hsk2" / "output" / "de_01"
DATA = ROOT / "hsk2" / "data" / "de_01"

QUESTIONS = OUT / "questions"
GROUPS_DIR = OUT / "groups"

BACKUP = OUT / "backup_truoc_lam_dep"

JSON_PATH = DATA / "hinh_60_cau_ung_vien.json"
HTML_PATH = OUT / "kiem_tra_60_cau.html"


# ==========================================
# SO CAU TREN TUNG TRANG PDF
# ==========================================

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


# ==========================================
# NHAN DIEN SO CAU
# ==========================================

def parse_number(value):
    value = unicodedata.normalize(
        "NFKC", str(value)
    ).strip()

    match = re.match(
        r"^(\d{1,2})(?=[.、):：]|$)",
        value
    )

    if match:
        return int(match.group(1))

    return None


def find_positions(page, numbers):
    positions = {}

    for word in page.get_text("words"):
        x0, y0, x1, y1, raw = word[:5]

        number = parse_number(raw)

        if number not in numbers:
            continue

        if not (0 <= x0 <= page.rect.width * 0.35):
            continue

        if not (
            page.rect.height * 0.05
            < y0
            < page.rect.height * 0.94
        ):
            continue

        item = (x0, y0, x1, y1)

        if number not in positions:
            positions[number] = item
        elif x0 < positions[number][0]:
            positions[number] = item

    missing = [
        number
        for number in numbers
        if number not in positions
    ]

    if missing:
        raise RuntimeError(
            f"Khong tim thay so cau: {missing}"
        )

    return positions


# ==========================================
# TIM NOI DUNG CUOI CUA CAU
# ==========================================

def last_content_bottom(page, top):
    """
    Tim dong noi dung cuoi truoc chan trang.
    Khong lay so trang H20901 - ...
    """

    limit = page.rect.height - 65

    words = [
        word
        for word in page.get_text("words")
        if (
            word[1] >= top
            and word[3] < limit
            and word[0] >= 15
        )
    ]

    if not words:
        return top + 45

    return max(word[3] for word in words) + 9


# ==========================================
# TAO VUNG CAT MOI
# ==========================================

def make_rect(page, numbers, positions, index):
    number = numbers[index]
    y = positions[number][1]

    # Nghe 11-20 chi co so cau va o chon.
    if 11 <= number <= 20:
        top = y - 10
        bottom = y + 24

    else:
        # Giu dong Pinyin ngay tren chu Han.
        # Tranh lay dong truoc do.
        top = y - 17

        if index < len(numbers) - 1:
            next_number = numbers[index + 1]
            next_y = positions[next_number][1]

            bottom = next_y - 17

        else:
            # Cau cuoi trang: ket thuc theo noi dung that
            bottom = last_content_bottom(page, top)

    top = max(15, top)

    bottom = min(
        page.rect.height - 55,
        bottom
    )

    if bottom <= top + 12:
        raise RuntimeError(
            f"Vung cat cau {number} khong hop le."
        )

    # Lay du chu Han, Pinyin va o chon ben phai.
    return fitz.Rect(
        30,
        top,
        page.rect.width - 24,
        bottom
    )


# ==========================================
# SAO LUU
# ==========================================

def backup_originals():
    BACKUP.mkdir(
        parents=True,
        exist_ok=True
    )

    for number in range(11, 61):
        name = f"cau_{number:02d}.png"

        original = QUESTIONS / name
        backup = BACKUP / name

        if not original.is_file():
            raise FileNotFoundError(original)

        if not backup.exists():
            shutil.copy2(original, backup)

    for original in [JSON_PATH, HTML_PATH]:
        backup = BACKUP / original.name

        if original.is_file() and not backup.exists():
            shutil.copy2(original, backup)

    print("Da sao luu du lieu cu.")


# ==========================================
# HTML XEM TRUOC MOI
# ==========================================

def create_html():
    parts = [
        """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HSK2 - Đề 1 | Kiểm tra ảnh</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f5f7fb;
    color: #24344c;
}

.container {
    width: min(1080px, 100%);
    margin: 0 auto;
    padding: 26px 18px 60px;
}

.header {
    background: white;
    border: 1px solid #dce5f1;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 22px;
}

.header h1 {
    font-size: 24px;
    margin: 0 0 10px;
}

.header p {
    color: #64748b;
    margin: 0;
    line-height: 1.6;
}

.section {
    margin-top: 30px;
}

.section-title {
    font-size: 19px;
    font-weight: 700;
    margin: 0 0 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #dce5f1;
}

.grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
}

.grid.two {
    grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid.compact {
    grid-template-columns: repeat(5, minmax(0, 1fr));
}

.card {
    background: white;
    border: 1px solid #dce5f1;
    border-radius: 12px;
    padding: 14px 18px;
    min-width: 0;
}

.card-title {
    font-size: 15px;
    font-weight: 700;
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
    padding: 16px;
    text-align: center;
}

.simple-card .card-title {
    margin: 0;
    font-size: 16px;
}

.simple-hint {
    font-size: 12px;
    color: #64748b;
    margin-top: 6px;
}

.group {
    background: white;
    border: 1px solid #dce5f1;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 16px;
}

.group-heading {
    font-size: 14px;
    font-weight: 700;
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

.note {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 9px;
    padding: 12px 14px;
    font-size: 13px;
    line-height: 1.6;
    color: #526174;
    margin-bottom: 14px;
}

@media(max-width: 750px) {
    .container {
        padding: 12px;
    }

    .grid.two,
    .grid.compact {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .card {
        padding: 12px;
    }
}

@media(max-width: 450px) {
    .grid.two {
        grid-template-columns: 1fr;
    }
}
</style>
</head>

<body>
<div class="container">

<div class="header">
    <h1>HSK2 – Đề 1 (H20901)</h1>
    <p>
        Kiểm tra 60 câu hỏi • 35 câu Nghe • 25 câu Đọc.
        Chỉ hiển thị nội dung đề, không hiển thị đáp án.
    </p>
</div>
"""
    ]

    for title, start, end, group in SECTIONS:
        parts.append('<section class="section">')
        parts.append(
            f'<h2 class="section-title">{title}</h2>'
        )

        if group:
            parts.append(
                '<div class="group">'
                '<div class="group-heading">'
                'Bảng lựa chọn chung'
                '</div>'
                f'<img src="groups/{group}.png" '
                'alt="Bảng lựa chọn chung">'
                '</div>'
            )

        # Nghe 11-20: audio + bang hinh A-F
        # Khong can hien thi anh PDF co moi so cau va o tick.
        is_simple = 11 <= start <= 20

        if is_simple:
            parts.append(
                '<div class="note">'
                'Nghe nội dung từ MP3 và chọn hình phù hợp '
                'trong bảng A–F phía trên. '
                'PDF gốc không có câu hỏi bằng chữ ở phần này.'
                '</div>'
            )

        css_class = "grid"

        if start <= 10:
            css_class = "grid two"

        elif is_simple:
            css_class = "grid compact"

        parts.append(
            f'<div class="{css_class}">'
        )

        for number in range(start, end + 1):
            if is_simple:
                parts.append(
                    '<div class="card simple-card">'
                    f'<div class="card-title">Câu {number:02d}</div>'
                    ''
                    '</div>'
                )

            else:
                picture_class = (
                    "picture-card"
                    if number <= 10 else ""
                )

                parts.append(
                    f'<div class="card {picture_class}">'
                    f'<div class="card-title">Câu {number:02d}</div>'
                    f'<img class="question-image" '
                    f'src="questions/cau_{number:02d}.png" '
                    f'alt="Câu {number}">'
                    '</div>'
                )

        parts.append("</div>")
        parts.append("</section>")

    parts.append(
        '</div></body></html>'
    )

    HTML_PATH.write_text(
        "\n".join(parts),
        encoding="utf-8"
    )


# ==========================================
# MAIN
# ==========================================

def main():
    print("=" * 60)
    print("MOC HAN - LAM DEP HSK2 DE 1")
    print("=" * 60)

    if not PDF_PATH.is_file():
        raise FileNotFoundError(PDF_PATH)

    if not JSON_PATH.is_file():
        raise FileNotFoundError(JSON_PATH)

    if not GROUPS_DIR.is_dir():
        raise FileNotFoundError(GROUPS_DIR)

    with JSON_PATH.open(
        "r",
        encoding="utf-8-sig"
    ) as f:
        manifest = json.load(f)

    # Xac nhan co du 60 cau va 6 bang.
    if len(manifest.get("cau_hoi", {})) != 60:
        raise RuntimeError(
            "JSON chua du 60 cau hoi."
        )

    if len(manifest.get("bang_lua_chon", {})) != 6:
        raise RuntimeError(
            "JSON chua du 6 bang lua chon."
        )

    # Tim tat ca toa do truoc khi ghi de.
    crops = {}

    with fitz.open(PDF_PATH) as doc:
        if len(doc) != 18:
            raise RuntimeError(
                "PDF khong phai ban H20901 18 trang."
            )

        for page_no, numbers in PAGE_QUESTIONS.items():
            page = doc[page_no - 1]
            positions = find_positions(page, numbers)

            for index, number in enumerate(numbers):
                crops[number] = (
                    page_no,
                    make_rect(
                        page,
                        numbers,
                        positions,
                        index
                    )
                )

        print("\n===== SAO LUU =====")
        backup_originals()

        print("\n===== CAT LAI ANH =====")

        for number in range(11, 61):
            page_no, rect = crops[number]
            page = doc[page_no - 1]

            pix = page.get_pixmap(
                matrix=fitz.Matrix(3, 3),
                clip=rect,
                alpha=False
            )

            filename = f"cau_{number:02d}.png"
            pix.save(
                str(QUESTIONS / filename)
            )

            manifest["cau_hoi"][str(number)] = {
                "trang_pdf": page_no,
                "anh": f"questions/{filename}",
                "toa_do": [
                    round(v, 2) for v in rect
                ]
            }

            print(
                f"Cau {number:02d}: "
                f"trang {page_no}, "
                f"y={rect.y0:.1f}-{rect.y1:.1f}"
            )

    JSON_PATH.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\n===== TAO HTML MOI =====")
    create_html()

    print("\n===== HOAN THANH =====")
    print("Giu nguyen anh 1-10.")
    print("Da cat lai anh 11-60.")
    print("Giu nguyen 6 bang lua chon.")
    print("Da cai thien HTML.")
    print(f"HTML: {HTML_PATH}")
    print(f"Backup: {BACKUP}")
    print("Khong thay doi SQL Server.")


if __name__ == "__main__":
    main()
