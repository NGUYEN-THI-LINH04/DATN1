
# -*- coding: utf-8 -*-
"""
MOC HAN - HSK4 DE 08 (H41328)
BUOC 1 - CHUAN BI 100 DAP AN TU 2 PDF

Ke thua quy trinh HSK4 De 7.

- H41008.pdf: 16 trang de thi.
- H41008_dap_an.pdf: 18 trang.
- Dap an Nghe/Doc nam o trang 17.
- Dap an Viet nam o trang 18.
- Kiem tra 10 cau Viet sap xep voi PDF de.
- Giu 5 cau Viet tranh cham TU DONG.
- Loai bo watermark trong PDF dap an.
- Tao de_08_dap_an.json.

KHONG ket noi SQL.
KHONG sua cac de cu.
KHONG sua cac bang Bai tap.
"""

from itertools import permutations
from pathlib import Path

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

SOURCE = (
    BASE / "source" / "De_HSK" / "HSK4"
)

DATA = (
    BASE / "hsk4" / "data" / "de_08"
)

PDF_FILE = SOURCE / "H41008.pdf"

ANSWER_PDF = SOURCE / "H41008_dap_an.pdf"

MP3_FILE = SOURCE / "H41008.mp3"

ANSWER_FILE = DATA / "de_08_dap_an.json"

CODE = "H41328"

DE_NUMBER = 8

WORDS = {
    96: "袜子",
    97: "加班",
    98: "估计",
    99: "脏",
    100: "看法",
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
# 3. LOAI BO WATERMARK TRONG PDF DAP AN
# =====================================================

def clean_answer_text(text):

    return re.sub(
        r"(?im)^\s*"
        r"(?:www\.)?tiengtrungnet\.com"
        r"\s*$",
        "",
        text
    )


# =====================================================
# 4. DOC DAP AN VIET CO SO CAU
# =====================================================

def numbered_answers(text, first, last):

    text = clean_answer_text(text)

    matches = list(
        re.finditer(
            r"(?m)^\s*(\d{2,3})"
            r"\s*[.．、]",
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
            str(n)
            for n in range(first, last + 1)
        },

        f"PDF thieu dap an Viet {first}-{last}"
    )

    return result


# =====================================================
# 5. DOC 85 DAP AN NGHE VA DOC
# =====================================================

def official_mcq(answer_doc):

    # Trang 17 cua PDF 18 trang.
    # Trong PyMuPDF, chi so trang bat dau tu 0.

    text = clean_answer_text(
        answer_doc[16].get_text("text")
    )

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
            f"Trung dap an Nghe/Doc cau {number}"
        )

        if number <= 10:

            valid = value in ("√", "×")

        elif 46 <= number <= 55:

            valid = value in "ABCDEF"

        elif 56 <= number <= 65:

            valid = (
                len(value) == 3
                and set(value) == set("ABC")
            )

        else:

            valid = value in "ABCD"

        require(
            valid,
            f"Cau {number} sai dinh dang "
            f"dap an: {value}"
        )

        answers[key] = value

    require(
        set(answers) == {
            str(n) for n in range(1, 86)
        },

        "PDF dap an trang 17 "
        "khong du 85 dap an Nghe/Doc"
    )

    return answers


# =====================================================
# 6. TACH CUM TU VIET 86-95
# =====================================================

def tokens_from_pdf(exam):

    tokens = {}

    # Trang 15 cua PDF de thi.
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

            f"Cau {number} sai so cum tu: "
            f"{values}"
        )

        tokens[number] = values

    require(
        set(tokens) == set(range(86, 96)),

        "Trang 15 khong du 10 cau Viet: "
        f"{sorted(tokens)}"
    )

    return tokens


