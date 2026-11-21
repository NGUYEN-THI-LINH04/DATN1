
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 5

BUOC 2:
- Giu nguyen 10 anh dau tien.
- Tach anh cau 11-60.
- Tao 6 bang lua chon chung.
- Tao HTML xem truoc 60 cau.
- Tao JSON thong tin anh.

Tai su dung script HSK2 De 2 da chay thanh cong.
Ma de va PDF lay tu JSON dap an De 5.

Khong thay doi SQL Server.
Khong sua cac de HSK1 va HSK2 De 1-4.
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

DATA_DIR = HSK2 / "data" / "de_05"
OUTPUT_DIR = HSK2 / "output" / "de_05"

ANSWER_FILE = DATA_DIR / "de_05_dap_an.json"

QUESTION_DIR = OUTPUT_DIR / "questions"
GROUP_DIR = OUTPUT_DIR / "groups"

MANIFEST_FILE = (
    DATA_DIR / "hinh_60_cau_ung_vien.json"
)

HTML_FILE = OUTPUT_DIR / "kiem_tra_60_cau.html"


# =====================================================
# 2. DOC THONG TIN DE 5
# =====================================================

def load_json(path):
    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def normalize_text(value):
    text = unicodedata.normalize(
        "NFKC", str(value)
    ).upper()

    return re.sub(r"[^A-Z0-9]", "", text)


def read_exam_info():
    data = load_json(ANSWER_FILE)

    if data.get("so_de") != 5:
        raise RuntimeError(
            "JSON dap an khong phai HSK2 De 5."
        )

    exam_code = str(
        data.get("ma_de_goc", "")
    ).strip().upper()

    if not re.fullmatch(r"H2\d{4}", exam_code):
        raise RuntimeError(
            f"Ma de goc khong hop le: {exam_code}"
        )

    answers = data.get("dap_an", {})

    expected = {
        str(n) for n in range(1, 61)
    }

    if set(answers) != expected:
        raise RuntimeError(
            "JSON dap an chua du 60 cau."
        )

    pdf_value = data.get("file_pdf")
    mp3_value = data.get("file_mp3")

    if not pdf_value or not mp3_value:
        raise RuntimeError(
            "JSON dap an thieu duong dan PDF hoac MP3."
        )

    pdf_file = Path(pdf_value)
    mp3_file = Path(mp3_value)

    if not pdf_file.is_file():
        raise FileNotFoundError(pdf_file)

    if not mp3_file.is_file():
        raise FileNotFoundError(mp3_file)

    return exam_code, pdf_file, mp3_file


# =====================================================
# 3. KIEM TRA PDF
# =====================================================

def check_pdf(exam_code, pdf_file):
    with fitz.open(pdf_file) as doc:
        print(f"PDF co {len(doc)} trang")

        if len(doc) != 18:
            raise RuntimeError(
                "PDF khong dung 18 trang. "
                "Can kiem tra lai bo cuc."
            )

        cover = normalize_text(
            doc[0].get_text("text")
        )

        answer_page = normalize_text(
            doc[17].get_text("text")
        )

        if exam_code not in cover:
            raise RuntimeError(
                "Ma de trong JSON khac trang bia PDF."
            )

        if exam_code not in answer_page:
            raise RuntimeError(
                "Ma de trong JSON khac trang dap an PDF."
            )

        if "答案" not in doc[17].get_text("text"):
            raise RuntimeError(
                "Trang 18 khong phai trang dap an."
            )

    print("Da xac nhan ma de:", exam_code)
    print("Trang cau hoi: 2-13")
    print("Trang bo qua: 14-17")
    print("Trang dap an: 18")


# =====================================================
# 4. KIEM TRA 10 ANH DA HOAN THANH
# =====================================================

def check_first_ten():
    for number in range(1, 11):
        image = (
            QUESTION_DIR / f"cau_{number:02d}.png"
        )

        if not image.is_file():
            raise FileNotFoundError(
                f"Thieu anh cau {number}: {image}"
            )

    print("Da kiem tra 10 anh dau tien.")


# =====================================================
# 5. TAO BO TACH ANH DE 5
# =====================================================

