
# -*- coding: utf-8 -*-
"""
MỘC HÁN - HSK1 ĐỀ 1 (H10000)

Hoàn thiện phần hình ảnh:
- Giữ nguyên 10 câu đã tách trước.
- Tách câu 6-20 và 26-40.
- Tách bảng lựa chọn dùng chung.
- Tạo HTML xem trước đủ 40 câu.

Chưa sửa SQL, PDF gốc hoặc MP3.
Không hiển thị đáp án đúng.
"""

import json
from html import escape
from pathlib import Path

try:
    import fitz
except ImportError:
    raise SystemExit(
        "Cài PyMuPDF: python -m pip install pymupdf"
    )


# =====================================================
# 1. ĐƯỜNG DẪN
# =====================================================

ROOT = Path(__file__).resolve().parent.parent

SOURCE = ROOT / "source" / "De_HSK" / "HSK1"

DATA = ROOT / "hsk1" / "data" / "de_01"

OUTPUT = ROOT / "hsk1" / "output" / "de_01"

QUESTIONS = OUTPUT / "questions"
GROUPS = OUTPUT / "groups"

PDF = SOURCE / "H10000.pdf"
PREVIEW = DATA / "preview_de1.json"

RESULT = DATA / "hinh_40_cau.json"
HTML = OUTPUT / "kiem_tra_40_cau.html"

QUESTIONS.mkdir(parents=True, exist_ok=True)
GROUPS.mkdir(parents=True, exist_ok=True)

if not PDF.is_file():
    raise SystemExit(f"Không tìm thấy: {PDF}")

if not PREVIEW.is_file():
    raise SystemExit(
        "Thiếu preview_de1.json. "
        "Hãy chạy prepare_de1.py trước."
    )

preview_data = json.loads(
    PREVIEW.read_text(encoding="utf-8")
)

if len(preview_data.get("cau_hoi", [])) != 40:
    raise SystemExit(
        "JSON chuẩn bị chưa đủ 40 câu."
    )


# =====================================================
# 2. CẤU HÌNH CẮT PDF H10000
#
# Tọa độ theo PDF gốc, đơn vị point.
# Mỗi vùng giữ nguyên nội dung gốc.
# Không dùng OCR hoặc tự tạo câu hỏi.
#
# (trang PDF, x0, y0, x1, y1)
# =====================================================

REGIONS = {

    # Nghe - Phần 2: 3 lựa chọn hình/câu
    6:  (4, 90, 340, 510, 465),
    7:  (4, 90, 485, 510, 610),
    8:  (4, 90, 630, 510, 757),
    9:  (5, 90, 142, 510, 268),
    10: (5, 90, 285, 510, 412),

    # Nghe - Phần 3:
    # Dùng bảng hình A-F riêng.
    # Mỗi câu chỉ có số thứ tự trên PDF.
    # Không tạo ảnh câu trống.

    # Nghe - Phần 4: chọn A/B/C
    16: (7, 90, 318, 505, 386),
    17: (7, 90, 380, 505, 448),
    18: (7, 90, 442, 505, 509),
    19: (7, 90, 503, 505, 570),
    20: (7, 90, 565, 505, 634),

    # Đọc - Phần 2:
    # Dùng bảng hình A-F riêng.

    # Đọc - Phần 3:
    # Cắt cột câu hỏi bên trái.
    # Nhóm lựa chọn A-F ở bên phải.
    31: (10, 88, 231, 365, 293),
    32: (10, 88, 294, 365, 355),
    33: (10, 88, 356, 365, 418),
    34: (10, 88, 419, 365, 481),
    35: (10, 88, 482, 365, 544),

    # Đọc - Phần 4:
    # Giữ nguyên nội dung mỗi câu.
    36: (11, 88, 306, 510, 371),
    37: (11, 88, 374, 510, 443),
    38: (11, 88, 445, 510, 511),
    39: (11, 88, 512, 510, 594),
    40: (11, 88, 596, 510, 691),
}


# Các bảng lựa chọn dùng chung cho nhóm câu.
#
# Nghe phần 3: 6 tranh A-F
# Đọc phần 2: 6 tranh A-F
# Đọc phần 3: các câu lựa chọn A-F
# Đọc phần 4: các cụm từ/câu lựa chọn A-F

