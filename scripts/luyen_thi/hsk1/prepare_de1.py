
# -*- coding: utf-8 -*-
"""
MỘC HÁN - XỬ LÝ HSK1 ĐỀ 1 (H10000)

Nguồn:
    H10000.pdf
    H10000 答案.pdf
    H10000.mp3

Đầu ra:
    - Ảnh 11 trang đề
    - JSON xem trước
    - CSV 40 đáp án
    - HTML xem trước đề

Chưa kết nối hoặc thay đổi SQL Server.
"""

import csv
import html
import json
import re

from pathlib import Path
from urllib.parse import quote

try:
    import fitz
except ImportError:
    raise SystemExit(
        "Chưa cài PyMuPDF. "
        "Chạy: python -m pip install pymupdf"
    )


# ============================================================
# 1. ĐƯỜNG DẪN
# ============================================================

BASE = Path(__file__).resolve().parents[1]

SOURCE = BASE / "source" / "De_HSK" / "HSK1"

DATA = BASE / "hsk1" / "data" / "de_01"
OUTPUT = BASE / "hsk1" / "output" / "de_01"

PDF = SOURCE / "H10000.pdf"
ANSWER_PDF = SOURCE / "H10000 答案.pdf"
AUDIO = SOURCE / "H10000.mp3"


# ============================================================
# 2. KIỂM TRA FILE NGUỒN
# ============================================================

for file in (PDF, ANSWER_PDF, AUDIO):
    if not file.is_file():
        raise SystemExit(
            f"Không tìm thấy file nguồn: {file}"
        )

DATA.mkdir(parents=True, exist_ok=True)
OUTPUT.mkdir(parents=True, exist_ok=True)

print("Đã tìm thấy PDF, đáp án và MP3.")


# ============================================================
# 3. TRÍCH XUẤT ĐÁP ÁN
# ============================================================

with fitz.open(ANSWER_PDF) as doc:
    answer_text = "\n".join(
        page.get_text(sort=True)
        for page in doc
    )

pattern = re.compile(
    r"(?<!\d)(\d{1,2})\s*[．.、]\s*([A-F√×])"
)

answers = {}

for number_text, answer in pattern.findall(answer_text):

    number = int(number_text)

    if not 1 <= number <= 40:
        continue

    if (
        number in answers
        and answers[number] != answer
    ):
        raise SystemExit(
            f"Đáp án câu {number} bị mâu thuẫn."
        )

    answers[number] = answer


missing = [
    n for n in range(1, 41)
    if n not in answers
]

if missing:
    raise SystemExit(
        f"Thiếu đáp án: {missing}. "
        "Cần kiểm tra PDF trước khi tiếp tục."
    )

print("Đã lấy đủ 40 đáp án.")


# ============================================================
# 4. XÁC ĐỊNH TRANG CHỨA CÂU HỎI
#
# Chỉ dùng cho H10000 đã kiểm tra.
# Các đề khác sẽ có sơ đồ riêng nếu bố cục khác.
# ============================================================

def get_question_info(number):

    if 1 <= number <= 5:
        return "nghe", 1, 3

    if 6 <= number <= 8:
        return "nghe", 2, 4

    if 9 <= number <= 10:
        return "nghe", 2, 5

    if 11 <= number <= 15:
        return "nghe", 3, 6

    if 16 <= number <= 20:
        return "nghe", 4, 7

    if 21 <= number <= 25:
        return "doc", 1, 8

    if 26 <= number <= 30:
        return "doc", 2, 9

    if 31 <= number <= 35:
        return "doc", 3, 10

    return "doc", 4, 11


# ============================================================
# 5. XUẤT ẢNH VÀ VĂN BẢN CÁC TRANG PDF
# ============================================================

pages = []

with fitz.open(PDF) as doc:

    if len(doc) != 11:
        raise SystemExit(
            f"H10000 dự kiến 11 trang, "
            f"nhưng hiện có {len(doc)} trang."
        )

    for index, page in enumerate(doc, start=1):

        image_name = f"trang_{index:02d}.png"

        image = page.get_pixmap(
            dpi=140,
            alpha=False
        )

        image.save(OUTPUT / image_name)

        page_text = page.get_text(sort=True)

        text_path = DATA / f"trang_{index:02d}.txt"

        text_path.write_text(
            page_text,
            encoding="utf-8"
        )

        pages.append({
            "trang": index,
            "anh": image_name,
            "so_anh_nhung": len(page.get_images()),
            "so_ky_tu": len(page_text)
        })

        print(f"Đã xử lý trang {index}/11")


# ============================================================
# 6. TẠO DANH SÁCH 40 CÂU HỎI XEM TRƯỚC
#
# Chưa tự nhận dạng nội dung câu trong hình ảnh.
# Chưa chia thời gian nghe MP3.
# ============================================================

