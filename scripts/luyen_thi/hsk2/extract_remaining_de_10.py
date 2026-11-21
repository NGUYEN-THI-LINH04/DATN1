
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 10 (H21332)

BUOC 2:
- Su dung lai thuat toan tach anh De 7.
- Giu nguyen 10 anh dau tien cua De 10.
- Tach cau 11-60.
- Bo qua trang PDF so 8.
- Tao 6 bang lua chon chung.
- Doi chieu 60 dap an voi PDF rieng.
- Tao JSON manifest.
- Tao HTML kiem tra toan bo 60 cau.

KHONG thay doi SQL Server.
KHONG sua cac de da hoan thanh.
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

ROOT = Path(r"D:\DATN1")

HSK2 = (
    ROOT / "scripts" / "luyen_thi" / "hsk2"
)

SOURCE_SCRIPT = (
    HSK2 / "extract_remaining_de_07.py"
)

DATA = HSK2 / "data" / "de_10"
OUTPUT = HSK2 / "output" / "de_10"

ANSWER_JSON = DATA / "de_10_dap_an.json"

QUESTION_DIR = OUTPUT / "questions"
GROUP_DIR = OUTPUT / "groups"

MANIFEST_JSON = (
    DATA / "hinh_60_cau_ung_vien.json"
)

HTML_FILE = OUTPUT / "kiem_tra_60_cau.html"

EXAM_CODE = "H21332"


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
# 3. DAP AN GOC H21332
# =====================================================

