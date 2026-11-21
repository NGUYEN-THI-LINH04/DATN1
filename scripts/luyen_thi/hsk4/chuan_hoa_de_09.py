
# -*- coding: utf-8 -*-
"""
MOC HAN - HSK4 DE 09 (H41329)
BUOC 3 - CHUAN HOA 100 CAU VA MEDIA

Ke thua chuan hoa De 7:
- PDF de 16 trang + PDF dap an rieng 2 trang.
- Kiem tra 100 dap an buoc 1.
- Kiem tra 100 anh va 2 bang A-F buoc 2.
- Doi chieu dap an voi PDF goc.
- Giu nguyen cum "1084 公里" cau 93.
- Khong co dap an thay the.
- Viet tranh 96-100 cham TU DONG.
- Sao chep anh, bang A-F va MP3.
- Tao de_09.json de nhap SQL.

KHONG ket noi SQL.
KHONG sua cac de cu.
KHONG sua bang Bai tap.
"""

from itertools import permutations
from pathlib import Path

import filecmp
import json
import os
import re
import shutil
import unicodedata

import fitz
from mutagen.mp3 import MP3


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

SOURCE = BASE / "source" / "De_HSK" / "HSK4"

DATA = BASE / "hsk4" / "data" / "de_09"

OUTPUT = BASE / "hsk4" / "output" / "de_09"

MEDIA_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk4"
)

MEDIA = MEDIA_ROOT / "de_09"

PDF_FILE = SOURCE / "H41009.pdf"

ANSWER_PDF = SOURCE / "H41009_dap_an.pdf"

MP3_FILE = SOURCE / "H41009.mp3"

ANSWER_FILE = DATA / "de_09_dap_an.json"

MANIFEST_FILE = (
    DATA / "hinh_100_cau_ung_vien.json"
)

FINAL_FILE = DATA / "de_09.json"

CODE = "H41329"
DE_NUMBER = 9

AUDIO_NAME = "H41009.mp3"

WORDS = {
    96: "肚子",
    97: "擦",
    98: "打折",
    99: "果汁",
    100: "重",
}

GROUPS = {
    "doc_46_50": (7, 46, 50, "ABCDEF"),
    "doc_51_55": (8, 51, 55, "ABCDEF"),
}

PAGE_MAP = {
    2: range(1, 11),
    3: range(11, 21),
    4: range(21, 26),
    5: range(26, 35),
    6: range(35, 46),

    7: range(46, 51),
    8: range(51, 56),

    9: range(56, 60),
    10: range(60, 66),

    11: range(66, 70),
    12: range(70, 76),

    13: range(76, 82),
    14: range(82, 86),

    15: range(86, 96),
    16: range(96, 101),
}


# =====================================================
# 2. HAM HO TRO
# =====================================================

def require(ok, message):

    if not ok:
        raise RuntimeError(message)


def require_file(path):

    require(
        path.is_file()
        and path.stat().st_size > 0,

        f"Thieu file hoac file rong: {path}"
    )

    return path


def read_json(path):

    return json.loads(
        require_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


def compact(value):

    value = unicodedata.normalize(
        "NFKC",
        str(value)
    )

    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "",
        value
    )


# =====================================================
# 3. TRANG, KY NANG, DANG CAU HOI
# =====================================================

def page_for(number):

    for page, numbers in PAGE_MAP.items():

        if number in numbers:
            return page

    raise RuntimeError(
        f"Khong tim thay trang cau {number}"
    )


def skill_for(number):

    if number <= 45:
        return "nghe"

    if number <= 85:
        return "doc"

    return "viet"


def part_for(number):

    if number <= 10:
        return "Nghe - Phần 1"

    if number <= 25:
        return "Nghe - Phần 2"

    if number <= 45:
        return "Nghe - Phần 3"

    if number <= 55:
        return "Đọc - Phần 1"

    if number <= 65:
        return "Đọc - Phần 2"

    if number <= 85:
        return "Đọc - Phần 3"

    if number <= 95:
        return "Viết - Phần 1"

    return "Viết - Phần 2"