SHARED_REGIONS = {
    "nghe_phan_3": (6, 84, 150, 510, 550),
    "doc_phan_2": (9, 84, 150, 510, 530),
    "doc_phan_3": (10, 367, 163, 520, 550),
    "doc_phan_4": (11, 84, 160, 515, 316),
}


# =====================================================
# 3. HÀM CẮT ẢNH
# =====================================================

def crop_pdf(doc, region, destination):
    page_number, x0, y0, x1, y1 = region

    page = doc[page_number - 1]

    rect = fitz.Rect(x0, y0, x1, y1)

    if not page.rect.contains(rect):
        raise RuntimeError(
            f"Vùng cắt nằm ngoài trang {page_number}"
        )

    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(2.5, 2.5),
        clip=rect,
        alpha=False,
    )

    pixmap.save(str(destination))


# =====================================================
# 4. TÁCH ẢNH CÂU HỎI VÀ BẢNG CHUNG
# =====================================================

with fitz.open(PDF) as document:

    if len(document) != 11:
        raise SystemExit(
            f"PDF H10000 có {len(document)} trang, "
            "khác cấu trúc dự kiến 11 trang."
        )

    for number, region in REGIONS.items():

        filename = f"cau_{number:02d}.png"
        destination = QUESTIONS / filename

        crop_pdf(document, region, destination)

        print(f"Đã tách câu {number:02d}")

    for name, region in SHARED_REGIONS.items():

        destination = GROUPS / f"{name}.png"

        crop_pdf(document, region, destination)

        print(f"Đã tách bảng chung: {name}")


# =====================================================
# 5. TẠO DANH SÁCH ĐỦ 40 CÂU
#
# Đáp án nằm trong JSON gốc riêng.
# JSON này chỉ chứa dữ liệu hiển thị.
# =====================================================

def group_for_question(number):

    if 11 <= number <= 15:
        return "groups/nghe_phan_3.png"

    if 26 <= number <= 30:
        return "groups/doc_phan_2.png"

    if 31 <= number <= 35:
        return "groups/doc_phan_3.png"

    if 36 <= number <= 40:
        return "groups/doc_phan_4.png"

    return None


def question_image(number):

    # Phần nghe 3 và đọc 2 chỉ có bảng chung.
    if 11 <= number <= 15:
        return None

    if 26 <= number <= 30:
        return None

    filename = f"cau_{number:02d}.png"

    if not (QUESTIONS / filename).is_file():
        raise RuntimeError(
            f"Thiếu ảnh câu {number}: {filename}"
        )

    return f"questions/{filename}"


questions = []

for number in range(1, 41):

    if number <= 20:
        skill = "nghe"
    else:
        skill = "doc"

    if number <= 5:
        part = 1
    elif number <= 10:
        part = 2
    elif number <= 15:
        part = 3
    elif number <= 20:
        part = 4
    elif number <= 25:
        part = 1
    elif number <= 30:
        part = 2
    elif number <= 35:
        part = 3
    else:
        part = 4

    if 11 <= number <= 15:
        question_type = "ghep_hinh_theo_audio"

    elif 26 <= number <= 30:
        question_type = "ghep_hinh_theo_noi_dung"

    elif 31 <= number <= 40:
        question_type = "ghep_cap"

    elif number <= 5 or 21 <= number <= 25:
        question_type = "dung_sai"

    else:
        question_type = "chon_mot"

    questions.append({
        "so_cau": number,
        "ky_nang": skill,
        "phan": part,
        "loai_cau_hoi": question_type,
        "anh_cau_hoi": question_image(number),
        "anh_nhom_lua_chon": group_for_question(number),
        "bat_dau_audio": None,
        "ket_thuc_audio": None,
        "da_kiem_tra_hinh": False,
    })


result = {
    "cap_hsk": 1,
    "ten_de": "Đề 1",
    "ma_de_goc": "H10000",
    "so_cau": 40,
    "so_cau_nghe": 20,
    "so_cau_doc": 20,
    "trang_thai": "cho_kiem_tra_hinh",
    "cau_hoi": questions,
}

RESULT.write_text(
    json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)


# =====================================================
# 6. HTML XEM TRƯỚC
# Không hiển thị đáp án.
# Bảng chung chỉ hiển thị một lần mỗi phần.
# =====================================================

