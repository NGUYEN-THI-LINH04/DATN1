
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 11 (H21335)

BUOC 1:
- Doc PDF 19 trang.
- Doc ma de H21335.
- Lay bang dap an o trang 19.
- Doi chieu 60 dap an chinh thuc.
- Tach anh cau 1-10.
- Tao HTML kiem tra 10 cau.
- Luu so do trang cho buoc tach cau 11-60.

Bo cuc:
  Trang 1: Bia
  Trang 2-7: Nghe, cau 1-35
  Trang 8: Bo qua
  Trang 9-14: Doc, cau 36-60
  Trang 15-18: Loi thoai phan Nghe
  Trang 19: Dap an

KHONG thay doi SQL Server.
KHONG sua cac de da hoan thanh.
"""

from pathlib import Path
import importlib.util
import json
import re
import unicodedata

import fitz


# =====================================================
# 1. CAU HINH DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

HSK2 = ROOT / "hsk2"

SOURCE = ROOT / "source" / "De_HSK" / "HSK2"

PDF_FILE = SOURCE / "Đề HSK 2 số 11.pdf"

EXAM_CODE = "H21335"
EXAM_NUMBER = 11

HELPER_FILE = HSK2 / "prepare_de_02.py"

DATA = HSK2 / "data" / "de_11"

OUTPUT = HSK2 / "output" / "de_11"

QUESTIONS = OUTPUT / "questions"

ANSWER_JSON = DATA / "de_11_dap_an.json"

PREVIEW_HTML = OUTPUT / "kiem_tra_10_cau.html"


# =====================================================
# 2. SO DO TRANG PDF
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

TRANSCRIPT_PAGES = [15, 16, 17, 18]

ANSWER_PAGE = 19


# =====================================================
# 3. DAP AN CHINH THUC H21335
# =====================================================

EXPECTED_ROWS = [
    "√ × × √ ×",
    "√ √ √ × ×",
    "B E F A C",
    "A C D B E",
    "A A C B A",
    "C B A C B",
    "B B C C A",
    "F A E B C",
    "C D A F B",
    "× √ × √ ×",
    "F C B A D",
    "E D A B C",
]


def build_expected_answers():

    result = {}

    for row_index, row in enumerate(EXPECTED_ROWS):

        values = row.split()

        if len(values) != 5:
            raise RuntimeError(
                "Bang dap an goc sai dinh dang."
            )

        for offset, answer in enumerate(values):

            number = row_index * 5 + offset + 1
            result[number] = answer

    if set(result) != set(range(1, 61)):
        raise RuntimeError(
            "Bang dap an goc khong du 60 cau."
        )

    return result


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

    value = normalize(text).upper()

    return re.sub(
        r"[^A-Z0-9]",
        "",
        value
    )


def normalize_filename(text):

    value = unicodedata.normalize(
        "NFD",
        str(text)
    ).lower()

    value = "".join(
        char for char in value
        if unicodedata.category(char) != "Mn"
    )

    return value.replace("đ", "d")


# =====================================================
# 5. TIM FILE MP3 DE 11
# =====================================================

def find_audio():

    names = [
        "Đề HSK 2 số 11.mp3",
        "Đề HSK 2 số 11 file nghe.mp3",
        "Đề HSK 2 số 11 (1).mp3",
    ]

    for name in names:

        path = SOURCE / name

        if path.is_file():
            return path

    candidates = []

    if SOURCE.is_dir():

        for path in SOURCE.glob("*.mp3"):

            name = normalize_filename(path.stem)

            if re.search(
                r"\bso\s*0?11(?!\d)",
                name
            ):
                candidates.append(path)

    if len(candidates) == 1:
        return candidates[0]

    if len(candidates) > 1:
        raise RuntimeError(
            "Tim thay nhieu MP3 De 11.\n"
            "Can kiem tra de tranh chon nham:\n"
            + "\n".join(
                str(path) for path in candidates
            )
        )

    # Chua co MP3 van duoc tach anh.
    return None


# =====================================================
# 6. DOC MA DE
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
            "Khong xac dinh duoc ma de: "
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
# 8. DOC 60 DAP AN TU TRANG 19
# =====================================================

def extract_answers(page):

    text = normalize(
        page.get_text("text")
    )

    if "答案" not in text:
        raise RuntimeError(
            "Trang 19 khong co bang 答案."
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
                f"Trung dap an cau {number}."
            )

        validate_answer(number, answer)

        answers[number] = answer

    expected_numbers = set(range(1, 61))

    if set(answers) != expected_numbers:

        missing = sorted(
            expected_numbers - set(answers)
        )

        raise RuntimeError(
            f"Trang 19 chua du 60 dap an. "
            f"Thieu: {missing}"
        )

    # Doi chieu voi bang dap an H21335.
    for number in range(1, 61):

        actual = answers[number]
        expected = EXPECTED_ANSWERS[number]

        if actual != expected:
            raise RuntimeError(
                f"Cau {number} khong khop: "
                f"PDF={actual}, "
                f"doi_chieu={expected}"
            )

    return answers


# =====================================================
# 9. KIEM TRA TIEU DE NHOM CAU
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


# =====================================================
# 10. KIEM TRA BO CUC PDF
# =====================================================

def check_exam_pdf(doc):

    if len(doc) != 19:
        raise RuntimeError(
            f"PDF co {len(doc)} trang. "
            "H21335 phai co 19 trang."
        )

    cover_code = get_exam_code(doc[0])

    if cover_code != EXAM_CODE:
        raise RuntimeError(
            f"Trang bia sai ma de: {cover_code}"
        )

    answer_code = get_exam_code(
        doc[ANSWER_PAGE - 1]
    )

    if answer_code != EXAM_CODE:
        raise RuntimeError(
            "Ma de trang 19 khong khop "
            "trang bia."
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

        if not has_heading(
            doc[page_no - 1],
            first,
            last
        ):
            raise RuntimeError(
                f"Trang {page_no} khong co "
                f"nhom cau {first}-{last}."
            )

    # Trang 8 khong co cau hoi.
    for first, last in [
        (36, 40),
        (41, 45),
        (46, 50),
        (51, 55),
        (56, 60),
    ]:

        if has_heading(
            doc[7],
            first,
            last
        ):
            raise RuntimeError(
                "Trang 8 co cau hoi. "
                "Bo cuc PDF khong dung."
            )

    # Trang 15 la dau phan loi thoai nghe.
    transcript_text = normalize(
        doc[14].get_text("text")
    )

    if "听力材料" not in transcript_text:
        raise RuntimeError(
            "Trang 15 khong phai "
            "phan loi thoai nghe."
        )

    # Trang 19 phai la bang dap an.
    answer_text = normalize(
        doc[18].get_text("text")
    )

    if "答案" not in answer_text:
        raise RuntimeError(
            "Trang 19 khong phai bang dap an."
        )

    print("\n===== BO CUC PDF =====")
    print("Ma de: H21335")
    print("PDF: 19 trang")
    print("Trang 2-7: cau 1-35")
    print("Trang 8: bo qua")
    print("Trang 9-14: cau 36-60")
    print("Trang 15-18: loi thoai nghe")
    print("Trang 19: dap an")


# =====================================================
# 11. NAP HAM CAT ANH DA CO
# =====================================================

def load_helpers():

    if not HELPER_FILE.is_file():
        raise FileNotFoundError(
            HELPER_FILE
        )

    spec = importlib.util.spec_from_file_location(
        "hsk2_prepare_de02_helpers",
        HELPER_FILE
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "Khong nap duoc script De 2."
        )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    for name in (
        "get_question_positions",
        "get_crop_rect",
    ):

        if not callable(
            getattr(module, name, None)
        ):
            raise RuntimeError(
                f"Script mau thieu ham: {name}"
            )

    return module


# =====================================================
# 12. TAO HTML KIEM TRA 10 CAU
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

<title>HSK2 - Đề 11 (H21335)</title>

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
    margin: auto;
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

    <h1>HSK2 – Đề 11 (H21335)</h1>

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

    content = content.replace(
        "__CARDS__",
        "\n".join(cards)
    )

    PREVIEW_HTML.write_text(
        content,
        encoding="utf-8"
    )


# =====================================================
# 13. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK2 DE 11")
    print("MA DE H21335")
    print("=" * 60)

    if not PDF_FILE.is_file():
        raise FileNotFoundError(
            "Khong tim thay PDF De 11:\n"
            + str(PDF_FILE)
        )

    mp3_file = find_audio()

    print(f"\nPDF: {PDF_FILE.name}")

    if mp3_file:
        print(f"MP3: {mp3_file.name}")
    else:
        print(
            "Chua tim thay MP3 De 11. "
            "Van co the tach anh."
        )

    helpers = load_helpers()

    with fitz.open(PDF_FILE) as doc:

        # ============================================
        # 14. KIEM TRA PDF
        # ============================================

        check_exam_pdf(doc)

        # ============================================
        # 15. LAY 60 DAP AN O TRANG 19
        # ============================================

        answers = extract_answers(
            doc[ANSWER_PAGE - 1]
        )

        print("\n===== 60 DAP AN =====")

        for start in range(1, 61, 5):

            row = [
                answers[number]
                for number in range(
                    start,
                    start + 5
                )
            ]

            print(
                f"{start:02d}-{start+4:02d}: "
                + " ".join(row)
            )

        print(
            "\nDoi chieu trang 19: 60/60 KHOP"
        )

        # ============================================
        # 16. TACH 10 ANH DAU
        # ============================================

        DATA.mkdir(
            parents=True,
            exist_ok=True
        )

        QUESTIONS.mkdir(
            parents=True,
            exist_ok=True
        )

        first_pages = {
            2: list(range(1, 6)),
            3: list(range(6, 11)),
        }

        print("\n===== TACH ANH CAU 1-10 =====")

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

                rect = (
                    fitz.Rect(rect) & page.rect
                )

                if (
                    rect.is_empty
                    or rect.width < 10
                    or rect.height < 8
                ):
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
    # 17. LUU JSON DAP AN
    # ================================================

    result = {
        "cap_hsk": 2,
        "so_de": EXAM_NUMBER,
        "ma_de_goc": EXAM_CODE,

        "file_pdf": str(PDF_FILE),
        "file_mp3": (
            str(mp3_file) if mp3_file else None
        ),

        "nguon_dap_an": "pdf_chung",
        "so_trang_pdf_de": 19,
        "trang_dap_an": 19,

        "tong_cau": 60,
        "so_cau_nghe": 35,
        "so_cau_doc": 25,

        "trang_bo_qua": [
            1, 8, 15, 16, 17, 18
        ],

        "trang_loi_thoai": TRANSCRIPT_PAGES,

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
            str(number): answers[number]
            for number in range(1, 61)
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
    # 18. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH BUOC 1")
    print("=" * 60)

    print("Ma de: H21335")
    print("PDF: 19 trang")
    print("Trang 8: da bo qua")
    print("Loi thoai nghe: trang 15-18")
    print("Trang dap an: 19")
    print("Dap an: 60/60")
    print("Anh cau hoi: 10/60")

    print(f"JSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    if not mp3_file:
        print(
            "\nLUU Y: Can bo sung MP3 H21335 "
            "truoc khi nhap SQL."
        )

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
