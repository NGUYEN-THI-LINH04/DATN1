
# -*- coding: utf-8 -*-
"""
MỘC HÁN - HSK1
TÁCH 10 CÂU HỎI CÓ HÌNH ẢNH RIÊNG

Mặc định:
    Đề 3 - H10902

Xử lý:
    - Câu 1-5: Nghe phần 1
    - Câu 21-25: Đọc phần 1

Phương pháp:
    - Đọc hình ảnh nhúng trực tiếp từ PDF.
    - Tìm 5 ảnh xếp thành một cột.
    - Bỏ ảnh ví dụ ở phía trên.
    - Cắt ảnh theo vị trí thực tế.
    - Xuất PNG, JSON và HTML xem trước.

HTML chỉ hiển thị tên câu và hình ảnh.
Đáp án vẫn được giữ trong JSON.

Có thể tái sử dụng cho đề HSK1 khác
bằng tham số --ma-de và --de.

KHÔNG nhập SQL Server.
KHÔNG sửa dữ liệu các đề khác.
"""

import argparse
import itertools
import json

from html import escape
from pathlib import Path
from statistics import median, pstdev

import fitz


# ==================================================
# 1. ĐƯỜNG DẪN CHUNG
# ==================================================

HSK1 = Path(__file__).resolve().parent

BASE = HSK1.parent

SOURCE = (
    BASE
    / "source"
    / "De_HSK"
    / "HSK1"
)

RENDER_DPI = 220


# ==================================================
# 2. ĐỌC JSON
# ==================================================

def read_json(path):

    if not path.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy file: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )


# ==================================================
# 3. XÁC ĐỊNH ẢNH NHÚNG TRONG PDF
# ==================================================

def image_rectangles(page):

    """
    Tìm những ảnh thực tế trên trang PDF.

    Không tìm số câu bằng get_text().
    Không dùng tọa độ cắt của Đề 2.
    """

    found = {}

    infos = page.get_image_info()

    for info in infos:

        if "bbox" not in info:
            continue

        rect = (
            fitz.Rect(info["bbox"])
            & page.rect
        )

        if rect.is_empty:
            continue

        # Bỏ ảnh quá nhỏ.
        if (
            rect.width < 18
            or rect.height < 18
        ):
            continue

        # Bỏ ảnh nền hoặc ảnh quá rộng.
        if (
            rect.width
            > page.rect.width * 0.75
        ):
            continue

        # Bỏ vùng đầu trang và vùng ngoài nội dung.
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
        key=lambda r: (
            (r.y0 + r.y1) / 2,
            (r.x0 + r.x1) / 2
        )
    )


# ==================================================
# 4. CHỌN 5 ẢNH CỦA 5 CÂU
# ==================================================

