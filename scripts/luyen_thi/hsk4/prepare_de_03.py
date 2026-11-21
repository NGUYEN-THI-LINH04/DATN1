
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK4 DE 03 (H41003)
BUOC 1 - KIEM TRA PDF VA TACH DAP AN

- Ke thua cau truc De 1 va De 2.
- Tach 85 dap an Nghe/Doc.
- Tach 10 dap an Viet sap xep.
- Giu 2 dap an hop le cau 93.
- Tach 5 dap an Viet theo tranh.
- Kiem tra tu goi y va hinh minh hoa.
- Tao JSON, 4 anh preview va HTML.

CAU 96-100: CHAM TU DONG THEO CAU MAU.

KHONG sua SQL Server.
KHONG sua cac de thi cu.
"""

from pathlib import Path
from itertools import permutations
from html import escape

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

PDF_FILE = SOURCE / "H41003.pdf"
MP3_FILE = SOURCE / "H41003.mp3"

DATA = BASE / "hsk4" / "data" / "de_03"
OUTPUT = BASE / "hsk4" / "output" / "de_03"

ANSWER_FILE = DATA / "de_03_dap_an.json"
HTML_FILE = OUTPUT / "kiem_tra_buoc_1.html"

CODE = "H41003"

WORDS = {
    96: "收拾",
    97: "理发",
    98: "困",
    99: "激动",
    100: "讨论",
}

PREVIEW_PAGES = (7, 8, 15, 16)


# =====================================================
# 2. HAM KIEM TRA
# =====================================================

def require(ok, message):

    if not ok:
        raise RuntimeError(message)


def compact(text):

    text = unicodedata.normalize(
        "NFKC",
        str(text)
    )

    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "",
        text
    )


# =====================================================
# 3. KIEM TRA BO CUC PDF
# =====================================================

def verify_pdf(doc):

    require(
        len(doc) == 24,
        f"H41003 phai co 24 trang, "
        f"nhan {len(doc)}."
    )

    require(
        CODE in doc[0].get_text("text"),
        "Trang bia khong dung ma H41003."
    )

    # PDF goc co footer bia H41001 - 1.
    # Chi kiem tra ma de chinh H41003.

    checks = {
        2: ("第一部分", "判断对错"),
        3: ("第二部分", "11"),
        5: ("第三部分", "26"),

        7: ("第一部分", "选词填空", "46"),
        8: ("选词填空", "51"),

        9: ("第二部分", "排列顺序", "56"),
        11: ("第三部分", "66"),

        15: ("第一部分", "完成句子", "86"),
        16: ("第二部分", "看图", "96", "100"),

        17: (CODE, "听力材料"),

        23: (
            CODE,
            "卷答案",
            "听力",
            "阅读"
        ),

        24: ("书写", "86", "100"),
    }

    for number, terms in checks.items():

        text = re.sub(
            r"\s+",
            "",
            doc[number - 1].get_text("text")
        )

        missing = [
            term
            for term in terms
            if term not in text
        ]

        require(
            not missing,
            f"Trang {number} "
            f"khong dung bo cuc. "
            f"Thieu: {missing}"
        )

    require(
        len(doc[15].get_images(full=True)) == 6,
        "Trang 16 phai co "
        "1 anh vi du va 5 anh cau hoi."
    )


# =====================================================
# 4. TACH 85 DAP AN NGHE VA DOC
# =====================================================

def extract_objective(doc):

    text = doc[22].get_text("text")

    matches = re.findall(
        r"(?<!\d)"
        r"(\d{1,3})"
        r"\s*[.．、]\s*"
        r"([A-F√×]{1,3})"
        r"(?![A-Z])",
        text
    )

    answers = {}

    for key, value in matches:

        number = int(key)

        if not 1 <= number <= 85:
            continue

        require(
            key not in answers,
            f"Trung dap an cau {number} "
            "o trang 23."
        )

        answers[key] = value

    expected = {
        str(i)
        for i in range(1, 86)
    }

    require(
        set(answers) == expected,
        "Thieu dap an Nghe/Doc: "
        + str(
            sorted(
                int(i)
                for i in expected - set(answers)
            )
        )
    )

    # ================================================
    # 5. KIEM TRA TUNG LOAI DAP AN
    # ================================================

    for number in range(1, 86):

        answer = answers[str(number)]

        if number <= 10:

            valid = answer in {"√", "×"}

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
            f"Cau {number} "
            f"sai dang dap an: {answer}"
        )

    return answers


# =====================================================
# 6. TACH NOI DUNG THEO SO CAU
# =====================================================

def numbered_blocks(text, first, last):

    hits = list(
        re.finditer(
            r"(?m)^\s*"
            r"(\d{2,3})"
            r"\s*[.．、]",
            text
        )
    )

    result = {}

    for index, match in enumerate(hits):

        number = int(match.group(1))

        if not first <= number <= last:
            continue

        require(
            str(number) not in result,
            f"Trung nhan cau {number}."
        )

        stop = (
            hits[index + 1].start()
            if index + 1 < len(hits)
            else len(text)
        )

        result[str(number)] = re.sub(
            r"\s+",
            "",
            text[match.end():stop]
        )

    expected = {
        str(i)
        for i in range(first, last + 1)
    }

    require(
        set(result) == expected,
        f"Thieu dap an {first}-{last}: "
        + str(
            sorted(
                int(i)
                for i in expected - set(result)
            )
        )
    )

    return result


# =====================================================
# 7. TACH DAP AN VIET 86-100
# =====================================================

def extract_writing(doc):

    text = doc[23].get_text("text")

    require(
        "第二部分" in text,
        "Trang 24 thieu phan "
        "Viet theo tranh."
    )

    first, second = text.split(
        "第二部分",
        1
    )

    writing_raw = numbered_blocks(
        first,
        86,
        95
    )

    open_raw = numbered_blocks(
        second,
        96,
        100
    )

    answers = {}
    alternatives = {}
    references = {}

    # ================================================
    # 8. VIET SAP XEP
    # ================================================

    for number in range(86, 96):

        key = str(number)

        variants = [
            value.strip()

            for value in re.split(
                r"[/／]",
                writing_raw[key]
            )

            if value.strip()
        ]

        require(
            variants
            and all(
                value.endswith(
                    ("。", "？", "?", "！", "!")
                )
                for value in variants
            ),

            f"Dap an cau {number} "
            f"khong hop le: {variants}"
        )

        answers[key] = variants[0]

        if len(variants) > 1:
            alternatives[key] = variants[1:]

    # H41003: chi cau 93 co 2 dap an.
    require(
        set(alternatives) == {"93"}
        and len(alternatives["93"]) == 1,

        "De 3 chi co cau 93 "
        "co hai dap an hop le."
    )

    # ================================================
    # 9. VIET THEO TRANH
    # ================================================

    for number, word in WORDS.items():

        answer = open_raw[str(number)]

        require(
            answer.endswith("。")
            and word in answer,

            f"Cau {number} "
            "thieu dap an mau hoac "
            f"thieu tu '{word}': {answer}"
        )

        references[str(number)] = [answer]

    return answers, alternatives, references


# =====================================================
# 10. TACH CUM TU VIET SAP XEP
# =====================================================

def extract_writing_tokens(
    doc,
    writing,
    alternatives
):

    tokens = {}

    for line in doc[14].get_text(
        "text"
    ).splitlines():

        match = re.match(
            r"^\s*"
            r"(8[6-9]|9[0-5])"
            r"\s*[.．、]\s*"
            r"(.+)$",
            line
        )

        if not match:
            continue

        number = int(match.group(1))

        # Tach theo 2+ khoang trang.
        # Giu khoang trang ben trong cum:
        # "2009 年7 月8 号".

        words = [
            item.strip()

            for item in re.split(
                r"\s{2,}",
                match.group(2).strip()
            )

            if item.strip()
        ]

        require(
            3 <= len(words) <= 9,

            f"Cau {number} "
            f"sai so cum tu: {words}"
        )

        require(
            str(number) not in tokens,
            f"Trung cum tu cau {number}."
        )

        tokens[str(number)] = words

    expected = {
        str(i)
        for i in range(86, 96)
    }

    require(
        set(tokens) == expected,

        "Trang 15 thieu "
        "cac cau Viet sap xep."
    )

    # ================================================
    # 11. KIEM TRA GHEP DAP AN
    # ================================================

    for number in range(86, 96):

        key = str(number)

        valid_forms = {
            compact("".join(order))

            for order in permutations(
                tokens[key]
            )
        }

        candidates = [
            writing[key]
        ] + alternatives.get(
            key,
            []
        )

        for answer in candidates:

            require(
                compact(answer) in valid_forms,

                f"Cau {number} "
                "khong ghep duoc dap an.\n"
                f"Dap an: {answer}\n"
                f"Cum tu: {tokens[key]}"
            )

    return tokens


# =====================================================
# 12. KIEM TRA HINH VA TU CHO SAN
# =====================================================

def verify_picture_words(doc):

    page = doc[15]

    words = page.get_text("words")

    images = []

    for item in page.get_images(
        full=True
    ):
        images.extend(
            page.get_image_rects(item[0])
        )

    require(
        len(images) == 6,

        "Trang 16 khong du "
        "1 anh vi du va 5 anh cau hoi."
    )

    used = set()

    half = page.rect.width / 2

    for number, hint in WORDS.items():

        # ============================================
        # 13. TIM SO CAU
        # ============================================

        anchors = [
            fitz.Rect(word[:4])

            for word in words

            if re.fullmatch(
                rf"{number}[.．、]",
                word[4]
            )
        ]

        # ============================================
        # 14. TIM TU GOI Y
        # ============================================

        hints = [
            fitz.Rect(word[:4])

            for word in words

            if word[4] == hint
        ]

        require(
            len(anchors) == 1
            and len(hints) == 1,

            f"Trang 16 thieu "
            f"so cau/tu goi y: "
            f"{number} {hint}"
        )

        anchor = anchors[0]
        label = hints[0]

        side = anchor.x0 < half

        require(
            (label.x0 < half) == side
            and abs(
                anchor.y0 - label.y0
            ) < 16,

            f"Cau {number}: "
            "tu goi y khong cung cot/hang."
        )

        # ============================================
        # 15. TIM ANH CUNG COT VA HANG
        # ============================================

        candidates = [
            rect

            for rect in images

            if (
                (
                    rect.x0 + rect.x1
                ) / 2 < half
            ) == side

            and abs(
                rect.y1 - anchor.y0
            ) < 85
        ]

        require(
            len(candidates) == 1,

            f"Cau {number}: "
            "khong tim dung anh minh hoa. "
            f"Tim duoc: {len(candidates)}"
        )

        signature = tuple(
            round(value, 1)
            for value in candidates[0]
        )

        require(
            signature not in used,
            f"Cau {number} bi trung anh."
        )

        used.add(signature)

    require(
        len(used) == 5,
        "Khong du 5 anh cau Viet."
    )


# =====================================================
# 16. TAO HTML XEM TRUOC
# =====================================================

def make_html():

    cards = []

    for page in PREVIEW_PAGES:

        cards.append(
            "<section>"
            f"<h2>Trang {page}</h2>"
            '<img src="preview_pages/'
            f'trang_{page:02d}.png" '
            f'alt="Trang {page}">'
            "</section>"
        )

    hints = " · ".join(
        f"{number}: {escape(word)}"

        for number, word in WORDS.items()
    )

    return (
        """<!doctype html>
