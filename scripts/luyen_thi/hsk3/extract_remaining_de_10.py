
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 10 - BUOC 2
MA DE GOC: H31328

- Kiem tra JSON buoc 1.
- Tach anh cau 11-80 theo vi tri so cau tren PDF.
- Tach 4 bang lua chon chung phan Doc.
- Giu lai 2 bang hinh Nghe cua buoc 1.
- Tao manifest 80 cau, 6 bang chung.
- Tao HTML xem truoc 80 cau.

KHONG sua SQL Server.
KHONG sua cac de thi cu.
"""

from pathlib import Path
import json
import os
import re
import html

import fitz


# ====================================================
# 1. CAU HINH
# ====================================================

ROOT = Path(
    os.environ.get(
        "MOC_HAN_ROOT",
        r"D:\DATN1"
    )
)

BASE = ROOT / "scripts" / "luyen_thi"

DATA = BASE / "hsk3" / "data" / "de_10"

OUTPUT = BASE / "hsk3" / "output" / "de_10"

QUESTIONS = OUTPUT / "questions"
GROUPS = OUTPUT / "groups"

ANSWER_FILE = DATA / "de_10_dap_an.json"

MANIFEST_FILE = (
    DATA / "hinh_80_cau_ung_vien.json"
)

PREVIEW_FILE = (
    OUTPUT / "kiem_tra_80_cau.html"
)

CODE = "H31328"

# Chat luong anh, co the tang neu can.
ZOOM = 2.2


# ====================================================
# 2. TRANG PDF CUA TUNG NHOM CAU
# ====================================================

PAGE_QUESTIONS = {
    4: list(range(11, 21)),
    5: list(range(21, 31)),
    6: list(range(31, 41)),
    7: list(range(41, 46)),
    8: list(range(46, 51)),
    9: list(range(51, 56)),
    10: list(range(56, 61)),
    11: list(range(61, 65)),
    12: list(range(65, 71)),
    13: list(range(71, 76)),
    14: list(range(76, 81)),
}


# ====================================================
# 3. CAU HINH 6 BANG CHUNG
# ====================================================

# Toa do la toa do PDF, khong phai pixel PNG.
# Cac bang Doc chi chua lua chon A-F/A-E.

GROUP_CONFIG = {
    "nghe_01_05": {
        "trang_pdf": 2,
        "cau_tu": 1,
        "cau_den": 5,
        "lua_chon": "ABCDEF",
        "anh": "groups/nghe_01_05.png",
    },

    "nghe_06_10": {
        "trang_pdf": 3,
        "cau_tu": 6,
        "cau_den": 10,
        "lua_chon": "ABCDE",
        "anh": "groups/nghe_06_10.png",
    },

    "doc_41_45": {
        "trang_pdf": 7,
        "cau_tu": 41,
        "cau_den": 45,
        "lua_chon": "ABCDEF",
        "anh": "groups/doc_41_45.png",
        "rect": (65, 215, 540, 455),
    },

    "doc_46_50": {
        "trang_pdf": 8,
        "cau_tu": 46,
        "cau_den": 50,
        "lua_chon": "ABCDE",
        "anh": "groups/doc_46_50.png",
        "rect": (65, 200, 540, 355),
    },

    "doc_51_55": {
        "trang_pdf": 9,
        "cau_tu": 51,
        "cau_den": 55,
        "lua_chon": "ABCDEF",
        "anh": "groups/doc_51_55.png",
        "rect": (65, 215, 540, 310),
    },

    "doc_56_60": {
        "trang_pdf": 10,
        "cau_tu": 56,
        "cau_den": 60,
        "lua_chon": "ABCDEF",
        "anh": "groups/doc_56_60.png",
        "rect": (65, 205, 540, 290),
    },
}


# ====================================================
# 4. HAM CHUNG
# ====================================================

def load_json(path):

    if not path.is_file():
        raise RuntimeError(
            f"Khong tim thay JSON:\n{path}"
        )

    return json.loads(
        path.read_text(encoding="utf-8-sig")
    )


def save_safe(path, content):

    if path.exists():

        if path.read_bytes() != content:

            raise RuntimeError(
                "File da ton tai voi noi dung khac."
                "\nKhong ghi de:\n"
                + str(path)
            )

        return

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_bytes(content)


def page_for(number):

    if number <= 5:
        return 2

    if number <= 10:
        return 3

    for page_no, numbers in PAGE_QUESTIONS.items():

        if number in numbers:
            return page_no

    raise RuntimeError(
        f"Khong co trang PDF cho cau {number}"
    )


def group_for(number):

    for name, config in GROUP_CONFIG.items():

        if (
            config["cau_tu"]
            <= number
            <= config["cau_den"]
        ):
            return name

    return None


def question_kind(number):

    if number <= 10:
        return "chon_hinh"

    if number <= 20:
        return "dung_sai"

    if number <= 40:
        return "chon_mot"

    if number <= 60:
        return "ghep_lua_chon"

    if number <= 70:
        return "chon_mot"

    if number <= 75:
        return "sap_xep"

    return "dien_tu"


def question_section(number):

    if number <= 40:
        return "nghe"

    if number <= 70:
        return "doc"

    return "viet"


# ====================================================
# 5. TIM VI TRI SO CAU TREN TRANG
# ====================================================

def find_question_positions(page, numbers):

    """
    Lay bbox cua dong bat dau bang so cau.

    Dung get_text("dict") de tranh loi:
    - So cau tach khoi dau cham.
    - Khoang trang khac nhau.
    - Cau hoi co nhieu dong.
    """

    wanted = set(numbers)

    positions = {}

    for block in page.get_text("dict")["blocks"]:

        if "lines" not in block:
            continue

        for line in block["lines"]:

            text = "".join(
                span["text"]
                for span in line["spans"]
            ).strip()

            match = re.match(
                r"^(\d{1,2})\s*[.．、]",
                text
            )

            if not match:
                continue

            number = int(match.group(1))

            if number not in wanted:
                continue

            if number in positions:
                raise RuntimeError(
                    f"Trung vi tri cau {number}"
                )

            positions[number] = (
                float(line["bbox"][1])
            )

    missing = wanted - set(positions)

    if missing:

        raise RuntimeError(
            "Khong tim thay vi tri cau: "
            + str(sorted(missing))
        )

    return positions


# ====================================================
# 6. CAT ANH TUNG CAU
# ====================================================

def extract_question_images(doc):

    output = {}

    for page_no, numbers in PAGE_QUESTIONS.items():

        page = doc[page_no - 1]

        positions = find_question_positions(
            page,
            numbers
        )

        sorted_numbers = sorted(numbers)

        for index, number in enumerate(sorted_numbers):

            top = positions[number] - 7

            if index + 1 < len(sorted_numbers):

                next_number = sorted_numbers[
                    index + 1
                ]

                bottom = (
                    positions[next_number] - 9
                )

            else:

                # Gioi han truoc footer H31328.
                bottom = min(
                    page.rect.height - 48,
                    760
                )

            if bottom <= top:

                raise RuntimeError(
                    f"Khung cau {number} khong hop le"
                )

            # Lay du chieu ngang de giu tron
            # noi dung Trung, Viet va dap an.
            rect = fitz.Rect(
                55,
                max(0, top),
                page.rect.width - 45,
                min(page.rect.height, bottom)
            )

            if not page.rect.contains(rect):

                raise RuntimeError(
                    f"Khung cau {number} ngoai trang"
                )

            pix = page.get_pixmap(
                matrix=fitz.Matrix(ZOOM, ZOOM),
                clip=rect,
                alpha=False
            )

            relative = (
                f"questions/cau_{number:02d}.png"
            )

            output[relative] = (
                pix.tobytes("png")
            )

        print(
            f"Trang {page_no}: "
            f"{len(numbers)} cau"
        )

    if len(output) != 70:

        raise RuntimeError(
            f"Chi tach duoc {len(output)}/70 anh"
        )

    return output


# ====================================================
# 7. CAT 4 BANG LUA CHON DOC
# ====================================================

def extract_reading_groups(doc):

    output = {}

    for name, config in GROUP_CONFIG.items():

        if name.startswith("nghe_"):
            continue

        page = doc[
            config["trang_pdf"] - 1
        ]

        rect = fitz.Rect(
            config["rect"]
        )

        if not page.rect.contains(rect):

            raise RuntimeError(
                f"Khung {name} ngoai trang PDF"
            )

        pix = page.get_pixmap(
            matrix=fitz.Matrix(ZOOM, ZOOM),
            clip=rect,
            alpha=False
        )

        output[config["anh"]] = (
            pix.tobytes("png")
        )

        print(
            f"{name}: "
            f"{len(config['lua_chon'])} lua chon"
        )

    if len(output) != 4:

        raise RuntimeError(
            "Khong du 4 bang lua chon Doc"
        )

    return output


# ====================================================
# 8. KIEM TRA HAI BANG NGHE BUOC 1
# ====================================================

def check_listening_groups():

    for name in (
        "nghe_01_05",
        "nghe_06_10"
    ):

        path = GROUPS / f"{name}.png"

        if (
            not path.is_file()
            or path.stat().st_size == 0
        ):

            raise RuntimeError(
                "Thieu bang hinh Nghe "
                "tu buoc 1:\n"
                + str(path)
            )

        if not path.read_bytes().startswith(
            b"\x89PNG\r\n\x1a\n"
        ):

            raise RuntimeError(
                f"Anh PNG khong hop le: {path}"
            )


# ====================================================
# 9. TAO MANIFEST 80 CAU
# ====================================================

def make_manifest(answer_data):

    questions = {}

    for number in range(1, 81):

        group = group_for(number)

        questions[str(number)] = {
            "so_cau": number,

            "phan": question_section(number),

            "dang": question_kind(number),

            "trang_pdf": page_for(number),

            "anh": (
                None
                if number <= 10
                else (
                    f"questions/cau_{number:02d}.png"
                )
            ),

            "nhom_lua_chon": group,

            "dap_an_dung": (
                answer_data["dap_an"][str(number)]
            ),
        }

    groups = {}

    for name, config in GROUP_CONFIG.items():

        groups[name] = {
            "trang_pdf": config["trang_pdf"],

            "cau_tu": config["cau_tu"],

            "cau_den": config["cau_den"],

            "lua_chon": config["lua_chon"],

            "anh": config["anh"],
        }

    return {
        "cap_hsk": 3,
        "so_de": 10,
        "ma_de_goc": CODE,

        "so_cau": 80,

        "so_trang_pdf": 16,

        "trang_dap_an": [15, 16],

        "trang_loi_thoai": [],

        "dap_an_thay_the": {},

        "cau_hoi": questions,

        "bang_lua_chon": groups,
    }


# ====================================================
# 10. TAO HTML XEM TRUOC
# ====================================================

def make_preview(answer_data):

    sections = []

    for number in range(1, 81):

        group = group_for(number)

        if number <= 10:

            image = (
                f"groups/{group}.png"
            )

            # Bang chung hien mot lan
            # cho tung nhom 5 cau.
            if number not in (1, 6):
                image = None

        else:

            image = (
                f"questions/cau_{number:02d}.png"
            )

        image_html = ""

        if image:

            image_html = (
                '<img src="'
                + html.escape(image, quote=True)
                + '" alt="Cau '
                + str(number)
                + '">'
            )

        answer = html.escape(
            str(
                answer_data["dap_an"][
                    str(number)
                ]
            )
        )

        sections.append(
            f'<section id="cau-{number}">'
            f'<h3>Câu {number}</h3>'
            f'{image_html}'
            '<details>'
            '<summary>Xem đáp án</summary>'
            f'<p>Đáp án: <b>{answer}</b></p>'
            '</details>'
            '</section>'
        )

    # Bang lua chon Doc hien truoc
    # cau dau tien cua moi nhom.
    for name, config in GROUP_CONFIG.items():

        if not name.startswith("doc_"):
            continue

        first = config["cau_tu"]

        target = f'<section id="cau-{first}">'

        group_html = (
            '<section class="shared">'
            f'<h2>Bảng lựa chọn câu '
            f'{first}–{config["cau_den"]}</h2>'
            f'<img src="{config["anh"]}" '
            'alt="Bang lua chon">'
            '</section>'
        )

        for index, section in enumerate(sections):

            if section.startswith(target):

                sections[index] = (
                    group_html + section
                )

                break

    page_html = """
