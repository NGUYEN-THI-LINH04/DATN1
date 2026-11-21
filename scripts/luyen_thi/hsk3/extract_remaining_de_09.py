
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 09 (H31327) - BUOC 2.

- Giu nguyen 2 bang hinh Nghe cua buoc 1.
- Tach 70 anh cau 11-80 va 4 bang lua chon Doc.
- Kiem tra A/B/C, Pinyin, cau 57 va 67.
- Tao manifest va trang HTML xem truoc.

KHONG ket noi SQL Server, KHONG sua de cu.
"""

from pathlib import Path
from html import escape
import hashlib
import json
import os
import re
import unicodedata

import fitz


# =====================================================
# 1. CAU HINH DUONG DAN
# =====================================================

ROOT = Path(
    os.environ.get("MOC_HAN_ROOT", r"D:\DATN1")
)

BASE = ROOT / "scripts" / "luyen_thi"

SOURCE = (
    BASE / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 9"
)

DATA = BASE / "hsk3" / "data" / "de_09"

OUTPUT = BASE / "hsk3" / "output" / "de_09"

QUESTIONS = OUTPUT / "questions"

GROUP_DIR = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_09_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_80_cau_ung_vien.json"
)

PREVIEW_HTML = (
    OUTPUT / "kiem_tra_80_cau.html"
)

# Ma goc tren PDF, KHONG phai H31009.
CODE = "H31327"


# =====================================================
# 2. SO DO TRANG CAU HOI
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
# 3. GIOI HAN CAT CAU CUOI MOI TRANG
# =====================================================

PAGE_BOTTOM = {
    4: 741,
    5: 735,
    6: 742,

    7: 678,
    8: 532,
    9: 628,
    10: 741,

    11: 742,
    12: 754,

    13: 560,
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

def require_file(path):

    if (
        not path.is_file()
        or path.stat().st_size == 0
    ):
        raise RuntimeError(
            f"Thieu file hoac file rong: {path}"
        )

    return path


def read_json(path):

    return json.loads(
        require_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


def normalized(value):

    return unicodedata.normalize(
        "NFKC",
        str(value)
    )


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
                "Khong ghi de file "
                f"khac noi dung: {path}"
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

    for page, numbers in PAGE_QUESTIONS.items():

        if number in numbers:
            return page

    raise RuntimeError(
        f"Khong co trang PDF cho cau {number}"
    )


# =====================================================
# 9. XAC DINH NHOM LUA CHON
# =====================================================

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
# 10. KIEM TRA JSON BUOC 1
# =====================================================

def check_source():

    source = read_json(ANSWER_JSON)

    identity = (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc"),
    )

    if identity != (3, 9, CODE):
        raise RuntimeError(
            "JSON buoc 1 khong phai "
            "HSK3 De 9 H31327"
        )

    counts = tuple(
        source.get(key)

        for key in (
            "tong_cau",
            "so_cau_nghe",
            "so_cau_doc",
            "so_cau_viet",
        )
    )

    if counts != (80, 40, 30, 10):
        raise RuntimeError(
            "So cau trong JSON buoc 1 "
            "khong hop le"
        )

    answers = source.get("dap_an", {})

    expected = {
        str(n) for n in range(1, 81)
    }

    if (
        set(answers) != expected
        or any(
            not str(value).strip()
            for value in answers.values()
        )
    ):
        raise RuntimeError(
            "JSON buoc 1 thieu hoac "
            "co dap an rong"
        )

    # ================================================
    # 11. KIEM TRA DAP AN THAY THE
    # ================================================

    if source.get("dap_an_thay_the") != {}:
        raise RuntimeError(
            "De 9 co dap an thay the "
            "chua duoc xu ly"
        )

    # ================================================
    # 12. KIEM TRA CUM TU SAP XEP
    # ================================================

    tokens = source.get(
        "cum_tu_sap_xep", {}
    )

    if set(tokens) != {
        str(n) for n in range(71, 76)
    }:
        raise RuntimeError(
            "Thieu cum tu sap xep cau 71-75"
        )

    # ================================================
    # 13. KIEM TRA PDF NGUON
    # ================================================

    path_value = source.get("file_pdf")

    if not path_value:
        raise RuntimeError(
            "JSON buoc 1 thieu file_pdf"
        )

    pdf = require_file(
        Path(path_value)
    )

    if (
        pdf.parent.resolve()
        != SOURCE.resolve()
    ):
        raise RuntimeError(
            "PDF khong nam trong "
            "thu muc HSK3 DE 9"
        )

    # ================================================
    # 14. BAO VE HAI BANG NGHE
    # ================================================

    old_hashes = {
        name: sha256(
            GROUP_DIR / f"{name}.png"
        )
        for name in EXISTING_GROUPS
    }

    return source, pdf, old_hashes


# =====================================================
# 15. KIEM TRA PDF
# =====================================================

def check_pdf(doc):

    if len(doc) != 16:
        raise RuntimeError(
            "PDF H31327 phai co 16 trang; "
            f"hien co {len(doc)}"
        )

    if (
        CODE not in doc[0].get_text("text")
        or CODE not in doc[14].get_text("text")
    ):
        raise RuntimeError(
            "Sai ma de PDF, can H31327"
        )

    if (
        "答案" not in doc[14].get_text("text")
        or "书" not in doc[15].get_text("text")
    ):
        raise RuntimeError(
            "Trang 15-16 "
            "khong phai bang dap an"
        )

    total = sum(
        len(numbers)
        for numbers in PAGE_QUESTIONS.values()
    )

    if total != 70:
        raise RuntimeError(
            "So do trang khong du 70 cau"
        )


# =====================================================
# 16. TIM VI TRI TUNG SO CAU
# =====================================================

def find_positions(
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

    # ================================================
    # 17. KIEM TRA DU VA DUNG THU TU
    # ================================================

    missing = sorted(
        set(numbers) - set(found)
    )

    duplicates = sorted(
        number

        for number, points in found.items()

        if len(points) != 1
    )

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
                "sai thu tu cau"
            )

    return positions


# =====================================================
# 18. TINH TOA DO CAT TUNG CAU
# =====================================================

def crop_question(
    page,
    page_no,
    numbers,
    positions,
    index
):

    number = numbers[index]

    # Cau 76-80 co Pinyin o tren chu Han.
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

    if index < len(numbers) - 1:

        next_number = numbers[index + 1]

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
        or rect.height < 20
        or rect.width < 200
    ):
        raise RuntimeError(
            f"Cau {number} "
            f"co khung cat loi: {rect}"
        )

    words = page.get_text("words")

    # ================================================
    # 19. KIEM TRA A/B/C
    # ================================================

    if (
        21 <= number <= 40
        or 61 <= number <= 70
    ):

        found = {
            normalized(word[4]).strip()

            for word in words

            if (
                normalized(word[4]).strip()
                in "ABC"

                and len(
                    normalized(word[4]).strip()
                ) == 1

                and rect.contains(
                    fitz.Rect(word[:4])
                )
            )
        }

        if found != set("ABC"):

            missing = sorted(
                set("ABC") - found
            )

            raise RuntimeError(
                f"Cau {number} "
                f"thieu A/B/C: {missing}"
            )

    # ================================================
    # 20. KIEM TRA PINYIN CAU 76-80
    # ================================================

    if writing_pinyin:

        pinyin_words = [
            word[4]

            for word in words

            if (
                re.search(
                    r"[A-Za-z]",
                    str(word[4])
                )

                and word[1] < positions[number]

                and rect.contains(
                    fitz.Rect(word[:4])
                )
            )
        ]

        if not pinyin_words:
            raise RuntimeError(
                f"Cau {number} mat Pinyin"
            )

    # ================================================
    # 21. KIEM TRA RIENG CAU 57 VA 67
    # ================================================

    clip_text = normalized(
        page.get_text(
            "text",
            clip=rect
        )
    ).replace(" ", "")

    if number == 57:

        if (
            "下周我要去旅游" not in clip_text
            or "打算去哪儿" not in clip_text
        ):
            raise RuntimeError(
                "Anh cau 57 thieu "
                "mot trong hai dong hoi/dap"
            )

    if number == 67:

        if (
            "张" not in clip_text
            or "姓放在前面" not in clip_text
        ):
            raise RuntimeError(
                "Anh cau 67 thieu "
                "noi dung ve ho va ten"
            )

    return rect


# =====================================================
# 22. TACH BANG LUA CHON CHUNG
# =====================================================

def crop_group(
    page,
    name,
    config
):

    rect = fitz.Rect(
        config["rect"]
    )

    if not page.rect.contains(rect):
        raise RuntimeError(
            f"Bang {name} nam ngoai trang"
        )

    labels = {
        normalized(word[4]).strip()

        for word in page.get_text("words")

        if rect.contains(
            fitz.Point(
                word[0],
                word[1]
            )
        )
    }

    missing = (
        set(config["lua_chon"]) - labels
    )

    if missing:
        raise RuntimeError(
            f"Bang {name} "
            f"thieu nhan: {sorted(missing)}"
        )

    return rect


# =====================================================
# 23. XUAT ANH PNG
# =====================================================

def render_png(page, rect):

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
        "<h1>HSK3 – Đề 9 (H31327)</h1>",

        "<p>"
        "Kiểm tra hình 80 câu. "
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

        # Hien thi moi bang chung mot lan.
        group = group_for(number)

        if (
            group
            and number
            == ALL_GROUPS[group]["cau_tu"]
        ):

            last = ALL_GROUPS[group]["cau_den"]

            blocks.append(
                '<section class="group">'
                f'<h3>Bảng lựa chọn câu '
                f'{number}–{last}</h3>'
                f'<img src="groups/'
                f'{escape(group)}.png">'
                '</section>'
            )

        if number <= 10:

            blocks.append(
                '<span class="mini">'
                f'Câu {number}</span>'
            )

        else:

            filename = (
                f"cau_{number:02d}.png"
            )

            blocks.append(
                '<section>'
                f'<h3>Câu {number:02d}</h3>'
                '<img src="questions/'
                f'{filename}">'
                '</section>'
            )

    html = """
