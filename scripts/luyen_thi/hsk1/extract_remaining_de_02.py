
# -*- coding: utf-8 -*-
"""
MỘC HÁN - HSK1 ĐỀ 2 (H10901)

TÁCH HÌNH ẢNH ĐỦ 40 CÂU

Đặc biệt:
- Câu 6-10 tự tìm ảnh nhúng trong PDF.
- Mở rộng mép trên để không cắt mất đầu ảnh.
- Giữ nguyên 10 câu đã tách trước.
- Giữ nguyên các phần Đọc và bảng A-F.
- Xuất JSON và HTML để kiểm tra.

Không sửa Đề 1.
Không tạo JSON nhập SQL.
Không thay đổi SQL Server.
"""

import json
from html import escape
from pathlib import Path

import fitz


# ==================================================
# 1. ĐƯỜNG DẪN
# ==================================================

HSK1 = Path(__file__).resolve().parent
BASE = HSK1.parent

PDF = (
    BASE / "source" / "De_HSK"
    / "HSK1" / "Đề 2" / "H1 ĐỀ 2.pdf"
)

DATA = HSK1 / "data" / "de_02"
OUTPUT = HSK1 / "output" / "de_02"

QUESTIONS = OUTPUT / "questions"
GROUPS = OUTPUT / "groups"

FIRST_10 = DATA / "hinh_cau_hoi_kiem_tra.json"
ANSWERS = DATA / "de_02_dap_an.json"

RESULT = DATA / "hinh_40_cau_ung_vien.json"
HTML = OUTPUT / "kiem_tra_40_cau_ung_vien.html"


# ==================================================
# 2. TỌA ĐỘ CẮT PDF
#
# (Trang, x0, y0, x1, y1)
#
# Câu 6-10:
# Đây chỉ là vùng tham chiếu để nhận diện
# đúng hàng ảnh. Mép trên sẽ được tính lại
# từ tọa độ ảnh thật trong PDF.
# ==================================================

REGIONS = {

    # Nghe phần 2
    6:  (3, 90, 340, 510, 445),
    7:  (3, 90, 485, 510, 585),
    8:  (3, 90, 630, 510, 735),
    9:  (4, 90, 142, 510, 250),
    10: (4, 90, 285, 510, 395),

    # Nghe phần 4 - giữ nguyên
    16: (6, 90, 318, 505, 386),
    17: (6, 90, 380, 505, 448),
    18: (6, 90, 442, 505, 509),
    19: (6, 90, 503, 505, 570),
    20: (6, 90, 565, 505, 634),

    # Đọc phần 3 - giữ nguyên
    31: (9, 88, 231, 365, 293),
    32: (9, 88, 294, 365, 355),
    33: (9, 88, 356, 365, 418),
    34: (9, 88, 419, 365, 481),
    35: (9, 88, 482, 365, 544),

    # Đọc phần 4 - giữ nguyên
    36: (10, 88, 306, 510, 371),
    37: (10, 88, 374, 510, 443),
    38: (10, 88, 445, 510, 511),
    39: (10, 88, 512, 510, 594),
    40: (10, 88, 596, 510, 691),
}

# Những câu tự xác định mép trên bằng ảnh gốc.
AUTO_TOP_QUESTIONS = {6, 7, 8, 9, 10}


# ==================================================
# 3. BẢNG LỰA CHỌN CHUNG
# ==================================================

SHARED = {

    "nghe_phan_3": (
        5, 84, 150, 510, 510
    ),

    "doc_phan_2": (
        8, 84, 150, 510, 530
    ),

    "doc_phan_3": (
        9, 367, 163, 520, 550
    ),

    "doc_phan_4": (
        10, 84, 160, 515, 245
    ),
}


# ==================================================
# 4. HÀM ĐỌC JSON
# ==================================================

def read_json(path):

    if not path.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy: {path}"
        )

    return json.loads(
        path.read_text(encoding="utf-8-sig")
    )


