
# -*- coding: utf-8 -*-
"""
MOC HAN - HSK4 DE 05 (H41005)

BUOC 3 - CHUAN HOA 100 CAU VA MEDIA

Ke thua dinh dang JSON da kiem thu o H41001-H41004.

- Kiem tra dap an buoc 1.
- Kiem tra manifest 100 anh buoc 2.
- Doi chieu dap an voi PDF H41005.
- Giu 2 dap an hop le cua cau 94.
- Cau 96-100 cham TU DONG theo dap an mau.
- Sao chep 100 anh, 2 bang chung va MP3.
- Tao de_05.json de nhap SQL.

KHONG ket noi SQL.
KHONG sua H41001-H41004.
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

DATA = BASE / "hsk4" / "data" / "de_05"

OUTPUT = BASE / "hsk4" / "output" / "de_05"

MEDIA_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk4"
)

MEDIA = MEDIA_ROOT / "de_05"

PDF_FILE = SOURCE / "H41005.pdf"
MP3_FILE = SOURCE / "H41005.mp3"

ANSWER_FILE = DATA / "de_05_dap_an.json"
MANIFEST_FILE = DATA / "hinh_100_cau_ung_vien.json"
FINAL_FILE = DATA / "de_05.json"

CODE = "H41005"

WORDS = {
    96: "消息",
    97: "猜",
    98: "信用卡",
    99: "沙发",
    100: "困",
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
# 3. TRANG, KY NANG, PHAN THI
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


# =====================================================
# 4. DANG CAU HOI VA LUA CHON
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
            f"Trung cau Viet {number}"
        )

        require(
            3 <= len(values) <= 9,
            f"Cau {number} sai so cum tu: {values}"
        )

        tokens[number] = values

    require(
        set(tokens) == set(range(86, 96)),
        "Trang 15 khong du 10 cau Viet: "
        f"{sorted(tokens)}"
    )

    return tokens


# =====================================================
# 6. DOC DAP AN VIET TU TRANG 24
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

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )

        value = re.sub(
            r"\s+",
            "",
            text[match.end():end]
        )

        key = str(number)

        require(
            key not in result,
            f"Trung dap an Viet {number}"
        )

        result[key] = value

    require(
        set(result) == {
            str(number)
            for number in range(first, last + 1)
        },
        f"Trang 24 khong du dap an {first}-{last}"
    )

    return result


# =====================================================
# 7. KIEM TRA JSON DAP AN BUOC 1
# =====================================================

def validate_answers(source, doc):

    require(
        (
            source.get("cap_hsk"),
            source.get("so_de"),
            source.get("ma_de_goc")
        ) == (4, 5, CODE),
        "JSON buoc 1 khong phai H41005"
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
        "Duong dan PDF buoc 1 khong khop"
    )

    require(
        Path(
            source.get("file_mp3") or ""
        ).resolve() == MP3_FILE.resolve(),
        "Duong dan MP3 buoc 1 khong khop"
    )

    require(
        source.get("cau_can_cham_thu_cong") == [],
        "H41005 khong duoc cham thu cong"
    )

    require(
        source.get("che_do_cham_viet_mo")
        == "cham_tu_dong_theo_mau",
        "Sai che do cham Viet theo tranh"
    )

    answers = source.get("dap_an") or {}

    require(
        isinstance(answers, dict)
        and set(answers) == {
            str(n) for n in range(1, 101)
        },
        "JSON buoc 1 thieu 100 dap an"
    )

    # Dap an Nghe va Doc
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
            f"Cau {number} sai dap an: {answer}"
        )

    # Viet sap xep
    for number in range(86, 96):
        answer = answers[str(number)]

        require(
            isinstance(answer, str)
            and bool(answer.strip()),
            f"Thieu dap an Viet cau {number}"
        )

    # Viet theo tranh
    for number in range(96, 101):
        require(
            answers[str(number)] is None,
            f"Buoc 1 cau {number} phai luu dap_an = null"
        )

    # Cau 94 co hai dap an
    alternatives = (
        source.get("dap_an_thay_the") or {}
    )

    require(
        set(alternatives) == {"94"}
        and isinstance(
            alternatives.get("94"),
            list
        )
        and len(alternatives["94"]) == 1,
        "H41005 chi co cau 94 "
        "co mot dap an thay the"
    )

    words = (
        source.get("tu_cho_san_viet_mo")
        or {}
    )

    require(
        words == {
            str(number): word
            for number, word in WORDS.items()
        },
        "Tu goi y 96-100 khac PDF"
    )

    references = (
        source.get("dap_an_tham_khao_viet_mo")
        or {}
    )

    require(
        set(references) == {
            str(n) for n in range(96, 101)
        },
        "Thieu 5 dap an tham khao Viet tranh"
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
            f"Cau {number} thieu cau mau "
            "hoac tu goi y"
        )

    # ================================================
    # 8. DOI CHIEU 85 DAP AN VOI PDF TRANG 23
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
            f"Trung dap an trang 23: {key}"
        )

        official[key] = value

    require(
        set(official) == {
            str(n) for n in range(1, 86)
        },
        "PDF trang 23 khong du 85 dap an"
    )

    for number in range(1, 86):
        key = str(number)

        require(
            answers[key] == official[key],
            f"Cau {number}: dap an JSON khac PDF H41005"
        )

    # ================================================
    # 9. KIEM TRA CUM TU VIET
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
            "khac PDF trang 15"
        )

    for number in range(86, 96):
        key = str(number)
        values = tokens[number]

        candidates = (
            [answers[key]]
            + alternatives.get(key, [])
        )

        possible = {
            compact("".join(order))
            for order in permutations(values)
        }

        for answer in candidates:
            require(
                compact(answer) in possible,
                f"Cau {number} khong ghep duoc dap an:\n"
                f"Dap an: {answer}\n"
                f"Cum tu: {values}"
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

        stored_variants = (
            [answers[key]]
            + alternatives.get(key, [])
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
            "dap an Viet khac PDF trang 24"
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
            "cau mau khac PDF trang 24"
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
        ) == (4, 5, CODE, 100),
        "Manifest buoc 2 khong phai H41005"
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
        "Manifest sai cau truc PDF"
    )

    require(
        manifest.get("cau_can_cham_thu_cong") == []
        and manifest.get("che_do_cham_viet_mo")
        == "cham_tu_dong_theo_mau",
        "Manifest chua dat che do cham tu dong"
    )

    items = manifest.get("cau_hoi") or {}

    require(
        isinstance(items, dict)
        and set(items) == {
            str(n) for n in range(1, 101)
        },
        "Manifest thieu 100 cau hoi"
    )

    groups = (
        manifest.get("bang_lua_chon") or {}
    )

    require(
        isinstance(groups, dict)
        and set(groups) == set(GROUPS),
        "Manifest thieu hai bang A-F"
    )

    copies = []

    # Kiem tra 100 anh
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

        # Nhom Doc dung chung doan van
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

    # Kiem tra 2 bang lua chon
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
# 12. KIEM TRA MEDIA
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
                "Media da ton tai voi noi dung khac:\n"
                + str(destination)
            )


# =====================================================
# 13. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK4 DE 05 - BUOC 3")
    print("CHUAN HOA H41005")
    print("=" * 60)

    require_file(PDF_FILE)
    require_file(MP3_FILE)

    source = read_json(ANSWER_FILE)
    manifest = read_json(MANIFEST_FILE)

    # Kiem tra PDF va dap an
    with fitz.open(PDF_FILE) as doc:

        require(
            len(doc) == 24
            and CODE in doc[0].get_text("text")
            and CODE in doc[22].get_text("text"),
            "PDF khong phai H41005 (24 trang)"
        )

        (
            answers,
            alternatives,
            references,
            words,
            tokens
        ) = validate_answers(source, doc)

    # Kiem tra manifest
    items, copies = validate_manifest(
        manifest,
        words
    )

    # Doc thoi luong MP3
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
        MEDIA_ROOT / f"{CODE}.mp3"
    ))

    inspect_media(copies)

    # ================================================
    # 14. TAO 100 CAU HOI
    # ================================================

    questions = []

    for number in range(1, 101):

        key = str(number)
        item = items[key]

        other = alternatives.get(
            key,
            []
        )

        # Viet sap xep 86-95
        if 86 <= number <= 95:

            values = tokens[number]

            if other:
                answer = [answers[key]] + other
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

        # Viet theo tranh 96-100
        elif number >= 96:

            answer = {
                "che_do": "cham_tu_dong_theo_mau",
                "tu_cho_san": words[key],
                "dap_an_tham_khao": references[key]
            }

            options = []

        # Nghe va Doc
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
                "hsk4/de_05/"
                + item["anh"]
            ),

            "anh_nhom_lua_chon": (
                "/static/media/luyen_thi/"
                "hsk4/de_05/groups/"
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

        questions.append(question)

    # ================================================
    # 15. TAO JSON CUOI CUNG
    # ================================================

    result = {

        "ma_de_goc": CODE,

        "cap_hsk": 4,

        "so_de": 5,
        "thu_tu": 5,

        "ten_hien_thi": "Đề 5",

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
                f"hsk4/{CODE}.mp3"
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
    # 16. KIEM TRA KHONG GHI DE JSON CU
    # ================================================

    content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    require(
        not FINAL_FILE.exists()
        or FINAL_FILE.read_bytes() == content,

        "de_05.json da ton tai "
        "voi noi dung khac.\n"
        "KHONG ghi de: "
        + str(FINAL_FILE)
    )

    # ================================================
    # 17. SAO CHEP MEDIA
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
    # 18. LUU JSON
    # ================================================

    if not FINAL_FILE.exists():

        FINAL_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        FINAL_FILE.write_bytes(content)

    # ================================================
    # 19. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH CHUAN HOA HSK4 DE 05")
    print("=" * 60)

    print("Ma de: H41005")
    print("Ten hien thi: De 5")
    print("Tong cau: 100")

    print("Nghe: 45/45")
    print("Doc: 40/40")

    print("Viet sap xep: 10/10")
    print("Viet theo tranh: 5/5 cau mau")

    print("Dap an thay the: cau 94")
    print("Che do cham: TU DONG")

    print("Anh: 100/100")
    print("Bang lua chon: 2/2")

    print(f"MP3: {duration} giay")
    print("Thoi gian thi: 100 phut")

    print(f"\nJSON: {FINAL_FILE}")

    print("\nCHUA thay doi SQL Server.")
    print("CHUA nhap de.")


if __name__ == "__main__":
    main()
