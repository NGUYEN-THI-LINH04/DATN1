
# -*- coding: utf-8 -*-
"""
MỘC HÁN - HSK1 ĐỀ 4 (H11007)

Tách 30 câu còn lại theo đúng bố cục H11007.pdf.

- Giữ nguyên ảnh câu 1-5, 21-25.
- Cắt 25 ảnh riêng: 6-10, 16-20, 26-40.
- Tạo 4 bảng lựa chọn chung A-F.
- Ghép JSON đủ 40 câu.
- Tạo HTML chỉ hiển thị số câu và hình.

Vùng cắt dựa trên vị trí câu trong PDF gốc.
Không chia đều trang PDF.
Không sử dụng tọa độ của Đề 3.
Không nhập SQL.
"""

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

MA_DE = "H11007"

PDF_FILE = SOURCE / "H11007.pdf"

DATA = HSK1 / "data" / "de_07"
OUTPUT = HSK1 / "output" / "de_07"

QUESTIONS_DIR = OUTPUT / "questions"
GROUPS_DIR = OUTPUT / "groups"

ANSWERS_FILE = DATA / "de_07_dap_an.json"
FIRST_FILE = DATA / "hinh_cau_hoi_kiem_tra.json"

RESULT_FILE = DATA / "hinh_40_cau_ung_vien.json"
HTML_FILE = OUTPUT / "kiem_tra_40_cau_ung_vien.html"

SCALE = 3.0


# ==================================================
# 2. TỌA ĐỘ TỪ PDF H11007
#
# (trang PDF, x0, y0, x1, y1)
#
# PDF: 595.2 x 841.92
# ==================================================

REGIONS = {

    # NGHE PHẦN 2 - HSK1 ĐỀ 7 (H11007)
    # Trang 3: câu 6-8
    # Trang 4: câu 9-10

    6:  (3, 40, 345, 560, 465),
    7:  (3, 40, 490, 560, 610),
    8:  (3, 40, 635, 560, 755),

    9:  (4, 55, 150, 565, 300),
    10: (4, 55, 295, 565, 445),
    # ----------------------------------------------
    # NGHE PHẦN 4
    # Trang 6
    # ----------------------------------------------

    16: (6, 38, 324, 560, 386),
    17: (6, 38, 386, 560, 448),
    18: (6, 38, 448, 560, 510),
    19: (6, 38, 510, 560, 572),
    20: (6, 38, 572, 560, 634),

    # ----------------------------------------------
    # ĐỌC PHẦN 2
    # Trang 8
    # ----------------------------------------------

    26: (8, 42, 554, 555, 596),
    27: (8, 42, 596, 555, 631),
    28: (8, 42, 631, 555, 665),
    29: (8, 42, 665, 555, 700),
    30: (8, 42, 700, 555, 739),

    # ĐỌC - PHẦN 3
    # Trang 9: giữ đủ câu hỏi và ô vuông trả lời.

    31: (9, 35, 229, 400, 292),
    32: (9, 35, 292, 400, 354),
    33: (9, 35, 354, 400, 417),
    34: (9, 35, 417, 400, 479),
    35: (9, 35, 479, 400, 548),

    # ----------------------------------------------
    # ĐỌC PHẦN 4
    # Trang 10
    # Câu 39-40 có nhiều dòng hơn.
    # ----------------------------------------------

    36: (10, 38, 306, 558, 367),
    37: (10, 38, 367, 558, 432),
    38: (10, 38, 432, 558, 497),
    39: (10, 38, 497, 558, 592),
    40: (10, 38, 592, 558, 700),
}


# ==================================================
# 3. 4 BẢNG LỰA CHỌN CHUNG
# ==================================================

SHARED = {

    "nghe_phan_3": (
        5, 30, 90, 570, 515
    ),

    # Chỉ lấy bảng lựa chọn A-F,
    # bỏ tiêu đề phía trên và ví dụ phía dưới.

    "doc_phan_2": (
    8, 65, 165, 535, 545
    ),

    "doc_phan_3": (
    9, 365, 105, 580, 540
    ),

    "doc_phan_4": (
        10, 55, 154, 580, 229
    ),
}


FIRST_NUMBERS = (
    set(range(1, 6))
    | set(range(21, 26))
)


# ==================================================
# 4. ĐỌC JSON
# ==================================================

def read_json(path):

    if not path.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy: {path}"
        )

    return json.loads(
        path.read_text(encoding="utf-8-sig")
    )


def normalize_answer(value):

    value = str(value).strip().upper()

    return {
        "X": "×",
        "✗": "×",
        "✘": "×",
        "✓": "√",
        "✔": "√",
    }.get(value, value)


