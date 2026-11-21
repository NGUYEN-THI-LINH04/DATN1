
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK4 DE 01 (H41001)
BUOC 2 - TACH HINH CAU HOI

- Tach 100 anh cau hoi.
- Tach 2 bang lua chon Doc 46-55.
- Giu nguyen doan chung 80-81, 82-83, 84-85.
- Tach 5 cau Viet tranh theo bo cuc 2 cot.
- Tao manifest JSON va HTML xem truoc.
- Khong hien dap an trong HTML.

KHONG sua SQL Server.
KHONG sua cac de thi cu.
KHONG ghi de file khac noi dung.
"""

from pathlib import Path
from html import escape

import json
import os
import re

import fitz


# =====================================================
# 1. CAU HINH
# =====================================================

ROOT = Path(
    os.environ.get(
        "MOC_HAN_ROOT",
        r"D:\DATN1"
    )
)

BASE = ROOT / "scripts" / "luyen_thi"

DATA = BASE / "hsk4" / "data" / "de_01"

OUT = BASE / "hsk4" / "output" / "de_01"

PDF_FILE = (
    BASE / "source" / "De_HSK"
    / "HSK4" / "H41001.pdf"
)

SOURCE_JSON = DATA / "de_01_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_100_cau_ung_vien.json"
)

HTML_FILE = OUT / "kiem_tra_100_cau.html"

ZOOM = 2.4

CODE = "H41001"


# =====================================================
# 2. SO DO CAU HOI THEO TRANG PDF
# =====================================================

PAGE_MAP = {
    2: range(1, 11),

    3: range(11, 21),
    4: range(21, 26),

    5: range(26, 35),
    6: range(35, 46),

    7: range(46, 51),
    8: range(51, 56),

    9: range(56, 60),
    10: range(60, 66),

    11: range(66, 70),
    12: range(70, 76),

    13: range(76, 82),
    14: range(82, 86),

    15: range(86, 96),
    16: range(96, 101),
}


# =====================================================
# 3. BANG LUA CHON CHUNG
# =====================================================

GROUPS = {
    "doc_46_50": (7, 46, 50, "ABCDEF"),
    "doc_51_55": (8, 51, 55, "ABCDEF"),
}


# =====================================================
# 4. TU CHO SAN - VIET TRANH
# =====================================================

WORDS = {
    96: "日记",
    97: "尝",
    98: "破",
    99: "凉快",
    100: "活泼",
}


# =====================================================
# 5. NHAN SO CAU TRONG PDF
# =====================================================

ANCHOR_RE = re.compile(
    r"^\s*(\d{1,3})"
    r"(?:\s*[-–—－~～]\s*(\d{1,3}))?"
    r"\s*[.．、]"
)


# =====================================================
# 6. HAM HO TRO
# =====================================================

def require(path):

    if (
        not path.is_file()
        or path.stat().st_size == 0
    ):
        raise RuntimeError(
            f"Thieu file hoac file rong: {path}"
        )

    return path


def line_items(page):

    result = []

    for block in page.get_text("dict")["blocks"]:

        for line in block.get("lines", []):

            text = "".join(
                span.get("text", "")
                for span in line.get("spans", [])
            ).strip()

            if text:

                result.append((
                    text,
                    fitz.Rect(line["bbox"])
                ))

    return result


# =====================================================
# 7. TIM VI TRI CAC SO CAU
# =====================================================


# =====================================================
# 7. TIM VI TRI SO CAU TRONG PDF
# =====================================================

def find_anchors(page, numbers, page_no):

    numbers = set(numbers)

    # ================================================
    # TRANG 16: 5 CAU VIET TRANH, BO CUC 2 COT
    # ================================================

    if page_no == 16:

        result = []

        for number in sorted(numbers):

            candidates = []

            # Tim truc tiep vi tri so cau trong PDF,
            # khong phu thuoc dau dong van ban.
            for ending in ("．", ".", "、"):

                keyword = f"{number}{ending}"

                candidates.extend(
                    page.search_for(keyword)
                )

            # Neu PDF tach so cau thanh mot tu rieng,
            # thu tim qua get_text("words").
            if not candidates:

                for word in page.get_text("words"):

                    value = str(word[4]).strip()

                    if re.fullmatch(
                        rf"{number}\s*[.．、]",
                        value
                    ):

                        candidates.append(
                            fitz.Rect(word[:4])
                        )

            # Du phong khi PDF gop 2 cot
            # vao cung mot dong van ban.
            if not candidates:

                for block in page.get_text(
                    "rawdict"
                )["blocks"]:

                    for line in block.get(
                        "lines", []
                    ):

                        chars = [
                            char

                            for span in line.get(
                                "spans", []
                            )

                            for char in span.get(
                                "chars", []
                            )
                        ]

                        content = "".join(
                            char["c"]
                            for char in chars
                        )

                        pattern = re.compile(
                            rf"(?<!\d){number}"
                            r"\s*[.．、]"
                        )

                        for match in pattern.finditer(
                            content
                        ):

                            selected = chars[
                                match.start():
                                match.end()
                            ]

                            boxes = [
                                fitz.Rect(
                                    char["bbox"]
                                )
                                for char in selected
                                if not char["c"].isspace()
                            ]

                            if boxes:

                                rect = boxes[0]

                                for box in boxes[1:]:
                                    rect |= box

                                candidates.append(rect)

            # ========================================
            # LOC VI TRI SO CAU THUC TE
            # ========================================

            valid = []

            for rect in candidates:

                if not (
                    45 < rect.x0
                    < page.rect.width - 25
                ):
                    continue

                if not (
                    page.rect.height * 0.28
                    < rect.y0
                    < page.rect.height - 65
                ):
                    continue

                # Bo ket qua trung toa do.
                if any(
                    abs(rect.x0 - old.x0) < 2
                    and abs(rect.y0 - old.y0) < 2

                    for old in valid
                ):
                    continue

                valid.append(rect)

            if len(valid) != 1:

                raise RuntimeError(
                    f"Trang 16: khong xac dinh "
                    f"duoc duy nhat cau {number}."
                    f"\nSo vi tri: {len(valid)}"
                    f"\nVi tri: {valid}"
                )

            result.append({
                "first": number,
                "last": number,
                "rect": valid[0]
            })

        # Sap xep theo hang roi den cot.
        result.sort(
            key=lambda item: (
                round(
                    item["rect"].y0 / 15
                ),
                item["rect"].x0
            )
        )

        found = [
            item["first"]
            for item in result
        ]

        if set(found) != numbers:

            raise RuntimeError(
                f"Trang 16 sai so cau: {found}"
            )

        print(
            "Trang 16 - da nhan dien:",
            ", ".join(
                str(number)
                for number in found
            )
        )

        return result

    # ================================================
    # CAC TRANG 2-15: GIU NGUYEN LOGIC CU
    # ================================================

    result = []

    for text, rect in line_items(page):

        match = ANCHOR_RE.match(text)

        if not match:
            continue

        first = int(match.group(1))

        last = int(
            match.group(2) or first
        )

        question_numbers = set(
            range(first, last + 1)
        )

        if not question_numbers.issubset(
            numbers
        ):
            continue

        if not 40 < rect.x0 < 155:
            continue

        if not (
            45 < rect.y0
            < page.rect.height - 45
        ):
            continue

        result.append({
            "first": first,
            "last": last,
            "rect": rect
        })

    result.sort(
        key=lambda item: (
            item["rect"].y0,
            item["rect"].x0
        )
    )

    found = []

    for item in result:

        found.extend(
            range(
                item["first"],
                item["last"] + 1
            )
        )

    if sorted(found) != sorted(numbers):

        raise RuntimeError(
            f"Trang {page_no} sai so cau."
            f"\nCan: {sorted(numbers)}"
            f"\nTim duoc: {found}"
        )

    return result



# =====================================================
# 8. XAC DINH CUOI NOI DUNG TRANG
# =====================================================

def bottom_content(page, last_anchor):

    limit = page.rect.height - 53

    for text, box in line_items(page):

        if (
            re.search(
                r"H41001\s*[-－–]\s*\d+",
                text
            )
            and box.y0
            > page.rect.height * 0.72
        ):

            limit = min(
                limit,
                box.y0 - 8
            )

    bottoms = [
        box.y1

        for text, box in line_items(page)

        if (
            last_anchor.y0 - 1
            <= box.y0 < limit
        )

        and not text.startswith(
            "H41001"
        )
    ]

    return min(
        limit,
        max(
            bottoms,
            default=last_anchor.y1
        ) + 12
    )


# =====================================================
# 9. XUAT ANH PNG
# =====================================================

def pix_png(page, rect):

    if (
        rect.is_empty
        or not page.rect.contains(rect)
        or rect.height < 18
    ):

        raise RuntimeError(
            f"Khung cat khong hop le: {rect}"
        )

    pix = page.get_pixmap(
        matrix=fitz.Matrix(
            ZOOM,
            ZOOM
        ),
        clip=rect,
        alpha=False
    )

    return pix.tobytes("png")


# =====================================================
# 10. KIEM TRA LUA CHON
# =====================================================

def check_choice_letters(
    page,
    rect,
    expected,
    number
):

    text = page.get_text(
        "text",
        clip=rect
    )

    letters = set(
        re.findall(
            r"(?<![A-Za-z])[A-F](?![A-Za-z])",
            text
        )
    ) & set(expected)

    if letters != set(expected):

        raise RuntimeError(
            f"Cau {number} "
            "thieu lua chon."
            f"\nCan: {expected}"
            f"\nTim: {sorted(letters)}"
        )


# =====================================================
# 11. CAT CAU HOI TRANG 2-15
# =====================================================

def crop_normal_page(
    page,
    page_no,
    numbers
):

    anchors = find_anchors(
        page,
        numbers,
        page_no
    )

    image_bytes = {}

    descriptions = {}

    for index, item in enumerate(anchors):

        first = item["first"]
        last = item["last"]

        top = max(
            0,
            item["rect"].y0 - 11
        )

        if index + 1 < len(anchors):

            bottom = (
                anchors[index + 1]["rect"].y0
                - 9
            )

        else:

            bottom = bottom_content(
                page,
                item["rect"]
            )

        rect = fitz.Rect(
            70,
            top,
            page.rect.width - 48,
            bottom
        )

        clipped = page.get_text(
            "text",
            clip=rect
        )

        pattern = (
            rf"(?<!\d){first}"
            rf"\s*(?:[-–—－]\s*{last})?"
            r"\s*[.．、]"
        )

        if not re.search(
            pattern,
            clipped
        ):

            raise RuntimeError(
                f"Anh cau {first}-{last} "
                "bi mat so cau."
            )

        # ============================================
        # 12. KIEM TRA DANG LUA CHON
        # ============================================

        if (
            11 <= first <= 45
            or 56 <= first <= 85
        ):

            expected = (
                "ABC"
                if 56 <= first <= 65
                else "ABCD"
            )

            check_choice_letters(
                page,
                rect,
                expected,
                first
            )

        # ============================================
        # 13. LUU ANH
        # ============================================

        png = pix_png(
            page,
            rect
        )

        # Cac cau doc chung doan:
        # 80-81, 82-83, 84-85
        # moi cau co duong dan anh rieng,
        # nhung su dung cung noi dung doan.

        for number in range(
            first,
            last + 1
        ):

            relative = (
                "questions/"
                f"cau_{number:03d}.png"
            )

            image_bytes[
                OUT / relative
            ] = png

            if 46 <= number <= 50:
                group = "doc_46_50"

            elif 51 <= number <= 55:
                group = "doc_51_55"

            else:
                group = None

            descriptions[str(number)] = {
                "trang_pdf": page_no,

                "anh": relative,

                "nhom_lua_chon": group,

                "nhom_doc_chung": (
                    f"{first}-{last}"
                    if first < last
                    else None
                ),

                "toa_do": [
                    round(value, 2)
                    for value in rect
                ],
            }

    return image_bytes, descriptions


# =====================================================
# 14. TIM HINH ANH NHO TRONG PDF
# =====================================================

def image_rects(page):

    result = []

    for image in page.get_images(
        full=True
    ):

        for rect in page.get_image_rects(
            image[0]
        ):

            if (
                rect.width <= 35
                or rect.height <= 35
            ):
                continue

            duplicate = any(
                abs(rect.x0 - existing.x0) < 0.5
                and abs(rect.y0 - existing.y0) < 0.5

                for existing in result
            )

            if not duplicate:

                result.append(rect)

    return result


# =====================================================
# 15. CAT 5 CAU VIET TRANH HAI COT
# =====================================================

def crop_pictures(page):

    """
    Bo cuc trang 16:

    96 | 97
    98 | 99
    100

    Moi cau phai gom:
    - So cau
    - Hinh minh hoa
    - Tu cho san
    """

    anchors = find_anchors(
        page,
        range(96, 101),
        16
    )

    if any(
        item["first"] != item["last"]
        for item in anchors
    ):

        raise RuntimeError(
            "Trang 16 sai bo cuc 5 cau."
        )

    by_number = {
        item["first"]: item["rect"]
        for item in anchors
    }

    pictures = image_rects(page)

    # 1 anh vi du + 5 anh cau hoi.
    if len(pictures) < 6:

        raise RuntimeError(
            "Trang 16 thieu anh."
            "\nCan it nhat 6 anh "
            "(bao gom 1 anh vi du)."
        )

    result = {}

    descriptions = {}

    used = []

    half = page.rect.width / 2

    for number in range(96, 101):

        anchor = by_number[number]

        is_left = number in (
            96, 98, 100
        )

        # ============================================
        # 16. TIM HINH DUNG COT
        # ============================================

        candidates = [
            rect
            for rect in pictures

            if (
                (
                    (
                        rect.x0 + rect.x1
                    ) / 2 < half
                ) == is_left
            )

            and abs(
                rect.y1 - anchor.y0
            ) < 85
        ]

        candidates.sort(
            key=lambda rect: (
                abs(
                    rect.y1 - anchor.y0
                ),
                abs(
                    rect.y0 - anchor.y0
                )
            )
        )

        if not candidates:

            raise RuntimeError(
                f"Cau {number} "
                "khong tim thay "
                "anh minh hoa."
            )

        picture = candidates[0]

        tag = tuple(
            round(value, 1)
            for value in picture
        )

        if tag in used:

            raise RuntimeError(
                f"Cau {number} "
                "dung trung anh."
            )

        used.append(tag)

        # ============================================
        # 17. CAT TRON HINH VA TU
        # ============================================

        rect = fitz.Rect(
            70 if is_left else half - 3,

            min(
                picture.y0,
                anchor.y0
            ) - 15,

            (
                half + 7
                if is_left
                else page.rect.width - 35
            ),

            max(
                picture.y1,
                anchor.y1
            ) + 17
        )

        clipped = page.get_text(
            "text",
            clip=rect
        )

        if not re.search(
            rf"(?<!\d){number}\s*[.．、]",
            clipped
        ):

            raise RuntimeError(
                f"Cau {number} "
                "bi mat so cau."
            )

        if WORDS[number] not in clipped:

            raise RuntimeError(
                f"Cau {number} "
                "bi mat tu cho san: "
                + WORDS[number]
            )

        if not rect.contains(
            picture
        ):

            raise RuntimeError(
                f"Cau {number} "
                "bi cat mat hinh."
            )

        # ============================================
        # 18. XUAT HINH
        # ============================================

        relative = (
            "questions/"
            f"cau_{number:03d}.png"
        )

        result[
            OUT / relative
        ] = pix_png(
            page,
            rect
        )

        descriptions[str(number)] = {
            "trang_pdf": 16,

            "anh": relative,

            "nhom_lua_chon": None,

            "nhom_doc_chung": None,

            "tu_cho_san": WORDS[number],

            "toa_do": [
                round(value, 2)
                for value in rect
            ],
        }

    return result, descriptions


# =====================================================
# 19. CAT HAI BANG DOC 46-55
# =====================================================

def crop_choice_groups(doc):

    files = {}

    manifest = {}

    for name, (
        page_no,
        first,
        last,
        labels
    ) in GROUPS.items():

        page = doc[page_no - 1]

        lines = line_items(page)

        # Tim dong "例如" de tranh cat nham vi du.
        examples = [
            rect.y0

            for text, rect in lines

            if "例如" in text
        ]

        if len(examples) != 1:

            raise RuntimeError(
                f"Trang {page_no} "
                "khong tim dung dong vi du."
            )

        example_y = examples[0]

        words = page.get_text(
            "words"
        )

        selected = {}

        # ============================================
        # 20. TIM A-F
        # ============================================

        for letter in labels:

            candidates = [
                word

                for word in words

                if (
                    word[4] == letter

                    and 100 < word[1]
                    < example_y - 15
                )
            ]

            if len(candidates) != 1:

                raise RuntimeError(
                    f"Bang {name}, "
                    f"nhan {letter}: "
                    f"{len(candidates)} vi tri."
                )

            selected[letter] = (
                fitz.Rect(
                    candidates[0][:4]
                )
            )

        # ============================================
        # 21. KIEM TRA CAC NHAN CUNG HANG
        # ============================================

        y_values = [
            rect.y0
            for rect in selected.values()
        ]

        if (
            max(y_values)
            - min(y_values)
            > 16
        ):

            raise RuntimeError(
                f"Bang {name} "
                "A-F khong cung hang."
            )

        # ============================================
        # 22. TAO KHUNG BANG
        # ============================================

        rect = fitz.Rect(
            70,

            min(y_values) - 13,

            page.rect.width - 42,

            max(
                rect.y1
                for rect in selected.values()
            ) + 14
        )

        clipped = page.get_text(
            "text",
            clip=rect
        )

        if (
            "例如" in clipped

            or not re.search(
                r"[\u3400-\u9fff]",
                clipped
            )
        ):

            raise RuntimeError(
                f"Bang {name} "
                "bi dinh vi du "
                "hoac thieu chu Han."
            )

        check_choice_letters(
            page,
            rect,
            labels,
            name
        )

        # ============================================
        # 23. XUAT BANG
        # ============================================

        relative = (
            f"groups/{name}.png"
        )

        files[
            OUT / relative
        ] = pix_png(
            page,
            rect
        )

        manifest[name] = {
            "trang_pdf": page_no,

            "cau_tu": first,

            "cau_den": last,

            "lua_chon": labels,

            "anh": relative,

            "toa_do": [
                round(value, 2)
                for value in rect
            ],
        }

    return files, manifest


# =====================================================
# 24. TAO HTML KIEM TRA 100 CAU
# =====================================================

def build_html(descriptions):

    sections = []

    shown_shared = set()

    for number in range(1, 101):

        if number == 1:

            sections.append(
                "<h2>I. Nghe – Câu 1–45</h2>"
            )

        if number == 46:

            sections.append(
                "<h2>II. Đọc – Câu 46–85</h2>"
            )

        if number == 86:

            sections.append(
                "<h2>III. Viết – Câu 86–100</h2>"
            )

        # ============================================
        # 25. BANG DOC CHUNG HIEN THI MOT LAN
        # ============================================

        if number in (46, 51):

            name = (
                "doc_46_50"
                if number == 46
                else "doc_51_55"
            )

            sections.append(
                '<section class="shared">'
                f'<h3>Bảng lựa chọn câu '
                f'{number}–{number + 4}</h3>'
                f'<img src="groups/{name}.png" '
                'alt="Bảng A–F">'
                '</section>'
            )

        item = descriptions[
            str(number)
        ]

        shared = item.get(
            "nhom_doc_chung"
        )

        # ============================================
        # 26. DOAN DOC CHUNG CHI HIEN MOT LAN
        # ============================================

        if shared and shared in shown_shared:
            continue

        if shared:
            shown_shared.add(shared)

        label = (
            "Câu " + shared.replace("-", "–")
            if shared
            else f"Câu {number}"
        )

        relative = escape(
            item["anh"],
            quote=True
        )

        sections.append(
            "<section>"
            f"<h3>{label}</h3>"
            f'<img src="{relative}" '
            f'alt="{label}">'
            "</section>"
        )

    # ================================================
    # 27. CSS HTML
    # ============================================

    html = """