def pick_five(rects, page):

    """
    Chọn 5 ảnh xếp thành một cột,
    có khoảng cách hàng tương đối đều.

    Hình ví dụ nằm phía trên nên ưu tiên
    nhóm 5 ảnh ở phần thấp hơn của trang.

    Kết quả vẫn cần kiểm tra bằng HTML.
    """

    if len(rects) < 5:
        raise ValueError(
            f"Chỉ phát hiện {len(rects)} ảnh. "
            "Không đủ để tách 5 câu."
        )

    best = None

    all_centers = [
        (r.y0 + r.y1) / 2
        for r in rects
    ]

    last_center = max(all_centers)

    for combo in itertools.combinations(
        rects, 5
    ):

        ordered = sorted(
            combo,
            key=lambda r: (
                (r.y0 + r.y1) / 2
            )
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

        if min(gaps) < 25:
            continue

        if max(gaps) > 190:
            continue

        mean_gap = (
            sum(gaps) / len(gaps)
        )

        if mean_gap <= 0:
            continue

        # Ưu tiên các ảnh có khoảng cách đều,
        # cùng cột và nằm ở phần dưới trang.
        score = (
            pstdev(gaps)
            / mean_gap
            * 100
            + pstdev(xs) * 0.35
            + max(
                0,
                last_center - ys[-1]
            ) * 0.10
        )

        if mean_gap < 48:
            score += 20

        if ys[0] < page.rect.height * 0.40:
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
        raise ValueError(
            "Không tìm được nhóm 5 ảnh phù hợp. "
            "Cần xem vị trí ảnh trong PDF."
        )

    return best[1], best[0]


# ==================================================
# 5. XÁC ĐỊNH VÙNG CẮT CÂU HỎI
# ==================================================

def crop_for_question(
    page,
    rect,
    ordered,
    index,
    skill
):

    """
    NGHE:
        Cắt hình minh họa của câu.

    ĐỌC:
        Cắt hình cùng nội dung chữ Hán,
        pinyin nằm cùng hàng.
    """

    if skill == "nghe":

        # Nới viền tránh cắt sát hình.
        region = fitz.Rect(
            rect.x0 - 8,
            rect.y0 - 8,
            rect.x1 + 8,
            rect.y1 + 8
        )

    else:

        centers = [
            (r.y0 + r.y1) / 2
            for r in ordered
        ]

        gaps = [
            centers[i + 1] - centers[i]
            for i in range(4)
        ]

        gap = median(gaps)

        # Giới hạn hàng theo trung điểm
        # giữa các hình liên tiếp.
        if index == 0:

            y0 = (
                centers[0] - gap / 2
            )

        else:

            y0 = (
                centers[index - 1]
                + centers[index]
            ) / 2

        if index == 4:

            y1 = (
                centers[4] + gap / 2
            )

        else:

            y1 = (
                centers[index]
                + centers[index + 1]
            ) / 2

        # Giữ cả hình và chữ Hán bên phải.
        region = fitz.Rect(
            rect.x0 - 12,
            y0 + 1,
            rect.x0 + 270,
            y1 - 1
        )

    return region & page.rect


# ==================================================
# 6. KIỂM TRA CÁC VÙNG CẮT
# ==================================================

def validate_crops(rows):

    if len(rows) != 10:
        raise ValueError(
            "Phải có đúng 10 câu."
        )

    expected = (
        list(range(1, 6))
        + list(range(21, 26))
    )

    numbers = [
        item["so_cau"]
        for item in rows
    ]

    if numbers != expected:
        raise ValueError(
            "Thứ tự 10 câu không chính xác."
        )

    for item in rows:

        rect = item["crop"]

        if (
            rect.is_empty
            or rect.width < 20
            or rect.height < 20
        ):
            raise ValueError(
                "Vùng cắt không hợp lệ "
                f"ở câu {item['so_cau']}."
            )


# ==================================================
# 7. XUẤT ẢNH PNG
# ==================================================

def export_images(
    document,
    rows,
    images_dir
):

    images_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    final_rows = []

    for item in rows:

        number = item["so_cau"]

        page_number = (
            item["trang_pdf"]
        )

        page = document[
            page_number - 1
        ]

        crop = item["crop"]

        filename = (
            f"cau_{number:02d}.png"
        )

        output_file = (
            images_dir / filename
        )

        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(
                RENDER_DPI / 72,
                RENDER_DPI / 72
            ),
            clip=crop,
            colorspace=fitz.csRGB,
            alpha=False
        )

        pixmap.save(
            str(output_file)
        )

        final_rows.append({

            "so_cau": number,

            "ky_nang": item["ky_nang"],

            "trang_pdf": page_number,

            "anh_cau_hoi": (
                f"questions/{filename}"
            ),

            "dap_an_goc": item["dap_an"],

            "vung_cat_pdf": [
                round(value, 2)
                for value in crop
            ],

            "da_kiem_tra_hinh": False

        })

        print(
            f"Đã cắt câu {number:02d}"
            f" - trang {page_number}"
        )

    return final_rows


# ==================================================
# 8. TẠO HTML KIỂM TRA
# ==================================================

