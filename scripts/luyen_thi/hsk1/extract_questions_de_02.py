
# -*- coding: utf-8 -*-
"""
MỘC HÁN - HSK1 / ĐỀ 2 - TÁCH THỬ CÂU HỎI

Mã đề: H10901

Bước đầu:
- Tìm các vùng ảnh trong PDF.
- Nhận diện 5 hàng ảnh theo vị trí.
- Tách thử câu 1-5 và 21-25.
- Ghép đáp án từ de_02_dap_an.json.
- Xuất PNG, JSON và HTML xem trước.

Vùng cắt tự động chỉ là ứng viên.
Phải kiểm tra hình trước khi sử dụng.

Không thay đổi Đề 1.
Không tạo de_02.json để import.
Không thay đổi SQL Server.
"""

import argparse
import itertools
import json

from html import escape
from pathlib import Path
from statistics import median, pstdev

import fitz


# ==================================================
# 1. ĐƯỜNG DẪN
# ==================================================

HSK1 = Path(__file__).resolve().parent

BASE = HSK1.parent

SOURCE = (
    BASE
    / "source"
    / "De_HSK"
    / "HSK1"
    / "Đề 2"
)

PDF = SOURCE / "H1 ĐỀ 2.pdf"

DATA = HSK1 / "data" / "de_02"

OUTPUT = HSK1 / "output" / "de_02"

IMAGES = OUTPUT / "questions"

ANSWERS = DATA / "de_02_dap_an.json"

RESULT = DATA / "hinh_cau_hoi_kiem_tra.json"

HTML = OUTPUT / "kiem_tra_10_cau.html"

RENDER_DPI = 220


# ==================================================
# 2. ĐỌC ĐÁP ÁN ĐÃ CHUẨN BỊ
# ==================================================

def load_answers():

    if not ANSWERS.is_file():
        raise FileNotFoundError(
            "Chưa có de_02_dap_an.json. "
            "Hãy chạy prepare_de_02.py trước."
        )

    data = json.loads(
        ANSWERS.read_text(
            encoding="utf-8-sig"
        )
    )

    if data.get("ma_de_goc") != "H10901":
        raise ValueError(
            "Mã đề JSON phải là H10901."
        )

    answers = {
        int(number): value
        for number, value
        in data["dap_an"].items()
    }

    numbers = (
        list(range(1, 6))
        + list(range(21, 26))
    )

    for number in numbers:
        if number not in answers:
            raise ValueError(
                f"Thiếu đáp án câu {number}."
            )

    return answers


# ==================================================
# 3. PHÁT HIỆN VÙNG ẢNH TRONG PDF
# ==================================================

def image_rectangles(page):
    """
    Lấy tọa độ ảnh hiển thị trên trang PDF.

    Không dùng tọa độ cố định của H10000.
    """

    found = {}

    for info in page.get_image_info():

        rect = (
            fitz.Rect(info["bbox"])
            & page.rect
        )

        if rect.is_empty:
            continue

        if (
            rect.width < 18
            or rect.height < 18
        ):
            continue

        # Bỏ ảnh quá rộng, ví dụ nền trang.
        if rect.width > page.rect.width * 0.75:
            continue

        if not (
            page.rect.height * 0.10
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
        key=lambda r: (r.y0, r.x0)
    )


# ==================================================
# 4. TÌM NĂM HÀNG ẢNH CÓ VỊ TRÍ PHÙ HỢP
# ==================================================

def pick_five(rects):
    """
    Tìm nhóm 5 ảnh xếp thành một cột,
    có khoảng cách hàng tương đối đều.

    Đây là nhận diện ứng viên, không phải
    xác nhận nội dung của từng câu hỏi.
    """

    if len(rects) < 5:
        raise ValueError(
            f"Chỉ tìm thấy {len(rects)} ảnh. "
            "Cần kiểm tra lại trang PDF."
        )

    best = None

    for combo in itertools.combinations(
        rects, 5
    ):

        ordered = sorted(
            combo,
            key=lambda r: (r.y0 + r.y1) / 2
        )

        ys = [
            (r.y0 + r.y1) / 2
            for r in ordered
        ]

        xs = [
            (r.x0 + r.x1) / 2
            for r in ordered
        ]

        gaps = [
            ys[index + 1] - ys[index]
            for index in range(4)
        ]

        if (
            min(gaps) < 25
            or max(gaps) > 190
        ):
            continue

        mean_gap = sum(gaps) / len(gaps)

        score = (
            pstdev(gaps) / mean_gap * 100
            + pstdev(xs) * 0.35
            + (20 if mean_gap < 48 else 0)
        )

        if (
            best is None
            or score < best[0]
        ):
            best = (
                score,
                ordered
            )

    if best is None:
        raise ValueError(
            "Không phát hiện được 5 hàng ảnh "
            "phù hợp. Không tự cắt bừa."
        )

    return best[1], best[0]


