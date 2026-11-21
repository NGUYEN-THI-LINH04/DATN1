
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK4 DE 03 (H41003)
BUOC 2 - TACH 100 ANH CAU HOI

Ke thua cau truc De 1 va De 2.

- Tach 100 anh cau hoi.
- Tach 2 bang lua chon Doc 46-55.
- Giu doan chung 80-81, 82-83, 84-85.
- Tach 5 tranh Viet theo hai cot.
- Tao manifest JSON va HTML xem truoc.
- Khong hien dap an trong HTML.

KHONG thay doi SQL Server.
KHONG sua cac de HSK da hoan thanh.
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

PDF = (
    BASE / "source" / "De_HSK"
    / "HSK4" / "H41003.pdf"
)

DATA = BASE / "hsk4" / "data" / "de_03"

OUT = BASE / "hsk4" / "output" / "de_03"

ANSWER_JSON = DATA / "de_03_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_100_cau_ung_vien.json"
)

PREVIEW_HTML = OUT / "kiem_tra_100_cau.html"

CODE = "H41003"

ZOOM = 2.4


# =====================================================
# 2. TU CHO SAN CAU 96-100
# =====================================================

WORDS = {
    96: "收拾",
    97: "理发",
    98: "困",
    99: "激动",
    100: "讨论",
}


# =====================================================
# 3. PHAN BO CAU HOI THEO TRANG
# =====================================================