def make_html(
    results,
    html_path,
    ma_de,
    so_de
):

    parts = [

        '<!DOCTYPE html>',
        '<html lang="vi">',

        '<head>',
        '<meta charset="utf-8">',

        '<meta name="viewport" '
        'content="width=device-width, initial-scale=1">',

        f"<title>HSK1 Đề {so_de}"
        " - Kiểm tra 10 câu</title>",

        "<style>",

        "*{box-sizing:border-box}",

        "body{"
        "font-family:Arial,sans-serif;"
        "background:#f4f6fa;"
        "color:#263238;"
        "margin:0;"
        "padding:24px"
        "}",

        "main{"
        "max-width:1120px;"
        "margin:auto"
        "}",

        "h1{margin-bottom:8px}",

        ".notice{"
        "background:#fff3d6;"
        "border:1px solid #edd18d;"
        "padding:15px;"
        "border-radius:10px;"
        "line-height:1.6;"
        "margin:18px 0"
        "}",

        ".grid{"
        "display:grid;"
        "grid-template-columns:"
        "repeat(2,minmax(0,1fr));"
        "gap:16px"
        "}",

        ".card{"
        "background:white;"
        "border:1px solid #ddd;"
        "border-radius:12px;"
        "padding:16px"
        "}",

        ".card h3{"
        "margin-top:0;"
        "color:#174ea6"
        "}",

        ".card img{"
        "display:block;"
        "max-width:100%;"
        "max-height:350px;"
        "object-fit:contain;"
        "background:white"
        "}",

        "h2{margin-top:28px}",

        "@media(max-width:700px){"
        ".grid{grid-template-columns:1fr}"
        "}",

        "</style>",

        "</head>",

        "<body><main>",

        f"<h1>HSK1 - Đề {so_de} "
        f"({escape(ma_de)})</h1>",

        '<div class="notice">',

        "<strong>Kiểm tra 10 ảnh đã cắt.</strong>"
        "<p>Nghe phần 1: câu 1-5.<br>"
        "Đọc phần 1: câu 21-25.</p>",

        "Ảnh được chọn tự động từ PDF. "
        "Cần kiểm tra xem từng ảnh có "
        "đúng câu hỏi và có bị cắt mất "
        "nội dung hay không.",

        "</div>",

    ]

    sections = [

        (
            "nghe",
            "Nghe - Phần 1 (Câu 1-5)"
        ),

        (
            "doc",
            "Đọc - Phần 1 (Câu 21-25)"
        )

    ]

    for skill, title in sections:

        parts.append(
            f"<h2>{escape(title)}</h2>"
        )

        parts.append(
            '<div class="grid">'
        )

        for row in results:

            if row["ky_nang"] != skill:
                continue

            number = row["so_cau"]

            image_path = escape(
                row["anh_cau_hoi"],
                quote=True
            )

            # Chỉ hiển thị tên câu và ảnh.
            # Không hiển thị trang PDF,
            # đáp án hoặc trạng thái.
            parts.extend([

                '<article class="card">',

                f"<h3>Câu {number:02d}</h3>",

                f'<img src="{image_path}" '
                f'alt="Câu {number}">',

                "</article>"

            ])

        parts.append("</div>")

    parts.extend([

        "</main>",
        "</body>",
        "</html>"

    ])

    html_path.write_text(
        "\n".join(parts),
        encoding="utf-8"
    )


# ==================================================
# 9. XỬ LÝ MỘT NHÓM 5 CÂU
# ==================================================

def process_section(
    document,
    skill,
    page_number,
    first_question,
    answers
):

    if not (
        1 <= page_number <= len(document)
    ):
        raise ValueError(
            "Trang PDF không hợp lệ: "
            f"{page_number}"
        )

    page = document[
        page_number - 1
    ]

    rects = image_rectangles(page)

    print()
    print("=" * 45)

    print(
        f"{skill.upper()} "
        f"- Trang {page_number}"
    )

    print("=" * 45)

    print(
        "Số vùng ảnh ứng viên:",
        len(rects)
    )

    for index, rect in enumerate(
        rects, 1
    ):

        print(
            f"Ảnh {index:02d}: "
            f"x={rect.x0:.1f}-"
            f"{rect.x1:.1f}, "
            f"y={rect.y0:.1f}-"
            f"{rect.y1:.1f}"
        )

    selected, score = pick_five(
        rects, page
    )

    print(
        "\nĐiểm nhận diện:",
        round(score, 2)
    )

    print(
        "5 hình ứng viên đã chọn:"
    )

    rows = []

    for index, rect in enumerate(
        selected
    ):

        number = (
            first_question + index
        )

        crop = crop_for_question(
            page,
            rect,
            selected,
            index,
            skill
        )

        print(
            f"  Câu {number:02d}: "
            f"x={crop.x0:.1f}-"
            f"{crop.x1:.1f}, "
            f"y={crop.y0:.1f}-"
            f"{crop.y1:.1f}"
        )

        rows.append({

            "so_cau": number,

            "ky_nang": skill,

            "trang_pdf": page_number,

            "crop": crop,

            "dap_an": answers[number]

        })

    return rows