def build_extractor(exam_code, pdf_file):
    if not SOURCE_SCRIPT.is_file():
        raise FileNotFoundError(SOURCE_SCRIPT)

    source = SOURCE_SCRIPT.read_text(
        encoding="utf-8-sig"
    )

    required = [
        "H20902",
        "de_02",
        "Đề HSK 2 số 2.pdf",
    ]

    for value in required:
        if value not in source:
            raise RuntimeError(
                f"Script De 2 thieu: {value}"
            )

    # Ten PDF cua De 5 lay tu JSON,
    # khong tu doan ten file.
    replacements = [
        (
            "Đề HSK 2 số 2.pdf",
            pdf_file.name
        ),
        (
            "H20902",
            exam_code
        ),
        (
            "de_02",
            "de_05"
        ),
        (
            "Đề 2",
            "Đề 5"
        ),
        (
            "DE 2",
            "DE 5"
        ),
        (
            "De 2",
            "De 5"
        ),
    ]

    for old, new in replacements:
        source = source.replace(old, new)

    # Kiem tra khong con duong dan De 2.
    if "de_02" in source or "H20902" in source:
        raise RuntimeError(
            "Script van con tham chieu De 2."
        )

    if "Đề HSK 2 số 2.pdf" in source:
        raise RuntimeError(
            "Chua thay ten PDF nguon."
        )

    # Kiem tra cu phap truoc khi chay.
    compiled = compile(
        source,
        str(HSK2 / "extract_remaining_de_05.py"),
        "exec"
    )

    return compiled


# =====================================================
# 6. KIEM TRA KET QUA TACH ANH
# =====================================================

def check_result(exam_code):
    manifest = load_json(MANIFEST_FILE)

    if manifest.get("ma_de_goc") != exam_code:
        raise RuntimeError(
            "Ma de trong JSON hinh khong dung."
        )

    questions = manifest.get("cau_hoi", {})
    groups = manifest.get("bang_lua_chon", {})

    expected = {
        str(n) for n in range(1, 61)
    }

    if set(questions) != expected:
        raise RuntimeError(
            "JSON hinh chua du thong tin 60 cau."
        )

    expected_groups = {
        "nghe_11_15",
        "nghe_16_20",
        "doc_36_40",
        "doc_41_45",
        "doc_51_55",
        "doc_56_60",
    }

    if set(groups) != expected_groups:
        raise RuntimeError(
            "Chua du 6 bang lua chon."
        )

    # Kiem tra 60 anh cau hoi da tao.
    for number in range(1, 61):
        image = (
            QUESTION_DIR / f"cau_{number:02d}.png"
        )

        if not image.is_file():
            raise FileNotFoundError(image)

    # Kiem tra 6 bang lua chon.
    for group in expected_groups:
        image = GROUP_DIR / f"{group}.png"

        if not image.is_file():
            raise FileNotFoundError(image)

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
    print("HOAN THANH HSK2 DE 5")
    print("=" * 60)

    print(f"Ma de: {exam_code}")
    print("Anh cau hoi: 60/60")
    print("Bang lua chon: 6/6")
    print("Dap an: 60/60")
    print(f"JSON: {MANIFEST_FILE}")
    print(f"HTML: {HTML_FILE}")

    print("\nChua chuan hoa de.")
    print("Chua thay doi SQL Server.")


# =====================================================
# 7. CHUONG TRINH CHINH
# =====================================================

def main():
    print("=" * 60)
    print("MOC HAN - HSK2 DE 5")
    print("TACH ANH CAU 11-60")
    print("=" * 60)

    exam_code, pdf_file, mp3_file = read_exam_info()

    print(f"\nMa de: {exam_code}")
    print(f"PDF: {pdf_file.name}")
    print(f"MP3: {mp3_file.name}")

    check_pdf(exam_code, pdf_file)
    check_first_ten()

    compiled = build_extractor(
        exam_code,
        pdf_file
    )

    print("\n===== BAT DAU TACH ANH =====")

    # Chay bo xu ly cua De 2 voi du lieu De 5.
    # Khong chinh sua script De 2 tren o dia.
    namespace = {
        "__name__": "__main__",
        "__file__": str(
            HSK2 / "extract_remaining_de_05.py"
        ),
    }

    exec(compiled, namespace)

    check_result(exam_code)


if __name__ == "__main__":
    main()
