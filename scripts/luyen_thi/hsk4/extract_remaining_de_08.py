
# -*- coding: utf-8 -*-
"""
MOC HAN - HSK4 DE 08 (H41328) - BUOC 2

Dung thuat toan tach anh da kiem thu o De 5 va De 7.

- H41008.pdf: 16 trang cau hoi.
- H41008_dap_an.pdf: 18 trang, dap an o trang 17-18.
- 100 anh cau hoi, 2 bang A-F, 3 cum Doc chung.
- 5 tranh Viet 96-100 co tu goi y.
- Tao manifest JSON va HTML xem truoc, khong hien dap an.

KHONG ket noi SQL.
KHONG sua cac de truoc.
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

SOURCE = BASE / "source" / "De_HSK" / "HSK4"
DATA = BASE / "hsk4" / "data" / "de_08"
OUTPUT = BASE / "hsk4" / "output" / "de_08"

PDF_FILE = SOURCE / "H41008.pdf"
ANSWER_PDF = SOURCE / "H41008_dap_an.pdf"

SOURCE_JSON = DATA / "de_08_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_100_cau_ung_vien.json"
)

HTML_FILE = OUTPUT / "kiem_tra_100_cau.html"

CODE = "H41328"
DE_NUMBER = 8
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
    96: "袜子",
    97: "加班",
    98: "估计",
    99: "脏",
    100: "看法",
}

ANCHOR_RE = re.compile(
    r"^\s*(\d{1,3})"
    r"(?:\s*[-–—－~～]\s*(\d{1,3}))?"
    r"\s*[.．、]"
)


# =====================================================
# 3. HAM HO TRO
# =====================================================

def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def require_file(path):
    require(
        path.is_file()
        and path.stat().st_size > 0,
        f"Thieu file hoac file rong: {path}"
    )

    return path


def read_json(path):
    return json.loads(
        require_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


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
# 4. TIM SO CAU TRONG PDF
# =====================================================

def find_anchors(page, numbers, page_no):
    wanted = set(numbers)
    found = []

    # Trang 16: 5 tranh Viet hai cot.
    if page_no == 16:
        words = page.get_text("words")

        for number in sorted(wanted):
            matches = [
                fitz.Rect(word[:4])
                for word in words
                if re.fullmatch(
                    rf"{number}\s*[.．、]",
                    word[4]
                )
                and 60 < word[0] < page.rect.width - 25
                and (
                    page.rect.height * 0.35
                    < word[1]
                    < page.rect.height - 60
                )
            ]

            require(
                len(matches) == 1,
                f"Trang 16: cau {number} "
                f"tim duoc {len(matches)} moc"
            )

            found.append({
                "first": number,
                "last": number,
                "rect": matches[0]
            })

        return sorted(
            found,
            key=lambda item: (
                round(item["rect"].y0 / 15),
                item["rect"].x0
            )
        )

    # Trang 2-15.
    for value, rect in line_items(page):
        match = ANCHOR_RE.match(value)

        if not match:
            continue

        first = int(match.group(1))
        last = int(
            match.group(2) or first
        )

        if not set(
            range(first, last + 1)
        ).issubset(wanted):
            continue

        if not (40 < rect.x0 < 155):
            continue

        if not (
            45 < rect.y0 < page.rect.height - 45
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

    require(
        sorted(actual) == sorted(wanted),
        f"Trang {page_no} sai moc so cau.\n"
        f"Can: {sorted(wanted)}\n"
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
            and rect.y0 > page.rect.height * 0.72
        ):
            limit = min(
                limit,
                rect.y0 - 8
            )

    bottoms = [
        rect.y1
        for value, rect in line_items(page)
        if (
            anchor.y0 - 1 <= rect.y0 < limit
            and not value.startswith(CODE)
        )
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
    require(
        not rect.is_empty
        and page.rect.contains(rect)
        and rect.height >= 18,
        f"Khung cat khong hop le: {rect}"
    )

    pix = page.get_pixmap(
        matrix=fitz.Matrix(ZOOM, ZOOM),
        clip=rect,
        alpha=False
    )

    return pix.tobytes("png")


# =====================================================
# 7. KIEM TRA LUA CHON
# =====================================================

def check_choice_letters(
    page, rect, letters, number
):
    value = page.get_text(
        "text",
        clip=rect
    )

    present = set(
        re.findall(
            r"(?<![A-Za-z])[A-F](?![A-Za-z])",
            value
        )
    )

    require(
        set(letters).issubset(present),
        f"Cau/bang {number} thieu lua chon. "
        f"Can {letters}, thay {sorted(present)}"
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

    images = {}
    items = {}

    for index, item in enumerate(anchors):
        first = item["first"]
        last = item["last"]

        top = max(
            0,
            item["rect"].y0 - 11
        )

        if index + 1 < len(anchors):
            bottom = (
                anchors[index + 1]["rect"].y0 - 9
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

        require(
            re.search(pattern, value),
            f"Trang {page_no}: cau {first}-{last} "
            "bi cat mat so cau"
        )

        # Kiem tra cac lua chon ABC / ABCD.
        if (
            11 <= first <= 45
            or 56 <= first <= 85
        ):
            letters = (
                "ABC"
                if 56 <= first <= 65
                else "ABCD"
            )

            check_choice_letters(
                page,
                rect,
                letters,
                first
            )

        image = png_bytes(page, rect)

        # Giu nguyen doan Doc chung.
        for number in range(
            first,
            last + 1
        ):
            relative = (
                f"questions/cau_{number:03d}.png"
            )

            images[OUTPUT / relative] = image

            if 46 <= number <= 50:
                group = "doc_46_50"
            elif 51 <= number <= 55:
                group = "doc_51_55"
            else:
                group = None

            items[str(number)] = {
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

    return images, items


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
                abs(rect.x0 - old.x0) < 0.5
                and abs(rect.y0 - old.y0) < 0.5
                for old in result
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

    require(
        len(pictures) >= 6,
        "Trang 16 thieu anh vi du "
        "hoac 5 tranh Viet"
    )

    images = {}
    items = {}
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

        require(
            (anchor.x0 < half) == left,
            f"Cau {number} sai cot"
        )

        candidates = [
            rect
            for rect in pictures
            if (
                (
                    (rect.x0 + rect.x1) / 2 < half
                ) == left
            )
            and abs(
                rect.y1 - anchor.y0
            ) < 85
        ]

        candidates.sort(
            key=lambda rect: (
                abs(rect.y1 - anchor.y0),
                abs(rect.y0 - anchor.y0)
            )
        )

        require(
            candidates,
            f"Cau {number} khong tim thay tranh"
        )

        picture = candidates[0]

        picture_id = tuple(
            round(x, 1)
            for x in picture
        )

        require(
            picture_id not in used,
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
            ) + 17
        )

        value = page.get_text(
            "text",
            clip=rect
        )

        require(
            re.search(
                rf"(?<!\d){number}\s*[.．、]",
                value
            ),
            f"Cau {number} bi cat mat so cau"
        )

        require(
            WORDS[number] in value,
            f"Cau {number} mat tu "
            f"{WORDS[number]}"
        )

        require(
            rect.contains(picture),
            f"Cau {number} bi cat mat tranh"
        )

        relative = (
            f"questions/cau_{number:03d}.png"
        )

        images[OUTPUT / relative] = png_bytes(
            page,
            rect
        )

        items[str(number)] = {
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

    return images, items


# =====================================================
# 11. CAT HAI BANG A-F
# =====================================================

def crop_choice_groups(doc):
    images = {}
    items = {}

    for name, (
        page_no, first, last, labels
    ) in GROUPS.items():

        page = doc[page_no - 1]

        examples = [
            rect.y0
            for value, rect in line_items(page)
            if "例如" in value
        ]

        require(
            len(examples) == 1,
            f"Trang {page_no}: "
            "khong xac dinh duoc vi du"
        )

        selected = {}
        words = page.get_text("words")

        for letter in labels:
            matches = [
                word
                for word in words
                if (
                    word[4] == letter
                    and 100 < word[1]
                    < examples[0] - 15
                )
            ]

            require(
                len(matches) == 1,
                f"Bang {name}, nhan {letter}: "
                f"tim {len(matches)} vi tri"
            )

            selected[letter] = fitz.Rect(
                matches[0][:4]
            )

        positions = [
            rect.y0
            for rect in selected.values()
        ]

        require(
            max(positions) - min(positions) <= 16,
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

        require(
            (
                "例如" not in value
                and re.search(
                    r"[\u3400-\u9fff]",
                    value
                )
            ),
            f"Bang {name} bi cat nham"
        )

        check_choice_letters(
            page,
            rect,
            labels,
            name
        )

        relative = f"groups/{name}.png"

        images[OUTPUT / relative] = png_bytes(
            page,
            rect
        )

        items[name] = {
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

    return images, items


# =====================================================
# 12. TAO HTML XEM TRUOC
# =====================================================

def build_html(items):
    content = []
    displayed_shared = set()

    for number in range(1, 101):

        if number == 1:
            content.append(
                "<h2>I. Nghe - Câu 1–45</h2>"
            )

        elif number == 46:
            content.append(
                "<h2>II. Đọc - Câu 46–85</h2>"
            )

        elif number == 86:
            content.append(
                "<h2>III. Viết - Câu 86–100</h2>"
            )

        # Hien hai bang A-F mot lan.
        if number in (46, 51):
            name = (
                "doc_46_50"
                if number == 46
                else "doc_51_55"
            )

            content.append(
                '<section class="shared">'
                f'<h3>Bảng A-F câu '
                f'{number}–{number + 4}</h3>'
                f'<img src="groups/{name}.png" '
                'alt="Bảng A-F">'
                '</section>'
            )

        item = items[str(number)]
        shared = item.get("nhom_doc_chung")

        if shared and shared in displayed_shared:
            continue

        if shared:
            displayed_shared.add(shared)

        label = (
            "Câu " + shared.replace("-", "–")
            if shared
            else f"Câu {number}"
        )

        src = escape(
            item["anh"],
            quote=True
        )

        content.append(
            f'<section><h3>{label}</h3>'
            f'<img src="{src}" '
            f'alt="{label}"></section>'
        )

    html = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>HSK4 - Đề 8 (H41328)</title>

<style>
* {
    box-sizing: border-box;
}

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
    background: white;
    border: 1px solid #dbe3ef;
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
}

.shared {
    background: #f7faff;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: auto;
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

<h1>HSK4 – Đề 8 (H41328)</h1>

<p>
<small>
Ảnh lấy từ PDF gốc.
Không hiển thị đáp án.
Chưa nhập SQL.
</small>
</p>

__SECTIONS__

</main>
</body>
</html>"""

    return html.replace(
        "__SECTIONS__",
        "\n".join(content)
    ).encode("utf-8")


