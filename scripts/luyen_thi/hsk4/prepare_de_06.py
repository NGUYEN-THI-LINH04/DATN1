
# -*- coding: utf-8 -*-
"""
MOC HAN - HSK4 DE 06

FILE NGUON: H41006.pdf
MA DE GOC THUC TE: H41008
TEN HIEN THI: De 6

BUOC 1 - CHUAN BI DAP AN TU PDF

Ke thua cau truc HSK4 De 5.

- Doc 85 dap an Nghe va Doc.
- Doc 15 dap an Viet.
- Kiem tra 10 cau Viet sap xep.
- Giu 5 tu goi y va cau mau 96-100.
- De nay khong co dap an thay the.
- Cau 96-100 cham TU DONG theo mau.
- Tao de_06_dap_an.json.

KHONG ket noi SQL Server.
KHONG sua cac de thi cu.
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

SOURCE = (
    BASE / "source" / "De_HSK" / "HSK4"
)

DATA = (
    BASE / "hsk4" / "data" / "de_06"
)

PDF_FILE = SOURCE / "H41006.pdf"
MP3_FILE = SOURCE / "H41006.mp3"

ANSWER_FILE = DATA / "de_06_dap_an.json"

# Ma goc ghi trong PDF, khong phai ten file.
CODE = "H41008"

# So thu tu hien thi tren Moc Han.
DE_NUMBER = 6

WORDS = {
    96: "困",
    97: "味道",
    98: "怀疑",
    99: "来得及",
    100: "肚子",
}


# =====================================================
# 2. HAM HO TRO
# =====================================================

def require(ok, message):

    if not ok:
        raise RuntimeError(message)


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
# 3. DOC DAP AN CO SO CAU TU TRANG 24
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

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )

        key = str(number)

        require(
            key not in result,
            f"Trung dap an Viet cau {number}"
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
        f"Trang 24 khong du dap an {first}-{last}"
    )

    return result


# =====================================================
# 4. DOC 85 DAP AN NGHE VA DOC
# =====================================================

def find_official_mcq(doc):

    text = doc[22].get_text("text")

    matches = re.findall(
        r"(?<!\d)"
        r"(\d{1,3})"
        r"\s*[.．、]\s*"
        r"([A-F√×]{1,3})"
        r"(?![A-Z])",
        text
    )

    result = {}

    for number_text, answer in matches:

        number = int(number_text)

        if not 1 <= number <= 85:
            continue

        key = str(number)

        require(
            key not in result,
            f"Trung dap an cau {number}"
        )

        if number <= 10:

            valid = answer in ("√", "×")

        elif 46 <= number <= 55:

            valid = answer in "ABCDEF"

        elif 56 <= number <= 65:

            valid = (
                len(answer) == 3
                and set(answer) == set("ABC")
            )

        else:

            valid = answer in "ABCD"

        require(
            valid,
            f"Cau {number}: "
            f"sai dinh dang dap an {answer}"
        )

        result[key] = answer

    require(
        set(result) == {
            str(n) for n in range(1, 86)
        },
        "Trang 23 khong du 85 dap an"
    )

    return result


# =====================================================
# 5. TACH CUM TU VIET 86-95
# =====================================================

def tokens_from_pdf(doc):

    tokens = {}

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
            f"Cau {number}: sai cum tu {values}"
        )

        tokens[number] = values

    require(
        set(tokens) == set(range(86, 96)),
        "Trang 15 khong du 10 cau Viet"
    )

    return tokens


# =====================================================
# 6. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 06 - BUOC 1")
    print("CHUAN BI DAP AN TU PDF")
    print("=" * 60)

    # ================================================
    # 7. KIEM TRA FILE NGUON
    # ================================================

    for path in (PDF_FILE, MP3_FILE):

        require(
            path.is_file()
            and path.stat().st_size > 0,
            f"Thieu file: {path}"
        )

    # ================================================
    # 8. DOC PDF
    # ================================================

    with fitz.open(PDF_FILE) as doc:

        require(
            len(doc) == 24,
            "PDF phai co 24 trang"
        )

        require(
            CODE in doc[0].get_text("text")
            and CODE in doc[22].get_text("text"),
            "PDF khong khop ma de goc H41008"
        )

        answers = find_official_mcq(doc)

        tokens = tokens_from_pdf(doc)

        # ============================================
        # 9. KIEM TRA 5 TU GOI Y
        # ============================================

        page16 = doc[15].get_text("text")

        for number, word in WORDS.items():

            require(
                re.search(
                    rf"(?<!\d){number}\s*[.．、]",
                    page16
                )
                and word in page16,

                f"Thieu cau {number}: {word}"
            )

        # ============================================
        # 10. DOC DAP AN VIET TRANG 24
        # ============================================

        page24 = doc[23].get_text("text")

        require(
            "第一部分" in page24
            and "第二部分" in page24,
            "Trang 24 thieu hai phan Viet"
        )

        part_one, part_two = page24.split(
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
    # 11. DAP AN SAP XEP CAU 86-95
    # ================================================

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

        # PDF nay khong co dap an thay the.
        require(
            len(variants) == 1,
            f"Cau {number} co nhieu dap an. "
            "Can doi chieu lai PDF."
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
            "ghep duoc tu cum tu PDF.\n"
            f"Dap an: {variants[0]}\n"
            f"Cum tu: {tokens[number]}"
        )

        answers[key] = variants[0]

    # ================================================
    # 12. VIET THEO TRANH CAU 96-100
    # ================================================

    references = {}

    for number in range(96, 101):

        key = str(number)

        sentence = official_open[key]

        require(
            WORDS[number] in sentence,
            f"Cau {number}: cau mau thieu "
            f"tu goi y {WORDS[number]}"
        )

        references[key] = [sentence]

        # Dap an mo nam trong
        # dap_an_tham_khao_viet_mo.
        answers[key] = None

    require(
        set(answers) == {
            str(n) for n in range(1, 101)
        },
        "Chua du 100 dap an"
    )

    # ================================================
    # 13. TAO JSON BUOC 1
    # ================================================

    result = {

        "ma_de_goc": CODE,

        "cap_hsk": 4,

        "so_de": DE_NUMBER,

        "tong_cau": 100,

        "so_cau_nghe": 45,
        "so_cau_doc": 40,
        "so_cau_viet": 15,

        "so_trang_pdf": 24,

        "trang_loi_thoai": list(range(17, 23)),

        "trang_dap_an": [23, 24],

        "file_pdf": str(PDF_FILE),

        "file_mp3": str(MP3_FILE),

        "dap_an": answers,

        "dap_an_thay_the": {},

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
    # 14. KHONG GHI DE JSON KHAC NOI DUNG
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

    if not ANSWER_FILE.exists():

        ANSWER_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        ANSWER_FILE.write_bytes(content)

    # ================================================
    # 15. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH HSK4 DE 06 - BUOC 1")
    print("=" * 60)

    print("Ten hien thi: De 6")
    print(f"Ma de goc PDF: {CODE}")

    print("Nghe: 45/45")
    print("Doc: 40/40")
    print("Viet: 15/15")

    print("Dap an thay the: KHONG CO")

    print(
        "Tu goi y:",
        ", ".join(WORDS.values())
    )

    print("Viet tranh: TU DONG THEO DAP AN MAU")

    print(f"\nJSON: {ANSWER_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
