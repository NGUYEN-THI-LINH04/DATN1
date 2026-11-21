
# -*- coding: utf-8 -*-
"""
MOC HAN - HSK4 DE 06 - BUOC 2

PDF nguon: H41006.pdf
Ma de goc trong PDF: H41008

Ke thua thuat toan da dung cho HSK4 De 5.

- Tach 100 anh cau hoi.
- Tach 2 bang lua chon A-F.
- Giu doan Doc chung 80-81, 82-83, 84-85.
- Tach 5 tranh Viet 96-100 tu anh nhung PDF.
- Tao manifest JSON va HTML xem truoc.

KHONG hien thi dap an.
KHONG ket noi SQL.
KHONG sua cac de cu.
"""

from html import escape
from pathlib import Path

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

DATA = BASE / "hsk4" / "data" / "de_06"

OUTPUT = BASE / "hsk4" / "output" / "de_06"

PDF_FILE = (
    BASE / "source" / "De_HSK"
    / "HSK4" / "H41006.pdf"
)

SOURCE_JSON = DATA / "de_06_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_100_cau_ung_vien.json"
)

HTML_FILE = OUTPUT / "kiem_tra_100_cau.html"

CODE = "H41008"
DE_NUMBER = 6

ZOOM = 2.4


# =====================================================
# 2. PHAN BO CAU THEO TRANG
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
# 3. BANG LUA CHON VA TU GOI Y
# =====================================================

GROUPS = {
    "doc_46_50": (7, 46, 50, "ABCDEF"),
    "doc_51_55": (8, 51, 55, "ABCDEF"),
}

WORDS = {
    96: "困",
    97: "味道",
    98: "怀疑",
    99: "来得及",
    100: "肚子",
}

ANCHOR_RE = re.compile(
    r"^\s*(\d{1,3})"
    r"(?:\s*[-–—－~～]\s*(\d{1,3}))?"
    r"\s*[.．、]"
)


# =====================================================
# 4. HAM HO TRO
# =====================================================

def require_file(path):

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

            value = "".join(
                span.get("text", "")
                for span in line.get("spans", [])
            ).strip()

            if value:
                result.append((
                    value,
                    fitz.Rect(line["bbox"])
                ))

    return result


# =====================================================
# 5. TIM SO CAU TU PDF
# =====================================================

def find_anchors(page, numbers, page_no):

    numbers = set(numbers)
    found = []

    # ================================================
    # TRANG 16 - TRANH VIET HAI COT
    # ================================================

    if page_no == 16:

        for number in sorted(numbers):

            matches = [
                fitz.Rect(word[:4])

                for word in page.get_text("words")

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
                    f"tim duoc {len(matches)} vi tri"
                )

            found.append({
                "first": number,
                "last": number,
                "rect": matches[0]
            })

        return sorted(
            found,

            key=lambda item: (
                round(
                    item["rect"].y0 / 15
                ),
                item["rect"].x0
            )
        )

    # ================================================
    # TRANG 2-15
    # ================================================

    for value, rect in line_items(page):

        match = ANCHOR_RE.match(value)

        if not match:
            continue

        first = int(match.group(1))

        last = int(
            match.group(2) or match.group(1)
        )

        if not set(
            range(first, last + 1)
        ).issubset(numbers):
            continue

        if not (40 < rect.x0 < 155):
            continue

        if not (
            45 < rect.y0
            < page.rect.height - 45
        ):
            continue

        found.append({
            "first": first,
            "last": last,
            "rect": rect
        })

    found.sort(
        key=lambda item: (
            item["rect"].y0,
            item["rect"].x0
        )
    )

    actual = [
        number

        for item in found

        for number in range(
            item["first"],
            item["last"] + 1
        )
    ]

    if sorted(actual) != sorted(numbers):

        raise RuntimeError(
            f"Trang {page_no} sai so cau.\n"
            f"Can: {sorted(numbers)}\n"
            f"Tim: {actual}"
        )

    return found


# =====================================================
# 6. TIM CUOI NOI DUNG TRANG
# =====================================================

def bottom_content(page, anchor):

    limit = page.rect.height - 53

    for value, rect in line_items(page):

        if (
            re.search(
                r"H41008\s*[-－–]\s*\d+",
                value
            )

            and rect.y0
            > page.rect.height * 0.72
        ):
            limit = min(
                limit,
                rect.y0 - 8
            )

    bottoms = [
        rect.y1

        for value, rect in line_items(page)

        if (
            anchor.y0 - 1
            <= rect.y0 < limit
        )

        and not value.startswith(CODE)
    ]

    return min(
        limit,

        max(
            bottoms,
            default=anchor.y1
        ) + 12
    )


