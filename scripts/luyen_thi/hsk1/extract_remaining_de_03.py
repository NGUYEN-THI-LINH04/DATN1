
# -*- coding: utf-8 -*-
"""
MỘC HÁN - HSK1 ĐỀ 3 (H10902)

Tách ảnh phần còn lại của đề thi.

- Giữ nguyên 10 ảnh câu 1-5 và 21-25.
- Giữ nguyên cách tách Nghe phần 2-4.
- Bổ sung nội dung câu 26-30.
- Điều chỉnh vùng câu 34-35, 39-40.
- Thu khoảng trắng quanh câu đọc.
- Ghép JSON đủ 40 câu và HTML kiểm tra.

Các vùng cắt vẫn phải kiểm tra trên PDF gốc.
Không nhập SQL Server.
"""

import argparse
import json

from html import escape
from pathlib import Path

import fitz


# ==================================================
# 1. ĐƯỜNG DẪN
# ==================================================

HSK1 = Path(__file__).resolve().parent

SOURCE = (
    HSK1.parent
    / "source"
    / "De_HSK"
    / "HSK1"
)


# ==================================================
# 2. VÙNG CẮT CÂU HỎI
# ==================================================

# Định dạng:
# (trang_pdf, x0, y0, x1, y1)
#
# Hệ tọa độ tham chiếu: 595 x 842.
#
# Câu 26-30, 34-35, 39-40 có vùng cắt mới.
# Phải kiểm tra HTML trước khi chuẩn hóa.

REGIONS = {

    # ----------------------------------------------
    # NGHE - PHẦN 2
    # Giữ cách xử lý đã chạy được.
    # ----------------------------------------------

    6:  (3, 90, 340, 510, 445),
    7:  (3, 90, 485, 510, 585),
    8:  (3, 90, 630, 510, 735),
    9:  (4, 90, 142, 510, 250),
    10: (4, 90, 285, 510, 395),

    # ----------------------------------------------
    # NGHE - PHẦN 4
    # ----------------------------------------------

    16: (6, 90, 318, 505, 386),
    17: (6, 90, 380, 505, 448),
    18: (6, 90, 442, 505, 509),
    19: (6, 90, 503, 505, 570),
    20: (6, 90, 565, 505, 634),

    # ----------------------------------------------
    # ĐỌC - PHẦN 2
    # Bổ sung câu 26-30 dưới bảng A-F.
    # Tọa độ dự kiến trên trang 8.
    # ----------------------------------------------

    26: (8, 85, 541, 515, 590),
    27: (8, 85, 590, 515, 643),
    28: (8, 85, 643, 515, 696),
    29: (8, 85, 696, 515, 750),
    30: (8, 85, 750, 515, 818),

    # ----------------------------------------------
    # ĐỌC - PHẦN 3
    # Điều chỉnh câu 34-35.
    # ----------------------------------------------

    31: (9, 88, 231, 365, 293),
    32: (9, 88, 294, 365, 355),
    33: (9, 88, 356, 365, 418),
    34: (9, 88, 419, 365, 522),
    35: (9, 88, 523, 365, 650),

    # ----------------------------------------------
    # ĐỌC - PHẦN 4
    # Mở rộng câu 39, dịch vùng câu 40 xuống.
    # ----------------------------------------------

    36: (10, 88, 306, 510, 371),
    37: (10, 88, 374, 510, 443),
    38: (10, 88, 445, 510, 511),
    39: (10, 88, 512, 510, 639),
    40: (10, 88, 640, 510, 735),

}


# ==================================================
# 3. BẢNG LỰA CHỌN CHUNG
# ==================================================

SHARED = {

    "nghe_phan_3": (
        5, 84, 150, 510, 510
    ),

    "doc_phan_2": (
        8, 84, 150, 510, 510
    ),

    "doc_phan_3": (
        9, 367, 163, 520, 567
    ),

    "doc_phan_4": (
        10, 84, 160, 515, 228
    ),

}


FIRST = (
    set(range(1, 6))
    | set(range(21, 26))
)


GROUP_RANGES = {

    "nghe_phan_3": range(11, 16),

    "doc_phan_2": range(26, 31),

    "doc_phan_3": range(31, 36),

    "doc_phan_4": range(36, 41),

}


