
# -*- coding: utf-8 -*-
"""
MỘC HÁN - HSK1 ĐỀ 1 (H10000)

Chỉnh vùng cắt:
- Câu 6-10: bỏ phần bị dính từ hàng khác.
- Câu 26-30: bổ sung câu chữ Hán và pinyin.

Cập nhật JSON và tạo trang kiểm tra.
Không sửa PDF, MP3 hoặc SQL Server.
"""

import json
from html import escape
from pathlib import Path

try:
    import fitz
except ImportError:
    raise SystemExit(
        "Thiếu PyMuPDF. Chạy: python -m pip install pymupdf"
    )


# ==================================================
# 1. ĐƯỜNG DẪN
# ==================================================

BASE = Path(__file__).resolve().parents[1]

SOURCE_PDF = (
    BASE / "source" / "De_HSK" / "HSK1"
    / "H10000.pdf"
)

DATA_DIR = BASE / "hsk1" / "data" / "de_01"
OUTPUT_DIR = BASE / "hsk1" / "output" / "de_01"
QUESTIONS_DIR = OUTPUT_DIR / "questions"

JSON_PATH = DATA_DIR / "hinh_40_cau.json"
HTML_PATH = OUTPUT_DIR / "kiem_tra_10_cau_da_sua.html"

if not SOURCE_PDF.is_file():
    raise SystemExit(f"Thiếu PDF: {SOURCE_PDF}")

if not JSON_PATH.is_file():
    raise SystemExit(
        "Thiếu hinh_40_cau.json. "
        "Chạy extract_remaining_de1.py trước."
    )

QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. TỌA ĐỘ ĐÃ KIỂM TRA TRÊN PDF H10000
#
# (Trang PDF, x0, y0, x1, y1)
# Chỉ sử dụng cho mã đề H10000.
# ==================================================

REGIONS = {
    6:  (4, 154, 303, 515, 446),
    7:  (4, 154, 448, 515, 591),
    8:  (4, 154, 592, 515, 736),
    9:  (5, 154, 103, 515, 247),
    10: (5, 154, 249, 515, 393),

    26: (9, 121, 574, 420, 607),
    27: (9, 121, 608, 420, 641),
    28: (9, 121, 642, 420, 675),
    29: (9, 121, 677, 420, 708),
    30: (9, 121, 711, 420, 744),
}


# ==================================================
# 3. CẮT LẠI HÌNH TỪ PDF GỐC
# ==================================================

with fitz.open(SOURCE_PDF) as doc:

    if len(doc) != 11:
        raise SystemExit(
            "PDF không đúng cấu trúc H10000."
        )

    for number, region in REGIONS.items():

        page_number, x0, y0, x1, y1 = region
        page = doc[page_number - 1]

        rect = fitz.Rect(x0, y0, x1, y1)

        if not page.rect.contains(rect):
            raise RuntimeError(
                f"Vùng cắt câu {number} không hợp lệ."
            )

        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(3, 3),
            clip=rect,
            alpha=False,
        )

        filename = f"cau_{number:02d}.png"

        pixmap.save(
            str(QUESTIONS_DIR / filename)
        )

        print(f"Đã chỉnh câu {number}: {filename}")


# ==================================================
# 4. CẬP NHẬT JSON 40 CÂU
# Không đưa đáp án vào JSON hiển thị.
# ==================================================

data = json.loads(
    JSON_PATH.read_text(encoding="utf-8")
)

questions = data.get("cau_hoi", [])

if len(questions) != 40:
    raise SystemExit(
        "JSON chưa đủ 40 câu hỏi."
    )

question_map = {
    int(q["so_cau"]): q
    for q in questions
}

if any(n not in question_map for n in REGIONS):
    raise SystemExit(
        "JSON thiếu câu cần chỉnh sửa."
    )

for number in REGIONS:

    question = question_map[number]

    question["anh_cau_hoi"] = (
        f"questions/cau_{number:02d}.png"
    )

    question["da_kiem_tra_hinh"] = False

# Lưu bản sao dự phòng một lần.
backup = DATA_DIR / "hinh_40_cau_truoc_chinh_sua.json"

if not backup.exists():
    backup.write_text(
        JSON_PATH.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

JSON_PATH.write_text(
    json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)

print("Đã cập nhật JSON 40 câu.")


# ==================================================
# 5. TẠO HTML KIỂM TRA 10 CÂU
# Không hiển thị đáp án.
# ==================================================

parts = [
    "<!doctype html>",
    '<html lang="vi">',
    "<head>",
    '<meta charset="utf-8">',
    "<title>HSK1 - Kiểm tra ảnh đã sửa</title>",
    "<style>",
    "*{box-sizing:border-box}",
    "body{margin:0;padding:25px;"
    "background:#faf1e5;"
    "font-family:Arial,sans-serif}",
    "main{max-width:1050px;margin:auto}",
    "h1{font-size:26px}",
    "h2{font-size:19px;margin-top:30px}",
    ".grid{display:grid;"
    "grid-template-columns:repeat(2,minmax(0,1fr));"
    "gap:16px}",
    ".card{border:2px solid #333;"
    "background:#fffaf3;border-radius:10px;"
    "padding:15px}",
    ".card strong{display:block;margin-bottom:12px}",
    ".image{background:white;"
    "display:flex;align-items:center;"
    "justify-content:center;"
    "min-height:140px;padding:10px}",
    ".image img{max-width:100%;"
    "height:auto;object-fit:contain}",
    "@media(max-width:650px){"
    ".grid{grid-template-columns:1fr}}",
    "</style>",
    "</head>",
    "<body><main>",
    "<h1>HSK1 - Đề 1 (H10000)</h1>",
    "<p>Kiểm tra các câu đã chỉnh sửa.</p>",
]

for title, numbers in [
    ("Nghe hiểu - Câu 6 đến 10", range(6, 11)),
    ("Đọc hiểu - Câu 26 đến 30", range(26, 31)),
]:

    parts.append(f"<h2>{escape(title)}</h2>")
    parts.append('<div class="grid">')

    for number in numbers:

        filename = f"questions/cau_{number:02d}.png"

        parts.extend([
            '<div class="card">',
            f"<strong>Câu {number}</strong>",
            '<div class="image">',
            f'<img src="{escape(filename, quote=True)}" '
            f'alt="Câu {number}">',
            "</div>",
            "</div>",
        ])

    parts.append("</div>")

parts.extend(["</main></body></html>"])

HTML_PATH.write_text(
    "\n".join(parts),
    encoding="utf-8",
)

print()
print("========== HOÀN THÀNH ==========")
print("Đã chỉnh sửa 10 câu.")
print("Đã bổ sung nội dung câu 26-30.")
print("HTML:", HTML_PATH)
print("JSON:", JSON_PATH)
print("Chưa thay đổi SQL Server.")