# =====================================================
# 7. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 08 - BUOC 1")
    print("CHUAN BI DAP AN H41328")
    print("=" * 60)

    # ================================================
    # 8. KIEM TRA FILE NGUON
    # ================================================

    for path in (
        PDF_FILE,
        ANSWER_PDF,
        MP3_FILE
    ):
        require_file(path)

    # ================================================
    # 9. KIEM TRA HAI PDF
    # ================================================

    with fitz.open(PDF_FILE) as exam, \
         fitz.open(ANSWER_PDF) as answer_doc:

        require(
            len(exam) == 16,
            "H41008.pdf phai co 16 trang"
        )

        require(
            len(answer_doc) == 18,
            "H41008_dap_an.pdf phai co 18 trang"
        )

        require(
            CODE in exam[0].get_text("text")
            and CODE in exam[15].get_text("text"),

            "PDF de thi khong phai H41328"
        )

        require(
            CODE in answer_doc[0].get_text("text")
            and CODE in answer_doc[16].get_text("text")
            and "卷答案" in answer_doc[16].get_text("text"),

            "PDF dap an khong phai H41328 "
            "hoac sai trang 17"
        )

        # ============================================
        # 10. DOC 85 DAP AN NGHE VA DOC
        # ============================================

        answers = official_mcq(answer_doc)

        # ============================================
        # 11. TACH CUM TU VIET 86-95
        # ============================================

        tokens = tokens_from_pdf(exam)

        # ============================================
        # 12. KIEM TRA TU GOI Y 96-100
        # ============================================

        page16 = exam[15].get_text("text")

        for number, word in WORDS.items():

            require(
                re.search(
                    rf"(?<!\d){number}"
                    r"\s*[.．、]",
                    page16
                )
                and word in page16,

                f"Trang 16 thieu cau {number} "
                f"hoac tu goi y {word}"
            )

        # ============================================
        # 13. DOC DAP AN VIET TRANG 18
        # ============================================

        answer_text = clean_answer_text(
            answer_doc[17].get_text("text")
        )

        require(
            "第一部分" in answer_text
            and "第二部分" in answer_text,

            "Trang 18 thieu hai phan Viet"
        )

        first_part, second_part = (
            answer_text.split(
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
    # 14. KIEM TRA VIET SAP XEP 86-95
    # ================================================

    alternatives = {}

    for number in range(86, 96):

        key = str(number)

        variants = [
            value.strip()

            for value in re.split(
                r"[/／]",
                official_writing[key]
            )

            if value.strip()
        ]

        # PDF De 8 khong liet ke
        # dap an thay the.

        require(
            len(variants) == 1,

            f"Cau {number} co dap an thay the "
            "can doi chieu PDF"
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
            "dap an tu cum tu.\n"

            f"Dap an: {variants[0]}\n"
            f"Cum tu: {tokens[number]}"
        )

        answers[key] = variants[0]

    # ================================================
    # 15. VIET THEO TRANH 96-100
    # ================================================

    references = {}

    for number in range(96, 101):

        key = str(number)

        sentence = official_open[key]

        require(
            WORDS[number] in sentence,

            f"Cau {number} thieu tu goi y "
            f"{WORDS[number]} trong dap an mau"
        )

        references[key] = [sentence]

        # Cau Viet theo tranh se duoc
        # cham tu dong theo dap an tham khao.

        answers[key] = None

    require(
        set(answers) == {
            str(n) for n in range(1, 101)
        },

        "Chua du 100 dap an"
    )

    # ================================================
    # 16. TAO JSON BUOC 1
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

        # Trang 17-18 trong PDF dap an 18 trang.
        "trang_dap_an": [17, 18],

        "nguon_dap_an": "pdf_rieng",

        "file_pdf": str(PDF_FILE),

        "file_dap_an_pdf": str(ANSWER_PDF),

        "file_mp3": str(MP3_FILE),

        "dap_an": answers,

        "dap_an_thay_the": alternatives,

        "cum_tu_viet_sap_xep": {
            str(n): tokens[n]
            for n in range(86, 96)
        },

        "tu_cho_san_viet_mo": {
            str(n): WORDS[n]
            for n in range(96, 101)
        },

        "dap_an_tham_khao_viet_mo": references,

        "cau_can_cham_thu_cong": [],

        "che_do_cham_viet_mo": (
            "cham_tu_dong_theo_mau"
        )
    }

    # ================================================
    # 17. KIEM TRA KHONG GHI DE JSON CU
    # ================================================

    content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    require(
        not ANSWER_FILE.exists()
        or ANSWER_FILE.read_bytes() == content,

        "de_08_dap_an.json da ton tai "
        "voi noi dung khac.\n"
        "KHONG ghi de: "
        + str(ANSWER_FILE)
    )

    # ================================================
    # 18. LUU JSON
    # ================================================

    if not ANSWER_FILE.exists():

        ANSWER_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        ANSWER_FILE.write_bytes(content)

    # ================================================
    # 19. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH HSK4 DE 08 - BUOC 1")
    print("=" * 60)

    print("Ma de goc: H41328")
    print("Ten hien thi: De 8")

    print("Nghe: 45/45")
    print("Doc: 40/40")
    print("Viet: 15/15")

    print("Dap an thay the: KHONG CO TRONG PDF")

    print(
        "Tu goi y: "
        + ", ".join(WORDS.values())
    )

    print("Viet theo tranh: TU DONG THEO MAU")

    print("PDF de thi: 16 trang")
    print("PDF dap an: 18 trang")
    print("Trang dap an: 17-18")

    print(f"\nJSON: {ANSWER_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