questions = []

for number in range(1, 41):

    skill, part, page = get_question_info(number)

    questions.append({
        "so_cau": number,
        "ky_nang": skill,
        "phan": part,
        "trang_pdf": page,
        "anh_trang": f"trang_{page:02d}.png",
        "dap_an_goc": answers[number],
        "noi_dung_cau_hoi": None,
        "lua_chon": [],
        "anh_cau_hoi": None,
        "bat_dau_audio": None,
        "ket_thuc_audio": None,
        "da_kiem_tra": False
    })


data = {
    "cap_hsk": 1,
    "ten_hien_thi": "Đề 1",
    "ma_de_goc": "H10000",
    "so_cau": 40,
    "so_cau_nghe": 20,
    "so_cau_doc": 20,
    "so_cau_viet": 0,
    "pdf_goc": PDF.name,
    "pdf_dap_an": ANSWER_PDF.name,
    "audio_goc": AUDIO.name,
    "trang_thai": "xem_truoc_chua_nhap_sql",
    "trang": pages,
    "cau_hoi": questions
}


# ============================================================
# 7. TẠO JSON
# ============================================================

json_path = DATA / "preview_de1.json"

json_path.write_text(
    json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    ),
    encoding="utf-8"
)


# ============================================================
# 8. TẠO CSV ĐÁP ÁN
# ============================================================

csv_path = DATA / "dap_an_de1.csv"

with csv_path.open(
    "w",
    encoding="utf-8-sig",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "SoCau",
        "KyNang",
        "Phan",
        "TrangPDF",
        "DapAn"
    ])

    for question in questions:

        writer.writerow([
            question["so_cau"],
            question["ky_nang"],
            question["phan"],
            question["trang_pdf"],
            question["dap_an_goc"]
        ])


# ============================================================
# 9. TẠO TRANG HTML XEM TRƯỚC
# ============================================================

audio_relative = "../../../source/De_HSK/HSK1/H10000.mp3"
audio_url = quote(audio_relative, safe="/.")

html_parts = [
    '<!DOCTYPE html>',
    '<html lang="vi">',
    '<head>',
    '<meta charset="utf-8">',
    '<title>HSK1 - Đề 1</title>',
    '<style>',
    'body {font-family:Arial,sans-serif;'
    'background:#f8f0e5;margin:24px;}',
    'main {max-width:1000px;margin:auto;}',
    'section {background:white;padding:18px;'
    'margin:20px 0;border-radius:10px;}',
    'img {width:100%;height:auto;}',
    'table {border-collapse:collapse;width:100%;}',
    'th,td {border:1px solid #ddd;'
    'padding:7px;text-align:center;}',
    'audio {width:100%;}',
    '</style>',
    '</head>',
    '<body>',
    '<main>',
    '<h1>HSK1 - Đề 1 (H10000)</h1>',
    '<p>Xem trước đề và kiểm tra đáp án.</p>',
    '<section>',
    '<h2>Âm thanh</h2>',
    f'<audio controls src="{audio_url}"></audio>',
    '</section>',
    '<section>',
    '<h2>Danh sách đáp án</h2>',
    '<table>',
    '<tr><th>Câu</th><th>Phần</th><th>Đáp án</th></tr>'
]

for question in questions:

    html_parts.append(
        f'<tr>'
        f'<td>{question["so_cau"]}</td>'
        f'<td>{html.escape(question["ky_nang"])}</td>'
        f'<td>{html.escape(question["dap_an_goc"])}</td>'
        f'</tr>'
    )

html_parts.append('</table></section>')

for page in pages:

    html_parts.append(
        f'<section>'
        f'<h2>Trang PDF {page["trang"]}</h2>'
        f'<img src="{page["anh"]}" '
        f'alt="Trang {page["trang"]}">'
        f'</section>'
    )

html_parts.extend([
    '</main>',
    '</body>',
    '</html>'
])

html_path = OUTPUT / "xem_truoc.html"

html_path.write_text(
    "\n".join(html_parts),
    encoding="utf-8"
)


# ============================================================
# 10. KẾT QUẢ
# ============================================================

print("\n========== HOÀN THÀNH ==========")
print("Cấp độ: HSK1")
print("Đề: Đề 1")
print("Mã gốc: H10000")
print("Số trang:", len(pages))
print("Số câu:", len(questions))
print("Đáp án:", len(answers))
print("Audio:", AUDIO.name)

print("\nJSON:", json_path)
print("CSV:", csv_path)
print("HTML:", html_path)

print("\nChưa nhập dữ liệu SQL Server.")
print("Chưa tách riêng từng câu hỏi và audio.")