def kind_for(number):

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


def choices_for(number):

    if number <= 10:
        return ["√", "×"]

    if number <= 45:
        return list("ABCD")

    if number <= 55:
        return list("ABCDEF")

    if number <= 65:
        return list("ABC")

    if number <= 85:
        return list("ABCD")

    return []


# =====================================================
# 4. TACH CUM TU VIET 86-95
# =====================================================

def tokens_from_pdf(exam):

    tokens = {}

    text = exam[14].get_text("text")

    for line in text.splitlines():

        match = re.match(
            r"^\s*(8[6-9]|9[0-5])"
            r"\s*[.．、]\s*(.+)$",
            line
        )

        if not match:
            continue

        number = int(match.group(1))

        values = [
            item.strip()

            for item in re.split(
                r"\s{2,}",
                match.group(2).strip()
            )

            if item.strip()
        ]

        require(
            number not in tokens,

            f"Trung cum tu cau {number}"
        )

        require(
            3 <= len(values) <= 9,

            f"Cau {number}: sai cum tu {values}"
        )

        tokens[number] = values

    require(
        set(tokens) == set(range(86, 96)),

        "Trang 15 khong du 10 cau Viet"
    )

    # Giu cum so va don vi o cau 93.
    require(
        "1084 公里" in tokens[93],

        "Cau 93 phai giu nguyen "
        "cum '1084 公里'"
    )

    return tokens


# =====================================================
# 5. DOC DAP AN VIET TU PDF RIENG
# =====================================================

def numbered_answers(text, first, last):

    matches = list(
        re.finditer(
            r"(?m)^\s*(\d{2,3})"
            r"\s*[.．、]",
            text
        )
    )

    result = {}

    for index, match in enumerate(matches):

        number = int(match.group(1))

        if not first <= number <= last:
            continue

        end = (
            matches[index + 1].start()

            if index + 1 < len(matches)

            else len(text)
        )

        key = str(number)

        require(
            key not in result,

            f"Trung dap an Viet {number}"
        )

        answer = re.sub(
            r"\s+",
            "",
            text[match.end():end]
        )

        require(
            bool(answer),

            f"Dap an Viet cau {number} rong"
        )

        result[key] = answer

    require(
        set(result) == {
            str(number)
            for number in range(first, last + 1)
        },

        f"PDF dap an thieu cau {first}-{last}"
    )

    return result


# =====================================================
# 6. KIEM TRA JSON BUOC 1
# =====================================================