<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport"
      content="width=device-width,initial-scale=1">

<title>HSK3 Đề 10 - Kiểm tra 80 câu</title>

<style>
* { box-sizing: border-box; }

body {
    font-family: Arial, sans-serif;
    background: #f3f5f9;
    color: #172b4d;
    margin: 0;
    padding: 20px;
}

main {
    max-width: 940px;
    margin: 0 auto;
}

section {
    background: white;
    padding: 20px;
    margin: 16px 0;
    border: 1px solid #dce4ed;
    border-radius: 12px;
}

section.shared {
    background: #f8fbff;
}

h1 { margin-bottom: 8px; }

h3 { margin-top: 0; }

img {
    display: block;
    width: 100%;
    height: auto;
    object-fit: contain;
    margin: 10px auto;
}

details {
    margin-top: 14px;
}

summary {
    cursor: pointer;
    font-weight: bold;
}

.note {
    color: #64748b;
}

nav {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 18px 0;
}

nav a {
    text-decoration: none;
    padding: 7px 10px;
    background: white;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    color: #172b4d;
}
</style>
</head>

<body>
<main>

<h1>HSK3 – Đề 10 (H31328)</h1>

<p class="note">
Kiểm tra hình câu 1–80.
Đáp án chỉ hiện khi bấm xem.
Chưa thay đổi SQL Server.
</p>

