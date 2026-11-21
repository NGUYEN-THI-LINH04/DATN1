
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 03 - H31003

BUOC 2:
- Giu nguyen 2 bang hinh Nghe cau 1-10.
- Tach 70 anh cau hoi 11-80.
- Tach 4 bang lua chon chung phan Doc.
- Giu day du A/B/C cua cau 61-70.
- Giu Pinyin o cau Viet 76-80.
- Tao manifest JSON.
- Tao HTML kiem tra 80 cau.

KHONG thay doi SQL Server.
KHONG sua HSK3 De 1.
KHONG sua HSK1/HSK2.
"""

from pathlib import Path
from html import escape
import hashlib
import json
import re

import fitz


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

HSK3 = (
    ROOT / "scripts" / "luyen_thi" / "hsk3"
)

SOURCE = (
    ROOT / "scripts" / "luyen_thi"
    / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 3"
)

DATA = HSK3 / "data" / "de_03"
OUTPUT = HSK3 / "output" / "de_03"

QUESTIONS = OUTPUT / "questions"
GROUPS = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_03_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_80_cau_ung_vien.json"
)

PREVIEW_HTML = (
    OUTPUT / "kiem_tra_80_cau.html"
)

EXAM_CODE = "H31003"


# =====================================================
# 2. SO DO TRANG PDF
# =====================================================

PAGE_QUESTIONS = {
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
# 3. GIOI HAN VUNG CAT TUNG TRANG
# =====================================================

PAGE_BOTTOM = {
    4: 741,
    5: 735,
    6: 742,

    7: 678,
    8: 532,
    9: 628,
    10: 741,

    11: 719,

    # Cau 70 nam cuoi trang.
    # Mo rong de lay du A/B/C.
    12: 745,

    13: 545,
    14: 559,
}


# =====================================================
# 4. HAI BANG HINH NGHE DA CO
# =====================================================

EXISTING_GROUPS = {
    "nghe_01_05": {
        "trang_pdf": 2,
        "lua_chon": "ABCDEF",
        "cau_tu": 1,
        "cau_den": 5,
    },

    "nghe_06_10": {
        "trang_pdf": 3,
        "lua_chon": "ABCDE",
        "cau_tu": 6,
        "cau_den": 10,
    },
}


# =====================================================
# 5. BON BANG LUA CHON PHAN DOC
# =====================================================

NEW_GROUPS = {
    "doc_41_45": {
        "trang_pdf": 7,
        "rect": (75, 190, 530, 395),
        "lua_chon": "ABCDEF",
        "cau_tu": 41,
        "cau_den": 45,
    },

    "doc_46_50": {
        "trang_pdf": 8,
        "rect": (75, 137, 530, 307),
        "lua_chon": "ABCDE",
        "cau_tu": 46,
        "cau_den": 50,
    },

    "doc_51_55": {
        "trang_pdf": 9,
        "rect": (80, 158, 532, 206),
        "lua_chon": "ABCDEF",
        "cau_tu": 51,
        "cau_den": 55,
    },

    "doc_56_60": {
        "trang_pdf": 10,
        "rect": (80, 124, 532, 170),
        "lua_chon": "ABCDEF",
        "cau_tu": 56,
        "cau_den": 60,
    },
}

ALL_GROUPS = {
    **EXISTING_GROUPS,
    **NEW_GROUPS,
}


# =====================================================
# 6. CAC HAM HO TRO
# =====================================================

def check_file(path):

    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay file:\n{path}"
        )

    if path.stat().st_size == 0:
        raise RuntimeError(
            f"File rong: {path}"
        )


def load_json(path):

    check_file(path)

    with path.open(
        "r",
        encoding="utf-8-sig"
    ) as f:
        return json.load(f)


def sha256(path):

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def write_safe(path, content):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if path.exists():

        if path.read_bytes() != content:
            raise RuntimeError(
                "File da ton tai nhung "
                "khac noi dung.\n"
                "Khong ghi de:\n"
                + str(path)
            )

        return

    path.write_bytes(content)


def json_bytes(data):

    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")


def group_for(number):

    for name, config in ALL_GROUPS.items():

        if (
            config["cau_tu"]
            <= number
            <= config["cau_den"]
        ):
            return name

    return None


def page_for(number):

    if 1 <= number <= 5:
        return 2

    if 6 <= number <= 10:
        return 3

    for page_no, numbers in (
        PAGE_QUESTIONS.items()
    ):

        if number in numbers:
            return page_no

    raise RuntimeError(
        f"Khong co trang cau {number}."
    )


# =====================================================
# 7. KIEM TRA JSON BUOC 1
# =====================================================

def read_sources():

    data = load_json(ANSWER_JSON)

    if data.get("cap_hsk") != 3:
        raise RuntimeError(
            "JSON khong phai HSK3."
        )

    if data.get("so_de") != 3:
        raise RuntimeError(
            "JSON khong phai De 3."
        )

    if data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "JSON khong phai H31003."
        )

    if (
        data.get("tong_cau") != 80
        or data.get("so_cau_nghe") != 40
        or data.get("so_cau_doc") != 30
        or data.get("so_cau_viet") != 10
    ):
        raise RuntimeError(
            "Thong tin so cau khong dung."
        )

    answers = data.get("dap_an", {})

    expected_numbers = {
        str(n) for n in range(1, 81)
    }

    if set(answers) != expected_numbers:
        raise RuntimeError(
            "JSON buoc 1 khong du 80 dap an."
        )

    for number in range(1, 81):

        answer = str(
            answers[str(number)]
        ).strip()

        if not answer:
            raise RuntimeError(
                f"Thieu dap an cau {number}."
            )

    pdf_value = data.get("file_pdf")

    if not pdf_value:
        raise RuntimeError(
            "JSON thieu duong dan PDF."
        )

    pdf_path = Path(pdf_value)

    check_file(pdf_path)

    if pdf_path.parent.resolve() != SOURCE.resolve():
        raise RuntimeError(
            "PDF khong nam trong "
            "thu muc HSK3 DE 3."
        )

    # Hai bang hinh Nghe da duoc duyet.
    # Ghi hash de chac chan khong bi sua.
    old_hashes = {}

    for name in EXISTING_GROUPS:

        path = GROUPS / f"{name}.png"

        check_file(path)

        old_hashes[name] = sha256(path)

    return pdf_path, answers, old_hashes


# =====================================================
# 8. KIEM TRA PDF H31003
# =====================================================

def check_pdf(doc):

    if len(doc) != 22:
        raise RuntimeError(
            f"PDF co {len(doc)} trang, "
            "H31003 phai co 22 trang."
        )

    cover = re.sub(
        r"\s+",
        "",
        doc[0].get_text("text")
    )

    if EXAM_CODE not in cover:
        raise RuntimeError(
            "Trang bia khong phai H31003."
        )

    for page_no in (21, 22):

        text = doc[
            page_no - 1
        ].get_text("text")

        if EXAM_CODE not in text:
            raise RuntimeError(
                f"Trang {page_no} sai ma de."
            )

    transcript = doc[14].get_text("text")

    if "听力材料" not in transcript:
        raise RuntimeError(
            "Trang 15 khong phai loi thoai."
        )

    if "答案" not in doc[20].get_text("text"):
        raise RuntimeError(
            "Trang 21 khong phai dap an."
        )

    if "书" not in doc[21].get_text("text"):
        raise RuntimeError(
            "Trang 22 khong phai dap an Viet."
        )

    total = sum(
        len(numbers)
        for numbers in PAGE_QUESTIONS.values()
    )

    if total != 70:
        raise RuntimeError(
            "So do trang khong du 70 cau."
        )

    print("PDF: 22 trang - H31003")


# =====================================================
# 9. TIM VI TRI SO CAU TRONG PDF
# =====================================================

def question_positions(
    page,
    numbers,
    page_no
):

    found = {}

    blocks = page.get_text(
        "dict"
    )["blocks"]

    for block in blocks:

        for line in block.get("lines", []):

            text = "".join(
                span.get("text", "")
                for span in line.get("spans", [])
            ).strip()

            match = re.match(
                r"^(\d{1,2})\s*[.．、]",
                text
            )

            if not match:
                continue

            number = int(match.group(1))

            x0, y0, _, _ = line["bbox"]

            if (
                number in numbers
                and x0 < 125
                and y0 < 760
            ):
                found.setdefault(
                    number, []
                ).append(float(y0))

    # Phai tim du va duy nhat tung cau.
    if (
        set(found) != set(numbers)
        or any(
            len(values) != 1
            for values in found.values()
        )
    ):

        missing = sorted(
            set(numbers) - set(found)
        )

        raise RuntimeError(
            f"Trang {page_no} khong nhan dien "
            f"du cac so cau.\n"
            f"Thieu: {missing}\n"
            f"Tim thay: {found}"
        )

    positions = {
        number: found[number][0]
        for number in numbers
    }

    for first, second in zip(
        numbers,
        numbers[1:]
    ):

        if positions[first] >= positions[second]:
            raise RuntimeError(
                f"Thu tu cau trang "
                f"{page_no} khong dung."
            )

    return positions


# =====================================================
# 10. TINH TOA DO CAT TUNG CAU
# =====================================================

def question_rect(
    page,
    page_no,
    numbers,
    positions,
    index
):

    number = numbers[index]

    # Cau 76-80 co Pinyin phia tren
    # cau hoi nen phai cat cao hon.
    is_writing_2 = (
        76 <= number <= 80
    )

    top_padding = (
        26 if is_writing_2 else 11
    )

    next_padding = (
        27 if is_writing_2 else 10
    )

    top = (
        positions[number] - top_padding
    )

    if index + 1 < len(numbers):

        next_number = numbers[index + 1]

        bottom = (
            positions[next_number] - next_padding
        )

    else:

        bottom = PAGE_BOTTOM[page_no]

    rect = fitz.Rect(
        75,
        top,
        530,
        bottom
    ) & page.rect

    if (
        rect.is_empty
        or rect.height < 20
        or rect.width < 200
    ):
        raise RuntimeError(
            f"Cau {number} co toa do "
            f"khong hop le: {rect}"
        )

    return rect


# =====================================================
# 11. XAC MINH CAC PHUONG AN A/B/C
# =====================================================

def check_abc(page, rect, number):

    if not (
        21 <= number <= 40
        or 61 <= number <= 70
    ):
        return

    found = set()

    for word in page.get_text("words"):

        x0, y0, _, _, value = word[:5]

        value = value.strip()

        if (
            value in ("A", "B", "C")
            and rect.contains(
                fitz.Point(x0, y0)
            )
        ):
            found.add(value)

    if found != set("ABC"):

        raise RuntimeError(
            f"Anh cau {number} thieu "
            "phuong an A/B/C.\n"
            f"Tim thay: {sorted(found)}"
        )


# =====================================================
# 12. RENDER ANH PNG
# =====================================================

def render_png(page, rect):

    pix = page.get_pixmap(
        matrix=fitz.Matrix(2.5, 2.5),
        clip=rect,
        alpha=False
    )

    return pix.tobytes("png")


# =====================================================
# 13. KIEM TRA BANG LUA CHON CHUNG
# =====================================================

def check_group_labels(
    page,
    rect,
    labels
):

    found = set()

    for word in page.get_text("words"):

        x0, y0, _, _, value = word[:5]

        value = value.strip()

        if (
            value in labels
            and rect.contains(
                fitz.Point(x0, y0)
            )
        ):
            found.add(value)

    if found != set(labels):

        raise RuntimeError(
            "Bang lua chon thieu nhan.\n"
            f"Can: {labels}\n"
            f"Tim thay: {sorted(found)}"
        )


# =====================================================
# 14. TAO HTML XEM TRUOC 80 CAU
# =====================================================

def create_preview():

    blocks = []

    for number in range(1, 81):

        if number == 1:
            blocks.append(
                '<h2 class="part">'
                'I. Nghe - Câu 1–40</h2>'
            )

        elif number == 41:
            blocks.append(
                '<h2 class="part">'
                'II. Đọc - Câu 41–70</h2>'
            )

        elif number == 71:
            blocks.append(
                '<h2 class="part">'
                'III. Viết - Câu 71–80</h2>'
            )

        group = group_for(number)

        if group:

            config = ALL_GROUPS[group]

            if number == config["cau_tu"]:

                blocks.append(
                    '<section class="group">'
                    f'<h3>Bảng lựa chọn '
                    f'câu {config["cau_tu"]}–'
                    f'{config["cau_den"]}</h3>'
                    f'<img src="groups/'
                    f'{escape(group)}.png" '
                    f'alt="Bảng lựa chọn">'
                    '</section>'
                )

        # Cau 1-10 chi co bang hinh chung.
        if number <= 10:

            blocks.append(
                f'<span class="mini">'
                f'Câu {number}</span>'
            )

        else:

            blocks.append(
                '<section class="question">'
                f'<h3>Câu {number:02d}</h3>'
                f'<img src="questions/'
                f'cau_{number:02d}.png" '
                f'alt="Câu {number}">'
                '</section>'
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

<title>HSK3 Đề 3 - H31003</title>

<style>
* {
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    color: #18263d;
    background: #f4f6fa;
    margin: 0;
    padding: 22px;
}

.container {
    max-width: 1000px;
    margin: auto;
}

h1 {
    font-size: 25px;
}

.hint {
    color: #64748b;
    line-height: 1.6;
}

.part {
    padding: 15px 0;
    border-bottom: 2px solid #cbd5e1;
}

.group,
.question {
    background: white;
    padding: 18px;
    border: 1px solid #dbe2eb;
    border-radius: 12px;
    margin: 15px 0;
}

.group {
    background: #eff6ff;
}

h3 {
    font-size: 17px;
    margin: 0 0 12px;
}

.group img,
.question img {
    display: block;
    max-width: 100%;
    height: auto;
    object-fit: contain;
}

.mini {
    display: inline-block;
    padding: 12px 18px;
    background: white;
    border: 1px solid #cbd5e1;
    border-radius: 9px;
    margin: 7px;
}
</style>

</head>

<body>
<main class="container">

<h1>HSK3 – Đề 3 (H31003)</h1>

<p class="hint">
Kiểm tra toàn bộ 80 câu.
Không hiển thị đáp án.
Chưa thay đổi SQL Server.
</p>

__BLOCKS__

</main>
</body>
</html>
"""

    return html.replace(
        "__BLOCKS__",
        "\n".join(blocks)
    ).encode("utf-8")