# ==================================================
# 4. ĐỌC JSON
# ==================================================

def read_json(path):

    if not path.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )


# ==================================================
# 5. KIỂM TRA VÙNG CẮT
# ==================================================

def validate_region(region, label):

    if (
        not isinstance(region, (tuple, list))
        or len(region) != 5
    ):
        raise ValueError(
            f"{label}: phải gồm "
            "[trang, x0, y0, x1, y1]"
        )

    page_number = int(region[0])

    x0, y0, x1, y1 = map(
        float,
        region[1:]
    )

    if (
        page_number < 1
        or x0 < 0
        or y0 < 0
        or x0 >= x1
        or y0 >= y1
    ):
        raise ValueError(
            f"{label}: tọa độ không hợp lệ."
        )

    return (
        page_number,
        x0, y0, x1, y1
    )


# ==================================================
# 6. CẤU HÌNH DÙNG LẠI CHO ĐỀ SAU
# ==================================================

def load_config(path):

    regions = dict(REGIONS)
    shared = dict(SHARED)

    if path is not None:

        config = read_json(path)

        for key, value in config.get(
            "regions", {}
        ).items():

            number = int(key)

            if number not in regions:
                raise ValueError(
                    f"Số câu không hợp lệ: {number}"
                )

            regions[number] = validate_region(
                value,
                f"Câu {number}"
            )

        for key, value in config.get(
            "shared", {}
        ).items():

            if key not in shared:
                raise ValueError(
                    f"Tên nhóm không hợp lệ: {key}"
                )

            shared[key] = validate_region(
                value,
                key
            )

    return regions, shared


# ==================================================
# 7. QUY ĐỔI TỌA ĐỘ PDF
# ==================================================

def scale_rect(page, region):

    _, x0, y0, x1, y1 = region

    scale_x = (
        page.rect.width / 595.0
    )

    scale_y = (
        page.rect.height / 842.0
    )

    rect = fitz.Rect(

        x0 * scale_x,
        y0 * scale_y,

        x1 * scale_x,
        y1 * scale_y

    )

    return rect & page.rect


# ==================================================
# 8. ĐIỀU CHỈNH ẢNH CÂU 6-10
# ==================================================

def adjust_photo_row(
    page,
    rect,
    number
):

    """
    Giữ phương pháp Đề 2.

    Tìm ba hình ảnh A, B, C thực tế
    trong PDF và mở rộng mép cắt khi cần.
    """

    scale_y = (
        page.rect.height / 842.0
    )

    target_y = (
        rect.y0 + rect.y1
    ) / 2

    search_top = max(
        page.rect.y0,
        rect.y0 - 120 * scale_y
    )

    search_bottom = min(
        page.rect.y1,
        rect.y1 + 12 * scale_y
    )

    images = []

    for info in page.get_image_info():

        image_rect = (
            fitz.Rect(info["bbox"])
            & page.rect
        )

        if (
            image_rect.is_empty
            or image_rect.width < 18
            or image_rect.height < 18
        ):
            continue

        center_x = (
            image_rect.x0 + image_rect.x1
        ) / 2

        center_y = (
            image_rect.y0 + image_rect.y1
        ) / 2

        if (
            rect.x0 <= center_x <= rect.x1
            and search_top
            <= center_y
            <= search_bottom
        ):
            images.append(image_rect)

    selected = []

    for column in range(3):

        left = (
            rect.x0
            + column * rect.width / 3
        )

        right = (
            left + rect.width / 3
        )

        matches = []

        for image_rect in images:

            center_x = (
                image_rect.x0 + image_rect.x1
            ) / 2

            if left <= center_x <= right:

                center_y = (
                    image_rect.y0 + image_rect.y1
                ) / 2

                distance = abs(
                    center_y - target_y
                )

                matches.append((
                    distance,
                    image_rect
                ))

        if not matches:
            raise RuntimeError(
                f"Câu {number}: không thấy "
                f"ảnh cột {'ABC'[column]}."
            )

        matches.sort(
            key=lambda item: item[0]
        )

        selected.append(
            matches[0][1]
        )

    centers = [
        (r.y0 + r.y1) / 2
        for r in selected
    ]

    if (
        max(centers) - min(centers)
        > 70 * scale_y
    ):
        raise RuntimeError(
            f"Câu {number}: ba hình "
            "không cùng một hàng."
        )

    actual_top = min(
        r.y0 for r in selected
    )

    actual_bottom = max(
        r.y1 for r in selected
    )

    new_top = max(
        page.rect.y0,
        min(
            rect.y0,
            actual_top - 12 * scale_y
        )
    )

    new_bottom = min(
        page.rect.y1,
        max(
            rect.y1,
            actual_bottom + 8 * scale_y
        )
    )

    return fitz.Rect(
        rect.x0,
        new_top,
        rect.x1,
        new_bottom
    )


