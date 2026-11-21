
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 11 (H21335)

BUOC 2:
- Giu nguyen 10 anh cau hoi dau.
- Tach tiep cau 11-60.
- Tao 6 bang lua chon chung.
- Bo qua trang 8.
- Khong cat trang loi thoai 15-18.
- Doc dap an trang 19.
- Tao manifest JSON va HTML kiem tra 60 cau.

Tai su dung cac ham cat anh cua De 7.
Khong sua file De 7.
Khong thay doi SQL Server.
"""

from pathlib import Path
import hashlib
import importlib.util
import json
import re
import unicodedata

import fitz


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

HSK2 = ROOT / "scripts" / "luyen_thi" / "hsk2"

HELPER_SCRIPT = (
    HSK2 / "extract_remaining_de_07.py"
)

DATA = HSK2 / "data" / "de_11"
OUTPUT = HSK2 / "output" / "de_11"

ANSWER_JSON = DATA / "de_11_dap_an.json"

QUESTION_DIR = OUTPUT / "questions"
GROUP_DIR = OUTPUT / "groups"

MANIFEST_JSON = (
    DATA / "hinh_60_cau_ung_vien.json"
)

HTML_FILE = OUTPUT / "kiem_tra_60_cau.html"

EXAM_CODE = "H21335"
EXAM_NUMBER = 11


# =====================================================
# 2. SO DO TRANG PDF
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
# 3. HAM HO TRO
# =====================================================

def load_json(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


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


def file_hash(path):

    digest = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def check_file(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    if path.stat().st_size == 0:
        raise RuntimeError(
            f"File rong: {path}"
        )


def has_heading(page, first, last):

    text = normalize(
        page.get_text("text")
    )

    pattern = (
        rf"第\s*{first}\s*[-–—]\s*"
        rf"{last}\s*题"
    )

    return bool(re.search(pattern, text))


# =====================================================
# 4. NAP HAM CAT ANH TU DE 7
# =====================================================

def load_helpers():

    check_file(HELPER_SCRIPT)

    spec = importlib.util.spec_from_file_location(
        "hsk2_extract_de07_helpers",
        HELPER_SCRIPT
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "Khong nap duoc script De 7."
        )

    module = importlib.util.module_from_spec(spec)

    # Chi nap ham, khong chay main() cua De 7.
    spec.loader.exec_module(module)

    required = [
        "find_question_positions",
        "question_rect",
        "group_rect",
    ]

    for name in required:

        if not callable(
            getattr(module, name, None)
        ):
            raise RuntimeError(
                f"Script De 7 thieu ham: {name}"
            )

    return module


# =====================================================
# 5. DOC DAP AN TRANG 19
# =====================================================

def extract_pdf_answers(page):

    text = normalize(
        page.get_text("text")
    )

    if "答案" not in text:
        raise RuntimeError(
            "Trang 19 khong co bang dap an."
        )

    pattern = re.compile(
        r"(?<!\d)(\d{1,2})\s*[.、]\s*([A-F√×])"
    )

    answers = {}

    for match in pattern.finditer(text):

        number = int(match.group(1))
        answer = match.group(2)

        if not 1 <= number <= 60:
            continue

        if number in answers:
            raise RuntimeError(
                f"Trung dap an cau {number}."
            )

        answers[number] = answer

    if set(answers) != set(range(1, 61)):
        raise RuntimeError(
            "Trang 19 khong du 60 dap an."
        )

    return answers


# =====================================================
# 6. KIEM TRA PDF 19 TRANG
# =====================================================

def check_pdf(doc):

    if len(doc) != 19:
        raise RuntimeError(
            f"PDF co {len(doc)} trang. "
            "De 11 phai co 19 trang."
        )

    cover = normalize_code(
        doc[0].get_text("text")
    )

    answer_page = normalize_code(
        doc[18].get_text("text")
    )

    if EXAM_CODE not in cover:
        raise RuntimeError(
            "Trang bia khong phai H21335."
        )

    if EXAM_CODE not in answer_page:
        raise RuntimeError(
            "Trang dap an khong phai H21335."
        )

    checks = [
        (2, 1, 10),
        (4, 11, 15),
        (5, 16, 20),
        (6, 21, 30),
        (7, 31, 35),
        (9, 36, 40),
        (10, 41, 45),
        (11, 46, 50),
        (13, 51, 55),
        (14, 56, 60),
    ]

    for page_no, first, last in checks:

        if not has_heading(
            doc[page_no - 1],
            first,
            last
        ):
            raise RuntimeError(
                f"Trang {page_no} khong co "
                f"nhom cau {first}-{last}."
            )

    # Trang 8 khong duoc co noi dung Doc.
    for first, last in [
        (36, 40),
        (41, 45),
        (46, 50),
        (51, 55),
        (56, 60),
    ]:

        if has_heading(doc[7], first, last):
            raise RuntimeError(
                "Trang 8 co cau hoi."
            )

    # Trang 15 bat dau phan loi thoai.
    transcript = normalize(
        doc[14].get_text("text")
    )

    if "听力材料" not in transcript:
        raise RuntimeError(
            "Trang 15 khong phai loi thoai Nghe."
        )

    # Trang 19 la dap an.
    answer_text = normalize(
        doc[18].get_text("text")
    )

    if "答案" not in answer_text:
        raise RuntimeError(
            "Trang 19 khong phai bang dap an."
        )

    print("PDF: 19 trang")
    print("Trang 2-7: cau 1-35")
    print("Trang 8: bo qua")
    print("Trang 9-14: cau 36-60")
    print("Trang 15-18: loi thoai Nghe")
    print("Trang 19: dap an")


# =====================================================
# 7. KIEM TRA JSON VA 10 ANH DAU
# =====================================================

def check_sources():

    data = load_json(ANSWER_JSON)

    if data.get("so_de") != EXAM_NUMBER:
        raise RuntimeError(
            "JSON khong phai De 11."
        )

    if data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "JSON khong phai H21335."
        )

    answers = data.get("dap_an", {})

    if set(answers) != {
        str(n) for n in range(1, 61)
    }:
        raise RuntimeError(
            "JSON khong du 60 dap an."
        )

    pdf_value = data.get("file_pdf")

    if not pdf_value:
        raise RuntimeError(
            "JSON thieu duong dan PDF."
        )

    pdf_file = Path(pdf_value)

    check_file(pdf_file)

    first_hashes = {}

    for number in range(1, 11):

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        check_file(path)

        first_hashes[number] = file_hash(path)

    return pdf_file, answers, first_hashes


# =====================================================
# 8. TAO ANH KHONG GHI DE ANH KHAC NHAU
# =====================================================

def render_image(page, rect):

    rect = fitz.Rect(rect) & page.rect

    if (
        rect.is_empty
        or rect.width <= 10
        or rect.height <= 8
    ):
        raise RuntimeError(
            f"Vung cat anh khong hop le: {rect}"
        )

    pix = page.get_pixmap(
        matrix=fitz.Matrix(3, 3),
        clip=rect,
        alpha=False
    )

    return pix.tobytes("png")


def check_existing_image(destination, content):

    if destination.exists():

        if destination.read_bytes() != content:
            raise RuntimeError(
                "Anh dich da ton tai nhung "
                "khac noi dung.\n"
                "Khong tu ghi de:\n"
                + str(destination)
            )


# =====================================================
# 9. TAO HTML KIEM TRA 60 CAU
# =====================================================

def create_preview():

    cards = []

    for number in range(1, 61):

        if number in GROUP_START:

            group = GROUP_START[number]

            cards.append(
                f"""
                <section class="group">
                    <h2>Bảng lựa chọn - Câu {number}</h2>
                    <img
                        src="groups/{group}.png"
                        alt="{group}"
                    >
                </section>
                """
            )

        # Cau 11-20 chi can so cau
        # va bang hinh lua chon chung.
        if 11 <= number <= 20:

            cards.append(
                f"""
                <div class="number-only">
                    Câu {number}
                </div>
                """
            )

            continue

        cards.append(
            f"""
            <section class="question">
                <h3>Câu {number:02d}</h3>
                <img
                    src="questions/cau_{number:02d}.png"
                    alt="Câu {number}"
                >
            </section>
            """
        )

    content = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>HSK2 - Đề 11 (H21335)</title>

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
    margin-bottom: 10px;
}

.note {
    color: #64748b;
    line-height: 1.6;
    margin-bottom: 24px;
}

.question,
.group {
    background: white;
    padding: 18px;
    margin-bottom: 18px;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

.group {
    background: #eff6ff;
    border-color: #bfdbfe;
}

h2, h3 {
    margin: 0 0 14px;
    font-size: 18px;
}

img {
    display: block;
    width: 100%;
    height: auto;
    object-fit: contain;
}

.number-only {
    display: inline-block;
    padding: 14px 22px;
    margin: 0 9px 16px 0;
    background: white;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    font-weight: bold;
}
</style>
</head>

<body>
<div class="container">

    <h1>HSK2 – Đề 11 (H21335)</h1>

    <p class="note">
        Kiểm tra 60 câu hỏi và
        6 bảng lựa chọn chung.
        Không hiển thị đáp án.
        Chưa thay đổi SQL Server.
    </p>

    __CARDS__

</div>
</body>
</html>
"""

    return content.replace(
        "__CARDS__",
        "\n".join(cards)
    )


