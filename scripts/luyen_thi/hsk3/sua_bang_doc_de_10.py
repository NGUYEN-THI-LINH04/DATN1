
# -*- coding: utf-8 -*-

"""
MOC HAN - SUA BANG LUA CHON HSK3 DE 10
MA DE GOC: H31328

- Su dung toa do bang Doc theo De 9.
- Sua 4 bang lua chon cau 41-60.
- Kiem tra nhan A-F / A-E truoc khi luu.
- Sao luu 4 anh cu.
- Khong tach lai 70 anh cau hoi.
- Khong sua HTML, JSON, MP3 hay SQL Server.
"""

from pathlib import Path
import json
import os
import re
import shutil
import unicodedata

import fitz


# =====================================================
# 1. DUONG DAN
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

GROUP_DIR = OUTPUT / "groups"

BACKUP_DIR = (
    OUTPUT / "backup_bang_doc_truoc_sua"
)

ANSWER_JSON = DATA / "de_10_dap_an.json"

PREVIEW_HTML = OUTPUT / "kiem_tra_80_cau.html"

CODE = "H31328"

ZOOM = 2.5


# =====================================================
# 2. TOA DO BANG LUA CHON GIONG DE 9
# =====================================================

# Luu y:
# Day la toa do cua bang chua A-F / A-E,
# KHONG phai toa do cua dong "例如".