# =====================================================
# 7. XUAT PNG
# =====================================================

def png_bytes(page, rect):

    if (
        rect.is_empty
        or not page.rect.contains(rect)
        or rect.height < 18
    ):
        raise RuntimeError(
            f"Khung cat khong hop le: {rect}"
        )

    pix = page.get_pixmap(
        matrix=fitz.Matrix(ZOOM, ZOOM),
        clip=rect,
        alpha=False
    )

    return pix.tobytes("png")


# =====================================================
# 8. KIEM TRA LUA CHON
# =====================================================

def check_choice_letters(
    page,
    rect,
    expected,
    number
):

    value = page.get_text(
        "text",
        clip=rect
    )

    letters = set(
        re.findall(
            r"(?<![A-Za-z])[A-F](?![A-Za-z])",
            value
        )
    ) & set(expected)

    if letters != set(expected):

        raise RuntimeError(
            f"Cau {number} thieu lua chon. "
            f"Can {expected}, "
            f"tim {sorted(letters)}"
        )


# =====================================================
# 9. CAT CAU 1-95
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

    files = {}
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

        value = page.get_text(
            "text",
            clip=rect
        )

        pattern = (
            rf"(?<!\d){first}"
            rf"\s*(?:[-–—－]\s*{last})?"
            r"\s*[.．、]"
        )

        if not re.search(pattern, value):

            raise RuntimeError(
                f"Cau {first}-{last} "
                "bi mat so cau"
            )

        # Kiem tra lua chon ABC / ABCD.
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

        image = png_bytes(
            page,
            rect
        )

        # Giu nguyen anh chung cua cac cap
        # 80-81, 82-83, 84-85.

        for number in range(
            first,
            last + 1
        ):

            relative = (
                f"questions/cau_{number:03d}.png"
            )

            files[OUTPUT / relative] = image

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
                    round(x, 2)
                    for x in rect
                ]
            }

    return files, descriptions


# =====================================================
# 10. TIM ANH NHUNG TRONG PDF
# =====================================================

def image_rects(page):

    result = []

    for item in page.get_images(full=True):

        for rect in page.get_image_rects(
            item[0]
        ):

            if (
                rect.width <= 35
                or rect.height <= 35
            ):
                continue

            duplicate = any(
                abs(rect.x0 - other.x0) < 0.5

                and abs(
                    rect.y0 - other.y0
                ) < 0.5

                for other in result
            )

            if not duplicate:
                result.append(rect)

    return result


# =====================================================
# 11. CAT TRANH VIET 96-100
# =====================================================

def crop_pictures(page):

    anchors = find_anchors(
        page,
        range(96, 101),
        16
    )

    by_number = {
        item["first"]: item["rect"]

        for item in anchors
    }

    pictures = image_rects(page)

    if len(pictures) < 6:

        raise RuntimeError(
            "Trang 16 thieu 1 anh vi du "
            "va 5 anh Viet"
        )

    files = {}
    descriptions = {}
    used = set()

    half = page.rect.width / 2

    for number in range(96, 101):

        anchor = by_number[number]

        # Bo cuc:
        # 96 | 97
        # 98 | 99
        # 100

        left = number in (
            96,
            98,
            100
        )

        if (
            (anchor.x0 < half) != left
        ):
            raise RuntimeError(
                f"Cau {number} sai cot"
            )

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
                f"Cau {number} "
                "khong tim thay tranh"
            )

        picture = candidates[0]

        picture_id = tuple(
            round(x, 1)
            for x in picture
        )

        if picture_id in used:

            raise RuntimeError(
                f"Cau {number} bi trung tranh"
            )

        used.add(picture_id)

        # Cat du tranh, so cau, tu goi y.

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

        value = page.get_text(
            "text",
            clip=rect
        )

        if not re.search(
            rf"(?<!\d){number}\s*[.．、]",
            value
        ):

            raise RuntimeError(
                f"Cau {number} mat so cau"
            )

        if WORDS[number] not in value:

            raise RuntimeError(
                f"Cau {number} mat tu "
                f"{WORDS[number]}"
            )

        if not rect.contains(picture):

            raise RuntimeError(
                f"Cau {number} bi cat mat tranh"
            )

        relative = (
            f"questions/cau_{number:03d}.png"
        )

        files[OUTPUT / relative] = png_bytes(
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
                round(x, 2)
                for x in rect
            ]
        }

    return files, descriptions