# =====================================================
# 13. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 08 - BUOC 2")
    print("TACH ANH H41328")
    print("=" * 60)

    require_file(PDF_FILE)
    require_file(ANSWER_PDF)

    source = read_json(SOURCE_JSON)

    # ================================================
    # 14. KIEM TRA JSON BUOC 1
    # ================================================

    identity = (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc")
    )

    require(
        identity == (4, DE_NUMBER, CODE),
        "JSON buoc 1 khong phai "
        "HSK4 De 8 / H41328"
    )

    counts = (
        source.get("tong_cau"),
        source.get("so_cau_nghe"),
        source.get("so_cau_doc"),
        source.get("so_cau_viet")
    )

    require(
        counts == (100, 45, 40, 15),
        "JSON buoc 1 sai so cau"
    )

    require(
        set(
            source.get("dap_an") or {}
        ) == {
            str(n)
            for n in range(1, 101)
        },
        "Buoc 1 chua du 100 dap an"
    )

    require(
        Path(
            source.get("file_pdf") or ""
        ).resolve() == PDF_FILE.resolve()

        and Path(
            source.get("file_dap_an_pdf") or ""
        ).resolve() == ANSWER_PDF.resolve(),

        "Duong dan PDF khac JSON buoc 1"
    )

    # ================================================
    # 15. KIEM TRA CAU TRUC PDF
    # ================================================

    require(
        source.get("so_trang_pdf") == 16
        and source.get("nguon_dap_an") == "pdf_rieng"
        and source.get("trang_loi_thoai") == []
        and source.get("trang_dap_an") == [17, 18],

        "Buoc 1 sai cau truc PDF "
        "16 trang de + 18 trang PDF dap an"
    )

    require(
        source.get("cau_can_cham_thu_cong") == []
        and source.get("che_do_cham_viet_mo")
        == "cham_tu_dong_theo_mau",

        "Buoc 1 chua bat cham Viet tu dong"
    )

    require(
        source.get("dap_an_thay_the") == {},
        "De 8 khong co dap an thay the trong PDF"
    )

    require(
        source.get("tu_cho_san_viet_mo")
        == {
            str(n): WORDS[n]
            for n in range(96, 101)
        },

        "Sai 5 tu goi y Viet tranh"
    )

    require(
        set(
            source.get(
                "dap_an_tham_khao_viet_mo"
            ) or {}
        ) == {
            str(n)
            for n in range(96, 101)
        },

        "Thieu 5 cau mau Viet theo tranh"
    )

    # ================================================
    # 16. KIEM TRA PDF DAP AN
    # ================================================

    with fitz.open(ANSWER_PDF) as answer_doc:

        require(
            len(answer_doc) == 18
            and CODE in answer_doc[0].get_text("text")
            and CODE in answer_doc[16].get_text("text")
            and "卷答案" in answer_doc[16].get_text("text"),

            "PDF dap an phai co 18 trang, "
            "dap an o trang 17-18"
        )

    # ================================================
    # 17. CAT 100 ANH
    # ================================================

    outputs = {}
    items = {}

    with fitz.open(PDF_FILE) as doc:

        require(
            len(doc) == 16
            and CODE in doc[0].get_text("text")
            and CODE in doc[15].get_text("text"),

            "PDF de thi khong phai "
            "H41328 / 16 trang"
        )

        for page_no, numbers in PAGE_MAP.items():

            if page_no == 16:

                images, descriptions = (
                    crop_pictures(doc[15])
                )

            else:

                images, descriptions = (
                    crop_normal_page(
                        doc[page_no - 1],
                        page_no,
                        numbers
                    )
                )

            outputs.update(images)
            items.update(descriptions)

            print(
                f"Trang {page_no}: "
                f"{len(descriptions)} cau"
            )

        group_images, group_manifest = (
            crop_choice_groups(doc)
        )

        outputs.update(group_images)

    # ================================================
    # 18. KIEM TRA SO LUONG
    # ================================================

    require(
        set(items) == {
            str(n)
            for n in range(1, 101)
        },
        "Khong du 100 cau hoi"
    )

    require(
        len(outputs) == 102,
        f"Can 102 anh, tim thay {len(outputs)}"
    )

    # ================================================
    # 19. TAO MANIFEST
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

        "trang_cau_hoi": list(range(2, 17)),

        "trang_loi_thoai": [],

        "trang_dap_an": [17, 18],

        "nguon_dap_an": "pdf_rieng",

        "file_dap_an_pdf": str(ANSWER_PDF),

        "cau_hoi": {
            str(n): items[str(n)]
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

    outputs[HTML_FILE] = build_html(items)

    # ================================================
    # 20. KHONG GHI DE FILE KHAC NOI DUNG
    # ================================================

    for path, content in outputs.items():

        require(
            not path.exists()
            or path.read_bytes() == content,

            "File da ton tai voi noi dung khac.\n"
            "KHONG ghi de: "
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
    print("HOAN THANH HSK4 DE 08 - BUOC 2")
    print("=" * 60)

    print("Anh cau hoi: 100/100")
    print("Bang A-F: 2/2")

    print(
        "Doan Doc chung: "
        "80-81, 82-83, 84-85"
    )

    print(
        "Viet tranh: 96-100, du tu goi y"
    )

    print(
        "Cham Viet theo tranh: TU DONG"
    )

    print(f"Manifest: {MANIFEST_JSON}")
    print(f"HTML: {HTML_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
