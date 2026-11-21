
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 3
BUOC 1: CHUAN BI DE

- Kiem tra PDF va MP3.
- Nhan dien ma de trong PDF.
- Lay 60 dap an tu trang cuoi.
- Tach 10 cau Nghe dau tien.
- Tao HTML kiem tra.

Khong thay doi SQL Server.
Khong sua De 1 va De 2.
"""

from pathlib import Path
import importlib.util
import json
import re
import unicodedata

import fitz


ROOT = Path(r"D:\DATN1\scripts\luyen_thi")
HSK2 = ROOT / "hsk2"

PDF_FILE = (
    ROOT / "source" / "De_HSK" / "HSK2"
    / "Đề HSK 2 số 3.pdf"
)

MP3_FILE = (
    ROOT / "source" / "De_HSK" / "HSK2"
    / "Đề HSK 2 số 3 file nghe.mp3"
)

# Tai su dung cac ham cat anh da chay thanh cong.
TEMPLATE = HSK2 / "prepare_de_02.py"

DATA = HSK2 / "data" / "de_03"
OUTPUT = HSK2 / "output" / "de_03"
QUESTIONS = OUTPUT / "questions"

ANSWER_JSON = DATA / "de_03_dap_an.json"
PREVIEW_HTML = OUTPUT / "kiem_tra_10_cau.html"

EXPECTED_CODE = "H21003"


def compact(text):
    """Chuan hoa khoang trang va ky tu trong ma de."""
    text = unicodedata.normalize(
        "NFKC", str(text)
    ).upper()

    return re.sub(r"[^A-Z0-9]", "", text)


def get_pdf_codes(doc):
    """Tim ma de tu bia, trang cau hoi va trang dap an."""
    found = set()

    for page_no in (0, 1, 17):
        text = compact(
            doc[page_no].get_text("text")
        )

        for code in re.findall(r"H2\d{4}", text):
            found.add(code)

    return sorted(found)


def extract_answers(page):
    text = unicodedata.normalize(
        "NFKC",
        page.get_text("text")
    )

    if "答案" not in text:
        raise RuntimeError(
            "Trang 18 khong phai trang dap an."
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

        answers[number] = answer

    missing = [
        n for n in range(1, 61)
        if n not in answers
    ]

    if missing:
        raise RuntimeError(
            f"Chua doc du 60 dap an: {missing}"
        )

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
                f"Dap an cau {number} sai dang: {answer}"
            )

    return answers


def load_extraction_helpers():
    """Nap ham cat anh tu script De 2, khong chay main."""
    if not TEMPLATE.is_file():
        raise FileNotFoundError(TEMPLATE)

    spec = importlib.util.spec_from_file_location(
        "hsk2_prepare_de02_helpers",
        TEMPLATE
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def main():
    print("=" * 60)
    print("MOC HAN - HSK2 DE 3")
    print("CHUAN BI 60 DAP AN VA 10 CAU DAU")
    print("=" * 60)

    for path in (PDF_FILE, MP3_FILE, TEMPLATE):
        if not path.is_file():
            raise FileNotFoundError(path)

    helpers = load_extraction_helpers()

    DATA.mkdir(parents=True, exist_ok=True)
    QUESTIONS.mkdir(parents=True, exist_ok=True)

    with fitz.open(PDF_FILE) as doc:
        print(f"\nPDF co {len(doc)} trang")

        if len(doc) != 18:
            raise RuntimeError(
                "PDF khong dung 18 trang."
            )

        codes = get_pdf_codes(doc)

        print("Ma de doc duoc tu PDF:", codes)

        if EXPECTED_CODE not in codes:
            raise RuntimeError(
                f"PDF khong xac nhan duoc {EXPECTED_CODE}. "
                f"Ma tim thay: {codes}. "
                "Can kiem tra lai ma de goc."
            )

        if any(code != EXPECTED_CODE for code in codes):
            raise RuntimeError(
                "Phat hien ma de khac nhau trong PDF: "
                + str(codes)
            )

        answers = extract_answers(doc[17])

        print("\n===== 60 DAP AN =====")

        for start in range(1, 61, 5):
            row = [
                answers[n]
                for n in range(start, start + 5)
            ]
            print(
                f"{start:02d}-{start+4:02d}: "
                + " ".join(row)
            )

        print("\n===== TACH ANH CAU 1-10 =====")

        for page_no, numbers in [
            (2, list(range(1, 6))),
            (3, list(range(6, 11)))
        ]:
            page = doc[page_no - 1]

            positions = helpers.get_question_positions(
                page, numbers
            )

            for index, number in enumerate(numbers):
                rect = helpers.get_crop_rect(
                    page, numbers, positions, index
                )

                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2.5, 2.5),
                    clip=rect,
                    alpha=False
                )

                filename = f"cau_{number:02d}.png"

                pix.save(str(QUESTIONS / filename))

                print(
                    f"Cau {number:02d}: "
                    f"trang {page_no}"
                )

    # Luu JSON dap an De 3
    answer_data = {
        "cap_hsk": 2,
        "so_de": 3,
        "ma_de_goc": EXPECTED_CODE,
        "file_pdf": str(PDF_FILE),
        "file_mp3": str(MP3_FILE),
        "tong_cau": 60,
        "so_cau_nghe": 35,
        "so_cau_doc": 25,
        "trang_cau_hoi": list(range(2, 14)),
        "trang_bo_qua": [1, 14, 15, 16, 17],
        "trang_dap_an": 18,
        "dap_an": {
            str(n): answers[n]
            for n in range(1, 61)
        }
    }

    ANSWER_JSON.write_text(
        json.dumps(
            answer_data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # Tao HTML xem truoc bang giao dien De 2.
    helpers.PREVIEW_HTML = PREVIEW_HTML
    helpers.create_preview()

    html_content = PREVIEW_HTML.read_text(
        encoding="utf-8"
    )

    html_content = (
        html_content
        .replace("H20902", EXPECTED_CODE)
        .replace("Đề 2", "Đề 3")
        .replace("De 2", "De 3")
    )

    PREVIEW_HTML.write_text(
        html_content,
        encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("HOAN THANH BUOC 1")
    print("=" * 60)
    print(f"Ma de: {EXPECTED_CODE}")
    print("Dap an: 60/60")
    print("Anh cau hoi: 10/60")
    print(f"JSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
