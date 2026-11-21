
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 01 - H31001

BUOC 1:
- Doc PDF goc 22 trang.
- Xac nhan ma de H31001.
- Kiem tra bo cuc 80 cau.
- Lay 70 dap an Nghe/Doc o trang 21.
- Lay 10 dap an Viet o trang 22.
- Doi chieu 80/80 dap an.
- Tach 2 bang hinh chung cau 1-10.
- Tao JSON dap an va HTML xem truoc.

Khong thay doi SQL Server.
Khong anh huong HSK1/HSK2.
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

HSK3 = (
    ROOT / "scripts" / "luyen_thi" / "hsk3"
)

SOURCE = (
    ROOT / "scripts" / "luyen_thi"
    / "source" / "De_HSK" / "HSK3" / "ĐỀ 1"
)

PDF_FILE = (
    SOURCE / "Đề thi tiếng Trung HSK3 SỐ 1.pdf"
)

MP3_FILE = (
    SOURCE / "Đề thi tiếng Trung HSK3 SỐ 1.mp3"
)

DATA = HSK3 / "data" / "de_01"
OUTPUT = HSK3 / "output" / "de_01"
GROUP_DIR = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_01_dap_an.json"
PREVIEW_HTML = OUTPUT / "kiem_tra_10_cau.html"

EXAM_CODE = "H31001"
EXAM_NUMBER = 1


# =====================================================
# 2. BO CUC DE
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

TRANSCRIPT_PAGES = list(range(15, 21))
ANSWER_PAGES = [21, 22]

# Toa do da doi chieu tren PDF H31001.
# Chi cat khu vuc hinh, bo qua cau vi du
# va cac o dien dap an.
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
# 3. DAP AN GOC PHAN NGHE + DOC
# =====================================================

EXPECTED_ROWS = [
    "B C E F A",
    "B C A D E",
    "× √ × √ √",
    "× √ √ × ×",
    "B C C C B",
    "C A A B C",
    "B B B C A",
    "C A C A A",
    "C B A D F",
    "B D E A C",
    "F D C B A",
    "A B E F C",
    "A A C B B",
    "A A B B C",
]


# =====================================================
# 4. DAP AN GOC PHAN VIET
# =====================================================

EXPECTED_WRITING = {
    71: "弟弟高兴地笑了。",
    72: "上午的考试比较简单。",
    73: "这个城市的环境变得越来越好了。",
    74: "那位医生送给他一个礼物。",
    75: "其他班的成绩也有很大提高。",
    76: "出",
    77: "元",
    78: "叫",
    79: "中",
    80: "米",
}


# =====================================================
# 5. HAM HO TRO
# =====================================================

def normalize(text):
    return unicodedata.normalize(
        "NFKC", str(text)
    )


def normalize_code(text):
    return re.sub(
        r"[^A-Z0-9]",
        "",
        normalize(text).upper()
    )


def check_file(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay file:\n{path}"
        )

    if path.stat().st_size == 0:
        raise RuntimeError(
            f"File rong: {path}"
        )


def write_safe(path, content):
    """
    Neu file da ton tai va noi dung khac
    thi khong tu dong ghi de.
    """
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if path.exists():
        if path.read_bytes() != content:
            raise RuntimeError(
                "File da ton tai nhung noi dung khac."
                "\nKhong ghi de:\n"
                + str(path)
            )
        return

    path.write_bytes(content)


def expected_objective_answers():
    result = {}

    for row_index, row in enumerate(EXPECTED_ROWS):
        values = row.split()

        if len(values) != 5:
            raise RuntimeError(
                "Dap an mau sai dinh dang."
            )

        for index, value in enumerate(values):
            number = row_index * 5 + index + 1
            result[number] = value

    if set(result) != set(range(1, 71)):
        raise RuntimeError(
            "Bang dap an mau khong du 70 cau."
        )

    return result


EXPECTED_OBJECTIVE = expected_objective_answers()


# =====================================================
# 6. KIEM TRA KIEU DAP AN
# =====================================================

