
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 6 (H21006)

BUOC 2:
- Su dung lai bo tach anh De 2.
- Ho tro PDF 14 trang.
- Giu nguyen 10 anh dau tien.
- Tach cau 11-60.
- Tao 6 bang lua chon chung.
- Tao JSON thong tin anh.
- Tao HTML kiem tra 60 cau.

Khong thay doi SQL Server.
Khong sua cac de da hoan thanh.
"""

from pathlib import Path
import hashlib
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

DATA_DIR = HSK2 / "data" / "de_06"
OUTPUT_DIR = HSK2 / "output" / "de_06"

ANSWER_FILE = DATA_DIR / "de_06_dap_an.json"

QUESTION_DIR = OUTPUT_DIR / "questions"
GROUP_DIR = OUTPUT_DIR / "groups"

MANIFEST_FILE = (
    DATA_DIR / "hinh_60_cau_ung_vien.json"
)

HTML_FILE = (
    OUTPUT_DIR / "kiem_tra_60_cau.html"
)

EXPECTED_CODE = "H21006"

EXPECTED_GROUPS = {
    "nghe_11_15",
    "nghe_16_20",
    "doc_36_40",
    "doc_41_45",
    "doc_51_55",
    "doc_56_60",
}


# =====================================================
# 2. HAM DUNG CHUNG
# =====================================================

def load_json(path):
    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def normalize_code(value):
    text = unicodedata.normalize(
        "NFKC", str(value)
    ).upper()

    return re.sub(r"[^A-Z0-9]", "", text)


def file_hash(path):
    hasher = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024), b""
        ):
            hasher.update(block)

    return hasher.hexdigest()


# =====================================================
# 3. DOC THONG TIN DE 6
# =====================================================

def read_exam_info():
    data = load_json(ANSWER_FILE)

    if data.get("so_de") != 6:
        raise RuntimeError(
            "JSON dap an khong phai HSK2 De 6."
        )

    exam_code = str(
        data.get("ma_de_goc", "")
    ).strip().upper()

    if exam_code != EXPECTED_CODE:
        raise RuntimeError(
            f"Ma de khong dung. "
            f"Can {EXPECTED_CODE}, nhan {exam_code}."
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
            "Thieu duong dan PDF hoac MP3."
        )

    pdf_file = Path(pdf_value)
    mp3_file = Path(mp3_value)

    if not pdf_file.is_file():
        raise FileNotFoundError(pdf_file)

    if not mp3_file.is_file():
        raise FileNotFoundError(mp3_file)

    return exam_code, pdf_file, mp3_file


# =====================================================
# 4. KIEM TRA PDF 14 TRANG
# =====================================================

def check_pdf(exam_code, pdf_file):
    with fitz.open(pdf_file) as doc:

        print(f"PDF co {len(doc)} trang")

        if len(doc) != 14:
            raise RuntimeError(
                "PDF De 6 phai co 14 trang."
            )

        cover = normalize_code(
            doc[0].get_text("text")
        )

        answer_page = normalize_code(
            doc[13].get_text("text")
        )

        if exam_code not in cover:
            raise RuntimeError(
                "Ma de khong khop trang bia."
            )

        if exam_code not in answer_page:
            raise RuntimeError(
                "Ma de khong khop trang dap an."
            )

        if "答案" not in doc[13].get_text("text"):
            raise RuntimeError(
                "Trang 14 khong phai trang dap an."
            )

    print(f"Ma de PDF: {exam_code}")
    print("Trang cau hoi: 2-13")
    print("Trang dap an: 14")
    print("Khong co trang loi thoai nghe.")


# =====================================================
# 5. KIEM TRA VA BAO VE 10 ANH DAU
# =====================================================

def check_first_ten():
    hashes = {}

    for number in range(1, 11):

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if not path.is_file():
            raise FileNotFoundError(
                f"Thieu anh cau {number}: {path}"
            )

        hashes[number] = file_hash(path)

    print("Da co 10 anh dau tien.")

    return hashes


def verify_first_ten(hashes):
    for number, old_hash in hashes.items():

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if not path.is_file():
            raise RuntimeError(
                f"Anh cau {number} da bi mat."
            )

        if file_hash(path) != old_hash:
            raise RuntimeError(
                f"Anh cau {number} da bi thay doi."
            )

    print("10 anh dau tien duoc giu nguyen.")


# =====================================================
# 6. CHUAN BI BO TACH ANH
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
                f"Script mau thieu: {value}"
            )

    # Chuyen tham chieu tu De 2 sang De 6.
    replacements = [
        (
            "Đề HSK 2 số 2.pdf",
            pdf_file.name
        ),
        ("H20902", exam_code),
        ("de_02", "de_06"),
        ("Đề 2", "Đề 6"),
        ("DE 2", "DE 6"),
        ("De 2", "De 6"),
    ]

    for old, new in replacements:
        source = source.replace(old, new)

    # Dieu chinh kiem tra 18 trang thanh 14 trang
    # neu script mau co kiem tra so trang.
    source = re.sub(
        r"((?:len\s*\(\s*doc\s*\)|"
        r"doc\.page_count)\s*(?:!=|==|<|>)\s*)18\b",
        lambda m: m.group(1) + "14",
        source
    )

    # Trang dap an: index 17 -> index 13.
    # Chi thay cach truy cap trang dap an,
    # khong sua toa do cat anh.
    source = re.sub(
        r"\bdoc\s*\[\s*17\s*\]",
        "doc[13]",
        source
    )

    source = re.sub(
        r"\bdoc\.load_page\s*\(\s*17\s*\)",
        "doc.load_page(13)",
        source
    )

    # Kiem tra khong con tham chieu De 2.
    for old in required:
        if old in source:
            raise RuntimeError(
                f"Con tham chieu cu: {old}"
            )

    compiled = compile(
        source,
        str(
            HSK2 / "extract_remaining_de_06.py"
        ),
        "exec"
    )

    return compiled


# =====================================================
# 7. KIEM TRA 60 ANH SAU KHI TACH
# =====================================================

def check_result(exam_code, original_hashes):

    verify_first_ten(original_hashes)

    manifest = load_json(MANIFEST_FILE)

    if manifest.get("ma_de_goc") != exam_code:
        raise RuntimeError(
            "Ma de trong JSON hinh khong dung."
        )

    questions = manifest.get("cau_hoi", {})
    groups = manifest.get("bang_lua_chon", {})

    expected_questions = {
        str(n) for n in range(1, 61)
    }

    if set(questions) != expected_questions:
        raise RuntimeError(
            "JSON hinh khong du 60 cau."
        )

    if set(groups) != EXPECTED_GROUPS:
        raise RuntimeError(
            "JSON hinh khong du 6 bang lua chon."
        )

    # Kiem tra 60 anh cau hoi.
    for number in range(1, 61):

        image = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if not image.is_file():
            raise FileNotFoundError(image)

        if image.stat().st_size == 0:
            raise RuntimeError(
                f"Anh cau {number} bi rong."
            )

    # Kiem tra 6 bang lua chon chung.
    for group in EXPECTED_GROUPS:

        image = (
            GROUP_DIR / f"{group}.png"
        )

        if not image.is_file():
            raise FileNotFoundError(image)

        if image.stat().st_size == 0:
            raise RuntimeError(
                f"Bang lua chon {group} bi rong."
            )

    if not HTML_FILE.is_file():
        raise FileNotFoundError(HTML_FILE)

    html = HTML_FILE.read_text(
        encoding="utf-8"
    )

    if exam_code not in html:
        raise RuntimeError(
            "HTML khong hien thi dung ma de."
        )

    print("\n" + "=" * 60)
    print("HOAN THANH HSK2 DE 6")
    print("=" * 60)

    print(f"Ma de: {exam_code}")
    print("Tong cau: 60/60")
    print("Bang lua chon chung: 6/6")
    print("Dap an: 60/60")
    print(f"JSON: {MANIFEST_FILE}")
    print(f"HTML: {HTML_FILE}")

    print("\nChua chuan hoa de.")
    print("Chua thay doi SQL Server.")


# =====================================================
# 8. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK2 DE 6")
    print("TACH ANH CAU 11-60")
    print("=" * 60)

    exam_code, pdf_file, mp3_file = read_exam_info()

    print(f"\nMa de: {exam_code}")
    print(f"PDF: {pdf_file.name}")
    print(f"MP3: {mp3_file.name}")

    check_pdf(exam_code, pdf_file)

    original_hashes = check_first_ten()

    compiled = build_extractor(
        exam_code,
        pdf_file
    )

    print("\n===== BAT DAU TACH ANH =====")

    # Chay bo tach anh da thanh cong cua De 2,
    # nhung dung du lieu va thu muc De 6.
    namespace = {
        "__name__": "__main__",
        "__file__": str(
            HSK2 / "extract_remaining_de_06.py"
        ),
    }

    exec(compiled, namespace)

    check_result(
        exam_code,
        original_hashes
    )


if __name__ == "__main__":
    main()
