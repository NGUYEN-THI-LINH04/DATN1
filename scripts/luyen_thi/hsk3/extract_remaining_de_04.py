
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 04 (H31004), BUOC 2.

- Giu nguyen 2 bang hinh Nghe cau 1-10.
- Tach 70 anh cau hoi 11-80.
- Tach 4 bang lua chon chung phan Doc.
- Kiem tra A/B/C cua cac cau trac nghiem.
- Giu Pinyin cua cau 76-80.
- Bao toan dap an thay the cua cau 75.
- Tao JSON manifest va HTML xem truoc.

KHONG ket noi SQL Server.
KHONG sua cac de thi da hoan thanh.
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
    / "source" / "De_HSK" / "HSK3" / "ĐỀ 4"
)

DATA = HSK3 / "data" / "de_04"
OUTPUT = HSK3 / "output" / "de_04"

QUESTIONS = OUTPUT / "questions"
GROUPS = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_04_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_80_cau_ung_vien.json"
)

PREVIEW_HTML = (
    OUTPUT / "kiem_tra_80_cau.html"
)

EXAM_CODE = "H31004"


# =====================================================
# 2. SO DO 70 CAU HOI
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
# 3. GIOI HAN VUNG CAT
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
# 5. BON BANG LUA CHON CHUNG PHAN DOC
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

    if (
        not path.is_file()
        or path.stat().st_size == 0
    ):
        raise RuntimeError(
            f"Thieu file hoac file rong:\n{path}"
        )

    return path