# ==================================================
# 9. THU KHOẢNG TRẮNG QUANH CÂU ĐỌC
# ==================================================

def tighten_to_content(
    page,
    rect,
    margin=9
):

    """
    Tự tìm vùng chữ và hình có màu tối
    trong ảnh PDF để bỏ bớt khoảng trắng.

    Không sử dụng OCR.
    Giữ khoảng đệm bảo vệ dấu và chữ Hán.
    """

    zoom = 1.5

    pixmap = page.get_pixmap(

        matrix=fitz.Matrix(
            zoom, zoom
        ),

        clip=rect,

        colorspace=fitz.csGRAY,

        alpha=False

    )

    width = pixmap.width
    height = pixmap.height
    stride = pixmap.stride

    pixels = pixmap.samples

    left = width
    top = height

    right = -1
    bottom = -1

    for y in range(height):

        row = pixels[
            y * stride:
            y * stride + width
        ]

        for x, value in enumerate(row):

            if value < 208:

                left = min(left, x)
                top = min(top, y)

                right = max(right, x)
                bottom = max(bottom, y)

    if right < 0:
        return rect

    padding = margin * zoom

    result = fitz.Rect(

        rect.x0 + max(
            0,
            left - padding
        ) / zoom,

        rect.y0 + max(
            0,
            top - padding
        ) / zoom,

        rect.x0 + min(
            width,
            right + padding
        ) / zoom,

        rect.y0 + min(
            height,
            bottom + padding
        ) / zoom

    ) & rect

    if (
        result.width < 60
        or result.height < 15
    ):
        return rect

    return result


# ==================================================
# 10. LÊN KẾ HOẠCH CẮT
# ==================================================

def plan_crop(
    document,
    region,
    label,
    number=None
):

    page_number = int(region[0])

    if not (
        1 <= page_number <= len(document)
    ):
        raise ValueError(
            f"{label}: trang {page_number} "
            "không tồn tại."
        )

    page = document[
        page_number - 1
    ]

    rect = scale_rect(
        page,
        region
    )

    if number in range(6, 11):

        rect = adjust_photo_row(
            page,
            rect,
            number
        )

    # Chỉ thu vùng các câu đọc mới.
    # Không tác động ảnh Nghe và bảng nhóm.
    if number in range(26, 41):

        rect = tighten_to_content(
            page,
            rect,
            margin=8
        )

    if (
        rect.is_empty
        or rect.width < 15
        or rect.height < 15
    ):
        raise ValueError(
            f"{label}: vùng cắt không hợp lệ."
        )

    return page_number, rect


# ==================================================
# 11. LƯU ẢNH
# ==================================================

def save_crop(
    document,
    plan,
    destination
):

    page_number, rect = plan

    page = document[
        page_number - 1
    ]

    pixmap = page.get_pixmap(

        matrix=fitz.Matrix(
            2.6, 2.6
        ),

        clip=rect,

        colorspace=fitz.csRGB,

        alpha=False

    )

    pixmap.save(
        str(destination)
    )


# ==================================================
# 12. THÔNG TIN CÂU HỎI
# ==================================================

def skill_part(number):

    if number <= 20:

        return (
            "nghe",
            (number - 1) // 5 + 1
        )

    return (
        "doc",
        (number - 21) // 5 + 1
    )


def question_type(number):

    if (
        number <= 5
        or 21 <= number <= 25
    ):
        return "dung_sai"

    if 11 <= number <= 15:
        return "ghep_hinh_theo_audio"

    if 26 <= number <= 30:
        return "ghep_hinh_theo_noi_dung"

    if number >= 31:
        return "ghep_cap"

    return "chon_mot"


