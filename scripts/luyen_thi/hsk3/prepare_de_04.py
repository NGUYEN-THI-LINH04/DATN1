
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 04 (H31004)

BUOC 1:
- Doc PDF goc 22 trang.
- Kiem tra ma de va bo cuc.
- Lay 70 dap an Nghe/Doc.
- Lay 10 dap an Viet.
- Giu 2 dap an hop le cua cau 75.
- Tach 2 bang hinh chung cau 1-10.
- Tao JSON dap an va HTML xem truoc.

KHONG thay doi SQL Server.
KHONG anh huong cac de da hoan thanh.
"""

from pathlib import Path
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
    / "HSK3" / "ĐỀ 4"
)

HSK3 = BASE / "hsk3"

DATA = HSK3 / "data" / "de_04"
OUTPUT = HSK3 / "output" / "de_04"

GROUP_DIR = OUTPUT / "groups"

ANSWER_JSON = (
    DATA / "de_04_dap_an.json"
)

PREVIEW_HTML = (
    OUTPUT / "kiem_tra_10_cau.html"
)

EXAM_CODE = "H31004"
EXAM_NUMBER = 4


# =====================================================
# 2. BO CUC PDF
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

TRANSCRIPT_PAGES = list(range(15, 21))
ANSWER_PAGES = [21, 22]


# =====================================================
# 3. HAI BANG HINH CHUNG
# =====================================================

GROUP_RECTS = {
    "nghe_01_05": {
        "trang_pdf": 2,
        "rect": (75, 175, 515, 515),
        "lua_chon": "ABCDEF",
    },

    "nghe_06_10": {
        "trang_pdf": 3,
        "rect": (75, 130, 515, 522),
        "lua_chon": "ABCDE",
    },
}


# =====================================================
# 4. DAP AN GOC H31004 - NGHE/DOC
# =====================================================

EXPECTED_ROWS = [
    "C E F A B",
    "A E B D C",

    "√ × × × √",
    "√ × × √ √",

    "C A A C A",
    "B B C A C",

    "C B A A B",
    "A C B C A",

    "C D B F A",
    "C A D E B",

    "B F C D A",
    "F B E C A",

    "B A B A B",
    "B C C C B",
]


# =====================================================
# 5. DAP AN GOC H31004 - PHAN VIET
# =====================================================

EXPECTED_WRITING = {
    71: ["药在我的包里。"],

    72: ["他要去机场接女朋友。"],

    73: ["你脚下的路还很长。"],

    74: ["她不喜欢用铅笔写字。"],

    # PDF chap nhan ca hai cach viet.
    75: [
        "你丈夫的鼻子怎么了？",
        "你的丈夫鼻子怎么了？",
    ],

    76: ["手"],
    77: ["是"],
    78: ["家"],
    79: ["会"],
    80: ["花"],
}


# =====================================================
# 6. HAM HO TRO
# =====================================================

def normalize(text):

    return unicodedata.normalize(
        "NFKC",
        str(text)
    )


def compact(text):

    return re.sub(
        r"\s+",
        "",
        normalize(text)
    )


def check_file(path):

    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay:\n{path}"
        )

    if path.stat().st_size == 0:
        raise RuntimeError(
            f"File rong: {path}"
        )


def find_source_files():

    pdf_files = sorted(
        SOURCE.glob("*.pdf")
    )

    mp3_files = sorted(
        SOURCE.glob("*.mp3")
    )

    if len(pdf_files) != 1:
        raise RuntimeError(
            "Thu muc DE 4 phai co dung "
            "1 file PDF.\n"
            f"Tim thay: {len(pdf_files)}"
        )

    if len(mp3_files) > 1:
        raise RuntimeError(
            "Thu muc DE 4 co nhieu MP3."
        )

    pdf_file = pdf_files[0]
    check_file(pdf_file)

    mp3_file = (
        mp3_files[0]
        if mp3_files else None
    )

    if mp3_file:
        check_file(mp3_file)

    return pdf_file, mp3_file


def write_safe(path, content):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if path.exists():

        if path.read_bytes() != content:
            raise RuntimeError(
                "File da ton tai voi "
                "noi dung khac.\n"
                "Khong ghi de:\n"
                + str(path)
            )

        return

    path.write_bytes(content)


# =====================================================
# 7. TAO BANG 70 DAP AN MAU
# =====================================================

def expected_objective():

    result = {}

    for row_index, row in enumerate(
        EXPECTED_ROWS
    ):

        values = row.split()

        if len(values) != 5:
            raise RuntimeError(
                "Bang dap an mau sai."
            )

        for index, answer in enumerate(
            values
        ):

            number = (
                row_index * 5 + index + 1
            )

            result[number] = answer

    if set(result) != set(range(1, 71)):
        raise RuntimeError(
            "Dap an mau khong du 70 cau."
        )

    return result


EXPECTED_OBJECTIVE = expected_objective()


# =====================================================
# 8. KIEM TRA DANG DAP AN
# =====================================================

def validate_objective(number, answer):

    if number <= 5:
        allowed = set("ABCDEF")

    elif number <= 10:
        allowed = set("ABCDE")

    elif number <= 20:
        allowed = {"√", "×"}

    elif number <= 40:
        allowed = set("ABC")

    elif number <= 45:
        allowed = set("ABCDEF")

    elif number <= 50:
        allowed = set("ABCDE")

    elif number <= 60:
        allowed = set("ABCDEF")

    elif number <= 70:
        allowed = set("ABC")

    else:
        raise RuntimeError(
            f"So cau khong hop le: {number}"
        )

    if answer not in allowed:
        raise RuntimeError(
            f"Sai dang dap an cau {number}: "
            f"{answer}"
        )


# =====================================================
# 9. KIEM TRA PDF GOC
# =====================================================

def check_pdf(doc):

    if len(doc) != 22:
        raise RuntimeError(
            f"PDF co {len(doc)} trang, "
            "H31004 phai co 22 trang."
        )

    cover = compact(
        doc[0].get_text("text")
    )

    if EXAM_CODE not in cover:
        raise RuntimeError(
            "Trang bia khong phai H31004."
        )

    for page_no in (21, 22):

        text = compact(
            doc[page_no - 1].get_text("text")
        )

        if EXAM_CODE not in text:
            raise RuntimeError(
                f"Trang {page_no} sai ma de."
            )

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

    transcript = compact(
        doc[14].get_text("text")
    )

    if "听力材料" not in transcript:
        raise RuntimeError(
            "Trang 15 khong phai "
            "loi thoai Nghe."
        )

    if "答案" not in doc[20].get_text("text"):
        raise RuntimeError(
            "Trang 21 khong phai dap an."
        )

    if "书" not in doc[21].get_text("text"):
        raise RuntimeError(
            "Trang 22 khong phai dap an Viet."
        )

    print("\n===== BO CUC PDF =====")
    print("PDF: 22 trang")
    print("Trang 2-6: Nghe 40 cau")
    print("Trang 7-12: Doc 30 cau")
    print("Trang 13-14: Viet 10 cau")
    print("Trang 15-20: Loi thoai Nghe")
    print("Trang 21-22: Dap an")


# =====================================================
# 10. TRICH XUAT 70 DAP AN NGHE/DOC
# =====================================================

def extract_objective_answers(page):

    text = normalize(
        page.get_text("text")
    )

    pattern = re.compile(
        r"(?<!\d)(\d{1,2})\s*[.、]"
        r"\s*([A-F√×])(?=\s|$)"
    )

    answers = {}

    for match in pattern.finditer(text):

        number = int(match.group(1))
        answer = match.group(2)

        if not 1 <= number <= 70:
            continue

        if number in answers:
            raise RuntimeError(
                f"Trung dap an cau {number}."
            )

        validate_objective(
            number,
            answer
        )

        answers[number] = answer

    if set(answers) != set(range(1, 71)):

        missing = sorted(
            set(range(1, 71)) - set(answers)
        )

        raise RuntimeError(
            f"Thieu dap an: {missing}"
        )

    # Doi chieu voi bang da kiem tra
    # tren trang 21 cua H31004.
    for number in range(1, 71):

        if (
            answers[number]
            != EXPECTED_OBJECTIVE[number]
        ):
            raise RuntimeError(
                f"Dap an cau {number} "
                "khong khop PDF H31004."
            )

    return answers


# =====================================================
# 11. TRICH XUAT 10 DAP AN VIET
# =====================================================

def extract_writing_answers(page):

    # Giu nguyen chu Han va dau cau
    # de bao toan dap an goc.
    text = page.get_text("text")

    pattern = re.compile(
        r"^\s*(7[1-9]|80)\s*[.．、]"
        r"\s*([^\n]+)",
        re.MULTILINE
    )

    raw_answers = {}

    for match in pattern.finditer(text):

        number = int(match.group(1))
        value = match.group(2).strip()

        if number in raw_answers:
            raise RuntimeError(
                f"Trung dap an Viet cau {number}."
            )

        raw_answers[number] = value

    if set(raw_answers) != set(range(71, 81)):

        missing = sorted(
            set(range(71, 81))
            - set(raw_answers)
        )

        raise RuntimeError(
            f"Thieu dap an Viet: {missing}"
        )

    answers = {}
    alternatives = {}

    for number in range(71, 81):

        # Cau 75 co hai cach sap xep dung,
        # duoc ngan cach boi dau /.
        values = [
            value.strip()
            for value in raw_answers[number].split("/")
            if value.strip()
        ]

        expected = EXPECTED_WRITING[number]

        if len(values) != len(expected):
            raise RuntimeError(
                f"Cau {number} sai "
                "so luong dap an."
            )

        for actual, target in zip(
            values,
            expected
        ):

            if compact(actual) != compact(target):
                raise RuntimeError(
                    f"Sai dap an Viet cau {number}."
                    f"\nPDF: {actual}"
                    f"\nMau: {target}"
                )

        # Dap an dau tien la dap an chinh.
        answers[number] = values[0]

        # Giu cac dap an khac.
        if len(values) > 1:
            alternatives[str(number)] = values[1:]

    return answers, alternatives, raw_answers


# =====================================================
# 12. XAC DINH DANG CAU HOI
# =====================================================

def question_type(number):

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


def question_page(number):

    for page_no, numbers in (
        PAGE_QUESTIONS.items()
    ):

        if number in numbers:
            return page_no

    raise RuntimeError(
        f"Khong co trang cau {number}."
    )


# =====================================================
# 13. TACH HAI BANG HINH CAU 1-10
# =====================================================

def render_groups(doc):

    result = {}

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
                f"Toa do bang {name} sai."
            )

        found = set()

        for word in page.get_text("words"):

            x0, y0, _, _, value = word[:5]

            value = normalize(
                value
            ).strip()

            if (
                value in config["lua_chon"]
                and len(value) == 1
                and rect.contains(
                    fitz.Point(x0, y0)
                )
            ):
                found.add(value)

        expected = set(
            config["lua_chon"]
        )

        if found != expected:
            raise RuntimeError(
                f"Bang {name} thieu nhan."
                f"\nTim thay: {sorted(found)}"
            )

        pix = page.get_pixmap(
            matrix=fitz.Matrix(2.5, 2.5),
            clip=rect,
            alpha=False
        )

        result[name] = pix.tobytes("png")

        print(
            f"{name}: trang {page_no}, "
            f"{len(found)} lua chon"
        )

    return result


# =====================================================
# 14. TAO HTML XEM TRUOC
# =====================================================

def create_preview():

    blocks = []

    for first, last, group in [
        (1, 5, "nghe_01_05"),
        (6, 10, "nghe_06_10"),
    ]:

        numbers = "".join(
            f'<span class="number">Câu {n}</span>'
            for n in range(first, last + 1)
        )

        blocks.append(
            f"""
