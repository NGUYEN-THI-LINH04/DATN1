
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 08 (H31008)

BUOC 1:
- Kiem tra PDF 22 trang.
- Doc va doi chieu 70 dap an Nghe/Doc.
- Doc 10 dap an Viet.
- Kiem tra cum tu sap xep cau 71-75.
- Tach 2 bang hinh Nghe cau 1-10.
- Tao JSON dap an.
- Tao HTML xem truoc.

KHONG ket noi SQL Server.
KHONG sua cac de thi cu.
KHONG ghi de file khac noi dung.
"""

from pathlib import Path
from itertools import permutations
import json
import re
import unicodedata

import fitz


# =====================================================
# 1. CAU HINH
# =====================================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "luyen_thi"

SOURCE = (
    BASE / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 8"
)

DATA = BASE / "hsk3" / "data" / "de_08"

OUTPUT = BASE / "hsk3" / "output" / "de_08"

GROUP_DIR = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_08_dap_an.json"

PREVIEW_HTML = (
    OUTPUT / "kiem_tra_10_cau.html"
)

CODE = "H31008"


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
        "rect": (75, 175, 515, 515),
        "lua_chon": "ABCDEF",
        "cau_tu": 1,
        "cau_den": 5,
    },

    "nghe_06_10": {
        "trang_pdf": 3,
        "rect": (75, 130, 515, 522),
        "lua_chon": "ABCDE",
        "cau_tu": 6,
        "cau_den": 10,
    },
}


# =====================================================
# 4. DAP AN H31008 - NGHE/DOC
# =====================================================

# Doi chieu theo trang 21 PDF H31008.

EXPECTED_ROWS = [
    "A B F C E",
    "C B A E D",

    "× × √ × √",
    "× √ √ × √",

    "B C B A A",
    "B B C A A",

    "C C B A B",
    "A C A C B",

    "F B C D A",
    "D A E C B",

    "D B F A C",
    "A C F B E",

    "A C C B A",
    "C A B C B",
]


# =====================================================
# 5. DAP AN H31008 - PHAN VIET
# =====================================================

# Doi chieu theo trang 22 PDF H31008.

EXPECTED_WRITING = {
    71: "那位邻居很热情。",

    72: "这个楼一共三层。",

    73: "菜单被服务员拿走了。",

    74: "中国南方的雨水比北方多。",

    75: "把冰箱放厨房里吧。",

    76: "几",
    77: "心",
    78: "下",
    79: "大",
    80: "云",
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
        or path.stat().st_size <= 0
    ):
        raise RuntimeError(
            f"Thieu file hoac file rong:\n{path}"
        )

    return path


# =====================================================
# 7. TIM PDF VA MP3 NGUON
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
            "Thu muc DE 8 can dung 1 PDF."
            f"\nTim thay: {len(pdfs)}"
            f"\nThu muc: {SOURCE}"
        )

    if len(mp3s) > 1:

        raise RuntimeError(
            "Thu muc DE 8 co nhieu MP3."
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

    if len(doc) != 22:

        raise RuntimeError(
            "PDF H31008 phai co 22 trang."
            f"\nHien tai: {len(doc)}"
        )

    # Trang bia va trang 21 co ma de.
    # Trang 22 khong bat buoc lap lai ma de.

    for page_no in (1, 21):

        text = norm(
            doc[page_no - 1].get_text("text")
        )

        if CODE not in text:

            raise RuntimeError(
                f"Trang {page_no} "
                f"khong co ma de {CODE}."
            )

    # Kiem tra trang loi thoai.

    transcript = compact(
        doc[14].get_text("text")
    )

    if "听力材料" not in transcript:

        raise RuntimeError(
            "Trang 15 khong phai "
            "loi thoai Nghe."
        )

    # Kiem tra hai trang dap an.

    if "答案" not in doc[20].get_text("text"):

        raise RuntimeError(
            "Trang 21 khong phai "
            "dap an Nghe/Doc."
        )

    if "书" not in doc[21].get_text("text"):

        raise RuntimeError(
            "Trang 22 khong phai dap an Viet."
        )

    # Kiem tra tieu de cac phan.

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

        text = norm(
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

    print("PDF: 22 trang")

    print("Trang 2-14: Cau hoi")
    print("Trang 15-20: Loi thoai Nghe")
    print("Trang 21: Dap an Nghe/Doc")
    print("Trang 22: Dap an Viet")


# =====================================================
# 13. DOC 70 DAP AN NGHE/DOC
# =====================================================

def read_objective(page):

    text = norm(
        page.get_text("text")
    )

    pattern = re.compile(
        r"(?<!\d)(\d{1,2})\s*[.、]"
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
                f"sai dang: {answer}"
            )

        answers[number] = answer

    if set(answers) != set(range(1, 71)):

        missing = sorted(
            set(range(1, 71))
            - set(answers)
        )

        raise RuntimeError(
            f"Thieu dap an Nghe/Doc: {missing}"
        )

    # ================================================
    # 14. DOI CHIEU BANG DAP AN GOC
    # ================================================

    expected = [
        item

        for row in EXPECTED_ROWS

        for item in row.split()
    ]

    if len(expected) != 70:

        raise RuntimeError(
            "Bang doi chieu khong du "
            "70 dap an."
        )

    for number in range(1, 71):

        if (
            answers[number]
            != expected[number - 1]
        ):

            raise RuntimeError(
                f"Dap an cau {number} "
                "khong khop PDF H31008."
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

        if (
            compact(answers[number])
            != compact(EXPECTED_WRITING[number])
        ):

            raise RuntimeError(
                f"Sai dap an Viet cau {number}."
                f"\nPDF: {answers[number]}"
                f"\nMau: {EXPECTED_WRITING[number]}"
            )

    # Cau 76-80 dien 1 chu Han.

    for number in range(76, 81):

        if len(compact(answers[number])) != 1:

            raise RuntimeError(
                f"Cau {number} khong phai "
                "dien mot chu Han."
            )

    return answers


# =====================================================
# 17. DOC CUM TU SAP XEP CAU 71-75
# =====================================================

def read_writing_tokens(page, answers):

    text = page.get_text("text")

    tokens = {}

    pattern = re.compile(
        r"^\s*(7[1-5])\s*[.．、]"
        r"\s*(.+)"
    )

    for line in text.splitlines():

        match = pattern.match(line)

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
            part.strip()

            for part in re.split(
                r"\s{2,}",
                match.group(2)
            )

            if part.strip()
        ]

        tokens[number] = values

    if set(tokens) != set(range(71, 76)):

        raise RuntimeError(
            "Khong doc du cum tu "
            "sap xep cau 71-75."
        )

    # ================================================
    # 18. KIEM TRA KHA NANG GHEP CAU
    # ================================================

    for number in range(71, 76):

        values = tokens[number]

        if not 3 <= len(values) <= 8:

            raise RuntimeError(
                f"Cau {number} co so "
                "cum tu khong hop le."
            )

        valid = any(
            compact("".join(order))
            == compact(answers[number])

            for order in permutations(values)
        )

        if not valid:

            raise RuntimeError(
                f"Cau {number}: dap an "
                "khong ghep duoc tu "
                "cac cum tu trong PDF."
            )

    return tokens


# =====================================================
# 19. TACH HAI BANG HINH NGHE
# =====================================================

def render_groups(doc):

    images = {}

    for name, config in (
        GROUP_RECTS.items()
    ):

        page_no = config["trang_pdf"]

        page = doc[page_no - 1]

        rect = fitz.Rect(
            config["rect"]
        )

        if not page.rect.contains(rect):

            raise RuntimeError(
                f"Khung hinh {name} "
                "nam ngoai trang PDF."
            )

        # ============================================
        # 20. KIEM TRA NHAN A-F / A-E
        # ============================================

        labels = {
            norm(word[4]).strip()

            for word in page.get_text("words")

            if rect.contains(
                fitz.Point(
                    word[0],
                    word[1]
                )
            )
        }

        expected = set(
            config["lua_chon"]
        )

        if not expected.issubset(labels):

            missing = sorted(
                expected - labels
            )

            raise RuntimeError(
                f"Bang {name} thieu nhan: "
                f"{missing}"
            )

        # ============================================
        # 21. KIEM TRA ANH NAM TRONG VUNG CAT
        # ============================================

        image_boxes = [
            image_rect

            for image in page.get_images(
                full=True
            )

            for image_rect in (
                page.get_image_rects(
                    image[0]
                )
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

    cards = []

    for name, config in (
        GROUP_RECTS.items()
    ):

        first = config["cau_tu"]
        last = config["cau_den"]

        numbers = "".join(
            f'<span class="pill">Câu {n}</span>'

            for n in range(
                first,
                last + 1
            )
        )

        cards.append(
            '<section>'
            f'<h2>Câu {first}–{last}</h2>'
            f'<img src="groups/{name}.png" '
            f'alt="Hình câu {first}-{last}">'
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

<title>HSK3 Đề 8 - Kiểm tra câu 1–10</title>

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
    max-width: 1000px;
    margin: auto;
}

section {
    padding: 20px;
    margin: 18px 0;
    border: 1px solid #dce3ee;
    border-radius: 14px;
    background: white;
}

section img {
    display: block;
    max-width: 100%;
    height: auto;
    margin: auto;
}

.numbers {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 18px;
}

.pill {
    display: inline-block;
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

<h1>HSK3 – Đề 8 (H31008)</h1>

<p>
Kiểm tra hai bảng hình câu 1–10.
Chưa hiển thị đáp án.
Chưa thay đổi SQL Server.
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
# 24. LUU FILE AN TOAN
# =====================================================

def safe_write(path, content):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if path.exists():

        if path.read_bytes() != content:

            raise RuntimeError(
                "File da ton tai voi "
                "noi dung khac."
                "\nKhong ghi de:\n"
                + str(path)
            )

        return

    path.write_bytes(content)


# =====================================================
# 25. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 08 - BUOC 1")
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
    # 26. DOC PDF VA DAP AN
    # ================================================

    with fitz.open(pdf_file) as doc:

        check_pdf(doc)

        objective = read_objective(
            doc[20]
        )

        writing = read_writing(
            doc[21]
        )

        answers = {
            **objective,
            **writing
        }

        # Kiem tra cum tu 71-75.
        tokens = read_writing_tokens(
            doc[12],
            answers
        )

        # Tach hai bang hinh.
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
        "so_de": 8,
        "ma_de_goc": CODE,

        "file_pdf": str(pdf_file),

        "file_mp3": (
            str(mp3_file)
            if mp3_file else None
        ),

        "nguon_dap_an": "pdf_chung",

        "so_trang_pdf_de": 22,

        "tong_cau": 80,

        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "thoi_gian_pdf_phut": 90,

        "thoi_gian_lam_bai_de_xuat_phut": 85,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        "trang_loi_thoai": list(
            range(15, 21)
        ),

        "trang_dap_an": [21, 22],

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

        # Khong co dap an thay the
        # duoc ghi trong PDF goc.
        "dap_an_thay_the": {},

        "dap_an_pdf_nguyen_van": {
            str(number): writing[number]

            for number in range(71, 81)
        },

        # Luu cum tu goc de dung
        # khi chuan hoa JSON.
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
    # 30. BAO VE FILE CU
    # ================================================

    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):

            raise RuntimeError(
                "File da ton tai voi "
                "noi dung khac."
                "\nKhong ghi de:\n"
                + str(path)
            )

    # ================================================
    # 31. LUU FILE
    # ================================================

    for path, content in outputs.items():

        safe_write(
            path,
            content
        )

    # ================================================
    # 32. KET QUA
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH HSK3 DE 08 - BUOC 1")
    print("=" * 60)

    print("Ma de: H31008")
    print("PDF: 22 trang")

    print("Nghe: 40")
    print("Doc: 30")
    print("Viet: 10")

    print("Dap an: 80/80")

    print("Cum tu cau 71-75: 5/5 KHOP")

    print("Bang hinh cau 1-5: 6 lua chon")
    print("Bang hinh cau 6-10: 5 lua chon")

    print("Dap an thay the: khong co trong PDF")

    print(f"\nJSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
