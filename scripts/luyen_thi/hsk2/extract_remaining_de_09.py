
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 9 (H21331)

BUOC 2:
- Giu nguyen 10 anh cau dau.
- Tach cau 11-60.
- Tao 6 bang lua chon chung.
- Kiem tra 60 dap an voi PDF rieng.
- Tao JSON manifest va HTML 60 cau.

Khong thay doi SQL Server.
Khong thay doi cac de da hoan thanh.
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

HSK2 = ROOT / "scripts" / "luyen_thi" / "hsk2"

SOURCE_SCRIPT = (
    HSK2 / "extract_remaining_de_07.py"
)

DATA = HSK2 / "data" / "de_09"
OUTPUT = HSK2 / "output" / "de_09"

ANSWER_JSON = DATA / "de_09_dap_an.json"

QUESTION_DIR = OUTPUT / "questions"
GROUP_DIR = OUTPUT / "groups"

MANIFEST_JSON = (
    DATA / "hinh_60_cau_ung_vien.json"
)

HTML_FILE = OUTPUT / "kiem_tra_60_cau.html"

EXAM_CODE = "H21331"


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
# 3. DAP AN GOC CUA H21331
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

    result = {}

    for row_index, row in enumerate(EXPECTED_ROWS):

        values = row.split()

        if len(values) != 5:
            raise RuntimeError(
                "Bang dap an goc khong hop le."
            )

        for offset, answer in enumerate(values):

            number = row_index * 5 + offset + 1

            result[number] = answer

    if len(result) != 60:
        raise RuntimeError(
            "Bang dap an goc khong du 60 cau."
        )

    return result


EXPECTED_ANSWERS = build_expected_answers()


# =====================================================
# 4. CAC HAM HO TRO
# =====================================================

def load_json(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


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


def file_hash(path):

    digest = hashlib.sha256()

    with path.open("rb") as f:

        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def extract_pdf_answers(page):

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

        if not 1 <= number <= 60:
            continue

        if number in answers:
            raise RuntimeError(
                f"Trung dap an cau {number} trong PDF."
            )

        answers[number] = answer

    if set(answers) != set(range(1, 61)):
        raise RuntimeError(
            "PDF dap an khong du 60 cau."
        )

    return answers


# =====================================================
# 5. KIEM TRA DU LIEU NGUON
# =====================================================

def check_sources():

    if not SOURCE_SCRIPT.is_file():
        raise FileNotFoundError(
            "Thieu script goc De 7:\n"
            + str(SOURCE_SCRIPT)
        )

    answer_data = load_json(ANSWER_JSON)

    if answer_data.get("so_de") != 9:
        raise RuntimeError(
            "JSON dap an khong phai De 9."
        )

    if answer_data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "JSON dap an khong phai H21331."
        )

    answers = answer_data.get("dap_an", {})

    if set(answers) != {
        str(n) for n in range(1, 61)
    }:
        raise RuntimeError(
            "JSON dap an chua du 60 cau."
        )

    # Doi chieu JSON voi 60 dap an goc.
    for number in range(1, 61):

        actual = str(
            answers[str(number)]
        ).strip()

        expected = EXPECTED_ANSWERS[number]

        if actual != expected:
            raise RuntimeError(
                f"Dap an cau {number} sai: "
                f"JSON={actual}, goc={expected}"
            )

    pdf_value = answer_data.get("file_pdf")
    answer_value = answer_data.get("file_dap_an")

    if not pdf_value or not answer_value:
        raise RuntimeError(
            "JSON thieu duong dan hai file PDF."
        )

    pdf_file = Path(pdf_value)
    answer_pdf = Path(answer_value)

    if not pdf_file.is_file():
        raise FileNotFoundError(pdf_file)

    if not answer_pdf.is_file():
        raise FileNotFoundError(answer_pdf)

    # ================================================
    # 6. KIEM TRA PDF DE THI
    # ================================================

    with fitz.open(pdf_file) as doc:

        if len(doc) != 14:
            raise RuntimeError(
                f"PDF co {len(doc)} trang, "
                "H21331 phai co 14 trang."
            )

        cover = normalize_code(
            doc[0].get_text("text")
        )

        if EXAM_CODE not in cover:
            raise RuntimeError(
                "Trang bia khong phai H21331."
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

            text = unicodedata.normalize(
                "NFKC",
                doc[page_no - 1].get_text("text")
            )

            pattern = (
                rf"第\s*{first}\s*[-–—]\s*"
                rf"{last}\s*题"
            )

            if not re.search(pattern, text):
                raise RuntimeError(
                    f"Trang PDF {page_no} "
                    f"khong co nhom {first}-{last}."
                )

        page_8_text = doc[7].get_text("text")

        if re.search(
            r"第\s*(36|41|46|51|56)\s*[-–—]",
            page_8_text
        ):
            raise RuntimeError(
                "Trang 8 co cau hoi, "
                "khong dung bo cuc H21331."
            )

    # ================================================
    # 7. KIEM TRA PDF DAP AN RIENG
    # ================================================

    with fitz.open(answer_pdf) as doc:

        if len(doc) != 1:
            raise RuntimeError(
                "PDF dap an phai co 1 trang."
            )

        code = normalize_code(
            doc[0].get_text("text")
        )

        if EXAM_CODE not in code:
            raise RuntimeError(
                "PDF dap an khong phai H21331."
            )

        pdf_answers = extract_pdf_answers(
            doc[0]
        )

    for number in range(1, 61):

        if pdf_answers[number] != EXPECTED_ANSWERS[number]:
            raise RuntimeError(
                f"Cau {number} khong khop PDF dap an."
            )

    # ================================================
    # 8. BAO VE 10 ANH DA HOAN THANH
    # ================================================

    first_hashes = {}

    for number in range(1, 11):

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if not path.is_file():
            raise FileNotFoundError(
                f"Thieu anh cau {number}: {path}"
            )

        first_hashes[number] = file_hash(path)

    print("\n===== KIEM TRA NGUON =====")
    print("Ma de: H21331")
    print("PDF de thi: 14 trang")
    print("PDF dap an: 1 trang")
    print("Trang 8: bo qua")
    print("Dap an: 60/60 KHOP")
    print("Anh dau tien: 10/10")

    return pdf_file, first_hashes


# =====================================================
# 9. SU DUNG LAI THUAT TOAN DE 7
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
        value for value in required
        if value not in source
    ]

    if missing:
        raise RuntimeError(
            "Script De 7 khac phien ban "
            "da su dung, khong tu chuyen doi.\n"
            "Thieu:\n"
            + "\n".join(missing)
        )

    # Chi chuyen doi code trong bo nho.
    # Khong ghi de script De 7.

    converted = source

    converted = converted.replace(
        "H21329",
        EXAM_CODE
    )

    converted = converted.replace(
        "de_07",
        "de_09"
    )

    converted = converted.replace(
        '"Đề HSK 2 số 7.pdf"',
        repr(pdf_file.name)
    )

    converted = converted.replace(
        'get("so_de") != 7',
        'get("so_de") != 9'
    )

    converted = converted.replace(
        '"so_de": 7',
        '"so_de": 9'
    )

    converted = converted.replace(
        "DE 7",
        "DE 9"
    )

    converted = converted.replace(
        "De 7",
        "De 9"
    )

    converted = converted.replace(
        "Đề 7",
        "Đề 9"
    )

    # Khong cho phep con tham chieu De 7.
    if (
        "H21329" in converted
        or "de_07" in converted
        or 'get("so_de") != 7' in converted
        or '"so_de": 7' in converted
    ):
        raise RuntimeError(
            "Con tham chieu De 7 trong code."
        )

    program = compile(
        converted,
        str(SOURCE_SCRIPT),
        "exec"
    )

    print("\n===== TACH CAU 11-60 =====")
    print("Su dung thuat toan De 7 da hoat dong.")
    print("PDF:", pdf_file.name)

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
    }

    exec(program, namespace)