PAGES = {
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
# 4. BANG LUA CHON CHUNG
# =====================================================

GROUPS = {
    "doc_46_50": (7, 46, 50, "ABCDEF"),
    "doc_51_55": (8, 51, 55, "ABCDEF"),
}


ANCHOR = re.compile(
    r"^\s*(\d{1,3})"
    r"(?:\s*[-–—－~～]\s*(\d{1,3}))?"
    r"\s*[.．、]"
)


# =====================================================
# 5. HAM KIEM TRA
# =====================================================

def require(condition, message):

    if not condition:
        raise RuntimeError(message)


def read_file(path):

    require(
        path.is_file()
        and path.stat().st_size > 0,
        f"Thieu file: {path}"
    )

    return path


# =====================================================
# 6. DOC CAC DONG VAN BAN PDF
# =====================================================

def lines(page):

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
# 7. TIM VI TRI SO CAU
# =====================================================

def anchors_for(page, page_no, numbers):

    expected = set(numbers)
    result = []

    # Trang 16 co hai cot.
    if page_no == 16:

        words = page.get_text("words")

        for number in sorted(expected):

            hits = [
                fitz.Rect(word[:4])
                for word in words

                if re.fullmatch(
                    rf"{number}\s*[.．、]",
                    word[4]
                )

                and 60 < word[0] < page.rect.width - 25
                and 300 < word[1] < page.rect.height - 60
            ]

            require(
                len(hits) == 1,
                f"Trang 16, cau {number}: "
                f"tim duoc {len(hits)} vi tri."
            )

            result.append((
                number,
                number,
                hits[0]
            ))

    # Trang 2-15: mot cot.
    else:

        for text, rect in lines(page):

            match = ANCHOR.match(text)

            if not match:
                continue

            if not (
                40 < rect.x0 < 155
                and 45 < rect.y0 < page.rect.height - 45
            ):
                continue

            first = int(match.group(1))
            last = int(match.group(2) or first)

            if set(
                range(first, last + 1)
            ).issubset(expected):

                result.append((
                    first,
                    last,
                    rect
                ))

    result.sort(
        key=lambda item: (
            item[2].y0,
            item[2].x0
        )
    )

    found = [
        number

        for first, last, _ in result

        for number in range(first, last + 1)
    ]

    require(
        sorted(found) == sorted(expected),

        f"Trang {page_no}: "
        f"can {sorted(expected)}, "
        f"tim thay {found}"
    )

    return result


# =====================================================
# 8. XAC DINH CUOI NOI DUNG TRANG
# =====================================================

def bottom_content(page, last_anchor):

    limit = page.rect.height - 52

    for text, rect in lines(page):

        if (
            re.search(
                r"H41003\s*[-－–]\s*\d+",
                text
            )

            and rect.y0 > page.rect.height * 0.70
        ):

            limit = min(
                limit,
                rect.y0 - 8
            )

    ends = [
        rect.y1

        for text, rect in lines(page)

        if (
            last_anchor.y0 - 1
            <= rect.y0 < limit
        )

        and not text.startswith("H41003")
    ]

    return min(
        limit,
        max(
            ends,
            default=last_anchor.y1
        ) + 12
    )


# =====================================================
# 9. XUAT ANH PNG
# =====================================================

def png(page, rect):

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
# 10. KIEM TRA CAC NHAN LUA CHON
# =====================================================

def letters_present(page, rect, expected):

    text = page.get_text(
        "text",
        clip=rect
    )

    found = re.findall(
        r"(?<![A-Za-z])[A-F](?![A-Za-z])",
        text
    )

    return set(found) & set(expected)


# =====================================================
# 11. CAT CAC CAU TRANG 2-15
# =====================================================

def crop_normal(page, page_no, numbers):

    found = anchors_for(
        page,
        page_no,
        numbers
    )

    files = {}
    items = {}

    for index, (
        first,
        last,
        anchor
    ) in enumerate(found):

        top = max(
            0,
            anchor.y0 - 10
        )

        if index + 1 < len(found):

            bottom = (
                found[index + 1][2].y0 - 7
            )

        else:

            bottom = bottom_content(
                page,
                anchor
            )

        rect = fitz.Rect(
            70,
            top,
            page.rect.width - 48,
            bottom
        )

        content = page.get_text(
            "text",
            clip=rect
        )

        pattern = (
            rf"(?<!\d){first}"
            rf"\s*(?:[-–—－]\s*{last})?"
            r"\s*[.．、]"
        )

        require(
            re.search(pattern, content),

            f"Trang {page_no}: "
            f"cau {first}-{last} mat so cau."
        )

        # Nghe, Doc trac nghiem va sap xep ABC.
        if (
            11 <= first <= 45
            or 56 <= first <= 85
        ):

            needed = (
                "ABC"
                if 56 <= first <= 65
                else "ABCD"
            )

            actual = letters_present(
                page,
                rect,
                needed
            )

            require(
                actual == set(needed),

                f"Cau {first}: "
                f"thieu lua chon "
                f"{set(needed) - actual}"
            )

        image_data = png(page, rect)

        # 80-81, 82-83, 84-85:
        # Moi cau co anh rieng nhung
        # giu nguyen doan van chung.
        for number in range(
            first,
            last + 1
        ):

            relative = (
                f"questions/cau_{number:03d}.png"
            )

            files[OUT / relative] = image_data

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
                    if last > first
                    else None
                ),

                "toa_do": [
                    round(value, 2)
                    for value in rect
                ]
            }

    return files, items


# =====================================================
# 12. LAY TOA DO ANH NHUNG
# =====================================================

def embedded_images(page):

    result = []

    for info in page.get_images(full=True):

        for rect in page.get_image_rects(
            info[0]
        ):

            if (
                rect.width <= 35
                or rect.height <= 35
            ):
                continue

            duplicated = any(
                abs(rect.x0 - old.x0) < 0.5
                and abs(rect.y0 - old.y0) < 0.5

                for old in result
            )

            if not duplicated:
                result.append(rect)

    return result


# =====================================================
# 13. CAT TRANH CAU 96-100
# =====================================================

