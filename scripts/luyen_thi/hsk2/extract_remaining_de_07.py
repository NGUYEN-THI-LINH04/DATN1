
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 7 (H21329)

BUOC 2:
- Giu nguyen 10 anh dau tien.
- Tach cau 11-60.
- Bo qua trang PDF so 8.
- Tao 6 bang lua chon chung.
- Tao JSON thong tin anh.
- Tao HTML kiem tra 60 cau.

PDF de thi: 14 trang.
PDF dap an: file rieng.

Khong thay doi SQL Server.
Khong sua cac de HSK1 va HSK2 De 1-6.
"""

from pathlib import Path
import json
import re
import html
import hashlib
import unicodedata

import fitz


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

HSK2 = ROOT / "hsk2"

SOURCE = ROOT / "source" / "De_HSK" / "HSK2"

PDF_FILE = SOURCE / "Đề HSK 2 số 7.pdf"

DATA = HSK2 / "data" / "de_07"

OUTPUT = HSK2 / "output" / "de_07"

QUESTION_DIR = OUTPUT / "questions"

GROUP_DIR = OUTPUT / "groups"

ANSWER_FILE = DATA / "de_07_dap_an.json"

MANIFEST_FILE = (
    DATA / "hinh_60_cau_ung_vien.json"
)

HTML_FILE = OUTPUT / "kiem_tra_60_cau.html"

EXAM_CODE = "H21329"


# =====================================================
# 2. BANG TRANG PDF CHINH XAC
# =====================================================

PAGE_QUESTIONS = {
    2: list(range(1, 6)),
    3: list(range(6, 11)),

    4: list(range(11, 16)),
    5: list(range(16, 21)),

    6: list(range(21, 31)),
    7: list(range(31, 36)),

    # Trang 8 khong co cau hoi.

    9: list(range(36, 41)),
    10: list(range(41, 46)),

    11: [46, 47, 48],
    12: [49, 50],

    13: list(range(51, 56)),
    14: list(range(56, 61)),
}


GROUP_PAGES = {
    "nghe_11_15": 4,
    "nghe_16_20": 5,

    "doc_36_40": 9,
    "doc_41_45": 10,

    "doc_51_55": 13,
    "doc_56_60": 14,
}


GROUP_START = {
    11: "nghe_11_15",
    16: "nghe_16_20",

    36: "doc_36_40",
    41: "doc_41_45",

    51: "doc_51_55",
    56: "doc_56_60",
}


# =====================================================
# 3. CAC HAM DUNG CHUNG
# =====================================================

def load_json(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open(
        "r",
        encoding="utf-8-sig"
    ) as f:
        return json.load(f)


def normalize(text):

    return unicodedata.normalize(
        "NFKC",
        str(text)
    )


def normalize_code(text):

    text = normalize(text).upper()

    return re.sub(
        r"[^A-Z0-9]",
        "",
        text
    )


def sha256(path):

    h = hashlib.sha256()

    with path.open("rb") as f:

        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()


def clip_rect(page, x0, y0, x1, y1):

    x0 = max(0, x0)
    y0 = max(0, y0)

    x1 = min(page.rect.width, x1)
    y1 = min(page.rect.height, y1)

    rect = fitz.Rect(x0, y0, x1, y1)

    if rect.width <= 10 or rect.height <= 8:
        raise RuntimeError(
            f"Toa do cat anh khong hop le: {rect}"
        )

    return rect


def save_image(page, rect, destination):

    pix = page.get_pixmap(
        matrix=fitz.Matrix(3, 3),
        clip=rect,
        alpha=False
    )

    pix.save(str(destination))


# =====================================================
# 4. KIEM TRA PDF VA DAP AN
# =====================================================

def check_sources():

    if not PDF_FILE.is_file():
        raise FileNotFoundError(PDF_FILE)

    data = load_json(ANSWER_FILE)

    if data.get("so_de") != 7:
        raise RuntimeError(
            "JSON dap an khong phai De 7."
        )

    if data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "Ma de trong JSON dap an khong dung."
        )

    answers = data.get("dap_an", {})

    expected = {
        str(n) for n in range(1, 61)
    }

    if set(answers) != expected:
        raise RuntimeError(
            "JSON dap an khong du 60 cau."
        )

    # Kiem tra 10 anh dau da co.
    first_hashes = {}

    for number in range(1, 11):

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if not path.is_file():
            raise FileNotFoundError(
                f"Thieu anh cau {number}: {path}"
            )

        first_hashes[number] = sha256(path)

    return data, first_hashes


def check_pdf(doc):

    if len(doc) != 14:
        raise RuntimeError(
            f"PDF co {len(doc)} trang, "
            "du kien 14 trang."
        )

    cover = normalize_code(
        doc[0].get_text("text")
    )

    if EXAM_CODE not in cover:
        raise RuntimeError(
            "Trang bia khong phai H21329."
        )

    # Trang 8 phai duoc bo qua.
    page_8 = normalize(
        doc[7].get_text("text")
    )

    if re.search(
        r"第\s*(?:36|41|46|51|56)\s*[-–]",
        page_8
    ):
        raise RuntimeError(
            "Trang 8 co cau hoi, "
            "can kiem tra lai bo cuc."
        )

    # Trang 9 phai co cau 36-40.
    page_9 = normalize(
        doc[8].get_text("text")
    )

    if not re.search(
        r"第\s*36\s*[-–]\s*40\s*题",
        page_9
    ):
        raise RuntimeError(
            "Trang 9 khong co nhom cau 36-40."
        )

    # Trang 14 phai co cau 56-60.
    page_14 = normalize(
        doc[13].get_text("text")
    )

    if not re.search(
        r"第\s*56\s*[-–]\s*60\s*题",
        page_14
    ):
        raise RuntimeError(
            "Trang 14 khong co nhom cau 56-60."
        )

    print("PDF: 14 trang")
    print("Ma de: H21329")
    print("Trang 8: bo qua")
    print("Trang 9-14: phan Doc")


# =====================================================
# 5. XAC DINH VI TRI CAC CAU
# =====================================================

def find_question_positions(page, numbers):

    expected = set(numbers)

    positions = {}

    # Uu tien lay toa do tu cac word cua PDF.
    words = page.get_text("words")

    for word in words:

        x0, y0, x1, y1, content = word[:5]

        value = normalize(content).strip()

        match = re.match(
            r"^(\d{1,2})[.、]",
            value
        )

        if not match:
            continue

        number = int(match.group(1))

        if number not in expected:
            continue

        if x0 > page.rect.width * 0.35:
            continue

        if not (
            page.rect.height * 0.05
            <= y0
            <= page.rect.height * 0.94
        ):
            continue

        if number not in positions:
            positions[number] = float(y0)

    # Neu khong tim thay, tim them trong span.
    missing = expected - set(positions)

    if missing:

        data = page.get_text("dict")

        for block in data.get("blocks", []):

            if "lines" not in block:
                continue

            for line in block["lines"]:

                for span in line["spans"]:

                    value = normalize(
                        span.get("text", "")
                    ).strip()

                    match = re.match(
                        r"^(\d{1,2})[.、]",
                        value
                    )

                    if not match:
                        continue

                    number = int(match.group(1))

                    if number not in missing:
                        continue

                    bbox = span["bbox"]

                    x0 = float(bbox[0])
                    y0 = float(bbox[1])

                    if x0 > page.rect.width * 0.35:
                        continue

                    positions[number] = y0

    missing = expected - set(positions)

    if missing:
        raise RuntimeError(
            f"Khong tim thay vi tri cau "
            f"{sorted(missing)}"
        )

    # Kiem tra thu tu tu tren xuong duoi.
    ordered = [
        positions[n]
        for n in numbers
    ]

    if any(
        ordered[i] >= ordered[i + 1]
        for i in range(len(ordered) - 1)
    ):
        raise RuntimeError(
            "Thu tu toa do cau hoi khong dung."
        )

    return positions


# =====================================================
# 6. TINH VUNG CAT ANH TUNG CAU
# =====================================================

def question_rect(
    page,
    numbers,
    positions,
    index
):

    number = numbers[index]

    y = positions[number]

    # Cau 11-20 chi luu anh so cau,
    # khong hien thi anh nay trong HTML.
    if 11 <= number <= 20:

        return clip_rect(
            page,
            30,
            y - 8,
            page.rect.width - 25,
            y + 23
        )

    # Giu phan pinyin phia tren chu Han.
    top = y - 17

    if index + 1 < len(numbers):

        next_number = numbers[index + 1]

        bottom = (
            positions[next_number] - 17
        )

    else:

        # Cau cuoi trang:
        # lay den het noi dung nhung bo footer.
        word_bottoms = []

        for word in page.get_text("words"):

            wy0 = word[1]
            wy1 = word[3]

            if (
                wy0 >= top
                and wy1 < page.rect.height - 55
            ):
                word_bottoms.append(wy1)

        if word_bottoms:
            bottom = max(word_bottoms) + 12
        else:
            bottom = page.rect.height - 65

    return clip_rect(
        page,
        30,
        top,
        page.rect.width - 24,
        bottom
    )


# =====================================================
# 7. CAT BANG LUA CHON CHUNG
# =====================================================

def group_rect(page, first_question_y):

    top = page.rect.height * 0.085

    # Phan bang lua chon nam tren vi du.
    examples = page.search_for("例如")

    before_question = [
        rect.y0
        for rect in examples
        if rect.y0 < first_question_y
    ]

    if before_question:

        bottom = min(before_question) - 12

    else:

        bottom = first_question_y - 35

    if bottom <= top + 30:
        raise RuntimeError(
            "Khong xac dinh duoc "
            "vung bang lua chon."
        )

    return clip_rect(
        page,
        25,
        top,
        page.rect.width - 20,
        bottom
    )


# =====================================================
# 8. TAO HTML KIEM TRA 60 CAU
# =====================================================

def create_preview():

    parts = []

    for number in range(1, 61):

        # Hien thi bang lua chon o dau moi nhom.
        if number in GROUP_START:

            group = GROUP_START[number]

            parts.append(
                f"""
                <div class="group-card">
                    <h3>
                        Bảng lựa chọn:
                        {html.escape(group)}
                    </h3>

                    <img
                        src="groups/{group}.png"
                        alt="{group}"
                    >
                </div>
                """
            )

        # Cau 11-20 chi hien thi so cau.
        if 11 <= number <= 20:

            parts.append(
                f"""
                <div class="number-card">
                    Câu {number}
                </div>
                """
            )

            continue

        filename = f"cau_{number:02d}.png"

        parts.append(
            f"""
            <div class="question-card">
                <h3>Câu {number:02d}</h3>

                <img
                    src="questions/{filename}"
                    alt="Câu {number}"
                >
            </div>
            """
        )

    content = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>HSK2 - Đề 7 (H21329)</title>

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
        max-width: 1050px;
        margin: auto;
    }

    h1 {
        font-size: 26px;
        margin-bottom: 8px;
    }

    .note {
        color: #64748b;
        line-height: 1.6;
        margin-bottom: 24px;
    }

    .question-card,
    .group-card {
        margin-bottom: 18px;
        padding: 18px;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
    }

    h3 {
        margin: 0 0 14px;
        font-size: 18px;
    }

    img {
        display: block;
        width: 100%;
        height: auto;
        object-fit: contain;
    }

    .group-card {
        background: #eff6ff;
        border-color: #bfdbfe;
    }

    .number-card {
        display: inline-block;
        margin: 0 9px 16px 0;
        padding: 14px 22px;
        background: white;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        font-weight: bold;
    }

    .first-ten {
        display: grid;
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
        gap: 16px;
    }

    .first-ten .question-card {
        margin-bottom: 0;
    }

    @media (max-width: 750px) {
        .first-ten {
            grid-template-columns: 1fr;
        }
    }
</style>
</head>

<body>
<div class="container">

    <h1>HSK2 - Đề 7 (H21329)</h1>

    <p class="note">
        Kiểm tra 60 câu hỏi và
        6 bảng lựa chọn chung.
        Không hiển thị đáp án.
        Chưa thay đổi SQL Server.
    </p>

    __BODY__

</div>
</body>
</html>
"""

    # Giao dien 2 cot cho 10 cau dau.
    first_ten = []

    for number in range(1, 11):

        first_ten.append(
            f"""
            <div class="question-card">
                <h3>Câu {number:02d}</h3>
                <img
                    src="questions/cau_{number:02d}.png"
                    alt="Câu {number}"
                >
            </div>
            """
        )

    # parts da co cau 1-10, nen bo 10 phan dau.
    remaining = parts[10:]

    body = (
        '<div class="first-ten">'
        + "\n".join(first_ten)
        + "</div>\n"
        + "\n".join(remaining)
    )

    content = content.replace(
        "__BODY__",
        body
    )

    HTML_FILE.write_text(
        content,
        encoding="utf-8"
    )


