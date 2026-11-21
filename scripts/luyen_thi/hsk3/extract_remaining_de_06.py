
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 06 (H31006)

BUOC 2:
- Giu nguyen 2 bang hinh Nghe cau 1-10.
- Tach 70 anh cau hoi 11-80.
- Tach 4 bang lua chon chung phan Doc.
- Kiem tra A/B/C cua cac cau trac nghiem.
- Giu Pinyin cua cau 76-80.
- Bao toan 2 dap an hop le cua cau 75.
- Tao manifest JSON va HTML kiem tra 80 cau.

PDF H31006 co 16 trang:
- Trang 2-14: Cau hoi
- Trang 15: Dap an Nghe/Doc
- Trang 16: Dap an Viet
- Khong co trang loi thoai Nghe.

KHONG ket noi SQL Server.
KHONG thay doi cac de da hoan thanh.
"""

from pathlib import Path
from html import escape
import hashlib
import json
import re
import unicodedata

import fitz


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "luyen_thi"

SOURCE = (
    BASE / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 6"
)

DATA = (
    BASE / "hsk3" / "data" / "de_06"
)

OUTPUT = (
    BASE / "hsk3" / "output" / "de_06"
)

QUESTIONS = OUTPUT / "questions"

GROUP_DIR = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_06_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_80_cau_ung_vien.json"
)

PREVIEW_HTML = (
    OUTPUT / "kiem_tra_80_cau.html"
)

EXAM_CODE = "H31006"


# =====================================================
# 2. SO DO TRANG 70 CAU HOI
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

    # Giu du A/B/C cua cau 64.
    11: 742,

    # Giu du A/B/C cua cau 70.
    12: 754,

    13: 545,
    14: 559,
}


# =====================================================
# 4. HAI BANG HINH NGHE DA HOAN THANH
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
# 6. HAM HO TRO
# =====================================================

def check_file(path):

    if (
        not path.is_file()
        or path.stat().st_size == 0
    ):
        raise RuntimeError(
            f"Thieu file hoac file rong: {path}"
        )

    return path


def load_json(path):

    return json.loads(
        check_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


def json_bytes(data):

    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")


def sha256(path):

    return hashlib.sha256(
        check_file(path).read_bytes()
    ).hexdigest()


def check_write(path, content):

    if (
        path.exists()
        and path.read_bytes() != content
    ):
        raise RuntimeError(
            "File da ton tai voi noi dung khac."
            "\nKhong ghi de:\n"
            + str(path)
        )


def write_safe(path, content):

    check_write(path, content)

    if not path.exists():

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        path.write_bytes(content)


# =====================================================
# 7. TIM TRANG PDF CUA MOI CAU
# =====================================================

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
        f"Khong tim thay trang cau {number}."
    )


# =====================================================
# 8. TIM NHOM LUA CHON CUA MOI CAU
# =====================================================

def group_for(number):

    for name, config in ALL_GROUPS.items():

        if (
            config["cau_tu"]
            <= number
            <= config["cau_den"]
        ):
            return name

    return None


# =====================================================
# 9. KIEM TRA DU LIEU BUOC 1
# =====================================================

def validate_source():

    info = load_json(ANSWER_JSON)

    identity = (
        info.get("cap_hsk"),
        info.get("so_de"),
        info.get("ma_de_goc"),
    )

    if identity != (3, 6, EXAM_CODE):
        raise RuntimeError(
            "JSON buoc 1 khong phai "
            "HSK3 De 6 - H31006."
        )

    counts = (
        info.get("tong_cau"),
        info.get("so_cau_nghe"),
        info.get("so_cau_doc"),
        info.get("so_cau_viet"),
    )

    if counts != (80, 40, 30, 10):
        raise RuntimeError(
            "So cau trong JSON buoc 1 sai."
        )

    answers = info.get("dap_an", {})

    expected_numbers = {
        str(number)
        for number in range(1, 81)
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
                f"Dap an cau {number} rong."
            )

    # ================================================
    # 10. BAO TOAN DAP AN THAY THE CAU 75
    # ================================================

    alternatives = info.get(
        "dap_an_thay_the", {}
    )

    expected_alternative = (
        "对这条绿裤子，她很满意。"
    )

    if set(alternatives) != {"75"}:
        raise RuntimeError(
            "Thieu dap an thay the cua cau 75."
        )

    if alternatives["75"] != [
        expected_alternative
    ]:
        raise RuntimeError(
            "Dap an thay the cau 75 sai."
        )

    if answers["75"] != (
        "她对这条绿裤子很满意。"
    ):
        raise RuntimeError(
            "Dap an chinh cau 75 sai."
        )

    # ================================================
    # 11. KIEM TRA PDF NGUON
    # ================================================

    pdf_value = info.get("file_pdf")

    if not pdf_value:
        raise RuntimeError(
            "JSON buoc 1 thieu duong dan PDF."
        )

    pdf_path = check_file(
        Path(pdf_value)
    )

    if (
        pdf_path.parent.resolve()
        != SOURCE.resolve()
    ):
        raise RuntimeError(
            "PDF khong nam trong thu muc "
            "HSK3 DE 6."
        )

    # ================================================
    # 12. BAO VE HAI BANG HINH NGHE
    # ================================================

    old_hashes = {}

    for name in EXISTING_GROUPS:

        path = (
            GROUP_DIR / f"{name}.png"
        )

        old_hashes[name] = sha256(path)

    return (
        pdf_path,
        info,
        old_hashes,
    )


# =====================================================
# 13. KIEM TRA PDF H31006
# =====================================================

def validate_pdf(doc):

    if len(doc) != 16:
        raise RuntimeError(
            f"PDF H31006 phai co 16 trang, "
            f"nhung hien co {len(doc)}."
        )

    cover = doc[0].get_text("text")

    answer_page = doc[14].get_text("text")

    writing_page = doc[15].get_text("text")

    if (
        EXAM_CODE not in cover
        or EXAM_CODE not in answer_page
    ):
        raise RuntimeError(
            "Ma de PDF khong phai H31006."
        )

    if "答案" not in answer_page:
        raise RuntimeError(
            "Trang 15 khong phai "
            "bang dap an Nghe/Doc."
        )

    if "书" not in writing_page:
        raise RuntimeError(
            "Trang 16 khong phai "
            "dap an Viet."
        )

    total = sum(
        len(numbers)
        for numbers in PAGE_QUESTIONS.values()
    )

    if total != 70:
        raise RuntimeError(
            "So do trang khong du 70 cau."
        )


# =====================================================
# 14. TIM VI TRI TUNG CAU TRONG PDF
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

        for line in block.get(
            "lines", []
        ):

            text = "".join(
                span.get("text", "")
                for span in line.get(
                    "spans", []
                )
            ).strip()

            match = re.match(
                r"^(\d{1,2})\s*[.．、]",
                text
            )

            if not match:
                continue

            number = int(
                match.group(1)
            )

            x0, y0, _, _ = line["bbox"]

            if (
                number in numbers
                and x0 < 125
                and y0 < 760
            ):

                found.setdefault(
                    number, []
                ).append(float(y0))

    # Moi cau phai co dung mot vi tri.
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
            f"Trang {page_no} khong "
            "nhan dien du cac so cau.\n"
            f"Thieu: {missing}\n"
            f"Tim thay: {found}"
        )

    positions = {
        number: found[number][0]
        for number in numbers
    }

    # Kiem tra thu tu tu tren xuong.
    for first, second in zip(
        numbers,
        numbers[1:]
    ):

        if (
            positions[first]
            >= positions[second]
        ):
            raise RuntimeError(
                f"Thu tu cau trang "
                f"{page_no} bi sai."
            )

    return positions


# =====================================================
# 15. TINH TOA DO CAT TUNG CAU
# =====================================================

def question_rect(
    page,
    page_no,
    numbers,
    positions,
    index
):

    number = numbers[index]

    # Phan Viet 76-80 co Pinyin
    # nam phia tren dong cau hoi.
    writing_pinyin = (
        76 <= number <= 80
    )

    top_padding = (
        26 if writing_pinyin else 11
    )

    next_padding = (
        27 if writing_pinyin else 10
    )

    top = (
        positions[number] - top_padding
    )

    if index + 1 < len(numbers):

        next_number = (
            numbers[index + 1]
        )

        bottom = (
            positions[next_number]
            - next_padding
        )

    else:

        bottom = PAGE_BOTTOM[page_no]

    rect = (
        fitz.Rect(
            75,
            top,
            530,
            bottom
        ) & page.rect
    )

    if (
        rect.is_empty
        or rect.width < 200
        or rect.height < 20
    ):
        raise RuntimeError(
            f"Cau {number} co khung cat "
            f"khong hop le: {rect}"
        )

    words = page.get_text("words")

    # ================================================
    # 16. KIEM TRA KHONG MAT A/B/C
    # ================================================

    if (
        21 <= number <= 40
        or 61 <= number <= 70
    ):

        found = set()

        for word in words:

            value = str(
                word[4]
            ).strip()

            if (
                value in ("A", "B", "C")
                and rect.contains(
                    fitz.Rect(word[:4])
                )
            ):
                found.add(value)

        if found != set("ABC"):

            raise RuntimeError(
                f"Cau {number} thieu "
                "phuong an A/B/C.\n"
                f"Tim thay: {sorted(found)}"
            )

    # ================================================
    # 17. KIEM TRA PINYIN CAU 76-80
    # ================================================

    if writing_pinyin:

        pinyin_words = []

        for word in words:

            value = str(
                word[4]
            )

            if (
                re.search(r"[a-zA-Z]", value)
                and word[1] < positions[number]
                and rect.contains(
                    fitz.Rect(word[:4])
                )
            ):

                pinyin_words.append(value)

        if not pinyin_words:

            raise RuntimeError(
                f"Cau {number} thieu Pinyin."
            )

    return rect


# =====================================================
# 18. KIEM TRA BANG LUA CHON CHUNG
# =====================================================

def group_rect(
    page,
    name,
    config
):

    rect = fitz.Rect(
        config["rect"]
    )

    if not page.rect.contains(rect):
        raise RuntimeError(
            f"Toa do bang {name} "
            "khong hop le."
        )

    found = set()

    for word in page.get_text("words"):

        x0, y0, _, _, value = word[:5]

        value = unicodedata.normalize(
            "NFKC",
            str(value)
        ).strip()

        if rect.contains(
            fitz.Point(x0, y0)
        ):
            found.add(value)

    expected = set(
        config["lua_chon"]
    )

    if not expected.issubset(found):

        missing = sorted(
            expected - found
        )

        raise RuntimeError(
            f"Bang {name} thieu nhan: "
            f"{missing}"
        )

    return rect


# =====================================================
# 19. XUAT ANH PNG
# =====================================================

def render_png(page, rect):

    pix = page.get_pixmap(
        matrix=fitz.Matrix(2.5, 2.5),
        clip=rect,
        alpha=False
    )

    return pix.tobytes("png")


# =====================================================
# 20. TAO HTML KIEM TRA 80 CAU
# =====================================================

def create_preview():

    blocks = [
        "<h1>HSK3 – Đề 6 (H31006)</h1>",

        "<p>"
        "Kiểm tra hình ảnh 80 câu. "
        "Không hiển thị đáp án. "
        "Chưa thay đổi SQL Server."
        "</p>",
    ]

    for number in range(1, 81):

        if number == 1:

            blocks.append(
                "<h2>I. Nghe – Câu 1–40</h2>"
            )

        elif number == 41:

            blocks.append(
                "<h2>II. Đọc – Câu 41–70</h2>"
            )

        elif number == 71:

            blocks.append(
                "<h2>III. Viết – Câu 71–80</h2>"
            )

        # Hien thi bang chung mot lan
        # o dau moi nhom.
        group = group_for(number)

        if group:

            config = ALL_GROUPS[group]

            if number == config["cau_tu"]:

                last = config["cau_den"]

                blocks.append(
                    '<section class="group">'
                    f'<h3>Bảng lựa chọn câu '
                    f'{number}–{last}</h3>'
                    '<img src="groups/'
                    f'{escape(group)}.png" '
                    'alt="Bảng lựa chọn">'
                    '</section>'
                )

        if number <= 10:

            blocks.append(
                '<span class="mini">'
                f'Câu {number}'
                '</span>'
            )

        else:

            filename = (
                f"cau_{number:02d}.png"
            )

            blocks.append(
                '<section>'
                f'<h3>Câu {number:02d}</h3>'
                '<img src="questions/'
                f'{filename}" '
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

<title>HSK3 Đề 6 – H31006</title>

<style>
* {
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    background: #f3f5fa;
    color: #18263d;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 1050px;
    margin: auto;
}

h1 {
    font-size: 26px;
}

h2 {
    border-bottom: 2px solid #dde4ef;
    padding: 14px 0;
    margin-top: 35px;
}

p {
    color: #66748a;
    line-height: 1.6;
}

section {
    background: #fff;
    padding: 18px;
    border: 1px solid #dce3ef;
    border-radius: 12px;
    margin: 15px 0;
}

section.group {
    background: #eff6ff;
}

h3 {
    font-size: 17px;
    margin: 0 0 12px;
}

section img {
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
# 21. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 06")
    print("BUOC 2 - TACH CAU 11-80")
    print("=" * 60)

    (
        pdf_path,
        source_info,
        old_hashes
    ) = validate_source()

    images = {}

    question_manifest = {}
    group_manifest = {}

    # ================================================
    # 22. GHI NHAN HAI BANG NGHE DA CO
    # ================================================

    for name, config in (
        EXISTING_GROUPS.items()
    ):

        group_manifest[name] = {
            "trang_pdf": config["trang_pdf"],
            "anh": f"groups/{name}.png",
            "lua_chon": config["lua_chon"],
            "cau_tu": config["cau_tu"],
            "cau_den": config["cau_den"],
        }

    with fitz.open(pdf_path) as doc:

        validate_pdf(doc)

        # ============================================
        # 23. GHI NHAN CAU 1-10
        # ============================================

        for number in range(1, 11):

            question_manifest[
                str(number)
            ] = {
                "trang_pdf": page_for(number),
                "anh": None,
                "nhom_lua_chon": group_for(number),
            }

        # ============================================
        # 24. TACH 70 ANH CAU 11-80
        # ============================================

        print(
            "\n===== TACH 70 ANH CAU HOI ====="
        )

        for page_no, numbers in (
            PAGE_QUESTIONS.items()
        ):

            page = doc[
                page_no - 1
            ]

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

                filename = (
                    f"cau_{number:02d}.png"
                )

                relative = (
                    f"questions/{filename}"
                )

                destination = (
                    QUESTIONS / filename
                )

                images[destination] = (
                    render_png(page, rect)
                )

                question_manifest[
                    str(number)
                ] = {
                    "trang_pdf": page_no,
                    "anh": relative,

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
                f"Trang {page_no}: "
                f"{len(numbers)} cau"
            )

        # ============================================
        # 25. TACH BON BANG LUA CHON DOC
        # ============================================

        print(
            "\n===== BANG LUA CHON DOC ====="
        )

        for name, config in (
            NEW_GROUPS.items()
        ):

            page_no = config["trang_pdf"]

            page = doc[
                page_no - 1
            ]

            rect = group_rect(
                page,
                name,
                config
            )

            destination = (
                GROUP_DIR / f"{name}.png"
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
                "toa_do": list(
                    config["rect"]
                ),
            }

            print(
                f"{name}: "
                f"{len(config['lua_chon'])} "
                "lua chon"
            )

    # ================================================
    # 26. KIEM TRA SO LUONG ANH
    # ================================================

    if len(question_manifest) != 80:
        raise RuntimeError(
            "Manifest khong du 80 cau."
        )

    if len(group_manifest) != 6:
        raise RuntimeError(
            "Manifest khong du 6 bang."
        )

    # 70 anh cau hoi + 4 bang Doc moi.
    if len(images) != 74:
        raise RuntimeError(
            f"So anh moi sai: "
            f"{len(images)}/74"
        )

    expected_numbers = {
        str(number)
        for number in range(1, 81)
    }

    if (
        set(question_manifest)
        != expected_numbers
    ):
        raise RuntimeError(
            "So cau manifest khong "
            "lien tuc tu 1-80."
        )

    # ================================================
    # 27. TAO MANIFEST JSON
    # ================================================

    manifest = {
        "cap_hsk": 3,
        "so_de": 6,
        "ma_de_goc": EXAM_CODE,

        "so_trang_pdf": 16,
        "so_cau": 80,

        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        # PDF De 6 khong co transcript.
        "trang_loi_thoai": [],

        "trang_dap_an": [15, 16],

        "cau_hoi": question_manifest,

        "bang_lua_chon": group_manifest,

        # Giu dap an hop le thu hai
        # cua cau 75 cho buoc chuan hoa.
        "dap_an_thay_the": (
            source_info["dap_an_thay_the"]
        ),
    }

    # ================================================
    # 28. TAO FILE JSON VA HTML
    # ================================================

    outputs = dict(images)

    outputs[MANIFEST_JSON] = (
        json_bytes(manifest)
    )

    outputs[PREVIEW_HTML] = (
        create_preview()
    )

    # ================================================
    # 29. BAO VE FILE CU TRUOC KHI GHI
    # ================================================

    for path, content in (
        outputs.items()
    ):

        check_write(path, content)

    # Kiem tra hai bang Nghe khong doi.
    for name, old_hash in (
        old_hashes.items()
    ):

        path = (
            GROUP_DIR / f"{name}.png"
        )

        if sha256(path) != old_hash:

            raise RuntimeError(
                f"Bang hinh Nghe {name} "
                "da bi thay doi."
            )

    # ================================================
    # 30. LUU ANH, JSON VA HTML
    # ================================================

    for path, content in (
        outputs.items()
    ):

        write_safe(path, content)

    # ================================================
    # 31. KIEM TRA SAU KHI LUU
    # ================================================

    for number in range(11, 81):

        check_file(
            QUESTIONS
            / f"cau_{number:02d}.png"
        )

    for name in ALL_GROUPS:

        check_file(
            GROUP_DIR / f"{name}.png"
        )

    for name, old_hash in (
        old_hashes.items()
    ):

        path = (
            GROUP_DIR / f"{name}.png"
        )

        if sha256(path) != old_hash:

            raise RuntimeError(
                f"Bang Nghe {name} "
                "khong con nguyen ven."
            )

    # ================================================
    # 32. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH HSK3 DE 06 - BUOC 2"
    )

    print("=" * 60)

    print("Ma de: H31006")
    print("PDF: 16 trang")

    print("Anh cau 11-80: 70/70")

    print(
        "Bang lua chon: 6/6 "
        "(2 Nghe + 4 Doc)"
    )

    print(
        "Cau 21-40 va 61-70: "
        "da kiem tra A/B/C"
    )

    print(
        "Cau 76-80: "
        "da kiem tra Pinyin"
    )

    print(
        "Cau 75: "
        "da bao toan dap an thay the"
    )

    print(f"\nJSON: {MANIFEST_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
