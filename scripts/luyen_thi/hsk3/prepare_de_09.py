
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 09 (H31327) - BUOC 1

- PDF goc: 16 trang.
- Cau hoi: trang 2-14.
- Dap an Nghe/Doc: trang 15.
- Dap an Viet: trang 16.
- Kiem tra 80 dap an.
- Kiem tra 5 cau sap xep 71-75.
- Tach 2 bang hinh chung cau 1-10.
- Tao JSON va HTML xem truoc.

KHONG ket noi SQL Server.
KHONG sua cac de thi cu.
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
    os.environ.get("MOC_HAN_ROOT", r"D:\DATN1")
)

BASE = ROOT / "scripts" / "luyen_thi"

SOURCE = (
    BASE / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 9"
)

DATA = (
    BASE / "hsk3" / "data" / "de_09"
)

OUTPUT = (
    BASE / "hsk3" / "output" / "de_09"
)

GROUP_DIR = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_09_dap_an.json"

PREVIEW_HTML = (
    OUTPUT / "kiem_tra_10_cau.html"
)

# Ma de GOC tren PDF, khong phai H31009.
CODE = "H31327"


# =====================================================
# 2. SO DO TRANG CAU HOI
# =====================================================

PAGE_QUESTIONS = {
    2: list(range(1, 6)),
    3: list(range(6, 11)),

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


# =====================================================
# 3. HAI BANG HINH NGHE CAU 1-10
# =====================================================

GROUP_RECTS = {
    "nghe_01_05": {
        "trang_pdf": 2,
        "rect": (75, 165, 515, 515),
        "lua_chon": "ABCDEF",
        "cau_tu": 1,
        "cau_den": 5,
    },

    "nghe_06_10": {
        "trang_pdf": 3,
        "rect": (75, 130, 515, 510),
        "lua_chon": "ABCDE",
        "cau_tu": 6,
        "cau_den": 10,
    },
}


# =====================================================
# 4. DAP AN GOC H31327 - NGHE/DOC
# =====================================================

# Doi chieu theo trang 15 PDF.

EXPECTED_ROWS = [
    "F A C E B",
    "B A D E C",

    "× √ × × √",
    "√ × √ × √",

    "A B A A C",
    "C A B A B",

    "B C A B C",
    "A A B C C",

    "B D C F A",
    "E D C A B",

    "A C D F B",
    "C F E A B",

    "B A A C C",
    "B C B B C",
]


# =====================================================
# 5. DAP AN GOC H31327 - PHAN VIET
# =====================================================

# Doi chieu theo trang 16 PDF.

EXPECTED_WRITING = {
    71: "蛋糕被我吃了。",

    72: "猫是一种爱干净的动物。",

    73: "那个体育馆能坐两万人。",

    74: "街道两边的树长得真高。",

    75: "请用黑板上的词写一个句子。",

    76: "文",
    77: "公",
    78: "到",
    79: "学",
    80: "和",
}


# =====================================================
# 6. CAC HAM HO TRO
# =====================================================

def normalize(value):

    return unicodedata.normalize(
        "NFKC",
        str(value)
    )


def compact(value):

    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "",
        normalize(value)
    )


def require_file(path):

    if (
        not path.is_file()
        or path.stat().st_size == 0
    ):
        raise RuntimeError(
            f"File khong ton tai hoac rong:\n{path}"
        )

    return path


# =====================================================
# 7. TIM PDF VA MP3
# =====================================================