# =====================================================
# 15. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 03")
    print("BUOC 2 - TACH CAU 11-80")
    print("=" * 60)

    (
        pdf_path,
        answers,
        original_hashes
    ) = read_sources()

    images = {}

    question_manifest = {}
    group_manifest = {}

    # Giu lai hai bang hinh Nghe.
    for name, config in EXISTING_GROUPS.items():

        group_manifest[name] = {
            "trang_pdf": config["trang_pdf"],
            "anh": f"groups/{name}.png",
            "lua_chon": config["lua_chon"],
            "cau_tu": config["cau_tu"],
            "cau_den": config["cau_den"],
        }

    with fitz.open(pdf_path) as doc:

        check_pdf(doc)

        # ============================================
        # 16. GHI NHAN CAU 1-10
        # ============================================

        for number in range(1, 11):

            question_manifest[str(number)] = {
                "trang_pdf": page_for(number),
                "anh": None,
                "nhom_lua_chon": group_for(number),
            }

        # ============================================
        # 17. TACH 70 CAU 11-80
        # ============================================

        print(
            "\n===== TACH 70 ANH CAU HOI ====="
        )

        for page_no, numbers in (
            PAGE_QUESTIONS.items()
        ):

            page = doc[page_no - 1]

            positions = question_positions(
                page,
                numbers,
                page_no
            )

            for index, number in enumerate(
                numbers
            ):

                rect = question_rect(
                    page,
                    page_no,
                    numbers,
                    positions,
                    index
                )

                # Bao dam khong mat A/B/C
                # o cau Nghe 21-40 va Doc 61-70.
                check_abc(
                    page,
                    rect,
                    number
                )

                filename = (
                    f"cau_{number:02d}.png"
                )

                destination = (
                    QUESTIONS / filename
                )

                images[destination] = (
                    render_png(page, rect)
                )

                question_manifest[str(number)] = {
                    "trang_pdf": page_no,
                    "anh": (
                        f"questions/{filename}"
                    ),
                    "nhom_lua_chon": (
                        group_for(number)
                    ),
                    "toa_do": [
                        round(value, 2)
                        for value in (
                            rect.x0,
                            rect.y0,
                            rect.x1,
                            rect.y1
                        )
                    ],
                }

                print(
                    f"Cau {number:02d}: "
                    f"trang PDF {page_no}"
                )

        # ============================================
        # 18. TACH BON BANG LUA CHON DOC
        # ============================================

        print(
            "\n===== BANG LUA CHON PHAN DOC ====="
        )

        for name, config in NEW_GROUPS.items():

            page_no = config["trang_pdf"]

            page = doc[page_no - 1]

            rect = fitz.Rect(
                config["rect"]
            )

            if not page.rect.contains(rect):
                raise RuntimeError(
                    f"Toa do bang {name} sai."
                )

            check_group_labels(
                page,
                rect,
                config["lua_chon"]
            )

            destination = (
                GROUPS / f"{name}.png"
            )

            images[destination] = (
                render_png(page, rect)
            )

            group_manifest[name] = {
                "trang_pdf": page_no,
                "anh": f"groups/{name}.png",
                "lua_chon": config["lua_chon"],
                "cau_tu": config["cau_tu"],
                "cau_den": config["cau_den"],
                "toa_do": list(config["rect"]),
            }

            print(
                f"{name}: trang {page_no}, "
                f"{len(config['lua_chon'])} lua chon"
            )

    # =================================================
    # 19. KIEM TRA KET QUA TRUOC KHI GHI
    # =================================================

    if len(question_manifest) != 80:
        raise RuntimeError(
            "Manifest khong du 80 cau."
        )

    if len(group_manifest) != 6:
        raise RuntimeError(
            "Manifest khong du 6 bang."
        )

    # 70 anh cau hoi + 4 bang Doc.
    if len(images) != 74:
        raise RuntimeError(
            f"So anh moi sai: {len(images)}/74"
        )

    if set(question_manifest) != {
        str(number)
        for number in range(1, 81)
    }:
        raise RuntimeError(
            "So cau trong manifest "
            "khong lien tuc 1-80."
        )

    # =================================================
    # 20. TAO MANIFEST JSON
    # =================================================

    manifest = {
        "cap_hsk": 3,
        "so_de": 3,
        "ma_de_goc": EXAM_CODE,

        "so_trang_pdf": 22,
        "so_cau": 80,

        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        "trang_loi_thoai": list(
            range(15, 21)
        ),

        "trang_dap_an": [21, 22],

        "cau_hoi": question_manifest,
        "bang_lua_chon": group_manifest,
    }

    # =================================================
    # 21. TAO HTML VA JSON
    # =================================================

    outputs = dict(images)

    outputs[MANIFEST_JSON] = (
        json_bytes(manifest)
    )

    outputs[PREVIEW_HTML] = (
        create_preview()
    )

    # =================================================
    # 22. KIEM TRA KHONG GHI DE FILE CU
    # =================================================

    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):
            raise RuntimeError(
                "File da ton tai voi "
                "noi dung khac.\n"
                "Khong ghi de:\n"
                + str(path)
            )

    # Kiem tra lai hai bang hinh Nghe.
    for name, old_hash in (
        original_hashes.items()
    ):

        path = GROUPS / f"{name}.png"

        if sha256(path) != old_hash:
            raise RuntimeError(
                f"Bang hinh Nghe {name} "
                "da bi thay doi."
            )

    # =================================================
    # 23. LUU ANH, JSON VA HTML
    # =================================================

    for path, content in outputs.items():

        write_safe(
            path,
            content
        )

    # =================================================
    # 24. KIEM TRA SAU KHI LUU
    # =================================================

    for number in range(11, 81):

        check_file(
            QUESTIONS
            / f"cau_{number:02d}.png"
        )

    for name in ALL_GROUPS:

        check_file(
            GROUPS / f"{name}.png"
        )

    for name, old_hash in (
        original_hashes.items()
    ):

        path = GROUPS / f"{name}.png"

        if sha256(path) != old_hash:
            raise RuntimeError(
                f"Bang hinh {name} "
                "khong con nguyen ven."
            )

    # =================================================
    # 25. HOAN THANH
    # =================================================

    print("\n" + "=" * 60)
    print("HOAN THANH HSK3 DE 03 - BUOC 2")
    print("=" * 60)

    print("Ma de: H31003")

    print("Dap an buoc 1: 80/80")
    print("Anh cau 11-80: 70/70")

    print(
        "Bang lua chon: 6/6 "
        "(2 Nghe + 4 Doc)"
    )

    print(
        "Bang Nghe 1-10: "
        "KHONG THAY DOI"
    )

    print(
        "Cau 61-70: da kiem tra A/B/C"
    )

    print(
        "Cau 76-80: da giu Pinyin"
    )

    print(f"\nJSON: {MANIFEST_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
