
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK4 DE 01 (H41001) - BUOC 1

- Kiem tra PDF 24 trang va MP3.
- Doc 85 dap an Nghe/Doc.
- Doc 10 dap an sap xep.
- Luu dap an thay the.
- Luu 5 dap an tham khao Viet mo.
- Xuat JSON va HTML kiem tra PDF.

KHONG ket noi SQL Server.
KHONG sua cac de thi cu.
KHONG hien dap an trong HTML.
"""

from pathlib import Path
from html import escape
import json
import re
import unicodedata

import fitz


# =====================================================
# 1. CAU HINH
# =====================================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "luyen_thi"

SOURCE = BASE / "source" / "De_HSK" / "HSK4"

DATA = BASE / "hsk4" / "data" / "de_01"

OUTPUT = BASE / "hsk4" / "output" / "de_01"

PREVIEW_DIR = OUTPUT / "preview_pages"

PDF_FILE = SOURCE / "H41001.pdf"

MP3_FILE = SOURCE / "H41001.mp3"

JSON_FILE = DATA / "de_01_dap_an.json"

HTML_FILE = OUTPUT / "kiem_tra_buoc_1.html"

CODE = "H41001"


# =====================================================
# 2. TU CHO SAN O CAU 96-100
# =====================================================

# Day la tu bat buoc su dung khi dat cau.
# KHONG phai dap an duy nhat.

WRITING_WORDS = {
    96: "日记",
    97: "尝",
    98: "破",
    99: "凉快",
    100: "活泼",
}

# Trang PDF danh so tu 1.
PREVIEW_PAGES = [7, 8, 15, 16]


# =====================================================
# 3. HAM HO TRO
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


def normalized(text):

    return unicodedata.normalize(
        "NFKC",
        str(text)
    )


# =====================================================
# 4. TACH DAP AN THEO SO CAU
# =====================================================

def split_numbered_answers(
    page_text,
    first,
    last
):

    """
    Tach noi dung sau cac nhan:
    1. ... 85.
    86. ... 100.

    Giu nguyen dau cau tieng Trung.
    """

    text = str(page_text)

    pattern = re.compile(
        r"(?<!\d)(\d{1,3})\s*[.．、]\s*"
    )

    hits = [
        (int(match.group(1)), match)

        for match in pattern.finditer(text)

        if (
            first <= int(match.group(1)) <= last
        )
    ]

    found = {}

    for index, (number, match) in enumerate(hits):

        if number in found:

            raise RuntimeError(
                f"Trung nhan cau {number} "
                "trong trang dap an."
            )

        if index + 1 < len(hits):

            stop = hits[index + 1][1].start()

        else:
            stop = len(text)

        found[number] = (
            text[match.end():stop].strip()
        )

    expected = set(
        range(first, last + 1)
    )

    if set(found) != expected:

        missing = sorted(
            expected - set(found)
        )

        raise RuntimeError(
            f"Khong doc du dap an "
            f"{first}-{last}.\n"
            f"Thieu: {missing}\n"
            "Can kiem tra lai trang PDF."
        )

    return found


# =====================================================
# 5. DOC 85 DAP AN NGHE/DOC
# =====================================================

def extract_objective(page_text):

    blocks = split_numbered_answers(
        page_text,
        1,
        85
    )

    result = {}

    for number, raw in blocks.items():

        # Cho phep BAC hoac B A C.
        match = re.match(
            r"^\s*([A-F√×](?:\s*[A-F]){0,2})",
            raw
        )

        if not match:

            raise RuntimeError(
                f"Khong doc duoc dap an "
                f"cau {number}: {raw[:80]!r}"
            )

        answer = re.sub(
            r"\s+",
            "",
            match.group(1)
        )

        # ============================================
        # 6. KIEM TRA TUNG DANG CAU
        # ============================================

        if number <= 10:

            valid = answer in ("√", "×")

        elif 56 <= number <= 65:

            valid = (
                len(answer) == 3
                and set(answer) == set("ABC")
            )

        elif 46 <= number <= 55:

            valid = (
                len(answer) == 1
                and answer in "ABCDEF"
            )

        else:

            valid = (
                len(answer) == 1
                and answer in "ABCD"
            )

        if not valid:

            raise RuntimeError(
                f"Cau {number} "
                f"sai dang dap an: {answer}"
            )

        result[number] = answer

    return result


# =====================================================
# 7. DOC 15 DAP AN VIET
# =====================================================

def extract_writing(page_text):

    blocks = split_numbered_answers(
        page_text,
        86,
        100
    )

    primary = {}
    alternatives = {}
    references = {}

    for number in range(86, 101):

        raw = blocks[number]

        # Cau 95: bo tieu de phan 2.
        if number == 95:

            raw = re.split(
                r"第\s*二\s*部\s*分",
                raw
            )[0]

        # Cau 100: bo footer trang.
        if number == 100:

            raw = re.split(
                r"H41001\s*[-–]\s*23",
                raw
            )[0]

        # Dap an cach nhau bang /.
        variants = [
            value.strip()

            for value in re.split(
                r"\s*[/／]\s*",
                raw
            )

            if value.strip()
        ]

        if not variants:

            raise RuntimeError(
                f"Khong doc duoc "
                f"dap an Viet cau {number}."
            )

        # ============================================
        # 8. CAU 86-95: SAP XEP
        # ============================================

        if number <= 95:

            primary[number] = variants[0]

            if len(variants) > 1:

                alternatives[number] = (
                    variants[1:]
                )

        # ============================================
        # 9. CAU 96-100: VIET CAU MO
        # ============================================

        else:

            references[number] = variants

    # PDF H41001 ghi nhieu dap an
    # cho cau 86, 91 va 95.
    for number in (86, 91, 95):

        if not alternatives.get(number):

            raise RuntimeError(
                f"Cau {number} thieu "
                "dap an thay the."
            )

    return (
        primary,
        alternatives,
        references
    )


# =====================================================
# 10. KIEM TRA BO CUC PDF
# =====================================================


# =====================================================
# 10. KIEM TRA BO CUC PDF HSK4 H41001
# =====================================================

def verify_pdf(doc):

    if len(doc) != 24:
        raise RuntimeError(
            "PDF H41001 phai co 24 trang. "
            f"Hien co: {len(doc)}"
        )

    # Kiem tra ma de goc.
    cover = doc[0].get_text("text")

    if CODE not in cover:
        raise RuntimeError(
            "PDF khong dung ma de H41001."
        )

    # Loai bo khoang trang khi doi chieu
    # vi PDF co the tach '听 力' va '书 写'.
    def page_text(page_no):
        text = normalized(
            doc[page_no - 1].get_text("text")
        )

        return re.sub(r"\s+", "", text)

    # (so trang PDF, cac noi dung bat buoc)
    checks = [
        (2, ["第一部分", "判断对错"]),
        (3, ["第二部分", "11"]),
        (5, ["第三部分", "26"]),

        (7, ["第一部分", "选词填空"]),
        (8, ["选词填空", "51"]),
        (9, ["第二部分", "排列顺序"]),
        (11, ["第三部分", "66"]),

        (15, ["第一部分", "完成句子"]),
        (16, ["第二部分", "看图"]),

        (17, ["听力材料"]),

        (23, ["答案", "听力"]),
        (24, ["书写", "86"]),
    ]

    # Kiem tra tung trang.
    for page_no, required in checks:

        text = page_text(page_no)

        missing = [
            value
            for value in required
            if value not in text
        ]

        if missing:
            raise RuntimeError(
                f"Trang {page_no} khong dung bo cuc. "
                f"Thieu: {missing}"
            )

    # Kiem tra phan Viet mo 96-100.
    writing_text = page_text(16)

    for number, word in WRITING_WORDS.items():

        pattern = rf"(?<!\d){number}[.．、]"

        if (
            not re.search(pattern, writing_text)
            or word not in writing_text
        ):
            raise RuntimeError(
                f"Trang 16 thieu cau {number} "
                f"hoac tu {word}."
            )

    print("\n===== KIEM TRA BO CUC PDF =====")

    print("PDF: 24 trang")

    print("Nghe: trang 2-6, cau 1-45")
    print("Doc: trang 7-14, cau 46-85")
    print("Viet: trang 15-16, cau 86-100")

    print("Loi thoai: trang 17-22")
    print("Dap an: trang 23-24")

    print("Bo cuc PDF: DAT")

    # ================================================
    # 11. KIEM TRA TU CAU 96-100
    # ============================================

    writing_text = normalized(
        doc[15].get_text("text")
    )

    for number, word in (
        WRITING_WORDS.items()
    ):

        has_number = re.search(
            rf"(?<!\d){number}\s*[.．、]",
            writing_text
        )

        if (
            word not in writing_text
            or not has_number
        ):

            raise RuntimeError(
                f"Trang 16 thieu cau "
                f"{number} hoac tu {word}."
            )


# =====================================================
# 12. XAC DINH DANG CAU HOI
# =====================================================

def question_kind(number):

    if number <= 10:
        return "dung_sai"

    if number <= 45:
        return "chon_mot"

    if number <= 55:
        return "ghep_lua_chon"

    if number <= 65:
        return "sap_xep_abc"

    if number <= 85:
        return "chon_mot"

    if number <= 95:
        return "sap_xep"

    return "viet_cau_theo_tranh"


# =====================================================
# 13. TAO HTML XEM TRUOC
# =====================================================

def preview_html():

    items = [
        (
            7,
            "Đọc – Bảng lựa chọn câu 46–50"
        ),
        (
            8,
            "Đọc – Bảng lựa chọn câu 51–55"
        ),
        (
            15,
            "Viết – Sắp xếp câu 86–95"
        ),
        (
            16,
            "Viết – Nhìn hình đặt câu 96–100"
        ),
    ]

    sections = "\n".join(
        (
            "<section>"
            f"<h2>{escape(title)}</h2>"
            '<img src="preview_pages/'
            f'trang_{page:02d}.png" '
            f'alt="Trang PDF {page}">'
            "</section>"
        )

        for page, title in items
    )

    template = """