<!doctype html>
<html lang="vi">

<head>
<meta charset="utf-8">

<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>HSK4 Đề 1 - Kiểm tra 100 câu</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    background: #f2f5fa;
    font: 16px Arial, sans-serif;
    color: #17314e;
}

main {
    max-width: 960px;
    margin: auto;
}

section {
    background: #fff;
    border: 1px solid #dbe3ef;
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
}

section.shared {
    background: #f7faff;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
}

h2 {
    margin-top: 36px;
}

h3 {
    margin: 0 0 14px;
}

small {
    color: #52677f;
}
</style>

</head>

<body>
<main>

<h1>HSK4 – Đề 1 (H41001)</h1>

<small>
Ảnh lấy từ PDF gốc.
Không hiển thị đáp án.
Chưa nhập SQL.
</small>

__SECTIONS__

</main>
</body>
</html>
"""

    return html.replace(
        "__SECTIONS__",
        "\n".join(sections)
    ).encode("utf-8")


# =====================================================
# 28. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 01")
    print("BUOC 2 - TACH 100 CAU HOI")
    print("=" * 60)

    require(PDF_FILE)

    source = json.loads(
        require(
            SOURCE_JSON
        ).read_text(
            encoding="utf-8-sig"
        )
    )

    # ================================================
    # 29. KIEM TRA JSON BUOC 1
    # ============================================

    identity = (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc")
    )

    if identity != (4, 1, CODE):

        raise RuntimeError(
            "JSON buoc 1 khong phai H41001."
        )

    if (
        source.get("tong_cau") != 100

        or set(
            source.get("dap_an", {})
        ) != {
            str(number)
            for number in range(1, 101)
        }
    ):

        raise RuntimeError(
            "JSON buoc 1 thieu 100 cau."
        )

    if (
        Path(
            source.get("file_pdf", "")
        ).resolve()
        != PDF_FILE.resolve()
    ):

        raise RuntimeError(
            "PDF khong khop buoc 1."
        )

    if (
        source.get(
            "cau_can_cham_thu_cong"
        ) != list(range(96, 101))
    ):

        raise RuntimeError(
            "Cau 96-100 chua "
            "duoc danh dau cham thu cong."
        )

    # ================================================
    # 30. DOC PDF VA TACH ANH
    # ============================================

    outputs = {}

    descriptions = {}

    with fitz.open(PDF_FILE) as doc:

        if (
            len(doc) != 24
            or CODE not in doc[0].get_text(
                "text"
            )
        ):

            raise RuntimeError(
                "PDF khong phai H41001 "
                "24 trang."
            )

        for page_no, numbers in (
            PAGE_MAP.items()
        ):

            if page_no == 16:

                pictures, items = (
                    crop_pictures(
                        doc[15]
                    )
                )

            else:

                pictures, items = (
                    crop_normal_page(
                        doc[page_no - 1],
                        page_no,
                        numbers
                    )
                )

            outputs.update(
                pictures
            )

            descriptions.update(
                items
            )

            print(
                f"Trang {page_no}: "
                f"{len(items)} cau"
            )

        # ============================================
        # 31. TACH HAI BANG DOC
        # ============================================

        group_files, group_manifest = (
            crop_choice_groups(doc)
        )

        outputs.update(
            group_files
        )

    # ================================================
    # 32. KIEM TRA 100 CAU
    # ============================================

    if set(descriptions) != {
        str(number)
        for number in range(1, 101)
    }:

        raise RuntimeError(
            "Khong du 100 anh cau hoi."
        )

    if len(outputs) != 102:

        raise RuntimeError(
            "Khong du 102 hinh "
            "(100 cau + 2 bang)."
            f"\nHien co: {len(outputs)}"
        )

    # ================================================
    # 33. TAO MANIFEST
    # ============================================

    manifest = {
        "cap_hsk": 4,
        "so_de": 1,
        "ma_de_goc": CODE,

        "so_trang_pdf": 24,

        "so_cau": 100,

        "so_cau_nghe": 45,
        "so_cau_doc": 40,
        "so_cau_viet": 15,

        "trang_cau_hoi": list(
            range(2, 17)
        ),

        "trang_loi_thoai": list(
            range(17, 23)
        ),

        "trang_dap_an": [23, 24],

        "cau_hoi": {
            str(number): descriptions[
                str(number)
            ]

            for number in range(1, 101)
        },

        "bang_lua_chon": (
            group_manifest
        ),

        "dap_an_thay_the": (
            source.get(
                "dap_an_thay_the", {}
            )
        ),

        "cau_can_cham_thu_cong": list(
            range(96, 101)
        ),
    }

    # ================================================
    # 34. THEM JSON VA HTML
    # ============================================

    outputs[MANIFEST_JSON] = json.dumps(
        manifest,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    outputs[HTML_FILE] = build_html(
        descriptions
    )

    # ================================================
    # 35. KIEM TRA TRUOC KHI GHI FILE
    # ============================================

    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):

            raise RuntimeError(
                "File da ton tai "
                "voi noi dung khac."
                "\nKHONG ghi de:\n"
                + str(path)
            )

    # ================================================
    # 36. LUU DU LIEU
    # ============================================

    for path, content in outputs.items():

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not path.exists():

            path.write_bytes(
                content
            )

    # ================================================
    # 37. KET QUA
    # ============================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH HSK4 DE 01 - BUOC 2"
    )

    print("=" * 60)

    print("Ma de goc: H41001")

    print("Anh cau hoi: 100/100")

    print("Bang Doc chung: 2/2")

    print(
        "Cau Doc dung chung: "
        "80-81, 82-83, 84-85"
    )

    print(
        "Viet tranh 96-100: "
        "5/5 anh co tu cho san"
    )

    print(
        "HTML: khong hien dap an"
    )

    print(f"\nManifest: {MANIFEST_JSON}")
    print(f"HTML: {HTML_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
