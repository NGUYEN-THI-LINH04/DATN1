
# -*- coding: utf-8 -*-
"""
MOC HAN - HSK4 DE 07 (H41327)
BUOC 2 - TACH 100 ANH CAU HOI

Ke thua thuat toan HSK4 De 5.

- PDF de: H41007.pdf (16 trang).
- PDF dap an: H41007_dap_an.pdf (2 trang).
- Tach 100 anh cau hoi va 2 bang A-F.
- Giu doan Doc chung 80-81, 82-83, 84-85.
- Tach 5 tranh Viet 96-100 tu anh nhung PDF.
- Tao manifest JSON va HTML xem truoc.
- Khong hien thi dap an.

KHONG ket noi SQL Server.
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
    os.environ.get("MOC_HAN_ROOT", r"D:\DATN1")
)

BASE = ROOT / "scripts" / "luyen_thi"

DATA = BASE / "hsk4" / "data" / "de_07"
OUTPUT = BASE / "hsk4" / "output" / "de_07"

SOURCE = BASE / "source" / "De_HSK" / "HSK4"

PDF_FILE = SOURCE / "H41007.pdf"
ANSWER_PDF = SOURCE / "H41007_dap_an.pdf"

SOURCE_JSON = DATA / "de_07_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_100_cau_ung_vien.json"
)

HTML_FILE = OUTPUT / "kiem_tra_100_cau.html"

CODE = "H41327"
DE_NUMBER = 7

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

GROUPS = {
    "doc_46_50": (7, 46, 50, "ABCDEF"),
    "doc_51_55": (8, 51, 55, "ABCDEF"),
}

WORDS = {
    96: "轻",
    97: "答案",
    98: "钥匙",
    99: "激动",
    100: "聊天儿",
}

ANCHOR_RE = re.compile(
    r"^\s*(\d{1,3})"
    r"(?:\s*[-–—－~～]\s*(\d{1,3}))?"
    r"\s*[.．、]"
)


# =====================================================
# 3. HAM HO TRO
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
# 4. TIM VI TRI SO CAU
# =====================================================

def find_anchors(page, numbers, page_no):

    numbers = set(numbers)
    found = []

    # Trang 16: 5 tranh Viet hai cot.
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
                rect for rect in matches

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
                "rect": matches[0],
            })

        return sorted(
            found,
            key=lambda item: (
                round(
                    item["rect"].y0 / 15
                ),
                item["rect"].x0,
            )
        )

    # Trang 2-15.
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
            "rect": rect,
        })

    found.sort(
        key=lambda item: (
            item["rect"].y0,
            item["rect"].x0,
        )
    )

    actual = [
        n
        for item in found
        for n in range(
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
# 5. TIM CUOI NOI DUNG TRANG
# =====================================================

def bottom_content(page, anchor):

    limit = page.rect.height - 53

    for value, rect in line_items(page):

        if (
            re.search(
                rf"{CODE}\s*[-－–]\s*\d+",
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
# 6. XUAT ANH PNG
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
        alpha=False,
    )

    return pix.tobytes("png")


# =====================================================
# 7. KIEM TRA LUA CHON
# =====================================================

def check_choice_letters(
    page, rect, expected, number
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
# 8. CAT CAU 1-95
# =====================================================

def crop_normal_page(page, page_no, numbers):

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
                f"Cau {first}-{last} bi mat so cau"
            )

        # Kiem tra ABC / ABCD.
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

        image = png_bytes(page, rect)

        # Cac cau 80-85 dung chung doan van.
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
                ],
            }

    return files, descriptions


# =====================================================
# 9. TIM ANH NHUNG TRONG PDF
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
                and abs(rect.y0 - other.y0) < 0.5

                for other in result
            )

            if not duplicate:
                result.append(rect)

    return result


# =====================================================
# 10. CAT 5 TRANH VIET 96-100
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
            96, 98, 100
        )

        if (anchor.x0 < half) != left:

            raise RuntimeError(
                f"Cau {number} sai cot"
            )

        candidates = [
            rect

            for rect in pictures

            if (
                (
                    (rect.x0 + rect.x1) / 2
                    < half
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
                f"Cau {number} khong tim thay tranh"
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

        # Cat du hinh, so cau va tu goi y.
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
            ) + 17,
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
            ],
        }

    return files, descriptions


# =====================================================
# 11. CAT HAI BANG LUA CHON A-F
# =====================================================

def crop_choice_groups(doc):

    files = {}
    manifest = {}

    for name, (
        page_no, first, last, labels
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

        if max(positions) - min(positions) > 16:

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
            ) + 14,
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
            ],
        }

    return files, manifest


# =====================================================
# 12. TAO HTML XEM TRUOC
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

        # Hai bang A-F hien thi mot lan.
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
<meta name="viewport"
      content="width=device-width,initial-scale=1">
<title>HSK4 Đề 7 - Kiểm tra 100 câu</title>

<style>
* { box-sizing:border-box; }

body {
    margin:0;
    padding:20px;
    background:#f2f5fa;
    color:#17314e;
    font:16px Arial,sans-serif;
}

main {
    max-width:960px;
    margin:auto;
}

section {
    background:#fff;
    border:1px solid #dbe3ef;
    border-radius:12px;
    padding:20px;
    margin:16px 0;
}

section.shared {
    background:#f7faff;
}

img {
    max-width:100%;
    height:auto;
    display:block;
    margin:0 auto;
}

h2 { margin-top:36px; }
h3 { margin:0 0 14px; }
small { color:#52677f; }
</style>
</head>

<body>
<main>

<h1>HSK4 - Đề 7 (H41327)</h1>

<p><small>
Ảnh lấy từ PDF gốc.
Không hiển thị đáp án.
Chưa nhập SQL Server.
</small></p>

__SECTIONS__

</main>
</body>
</html>"""

    return html.replace(
        "__SECTIONS__",
        "\n".join(sections)
    ).encode("utf-8")