# ==================================================
# 5. XÁC ĐỊNH CẤU TRÚC CÂU HỎI
# ==================================================

def part_of(number):

    if number <= 20:
        return (number - 1) // 5 + 1

    return (number - 21) // 5 + 1


def question_type(number):

    if number <= 5 or 21 <= number <= 25:
        return "dung_sai"

    if 11 <= number <= 15:
        return "ghep_hinh_theo_audio"

    if 26 <= number <= 30:
        return "ghep_hinh_theo_noi_dung"

    if 31 <= number <= 40:
        return "ghep_cap"

    return "chon_mot"


def shared_for(number):

    if 11 <= number <= 15:
        return "groups/nghe_phan_3.png"

    if 26 <= number <= 30:
        return "groups/doc_phan_2.png"

    if 31 <= number <= 35:
        return "groups/doc_phan_3.png"

    if 36 <= number <= 40:
        return "groups/doc_phan_4.png"

    return None


# ==================================================
# 6. QUY ĐỔI TỌA ĐỘ PDF
# ==================================================

def get_region(page, region):

    _, x0, y0, x1, y1 = region

    scale_x = page.rect.width / 595.0
    scale_y = page.rect.height / 842.0

    rect = fitz.Rect(
        x0 * scale_x,
        y0 * scale_y,
        x1 * scale_x,
        y1 * scale_y,
    )

    return rect & page.rect


# ==================================================
# 7. TỰ XÁC ĐỊNH MÉP TRÊN CÂU 6-10
#
# Thay vì đoán y0, Python tìm ảnh thật
# trong ba cột A, B, C của hàng câu hỏi.
#
# Sau đó lấy mép trên nhỏ nhất trong ba ảnh.
# Nếu không tìm đủ ảnh, dừng để kiểm tra,
# không xuất ảnh có nguy cơ bị cắt mất.
# ==================================================

def adjust_photo_region(page, rect, number):

    scale_y = page.rect.height / 842.0

    row_center_y = (
        rect.y0 + rect.y1
    ) / 2

    column_width = rect.width / 3

    # Cho phép tìm ảnh bắt đầu phía trên
    # mép cắt cũ tối đa 120 point.
    search_top = max(
        page.rect.y0,
        rect.y0 - 120 * scale_y,
    )

    search_bottom = min(
        page.rect.y1,
        rect.y1 + 12 * scale_y,
    )

    candidates = []

    for info in page.get_image_info():

        image_rect = fitz.Rect(
            info["bbox"]
        )

        if (
            image_rect.width < 18
            or image_rect.height < 18
        ):
            continue

        center_x = (
            image_rect.x0 + image_rect.x1
        ) / 2

        center_y = (
            image_rect.y0 + image_rect.y1
        ) / 2

        # Chỉ lấy ảnh trong hàng đang xét.
        if not (
            rect.x0 <= center_x <= rect.x1
            and search_top <= center_y <= search_bottom
        ):
            continue

        candidates.append(image_rect)

    selected = []

    # Tìm ảnh ở từng cột A, B, C.
    for column in range(3):

        left = (
            rect.x0 + column * column_width
        )

        right = left + column_width

        matches = []

        for image_rect in candidates:

            center_x = (
                image_rect.x0 + image_rect.x1
            ) / 2

            if left <= center_x <= right:

                center_y = (
                    image_rect.y0 + image_rect.y1
                ) / 2

                distance = abs(
                    center_y - row_center_y
                )

                matches.append((
                    distance,
                    image_rect
                ))

        if not matches:

            raise RuntimeError(
                f"Câu {number}: không tìm thấy "
                f"ảnh ở cột {'ABC'[column]}. "
                "Cần kiểm tra tọa độ PDF."
            )

        matches.sort(
            key=lambda item: item[0]
        )

        selected.append(
            matches[0][1]
        )

    # Kiểm tra ba ảnh có nằm gần cùng hàng.
    centers_y = [
        (r.y0 + r.y1) / 2
        for r in selected
    ]

    if (
        max(centers_y) - min(centers_y)
        > 70 * scale_y
    ):
        raise RuntimeError(
            f"Câu {number}: ba ảnh không "
            "cùng hàng. Dừng để tránh "
            "cắt nhầm câu."
        )

    # Mép trên thực tế của ba ảnh.
    actual_top = min(
        image_rect.y0
        for image_rect in selected
    )

    # Chừa khoảng trắng 12 point.
    new_top = max(
        page.rect.y0,
        min(
            rect.y0,
            actual_top - 12 * scale_y,
        )
    )

    # Giữ mép dưới đã được thu gọn.
    adjusted = fitz.Rect(
        rect.x0,
        new_top,
        rect.x1,
        rect.y1,
    )

    print(
        f"  Câu {number:02d}: "
        f"mép trên {rect.y0:.1f}"
        f" -> {new_top:.1f}"
    )

    # Cảnh báo nếu ảnh vẫn chạm mép dưới.
    image_bottom = max(
        image_rect.y1
        for image_rect in selected
    )

    if image_bottom > adjusted.y1:

        print(
            f"  CẢNH BÁO câu {number}: "
            "ảnh có thể vượt mép dưới, "
            "cần kiểm tra HTML."
        )

    return adjusted