def crop_pictures(page):

    found = anchors_for(
        page,
        16,
        range(96, 101)
    )

    anchors = {
        first: rect
        for first, last, rect in found
    }

    pictures = embedded_images(page)

    require(
        len(pictures) >= 6,

        "Trang 16 phai co 1 anh vi du "
        "va 5 anh cau hoi."
    )

    half = page.rect.width / 2

    files = {}
    items = {}
    used = set()

    for number, hint in WORDS.items():

        anchor = anchors[number]

        # 96 | 97
        # 98 | 99
        # 100
        left = number in (96, 98, 100)

        require(
            (anchor.x0 < half) == left,
            f"Cau {number} nam sai cot."
        )

        candidates = [
            rect
            for rect in pictures

            if (
                ((rect.x0 + rect.x1) / 2 < half)
                == left
            )

            and abs(
                rect.y1 - anchor.y0
            ) < 85
        ]

        candidates.sort(
            key=lambda rect: abs(
                rect.y1 - anchor.y0
            )
        )

        require(
            candidates,

            f"Cau {number}: "
            "khong tim thay anh minh hoa."
        )

        picture = candidates[0]

        identity = tuple(
            round(value, 1)
            for value in picture
        )

        require(
            identity not in used,

            f"Cau {number}: anh trung "
            "voi cau truoc."
        )

        used.add(identity)

        # Cat du anh, so cau va tu goi y.
        rect = fitz.Rect(
            70 if left else half - 3,

            max(
                0,
                min(
                    picture.y0,
                    anchor.y0
                ) - 15
            ),

            (
                half + 7
                if left
                else page.rect.width - 35
            ),

            min(
                page.rect.height,
                max(
                    picture.y1,
                    anchor.y1
                ) + 17
            )
        )

        content = page.get_text(
            "text",
            clip=rect
        )

        require(
            re.search(
                rf"(?<!\d){number}\s*[.．、]",
                content
            ),

            f"Cau {number}: mat so cau."
        )

        require(
            hint in content,

            f"Cau {number}: "
            f"mat tu goi y '{hint}'."
        )

        require(
            rect.contains(picture),

            f"Cau {number}: "
            "cat mat anh minh hoa."
        )

        relative = (
            f"questions/cau_{number:03d}.png"
        )

        files[OUT / relative] = png(
            page,
            rect
        )

        items[str(number)] = {
            "trang_pdf": 16,
            "anh": relative,

            "nhom_lua_chon": None,
            "nhom_doc_chung": None,

            "tu_cho_san": hint,

            "toa_do": [
                round(value, 2)
                for value in rect
            ]
        }

    require(
        len(used) == 5,
        "Khong du 5 tranh khac nhau."
    )

    return files, items


# =====================================================
# 14. CAT BANG LUA CHON CHUNG 46-55
# =====================================================

def crop_choice_groups(doc):

    files = {}
    groups = {}

    for name, (
        page_no,
        start,
        end,
        alphabet
    ) in GROUPS.items():

        page = doc[page_no - 1]

        examples = [
            rect.y0

            for text, rect in lines(page)

            if "例如" in text
        ]

        require(
            len(examples) == 1,

            f"Trang {page_no}: "
            "khong xac dinh dong vi du."
        )

        selections = {}

        for letter in alphabet:

            hits = [
                fitz.Rect(word[:4])

                for word in page.get_text("words")

                if (
                    word[4] == letter
                    and 100 < word[1]
                    < examples[0] - 15
                )
            ]

            require(
                len(hits) == 1,

                f"Bang {name}, nhan {letter}: "
                f"{len(hits)} vi tri."
            )

            selections[letter] = hits[0]

        positions = [
            rect.y0
            for rect in selections.values()
        ]

        require(
            max(positions) - min(positions) <= 16,

            f"Bang {name}: "
            "A-F khong cung hang."
        )

        rect = fitz.Rect(
            70,

            min(positions) - 13,

            page.rect.width - 42,

            max(
                item.y1
                for item in selections.values()
            ) + 15
        )

        content = page.get_text(
            "text",
            clip=rect
        )

        require(
            "例如" not in content
            and re.search(
                r"[\u3400-\u9fff]",
                content
            ),

            f"Bang {name} bi cat nham."
        )

        require(
            letters_present(
                page,
                rect,
                alphabet
            ) == set(alphabet),

            f"Bang {name}: thieu nhan A-F."
        )

        relative = f"groups/{name}.png"

        files[OUT / relative] = png(
            page,
            rect
        )

        groups[name] = {
            "trang_pdf": page_no,
            "cau_tu": start,
            "cau_den": end,

            "lua_chon": alphabet,

            "anh": relative,

            "toa_do": [
                round(value, 2)
                for value in rect
            ]
        }

    return files, groups