def validate_objective_answer(number, answer):
    if 1 <= number <= 5:
        allowed = set("ABCDEF")

    elif 6 <= number <= 10:
        allowed = set("ABCDE")

    elif 11 <= number <= 20:
        allowed = {"√", "×"}

    elif 21 <= number <= 40:
        allowed = set("ABC")

    elif 41 <= number <= 45:
        allowed = set("ABCDEF")

    elif 46 <= number <= 50:
        allowed = set("ABCDE")

    elif 51 <= number <= 60:
        allowed = set("ABCDEF")

    elif 61 <= number <= 70:
        allowed = set("ABC")

    else:
        raise RuntimeError(
            f"Cau {number} khong thuoc Nghe/Doc."
        )

    if answer not in allowed:
        raise RuntimeError(
            f"Dap an cau {number} sai dang: "
            f"{answer}"
        )


# =====================================================
# 7. DOC DAP AN TRANG 21
# =====================================================

def extract_objective_answers(page):
    text = normalize(
        page.get_text("text")
    )

    if "答案" not in text:
        raise RuntimeError(
            "Trang 21 khong co tieu de 答案."
        )

    pattern = re.compile(
        r"(?<!\d)(\d{1,2})\s*[.、]\s*"
        r"([A-F√×])(?=\s|$)"
    )

    answers = {}

    for match in pattern.finditer(text):
        number = int(match.group(1))
        answer = match.group(2)

        if not 1 <= number <= 70:
            continue

        if number in answers:
            raise RuntimeError(
                f"Trung dap an cau {number}."
            )

        validate_objective_answer(
            number, answer
        )

        answers[number] = answer

    if set(answers) != set(range(1, 71)):
        missing = sorted(
            set(range(1, 71)) - set(answers)
        )
        raise RuntimeError(
            f"Thieu dap an Nghe/Doc: {missing}"
        )

    for number in range(1, 71):
        if answers[number] != EXPECTED_OBJECTIVE[number]:
            raise RuntimeError(
                f"Dap an cau {number} khong khop."
            )

    return answers


# =====================================================
# 8. DOC DAP AN PHAN VIET TRANG 22
# =====================================================

def extract_writing_answers(page):
    text = normalize(
        page.get_text("text")
    )

    if "书" not in text or "写" not in text:
        raise RuntimeError(
            "Trang 22 khong phai dap an Viet."
        )

    pattern = re.compile(
        r"^\s*(7[1-9]|80)\s*[.、]\s*"
        r"([^\n]+)",
        re.MULTILINE
    )

    answers = {}

    for match in pattern.finditer(text):
        number = int(match.group(1))
        answer = match.group(2).strip()

        if number in answers:
            raise RuntimeError(
                f"Trung dap an cau {number}."
            )

        answers[number] = answer

    if set(answers) != set(range(71, 81)):
        raise RuntimeError(
            "Trang 22 khong du 10 dap an Viet."
        )

    for number in range(71, 81):
        if answers[number] != EXPECTED_WRITING[number]:
            raise RuntimeError(
                f"Dap an Viet cau {number} khong khop."
                f"\nPDF: {answers[number]}"
                f"\nGoc: {EXPECTED_WRITING[number]}"
            )

    return answers


# =====================================================
# 9. KIEM TRA TIEU DE TRANG
# =====================================================

def has_heading(page, first, last):
    text = normalize(
        page.get_text("text")
    )

    pattern = (
        rf"第\s*{first}\s*[-–—]\s*"
        rf"{last}\s*题"
    )

    return bool(
        re.search(pattern, text)
    )