# =====================================================
# 9. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK2 DE 7")
    print("TACH CAU 11-60")
    print("MA DE H21329")
    print("=" * 60)

    answer_data, first_hashes = check_sources()

    QUESTION_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    GROUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    question_manifest = {}

    group_manifest = {}

    with fitz.open(PDF_FILE) as doc:

        check_pdf(doc)

        # Ghi thong tin cua 10 anh da co.
        for page_no in (2, 3):

            for number in PAGE_QUESTIONS[page_no]:

                question_manifest[str(number)] = {
                    "trang_pdf": page_no,
                    "anh": (
                        f"questions/cau_{number:02d}.png"
                    ),
                    "toa_do": None
                }

        # ============================================
        # 10. TACH CAU 11-60
        # ============================================

        print("\n===== TACH CAU 11-60 =====")

        for page_no, numbers in PAGE_QUESTIONS.items():

            if page_no in (2, 3):
                continue

            page = doc[page_no - 1]

            positions = find_question_positions(
                page,
                numbers
            )

            for index, number in enumerate(numbers):

                rect = question_rect(
                    page,
                    numbers,
                    positions,
                    index
                )

                filename = (
                    f"cau_{number:02d}.png"
                )

                destination = (
                    QUESTION_DIR / filename
                )

                save_image(
                    page,
                    rect,
                    destination
                )

                question_manifest[str(number)] = {
                    "trang_pdf": page_no,
                    "anh": f"questions/{filename}",
                    "toa_do": [
                        round(rect.x0, 2),
                        round(rect.y0, 2),
                        round(rect.x1, 2),
                        round(rect.y1, 2),
                    ]
                }

                print(
                    f"Cau {number:02d}: "
                    f"trang PDF {page_no}"
                )

        # ============================================
        # 11. TACH 6 BANG LUA CHON
        # ============================================

        print("\n===== TACH BANG LUA CHON =====")

        for group, page_no in GROUP_PAGES.items():

            page = doc[page_no - 1]

            numbers = PAGE_QUESTIONS[page_no]

            positions = find_question_positions(
                page,
                numbers
            )

            first_number = numbers[0]

            rect = group_rect(
                page,
                positions[first_number]
            )

            filename = f"{group}.png"

            save_image(
                page,
                rect,
                GROUP_DIR / filename
            )

            group_manifest[group] = {
                "trang_pdf": page_no,
                "anh": f"groups/{filename}",
                "toa_do": [
                    round(rect.x0, 2),
                    round(rect.y0, 2),
                    round(rect.x1, 2),
                    round(rect.y1, 2),
                ]
            }

            print(
                f"{group}: trang PDF {page_no}"
            )

    # =================================================
    # 12. KIEM TRA 10 ANH DAU KHONG BI THAY DOI
    # =================================================

    for number, old_hash in first_hashes.items():

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if sha256(path) != old_hash:
            raise RuntimeError(
                f"Anh cau {number} da bi thay doi."
            )

    # =================================================
    # 13. KIEM TRA DU SO LUONG
    # =================================================

    expected = {
        str(n) for n in range(1, 61)
    }

    if set(question_manifest) != expected:
        raise RuntimeError(
            "Chua du thong tin 60 cau."
        )

    if set(group_manifest) != set(GROUP_PAGES):
        raise RuntimeError(
            "Chua du 6 bang lua chon."
        )

    for number in range(1, 61):

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if not path.is_file():
            raise FileNotFoundError(path)

        if path.stat().st_size == 0:
            raise RuntimeError(
                f"Anh cau {number} bi rong."
            )

    for group in GROUP_PAGES:

        path = GROUP_DIR / f"{group}.png"

        if not path.is_file():
            raise FileNotFoundError(path)

    # =================================================
    # 14. LUU JSON THONG TIN ANH
    # =================================================

    manifest = {
        "cap_hsk": 2,
        "so_de": 7,
        "ma_de_goc": EXAM_CODE,

        "so_trang_pdf": 14,

        "trang_bo_qua": [1, 8],

        "trang_cau_hoi": sorted(
            PAGE_QUESTIONS.keys()
        ),

        "cau_hoi": question_manifest,

        "bang_lua_chon": group_manifest,
    }

    MANIFEST_FILE.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # =================================================
    # 15. TAO HTML KIEM TRA
    # =================================================

    create_preview()

    print("\n" + "=" * 60)
    print("HOAN THANH HSK2 DE 7")
    print("=" * 60)

    print("Ma de: H21329")
    print("PDF de thi: 14 trang")
    print("Trang 8: da bo qua")
    print("Anh cau hoi: 60/60")
    print("Bang lua chon: 6/6")
    print("Dap an: 60/60")

    print(f"JSON: {MANIFEST_FILE}")
    print(f"HTML: {HTML_FILE}")

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
