
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK4 DE 02 (H41002)
BUOC 1 - XU LY DAP AN VA KIEM TRA PDF

- Doc PDF H41002 (24 trang).
- Tach 85 dap an Nghe/Doc.
- Tach 10 dap an Viet sap xep.
- Giu dap an thay the cua cau 91.
- Tach 5 dap an Viet theo tranh.
- Kiem tra 10 bo cum tu sap xep.
- Kiem tra hinh va tu cho san 96-100.
- Tao JSON va HTML xem truoc.

Viet theo tranh: CHAM TU DONG THEO CAU MAU.

KHONG ket noi SQL Server.
KHONG sua H41001.
"""

from pathlib import Path
from html import escape
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

PDF_FILE = SOURCE / "H41002.pdf"
MP3_FILE = SOURCE / "H41002.mp3"

DATA = (
    BASE / "hsk4" / "data" / "de_02"
)

OUTPUT = (
    BASE / "hsk4" / "output" / "de_02"
)

ANSWER_FILE = (
    DATA / "de_02_dap_an.json"
)

HTML_FILE = (
    OUTPUT / "kiem_tra_buoc_1.html"
)

CODE = "H41002"

# Tu cho san thuc te tren trang 16.
WORDS = {
    96: "吃惊",
    97: "汗",
    98: "挂",
    99: "香",
    100: "杂志",
}

PREVIEW_PAGES = (
    7, 8, 15, 16
)


# =====================================================
# 2. HAM KIEM TRA
# =====================================================

def require(condition, message):

    if not condition:
        raise RuntimeError(message)


def compact(value):

    result = unicodedata.normalize(
        "NFKC",
        str(value)
    )

    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "",
        result
    )


def get_text(doc, number):

    return doc[
        number - 1
    ].get_text("text")


# =====================================================
# 3. KIEM TRA BO CUC PDF
# =====================================================

def verify_pdf(doc):

    require(
        len(doc) == 24,
        f"PDF phai 24 trang, "
        f"hien co {len(doc)}."
    )

    require(
        CODE in get_text(doc, 1),
        "Bia PDF khong co H41002."
    )

    # Bia PDF goc co footer H41001 - 1.
    # Day la loi in san cua PDF,
    # khong phai ma de H41002.

    checks = {
        2: (
            "第一部分",
            "判断对错"
        ),

        3: (
            "第二部分",
            "11"
        ),

        5: (
            "第三部分",
            "26"
        ),

        7: (
            "第一部分",
            "选词填空",
            "46"
        ),

        8: (
            "选词填空",
            "51"
        ),

        9: (
            "第二部分",
            "排列顺序",
            "56"
        ),

        11: (
            "第三部分",
            "66"
        ),

        15: (
            "第一部分",
            "完成句子",
            "86"
        ),

        16: (
            "第二部分",
            "看图",
            "96",
            "100"
        ),

        17: (
            "听力材料",
        ),

        23: (
            "卷答案",
            "听力",
            "阅读"
        ),

        24: (
            "书写",
            "86",
            "100"
        ),
    }

    for number, needles in checks.items():

        text = re.sub(
            r"\s+",
            "",
            get_text(doc, number)
        )

        missing = [
            word
            for word in needles
            if word not in text
        ]

        require(
            not missing,
            f"Trang {number} sai bo cuc. "
            f"Thieu: {missing}"
        )

    # Trang 16: 1 anh vi du + 5 anh
    require(
        len(
            doc[15].get_images(
                full=True
            )
        ) >= 6,

        "Trang 16 khong du 6 anh."
    )


# =====================================================
# 4. TACH DAP AN NGHE VA DOC
# =====================================================

def extract_objective(doc):

    text = get_text(doc, 23)

    matches = re.findall(
        r"(?<!\d)"
        r"(\d{1,3})"
        r"\s*[.．、]\s*"
        r"([A-F√×]{1,3})"
        r"(?![A-Z])",

        text
    )

    result = {}

    for key, value in matches:

        number = int(key)

        require(
            1 <= number <= 85,
            f"Dap an ngoai pham vi: {number}"
        )

        require(
            str(number) not in result,
            f"Trung dap an cau {number}"
        )

        result[str(number)] = value

    require(
        set(result) == {
            str(i)
            for i in range(1, 86)
        },

        "Trang 23 khong du "
        "85 dap an Nghe/Doc."
    )

    # ================================================
    # 5. KIEM TRA DANG DAP AN
    # ================================================

    for number in range(1, 86):

        answer = result[
            str(number)
        ]

        if number <= 10:

            valid = answer in {
                "√", "×"
            }

        elif (
            number <= 45
            or 66 <= number <= 85
        ):

            valid = answer in set(
                "ABCD"
            )

        elif number <= 55:

            valid = answer in set(
                "ABCDEF"
            )

        else:

            valid = (
                len(answer) == 3
                and set(answer)
                == set("ABC")
            )

        require(
            valid,
            f"Cau {number} sai dap an: "
            f"{answer}"
        )

    return result


# =====================================================
# 6. TACH NOI DUNG THEO SO CAU
# =====================================================

def parse_numbered_section(
    text,
    first,
    last
):

    pattern = re.compile(
        r"(?m)^\s*"
        r"(\d{2,3})"
        r"\s*[.．、]"
    )

    matches = list(
        pattern.finditer(text)
    )

    result = {}

    for index, match in enumerate(matches):

        number = int(
            match.group(1)
        )

        if not first <= number <= last:
            continue

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )

        block = text[
            match.end():end
        ]

        # Ghep cac dong dap an
        # bi ngat giua cau tieng Trung.
        block = re.sub(
            r"\s+",
            "",
            block
        )

        result[str(number)] = block

    require(
        set(result) == {
            str(i)
            for i in range(
                first,
                last + 1
            )
        },

        f"Khong du dap an "
        f"{first}-{last}. "
        f"Tim thay: {sorted(result)}"
    )

    return result


# =====================================================
# 7. TACH DAP AN VIET 86-100
# =====================================================

def extract_writing(doc):

    raw = get_text(
        doc,
        24
    )

    require(
        "第二部分" in raw,
        "Trang 24 thieu phan Viet 2."
    )

    part_one, part_two = raw.split(
        "第二部分",
        1
    )

    raw_primary = parse_numbered_section(
        part_one,
        86,
        95
    )

    raw_open = parse_numbered_section(
        part_two,
        96,
        100
    )

    main = {}

    alternatives = {}

    # ================================================
    # 8. CAU VIET SAP XEP 86-95
    # ================================================

    for number in range(86, 96):

        key = str(number)

        variants = [
            value.strip()

            for value in re.split(
                r"[/／]",
                raw_primary[key]
            )

            if value.strip()
        ]

        require(
            variants
            and all(
                value.endswith("。")
                for value in variants
            ),

            f"Dap an Viet cau {number} "
            "khong hop le."
        )

        main[key] = variants[0]

        if len(variants) > 1:

            alternatives[key] = (
                variants[1:]
            )

    # PDF H41002 chi co cau 91
    # ghi ro hai dap an hop le.
    require(
        set(alternatives) == {"91"},
        "Danh sach dap an thay the "
        "khong khop PDF H41002: "
        + str(sorted(alternatives))
    )

    # ================================================
    # 9. CAU VIET THEO TRANH 96-100
    # ================================================

    references = {}

    for number in range(96, 101):

        key = str(number)

        value = raw_open[key]

        require(
            value.endswith("。"),
            f"Thieu dap an tham khao "
            f"cau {number}"
        )

        require(
            WORDS[number] in value,

            f"Dap an cau {number} "
            f"thieu tu {WORDS[number]}"
        )

        references[key] = [value]

    return (
        main,
        alternatives,
        references
    )


# =====================================================
# 10. TACH CUM TU VIET SAP XEP
# =====================================================

def extract_writing_tokens(
    doc,
    writing_main,
    alternatives
):

    tokens = {}

    text = get_text(
        doc,
        15
    )

    for line in text.splitlines():

        match = re.match(
            r"^\s*"
            r"(8[6-9]|9[0-5])"
            r"\s*[.．、]\s*"
            r"(.+)$",

            line
        )

        if not match:
            continue

        number = int(
            match.group(1)
        )

        items = [
            value.strip()

            for value in re.split(
                r"\s{2,}",
                match.group(2).strip()
            )

            if value.strip()
        ]

        require(
            3 <= len(items) <= 9,
            f"Cau {number} "
            f"sai so cum tu: {items}"
        )

        require(
            str(number) not in tokens,
            f"Trung cau Viet {number}"
        )

        tokens[str(number)] = items

    require(
        set(tokens) == {
            str(i)
            for i in range(86, 96)
        },

        "Trang 15 khong du "
        "10 cau Viet sap xep."
    )

    # ================================================
    # 11. KIEM TRA DAP AN CO GHEP DUOC KHONG
    # ================================================

    for number in range(86, 96):

        words = tokens[
            str(number)
        ]

        candidates = [
            writing_main[str(number)]
        ] + alternatives.get(
            str(number),
            []
        )

        formed = {
            compact(
                "".join(order)
            )

            for order in permutations(
                words
            )
        }

        for answer in candidates:

            require(
                compact(answer) in formed,

                f"Cau {number} "
                "khong ghep duoc dap an.\n"
                f"Dap an: {answer}\n"
                f"Cum tu: {words}"
            )

    return tokens


# =====================================================
# 12. KIEM TRA HINH VIET THEO TRANH
# =====================================================

def verify_picture_words(doc):

    page = doc[15]

    tokens = page.get_text(
        "words"
    )

    image_rects = []

    for entry in page.get_images(
        full=True
    ):

        image_rects.extend(
            page.get_image_rects(
                entry[0]
            )
        )

    half = page.rect.width / 2

    for number, word in WORDS.items():

        # ============================================
        # 13. TIM SO CAU
        # ============================================

        anchors = [
            fitz.Rect(
                token[:4]
            )

            for token in tokens

            if re.fullmatch(
                rf"{number}\s*[.．、]",
                token[4]
            )
        ]

        # ============================================
        # 14. TIM TU CHO SAN
        # ============================================

        names = [
            fitz.Rect(
                token[:4]
            )

            for token in tokens

            if token[4] == word
        ]

        require(
            len(anchors) == 1
            and len(names) == 1,

            f"Cau {number}: "
            "khong tim dung so cau "
            "hoac tu goi y."
        )

        anchor = anchors[0]
        label = names[0]

        # So cau va tu phai cung hang.
        require(
            abs(
                anchor.y0 - label.y0
            ) < 15,

            f"Cau {number}: "
            "so cau va tu khong cung hang."
        )

        left = (
            anchor.x0 < half
        )

        require(
            (
                label.x0 < half
            ) == left,

            f"Cau {number}: "
            "tu goi y sai cot."
        )

        # ============================================
        # 15. TIM ANH TREN CUNG HANG
        # ============================================

        pictures = [
            rect

            for rect in image_rects

            if (
                (
                    (
                        rect.x0 + rect.x1
                    ) / 2 < half
                ) == left
            )

            and abs(
                anchor.y0 - rect.y1
            ) <= 25
        ]

        require(
            len(pictures) == 1,

            f"Cau {number}: "
            "khong tim dung "
            "anh minh hoa."
        )


# =====================================================
# 16. TAO HTML XEM TRUOC
# =====================================================

def build_html():

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

    items = " · ".join(
        f"{number}: {escape(word)}"

        for number, word
        in WORDS.items()
    )

    return (
        """<!doctype html>
