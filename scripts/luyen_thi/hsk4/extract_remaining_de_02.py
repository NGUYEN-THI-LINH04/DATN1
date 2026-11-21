
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK4 DE 02 (H41002)
BUOC 2 - TACH 100 ANH CAU HOI

Ke thua cau truc HSK4 De 1.

- Tach 100 anh cau hoi.
- Tach 2 bang lua chon Doc 46-55.
- Giu doan chung 80-81, 82-83, 84-85.
- Tach 5 tranh Viet theo bo cuc 2 cot.
- Tao manifest JSON.
- Tao HTML xem truoc khong co dap an.
- Viet theo tranh cham tu dong theo cau mau.

KHONG thay doi SQL.
KHONG sua HSK4 De 1.
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

DATA = BASE / "hsk4" / "data" / "de_02"

OUT = BASE / "hsk4" / "output" / "de_02"

PDF_FILE = (
    BASE / "source" / "De_HSK"
    / "HSK4" / "H41002.pdf"
)

SOURCE_JSON = DATA / "de_02_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_100_cau_ung_vien.json"
)

HTML_FILE = OUT / "kiem_tra_100_cau.html"

CODE = "H41002"

ZOOM = 2.4


# =====================================================
# 2. SO DO CAU HOI THEO TRANG
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
# 3. HAI BANG LUA CHON DOC
# =====================================================

GROUPS = {
    "doc_46_50": (
        7, 46, 50, "ABCDEF"
    ),

    "doc_51_55": (
        8, 51, 55, "ABCDEF"
    ),
}


# =====================================================
# 4. TU CHO SAN VIET TRANH DE 2
# =====================================================

WORDS = {
    96: "吃惊",
    97: "汗",
    98: "挂",
    99: "香",
    100: "杂志",
}


# =====================================================
# 5. MAU NHAN DIEN SO CAU
# =====================================================

ANCHOR_RE = re.compile(
    r"^\s*(\d{1,3})"
    r"(?:\s*[-–—－~～]\s*(\d{1,3}))?"
    r"\s*[.．、]"
)


# =====================================================
# 6. KIEM TRA FILE
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


# =====================================================
# 7. DOC CAC DONG VAN BAN PDF
# =====================================================

def line_items(page):

    result = []

    for block in page.get_text("dict")["blocks"]:

        for line in block.get("lines", []):

            text = "".join(
                span.get("text", "")
                for span in line.get(
                    "spans", []
                )
            ).strip()

            if text:

                result.append((
                    text,
                    fitz.Rect(line["bbox"])
                ))

    return result


# =====================================================
# 8. TIM SO CAU
# =====================================================

def find_anchors(page, numbers, page_no):

    numbers = set(numbers)

    result = []

    # ================================================
    # TRANG 16: VIET TRANH HAI COT
    # ================================================

    if page_no == 16:

        # PDF co the gop cau 96 va 97
        # vao cung mot dong.
        #
        # Tim theo words de khong bo sot
        # cau 97 va 99 nhu loi truoc day.

        words = page.get_text("words")

        for number in sorted(numbers):

            matches = [
                fitz.Rect(word[:4])

                for word in words

                if re.fullmatch(
                    rf"{number}\s*[.．、]",
                    word[4]
                )
            ]

            matches = [
                rect

                for rect in matches

                if (
                    60 < rect.x0
                    < page.rect.width - 25
                )

                and (
                    page.rect.height * 0.35
                    < rect.y0
                    < page.rect.height - 60
                )
            ]

            if len(matches) != 1:

                raise RuntimeError(
                    f"Trang 16: cau {number}, "
                    f"tim thay {len(matches)} "
                    "vi tri."
                )

            result.append({
                "first": number,
                "last": number,
                "rect": matches[0]
            })

        result.sort(
            key=lambda item: (
                round(
                    item["rect"].y0 / 15
                ),
                item["rect"].x0
            )
        )

        return result

    # ================================================
    # TRANG 2-15: NOI DUNG MOT COT
    # ================================================

    for text, rect in line_items(page):

        match = ANCHOR_RE.match(text)

        if not match:
            continue

        first = int(match.group(1))

        last = int(
            match.group(2)
            or match.group(1)
        )

        found_range = set(
            range(first, last + 1)
        )

        if not found_range.issubset(
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
            f"\nTim: {found}"
        )

    return result


# =====================================================
# 9. XAC DINH CUOI NOI DUNG TRANG
# =====================================================

