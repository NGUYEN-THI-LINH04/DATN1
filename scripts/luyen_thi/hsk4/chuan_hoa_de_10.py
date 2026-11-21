
# -*- coding: utf-8 -*-
"""
MOC HAN - HSK4 DE 10 (H41330)
BUOC 3 - CHUAN HOA 100 CAU VA MEDIA

Ke thua cau truc chuan hoa De 9:
- PDF de 16 trang, PDF dap an rieng 2 trang.
- Doi chieu dap an Nghe/Doc 1-85 voi PDF dap an.
- Kiem tra cum tu Viet 86-95.
- Giu '将于15 分钟后' o cau 95.
- Viet tranh 96-100 cham TU DONG theo cau mau.
- Kiem tra 100 anh va 2 bang A-F.
- Sao chep media va MP3.
- Tao de_10.json cho script nhap SQL.

KHONG ket noi SQL.
KHONG sua cac de 1-9 hoac bang Bai tap.
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
    os.environ.get("MOC_HAN_ROOT", r"D:\DATN1")
)

BASE = ROOT / "scripts" / "luyen_thi"
SOURCE = BASE / "source" / "De_HSK" / "HSK4"

DATA = BASE / "hsk4" / "data" / "de_10"
OUTPUT = BASE / "hsk4" / "output" / "de_10"

MEDIA_ROOT = (
    ROOT / "static" / "media" / "luyen_thi" / "hsk4"
)

MEDIA = MEDIA_ROOT / "de_10"

PDF_FILE = SOURCE / "H41010.pdf"
ANSWER_PDF = SOURCE / "H41010_dap_an.pdf"
MP3_FILE = SOURCE / "H41010.mp3"

ANSWER_FILE = DATA / "de_10_dap_an.json"

MANIFEST_FILE = (
    DATA / "hinh_100_cau_ung_vien.json"
)

FINAL_FILE = DATA / "de_10.json"

CODE = "H41330"
DE_NUMBER = 10
AUDIO_NAME = "H41010.mp3"

WORDS = {
    96: "零钱",
    97: "俩",
    98: "严重",
    99: "猜",
    100: "挂",
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

def require(condition, message):
    if not condition:
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
# 3. TRANG, KY NANG, DANG CAU HOI
# =====================================================

def page_for(number):
    for page, numbers in PAGE_MAP.items():
        if number in numbers:
            return page

    raise RuntimeError(
        f"Khong tim thay trang cau {number}"
    )


def skill_for(n):
    if n <= 45:
        return "nghe"

    if n <= 85:
        return "doc"

    return "viet"


def part_for(n):
    if n <= 10:
        return "Nghe - Phần 1"

    if n <= 25:
        return "Nghe - Phần 2"

    if n <= 45:
        return "Nghe - Phần 3"

    if n <= 55:
        return "Đọc - Phần 1"

    if n <= 65:
        return "Đọc - Phần 2"

    if n <= 85:
        return "Đọc - Phần 3"

    if n <= 95:
        return "Viết - Phần 1"

    return "Viết - Phần 2"


def kind_for(n):
    if n <= 10:
        return "dung_sai"

    if n <= 45:
        return "chon_mot"

    if n <= 55:
        return "ghep_lua_chon"

    if n <= 65:
        return "sap_xep_abc"

    if n <= 85:
        return "chon_mot"

    if n <= 95:
        return "sap_xep"

    return "viet_cau_theo_tranh"


def choices_for(n):
    if n <= 10:
        return ["√", "×"]

    if n <= 45:
        return list("ABCD")

    if n <= 55:
        return list("ABCDEF")

    if n <= 65:
        return list("ABC")

    if n <= 85:
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

        n = int(match.group(1))

        values = [
            item.strip()

            for item in re.split(
                r"\s{2,}",
                match.group(2).strip()
            )

            if item.strip()
        ]

        require(
            n not in tokens,
            f"Trung cum tu cau {n}"
        )

        require(
            3 <= len(values) <= 9,
            f"Cau {n} sai cum tu: {values}"
        )

        tokens[n] = values

    require(
        set(tokens) == set(range(86, 96)),
        "Trang 15 khong du 10 cau Viet 86-95"
    )

    # Giu nguyen cum thoi gian o cau 95.
    require(
        "将于15 分钟后" in tokens[95],
        "Cau 95 phai giu nguyen "
        "cum '将于15 分钟后'"
    )

    return tokens


# =====================================================
# 5. DOC DAP AN VIET TU PDF RIENG
# =====================================================

def numbered_answers(text, first, last):

    matches = list(
        re.finditer(
            r"(?m)^\s*(\d{2,3})\s*[.．、]",
            text
        )
    )

    result = {}

    for i, match in enumerate(matches):

        n = int(match.group(1))

        if not first <= n <= last:
            continue

        key = str(n)

        require(
            key not in result,
            f"Trung dap an Viet cau {n}"
        )

        end = (
            matches[i + 1].start()
            if i + 1 < len(matches)
            else len(text)
        )

        answer = re.sub(
            r"\s+",
            "",
            text[match.end():end]
        )

        require(
            bool(answer),
            f"Dap an Viet cau {n} rong"
        )

        result[key] = answer

    require(
        set(result) == {
            str(n)
            for n in range(first, last + 1)
        },
        f"PDF dap an thieu cau {first}-{last}"
    )

    return result


# =====================================================
# 6. DOI CHIEU JSON BUOC 1 VOI HAI PDF
# =====================================================

def validate_answers(source, exam, key_doc):

    require(
        (
            source.get("cap_hsk"),
            source.get("so_de"),
            source.get("ma_de_goc")
        ) == (4, DE_NUMBER, CODE),
        "JSON buoc 1 khong phai De 10 / H41330"
    )

    require(
        tuple(
            source.get(k)
            for k in (
                "tong_cau",
                "so_cau_nghe",
                "so_cau_doc",
                "so_cau_viet"
            )
        ) == (100, 45, 40, 15),
        "JSON buoc 1 sai tong so cau"
    )

    # Kiem tra duong dan 3 file nguon.
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

    # Kiem tra cau truc PDF 16+2 trang.
    require(
        source.get("so_trang_pdf") == 16
        and source.get("trang_loi_thoai") == []
        and source.get("trang_dap_an") == [1, 2]
        and source.get("nguon_dap_an") == "pdf_rieng",
        "JSON buoc 1 sai cau truc PDF 16+2 trang"
    )

    # ================================================
    # 7. KIEM TRA CHAM VIET TU DONG
    # ================================================

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
            str(n) for n in range(1, 101)
        },
        "JSON buoc 1 thieu 100 dap an"
    )

    # De 10 khong co dap an thay the.
    alternatives = source.get(
        "dap_an_thay_the"
    )

    require(
        alternatives == {},
        "De 10 khong co dap an thay the"
    )

    # ================================================
    # 8. KIEM TRA TU GOI Y VA CAU MAU
    # ================================================

    words = source.get(
        "tu_cho_san_viet_mo"
    ) or {}

    require(
        words == {
            str(n): WORDS[n]
            for n in range(96, 101)
        },
        "Sai 5 tu goi y Viet theo tranh"
    )

    references = source.get(
        "dap_an_tham_khao_viet_mo"
    ) or {}

    require(
        isinstance(references, dict)
        and set(references) == {
            str(n) for n in range(96, 101)
        },
        "Thieu 5 cau mau Viet theo tranh"
    )

    # ================================================
    # 9. DOI CHIEU 85 DAP AN NGHE VA DOC
    # ================================================

    official = {}

    text = key_doc[0].get_text("text")

    matches = re.findall(
        r"(?<!\d)"
        r"(\d{1,3})"
        r"\s*[.．、]\s*"
        r"([A-F√×]{1,3})"
        r"(?![A-Z])",
        text
    )

    for number_text, value in matches:

        n = int(number_text)

        if not 1 <= n <= 85:
            continue

        key = str(n)

        require(
            key not in official,
            f"Trung dap an PDF cau {n}"
        )

        official[key] = value

    require(
        set(official) == {
            str(n) for n in range(1, 86)
        },
        "PDF dap an trang 1 khong du 85 cau"
    )

    for n in range(1, 86):

        answer = answers[str(n)]

        if 56 <= n <= 65:

            valid = (
                isinstance(answer, str)
                and len(answer) == 3
                and set(answer) == set("ABC")
            )

        else:

            valid = answer in choices_for(n)

        require(
            valid,
            f"Cau {n} sai dang dap an: {answer}"
        )

        require(
            answer == official[str(n)],
            f"Cau {n} khac PDF dap an"
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
                str(n): tokens[n]
                for n in range(86, 96)
            },
            "Cum tu Viet buoc 1 khac PDF de"
        )

    # ================================================
    # 11. DOC DAP AN VIET TRANG 2
    # ================================================

    text = key_doc[1].get_text("text")

    require(
        "第一部分" in text
        and "第二部分" in text,
        "PDF dap an trang 2 thieu hai phan Viet"
    )

    first_part, second_part = text.split(
        "第二部分",
        1
    )

    pdf_writing = numbered_answers(
        first_part, 86, 95
    )

    pdf_open = numbered_answers(
        second_part, 96, 100
    )

    # ================================================
    # 12. KIEM TRA 10 CAU VIET SAP XEP
    # ================================================

    for n in range(86, 96):

        key = str(n)
        answer = answers[key]

        require(
            isinstance(answer, str)
            and bool(answer.strip()),
            f"Cau Viet {n} rong"
        )

        variants = [
            value
            for value in re.split(
                r"[/／]",
                pdf_writing[key]
            )
            if value
        ]

        require(
            len(variants) == 1
            and compact(variants[0]) == compact(answer),
            f"Cau {n} khac dap an PDF "
            "hoac co dap an thay the"
        )

        possible = {
            compact("".join(order))
            for order in permutations(tokens[n])
        }

        require(
            compact(answer) in possible,
            f"Cau {n} khong ghep duoc "
            "dap an tu cac cum tu"
        )

    # ================================================
    # 13. KIEM TRA 5 CAU MAU VIET TRANH
    # ================================================

    for n in range(96, 101):

        key = str(n)
        values = references[key]

        require(
            answers[key] is None,
            f"Cau {n} phai co dap_an=null"
        )

        require(
            isinstance(values, list)
            and bool(values)
            and all(
                isinstance(v, str)
                and bool(compact(v))
                and WORDS[n] in v
                for v in values
            ),
            f"Cau {n} thieu cau mau "
            "hoac tu goi y"
        )

        require(
            compact(pdf_open[key]) in [
                compact(v) for v in values
            ],
            f"Cau {n} co cau mau "
            "khac PDF dap an"
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
        "Manifest khong phai HSK4 De 10"
    )

    require(
        manifest.get("so_trang_pdf") == 16
        and manifest.get("trang_cau_hoi")
        == list(range(2, 17))
        and manifest.get("trang_loi_thoai") == []
        and manifest.get("trang_dap_an") == [1, 2]
        and manifest.get("nguon_dap_an") == "pdf_rieng"
        and Path(
            manifest.get("file_dap_an_pdf") or ""
        ).resolve() == ANSWER_PDF.resolve(),
        "Manifest sai cau truc "
        "hoac duong dan PDF dap an"
    )

    require(
        manifest.get("cau_can_cham_thu_cong") == []
        and manifest.get("che_do_cham_viet_mo")
        == "cham_tu_dong_theo_mau"
        and manifest.get("dap_an_thay_the") == {},
        "Manifest sai che do cham "
        "hoac dap an thay the"
    )

    items = manifest.get("cau_hoi") or {}

    groups = manifest.get(
        "bang_lua_chon"
    ) or {}

    require(
        isinstance(items, dict)
        and set(items) == {
            str(n) for n in range(1, 101)
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
    # 15. KIEM TRA 100 ANH
    # ================================================

    for n in range(1, 101):

        item = items[str(n)]

        relative = (
            f"questions/cau_{n:03d}.png"
        )

        require(
            item.get("trang_pdf") == page_for(n)
            and item.get("anh") == relative,
            f"Cau {n} sai trang "
            "hoac duong dan anh"
        )

        if 46 <= n <= 50:
            group = "doc_46_50"

        elif 51 <= n <= 55:
            group = "doc_51_55"

        else:
            group = None

        require(
            item.get("nhom_lua_chon") == group,
            f"Cau {n} sai nhom lua chon"
        )

        if n >= 96:
            require(
                item.get("tu_cho_san")
                == words[str(n)],
                f"Cau {n} sai tu goi y"
            )

        # Giu cac doan Doc chung.
        if 80 <= n <= 85:

            if n <= 81:
                shared = "80-81"

            elif n <= 83:
                shared = "82-83"

            else:
                shared = "84-85"

            require(
                item.get("nhom_doc_chung")
                == shared,
                f"Cau {n} sai nhom Doc {shared}"
            )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    # ================================================
    # 16. KIEM TRA HAI BANG A-F
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
            f"Bang {name} sai du lieu"
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
# 17. KIEM TRA MEDIA TRUOC KHI SAO CHEP
# =====================================================

def inspect_media(copies):

    for source_file, destination in copies:

        require_file(source_file)

        if source_file.suffix.lower() == ".png":

            with source_file.open("rb") as stream:

                require(
                    stream.read(8)
                    == b"\x89PNG\r\n\x1a\n",
                    f"PNG khong hop le: {source_file}"
                )

        if destination.exists():

            require(
                filecmp.cmp(
                    source_file,
                    destination,
                    shallow=False
                ),
                "Media da ton tai voi noi dung khac."
                " KHONG ghi de: "
                + str(destination)
            )


# =====================================================
# 18. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 10 - BUOC 3")
    print("CHUAN HOA H41330")
    print("=" * 60)

    # ================================================
    # 19. KIEM TRA FILE NGUON
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
    # 20. DOI CHIEU HAI PDF VA DAP AN
    # ================================================

    with fitz.open(PDF_FILE) as exam, \
         fitz.open(ANSWER_PDF) as key_doc:

        require(
            len(exam) == 16
            and CODE in exam[0].get_text("text")
            and CODE in exam[15].get_text("text"),
            "PDF de khong phai H41330 / 16 trang"
        )

        require(
            len(key_doc) == 2
            and CODE in key_doc[0].get_text("text")
            and "卷答案" in key_doc[0].get_text("text"),
            "PDF dap an khong phai H41330 / 2 trang"
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
    # 21. KIEM TRA MANIFEST
    # ================================================

    items, copies = validate_manifest(
        manifest,
        words
    )

    # ================================================
    # 22. DOC THOI LUONG MP3
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
    # 23. TAO 100 CAU HOI
    # ================================================

    questions = []

    for n in range(1, 101):

        key = str(n)
        item = items[key]

        other = alternatives.get(
            key,
            []
        )

        # Viet sap xep 86-95.
        if 86 <= n <= 95:

            answer = (
                [answers[key]] + other
                if other
                else answers[key]
            )

            options = [
                {
                    "ma": str(i + 1),
                    "nhan": value
                }
                for i, value
                in enumerate(tokens[n])
            ]

        # Viet theo tranh 96-100.
        elif n >= 96:

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
                for value in choices_for(n)
            ]

        group = item.get(
            "nhom_lua_chon"
        )

        question = {

            "so_cau": n,

            "ky_nang": skill_for(n),

            "phan": part_for(n),

            "loai_cau_hoi": kind_for(n),

            "noi_dung": (
                "Nhìn tranh và đặt câu với từ: "
                + words[key]
                if n >= 96
                else None
            ),

            "trang_pdf": item["trang_pdf"],

            "anh_cau_hoi": (
                "/static/media/luyen_thi/"
                "hsk4/de_10/"
                + item["anh"]
            ),

            "anh_nhom_lua_chon": (
                "/static/media/luyen_thi/"
                "hsk4/de_10/groups/"
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

        if n >= 96:
            question["dap_an_tham_khao"] = (
                references[key]
            )

            question["tu_cho_san"] = words[key]

        questions.append(question)

    # ================================================
    # 24. TAO JSON CUOI CUNG
    # ================================================

    result = {

        "ma_de_goc": CODE,

        "cap_hsk": 4,

        "so_de": DE_NUMBER,
        "thu_tu": DE_NUMBER,

        "ten_hien_thi": "Đề 10",

        "so_cau": 100,

        "so_cau_nghe": 45,
        "so_cau_doc": 40,
        "so_cau_viet": 15,

        "thoi_gian_phut": 100,

        "thoi_gian_pdf_phut": 105,

        "so_trang_pdf_de": 16,

        "trang_cau_hoi": list(range(2, 17)),

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
    # 25. KHONG GHI DE JSON KHAC NOI DUNG
    # ================================================

    content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    require(
        not FINAL_FILE.exists()
        or FINAL_FILE.read_bytes() == content,

        "de_10.json da ton tai voi noi dung khac."
        " KHONG ghi de: "
        + str(FINAL_FILE)
    )

    # ================================================
    # 26. SAO CHEP MEDIA
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
            f"Sao chep media bi loi: {destination}"
        )

    # ================================================
    # 27. LUU JSON
    # ================================================

    if not FINAL_FILE.exists():

        FINAL_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        FINAL_FILE.write_bytes(content)

    # ================================================
    # 28. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH CHUAN HOA HSK4 DE 10")
    print("=" * 60)

    print("Ma de goc: H41330")
    print("Ten hien thi: De 10")
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
