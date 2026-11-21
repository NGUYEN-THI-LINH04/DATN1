
# -*- coding: utf-8 -*-
"""
MỘC HÁN - HSK1 / ĐỀ 1 - TÁCH CÂU HỎI

PDF nguồn: H10000.pdf

Tách thử:
- Câu 1-5: hình ảnh phần Nghe
- Câu 21-25: hình ảnh + chữ Hán + pinyin phần Đọc

Xuất PNG, JSON và HTML xem trước.
Không thay đổi SQL Server hoặc dữ liệu gốc.
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


# ============================================================
# 1. THƯ MỤC
# ============================================================

BASE = Path(__file__).resolve().parents[1]

PDF_PATH = (
    BASE / "source" / "De_HSK"
    / "HSK1" / "H10000.pdf"
)

DATA_DIR = (
    BASE / "hsk1" / "data" / "de_01"
)

OUTPUT_DIR = (
    BASE / "hsk1" / "output" / "de_01"
)

QUESTIONS_DIR = OUTPUT_DIR / "questions"

JSON_PATH = DATA_DIR / "preview_de1.json"
RESULT_JSON = DATA_DIR / "hinh_cau_hoi_kiem_tra.json"
HTML_PATH = OUTPUT_DIR / "kiem_tra_10_cau.html"

QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. KIỂM TRA DỮ LIỆU ĐÃ CHUẨN BỊ
# ============================================================

if not PDF_PATH.is_file():
    raise SystemExit(f"Không tìm thấy PDF: {PDF_PATH}")

if not JSON_PATH.is_file():
    raise SystemExit(
        "Chưa tìm thấy preview_de1.json. "
        "Hãy chạy prepare_de1.py trước."
    )

preview = json.loads(
    JSON_PATH.read_text(encoding="utf-8")
)

answers = {
    int(q["so_cau"]): q["dap_an_goc"]
    for q in preview["cau_hoi"]
}

numbers = list(range(1, 6)) + list(range(21, 26))

for number in numbers:
    if number not in answers:
        raise SystemExit(
            f"Thiếu đáp án của câu {number}."
        )


# ============================================================
# 3. CẤU TRÚC BẢNG CỦA H10000
#
# Đây là tọa độ PDF gốc, đơn vị point.
# Không phụ thuộc mức zoom khi xem trên Windows.
#
# Trang 3: Nghe 1-5
# Trang 8: Đọc 21-25
# ============================================================

ROW_EDGES = [
    345.8,
    427.9,
    510.2,
    592.3,
    674.6,
    756.7,
]

# Vùng nội dung của phần Đọc:
# gồm ảnh, pinyin và chữ Hán.
READ_X0 = 181.0
READ_X1 = 431.0

RENDER_DPI = 220


def render_region(page, rect, output_path):
    """Cắt một vùng PDF với chất lượng cao."""

    rect = fitz.Rect(rect)
    rect = rect & page.rect

    if rect.is_empty:
        raise RuntimeError(
            f"Vùng cắt không hợp lệ: {rect}"
        )

    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(
            RENDER_DPI / 72,
            RENDER_DPI / 72,
        ),
        clip=rect,
        alpha=False,
    )

    pixmap.save(str(output_path))


def get_image_in_row(page, y0, y1):
    """
    Tìm ảnh nhúng nằm trong hàng câu hỏi.
    Bỏ ảnh ví dụ bằng cách giới hạn vùng hàng.
    """

    matches = []

    for info in page.get_images(full=True):
        xref = info[0]

        for rect in page.get_image_rects(xref):
            center_y = (rect.y0 + rect.y1) / 2

            if not (y0 < center_y < y1):
                continue

            # Cột hình minh họa của bảng H10000.
            if not (180 < rect.x0 < 320):
                continue

            if rect.width < 12 or rect.height < 12:
                continue

            matches.append(rect)

    if len(matches) != 1:
        raise RuntimeError(
            "Không xác định được duy nhất một ảnh "
            f"ở vùng y={y0:.1f}-{y1:.1f}. "
            f"Tìm thấy {len(matches)} ảnh."
        )

    return matches[0]


# ============================================================
# 4. TÁCH 10 CÂU HỎI
# ============================================================

results = []

with fitz.open(PDF_PATH) as doc:

    if len(doc) < 8:
        raise SystemExit(
            "PDF không đủ trang để xử lý."
        )

    for number in numbers:

        if number <= 5:
            page_number = 3
            row_index = number - 1
            skill = "nghe"
        else:
            page_number = 8
            row_index = number - 21
            skill = "doc"

        page = doc[page_number - 1]

        y0 = ROW_EDGES[row_index]
        y1 = ROW_EDGES[row_index + 1]

        image_rect = get_image_in_row(
            page, y0, y1
        )

        if skill == "nghe":
            # Chỉ cắt hình minh họa.
            crop = fitz.Rect(
                image_rect.x0 - 4,
                image_rect.y0 - 4,
                image_rect.x1 + 4,
                image_rect.y1 + 4,
            )

        else:
            # Giữ cả hình và chữ Hán, pinyin.
            # Không lấy ô đáp án bên phải.
            crop = fitz.Rect(
                READ_X0,
                y0 + 2,
                READ_X1,
                y1 - 2,
            )

        filename = f"cau_{number:02d}.png"
        output_path = QUESTIONS_DIR / filename

        render_region(
            page,
            crop,
            output_path,
        )

        item = {
            "so_cau": number,
            "ky_nang": skill,
            "trang_pdf": page_number,
            "anh_cau_hoi": f"questions/{filename}",
            "dap_an_goc": answers[number],
            "vung_cat_pdf": [
                round(crop.x0, 2),
                round(crop.y0, 2),
                round(crop.x1, 2),
                round(crop.y1, 2),
            ],
            "da_kiem_tra_hinh": False,
        }

        results.append(item)

        print(
            f"Đã tách câu {number:02d} "
            f"({skill}) -> {filename}"
        )


# ============================================================
# 5. XUẤT JSON KẾT QUẢ
#
# Tạo file riêng, không ghi đè JSON ban đầu.
# ============================================================

result_data = {
    "cap_hsk": 1,
    "ten_de": "Đề 1",
    "ma_de_goc": "H10000",
    "trang_thai": "cho_kiem_tra_hinh",
    "so_cau_da_tach": len(results),
    "cau_hoi": results,
}

RESULT_JSON.write_text(
    json.dumps(
        result_data,
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)


# ============================================================
# 6. TẠO HTML XEM TRƯỚC 10 CÂU
# ============================================================

html_parts = [
    "<!DOCTYPE html>",
    '<html lang="vi">',
    "<head>",
    '<meta charset="utf-8">',
    '<meta name="viewport" '
    'content="width=device-width, initial-scale=1">',
    "<title>Mộc Hán - Kiểm tra câu HSK1</title>",
    "<style>",
    "*{box-sizing:border-box}",
    "body{font-family:Arial,sans-serif;"
    "background:#f8f0e5;color:#292929;"
    "margin:0;padding:24px}",
    "main{max-width:1050px;margin:auto}",
    "h1{font-size:27px}",
    "h2{margin-top:30px;font-size:20px}",
    ".grid{display:grid;"
    "grid-template-columns:repeat(2,minmax(0,1fr));"
    "gap:16px}",
    ".card{background:#fffaf3;"
    "border:2px solid #333;"
    "border-radius:10px;padding:16px}",
    ".card h3{margin:0 0 12px}",
    ".image{min-height:170px;"
    "display:flex;align-items:center;"
    "justify-content:center;"
    "background:white;border:1px solid #ddd;"
    "padding:12px}",
    ".image img{max-width:100%;"
    "max-height:220px;object-fit:contain}",
    ".answer{margin-top:12px;"
    "color:#666;font-size:14px}",
    ".notice{background:#fff;"
    "padding:14px;border-radius:8px}",
    "@media(max-width:650px){"
    ".grid{grid-template-columns:1fr}}",
    "</style>",
    "</head>",
    "<body><main>",
    "<h1>HSK1 - Đề 1 (H10000)</h1>",
    '<p class="notice">',
    "Đây là bản xem trước 10 câu đã tách từ PDF gốc. "
    "Đáp án chỉ dùng để kiểm tra dữ liệu, "
    "không hiển thị trong lúc thi thật.",
    "</p>",
]


for skill, title in [
    ("nghe", "Phần Nghe - Câu 1 đến 5"),
    ("doc", "Phần Đọc - Câu 21 đến 25"),
]:

    html_parts.append(
        f"<h2>{escape(title)}</h2>"
    )

    html_parts.append('<div class="grid">')

    for item in results:

        if item["ky_nang"] != skill:
            continue

        number = item["so_cau"]
        image_path = escape(
            item["anh_cau_hoi"],
            quote=True,
        )
        answer = escape(
            str(item["dap_an_goc"])
        )

        html_parts.extend([
    '<article class="card">',
    f"<h3>Câu {number}</h3>",
    '<div class="image">',
    f'<img src="{image_path}" '
    f'alt="Nội dung câu {number}">',
    "</div>",
    "</article>",
])

    html_parts.append("</div>")


html_parts.extend([
    "</main></body></html>"
])

HTML_PATH.write_text(
    "\n".join(html_parts),
    encoding="utf-8",
)


# ============================================================
# 7. THÔNG BÁO KẾT QUẢ
# ============================================================

print()
print("========== HOÀN THÀNH ==========")
print("Đề: HSK1 - Đề 1 (H10000)")
print("Câu Nghe đã tách: 5")
print("Câu Đọc đã tách: 5")
print("Tổng cộng:", len(results))
print()
print("Thư mục ảnh:", QUESTIONS_DIR)
print("JSON:", RESULT_JSON)
print("HTML:", HTML_PATH)
print()
print("Chưa thay đổi SQL Server.")
print("Chưa xử lý audio theo từng câu.")