READING_GROUPS = {
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


# =====================================================
# 3. HAM HO TRO
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


def normalize(value):

    return unicodedata.normalize(
        "NFKC",
        str(value)
    ).strip()


def read_json(path):

    return json.loads(
        require_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


# =====================================================
# 4. TIM PDF GOC DE 10
# =====================================================

def get_pdf():

    data = read_json(ANSWER_JSON)

    if (
        data.get("cap_hsk") != 3
        or data.get("so_de") != 10
        or data.get("ma_de_goc") != CODE
    ):
        raise RuntimeError(
            "JSON khong phai HSK3 De 10 H31328."
        )

    path_value = data.get("file_pdf")

    if not path_value:
        raise RuntimeError(
            "JSON thieu duong dan PDF."
        )

    pdf_path = require_file(
        Path(path_value)
    )

    if "HSK3" not in str(pdf_path):
        raise RuntimeError(
            "Duong dan PDF khong hop le."
        )

    return pdf_path


# =====================================================
# 5. NHAN DIEN NHAN LUA CHON
# =====================================================

def find_labels(page, rect):

    found = set()

    for word in page.get_text("words"):

        value = normalize(word[4])

        # Xet tam cua moi tu nam trong
        # vung can cat.
        center = fitz.Point(
            (word[0] + word[2]) / 2,
            (word[1] + word[3]) / 2
        )

        if not rect.contains(center):
            continue

        # Nhan A, B... co the di kem
        # dau cham hoac chu Han.
        match = re.match(
            r"^([A-F])(?:$|[.．、:：\s\u3400-\u9fff])",
            value
        )

        if match:
            found.add(
                match.group(1)
            )

    return found


# =====================================================
# 6. KIEM TRA VA CAT MOT BANG
# =====================================================

def extract_group(doc, name, config):

    page_no = config["trang_pdf"]

    page = doc[page_no - 1]

    rect = fitz.Rect(
        config["rect"]
    )

    if not page.rect.contains(rect):
        raise RuntimeError(
            f"Khung {name} nam ngoai trang PDF."
        )

    expected = set(
        config["lua_chon"]
    )

    found = find_labels(
        page,
        rect
    )

    missing = expected - found

    if missing:

        sample_text = page.get_text(
            "text",
            clip=rect
        )

        raise RuntimeError(
            f"\nBang {name} cat chua dung.\n"
            f"Can: {sorted(expected)}\n"
            f"Tim thay: {sorted(found)}\n"
            f"Thieu: {sorted(missing)}\n"
            f"Noi dung vung cat:\n{sample_text}\n"
            "Chua thay doi bat ky anh nao."
        )

    # Dam bao khong chi cat cac nhan A-F
    # ma con co noi dung chu Han.
    text = page.get_text(
        "text",
        clip=rect
    )

    if not re.search(
        r"[\u3400-\u9fff]",
        text
    ):
        raise RuntimeError(
            f"Bang {name} khong co "
            "noi dung chu Han."
        )

    pix = page.get_pixmap(
        matrix=fitz.Matrix(ZOOM, ZOOM),
        clip=rect,
        alpha=False
    )

    content = pix.tobytes("png")

    if not content.startswith(
        b"\x89PNG\r\n\x1a\n"
    ):
        raise RuntimeError(
            f"Khong tao duoc PNG cho {name}."
        )

    print(
        f"{name}: "
        f"du {config['lua_chon']} "
        f"- trang {page_no}"
    )

    return content


# =====================================================
# 7. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - SUA BANG DOC HSK3 DE 10")
    print("MA DE GOC H31328")
    print("=" * 60)

    pdf_path = get_pdf()

    print(f"\nPDF: {pdf_path}")

    # ================================================
    # 8. KIEM TRA FILE ANH HIEN TAI
    # ================================================

    for name in READING_GROUPS:

        require_file(
            GROUP_DIR / f"{name}.png"
        )

    require_file(
        PREVIEW_HTML
    )

    # ================================================
    # 9. DOC PDF VA TAO 4 ANH MOI
    # ================================================

    new_images = {}

    with fitz.open(pdf_path) as doc:

        if len(doc) != 16:
            raise RuntimeError(
                "PDF H31328 phai co 16 trang."
            )

        cover = doc[0].get_text(
            "text"
        )

        if CODE not in cover:
            raise RuntimeError(
                "PDF khong phai H31328."
            )

        print(
            "\n===== KIEM TRA 4 BANG DOC ====="
        )

        # Tao va kiem tra TOAN BO 4 anh
        # truoc khi sua file hien tai.
        for name, config in READING_GROUPS.items():

            new_images[name] = extract_group(
                doc,
                name,
                config
            )

    # ================================================
    # 10. SAO LUU ANH CU
    # ================================================

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for name in READING_GROUPS:

        old_path = GROUP_DIR / f"{name}.png"

        backup_path = (
            BACKUP_DIR / f"{name}.png"
        )

        # Sao luu lan dau, khong ghi de
        # ban sao luu neu chay lai.
        if not backup_path.exists():

            shutil.copy2(
                old_path,
                backup_path
            )

    print("\nDa sao luu 4 anh cu.")

    # ================================================
    # 11. THAY 4 ANH LUA CHON
    # ================================================

    changed = 0

    for name, content in new_images.items():

        destination = (
            GROUP_DIR / f"{name}.png"
        )

        if destination.read_bytes() == content:

            print(
                f"{name}: da dung, khong can sua"
            )

            continue

        # Ghi vao file tam truoc.
        temp_file = GROUP_DIR / (
            f"{name}.png.tmp"
        )

        temp_file.write_bytes(
            content
        )

        # Thay file cu bang file moi.
        temp_file.replace(
            destination
        )

        changed += 1

        print(
            f"{name}: DA SUA"
        )

    # ================================================
    # 12. KIEM TRA SAU KHI SUA
    # ================================================

    for name, content in new_images.items():

        path = GROUP_DIR / f"{name}.png"

        if path.read_bytes() != content:

            raise RuntimeError(
                f"Anh {name} luu khong khop."
            )

    print("\n" + "=" * 60)

    print(
        "HOAN THANH SUA BANG DOC HSK3 DE 10"
    )

    print("=" * 60)

    print("Ma de: H31328")
    print("Bang Doc: 4/4")

    print(f"So anh duoc cap nhat: {changed}")

    print("Cau 41-45: A-F")
    print("Cau 46-50: A-E")
    print("Cau 51-55: A-F")
    print("Cau 56-60: A-F")

    print("\nHTML cu van duoc su dung:")
    print(PREVIEW_HTML)

    print("\nKhong thay doi JSON.")
    print("Khong thay doi MP3.")
    print("Khong thay doi SQL Server.")


if __name__ == "__main__":
    main()
