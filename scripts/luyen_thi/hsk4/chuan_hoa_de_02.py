
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK4 DE 02 (H41002)
BUOC 3 - CHUAN HOA 100 CAU VA MEDIA

Ke thua dinh dang JSON da kiem thu o H41001.

- Kiem tra dap an buoc 1 voi PDF goc.
- Kiem tra manifest 100 cau buoc 2.
- Kiem tra cau Viet 86-95.
- Giu 2 dap an hop le cua cau 91.
- Cau 96-100 cham TU DONG theo cau mau.
- Sao chep 100 anh va 2 bang lua chon.
- Sao chep MP3.
- Tao de_02.json de kiem tra va nhap SQL.

KHONG ket noi SQL Server.
KHONG sua H41001.
KHONG sua cac bang Bai tap cu.
"""

from pathlib import Path
from itertools import permutations

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

DATA = BASE / "hsk4" / "data" / "de_02"

OUTPUT = BASE / "hsk4" / "output" / "de_02"

MEDIA_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk4"
)

MEDIA = MEDIA_ROOT / "de_02"

PDF_FILE = SOURCE / "H41002.pdf"

MP3_FILE = SOURCE / "H41002.mp3"

ANSWER_FILE = DATA / "de_02_dap_an.json"

MANIFEST_FILE = (
    DATA / "hinh_100_cau_ung_vien.json"
)

FINAL_FILE = DATA / "de_02.json"

CODE = "H41002"


# =====================================================
# 2. TU CHO SAN VIET THEO TRANH
# =====================================================

WORDS = {
    96: "吃惊",
    97: "汗",
    98: "挂",
    99: "香",
    100: "杂志",
}


# =====================================================
# 3. BANG LUA CHON CHUNG
# =====================================================

GROUPS = {
    "doc_46_50": (
        7, 46, 50, "ABCDEF"
    ),

    "doc_51_55": (
        8, 51, 55, "ABCDEF"
    ),
}


# =====================================================
# 4. SO DO TRANG PDF
# =====================================================

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
# 5. HAM KIEM TRA
# =====================================================

def require(condition, message):

    if not condition:
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
# 6. XAC DINH TRANG PDF
# =====================================================

def page_for(number):

    for page, numbers in PAGE_MAP.items():

        if number in numbers:
            return page

    raise RuntimeError(
        f"Khong tim thay trang cau {number}"
    )


# =====================================================
# 7. XAC DINH KY NANG
# =====================================================

def skill_for(number):

    if number <= 45:
        return "nghe"

    if number <= 85:
        return "doc"

    return "viet"


# =====================================================
# 8. XAC DINH PHAN THI
# =====================================================

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


# =====================================================
# 9. XAC DINH DANG CAU HOI
# =====================================================

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


# =====================================================
# 10. CAC LUA CHON
# =====================================================

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
# 11. DOC CUM TU VIET TU PDF
# =====================================================

def tokens_from_pdf(doc):

    tokens = {}

    for line in doc[14].get_text(
        "text"
    ).splitlines():

        match = re.match(
            r"^\s*(8[6-9]|9[0-5])"
            r"\s*[.．、]\s*(.+)$",

            line
        )

        if not match:
            continue

        number = int(
            match.group(1)
        )

        values = [
            item.strip()

            for item in re.split(
                r"\s+",
                match.group(2)
            )

            if item.strip()
        ]

        require(
            number not in tokens,
            f"Trung cau Viet {number} o PDF"
        )

        require(
            3 <= len(values) <= 9,
            f"Cau {number} sai so cum tu: {values}"
        )

        tokens[number] = values

    require(
        set(tokens) == set(
            range(86, 96)
        ),

        "Trang 15 khong du 10 cau Viet. "
        f"Tim thay: {sorted(tokens)}"
    )

    return tokens


# =====================================================
# 12. TACH DAP AN VIET TU TRANG 24
# =====================================================

def numbered_answers(
    text,
    first,
    last
):

    matches = list(
        re.finditer(
            r"(?m)^\s*(\d{2,3})\s*[.．、]",
            text
        )
    )

    result = {}

    for index, match in enumerate(matches):

        number = int(
            match.group(1)
        )

        if not first <= number <= last:
            continue

        end = (
            matches[index + 1].start()

            if index + 1 < len(matches)

            else len(text)
        )

        value = re.sub(
            r"\s+",
            "",
            text[
                match.end():end
            ]
        )

        result[str(number)] = value

    require(
        set(result) == {
            str(n)
            for n in range(
                first,
                last + 1
            )
        },

        f"Khong du dap an {first}-{last}"
    )

    return result


# =====================================================
# 13. KIEM TRA DAP AN BUOC 1
# =====================================================

def validate_answers(source, doc):

    identity = (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc")
    )

    require(
        identity == (4, 2, CODE),
        "JSON buoc 1 khong phai H41002."
    )

    counts = (
        source.get("tong_cau"),
        source.get("so_cau_nghe"),
        source.get("so_cau_doc"),
        source.get("so_cau_viet")
    )

    require(
        counts == (100, 45, 40, 15),
        "Sai so cau JSON buoc 1."
    )

    require(
        Path(
            source.get("file_pdf") or ""
        ).resolve() == PDF_FILE.resolve(),

        "PDF buoc 1 khong khop."
    )

    require(
        Path(
            source.get("file_mp3") or ""
        ).resolve() == MP3_FILE.resolve(),

        "MP3 buoc 1 khong khop."
    )

    # ================================================
    # 14. KIEM TRA CHE DO CHAM
    # ================================================

    require(
        source.get(
            "cau_can_cham_thu_cong"
        ) == [],

        "De 2 khong duoc cham thu cong."
    )

    require(
        source.get(
            "che_do_cham_viet_mo"
        ) == "cham_tu_dong_theo_mau",

        "Sai che do cham Viet theo tranh."
    )

    answers = source.get(
        "dap_an"
    ) or {}

    require(
        set(answers) == {
            str(n)
            for n in range(1, 101)
        },

        "JSON buoc 1 khong du 100 dap an."
    )

    # ================================================
    # 15. KIEM TRA DAP AN NGHE/DOC
    # ================================================

    for number in range(1, 86):

        answer = answers[
            str(number)
        ]

        if 56 <= number <= 65:

            valid = (
                isinstance(answer, str)
                and len(answer) == 3
                and set(answer) == set("ABC")
            )

        else:

            valid = (
                answer in choices_for(number)
            )

        require(
            valid,

            f"Dap an cau {number} "
            f"sai dinh dang: {answer}"
        )

    # ================================================
    # 16. KIEM TRA VIET SAP XEP
    # ================================================

    for number in range(86, 96):

        answer = answers[
            str(number)
        ]

        require(
            isinstance(answer, str)
            and bool(answer.strip()),

            f"Thieu dap an Viet {number}"
        )

    # ================================================
    # 17. VIET TRANH CO DAP AN RIENG
    # ================================================

    for number in range(96, 101):

        require(
            answers[str(number)] is None,

            f"Buoc 1 cau {number} "
            "phai de dap_an = null."
        )

    alternatives = source.get(
        "dap_an_thay_the"
    ) or {}

    # H41002 chi co cau 91 co hai dap an.
    require(
        set(alternatives) == {"91"}

        and isinstance(
            alternatives["91"],
            list
        )

        and len(
            alternatives["91"]
        ) == 1,

        "De 2 chi co cau 91 "
        "co mot dap an thay the."
    )

    words = source.get(
        "tu_cho_san_viet_mo"
    ) or {}

    expected_words = {
        str(number): word

        for number, word
        in WORDS.items()
    }

    require(
        words == expected_words,

        "Tu goi y 96-100 "
        "khong khop PDF H41002."
    )

    references = source.get(
        "dap_an_tham_khao_viet_mo"
    ) or {}

    require(
        set(references) == {
            str(n)
            for n in range(96, 101)
        },

        "Khong du 5 dap an mau "
        "Viet theo tranh."
    )

    for number in range(96, 101):

        values = references[
            str(number)
        ]

        require(
            isinstance(values, list)
            and bool(values)

            and all(
                isinstance(value, str)
                and bool(compact(value))
                and WORDS[number] in value

                for value in values
            ),

            f"Cau {number} thieu "
            "cau mau hoac tu goi y."
        )

    # ================================================
    # 18. DOI CHIEU 85 DAP AN VOI PDF
    # ================================================

    official = {}

    pattern = (
        r"(?<!\d)"
        r"(\d{1,3})"
        r"\s*[.．、]\s*"
        r"([A-F√×]{1,3})"
        r"(?![A-Z])"
    )

    matches = re.findall(
        pattern,
        doc[22].get_text("text")
    )

    for key, value in matches:

        if 1 <= int(key) <= 85:

            require(
                key not in official,

                f"Trung dap an cau {key} "
                "trang 23."
            )

            official[key] = value

    require(
        set(official) == {
            str(n)
            for n in range(1, 86)
        },

        "PDF trang 23 "
        "khong tach du 85 dap an."
    )

    for number in range(1, 86):

        key = str(number)

        require(
            answers[key] == official[key],

            f"Cau {number}: "
            "dap an JSON khac PDF H41002."
        )

    # ================================================
    # 19. KIEM TRA CUM TU VIET
    # ================================================

    tokens = tokens_from_pdf(doc)

    source_tokens = source.get(
        "cum_tu_viet_sap_xep"
    )

    if source_tokens is not None:

        require(
            source_tokens == {
                str(n): tokens[n]
                for n in range(86, 96)
            },

            "Cum tu Viet buoc 1 "
            "khac PDF trang 15."
        )

    for number in range(86, 96):

        values = tokens[number]

        candidates = [
            answers[str(number)]
        ] + alternatives.get(
            str(number),
            []
        )

        possible = {
            compact(
                "".join(order)
            )

            for order in permutations(
                values
            )
        }

        for answer in candidates:

            require(
                compact(answer) in possible,

                f"Cau {number} khong "
                f"ghep duoc dap an: {answer}\n"
                f"Cum tu: {values}"
            )

    # ================================================
    # 20. DOI CHIEU DAP AN VIET TRANG 24
    # ================================================

    pdf_text = doc[23].get_text(
        "text"
    )

    require(
        "第一部分" in pdf_text
        and "第二部分" in pdf_text,

        "Trang 24 thieu phan Viet."
    )

    part_one, part_two = pdf_text.split(
        "第二部分",
        1
    )

    pdf_writing = numbered_answers(
        part_one,
        86,
        95
    )

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

        stored_variants = [
            answers[key]
        ] + alternatives.get(
            key,
            []
        )

        require(
            [
                compact(value)
                for value in official_variants
            ] == [
                compact(value)
                for value in stored_variants
            ],

            f"Cau {number}: "
            "dap an Viet khac trang 24."
        )

    pdf_open = numbered_answers(
        part_two,
        96,
        100
    )

    for number in range(96, 101):

        key = str(number)

        require(
            compact(pdf_open[key]) in [
                compact(value)
                for value in references[key]
            ],

            f"Cau {number}: "
            "cau mau khong khop PDF."
        )

    return (
        answers,
        alternatives,
        references,
        words,
        tokens
    )


# =====================================================
# 21. KIEM TRA MANIFEST BUOC 2
# =====================================================

def validate_manifest(manifest, words):

    identity = (
        manifest.get("cap_hsk"),
        manifest.get("so_de"),
        manifest.get("ma_de_goc"),
        manifest.get("so_cau")
    )

    require(
        identity == (4, 2, CODE, 100),

        "Manifest buoc 2 "
        "khong phai H41002."
    )

    structure = (
        manifest.get("so_trang_pdf"),
        manifest.get("trang_loi_thoai"),
        manifest.get("trang_dap_an")
    )

    require(
        structure == (
            24,
            list(range(17, 23)),
            [23, 24]
        ),

        "Manifest sai cau truc PDF."
    )

    require(
        manifest.get(
            "cau_can_cham_thu_cong"
        ) == []

        and manifest.get(
            "che_do_cham_viet_mo"
        ) == "cham_tu_dong_theo_mau",

        "Manifest chua cham tu dong."
    )

    items = manifest.get(
        "cau_hoi"
    ) or {}

    require(
        set(items) == {
            str(n)
            for n in range(1, 101)
        },

        "Manifest thieu 100 cau."
    )

    groups = manifest.get(
        "bang_lua_chon"
    ) or {}

    require(
        set(groups) == set(GROUPS),

        "Manifest thieu 2 bang A-F."
    )

    copies = []

    # ================================================
    # 22. KIEM TRA 100 ANH
    # ================================================

    for number in range(1, 101):

        item = items[
            str(number)
        ]

        relative = (
            "questions/"
            f"cau_{number:03d}.png"
        )

        require(
            item.get("trang_pdf")
            == page_for(number)

            and item.get("anh")
            == relative,

            f"Cau {number}: "
            "sai anh hoac trang PDF."
        )

        if 46 <= number <= 50:

            group = "doc_46_50"

        elif 51 <= number <= 55:

            group = "doc_51_55"

        else:

            group = None

        require(
            item.get(
                "nhom_lua_chon"
            ) == group,

            f"Cau {number}: "
            "sai nhom lua chon."
        )

        if number >= 96:

            require(
                item.get(
                    "tu_cho_san"
                ) == words[str(number)],

                f"Cau {number}: "
                "hinh khong dung tu goi y."
            )

        # ============================================
        # 23. DOAN DOC CHUNG
        # ============================================

        if 80 <= number <= 85:

            if number <= 81:
                shared = "80-81"

            elif number <= 83:
                shared = "82-83"

            else:
                shared = "84-85"

            require(
                item.get(
                    "nhom_doc_chung"
                ) == shared,

                f"Cau {number}: "
                f"sai nhom Doc {shared}."
            )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    # ================================================
    # 24. HAI BANG LUA CHON
    # ================================================

    for name, expected in GROUPS.items():

        page, first, last, letters = (
            expected
        )

        item = groups[name]

        actual = (
            item.get("trang_pdf"),
            item.get("cau_tu"),
            item.get("cau_den"),
            item.get("lua_chon"),
            item.get("anh")
        )

        expected_values = (
            page,
            first,
            last,
            letters,
            f"groups/{name}.png"
        )

        require(
            actual == expected_values,

            f"Bang {name}: sai du lieu."
        )

        relative = (
            f"groups/{name}.png"
        )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    require(
        len(copies) == 102,

        "Khong du 100 anh va 2 bang."
    )

    return items, copies


# =====================================================
# 25. KIEM TRA MEDIA TRUOC KHI SAO CHEP
# =====================================================

def inspect_media(copies):

    for source_file, destination in copies:

        require_file(source_file)

        if source_file.suffix.lower() == ".png":

            with source_file.open("rb") as stream:

                require(
                    stream.read(8)
                    == b"\x89PNG\r\n\x1a\n",

                    "Anh PNG khong hop le: "
                    + str(source_file)
                )

        if destination.exists():

            require(
                filecmp.cmp(
                    source_file,
                    destination,
                    shallow=False
                ),

                "Media da ton tai "
                "voi noi dung khac: "
                + str(destination)
            )


# =====================================================
# 26. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)

    print(
        "MOC HAN - HSK4 DE 02 - BUOC 3"
    )

    print(
        "CHUAN HOA H41002"
    )

    print("=" * 60)

    require_file(PDF_FILE)
    require_file(MP3_FILE)

    source = read_json(
        ANSWER_FILE
    )

    manifest = read_json(
        MANIFEST_FILE
    )

    # ================================================
    # 27. KIEM TRA PDF VA DAP AN
    # ================================================

    with fitz.open(PDF_FILE) as doc:

        require(
            len(doc) == 24

            and CODE in doc[0].get_text(
                "text"
            )

            and CODE in doc[22].get_text(
                "text"
            ),

            "PDF khong phai H41002."
        )

        (
            answers,
            alternatives,
            references,
            words,
            tokens
        ) = validate_answers(
            source,
            doc
        )

    # ================================================
    # 28. KIEM TRA MANIFEST
    # ================================================

    items, copies = validate_manifest(
        manifest,
        words
    )

    # ================================================
    # 29. DOC THOI LUONG MP3
    # ================================================

    try:

        duration = round(
            float(
                MP3(
                    str(MP3_FILE)
                ).info.length
            ),
            2
        )

    except Exception as exc:

        raise RuntimeError(
            f"Khong doc duoc MP3: {exc}"
        ) from exc

    require(
        0 < duration < 10000,

        "Thoi luong MP3 bat thuong."
    )

    copies.append((
        MP3_FILE,
        MEDIA_ROOT / f"{CODE}.mp3"
    ))

    inspect_media(
        copies
    )

    # ================================================
    # 30. TAO 100 CAU HOI
    # ================================================

    questions = []

    for number in range(1, 101):

        key = str(number)

        item = items[key]

        labels = choices_for(
            number
        )

        other = alternatives.get(
            key,
            []
        )

        # ============================================
        # 31. XAC DINH DAP AN VA LUA CHON
        # ============================================

        if 86 <= number <= 95:

            values = tokens[number]

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

                for index, value
                in enumerate(values)
            ]

        elif number >= 96:

            # Khong con cham_thu_cong.
            # Backend HSK4 se so sanh
            # voi tung cau trong danh sach nay.

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

        else:

            answer = answers[key]

            options = [
                {
                    "ma": value,
                    "nhan": value
                }

                for value in labels
            ]

        # ============================================
        # 32. BANG LUA CHON CHUNG
        # ============================================

        group = item.get(
            "nhom_lua_chon"
        )

        # ============================================
        # 33. TAO DOI TUONG CAU HOI
        # ============================================

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
                "hsk4/de_02/"
                + item["anh"]
            ),

            "anh_nhom_lua_chon": (
                "/static/media/luyen_thi/"
                "hsk4/de_02/groups/"
                f"{group}.png"

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

            question["tu_cho_san"] = (
                words[key]
            )

        questions.append(
            question
        )

    # ================================================
    # 34. JSON CHUAN CUOI CUNG
    # ================================================

    result = {
        "ma_de_goc": CODE,

        "cap_hsk": 4,

        "so_de": 2,
        "thu_tu": 2,

        "ten_hien_thi": "Đề 2",

        "so_cau": 100,

        "so_cau_nghe": 45,
        "so_cau_doc": 40,
        "so_cau_viet": 15,

        "thoi_gian_phut": 100,

        "thoi_gian_pdf_phut": 105,

        "so_trang_pdf_de": 24,

        "trang_cau_hoi": list(
            range(2, 17)
        ),

        "trang_loi_thoai": list(
            range(17, 23)
        ),

        "trang_dap_an": [
            23, 24
        ],

        "nguon_dap_an": "pdf_chung",

        "file_pdf": str(PDF_FILE),

        "file_mp3": str(MP3_FILE),

        "audio": {
            "duong_dan": (
                "/static/media/luyen_thi/"
                f"hsk4/{CODE}.mp3"
            ),

            "thoi_luong_giay": duration
        },

        "dap_an_thay_the": (
            alternatives
        ),

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
    # 35. KIEM TRA KHONG GHI DE JSON KHAC
    # ================================================

    content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    require(
        not FINAL_FILE.exists()

        or FINAL_FILE.read_bytes() == content,

        "JSON de_02.json da ton tai "
        "voi noi dung khac."
        "\nKHONG ghi de: "
        + str(FINAL_FILE)
    )

    # ================================================
    # 36. SAO CHEP MEDIA
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
    # 37. LUU JSON
    # ================================================

    if not FINAL_FILE.exists():

        FINAL_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        FINAL_FILE.write_bytes(
            content
        )

    # ================================================
    # 38. KET QUA
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH CHUAN HOA HSK4 DE 02"
    )

    print("=" * 60)

    print("Ma de: H41002")
    print("Ten hien thi: De 2")

    print("Tong cau: 100")

    print("Nghe: 45/45")
    print("Doc: 40/40")

    print("Viet sap xep: 10/10")

    print(
        "Viet theo tranh: "
        "5/5 cau mau"
    )

    print(
        "Che do cham: TU DONG"
    )

    print(
        "Dap an thay the: cau 91"
    )

    print("Anh cau hoi: 100/100")
    print("Bang lua chon: 2/2")

    print(
        f"MP3: {duration} giay"
    )

    print(
        "Thoi gian thi: 100 phut"
    )

    print(
        f"\nJSON: {FINAL_FILE}"
    )

    print(
        "\nCHUA thay doi SQL Server."
    )


if __name__ == "__main__":
    main()
