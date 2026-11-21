
# -*- coding: utf-8 -*-

"""
MOC HAN - SUA HIEN THI HSK3 DE 10
MA DE GOC: H31328

1. Bo cac nut so cau duoi bang Doc 41-60.
2. Giu nguyen bang lua chon A-F / A-E.
3. Cat lai anh cau 76-80 de khong mat Pinyin.
4. Khong de anh cau truoc/dung vao cau sau.
5. Sao luu HTML va 5 anh truoc khi sua.

KHONG sua JSON dap an.
KHONG sua MP3.
KHONG ket noi SQL Server.
KHONG sua cac de thi cu.
"""

from pathlib import Path
import os
import re
import shutil
import unicodedata
import json

import fitz


# =====================================================
# 1. CAU HINH
# =====================================================

ROOT = Path(
    os.environ.get(
        "MOC_HAN_ROOT",
        r"D:\DATN1"
    )
)

BASE = ROOT / "scripts" / "luyen_thi"

DATA = BASE / "hsk3" / "data" / "de_10"

OUTPUT = BASE / "hsk3" / "output" / "de_10"

ANSWER_JSON = DATA / "de_10_dap_an.json"

HTML_FILE = OUTPUT / "kiem_tra_80_cau.html"

QUESTIONS = OUTPUT / "questions"

BACKUP = OUTPUT / "backup_truoc_sua_hien_thi"

CODE = "H31328"


# =====================================================
# 2. PINYIN GOC CUA CAU 76-80
# =====================================================

EXPECTED_PINYIN = {
    76: "zhong",
    77: "lai",
    78: "dian",
    79: "hao",
    80: "zhi",
}


# =====================================================
# 3. CAC BANG DOC CAN BO NUT SO CAU
# =====================================================

READ_GROUPS = (
    "doc_41_45",
    "doc_46_50",
    "doc_51_55",
    "doc_56_60",
)


# =====================================================
# 4. CAC HAM HO TRO
# =====================================================

def require_file(path):

    if (
        not path.is_file()
        or path.stat().st_size == 0
    ):
        raise RuntimeError(
            f"Thieu file hoac file rong:\n{path}"
        )

    return path


def deaccent(text):

    value = unicodedata.normalize(
        "NFD",
        text
    ).lower()

    return "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    ).strip()


# =====================================================
# 5. LAY CAC DONG VAN BAN TRONG PDF
# =====================================================

def find_line_rects(page):

    result = []

    blocks = page.get_text("dict")["blocks"]

    for block in blocks:

        for line in block.get("lines", []):

            text = "".join(
                span.get("text", "")
                for span in line.get(
                    "spans", []
                )
            ).strip()

            result.append((
                text,
                fitz.Rect(line["bbox"])
            ))

    return result


# =====================================================
# 6. CAT LAI 5 CAU VIET 76-80
# =====================================================