def validate_answers(source, exam, key_doc):

    identity = (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc")
    )

    require(
        identity == (4, DE_NUMBER, CODE),

        "JSON buoc 1 khong phai De 9 / H41329"
    )

    counts = tuple(
        source.get(key)

        for key in (
            "tong_cau",
            "so_cau_nghe",
            "so_cau_doc",
            "so_cau_viet"
        )
    )

    require(
        counts == (100, 45, 40, 15),

        "JSON buoc 1 sai tong so cau"
    )

    # Kiem tra 3 duong dan nguon.
    for field, expected in (
        ("file_pdf", PDF_FILE),
        ("file_dap_an_pdf", ANSWER_PDF),
        ("file_mp3", MP3_FILE)
    ):

        require(
            Path(
                source.get(field) or ""
            ).resolve() == expected.resolve(),

            f"Sai duong dan {field}"
        )

    require(
        source.get("so_trang_pdf") == 16

        and source.get("trang_loi_thoai") == []

        and source.get("trang_dap_an") == [1, 2]

        and source.get("nguon_dap_an")
        == "pdf_rieng",

        "JSON buoc 1 sai cau truc PDF 16+2"
    )

    require(
        source.get("cau_can_cham_thu_cong") == []

        and source.get("che_do_cham_viet_mo")
        == "cham_tu_dong_theo_mau",

        "Viet tranh phai cham tu dong"
    )

    answers = source.get("dap_an") or {}

    require(
        isinstance(answers, dict)

        and set(answers) == {
            str(number)
            for number in range(1, 101)
        },

        "JSON buoc 1 thieu 100 dap an"
    )

    # ================================================
    # 7. KIEM TRA DAP AN THAY THE
    # ================================================

    alternatives = source.get(
        "dap_an_thay_the"
    )

    require(
        alternatives == {},

        "De 9 khong co dap an thay the"
    )

    # ================================================
    # 8. KIEM TRA TU GOI Y
    # ================================================

    words = source.get(
        "tu_cho_san_viet_mo"
    ) or {}

    require(
        words == {
            str(number): WORDS[number]
            for number in range(96, 101)
        },

        "Sai 5 tu goi y 96-100"
    )

    references = source.get(
        "dap_an_tham_khao_viet_mo"
    ) or {}

    require(
        set(references) == {
            str(number)
            for number in range(96, 101)
        },

        "Thieu 5 cau mau Viet theo tranh"
    )

    # ================================================
    # 9. DOI CHIEU 85 DAP AN NGHE VA DOC
    # ================================================

    official = {}

    matches = re.findall(
        r"(?<!\d)"
        r"(\d{1,3})"
        r"\s*[.．、]\s*"
        r"([A-F√×]{1,3})"
        r"(?![A-Z])",

        key_doc[0].get_text("text")
    )

    for key, value in matches:

        number = int(key)

        if not 1 <= number <= 85:
            continue

        require(
            key not in official,

            f"Trung dap an PDF cau {number}"
        )

        official[key] = value

    require(
        set(official) == {
            str(number)
            for number in range(1, 86)
        },

        "PDF dap an trang 1 khong du 85 cau"
    )

    for number in range(1, 86):

        key = str(number)

        answer = answers[key]

        if 56 <= number <= 65:

            valid = (
                isinstance(answer, str)

                and len(answer) == 3

                and set(answer) == set("ABC")
            )

        else:

            valid = answer in choices_for(number)

        require(
            valid,

            f"Cau {number} sai dang dap an: "
            f"{answer}"
        )

        require(
            answer == official[key],

            f"Cau {number}: dap an JSON khac PDF"
        )

    # ================================================
    # 10. DOI CHIEU CUM TU VIET 86-95
    # ================================================

    tokens = tokens_from_pdf(exam)

    source_tokens = source.get(
        "cum_tu_viet_sap_xep"
    )

    if source_tokens is not None:

        require(
            source_tokens == {
                str(number): tokens[number]
                for number in range(86, 96)
            },

            "Cum tu Viet buoc 1 "
            "khac PDF trang 15"
        )

    # ================================================
    # 11. DOC DAP AN VIET TRANG 2
    # ================================================

    text = key_doc[1].get_text("text")

    require(
        "第一部分" in text
        and "第二部分" in text,

        "PDF dap an trang 2 "
        "thieu hai phan Viet"
    )

    first_part, second_part = text.split(
        "第二部分",
        1
    )

    official_writing = numbered_answers(
        first_part,
        86,
        95
    )

    official_open = numbered_answers(
        second_part,
        96,
        100
    )

    # ================================================
    # 12. KIEM TRA 10 CAU VIET SAP XEP
    # ================================================

    for number in range(86, 96):

        key = str(number)

        answer = answers[key]

        require(
            isinstance(answer, str)
            and bool(answer.strip()),

            f"Cau Viet {number} rong"
        )

        variants = [
            value

            for value in re.split(
                r"[/／]",
                official_writing[key]
            )

            if value
        ]

        require(
            len(variants) == 1

            and compact(variants[0])
            == compact(answer),

            f"Cau {number}: dap an Viet "
            "khac PDF hoac co dap an thay the"
        )

        possible = {
            compact("".join(order))

            for order in permutations(
                tokens[number]
            )
        }

        require(
            compact(answer) in possible,

            f"Cau {number}: khong ghep duoc "
            "dap an tu cac cum tu PDF"
        )

    # ================================================
    # 13. KIEM TRA 5 CAU MAU VIET TRANH
    # ================================================

    for number in range(96, 101):

        key = str(number)

        values = references[key]

        require(
            answers[key] is None,

            f"Cau {number}: "
            "dap_an phai la null"
        )

        require(
            isinstance(values, list)
            and bool(values)

            and all(
                isinstance(value, str)

                and bool(compact(value))

                and WORDS[number] in value

                for value in values
            ),

            f"Cau {number}: cau mau khong hop le"
        )

        require(
            compact(official_open[key]) in [
                compact(value)
                for value in values
            ],

            f"Cau {number}: "
            "cau mau khac PDF dap an"
        )

    return (
        answers,
        alternatives,
        references,
        words,
        tokens
    )


