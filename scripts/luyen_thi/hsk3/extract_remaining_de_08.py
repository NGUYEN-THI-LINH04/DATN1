
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 08 (H31008) - BUOC 2

- Giu nguyen 2 bang hinh Nghe cau 1-10.
- Tach 70 anh cau hoi 11-80.
- Tach 4 bang lua chon chung phan Doc.
- Kiem tra A/B/C cua cac cau trac nghiem.
- Giu Pinyin cua cau 76-80.
- Tao manifest JSON va HTML kiem tra 80 cau.

KHONG ket noi SQL Server.
KHONG thay doi cac de thi da hoan thanh.
KHONG ghi de file khac noi dung.
"""

from pathlib import Path
from html import escape

import hashlib
import json
import re
import unicodedata

import fitz


# =====================================================
# 1. CAU HINH DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "luyen_thi"

SOURCE = (
    BASE / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 8"
)

DATA = (
    BASE / "hsk3" / "data" / "de_08"
)

OUTPUT = (
    BASE / "hsk3" / "output" / "de_08"
)

QUESTIONS = OUTPUT / "questions"

GROUPS = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_08_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_80_cau_ung_vien.json"
)

PREVIEW_HTML = (
    OUTPUT / "kiem_tra_80_cau.html"
)

CODE = "H31008"


# =====================================================
# 2. SO DO TRANG CAU 11-80
# =====================================================

# So trang tinh tu 1.
# Khong su dung index Python 0.

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
# 3. GIOI HAN VUNG CAT CUOI TRANG
# =====================================================

# Da doi chieu voi PDF H31008.
# Chi dung cho cau cuoi cung moi trang.

PAGE_BOTTOM = {
    4: 741,
    5: 735,
    6: 742,

    7: 678,
    8: 532,
    9: 628,
    10: 741,

    # Giu du cau 64 va A/B/C.
    11: 742,

    # Giu du cau 70 va A/B/C.
    12: 754,

    13: 560,
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

def require_file(path):

    if (
        not path.is_file()
        or path.stat().st_size == 0
    ):
        raise RuntimeError(
            f"File khong ton tai hoac rong:\n{path}"
        )

    return path


def read_json(path):

    return json.loads(
        require_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


def bytes_json(value):

    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")


def sha256(path):

    return hashlib.sha256(
        require_file(path).read_bytes()
    ).hexdigest()


# =====================================================
# 7. GHI FILE AN TOAN
# =====================================================

def save_safe(path, content):

    if path.exists():

        if path.read_bytes() != content:

            raise RuntimeError(
                "KHONG ghi de file "
                "khac noi dung:\n"
                + str(path)
            )

        return

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_bytes(content)


# =====================================================
# 8. XAC DINH TRANG PDF
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


# =====================================================
# 9. XAC DINH NHOM LUA CHON
# =====================================================

def group_for(number):

    for name, item in (
        ALL_GROUPS.items()
    ):

        if (
            item["cau_tu"]
            <= number
            <= item["cau_den"]
        ):
            return name

    return None


# =====================================================
# 10. KIEM TRA JSON BUOC 1
# =====================================================

def validate_source():

    source = read_json(
        ANSWER_JSON
    )

    identity = (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc"),
    )

    if identity != (3, 8, CODE):

        raise RuntimeError(
            "JSON buoc 1 khong phai "
            "HSK3 De 8 - H31008."
        )

    counts = (
        source.get("tong_cau"),
        source.get("so_cau_nghe"),
        source.get("so_cau_doc"),
        source.get("so_cau_viet"),
    )

    if counts != (80, 40, 30, 10):

        raise RuntimeError(
            "JSON buoc 1 sai so cau."
        )

    # ================================================
    # 11. KIEM TRA DU 80 DAP AN
    # ================================================

    answers = source.get(
        "dap_an", {}
    )

    expected = {
        str(number)
        for number in range(1, 81)
    }

    if set(answers) != expected:

        raise RuntimeError(
            "JSON buoc 1 khong du 80 dap an."
        )

    for answer in answers.values():

        if not str(answer).strip():

            raise RuntimeError(
                "Co dap an rong."
            )

    # ================================================
    # 12. KIEM TRA DAP AN THAY THE
    # ================================================

    if source.get(
        "dap_an_thay_the"
    ) != {}:

        raise RuntimeError(
            "De 8 khong co dap an "
            "thay the trong PDF goc."
        )

    # ================================================
    # 13. KIEM TRA CUM TU SAP XEP
    # ================================================

    tokens = source.get(
        "cum_tu_sap_xep", {}
    )

    if set(tokens) != {
        str(number)
        for number in range(71, 76)
    }:

        raise RuntimeError(
            "JSON buoc 1 thieu "
            "cum tu sap xep cau 71-75."
        )

    # ================================================
    # 14. KIEM TRA PDF NGUON
    # ================================================

    path_value = source.get(
        "file_pdf"
    )

    if not path_value:

        raise RuntimeError(
            "JSON buoc 1 thieu file_pdf."
        )

    pdf_path = require_file(
        Path(path_value)
    )

    if (
        pdf_path.parent.resolve()
        != SOURCE.resolve()
    ):

        raise RuntimeError(
            "PDF khong nam trong "
            "thu muc HSK3 DE 8."
        )

    # ================================================
    # 15. BAO VE HAI BANG HINH NGHE
    # ================================================

    old_hashes = {}

    for name in EXISTING_GROUPS:

        path = (
            GROUPS / f"{name}.png"
        )

        old_hashes[name] = sha256(path)

    return (
        source,
        pdf_path,
        old_hashes,
    )


# =====================================================
# 16. KIEM TRA PDF H31008
# =====================================================

def validate_pdf(doc):

    if len(doc) != 22:

        raise RuntimeError(
            "PDF H31008 phai co 22 trang."
            f"\nHien co: {len(doc)}"
        )

    if (
        CODE not in doc[0].get_text("text")
        or CODE not in doc[20].get_text("text")
    ):

        raise RuntimeError(
            "PDF khong dung ma de H31008."
        )

    if "听力材料" not in doc[14].get_text(
        "text"
    ):

        raise RuntimeError(
            "Trang 15 khong phai "
            "loi thoai Nghe."
        )

    if (
        "答案" not in doc[20].get_text("text")
        or "书" not in doc[21].get_text("text")
    ):

        raise RuntimeError(
            "Khong tim thay "
            "dap an trang 21-22."
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
# 17. TIM VI TRI SO CAU
# =====================================================

def positions_for(
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
                ).append(
                    float(y0)
                )

    # ================================================
    # 18. KIEM TRA DU SO CAU
    # ================================================

    missing = sorted(
        set(numbers) - set(found)
    )

    duplicates = [
        number

        for number, values
        in found.items()

        if len(values) != 1
    ]

    if missing or duplicates:

        raise RuntimeError(
            f"Trang {page_no} "
            "nhan dien sai so cau.\n"
            f"Thieu: {missing}\n"
            f"Trung: {duplicates}"
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
                f"Trang {page_no} "
                "sai thu tu so cau."
            )

    return positions


# =====================================================
# 19. TINH TOA DO CAT TUNG CAU
# =====================================================

def question_rect(
    page,
    page_no,
    numbers,
    positions,
    index
):

    number = numbers[index]

    # Cau 76-80 co Pinyin phia tren.

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
        positions[number]
        - top_padding
    )

    if index < len(numbers) - 1:

        next_number = (
            numbers[index + 1]
        )

        bottom = (
            positions[next_number]
            - next_padding
        )

    else:

        bottom = PAGE_BOTTOM[
            page_no
        ]

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
            f"Cau {number} sai "
            f"vung cat: {rect}"
        )

    words = page.get_text(
        "words"
    )

    # ================================================
    # 20. KIEM TRA A/B/C
    # ================================================

    if (
        21 <= number <= 40
        or 61 <= number <= 70
    ):

        labels = set()

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

                labels.add(value)

        if labels != set("ABC"):

            missing = sorted(
                set("ABC") - labels
            )

            raise RuntimeError(
                f"Cau {number} "
                "thieu A/B/C.\n"
                f"Thieu: {missing}"
            )

    # ================================================
    # 21. KIEM TRA PINYIN CAU 76-80
    # ================================================

    if writing_pinyin:

        pinyin_words = []

        for word in words:

            value = str(
                word[4]
            )

            if (
                re.search(
                    r"[A-Za-z]",
                    value
                )

                and word[1] < positions[number]

                and rect.contains(
                    fitz.Rect(word[:4])
                )
            ):

                pinyin_words.append(
                    value
                )

        if not pinyin_words:

            raise RuntimeError(
                f"Cau {number} "
                "bi thieu Pinyin."
            )

    return rect


# =====================================================
# 22. KIEM TRA BANG LUA CHON CHUNG
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
            f"Bang {name} "
            "nam ngoai trang PDF."
        )

    labels = set()

    for word in page.get_text(
        "words"
    ):

        value = unicodedata.normalize(
            "NFKC",
            str(word[4])
        ).strip()

        if rect.contains(
            fitz.Point(
                word[0],
                word[1]
            )
        ):

            labels.add(value)

    expected = set(
        config["lua_chon"]
    )

    missing = expected - labels

    if missing:

        raise RuntimeError(
            f"Bang {name} thieu nhan: "
            f"{sorted(missing)}"
        )

    return rect


# =====================================================
# 23. XUAT ANH PNG
# =====================================================

def render_png(
    page,
    rect
):

    pix = page.get_pixmap(
        matrix=fitz.Matrix(2.5, 2.5),
        clip=rect,
        alpha=False
    )

    return pix.tobytes("png")


# =====================================================
# 24. TAO HTML KIEM TRA 80 CAU
# =====================================================

def create_preview():

    blocks = [
        "<h1>HSK3 – Đề 8 (H31008)</h1>",

        "<p>"
        "Kiểm tra toàn bộ 80 câu. "
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
        # o dau moi nhom cau hoi.

        group = group_for(
            number
        )

        if (
            group
            and number
            == ALL_GROUPS[group]["cau_tu"]
        ):

            last = ALL_GROUPS[group][
                "cau_den"
            ]

            blocks.append(
                '<section class="group">'
                f'<h3>Bảng lựa chọn câu '
                f'{number}–{last}</h3>'
                f'<img src="groups/'
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

<title>HSK3 Đề 8 - Kiểm tra 80 câu</title>

<style>
* {
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    background: #f3f5fa;
    color: #17263e;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 1040px;
    margin: auto;
}

h2 {
    margin-top: 34px;
    padding: 12px 0;
    border-bottom: 2px solid #dbe2eb;
}

section {
    background: white;
    border: 1px solid #dbe2eb;
    border-radius: 12px;
    padding: 18px;
    margin: 14px 0;
}

section.group {
    background: #eff6ff;
}

section img {
    display: block;
    max-width: 100%;
    height: auto;
}

h3 {
    font-size: 17px;
    margin: 0 0 12px;
}

.mini {
    display: inline-block;
    margin: 7px;
    padding: 12px 18px;
    background: white;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
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
# 25. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 08 - BUOC 2")
    print("=" * 60)

    (
        source,
        pdf_path,
        old_hashes
    ) = validate_source()

    images = {}

    question_manifest = {}

    group_manifest = {}

    # ================================================
    # 26. GIU LAI HAI BANG NGHE
    # ================================================

    for name, config in (
        EXISTING_GROUPS.items()
    ):

        group_manifest[name] = {
            **config,

            "anh": f"groups/{name}.png",
        }

    with fitz.open(pdf_path) as doc:

        validate_pdf(doc)

        # ============================================
        # 27. GHI NHAN CAU 1-10
        # ============================================

        for number in range(1, 11):

            question_manifest[
                str(number)
            ] = {
                "trang_pdf": page_for(number),

                "anh": None,

                "nhom_lua_chon": (
                    group_for(number)
                ),
            }

        # ============================================
        # 28. TACH 70 ANH CAU HOI
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

            positions = positions_for(
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
                    render_png(
                        page,
                        rect
                    )
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
        # 29. TACH BON BANG DOC
        # ============================================

        print(
            "\n===== TACH 4 BANG DOC ====="
        )

        for name, config in (
            NEW_GROUPS.items()
        ):

            page = doc[
                config["trang_pdf"] - 1
            ]

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
                "trang_pdf": config["trang_pdf"],

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
    # 30. KIEM TRA SO LUONG
    # ================================================

    expected_numbers = {
        str(number)
        for number in range(1, 81)
    }

    if (
        set(question_manifest)
        != expected_numbers

        or len(question_manifest) != 80
    ):

        raise RuntimeError(
            "Manifest khong du 80 cau."
        )

    if (
        set(group_manifest)
        != set(ALL_GROUPS)
    ):

        raise RuntimeError(
            "Manifest khong du 6 bang."
        )

    # 70 anh cau hoi + 4 bang Doc moi.

    if len(images) != 74:

        raise RuntimeError(
            f"So anh moi sai: "
            f"{len(images)}/74"
        )

    # ================================================
    # 31. TAO MANIFEST JSON
    # ================================================

    manifest = {
        "cap_hsk": 3,
        "so_de": 8,
        "ma_de_goc": CODE,

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

        "dap_an_thay_the": {},
    }

    # ================================================
    # 32. TAO FILE JSON VA HTML
    # ================================================

    outputs = {
        **images,

        MANIFEST_JSON: bytes_json(
            manifest
        ),

        PREVIEW_HTML: create_preview(),
    }

    # ================================================
    # 33. BAO VE FILE CU
    # ================================================

    # Kiem tra tat ca file truoc khi ghi
    # bat ky file moi nao.

    for path, content in (
        outputs.items()
    ):

        if (
            path.exists()
            and path.read_bytes() != content
        ):

            raise RuntimeError(
                "KHONG ghi de file "
                "khac noi dung:\n"
                + str(path)
            )

    # Hai bang Nghe phai nguyen ven.

    for name, old_hash in (
        old_hashes.items()
    ):

        path = (
            GROUPS / f"{name}.png"
        )

        if sha256(path) != old_hash:

            raise RuntimeError(
                f"Bang Nghe {name} "
                "da bi thay doi."
            )

    # ================================================
    # 34. LUU ANH, JSON VA HTML
    # ================================================

    for path, content in (
        outputs.items()
    ):

        save_safe(
            path,
            content
        )

    # ================================================
    # 35. KIEM TRA SAU KHI LUU
    # ================================================

    for number in range(11, 81):

        require_file(
            QUESTIONS
            / f"cau_{number:02d}.png"
        )

    for name in ALL_GROUPS:

        require_file(
            GROUPS / f"{name}.png"
        )

    for name, old_hash in (
        old_hashes.items()
    ):

        path = (
            GROUPS / f"{name}.png"
        )

        if sha256(path) != old_hash:

            raise RuntimeError(
                f"Bang Nghe {name} "
                "khong con nguyen ven."
            )

    # ================================================
    # 36. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH HSK3 DE 08 - BUOC 2"
    )

    print("=" * 60)

    print("Ma de: H31008")
    print("PDF: 22 trang")

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
        "Khong co dap an thay the "
        "trong PDF goc"
    )

    print(f"\nJSON: {MANIFEST_JSON}")

    print(f"HTML: {PREVIEW_HTML}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
