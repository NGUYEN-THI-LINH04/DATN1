
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 06 (H31006) - BUOC 3

- Su dung JSON HSK3 De 1 lam mau.
- Doi chieu 80 dap an theo PDF 16 trang.
- Tu dong doc cac cum tu cau 71-75 tu PDF.
- Giu 2 dap an hop le cua cau 75.
- Kiem tra 70 anh cau hoi va 6 bang chung.
- Sao chep 76 anh va MP3 sang static.
- Tao JSON de_06.json.

KHONG ket noi SQL Server.
KHONG sua cac de thi cu.
KHONG ghi de file khac noi dung.
"""

from pathlib import Path
from collections import Counter
from copy import deepcopy
from itertools import permutations

import json
import re
import shutil
import filecmp
import unicodedata

import fitz
from mutagen.mp3 import MP3


# =====================================================
# 1. CAU HINH
# =====================================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "luyen_thi"
HSK3 = BASE / "hsk3"

SOURCE = (
    BASE / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 6"
)

DATA = HSK3 / "data" / "de_06"
OUTPUT = HSK3 / "output" / "de_06"

MEDIA_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk3"
)

MEDIA = MEDIA_ROOT / "de_06"

TEMPLATE_FILE = (
    HSK3 / "data" / "de_01" / "de_01.json"
)

ANSWER_FILE = DATA / "de_06_dap_an.json"

MANIFEST_FILE = (
    DATA / "hinh_80_cau_ung_vien.json"
)

FINAL_FILE = DATA / "de_06.json"

CODE = "H31006"


# =====================================================
# 2. CAC BANG LUA CHON CHUNG
# =====================================================

# Ten nhom:
# (trang PDF, cau bat dau, cau ket thuc, lua chon)

GROUPS = {
    "nghe_01_05": (2, 1, 5, "ABCDEF"),
    "nghe_06_10": (3, 6, 10, "ABCDE"),

    "doc_41_45": (7, 41, 45, "ABCDEF"),
    "doc_46_50": (8, 46, 50, "ABCDE"),

    "doc_51_55": (9, 51, 55, "ABCDEF"),
    "doc_56_60": (10, 56, 60, "ABCDEF"),
}


# =====================================================
# 3. SO DO TRANG PDF
# =====================================================

PAGES = {
    2: range(1, 6),
    3: range(6, 11),

    4: range(11, 21),
    5: range(21, 31),
    6: range(31, 41),

    7: range(41, 46),
    8: range(46, 51),

    9: range(51, 56),
    10: range(56, 61),

    11: range(61, 65),
    12: range(65, 71),

    13: range(71, 76),
    14: range(76, 81),
}


# =====================================================
# 4. HAM HO TRO
# =====================================================

def check_file(path):

    if (
        not path.is_file()
        or path.stat().st_size == 0
    ):
        raise RuntimeError(
            f"Thieu file hoac file rong:\n{path}"
        )

    return path


def load_json(path):

    return json.loads(
        check_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


def normalize(value):

    return unicodedata.normalize(
        "NFKC",
        str(value)
    )


def compact(value):

    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "",
        normalize(value)
    )


def replace_refs(value):

    if isinstance(value, str):

        return (
            value
            .replace("H31001", CODE)
            .replace("de_01", "de_06")
            .replace("Đề 1", "Đề 6")
            .replace("ĐỀ 1", "ĐỀ 6")
        )

    if isinstance(value, list):

        return [
            replace_refs(item)
            for item in value
        ]

    if isinstance(value, dict):

        return {
            key: replace_refs(item)
            for key, item in value.items()
        }

    return value


# =====================================================
# 5. XAC DINH KY NANG
# =====================================================

def skill_for(number):

    if number <= 40:
        return "nghe"

    if number <= 70:
        return "doc"

    return "viet"


# =====================================================
# 6. XAC DINH LOAI CAU HOI
# =====================================================

def kind_for(number):

    if number <= 10:
        return "chon_hinh"

    if number <= 20:
        return "dung_sai"

    if number <= 40:
        return "chon_mot"

    if number <= 60:
        return "ghep_lua_chon"

    if number <= 70:
        return "chon_mot"

    if number <= 75:
        return "sap_xep"

    return "dien_tu"


# =====================================================
# 7. XAC DINH PHAN THI
# =====================================================

def part_for(number):

    if number <= 40:

        index = (
            (number - 1) // 10 + 1
        )

        return f"Nghe - Phần {index}"

    if number <= 50:
        return "Đọc - Phần 1"

    if number <= 60:
        return "Đọc - Phần 2"

    if number <= 70:
        return "Đọc - Phần 3"

    if number <= 75:
        return "Viết - Phần 1"

    return "Viết - Phần 2"


# =====================================================
# 8. XAC DINH TRANG VA NHOM LUA CHON
# =====================================================

def page_for(number):

    for page, numbers in PAGES.items():

        if number in numbers:
            return page

    raise RuntimeError(
        f"Cau {number} khong co trang PDF."
    )


def group_for(number):

    for name, (
        _page,
        first,
        last,
        _labels
    ) in GROUPS.items():

        if first <= number <= last:
            return name

    return None


# =====================================================
# 9. TAO DANH SACH LUA CHON
# =====================================================

def choice_values(number, tokens):

    if number <= 5:
        return list("ABCDEF")

    if number <= 10:
        return list("ABCDE")

    if number <= 20:
        return ["√", "×"]

    if number <= 40:
        return list("ABC")

    if number <= 45:
        return list("ABCDEF")

    if number <= 50:
        return list("ABCDE")

    if number <= 60:
        return list("ABCDEF")

    if number <= 70:
        return list("ABC")

    if number <= 75:
        return tokens[number]

    return []


def choices_for(number, tokens):

    return [
        {
            "ma": value,
            "nhan": value,
        }
        for value in choice_values(
            number,
            tokens
        )
    ]


# =====================================================
# 10. DOC DAP AN VA CUM TU TU PDF
# =====================================================

def read_pdf_data(pdf_path):

    with fitz.open(pdf_path) as doc:

        # ============================================
        # KIEM TRA PDF
        # ============================================

        if len(doc) != 16:
            raise RuntimeError(
                "PDF H31006 phai co 16 trang."
            )

        cover = doc[0].get_text("text")
        answer_page = doc[14].get_text("text")
        writing_page = doc[15].get_text("text")

        if (
            CODE not in cover
            or CODE not in answer_page
        ):
            raise RuntimeError(
                "PDF khong phai H31006."
            )

        if (
            "答案" not in answer_page
            or "书" not in writing_page
        ):
            raise RuntimeError(
                "Trang dap an 15-16 khong dung."
            )

        # ============================================
        # 11. DOC 70 DAP AN NGHE/DOC
        # ============================================

        objective = {}

        text = normalize(answer_page)

        pattern = re.compile(
            r"(?<!\d)(\d{1,2})\s*[.．、]"
            r"\s*([A-F√×])(?=\s|$)"
        )

        for match in pattern.finditer(text):

            number = int(
                match.group(1)
            )

            if not 1 <= number <= 70:
                continue

            if number in objective:
                raise RuntimeError(
                    f"Trung dap an cau {number}."
                )

            objective[number] = (
                match.group(2)
            )

        if set(objective) != set(range(1, 71)):
            raise RuntimeError(
                "Trang 15 khong du 70 dap an."
            )

        # ============================================
        # 12. DOC 10 DAP AN VIET
        # ============================================

        writing = {}

        writing_pattern = re.compile(
            r"^\s*(7[1-9]|80)\s*[.．、]"
            r"\s*([^\n]+)",
            re.MULTILINE
        )

        for match in writing_pattern.finditer(
            writing_page
        ):

            number = int(
                match.group(1)
            )

            if number in writing:
                raise RuntimeError(
                    f"Trung dap an Viet {number}."
                )

            writing[number] = [
                value.strip()
                for value in match.group(2).split("/")
                if value.strip()
            ]

        if set(writing) != set(range(71, 81)):
            raise RuntimeError(
                "Trang 16 khong du 10 dap an Viet."
            )

        # Chi cau 75 co 2 dap an.
        for number, values in writing.items():

            expected_count = (
                2 if number == 75 else 1
            )

            if len(values) != expected_count:
                raise RuntimeError(
                    f"Cau {number} sai "
                    "so luong dap an."
                )

        answers = {
            **objective,
            **{
                number: values[0]
                for number, values in writing.items()
            },
        }

        alternatives = {
            "75": writing[75][1:]
        }

        # ============================================
        # 13. LAY CUM TU SAP XEP CAU 71-75
        # ============================================

        tokens = {}

        text = normalize(
            doc[12].get_text("text")
        )

        for line in text.splitlines():

            match = re.match(
                r"^\s*(7[1-5])\s*[.．、]"
                r"\s*(.+)",
                line
            )

            if not match:
                continue

            number = int(
                match.group(1)
            )

            if number in tokens:
                raise RuntimeError(
                    f"Trung cum tu cau {number}."
                )

            values = [
                value.strip()
                for value in re.split(
                    r"\s{2,}",
                    match.group(2)
                )
                if value.strip()
            ]

            tokens[number] = values

        if set(tokens) != set(range(71, 76)):
            raise RuntimeError(
                "Khong doc du cum tu cau 71-75."
            )

        # ============================================
        # 14. KIEM TRA GHEP CAU VIET
        # ============================================

        for number in range(71, 76):

            values = tokens[number]

            if not 3 <= len(values) <= 8:
                raise RuntimeError(
                    f"Cau {number} co "
                    "so cum tu khong hop le."
                )

            combinations = {
                compact("".join(order))
                for order in permutations(values)
            }

            valid_answers = [
                answers[number],
                *alternatives.get(
                    str(number), []
                ),
            ]

            for answer in valid_answers:

                if (
                    compact(answer)
                    not in combinations
                ):
                    raise RuntimeError(
                        f"Cau {number} "
                        "khong ghep duoc dap an:\n"
                        + answer
                    )

        # Cau 76-80: moi cau mot chu Han.
        for number in range(76, 81):

            if len(
                compact(answers[number])
            ) != 1:
                raise RuntimeError(
                    f"Cau {number} "
                    "phai dien mot chu Han."
                )

    return (
        answers,
        alternatives,
        tokens
    )


# =====================================================
# 15. KIEM TRA FILE MEDIA TRUOC KHI COPY
# =====================================================

def check_copy_pairs(pairs):

    for source, destination in pairs:

        check_file(source)

        if destination.exists():

            if not filecmp.cmp(
                source,
                destination,
                shallow=False
            ):
                raise RuntimeError(
                    "File dich da ton tai "
                    "voi noi dung khac:\n"
                    + str(destination)
                )


# =====================================================
# 16. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 06")
    print("BUOC 3 - CHUAN HOA H31006")
    print("=" * 60)

    # ================================================
    # 17. DOC JSON NGUON
    # ================================================

    template = load_json(
        TEMPLATE_FILE
    )

    source_info = load_json(
        ANSWER_FILE
    )

    manifest = load_json(
        MANIFEST_FILE
    )

    if (
        template.get("ma_de_goc") != "H31001"
        or len(template.get("cau_hoi", [])) != 80
    ):
        raise RuntimeError(
            "JSON mau De 1 khong hop le."
        )

    if (
        source_info.get("cap_hsk"),
        source_info.get("so_de"),
        source_info.get("ma_de_goc"),
    ) != (3, 6, CODE):
        raise RuntimeError(
            "JSON dap an khong phai De 6."
        )

    if (
        manifest.get("cap_hsk"),
        manifest.get("so_de"),
        manifest.get("ma_de_goc"),
        manifest.get("so_cau"),
    ) != (3, 6, CODE, 80):
        raise RuntimeError(
            "Manifest khong phai De 6."
        )

    if (
        manifest.get("so_trang_pdf") != 16
        or manifest.get("trang_dap_an")
        != [15, 16]
    ):
        raise RuntimeError(
            "Manifest sai so trang "
            "hoac vi tri dap an."
        )

    # ================================================
    # 18. TIM PDF VA MP3
    # ================================================

    pdfs = sorted(
        SOURCE.glob("*.pdf")
    )

    mp3s = sorted(
        SOURCE.glob("*.mp3")
    )

    if (
        len(pdfs) != 1
        or len(mp3s) != 1
    ):
        raise RuntimeError(
            "Thu muc DE 6 phai co "
            "dung 1 PDF va 1 MP3."
        )

    pdf_file = check_file(pdfs[0])
    mp3_file = check_file(mp3s[0])

    source_pdf = source_info.get(
        "file_pdf"
    )

    if (
        not source_pdf
        or Path(source_pdf).resolve()
        != pdf_file.resolve()
    ):
        raise RuntimeError(
            "PDF trong JSON buoc 1 "
            "khong khop file goc."
        )

    # ================================================
    # 19. DOI CHIEU 80 DAP AN
    # ================================================

    (
        pdf_answers,
        pdf_alternatives,
        writing_tokens
    ) = read_pdf_data(pdf_file)

    source_answers = source_info.get(
        "dap_an", {}
    )

    if set(source_answers) != {
        str(n) for n in range(1, 81)
    }:
        raise RuntimeError(
            "JSON buoc 1 thieu 80 dap an."
        )

    for number in range(1, 81):

        if compact(
            source_answers[str(number)]
        ) != compact(
            pdf_answers[number]
        ):
            raise RuntimeError(
                f"Sai dap an cau {number} "
                "so voi PDF."
            )

    if (
        source_info.get("dap_an_thay_the")
        != pdf_alternatives
    ):
        raise RuntimeError(
            "Dap an thay the cau 75 "
            "khong khop PDF."
        )

    if (
        manifest.get("dap_an_thay_the")
        != pdf_alternatives
    ):
        raise RuntimeError(
            "Manifest thieu dap an "
            "thay the cau 75."
        )

    print("\n===== KIEM TRA DAP AN =====")
    print("Nghe/Doc: 70/70")
    print("Viet: 10/10")
    print("Tong: 80/80")
    print("Cau 75: 2 dap an hop le")
    print("Cau 71-75: cum tu khop PDF")

    # ================================================
    # 20. KIEM TRA MANIFEST ANH
    # ================================================

    question_manifest = manifest.get(
        "cau_hoi", {}
    )

    group_manifest = manifest.get(
        "bang_lua_chon", {}
    )

    if set(question_manifest) != {
        str(n) for n in range(1, 81)
    }:
        raise RuntimeError(
            "Manifest khong du 80 cau."
        )

    if set(group_manifest) != set(GROUPS):
        raise RuntimeError(
            "Manifest khong du 6 bang."
        )

    # ================================================
    # 21. KIEM TRA 70 ANH CAU HOI
    # ================================================

    copies = []

    for number in range(1, 81):

        item = question_manifest[
            str(number)
        ]

        if (
            item.get("trang_pdf")
            != page_for(number)
        ):
            raise RuntimeError(
                f"Cau {number} sai trang PDF."
            )

        if (
            item.get("nhom_lua_chon")
            != group_for(number)
        ):
            raise RuntimeError(
                f"Cau {number} sai nhom lua chon."
            )

        if number <= 10:

            if item.get("anh") is not None:
                raise RuntimeError(
                    f"Cau {number} "
                    "khong duoc co anh rieng."
                )

            continue

        relative = (
            f"questions/cau_{number:02d}.png"
        )

        if item.get("anh") != relative:
            raise RuntimeError(
                f"Manifest sai anh cau {number}."
            )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    # ================================================
    # 22. KIEM TRA 6 BANG LUA CHON
    # ================================================

    for name, (
        page,
        first,
        last,
        labels
    ) in GROUPS.items():

        item = group_manifest[name]

        actual = (
            item.get("trang_pdf"),
            item.get("cau_tu"),
            item.get("cau_den"),
            item.get("lua_chon"),
            item.get("anh"),
        )

        expected = (
            page,
            first,
            last,
            labels,
            f"groups/{name}.png",
        )

        if actual != expected:
            raise RuntimeError(
                f"Manifest sai bang {name}."
            )

        relative = f"groups/{name}.png"

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    if len(copies) != 76:
        raise RuntimeError(
            f"Khong du 76 anh: "
            f"{len(copies)}/76"
        )

    print("\n===== KIEM TRA HINH =====")
    print("Anh cau hoi: 70/70")
    print("Bang chung: 6/6")

    # ================================================
    # 23. DOC THOI LUONG MP3
    # ================================================

    try:

        duration = round(
            float(
                MP3(str(mp3_file)).info.length
            ),
            2
        )

    except Exception as exc:

        raise RuntimeError(
            f"Khong doc duoc MP3: {exc}"
        ) from exc

    if duration <= 0:
        raise RuntimeError(
            "Thoi luong MP3 khong hop le."
        )

    # ================================================
    # 24. TAO JSON TU MAU DE 1
    # ================================================

    result = replace_refs(
        deepcopy(template)
    )

    result.update({
        "cap_hsk": 3,
        "so_de": 6,
        "ma_de_goc": CODE,

        "ten_hien_thi": "Đề 6",
        "thu_tu": 6,

        "so_cau": 80,
        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "thoi_gian_phut": 85,

        "so_trang_pdf_de": 16,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        # PDF khong co transcript.
        "trang_loi_thoai": [],

        "trang_dap_an": [15, 16],

        "nguon_dap_an": "pdf_chung",

        "file_pdf": str(pdf_file),
        "file_mp3": str(mp3_file),

        "dap_an_thay_the": (
            pdf_alternatives
        ),
    })

    result.pop(
        "file_dap_an",
        None
    )

    # ================================================
    # 25. CAP NHAT AUDIO
    # ================================================

    if not isinstance(
        result.get("audio"),
        dict
    ):
        raise RuntimeError(
            "JSON mau De 1 thieu audio."
        )

    result["audio"].update({
        "duong_dan": (
            "/static/media/luyen_thi/"
            f"hsk3/{CODE}.mp3"
        ),

        "thoi_luong_giay": duration,
    })

    # ================================================
    # 26. TAO 80 CAU HOI
    # ================================================

    questions = []

    for number, original in enumerate(
        template["cau_hoi"],
        start=1
    ):

        if original.get("so_cau") != number:
            raise RuntimeError(
                f"JSON mau sai cau {number}."
            )

        question = replace_refs(
            deepcopy(original)
        )

        group = group_for(number)

        if number <= 10:
            question_image = None

        else:
            question_image = (
                "/static/media/luyen_thi/"
                "hsk3/de_06/questions/"
                f"cau_{number:02d}.png"
            )

        if group:
            group_image = (
                "/static/media/luyen_thi/"
                "hsk3/de_06/groups/"
                f"{group}.png"
            )

        else:
            group_image = None

        question.update({
            "so_cau": number,

            "ky_nang": skill_for(number),
            "phan": part_for(number),

            "loai_cau_hoi": kind_for(number),

            # Noi dung cau hoi da co trong anh.
            "noi_dung": None,

            "trang_pdf": page_for(number),

            "dap_an_dung": (
                pdf_answers[number]
            ),

            "lua_chon_json": choices_for(
                number,
                writing_tokens
            ),

            "da_duyet": False,

            "anh_cau_hoi": question_image,

            "anh_nhom_lua_chon": group_image,
        })

        # Dong bo cac truong dang cau.
        for field in (
            "dang",
            "dang_cau_hoi",
            "kieu_cau_hoi"
        ):

            if field in question:
                question[field] = kind_for(
                    number
                )

        # Khong ke thua dap an thay the
        # cua De 1.
        question.pop(
            "dap_an_thay_the",
            None
        )

        # Giu hai dap an cau 75.
        if number == 75:

            question["dap_an_thay_the"] = list(
                pdf_alternatives["75"]
            )

        if number <= 70:

            if (
                pdf_answers[number]
                not in choice_values(
                    number,
                    writing_tokens
                )
            ):
                raise RuntimeError(
                    f"Dap an cau {number} "
                    "ngoai lua chon."
                )

        questions.append(question)

    # ================================================
    # 27. KIEM TRA SO LUONG CAU
    # ================================================

    if Counter(
        question["ky_nang"]
        for question in questions
    ) != {
        "nghe": 40,
        "doc": 30,
        "viet": 10
    }:
        raise RuntimeError(
            "Sai so cau Nghe/Doc/Viet."
        )

    result["cau_hoi"] = questions

    # ================================================
    # 28. KIEM TRA JSON TRUOC KHI LUU
    # ================================================

    json_content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    raw = json_content.decode("utf-8")

    for old_ref in (
        "H31001",
        "/hsk3/de_01/",
        "de_01.json"
    ):

        if old_ref in raw:
            raise RuntimeError(
                "JSON con tham chieu De 1: "
                + old_ref
            )

    if FINAL_FILE.exists():

        if FINAL_FILE.read_bytes() != json_content:
            raise RuntimeError(
                "JSON De 6 da ton tai voi "
                "noi dung khac.\n"
                "Khong ghi de:\n"
                + str(FINAL_FILE)
            )

    # ================================================
    # 29. KIEM TRA MEDIA DICH
    # ================================================

    copies.append((
        mp3_file,
        MEDIA_ROOT / f"{CODE}.mp3"
    ))

    check_copy_pairs(
        copies
    )

    # ================================================
    # 30. SAO CHEP ANH VA MP3
    # ================================================

    print("\n===== SAO CHEP MEDIA =====")

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

    # ================================================
    # 31. LUU JSON
    # ================================================

    if not FINAL_FILE.exists():

        FINAL_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        FINAL_FILE.write_bytes(
            json_content
        )

    # ================================================
    # 32. KET QUA
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH CHUAN HOA HSK3 DE 06")
    print("=" * 60)

    print("Ma de: H31006")

    print(
        "Tong cau: 80 "
        "(Nghe 40, Doc 30, Viet 10)"
    )

    print("Dap an: 80/80")
    print("Anh cau hoi: 70/70")
    print("Bang chung: 6/6")

    print(
        "Cau 75: da giu 2 dap an "
        "hop le trong JSON"
    )

    print(
        "PDF: 16 trang, "
        "dap an trang 15-16"
    )

    print(f"MP3: {duration} giay")
    print("Thoi gian thi: 85 phut")

    print(f"\nJSON: {FINAL_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