# =====================================================
# 10. KIEM TRA KET QUA SAU KHI TACH
# =====================================================

def verify_results(first_hashes):

    # Kiem tra 60 anh cau hoi.
    for number in range(1, 61):

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if not path.is_file():
            raise FileNotFoundError(path)

        if path.stat().st_size == 0:
            raise RuntimeError(
                f"Anh cau {number} bi rong."
            )

    # Dam bao 10 anh dau khong bi thay doi.
    for number, old_hash in first_hashes.items():

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if file_hash(path) != old_hash:
            raise RuntimeError(
                f"Anh cau {number} da thay doi."
            )

    # Kiem tra 6 bang lua chon.
    for group in GROUP_PAGES:

        path = GROUP_DIR / f"{group}.png"

        if not path.is_file():
            raise FileNotFoundError(path)

        if path.stat().st_size == 0:
            raise RuntimeError(
                f"Bang {group} bi rong."
            )

    manifest = load_json(MANIFEST_JSON)

    if manifest.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "Ma de trong manifest sai."
        )

    if manifest.get("so_de") != 9:
        raise RuntimeError(
            "Manifest khong phai De 9."
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

    # Kiem tra trang PDF cua tung cau.
    for page_no, numbers in PAGE_QUESTIONS.items():

        for number in numbers:

            actual_page = (
                images[str(number)].get("trang_pdf")
            )

            if actual_page != page_no:
                raise RuntimeError(
                    f"Cau {number} sai trang PDF: "
                    f"{actual_page}, can {page_no}"
                )

    for group, page_no in GROUP_PAGES.items():

        actual = groups[group].get("trang_pdf")

        if actual != page_no:
            raise RuntimeError(
                f"Bang {group} sai trang PDF."
            )

    if not HTML_FILE.is_file():
        raise FileNotFoundError(HTML_FILE)

    html_content = HTML_FILE.read_text(
        encoding="utf-8"
    )

    if EXAM_CODE not in html_content:
        raise RuntimeError(
            "HTML khong co ma H21331."
        )

    if "H21329" in html_content:
        raise RuntimeError(
            "HTML van chua ma De 7."
        )

    print("\n" + "=" * 60)
    print("KIEM TRA HOAN TAT")
    print("=" * 60)

    print("Ma de: H21331")
    print("So de: 9")
    print("Anh cau hoi: 60/60")
    print("Bang lua chon: 6/6")
    print("Dap an: 60/60")
    print("Anh cau 1-10: KHONG THAY DOI")
    print("Trang 8: DA BO QUA")

    print(f"\nJSON: {MANIFEST_JSON}")
    print(f"HTML: {HTML_FILE}")
    print("\nChua thay doi SQL Server.")


# =====================================================
# 11. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK2 DE 9")
    print("TACH 60 CAU - H21331")
    print("=" * 60)

    pdf_file, first_hashes = check_sources()

    run_extraction(pdf_file)

    verify_results(first_hashes)


if __name__ == "__main__":
    main()