def find_sources():

    pdfs = sorted(
        SOURCE.glob("*.pdf")
    )

    mp3s = sorted(
        SOURCE.glob("*.mp3")
    )

    if len(pdfs) != 1:

        raise RuntimeError(
            "Thu muc DE 9 can dung 1 PDF."
            f"\nTim thay: {len(pdfs)}"
            f"\nThu muc: {SOURCE}"
        )

    if len(mp3s) > 1:

        raise RuntimeError(
            "Thu muc DE 9 co nhieu MP3."
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
# 8. XAC DINH TRANG PDF
# =====================================================

def page_for(number):

    for page_no, numbers in (
        PAGE_QUESTIONS.items()
    ):

        if number in numbers:
            return page_no

    raise RuntimeError(
        f"Khong tim thay trang cau {number}."
    )


# =====================================================
# 9. XAC DINH KY NANG
# =====================================================

def section_for(number):

    if number <= 40:
        return "nghe"

    if number <= 70:
        return "doc"

    return "viet"


# =====================================================
# 10. XAC DINH DANG CAU HOI
# =====================================================

def kind_for(number):

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


# =====================================================
# 11. KIEM TRA DANG DAP AN
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
# 12. KIEM TRA BO CUC PDF
# =====================================================

def check_pdf(doc):

    if len(doc) != 16:

        raise RuntimeError(
            "PDF H31327 phai co 16 trang."
            f"\nHien co: {len(doc)}"
        )

    cover = normalize(
        doc[0].get_text("text")
    )

    answer_page = normalize(
        doc[14].get_text("text")
    )

    if (
        CODE not in cover
        or CODE not in answer_page
    ):
        raise RuntimeError(
            "Ma de PDF khong phai H31327."
        )

    if "答案" not in doc[14].get_text("text"):

        raise RuntimeError(
            "Trang 15 khong phai "
            "bang dap an Nghe/Doc."
        )

    if "书" not in doc[15].get_text("text"):

        raise RuntimeError(
            "Trang 16 khong phai dap an Viet."
        )

    # Trang 12 tiep noi cau 65-70
    # nen khong co tieu de rieng.

    headings = [
        (2, 1, 5),
        (3, 6, 10),

        (4, 11, 20),
        (5, 21, 30),
        (6, 31, 40),

        (7, 41, 45),
        (8, 46, 50),

        (9, 51, 55),
        (10, 56, 60),

        (11, 61, 70),

        (13, 71, 75),
        (14, 76, 80),
    ]

    for page_no, first, last in headings:

        text = normalize(
            doc[page_no - 1].get_text("text")
        )

        pattern = (
            rf"第\s*{first}\s*[-–—]"
            rf"\s*{last}\s*题"
        )

        if not re.search(pattern, text):

            raise RuntimeError(
                f"Trang {page_no} thieu "
                f"tieu de cau {first}-{last}."
            )

    print("\n===== BO CUC PDF =====")

    print("PDF: 16 trang")
    print("Trang 2-14: Cau hoi")
    print("Trang 15: Dap an Nghe/Doc")
    print("Trang 16: Dap an Viet")
    print("Khong co trang loi thoai Nghe")


# =====================================================
# 13. DOC 70 DAP AN NGHE/DOC
# =====================================================

def read_objective(page):

    text = normalize(
        page.get_text("text")
    )

    pattern = re.compile(
        r"(?<!\d)(\d{1,2})\s*[.．、]"
        r"\s*([A-F√×])(?=\s|$)"
    )

    answers = {}

    for match in pattern.finditer(text):

        number = int(
            match.group(1)
        )

        if not 1 <= number <= 70:
            continue

        if number in answers:

            raise RuntimeError(
                f"Trung dap an cau {number}."
            )

        answer = match.group(2)

        if answer not in allowed_for(number):

            raise RuntimeError(
                f"Dap an cau {number} "
                "khong hop le."
            )

        answers[number] = answer

    if set(answers) != set(range(1, 71)):

        missing = sorted(
            set(range(1, 71))
            - set(answers)
        )

        raise RuntimeError(
            f"Thieu dap an: {missing}"
        )

    # ================================================
    # 14. DOI CHIEU BANG DAP AN PDF
    # ================================================

    expected = [
        value
        for row in EXPECTED_ROWS
        for value in row.split()
    ]

    if len(expected) != 70:

        raise RuntimeError(
            "Bang doi chieu khong du 70 dap an."
        )

    for number in range(1, 71):

        if (
            answers[number]
            != expected[number - 1]
        ):
            raise RuntimeError(
                f"Dap an cau {number} "
                "khong khop bang goc."
            )

    return answers


# =====================================================
# 15. DOC 10 DAP AN VIET
# =====================================================

def read_writing(page):

    text = page.get_text("text")

    pattern = re.compile(
        r"^\s*(7[1-9]|80)\s*[.．、]"
        r"\s*([^\n]+)",
        re.MULTILINE
    )

    answers = {}

    for match in pattern.finditer(text):

        number = int(
            match.group(1)
        )

        if number in answers:

            raise RuntimeError(
                f"Trung dap an Viet cau {number}."
            )

        answers[number] = (
            match.group(2).strip()
        )

    if set(answers) != set(range(71, 81)):

        missing = sorted(
            set(range(71, 81))
            - set(answers)
        )

        raise RuntimeError(
            f"Thieu dap an Viet: {missing}"
        )

    # ================================================
    # 16. DOI CHIEU DAP AN VIET
    # ================================================

    for number in range(71, 81):

        if compact(
            answers[number]
        ) != compact(
            EXPECTED_WRITING[number]
        ):

            raise RuntimeError(
                f"Dap an Viet cau {number} "
                "khong khop PDF."
            )

    # Cau 76-80: dien mot chu Han.

    for number in range(76, 81):

        if len(compact(answers[number])) != 1:

            raise RuntimeError(
                f"Cau {number} phai dien "
                "mot chu Han."
            )

    return answers


# =====================================================
# 17. DOC CUM TU SAP XEP CAU 71-75
# =====================================================

def read_writing_tokens(page, answers):

    text = page.get_text("text")

    tokens = {}

    for line in text.splitlines():

        match = re.match(
            r"^\s*(7[1-5])\s*[.．、]"
            r"\s*(.+)",
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

    if set(tokens) != set(range(71, 76)):

        raise RuntimeError(
            "Khong tim du 5 cau "
            "sap xep 71-75."
        )

    # ================================================
    # 18. KIEM TRA KHA NANG GHEP CAU
    # ================================================

    for number in range(71, 76):

        values = tokens[number]

        if not 3 <= len(values) <= 8:

            raise RuntimeError(
                f"Cau {number} co "
                "so cum tu khong hop le."
            )

        valid = any(
            compact("".join(order))
            == compact(answers[number])

            for order in permutations(values)
        )

        if not valid:

            raise RuntimeError(
                f"Cau {number}: dap an "
                "khong ghep duoc tu PDF."
            )

    return tokens


# =====================================================
# 19. TACH HAI BANG HINH CAU 1-10
# =====================================================

def render_groups(doc):

    images = {}

    for name, config in GROUP_RECTS.items():

        page = doc[
            config["trang_pdf"] - 1
        ]

        rect = fitz.Rect(
            config["rect"]
        )

        if not page.rect.contains(rect):

            raise RuntimeError(
                f"Khung cat {name} ngoai trang."
            )

        # ============================================
        # 20. KIEM TRA NHAN LUA CHON
        # ============================================

        labels = {
            normalize(word[4]).strip()

            for word in page.get_text("words")

            if rect.contains(
                fitz.Point(
                    word[0],
                    word[1]
                )
            )
        }

        expected_labels = set(
            config["lua_chon"]
        )

        missing = expected_labels - labels

        if missing:

            raise RuntimeError(
                f"Bang {name} thieu "
                f"nhan: {sorted(missing)}"
            )

        # ============================================
        # 21. KIEM TRA SO ANH TRONG BANG
        # ============================================

        image_boxes = [
            image_rect

            for image in page.get_images(
                full=True
            )

            for image_rect in page.get_image_rects(
                image[0]
            )
        ]

        contained = sum(
            rect.contains(image_rect)

            for image_rect in image_boxes
        )

        expected_count = len(
            config["lua_chon"]
        )

        if contained != expected_count:

            raise RuntimeError(
                f"Bang {name} co "
                f"{contained} anh, "
                f"can {expected_count}."
            )

        # ============================================
        # 22. XUAT ANH PNG
        # ============================================

        pix = page.get_pixmap(
            matrix=fitz.Matrix(2.5, 2.5),
            clip=rect,
            alpha=False
        )

        images[name] = (
            pix.tobytes("png")
        )

        print(
            f"{name}: "
            f"{expected_count} lua chon, "
            f"{contained} anh"
        )

    return images


# =====================================================
# 23. TAO HTML XEM TRUOC
# =====================================================

def preview_html():

    sections = []

    for name, config in GROUP_RECTS.items():

        first = config["cau_tu"]
        last = config["cau_den"]

        numbers = "".join(
            f'<span>Câu {number}</span>'

            for number in range(
                first,
                last + 1
            )
        )

        sections.append(
            '<section>'
            f'<h2>Câu {first}–{last}</h2>'

            f'<img src="groups/{name}.png" '
            f'alt="Hình câu {first}-{last}">'

            f'<div class="nums">{numbers}</div>'
            '</section>'
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

<title>HSK3 Đề 9 - H31327</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 24px;
    background: #f3f5f9;
    color: #1e293b;
    font-family: Arial, sans-serif;
}

main {
    max-width: 960px;
    margin: auto;
}

section {
    background: white;
    border: 1px solid #dbe2eb;
    border-radius: 14px;
    padding: 20px;
    margin: 20px 0;
}

section img {
    display: block;
    width: 100%;
    max-width: 760px;
    height: auto;
    margin: auto;
}

.nums {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 20px;
}

.nums span {
    padding: 10px 14px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-weight: bold;
}

p {
    color: #64748b;
}
</style>

</head>

<body>

<main>

<h1>HSK3 – Đề 9 (H31327)</h1>

<p>
Kiểm tra hai bảng hình câu 1–10.
Không hiển thị đáp án.
Chưa thay đổi SQL Server.
</p>

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
# 24. LUU FILE AN TOAN
# =====================================================

def save_safe(path, content):

    if path.exists():

        if path.read_bytes() != content:

            raise RuntimeError(
                "File da ton tai voi "
                "noi dung khac.\n"
                "KHONG ghi de:\n"
                + str(path)
            )

        return

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_bytes(content)


# =====================================================
# 25. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 09 - BUOC 1")
    print("MA DE GOC H31327")
    print("=" * 60)

    pdf_file, mp3_file = find_sources()

    print(f"PDF: {pdf_file.name}")

    if mp3_file:

        print(f"MP3: {mp3_file.name}")

    else:

        print(
            "Chua co MP3 - "
            "buoc 1 van chay duoc."
        )

    # ================================================
    # 26. DOC PDF VA DOI CHIEU DAP AN
    # ================================================

    with fitz.open(pdf_file) as doc:

        check_pdf(doc)

        # Trang 15 -> index 14.
        objective = read_objective(
            doc[14]
        )

        # Trang 16 -> index 15.
        writing = read_writing(
            doc[15]
        )

        answers = {
            **objective,
            **writing
        }

        # Cau 71-75 nam o trang 13.
        tokens = read_writing_tokens(
            doc[12],
            answers
        )

        print("\n===== DOI CHIEU DAP AN =====")

        print("Nghe/Doc: 70/70")
        print("Viet: 10/10")
        print("Cum tu 71-75: 5/5")

        print("\n===== TACH BANG HINH =====")

        images = render_groups(
            doc
        )

    if set(answers) != set(range(1, 81)):

        raise RuntimeError(
            "Khong du 80 dap an."
        )

    # ================================================
    # 27. TAO DANH SACH 80 CAU
    # ================================================

    questions = []

    for number in range(1, 81):

        if number <= 5:
            group = "nghe_01_05"

        elif number <= 10:
            group = "nghe_06_10"

        else:
            group = None

        questions.append({
            "so_cau": number,

            "phan": section_for(number),

            "dang": kind_for(number),

            "trang_pdf": page_for(number),

            "dap_an_dung": answers[number],

            "nhom_hinh": group,

            "da_duyet": False,
        })

    # ================================================
    # 28. TAO JSON DAP AN
    # ================================================

    result = {
        "cap_hsk": 3,
        "so_de": 9,
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

        # PDF H31327 khong co transcript.
        "trang_loi_thoai": [],

        "trang_dap_an": [15, 16],

        "bang_trang_cau_hoi": {
            str(page): numbers

            for page, numbers
            in PAGE_QUESTIONS.items()
        },

        "bang_hinh_chung": {
            name: {
                "trang_pdf": config["trang_pdf"],

                "lua_chon": config["lua_chon"],

                "anh": f"groups/{name}.png",
            }

            for name, config
            in GROUP_RECTS.items()
        },

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
    # 29. CHUAN BI FILE DAU RA
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
    # 30. KIEM TRA KHONG GHI DE FILE CU
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
    # 31. LUU JSON, ANH VA HTML
    # ================================================

    for path, content in outputs.items():

        save_safe(
            path,
            content
        )

    # ================================================
    # 32. KET QUA
    # ================================================

    print("\n" + "=" * 60)

    print("HOAN THANH HSK3 DE 09 - BUOC 1")

    print("=" * 60)

    print("Ma de goc: H31327")
    print("Ten: De 9")

    print("PDF: 16 trang")

    print("Nghe: 40")
    print("Doc: 30")
    print("Viet: 10")

    print("Dap an: 80/80")

    print("Cum tu 71-75: 5/5 KHOP")

    print("Bang hinh cau 1-5: 6 lua chon")
    print("Bang hinh cau 6-10: 5 lua chon")

    print("Dap an thay the: khong co trong PDF")

    print(f"\nJSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
