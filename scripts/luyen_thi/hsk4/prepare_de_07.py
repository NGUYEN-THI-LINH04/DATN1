
# -*- coding: utf-8 -*-
"""
MOC HAN - HSK4 DE 07 (H41327)
BUOC 1 - CHUAN BI 100 DAP AN

Ke thua quy trinh HSK4 De 5.

- PDF de thi 16 trang: H41007.pdf.
- PDF dap an 2 trang: H41007_dap_an.pdf.
- Doc 85 dap an Nghe/Doc tu PDF dap an, trang 1.
- Kiem tra cau Viet 86-95 voi PDF de, trang 15.
- Lay 5 cau mau Viet tranh tu PDF dap an, trang 2.
- Tao de_07_dap_an.json.

KHONG ket noi SQL.
KHONG sua de da nhap.
KHONG sua cac bang Bai tap.
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

DATA = BASE / "hsk4" / "data" / "de_07"

PDF_FILE = SOURCE / "H41007.pdf"

ANSWER_PDF = SOURCE / "H41007_dap_an.pdf"

MP3_FILE = SOURCE / "H41007.mp3"

ANSWER_FILE = DATA / "de_07_dap_an.json"

CODE = "H41327"

DE_NUMBER = 7

WORDS = {
    96: "轻",
    97: "答案",
    98: "钥匙",
    99: "激动",
    100: "聊天儿",
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
            f"Trung dap an Viet {number}"
        )

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )

        answer = re.sub(
            r"\s+",
            "",
            text[match.end():end]
        )

        require(
            bool(answer),
            f"Dap an cau {number} rong"
        )

        result[key] = answer

    require(
        set(result) == {
            str(n)
            for n in range(first, last + 1)
        },
        f"PDF dap an khong du cau {first}-{last}"
    )

    return result


# =====================================================
# 4. DOC 85 DAP AN NGHE VA DOC
# =====================================================

def find_official_mcq(answer_doc):

    # PDF dap an rieng - trang 1
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
            f"Cau {number} sai dang dap an: {value}"
        )

        answers[key] = value

    require(
        set(answers) == {
            str(n) for n in range(1, 86)
        },
        "PDF dap an trang 1 khong du "
        "85 cau Nghe/Doc"
    )

    return answers


# =====================================================
# 5. TACH CUM TU VIET 86-95 TU PDF DE THI
# =====================================================

def tokens_from_pdf(doc):

    tokens = {}

    # Trang 15 PDF de thi
    text = doc[14].get_text("text")

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
            value.strip()
            for value in re.split(
                r"\s{2,}",
                match.group(2).strip()
            )
            if value.strip()
        ]

        require(
            3 <= len(values) <= 9,
            f"Cau {number} sai cum tu: {values}"
        )

        tokens[number] = values

    require(
        set(tokens) == set(range(86, 96)),
        "PDF de thi trang 15 khong du "
        "10 cau Viet sap xep"
    )

    return tokens


# =====================================================
# 6. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 07 - BUOC 1")
    print("CHUAN BI DAP AN H41327")
    print("=" * 60)

    # ================================================
    # 7. KIEM TRA 3 FILE NGUON
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
            len(exam) == 16,
            "H41007.pdf phai co 16 trang"
        )

        require(
            len(key_doc) == 2,
            "H41007_dap_an.pdf phai co 2 trang"
        )

        require(
            CODE in exam[0].get_text("text")
            and CODE in exam[15].get_text("text"),
            "PDF de thi khong phai H41327"
        )

        require(
            CODE in key_doc[0].get_text("text")
            and "卷答案" in key_doc[0].get_text("text"),
            "PDF dap an khong phai H41327"
        )

        # ============================================
        # 9. DOC 85 DAP AN NGHE VA DOC
        # ============================================

        answers = find_official_mcq(key_doc)

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

                f"Trang 16 thieu cau {number}: {word}"
            )

        # ============================================
        # 12. DOC DAP AN VIET TU PDF RIENG
        # ============================================

        text = key_doc[1].get_text("text")

        require(
            "第一部分" in text
            and "第二部分" in text,
            "PDF dap an trang 2 "
            "thieu hai phan Viet"
        )

        part_one, part_two = text.split(
            "第二部分",
            1
        )

        official_writing = numbered_answers(
            part_one,
            86,
            95
        )

        official_open = numbered_answers(
            part_two,
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
            value.strip()
            for value in re.split(
                r"[/／]",
                official_writing[key]
            )
            if value.strip()
        ]

        # PDF De 7 khong liet ke
        # dap an thay the.
        require(
            len(variants) == 1,
            f"Cau {number} co dap an thay the. "
            "Can kiem tra lai PDF"
        )

        possible = {
            compact("".join(order))
            for order in permutations(
                tokens[number]
            )
        }

        require(
            compact(variants[0]) in possible,

            f"Cau {number}: dap an khong "
            "ghep duoc voi cac cum tu.\n"
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
            f"Cau {number}: cau mau "
            f"khong co tu {WORDS[number]}"
        )

        references[key] = [sentence]

        # Dap an theo tranh se chua
        # trong dap_an_tham_khao_viet_mo.
        answers[key] = None

    require(
        set(answers) == {
            str(n) for n in range(1, 101)
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

        # PDF de thi khong chua
        # cac trang loi thoai rieng.
        "trang_loi_thoai": [],

        # Danh so trang trong PDF dap an rieng.
        "trang_dap_an": [1, 2],

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
    # 16. KIEM TRA KHONG GHI DE JSON CU
    # ================================================

    content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    require(
        not ANSWER_FILE.exists()
        or ANSWER_FILE.read_bytes() == content,

        "de_07_dap_an.json da ton tai "
        "voi noi dung khac.\n"
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
    print("HOAN THANH HSK4 DE 07 - BUOC 1")
    print("=" * 60)

    print("Ma de goc: H41327")
    print("Ten hien thi: De 7")

    print("Nghe: 45/45")
    print("Doc: 40/40")
    print("Viet: 15/15")

    print("Dap an thay the: KHONG CO TRONG PDF")

    print(
        "Tu goi y:",
        ", ".join(WORDS.values())
    )

    print("Viet theo tranh: TU DONG THEO MAU")

    print("PDF de thi: 16 trang")
    print("PDF dap an rieng: 2 trang")

    print(f"\nJSON: {ANSWER_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
