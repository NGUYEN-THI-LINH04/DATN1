
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 07 (H31007) - BUOC 1.

- PDF de thi: 14 trang.
- PDF dap an rieng: 2 trang.
- Doc va doi chieu 80 dap an.
- Giu 2 dap an dung cau 77: 元 / 圆.
- Phat hien sai khac giua de va dap an cau 72.
- Tach 2 bang hinh Nghe cau 1-10.
- Tao JSON va HTML xem truoc.

KHONG ket noi SQL Server.
KHONG sua cac de thi cu.
"""

from pathlib import Path
from itertools import permutations
import json
import re
import unicodedata

import fitz


# =====================================================
# 1. CAU HINH
# =====================================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "luyen_thi"

SOURCE = (
    BASE / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 7"
)

DATA = (
    BASE / "hsk3" / "data" / "de_07"
)

OUTPUT = (
    BASE / "hsk3" / "output" / "de_07"
)

GROUP_DIR = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_07_dap_an.json"

PREVIEW_HTML = (
    OUTPUT / "kiem_tra_10_cau.html"
)

CODE = "H31007"


# =====================================================
# 2. HAI BANG HINH NGHE
# =====================================================

GROUP_RECTS = {
    "nghe_01_05": {
        "page": 2,
        "rect": (75, 175, 515, 515),
        "labels": "ABCDEF",
        "first": 1,
        "last": 5,
    },

    "nghe_06_10": {
        "page": 3,
        "rect": (75, 130, 515, 522),
        "labels": "ABCDE",
        "first": 6,
        "last": 10,
    },
}


# =====================================================
# 3. SO DO TRANG CAU HOI
# =====================================================

PAGE_QUESTIONS = {
    2: range(1, 6),
    3: range(6, 11),

    4: range(11, 21),
    5: range(21, 31),
    6: range(31, 41),

    7: range(41, 46),
    8: range(46, 51),

    9: range(51, 56),
    10: range(56, 61),

    11: range(61, 65),
    12: range(65, 71),

    13: range(71, 76),
    14: range(76, 81),
}


# =====================================================
# 4. DAP AN NGHE/DOC H31007
# =====================================================

EXPECTED_ROWS = [
    "E F B C A",
    "C B A E D",

    "× √ × √ ×",
    "√ √ √ × ×",

    "A C A A B",
    "B C A C B",

    "C C B B A",
    "A B B C C",

    "B F C D A",
    "B A D E C",

    "F A B C D",
    "A E B C F",

    "A B C B A",
    "A B A C C",
]


# =====================================================
# 5. DAP AN VIET H31007
# =====================================================

EXPECTED_WRITING = {
    71: ["我喜欢中国文化。"],

    # PDF de ghi "他的姓名".
    # PDF dap an ghi "他的名字".
    # Se bao toan nguyen van va canh bao.
    72: ["他的名字被写错了。"],

    73: ["她身高不到一米七。"],

    74: ["现在画羊的耳朵和鼻子。"],

    75: ["如果有面条就更好了。"],

    76: ["手"],

    # Hai dap an hop le.
    77: ["元", "圆"],

    78: ["牛"],
    79: ["电"],
    80: ["云"],
}


# =====================================================
# 6. HAM HO TRO
# =====================================================

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


def check_file(path):

    if (
        not path.is_file()
        or path.stat().st_size == 0
    ):
        raise RuntimeError(
            f"Thieu file hoac file rong: {path}"
        )

    return path


# =====================================================
# 7. TIM PDF DE VA PDF DAP AN
# =====================================================

def find_sources():

    pdfs = sorted(
        SOURCE.glob("*.pdf")
    )

    if len(pdfs) != 2:

        raise RuntimeError(
            "De 7 can dung 2 PDF: "
            "1 de thi + 1 dap an.\n"
            f"Tim thay: {len(pdfs)}\n"
            f"Thu muc: {SOURCE}"
        )

    exam = None
    answer = None

    # Xac dinh theo so trang,
    # khong phu thuoc ten file.
    for path in pdfs:

        check_file(path)

        with fitz.open(path) as doc:

            count = len(doc)

            if count == 14:

                if exam is not None:
                    raise RuntimeError(
                        "Co nhieu PDF de thi 14 trang."
                    )

                exam = path

            elif count == 2:

                if answer is not None:
                    raise RuntimeError(
                        "Co nhieu PDF dap an 2 trang."
                    )

                answer = path

            else:

                raise RuntimeError(
                    f"PDF {path.name} co "
                    f"{count} trang, sai mau 14+2."
                )

    if exam is None or answer is None:

        raise RuntimeError(
            "Khong xac dinh du PDF de thi "
            "14 trang va dap an 2 trang."
        )

    mp3s = sorted(
        SOURCE.glob("*.mp3")
    )

    if len(mp3s) > 1:

        raise RuntimeError(
            "Thu muc DE 7 co nhieu MP3."
        )

    mp3 = (
        check_file(mp3s[0])
        if mp3s else None
    )

    return exam, answer, mp3


# =====================================================
# 8. KIEM TRA DANG DAP AN
# =====================================================

def objective_options(number):

    if number <= 5:
        return set("ABCDEF")

    if number <= 10:
        return set("ABCDE")

    if number <= 20:
        return {"√", "×"}

    if number <= 40:
        return set("ABC")

    if number <= 45:
        return set("ABCDEF")

    if number <= 50:
        return set("ABCDE")

    if number <= 60:
        return set("ABCDEF")

    return set("ABC")


# =====================================================
# 9. DOC PDF DAP AN RIENG
# =====================================================

def read_answers(doc):

    if (
        len(doc) != 2
        or CODE not in doc[0].get_text("text")
    ):

        raise RuntimeError(
            "PDF dap an khong phai H31007."
        )

    text = unicodedata.normalize(
        "NFKC",
        doc[0].get_text("text")
    )

    found = {}

    regex = re.compile(
        r"(?<!\d)(\d{1,2})\s*[.．、]"
        r"\s*([A-F√×])(?=\s|$)"
    )

    # ================================================
    # 10. LAY 70 DAP AN NGHE/DOC
    # ================================================

    for match in regex.finditer(text):

        number = int(
            match.group(1)
        )

        if not 1 <= number <= 70:
            continue

        if number in found:
            raise RuntimeError(
                f"Trung dap an cau {number}."
            )

        answer = match.group(2)

        if answer not in objective_options(number):

            raise RuntimeError(
                f"Dap an cau {number} "
                f"ngoai lua chon: {answer}"
            )

        found[number] = answer

    if set(found) != set(range(1, 71)):

        missing = sorted(
            set(range(1, 71)) - set(found)
        )

        raise RuntimeError(
            f"Thieu dap an Nghe/Doc: {missing}"
        )

    # Doi chieu voi bang dap an goc.
    expected = [
        value

        for row in EXPECTED_ROWS
        for value in row.split()
    ]

    if len(expected) != 70:

        raise RuntimeError(
            "Bang mau khong du 70 dap an."
        )

    for number in range(1, 71):

        if found[number] != expected[number - 1]:

            raise RuntimeError(
                f"Dap an cau {number} "
                "khong khop PDF goc."
            )

    # ================================================
    # 11. LAY 10 DAP AN VIET
    # ================================================

    writing_text = doc[1].get_text("text")

    raw = {}

    writing_regex = re.compile(
        r"^\s*(7[1-9]|80)\s*[.．、]"
        r"\s*([^\n]+)",
        re.MULTILINE
    )

    for match in writing_regex.finditer(
        writing_text
    ):

        number = int(
            match.group(1)
        )

        if number in raw:

            raise RuntimeError(
                f"Trung cau Viet {number}."
            )

        raw[number] = [
            value.strip()

            for value in match.group(2).split("/")

            if value.strip()
        ]

    if set(raw) != set(range(71, 81)):

        missing = sorted(
            set(range(71, 81)) - set(raw)
        )

        raise RuntimeError(
            f"Thieu dap an Viet: {missing}"
        )

    # ================================================
    # 12. DOI CHIEU DAP AN VIET
    # ================================================

    alternatives = {}

    for number, values in raw.items():

        reference = EXPECTED_WRITING[number]

        if (
            [compact(v) for v in values]
            != [compact(v) for v in reference]
        ):

            raise RuntimeError(
                f"Cau {number} khong khop "
                "dap an PDF goc."
            )

        found[number] = values[0]

        if len(values) > 1:

            alternatives[str(number)] = (
                values[1:]
            )

    if alternatives != {
        "77": ["圆"]
    }:

        raise RuntimeError(
            "Dap an thay the cau 77 "
            "khong dung."
        )

    return found, alternatives, raw


# =====================================================
# 13. KIEM TRA PDF DE THI
# =====================================================

def check_pdf(doc):

    if (
        len(doc) != 14
        or CODE not in doc[0].get_text("text")
    ):

        raise RuntimeError(
            "PDF de thi khong phai "
            "H31007 - 14 trang."
        )

    if (
        "听" not in doc[1].get_text("text")
        or "书" not in doc[12].get_text("text")
    ):

        raise RuntimeError(
            "PDF thieu trang Nghe/Viet."
        )

    for page_no, numbers in (
        PAGE_QUESTIONS.items()
    ):

        first = numbers.start
        last = numbers.stop - 1

        # Cau 65-70 tiep noi trang 11.
        if first == 65:
            continue

        text = unicodedata.normalize(
            "NFKC",
            doc[page_no - 1].get_text("text")
        )

        pattern = (
            rf"第\s*{first}\s*[-–—]"
            rf"\s*{last}\s*题"
        )

        if first == 61:

            pattern = (
                r"第\s*61\s*[-–—]"
                r"\s*70\s*题"
            )

        if not re.search(pattern, text):

            raise RuntimeError(
                f"Trang {page_no} thieu "
                f"tieu de cau {first}-{last}."
            )


# =====================================================
# 14. KIEM TRA CUM TU SAP XEP CAU 71-75
# =====================================================

def check_writing_compatibility(
    doc,
    answers
):

    tokens = {}

    text = doc[12].get_text("text")

    for line in text.splitlines():

        match = re.match(
            r"^\s*(7[1-5])\s*[.．、]"
            r"\s*(.+)",
            line
        )

        if not match:
            continue

        number = int(
            match.group(1)
        )

        if number in tokens:

            raise RuntimeError(
                f"Trung cum tu cau {number}."
            )

        tokens[number] = [
            value.strip()

            for value in re.split(
                r"\s{2,}",
                match.group(2)
            )

            if value.strip()
        ]

    if set(tokens) != set(range(71, 76)):

        raise RuntimeError(
            "PDF khong du cum tu cau 71-75."
        )

    issues = []

    for number in range(71, 76):

        values = tokens[number]

        if not 3 <= len(values) <= 8:

            raise RuntimeError(
                f"Cau {number} co "
                "so cum tu khong hop le."
            )

        valid = any(
            compact("".join(order))
            == compact(answers[number])

            for order in permutations(values)
        )

        if valid:
            continue

        # Cau 72: PDF de va dap an mau thuan.
        # Ghi nhan, khong tu dong thay doi.
        if number != 72:

            raise RuntimeError(
                f"Cau {number} khong ghep "
                "duoc dap an PDF."
            )

        issue = {
            "so_cau": 72,

            "loai": (
                "de_va_dap_an_khong_khop"
            ),

            "cum_tu_trong_de": values,

            "dap_an_trong_pdf": answers[72],

            "goi_y_theo_cum_tu": (
                "他的姓名被写错了。"
            ),

            "ghi_chu": (
                "PDF de ghi 他的姓名; "
                "PDF dap an ghi 他的名字. "
                "Can ra soat truoc khi nhap SQL."
            ),
        }

        # Kiem tra goi y that su co the
        # ghep tu cac cum trong PDF.
        suggested = issue[
            "goi_y_theo_cum_tu"
        ]

        if not any(
            compact("".join(order))
            == compact(suggested)

            for order in permutations(values)
        ):

            raise RuntimeError(
                "Goi y cau 72 khong "
                "ghep duoc tu PDF de."
            )

        issues.append(issue)

    return tokens, issues


# =====================================================
# 15. TACH HAI BANG HINH NGHE
# =====================================================

def extract_group_images(doc):

    images = {}

    for name, config in (
        GROUP_RECTS.items()
    ):

        page = doc[
            config["page"] - 1
        ]

        rect = fitz.Rect(
            config["rect"]
        )

        if not page.rect.contains(rect):

            raise RuntimeError(
                f"Toa do bang {name} "
                "nam ngoai trang."
            )

        labels = {
            str(word[4]).strip()

            for word in page.get_text("words")

            if rect.contains(
                fitz.Rect(word[:4])
            )
        }

        expected_labels = set(
            config["labels"]
        )

        if not expected_labels.issubset(
            labels
        ):

            raise RuntimeError(
                f"Bang {name} thieu nhan: "
                f"{expected_labels - labels}"
            )

        # Kiem tra anh goc khong bi cat.
        image_rects = []

        for image in page.get_images(full=True):

            image_rects.extend(
                page.get_image_rects(
                    image[0]
                )
            )

        inside = sum(
            rect.contains(image_rect)

            for image_rect in image_rects
        )

        if inside != len(config["labels"]):

            raise RuntimeError(
                f"Bang {name} co {inside} hinh, "
                f"can {len(config['labels'])}."
            )

        pix = page.get_pixmap(
            matrix=fitz.Matrix(2.5, 2.5),
            clip=rect,
            alpha=False
        )

        images[name] = pix.tobytes("png")

    return images


# =====================================================
# 16. TAO HTML KIEM TRA HINH
# =====================================================

def preview_html():

    cards = []

    for name, config in (
        GROUP_RECTS.items()
    ):

        first = config["first"]
        last = config["last"]

        numbers = "".join(
            f'<span class="pill">Câu {n}</span>'

            for n in range(
                first,
                last + 1
            )
        )

        cards.append(
            '<section>'
            f'<h2>Câu {first}–{last}</h2>'
            f'<img src="groups/{name}.png" '
            'alt="Bảng hình">'
            f'<div class="nums">{numbers}</div>'
            '</section>'
        )

    html = """
