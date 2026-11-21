
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 8 (H21330)

BUOC 2:
- Tai su dung bo tach anh De 7 da hoat dong.
- Giu nguyen 10 anh dau cua De 8.
- Tach cau 11-60 theo PDF H21330.
- Bo qua trang 8.
- Tao 6 bang lua chon chung.
- Tao JSON thong tin anh.
- Tao HTML kiem tra du 60 cau.

Khong thay doi De 7.
Khong thay doi SQL Server.
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

DATA = HSK2 / "data" / "de_08"
OUTPUT = HSK2 / "output" / "de_08"

ANSWER_JSON = DATA / "de_08_dap_an.json"

QUESTION_DIR = OUTPUT / "questions"
GROUP_DIR = OUTPUT / "groups"

MANIFEST_JSON = (
    DATA / "hinh_60_cau_ung_vien.json"
)

HTML_FILE = OUTPUT / "kiem_tra_60_cau.html"

EXAM_CODE = "H21330"


# =====================================================
# 2. SO DO TRANG CUA DE 8
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
# 3. DAP AN DOI CHIEU TU PDF H21330
# =====================================================

EXPECTED_ROWS = [
    "√ √ × √ ×",
    "× √ × √ ×",
    "F A C B E",
    "A D C E B",
    "A C B B C",
    "B B A C A",
    "C A B C A",
    "C A E F B",
    "F A B D C",
    "× √ × × √",
    "D A B F C",
    "A C D B E",
]

EXPECTED_ANSWERS = {}

for row_index, row in enumerate(EXPECTED_ROWS):
    values = row.split()

    if len(values) != 5:
        raise RuntimeError(
            "Bang dap an doi chieu sai."
        )

    for offset, answer in enumerate(values):
        number = row_index * 5 + offset + 1
        EXPECTED_ANSWERS[number] = answer


# =====================================================
# 4. HAM HO TRO
# =====================================================

