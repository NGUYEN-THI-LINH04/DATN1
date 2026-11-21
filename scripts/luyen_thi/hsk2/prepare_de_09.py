
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 9 (H21331)

BUOC 1:
- Doc PDF de thi 14 trang.
- Doc PDF dap an rieng 1 trang.
- Kiem tra ma de H21331.
- Doi chieu du 60 dap an.
- Tach 10 anh cau hoi dau tien.
- Tao HTML kiem tra 10 anh.
- Luu so do trang de tach tiep cau 11-60.

Khong thay doi SQL Server.
Khong sua cac de HSK1 va HSK2 De 1-8.
"""

from pathlib import Path
import importlib.util
import json
import re
import unicodedata
import html

import fitz


# =====================================================
# 1. CAU HINH DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

HSK2 = ROOT / "hsk2"

SOURCE = ROOT / "source" / "De_HSK" / "HSK2"

EXAM_CODE = "H21331"

PDF_NAMES = [
    "Đề HSK 2 số 9.pdf",
    "Đề HSK 2 số 9 (1).pdf",
]

ANSWER_NAMES = [
    "Đề HSK 2 số 9-answer-sheet.pdf",
    "Đề HSK 2 số 9_ dap_an.pdf",
    "Đề HSK 2 số 9 dap an.pdf",
]

AUDIO_NAMES = [
    "Đề HSK 2 số 9 file nghe.mp3",
    "Đề HSK 2 số 9.mp3",
    "Đề HSK 2 số 9 (1).mp3",
]

# Ham cat anh da su dung o cac de truoc.
HELPER_FILE = HSK2 / "prepare_de_02.py"

DATA = HSK2 / "data" / "de_09"

OUTPUT = HSK2 / "output" / "de_09"

QUESTIONS = OUTPUT / "questions"

ANSWER_JSON = DATA / "de_09_dap_an.json"

PREVIEW_HTML = OUTPUT / "kiem_tra_10_cau.html"


# =====================================================
# 2. SO DO TRANG PDF H21331
# =====================================================

PAGE_QUESTIONS = {
    2: list(range(1, 6)),
    3: list(range(6, 11)),
    4: list(range(11, 16)),
    5: list(range(16, 21)),
    6: list(range(21, 31)),
    7: list(range(31, 36)),

    # Trang 8 chi co footer, bo qua.

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
# 3. DAP AN GOC DE DOI CHIEU
# =====================================================

EXPECTED_ROWS = [
    "× × √ √ ×",
    "× × √ √ √",
    "C B E A F",
    "D B A C E",
    "B C B B A",
    "A B C A C",
    "C C A B A",
    "A B E C F",
    "B C D F A",
    "× √ × √ ×",
    "D C B A F",
    "D B E A C",
]


def build_expected_answers():

    answers = {}

    for row_index, row in enumerate(EXPECTED_ROWS):

        values = row.split()

        if len(values) != 5:
            raise RuntimeError(
                "Bang dap an doi chieu sai."
            )

        for index, answer in enumerate(values):

            number = row_index * 5 + index + 1
            answers[number] = answer

    if len(answers) != 60:
        raise RuntimeError(
            "Bang dap an doi chieu khong du 60 cau."
        )

    return answers


EXPECTED_ANSWERS = build_expected_answers()


# =====================================================
# 4. HAM CHUAN HOA CHUOI
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
        char for char in text
        if unicodedata.category(char) != "Mn"
    )

    return text.replace("đ", "d")


# =====================================================
# 5. TIM FILE NGUON
# =====================================================

def find_source(names, extension, category):

    if not SOURCE.is_dir():
        raise FileNotFoundError(SOURCE)

    # Tim theo dung ten truoc.
    for filename in names:

        path = SOURCE / filename

        if path.is_file():
            return path

    candidates = []

    pattern = re.compile(
        r"\bso\s*0?9(?!\d)"
    )

    for path in SOURCE.iterdir():

        if not path.is_file():
            continue

        if path.suffix.lower() != extension.lower():
            continue

        filename = normalize_filename(path.stem)

        if not pattern.search(filename):
            continue

        is_answer = (
            "answer" in filename
            or "dap_an" in filename
            or "dap an" in filename
        )

        if category == "answer" and not is_answer:
            continue

        if category == "exam" and is_answer:
            continue

        candidates.append(path)

    if len(candidates) == 1:
        return candidates[0]

    if not candidates:
        raise FileNotFoundError(
            f"Khong tim thay file {category} "
            f"De 9 trong:\n{SOURCE}"
        )

    raise RuntimeError(
        f"Co nhieu file {category}, "
        "khong tu chon nham:\n"
        + "\n".join(str(p) for p in candidates)
    )


def find_audio():

    try:
        return find_source(
            AUDIO_NAMES,
            ".mp3",
            "audio"
        )
    except FileNotFoundError:
        return None


# =====================================================
# 6. DOC MA DE PDF
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
            "Khong tim thay ma de duy nhat: "
            + str(sorted(codes))
        )

    return codes.pop()


# =====================================================
# 7. KIEM TRA DANG DAP AN
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
            f"Dap an cau {number} khong hop le: "
            f"{answer}"
        )


# =====================================================
# 8. DOC 60 DAP AN TU PDF RIENG
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

        if number < 1 or number > 60:
            continue

        if number in answers:
            raise RuntimeError(
                f"Trung dap an cau {number}."
            )

        validate_answer(number, answer)

        answers[number] = answer

    if set(answers) != set(range(1, 61)):

        missing = sorted(
            set(range(1, 61)) - set(answers)
        )

        raise RuntimeError(
            f"PDF dap an thieu cau: {missing}"
        )

    # Doi chieu voi bang dap an da kiem tra.
    for number in range(1, 61):

        actual = answers[number]
        expected = EXPECTED_ANSWERS[number]

        if actual != expected:
            raise RuntimeError(
                f"Cau {number} khong khop dap an "
                f"goc: PDF={actual}, "
                f"doi chieu={expected}"
            )

    return answers


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
            "H21331 phai co 14 trang."
        )

    cover_code = get_exam_code(doc[0])

    if cover_code != EXAM_CODE:
        raise RuntimeError(
            f"PDF khong phai H21331: {cover_code}"
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
                f"Trang PDF {page_no} "
                f"khong co nhom cau {first}-{last}."
            )

    # Trang 8 khong co cau hoi.
    page_8 = doc[7]

    for first, last in [
        (36, 40),
        (41, 45),
        (46, 50),
        (51, 55),
        (56, 60),
    ]:
        if has_heading(page_8, first, last):
            raise RuntimeError(
                "Trang 8 co cau hoi. "
                "Can kiem tra lai PDF."
            )

    print("\n===== BO CUC PDF =====")
    print("Ma de: H21331")
    print("PDF de thi: 14 trang")
    print("Trang 2-7: 35 cau Nghe")
    print("Trang 8: bo qua")
    print("Trang 9-14: 25 cau Doc")
    print("PDF dap an: file rieng")


# =====================================================
# 10. NAP HAM CAT ANH DA CO
# =====================================================

def load_helpers():

    if not HELPER_FILE.is_file():
        raise FileNotFoundError(HELPER_FILE)

    spec = importlib.util.spec_from_file_location(
        "hsk2_prepare_de02_helpers",
        HELPER_FILE
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "Khong nap duoc script tach anh De 2."
        )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    for name in [
        "get_question_positions",
        "get_crop_rect",
    ]:
        if not callable(
            getattr(module, name, None)
        ):
            raise RuntimeError(
                f"Script De 2 thieu ham {name}."
            )

    return module


# =====================================================
# 11. TAO HTML KIEM TRA 10 ANH
# =====================================================

def create_preview():

    cards = []

    for number in range(1, 11):

        cards.append(
            f"""
            <article class="card">
                <h3>Câu {number:02d}</h3>

                <img
                    src="questions/cau_{number:02d}.png"
                    alt="Câu {number}"
                >
            </article>
            """
        )

    content = """
