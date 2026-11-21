
# -*- coding: utf-8 -*-
"""
MOC HAN - HSK4 DE 09 (H41329)
BUOC 1 - CHUAN BI DAP AN

Ke thua cau truc prepare_de_07.py:
- PDF de 16 trang, PDF dap an rieng 2 trang.
- Doc 85 dap an Nghe/Doc va 15 dap an Viet.
- Doi chieu 10 cau Viet sap xep voi cum tu trong PDF.
- 5 cau Viet tranh cham tu dong theo dap an mau.
- Khong nhap SQL, khong sua de cu.
"""

from pathlib import Path
from itertools import permutations

import json
import os
import re
import unicodedata

import fitz


# =====================================================
# 1. CAU HINH
# =====================================================

ROOT = Path(
    os.environ.get(
        "MOC_HAN_ROOT",
        r"D:\DATN1"
    )
)

BASE = ROOT / "scripts" / "luyen_thi"

SOURCE = BASE / "source" / "De_HSK" / "HSK4"

DATA = BASE / "hsk4" / "data" / "de_09"

PDF_FILE = SOURCE / "H41009.pdf"

ANSWER_PDF = SOURCE / "H41009_dap_an.pdf"

MP3_FILE = SOURCE / "H41009.mp3"

ANSWER_FILE = DATA / "de_09_dap_an.json"

CODE = "H41329"
DE_NUMBER = 9

WORDS = {
    96: "肚子",
    97: "擦",
    98: "打折",
    99: "果汁",
    100: "重",
}


# =====================================================
# 2. HAM HO TRO
# =====================================================

def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def require_file(path):
    require(
        path.is_file()
        and path.stat().st_size > 0,

        f"Thieu file hoac file rong: {path}"
    )

    return path


def compact(value):
    value = unicodedata.normalize(
        "NFKC",
        str(value)
    )

    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "",
        value
    )


# =====================================================
# 3. DOC DAP AN VIET CO SO CAU
# =====================================================

def numbered_answers(text, first, last):

    matches = list(
        re.finditer(
            r"(?m)^\s*(\d{2,3})\s*[.．、]",
            text
        )
    )

    result = {}

    for index, match in enumerate(matches):

        number = int(match.group(1))

        if not first <= number <= last:
            continue

        key = str(number)

        require(
            key not in result,
            f"Trung dap an Viet cau {number}"
        )

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )

        value = re.sub(
            r"\s+",
            "",
            text[match.end():end]
        )

        require(
            bool(value),
            f"Dap an Viet cau {number} rong"
        )

        result[key] = value

    require(
        set(result) == {
            str(number)
            for number in range(first, last + 1)
        },

        f"PDF dap an thieu cau {first}-{last}"
    )

    return result


# =====================================================
# 4. DOC 85 DAP AN NGHE VA DOC
# =====================================================

def official_mcq(answer_doc):

    # PDF dap an rieng - trang 1.
    text = answer_doc[0].get_text("text")

    matches = re.findall(
        r"(?<!\d)"
        r"(\d{1,3})"
        r"\s*[.．、]\s*"
        r"([A-F√×]{1,3})"
        r"(?![A-Z])",
        text
    )

    answers = {}

    for number_text, value in matches:

        number = int(number_text)

        if not 1 <= number <= 85:
            continue

        key = str(number)

        require(
            key not in answers,
            f"Trung dap an cau {number}"
        )

        if number <= 10:
            valid = value in ("√", "×")

        elif number <= 45 or 66 <= number <= 85:
            valid = value in "ABCD"

        elif number <= 55:
            valid = value in "ABCDEF"

        else:
            valid = (
                len(value) == 3
                and set(value) == set("ABC")
            )

        require(
            valid,
            f"Cau {number}: sai dap an {value}"
        )

        answers[key] = value

    require(
        set(answers) == {
            str(number)
            for number in range(1, 86)
        },

        "PDF dap an trang 1 khong du "
        "85 dap an Nghe/Doc"
    )

    return answers


# =====================================================
# 5. TACH CUM TU VIET 86-95
# =====================================================

def tokens_from_pdf(exam):

    tokens = {}

    # Trang 15 PDF de thi.
    text = exam[14].get_text("text")

    for line in text.splitlines():

        match = re.match(
            r"^\s*(8[6-9]|9[0-5])"
            r"\s*[.．、]\s*(.+)$",
            line
        )

        if not match:
            continue

        number = int(match.group(1))

        require(
            number not in tokens,
            f"Trung cau Viet {number}"
        )

        # Tach theo 2 khoang trang tro len.
        # Giu cum "1084 公里" o cau 93.
        values = [
            item.strip()

            for item in re.split(
                r"\s{2,}",
                match.group(2).strip()
            )

            if item.strip()
        ]

        require(
            3 <= len(values) <= 9,

            f"Cau {number}: "
            f"sai so cum tu {values}"
        )

        tokens[number] = values

    require(
        set(tokens) == set(range(86, 96)),

        "PDF de trang 15 thieu "
        "10 cau Viet 86-95"
    )

    return tokens