<!doctype html>
<html lang="vi">

<head>
<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>HSK3 Đề 9 - Kiểm tra 80 câu</title>

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
    max-width: 1020px;
    margin: auto;
}

h2 {
    padding: 13px 0;
    border-bottom: 2px solid #dbe2eb;
    margin-top: 34px;
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
    object-fit: contain;
}

h3 {
    font-size: 17px;
    margin: 0 0 12px;
}

.mini {
    display: inline-block;
    margin: 7px;
    padding: 12px 18px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: white;
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
    print("MOC HAN - HSK3 DE 09 - BUOC 2")
    print("MA DE GOC H31327")
    print("=" * 60)

    (
        source,
        pdf_path,
        old_hashes
    ) = check_source()

    images = {}
    questions = {}
    groups = {}

    # ================================================
    # 26. GIU NGUYEN HAI BANG NGHE
    # ================================================

    for name, config in (
        EXISTING_GROUPS.items()
    ):

        groups[name] = {
            **config,
            "anh": f"groups/{name}.png",
        }

    with fitz.open(pdf_path) as doc:

        check_pdf(doc)

        # ============================================
        # 27. GHI NHAN CAU 1-10
        # ============================================

        for number in range(1, 11):

            questions[str(number)] = {
                "trang_pdf": page_for(number),
                "anh": None,
                "nhom_lua_chon": group_for(number),
            }

        # ============================================
        # 28. TACH 70 ANH CAU 11-80
        # ============================================

        print(
            "\n===== TACH 70 ANH CAU 11-80 ====="
        )

        for page_no, numbers in (
            PAGE_QUESTIONS.items()
        ):

            page = doc[page_no - 1]

            positions = find_positions(
                page,
                numbers,
                page_no
            )

            for index, number in enumerate(
                numbers
            ):

                rect = crop_question(
                    page,
                    page_no,
                    numbers,
                    positions,
                    index
                )

                filename = (
                    f"cau_{number:02d}.png"
                )

                images[
                    QUESTIONS / filename
                ] = render_png(page, rect)

                questions[str(number)] = {
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
                f"Trang PDF {page_no}: "
                f"{len(numbers)} cau"
            )

        # ============================================
        # 29. TACH 4 BANG LUA CHON DOC
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

            rect = crop_group(
                page,
                name,
                config
            )

            images[
                GROUP_DIR / f"{name}.png"
            ] = render_png(
                page,
                rect
            )

            groups[name] = {
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
        str(n) for n in range(1, 81)
    }

    if set(questions) != expected_numbers:
        raise RuntimeError(
            "Manifest khong du 80 cau"
        )

    if (
        set(groups) != set(ALL_GROUPS)
        or len(images) != 74
    ):
        raise RuntimeError(
            "So anh/nhom sai: "
            f"anh moi {len(images)}, "
            f"nhom {len(groups)}"
        )

    # ================================================
    # 31. TAO MANIFEST JSON
    # ================================================

    manifest = {
        "cap_hsk": 3,
        "so_de": 9,
        "ma_de_goc": CODE,

        "so_trang_pdf": 16,

        "so_cau": 80,

        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        "trang_loi_thoai": [],

        "trang_dap_an": [15, 16],

        "cau_hoi": questions,

        "bang_lua_chon": groups,

        "dap_an_thay_the": (
            source["dap_an_thay_the"]
        ),
    }

    # ================================================
    # 32. TAO JSON VA HTML
    # ================================================

    outputs = {
        **images,

        MANIFEST_JSON: json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8"),

        PREVIEW_HTML: create_preview(),
    }

    # ================================================
    # 33. BAO VE FILE CU
    # ================================================

    # Kiem tra tat ca file truoc khi ghi.
    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):
            raise RuntimeError(
                "KHONG ghi de file "
                f"khac noi dung: {path}"
            )

    # Hai bang Nghe phai giu nguyen.
    for name, old_hash in (
        old_hashes.items()
    ):

        path = GROUP_DIR / f"{name}.png"

        if sha256(path) != old_hash:
            raise RuntimeError(
                f"Bang Nghe {name} da thay doi"
            )

    # ================================================
    # 34. LUU ANH, JSON VA HTML
    # ================================================

    for path, content in outputs.items():

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
            GROUP_DIR / f"{name}.png"
        )

    for name, old_hash in (
        old_hashes.items()
    ):

        path = GROUP_DIR / f"{name}.png"

        if sha256(path) != old_hash:
            raise RuntimeError(
                f"Bang Nghe {name} bi thay doi"
            )

    # ================================================
    # 36. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH HSK3 DE 09 - BUOC 2"
    )

    print("=" * 60)

    print("Ma de goc: H31327")

    print("Anh cau 11-80: 70/70")

    print(
        "Bang lua chon: 6/6 "
        "(2 Nghe + 4 Doc)"
    )

    print(
        "Cau 21-40, 61-70: A/B/C DAY DU"
    )

    print(
        "Cau 57 va 67: da kiem tra noi dung"
    )

    print(
        "Cau 76-80: Pinyin DAY DU"
    )

    print(f"\nJSON: {MANIFEST_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
