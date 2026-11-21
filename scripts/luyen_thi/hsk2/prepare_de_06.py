
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 6

Buoc 1:
- Tu tim PDF va MP3 cua De 6.
- Doc ma de goc tu PDF.
- Kiem tra ma de tren trang bia va dap an.
- Lay 60 dap an tu trang cuoi.
- Tach 10 anh cau hoi Nghe dau tien.
- Tao HTML de kiem tra.

Khong thay doi SQL Server.
Khong sua HSK1 va HSK2 De 1-5.
"""

from pathlib import Path
import importlib.util
import json
import re
import unicodedata

import fitz


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

HSK2 = ROOT / "hsk2"

SOURCE = ROOT / "source" / "De_HSK" / "HSK2"

# Script De 2 da tach anh thanh cong
TEMPLATE = HSK2 / "prepare_de_02.py"

DATA = HSK2 / "data" / "de_06"

OUTPUT = HSK2 / "output" / "de_06"

QUESTIONS = OUTPUT / "questions"

ANSWER_JSON = DATA / "de_06_dap_an.json"

PREVIEW_HTML = OUTPUT / "kiem_tra_10_cau.html"


# =====================================================
# 2. TIM FILE PDF VA MP3
# =====================================================

def find_source_file(extension, preferred_name):

    preferred = SOURCE / preferred_name

    if preferred.is_file():
        return preferred

    if not SOURCE.is_dir():
        raise FileNotFoundError(SOURCE)

    # Tim ten file co "so 6" hoac "so 06"
    pattern = re.compile(
        r"\bs[ốo]\s*0?6(?!\d)",
        re.IGNORECASE
    )

    candidates = []

    for path in SOURCE.iterdir():

        if not path.is_file():
            continue

        if path.suffix.lower() != extension.lower():
            continue

        name = unicodedata.normalize(
            "NFC", path.stem
        )

        if pattern.search(name):
            candidates.append(path)

    if len(candidates) == 1:
        return candidates[0]

    if not candidates:
        raise FileNotFoundError(
            f"Khong tim thay file {extension} "
            f"cua HSK2 De 6 trong {SOURCE}"
        )

    raise RuntimeError(
        "Tim thay nhieu file, chua the chon chinh xac:\n"
        + "\n".join(str(p) for p in candidates)
    )


# =====================================================
# 3. DOC MA DE GOC
# =====================================================

def get_exam_code(page):

    text = unicodedata.normalize(
        "NFKC",
        page.get_text("text")
    )

    text = re.sub(r"\s+", "", text)

    codes = set(
        re.findall(
            r"H2\d{4}",
            text,
            re.IGNORECASE
        )
    )

    if len(codes) != 1:
        raise RuntimeError(
            "Khong xac dinh duoc ma de duy nhat: "
            + str(sorted(codes))
        )

    return codes.pop().upper()


# =====================================================
# 4. DOC 60 DAP AN TU PDF
# =====================================================

def extract_answers(page):

    text = unicodedata.normalize(
        "NFKC",
        page.get_text("text")
    )

    if "答案" not in text:
        raise RuntimeError(
            "Trang cuoi khong phai trang dap an."
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

    expected = set(range(1, 61))

    if set(answers) != expected:

        missing = sorted(
            expected - set(answers)
        )

        raise RuntimeError(
            f"Chua doc du 60 dap an: {missing}"
        )

    # Kiem tra dang dap an cua tung phan.
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
                f"Dap an cau {number} khong hop le: "
                f"{answer}"
            )

    return answers


# =====================================================
# 5. NAP HAM TACH ANH DA CO
# =====================================================

def load_helpers():

    if not TEMPLATE.is_file():
        raise FileNotFoundError(TEMPLATE)

    spec = importlib.util.spec_from_file_location(
        "hsk2_prepare_de02_helpers",
        TEMPLATE
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "Khong the nap script De 2."
        )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


# =====================================================
# 6. TAO HTML KIEM TRA
# =====================================================

def create_preview(helpers, exam_code):

    helpers.PREVIEW_HTML = PREVIEW_HTML

    # Su dung giao dien xem truoc cua De 2
    helpers.create_preview()

    content = PREVIEW_HTML.read_text(
        encoding="utf-8"
    )

    content = (
        content
        .replace("H20902", exam_code)
        .replace("Đề 2", "Đề 6")
        .replace("De 2", "De 6")
    )

    PREVIEW_HTML.write_text(
        content,
        encoding="utf-8"
    )


# =====================================================
# 7. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK2 DE 6")
    print("BUOC 1 - DAP AN VA 10 ANH DAU")
    print("=" * 60)

    # Tim file nguon
    pdf_file = find_source_file(
        ".pdf",
        "Đề HSK 2 số 6.pdf"
    )

    mp3_file = find_source_file(
        ".mp3",
        "Đề HSK 2 số 6 file nghe.mp3"
    )

    print(f"\nPDF: {pdf_file.name}")
    print(f"MP3: {mp3_file.name}")

    helpers = load_helpers()

    # ================================================
    # 8. DOC PDF VA KIEM TRA MA DE
    # ================================================

    with fitz.open(pdf_file) as doc:

        print(f"\nPDF co {len(doc)} trang")

        if len(doc) != 14:
                raise RuntimeError(
                    f"PDF De 6 co {len(doc)} trang, "
                    f"du kien 14 trang. Can kiem tra lai."
        )

        cover_code = get_exam_code(doc[0])

        answer_code = get_exam_code(doc[13])

        print("Ma de trang bia:", cover_code)
        print("Ma de trang dap an:", answer_code)

        if cover_code != answer_code:
            raise RuntimeError(
                "Ma de tren trang bia "
                "va trang dap an khac nhau."
            )

        exam_code = cover_code

        # Khong de trung ma de da nhap SQL
        used_codes = {
            "H20901",
            "H20902",
            "H21003",
            "H21004",
            "H21005",
        }

        if exam_code in used_codes:
            raise RuntimeError(
                f"Ma de {exam_code} da duoc su dung."
            )

        answers = extract_answers(doc[13])

        # ============================================
        # 9. HIEN THI 60 DAP AN
        # ============================================

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

        # ============================================
        # 10. TACH 10 ANH DAU TIEN
        # ============================================

        DATA.mkdir(
            parents=True,
            exist_ok=True
        )

        QUESTIONS.mkdir(
            parents=True,
            exist_ok=True
        )

        print("\n===== TACH ANH CAU 1-10 =====")

        for page_no, numbers in [
            (2, list(range(1, 6))),
            (3, list(range(6, 11))),
        ]:

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
                    f"Cau {number:02d}: trang {page_no}"
                )

    # =================================================
    # 11. LUU DAP AN JSON
    # =================================================

    result = {
        "cap_hsk": 2,
        "so_de": 6,
        "ma_de_goc": exam_code,
        "file_pdf": str(pdf_file),
        "file_mp3": str(mp3_file),
        "tong_cau": 60,
        "so_cau_nghe": 35,
        "so_cau_doc": 25,
        "trang_cau_hoi": list(range(2, 14)),
        "trang_bo_qua": [1],
        "trang_dap_an": 14,
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

    # =================================================
    # 12. TAO TRANG HTML KIEM TRA
    # =================================================

    create_preview(
        helpers,
        exam_code
    )

    print("\n" + "=" * 60)
    print("HOAN THANH BUOC 1")
    print("=" * 60)

    print(f"Ma de goc: {exam_code}")
    print("Dap an: 60/60")
    print("Anh cau hoi: 10/60")
    print(f"JSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