<!doctype html>
<html lang="vi">

<head>
<meta charset="utf-8">
<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>HSK3 Đề 7 - Kiểm tra câu 1–10</title>

<style>
body {
    font-family: Arial, sans-serif;
    background: #f4f6fa;
    color: #1e293b;
    max-width: 960px;
    margin: 25px auto;
    padding: 0 14px;
}

section {
    background: white;
    border: 1px solid #dbe2eb;
    border-radius: 14px;
    padding: 20px;
    margin: 16px 0;
}

img {
    display: block;
    max-width: 100%;
    height: auto;
    margin: auto;
}

.nums {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 18px;
}

.pill {
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 9px 12px;
    font-weight: bold;
}
</style>

</head>

<body>

<h1>HSK3 – Đề 7 (H31007)</h1>

<p>
Kiểm tra hình câu 1–10.
Không hiển thị đáp án.
</p>

__CARDS__

</body>
</html>
"""

    return html.replace(
        "__CARDS__",
        "\n".join(cards)
    ).encode("utf-8")


# =====================================================
# 17. LUU FILE AN TOAN
# =====================================================

def write_safe(path, content):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if path.exists():

        if path.read_bytes() != content:

            raise RuntimeError(
                "Khong ghi de file "
                "khac noi dung:\n"
                + str(path)
            )

    else:

        path.write_bytes(content)


# =====================================================
# 18. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 07 - BUOC 1")
    print("=" * 60)

    exam_pdf, answer_pdf, mp3 = (
        find_sources()
    )

    print("PDF de:", exam_pdf.name)
    print("PDF dap an:", answer_pdf.name)

    if mp3:
        print("MP3:", mp3.name)

    else:
        print(
            "Chua co MP3 - buoc 1 "
            "van chay duoc."
        )

    # ================================================
    # 19. DOC PDF VA DAP AN
    # ================================================

    with (
        fitz.open(exam_pdf) as exam,
        fitz.open(answer_pdf) as answer_doc
    ):

        check_pdf(exam)

        (
            answers,
            alternatives,
            raw_writing
        ) = read_answers(answer_doc)

        (
            tokens,
            issues
        ) = check_writing_compatibility(
            exam,
            answers
        )

        groups = extract_group_images(
            exam
        )

    # ================================================
    # 20. TAO JSON DAP AN
    # ================================================

    result = {
        "cap_hsk": 3,
        "so_de": 7,
        "ma_de_goc": CODE,

        "file_pdf": str(exam_pdf),
        "file_dap_an": str(answer_pdf),

        "file_mp3": (
            str(mp3)
            if mp3 else None
        ),

        "nguon_dap_an": "pdf_rieng",

        "so_trang_pdf_de": 14,
        "so_trang_pdf_dap_an": 2,

        "tong_cau": 80,
        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "thoi_gian_pdf_phut": 90,

        "thoi_gian_lam_bai_de_xuat_phut": 85,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        # De 7 khong co transcript.
        "trang_loi_thoai": [],

        # Thuoc PDF dap an rieng.
        "trang_dap_an": [1, 2],

        "bang_trang_cau_hoi": {
            str(page): list(numbers)

            for page, numbers
            in PAGE_QUESTIONS.items()
        },

        "bang_hinh_chung": {
            name: {
                "trang_pdf": config["page"],
                "lua_chon": config["labels"],
                "anh": f"groups/{name}.png",
            }

            for name, config
            in GROUP_RECTS.items()
        },

        "dap_an": {
            str(number): answers[number]

            for number in range(1, 81)
        },

        "dap_an_thay_the": alternatives,

        "dap_an_pdf_nguyen_van": {
            str(number): raw_writing[number]

            for number in range(71, 81)
        },

        "cum_tu_sap_xep": {
            str(number): tokens[number]

            for number in range(71, 76)
        },

        # Canh bao cau 72, giu nguyen
        # nguon de doi chieu khi chuan hoa.
        "can_ra_soat": issues,

        "cau_hoi": [],
    }

    # ================================================
    # 21. TAO DANH SACH 80 CAU
    # ================================================

    for number in range(1, 81):

        page = next(
            page_no

            for page_no, numbers
            in PAGE_QUESTIONS.items()

            if number in numbers
        )

        if number <= 5:
            group = "nghe_01_05"

        elif number <= 10:
            group = "nghe_06_10"

        else:
            group = None

        section = (
            "nghe"
            if number <= 40
            else "doc"
            if number <= 70
            else "viet"
        )

        result["cau_hoi"].append({
            "so_cau": number,
            "phan": section,
            "trang_pdf": page,

            "dap_an_dung": answers[number],

            "nhom_hinh": group,
            "da_duyet": False,
        })

    # ================================================
    # 22. CHUAN BI FILE DAU RA
    # ================================================

    json_content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    outputs = {
        ANSWER_JSON: json_content,
        PREVIEW_HTML: preview_html(),
    }

    for name, content in groups.items():

        outputs[
            GROUP_DIR / f"{name}.png"
        ] = content

    # Khong ghi de file cu khac noi dung.
    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):

            raise RuntimeError(
                "File da ton tai voi "
                "noi dung khac:\n"
                + str(path)
            )

    # ================================================
    # 23. LUU FILE
    # ================================================

    for path, content in outputs.items():

        write_safe(path, content)

    # ================================================
    # 24. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH HSK3 DE 07 - BUOC 1")
    print("=" * 60)

    print("PDF de: 14 trang")
    print("PDF dap an: 2 trang")

    print("Nghe: 40")
    print("Doc: 30")
    print("Viet: 10")

    print("Dap an: 80/80")

    print("Bang hinh cau 1-5: 6 lua chon")
    print("Bang hinh cau 6-10: 5 lua chon")

    print(
        "Cau 77: da luu "
        "2 dap an hop le (元, 圆)"
    )

    if issues:

        print("\nCAN RA SOAT CAU 72:")

        print(
            "De ghi: 他的姓名"
        )

        print(
            "Dap an PDF: "
            "他的名字被写错了。"
        )

        print(
            "Goi y theo cum tu de: "
            "他的姓名被写错了。"
        )

        print(
            "Chua tu dong sua dap an."
        )

    print(f"\nJSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