<html lang="vi">

<head>
<meta charset="utf-8">

<title>HSK4 Đề 3 - Kiểm tra bước 1</title>

<style>
body {
    background: #f2f5fa;
    color: #21354b;
    font: 16px Arial, sans-serif;
    margin: 24px;
}

main {
    max-width: 940px;
    margin: auto;
}

section {
    background: white;
    border: 1px solid #dce4ef;
    border-radius: 12px;
    padding: 18px;
    margin: 18px 0;
}

img {
    display: block;
    max-width: 100%;
    height: auto;
    margin: auto;
}

small {
    color: #586a80;
}
</style>

</head>

<body>
<main>

<h1>HSK4 – Đề 3 (H41003)</h1>

<p>
Trang xem trước PDF gốc.
Không hiển thị đáp án và
không thay đổi SQL.
</p>

<p>
<strong>Từ cho sẵn 96–100:</strong>
"""
        + hints
        + "</p>"
        + "\n".join(cards)
        + "\n</main></body></html>"
    )


# =====================================================
# 17. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 03 - BUOC 1")
    print("=" * 60)

    for path in (PDF_FILE, MP3_FILE):

        require(
            path.is_file()
            and path.stat().st_size > 0,

            f"Thieu file: {path}"
        )

    # ================================================
    # 18. DOC VA KIEM TRA PDF
    # ================================================

    with fitz.open(PDF_FILE) as doc:

        verify_pdf(doc)

        objective = extract_objective(doc)

        writing, alternatives, references = (
            extract_writing(doc)
        )

        tokens = extract_writing_tokens(
            doc,
            writing,
            alternatives
        )

        verify_picture_words(doc)

        # ============================================
        # 19. KET HOP 100 DAP AN
        # ============================================

        answers = {
            **objective,
            **writing,

            **{
                str(i): None
                for i in range(96, 101)
            }
        }

        require(
            len(answers) == 100,
            "Khong du 100 cau trong JSON."
        )

        # ============================================
        # 20. JSON BUOC 1
        # ============================================

        result = {
            "ma_de_goc": CODE,

            "cap_hsk": 4,
            "so_de": 3,

            "tong_cau": 100,

            "so_cau_nghe": 45,
            "so_cau_doc": 40,
            "so_cau_viet": 15,

            "thoi_gian_phut": 100,

            "file_pdf": str(PDF_FILE),
            "file_mp3": str(MP3_FILE),

            "so_trang_pdf": 24,

            "trang_loi_thoai": list(
                range(17, 23)
            ),

            "trang_dap_an": [23, 24],

            "dap_an": answers,

            "dap_an_thay_the": (
                alternatives
            ),

            "dap_an_tham_khao_viet_mo": (
                references
            ),

            "tu_cho_san_viet_mo": {
                str(number): word

                for number, word in WORDS.items()
            },

            "cum_tu_viet_sap_xep": tokens,

            "nhom_doc_chung": [
                "80-81",
                "82-83",
                "84-85"
            ],

            "cau_can_cham_thu_cong": [],

            "che_do_cham_viet_mo": (
                "cham_tu_dong_theo_mau"
            ),
        }

        files = {
            ANSWER_FILE: json.dumps(
                result,
                ensure_ascii=False,
                indent=2
            ).encode("utf-8"),

            HTML_FILE: make_html().encode(
                "utf-8"
            ),
        }

        # ============================================
        # 21. TAO ANH XEM TRUOC
        # ============================================

        for page_number in PREVIEW_PAGES:

            pix = doc[
                page_number - 1
            ].get_pixmap(
                matrix=fitz.Matrix(
                    1.8,
                    1.8
                ),
                alpha=False
            )

            files[
                OUTPUT
                / "preview_pages"
                / f"trang_{page_number:02d}.png"
            ] = pix.tobytes("png")

    # ================================================
    # 22. KHONG GHI DE FILE KHAC NOI DUNG
    # ================================================

    for path, content in files.items():

        require(
            not path.exists()
            or path.read_bytes() == content,

            "File da ton tai voi "
            "noi dung khac. Khong ghi de: "
            + str(path)
        )

    # ================================================
    # 23. LUU DU LIEU
    # ================================================

    for path, content in files.items():

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not path.exists():
            path.write_bytes(content)

    # ================================================
    # 24. KET QUA
    # ================================================

    print("Ma de: H41003")
    print("PDF: 24 trang")
    print("Nghe: 45/45")
    print("Doc: 40/40")
    print("Viet sap xep: 10/10")
    print("Viet theo tranh: 5/5 dap an mau")
    print("Dap an thay the: cau 93")
    print(
        "Cau 96-100: "
        "CHAM TU DONG THEO CAU MAU"
    )
    print("HTML: khong hien thi dap an")

    print(f"\nJSON: {ANSWER_FILE}")
    print(f"HTML: {HTML_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
