
# -*- coding: utf-8 -*-
"""
MỘC HÁN - HSK1 ĐỀ 8 (H11008)

TÁCH 10 CÂU HỎI CÓ HÌNH ẢNH RIÊNG

- Câu 1-5: Nghe hiểu - Phần 1
- Câu 21-25: Đọc hiểu - Phần 1

Phương pháp:
- Tìm ảnh nhúng trong PDF bằng PyMuPDF.
- Chọn 5 hình xếp thành một cột.
- Bỏ ảnh ví dụ ở đầu trang.
- Cắt từng câu thành ảnh PNG.
- Ghép đáp án từ de_08_dap_an.json.
- Tạo HTML kiểm tra ảnh.

HTML chỉ hiển thị số câu và hình ảnh.
Đáp án được giữ trong JSON.

CHỈ xử lý H11008 / de_08.
KHÔNG sửa các đề đã hoàn thành.
KHÔNG nhập SQL Server.
"""

import argparse
import itertools
import json

from html import escape
from pathlib import Path
from statistics import median, pstdev

import fitz


# ==================================================
# 1. CẤU HÌNH ĐỀ 8
# ==================================================

HSK1 = Path(__file__).resolve().parent

BASE = HSK1.parent

SOURCE = (
    BASE
    / "source"
    / "De_HSK"
    / "HSK1"
)

MA_DE = "H11008"

SO_DE = 8

PDF_FILE = SOURCE / "H11008.pdf"

DATA = HSK1 / "data" / "de_08"

OUTPUT = HSK1 / "output" / "de_08"

QUESTIONS = OUTPUT / "questions"

ANSWERS_FILE = (
    DATA / "de_08_dap_an.json"
)

RESULT_FILE = (
    DATA / "hinh_cau_hoi_kiem_tra.json"
)

HTML_FILE = (
    OUTPUT / "kiem_tra_10_cau.html"
)

RENDER_DPI = 220


# ==================================================
# 2. ĐỌC ĐÁP ÁN
# ==================================================

def load_answers():

    if not ANSWERS_FILE.is_file():

        raise FileNotFoundError(
            "Chưa có de_08_dap_an.json. "
            "Hãy chạy prepare_de_08.py trước."
        )

    data = json.loads(
        ANSWERS_FILE.read_text(
            encoding="utf-8-sig"
        )
    )

    if data.get("ma_de_goc") != MA_DE:

        raise ValueError(
            "Mã đề trong JSON phải là H11008."
        )

    raw = data.get("dap_an")

    if not isinstance(raw, dict):

        raise ValueError(
            "Không tìm thấy danh sách đáp án."
        )

    answers = {
        int(number): str(value).strip().upper()
        for number, value in raw.items()
    }

    if set(answers) != set(range(1, 41)):

        raise ValueError(
            "Đề 8 phải có đủ 40 đáp án."
        )

    return answers


# ==================================================
# 3. TÌM CÁC ẢNH NHÚNG TRONG PDF
# ==================================================

def image_rectangles(page):

    """
    Lấy tọa độ các ảnh hiển thị trên trang.

    Không dùng OCR và không tìm số câu
    bằng văn bản PDF.
    """

    found = {}

    for info in page.get_image_info():

        if "bbox" not in info:
            continue

        rect = (
            fitz.Rect(info["bbox"])
            & page.rect
        )

        if rect.is_empty:
            continue

        # Bỏ ảnh rất nhỏ.
        if (
            rect.width < 18
            or rect.height < 18
        ):
            continue

        # Bỏ ảnh nền hoặc ảnh chiếm phần lớn trang.
        if (
            rect.width > page.rect.width * 0.75
        ):
            continue

        # Bỏ vùng tiêu đề và ví dụ phía trên.
        if not (
            page.rect.height * 0.33
            < rect.y0
            < page.rect.height * 0.95
        ):
            continue

        key = tuple(
            round(value, 1)
            for value in rect
        )

        found[key] = rect

    return sorted(
        found.values(),
        key=lambda rect: (
            (rect.y0 + rect.y1) / 2,
            (rect.x0 + rect.x1) / 2
        )
    )


