
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 7 (H21329)

BUOC 1:
- Doc PDF de thi 14 trang.
- Doc PDF dap an rieng 1 trang.
- Kiem tra ma de H21329 trong ca hai PDF.
- Lay dung 60 dap an.
- Tach 10 anh cau hoi dau tien.
- Tao HTML kiem tra 10 anh.
- Luu thong tin trang de tach 50 cau con lai.

KHONG thay doi SQL Server.
KHONG sua cac de da hoan thanh.
"""

from pathlib import Path
import importlib.util
import json
import re
import unicodedata
import html

import fitz


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

HSK2 = ROOT / "hsk2"

SOURCE = ROOT / "source" / "De_HSK" / "HSK2"

PDF_FILE = SOURCE / "Đề HSK 2 số 7.pdf"

ANSWER_PDF = SOURCE / "Đề HSK 2 số 7_ dap_an.pdf"

MP3_FILE = SOURCE / "Đề HSK 2 số 7 file nghe.mp3"

# Dung lai ham tach anh da chay tot o De 2.
TEMPLATE = HSK2 / "prepare_de_02.py"

DATA = HSK2 / "data" / "de_07"

OUTPUT = HSK2 / "output" / "de_07"

QUESTIONS = OUTPUT / "questions"

ANSWER_JSON = DATA / "de_07_dap_an.json"

PREVIEW_HTML = OUTPUT / "kiem_tra_10_cau.html"

EXAM_CODE = "H21329"


# =====================================================
# 2. BANG TRANG PDF CHINH XAC
# =====================================================

PAGE_QUESTIONS = {
    2: list(range(1, 6)),
    3: list(range(6, 11)),
    4: list(range(11, 16)),
    5: list(range(16, 21)),
    6: list(range(21, 31)),
    7: list(range(31, 36)),
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
# 3. HAM XU LY CHUNG
# =====================================================

def normalize_code(value):

    text = unicodedata.normalize(
        "NFKC",
        str(value)
    ).upper()

    return re.sub(
        r"[^A-Z0-9]",
        "",
        text
    )


def normalize_filename(value):

    text = unicodedata.normalize(
        "NFD",
        str(value)
    ).lower()

    text = "".join(
        ch for ch in text
        if unicodedata.category(ch) != "Mn"
    )

    return text.replace("đ", "d")


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
# 4. TIM PDF DAP AN RIENG
# =====================================================

def find_answer_pdf():

    # Uu tien ten file nguoi dung da cung cap.
    if ANSWER_PDF.is_file():
        return ANSWER_PDF

    candidates = []

    for path in SOURCE.glob("*.pdf"):

        if path == PDF_FILE:
            continue

        name = normalize_filename(path.stem)

        # Vi du:
        # De HSK 2 so 7_ dap_an
        # De HSK 2 so 7 dap an
        # H21329 dap an
        is_exam_7 = bool(
            re.search(
                r"so\s*0?7(?!\d)",
                name
            )
        ) or "h21329" in name

        is_answer = (
            "dap" in name
            and "an" in name
        ) or "answer" in name

        if is_exam_7 and is_answer:
            candidates.append(path)

    if len(candidates) == 1:
        return candidates[0]

    if not candidates:
        raise FileNotFoundError(
            "Khong tim thay PDF dap an De 7.\n"
            "Hay dat file "
            "'Đề HSK 2 số 7_ dap_an.pdf' "
            f"vao thu muc:\n{SOURCE}"
        )

    raise RuntimeError(
        "Tim thay nhieu PDF dap an De 7:\n"
        + "\n".join(
            str(path) for path in candidates
        )
    )


# =====================================================
# 5. LAY 60 DAP AN TU PDF RIENG
# =====================================================

def extract_answers(page):

    text = unicodedata.normalize(
        "NFKC",
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
                f"Trung dap an cau {number}"
            )

        answers[number] = answer

    expected = set(range(1, 61))

    if set(answers) != expected:

        missing = sorted(
            expected - set(answers)
        )

        raise RuntimeError(
            f"PDF dap an thieu cau: {missing}"
        )

    # Kiem tra kieu dap an theo tung phan.
    for number, answer in answers.items():

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
                f"Dap an cau {number} "
                f"khong hop le: {answer}"
            )

    return answers


# =====================================================
# 6. NAP HAM TACH ANH DA HOAT DONG
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
            "Khong nap duoc script De 2."
        )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    required_functions = [
        "get_question_positions",
        "get_crop_rect",
    ]

    for name in required_functions:

        if not callable(
            getattr(module, name, None)
        ):
            raise RuntimeError(
                f"Script De 2 thieu ham: {name}"
            )

    return module


# =====================================================
# 7. KIEM TRA BO CUC DE THI
# =====================================================

def check_exam_pdf(doc):

    if len(doc) != 14:
        raise RuntimeError(
            f"PDF De 7 co {len(doc)} trang. "
            "Du kien 14 trang."
        )

    cover_code = get_exam_code(doc[0])

    print("Ma de trang bia:", cover_code)

    if cover_code != EXAM_CODE:
        raise RuntimeError(
            f"PDF khong phai {EXAM_CODE}."
        )

    # Kiem tra nhom cau cuoi nam o trang 14.
    last_page_text = doc[13].get_text("text")

    if not re.search(
        r"第\s*56\s*[-–]\s*60\s*题",
        last_page_text
    ):
        raise RuntimeError(
            "Trang 14 khong chua nhom cau 56-60."
        )

    # Trang 8 khong duoc su dung lam trang cau hoi.
    page_8_text = doc[7].get_text("text")

    if re.search(
        r"第\s*(?:36|41|46|51|56)\s*[-–]",
        page_8_text
    ):
        raise RuntimeError(
            "Trang 8 co noi dung cau hoi, "
            "can kiem tra lai bo cuc."
        )

    print("PDF de thi: 14 trang")
    print("Trang Nghe: 2-7")
    print("Trang 8: bo qua")
    print("Trang Doc: 9-14")


# =====================================================
# 8. TAO HTML KIEM TRA 10 CAU
# =====================================================

def create_preview():

    cards = []

    for number in range(1, 11):

        filename = f"cau_{number:02d}.png"

        cards.append(
            f"""
            <div class="card">
                <h3>Câu {number:02d}</h3>

                <img
                    src="questions/{filename}"
                    alt="Câu {number}"
                >
            </div>
            """
        )

    title = html.escape(
        f"HSK2 - Đề 7 ({EXAM_CODE})"
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
            color: #202938;
            background: #f3f5f9;
        }

        .container {
            max-width: 1100px;
            margin: 0 auto;
        }

        h1 {
            font-size: 25px;
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
# 9. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK2 DE 7")
    print("MA DE H21329")
    print("=" * 60)

    if not PDF_FILE.is_file():
        raise FileNotFoundError(PDF_FILE)

    if not MP3_FILE.is_file():
        raise FileNotFoundError(MP3_FILE)

    answer_pdf = find_answer_pdf()

    print(f"\nPDF de thi: {PDF_FILE.name}")
    print(f"PDF dap an: {answer_pdf.name}")
    print(f"MP3: {MP3_FILE.name}")

    helpers = load_helpers()

    # ================================================
    # 10. DOC PDF DAP AN RIENG
    # ================================================

    with fitz.open(answer_pdf) as answer_doc:

        print(
            f"\nPDF dap an co {len(answer_doc)} trang"
        )

        if len(answer_doc) != 1:
            raise RuntimeError(
                "PDF dap an De 7 phai co 1 trang."
            )

        answer_code = get_exam_code(
            answer_doc[0]
        )

        print(
            "Ma de trong PDF dap an:",
            answer_code
        )

        if answer_code != EXAM_CODE:
            raise RuntimeError(
                "PDF dap an khong khop ma H21329."
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
    # 11. CAT 10 ANH DAU TIEN
    # ================================================

    DATA.mkdir(
        parents=True,
        exist_ok=True
    )

    QUESTIONS.mkdir(
        parents=True,
        exist_ok=True
    )

    with fitz.open(PDF_FILE) as doc:

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

                filename = (
                    QUESTIONS
                    / f"cau_{number:02d}.png"
                )

                pix.save(str(filename))

                print(
                    f"Cau {number:02d}: "
                    f"trang PDF {page_no}"
                )

    # ================================================
    # 12. LUU JSON DAP AN
    # ================================================

    result = {
        "cap_hsk": 2,
        "so_de": 7,
        "ma_de_goc": EXAM_CODE,

        "file_pdf": str(PDF_FILE),
        "file_dap_an": str(answer_pdf),
        "file_mp3": str(MP3_FILE),

        "tong_cau": 60,
        "so_cau_nghe": 35,
        "so_cau_doc": 25,

        "so_trang_pdf_de": 14,

        "trang_cau_hoi": sorted(
            PAGE_QUESTIONS.keys()
        ),

        "trang_bo_qua": [1, 8],

        # Dap an nam trong PDF rieng.
        "trang_dap_an": 1,
        "nguon_dap_an": "pdf_rieng",

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
    # 13. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH BUOC 1")
    print("=" * 60)

    print("Ma de: H21329")
    print("PDF de thi: 14 trang")
    print("PDF dap an: 1 trang")
    print("Dap an: 60/60")
    print("Anh cau hoi: 10/60")

    print(f"JSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
