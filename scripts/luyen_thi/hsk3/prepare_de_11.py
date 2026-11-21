
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 11 (H31330) - BUOC 1

- Kiem tra PDF 16 trang.
- Doi chieu 70 dap an Nghe/Doc.
- Doi chieu 10 dap an Viet.
- Kiem tra cum tu sap xep cau 71-75.
- Tach 2 bang hinh Nghe cau 1-10.
- Tao JSON dap an va HTML xem truoc.

KHONG ket noi SQL Server.
KHONG sua 30 de thi cu.
KHONG ghi de file khac noi dung.
"""

from pathlib import Path
from itertools import permutations

import json
import os
import re
import unicodedata

import fitz


# =====================================================
# 1. CAU HINH DUONG DAN
# =====================================================

ROOT = Path(
    os.environ.get(
        "MOC_HAN_ROOT",
        r"D:\DATN1"
    )
)

BASE = ROOT / "scripts" / "luyen_thi"

SOURCE = (
    BASE / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 11"
)

DATA = BASE / "hsk3" / "data" / "de_11"

OUTPUT = BASE / "hsk3" / "output" / "de_11"

GROUP_DIR = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_11_dap_an.json"

PREVIEW_HTML = (
    OUTPUT / "kiem_tra_10_cau.html"
)

# Ma goc tren PDF.
CODE = "H31330"


# =====================================================
# 2. SO DO TRANG PDF
# =====================================================

PAGE_QUESTIONS = {
    2: range(1, 6),
    3: range(6, 11),

    4: range(11, 21),
    5: range(21, 31),
    6: range(31, 41),

    7: range(41, 46),
    8: range(46, 51),

    9: range(51, 56),
    10: range(56, 61),

    11: range(61, 65),
    12: range(65, 71),

    13: range(71, 76),
    14: range(76, 81),
}


# =====================================================
# 3. HAI BANG HINH NGHE
# =====================================================

GROUPS = {
    "nghe_01_05": {
        "trang_pdf": 2,
        "cau_tu": 1,
        "cau_den": 5,
        "lua_chon": "ABCDEF",
    },

    "nghe_06_10": {
        "trang_pdf": 3,
        "cau_tu": 6,
        "cau_den": 10,
        "lua_chon": "ABCDE",
    },
}


# =====================================================
# 4. DAP AN NGHE/DOC H31330
# =====================================================

# Doi chieu trang 15 cua PDF goc.
# 14 dong, moi dong 5 dap an.

EXPECTED_ROWS = [
    "B F A C E",
    "B D A C E",

    "√ √ × √ √",
    "× √ × × ×",

    "C A B B A",
    "C B B C B",

    "A C A A C",
    "C A C B B",

    "C A D F B",
    "C D A B E",

    "A D F C B",
    "C E F B A",

    "B C A B B",
    "C C A A A",
]


# =====================================================
# 5. DAP AN VIET H31330
# =====================================================

# Doi chieu trang 16 cua PDF goc.

EXPECTED_WRITING = {
    71: "这次旅游花了一万元。",
    72: "她丈夫在大学教中文。",
    73: "妹妹害怕得哭了起来。",
    74: "飞机马上就要起飞了。",
    75: "今晚的月亮真大啊！",

    76: "会",
    77: "更",
    78: "车",
    79: "年",
    80: "为",
}


# =====================================================
# 6. HAM HO TRO
# =====================================================

def norm(value):

    return unicodedata.normalize(
        "NFKC",
        str(value)
    )


def compact(value):

    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "",
        norm(value)
    )


def require_file(path):

    if (
        not path.is_file()
        or path.stat().st_size == 0
    ):
        raise RuntimeError(
            f"Thieu file hoac file rong:\n{path}"
        )

    return path


# =====================================================
# 7. LUU FILE AN TOAN
# =====================================================

def save_safe(path, content):

    if path.exists():

        if path.read_bytes() != content:

            raise RuntimeError(
                "Khong ghi de file "
                "da co noi dung khac:\n"
                + str(path)
            )

        return

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_bytes(content)


# =====================================================
# 8. TIM PDF VA MP3
# =====================================================

def find_sources():

    pdfs = sorted(
        SOURCE.glob("*.pdf")
    )

    mp3s = sorted(
        SOURCE.glob("*.mp3")
    )

    if (
        len(pdfs) != 1
        or len(mp3s) > 1
    ):
        raise RuntimeError(
            "Thu muc DE 11 can dung "
            "1 PDF va toi da 1 MP3.\n"
            f"PDF: {len(pdfs)}, MP3: {len(mp3s)}"
        )

    pdf_file = require_file(
        pdfs[0]
    )

    mp3_file = (
        require_file(mp3s[0])
        if mp3s else None
    )

    return pdf_file, mp3_file


# =====================================================
# 9. KIEM TRA DANG DAP AN
# =====================================================

def allowed_for(number):

    if number <= 5:
        return set("ABCDEF")

    if number <= 10:
        return set("ABCDE")

    if number <= 20:
        return {"√", "×"}

    if number <= 40:
        return set("ABC")

    if number <= 45:
        return set("ABCDEF")

    if number <= 50:
        return set("ABCDE")

    if number <= 60:
        return set("ABCDEF")

    return set("ABC")


# =====================================================
# 10. KIEM TRA BO CUC PDF
# =====================================================

def check_pdf(doc):

    if len(doc) != 16:

        raise RuntimeError(
            "PDF H31330 phai co 16 trang."
            f"\nHien co: {len(doc)}"
        )

    cover = doc[0].get_text("text")

    answer_page = doc[14].get_text("text")

    if (
        CODE not in cover
        or CODE not in answer_page
    ):
        raise RuntimeError(
            "PDF khong dung ma de H31330."
        )

    if (
        "答案" not in answer_page
        or "书" not in doc[15].get_text("text")
    ):
        raise RuntimeError(
            "Khong xac nhan duoc "
            "trang dap an 15-16."
        )

    numbers = [
        number

        for group in PAGE_QUESTIONS.values()
        for number in group
    ]

    if sorted(numbers) != list(
        range(1, 81)
    ):
        raise RuntimeError(
            "So do PDF khong du 80 cau."
        )


# =====================================================
# 11. DOC 70 DAP AN NGHE/DOC
# =====================================================

def read_objective(page):

    text = norm(
        page.get_text("text")
    )

    pattern = re.compile(
        r"(?<!\d)(\d{1,2})"
        r"\s*[.．、]\s*"
        r"([A-F√×])(?=\s|$)"
    )

    answers = {}

    for match in pattern.finditer(text):

        number = int(
            match.group(1)
        )

        answer = match.group(2)

        if not 1 <= number <= 70:
            continue

        if number in answers:

            raise RuntimeError(
                f"Trung dap an cau {number}."
            )

        if answer not in allowed_for(number):

            raise RuntimeError(
                f"Dap an cau {number} "
                f"ngoai lua chon: {answer}"
            )

        answers[number] = answer

    if set(answers) != set(
        range(1, 71)
    ):
        raise RuntimeError(
            "Khong du 70 dap an Nghe/Doc."
        )

    # ================================================
    # 12. DOI CHIEU 70 DAP AN
    # ================================================

    expected = [
        item

        for row in EXPECTED_ROWS
        for item in row.split()
    ]

    if len(expected) != 70:
        raise RuntimeError(
            "Bang doi chieu thieu dap an."
        )

    for number in range(1, 71):

        if (
            answers[number]
            != expected[number - 1]
        ):
            raise RuntimeError(
                f"Dap an cau {number} "
                "khong khop bang PDF goc."
            )

    return answers


# =====================================================
# 13. DOC 10 DAP AN VIET
# =====================================================

def read_writing(page):

    text = page.get_text("text")

    pattern = re.compile(
        r"^\s*(7[1-9]|80)"
        r"\s*[.．、]\s*([^\n]+)",
        re.MULTILINE
    )

    answers = {}

    for match in pattern.finditer(text):

        number = int(
            match.group(1)
        )

        answer = (
            match.group(2).strip()
        )

        if number in answers:

            raise RuntimeError(
                f"Trung dap an Viet {number}."
            )

        if "/" in answer:

            raise RuntimeError(
                f"Cau {number} co "
                "dap an thay the. "
                "Can xu ly rieng."
            )

        answers[number] = answer

    if set(answers) != set(
        range(71, 81)
    ):
        raise RuntimeError(
            "Khong du 10 dap an Viet."
        )

    # ================================================
    # 14. DOI CHIEU DAP AN VIET
    # ================================================

    for number in range(71, 81):

        if compact(
            answers[number]
        ) != compact(
            EXPECTED_WRITING[number]
        ):
            raise RuntimeError(
                f"Dap an Viet cau {number} "
                "khong khop PDF goc."
            )

        if number >= 76:

            if len(
                compact(answers[number])
            ) != 1:
                raise RuntimeError(
                    f"Cau {number} phai "
                    "dien mot chu Han."
                )

    return answers


# =====================================================
# 15. DOC CUM TU SAP XEP 71-75
# =====================================================

def read_writing_tokens(page, answers):

    text = page.get_text("text")

    tokens = {}

    for line in text.splitlines():

        match = re.match(
            r"^\s*(7[1-5])"
            r"\s*[.．、]\s*(.+)",
            line
        )

        if not match:
            continue

        number = int(
            match.group(1)
        )

        if number in tokens:

            raise RuntimeError(
                f"Trung cum tu cau {number}."
            )

        values = [
            value.strip()

            for value in re.split(
                r"\s{2,}",
                match.group(2)
            )

            if value.strip()
        ]

        tokens[number] = values

    if set(tokens) != set(
        range(71, 76)
    ):
        raise RuntimeError(
            "Khong du cum tu cau 71-75."
        )

    # ================================================
    # 16. KIEM TRA KHA NANG GHEP CAU
    # ================================================

    for number, values in tokens.items():

        if not 3 <= len(values) <= 8:

            raise RuntimeError(
                f"Cau {number} "
                "sai so cum tu."
            )

        valid = any(
            compact("".join(order))
            == compact(answers[number])

            for order in permutations(values)
        )

        if not valid:

            raise RuntimeError(
                f"Cau {number} khong ghep "
                "duoc dap an tu PDF de."
            )

    return tokens


# =====================================================
# 17. TACH HAI BANG HINH NGHE
# =====================================================

def render_groups(doc):

    images = {}
    group_info = {}

    for name, config in GROUPS.items():

        page = doc[
            config["trang_pdf"] - 1
        ]

        # ============================================
        # 18. LAY TOA DO HINH TU PDF GOC
        # ============================================

        image_rects = [
            rect

            for image in page.get_images(
                full=True
            )

            for rect in (
                page.get_image_rects(
                    image[0]
                )
            )
        ]

        expected_count = len(
            config["lua_chon"]
        )

        if len(image_rects) != expected_count:

            raise RuntimeError(
                f"Bang {name} co "
                f"{len(image_rects)} hinh, "
                f"can {expected_count}."
            )

        top = min(
            rect.y0 for rect in image_rects
        ) - 12

        bottom = max(
            rect.y1 for rect in image_rects
        ) + 12

        crop = fitz.Rect(
            80,
            top,
            530,
            bottom
        )

        if not page.rect.contains(crop):

            raise RuntimeError(
                f"Bang {name} "
                "nam ngoai trang PDF."
            )

        # ============================================
        # 19. KIEM TRA NHAN A-F / A-E
        # ============================================

        labels = set()

        for word in page.get_text("words"):

            value = str(
                word[4]
            ).strip()

            if (
                value in config["lua_chon"]
                and len(value) == 1
                and crop.contains(
                    fitz.Rect(word[:4])
                )
            ):
                labels.add(value)

        missing = (
            set(config["lua_chon"])
            - labels
        )

        if missing:

            raise RuntimeError(
                f"Bang {name} "
                f"thieu nhan: {sorted(missing)}"
            )

        # ============================================
        # 20. KIEM TRA KHONG CAT MAT HINH
        # ============================================

        if not all(
            crop.contains(rect)
            for rect in image_rects
        ):
            raise RuntimeError(
                f"Bang {name} bi cat mat hinh."
            )

        # ============================================
        # 21. XUAT ANH PNG
        # ============================================

        pix = page.get_pixmap(
            matrix=fitz.Matrix(2.5, 2.5),
            clip=crop,
            alpha=False
        )

        images[name] = (
            pix.tobytes("png")
        )

        group_info[name] = {
            "trang_pdf": config["trang_pdf"],
            "lua_chon": config["lua_chon"],
            "cau_tu": config["cau_tu"],
            "cau_den": config["cau_den"],
            "anh": f"groups/{name}.png",

            "toa_do": [
                round(value, 2)
                for value in crop
            ],
        }

    return images, group_info


# =====================================================
# 22. TAO HTML XEM TRUOC
# =====================================================

def preview_html():

    cards = []

    for name, config in GROUPS.items():

        first = config["cau_tu"]
        last = config["cau_den"]

        numbers = "".join(
            f'<span class="num">Câu {n}</span>'

            for n in range(
                first,
                last + 1
            )
        )

        cards.append(
            '<section>'
            f'<h2>Câu {first}–{last}</h2>'
            f'<img src="groups/{name}.png" '
            f'alt="Bảng hình câu {first}-{last}">'
            f'<div class="numbers">{numbers}</div>'
            '</section>'
        )

    html = """