# ==================================================
# 8. CẮT ẢNH PDF
# ==================================================

def crop_pdf(
    document,
    region,
    destination,
    number=None,
):

    page_number = region[0]

    if not 1 <= page_number <= len(document):
        raise ValueError(
            f"Trang PDF không hợp lệ: "
            f"{page_number}"
        )

    page = document[page_number - 1]

    rect = get_region(page, region)

    if number in AUTO_TOP_QUESTIONS:

        rect = adjust_photo_region(
            page,
            rect,
            number,
        )

    if (
        rect.is_empty
        or rect.width < 12
        or rect.height < 12
    ):
        raise ValueError(
            "Vùng cắt không hợp lệ ở "
            f"trang {page_number}."
        )

    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(2.5, 2.5),
        clip=rect,
        colorspace=fitz.csRGB,
        alpha=False,
    )

    pixmap.save(
        str(destination)
    )

    return [
        round(value, 2)
        for value in rect
    ]


# ==================================================
# 9. TẠO HTML XEM TRƯỚC
# ==================================================

def create_html(questions):

    html = [
        "<!DOCTYPE html>",
        '<html lang="vi">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" '
        'content="width=device-width, initial-scale=1">',
        "<title>HSK1 Đề 2 - 40 câu</title>",

        "<style>",
        "*{box-sizing:border-box}",

        "body{"
        "font-family:Arial,sans-serif;"
        "margin:0;padding:20px;"
        "background:#f8f0e5;"
        "color:#292929"
        "}",

        "main{max-width:1120px;margin:auto}",

        "h1{font-size:28px}",

        "h2{"
        "font-size:22px;"
        "margin-top:30px"
        "}",

        "h3{"
        "font-size:18px;"
        "margin-top:24px"
        "}",

        ".grid{"
        "display:grid;"
        "grid-template-columns:"
        "repeat(2,minmax(0,1fr));"
        "gap:14px"
        "}",

        ".card,.group{"
        "background:white;"
        "border:1px solid #555;"
        "border-radius:9px;"
        "padding:14px;"
        "margin-bottom:14px"
        "}",

        ".card img{"
        "max-width:100%;"
        "max-height:340px;"
        "object-fit:contain"
        "}",

        ".group img{"
        "max-width:100%;"
        "max-height:650px;"
        "object-fit:contain"
        "}",

        ".warn{"
        "padding:14px;"
        "background:#fff1cc;"
        "border-radius:8px"
        "}",

        "@media(max-width:700px){"
        ".grid{grid-template-columns:1fr}"
        "}",

        "</style>",
        "</head>",
        "<body><main>",

        "<h1>HSK1 - Đề 2 (H10901)</h1>",

        '<p class="warn">',
        "<strong>CHƯA DUYỆT:</strong> ",
        "Câu 6-10 đã tự điều chỉnh mép trên ",
        "theo ảnh thật trong PDF. ",
        "Cần kiểm tra lại trước khi nhập SQL.",
        "</p>",
    ]

    for skill, title in [
        ("nghe", "Nghe hiểu"),
        ("doc", "Đọc hiểu"),
    ]:

        html.append(
            f"<h2>{escape(title)}</h2>"
        )

        for part in range(1, 5):

            items = [
                item
                for item in questions
                if item["ky_nang"] == skill
                and item["phan"] == part
            ]

            if not items:
                continue

            html.append(
                f"<h3>Phần {part}</h3>"
            )

            shared = items[0][
                "anh_nhom_lua_chon"
            ]

            if shared:

                src = escape(
                    shared,
                    quote=True
                )

                html.extend([
                    '<div class="group">',
                    "<strong>",
                    "Nhóm lựa chọn A-F",
                    "</strong>",
                    f'<p><img src="{src}" '
                    'alt="Nhóm lựa chọn"></p>',
                    "</div>",
                ])

            html.append('<div class="grid">')

            for item in items:

                number = item["so_cau"]

                image_path = item[
                    "anh_cau_hoi"
                ]

                html.extend([
                    '<article class="card">',
                    f"<h4>Câu {number}</h4>",
                ])

                if image_path:

                    src = escape(
                        image_path,
                        quote=True
                    )

                    html.append(
                        f'<img src="{src}" '
                        f'alt="Câu {number}">'
                    )

                else:

                    html.append(
                        "<p>Sử dụng bảng lựa chọn "
                        "chung phía trên.</p>"
                    )

                html.append("</article>")

            html.append("</div>")

    html.extend([
        "</main>",
        "</body>",
        "</html>",
    ])

    HTML.write_text(
        "\n".join(html),
        encoding="utf-8",
    )