# =====================================================
# 15. TAO HTML KIEM TRA 100 CAU
# =====================================================

def build_html(items):

    blocks = []
    displayed = set()

    for number in range(1, 101):

        if number == 1:
            blocks.append(
                "<h2>I. Nghe · Câu 1–45</h2>"
            )

        if number == 46:
            blocks.append(
                "<h2>II. Đọc · Câu 46–85</h2>"
            )

        if number == 86:
            blocks.append(
                "<h2>III. Viết · Câu 86–100</h2>"
            )

        # Hai bang A-F chi hien mot lan.
        if number in (46, 51):

            group = (
                "doc_46_50"
                if number == 46
                else "doc_51_55"
            )

            blocks.append(
                '<section class="group">'
                f'<h3>Bảng lựa chọn câu '
                f'{number}–{number + 4}</h3>'
                f'<img src="groups/{group}.png" '
                'alt="Bảng lựa chọn chung A–F">'
                '</section>'
            )

        item = items[str(number)]

        shared = item.get(
            "nhom_doc_chung"
        )

        # Khong lap lai doan doc chung.
        if shared and shared in displayed:
            continue

        if shared:
            displayed.add(shared)

        if shared:
            label = (
                "Câu "
                + shared.replace("-", "–")
            )
        else:
            label = f"Câu {number}"

        path = escape(
            item["anh"],
            quote=True
        )

        blocks.append(
            "<section>"
            f"<h3>{label}</h3>"
            f'<img src="{path}" '
            f'alt="{escape(label)}">'
            "</section>"
        )

    html = """
<!doctype html>
<html lang="vi">

<head>
<meta charset="utf-8">
<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>HSK4 Đề 3 - Kiểm tra ảnh</title>

<style>
* {
    box-sizing: border-box;
}

body {
    font: 16px Arial, sans-serif;
    background: #f2f5fa;
    color: #20344e;
    margin: 0;
    padding: 18px;
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

section.group {
    background: #f7faff;
}

img {
    display: block;
    max-width: 100%;
    height: auto;
    margin: auto;
}

h3 {
    margin: 0 0 14px;
}

h2 {
    margin-top: 36px;
}

small {
    color: #607187;
}
</style>

</head>

<body>
<main>

<h1>HSK4 – Đề 3 (H41003)</h1>

<p>
<small>
Ảnh từ PDF gốc.
Không hiển thị đáp án.
Chưa nhập SQL Server.
</small>
</p>

__QUESTIONS__

</main>
</body>
</html>
"""

    html = html.replace(
        "__QUESTIONS__",
        "\n".join(blocks)
    )

    return html.encode("utf-8")


