
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 5

Buoc 1:
- Tu tim PDF va MP3 De 5.
- Doc ma de that tu PDF.
- Lay 60 dap an trang cuoi.
- Tach 10 anh cau hoi dau tien.
- Tao HTML kiem tra.

Khong thay doi SQL Server.
Khong sua cac de da hoan thanh.
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

TEMPLATE = HSK2 / "prepare_de_02.py"

DATA = HSK2 / "data" / "de_05"
OUTPUT = HSK2 / "output" / "de_05"
QUESTIONS = OUTPUT / "questions"

ANSWER_JSON = DATA / "de_05_dap_an.json"
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

    pattern = re.compile(
        r"\bs[ốo]\s*0?5(?!\d)",
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
            f"Khong tim thay file {extension} cua De 5 "
            f"trong {SOURCE}"
        )

    raise RuntimeError(
        "Co nhieu file nguon cua De 5:\n"
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
# 4. DOC 60 DAP AN
# =====================================================

def extract_answers(page):
    text = unicodedata.normalize(
        "NFKC",
        page.get_text("text")
    )

    if "答案" not in text:
        raise RuntimeError(
            "Trang cuoi khong co bang dap an."
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
            f"Chua du 60 dap an: {missing}"
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
                f"Dap an cau {number} khong hop le: "
                f"{answer}"
            )

    return answers


# =====================================================
# 5. NAP HAM TACH ANH DE 2
# =====================================================

def load_helpers():
    if not TEMPLATE.is_file():
        raise FileNotFoundError(TEMPLATE)

    spec = importlib.util.spec_from_file_location(
        "hsk2_prepare_de02_helpers",
        TEMPLATE
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


# =====================================================
# 6. TAO HTML KIEM TRA
# =====================================================

def create_preview(helpers, exam_code):
    helpers.PREVIEW_HTML = PREVIEW_HTML

    helpers.create_preview()

    content = PREVIEW_HTML.read_text(
        encoding="utf-8"
    )

    content = (
        content
        .replace("H20902", exam_code)
        .replace("Đề 2", "Đề 5")
        .replace("De 2", "De 5")
    )

    PREVIEW_HTML.write_text(
        content,
        encoding="utf-8"
    )


# =====================================================
# 7. MAIN
# =====================================================

def main():
    print("=" * 60)
    print("MOC HAN - HSK2 DE 5")
    print("BUOC 1 - 60 DAP AN VA 10 ANH DAU")
    print("=" * 60)

    pdf_file = find_source_file(
        ".pdf",
        "Đề HSK 2 số 5.pdf"
    )

    mp3_file = find_source_file(
        ".mp3",
        "Đề HSK 2 số 5 file nghe.mp3"
    )

    print(f"\nPDF: {pdf_file.name}")
    print(f"MP3: {mp3_file.name}")

    helpers = load_helpers()

    with fitz.open(pdf_file) as doc:

        print(f"\nPDF co {len(doc)} trang")

        if len(doc) != 18:
            raise RuntimeError(
                "PDF khong dung 18 trang. "
                "Can kiem tra bo cuc truoc khi tach."
            )

        cover_code = get_exam_code(doc[0])
        answer_code = get_exam_code(doc[17])

        print("Ma de trang bia:", cover_code)
        print("Ma de trang dap an:", answer_code)

        if cover_code != answer_code:
            raise RuntimeError(
                "Ma de trang bia va dap an khac nhau."
            )

        exam_code = cover_code

        # Ma de da nhap o 4 de truoc.
        used_codes = {
            "H20901",
            "H20902",
            "H21003",
            "H21004",
        }

        if exam_code in used_codes:
            raise RuntimeError(
                f"Ma de {exam_code} da duoc su dung. "
                "Khong tao de trung."
            )

        answers = extract_answers(doc[17])

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

        DATA.mkdir(
            parents=True,
            exist_ok=True
        )

        QUESTIONS.mkdir(
            parents=True,
            exist_ok=True
        )

        print("\n===== TACH CAU 1-10 =====")

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
    # 8. LUU 60 DAP AN
    # =================================================

    result = {
        "cap_hsk": 2,
        "so_de": 5,
        "ma_de_goc": exam_code,
        "file_pdf": str(pdf_file),
        "file_mp3": str(mp3_file),
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
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    create_preview(
        helpers,
        exam_code
    )

    print("\n" + "=" * 60)
    print("HOAN THANH BUOC 1")
    print("=" * 60)

    print(f"Ma de: {exam_code}")
    print("Dap an: 60/60")
    print("Anh cau hoi: 10/60")
    print(f"JSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