<section class="card">
    <h2>Câu {first}–{last}</h2>

    <img
        src="groups/{group}.png"
        alt="Bảng hình câu {first}-{last}"
    >

    <div class="numbers">
        {numbers}
    </div>
</section>
"""
        )

    html = """
<!DOCTYPE html>
<html lang="vi">

<head>
<meta charset="UTF-8">
<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>HSK3 Đề 4 - H31004</title>

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

.container {
    max-width: 1000px;
    margin: auto;
}

h1 {
    font-size: 25px;
}

p {
    color: #64748b;
    line-height: 1.6;
}

.card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px;
    margin-top: 20px;
}

.card h2 {
    font-size: 19px;
}

.card img {
    display: block;
    width: 100%;
    height: auto;
    object-fit: contain;
    max-width: 750px;
    margin: auto;
}

.numbers {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 20px;
}

.number {
    padding: 10px 14px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-weight: bold;
}
</style>

</head>

<body>
<div class="container">

<h1>HSK3 – Đề 4 (H31004)</h1>

<p>
Kiểm tra hai bảng hình câu 1–10.
Không hiển thị đáp án.
Chưa thay đổi SQL Server.
</p>

__BLOCKS__

</div>
</body>
</html>
"""

    return html.replace(
        "__BLOCKS__",
        "\n".join(blocks)
    ).encode("utf-8")


# =====================================================
# 15. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 04")
    print("BUOC 1 - H31004")
    print("=" * 60)

    pdf_file, mp3_file = find_source_files()

    print(f"PDF: {pdf_file.name}")

    if mp3_file:
        print(f"MP3: {mp3_file.name}")
    else:
        print(
            "Chua tim thay MP3. "
            "Van co the kiem tra PDF."
        )

    with fitz.open(pdf_file) as doc:

        check_pdf(doc)

        objective = extract_objective_answers(
            doc[20]
        )

        (
            writing,
            alternatives,
            raw_writing
        ) = extract_writing_answers(
            doc[21]
        )

        answers = {
            **objective,
            **writing
        }

        if set(answers) != set(range(1, 81)):
            raise RuntimeError(
                "Khong du 80 dap an."
            )

        print("\n===== DAP AN NGHE/DOC =====")

        for start in range(1, 71, 5):

            row = " ".join(
                answers[n]
                for n in range(
                    start,
                    start + 5
                )
            )

            print(
                f"{start:02d}-{start+4:02d}: {row}"
            )

        print("\n===== DAP AN VIET =====")

        for number in range(71, 81):
            print(
                f"{number}: {answers[number]}"
            )

        if alternatives:
            print(
                "\n===== DAP AN THAY THE ====="
            )

            for key, values in (
                alternatives.items()
            ):
                print(
                    f"Cau {key}: "
                    + " / ".join(values)
                )

        print("\nDoi chieu PDF: 80/80 KHOP")

        print("\n===== TACH BANG HINH =====")

        groups = render_groups(doc)

    # ================================================
    # 16. TAO DANH SACH 80 CAU
    # ================================================

    questions = []

    for number in range(1, 81):

        group = None

        if number <= 5:
            group = "nghe_01_05"

        elif number <= 10:
            group = "nghe_06_10"

        questions.append({
            "so_cau": number,

            "phan": question_section(number),

            "dang": question_type(number),

            "trang_pdf": question_page(number),

            "dap_an_dung": answers[number],

            "nhom_hinh": group,

            "da_duyet": False,
        })

    # ================================================
    # 17. TAO JSON DAP AN
    # ================================================

    result = {
        "cap_hsk": 3,
        "so_de": EXAM_NUMBER,
        "ma_de_goc": EXAM_CODE,

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

        "trang_loi_thoai": TRANSCRIPT_PAGES,

        "trang_dap_an": ANSWER_PAGES,

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

        # Giu lai dap an hop le thu hai
        # cua cau 75 de xu ly cham bai.
        "dap_an_thay_the": alternatives,

        "dap_an_pdf_nguyen_van": {
            str(number): raw_writing[number]
            for number in range(71, 81)
        },

        "cau_hoi": questions,
    }

    json_content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    html_content = create_preview()

    # ================================================
    # 18. CHUAN BI FILE DAU RA
    # ================================================

    outputs = {
        ANSWER_JSON: json_content,
        PREVIEW_HTML: html_content,
    }

    for name, content in groups.items():

        outputs[
            GROUP_DIR / f"{name}.png"
        ] = content

    # ================================================
    # 19. KHONG GHI DE FILE CU KHAC NOI DUNG
    # ================================================

    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):
            raise RuntimeError(
                "File da ton tai voi noi dung khac."
                "\nKhong ghi de:\n"
                + str(path)
            )

    # ================================================
    # 20. LUU JSON, HINH, HTML
    # ================================================

    for path, content in outputs.items():

        write_safe(path, content)

    # ================================================
    # 21. KET QUA
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH HSK3 DE 04 - BUOC 1")
    print("=" * 60)

    print("Ma de: H31004")
    print("PDF: 22 trang")

    print("Nghe: 40 cau")
    print("Doc: 30 cau")
    print("Viet: 10 cau")

    print("Dap an: 80/80")

    print("Bang hinh cau 1-5: 6 lua chon")
    print("Bang hinh cau 6-10: 5 lua chon")

    print("Cau 75: da giu 2 dap an hop le")

    print(f"\nJSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