def save_json(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp = path.with_suffix(".json.tmp")

    temp.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    temp.replace(path)


# ==================================================
# 5. LOẠI CÂU HỎI
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

    if number <= 5 or 21 <= number <= 25:
        return "dung_sai"

    if 11 <= number <= 15:
        return "ghep_hinh_theo_audio"

    if 26 <= number <= 30:
        return "ghep_hinh_theo_noi_dung"

    if number >= 31:
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
# 6. CẮT ẢNH PDF
# ==================================================

def crop_pdf(document, region, destination):

    page_number, x0, y0, x1, y1 = region

    if not 1 <= page_number <= len(document):
        raise ValueError(
            f"Trang PDF {page_number} không tồn tại."
        )

    page = document[page_number - 1]

    rect = fitz.Rect(
        float(x0),
        float(y0),
        float(x1),
        float(y1)
    ) & page.rect

    if (
        rect.is_empty
        or rect.width < 20
        or rect.height < 15
    ):
        raise ValueError(
            f"Vùng cắt không hợp lệ: {region}"
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    pix = page.get_pixmap(
        matrix=fitz.Matrix(SCALE, SCALE),
        clip=rect,
        colorspace=fitz.csRGB,
        alpha=False
    )

    pix.save(str(destination))

    return [
        round(float(value), 2)
        for value in rect
    ]


# ==================================================
# 7. TẠO HTML KIỂM TRA
# ==================================================

def create_html(questions):

    sections = [
        ("nghe", 1, "Nghe hiểu - Phần 1"),
        ("nghe", 2, "Nghe hiểu - Phần 2"),
        ("nghe", 3, "Nghe hiểu - Phần 3"),
        ("nghe", 4, "Nghe hiểu - Phần 4"),
        ("doc", 1, "Đọc hiểu - Phần 1"),
        ("doc", 2, "Đọc hiểu - Phần 2"),
        ("doc", 3, "Đọc hiểu - Phần 3"),
        ("doc", 4, "Đọc hiểu - Phần 4"),
    ]

    html = ["""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>HSK1 Đề 7 - Kiểm tra ảnh</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    font-family: Arial, sans-serif;
    background: #f4f6fa;
    color: #263238;
}

main {
    max-width: 1150px;
    margin: auto;
}

section {
    background: white;
    border-radius: 12px;
    padding: 18px;
    margin: 22px 0;
}

h2 {
    font-size: 18px;
    margin-top: 0;
}

.grid {
    display: grid;
    grid-template-columns:
        repeat(2, minmax(0, 1fr));
    gap: 14px;
}

.card {
    border: 1px solid #d9dfe8;
    border-radius: 9px;
    padding: 13px;
    min-width: 0;
}

.card h4 {
    margin: 0 0 10px;
    color: #1752a5;
}

.card img {
    display: block;
    width: 100%;
    height: auto;
    object-fit: contain;
}

.shared {
    border: 1px solid #d9dfe8;
    border-radius: 9px;
    padding: 12px;
    margin-bottom: 15px;
}

.shared img {
    display: block;
    width: 100%;
    height: auto;
    object-fit: contain;
}

.notice {
    padding: 13px;
    background: #fff4d6;
    border-radius: 8px;
    line-height: 1.6;
}

@media(max-width:720px) {
    .grid {
        grid-template-columns: 1fr;
    }
}
</style>
</head>
<body>
<main>

<h1>HSK1 - Đề 7 (H11007)</h1>

<div class="notice">
Kiểm tra ảnh đã cắt trước khi chuẩn hóa.
Các ảnh không tự động được đánh dấu là đã duyệt.
</div>
"""]

    for skill, part, title in sections:

        items = [
            item
            for item in questions
            if item["ky_nang"] == skill
            and item["phan"] == part
        ]

        html.append(
            "<section>"
            f"<h2>{escape(title)}</h2>"
        )

        shared = items[0][
            "anh_nhom_lua_chon"
        ]

        if shared:

            html.append(
                '<div class="shared">'
                f'<img src="{escape(shared, quote=True)}" '
                'alt="Bảng lựa chọn chung">'
                "</div>"
            )

        html.append('<div class="grid">')

        for item in items:

            number = item["so_cau"]

            image = item["anh_cau_hoi"]

            html.append(
                '<article class="card">'
                f"<h4>Câu {number:02d}</h4>"
            )

            if image:

                html.append(
                    f'<img src="{escape(image, quote=True)}" '
                    f'alt="Câu {number}">'
                )

            html.append("</article>")

        html.append("</div></section>")

    html.append(
        "</main></body></html>"
    )

    HTML_FILE.write_text(
        "\n".join(html),
        encoding="utf-8"
    )


# ==================================================
# 8. CHƯƠNG TRÌNH CHÍNH
# ==================================================

def main():

    print("=" * 55)
    print("MỘC HÁN - HSK1 ĐỀ 4 (H11007)")
    print("=" * 55)

    if not PDF_FILE.is_file():
        raise FileNotFoundError(
            f"Thiếu PDF: {PDF_FILE}"
        )

    answer_data = read_json(
        ANSWERS_FILE
    )

    first_data = read_json(
        FIRST_FILE
    )

    if (
        answer_data.get("ma_de_goc") != MA_DE
        or first_data.get("ma_de_goc") != MA_DE
    ):
        raise ValueError(
            "Mã đề trong các JSON không khớp H11007."
        )

    answers = {
        int(key): normalize_answer(value)
        for key, value
        in answer_data["dap_an"].items()
    }

    if set(answers) != set(range(1, 41)):
        raise ValueError(
            "Chưa đủ 40 đáp án."
        )

    first_questions = {
        int(item["so_cau"]): item
        for item in first_data["cau_hoi"]
    }

    if set(first_questions) != FIRST_NUMBERS:
        raise ValueError(
            "JSON 10 câu đầu không hợp lệ."
        )

    # Kiểm tra ảnh đã làm đúng.
    # Không xuất lại 10 ảnh này.

    for number, item in first_questions.items():

        relative = item.get("anh_cau_hoi")

        if (
            not relative
            or not (OUTPUT / relative).is_file()
        ):
            raise FileNotFoundError(
                f"Thiếu ảnh câu {number}."
            )

        if normalize_answer(
            item["dap_an_goc"]
        ) != answers[number]:
            raise ValueError(
                f"Đáp án câu {number} không khớp."
            )

    expected_regions = (
        set(range(6, 11))
        | set(range(16, 21))
        | set(range(26, 41))
    )

    if set(REGIONS) != expected_regions:
        raise ValueError(
            "Danh sách 25 vùng cắt chưa đủ."
        )

    QUESTIONS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    GROUPS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    crops = {}

    print("\n========== CẮT 25 CÂU ==========")

    with fitz.open(PDF_FILE) as document:

        if len(document) != 10:
            raise ValueError(
                "H11007 phải có 10 trang PDF."
            )

        for number, region in sorted(
            REGIONS.items()
        ):

            destination = (
                QUESTIONS_DIR
                / f"cau_{number:02d}.png"
            )

            crops[number] = crop_pdf(
                document,
                region,
                destination
            )

            print(
                f"Câu {number:02d}: "
                f"trang {region[0]}"
            )

        print(
            "\n========== CẮT 4 BẢNG CHUNG =========="
        )

        for name, region in SHARED.items():

            destination = (
                GROUPS_DIR / f"{name}.png"
            )

            crop_pdf(
                document,
                region,
                destination
            )

            print("Đã tạo:", name)

    # ----------------------------------------------
    # 8.1. GHÉP 40 CÂU
    # ----------------------------------------------

    questions = []

    for number in range(1, 41):

        skill, part = skill_part(number)

        original = first_questions.get(
            number, {}
        )

        if number in FIRST_NUMBERS:

            image = original["anh_cau_hoi"]

            page_number = original.get(
                "trang_pdf"
            )

            crop_rect = original.get(
                "vung_cat_pdf"
            )

        elif number in REGIONS:

            image = (
                f"questions/cau_{number:02d}.png"
            )

            page_number = REGIONS[number][0]

            crop_rect = crops[number]

        else:

            # Nghe phần 3: câu 11-15.
            image = None
            page_number = 5
            crop_rect = None

        questions.append({
            "so_cau": number,
            "ky_nang": skill,
            "phan": part,
            "loai_cau_hoi": question_type(number),
            "trang_pdf": page_number,
            "anh_cau_hoi": image,
            "anh_nhom_lua_chon": shared_for(number),
            "dap_an_goc": answers[number],
            "vung_cat_pdf": crop_rect,
            "da_kiem_tra_hinh": False,
        })

    # ----------------------------------------------
    # 8.2. KIỂM TRA FILE
    # ----------------------------------------------

    image_paths = set()

    group_paths = set()

    for item in questions:

        if item["anh_cau_hoi"]:
            image_paths.add(
                item["anh_cau_hoi"]
            )

        if item["anh_nhom_lua_chon"]:
            group_paths.add(
                item["anh_nhom_lua_chon"]
            )

    if (
        len(questions) != 40
        or len(image_paths) != 35
        or len(group_paths) != 4
    ):
        raise RuntimeError(
            "Số câu hoặc số ảnh không hợp lệ."
        )

    for relative in image_paths | group_paths:

        if not (OUTPUT / relative).is_file():
            raise FileNotFoundError(
                f"Thiếu ảnh: {relative}"
            )

    # ----------------------------------------------
    # 8.3. LƯU JSON VÀ HTML
    # ----------------------------------------------

    result = {
        "ma_de_goc": MA_DE,
        "cap_hsk": 1,
        "ten_de": "Đề 7",
        "so_cau": 40,
        "so_cau_nghe": 20,
        "so_cau_doc": 20,
        "trang_thai": "cho_kiem_tra_hinh",
        "cau_hoi": questions,
    }

    save_json(
        RESULT_FILE,
        result
    )

    create_html(
        questions
    )

    print(
        "\n========== HOÀN THÀNH =========="
    )

    print("Mã đề:", MA_DE)
    print("Tổng câu:", len(questions))
    print("Ảnh riêng:", len(image_paths))
    print("Bảng chung:", len(group_paths))
    print("Đáp án:", len(answers))

    print("\nJSON:", RESULT_FILE)
    print("HTML:", HTML_FILE)

    print("\nChưa thay đổi SQL Server.")


if __name__ == "__main__":
    main()