# =====================================================
# 14. KIEM TRA MANIFEST BUOC 2
# =====================================================

def validate_manifest(manifest, words):

    identity = (
        manifest.get("cap_hsk"),
        manifest.get("so_de"),
        manifest.get("ma_de_goc"),
        manifest.get("so_cau")
    )

    require(
        identity == (4, DE_NUMBER, CODE, 100),

        "Manifest khong phai HSK4 De 9"
    )

    require(
        manifest.get("so_trang_pdf") == 16

        and manifest.get("trang_loi_thoai") == []

        and manifest.get("trang_dap_an") == [1, 2]

        and manifest.get("nguon_dap_an")
        == "pdf_rieng",

        "Manifest sai cau truc PDF"
    )

    require(
        Path(
            manifest.get("file_dap_an_pdf") or ""
        ).resolve() == ANSWER_PDF.resolve(),

        "Manifest sai file PDF dap an"
    )

    require(
        manifest.get("cau_can_cham_thu_cong") == []

        and manifest.get("che_do_cham_viet_mo")
        == "cham_tu_dong_theo_mau",

        "Manifest chua cham Viet tu dong"
    )

    items = manifest.get("cau_hoi") or {}

    groups = manifest.get(
        "bang_lua_chon"
    ) or {}

    require(
        isinstance(items, dict)

        and set(items) == {
            str(number)
            for number in range(1, 101)
        },

        "Manifest thieu 100 cau hoi"
    )

    require(
        isinstance(groups, dict)

        and set(groups) == set(GROUPS),

        "Manifest thieu hai bang A-F"
    )

    copies = []

    # ================================================
    # 15. KIEM TRA 100 ANH
    # ================================================

    for number in range(1, 101):

        key = str(number)

        item = items[key]

        relative = (
            f"questions/cau_{number:03d}.png"
        )

        require(
            item.get("trang_pdf")
            == page_for(number)

            and item.get("anh") == relative,

            f"Cau {number}: sai trang "
            "hoac duong dan anh"
        )

        if 46 <= number <= 50:

            group = "doc_46_50"

        elif 51 <= number <= 55:

            group = "doc_51_55"

        else:

            group = None

        require(
            item.get("nhom_lua_chon") == group,

            f"Cau {number}: sai nhom lua chon"
        )

        if number >= 96:

            require(
                item.get("tu_cho_san")
                == words[key],

                f"Cau {number}: sai tu goi y"
            )

        # ============================================
        # 16. GIU DOAN DOC CHUNG
        # ============================================

        if 80 <= number <= 85:

            if number <= 81:

                shared = "80-81"

            elif number <= 83:

                shared = "82-83"

            else:

                shared = "84-85"

            require(
                item.get("nhom_doc_chung")
                == shared,

                f"Cau {number}: "
                f"sai doan Doc chung {shared}"
            )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    # ================================================
    # 17. KIEM TRA HAI BANG A-F
    # ================================================

    for name, expected in GROUPS.items():

        page, first, last, labels = expected

        item = groups[name]

        actual = (
            item.get("trang_pdf"),
            item.get("cau_tu"),
            item.get("cau_den"),
            item.get("lua_chon"),
            item.get("anh")
        )

        wanted = (
            page,
            first,
            last,
            labels,
            f"groups/{name}.png"
        )

        require(
            actual == wanted,

            f"Bang {name}: sai du lieu"
        )

        relative = f"groups/{name}.png"

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    require(
        len(copies) == 102,

        "Khong du 100 anh va 2 bang A-F"
    )

    return items, copies