def load_json(path):

    return json.loads(
        check_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


def json_bytes(value):

    return json.dumps(
        value,
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
            "Khong ghi de file khac noi dung:\n"
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
# 7. XAC DINH TRANG VA NHOM LUA CHON
# =====================================================

def page_for(number):

    if number <= 5:
        return 2

    if number <= 10:
        return 3

    for page_no, numbers in (
        PAGE_QUESTIONS.items()
    ):

        if number in numbers:
            return page_no

    raise RuntimeError(
        f"Cau {number} khong co trang PDF."
    )


def group_for(number):

    for name, item in ALL_GROUPS.items():

        if (
            item["cau_tu"]
            <= number
            <= item["cau_den"]
        ):
            return name

    return None


# =====================================================
# 8. KIEM TRA JSON BUOC 1
# =====================================================

def validate_source():

    info = load_json(ANSWER_JSON)

    if (
        info.get("cap_hsk"),
        info.get("so_de"),
        info.get("ma_de_goc")
    ) != (3, 4, EXAM_CODE):

        raise RuntimeError(
            "JSON dap an khong phai HSK3 De 4."
        )

    counts = (
        info.get("tong_cau"),
        info.get("so_cau_nghe"),
        info.get("so_cau_doc"),
        info.get("so_cau_viet"),
    )

    if counts != (80, 40, 30, 10):

        raise RuntimeError(
            "So cau trong JSON buoc 1 khong khop."
        )

    answers = info.get("dap_an", {})

    if set(answers) != {
        str(i) for i in range(1, 81)
    }:
        raise RuntimeError(
            "Khong du 80 dap an."
        )

    for answer in answers.values():

        if not str(answer).strip():
            raise RuntimeError(
                "Co dap an rong."
            )

    # De 4 co hai dap an dung cau 75.
    # Phai bao toan dap an thu hai.
    alternatives = info.get(
        "dap_an_thay_the", {}
    )

    alt_75 = alternatives.get("75")

    if not (
        isinstance(alt_75, list)
        and len(alt_75) == 1
        and str(alt_75[0]).strip()
    ):
        raise RuntimeError(
            "Thieu dap an thay the cua cau 75."
        )

    pdf_value = info.get("file_pdf")

    if not pdf_value:
        raise RuntimeError(
            "JSON thieu duong dan PDF."
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
            "HSK3 DE 4."
        )

    # Ghi hash de bao ve 2 bang Nghe.
    old_hashes = {}

    for name in EXISTING_GROUPS:

        path = GROUPS / f"{name}.png"

        old_hashes[name] = sha256(path)

    return pdf_path, old_hashes, info


# =====================================================
# 9. KIEM TRA PDF
# =====================================================

def validate_pdf(doc):

    if len(doc) != 22:

        raise RuntimeError(
            f"PDF co {len(doc)} trang, "
            "H31004 phai co 22 trang."
        )

    if EXAM_CODE not in doc[0].get_text(
        "text"
    ):
        raise RuntimeError(
            "Trang bia khong phai H31004."
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

    total = sum(
        len(numbers)
        for numbers in PAGE_QUESTIONS.values()
    )

    if total != 70:
        raise RuntimeError(
            "So do trang khong du 70 cau."
        )


# =====================================================
# 10. TIM VI TRI SO CAU
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

    # Moi cau phai tim du 1 vi tri.
    if (
        set(found) != set(numbers)
        or any(
            len(values) != 1
            for values in found.values()
        )
    ):

        raise RuntimeError(
            f"Trang {page_no} khong tim du "
            "vi tri cac cau.\n"
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
# 11. TINH TOA DO ANH TUNG CAU
# =====================================================

def question_rect(
    page,
    page_no,
    numbers,
    positions,
    index
):

    number = numbers[index]

    # Phan Viet 76-80 co Pinyin ben tren.
    writing_pinyin = number >= 76

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

        next_number = numbers[
            index + 1
        ]

        bottom = (
            positions[next_number]
            - next_padding
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
        or rect.width < 200
        or rect.height < 20
    ):
        raise RuntimeError(
            f"Cau {number} co toa do "
            f"khong hop le: {rect}"
        )

    # ================================================
    # 12. KIEM TRA KHONG MAT A/B/C
    # ================================================

    if (
        21 <= number <= 40
        or 61 <= number <= 70
    ):

        found = set()

        for word in page.get_text("words"):

            value = word[4]

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
                "lua chon A/B/C.\n"
                f"Tim thay: {sorted(found)}"
            )

    # ================================================
    # 13. KIEM TRA PINYIN CAU 76-80
    # ================================================

    if writing_pinyin:

        pinyin_words = []

        for word in page.get_text("words"):

            value = str(word[4])

            if (
                re.search(r"[a-zA-Z]", value)
                and rect.contains(
                    fitz.Rect(word[:4])
                )
                and word[1] < positions[number]
            ):
                pinyin_words.append(value)

        if not pinyin_words:
            raise RuntimeError(
                f"Cau {number} "
                "bi thieu Pinyin."
            )

    return rect


# =====================================================
# 14. KIEM TRA BANG LUA CHON CHUNG
# =====================================================

def group_rect(page, name, config):

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

        value = str(
            word[4]
        ).strip()

        if (
            len(value) == 1
            and value in config["lua_chon"]
            and rect.contains(
                fitz.Point(
                    word[0],
                    word[1]
                )
            )
        ):
            found.add(value)

    expected = set(
        config["lua_chon"]
    )

    if found != expected:

        raise RuntimeError(
            f"Bang {name} thieu nhan.\n"
            f"Thieu: {sorted(expected - found)}"
        )

    return rect


# =====================================================
# 15. RENDER ANH PNG
# =====================================================

def render_png(page, rect):

    pix = page.get_pixmap(
        matrix=fitz.Matrix(2.5, 2.5),
        clip=rect,
        alpha=False
    )

    return pix.tobytes("png")


# =====================================================
# 16. TAO HTML XEM TRUOC 80 CAU
# =====================================================

def create_preview():

    blocks = [
        "<h1>HSK3 – Đề 4 (H31004)</h1>",

        "<p>"
        "Kiểm tra 80 câu. "
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

        # Hien thi bang lua chon mot lan
        # o dau moi nhom cau hoi.
        group = group_for(number)

        if group:

            config = ALL_GROUPS[group]

            if number == config["cau_tu"]:

                last = config["cau_den"]

                blocks.append(
                    '<section class="group">'
                    f'<h3>Bảng lựa chọn '
                    f'câu {number}–{last}</h3>'
                    f'<img src="groups/'
                    f'{escape(group)}.png" '
                    'alt="Bảng lựa chọn">'
                    '</section>'
                )

        if number <= 10:

            blocks.append(
                f'<span class="mini">'
                f'Câu {number}</span>'
            )

        else:

            blocks.append(
                '<section>'
                f'<h3>Câu {number:02d}</h3>'
                '<img src="questions/'
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

<title>HSK3 Đề 4 – H31004</title>

<style>
* {
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    background: #f4f6fa;
    color: #18263d;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 1050px;
    margin: auto;
}

h1 {
    font-size: 25px;
}

h2 {
    border-bottom: 2px solid #dbe2eb;
    padding: 14px 0;
    margin-top: 35px;
}

p {
    color: #64748b;
    line-height: 1.6;
}

section {
    background: white;
    padding: 18px;
    border: 1px solid #dbe2eb;
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
# 17. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 04")
    print("BUOC 2 - TACH CAU 11-80")
    print("=" * 60)

    (
        pdf_path,
        old_hashes,
        source_info
    ) = validate_source()

    images = {}
    question_manifest = {}
    group_manifest = {}

    # ================================================
    # 18. GHI NHAN HAI BANG NGHE DA CO
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
        # 19. CAU 1-10
        # ============================================

        for number in range(1, 11):

            question_manifest[str(number)] = {
                "trang_pdf": page_for(number),
                "anh": None,
                "nhom_lua_chon": group_for(number),
            }

        # ============================================
        # 20. TACH 70 CAU 11-80
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

                filename = (
                    f"cau_{number:02d}.png"
                )

                relative_path = (
                    f"questions/{filename}"
                )

                destination = (
                    QUESTIONS / filename
                )

                images[destination] = (
                    render_png(
                        page,
                        rect
                    )
                )

                question_manifest[str(number)] = {
                    "trang_pdf": page_no,
                    "anh": relative_path,

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
        # 21. TACH BON BANG LUA CHON DOC
        # ============================================

        print(
            "\n===== BANG LUA CHON DOC ====="
        )

        for name, config in (
            NEW_GROUPS.items()
        ):

            page_no = config["trang_pdf"]

            page = doc[page_no - 1]

            rect = group_rect(
                page,
                name,
                config
            )

            destination = (
                GROUPS / f"{name}.png"
            )

            images[destination] = (
                render_png(
                    page,
                    rect
                )
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
                f"{name}: "
                f"{len(config['lua_chon'])} "
                "lua chon"
            )

    # ================================================
    # 22. KIEM TRA SO LUONG
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
            f"So anh moi sai: {len(images)}/74"
        )

    # ================================================
    # 23. TAO MANIFEST JSON
    # ================================================

    manifest = {
        "cap_hsk": 3,
        "so_de": 4,
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

        # Giu lai dap an thay the cua cau 75.
        "dap_an_thay_the": (
            source_info.get(
                "dap_an_thay_the", {}
            )
        ),
    }

    # ================================================
    # 24. TAO FILE JSON VA HTML
    # ================================================

    outputs = dict(images)

    outputs[MANIFEST_JSON] = (
        json_bytes(manifest)
    )

    outputs[PREVIEW_HTML] = (
        create_preview()
    )

    # ================================================
    # 25. BAO VE FILE CU
    # ================================================

    for path, content in outputs.items():

        check_write(
            path,
            content
        )

    for name, old_hash in (
        old_hashes.items()
    ):

        path = GROUPS / f"{name}.png"

        if sha256(path) != old_hash:
            raise RuntimeError(
                f"Bang hinh Nghe {name} "
                "da bi thay doi."
            )

    # ================================================
    # 26. LUU ANH VA JSON
    # ================================================

    for path, content in outputs.items():

        write_safe(
            path,
            content
        )

    # ================================================
    # 27. KIEM TRA SAU KHI LUU
    # ================================================

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
        old_hashes.items()
    ):

        path = GROUPS / f"{name}.png"

        if sha256(path) != old_hash:
            raise RuntimeError(
                f"Bang Nghe {name} "
                "khong con nguyen ven."
            )

    # ================================================
    # 28. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH HSK3 DE 04 - BUOC 2"
    )

    print("=" * 60)

    print("Ma de: H31004")
    print("Anh cau 11-80: 70/70")

    print(
        "Bang lua chon: 6/6 "
        "(2 Nghe + 4 Doc)"
    )

    print(
        "Cau 64 va 70: "
        "da kiem tra A/B/C"
    )

    print(
        "Cau 76-80: "
        "da kiem tra Pinyin"
    )

    print(
        "Cau 75: "
        "da giu dap an thay the"
    )

    print(f"\nJSON: {MANIFEST_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
