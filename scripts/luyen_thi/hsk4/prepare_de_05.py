
# -*- coding: utf-8 -*-
"""
MOC HAN - HSK4 DE 05 (H41005)

BUOC 1 - CHUAN BI DAP AN TU PDF

- Doc dap an Nghe/Doc 1-85 tu trang 23.
- Doc dap an Viet 86-100 tu trang 24.
- Giu dap an thay the cau 94.
- Kiem tra cum tu sap xep cau 86-95 voi trang 15.
- Giu 5 tu goi y va cau mau 96-100.
- Tao de_05_dap_an.json theo dinh dang H41003-H41004.

KHONG ket noi SQL.
KHONG tao anh.
KHONG sua cac de cu.
"""

import json
import os
import re
import unicodedata

from itertools import permutations
from pathlib import Path

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
    BASE / "hsk4" / "data" / "de_05"
)

PDF_FILE = SOURCE / "H41005.pdf"
MP3_FILE = SOURCE / "H41005.mp3"

ANSWER_FILE = DATA / "de_05_dap_an.json"

CODE = "H41005"

WORDS = {
    96: "消息",
    97: "猜",
    98: "信用卡",
    99: "沙发",
    100: "困",
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
# 3. DOC 85 DAP AN NGHE VA DOC
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
            f"Trung dap an {number} o trang 23"
        )

        if number <= 10:

            valid = answer in ("√", "×")

        elif 56 <= number <= 65:

            valid = (
                len(answer) == 3
                and set(answer) == set("ABC")
            )

        elif 46 <= number <= 55:

            valid = answer in "ABCDEF"

        else:

            valid = answer in "ABCD"

        require(
            valid,
            f"Sai dap an cau {number}: {answer}"
        )

        result[key] = answer

    require(
        set(result) == {
            str(n) for n in range(1, 86)
        },
        "Trang 23 khong du 85 dap an Nghe/Doc"
    )

    return result


# =====================================================
# 4. DOC DAP AN VIET TU TRANG 24
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

        value = re.sub(
            r"\s+",
            "",
            text[match.end():end]
        )

        key = str(number)

        require(
            key not in result,
            f"Trung dap an Viet {number}"
        )

        require(
            bool(value),
            f"Dap an Viet {number} rong"
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
# 5. TACH CUM TU VIET 86-95
# =====================================================

def tokens_from_pdf(doc):

    text = doc[14].get_text("text")

    result = {}

    for line in text.splitlines():

        match = re.match(
            r"^\s*(8[6-9]|9[0-5])"
            r"\s*[.．、]\s*(.+)$",
            line
        )

        if not match:
            continue

        number = int(match.group(1))

        values = [
            item.strip()

            for item in re.split(
                r"\s{2,}",
                match.group(2).strip()
            )

            if item.strip()
        ]

        require(
            number not in result,
            f"Trung cum tu cau {number}"
        )

        require(
            3 <= len(values) <= 9,
            f"Cau {number} sai cum tu: {values}"
        )

        result[number] = values

    require(
        set(result) == set(range(86, 96)),
        "Trang 15 khong du 10 cau Viet sap xep"
    )

    return result


# =====================================================
# 6. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 05 - BUOC 1")
    print("CHUAN BI DAP AN H41005")
    print("=" * 60)

    # ================================================
    # 7. KIEM TRA FILE NGUON
    # ================================================

    require(
        PDF_FILE.is_file()
        and PDF_FILE.stat().st_size > 0,
        f"Thieu PDF: {PDF_FILE}"
    )

    require(
        MP3_FILE.is_file()
        and MP3_FILE.stat().st_size > 0,
        f"Thieu MP3: {MP3_FILE}"
    )

    # ================================================
    # 8. DOC PDF VA DAP AN GOC
    # ================================================

    with fitz.open(PDF_FILE) as doc:

        require(
            len(doc) == 24,
            "H41005 phai co 24 trang"
        )

        require(
            CODE in doc[0].get_text("text")
            and CODE in doc[22].get_text("text"),
            "PDF khong phai H41005"
        )

        answers = find_official_mcq(doc)

        tokens = tokens_from_pdf(doc)

        # Kiem tra 5 tu goi y
        open_text = doc[15].get_text("text")

        for number, word in WORDS.items():

            require(
                word in open_text
                and re.search(
                    rf"(?<!\d){number}\s*[.．、]",
                    open_text
                ),
                f"Thieu tu goi y cau {number}: {word}"
            )

        # Dap an Viet trang 24
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
    # 9. DAP AN SAP XEP 86-95
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

        require(
            bool(variants),
            f"Thieu dap an cau {number}"
        )

        # H41005: cau 94 co hai dap an hop le
        if number == 94:

            require(
                len(variants) == 2,
                "Cau 94 phai co 2 dap an trong PDF"
            )

            alternatives[key] = [
                variants[1]
            ]

        else:

            require(
                len(variants) == 1,
                f"Cau {number} co dap an "
                "thay the chua duoc kiem tra"
            )

        possible = {
            compact("".join(order))

            for order in permutations(
                tokens[number]
            )
        }

        for value in variants:

            require(
                compact(value) in possible,
                f"Cau {number}: "
                "dap an khong ghep duoc "
                "tu cac cum tren trang 15.\n"
                f"Dap an: {value}\n"
                f"Cum tu: {tokens[number]}"
            )

        answers[key] = variants[0]

    # ================================================
    # 10. VIET THEO TRANH 96-100
    # ================================================

    references = {}

    for number in range(96, 101):

        key = str(number)

        sentence = official_open[key]

        require(
            WORDS[number] in sentence,
            f"Cau mau {number} "
            "khong chua tu goi y"
        )

        references[key] = [sentence]

        # Dap an cua cau viet mo nam
        # trong danh sach dap an tham khao.
        answers[key] = None

    require(
        set(answers) == {
            str(n) for n in range(1, 101)
        },
        "Chua du 100 dap an"
    )

    # ================================================
    # 11. TAO JSON BUOC 1
    # ================================================

    result = {

        "ma_de_goc": CODE,

        "cap_hsk": 4,

        "so_de": 5,

        "tong_cau": 100,

        "so_cau_nghe": 45,

        "so_cau_doc": 40,

        "so_cau_viet": 15,

        "so_trang_pdf": 24,

        "trang_loi_thoai": list(
            range(17, 23)
        ),

        "trang_dap_an": [23, 24],

        "file_pdf": str(PDF_FILE),

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
    # 12. KHONG GHI DE FILE KHAC NOI DUNG
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
    # 13. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH CHUAN BI DAP AN HSK4 DE 05")
    print("=" * 60)

    print("Ma de: H41005")

    print("Nghe: 45/45")
    print("Doc: 40/40")
    print("Viet: 15/15")

    print("Dap an thay the: cau 94")

    print(
        "Tu goi y 96-100:",
        ", ".join(WORDS.values())
    )

    print("Viet theo tranh: TU DONG")

    print("Trang PDF: 24")
    print("Trang dap an: 23-24")

    print(f"\nJSON: {ANSWER_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