# =====================================================
# 6. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 09 - BUOC 1")
    print("CHUAN BI DAP AN H41329")
    print("=" * 60)

    # ================================================
    # 7. KIEM TRA FILE NGUON
    # ================================================

    for path in (
        PDF_FILE,
        ANSWER_PDF,
        MP3_FILE
    ):
        require_file(path)

    # ================================================
    # 8. KIEM TRA HAI PDF
    # ================================================

    with fitz.open(PDF_FILE) as exam, \
         fitz.open(ANSWER_PDF) as key_doc:

        require(
            len(exam) == 16
            and len(key_doc) == 2,

            "PDF de phai co 16 trang, "
            "PDF dap an phai co 2 trang"
        )

        require(
            CODE in exam[0].get_text("text")
            and CODE in exam[15].get_text("text")
            and CODE in key_doc[0].get_text("text")
            and "卷答案" in key_doc[0].get_text("text"),

            "PDF de/dap an khong phai H41329"
        )

        # ============================================
        # 9. DOC 85 DAP AN NGHE VA DOC
        # ============================================

        answers = official_mcq(key_doc)

        # ============================================
        # 10. TACH CUM TU VIET 86-95
        # ============================================

        tokens = tokens_from_pdf(exam)

        # ============================================
        # 11. KIEM TRA TU GOI Y 96-100
        # ============================================

        page16 = exam[15].get_text("text")

        for number, word in WORDS.items():

            require(
                re.search(
                    rf"(?<!\d){number}\s*[.．、]",
                    page16
                )
                and word in page16,

                f"Trang 16 thieu cau {number} "
                f"hoac tu {word}"
            )

        # ============================================
        # 12. DOC DAP AN VIET TRANG 2
        # ============================================

        key_text = key_doc[1].get_text("text")

        require(
            "第一部分" in key_text
            and "第二部分" in key_text,

            "PDF dap an trang 2 "
            "thieu hai phan Viet"
        )

        first_part, second_part = (
            key_text.split(
                "第二部分",
                1
            )
        )

        official_writing = numbered_answers(
            first_part,
            86,
            95
        )

        official_open = numbered_answers(
            second_part,
            96,
            100
        )

    # ================================================
    # 13. KIEM TRA VIET SAP XEP 86-95
    # ================================================

    alternatives = {}

    for number in range(86, 96):

        key = str(number)

        variants = [
            item.strip()

            for item in re.split(
                r"[/／]",
                official_writing[key]
            )

            if item.strip()
        ]

        # De 9 khong co dap an thay the.
        require(
            len(variants) == 1,

            f"Cau {number} co nhieu dap an, "
            "can kiem tra PDF"
        )

        possible = {
            compact("".join(order))

            for order in permutations(
                tokens[number]
            )
        }

        require(
            compact(variants[0]) in possible,

            f"Cau {number} khong ghep duoc "
            "tu cac cum trong PDF:\n"

            f"Dap an: {variants[0]}\n"
            f"Cum tu: {tokens[number]}"
        )

        answers[key] = variants[0]

    # ================================================
    # 14. VIET THEO TRANH 96-100
    # ================================================

    references = {}

    for number in range(96, 101):

        key = str(number)

        sentence = official_open[key]

        require(
            WORDS[number] in sentence,

            f"Cau {number} thieu tu goi y "
            f"{WORDS[number]} trong cau mau"
        )

        references[key] = [sentence]

        # Dap an Viet mo nam trong:
        # dap_an_tham_khao_viet_mo.
        # Cham tu dong theo mau.
        answers[key] = None

    require(
        set(answers) == {
            str(number)
            for number in range(1, 101)
        },

        "Khong du 100 dap an"
    )

    # ================================================
    # 15. TAO JSON BUOC 1
    # ================================================

    result = {

        "ma_de_goc": CODE,

        "cap_hsk": 4,

        "so_de": DE_NUMBER,

        "tong_cau": 100,

        "so_cau_nghe": 45,
        "so_cau_doc": 40,
        "so_cau_viet": 15,

        "so_trang_pdf": 16,

        "trang_loi_thoai": [],

        # PDF dap an rieng co 2 trang.
        "trang_dap_an": [1, 2],

        "nguon_dap_an": "pdf_rieng",

        "file_pdf": str(PDF_FILE),

        "file_dap_an_pdf": str(ANSWER_PDF),

        "file_mp3": str(MP3_FILE),

        "dap_an": answers,

        "dap_an_thay_the": alternatives,

        "cum_tu_viet_sap_xep": {
            str(number): tokens[number]
            for number in range(86, 96)
        },

        "tu_cho_san_viet_mo": {
            str(number): WORDS[number]
            for number in range(96, 101)
        },

        "dap_an_tham_khao_viet_mo": references,

        "cau_can_cham_thu_cong": [],

        "che_do_cham_viet_mo": (
            "cham_tu_dong_theo_mau"
        )
    }

    # ================================================
    # 16. KHONG GHI DE JSON KHAC NOI DUNG
    # ================================================

    content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    require(
        not ANSWER_FILE.exists()
        or ANSWER_FILE.read_bytes() == content,

        "JSON da ton tai voi noi dung khac.\n"
        "KHONG ghi de: "
        + str(ANSWER_FILE)
    )

    # ================================================
    # 17. LUU JSON
    # ================================================

    if not ANSWER_FILE.exists():

        ANSWER_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        ANSWER_FILE.write_bytes(content)

    # ================================================
    # 18. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH HSK4 DE 09 - BUOC 1")
    print("=" * 60)

    print("Ma de goc: H41329")
    print("Ten hien thi: De 9")

    print("Nghe: 45/45")
    print("Doc: 40/40")
    print("Viet: 15/15")

    print("Dap an thay the: KHONG CO")

    print(
        "Tu goi y 96-100: "
        + ", ".join(WORDS.values())
    )

    print("Viet theo tranh: TU DONG THEO MAU")

    print("PDF de: 16 trang")
    print("PDF dap an: 2 trang")

    print(f"\nJSON: {ANSWER_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