<!doctype html>
<html lang="vi">

<head>
<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>HSK3 Đề 11 - H31330</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    background: #f2f5fa;
    color: #152944;
    font-family: Arial, sans-serif;
}

main {
    max-width: 960px;
    margin: auto;
}

section {
    background: white;
    border: 1px solid #d9e2ee;
    border-radius: 14px;
    padding: 24px;
    margin: 20px 0;
}

h2 {
    font-size: 21px;
}

img {
    display: block;
    max-width: 100%;
    height: auto;
    margin: 12px auto 20px;
}

.numbers {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.num {
    padding: 12px 17px;
    border: 1px solid #ccd8e7;
    border-radius: 8px;
}

p {
    color: #64748b;
}
</style>

</head>

<body>
<main>

<h1>HSK3 – Đề 11 (H31330)</h1>

<p>
Kiểm tra hai bảng hình câu 1–10.
Không hiển thị đáp án.
</p>

__CARDS__

</main>
</body>
</html>
"""

    return html.replace(
        "__CARDS__",
        "\n".join(cards)
    ).encode("utf-8")


# =====================================================
# 23. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 11 - BUOC 1")
    print("MA DE GOC H31330")
    print("=" * 60)

    pdf_file, mp3_file = find_sources()

    print("PDF:", pdf_file.name)

    if mp3_file:
        print("MP3:", mp3_file.name)
    else:
        print(
            "Chua co MP3 "
            "(buoc 1 khong bat buoc)."
        )

    # ================================================
    # 24. DOC PDF VA DAP AN
    # ================================================

    with fitz.open(pdf_file) as doc:

        check_pdf(doc)

        objective = read_objective(
            doc[14]
        )

        writing = read_writing(
            doc[15]
        )

        answers = {
            **objective,
            **writing
        }

        tokens = read_writing_tokens(
            doc[12],
            answers
        )

        images, group_info = (
            render_groups(doc)
        )

    # ================================================
    # 25. TAO DANH SACH 80 CAU
    # ================================================

    questions = []

    for number in range(1, 81):

        page = next(
            page_no

            for page_no, numbers
            in PAGE_QUESTIONS.items()

            if number in numbers
        )

        section = (
            "nghe"
            if number <= 40
            else "doc"
            if number <= 70
            else "viet"
        )

        if number <= 5:
            group = "nghe_01_05"

        elif number <= 10:
            group = "nghe_06_10"

        else:
            group = None

        if number <= 10:
            kind = "chon_hinh"

        elif number <= 20:
            kind = "dung_sai"

        elif number <= 40:
            kind = "chon_mot"

        elif number <= 60:
            kind = "ghep_lua_chon"

        elif number <= 70:
            kind = "chon_mot"

        elif number <= 75:
            kind = "sap_xep"

        else:
            kind = "dien_tu"

        questions.append({
            "so_cau": number,
            "phan": section,
            "dang": kind,
            "trang_pdf": page,

            "dap_an_dung": answers[number],

            "nhom_hinh": group,
            "da_duyet": False,
        })

    # ================================================
    # 26. TAO JSON DAP AN
    # ================================================

    result = {
        "cap_hsk": 3,
        "so_de": 11,
        "ma_de_goc": CODE,

        "file_pdf": str(pdf_file),

        "file_mp3": (
            str(mp3_file)
            if mp3_file else None
        ),

        "nguon_dap_an": "pdf_chung",

        "so_trang_pdf_de": 16,

        "tong_cau": 80,
        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "thoi_gian_pdf_phut": 90,

        "thoi_gian_lam_bai_de_xuat_phut": 85,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        "trang_loi_thoai": [],

        "trang_dap_an": [15, 16],

        "bang_trang_cau_hoi": {
            str(page): list(numbers)

            for page, numbers
            in PAGE_QUESTIONS.items()
        },

        "bang_hinh_chung": group_info,

        "dap_an": {
            str(number): answers[number]

            for number in range(1, 81)
        },

        "dap_an_thay_the": {},

        "dap_an_pdf_nguyen_van": {
            str(number): writing[number]

            for number in range(71, 81)
        },

        "cum_tu_sap_xep": {
            str(number): tokens[number]

            for number in range(71, 76)
        },

        "cau_hoi": questions,
    }

    # ================================================
    # 27. CHUAN BI FILE DAU RA
    # ================================================

    outputs = {
        ANSWER_JSON: json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8"),

        PREVIEW_HTML: preview_html(),
    }

    for name, content in images.items():

        outputs[
            GROUP_DIR / f"{name}.png"
        ] = content

    # ================================================
    # 28. KHONG GHI DE FILE KHAC NOI DUNG
    # ================================================

    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):
            raise RuntimeError(
                "File da co noi dung khac:\n"
                + str(path)
            )

    # ================================================
    # 29. LUU JSON, HTML VA HINH
    # ================================================

    for path, content in outputs.items():

        save_safe(
            path,
            content
        )

    # ================================================
    # 30. KET QUA
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH HSK3 DE 11 - BUOC 1"
    )

    print("=" * 60)

    print("Ma de goc: H31330")
    print("PDF: 16 trang")

    print("Nghe: 40")
    print("Doc: 30")
    print("Viet: 10")

    print("Dap an: 80/80")
    print("Cum tu 71-75: 5/5 KHOP")

    print("Bang hinh cau 1-5: 6 lua chon A-F")
    print("Bang hinh cau 6-10: 5 lua chon A-E")

    print("Khong hien thi dap an trong HTML")

    print(f"\nJSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