# =====================================================
# 12. CAT HAI BANG A-F
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

        examples = [
            rect.y0

            for value, rect in line_items(page)

            if "例如" in value
        ]

        if len(examples) != 1:

            raise RuntimeError(
                f"Trang {page_no} "
                "khong xac dinh duoc vi du"
            )

        selected = {}

        for letter in labels:

            candidates = [
                word

                for word in page.get_text("words")

                if word[4] == letter

                and (
                    100 < word[1]
                    < examples[0] - 15
                )
            ]

            if len(candidates) != 1:

                raise RuntimeError(
                    f"Bang {name}, nhan {letter}: "
                    f"tim {len(candidates)} vi tri"
                )

            selected[letter] = fitz.Rect(
                candidates[0][:4]
            )

        positions = [
            rect.y0
            for rect in selected.values()
        ]

        if (
            max(positions) - min(positions)
            > 16
        ):

            raise RuntimeError(
                f"Bang {name}: A-F khong cung hang"
            )

        rect = fitz.Rect(
            70,

            min(positions) - 13,

            page.rect.width - 42,

            max(
                r.y1
                for r in selected.values()
            ) + 14
        )

        value = page.get_text(
            "text",
            clip=rect
        )

        if (
            "例如" in value

            or not re.search(
                r"[\u3400-\u9fff]",
                value
            )
        ):

            raise RuntimeError(
                f"Bang {name} bi cat nham"
            )

        check_choice_letters(
            page,
            rect,
            labels,
            name
        )

        relative = f"groups/{name}.png"

        files[OUTPUT / relative] = png_bytes(
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
                round(x, 2)
                for x in rect
            ]
        }

    return files, manifest


# =====================================================
# 13. TAO HTML XEM TRUOC
# =====================================================

def build_html(descriptions):

    sections = []
    shown_shared = set()

    for number in range(1, 101):

        if number == 1:
            sections.append(
                "<h2>I. Nghe - Câu 1–45</h2>"
            )

        if number == 46:
            sections.append(
                "<h2>II. Đọc - Câu 46–85</h2>"
            )

        if number == 86:
            sections.append(
                "<h2>III. Viết - Câu 86–100</h2>"
            )

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
                'alt="Bảng A-F">'

                '</section>'
            )

        item = descriptions[str(number)]

        shared = item.get(
            "nhom_doc_chung"
        )

        if shared and shared in shown_shared:
            continue

        if shared:
            shown_shared.add(shared)

        label = (
            "Câu " + shared.replace("-", "–")

            if shared
            else f"Câu {number}"
        )

        src = escape(
            item["anh"],
            quote=True
        )

        sections.append(
            f'<section><h3>{label}</h3>'
            f'<img src="{src}" '
            f'alt="{label}"></section>'
        )

    html = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>HSK4 Đề 6 - Kiểm tra 100 câu</title>

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    padding: 20px;
    background: #f2f5fa;
    color: #17314e;
    font: 16px Arial, sans-serif;
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