html_parts = [
    "<!DOCTYPE html>",
    '<html lang="vi">',
    "<head>",
    '<meta charset="utf-8">',
    '<meta name="viewport" '
    'content="width=device-width, initial-scale=1">',
    "<title>HSK1 - Đề 1 - 40 câu</title>",
    "<style>",
    "*{box-sizing:border-box}",
    "body{margin:0;padding:24px;"
    "font-family:Arial,sans-serif;"
    "background:#f8f0e5;color:#292929}",
    "main{max-width:1000px;margin:auto}",
    "h1{font-size:28px}",
    "h2{margin:30px 0 12px;font-size:21px}",
    "h3{font-size:17px;margin:0 0 12px}",
    ".grid{display:grid;"
    "grid-template-columns:repeat(2,minmax(0,1fr));"
    "gap:14px}",
    ".card,.shared{background:#fffaf3;"
    "border:2px solid #333;border-radius:9px;"
    "padding:15px}",
    ".image{background:white;"
    "min-height:90px;display:flex;"
    "align-items:center;justify-content:center;"
    "padding:10px}",
    ".image img{max-width:100%;"
    "max-height:350px;object-fit:contain}",
    ".shared{margin-bottom:15px}",
    ".shared img{width:100%;max-height:650px;"
    "object-fit:contain}",
    ".note{color:#695d50;font-size:14px}",
    "@media(max-width:680px){"
    ".grid{grid-template-columns:1fr}}",
    "</style>",
    "</head>",
    "<body><main>",
    "<h1>HSK1 - Đề 1 (H10000)</h1>",
    "<p>Kiểm tra hình ảnh 40 câu. "
    "Chưa phải giao diện làm bài chính thức.</p>",
]

shown_groups = set()

for skill, skill_title in [
    ("nghe", "Nghe hiểu"),
    ("doc", "Đọc hiểu"),
]:

    html_parts.append(
        f"<h2>{escape(skill_title)}</h2>"
    )

    for part in range(1, 5):

        part_questions = [
            q for q in questions
            if q["ky_nang"] == skill
            and q["phan"] == part
        ]

        if not part_questions:
            continue

        html_parts.append(
            f"<h3>Phần {part}</h3>"
        )

        shared = part_questions[0][
            "anh_nhom_lua_chon"
        ]

        if shared and shared not in shown_groups:

            html_parts.extend([
                '<div class="shared">',
                '<p><strong>Nhóm lựa chọn chung</strong></p>',
                f'<img src="{escape(shared, quote=True)}" '
                'alt="Nhóm lựa chọn">',
                "</div>",
            ])

            shown_groups.add(shared)

        html_parts.append('<div class="grid">')

        for item in part_questions:

            number = item["so_cau"]
            image_path = item["anh_cau_hoi"]

            html_parts.extend([
                '<article class="card">',
                f"<h3>Câu {number}</h3>",
            ])

            if image_path:

                html_parts.extend([
                    '<div class="image">',
                    f'<img src="{escape(image_path, quote=True)}" '
                    f'alt="Câu {number}">',
                    "</div>",
                ])

            else:
                html_parts.append(
                    '<p class="note">'
                    "Sử dụng nhóm lựa chọn phía trên."
                    "</p>"
                )

            html_parts.append("</article>")

        html_parts.append("</div>")


html_parts.extend([
    "</main>",
    "</body>",
    "</html>",
])

HTML.write_text(
    "\n".join(html_parts),
    encoding="utf-8",
)


# =====================================================
# 7. TỔNG KẾT
# =====================================================

if len(questions) != 40:
    raise RuntimeError("Danh sách chưa đủ 40 câu.")

print()
print("========== HOÀN THÀNH ==========")
print("HSK1 - Đề 1 (H10000)")
print("Tổng số câu:", len(questions))
print("Ảnh câu mới:", len(REGIONS))
print("Bảng lựa chọn chung:", len(SHARED_REGIONS))
print("JSON:", RESULT)
print("HTML:", HTML)
print()
print("Chưa nhập SQL Server.")
print("Chưa tách audio theo từng câu.")
print("Cần kiểm tra lại ảnh trước khi nhập SQL.")
