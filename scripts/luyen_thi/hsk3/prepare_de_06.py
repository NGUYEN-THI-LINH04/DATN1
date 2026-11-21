
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 06 (H31006) - BUOC 1.

- PDF goc 16 trang (KHONG co trang loi thoai Nghe).
- 70 dap an Nghe/Doc: trang 15.
- 10 dap an Viet: trang 16.
- Cau 75 co 2 dap an hop le; luu ca hai.
- Tach 2 bang hinh chung cau 1-10.
- Tao JSON va HTML xem truoc.

Khong ket noi SQL Server.
Khong thay doi cac de cu.
"""

from pathlib import Path
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
    / "HSK3" / "ĐỀ 6"
)

DATA = BASE / "hsk3" / "data" / "de_06"

OUTPUT = BASE / "hsk3" / "output" / "de_06"

GROUP_DIR = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_06_dap_an.json"

PREVIEW_HTML = OUTPUT / "kiem_tra_10_cau.html"

EXAM_CODE = "H31006"
EXAM_NUMBER = 6


# =====================================================
# 2. SO DO TRANG CAU HOI
# =====================================================

PAGE_QUESTIONS = {
    2: list(range(1, 6)),
    3: list(range(6, 11)),
    4: list(range(11, 21)),
    5: list(range(21, 31)),
    6: list(range(31, 41)),
    7: list(range(41, 46)),
    8: list(range(46, 51)),
    9: list(range(51, 56)),
    10: list(range(56, 61)),
    11: list(range(61, 65)),
    12: list(range(65, 71)),
    13: list(range(71, 76)),
    14: list(range(76, 81)),
}


# =====================================================
# 3. HAI BANG HINH CHUNG
# =====================================================

GROUP_RECTS = {
    "nghe_01_05": {
        "trang_pdf": 2,
        "rect": (75, 175, 515, 515),
        "lua_chon": "ABCDEF",
    },

    "nghe_06_10": {
        "trang_pdf": 3,
        "rect": (75, 130, 515, 522),
        "lua_chon": "ABCDE",
    },
}


# =====================================================
# 4. DAP AN H31006 - NGHE/DOC
# =====================================================

# Dap an 1-70 theo trang 15 PDF.

EXPECTED_ROWS = [
    "A E C F B",
    "D C E B A",

    "× √ × × ×",
    "√ √ × √ √",

    "A C A C A",
    "B B A A B",

    "C C C B A",
    "B B B A A",

    "B F C D A",
    "C A B E D",

    "A F C B D",
    "C A F E B",

    "C C B C B",
    "A B C C A",
]


# =====================================================
# 5. DAP AN H31006 - PHAN VIET
# =====================================================

# Trang 16 cua PDF.
# Cau 75 co hai dap an hop le.

EXPECTED_WRITING = {
    71: ["咖啡里不要放糖。"],

    72: ["把碗和筷子洗干净了吗？"],

    73: ["孩子突然发烧了。"],

    74: ["看到这个句子表示游戏结束。"],

    75: [
        "她对这条绿裤子很满意。",
        "对这条绿裤子，她很满意。",
    ],

    76: ["也"],
    77: ["日"],
    78: ["在"],
    79: ["多"],
    80: ["为"],
}


# =====================================================
# 6. HAM HO TRO
# =====================================================

def norm(value):

    return unicodedata.normalize(
        "NFKC",
        str(value)
    )


def compact(value):

    return re.sub(
        r"\s+",
        "",
        norm(value)
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
# 7. TIM PDF VA MP3 NGUON
# =====================================================

def find_sources():

    pdf_files = sorted(
        SOURCE.glob("*.pdf")
    )

    mp3_files = sorted(
        SOURCE.glob("*.mp3")
    )

    if len(pdf_files) != 1:
        raise RuntimeError(
            f"Thu muc {SOURCE} can dung 1 PDF."
            f"\nTim thay: {len(pdf_files)}"
        )

    if len(mp3_files) > 1:
        raise RuntimeError(
            "Thu muc DE 6 co nhieu MP3."
        )

    pdf_file = check_file(
        pdf_files[0]
    )

    mp3_file = (
        check_file(mp3_files[0])
        if mp3_files else None
    )

    return pdf_file, mp3_file


# =====================================================
# 8. TAO BANG 70 DAP AN MAU
# =====================================================

def expected_objective():

    answers = {}

    for row_index, line in enumerate(
        EXPECTED_ROWS
    ):

        values = line.split()

        if len(values) != 5:
            raise RuntimeError(
                f"Dong dap an {row_index + 1} "
                "khong du 5 cau."
            )

        for offset, answer in enumerate(values):

            number = (
                row_index * 5 + offset + 1
            )

            answers[number] = answer

    if set(answers) != set(range(1, 71)):
        raise RuntimeError(
            "Bang dap an mau khong du 70 cau."
        )

    return answers


EXPECTED_OBJECTIVE = expected_objective()


# =====================================================
# 9. KIEM TRA DANG DAP AN
# =====================================================

def valid_answer(number, value):

    if number <= 5:
        allowed = set("ABCDEF")

    elif number <= 10:
        allowed = set("ABCDE")

    elif number <= 20:
        allowed = {"√", "×"}

    elif number <= 40:
        allowed = set("ABC")

    elif number <= 45:
        allowed = set("ABCDEF")

    elif number <= 50:
        allowed = set("ABCDE")

    elif number <= 60:
        allowed = set("ABCDEF")

    else:
        allowed = set("ABC")

    if value not in allowed:
        raise RuntimeError(
            f"Dap an cau {number} "
            f"ngoai lua chon: {value}"
        )


# =====================================================
# 10. KIEM TRA PDF GOC
# =====================================================

def check_pdf(doc):

    if len(doc) != 16:
        raise RuntimeError(
            f"H31006 phai co 16 trang, "
            f"nhung PDF co {len(doc)}."
        )

    # Trang 16 la dap an Viet,
    # khong bat buoc lap lai ma de.

    for page_no in (1, 15):

        text = compact(
            doc[page_no - 1].get_text("text")
        )

        if EXAM_CODE not in text:
            raise RuntimeError(
                f"Trang {page_no} khong co "
                f"ma de {EXAM_CODE}."
            )

    headings = [
        (2, 1, 5),
        (3, 6, 10),
        (4, 11, 20),
        (5, 21, 30),
        (6, 31, 40),
        (7, 41, 45),
        (8, 46, 50),
        (9, 51, 55),
        (10, 56, 60),
        (11, 61, 70),
        (13, 71, 75),
        (14, 76, 80),
    ]

    for page_no, first, last in headings:

        text = norm(
            doc[page_no - 1].get_text("text")
        )

        pattern = (
            rf"第\s*{first}\s*[-–—]"
            rf"\s*{last}\s*题"
        )

        if not re.search(pattern, text):
            raise RuntimeError(
                f"Trang {page_no} thieu "
                f"tieu de {first}-{last}."
            )

    if "答案" not in doc[14].get_text("text"):
        raise RuntimeError(
            "Trang 15 khong phai "
            "dap an Nghe/Doc."
        )

    if "书" not in doc[15].get_text("text"):
        raise RuntimeError(
            "Trang 16 khong phai dap an Viet."
        )

    print("\n===== BO CUC PDF =====")

    print("PDF: 16 trang")
    print("Nghe: 40 cau")
    print("Doc: 30 cau")
    print("Viet: 10 cau")

    print("Trang 2-14: de thi")
    print("Trang 15: dap an Nghe/Doc")
    print("Trang 16: dap an Viet")

    print(
        "PDF khong co trang loi thoai Nghe."
    )


# =====================================================
# 11. DOC 70 DAP AN NGHE/DOC
# =====================================================

def read_objective(page):

    text = norm(
        page.get_text("text")
    )

    pattern = re.compile(
        r"(?<!\d)(\d{1,2})\s*[.、]"
        r"\s*([A-F√×])(?=\s|$)"
    )

    answers = {}

    for match in pattern.finditer(text):

        number = int(
            match.group(1)
        )

        if not 1 <= number <= 70:
            continue

        if number in answers:
            raise RuntimeError(
                f"Trung dap an cau {number}."
            )

        value = match.group(2)

        valid_answer(
            number,
            value
        )

        answers[number] = value

    if set(answers) != set(range(1, 71)):

        missing = sorted(
            set(range(1, 71)) - set(answers)
        )

        raise RuntimeError(
            f"Thieu dap an: {missing}"
        )

    # Doi chieu 70 dap an voi bang goc.

    for number in range(1, 71):

        if (
            answers[number]
            != EXPECTED_OBJECTIVE[number]
        ):
            raise RuntimeError(
                f"Dap an cau {number} "
                "khac dap an da doi chieu."
            )

    return answers


# =====================================================
# 12. DOC 10 DAP AN VIET
# =====================================================

def read_writing(page):

    # Giu nguyen chu Han va dau cau.

    text = page.get_text("text")

    pattern = re.compile(
        r"^\s*(7[1-9]|80)\s*[.．、]"
        r"\s*([^\n]+)",
        re.MULTILINE
    )

    raw = {}

    for match in pattern.finditer(text):

        number = int(match.group(1))

        if number in raw:
            raise RuntimeError(
                f"Trung dap an Viet cau {number}."
            )

        raw[number] = (
            match.group(2).strip()
        )

    if set(raw) != set(range(71, 81)):

        missing = sorted(
            set(range(71, 81)) - set(raw)
        )

        raise RuntimeError(
            f"Thieu dap an Viet: {missing}"
        )

    answers = {}
    alternatives = {}

    for number in range(71, 81):

        values = [
            part.strip()

            for part in (
                raw[number].split("/")
            )

            if part.strip()
        ]

        expected = EXPECTED_WRITING[number]

        if len(values) != len(expected):
            raise RuntimeError(
                f"Cau {number} sai "
                "so luong dap an."
            )

        for actual, reference in zip(
            values,
            expected
        ):

            if (
                compact(actual)
                != compact(reference)
            ):
                raise RuntimeError(
                    f"Cau {number} sai dap an."
                    f"\nPDF: {actual}"
                    f"\nGoc: {reference}"
                )

        # Dap an dau la dap an chinh.

        answers[number] = values[0]

        # Luu dap an thay the neu co.

        if len(values) > 1:
            alternatives[str(number)] = (
                values[1:]
            )

    if set(alternatives) != {"75"}:
        raise RuntimeError(
            "De 6 phai giu dap an "
            "thay the cua cau 75."
        )

    return answers, alternatives, raw


# =====================================================
# 13. XAC DINH KY NANG
# =====================================================

def section(number):

    if number <= 40:
        return "nghe"

    if number <= 70:
        return "doc"

    return "viet"


# =====================================================
# 14. XAC DINH DANG CAU HOI
# =====================================================

def kind(number):

    if number <= 10:
        return "chon_hinh"

    if number <= 20:
        return "dung_sai"

    if number <= 40:
        return "chon_mot"

    if number <= 60:
        return "ghep_lua_chon"

    if number <= 70:
        return "chon_mot"

    if number <= 75:
        return "sap_xep"

    return "dien_tu"


# =====================================================
# 15. XAC DINH TRANG PDF CUA MOI CAU
# =====================================================

def page_for(number):

    for page_no, numbers in (
        PAGE_QUESTIONS.items()
    ):

        if number in numbers:
            return page_no

    raise RuntimeError(
        f"Khong tim thay trang cau {number}."
    )


# =====================================================
# 16. TACH HAI BANG HINH CAU 1-10
# =====================================================

def render_groups(doc):

    groups = {}

    for name, config in (
        GROUP_RECTS.items()
    ):

        page_no = config["trang_pdf"]

        page = doc[page_no - 1]

        rect = fitz.Rect(
            config["rect"]
        )

        if not page.rect.contains(rect):
            raise RuntimeError(
                f"Toa do bang {name} "
                "ngoai trang PDF."
            )

        labels = set()

        for word in page.get_text("words"):

            x0, y0, _, _, value = word[:5]

            value = norm(
                value
            ).strip()

            if (
                len(value) == 1
                and value in config["lua_chon"]
                and rect.contains(
                    fitz.Point(x0, y0)
                )
            ):
                labels.add(value)

        expected = set(
            config["lua_chon"]
        )

        if labels != expected:

            missing = sorted(
                expected - labels
            )

            raise RuntimeError(
                f"Bang {name} thieu "
                f"nhan: {missing}"
            )

        pix = page.get_pixmap(
            matrix=fitz.Matrix(2.5, 2.5),
            clip=rect,
            alpha=False
        )

        groups[name] = (
            pix.tobytes("png")
        )

        print(
            f"{name}: trang {page_no}, "
            f"{len(labels)} lua chon"
        )

    return groups


# =====================================================
# 17. TAO HTML XEM TRUOC
# =====================================================

def preview_html():

    cards = []

    group_info = [
        (1, 5, "nghe_01_05"),
        (6, 10, "nghe_06_10"),
    ]

    for first, last, name in group_info:

        labels = "".join(
            f'<span class="num">Câu {n}</span>'

            for n in range(
                first,
                last + 1
            )
        )

        cards.append(
            f'<section>'
            f'<h2>Câu {first}–{last}</h2>'
            f'<img src="groups/{name}.png" '
            f'alt="Bảng hình {first}-{last}">'
            f'<div class="nums">{labels}</div>'
            f'</section>'
        )

    html = """
