
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 8 (H21330)

BUOC 1:
- Doc PDF de thi 14 trang.
- Doc PDF dap an rieng 1 trang.
- Kiem tra ma de H21330.
- Lay 60 dap an that.
- Tach anh cau 1-10.
- Tao HTML kiem tra 10 cau.
- Luu so do trang PDF cho buoc tach cau 11-60.

Khong thay doi SQL Server.
Khong sua HSK1 va HSK2 De 1-7.
"""

from pathlib import Path
import importlib.util
import json
import re
import unicodedata
import html

import fitz


# =====================================================
# 1. CAU HINH
# =====================================================

ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

HSK2 = ROOT / "hsk2"

SOURCE = ROOT / "source" / "De_HSK" / "HSK2"

EXAM_CODE = "H21330"

# Ten file dung theo PDF da kiem tra.
PDF_NAMES = [
    "Đề HSK 2 số 8 (1).pdf",
    "Đề HSK 2 số 8.pdf",
]

ANSWER_NAMES = [
    "Đề HSK 2 số 8-answer-sheet.pdf",
    "Đề HSK 2 số 8_ dap_an.pdf",
    "Đề HSK 2 số 8 dap an.pdf",
]

AUDIO_NAMES = [
    "Đề HSK 2 số 8 (1).mp3",
    "Đề HSK 2 số 8.mp3",
    "Đề HSK 2 số 8 file nghe.mp3",
]

# Dung lai ham cat anh da chay thanh cong.
TEMPLATE = HSK2 / "prepare_de_02.py"

DATA = HSK2 / "data" / "de_08"

OUTPUT = HSK2 / "output" / "de_08"

QUESTIONS = OUTPUT / "questions"

ANSWER_JSON = DATA / "de_08_dap_an.json"

PREVIEW_HTML = OUTPUT / "kiem_tra_10_cau.html"


# =====================================================
# 2. SO DO TRANG PDF CHINH XAC
# =====================================================

PAGE_QUESTIONS = {
    2: list(range(1, 6)),
    3: list(range(6, 11)),

    4: list(range(11, 16)),
    5: list(range(16, 21)),

    6: list(range(21, 31)),
    7: list(range(31, 36)),

    # Trang 8 khong co cau hoi.

    9: list(range(36, 41)),
    10: list(range(41, 46)),

    11: [46, 47, 48],
    12: [49, 50],

    13: list(range(51, 56)),
    14: list(range(56, 61)),
}

GROUP_PAGES = {
    "nghe_11_15": 4,
    "nghe_16_20": 5,

    "doc_36_40": 9,
    "doc_41_45": 10,

    "doc_51_55": 13,
    "doc_56_60": 14,
}


# =====================================================
# 3. HAM CHUAN HOA CHUOI
# =====================================================

def normalize(text):
    return unicodedata.normalize(
        "NFKC",
        str(text)
    )


def normalize_code(text):
    text = normalize(text).upper()

    return re.sub(
        r"[^A-Z0-9]",
        "",
        text
    )


def normalize_filename(text):
    text = unicodedata.normalize(
        "NFD",
        str(text)
    ).lower()

    text = "".join(
        ch for ch in text
        if unicodedata.category(ch) != "Mn"
    )

    return text.replace("đ", "d")


# =====================================================
# 4. TIM FILE NGUON
# =====================================================

def find_source_file(names, extension, is_answer=False):

    if not SOURCE.is_dir():
        raise FileNotFoundError(SOURCE)

    # Uu tien dung ten file da biet.
    for filename in names:

        path = SOURCE / filename

        if path.is_file():
            return path

    # Neu ten khac, tim theo "so 8".
    candidates = []

    pattern = re.compile(
        r"\bso\s*0?8(?!\d)"
    )

    for path in SOURCE.iterdir():

        if not path.is_file():
            continue

        if path.suffix.lower() != extension.lower():
            continue

        filename = normalize_filename(path.stem)

        if not pattern.search(filename):
            continue

        answer_like = (
            "dap_an" in filename
            or "dap an" in filename
            or "answer" in filename
        )

        if extension.lower() == ".pdf":
            if answer_like != is_answer:
                continue

        candidates.append(path)

    if len(candidates) == 1:
        return candidates[0]

    if not candidates:
        raise FileNotFoundError(
            f"Khong tim thay file {extension} De 8 "
            f"(dap an: {is_answer}) trong:\n{SOURCE}"
        )

    raise RuntimeError(
        "Co nhieu file trung dieu kien, "
        "khong tu chon nham:\n"
        + "\n".join(
            str(path) for path in candidates
        )
    )


# =====================================================
# 5. DOC MA DE TRONG PDF
# =====================================================

def get_exam_code(page):

    text = normalize_code(
        page.get_text("text")
    )

    codes = set(
        re.findall(
            r"H2\d{4}",
            text
        )
    )

    if len(codes) != 1:
        raise RuntimeError(
            "Khong xac dinh duoc ma de duy nhat: "
            + str(sorted(codes))
        )

    return codes.pop()


# =====================================================
# 6. KIEM TRA DANG DAP AN
# =====================================================

def validate_answer(number, answer):

    if number <= 10 or 46 <= number <= 50:
        allowed = {"√", "×"}

    elif 21 <= number <= 35:
        allowed = set("ABC")

    elif 16 <= number <= 20 or 56 <= number <= 60:
        allowed = set("ABCDE")

    else:
        allowed = set("ABCDEF")

    if answer not in allowed:
        raise RuntimeError(
            f"Cau {number} co dap an sai dang: "
            f"{answer}"
        )


# =====================================================
# 7. DOC 60 DAP AN TU PDF RIENG
# =====================================================

def extract_answers(page):

    text = normalize(
        page.get_text("text")
    )

    if "答案" not in text:
        raise RuntimeError(
            "PDF dap an khong co tieu de 答案."
        )

    pattern = re.compile(
        r"(?<!\d)(\d{1,2})\s*[.、]\s*([A-F√×])"
    )

    answers = {}

    for match in pattern.finditer(text):

        number = int(match.group(1))
        answer = match.group(2)

        if not 1 <= number <= 60:
            continue

        if number in answers:
            raise RuntimeError(
                f"Trung dap an cau {number}"
            )

        validate_answer(number, answer)

        answers[number] = answer

    expected = set(range(1, 61))

    if set(answers) != expected:

        missing = sorted(
            expected - set(answers)
        )

        raise RuntimeError(
            f"Khong doc du 60 dap an. "
            f"Cac cau thieu: {missing}"
        )

    return answers


# =====================================================
# 8. NAP HAM TACH ANH DA HOAT DONG
# =====================================================

def load_helpers():

    if not TEMPLATE.is_file():
        raise FileNotFoundError(TEMPLATE)

    spec = importlib.util.spec_from_file_location(
        "hsk2_de02_helpers",
        TEMPLATE
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "Khong the nap script De 2."
        )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    for name in (
        "get_question_positions",
        "get_crop_rect"
    ):
        if not callable(
            getattr(module, name, None)
        ):
            raise RuntimeError(
                f"Script De 2 thieu ham {name}"
            )

    return module


# =====================================================
# 9. KIEM TRA BO CUC PDF
# =====================================================

def has_heading(page, first, last):

    text = normalize(
        page.get_text("text")
    )

    pattern = (
        rf"第\s*{first}\s*[-–—]\s*"
        rf"{last}\s*题"
    )

    return bool(
        re.search(pattern, text)
    )


def check_exam_pdf(doc):

    if len(doc) != 14:
        raise RuntimeError(
            f"PDF co {len(doc)} trang, "
            "De 8 H21330 phai co 14 trang."
        )

    cover_code = get_exam_code(doc[0])

    if cover_code != EXAM_CODE:
        raise RuntimeError(
            f"PDF khong phai H21330: {cover_code}"
        )

    checks = [
        (2, 1, 10),
        (4, 11, 15),
        (5, 16, 20),
        (6, 21, 30),
        (7, 31, 35),
        (9, 36, 40),
        (10, 41, 45),
        (11, 46, 50),
        (13, 51, 55),
        (14, 56, 60),
    ]

    for page_no, first, last in checks:

        page = doc[page_no - 1]

        if not has_heading(page, first, last):
            raise RuntimeError(
                f"Trang {page_no} khong co "
                f"tieu de cau {first}-{last}."
            )

    # Trang 8 chi co footer, khong co cau hoi.
    page_8 = doc[7]

    if any(
        has_heading(page_8, first, last)
        for first, last in [
            (36, 40),
            (41, 45),
            (46, 50),
            (51, 55),
            (56, 60),
        ]
    ):
        raise RuntimeError(
            "Trang 8 co cau hoi, "
            "can kiem tra lai bo cuc."
        )

    print("\n===== BO CUC PDF =====")
    print("PDF de thi: 14 trang")
    print("Ma de: H21330")
    print("Trang 2-7: 35 cau Nghe")
    print("Trang 8: bo qua")
    print("Trang 9-14: 25 cau Doc")
    print("PDF dap an: file rieng")


# =====================================================
# 10. TAO HTML KIEM TRA 10 ANH
# =====================================================

def create_preview():

    cards = []

    for number in range(1, 11):

        cards.append(
            f"""
            <div class="card">
                <h3>Câu {number:02d}</h3>

                <img
                    src="questions/cau_{number:02d}.png"
                    alt="Câu {number}"
                >
            </div>
            """
        )

    title = html.escape(
        "HSK2 - Đề 8 (H21330)"
    )

    content = """
