
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 4

BUOC 2:
- Giu nguyen 10 anh dau tien.
- Tach anh cau 11-60.
- Tao 6 bang lua chon chung.
- Tao HTML kiem tra 60 cau.
- Tao JSON thong tin anh.

Su dung lai bo tach anh De 2 da kiem tra.
Ma de duoc lay tu JSON dap an De 4.

Khong thay doi SQL Server.
Khong sua HSK1, HSK2 De 1-3.
"""

from pathlib import Path
import json
import re
import unicodedata
import fitz


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

HSK2 = ROOT / "hsk2"

SOURCE_SCRIPT = (
    HSK2 / "extract_remaining_de_02.py"
)

PDF_FILE = (
    ROOT / "source" / "De_HSK" / "HSK2"
    / "Đề HSK 2 số 4.pdf"
)

ANSWER_FILE = (
    HSK2 / "data" / "de_04"
    / "de_04_dap_an.json"
)

QUESTION_DIR = (
    HSK2 / "output" / "de_04" / "questions"
)

GROUP_DIR = (
    HSK2 / "output" / "de_04" / "groups"
)

OUTPUT_DIR = (
    HSK2 / "output" / "de_04"
)

MANIFEST_FILE = (
    HSK2 / "data" / "de_04"
    / "hinh_60_cau_ung_vien.json"
)

HTML_FILE = (
    OUTPUT_DIR / "kiem_tra_60_cau.html"
)


# =====================================================
# 2. DOC MA DE
# =====================================================

def normalize_code(value):
    text = unicodedata.normalize(
        "NFKC", str(value)
    ).upper()

    return re.sub(r"[^A-Z0-9]", "", text)


def read_exam_code():
    if not ANSWER_FILE.is_file():
        raise FileNotFoundError(ANSWER_FILE)

    with ANSWER_FILE.open(
        "r", encoding="utf-8-sig"
    ) as f:
        data = json.load(f)

    exam_code = data.get("ma_de_goc", "")

    if not re.fullmatch(r"H2\d{4}", exam_code):
        raise RuntimeError(
            f"Ma de trong JSON khong hop le: {exam_code}"
        )

    if data.get("so_de") != 4:
        raise RuntimeError(
            "JSON dap an khong phai De 4."
        )

    answers = data.get("dap_an", {})

    if set(answers) != {
        str(n) for n in range(1, 61)
    }:
        raise RuntimeError(
            "JSON dap an chua du 60 cau."
        )

    return exam_code


# =====================================================
# 3. KIEM TRA FILE PDF
# =====================================================

def check_pdf(exam_code):
    if not PDF_FILE.is_file():
        raise FileNotFoundError(PDF_FILE)

    with fitz.open(PDF_FILE) as doc:
        if len(doc) != 18:
            raise RuntimeError(
                f"PDF co {len(doc)} trang, "
                "can kiem tra lai bo cuc."
            )

        cover = normalize_code(
            doc[0].get_text("text")
        )

        answer_page = normalize_code(
            doc[17].get_text("text")
        )

        if exam_code not in cover:
            raise RuntimeError(
                "Ma de trong JSON khac trang bia PDF."
            )

        if exam_code not in answer_page:
            raise RuntimeError(
                "Ma de trong JSON khac trang dap an."
            )

        if "答案" not in doc[17].get_text("text"):
            raise RuntimeError(
                "Trang 18 khong phai trang dap an."
            )

    print(f"Da kiem tra PDF: {exam_code}")
    print("PDF: 18 trang")
    print("Trang cau hoi: 2-13")
    print("Trang bo qua: 14-17")
    print("Trang dap an: 18")


# =====================================================
# 4. KIEM TRA 10 ANH DA CO
# =====================================================

def check_first_ten():
    for number in range(1, 11):
        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if not path.is_file():
            raise FileNotFoundError(
                f"Thieu anh cau {number}: {path}"
            )

    print("Da co 10 anh cau hoi dau tien.")


# =====================================================
# 5. TAO CODE TACH ANH DE 4
# =====================================================

def build_extractor(exam_code):
    if not SOURCE_SCRIPT.is_file():
        raise FileNotFoundError(SOURCE_SCRIPT)

    code = SOURCE_SCRIPT.read_text(
        encoding="utf-8-sig"
    )

    required = [
        "H20902",
        "de_02",
        "Đề HSK 2 số 2.pdf",
    ]

    for value in required:
        if value not in code:
            raise RuntimeError(
                f"Script mau thieu: {value}"
            )

    replacements = [
        (
            "Đề HSK 2 số 2.pdf",
            "Đề HSK 2 số 4.pdf"
        ),
        ("H20902", exam_code),
        ("de_02", "de_04"),
        ("Đề 2", "Đề 4"),
        ("DE 2", "DE 4"),
        ("De 2", "De 4"),
    ]

    for old, new in replacements:
        code = code.replace(old, new)

    # Dam bao khong con tham chieu De 2.
    for old in required:
        if old in code:
            raise RuntimeError(
                f"Script moi con tham chieu cu: {old}"
            )

    # Kiem tra cu phap.
    compiled = compile(
        code,
        str(SOURCE_SCRIPT),
        "exec"
    )

    return compiled


# =====================================================
# 6. KIEM TRA KET QUA
# =====================================================

def check_result(exam_code):
    if not MANIFEST_FILE.is_file():
        raise FileNotFoundError(MANIFEST_FILE)

    with MANIFEST_FILE.open(
        "r", encoding="utf-8-sig"
    ) as f:
        manifest = json.load(f)

    if manifest.get("ma_de_goc") != exam_code:
        raise RuntimeError(
            "Ma de trong JSON hinh khong dung."
        )

    questions = manifest.get("cau_hoi", {})
    groups = manifest.get("bang_lua_chon", {})

    if set(questions) != {
        str(n) for n in range(1, 61)
    }:
        raise RuntimeError(
            "Chua du thong tin 60 cau."
        )

    if len(groups) != 6:
        raise RuntimeError(
            "Chua du 6 bang lua chon."
        )

    for number in range(1, 61):
        image_path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if not image_path.is_file():
            raise RuntimeError(
                f"Thieu anh cau {number}"
            )

    for group in groups:
        image_path = (
            GROUP_DIR / f"{group}.png"
        )

        if not image_path.is_file():
            raise RuntimeError(
                f"Thieu bang lua chon: {group}"
            )

    if not HTML_FILE.is_file():
        raise FileNotFoundError(HTML_FILE)

    html = HTML_FILE.read_text(
        encoding="utf-8"
    )

    if exam_code not in html:
        raise RuntimeError(
            "HTML chua hien thi dung ma de."
        )

    print("\n" + "=" * 60)
    print("HOAN THANH HSK2 DE 4")
    print("=" * 60)

    print(f"Ma de: {exam_code}")
    print("Tong cau: 60/60")
    print("Bang lua chon: 6/6")
    print("Dap an: 60/60")

    print(f"\nJSON: {MANIFEST_FILE}")
    print(f"HTML: {HTML_FILE}")

    print("\nChua chuan hoa de.")
    print("Chua thay doi SQL Server.")


# =====================================================
# 7. MAIN
# =====================================================

def main():
    print("=" * 60)
    print("MOC HAN - HSK2 DE 4")
    print("TACH CAU 11-60")
    print("=" * 60)

    exam_code = read_exam_code()

    print(f"\nMa de goc: {exam_code}")

    check_pdf(exam_code)
    check_first_ten()

    compiled = build_extractor(exam_code)

    print("\n===== BAT DAU TACH ANH =====")

    # Chay bo tach anh De 2 voi duong dan De 4.
    # Khong sua file script De 2.
    namespace = {
        "__name__": "__main__",
        "__file__": str(
            HSK2 / "extract_remaining_de_04.py"
        ),
    }

    exec(compiled, namespace)

    check_result(exam_code)


if __name__ == "__main__":
    main()
