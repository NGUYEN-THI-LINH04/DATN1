
# -*- coding: utf-8 -*-
"""
MOC HAN - HSK4 DE 06 - BUOC 3

PDF: H41006.pdf
Ma de goc trong PDF: H41008
Ten hien thi: De 6

Ke thua quy trinh chuan hoa HSK4 De 5:
- Doi chieu dap an buoc 1 voi PDF.
- Kiem tra manifest 100 anh buoc 2.
- Kiem tra 2 bang lua chon A-F.
- Giu cac doan Doc chung 80-85.
- De nay KHONG co dap an thay the.
- Cau 96-100 cham TU DONG theo mau.
- Sao chep 100 anh, 2 bang va MP3.
- Tao de_06.json.

KHONG ket noi SQL.
KHONG sua cac de HSK4 cu.
KHONG sua cac bang Bai tap.
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

DATA = BASE / "hsk4" / "data" / "de_06"
OUTPUT = BASE / "hsk4" / "output" / "de_06"

MEDIA_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk4"
)

MEDIA = MEDIA_ROOT / "de_06"

PDF_FILE = SOURCE / "H41006.pdf"
MP3_FILE = SOURCE / "H41006.mp3"

ANSWER_FILE = DATA / "de_06_dap_an.json"

MANIFEST_FILE = (
    DATA / "hinh_100_cau_ung_vien.json"
)

FINAL_FILE = DATA / "de_06.json"

# Ma goc thuc te in trong PDF
CODE = "H41008"

# Thu tu hien thi tren website
DE_NUMBER = 6

# Dung ten audio rieng de tranh trung De 8
AUDIO_FILENAME = "H41006.mp3"

WORDS = {
    96: "困",
    97: "味道",
    98: "怀疑",
    99: "来得及",
    100: "肚子",
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
        "NFKC", str(value)
    )
    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "", value
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

def tokens_from_pdf(doc):
    tokens = {}

    text = doc[14].get_text("text")

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
            f"Trung cau Viet {number}"
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
            f"Cau {number}: sai cum tu {values}"
        )

        tokens[number] = values

    require(
        set(tokens) == set(range(86, 96)),
        "PDF khong du 10 cau Viet sap xep"
    )

    return tokens


# =====================================================
# 5. DOC DAP AN VIET TRANG 24
# =====================================================

def numbered_answers(text, first, last):

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
            r"\s+", "",
            text[match.end():end]
        )

    require(
        set(result) == {
            str(n)
            for n in range(first, last + 1)
        },
        f"Trang 24 thieu dap an {first}-{last}"
    )

    return result


# =====================================================
# 6. KIEM TRA JSON DAP AN BUOC 1
# =====================================================

def validate_answers(source, doc):

    require(
        (
            source.get("cap_hsk"),
            source.get("so_de"),
            source.get("ma_de_goc")
        ) == (4, DE_NUMBER, CODE),
        "JSON buoc 1 sai danh tinh de"
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
        "JSON buoc 1 sai tong so cau"
    )

    require(
        Path(
            source.get("file_pdf") or ""
        ).resolve() == PDF_FILE.resolve(),
        "File PDF khong khop buoc 1"
    )

    require(
        Path(
            source.get("file_mp3") or ""
        ).resolve() == MP3_FILE.resolve(),
        "File MP3 khong khop buoc 1"
    )

    # ================================================
    # 7. KIEM TRA CHAM VIET TU DONG
    # ================================================

    require(
        source.get("cau_can_cham_thu_cong") == []
        and source.get("che_do_cham_viet_mo")
        == "cham_tu_dong_theo_mau",
        "Viet theo tranh phai cham tu dong"
    )

    answers = source.get("dap_an") or {}

    require(
        isinstance(answers, dict)
        and set(answers) == {
            str(n) for n in range(1, 101)
        },
        "JSON buoc 1 thieu 100 dap an"
    )

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
            f"Thieu dap an Viet cau {number}"
        )

    for number in range(96, 101):

        require(
            answers[str(number)] is None,
            f"Cau {number} phai co dap_an=null"
        )

    # De 6 KHONG co dap an thay the.
    alternatives = (
        source.get("dap_an_thay_the") or {}
    )

    require(
        alternatives == {},
        "De 6 khong co dap an thay the"
    )

    words = (
        source.get("tu_cho_san_viet_mo") or {}
    )

    require(
        words == {
            str(n): word
            for n, word in WORDS.items()
        },
        "5 tu goi y khong khop PDF"
    )

    references = (
        source.get("dap_an_tham_khao_viet_mo")
        or {}
    )

    require(
        set(references) == {
            str(n) for n in range(96, 101)
        },
        "Thieu 5 cau mau Viet"
    )

    for number in range(96, 101):

        values = references[str(number)]

        require(
            isinstance(values, list)
            and bool(values)
            and all(
                isinstance(value, str)
                and bool(compact(value))
                and WORDS[number] in value
                for value in values
            ),
            f"Cau {number}: cau mau sai tu goi y"
        )

    # ================================================
    # 8. DOI CHIEU 85 DAP AN VOI PDF
    # ================================================

    official = {}

    matches = re.findall(
        r"(?<!\d)"
        r"(\d{1,3})"
        r"\s*[.．、]\s*"
        r"([A-F√×]{1,3})"
        r"(?![A-Z])",
        doc[22].get_text("text")
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
            str(n) for n in range(1, 86)
        },
        "Trang 23 thieu 85 dap an"
    )

    for number in range(1, 86):

        key = str(number)

        require(
            answers[key] == official[key],
            f"Cau {number}: dap an khac PDF"
        )

    # ================================================
    # 9. DOI CHIEU CUM TU VIET
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
            "Cum tu Viet buoc 1 khac PDF"
        )

    for number in range(86, 96):

        possible = {
            compact("".join(order))
            for order in permutations(
                tokens[number]
            )
        }

        require(
            compact(answers[str(number)])
            in possible,
            f"Cau {number}: dap an khong "
            "ghep duoc tu cac cum tu"
        )

    # ================================================
    # 10. DOI CHIEU DAP AN VIET TRANG 24
    # ================================================

    pdf_text = doc[23].get_text("text")

    require(
        "第一部分" in pdf_text
        and "第二部分" in pdf_text,
        "Trang 24 thieu hai phan Viet"
    )

    part_one, part_two = pdf_text.split(
        "第二部分", 1
    )

    pdf_writing = numbered_answers(
        part_one, 86, 95
    )

    pdf_open = numbered_answers(
        part_two, 96, 100
    )

    for number in range(86, 96):

        key = str(number)

        variants = [
            compact(value)
            for value in re.split(
                r"[/／]",
                pdf_writing[key]
            )
            if value
        ]

        require(
            variants == [compact(answers[key])],
            f"Cau {number}: dap an Viet khac PDF"
        )

    for number in range(96, 101):

        key = str(number)

        require(
            compact(pdf_open[key]) in [
                compact(value)
                for value in references[key]
            ],
            f"Cau {number}: cau mau khac PDF"
        )

    return (
        answers,
        alternatives,
        references,
        words,
        tokens
    )


# =====================================================
# 11. KIEM TRA MANIFEST BUOC 2
# =====================================================

def validate_manifest(manifest, words):

    require(
        (
            manifest.get("cap_hsk"),
            manifest.get("so_de"),
            manifest.get("ma_de_goc"),
            manifest.get("so_cau")
        ) == (4, DE_NUMBER, CODE, 100),
        "Manifest khong phai De 6"
    )

    require(
        (
            manifest.get("so_trang_pdf"),
            manifest.get("trang_loi_thoai"),
            manifest.get("trang_dap_an")
        ) == (
            24,
            list(range(17, 23)),
            [23, 24]
        ),
        "Manifest sai trang PDF"
    )

    require(
        manifest.get("cau_can_cham_thu_cong")
        == []
        and manifest.get("che_do_cham_viet_mo")
        == "cham_tu_dong_theo_mau",
        "Manifest chua dat cham tu dong"
    )

    items = manifest.get("cau_hoi") or {}
    groups = manifest.get("bang_lua_chon") or {}

    require(
        set(items) == {
            str(n) for n in range(1, 101)
        },
        "Manifest thieu 100 cau"
    )

    require(
        set(groups) == set(GROUPS),
        "Manifest thieu 2 bang A-F"
    )

    copies = []

    # ================================================
    # 12. KIEM TRA 100 ANH
    # ================================================

    for number in range(1, 101):

        item = items[str(number)]

        relative = (
            f"questions/cau_{number:03d}.png"
        )

        require(
            item.get("trang_pdf")
            == page_for(number)
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
                item.get("nhom_doc_chung")
                == shared,
                f"Cau {number}: sai nhom Doc chung"
            )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    # ================================================
    # 13. KIEM TRA HAI BANG A-F
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
        "Khong du 100 anh va 2 bang"
    )

    return items, copies


# =====================================================
# 14. KIEM TRA MEDIA TRUOC KHI COPY
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
                "Media da ton tai voi noi dung khac.\n"
                "KHONG ghi de: "
                + str(destination)
            )


# =====================================================
# 15. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 06 - BUOC 3")
    print("CHUAN HOA H41008 (FILE H41006.pdf)")
    print("=" * 60)

    require_file(PDF_FILE)
    require_file(MP3_FILE)

    source = read_json(ANSWER_FILE)
    manifest = read_json(MANIFEST_FILE)

    # ================================================
    # 16. KIEM TRA PDF VA DAP AN
    # ================================================

    with fitz.open(PDF_FILE) as doc:

        require(
            len(doc) == 24
            and CODE in doc[0].get_text("text")
            and CODE in doc[22].get_text("text"),
            "PDF khong phai H41008 / 24 trang"
        )

        (
            answers,
            alternatives,
            references,
            words,
            tokens
        ) = validate_answers(source, doc)

    # ================================================
    # 17. KIEM TRA MANIFEST
    # ================================================

    items, copies = validate_manifest(
        manifest, words
    )

    # ================================================
    # 18. DOC THOI LUONG MP3
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

    # Giu ten audio rieng cho De 6.
    copies.append((
        MP3_FILE,
        MEDIA_ROOT / AUDIO_FILENAME
    ))

    inspect_media(copies)

    # ================================================
    # 19. TAO 100 CAU HOI
    # ================================================

    questions = []

    for number in range(1, 101):

        key = str(number)
        item = items[key]

        other = alternatives.get(
            key, []
        )

        # Viet sap xep 86-95
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

        # Viet theo tranh 96-100
        elif number >= 96:

            answer = {
                "che_do": "cham_tu_dong_theo_mau",
                "tu_cho_san": words[key],
                "dap_an_tham_khao": references[key]
            }

            options = []

        # Cac cau Nghe va Doc
        else:

            answer = answers[key]

            options = [
                {
                    "ma": value,
                    "nhan": value
                }
                for value in choices_for(number)
            ]

        group = item.get("nhom_lua_chon")

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
                "hsk4/de_06/"
                + item["anh"]
            ),

            "anh_nhom_lua_chon": (
                "/static/media/luyen_thi/"
                "hsk4/de_06/groups/"
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
    # 20. TAO JSON CUOI CUNG
    # ================================================

    result = {

        "ma_de_goc": CODE,

        "cap_hsk": 4,

        "so_de": DE_NUMBER,
        "thu_tu": DE_NUMBER,

        "ten_hien_thi": "Đề 6",

        "so_cau": 100,

        "so_cau_nghe": 45,
        "so_cau_doc": 40,
        "so_cau_viet": 15,

        "thoi_gian_phut": 100,

        "thoi_gian_pdf_phut": 105,

        "so_trang_pdf_de": 24,

        "trang_cau_hoi": list(range(2, 17)),

        "trang_loi_thoai": list(range(17, 23)),

        "trang_dap_an": [23, 24],

        "nguon_dap_an": "pdf_chung",

        "file_pdf": str(PDF_FILE),
        "file_mp3": str(MP3_FILE),

        "audio": {
            "duong_dan": (
                "/static/media/luyen_thi/"
                "hsk4/" + AUDIO_FILENAME
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
    # 21. KHONG GHI DE JSON KHAC NOI DUNG
    # ================================================

    content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    require(
        not FINAL_FILE.exists()
        or FINAL_FILE.read_bytes() == content,

        "de_06.json da ton tai voi noi dung khac.\n"
        "KHONG ghi de: "
        + str(FINAL_FILE)
    )

    # ================================================
    # 22. SAO CHEP MEDIA
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
    # 23. LUU JSON
    # ================================================

    if not FINAL_FILE.exists():

        FINAL_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        FINAL_FILE.write_bytes(content)

    # ================================================
    # 24. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH CHUAN HOA HSK4 DE 06")
    print("=" * 60)

    print(f"Ma de goc PDF: {CODE}")
    print("Ten hien thi: De 6")
    print("Tong cau: 100")

    print("Nghe: 45/45")
    print("Doc: 40/40")
    print("Viet sap xep: 10/10")
    print("Viet theo tranh: 5/5")

    print("Dap an thay the: KHONG CO")
    print("Che do cham: TU DONG")

    print("Anh: 100/100")
    print("Bang A-F: 2/2")

    print(f"MP3: {duration} giay")
    print("Thoi gian thi: 100 phut")

    print(
        "Audio website: "
        "/static/media/luyen_thi/hsk4/"
        + AUDIO_FILENAME
    )

    print(f"\nJSON: {FINAL_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