<!DOCTYPE html>
<html lang="vi">

<head>
<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>HSK2 - Đề 9 (H21331)</title>

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
    max-width: 1100px;
    margin: 0 auto;
}

h1 {
    font-size: 26px;
    margin-bottom: 10px;
}

.note {
    color: #64748b;
    line-height: 1.6;
    margin-bottom: 24px;
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

.card h3 {
    margin: 0 0 14px;
    font-size: 18px;
}

.card img {
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

    <h1>HSK2 – Đề 9 (H21331)</h1>

    <p class="note">
        Kiểm tra 10 ảnh câu hỏi đầu tiên.
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

    content = content.replace(
        "__CARDS__",
        "\n".join(cards)
    )

    PREVIEW_HTML.write_text(
        content,
        encoding="utf-8"
    )


# =====================================================
# 12. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK2 DE 9")
    print("MA DE H21331")
    print("=" * 60)

    pdf_file = find_source(
        PDF_NAMES,
        ".pdf",
        "exam"
    )

    answer_pdf = find_source(
        ANSWER_NAMES,
        ".pdf",
        "answer"
    )

    mp3_file = find_audio()

    print(f"\nPDF de thi: {pdf_file.name}")
    print(f"PDF dap an: {answer_pdf.name}")

    if mp3_file:
        print(f"MP3: {mp3_file.name}")
    else:
        print(
            "CHUA CO MP3: can bo sung "
            "truoc khi chuan hoa/import SQL."
        )

    helpers = load_helpers()

    # ================================================
    # 13. DOC PDF DAP AN
    # ================================================

    with fitz.open(answer_pdf) as doc:

        if len(doc) != 1:
            raise RuntimeError(
                "PDF dap an phai co 1 trang."
            )

        code = get_exam_code(doc[0])

        if code != EXAM_CODE:
            raise RuntimeError(
                f"PDF dap an sai ma de: {code}"
            )

        answers = extract_answers(doc[0])

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

    print("\nDoi chieu PDF dap an: 60/60 KHOP")

    # ================================================
    # 14. TACH 10 ANH DAU
    # ================================================

    # Kiem tra PDF truoc khi tao anh.
    with fitz.open(pdf_file) as doc:

        check_exam_pdf(doc)

        DATA.mkdir(
            parents=True,
            exist_ok=True
        )

        QUESTIONS.mkdir(
            parents=True,
            exist_ok=True
        )

        print("\n===== TACH ANH CAU 1-10 =====")

        first_pages = {
            2: list(range(1, 6)),
            3: list(range(6, 11)),
        }

        for page_no, numbers in first_pages.items():

            page = doc[page_no - 1]

            positions = (
                helpers.get_question_positions(
                    page,
                    numbers
                )
            )

            for index, number in enumerate(numbers):

                rect = helpers.get_crop_rect(
                    page,
                    numbers,
                    positions,
                    index
                )

                if not isinstance(rect, fitz.Rect):
                    rect = fitz.Rect(rect)

                rect = rect & page.rect

                if rect.is_empty:
                    raise RuntimeError(
                        f"Vung cat anh cau {number} "
                        "khong hop le."
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
    # 15. LUU JSON DAP AN
    # ================================================

    result = {
        "cap_hsk": 2,
        "so_de": 9,
        "ma_de_goc": EXAM_CODE,

        "file_pdf": str(pdf_file),
        "file_dap_an": str(answer_pdf),
        "file_mp3": (
            str(mp3_file) if mp3_file else None
        ),

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
    # 16. KET QUA
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH BUOC 1")
    print("=" * 60)

    print("Ma de: H21331")
    print("PDF de thi: 14 trang")
    print("PDF dap an: 1 trang rieng")
    print("Trang 8: da bo qua")
    print("Dap an: 60/60")
    print("Anh cau hoi: 10/60")

    print(f"JSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    if not mp3_file:
        print(
            "\nLUU Y: Chua co MP3 De 9. "
            "Can bo sung truoc khi nhap SQL."
        )

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