# ==================================================
# 5. XÁC ĐỊNH VÙNG CẮT
# ==================================================

def crop_for_question(
    page,
    rect,
    ordered,
    index,
    skill
):
    """
    Nghe:
        Giữ hình minh họa.

    Đọc:
        Thử giữ hình và nội dung
        nằm cùng hàng câu hỏi.
    """

    if skill == "nghe":

        region = fitz.Rect(
            rect.x0 - 5,
            rect.y0 - 5,
            rect.x1 + 5,
            rect.y1 + 5
        )

    else:

        centers = [
            (r.y0 + r.y1) / 2
            for r in ordered
        ]

        gap = median([
            centers[i + 1] - centers[i]
            for i in range(4)
        ])

        if index == 0:
            y0 = centers[0] - gap / 2
        else:
            y0 = (
                centers[index - 1]
                + centers[index]
            ) / 2

        if index == 4:
            y1 = centers[4] + gap / 2
        else:
            y1 = (
                centers[index]
                + centers[index + 1]
            ) / 2

        region = fitz.Rect(
            rect.x0 - 8,
            y0 + 1,
            rect.x0 + 255,
            y1 - 1
        )

    return region & page.rect


# ==================================================
# 6. TẠO HTML XEM TRƯỚC
# ==================================================

def make_html(results):

    parts = [
        '<!DOCTYPE html>',
        '<html lang="vi">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" '
        'content="width=device-width, initial-scale=1">',
        "<title>HSK1 Đề 2 - Kiểm tra ảnh</title>",
        "<style>",
        "body{font-family:Arial,sans-serif;"
        "background:#f8f0e5;color:#292929;"
        "padding:20px}",
        "main{max-width:1100px;margin:auto}",
        ".grid{display:grid;"
        "grid-template-columns:"
        "repeat(2,minmax(0,1fr));"
        "gap:16px}",
        ".card{background:white;"
        "border:1px solid #777;"
        "border-radius:10px;padding:14px}",
        "img{max-width:100%;"
        "max-height:320px;"
        "object-fit:contain}",
        ".notice{padding:12px;"
        "background:#fff2cf;"
        "border-radius:8px}",
        "@media(max-width:700px){"
        ".grid{grid-template-columns:1fr}}",
        "</style>",
        "</head>",
        "<body><main>",
        "<h1>HSK1 - Đề 2 (H10901)</h1>",
        '<p class="notice">',
        "<strong>Chưa duyệt ảnh.</strong> ",
        "Các vùng cắt được chọn tự động. ",
        "Cần đối chiếu PDF gốc trước khi "
        "dùng làm câu hỏi thực tế.",
        "</p>",
    ]

    groups = [
        ("nghe", "Nghe - Dự kiến câu 1-5"),
        ("doc", "Đọc - Dự kiến câu 21-25"),
    ]

    for skill, title in groups:

        parts.append(
            f"<h2>{escape(title)}</h2>"
        )

        parts.append('<div class="grid">')

        for row in results:

            if row["ky_nang"] != skill:
                continue

            number = row["so_cau"]

            page_number = row["trang_pdf"]

            image_path = escape(
                row["anh_cau_hoi"],
                quote=True
            )

            parts.extend([
                '<div class="card">',
                f"<h3>Câu {number} - "
                f"Trang {page_number}</h3>",
                f'<img src="{image_path}" '
                f'alt="Ảnh ứng viên câu {number}">',
                "<p>Chưa xác nhận ảnh đúng câu.</p>",
                "</div>",
            ])

        parts.append("</div>")

    parts.append("</main></body></html>")

    HTML.write_text(
        "\n".join(parts),
        encoding="utf-8"
    )