def make_new_writing_images(doc):

    # Trang PDF 14, index Python 13.
    page = doc[13]

    lines = find_line_rects(page)

    numbers = {}

    # ================================================
    # 7. TIM VI TRI SO CAU
    # ================================================

    for text, rect in lines:

        match = re.match(
            r"^\s*(7[6-9]|80)\s*[.．、]",
            text
        )

        if not match:
            continue

        number = int(match.group(1))

        if number in numbers:

            raise RuntimeError(
                f"Trung so cau {number} trong PDF."
            )

        numbers[number] = rect

    if set(numbers) != set(range(76, 81)):

        raise RuntimeError(
            "Khong nhan dien du cau 76-80."
        )

    # ================================================
    # 8. TIM PINYIN PHIA TREN MOI CAU
    # ================================================

    pinyin = {}

    for number, qrect in numbers.items():

        candidates = [
            (text, rect)

            for text, rect in lines

            if (
                qrect.y0 - 23
                <= rect.y0
                < qrect.y0
            )

            and 140 <= rect.x0 < 450

            and re.search(
                r"[a-zA-Z]",
                text
            )
        ]

        candidates = [
            item

            for item in candidates

            if deaccent(item[0])
            == EXPECTED_PINYIN[number]
        ]

        if len(candidates) != 1:

            raise RuntimeError(
                f"Khong tim thay Pinyin "
                f"cau {number}: {candidates}"
            )

        pinyin[number] = candidates[0]

    # ================================================
    # 9. TINH VUNG CAT MOI
    # ================================================

    output = {}

    for number in range(76, 81):

        text, pinyin_rect = pinyin[number]

        # Bat dau TRUOC Pinyin 10 don vi PDF.
        # Khong cat theo vi tri so cau nhu truoc.
        top = max(
            0,
            pinyin_rect.y0 - 10
        )

        # Ket thuc truoc Pinyin cau tiep theo.
        if number < 80:

            next_pinyin = (
                pinyin[number + 1][1]
            )

            bottom = next_pinyin.y0 - 10

        else:

            # Cau 80 la cau cuoi trang.
            # Cat sat noi dung, khong lay footer.
            bottom = (
                numbers[number].y1 + 33
            )

        rect = fitz.Rect(
            65,
            top,
            page.rect.width - 50,
            bottom
        )

        if (
            not page.rect.contains(rect)
            or rect.height < 35
        ):

            raise RuntimeError(
                f"Khung cau {number} "
                f"khong hop le: {rect}"
            )

        # ============================================
        # 10. KIEM TRA KHONG MAT PINYIN
        # ============================================

        visible_text = page.get_text(
            "text",
            clip=rect
        )

        if (
            text not in visible_text
            or str(number) not in visible_text
        ):

            raise RuntimeError(
                f"Anh cau {number} "
                "bi thieu Pinyin hoac chu Han."
            )

        # ============================================
        # 11. KHONG DINH PINYIN CAU SAU
        # ============================================

        if number < 80:

            next_pinyin = (
                EXPECTED_PINYIN[number + 1]
            )

            if next_pinyin in deaccent(
                visible_text
            ):

                raise RuntimeError(
                    f"Anh cau {number} "
                    "bi dinh Pinyin cau sau."
                )

        # ============================================
        # 12. XUAT ANH PNG
        # ============================================

        pix = page.get_pixmap(
            matrix=fitz.Matrix(2.5, 2.5),
            clip=rect,
            alpha=False
        )

        output[number] = pix.tobytes("png")

        print(
            f"Cau {number}: Pinyin {text} - OK"
        )

    return output


# =====================================================
# 13. BO CAC NUT SO CAU O PHAN DOC
# =====================================================

def patch_html(original):

    visited = set()
    removed = set()

    # Tim tung khung bang lua chon.
    card_re = re.compile(
        r'<section\s+class=["\']group-card["\']'
        r'\s*>.*?</section>',
        re.S | re.I
    )

    # Tim nhom nut Câu 41, Câu 42...
    buttons_re = re.compile(
        r'<div\s+class=["\']number-buttons["\']'
        r'\s*>.*?</div>',
        re.S | re.I
    )

    def replace(match):

        block = match.group(0)

        for name in READ_GROUPS:

            if (
                f"groups/{name}.png"
                not in block
            ):
                continue

            if name in visited:

                raise RuntimeError(
                    f"Trung khung {name} trong HTML."
                )

            visited.add(name)

            # Chi xoa nhom nut so cau.
            # KHONG xoa anh lua chon A-F / A-E.
            updated, count = buttons_re.subn(
                "",
                block,
                count=1
            )

            if count:
                removed.add(name)

            return updated

        # Cac khung Nghe giu nguyen.
        return block

    patched = card_re.sub(
        replace,
        original
    )

    # Kiem tra du 4 nhom Doc.
    if set(READ_GROUPS) != visited:

        missing = (
            set(READ_GROUPS) - visited
        )

        raise RuntimeError(
            "HTML khong dung cau truc "
            "group-card hien tai.\n"
            f"Thieu: {sorted(missing)}\n"
            "Khong tu dong ghi de."
        )

    return patched, removed