def check_pdf(doc):
    if len(doc) != 22:
        raise RuntimeError(
            f"PDF co {len(doc)} trang, "
            "H31001 phai co 22 trang."
        )

    cover = normalize_code(
        doc[0].get_text("text")
    )

    if EXAM_CODE not in cover:
        raise RuntimeError(
            "Trang bia khong phai H31001."
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
        if not has_heading(
            doc[page_no - 1],
            first,
            last
        ):
            raise RuntimeError(
                f"Trang {page_no} thieu "
                f"tieu de cau {first}-{last}."
            )

    transcript = normalize(
        doc[14].get_text("text")
    )

    if "听力材料" not in transcript:
        raise RuntimeError(
            "Trang 15 khong phai loi thoai Nghe."
        )

    answer_page_21 = normalize(
        doc[20].get_text("text")
    )

    if "答案" not in answer_page_21:
        raise RuntimeError(
            "Trang 21 khong phai bang dap an."
        )

    print("\n===== BO CUC PDF =====")
    print("PDF: 22 trang")
    print("Trang 2-6: Nghe 40 cau")
    print("Trang 7-12: Doc 30 cau")
    print("Trang 13-14: Viet 10 cau")
    print("Trang 15-20: loi thoai Nghe")
    print("Trang 21: dap an Nghe/Doc")
    print("Trang 22: dap an Viet")


# =====================================================
# 10. XAC DINH DANG CAU HOI
# =====================================================

def question_type(number):
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
        return "sap_xep_tu"

    return "dien_chu_han"


def question_section(number):
    if number <= 40:
        return "nghe"

    if number <= 70:
        return "doc"

    return "viet"


def question_page(number):
    for page_no, numbers in PAGE_QUESTIONS.items():
        if number in numbers:
            return page_no

    raise RuntimeError(
        f"Khong co trang cho cau {number}."
    )


# =====================================================
# 11. TAO 2 BANG HINH CHUNG
# =====================================================

def render_groups(doc):
    result = {}

    for group, config in GROUP_RECTS.items():
        page_no = config["trang_pdf"]

        page = doc[page_no - 1]
        rect = fitz.Rect(config["rect"])

        if not page.rect.contains(rect):
            raise RuntimeError(
                f"Toa do anh {group} khong hop le."
            )

        # Kiem tra cac nhan A-F/A-E.
        found = set()

        for word in page.get_text("words"):
            x0, y0, x1, y1, value = word[:5]

            value = normalize(value).strip()

            if (
                len(value) == 1
                and value in config["lua_chon"]
                and rect.contains(
                    fitz.Point(x0, y0)
                )
            ):
                found.add(value)

        expected_labels = set(
            config["lua_chon"]
        )

        if found != expected_labels:
            raise RuntimeError(
                f"Bang {group} thieu nhan."
                f"\nTim thay: {sorted(found)}"
            )

        pix = page.get_pixmap(
            matrix=fitz.Matrix(2.5, 2.5),
            clip=rect,
            alpha=False
        )

        result[group] = pix.tobytes("png")

        print(
            f"{group}: trang {page_no}, "
            f"{len(found)} lua chon"
        )

    return result


# =====================================================
# 12. TAO HTML KIEM TRA
# =====================================================

def create_preview():
    blocks = []

    for first, last, group in [
        (1, 5, "nghe_01_05"),
        (6, 10, "nghe_06_10"),
    ]:
        numbers = "".join(
            f'<span class="number">Câu {n}</span>'
            for n in range(first, last + 1)
        )

        blocks.append(
            f"""
<section class="card">
    <h2>Câu {first}–{last}</h2>

    <img
        src="groups/{group}.png"
        alt="Bảng hình câu {first}-{last}"
    >

    <div class="numbers">
        {numbers}
    </div>
</section>
"""
        )

    html = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>HSK3 Đề 1 - H31001</title>

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

.container {
    max-width: 1000px;
    margin: auto;
}

h1 {
    font-size: 25px;
}

p {
    color: #64748b;
    line-height: 1.6;
}

.card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px;
    margin-top: 20px;
}

.card h2 {
    font-size: 19px;
}

.card img {
    display: block;
    width: 100%;
    height: auto;
    object-fit: contain;
    max-width: 750px;
    margin: auto;
}

.numbers {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 20px;
}

.number {
    padding: 10px 14px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-weight: bold;
}
</style>
</head>

<body>
<div class="container">

<h1>HSK3 – Đề 1 (H31001)</h1>

<p>
Kiểm tra bảng hình chung câu 1–10.
Chưa hiển thị đáp án.
Chưa thay đổi SQL Server.
</p>

__BLOCKS__