def bottom_content(page, last_anchor):

    limit = page.rect.height - 53

    for text, box in line_items(page):

        if (
            re.search(
                r"H41002\s*[-－–]\s*\d+",
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
            "H41002"
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
# 10. XUAT ANH PNG
# =====================================================

def pix_png(page, rect):

    if (
        rect.is_empty
        or not page.rect.contains(rect)
        or rect.height < 18
    ):

        raise RuntimeError(
            "Khung cat anh khong hop le: "
            + str(rect)
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
# 11. KIEM TRA LUA CHON A-F
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
            f"Cau {number} thieu lua chon."
            f"\nCan: {expected}"
            f"\nTim: {sorted(letters)}"
        )


# =====================================================
# 12. CAT CAC CAU TRANG 2-15
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

        # ============================================
        # 13. TIM RANH GIOI GIUA HAI CAU
        # ============================================

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

        text = page.get_text(
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
            text
        ):

            raise RuntimeError(
                f"Anh cau {first}-{last} "
                "bi mat so cau."
            )

        # ============================================
        # 14. KIEM TRA LUA CHON
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
        # 15. LUU ANH TUNG CAU
        # ============================================

        png = pix_png(
            page,
            rect
        )

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
                ]
            }

    return image_bytes, descriptions


# =====================================================
# 16. TIM CAC HINH NHUNG TRONG PDF
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
                abs(
                    rect.x0 - existing.x0
                ) < 0.5

                and abs(
                    rect.y0 - existing.y0
                ) < 0.5

                for existing in result
            )

            if not duplicate:
                result.append(rect)

    return result


# =====================================================
# 17. CAT CAU 96-100 THEO HAI COT
# =====================================================

def crop_pictures(page):

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
            "Trang 16 sai bo cuc."
        )

    by_number = {
        item["first"]: item["rect"]
        for item in anchors
    }

    pictures = image_rects(page)

    # Gom 1 anh vi du va 5 anh cau hoi.
    if len(pictures) < 6:

        raise RuntimeError(
            "Trang 16 thieu anh."
            "\nCan it nhat 6 anh."
        )

    result = {}

    descriptions = {}

    used = []

    half = page.rect.width / 2

    for number in range(96, 101):

        anchor = by_number[number]

        # 96 | 97
        # 98 | 99
        # 100
        left = number in (
            96, 98, 100
        )

        # ============================================
        # 18. TIM ANH CUNG COT VOI SO CAU
        # ============================================

        candidates = [
            rect
            for rect in pictures

            if (
                (
                    (
                        rect.x0 + rect.x1
                    ) / 2 < half
                ) == left
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
                f"Cau {number} khong "
                "tim thay anh minh hoa."
            )

        picture = candidates[0]

        tag = tuple(
            round(value, 1)
            for value in picture
        )

        if tag in used:

            raise RuntimeError(
                f"Cau {number} dung "
                "trung anh."
            )

        used.append(tag)

        # ============================================
        # 19. CAT CA HINH VA TU CHO SAN
        # ============================================

        rect = fitz.Rect(
            70 if left else half - 3,

            min(
                picture.y0,
                anchor.y0
            ) - 15,

            (
                half + 7
                if left
                else page.rect.width - 35
            ),

            max(
                picture.y1,
                anchor.y1
            ) + 17
        )

        text = page.get_text(
            "text",
            clip=rect
        )

        if not re.search(
            rf"(?<!\d){number}\s*[.．、]",
            text
        ):

            raise RuntimeError(
                f"Cau {number} "
                "bi mat so cau."
            )

        if WORDS[number] not in text:

            raise RuntimeError(
                f"Cau {number} "
                "bi mat tu cho san: "
                + WORDS[number]
            )

        if not rect.contains(picture):

            raise RuntimeError(
                f"Cau {number} "
                "bi cat mat hinh."
            )

        # ============================================
        # 20. XUAT ANH
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
            ]
        }

    return result, descriptions


# =====================================================
# 21. CAT HAI BANG DOC 46-55
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

        page = doc[
            page_no - 1
        ]

        lines = line_items(page)

        examples = [
            rect.y0

            for text, rect in lines

            if "例如" in text
        ]

        if len(examples) != 1:

            raise RuntimeError(
                f"Trang {page_no} "
                "khong tim dung vi du."
            )

        example_y = examples[0]

        words = page.get_text(
            "words"
        )

        selected = {}

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
                    f"Bang {name}: "
                    f"nhan {letter} co "
                    f"{len(candidates)} vi tri."
                )

            selected[letter] = (
                fitz.Rect(
                    candidates[0][:4]
                )
            )

        # ============================================
        # 22. A-F PHAI CUNG HANG
        # ============================================

        positions = [
            rect.y0
            for rect in selected.values()
        ]

        if (
            max(positions)
            - min(positions)
            > 16
        ):

            raise RuntimeError(
                f"Bang {name} "
                "A-F khong cung hang."
            )

        rect = fitz.Rect(
            70,

            min(positions) - 13,

            page.rect.width - 42,

            max(
                item.y1
                for item in selected.values()
            ) + 14
        )

        text = page.get_text(
            "text",
            clip=rect
        )

        if (
            "例如" in text

            or not re.search(
                r"[\u3400-\u9fff]",
                text
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
            ]
        }

    return files, manifest