<nav>__NAV__</nav>

__CONTENT__

</main>
</body>
</html>
"""

    nav = "".join(
        f'<a href="#cau-{number}">'
        f'{number}</a>'
        for number in range(1, 81)
    )

    return (
        page_html
        .replace("__NAV__", nav)
        .replace(
            "__CONTENT__",
            "\n".join(sections)
        )
        .encode("utf-8")
    )


# ====================================================
# 11. CHUONG TRINH CHINH
# ====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 10")
    print("BUOC 2 - TACH HINH H31328")
    print("=" * 60)

    answer_data = load_json(
        ANSWER_FILE
    )

    if (
        answer_data.get("cap_hsk") != 3
        or answer_data.get("so_de") != 10
        or answer_data.get("ma_de_goc") != CODE
    ):

        raise RuntimeError(
            "JSON buoc 1 khong phai H31328"
        )

    answers = answer_data.get(
        "dap_an", {}
    )

    if set(answers) != {
        str(number)
        for number in range(1, 81)
    }:

        raise RuntimeError(
            "JSON buoc 1 khong du 80 dap an"
        )

    pdf_path = Path(
        answer_data["file_pdf"]
    )

    if not pdf_path.is_file():

        raise RuntimeError(
            f"Khong tim thay PDF: {pdf_path}"
        )

    check_listening_groups()

    # ================================================
    # 12. DOC PDF VA TACH ANH
    # ================================================

    with fitz.open(pdf_path) as doc:

        if len(doc) != 16:

            raise RuntimeError(
                "PDF H31328 phai co 16 trang"
            )

        if CODE not in doc[0].get_text():

            raise RuntimeError(
                "Sai ma de goc tren PDF"
            )

        print("\n===== TACH ANH CAU HOI =====")

        question_images = (
            extract_question_images(doc)
        )

        print("\n===== TACH BANG DOC =====")

        reading_groups = (
            extract_reading_groups(doc)
        )

    # ================================================
    # 13. TAO MANIFEST
    # ================================================

    manifest = make_manifest(
        answer_data
    )

    if (
        len(manifest["cau_hoi"]) != 80
        or len(manifest["bang_lua_chon"]) != 6
    ):

        raise RuntimeError(
            "Manifest khong du 80 cau / 6 bang"
        )

    # ================================================
    # 14. CHUAN BI FILE DAU RA
    # ================================================

    outputs = {}

    for relative, content in {
        **question_images,
        **reading_groups
    }.items():

        outputs[
            OUTPUT / relative
        ] = content

    outputs[MANIFEST_FILE] = (
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8")
    )

    outputs[PREVIEW_FILE] = (
        make_preview(answer_data)
    )

    # ================================================
    # 15. KHONG GHI DE FILE KHAC NOI DUNG
    # ================================================

    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):

            raise RuntimeError(
                "File da ton tai voi "
                "noi dung khac:\n"
                + str(path)
            )

    # ================================================
    # 16. LUU FILE
    # ================================================

    for path, content in outputs.items():

        save_safe(path, content)

    # ================================================
    # 17. KET QUA
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH HSK3 DE 10 - BUOC 2"
    )

    print("=" * 60)

    print("Ma de goc: H31328")
    print("Tong cau: 80")

    print("Anh cau hoi: 70/70")
    print("Bang chung: 6/6")
    print("Tong anh: 76")

    print("Dap an: 80/80")

    print(f"\nManifest: {MANIFEST_FILE}")
    print(f"HTML: {PREVIEW_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