def shared_for(number):

    for name, numbers in GROUP_RANGES.items():

        if number in numbers:

            return (
                f"groups/{name}.png"
            )

    return None


# ==================================================
# 13. HTML KIỂM TRA
# ==================================================

def make_html(
    questions,
    html_file,
    ma_de,
    so_de
):

    by_number = {
        item["so_cau"]: item
        for item in questions
    }

    parts = [f"""
<!DOCTYPE html>
<html lang="vi">
<head>

<meta charset="utf-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>HSK1 Đề {so_de} - Kiểm tra 40 câu</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background: #f4f6fa;
    color: #263238;
}}

main {{
    max-width: 1150px;
    margin: auto;
}}

section {{
    background: white;
    border-radius: 12px;
    padding: 18px;
    margin: 22px 0;
}}

.grid {{
    display: grid;
    grid-template-columns:
        repeat(2, minmax(0, 1fr));
    gap: 14px;
}}

.card,
.shared {{
    border: 1px solid #d9dfe8;
    border-radius: 9px;
    padding: 13px;
    background: white;
}}

.card h4 {{
    margin: 0 0 10px;
    color: #1752a5;
}}

.card img {{
    width: 100%;
    height: auto;
    display: block;
    object-fit: contain;
}}

.shared {{
    margin-bottom: 14px;
}}

.shared img {{
    display: block;
    width: 100%;
    height: auto;
    max-height: 750px;
    object-fit: contain;
}}

.notice {{
    background: #fff5d9;
    padding: 12px;
    border-radius: 8px;
    line-height: 1.5;
}}

@media(max-width:720px) {{
    .grid {{
        grid-template-columns: 1fr;
    }}
}}

</style>
</head>

<body>
<main>

<h1>
HSK1 - Đề {so_de} ({escape(ma_de)})
</h1>

<div class="notice">
Ảnh ứng viên chưa duyệt.
Cần kiểm tra kỹ câu 26-30, 34-35 và 39-40
với PDF gốc.
</div>
"""]

    for skill, label in [

        ("nghe", "Nghe hiểu"),

        ("doc", "Đọc hiểu")

    ]:

        for part in range(1, 5):

            numbers = [

                number

                for number in range(1, 41)

                if skill_part(number)
                == (skill, part)

            ]

            first_item = by_number[
                numbers[0]
            ]

            parts.append(
                "<section>"
                f"<h2>{label} - Phần {part}</h2>"
            )

            # --------------------------------------
            # BẢNG LỰA CHỌN CHUNG
            # --------------------------------------

            shared_image = first_item.get(
                "anh_nhom_lua_chon"
            )

            if shared_image:

                src = escape(
                    shared_image,
                    quote=True
                )

                parts.append(
                    '<div class="shared">'
                    "<strong>Bảng lựa chọn chung</strong>"
                    f'<img src="{src}" '
                    'alt="Bảng lựa chọn">'
                    "</div>"
                )

            parts.append(
                '<div class="grid">'
            )

            # --------------------------------------
            # TỪNG CÂU HỎI
            # --------------------------------------

            for number in numbers:

                item = by_number[number]

                image_path = item.get(
                    "anh_cau_hoi"
                )

                parts.append(
                    '<article class="card">'
                    f"<h4>Câu {number:02d}</h4>"
                )

                if image_path:

                    src = escape(
                        image_path,
                        quote=True
                    )

                    # Nhấn vào ảnh để mở kích thước lớn.
                    parts.append(
                        f'<a href="{src}" '
                        'target="_blank">'
                        f'<img src="{src}" '
                        f'alt="Câu {number}">'
                        "</a>"
                    )

                parts.append("</article>")

            parts.append(
                "</div></section>"
            )

    parts.append(
        "</main></body></html>"
    )

    html_file.write_text(
        "\n".join(parts),
        encoding="utf-8"
    )