# =====================================================
# 13. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 07 - BUOC 2")
    print("MA DE GOC: H41327")
    print("=" * 60)

    require_file(PDF_FILE)
    require_file(ANSWER_PDF)

    source = json.loads(
        require_file(SOURCE_JSON).read_text(
            encoding="utf-8-sig"
        )
    )

    # ================================================
    # 14. KIEM TRA JSON BUOC 1
    # ================================================

    identity = (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc"),
    )

    if identity != (4, DE_NUMBER, CODE):

        raise RuntimeError(
            "JSON buoc 1 khong phai De 7 / H41327"
        )

    if (
        source.get("tong_cau") != 100
        or set(source.get("dap_an", {}))
        != {
            str(n)
            for n in range(1, 101)
        }
    ):

        raise RuntimeError(
            "JSON buoc 1 chua du 100 dap an"
        )

    if (
        Path(source.get("file_pdf", "")).resolve()
        != PDF_FILE.resolve()
    ):

        raise RuntimeError(
            "Duong dan PDF khac JSON buoc 1"
        )

    if (
        Path(
            source.get("file_dap_an_pdf", "")
        ).resolve()
        != ANSWER_PDF.resolve()
    ):

        raise RuntimeError(
            "PDF dap an khong khop JSON buoc 1"
        )

    if (
        source.get("so_trang_pdf") != 16
        or source.get("nguon_dap_an") != "pdf_rieng"
        or source.get("trang_loi_thoai") != []
        or source.get("trang_dap_an") != [1, 2]
    ):

        raise RuntimeError(
            "JSON buoc 1 sai cau truc PDF 16+2 trang"
        )

    # ================================================
    # 15. KIEM TRA CHAM VIET TU DONG
    # ================================================

    if (
        source.get("cau_can_cham_thu_cong") != []
        or source.get("che_do_cham_viet_mo")
        != "cham_tu_dong_theo_mau"
    ):

        raise RuntimeError(
            "De 7 phai cham Viet theo tranh tu dong"
        )

    if source.get("tu_cho_san_viet_mo") != {
        str(n): word
        for n, word in WORDS.items()
    }:

        raise RuntimeError(
            "Tu cho san 96-100 khong khop PDF"
        )

    if set(
        source.get(
            "dap_an_tham_khao_viet_mo", {}
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
            "De 7 khong co dap an thay the"
        )

    # ================================================
    # 16. KIEM TRA PDF DAP AN RIENG
    # ================================================

    with fitz.open(ANSWER_PDF) as key_doc:

        if (
            len(key_doc) != 2
            or CODE not in key_doc[0].get_text("text")
            or "卷答案" not in key_doc[0].get_text("text")
        ):

            raise RuntimeError(
                "PDF dap an khong phai H41327 / 2 trang"
            )

    # ================================================
    # 17. TACH 100 ANH CAU HOI
    # ================================================

    outputs = {}
    descriptions = {}

    with fitz.open(PDF_FILE) as doc:

        if (
            len(doc) != 16
            or CODE not in doc[0].get_text("text")
            or CODE not in doc[15].get_text("text")
        ):

            raise RuntimeError(
                "PDF de thi khong phai H41327 "
                "hoac sai 16 trang"
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
                f"Trang {page_no}: {len(items)} cau"
            )

        group_files, group_manifest = (
            crop_choice_groups(doc)
        )

        outputs.update(group_files)

    # ================================================
    # 18. KIEM TRA SO LUONG
    # ================================================

    if set(descriptions) != {
        str(n) for n in range(1, 101)
    }:

        raise RuntimeError(
            "Khong du 100 anh cau hoi"
        )

    if len(outputs) != 102:

        raise RuntimeError(
            f"Can 102 anh, hien co {len(outputs)}"
        )

    # ================================================
    # 19. TAO MANIFEST JSON
    # ================================================

    manifest = {

        "cap_hsk": 4,

        "so_de": DE_NUMBER,

        "ma_de_goc": CODE,

        "so_trang_pdf": 16,

        "so_cau": 100,

        "so_cau_nghe": 45,
        "so_cau_doc": 40,
        "so_cau_viet": 15,

        "trang_cau_hoi": list(
            range(2, 17)
        ),

        "trang_loi_thoai": [],

        "trang_dap_an": [1, 2],

        "nguon_dap_an": "pdf_rieng",

        "file_dap_an_pdf": str(ANSWER_PDF),

        "cau_hoi": {
            str(n): descriptions[str(n)]
            for n in range(1, 101)
        },

        "bang_lua_chon": group_manifest,

        "dap_an_thay_the": {},

        "cau_can_cham_thu_cong": [],

        "che_do_cham_viet_mo": (
            "cham_tu_dong_theo_mau"
        ),
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
    # 20. KHONG GHI DE FILE KHAC NOI DUNG
    # ================================================

    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):

            raise RuntimeError(
                "File da ton tai voi noi dung khac.\n"
                "KHONG ghi de:\n"
                + str(path)
            )

    # ================================================
    # 21. LUU ANH, MANIFEST VA HTML
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
    print("HOAN THANH HSK4 DE 07 - BUOC 2")
    print("=" * 60)

    print("Anh cau hoi: 100/100")
    print("Bang lua chon A-F: 2/2")

    print(
        "Doc chung: 80-81, 82-83, 84-85"
    )

    print(
        "Viet tranh 96-100: "
        "5/5 anh co tu cho san"
    )

    print(
        "Che do cham: TU DONG THEO MAU"
    )

    print(f"Manifest: {MANIFEST_JSON}")
    print(f"HTML: {HTML_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