def load_json(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open(
        "r",
        encoding="utf-8-sig"
    ) as file:
        return json.load(file)


def file_hash(path):

    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def normalized_code(value):

    value = unicodedata.normalize(
        "NFKC",
        str(value)
    ).upper()

    return re.sub(
        r"[^A-Z0-9]",
        "",
        value
    )


# =====================================================
# 5. KIEM TRA DU LIEU DE 8
# =====================================================

def check_sources():

    if not SOURCE_SCRIPT.is_file():
        raise FileNotFoundError(
            "Khong tim thay script tach anh De 7:\n"
            + str(SOURCE_SCRIPT)
        )

    answer_data = load_json(ANSWER_JSON)

    if answer_data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "Ma de trong JSON khong phai H21330."
        )

    if answer_data.get("so_de") != 8:
        raise RuntimeError(
            "JSON dap an khong phai De 8."
        )

    answers = answer_data.get("dap_an", {})

    if set(answers) != {
        str(n) for n in range(1, 61)
    }:
        raise RuntimeError(
            "JSON chua du 60 dap an."
        )

    # Doi chieu dap an voi PDF ma nguoi dung da gui.
    for number in range(1, 61):

        actual = str(
            answers[str(number)]
        ).strip()

        expected = EXPECTED_ANSWERS[number]

        if actual != expected:
            raise RuntimeError(
                f"Dap an cau {number} khong khop: "
                f"JSON={actual}, PDF={expected}"
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

    if not pdf_file.is_file():
        raise FileNotFoundError(pdf_file)

    if not answer_pdf.is_file():
        raise FileNotFoundError(answer_pdf)

    with fitz.open(pdf_file) as doc:

        if len(doc) != 14:
            raise RuntimeError(
                "PDF De 8 phai co 14 trang."
            )

        cover = normalized_code(
            doc[0].get_text("text")
        )

        if EXAM_CODE not in cover:
            raise RuntimeError(
                "Trang bia khong phai H21330."
            )

        page_9 = unicodedata.normalize(
            "NFKC",
            doc[8].get_text("text")
        )

        page_14 = unicodedata.normalize(
            "NFKC",
            doc[13].get_text("text")
        )

        if not re.search(
            r"第\s*36\s*[-–]\s*40\s*题",
            page_9
        ):
            raise RuntimeError(
                "Trang 9 khong co cau 36-40."
            )

        if not re.search(
            r"第\s*56\s*[-–]\s*60\s*题",
            page_14
        ):
            raise RuntimeError(
                "Trang 14 khong co cau 56-60."
            )

    with fitz.open(answer_pdf) as doc:

        if len(doc) != 1:
            raise RuntimeError(
                "PDF dap an phai co 1 trang."
            )

        code = normalized_code(
            doc[0].get_text("text")
        )

        if EXAM_CODE not in code:
            raise RuntimeError(
                "PDF dap an khong phai H21330."
            )

    # Luu hash 10 anh da hoan thanh.
    first_hashes = {}

    for number in range(1, 11):

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if not path.is_file():
            raise FileNotFoundError(
                f"Thieu anh cau {number}."
            )

        first_hashes[number] = file_hash(path)

    print("\n===== KIEM TRA NGUON =====")
    print("Ma de: H21330")
    print("PDF de thi: 14 trang")
    print("PDF dap an: 1 trang rieng")
    print("Trang 8: bo qua")
    print("Dap an: 60/60 KHOP")
    print("Anh dau tien: 10/10")

    return pdf_file, first_hashes


# =====================================================
# 6. TAI SU DUNG BO TACH ANH DE 7
# =====================================================

def run_extraction(pdf_file):

    source = SOURCE_SCRIPT.read_text(
        encoding="utf-8-sig"
    )

    required = [
        "H21329",
        "de_07",
        "Đề HSK 2 số 7.pdf",
        'get("so_de") != 7',
        '"so_de": 7',
    ]

    missing = [
        value
        for value in required
        if value not in source
    ]

    if missing:
        raise RuntimeError(
            "Script De 7 khac phien ban da su dung.\n"
            "Khong tu chuyen doi de tranh loi.\n"
            "Khong tim thay:\n"
            + "\n".join(missing)
        )

    # Chi xu ly ban sao ma nguon trong bo nho.
    # Khong sua file extract_remaining_de_07.py.
    converted = source

    converted = converted.replace(
        "H21329",
        EXAM_CODE
    )

    converted = converted.replace(
        "de_07",
        "de_08"
    )

    converted = converted.replace(
        '"Đề HSK 2 số 7.pdf"',
        repr(pdf_file.name)
    )

    converted = converted.replace(
        'get("so_de") != 7',
        'get("so_de") != 8'
    )

    converted = converted.replace(
        '"so_de": 7',
        '"so_de": 8'
    )

    converted = converted.replace(
        "DE 7",
        "DE 8"
    )

    converted = converted.replace(
        "De 7",
        "De 8"
    )

    converted = converted.replace(
        "Đề 7",
        "Đề 8"
    )

    if (
        "H21329" in converted
        or "de_07" in converted
        or '"so_de": 7' in converted
    ):
        raise RuntimeError(
            "Con tham chieu De 7 sau chuyen doi."
        )

    # Kiem tra cu phap truoc khi thuc thi.
    program = compile(
        converted,
        str(Path(__file__).resolve()),
        "exec"
    )

    print("\n===== TACH CAU 11-60 =====")
    print("Su dung thuat toan De 7 da kiem tra.")
    print("Nguon PDF:", pdf_file.name)

    namespace = {
        "__name__": "__main__",
        "__file__": str(
            Path(__file__).resolve()
        ),
    }

    exec(program, namespace)


# =====================================================
# 7. KIEM TRA KET QUA
# =====================================================

def verify_results(first_hashes):

    # Kiem tra 60 anh.
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

    # Bao dam 10 anh dau khong thay doi.
    for number, old_hash in first_hashes.items():

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if file_hash(path) != old_hash:
            raise RuntimeError(
                f"Anh cau {number} da bi thay doi."
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
            "Ma de trong JSON hinh sai."
        )

    if manifest.get("so_de") != 8:
        raise RuntimeError(
            "JSON hinh khong phai De 8."
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
            "Manifest khong du 6 bang."
        )

    # Doi chieu vi tri trang PDF.
    for page_no, numbers in PAGE_QUESTIONS.items():

        for number in numbers:

            actual_page = (
                images[str(number)]
                .get("trang_pdf")
            )

            if actual_page != page_no:
                raise RuntimeError(
                    f"Cau {number} sai trang: "
                    f"{actual_page}, can {page_no}"
                )

    for group, page_no in GROUP_PAGES.items():

        actual_page = (
            groups[group].get("trang_pdf")
        )

        if actual_page != page_no:
            raise RuntimeError(
                f"Bang {group} sai trang."
            )

    if not HTML_FILE.is_file():
        raise FileNotFoundError(HTML_FILE)

    html_content = HTML_FILE.read_text(
        encoding="utf-8"
    )

    if EXAM_CODE not in html_content:
        raise RuntimeError(
            "HTML khong dung ma de H21330."
        )

    if "H21329" in html_content:
        raise RuntimeError(
            "HTML van hien thi ma De 7."
        )

    print("\n" + "=" * 60)
    print("KIEM TRA HOAN TAT")
    print("=" * 60)

    print("Ma de: H21330")
    print("So de: 8")
    print("Anh cau hoi: 60/60")
    print("Bang lua chon: 6/6")
    print("Dap an: 60/60")
    print("Anh cau 1-10: KHONG THAY DOI")
    print("Trang 8: DA BO QUA")

    print(f"\nJSON: {MANIFEST_JSON}")
    print(f"HTML: {HTML_FILE}")

    print("\nChua thay doi SQL Server.")


# =====================================================
# 8. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK2 DE 8")
    print("TACH 60 CAU - H21330")
    print("=" * 60)

    pdf_file, first_hashes = check_sources()

    run_extraction(pdf_file)

    verify_results(first_hashes)


if __name__ == "__main__":
    main()