h2 { margin-top: 36px; }
h3 { margin: 0 0 14px; }
small { color: #52677f; }
</style>
</head>

<body>
<main>

<h1>HSK4 - Đề 6 (mã PDF: H41008)</h1>

<p>
<small>
Ảnh lấy từ PDF gốc.
Không hiển thị đáp án.
Chưa nhập SQL Server.
</small>
</p>

__SECTIONS__

</main>
</body>
</html>"""

    return html.replace(
        "__SECTIONS__",
        "\n".join(sections)
    ).encode("utf-8")


# =====================================================
# 14. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 06 - BUOC 2")
    print("MA DE GOC PDF: H41008")
    print("=" * 60)

    require_file(PDF_FILE)

    source = json.loads(
        require_file(SOURCE_JSON).read_text(
            encoding="utf-8-sig"
        )
    )

    # ================================================
    # 15. KIEM TRA JSON BUOC 1
    # ================================================

    identity = (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc")
    )

    if identity != (4, DE_NUMBER, CODE):

        raise RuntimeError(
            "JSON buoc 1 khong phai "
            "De 6 / H41008"
        )

    if (
        source.get("tong_cau") != 100

        or set(
            source.get("dap_an", {})
        ) != {
            str(n)
            for n in range(1, 101)
        }
    ):

        raise RuntimeError(
            "JSON buoc 1 chua du 100 dap an"
        )

    if (
        Path(
            source.get("file_pdf", "")
        ).resolve()
        != PDF_FILE.resolve()
    ):

        raise RuntimeError(
            "Duong dan PDF khac JSON buoc 1"
        )

    # ================================================
    # 16. KIEM TRA CHAM VIET TU DONG
    # ================================================

    if (
        source.get("cau_can_cham_thu_cong") != []

        or source.get("che_do_cham_viet_mo")
        != "cham_tu_dong_theo_mau"
    ):

        raise RuntimeError(
            "De 6 phai cham Viet "
            "theo tranh tu dong"
        )

    if source.get(
        "tu_cho_san_viet_mo"
    ) != {
        str(n): word
        for n, word in WORDS.items()
    }:

        raise RuntimeError(
            "Tu cho san 96-100 khong khop PDF"
        )

    if set(
        source.get(
            "dap_an_tham_khao_viet_mo",
            {}
        )
    ) != {
        str(n)
        for n in range(96, 101)
    }:

        raise RuntimeError(
            "Thieu 5 cau mau Viet theo tranh"
        )

    if source.get("dap_an_thay_the") != {}:

        raise RuntimeError(
            "De 6 khong co dap an thay the"
        )

    # ================================================
    # 17. CAT 100 ANH TU PDF
    # ================================================

    outputs = {}
    descriptions = {}

    with fitz.open(PDF_FILE) as doc:

        if (
            len(doc) != 24

            or CODE not in doc[0].get_text("text")

            or CODE not in doc[22].get_text("text")
        ):

            raise RuntimeError(
                "PDF phai co 24 trang "
                "va ma goc H41008"
            )

        for page_no, numbers in PAGE_MAP.items():

            if page_no == 16:

                images, items = crop_pictures(
                    doc[15]
                )

            else:

                images, items = crop_normal_page(
                    doc[page_no - 1],
                    page_no,
                    numbers
                )

            outputs.update(images)
            descriptions.update(items)

            print(
                f"Trang {page_no}: "
                f"{len(items)} cau"
            )

        group_files, group_manifest = (
            crop_choice_groups(doc)
        )

        outputs.update(group_files)

    # ================================================
    # 18. KIEM TRA DU 102 ANH
    # ================================================

    if set(descriptions) != {
        str(n) for n in range(1, 101)
    }:

        raise RuntimeError(
            "Khong du 100 anh cau hoi"
        )

    if len(outputs) != 102:

        raise RuntimeError(
            f"Can 102 anh, "
            f"hien co {len(outputs)}"
        )

    # ================================================
    # 19. TAO MANIFEST
    # ================================================

    manifest = {

        "cap_hsk": 4,

        "so_de": DE_NUMBER,

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
            str(n): descriptions[str(n)]
            for n in range(1, 101)
        },

        "bang_lua_chon": group_manifest,

        "dap_an_thay_the": {},

        "cau_can_cham_thu_cong": [],

        "che_do_cham_viet_mo": (
            "cham_tu_dong_theo_mau"
        )
    }

    outputs[MANIFEST_JSON] = json.dumps(
        manifest,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    outputs[HTML_FILE] = build_html(
        descriptions
    )

    # ================================================
    # 20. KHONG GHI DE FILE CU KHAC NOI DUNG
    # ================================================

    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):

            raise RuntimeError(
                "File da ton tai voi "
                "noi dung khac.\n"
                "KHONG ghi de:\n"
                + str(path)
            )

    # ================================================
    # 21. LUU ANH, MANIFEST, HTML
    # ================================================

    for path, content in outputs.items():

        if not path.exists():

            path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            path.write_bytes(content)

    # ================================================
    # 22. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH HSK4 DE 06 - BUOC 2")
    print("=" * 60)

    print("Anh cau hoi: 100/100")
    print("Bang lua chon A-F: 2/2")

    print(
        "Doc chung: "
        "80-81, 82-83, 84-85"
    )

    print(
        "Viet tranh 96-100: "
        "5/5 anh co tu cho san"
    )

    print(
        "Che do cham: "
        "TU DONG THEO MAU"
    )

    print(f"Manifest: {MANIFEST_JSON}")
    print(f"HTML: {HTML_FILE}")

    print("CHUA thay doi SQL Server")


if __name__ == "__main__":
    main()