# ==================================================
# 10. CHƯƠNG TRÌNH CHÍNH
# ==================================================

def main():

    print("=" * 50)
    print("HSK1 - ĐỀ 2 - H10901")
    print("=" * 50)

    if not PDF.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy PDF: {PDF}"
        )

    first_data = read_json(FIRST_10)

    answer_data = read_json(ANSWERS)

    if (
        first_data.get("ma_de_goc") != "H10901"
        or answer_data.get("ma_de_goc") != "H10901"
    ):
        raise ValueError(
            "Mã đề phải là H10901."
        )

    # ----------------------------------------------
    # 10.1. ĐỌC 10 CÂU ĐÃ TÁCH
    # ----------------------------------------------

    first_questions = {
        int(item["so_cau"]): item
        for item in first_data["cau_hoi"]
    }

    expected_first = (
        set(range(1, 6))
        | set(range(21, 26))
    )

    if set(first_questions) != expected_first:
        raise ValueError(
            "JSON 10 câu chưa đúng."
        )

    # ----------------------------------------------
    # 10.2. ĐỌC 40 ĐÁP ÁN
    # ----------------------------------------------

    answers = {
        int(number): answer
        for number, answer
        in answer_data["dap_an"].items()
    }

    if set(answers) != set(range(1, 41)):
        raise ValueError(
            "Chưa có đủ 40 đáp án."
        )

    # ----------------------------------------------
    # 10.3. KIỂM TRA 10 ẢNH CŨ
    # ----------------------------------------------

    for item in first_questions.values():

        image_path = item.get(
            "anh_cau_hoi"
        )

        if (
            not image_path
            or not (
                OUTPUT / image_path
            ).is_file()
        ):
            raise FileNotFoundError(
                "Thiếu ảnh đã tách: "
                f"{image_path}"
            )

    print("Đã kiểm tra 10 câu ban đầu.")
    print("Đã kiểm tra 40 đáp án.")

    # ----------------------------------------------
    # 10.4. TẠO THƯ MỤC
    # ----------------------------------------------

    QUESTIONS.mkdir(
        parents=True,
        exist_ok=True,
    )

    GROUPS.mkdir(
        parents=True,
        exist_ok=True,
    )

    DATA.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    crops = {}

    # ----------------------------------------------
    # 10.5. TÁCH ẢNH MỚI
    # ----------------------------------------------

    print("\n=== TÁCH ẢNH CÂU HỎI ===")

    with fitz.open(PDF) as document:

        if len(document) != 10:
            raise ValueError(
                "PDF Đề 2 phải có 10 trang."
            )

        for number, region in REGIONS.items():

            filename = (
                f"cau_{number:02d}.png"
            )

            destination = (
                QUESTIONS / filename
            )

            crops[number] = crop_pdf(
                document,
                region,
                destination,
                number=number,
            )

            print(
                f"Đã tách câu {number:02d}"
            )

        # ------------------------------------------
        # 10.6. BẢNG CHUNG
        # ------------------------------------------

        print("\n=== BẢNG LỰA CHỌN CHUNG ===")

        for name, region in SHARED.items():

            destination = (
                GROUPS / f"{name}.png"
            )

            crop_pdf(
                document,
                region,
                destination,
            )

            print(
                f"Đã tách: {name}"
            )

    # ----------------------------------------------
    # 10.7. GHÉP DANH SÁCH 40 CÂU
    # ----------------------------------------------

    questions = []

    for number in range(1, 41):

        original = first_questions.get(
            number,
            {}
        )

        if number in first_questions:

            image = original[
                "anh_cau_hoi"
            ]

        elif number in REGIONS:

            image = (
                f"questions/cau_{number:02d}.png"
            )

        else:
            image = None

        page_number = original.get(
            "trang_pdf"
        )

        if number in REGIONS:
            page_number = REGIONS[number][0]

        questions.append({

            "so_cau": number,

            "ky_nang": (
                "nghe"
                if number <= 20
                else "doc"
            ),

            "phan": part_of(number),

            "loai_cau_hoi": question_type(
                number
            ),

            "trang_pdf": page_number,

            "anh_cau_hoi": image,

            "anh_nhom_lua_chon": (
                shared_for(number)
            ),

            "dap_an_goc": answers[number],

            "vung_cat_pdf": crops.get(
                number,
                original.get("vung_cat_pdf")
            ),

            "da_kiem_tra_hinh": False,
        })

    if (
        len(questions) != 40
        or [q["so_cau"] for q in questions]
        != list(range(1, 41))
    ):
        raise RuntimeError(
            "Danh sách câu hỏi không hợp lệ."
        )

    # ----------------------------------------------
    # 10.8. LƯU JSON
    # ----------------------------------------------

    result_data = {
        "ma_de_goc": "H10901",
        "cap_hsk": 1,
        "ten_de": "Đề 2",
        "so_cau": 40,
        "so_cau_nghe": 20,
        "so_cau_doc": 20,
        "trang_thai": "cho_kiem_tra_hinh",
        "cau_hoi": questions,
    }

    RESULT.write_text(
        json.dumps(
            result_data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # ----------------------------------------------
    # 10.9. TẠO HTML
    # ----------------------------------------------

    create_html(questions)

    # ----------------------------------------------
    # 10.10. THÔNG BÁO
    # ----------------------------------------------

    print()
    print("========== HOÀN THÀNH ==========")
    print("Đề: H10901")
    print("Tổng số câu:", len(questions))
    print("Ảnh câu mới:", len(REGIONS))
    print("Bảng chung:", len(SHARED))
    print()
    print("JSON:", RESULT)
    print("HTML:", HTML)
    print()
    print("Cần kiểm tra ảnh câu 6-10.")
    print("Chưa tạo de_02.json nhập SQL.")
    print("Không thay đổi SQL Server.")


if __name__ == "__main__":
    main()