# ==================================================
# 4. CHỌN NĂM HÌNH ỨNG VIÊN
# ==================================================

def pick_five(rects, page):

    """
    Chọn 5 ảnh có:
    - Vị trí theo chiều dọc tăng dần.
    - Khoảng cách hàng tương đối đều.
    - Tâm ảnh nằm gần cùng một cột.

    Ưu tiên các hình nằm bên dưới ví dụ.

    Kết quả phải kiểm tra bằng HTML.
    """

    if len(rects) < 5:

        raise RuntimeError(
            "Chỉ tìm thấy "
            f"{len(rects)} ảnh ứng viên, "
            "không đủ để tách 5 câu."
        )

    best = None

    last_center = max(
        (rect.y0 + rect.y1) / 2
        for rect in rects
    )

    for combination in itertools.combinations(
        rects, 5
    ):

        ordered = sorted(
            combination,
            key=lambda rect: (
                rect.y0 + rect.y1
            ) / 2
        )

        centers_y = [
            (rect.y0 + rect.y1) / 2
            for rect in ordered
        ]

        centers_x = [
            (rect.x0 + rect.x1) / 2
            for rect in ordered
        ]

        gaps = [
            centers_y[index + 1]
            - centers_y[index]
            for index in range(4)
        ]

        if min(gaps) < 25:
            continue

        if max(gaps) > 190:
            continue

        mean_gap = sum(gaps) / 4

        if mean_gap <= 0:
            continue

        score = (
            pstdev(gaps) / mean_gap * 100
            + pstdev(centers_x) * 0.35
            + max(
                0,
                last_center - centers_y[-1]
            ) * 0.10
        )

        if mean_gap < 48:
            score += 20

        if (
            centers_y[0]
            < page.rect.height * 0.40
        ):
            score += 15

        if (
            best is None
            or score < best[0]
        ):
            best = (
                score,
                ordered
            )

    if best is None:

        raise RuntimeError(
            "Không tìm được nhóm 5 ảnh "
            "xếp thành hàng phù hợp. "
            "Cần kiểm tra bố cục PDF H11008."
        )

    return best[1], best[0]


# ==================================================
# 5. XÁC ĐỊNH VÙNG CẮT TỪNG CÂU
# ==================================================

def crop_for_question(
    page,
    rect,
    ordered,
    index,
    skill
):

    if skill == "nghe":

        # Nghe phần 1 chỉ giữ hình minh họa.
        # Chừa viền để tránh mất đầu hoặc tay.
        crop = fitz.Rect(
            rect.x0 - 8,
            rect.y0 - 8,
            rect.x1 + 8,
            rect.y1 + 8
        )

    else:

        # Đọc phần 1 giữ cả hình và phần chữ
        # nằm bên phải trong cùng một hàng.

        centers = [
            (r.y0 + r.y1) / 2
            for r in ordered
        ]

        gaps = [
            centers[i + 1] - centers[i]
            for i in range(4)
        ]

        typical_gap = median(gaps)

        if index == 0:

            y0 = (
                centers[0] - typical_gap / 2
            )

        else:

            y0 = (
                centers[index - 1]
                + centers[index]
            ) / 2

        if index == 4:

            y1 = (
                centers[4] + typical_gap / 2
            )

        else:

            y1 = (
                centers[index]
                + centers[index + 1]
            ) / 2

        crop = fitz.Rect(
            rect.x0 - 12,
            y0 + 1,
            rect.x0 + 270,
            y1 - 1
        )

    return crop & page.rect


# ==================================================
# 6. TÁCH MỘT NHÓM NĂM CÂU
# ==================================================