# ==================================================
# 10. CHƯƠNG TRÌNH CHÍNH
# ==================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Tách 10 câu có hình riêng "
            "trong đề thi HSK1."
        )
    )

    parser.add_argument(
        "--ma-de",
        default="H10902",
        help="Mã đề PDF, ví dụ H10902."
    )

    parser.add_argument(
        "--de",
        type=int,
        default=3,
        help="Số thứ tự đề, mặc định 3."
    )

    parser.add_argument(
        "--trang-nghe",
        type=int,
        default=2,
        help="Trang chứa câu 1-5."
    )

    parser.add_argument(
        "--trang-doc",
        type=int,
        default=7,
        help="Trang chứa câu 21-25."
    )

    args = parser.parse_args()

    ma_de = args.ma_de.strip().upper()

    so_de = args.de

    if so_de < 1:
        raise ValueError(
            "Số đề phải lớn hơn 0."
        )

    de_folder = (
        f"de_{so_de:02d}"
    )

    pdf_file = (
        SOURCE / f"{ma_de}.pdf"
    )

    data_dir = (
        HSK1 / "data" / de_folder
    )

    output_dir = (
        HSK1 / "output" / de_folder
    )

    images_dir = (
        output_dir / "questions"
    )

    answers_file = (
        data_dir
        / f"{de_folder}_dap_an.json"
    )

    result_file = (
        data_dir
        / "hinh_cau_hoi_kiem_tra.json"
    )

    html_file = (
        output_dir
        / "kiem_tra_10_cau.html"
    )

    print("=" * 55)

    print(
        f"MỘC HÁN - HSK1 ĐỀ {so_de}"
    )

    print("Mã đề:", ma_de)

    print("=" * 55)

    # ----------------------------------------------
    # 10.1. KIỂM TRA FILE
    # ----------------------------------------------

    if not pdf_file.is_file():

        raise FileNotFoundError(
            f"Không tìm thấy PDF: {pdf_file}"
        )

    answer_data = read_json(
        answers_file
    )

    if answer_data.get(
        "ma_de_goc"
    ) != ma_de:

        raise ValueError(
            "Mã đề trong JSON đáp án "
            "không khớp PDF."
        )

    answers = {
        int(number): str(value).strip()
        for number, value
        in answer_data["dap_an"].items()
    }

    if set(answers) != set(
        range(1, 41)
    ):

        raise ValueError(
            "Chưa đủ 40 đáp án."
        )

    print(
        "\nĐã kiểm tra 40 đáp án."
    )

    # ----------------------------------------------
    # 10.2. NHẬN DIỆN 10 ẢNH
    # ----------------------------------------------

    rows = []

    with fitz.open(
        pdf_file
    ) as document:

        print(
            "Số trang PDF:",
            len(document)
        )

        sections = [

            (
                "nghe",
                args.trang_nghe,
                1
            ),

            (
                "doc",
                args.trang_doc,
                21
            )

        ]

        for (
            skill,
            page_number,
            first_question
        ) in sections:

            section_rows = (
                process_section(
                    document,
                    skill,
                    page_number,
                    first_question,
                    answers
                )
            )

            rows.extend(
                section_rows
            )

        # Kiểm tra đủ 10 câu trước
        # khi bắt đầu ghi ảnh.
        validate_crops(rows)

        # ------------------------------------------
        # 10.3. XUẤT ẢNH
        # ------------------------------------------

        data_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            "\n========== XUẤT ẢNH =========="
        )

        final_rows = export_images(
            document,
            rows,
            images_dir
        )

    # ----------------------------------------------
    # 10.4. LƯU JSON
    # ----------------------------------------------

    result_data = {

        "ma_de_goc": ma_de,

        "cap_hsk": 1,

        "ten_de": f"Đề {so_de}",

        "trang_thai": "cho_kiem_tra_hinh",

        "so_cau_da_tach": len(
            final_rows
        ),

        "ghi_chu": (
            "10 ảnh ứng viên được tìm "
            "từ ảnh nhúng trong PDF. "
            "Chưa xác nhận bằng mắt."
        ),

        "cau_hoi": final_rows

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
    # 10.5. LƯU HTML
    # ----------------------------------------------

    make_html(
        final_rows,
        html_file,
        ma_de,
        so_de
    )

    print()

    print("=" * 55)
    print("HOÀN THÀNH TÁCH 10 CÂU")
    print("=" * 55)

    print("Mã đề:", ma_de)

    print(
        "Số câu đã cắt:",
        len(final_rows),
        "/10"
    )

    print("JSON:", result_file)

    print("HTML:", html_file)

    print()

    print(
        "Chưa tạo JSON 40 câu."
    )

    print(
        "Chưa thay đổi SQL Server."
    )

    print(
        "Cần kiểm tra ảnh trước "
        "khi làm phần còn lại."
    )


if __name__ == "__main__":
    main()