# =====================================================
# 14. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 55)

    print(
        "MOC HAN - SUA HTML + PINYIN HSK3 DE 10"
    )

    print("=" * 55)

    # ================================================
    # 15. KIEM TRA JSON BUOC 1
    # ================================================

    source = json.loads(
        require_file(
            ANSWER_JSON
        ).read_text(
            encoding="utf-8-sig"
        )
    )

    if (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc")
    ) != (3, 10, CODE):

        raise RuntimeError(
            "JSON khong phai De 10 H31328."
        )

    pdf_value = source.get("file_pdf")

    if not pdf_value:

        raise RuntimeError(
            "JSON thieu duong dan PDF."
        )

    pdf = require_file(
        Path(pdf_value)
    )

    expected_folder = (
        BASE / "source" / "De_HSK"
        / "HSK3" / "ĐỀ 10"
    )

    if (
        pdf.parent.resolve()
        != expected_folder.resolve()
    ):

        raise RuntimeError(
            "PDF khong nam trong "
            "thu muc HSK3 DE 10."
        )

    # ================================================
    # 16. KIEM TRA HTML VA ANH HIEN TAI
    # ================================================

    require_file(
        HTML_FILE
    )

    for number in range(76, 81):

        require_file(
            QUESTIONS / f"cau_{number:02d}.png"
        )

    for name in READ_GROUPS:

        require_file(
            OUTPUT / "groups" / f"{name}.png"
        )

    # ================================================
    # 17. TAO LAI 5 ANH TU PDF
    # ================================================

    print("\n===== SUA ANH CAU 76-80 =====")

    with fitz.open(pdf) as doc:

        if (
            len(doc) != 16
            or CODE not in doc[0].get_text("text")
        ):

            raise RuntimeError(
                "PDF khong phai H31328."
            )

        images = make_new_writing_images(
            doc
        )

    # ================================================
    # 18. SUA HTML TRONG BO NHO
    # ================================================

    print("\n===== SUA HTML =====")

    raw_html = HTML_FILE.read_text(
        encoding="utf-8-sig"
    )

    new_html, removed = patch_html(
        raw_html
    )

    # ================================================
    # 19. SAO LUU FILE CU
    # ================================================

    BACKUP.mkdir(
        parents=True,
        exist_ok=True
    )

    old_files = [HTML_FILE]

    old_files.extend(
        QUESTIONS / f"cau_{n:02d}.png"
        for n in range(76, 81)
    )

    for src in old_files:

        saved = BACKUP / src.name

        if not saved.exists():

            shutil.copy2(
                src,
                saved
            )

    print("Da sao luu HTML va 5 anh cu.")

    # ================================================
    # 20. LUU 5 ANH MOI
    # ================================================

    for number, content in images.items():

        destination = (
            QUESTIONS / f"cau_{number:02d}.png"
        )

        if destination.read_bytes() == content:
            continue

        temporary = destination.with_suffix(
            ".png.tmp"
        )

        temporary.write_bytes(
            content
        )

        temporary.replace(
            destination
        )

    # ================================================
    # 21. CAP NHAT HTML
    # ================================================

    if raw_html != new_html:

        temporary = HTML_FILE.with_suffix(
            ".html.tmp"
        )

        temporary.write_text(
            new_html,
            encoding="utf-8"
        )

        temporary.replace(
            HTML_FILE
        )

    # ================================================
    # 22. HOAN THANH
    # ================================================

    print("\n" + "=" * 55)

    print("HOAN THANH SUA HIEN THI DE 10")

    print("=" * 55)

    print("Cau 76-80: 5/5 anh day du Pinyin")

    print(
        "Bang Doc 41-60: "
        "khong con cac nut so cau"
    )

    print(
        f"So nhom nut vua xoa: {len(removed)}"
    )

    print(
        "Bang lua chon A-F/A-E: GIU NGUYEN"
    )

    print(
        "Anh cau 11-75: GIU NGUYEN"
    )

    print("\nKhong sua JSON dap an.")
    print("Khong sua MP3.")
    print("Khong sua SQL Server.")

    print(f"\nHTML: {HTML_FILE}")
    print(f"Backup: {BACKUP}")


if __name__ == "__main__":
    main()