<!DOCTYPE html>
<html lang="vi">

<head>
<meta charset="UTF-8">
<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>HSK3 Đề 6 - H31006</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 24px;
    background: #f3f5f9;
    color: #1e293b;
    font-family: Arial, sans-serif;
}

main {
    max-width: 1000px;
    margin: auto;
}

section {
    background: #fff;
    border: 1px solid #dde4ef;
    border-radius: 14px;
    padding: 20px;
    margin: 18px 0;
}

section img {
    display: block;
    width: 100%;
    max-width: 750px;
    height: auto;
    object-fit: contain;
    margin: auto;
}

.nums {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 20px;
}

.num {
    padding: 10px 14px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-weight: bold;
}

p {
    color: #64748b;
    line-height: 1.6;
}
</style>

</head>

<body>
<main>

<h1>HSK3 – Đề 6 (H31006)</h1>

<p>
Kiểm tra bảng hình câu 1–10.
Không hiển thị đáp án.
Chưa thay đổi SQL Server.
</p>

__CARDS__

</main>
</body>
</html>
"""

    return html.replace(
        "__CARDS__",
        "\n".join(cards)
    ).encode("utf-8")


# =====================================================
# 18. LUU FILE AN TOAN
# =====================================================

def save_safe(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if path.exists():

        if path.read_bytes() != data:
            raise RuntimeError(
                "File da ton tai voi "
                "noi dung khac.\n"
                "Khong ghi de:\n"
                + str(path)
            )

        return

    path.write_bytes(data)


# =====================================================
# 19. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 06")
    print("BUOC 1 - H31006")
    print("=" * 60)

    pdf_file, mp3_file = (
        find_sources()
    )

    print(f"PDF: {pdf_file.name}")

    if mp3_file:
        print(f"MP3: {mp3_file.name}")

    else:
        print(
            "Chua co MP3 trong thu muc DE 6."
            "\nVan duoc chay buoc 1."
        )

    # ================================================
    # 20. KIEM TRA PDF VA DAP AN
    # ================================================

    with fitz.open(pdf_file) as doc:

        check_pdf(doc)

        # Trang 15 -> index 14.
        objective = read_objective(
            doc[14]
        )

        # Trang 16 -> index 15.
        (
            writing,
            alternatives,
            raw_writing
        ) = read_writing(
            doc[15]
        )

        answers = {
            **objective,
            **writing
        }

        if set(answers) != set(range(1, 81)):
            raise RuntimeError(
                "Khong du 80 dap an."
            )

        print("\n===== DAP AN NGHE/DOC =====")

        for first in range(1, 71, 5):

            row = " ".join(
                answers[number]

                for number in range(
                    first,
                    first + 5
                )
            )

            print(
                f"{first:02d}-{first+4:02d}: "
                f"{row}"
            )

        print("\n===== DAP AN VIET =====")

        for number in range(71, 81):
            print(
                f"{number}: {answers[number]}"
            )

        print(
            "\nDap an thay the cau 75: "
            + alternatives["75"][0]
        )

        print("\nDoi chieu PDF: 80/80 KHOP")

        # ============================================
        # 21. TACH HAI BANG HINH
        # ============================================

        print("\n===== TACH BANG HINH =====")

        groups = render_groups(
            doc
        )

    # ================================================
    # 22. TAO DANH SACH 80 CAU
    # ================================================

    questions = []

    for number in range(1, 81):

        if number <= 5:
            group = "nghe_01_05"

        elif number <= 10:
            group = "nghe_06_10"

        else:
            group = None

        questions.append({
            "so_cau": number,
            "phan": section(number),
            "dang": kind(number),
            "trang_pdf": page_for(number),
            "dap_an_dung": answers[number],
            "nhom_hinh": group,
            "da_duyet": False,
        })

    # ================================================
    # 23. TAO JSON DAP AN
    # ================================================

    result = {
        "cap_hsk": 3,
        "so_de": EXAM_NUMBER,
        "ma_de_goc": EXAM_CODE,

        "file_pdf": str(pdf_file),

        "file_mp3": (
            str(mp3_file)
            if mp3_file else None
        ),

        "nguon_dap_an": "pdf_chung",
        "so_trang_pdf_de": 16,

        "tong_cau": 80,
        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "thoi_gian_pdf_phut": 90,
        "thoi_gian_lam_bai_de_xuat_phut": 85,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        # PDF De 6 khong co transcript.
        "trang_loi_thoai": [],

        "trang_dap_an": [15, 16],

        "bang_trang_cau_hoi": {
            str(page): numbers

            for page, numbers
            in PAGE_QUESTIONS.items()
        },

        "bang_hinh_chung": {
            name: {
                "trang_pdf": info["trang_pdf"],
                "lua_chon": info["lua_chon"],
                "anh": f"groups/{name}.png",
            }

            for name, info
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

        "cau_hoi": questions,
    }

    # ================================================
    # 24. CHUAN BI FILE DAU RA
    # ================================================

    outputs = {
        ANSWER_JSON: json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8"),

        PREVIEW_HTML: preview_html(),
    }

    for name, content in groups.items():

        outputs[
            GROUP_DIR / f"{name}.png"
        ] = content

    # ================================================
    # 25. BAO VE FILE CU
    # ================================================

    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):
            raise RuntimeError(
                "File da ton tai "
                "voi noi dung khac.\n"
                "Khong ghi de:\n"
                + str(path)
            )

    # ================================================
    # 26. LUU JSON, ANH VA HTML
    # ================================================

    for path, content in outputs.items():

        save_safe(
            path,
            content
        )

    # ================================================
    # 27. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH HSK3 DE 06 - BUOC 1"
    )

    print("=" * 60)

    print("Ma de: H31006")
    print("PDF: 16 trang")

    print("Nghe: 40")
    print("Doc: 30")
    print("Viet: 10")

    print("Dap an: 80/80")

    print("Bang hinh cau 1-5: 6 lua chon")
    print("Bang hinh cau 6-10: 5 lua chon")

    print("Cau 75: da luu 2 dap an hop le")

    print(f"\nJSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