# =====================================================
# 24. HTML KIEM TRA KHONG HIEN DAP AN
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
        # 25. BANG A-F CHI HIEN MOT LAN
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

    html = """
<!doctype html>
<html lang="vi">

<head>
<meta charset="utf-8">

<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>HSK4 Đề 2 - Kiểm tra 100 câu</title>

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

<h1>HSK4 – Đề 2 (H41002)</h1>

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
# 27. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)

    print(
        "MOC HAN - HSK4 DE 02"
    )

    print(
        "BUOC 2 - TACH 100 CAU HOI"
    )

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
    # 28. KIEM TRA JSON BUOC 1
    # ================================================

    identity = (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc")
    )

    if identity != (4, 2, CODE):

        raise RuntimeError(
            "JSON buoc 1 "
            "khong phai H41002."
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
            "JSON buoc 1 "
            "thieu 100 cau."
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

    # ================================================
    # 29. XAC NHAN CHAM TU DONG
    # ================================================

    if (
        source.get(
            "cau_can_cham_thu_cong"
        ) != []

        or source.get(
            "che_do_cham_viet_mo"
        ) != "cham_tu_dong_theo_mau"
    ):

        raise RuntimeError(
            "De 2 phai cham Viet "
            "theo tranh tu dong."
        )

    expected_words = {
        str(number): word
        for number, word in WORDS.items()
    }

    if (
        source.get(
            "tu_cho_san_viet_mo"
        ) != expected_words
    ):

        raise RuntimeError(
            "5 tu cho san "
            "khong khop PDF H41002."
        )

    if (
        set(
            source.get(
                "dap_an_tham_khao_viet_mo",
                {}
            )
        ) != {
            str(number)
            for number in range(96, 101)
        }
    ):

        raise RuntimeError(
            "Khong du 5 dap an "
            "tham khao Viet tranh."
        )

    if (
        set(
            source.get(
                "dap_an_thay_the",
                {}
            )
        ) != {"91"}
    ):

        raise RuntimeError(
            "De 2 chi co cau 91 "
            "co dap an thay the."
        )

    # ================================================
    # 30. TACH ANH TU PDF
    # ================================================

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
                "PDF khong phai H41002 "
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

        group_files, group_manifest = (
            crop_choice_groups(doc)
        )

        outputs.update(
            group_files
        )

    # ================================================
    # 31. KIEM TRA DU 100 CAU
    # ================================================

    if set(descriptions) != {
        str(number)
        for number in range(1, 101)
    }:

        raise RuntimeError(
            "Khong du 100 cau hoi."
        )

    if len(outputs) != 102:

        raise RuntimeError(
            "Khong du 102 anh."
            f"\nHien co: {len(outputs)}"
        )

    # ================================================
    # 32. TAO MANIFEST
    # ================================================

    manifest = {
        "cap_hsk": 4,

        "so_de": 2,

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

        "bang_lua_chon": group_manifest,

        "dap_an_thay_the": source.get(
            "dap_an_thay_the", {}
        ),

        "cau_can_cham_thu_cong": [],

        "che_do_cham_viet_mo": (
            "cham_tu_dong_theo_mau"
        )
    }

    # ================================================
    # 33. TAO JSON VA HTML
    # ================================================

    outputs[
        MANIFEST_JSON
    ] = json.dumps(
        manifest,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    outputs[
        HTML_FILE
    ] = build_html(
        descriptions
    )

    # ================================================
    # 34. KHONG GHI DE FILE KHAC NOI DUNG
    # ================================================

    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):

            raise RuntimeError(
                "File da ton tai "
                "voi noi dung khac."
                "\nKhong ghi de: "
                + str(path)
            )

    # ================================================
    # 35. LUU DU LIEU
    # ================================================

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
    # 36. KET QUA
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH HSK4 DE 02 - BUOC 2"
    )

    print("=" * 60)

    print("Ma de goc: H41002")

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
        "Che do cham: "
        "TU DONG THEO DAP AN MAU"
    )

    print(
        "HTML: khong hien thi dap an"
    )

    print(
        f"\nManifest: {MANIFEST_JSON}"
    )

    print(
        f"HTML: {HTML_FILE}"
    )

    print(
        "\nCHUA thay doi SQL Server."
    )


if __name__ == "__main__":
    main()