EXPECTED_ROWS = [
    "√ × × √ ×",
    "× √ √ × √",
    "F E B C A",
    "B E C D A",
    "A C A A B",
    "A B B B C",
    "C C B A C",
    "B A F C E",
    "C A D B F",
    "× √ √ √ ×",
    "A D C B F",
    "B A D E C",
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
# 4. HAM HO TRO
# =====================================================

def load_json(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open(
        "r",
        encoding="utf-8-sig"
    ) as f:
        return json.load(f)


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


def file_hash(path):

    digest = hashlib.sha256()

    with path.open("rb") as f:

        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def check_file(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    if path.stat().st_size == 0:
        raise RuntimeError(
            f"File rong: {path}"
        )


# =====================================================
# 5. DOC DAP AN TU PDF RIENG
# =====================================================

def extract_pdf_answers(page):

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
                f"Trung dap an cau {number}."
            )

        answers[number] = answer

    if set(answers) != set(range(1, 61)):
        raise RuntimeError(
            "PDF dap an khong du 60 cau."
        )

    return answers


# =====================================================
# 6. KIEM TRA NGUON DE 10
# =====================================================

def check_sources():

    print("\n===== KIEM TRA NGUON =====")

    check_file(SOURCE_SCRIPT)
    check_file(ANSWER_JSON)

    answer_data = load_json(ANSWER_JSON)

    if answer_data.get("so_de") != 10:
        raise RuntimeError(
            "JSON dap an khong phai De 10."
        )

    if answer_data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "JSON dap an khong phai H21332."
        )

    answers = answer_data.get("dap_an", {})

    if set(answers) != {
        str(n) for n in range(1, 61)
    }:
        raise RuntimeError(
            "JSON khong du 60 dap an."
        )

    for number in range(1, 61):

        actual = str(
            answers[str(number)]
        ).strip()

        expected = EXPECTED_ANSWERS[number]

        if actual != expected:
            raise RuntimeError(
                f"Cau {number} sai dap an: "
                f"JSON={actual}, goc={expected}"
            )

    pdf_value = answer_data.get("file_pdf")
    answer_value = answer_data.get("file_dap_an")

    if not pdf_value or not answer_value:
        raise RuntimeError(
            "JSON thieu duong dan PDF de thi "
            "hoac PDF dap an."
        )

    pdf_file = Path(pdf_value)
    answer_pdf = Path(answer_value)

    check_file(pdf_file)
    check_file(answer_pdf)

    # =================================================
    # 7. KIEM TRA PDF DE THI
    # =================================================

    with fitz.open(pdf_file) as doc:

        if len(doc) != 14:
            raise RuntimeError(
                "PDF De 10 phai co 14 trang."
            )

        cover = normalize_code(
            doc[0].get_text("text")
        )

        if EXAM_CODE not in cover:
            raise RuntimeError(
                "Trang bia khong phai H21332."
            )

        checks = [
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

            text = normalize(
                doc[page_no - 1].get_text("text")
            )

            pattern = (
                rf"第\s*{first}\s*[-–—]\s*"
                rf"{last}\s*题"
            )

            if not re.search(pattern, text):
                raise RuntimeError(
                    f"Trang PDF {page_no} "
                    f"khong co nhom cau "
                    f"{first}-{last}."
                )

        # Trang 8 khong duoc co cau hoi.
        page_8 = normalize(
            doc[7].get_text("text")
        )

        if re.search(
            r"第\s*(36|41|46|51|56)\s*[-–—]",
            page_8
        ):
            raise RuntimeError(
                "Trang 8 co cau hoi. "
                "Can kiem tra lai PDF."
            )

    # =================================================
    # 8. KIEM TRA PDF DAP AN
    # =================================================

    with fitz.open(answer_pdf) as doc:

        if len(doc) != 1:
            raise RuntimeError(
                "PDF dap an phai co 1 trang."
            )

        answer_code = normalize_code(
            doc[0].get_text("text")
        )

        if EXAM_CODE not in answer_code:
            raise RuntimeError(
                "PDF dap an khong phai H21332."
            )

        pdf_answers = extract_pdf_answers(
            doc[0]
        )

    for number in range(1, 61):

        expected = EXPECTED_ANSWERS[number]
        pdf_answer = pdf_answers[number]

        if pdf_answer != expected:
            raise RuntimeError(
                f"Cau {number} khong khop PDF: "
                f"{pdf_answer} != {expected}"
            )

    # =================================================
    # 9. BAO VE 10 ANH DAU TIEN
    # =================================================

    first_hashes = {}

    for number in range(1, 11):

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        check_file(path)

        first_hashes[number] = file_hash(path)

    print("Ma de: H21332")
    print("PDF de thi: 14 trang")
    print("PDF dap an: 1 trang rieng")
    print("Trang 8: bo qua")
    print("Dap an: 60/60 KHOP")
    print("Anh cau 1-10: DA CO")

    return pdf_file, first_hashes


# =====================================================
# 10. TAI SU DUNG THUAT TOAN DE 7
# =====================================================

def run_extraction(pdf_file):

    source = SOURCE_SCRIPT.read_text(
        encoding="utf-8-sig"
    )

    required = [
        "H21329",
        "de_07",
        '"Đề HSK 2 số 7.pdf"',
        'get("so_de") != 7',
        '"so_de": 7',
    ]

    missing = [
        item
        for item in required
        if item not in source
    ]

    if missing:
        raise RuntimeError(
            "Script De 7 khac phien ban "
            "da su dung.\n"
            "Khong tu chuyen doi de tranh loi.\n"
            "Thieu:\n"
            + "\n".join(missing)
        )

    # Chi tao ban sao code trong bo nho.
    # Tuyet doi khong sua script De 7.

    converted = source

    # Doi ma de.
    converted = converted.replace(
        "H21329",
        EXAM_CODE
    )

    # Doi thu muc du lieu.
    converted = converted.replace(
        "de_07",
        "de_10"
    )

    # Doi ten PDF theo JSON da kiem tra.
    converted = converted.replace(
        '"Đề HSK 2 số 7.pdf"',
        json.dumps(
            pdf_file.name,
            ensure_ascii=False
        )
    )

    # Doi so de trong logic va manifest.
    converted = converted.replace(
        'get("so_de") != 7',
        'get("so_de") != 10'
    )

    converted = converted.replace(
        '"so_de": 7',
        '"so_de": 10'
    )

    converted = converted.replace(
        "DE 7",
        "DE 10"
    )

    converted = converted.replace(
        "De 7",
        "De 10"
    )

    converted = converted.replace(
        "Đề 7",
        "Đề 10"
    )

    # Kiem tra khong con tham chieu De 7.
    if (
        "H21329" in converted
        or "de_07" in converted
        or 'get("so_de") != 7' in converted
        or '"so_de": 7' in converted
    ):
        raise RuntimeError(
            "Code chuyen doi van con "
            "tham chieu De 7."
        )

    program = compile(
        converted,
        str(Path(__file__).resolve()),
        "exec"
    )

    print("\n===== TACH CAU 11-60 =====")
    print("Su dung thuat toan da chay o De 7-9.")
    print(f"PDF: {pdf_file.name}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(
            Path(__file__).resolve()
        ),
    }

    exec(program, namespace)


# =====================================================
# 11. KIEM TRA KET QUA
# =====================================================

def verify_results(first_hashes):

    print("\n===== KIEM TRA KET QUA =====")

    # Kiem tra 60 anh cau hoi.
    for number in range(1, 61):

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        check_file(path)

    # Dam bao 10 anh dau tien khong thay doi.
    for number, original_hash in first_hashes.items():

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if file_hash(path) != original_hash:
            raise RuntimeError(
                f"Anh cau {number} da bi thay doi."
            )

    # Kiem tra 6 bang lua chon.
    for group in GROUP_PAGES:

        path = GROUP_DIR / f"{group}.png"

        check_file(path)

    # Kiem tra manifest.
    manifest = load_json(MANIFEST_JSON)

    if manifest.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "Ma de trong manifest khong dung."
        )

    if manifest.get("so_de") != 10:
        raise RuntimeError(
            "Manifest khong phai De 10."
        )

    images = manifest.get("cau_hoi", {})
    groups = manifest.get("bang_lua_chon", {})

    if set(images) != {
        str(n) for n in range(1, 61)
    }:
        raise RuntimeError(
            "Manifest khong du 60 cau."
        )

    if set(groups) != set(GROUP_PAGES):
        raise RuntimeError(
            "Manifest khong du 6 bang lua chon."
        )

    # Doi chieu trang PDF cua tung cau.
    for page_no, numbers in PAGE_QUESTIONS.items():

        for number in numbers:

            actual = (
                images[str(number)].get("trang_pdf")
            )

            if actual != page_no:
                raise RuntimeError(
                    f"Cau {number} sai trang PDF: "
                    f"{actual}, can {page_no}"
                )

    # Doi chieu trang cua bang lua chon.
    for group, page_no in GROUP_PAGES.items():

        actual = groups[group].get("trang_pdf")

        if actual != page_no:
            raise RuntimeError(
                f"Bang {group} sai trang PDF: "
                f"{actual}, can {page_no}"
            )

    # Kiem tra HTML.
    check_file(HTML_FILE)

    html_content = HTML_FILE.read_text(
        encoding="utf-8"
    )

    if EXAM_CODE not in html_content:
        raise RuntimeError(
            "HTML khong co ma H21332."
        )

    if "H21329" in html_content:
        raise RuntimeError(
            "HTML van hien thi ma De 7."
        )

    print("\n" + "=" * 60)
    print("HOAN THANH HSK2 DE 10 - BUOC 2")
    print("=" * 60)

    print("Ma de: H21332")
    print("So de: 10")
    print("Anh cau hoi: 60/60")
    print("Bang lua chon: 6/6")
    print("Dap an: 60/60")
    print("Anh cau 1-10: KHONG THAY DOI")
    print("Trang 8: DA BO QUA")

    print(f"JSON: {MANIFEST_JSON}")
    print(f"HTML: {HTML_FILE}")

    print("\nChua thay doi SQL Server.")


# =====================================================
# 12. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK2 DE 10")
    print("TACH CAU 11-60 - H21332")
    print("=" * 60)

    pdf_file, first_hashes = check_sources()

    run_extraction(pdf_file)

    verify_results(first_hashes)


if __name__ == "__main__":
    main()