<!doctype html>
<html lang="vi">

<head>
<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>HSK4 Đề 1 - Kiểm tra PDF</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    background: #f4f6fa;
    color: #1d2b45;
    font-family: Arial, sans-serif;
}

main {
    max-width: 1000px;
    margin: auto;
}

section {
    background: white;
    border: 1px solid #dce3ed;
    border-radius: 12px;
    padding: 18px;
    margin: 18px 0;
}

h1 {
    font-size: 26px;
}

h2 {
    font-size: 19px;
}

img {
    display: block;
    max-width: 100%;
    height: auto;
    margin: auto;
}

p {
    color: #637188;
    line-height: 1.6;
}
</style>

</head>

<body>
<main>

<h1>HSK4 – Đề 1 (H41001)</h1>

<p>
Kiểm tra trang PDF gốc trước khi tách câu.
Không hiển thị đáp án.
Chưa thay đổi SQL Server.
</p>

__SECTIONS__

</main>
</body>
</html>
"""

    return template.replace(
        "__SECTIONS__",
        sections
    ).encode("utf-8")


# =====================================================
# 14. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)

    print(
        "MOC HAN - HSK4 DE 01 - BUOC 1"
    )

    print("MA DE GOC H41001")

    print("=" * 60)

    require_file(PDF_FILE)
    require_file(MP3_FILE)

    # ================================================
    # 15. DOC PDF VA DAP AN
    # ================================================

    with fitz.open(PDF_FILE) as doc:

        verify_pdf(doc)

        objective = extract_objective(
            doc[22].get_text("text")
        )

        (
            writing,
            alternatives,
            references
        ) = extract_writing(
            doc[23].get_text("text")
        )

        # Tao anh xem truoc 4 trang.
        previews = {}

        for page_no in PREVIEW_PAGES:

            page = doc[page_no - 1]

            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False
            )

            path = (
                PREVIEW_DIR
                / f"trang_{page_no:02d}.png"
            )

            previews[path] = (
                pix.tobytes("png")
            )

    # ================================================
    # 16. KIEM TRA SO LUONG
    # ================================================

    if (
        len(objective) != 85
        or len(writing) != 10
        or len(references) != 5
    ):

        raise RuntimeError(
            "Chua du 100 cau HSK4."
        )

    answers = {
        **objective,
        **writing
    }

    # Cau 96-100: dap an None co chu y.
    # Khong duoc cham theo mot chuoi duy nhat.

    # ================================================
    # 17. TAO JSON NGUON
    # ================================================

    result = {
        "cap_hsk": 4,
        "so_de": 1,
        "ma_de_goc": CODE,

        "file_pdf": str(PDF_FILE),
        "file_mp3": str(MP3_FILE),

        "so_trang_pdf_de": 24,

        "tong_cau": 100,
        "so_cau_nghe": 45,
        "so_cau_doc": 40,
        "so_cau_viet": 15,

        "thoi_gian_pdf_phut": 105,

        "thoi_gian_lam_bai_de_xuat_phut": 100,

        "ghi_chu_thoi_gian": (
            "PDF ghi 105 phut, bao gom "
            "5 phut dien thong tin ca nhan. "
            "100 phut tren website la de xuat, "
            "chua chot."
        ),

        "trang_cau_hoi": list(
            range(2, 17)
        ),

        "trang_loi_thoai": list(
            range(17, 23)
        ),

        "trang_dap_an": [23, 24],

        "dap_an": {
            str(number): answers.get(number)

            for number in range(1, 101)
        },

        "dap_an_thay_the": {
            str(number): values

            for number, values
            in alternatives.items()
        },

        "dap_an_tham_khao_viet_mo": {
            str(number): references[number]

            for number in range(96, 101)
        },

        "tu_cho_san_viet_mo": {
            str(number): WRITING_WORDS[number]

            for number in range(96, 101)
        },

        "cau_can_cham_thu_cong": list(
            range(96, 101)
        ),

        "dang_cau_hoi": {
            str(number): question_kind(number)

            for number in range(1, 101)
        },

        "ghi_chu": (
            "Cau 96-100 la bai Viet mo. "
            "Khong cham bang so sanh "
            "chuoi dap an tham khao."
        ),
    }

    # ================================================
    # 18. TAO FILE DAU RA
    # ================================================

    outputs = {
        JSON_FILE: json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8"),

        HTML_FILE: preview_html(),

        **previews
    }

    # Kiem tra xung dot truoc khi ghi.
    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):

            raise RuntimeError(
                "KHONG ghi de file "
                "co noi dung khac:\n"
                + str(path)
            )

    for path, content in outputs.items():

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not path.exists():

            path.write_bytes(
                content
            )

    # ================================================
    # 19. KET QUA
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH HSK4 DE 01 - BUOC 1"
    )

    print("=" * 60)

    print("Ma de: H41001")
    print("PDF: 24 trang")

    print("Nghe: 45/45")
    print("Doc: 40/40")

    print("Viet sap xep: 10/10")
    print("Viet mo: 5/5 dap an tham khao")

    print(
        "Dap an thay the:",
        ", ".join(
            str(number)
            for number in sorted(alternatives)
        )
    )

    print(
        "Cau 96-100: KHONG cham tu dong"
    )

    print(
        "HTML: khong hien thi dap an"
    )

    print(f"\nJSON: {JSON_FILE}")
    print(f"HTML: {HTML_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