</div>
</body>
</html>
"""

    return html.replace(
        "__BLOCKS__",
        "\n".join(blocks)
    ).encode("utf-8")


# =====================================================
# 13. CHUONG TRINH CHINH
# =====================================================

def main():
    print("=" * 60)
    print("MOC HAN - HSK3 DE 01")
    print("MA DE H31001")
    print("=" * 60)

    check_file(PDF_FILE)

    if MP3_FILE.is_file():
        check_file(MP3_FILE)
        print(f"MP3: {MP3_FILE.name}")
    else:
        print(
            "CANH BAO: Chua tim thay MP3."
            "\nVan co the tach anh truoc."
        )

    with fitz.open(PDF_FILE) as doc:
        check_pdf(doc)

        objective = extract_objective_answers(
            doc[20]
        )

        writing = extract_writing_answers(
            doc[21]
        )

        answers = {
            **objective,
            **writing
        }

        if set(answers) != set(range(1, 81)):
            raise RuntimeError(
                "Khong du 80 dap an."
            )

        print("\n===== 80 DAP AN =====")

        for start in range(1, 71, 5):
            row = " ".join(
                answers[n]
                for n in range(start, start + 5)
            )

            print(
                f"{start:02d}-{start+4:02d}: {row}"
            )

        print("\n===== PHAN VIET =====")

        for number in range(71, 81):
            print(
                f"{number}: {answers[number]}"
            )

        print("\nDoi chieu PDF: 80/80 KHOP")

        # Tach 2 bang hinh cau 1-10.
        print("\n===== TACH BANG HINH =====")
        groups = render_groups(doc)

    # ================================================
    # 14. TAO DANH SACH 80 CAU HOI
    # ================================================

    questions = []

    for number in range(1, 81):
        group = None

        if 1 <= number <= 5:
            group = "nghe_01_05"

        elif 6 <= number <= 10:
            group = "nghe_06_10"

        questions.append({
            "so_cau": number,
            "phan": question_section(number),
            "dang": question_type(number),
            "trang_pdf": question_page(number),
            "dap_an_dung": answers[number],
            "nhom_hinh": group,
            "da_duyet": False,
        })

    result = {
        "cap_hsk": 3,
        "so_de": EXAM_NUMBER,
        "ma_de_goc": EXAM_CODE,

        "file_pdf": str(PDF_FILE),
        "file_mp3": (
            str(MP3_FILE)
            if MP3_FILE.is_file()
            else None
        ),

        "nguon_dap_an": "pdf_chung",
        "so_trang_pdf_de": 22,

        "tong_cau": 80,
        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        # PDF 90 phut gom 5 phut dien
        # thong tin ca nhan.
        "thoi_gian_pdf_phut": 90,
        "thoi_gian_lam_bai_de_xuat_phut": 85,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        "trang_loi_thoai": TRANSCRIPT_PAGES,
        "trang_dap_an": ANSWER_PAGES,

        "bang_trang_cau_hoi": {
            str(page): numbers
            for page, numbers
            in PAGE_QUESTIONS.items()
        },

        "bang_hinh_chung": {
            name: {
                "trang_pdf": config["trang_pdf"],
                "lua_chon": config["lua_chon"],
                "anh": f"groups/{name}.png",
            }
            for name, config
            in GROUP_RECTS.items()
        },

        "dap_an": {
            str(number): answers[number]
            for number in range(1, 81)
        },

        "cau_hoi": questions,
    }

    json_content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    html_content = create_preview()

    # ================================================
    # 15. BAO VE FILE CU TRUOC KHI GHI
    # ================================================

    outputs = {
        ANSWER_JSON: json_content,
        PREVIEW_HTML: html_content,
    }

    for name, content in groups.items():
        outputs[
            GROUP_DIR / f"{name}.png"
        ] = content

    for path, content in outputs.items():
        if (
            path.exists()
            and path.read_bytes() != content
        ):
            raise RuntimeError(
                "File da co voi noi dung khac."
                "\nKhong ghi de:\n"
                + str(path)
            )

    # ================================================
    # 16. LUU JSON, ANH VA HTML
    # ================================================

    for path, content in outputs.items():
        write_safe(path, content)

    print("\n" + "=" * 60)
    print("HOAN THANH HSK3 DE 01 - BUOC 1")
    print("=" * 60)

    print("Ma de: H31001")
    print("PDF: 22 trang")
    print("Nghe: 40 cau")
    print("Doc: 30 cau")
    print("Viet: 10 cau")
    print("Dap an: 80/80")

    print("Bang hinh cau 1-5: 6 lua chon")
    print("Bang hinh cau 6-10: 5 lua chon")

    print(f"\nJSON: {ANSWER_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