<!DOCTYPE html>
<html lang="vi">

<head>
<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>__TITLE__</title>

<style>
    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        padding: 24px;
        font-family: Arial, sans-serif;
        color: #1e293b;
        background: #f3f5f9;
    }

    .container {
        max-width: 1100px;
        margin: auto;
    }

    h1 {
        font-size: 26px;
        margin-bottom: 10px;
    }

    .note {
        color: #64748b;
        margin-bottom: 24px;
        line-height: 1.6;
    }

    .grid {
        display: grid;
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
        gap: 18px;
    }

    .card {
        padding: 18px;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
    }

    h3 {
        margin: 0 0 14px;
        font-size: 18px;
    }

    img {
        display: block;
        width: 100%;
        height: auto;
        object-fit: contain;
    }

    @media (max-width: 750px) {
        .grid {
            grid-template-columns: 1fr;
        }
    }
</style>
</head>

<body>

<div class="container">

    <h1>__TITLE__</h1>

    <p class="note">
        Kiểm tra 10 ảnh đầu tiên.
        Không hiển thị đáp án.
        Chưa thay đổi SQL Server.
    </p>

    <div class="grid">
        __CARDS__
    </div>

</div>

</body>
</html>
"""

    content = (
        content
        .replace("__TITLE__", title)
        .replace("__CARDS__", "\n".join(cards))
    )

    PREVIEW_HTML.write_text(
        content,
        encoding="utf-8"
    )


# =====================================================
# 11. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK2 DE 8")
    print("MA DE H21330")
    print("=" * 60)

    pdf_file = find_source_file(
        PDF_NAMES,
        ".pdf",
        is_answer=False
    )

    answer_pdf = find_source_file(
        ANSWER_NAMES,
        ".pdf",
        is_answer=True
    )

    mp3_file = find_source_file(
        AUDIO_NAMES,
        ".mp3"
    )

    if not TEMPLATE.is_file():
        raise FileNotFoundError(TEMPLATE)

    print(f"\nPDF de thi: {pdf_file.name}")
    print(f"PDF dap an: {answer_pdf.name}")
    print(f"MP3: {mp3_file.name}")

    helpers = load_helpers()

    # ================================================
    # 12. DOC PDF DAP AN RIENG
    # ================================================

    with fitz.open(answer_pdf) as answer_doc:

        if len(answer_doc) != 1:
            raise RuntimeError(
                "PDF dap an phai co 1 trang."
            )

        answer_code = get_exam_code(
            answer_doc[0]
        )

        print(
            "\nMa de PDF dap an:",
            answer_code
        )

        if answer_code != EXAM_CODE:
            raise RuntimeError(
                "PDF dap an khong phai H21330."
            )

        answers = extract_answers(
            answer_doc[0]
        )

    print("\n===== 60 DAP AN =====")

    for start in range(1, 61, 5):

        row = [
            answers[n]
            for n in range(start, start + 5)
        ]

        print(
            f"{start:02d}-{start + 4:02d}: "
            + " ".join(row)
        )

    # ================================================
    # 13. KIEM TRA PDF VA TACH 10 ANH
    # ================================================

    DATA.mkdir(
        parents=True,
        exist_ok=True
    )

    QUESTIONS.mkdir(
        parents=True,
        exist_ok=True
    )

    with fitz.open(pdf_file) as doc:

        check_exam_pdf(doc)

        print("\n===== TACH CAU 1-10 =====")

        first_pages = {
            2: list(range(1, 6)),
            3: list(range(6, 11)),
        }

        for page_no, numbers in first_pages.items():

            page = doc[page_no - 1]

            positions = helpers.get_question_positions(
                page,
                numbers
            )

            for index, number in enumerate(numbers):

                rect = helpers.get_crop_rect(
                    page,
                    numbers,
                    positions,
                    index
                )

                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2.5, 2.5),
                    clip=rect,
                    alpha=False
                )

                destination = (
                    QUESTIONS
                    / f"cau_{number:02d}.png"
                )

                pix.save(str(destination))

                print(
                    f"Cau {number:02d}: "
                    f"trang PDF {page_no}"
                )

    # ================================================
    # 14. LUU JSON DAP AN
    # ================================================

    result = {
        "cap_hsk": 2,
        "so_de": 8,
        "ma_de_goc": EXAM_CODE,

        "file_pdf": str(pdf_file),
        "file_dap_an": str(answer_pdf),
        "file_mp3": str(mp3_file),

        "nguon_dap_an": "pdf_rieng",

        "so_trang_pdf_de": 14,
        "trang_dap_an": 1,

        "tong_cau": 60,
        "so_cau_nghe": 35,
        "so_cau_doc": 25,

        "trang_bo_qua": [1, 8],

        "trang_cau_hoi": sorted(
            PAGE_QUESTIONS.keys()
        ),

        "bang_trang_cau_hoi": {
            str(page_no): numbers
            for page_no, numbers
            in PAGE_QUESTIONS.items()
        },

        "bang_trang_lua_chon": GROUP_PAGES,

        "dap_an": {
            str(n): answers[n]
            for n in range(1, 61)
        }
    }

    ANSWER_JSON.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    create_preview()

    # ================================================
    # 15. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH BUOC 1")
    print("=" * 60)

    print("Ma de: H21330")
    print("PDF de thi: 14 trang")
    print("PDF dap an: 1 trang rieng")
    print("Trang 8: bo qua")
    print("Dap an: 60/60")
    print("Anh cau hoi: 10/60")

    print(f"JSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