# =====================================================
# 16. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 03 - BUOC 2")
    print("=" * 60)

    read_file(PDF)

    source = json.loads(
        read_file(
            ANSWER_JSON
        ).read_text(
            encoding="utf-8-sig"
        )
    )

    # ================================================
    # 17. KIEM TRA JSON BUOC 1
    # ================================================

    identity = (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc")
    )

    require(
        identity == (4, 3, CODE),

        "JSON buoc 1 khong phai H41003."
    )

    require(
        source.get("tong_cau") == 100

        and set(
            source.get("dap_an", {})
        ) == {
            str(number)
            for number in range(1, 101)
        },

        "JSON buoc 1 thieu dap an."
    )

    require(
        Path(
            source.get("file_pdf", "")
        ).resolve() == PDF.resolve(),

        "PDF khong khop JSON buoc 1."
    )

    require(
        source.get(
            "cau_can_cham_thu_cong"
        ) == []

        and source.get(
            "che_do_cham_viet_mo"
        ) == "cham_tu_dong_theo_mau",

        "De 3 phai cham tu dong "
        "theo cau mau."
    )

    expected_words = {
        str(number): word

        for number, word in WORDS.items()
    }

    require(
        source.get(
            "tu_cho_san_viet_mo"
        ) == expected_words,

        "Sai tu cho san 96-100."
    )

    require(
        set(
            source.get(
                "dap_an_thay_the",
                {}
            )
        ) == {"93"},

        "De 3 chi co cau 93 "
        "co dap an thay the."
    )

    require(
        set(
            source.get(
                "dap_an_tham_khao_viet_mo",
                {}
            )
        ) == {
            str(number)
            for number in range(96, 101)
        },

        "Thieu dap an mau 96-100."
    )

    # ================================================
    # 18. TACH ANH PDF
    # ================================================

    files = {}
    items = {}

    with fitz.open(PDF) as doc:

        require(
            len(doc) == 24

            and CODE in doc[0].get_text(
                "text"
            ),

            "PDF khong phai "
            "H41003 24 trang."
        )

        for page_no, numbers in PAGES.items():

            if page_no == 16:

                generated, descriptions = (
                    crop_pictures(
                        doc[15]
                    )
                )

            else:

                generated, descriptions = (
                    crop_normal(
                        doc[page_no - 1],
                        page_no,
                        numbers
                    )
                )

            files.update(generated)
            items.update(descriptions)

            print(
                f"Trang {page_no}: "
                f"{len(descriptions)} cau"
            )

        group_files, group_manifest = (
            crop_choice_groups(doc)
        )

        files.update(group_files)

    # ================================================
    # 19. KIEM TRA SO LUONG
    # ================================================

    require(
        set(items) == {
            str(number)
            for number in range(1, 101)
        },

        "Khong du 100 cau."
    )

    require(
        len(files) == 102,

        f"Can 102 anh, hien co {len(files)}."
    )

    # ================================================
    # 20. TAO MANIFEST
    # ================================================

    manifest = {
        "cap_hsk": 4,
        "so_de": 3,
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
            str(number): items[str(number)]
            for number in range(1, 101)
        },

        "bang_lua_chon": group_manifest,

        "dap_an_thay_the": source.get(
            "dap_an_thay_the",
            {}
        ),

        "cau_can_cham_thu_cong": [],

        "che_do_cham_viet_mo": (
            "cham_tu_dong_theo_mau"
        )
    }

    files[MANIFEST_JSON] = json.dumps(
        manifest,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    files[PREVIEW_HTML] = build_html(
        items
    )

    # ================================================
    # 21. KIEM TRA TRUOC KHI GHI FILE
    # ================================================

    for path, content in files.items():

        require(
            not path.exists()
            or path.read_bytes() == content,

            "Khong ghi de file "
            "co noi dung khac: "
            + str(path)
        )

    # ================================================
    # 22. LUU ANH, JSON VA HTML
    # ================================================

    for path, content in files.items():

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not path.exists():
            path.write_bytes(content)

    # ================================================
    # 23. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH HSK4 DE 03 - BUOC 2"
    )

    print("=" * 60)

    print("Anh cau hoi: 100/100")
    print("Bang lua chon chung: 2/2")

    print(
        "Doan Doc chung: "
        "80-81, 82-83, 84-85"
    )

    print(
        "Viet tranh: "
        "5/5 anh co tu cho san"
    )

    print(
        "Che do cham: "
        "TU DONG THEO CAU MAU"
    )

    print(
        "HTML: khong hien dap an"
    )

    print(
        f"\nManifest: {MANIFEST_JSON}"
    )

    print(
        f"HTML: {PREVIEW_HTML}"
    )

    print(
        "\nCHUA thay doi SQL Server."
    )


if __name__ == "__main__":
    main()
