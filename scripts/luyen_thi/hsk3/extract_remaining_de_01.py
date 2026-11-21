
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 01 (H31001)

BUOC 2:
- Giu nguyen 2 bang hinh Nghe cau 1-10.
- Tach 70 anh cau hoi 11-80.
- Tao 4 bang lua chon chung phan Doc.
- Giu pinyin trong cau Viet 76-80.
- Tao JSON manifest 80 cau.
- Tao HTML kiem tra toan bo de.

KHONG thay doi SQL Server.
KHONG sua HSK1 / HSK2.
"""

from pathlib import Path
import hashlib
import json
import re
import unicodedata

import fitz


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

HSK3 = (
    ROOT / "scripts" / "luyen_thi" / "hsk3"
)

DATA = HSK3 / "data" / "de_01"
OUTPUT = HSK3 / "output" / "de_01"

QUESTIONS = OUTPUT / "questions"
GROUPS = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_01_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_80_cau_ung_vien.json"
)

PREVIEW_HTML = (
    OUTPUT / "kiem_tra_80_cau.html"
)

EXAM_CODE = "H31001"


# =====================================================
# 2. SO DO TRANG CAU 11-80
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

# Gioi han cuoi vung cau hoi.
# Khong cat vao footer cua PDF.
PAGE_BOTTOM = {
    4: 741,
    5: 735,
    6: 742,
    7: 678,
    8: 532,
    9: 628,
    10: 741,
    11: 719,
    12: 719,
    13: 545,
    14: 559,
}


# =====================================================
# 3. BANG LUA CHON CHUNG PHAN DOC
# =====================================================

# (trang_pdf, toa_do, lua_chon, cau_dau, cau_cuoi)

NEW_GROUP_RECTS = {
    "doc_41_45": (
        7,
        (75, 190, 530, 395),
        "ABCDEF",
        41,
        45,
    ),

    "doc_46_50": (
        8,
        (75, 137, 530, 307),
        "ABCDE",
        46,
        50,
    ),

    "doc_51_55": (
        9,
        (80, 158, 532, 206),
        "ABCDEF",
        51,
        55,
    ),

    "doc_56_60": (
        10,
        (80, 124, 532, 170),
        "ABCDEF",
        56,
        60,
    ),
}


# =====================================================
# 4. HAI BANG HINH NGHE DA HOAN THANH
# =====================================================

EXISTING_GROUPS = {
    "nghe_01_05": (2, "ABCDEF", 1, 5),
    "nghe_06_10": (3, "ABCDE", 6, 10),
}


# =====================================================
# 5. DAP AN CHINH THUC H31001
# =====================================================

EXPECTED_ROWS = [
    "B C E F A",
    "B C A D E",
    "× √ × √ √",
    "× √ √ × ×",
    "B C C C B",
    "C A A B C",
    "B B B C A",
    "B B B C A",
]

# Dap an 31-70 va phan Viet.
# Xay dung lai day du trong ham ben duoi.

EXPECTED_OBJECTIVE_ROWS = [
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
# 6. HAM HO TRO
# =====================================================

def check_file(path):

    if not path.is_file():
        raise RuntimeError(
            f"Khong tim thay file:\n{path}"
        )

    if path.stat().st_size == 0:
        raise RuntimeError(
            f"File rong: {path}"
        )


def safe_write(path, content):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if path.exists():

        if path.read_bytes() != content:
            raise RuntimeError(
                "File da ton tai va khac noi dung."
                "\nKhong ghi de:\n"
                + str(path)
            )

        return

    path.write_bytes(content)


def sha256(path):

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def normalize(value):

    return unicodedata.normalize(
        "NFKC",
        str(value)
    )


# =====================================================
# 7. KIEM TRA DAP AN NGUON
# =====================================================

def expected_answers():

    result = {}

    for row_index, row in enumerate(
        EXPECTED_OBJECTIVE_ROWS
    ):

        values = row.split()

        if len(values) != 5:
            raise RuntimeError(
                "Bang dap an mau sai."
            )

        for offset, answer in enumerate(values):

            number = (
                row_index * 5 + offset + 1
            )

            result[number] = answer

    result.update(EXPECTED_WRITING)

    if set(result) != set(range(1, 81)):
        raise RuntimeError(
            "Bang dap an mau thieu cau."
        )

    return result


def read_sources():

    check_file(ANSWER_JSON)

    info = json.loads(
        ANSWER_JSON.read_text(
            encoding="utf-8-sig"
        )
    )

    if (
        info.get("cap_hsk") != 3
        or info.get("so_de") != 1
    ):
        raise RuntimeError(
            "JSON khong phai HSK3 De 1."
        )

    if info.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "Ma de khong phai H31001."
        )

    if (
        info.get("tong_cau") != 80
        or info.get("so_cau_viet") != 10
    ):
        raise RuntimeError(
            "So cau trong JSON khong dung."
        )

    answers = info.get("dap_an", {})

    if set(answers) != {
        str(n) for n in range(1, 81)
    }:
        raise RuntimeError(
            "JSON khong du 80 dap an."
        )

    expected = expected_answers()

    for number in range(1, 81):

        actual = answers[str(number)].strip()

        if actual != expected[number]:
            raise RuntimeError(
                f"Dap an cau {number} "
                "khong khop PDF goc."
            )

    pdf_value = info.get("file_pdf")

    if not pdf_value:
        raise RuntimeError(
            "JSON thieu duong dan PDF."
        )

    pdf_path = Path(pdf_value)

    check_file(pdf_path)

    # Bao ve 2 bang hinh Nghe.
    initial_hashes = {}

    for name in EXISTING_GROUPS:

        path = GROUPS / f"{name}.png"

        check_file(path)

        initial_hashes[name] = sha256(path)

    return (
        pdf_path,
        answers,
        initial_hashes,
    )


# =====================================================
# 8. KIEM TRA PDF
# =====================================================

def pdf_valid(doc):

    if len(doc) != 22:
        raise RuntimeError(
            f"PDF phai co 22 trang, "
            f"nhung co {len(doc)}."
        )

    for number in (1, 21, 22):

        text = re.sub(
            r"\s+",
            "",
            normalize(
                doc[number - 1].get_text("text")
            )
        )

        if EXAM_CODE not in text:
            raise RuntimeError(
                f"Trang {number} "
                f"khong co ma {EXAM_CODE}."
            )

    transcript = normalize(
        doc[14].get_text("text")
    )

    if "听力材料" not in transcript:
        raise RuntimeError(
            "Trang 15 khong phai loi thoai."
        )

    answer_text = normalize(
        doc[20].get_text("text")
    )

    if "答案" not in answer_text:
        raise RuntimeError(
            "Trang 21 khong phai bang dap an."
        )

    writing_text = normalize(
        doc[21].get_text("text")
    )

    if "书" not in writing_text:
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


# =====================================================
# 9. TIM VI TRI SO CAU
# =====================================================

def question_positions(page, numbers, page_no):

    found = {}

    for block in page.get_text("dict")["blocks"]:

        for line in block.get("lines", []):

            text = "".join(
                span["text"]
                for span in line["spans"]
            ).strip()

            match = re.match(
                r"^(\d{1,2})\s*[.．、]",
                text
            )

            if not match:
                continue

            number = int(match.group(1))

            x0, y0, _, _ = line["bbox"]

            # So cau phai o cot ben trai,
            # khong phai so trong noi dung.
            if (
                number in numbers
                and x0 < 125
                and y0 < 760
            ):

                found.setdefault(
                    number,
                    []
                ).append(float(y0))

    # Moi cau phai co dung mot vi tri.
    if (
        set(found) != set(numbers)
        or any(
            len(found[number]) != 1
            for number in found
        )
    ):
        raise RuntimeError(
            f"Trang {page_no}: khong tim "
            "duoc duy nhat vi tri moi cau.\n"
            f"Tim thay: {found}"
        )

    positions = {
        number: found[number][0]
        for number in numbers
    }

    for a, b in zip(
        numbers,
        numbers[1:]
    ):

        if positions[a] >= positions[b]:
            raise RuntimeError(
                f"Thu tu cau trang {page_no} sai."
            )

    return positions


# =====================================================
# 10. TINH VUNG CAT TUNG CAU
# =====================================================

def rect_for_question(
    page,
    page_no,
    numbers,
    positions,
    index
):

    number = numbers[index]

    # Cau 76-80 co Pinyin nam phia tren.
    is_writing_2 = 76 <= number <= 80

    if is_writing_2:
        top_padding = 26
        next_padding = 27
    else:
        top_padding = 11
        next_padding = 10

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
            f"Cau {number} co khung cat sai: "
            f"{rect}"
        )

    return rect


# =====================================================
# 11. XUAT ANH PNG
# =====================================================

def render_png(page, rect):

    pix = page.get_pixmap(
        matrix=fitz.Matrix(2.5, 2.5),
        clip=rect,
        alpha=False
    )

    return pix.tobytes("png")


# =====================================================
# 12. KIEM TRA NHAN A-F
# =====================================================

def validate_group_labels(
    page,
    rect,
    labels
):

    found = set()

    for word in page.get_text("words"):

        x0, y0, _, _, word_text = word[:5]

        text = normalize(
            word_text
        ).strip()

        if (
            text in labels
            and rect.contains(
                fitz.Point(x0, y0)
            )
        ):
            found.add(text)

    if found != set(labels):
        raise RuntimeError(
            f"Bang lua chon thieu nhan.\n"
            f"Can: {labels}\n"
            f"Tim thay: {sorted(found)}"
        )


# =====================================================
# 13. XAC DINH BANG CHUNG CUA CAU
# =====================================================

def group_for_question(number):

    for name, (
        _page,
        _labels,
        first,
        last
    ) in EXISTING_GROUPS.items():

        if first <= number <= last:
            return name

    for name, (
        _page,
        _rect,
        _labels,
        first,
        last
    ) in NEW_GROUP_RECTS.items():

        if first <= number <= last:
            return name

    return None


# =====================================================
# 14. TAO HTML KIEM TRA 80 CAU
# =====================================================

def make_html():

    blocks = []

    for number in range(1, 81):

        if number == 1:
            blocks.append(
                '<h2 class="part">'
                'I. Nghe (1–40)</h2>'
            )

        elif number == 41:
            blocks.append(
                '<h2 class="part">'
                'II. Đọc (41–70)</h2>'
            )

        elif number == 71:
            blocks.append(
                '<h2 class="part">'
                'III. Viết (71–80)</h2>'
            )

        # Chen bang lua chon chung.
        if number in (1, 6, 41, 46, 51, 56):

            group = group_for_question(number)

            if number == 1:
                last = 5

            elif number == 6:
                last = 10

            else:
                last = number + 4

            blocks.append(
                f'<div class="group">'
                f'<h3>Bảng lựa chọn: '
                f'câu {number}–{last}</h3>'
                f'<img '
                f'src="groups/{group}.png" '
                f'alt="{group}">'
                f'</div>'
            )

        # Cau 1-10 khong co anh rieng.
        if number <= 10:

            blocks.append(
                f'<div class="mini">'
                f'Câu {number}'
                f'</div>'
            )

        else:

            blocks.append(
                f'<div class="question">'
                f'<h3>Câu {number:02d}</h3>'
                f'<img '
                f'src="questions/cau_{number:02d}.png" '
                f'alt="Câu {number}">'
                f'</div>'
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

<title>HSK3 Đề 1 - H31001 - 80 câu</title>

<style>
* {
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    color: #18263d;
    background: #f4f6fa;
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

<h1>HSK3 – Đề 1 (H31001)</h1>

<p class="hint">
Xem trước 80 câu và các bảng lựa chọn chung.
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
    print("MOC HAN - HSK3 DE 01")
    print("TACH CAU 11-80 - H31001")
    print("=" * 60)

    (
        pdf_path,
        answers,
        original_group_hashes
    ) = read_sources()

    image_bytes = {}

    question_manifest = {}
    group_manifest = {}

    # ================================================
    # 16. GHI NHAN 2 BANG HINH DA CO
    # ================================================

    for name, (
        page_no,
        labels,
        first,
        last
    ) in EXISTING_GROUPS.items():

        group_manifest[name] = {
            "trang_pdf": page_no,
            "anh": f"groups/{name}.png",
            "lua_chon": labels,
            "cau_tu": first,
            "cau_den": last,
        }

    with fitz.open(pdf_path) as doc:

        pdf_valid(doc)

        # ============================================
        # 17. GHI NHAN CAU 1-10
        # ============================================

        for number in range(1, 11):

            group = group_for_question(
                number
            )

            question_manifest[str(number)] = {
                "trang_pdf": (
                    2 if number <= 5 else 3
                ),
                "anh": None,
                "nhom_lua_chon": group,
            }

        # ============================================
        # 18. TACH 70 CAU 11-80
        # ============================================

        print(
            "\n===== TACH 70 CAU (11-80) ====="
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

                rect = rect_for_question(
                    page,
                    page_no,
                    numbers,
                    positions,
                    index
                )

                destination = (
                    QUESTIONS
                    / f"cau_{number:02d}.png"
                )

                image_bytes[destination] = (
                    render_png(page, rect)
                )

                question_manifest[str(number)] = {
                    "trang_pdf": page_no,

                    "anh": (
                        f"questions/"
                        f"cau_{number:02d}.png"
                    ),

                    "nhom_lua_chon": (
                        group_for_question(number)
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
        # 19. TACH 4 BANG LUA CHON DOC
        # ============================================

        print(
            "\n===== TACH 4 BANG LUA CHON DOC ====="
        )

        for name, (
            page_no,
            coords,
            labels,
            first,
            last
        ) in NEW_GROUP_RECTS.items():

            page = doc[page_no - 1]

            rect = (
                fitz.Rect(coords) & page.rect
            )

            validate_group_labels(
                page,
                rect,
                labels
            )

            destination = (
                GROUPS / f"{name}.png"
            )

            image_bytes[destination] = (
                render_png(page, rect)
            )

            group_manifest[name] = {
                "trang_pdf": page_no,
                "anh": f"groups/{name}.png",
                "lua_chon": labels,
                "cau_tu": first,
                "cau_den": last,
                "toa_do": list(coords),
            }

            print(
                f"{name}: trang {page_no}, "
                f"{len(labels)} lua chon"
            )

    # ================================================
    # 20. KIEM TRA KET QUA TRUOC KHI GHI
    # ================================================

    if len(question_manifest) != 80:
        raise RuntimeError(
            "Manifest khong du 80 cau."
        )

    if len(group_manifest) != 6:
        raise RuntimeError(
            "Manifest khong du 6 bang."
        )

    # 70 anh cau hoi + 4 bang Doc.
    if len(image_bytes) != 74:
        raise RuntimeError(
            f"So anh can la 74, "
            f"hien tai: {len(image_bytes)}"
        )

    if set(question_manifest) != {
        str(number)
        for number in range(1, 81)
    }:
        raise RuntimeError(
            "So thu tu 80 cau khong day du."
        )

    # ================================================
    # 21. TAO MANIFEST JSON
    # ================================================

    manifest = {
        "cap_hsk": 3,
        "so_de": 1,
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

    # ================================================
    # 22. TAO JSON VA HTML
    # ================================================

    output_files = dict(image_bytes)

    output_files[MANIFEST_JSON] = (
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8")
    )

    output_files[PREVIEW_HTML] = make_html()

    # ================================================
    # 23. BAO VE FILE CU
    # ================================================

    # Kiem tra tat ca file truoc khi ghi.
    for path, content in output_files.items():

        if path.exists():

            if path.read_bytes() != content:
                raise RuntimeError(
                    "File da ton tai "
                    "voi noi dung khac.\n"
                    "Khong ghi de:\n"
                    + str(path)
                )

    # Dam bao hai bang hinh Nghe khong thay doi.
    for name, old_hash in (
        original_group_hashes.items()
    ):

        path = GROUPS / f"{name}.png"

        if sha256(path) != old_hash:
            raise RuntimeError(
                f"Bang hinh Nghe {name} "
                "da bi thay doi."
            )

    # ================================================
    # 24. LUU ANH, JSON VA HTML
    # ================================================

    for path, content in output_files.items():

        safe_write(
            path,
            content
        )

    # ================================================
    # 25. KIEM TRA SAU KHI LUU
    # ================================================

    for number in range(11, 81):

        check_file(
            QUESTIONS
            / f"cau_{number:02d}.png"
        )

    for name in group_manifest:

        check_file(
            GROUPS / f"{name}.png"
        )

    for name, old_hash in (
        original_group_hashes.items()
    ):

        path = GROUPS / f"{name}.png"

        if sha256(path) != old_hash:
            raise RuntimeError(
                f"Bang hinh {name} "
                "khong con nguyen ven."
            )

    # ================================================
    # 26. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH HSK3 DE 01 - BUOC 2")
    print("=" * 60)

    print("Ma de: H31001")
    print("Dap an tu buoc 1: 80/80")
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
        "Viet 71-80: da tach "
        "ca Pinyin va cho trong"
    )

    print(f"JSON: {MANIFEST_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