# =====================================================
# 9.1. SUA NHAN DIEN CAU 48 - H21335
# =====================================================

def find_positions_de11(page, numbers, helpers):

    # Cac trang khac giu nguyen thuat toan cu.
    if numbers != [46, 47, 48]:
        return helpers.find_question_positions(
            page,
            numbers
        )

    # Trang 11: tim cau 46 va 47 truoc.
    positions = helpers.find_question_positions(
        page,
        [46, 47]
    )

    # PDF H21335 ghi "48 ." co khoang trang.
    # Tim so 48 khong bat buoc kem dau cham.
    candidates = []

    for word in page.get_text("words"):

        x0, y0, x1, y1, content = word[:5]

        value = unicodedata.normalize(
            "NFKC",
            str(content)
        ).strip()

        if not re.fullmatch(
            r"48[.、]?",
            value
        ):
            continue

        # So cau phai o cot ben trai.
        if x0 > page.rect.width * 0.35:
            continue

        # Cau 48 phai nam ben duoi cau 47.
        if y0 <= positions[47]:
            continue

        # Bo qua footer.
        if y0 >= page.rect.height - 55:
            continue

        candidates.append(float(y0))

    if len(candidates) != 1:
        raise RuntimeError(
            "Khong xac dinh duoc duy nhat "
            f"vi tri cau 48: {candidates}"
        )

    positions[48] = candidates[0]

    if not (
        positions[46]
        < positions[47]
        < positions[48]
    ):
        raise RuntimeError(
            "Thu tu cau 46-48 khong dung."
        )

    print(
        "Da nhan dien cau 48: "
        f"y={positions[48]:.2f}"
    )

    return positions