# =====================================================
# 18. KIEM TRA MEDIA TRUOC KHI SAO CHEP
# =====================================================

def inspect_media(copies):

    for source_file, destination in copies:

        require_file(source_file)

        if source_file.suffix.lower() == ".png":

            with source_file.open("rb") as stream:

                require(
                    stream.read(8)
                    == b"\x89PNG\r\n\x1a\n",

                    f"Anh PNG khong hop le: "
                    f"{source_file}"
                )

        if destination.exists():

            require(
                filecmp.cmp(
                    source_file,
                    destination,
                    shallow=False
                ),

                "Media da ton tai voi noi dung khac."
                "\nKHONG ghi de: "
                + str(destination)
            )


# =====================================================
# 19. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 09 - BUOC 3")
    print("CHUAN HOA H41329")
    print("=" * 60)

    # ================================================
    # 20. KIEM TRA FILE NGUON
    # ================================================

    for path in (
        PDF_FILE,
        ANSWER_PDF,
        MP3_FILE
    ):

        require_file(path)

    source = read_json(ANSWER_FILE)

    manifest = read_json(MANIFEST_FILE)

    # ================================================
    # 21. DOI CHIEU HAI PDF VA DAP AN
    # ================================================

    with fitz.open(PDF_FILE) as exam, \
         fitz.open(ANSWER_PDF) as key_doc:

        require(
            len(exam) == 16

            and CODE in exam[0].get_text("text")

            and CODE in exam[15].get_text("text"),

            "PDF de khong phai "
            "H41329 / 16 trang"
        )

        require(
            len(key_doc) == 2

            and CODE in key_doc[0].get_text("text")

            and "卷答案" in key_doc[0].get_text("text"),

            "PDF dap an khong phai "
            "H41329 / 2 trang"
        )

        (
            answers,
            alternatives,
            references,
            words,
            tokens
        ) = validate_answers(
            source,
            exam,
            key_doc
        )

    # ================================================
    # 22. KIEM TRA MANIFEST
    # ================================================

    items, copies = validate_manifest(
        manifest,
        words
    )

    # ================================================
    # 23. DOC THOI LUONG MP3
    # ================================================

    try:

        duration = round(
            float(
                MP3(str(MP3_FILE)).info.length
            ),
            2
        )

    except Exception as exc:

        raise RuntimeError(
            f"Khong doc duoc MP3: {exc}"
        ) from exc

    require(
        0 < duration < 10000,

        "Thoi luong MP3 bat thuong"
    )

    copies.append((
        MP3_FILE,
        MEDIA_ROOT / AUDIO_NAME
    ))

    inspect_media(copies)

    # ================================================
    # 24. TAO 100 CAU HOI
    # ================================================

    questions = []

    for number in range(1, 101):

        key = str(number)

        item = items[key]

        other = alternatives.get(
            key,
            []
        )

        # ============================================
        # 25. VIET SAP XEP 86-95
        # ============================================

        if 86 <= number <= 95:

            if other:

                answer = [
                    answers[key]
                ] + other

            else:

                answer = answers[key]

            options = [
                {
                    "ma": str(index + 1),
                    "nhan": value
                }

                for index, value in enumerate(
                    tokens[number]
                )
            ]

        # ============================================
        # 26. VIET THEO TRANH 96-100
        # ============================================

        elif number >= 96:

            answer = {
                "che_do": (
                    "cham_tu_dong_theo_mau"
                ),

                "tu_cho_san": words[key],

                "dap_an_tham_khao": (
                    references[key]
                )
            }

            options = []

        # ============================================
        # 27. CAC CAU NGHE VA DOC
        # ============================================

        else:

            answer = answers[key]

            options = [
                {
                    "ma": value,
                    "nhan": value
                }

                for value in choices_for(number)
            ]

        group = item.get(
            "nhom_lua_chon"
        )

        question = {

            "so_cau": number,

            "ky_nang": skill_for(number),

            "phan": part_for(number),

            "loai_cau_hoi": kind_for(number),

            "noi_dung": (
                "Nhìn tranh và đặt câu với từ: "
                + words[key]

                if number >= 96
                else None
            ),

            "trang_pdf": item["trang_pdf"],

            "anh_cau_hoi": (
                "/static/media/luyen_thi/"
                "hsk4/de_09/"
                + item["anh"]
            ),

            "anh_nhom_lua_chon": (
                "/static/media/luyen_thi/"
                "hsk4/de_09/groups/"
                + group + ".png"

                if group
                else None
            ),

            "lua_chon_json": options,

            "dap_an_dung": answer,

            "dap_an_thay_the": other,

            "nhom_doc_chung": item.get(
                "nhom_doc_chung"
            ),

            "cham_thu_cong": False,

            "da_duyet": False
        }

        if number >= 96:

            question["dap_an_tham_khao"] = (
                references[key]
            )

            question["tu_cho_san"] = words[key]

        questions.append(question)

    # ================================================
    # 28. TAO JSON CUOI CUNG
    # ================================================

    result = {

        "ma_de_goc": CODE,

        "cap_hsk": 4,

        "so_de": DE_NUMBER,

        "thu_tu": DE_NUMBER,

        "ten_hien_thi": "Đề 9",

        "so_cau": 100,

        "so_cau_nghe": 45,

        "so_cau_doc": 40,

        "so_cau_viet": 15,

        "thoi_gian_phut": 100,

        "thoi_gian_pdf_phut": 105,

        "so_trang_pdf_de": 16,

        "trang_cau_hoi": list(
            range(2, 17)
        ),

        "trang_loi_thoai": [],

        "trang_dap_an": [1, 2],

        "nguon_dap_an": "pdf_rieng",

        "file_pdf": str(PDF_FILE),

        "file_dap_an_pdf": str(ANSWER_PDF),

        "file_mp3": str(MP3_FILE),

        "audio": {

            "duong_dan": (
                "/static/media/luyen_thi/"
                "hsk4/" + AUDIO_NAME
            ),

            "thoi_luong_giay": duration
        },

        "dap_an_thay_the": alternatives,

        "dap_an_tham_khao_viet_mo": (
            references
        ),

        "cau_can_cham_thu_cong": [],

        "che_do_cham_viet_mo": (
            "cham_tu_dong_theo_mau"
        ),

        "san_sang_nhap_sql": True,

        "cau_hoi": questions
    }

    # ================================================
    # 29. KIEM TRA KHONG GHI DE JSON CU
    # ================================================

    content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    require(
        not FINAL_FILE.exists()
        or FINAL_FILE.read_bytes() == content,

        "JSON cu co noi dung khac."
        "\nKHONG ghi de: "
        + str(FINAL_FILE)
    )

    # ================================================
    # 30. SAO CHEP MEDIA
    # ================================================

    for source_file, destination in copies:

        if not destination.exists():

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(
                source_file,
                destination
            )

        require(
            filecmp.cmp(
                source_file,
                destination,
                shallow=False
            ),

            "Sao chep media bi loi: "
            + str(destination)
        )

    # ================================================
    # 31. LUU JSON
    # ================================================

    if not FINAL_FILE.exists():

        FINAL_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        FINAL_FILE.write_bytes(content)

    # ================================================
    # 32. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH CHUAN HOA HSK4 DE 09")
    print("=" * 60)

    print("Ma de goc: H41329")
    print("Ten hien thi: De 9")

    print("Tong cau: 100")

    print("Nghe: 45/45")
    print("Doc: 40/40")

    print("Viet sap xep: 10/10")
    print("Viet theo tranh: 5/5 cau mau")

    print("Dap an thay the: KHONG CO")
    print("Che do cham: TU DONG")

    print("Anh: 100/100")
    print("Bang A-F: 2/2")

    print(f"MP3: {duration} giay")
    print("Thoi gian thi: 100 phut")

    print(f"\nJSON: {FINAL_FILE}")

    print("\nCHUA thay doi SQL Server.")
    print("CHUA nhap de.")


if __name__ == "__main__":
    main()
