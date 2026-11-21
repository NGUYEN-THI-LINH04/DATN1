
# -*- coding: utf-8 -*-
"""
MOC HAN - HSK4 DE 08 (H41328)
BUOC 3 - CHUAN HOA 100 CAU VA MEDIA

Ke thua cau truc chuan hoa HSK4 De 5 / De 7.

- PDF de thi: H41008.pdf (16 trang).
- PDF dap an: H41008_dap_an.pdf (18 trang).
- Dap an nam o trang 17-18.
- Doi chieu 100 dap an voi PDF.
- Kiem tra manifest 100 anh va 2 bang A-F.
- Giu 5 cau Viet tranh cham TU DONG.
- Sao chep 100 anh, 2 bang A-F va MP3.
- Tao de_08.json de nhap SQL.

KHONG ket noi SQL.
KHONG sua cac de da nhap.
KHONG sua cac bang Bai tap.
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

DATA = BASE / "hsk4" / "data" / "de_08"
OUTPUT = BASE / "hsk4" / "output" / "de_08"

MEDIA_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk4"
)

MEDIA = MEDIA_ROOT / "de_08"

PDF_FILE = SOURCE / "H41008.pdf"
ANSWER_PDF = SOURCE / "H41008_dap_an.pdf"
MP3_FILE = SOURCE / "H41008.mp3"

ANSWER_FILE = DATA / "de_08_dap_an.json"

MANIFEST_FILE = (
    DATA / "hinh_100_cau_ung_vien.json"
)

FINAL_FILE = DATA / "de_08.json"

CODE = "H41328"
DE_NUMBER = 8

AUDIO_NAME = "H41008.mp3"

WORDS = {
    96: "袜子",
    97: "加班",
    98: "估计",
    99: "脏",
    100: "看法",
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
        path.is_file() and path.stat().st_size > 0,
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
# 3. LOAI BO WATERMARK CUA PDF DAP AN
# =====================================================

def clean_answer_text(text):
    return re.sub(
        r"(?im)^\s*"
        r"(?:www\.)?tiengtrungnet\.com"
        r"\s*$",
        "",
        text
    )


# =====================================================
# 4. TRANG, KY NANG, DANG CAU HOI
# =====================================================

def page_for(number):
    for page, numbers in PAGE_MAP.items():
        if number in numbers:
            return page

    raise RuntimeError(
        f"Khong tim thay trang cua cau {number}"
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
# 5. TACH CUM TU VIET 86-95
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

        require(
            number not in tokens,
            f"Trung cum tu cau {number}"
        )

        values = [
            item.strip()

            for item in re.split(
                r"\s{2,}",
                match.group(2).strip()
            )

            if item.strip()
        ]

        require(
            3 <= len(values) <= 9,
            f"Cau {number} sai so cum tu: {values}"
        )

        tokens[number] = values

    require(
        set(tokens) == set(range(86, 96)),
        "PDF de trang 15 thieu cau Viet 86-95"
    )

    return tokens


# =====================================================
# 6. DOC DAP AN VIET TU TRANG 18
# =====================================================

def numbered_answers(text, first, last):
    text = clean_answer_text(text)

    matches = list(
        re.finditer(
            r"(?m)^\s*(\d{2,3})\s*[.．、]",
            text
        )
    )

    result = {}

    for index, match in enumerate(matches):
        number = int(match.group(1))

        if not first <= number <= last:
            continue

        key = str(number)

        require(
            key not in result,
            f"Trung dap an Viet {number}"
        )

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )

        result[key] = re.sub(
            r"\s+",
            "",
            text[match.end():end]
        )

        require(
            bool(result[key]),
            f"Dap an Viet {number} rong"
        )

    require(
        set(result) == {
            str(number)
            for number in range(first, last + 1)
        },
        f"PDF trang 18 khong du dap an {first}-{last}"
    )

    return result


# =====================================================
# 7. DOI CHIEU JSON BUOC 1 VOI PDF
# =====================================================

def validate_answers(source, exam, key_doc):

    require(
        (
            source.get("cap_hsk"),
            source.get("so_de"),
            source.get("ma_de_goc")
        ) == (4, DE_NUMBER, CODE),

        "JSON buoc 1 khong phai De 8 / H41328"
    )

    require(
        tuple(
            source.get(key)

            for key in (
                "tong_cau",
                "so_cau_nghe",
                "so_cau_doc",
                "so_cau_viet"
            )
        ) == (100, 45, 40, 15),

        "JSON buoc 1 sai so cau"
    )

    # ================================================
    # 8. KIEM TRA DUONG DAN FILE
    # ================================================

    for field, path in (
        ("file_pdf", PDF_FILE),
        ("file_dap_an_pdf", ANSWER_PDF),
        ("file_mp3", MP3_FILE)
    ):

        require(
            Path(
                source.get(field) or ""
            ).resolve() == path.resolve(),

            f"JSON buoc 1 sai duong dan {field}"
        )

    # ================================================
    # 9. KIEM TRA CAU TRUC PDF
    # ================================================

    require(
        source.get("so_trang_pdf") == 16
        and source.get("trang_loi_thoai") == []
        and source.get("trang_dap_an") == [17, 18]
        and source.get("nguon_dap_an") == "pdf_rieng",

        "JSON buoc 1 sai cau truc PDF"
    )

    require(
        source.get("cau_can_cham_thu_cong") == []
        and source.get("che_do_cham_viet_mo")
        == "cham_tu_dong_theo_mau",

        "Phan Viet phai cham tu dong"
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
    # 10. KIEM TRA DAP AN THAY THE
    # ================================================

    alternatives = source.get(
        "dap_an_thay_the"
    )

    require(
        alternatives == {},

        "De 8 khong co dap an thay the trong PDF"
    )

    # ================================================
    # 11. KIEM TRA TU GOI Y VA CAU MAU
    # ================================================

    words = source.get(
        "tu_cho_san_viet_mo"
    ) or {}

    require(
        words == {
            str(number): WORDS[number]
            for number in range(96, 101)
        },

        "JSON buoc 1 sai 5 tu goi y"
    )

    references = source.get(
        "dap_an_tham_khao_viet_mo"
    ) or {}

    require(
        set(references) == {
            str(number)
            for number in range(96, 101)
        },

        "Thieu 5 cau mau Viet tranh"
    )

    # ================================================
    # 12. KIEM TRA DANG DAP AN 1-100
    # ================================================

    for number in range(1, 86):
        answer = answers[str(number)]

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
            f"Cau {number}: sai dap an {answer}"
        )

    for number in range(86, 96):
        answer = answers[str(number)]

        require(
            isinstance(answer, str)
            and bool(answer.strip()),

            f"Cau Viet {number} rong"
        )

    for number in range(96, 101):
        key = str(number)

        require(
            answers[key] is None,
            f"Cau {number} phai dap_an=null"
        )

        values = references[key]

        require(
            isinstance(values, list)
            and bool(values)

            and all(
                isinstance(value, str)
                and bool(compact(value))
                and WORDS[number] in value

                for value in values
            ),

            f"Cau {number} sai cau mau"
        )

    # ================================================
    # 13. DOI CHIEU 85 DAP AN NGHE VA DOC
    # ================================================

    official = {}

    text = clean_answer_text(
        key_doc[16].get_text("text")
    )

    matches = re.findall(
        r"(?<!\d)"
        r"(\d{1,3})"
        r"\s*[.．、]\s*"
        r"([A-F√×]{1,3})"
        r"(?![A-Z])",
        text
    )

    for key, value in matches:
        if not 1 <= int(key) <= 85:
            continue

        require(
            key not in official,
            f"Trung dap an PDF cau {key}"
        )

        official[key] = value

    require(
        set(official) == {
            str(number)
            for number in range(1, 86)
        },

        "PDF trang 17 thieu 85 dap an"
    )

    for number in range(1, 86):
        key = str(number)

        require(
            answers[key] == official[key],

            f"Cau {number}: JSON khac PDF trang 17"
        )

    # ================================================
    # 14. DOI CHIEU CUM TU VIET
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

            "Cum tu Viet khac PDF trang 15"
        )

    # ================================================
    # 15. DOI CHIEU DAP AN VIET TRANG 18
    # ================================================

    key_text = clean_answer_text(
        key_doc[17].get_text("text")
    )

    require(
        "第一部分" in key_text
        and "第二部分" in key_text,

        "PDF trang 18 thieu hai phan Viet"
    )

    first_part, second_part = key_text.split(
        "第二部分",
        1
    )

    pdf_writing = numbered_answers(
        first_part,
        86,
        95
    )

    pdf_open = numbered_answers(
        second_part,
        96,
        100
    )

    # ================================================
    # 16. KIEM TRA VIET SAP XEP 86-95
    # ================================================

    for number in range(86, 96):
        key = str(number)

        official_variants = [
            value

            for value in re.split(
                r"[/／]",
                pdf_writing[key]
            )

            if value
        ]

        require(
            [
                compact(value)
                for value in official_variants
            ] == [compact(answers[key])],

            f"Cau {number}: dap an Viet khac PDF"
        )

        possible = {
            compact("".join(order))

            for order in permutations(
                tokens[number]
            )
        }

        require(
            compact(answers[key]) in possible,

            f"Cau {number}: khong ghep duoc "
            "dap an tu cum tu PDF"
        )

    # ================================================
    # 17. KIEM TRA 5 CAU MAU VIET TRANH
    # ================================================

    for number in range(96, 101):
        key = str(number)

        require(
            compact(pdf_open[key]) in [
                compact(value)
                for value in references[key]
            ],

            f"Cau {number}: cau mau khac PDF "
            "hoac dinh watermark"
        )

    return (
        answers,
        alternatives,
        references,
        words,
        tokens
    )


# =====================================================
# 18. KIEM TRA MANIFEST BUOC 2
# =====================================================

def validate_manifest(manifest, words):

    require(
        (
            manifest.get("cap_hsk"),
            manifest.get("so_de"),
            manifest.get("ma_de_goc"),
            manifest.get("so_cau")
        ) == (4, DE_NUMBER, CODE, 100),

        "Manifest khong phai De 8 / 100 cau"
    )

    require(
        manifest.get("so_trang_pdf") == 16
        and manifest.get("trang_loi_thoai") == []
        and manifest.get("trang_dap_an") == [17, 18]
        and manifest.get("nguon_dap_an") == "pdf_rieng",

        "Manifest sai cau truc PDF"
    )

    require(
        Path(
            manifest.get("file_dap_an_pdf") or ""
        ).resolve() == ANSWER_PDF.resolve(),

        "Manifest sai duong dan PDF dap an"
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

        "Manifest thieu 2 bang A-F"
    )

    copies = []

    # ================================================
    # 19. KIEM TRA 100 ANH
    # ================================================

    for number in range(1, 101):
        item = items[str(number)]

        relative = (
            f"questions/cau_{number:03d}.png"
        )

        require(
            item.get("trang_pdf") == page_for(number)
            and item.get("anh") == relative,

            f"Cau {number}: sai trang hoac anh"
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
                == words[str(number)],

                f"Cau {number}: sai tu goi y"
            )

        if 80 <= number <= 85:

            if number <= 81:
                shared = "80-81"

            elif number <= 83:
                shared = "82-83"

            else:
                shared = "84-85"

            require(
                item.get("nhom_doc_chung") == shared,

                f"Cau {number}: sai nhom Doc {shared}"
            )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    # ================================================
    # 20. KIEM TRA HAI BANG A-F
    # ================================================

    for name, expected in GROUPS.items():
        page, first, last, letters = expected

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
            letters,
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

        "Khong du 100 anh va 2 bang"
    )

    return items, copies


# =====================================================
# 21. KIEM TRA MEDIA TRUOC KHI COPY
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

                "Media da ton tai voi noi dung khac.\n"
                "KHONG ghi de:\n"
                + str(destination)
            )


# =====================================================
# 22. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 08 - BUOC 3")
    print("CHUAN HOA H41328")
    print("=" * 60)

    # ================================================
    # 23. KIEM TRA FILE NGUON
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
    # 24. DOI CHIEU HAI PDF
    # ================================================

    with fitz.open(PDF_FILE) as exam, \
         fitz.open(ANSWER_PDF) as key_doc:

        require(
            len(exam) == 16
            and CODE in exam[0].get_text("text")
            and CODE in exam[15].get_text("text"),

            "PDF de khong phai H41328 / 16 trang"
        )

        require(
            len(key_doc) == 18
            and CODE in key_doc[0].get_text("text")
            and CODE in key_doc[16].get_text("text")
            and "卷答案" in key_doc[16].get_text("text"),

            "PDF dap an khong phai H41328 / 18 trang"
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
    # 25. KIEM TRA MANIFEST
    # ================================================

    items, copies = validate_manifest(
        manifest,
        words
    )

    # ================================================
    # 26. DOC THOI LUONG MP3
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
    # 27. TAO 100 CAU HOI
    # ================================================

    questions = []

    for number in range(1, 101):

        key = str(number)
        item = items[key]

        other = alternatives.get(
            key,
            []
        )

        # Viet sap xep 86-95.
        if 86 <= number <= 95:

            answer = (
                [answers[key]] + other
                if other
                else answers[key]
            )

            options = [
                {
                    "ma": str(index + 1),
                    "nhan": value
                }

                for index, value
                in enumerate(tokens[number])
            ]

        # Viet theo tranh 96-100.
        elif number >= 96:

            answer = {
                "che_do": "cham_tu_dong_theo_mau",
                "tu_cho_san": words[key],
                "dap_an_tham_khao": references[key]
            }

            options = []

        # Nghe va Doc 1-85.
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
                "hsk4/de_08/"
                + item["anh"]
            ),

            "anh_nhom_lua_chon": (
                "/static/media/luyen_thi/"
                "hsk4/de_08/groups/"
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

        "ten_hien_thi": "Đề 8",

        "so_cau": 100,

        "so_cau_nghe": 45,
        "so_cau_doc": 40,
        "so_cau_viet": 15,

        "thoi_gian_phut": 100,

        "thoi_gian_pdf_phut": 105,

        "so_trang_pdf_de": 16,

        "trang_cau_hoi": list(range(2, 17)),

        "trang_loi_thoai": [],

        "trang_dap_an": [17, 18],

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

        "dap_an_tham_khao_viet_mo": references,

        "cau_can_cham_thu_cong": [],

        "che_do_cham_viet_mo": (
            "cham_tu_dong_theo_mau"
        ),

        "san_sang_nhap_sql": True,

        "cau_hoi": questions
    }

    # ================================================
    # 29. KHONG GHI DE JSON CU
    # ================================================

    content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    require(
        not FINAL_FILE.exists()
        or FINAL_FILE.read_bytes() == content,

        "de_08.json da ton tai voi noi dung khac.\n"
        "KHONG ghi de:\n"
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
    print("HOAN THANH CHUAN HOA HSK4 DE 08")
    print("=" * 60)

    print("Ma de goc: H41328")
    print("Ten hien thi: De 8")

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