# =====================================================
# 10. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK2 DE 11")
    print("TACH CAU 11-60 - H21335")
    print("=" * 60)

    (
        pdf_file,
        answers,
        first_hashes
    ) = check_sources()

    helpers = load_helpers()

    question_manifest = {}
    group_manifest = {}

    # Chua anh trong bo nho truoc khi luu.
    pending_images = {}

    with fitz.open(pdf_file) as doc:

        check_pdf(doc)

        # ============================================
        # 11. DOI CHIEU 60 DAP AN
        # ============================================

        pdf_answers = extract_pdf_answers(
            doc[18]
        )

        for number in range(1, 61):

            actual = str(
                answers[str(number)]
            ).strip()

            if actual != pdf_answers[number]:
                raise RuntimeError(
                    f"Cau {number} sai dap an: "
                    f"JSON={actual}, "
                    f"PDF={pdf_answers[number]}"
                )

        print("\nDap an: 60/60 KHOP")

        # ============================================
        # 12. GHI NHAN 10 ANH DAU
        # ============================================

        for page_no in (2, 3):

            for number in PAGE_QUESTIONS[page_no]:

                question_manifest[str(number)] = {
                    "trang_pdf": page_no,
                    "anh": (
                        f"questions/cau_{number:02d}.png"
                    ),
                    "toa_do": None,
                }

        # ============================================
        # 13. TACH CAU 11-60
        # ============================================

        print("\n===== TACH CAU 11-60 =====")

        for page_no, numbers in PAGE_QUESTIONS.items():

            if page_no in (2, 3):
                continue

            page = doc[page_no - 1]

            positions = find_positions_de11(
                 page,
                 numbers,
                 helpers
            )

            for index, number in enumerate(numbers):

                rect = helpers.question_rect(
                    page,
                    numbers,
                    positions,
                    index
                )

                destination = (
                    QUESTION_DIR
                    / f"cau_{number:02d}.png"
                )

                content = render_image(
                    page,
                    rect
                )

                check_existing_image(
                    destination,
                    content
                )

                pending_images[destination] = content

                question_manifest[str(number)] = {
                    "trang_pdf": page_no,
                    "anh": (
                        f"questions/cau_{number:02d}.png"
                    ),
                    "toa_do": [
                        round(rect.x0, 2),
                        round(rect.y0, 2),
                        round(rect.x1, 2),
                        round(rect.y1, 2),
                    ],
                }

                print(
                    f"Cau {number:02d}: "
                    f"trang PDF {page_no}"
                )

        # ============================================
        # 14. TACH 6 BANG LUA CHON
        # ============================================

        print("\n===== TACH 6 BANG LUA CHON =====")

        for group, page_no in GROUP_PAGES.items():

            page = doc[page_no - 1]

            numbers = PAGE_QUESTIONS[page_no]

            positions = (
                helpers.find_question_positions(
                    page,
                    numbers
                )
            )

            rect = helpers.group_rect(
                page,
                positions[numbers[0]]
            )

            destination = (
                GROUP_DIR / f"{group}.png"
            )

            content = render_image(
                page,
                rect
            )

            check_existing_image(
                destination,
                content
            )

            pending_images[destination] = content

            group_manifest[group] = {
                "trang_pdf": page_no,
                "anh": f"groups/{group}.png",
                "toa_do": [
                    round(rect.x0, 2),
                    round(rect.y0, 2),
                    round(rect.x1, 2),
                    round(rect.y1, 2),
                ],
            }

            print(
                f"{group}: trang PDF {page_no}"
            )

    # ================================================
    # 15. KIEM TRA TRUOC KHI LUU
    # ================================================

    expected = {
        str(n) for n in range(1, 61)
    }

    if set(question_manifest) != expected:
        raise RuntimeError(
            "Manifest khong du 60 cau."
        )

    if set(group_manifest) != set(GROUP_PAGES):
        raise RuntimeError(
            "Manifest khong du 6 bang."
        )

    for number, old_hash in first_hashes.items():

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if file_hash(path) != old_hash:
            raise RuntimeError(
                f"Anh cau {number} da bi thay doi."
            )

    manifest = {
        "cap_hsk": 2,
        "so_de": EXAM_NUMBER,
        "ma_de_goc": EXAM_CODE,

        "so_trang_pdf": 19,

        "trang_bo_qua": [
            1, 8, 15, 16, 17, 18, 19
        ],

        "trang_cau_hoi": sorted(
            PAGE_QUESTIONS.keys()
        ),

        "trang_dap_an": 19,

        "cau_hoi": question_manifest,
        "bang_lua_chon": group_manifest,
    }

    manifest_content = json.dumps(
        manifest,
        ensure_ascii=False,
        indent=2
    )

    html_content = create_preview()

    # Bao ve manifest da ton tai.
    if MANIFEST_JSON.exists():

        existing = load_json(MANIFEST_JSON)

        if existing != manifest:
            raise RuntimeError(
                "Manifest De 11 da ton tai "
                "voi noi dung khac.\n"
                "Khong tu ghi de."
            )

    # Bao ve HTML da ton tai.
    if HTML_FILE.exists():

        existing_html = HTML_FILE.read_text(
            encoding="utf-8-sig"
        )

        if existing_html != html_content:
            raise RuntimeError(
                "HTML De 11 da ton tai "
                "voi noi dung khac.\n"
                "Khong tu ghi de."
            )

    # ================================================
    # 16. LUU ANH
    # ================================================

    QUESTION_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    GROUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for destination, content in pending_images.items():

        if not destination.exists():
            destination.write_bytes(content)

    # ================================================
    # 17. LUU JSON VA HTML
    # ================================================

    DATA.mkdir(
        parents=True,
        exist_ok=True
    )

    if not MANIFEST_JSON.exists():
        MANIFEST_JSON.write_text(
            manifest_content,
            encoding="utf-8"
        )

    if not HTML_FILE.exists():
        HTML_FILE.write_text(
            html_content,
            encoding="utf-8"
        )

    # ================================================
    # 18. KIEM TRA KET QUA
    # ================================================

    for number in range(1, 61):

        check_file(
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

    for group in GROUP_PAGES:

        check_file(
            GROUP_DIR / f"{group}.png"
        )

    for number, old_hash in first_hashes.items():

        path = (
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

        if file_hash(path) != old_hash:
            raise RuntimeError(
                f"Anh cau {number} da bi thay doi."
            )

    print("\n" + "=" * 60)
    print("HOAN THANH HSK2 DE 11 - BUOC 2")
    print("=" * 60)

    print("Ma de: H21335")
    print("So de: 11")
    print("Anh cau hoi: 60/60")
    print("Bang lua chon: 6/6")
    print("Dap an: 60/60")
    print("Anh cau 1-10: KHONG THAY DOI")
    print("Trang 8: DA BO QUA")
    print("Trang 15-19: KHONG CAT ANH")

    print(f"\nJSON: {MANIFEST_JSON}")
    print(f"HTML: {HTML_FILE}")

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