<html lang="vi">

<head>
<meta charset="utf-8">

<title>HSK4 Đề 2 - Kiểm tra bước 1</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 24px;
    font: 16px Arial, sans-serif;
    background: #f4f6fa;
    color: #203044;
}

main {
    max-width: 930px;
    margin: auto;
}

section {
    background: white;
    border: 1px solid #dee3ed;
    border-radius: 12px;
    margin: 18px 0;
    padding: 18px;
}

img {
    display: block;
    max-width: 100%;
    height: auto;
    margin: auto;
}

small {
    color: #546477;
}
</style>

</head>

<body>
<main>

<h1>HSK4 – Đề 2 (H41002)</h1>

<p>
    <strong>Bước 1:</strong>
    Kiểm tra bố cục và nội dung câu hỏi
    trên PDF gốc.
</p>

<p>
    <small>
        Không hiển thị đáp án câu 1–100.
        Không nhập SQL.
    </small>
</p>

<p>
    <strong>Từ cho sẵn câu 96–100:</strong>
    """
        + items
        + "</p>"
        + "".join(cards)
        + "</main></body></html>"
    )


# =====================================================
# 17. GHI FILE AN TOAN
# =====================================================

def write_checked(path, data):

    if path.is_file():

        require(
            path.read_bytes() == data,

            "Khong ghi de file "
            "co noi dung khac: "
            + str(path)
        )

        return

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_bytes(data)


# =====================================================
# 18. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)

    print(
        "MOC HAN - HSK4 DE 02 - BUOC 1"
    )

    print("=" * 60)

    for file in (
        PDF_FILE,
        MP3_FILE
    ):

        require(
            file.is_file()
            and file.stat().st_size > 0,

            f"Thieu file: {file}"
        )

    # ================================================
    # 19. DOC VA KIEM TRA PDF
    # ================================================

    with fitz.open(PDF_FILE) as doc:

        verify_pdf(doc)

        objective = extract_objective(
            doc
        )

        (
            writing,
            alternatives,
            references
        ) = extract_writing(doc)

        tokens = extract_writing_tokens(
            doc,
            writing,
            alternatives
        )

        verify_picture_words(
            doc
        )

        # ============================================
        # 20. KET HOP 100 DAP AN
        # ============================================

        answers = {
            **objective,
            **writing,

            **{
                str(number): None

                for number
                in range(96, 101)
            }
        }

        require(
            len(answers) == 100,

            "Khong du 100 cau."
        )

        # Cac cau 96-100 co dap an mau
        # luu tai references.
        # JSON chuan o buoc 3 se tao
        # object cham tu dong cho moi cau.

        # ============================================
        # 21. TAO JSON BUOC 1
        # ============================================

        model = {
            "ma_de_goc": CODE,

            "cap_hsk": 4,
            "so_de": 2,

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

            "trang_dap_an": [
                23, 24
            ],

            "dap_an": answers,

            "dap_an_thay_the": (
                alternatives
            ),

            "dap_an_tham_khao_viet_mo": (
                references
            ),

            "tu_cho_san_viet_mo": {
                str(number): word

                for number, word
                in WORDS.items()
            },

            "cum_tu_viet_sap_xep": (
                tokens
            ),

            "nhom_doc_chung": [
                "80-81",
                "82-83",
                "84-85"
            ],

            # HSK4 tu dong cham theo mau.
            "cau_can_cham_thu_cong": [],

            "che_do_cham_viet_mo": (
                "cham_tu_dong_theo_mau"
            ),
        }

        data = json.dumps(
            model,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8")

        # ============================================
        # 22. TAO ANH XEM TRUOC
        # ============================================

        previews = {}

        for number in PREVIEW_PAGES:

            pix = doc[
                number - 1
            ].get_pixmap(
                matrix=fitz.Matrix(
                    1.7,
                    1.7
                ),
                alpha=False
            )

            previews[
                OUTPUT
                / "preview_pages"
                / f"trang_{number:02d}.png"
            ] = pix.tobytes("png")

    # ================================================
    # 23. LUU JSON VA HTML
    # ================================================

    write_checked(
        ANSWER_FILE,
        data
    )

    for path, content in (
        previews.items()
    ):

        write_checked(
            path,
            content
        )

    write_checked(
        HTML_FILE,
        build_html().encode(
            "utf-8"
        )
    )

    # ================================================
    # 24. KET QUA
    # ================================================

    print(
        "Ma de: H41002"
    )

    print(
        "PDF: 24 trang"
    )

    print(
        "Nghe: 45/45"
    )

    print(
        "Doc: 40/40"
    )

    print(
        "Viet sap xep: 10/10"
    )

    print(
        "Viet theo tranh: "
        "5/5 dap an mau"
    )

    print(
        "Dap an thay the: cau 91"
    )

    print(
        "Cau 96-100: "
        "CHAM TU DONG THEO CAU MAU"
    )

    print(
        "HTML: khong hien thi dap an"
    )

    print(
        f"\nJSON: {ANSWER_FILE}"
    )

    print(
        f"HTML: {HTML_FILE}"
    )

    print(
        "\nCHUA thay doi SQL Server."
    )


if __name__ == "__main__":
    main()
