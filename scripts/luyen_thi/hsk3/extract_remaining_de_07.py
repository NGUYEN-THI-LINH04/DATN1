
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 07 (H31007) - BUOC 2.

- Giu nguyen 2 bang hinh Nghe cau 1-10.
- Tach 70 anh cau 11-80.
- Tach 4 bang lua chon chung phan Doc.
- Kiem tra A/B/C va Pinyin.
- Tao manifest JSON va HTML kiem tra 80 cau.
- Giu canh bao cau 72.
- Giu hai dap an cau 77: 元 / 圆.

KHONG ket noi SQL Server.
KHONG thay doi cac de thi cu.
"""

from pathlib import Path
from html import escape
import hashlib
import json
import re

import fitz


# =====================================================
# 1. CAU HINH DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "luyen_thi"

SOURCE = (
    BASE / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 7"
)

DATA = BASE / "hsk3" / "data" / "de_07"

OUTPUT = BASE / "hsk3" / "output" / "de_07"

QUESTION_DIR = OUTPUT / "questions"

GROUP_DIR = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_07_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_80_cau_ung_vien.json"
)

PREVIEW_HTML = (
    OUTPUT / "kiem_tra_80_cau.html"
)

CODE = "H31007"


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
# 3. GIOI HAN VUNG CAT CUOI TRANG
# =====================================================

PAGE_BOTTOM = {
    4: 741,
    5: 735,
    6: 742,

    7: 678,
    8: 532,
    9: 628,
    10: 741,

    # Cau 64 giu du A/B/C.
    11: 742,

    # Cau 70 giu du A/B/C.
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
            f"File khong ton tai hoac rong: {path}"
        )

    return path


def read_json(path):

    return json.loads(
        require_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


def to_bytes(obj):

    return json.dumps(
        obj,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")


def sha256(path):

    return hashlib.sha256(
        require_file(path).read_bytes()
    ).hexdigest()


def safe_write(path, content):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if path.exists():

        if path.read_bytes() != content:
            raise RuntimeError(
                "KHONG ghi de file "
                f"khac noi dung: {path}"
            )

        return

    path.write_bytes(content)


# =====================================================
# 7. XAC DINH TRANG PDF CUA CAU HOI
# =====================================================

def page_for(number):

    if 1 <= number <= 5:
        return 2

    if 6 <= number <= 10:
        return 3

    for page, numbers in PAGE_QUESTIONS.items():

        if number in numbers:
            return page

    raise RuntimeError(
        f"Khong co trang cho cau {number}"
    )


# =====================================================
# 8. XAC DINH NHOM LUA CHON
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
# 9. KIEM TRA JSON BUOC 1
# =====================================================

def validate_source():

    source = read_json(ANSWER_JSON)

    identity = (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc"),
    )

    if identity != (3, 7, CODE):
        raise RuntimeError(
            "JSON buoc 1 khong phai "
            "HSK3 De 7."
        )

    counts = (
        source.get("tong_cau"),
        source.get("so_cau_nghe"),
        source.get("so_cau_doc"),
        source.get("so_cau_viet"),
    )

    if counts != (80, 40, 30, 10):
        raise RuntimeError(
            "So cau trong JSON buoc 1 sai."
        )

    answers = source.get("dap_an", {})

    expected_numbers = {
        str(number)
        for number in range(1, 81)
    }

    if set(answers) != expected_numbers:
        raise RuntimeError(
            "JSON buoc 1 thieu 80 dap an."
        )

    # ================================================
    # 10. GIU DAP AN THAY THE CAU 77
    # ================================================

    alternatives = source.get(
        "dap_an_thay_the"
    )

    if (
        alternatives != {"77": ["圆"]}
        or answers.get("77") != "元"
    ):
        raise RuntimeError(
            "Thieu hoac sai dap an "
            "thay the cau 77."
        )

    # ================================================
    # 11. GIU CANH BAO CAU 72
    # ================================================

    issues = source.get(
        "can_ra_soat", []
    )

    if not isinstance(issues, list):
        raise RuntimeError(
            "Danh sach can_ra_soat khong hop le."
        )

    if not any(
        item.get("so_cau") == 72
        for item in issues
    ):
        raise RuntimeError(
            "Thieu canh bao cau 72."
        )

    # ================================================
    # 12. KIEM TRA HAI PDF NGUON
    # ================================================

    exam_pdf = require_file(
        Path(source.get("file_pdf", ""))
    )

    answer_pdf = require_file(
        Path(source.get("file_dap_an", ""))
    )

    if (
        exam_pdf.parent.resolve()
        != SOURCE.resolve()
    ):
        raise RuntimeError(
            "PDF de khong thuoc HSK3 De 7."
        )

    if (
        answer_pdf.parent.resolve()
        != SOURCE.resolve()
    ):
        raise RuntimeError(
            "PDF dap an khong thuoc HSK3 De 7."
        )

    # ================================================
    # 13. BAO VE HAI BANG NGHE
    # ================================================

    hashes = {}

    for name in EXISTING_GROUPS:

        path = GROUP_DIR / f"{name}.png"

        hashes[name] = sha256(path)

    return (
        exam_pdf,
        answer_pdf,
        source,
        hashes,
    )


# =====================================================
# 14. KIEM TRA PDF
# =====================================================

def validate_pdf(doc, answer_doc):

    if len(doc) != 14:
        raise RuntimeError(
            "PDF De 7 phai co 14 trang."
        )

    if len(answer_doc) != 2:
        raise RuntimeError(
            "PDF dap an phai co 2 trang."
        )

    if CODE not in doc[0].get_text("text"):
        raise RuntimeError(
            "PDF de khong phai H31007."
        )

    if CODE not in answer_doc[0].get_text(
        "text"
    ):
        raise RuntimeError(
            "PDF dap an khong phai H31007."
        )

    total = sum(
        len(numbers)
        for numbers in PAGE_QUESTIONS.values()
    )

    if total != 70:
        raise RuntimeError(
            "So do trang khong du "
            "70 cau 11-80."
        )


# =====================================================
# 15. TIM VI TRI SO CAU
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

    # Moi cau phai co mot vi tri duy nhat.
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
            f"Trang {page_no} nhan dien "
            "sai so cau.\n"
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
                f"Trang {page_no} "
                "co thu tu cau sai."
            )

    return positions


# =====================================================
# 16. TINH TOA DO CAT ANH TUNG CAU
# =====================================================

def crop_question(
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
            f"Khung cat cau {number} sai: {rect}"
        )

    words = page.get_text("words")

    # ================================================
    # 17. KIEM TRA A/B/C
    # ================================================

    if (
        21 <= number <= 40
        or 61 <= number <= 70
    ):

        labels = {
            str(word[4]).strip()

            for word in words

            if (
                str(word[4]).strip()
                in ("A", "B", "C")

                and rect.contains(
                    fitz.Rect(word[:4])
                )
            )
        }

        if labels != set("ABC"):
            raise RuntimeError(
                f"Cau {number} bi mat "
                "A/B/C.\n"
                f"Tim thay: {sorted(labels)}"
            )

    # ================================================
    # 18. KIEM TRA PINYIN CAU 76-80
    # ================================================

    if writing_pinyin:

        found_pinyin = [
            word[4]

            for word in words

            if (
                re.search(
                    r"[a-zA-Z]",
                    str(word[4])
                )

                and word[1] < positions[number]

                and rect.contains(
                    fitz.Rect(word[:4])
                )
            )
        ]

        if not found_pinyin:
            raise RuntimeError(
                f"Cau {number} "
                "co the bi mat Pinyin."
            )

    return rect


# =====================================================
# 19. CAT BANG LUA CHON PHAN DOC
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
            f"Toa do bang {name} sai."
        )

    words = page.get_text("words")

    labels = {
        str(word[4]).strip()

        for word in words

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
            f"Bang {name} thieu nhan: "
            f"{sorted(missing)}"
        )

    return rect


# =====================================================
# 20. XUAT ANH PNG
# =====================================================

def png(page, rect):

    pix = page.get_pixmap(
        matrix=fitz.Matrix(2.5, 2.5),
        clip=rect,
        alpha=False
    )

    return pix.tobytes("png")


# =====================================================
# 21. TAO HTML KIEM TRA 80 CAU
# =====================================================

def preview_html():

    blocks = [
        "<h1>HSK3 – Đề 7 (H31007)</h1>",

        "<p>"
        "Kiểm tra hình 80 câu. "
        "Không hiển thị đáp án. "
        "Chưa nhập SQL Server."
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

<title>HSK3 Đề 7 - Kiểm tra 80 câu</title>

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
# 22. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 07 - BUOC 2")
    print("=" * 60)

    (
        exam_path,
        answer_path,
        source,
        old_hashes
    ) = validate_source()

    images = {}
    questions = {}
    groups = {}

    # ================================================
    # 23. GIU HAI BANG NGHE DA CO
    # ================================================

    for name, config in (
        EXISTING_GROUPS.items()
    ):

        groups[name] = {
            **config,
            "anh": f"groups/{name}.png",
        }

    with (
        fitz.open(exam_path) as doc,
        fitz.open(answer_path) as answer_doc
    ):

        validate_pdf(
            doc,
            answer_doc
        )

        # ============================================
        # 24. GHI NHAN CAU 1-10
        # ============================================

        for number in range(1, 11):

            questions[str(number)] = {
                "trang_pdf": page_for(number),
                "anh": None,
                "nhom_lua_chon": group_for(number),
            }

        # ============================================
        # 25. TACH 70 CAU 11-80
        # ============================================

        print("\n===== TACH ANH 11-80 =====")

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

                destination = (
                    QUESTION_DIR / filename
                )

                images[destination] = (
                    png(page, rect)
                )

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
        # 26. TACH BON BANG DOC
        # ============================================

        print("\n===== TACH BANG DOC =====")

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

            destination = (
                GROUP_DIR / f"{name}.png"
            )

            images[destination] = (
                png(page, rect)
            )

            groups[name] = {
                "trang_pdf": config["trang_pdf"],

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
    # 27. KIEM TRA SO LUONG
    # ================================================

    expected_numbers = {
        str(number)
        for number in range(1, 81)
    }

    if (
        len(questions) != 80
        or set(questions) != expected_numbers
    ):
        raise RuntimeError(
            "Manifest khong du 80 cau."
        )

    if set(groups) != set(ALL_GROUPS):
        raise RuntimeError(
            "Manifest khong du 6 bang."
        )

    # 70 anh cau + 4 bang Doc.
    if len(images) != 74:
        raise RuntimeError(
            f"So anh moi sai: "
            f"{len(images)}/74"
        )

    # ================================================
    # 28. TAO MANIFEST JSON
    # ================================================

    manifest = {
        "cap_hsk": 3,
        "so_de": 7,
        "ma_de_goc": CODE,

        "so_trang_pdf": 14,
        "so_trang_pdf_dap_an": 2,

        "so_cau": 80,
        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        "trang_loi_thoai": [],

        # Thuoc PDF dap an rieng.
        "trang_dap_an": [1, 2],

        "cau_hoi": questions,

        "bang_lua_chon": groups,

        # Hai dap an hop le cau 77.
        "dap_an_thay_the": (
            source["dap_an_thay_the"]
        ),

        # Bao toan canh bao cau 72.
        "can_ra_soat": (
            source["can_ra_soat"]
        ),
    }

    # ================================================
    # 29. TAO JSON VA HTML
    # ================================================

    outputs = {
        **images,

        MANIFEST_JSON: to_bytes(manifest),

        PREVIEW_HTML: preview_html(),
    }

    # ================================================
    # 30. BAO VE FILE CU
    # ================================================

    # Kiem tra tat ca file truoc khi ghi.
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

    # Hai bang Nghe phai giu nguyen.
    for name, old_hash in old_hashes.items():

        path = GROUP_DIR / f"{name}.png"

        if sha256(path) != old_hash:
            raise RuntimeError(
                f"Bang Nghe {name} "
                "da bi thay doi."
            )

    # ================================================
    # 31. LUU ANH, JSON VA HTML
    # ================================================

    for path, content in outputs.items():

        safe_write(
            path,
            content
        )

    # ================================================
    # 32. KIEM TRA SAU KHI LUU
    # ================================================

    for number in range(11, 81):

        require_file(
            QUESTION_DIR
            / f"cau_{number:02d}.png"
        )

    for name in ALL_GROUPS:

        require_file(
            GROUP_DIR / f"{name}.png"
        )

    for name, old_hash in old_hashes.items():

        path = GROUP_DIR / f"{name}.png"

        if sha256(path) != old_hash:
            raise RuntimeError(
                f"Bang Nghe {name} "
                "khong con nguyen ven."
            )

    # ================================================
    # 33. KET QUA
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH HSK3 DE 07 - BUOC 2")
    print("=" * 60)

    print("Ma de: H31007")
    print("PDF de: 14 trang")
    print("PDF dap an: 2 trang")

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
        "Cau 77: giu 2 dap an 元 / 圆"
    )

    print(
        "Cau 72: GIU CANH BAO "
        "DE VA DAP AN KHONG KHOP"
    )

    print(f"\nJSON: {MANIFEST_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