def process_section(
    document,
    skill,
    page_number,
    start_number,
    answers
):

    if not 1 <= page_number <= len(document):

        raise ValueError(
            f"Trang PDF {page_number} "
            "không hợp lệ."
        )

    page = document[page_number - 1]

    rects = image_rectangles(page)

    print(
        "\n================================="
    )

    print(
        f"{skill.upper()} - TRANG {page_number}"
    )

    print(
        "================================="
    )

    print(
        "Số ảnh ứng viên:",
        len(rects)
    )

    for index, rect in enumerate(rects, 1):

        print(
            f"Ảnh {index:02d}: "
            f"x={rect.x0:.1f}-{rect.x1:.1f}, "
            f"y={rect.y0:.1f}-{rect.y1:.1f}"
        )

    selected, score = pick_five(
        rects,
        page
    )

    print(
        "Điểm chọn 5 ảnh:",
        round(score, 2)
    )

    result = []

    for index, rect in enumerate(selected):

        number = start_number + index

        crop = crop_for_question(
            page,
            rect,
            selected,
            index,
            skill
        )

        if (
            crop.is_empty
            or crop.width < 20
            or crop.height < 20
        ):

            raise ValueError(
                f"Câu {number}: "
                "vùng cắt không hợp lệ."
            )

        result.append({
            "so_cau": number,
            "ky_nang": skill,
            "trang_pdf": page_number,
            "dap_an_goc": answers[number],
            "crop": crop
        })

        print(
            f"Câu {number:02d}: "
            f"x={crop.x0:.1f}-{crop.x1:.1f}, "
            f"y={crop.y0:.1f}-{crop.y1:.1f}"
        )

    return result


# ==================================================
# 7. LƯU ẢNH PNG
# ==================================================

def export_images(document, rows):

    QUESTIONS.mkdir(
        parents=True,
        exist_ok=True
    )

    final_rows = []

    for item in rows:

        number = item["so_cau"]

        page_number = item["trang_pdf"]

        page = document[page_number - 1]

        crop = item["crop"]

        filename = f"cau_{number:02d}.png"

        destination = QUESTIONS / filename

        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(
                RENDER_DPI / 72,
                RENDER_DPI / 72
            ),
            clip=crop,
            colorspace=fitz.csRGB,
            alpha=False
        )

        pixmap.save(str(destination))

        final_rows.append({
            "so_cau": number,
            "ky_nang": item["ky_nang"],
            "trang_pdf": page_number,
            "anh_cau_hoi": (
                f"questions/{filename}"
            ),
            "dap_an_goc": item["dap_an_goc"],
            "vung_cat_pdf": [
                round(float(value), 2)
                for value in crop
            ],
            "da_kiem_tra_hinh": False
        })

        print(
            f"Đã xuất ảnh câu {number:02d}"
        )

    return final_rows


# ==================================================
# 8. TẠO HTML KIỂM TRA
# ==================================================

def make_html(rows):

    parts = [
        "<!DOCTYPE html>",
        '<html lang="vi">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" '
        'content="width=device-width,initial-scale=1">',

        "<title>HSK1 Đề 8 - Kiểm tra 10 câu</title>",

        "<style>",

        "*{box-sizing:border-box}",

        "body{"
        "font-family:Arial,sans-serif;"
        "background:#f4f6fa;"
        "color:#263238;"
        "padding:22px;"
        "margin:0"
        "}",

        "main{max-width:1100px;margin:auto}",

        "h1{margin-bottom:8px}",

        ".notice{"
        "background:#fff3d6;"
        "border:1px solid #ecd18f;"
        "padding:14px;"
        "border-radius:10px;"
        "line-height:1.6;"
        "margin-bottom:20px"
        "}",

        "section{margin:24px 0}",

        ".grid{"
        "display:grid;"
        "grid-template-columns:"
        "repeat(2,minmax(0,1fr));"
        "gap:14px"
        "}",

        ".card{"
        "background:white;"
        "border:1px solid #ddd;"
        "border-radius:10px;"
        "padding:14px;"
        "min-width:0"
        "}",

        ".card h3{"
        "margin:0 0 10px;"
        "color:#1752a5"
        "}",

        ".card img{"
        "display:block;"
        "max-width:100%;"
        "max-height:350px;"
        "object-fit:contain"
        "}",

        "@media(max-width:720px){"
        ".grid{grid-template-columns:1fr}"
        "}",

        "</style>",

        "</head>",
        "<body><main>",

        f"<h1>HSK1 - Đề {SO_DE} ({MA_DE})</h1>",

        '<div class="notice">',
        "Kiểm tra 10 ảnh đã cắt từ PDF H11008. "
        "Cần bảo đảm đúng thứ tự câu và "
        "không bị cắt mất nội dung.",
        "</div>",
    ]

    sections = [
        ("nghe", "Nghe hiểu - Phần 1 (1-5)"),
        ("doc", "Đọc hiểu - Phần 1 (21-25)")
    ]

    for skill, title in sections:

        parts.append(
            f"<section><h2>{escape(title)}</h2>"
        )

        parts.append('<div class="grid">')

        for item in rows:

            if item["ky_nang"] != skill:
                continue

            number = item["so_cau"]

            src = escape(
                item["anh_cau_hoi"],
                quote=True
            )

            parts.extend([
                '<article class="card">',
                f"<h3>Câu {number:02d}</h3>",
                f'<img src="{src}" '
                f'alt="Câu {number}">',
                "</article>"
            ])

        parts.append("</div></section>")

    parts.extend([
        "</main>",
        "</body>",
        "</html>"
    ])

    HTML_FILE.write_text(
        "\n".join(parts),
        encoding="utf-8"
    )