# ==================================================
# 14. CHƯƠNG TRÌNH CHÍNH
# ==================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Tách ảnh HSK1 phần còn lại. "
            "Không nhập SQL."
        )
    )

    parser.add_argument(
        "--ma-de",
        default="H10902"
    )

    parser.add_argument(
        "--de",
        type=int,
        default=3
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="JSON cấu hình tọa độ riêng."
    )

    args = parser.parse_args()

    ma_de = (
        args.ma_de.strip().upper()
    )

    if (
        args.de < 1
        or not ma_de
    ):
        raise ValueError(
            "Mã đề hoặc số đề không hợp lệ."
        )

    folder_name = (
        f"de_{args.de:02d}"
    )

    pdf_file = (
        SOURCE / f"{ma_de}.pdf"
    )

    data_dir = (
        HSK1 / "data" / folder_name
    )

    output_dir = (
        HSK1 / "output" / folder_name
    )

    questions_dir = (
        output_dir / "questions"
    )

    groups_dir = (
        output_dir / "groups"
    )

    answer_file = (
        data_dir
        / f"{folder_name}_dap_an.json"
    )

    first_file = (
        data_dir
        / "hinh_cau_hoi_kiem_tra.json"
    )

    result_file = (
        data_dir
        / "hinh_40_cau_ung_vien.json"
    )

    html_file = (
        output_dir
        / "kiem_tra_40_cau_ung_vien.html"
    )

    print("=" * 55)

    print(
        f"MỘC HÁN - HSK1 ĐỀ {args.de}"
    )

    print(
        "Mã đề:", ma_de
    )

    print("=" * 55)

    # ----------------------------------------------
    # 14.1. KIỂM TRA FILE NGUỒN
    # ----------------------------------------------

    if not pdf_file.is_file():
        raise FileNotFoundError(
            f"Thiếu PDF: {pdf_file}"
        )

    first_json = read_json(
        first_file
    )

    answers_json = read_json(
        answer_file
    )

    if (
        first_json.get("ma_de_goc") != ma_de
        or answers_json.get("ma_de_goc") != ma_de
    ):
        raise ValueError(
            "Mã đề PDF và JSON không khớp."
        )

    # ----------------------------------------------
    # 14.2. ĐỌC 10 ẢNH ĐÃ HOÀN THÀNH
    # ----------------------------------------------

    first_questions = {

        int(item["so_cau"]): item

        for item in first_json["cau_hoi"]

    }

    answers = {

        int(key): str(value).strip()

        for key, value
        in answers_json["dap_an"].items()

    }

    if set(first_questions) != FIRST:

        raise ValueError(
            "Thiếu 10 câu đầu "
            "(1-5 và 21-25)."
        )

    if set(answers) != set(
        range(1, 41)
    ):

        raise ValueError(
            "Chưa đủ 40 đáp án."
        )

    for number, item in first_questions.items():

        image_path = item.get(
            "anh_cau_hoi"
        )

        if (
            not image_path
            or not (
                output_dir / image_path
            ).is_file()
        ):

            raise FileNotFoundError(
                f"Câu {number}: "
                "thiếu ảnh đã tách trước."
            )

        if (
            str(
                item.get("dap_an_goc", "")
            ).strip()
            != answers[number]
        ):

            raise ValueError(
                f"Câu {number}: "
                "đáp án không khớp."
            )

    print(
        "\nĐã kiểm tra 10 ảnh ban đầu."
    )

    print(
        "Đã kiểm tra đủ 40 đáp án."
    )

    # ----------------------------------------------
    # 14.3. ĐỌC VÙNG CẮT
    # ----------------------------------------------

    regions, shared_regions = (
        load_config(
            args.config
        )
    )

    expected_regions = (
        set(range(6, 11))
        | set(range(16, 21))
        | set(range(26, 41))
    )

    if (
        set(regions) != expected_regions
        or set(shared_regions) != set(SHARED)
    ):
        raise ValueError(
            "Danh sách vùng cắt không hợp lệ."
        )

    # ----------------------------------------------
    # 14.4. CẮT ẢNH TỪ PDF
    # ----------------------------------------------

    with fitz.open(
        pdf_file
    ) as document:

        if len(document) != 10:

            raise ValueError(
                f"PDF có {len(document)} trang. "
                "Cần kiểm tra lại bố cục."
            )

        plans = {}

        group_plans = {}

        # Kiểm tra các vùng trước khi ghi ảnh.
        for number, region in sorted(
            regions.items()
        ):

            plans[number] = plan_crop(
                document,
                region,
                f"Câu {number}",
                number
            )

        for name, region in (
            shared_regions.items()
        ):

            group_plans[name] = plan_crop(
                document,
                region,
                name
            )

        questions_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        groups_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            "\n========== TÁCH ẢNH CÂU =========="
        )

        for number, plan in plans.items():

            destination = (
                questions_dir
                / f"cau_{number:02d}.png"
            )

            save_crop(
                document,
                plan,
                destination
            )

            print(
                f"Đã cắt câu {number:02d} "
                f"- trang {plan[0]}"
            )

        print(
            "\n========== BẢNG CHUNG =========="
        )

        for name, plan in group_plans.items():

            destination = (
                groups_dir
                / f"{name}.png"
            )

            save_crop(
                document,
                plan,
                destination
            )

            print(
                f"Đã cắt {name}"
            )

    # ----------------------------------------------
    # 14.5. GHÉP JSON ĐỦ 40 CÂU
    # ----------------------------------------------

    questions = []

    for number in range(1, 41):

        skill, part = skill_part(
            number
        )

        plan = plans.get(
            number
        )

        original = first_questions.get(
            number, {}
        )

        if plan:

            image_path = (
                f"questions/cau_{number:02d}.png"
            )

            page_number = (
                plan[0]
            )

            crop = [
                round(value, 2)
                for value in plan[1]
            ]

        else:

            image_path = original.get(
                "anh_cau_hoi"
            )

            page_number = original.get(
                "trang_pdf"
            )

            crop = original.get(
                "vung_cat_pdf"
            )

        questions.append({

            "so_cau": number,

            "ky_nang": skill,

            "phan": part,

            "loai_cau_hoi": question_type(
                number
            ),

            "trang_pdf": page_number,

            "anh_cau_hoi": image_path,

            "anh_nhom_lua_chon": shared_for(
                number
            ),

            "dap_an_goc": answers[number],

            "vung_cat_pdf": crop,

            "da_kiem_tra_hinh": False

        })

    # ----------------------------------------------
    # 14.6. KIỂM TRA ĐỦ 40 CÂU
    # ----------------------------------------------

    if (
        len(questions) != 40
        or [
            item["so_cau"]
            for item in questions
        ] != list(range(1, 41))
    ):

        raise RuntimeError(
            "Danh sách 40 câu không hợp lệ."
        )

    for item in questions:

        if (
            not item["anh_cau_hoi"]
            and not item["anh_nhom_lua_chon"]
        ):

            raise RuntimeError(
                f"Câu {item['so_cau']} "
                "chưa có ảnh."
            )

        for field in (
            "anh_cau_hoi",
            "anh_nhom_lua_chon"
        ):

            image_path = item[field]

            if image_path:

                full_path = (
                    output_dir / image_path
                )

                if not full_path.is_file():

                    raise FileNotFoundError(
                        f"Thiếu ảnh: {full_path}"
                    )

    # ----------------------------------------------
    # 14.7. LƯU JSON
    # ----------------------------------------------

    result_data = {

        "ma_de_goc": ma_de,

        "cap_hsk": 1,

        "ten_de": f"Đề {args.de}",

        "so_cau": 40,

        "so_cau_nghe": 20,

        "so_cau_doc": 20,

        "trang_thai": "cho_kiem_tra_hinh",

        "ghi_chu": (
            "Ảnh ứng viên. "
            "Cần kiểm tra phần Đọc 2-4 "
            "trước khi chuẩn hóa."
        ),

        "cau_hoi": questions

    }

    result_file.write_text(

        json.dumps(
            result_data,
            ensure_ascii=False,
            indent=2
        ),

        encoding="utf-8"

    )

    # ----------------------------------------------
    # 14.8. TẠO HTML
    # ----------------------------------------------

    make_html(
        questions,
        html_file,
        ma_de,
        args.de
    )

    print(
        "\n========== KẾT QUẢ =========="
    )

    print(
        "Tổng câu:", len(questions)
    )

    print(
        "Ảnh riêng:",
        sum(
            bool(item["anh_cau_hoi"])
            for item in questions
        )
    )

    print(
        "Bảng chung:",
        len(group_plans)
    )

    print(
        "\nJSON:", result_file
    )

    print(
        "HTML:", html_file
    )

    print(
        "\nChưa duyệt ảnh."
    )

    print(
        "Chưa nhập SQL Server."
    )


if __name__ == "__main__":
    main()