# ==================================================
# 7. CHƯƠNG TRÌNH CHÍNH
# ==================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Trích thử ảnh HSK1 Đề 2. "
            "Không nhập SQL."
        )
    )

    parser.add_argument(
        "--trang-nghe",
        type=int,
        default=2,
        help="Trang PDF ứng viên câu 1-5."
    )

    parser.add_argument(
        "--trang-doc",
        type=int,
        default=7,
        help="Trang PDF ứng viên câu 21-25."
    )

    args = parser.parse_args()

    answers = load_answers()

    if not PDF.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy PDF: {PDF}"
        )

    results = []

    with fitz.open(PDF) as document:

        sections = [
            ("nghe", args.trang_nghe, 1),
            ("doc", args.trang_doc, 21),
        ]

        for (
            skill,
            page_number,
            first_question
        ) in sections:

            if not (
                1 <= page_number <= len(document)
            ):
                raise ValueError(
                    f"Trang PDF không hợp lệ: "
                    f"{page_number}"
                )

            page = document[
                page_number - 1
            ]

            rects = image_rectangles(page)

            print()
            print(
                f"{skill.upper()} - "
                f"Trang {page_number}"
            )

            print(
                "Số vùng ảnh ứng viên:",
                len(rects)
            )

            for index, rect in enumerate(
                rects, 1
            ):
                print(
                    f"  Ảnh {index:02d}: "
                    f"x={rect.x0:.0f}-"
                    f"{rect.x1:.0f}, "
                    f"y={rect.y0:.0f}-"
                    f"{rect.y1:.0f}"
                )

            selected, score = pick_five(rects)

            print(
                "Đã tìm 5 hàng ảnh ứng viên. "
                "Cần kiểm tra bằng mắt."
            )

            for index, rect in enumerate(
                selected
            ):

                number = first_question + index

                crop = crop_for_question(
                    page,
                    rect,
                    selected,
                    index,
                    skill
                )

                if crop.is_empty:
                    raise ValueError(
                        f"Vùng cắt câu {number} "
                        "không hợp lệ."
                    )

                results.append((
                    page,
                    number,
                    skill,
                    page_number,
                    crop,
                    answers[number]
                ))

        # Chỉ xuất file sau khi cả hai
        # nhóm đã xác định được vùng cắt.

        IMAGES.mkdir(
            parents=True,
            exist_ok=True
        )

        DATA.mkdir(
            parents=True,
            exist_ok=True
        )

        OUTPUT.mkdir(
            parents=True,
            exist_ok=True
        )

        final_rows = []

        for (
            page,
            number,
            skill,
            page_number,
            crop,
            answer
        ) in results:

            filename = (
                f"cau_{number:02d}.png"
            )

            output_file = (
                IMAGES / filename
            )

            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(
                    RENDER_DPI / 72,
                    RENDER_DPI / 72
                ),
                clip=crop,
                alpha=False
            )

            pixmap.save(
                str(output_file)
            )

            item = {
                "so_cau": number,
                "ky_nang": skill,
                "trang_pdf": page_number,
                "anh_cau_hoi": (
                    f"questions/{filename}"
                ),
                "dap_an_goc": answer,
                "vung_cat_pdf": [
                    round(value, 2)
                    for value in crop
                ],
                "da_kiem_tra_hinh": False
            }

            final_rows.append(item)

            print(
                f"Đã xuất ảnh ứng viên "
                f"câu {number:02d}"
            )

    # ==============================================
    # 8. LƯU JSON KIỂM TRA
    # ==============================================

    result_data = {
        "ma_de_goc": "H10901",
        "cap_hsk": 1,
        "ten_de": "Đề 2",
        "trang_thai": "cho_kiem_tra_hinh",
        "so_cau_da_tach": len(final_rows),
        "ghi_chu": (
            "Các vùng cắt chỉ là ứng viên, "
            "chưa xác nhận đúng câu hỏi."
        ),
        "cau_hoi": final_rows
    }

    RESULT.write_text(
        json.dumps(
            result_data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # ==============================================
    # 9. TẠO HTML XEM TRƯỚC
    # ==============================================

    make_html(final_rows)

    print()
    print("========== HOÀN THÀNH ==========")

    print("Đề: H10901")
    print("Ảnh ứng viên:", len(final_rows))
    print("Thư mục ảnh:", IMAGES)
    print("JSON kiểm tra:", RESULT)
    print("HTML xem trước:", HTML)
    print()
    print("Chưa xác nhận nội dung câu hỏi.")
    print("Chưa tạo de_02.json nhập SQL.")
    print("Không thay đổi SQL Server.")


if __name__ == "__main__":
    main()