# ==================================================
# 9. CHƯƠNG TRÌNH CHÍNH
# ==================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Tách 10 câu đầu của HSK1 Đề 8."
        )
    )

    parser.add_argument(
        "--trang-nghe",
        type=int,
        default=2,
        help="Trang PDF câu 1-5, mặc định 2."
    )

    parser.add_argument(
        "--trang-doc",
        type=int,
        default=7,
        help="Trang PDF câu 21-25, mặc định 7."
    )

    args = parser.parse_args()

    print("=" * 55)
    print("MỘC HÁN - HSK1 ĐỀ 8")
    print("Mã đề:", MA_DE)
    print("=" * 55)

    if not PDF_FILE.is_file():

        raise FileNotFoundError(
            f"Không tìm thấy PDF: {PDF_FILE}"
        )

    answers = load_answers()

    print("Đã kiểm tra đủ 40 đáp án.")

    rows = []

    with fitz.open(PDF_FILE) as document:

        print(
            "Số trang PDF:",
            len(document)
        )

        sections = [
            ("nghe", args.trang_nghe, 1),
            ("doc", args.trang_doc, 21)
        ]

        for (
            skill,
            page_number,
            start_number
        ) in sections:

            rows.extend(
                process_section(
                    document,
                    skill,
                    page_number,
                    start_number,
                    answers
                )
            )

        expected_numbers = (
            list(range(1, 6))
            + list(range(21, 26))
        )

        actual_numbers = [
            item["so_cau"]
            for item in rows
        ]

        if actual_numbers != expected_numbers:

            raise RuntimeError(
                "Danh sách 10 câu chưa đúng."
            )

        DATA.mkdir(
            parents=True,
            exist_ok=True
        )

        OUTPUT.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            "\n========== XUẤT ẢNH =========="
        )

        final_rows = export_images(
            document,
            rows
        )

    result = {
        "ma_de_goc": MA_DE,
        "cap_hsk": 1,
        "ten_de": "Đề 8",
        "trang_thai": "cho_kiem_tra_hinh",
        "so_cau_da_tach": 10,
        "ghi_chu": (
            "Ảnh ứng viên từ H11008.pdf. "
            "Cần kiểm tra HTML."
        ),
        "cau_hoi": final_rows
    }

    RESULT_FILE.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    make_html(final_rows)

    print(
        "\n========== HOÀN THÀNH =========="
    )

    print("Mã đề:", MA_DE)
    print("Tổng ảnh:", len(final_rows), "/10")
    print("JSON:", RESULT_FILE)
    print("HTML:", HTML_FILE)

    print(
        "\nChưa tách 30 câu còn lại."
    )

    print(
        "Chưa tạo JSON nhập SQL."
    )

    print(
        "Chưa thay đổi SQL Server."
    )


if __name__ == "__main__":
    main()
