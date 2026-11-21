
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 03 - H31003

BUOC 3: CHUAN HOA DU LIEU

- Su dung JSON HSK3 De 1 lam mau.
- Doc 80 dap an cua De 3.
- Doi chieu dap an voi PDF goc.
- Kiem tra 70 anh cau hoi.
- Kiem tra 6 bang lua chon.
- Chuan hoa 40 Nghe, 30 Doc, 10 Viet.
- Sao chep anh va MP3 vao static.
- Tao JSON de_03.json.

KHONG nhap SQL Server.
KHONG sua De 1 hoac HSK1/HSK2.
"""

from collections import Counter
from copy import deepcopy
from itertools import permutations
from pathlib import Path

import filecmp
import json
import re
import shutil
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
    / "HSK3" / "ĐỀ 3"
)

DATA = HSK3 / "data" / "de_03"
OUTPUT = HSK3 / "output" / "de_03"

MEDIA_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk3"
)

MEDIA = MEDIA_ROOT / "de_03"

TEMPLATE_FILE = (
    HSK3 / "data" / "de_01" / "de_01.json"
)

ANSWER_FILE = DATA / "de_03_dap_an.json"

MANIFEST_FILE = (
    DATA / "hinh_80_cau_ung_vien.json"
)

FINAL_FILE = DATA / "de_03.json"

CODE = "H31003"


# =====================================================
# 2. CUM TU SAP XEP CUA H31003
# =====================================================

WRITING_TOKENS = {
    71: [
        "送给", "她决定",
        "把手机", "弟弟"
    ],

    72: [
        "见面", "没", "我和这个学生",
        "很久", "了"
    ],

    73: [
        "经常", "的", "春天",
        "刮风", "这个城市"
    ],

    74: [
        "他的汉字", "写",
        "很漂亮", "得"
    ],

    75: [
        "花了", "叔叔的",
        "900 块钱", "太阳镜"
    ],
}


# =====================================================
# 3. BANG LUA CHON CHUNG
# =====================================================

GROUPS = {
    "nghe_01_05": (2, range(1, 6)),
    "nghe_06_10": (3, range(6, 11)),

    "doc_41_45": (7, range(41, 46)),
    "doc_46_50": (8, range(46, 51)),
    "doc_51_55": (9, range(51, 56)),
    "doc_56_60": (10, range(56, 61)),
}


# =====================================================
# 4. VI TRI CAU HOI TREN PDF
# =====================================================

PAGE_QUESTIONS = {
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
# 5. HAM HO TRO
# =====================================================

def check_file(path):

    if (
        not path.is_file()
        or path.stat().st_size == 0
    ):
        raise RuntimeError(
            f"Thieu file hoac file rong: {path}"
        )

    return path


def read_json(path):

    return json.loads(
        check_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


def normal(text):

    return unicodedata.normalize(
        "NFKC", str(text)
    )


def compact(text):

    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "",
        normal(text)
    )


def replace_refs(obj):

    if isinstance(obj, str):

        return (
            obj
            .replace("H31001", CODE)
            .replace("de_01", "de_03")
            .replace("Đề 1", "Đề 3")
        )

    if isinstance(obj, list):

        return [
            replace_refs(value)
            for value in obj
        ]

    if isinstance(obj, dict):

        return {
            key: replace_refs(value)
            for key, value in obj.items()
        }

    return obj


# =====================================================
# 6. KY NANG
# =====================================================

def skill(number):

    if number <= 40:
        return "nghe"

    if number <= 70:
        return "doc"

    return "viet"


# =====================================================
# 7. DANG CAU HOI
# =====================================================

def kind(number):

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
# 8. PHAN THI
# =====================================================

def part(number):

    ranges = [
        (1, 10, "Nghe - Phần 1"),
        (11, 20, "Nghe - Phần 2"),
        (21, 30, "Nghe - Phần 3"),
        (31, 40, "Nghe - Phần 4"),

        (41, 50, "Đọc - Phần 1"),
        (51, 60, "Đọc - Phần 2"),
        (61, 70, "Đọc - Phần 3"),

        (71, 75, "Viết - Phần 1"),
        (76, 80, "Viết - Phần 2"),
    ]

    for first, last, label in ranges:

        if first <= number <= last:
            return label

    raise RuntimeError(
        f"So cau khong hop le: {number}"
    )


def group_for(number):

    for name, (_, numbers) in GROUPS.items():

        if number in numbers:
            return name

    return None


def page_for(number):

    for page_no, numbers in (
        PAGE_QUESTIONS.items()
    ):

        if number in numbers:
            return page_no

    raise RuntimeError(
        f"Khong tim thay trang cau {number}"
    )


# =====================================================
# 9. TAO LUA CHON THEO DANG CAU
# =====================================================

def choice_values(number):

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
        return WRITING_TOKENS[number]

    return []


def choices(number):

    return [
        {
            "ma": value,
            "nhan": value
        }
        for value in choice_values(number)
    ]


# =====================================================
# 10. DOI CHIEU DAP AN PDF
# =====================================================

def read_pdf_answers(pdf_path):

    with fitz.open(pdf_path) as doc:

        if len(doc) != 22:
            raise RuntimeError(
                "PDF H31003 phai co 22 trang."
            )

        if CODE not in normal(
            doc[0].get_text("text")
        ):
            raise RuntimeError(
                "Trang bia khong phai H31003."
            )

        for page_no in (21, 22):

            if CODE not in normal(
                doc[page_no - 1].get_text("text")
            ):
                raise RuntimeError(
                    f"Trang {page_no} sai ma de."
                )

        text21 = normal(
            doc[20].get_text("text")
        )

        text22 = normal(
            doc[21].get_text("text")
        )

        # 70 dap an Nghe / Doc.
        pattern = re.compile(
            r"(?<!\d)(\d{1,2})\s*[.、]\s*"
            r"([A-F√×])(?=\s|$)"
        )

        objective = {}

        for match in pattern.finditer(text21):

            number = int(match.group(1))

            if not 1 <= number <= 70:
                continue

            if number in objective:
                raise RuntimeError(
                    f"Trung dap an cau {number}"
                )

            objective[number] = (
                match.group(2)
            )

        # 10 dap an Viet.
        writing_pattern = re.compile(
            r"^\s*(7[1-9]|80)\s*[.、]\s*"
            r"([^\n]+)",
            re.MULTILINE
        )

        writing = {}

        for match in writing_pattern.finditer(
            text22
        ):

            number = int(match.group(1))

            if number in writing:
                raise RuntimeError(
                    f"Trung dap an Viet cau {number}"
                )

            writing[number] = (
                match.group(2).strip()
            )

        answers = {
            **objective,
            **writing
        }

        if set(answers) != set(range(1, 81)):

            missing = sorted(
                set(range(1, 81))
                - set(answers)
            )

            raise RuntimeError(
                f"PDF thieu dap an: {missing}"
            )

        return answers


# =====================================================
# 11. KIEM TRA CUM TU PHAN VIET
# =====================================================

def verify_writing(answers):

    for number in range(71, 76):

        values = WRITING_TOKENS[number]

        valid = any(
            compact("".join(order))
            == compact(answers[number])

            for order in permutations(values)
        )

        if not valid:
            raise RuntimeError(
                f"Cac cum tu cau {number} "
                "khong ghep duoc dap an PDF."
            )

    for number in range(76, 81):

        answer = str(
            answers[number]
        ).strip()

        if len(answer) != 1:
            raise RuntimeError(
                f"Cau {number} khong phai "
                "dien mot chu Han."
            )


# =====================================================
# 12. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 03")
    print("BUOC 3 - CHUAN HOA H31003")
    print("=" * 60)

    # ================================================
    # 13. DOC JSON NGUON
    # ================================================

    template = read_json(TEMPLATE_FILE)

    source_answer = read_json(ANSWER_FILE)
    manifest = read_json(MANIFEST_FILE)

    if (
        template.get("ma_de_goc") != "H31001"
        or len(template.get("cau_hoi", [])) != 80
    ):
        raise RuntimeError(
            "JSON mau De 1 khong hop le."
        )

    if (
        source_answer.get("ma_de_goc") != CODE
        or source_answer.get("so_de") != 3
        or source_answer.get("cap_hsk") != 3
    ):
        raise RuntimeError(
            "JSON dap an buoc 1 sai de."
        )

    if (
        manifest.get("ma_de_goc") != CODE
        or manifest.get("so_de") != 3
        or manifest.get("so_cau") != 80
    ):
        raise RuntimeError(
            "Manifest anh buoc 2 sai de."
        )

    # ================================================
    # 14. TIM PDF VA MP3
    # ================================================

    pdf_files = list(
        SOURCE.glob("*.pdf")
    )

    mp3_files = list(
        SOURCE.glob("*.mp3")
    )

    if (
        len(pdf_files) != 1
        or len(mp3_files) != 1
    ):
        raise RuntimeError(
            "Thu muc DE 3 phai co "
            "dung 1 PDF va 1 MP3."
        )

    pdf_file = check_file(pdf_files[0])
    mp3_file = check_file(mp3_files[0])

    source_pdf = Path(
        source_answer.get("file_pdf", "")
    )

    if source_pdf.resolve() != pdf_file.resolve():
        raise RuntimeError(
            "PDF trong JSON buoc 1 "
            "khong khop file goc."
        )

    # ================================================
    # 15. DOI CHIEU 80 DAP AN
    # ================================================

    pdf_answers = read_pdf_answers(
        pdf_file
    )

    json_answers = source_answer.get(
        "dap_an", {}
    )

    if set(json_answers) != {
        str(n) for n in range(1, 81)
    }:
        raise RuntimeError(
            "JSON buoc 1 thieu dap an."
        )

    for number in range(1, 81):

        if compact(
            json_answers[str(number)]
        ) != compact(
            pdf_answers[number]
        ):
            raise RuntimeError(
                f"Dap an cau {number} "
                "khong khop PDF goc."
            )

    verify_writing(
        pdf_answers
    )

    print("\n===== KIEM TRA DAP AN =====")
    print("Nghe/Doc: 70/70")
    print("Viet: 10/10")
    print("Tong: 80/80")


    # ================================================
    # 16. KIEM TRA MANIFEST 80 CAU
    # ================================================

    expected_numbers = {
        str(n) for n in range(1, 81)
    }

    if set(
        manifest.get("cau_hoi", {})
    ) != expected_numbers:

        raise RuntimeError(
            "Manifest khong du 80 cau."
        )

    if set(
        manifest.get("bang_lua_chon", {})
    ) != set(GROUPS):

        raise RuntimeError(
            "Manifest khong du 6 bang."
        )


    # ================================================
    # 17. KIEM TRA 70 ANH CAU HOI
    # ================================================

    copies = []

    for number in range(1, 81):

        item = manifest["cau_hoi"][
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
                f"Cau {number} sai nhom."
            )

        if number <= 10:

            if item.get("anh") is not None:
                raise RuntimeError(
                    f"Cau {number} "
                    "khong dung anh rieng."
                )

            continue

        filename = (
            f"questions/cau_{number:02d}.png"
        )

        if item.get("anh") != filename:
            raise RuntimeError(
                f"Cau {number} sai ten anh."
            )

        source = check_file(
            OUTPUT / filename
        )

        destination = (
            MEDIA / filename
        )

        copies.append((
            source,
            destination
        ))


    # ================================================
    # 18. KIEM TRA 6 BANG LUA CHON
    # ================================================

    for name, (
        page_no,
        numbers
    ) in GROUPS.items():

        item = manifest[
            "bang_lua_chon"
        ][name]

        if (
            item.get("trang_pdf") != page_no
            or item.get("cau_tu") != numbers.start
            or item.get("cau_den")
            != numbers.stop - 1
        ):
            raise RuntimeError(
                f"Bang {name} khong hop le."
            )

        filename = (
            f"groups/{name}.png"
        )

        source = check_file(
            OUTPUT / filename
        )

        destination = (
            MEDIA / filename
        )

        copies.append((
            source,
            destination
        ))

    if len(copies) != 76:
        raise RuntimeError(
            "Khong du 76 anh."
        )

    print("\n===== KIEM TRA HINH =====")
    print("Anh cau hoi: 70/70")
    print("Bang chung: 6/6")


    # ================================================
    # 19. THOI LUONG MP3
    # ================================================

    duration = round(
        float(
            MP3(str(mp3_file)).info.length
        ),
        2
    )

    if duration <= 0:
        raise RuntimeError(
            "Thoi luong MP3 khong hop le."
        )


    # ================================================
    # 20. TAO JSON TU MAU H31001
    # ================================================

    final = replace_refs(
        deepcopy(template)
    )

    final.update({
        "cap_hsk": 3,
        "so_de": 3,
        "ma_de_goc": CODE,

        "ten_hien_thi": "Đề 3",
        "thu_tu": 3,

        "so_cau": 80,
        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "thoi_gian_phut": 85,

        "so_trang_pdf_de": 22,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        "trang_loi_thoai": list(
            range(15, 21)
        ),

        "trang_dap_an": [21, 22],

        "nguon_dap_an": "pdf_chung",

        "file_pdf": str(pdf_file),
        "file_mp3": str(mp3_file),
    })

    final.pop(
        "file_dap_an",
        None
    )


    # ================================================
    # 21. CAP NHAT AUDIO
    # ================================================

    final["audio"] = dict(
        final.get("audio") or {}
    )

    final["audio"].update({
        "duong_dan": (
            "/static/media/luyen_thi/"
            f"hsk3/{CODE}.mp3"
        ),

        "thoi_luong_giay": duration,
    })


    # ================================================
    # 22. TAO 80 CAU HOI
    # ================================================

    questions = []

    for number, old_question in enumerate(
        template["cau_hoi"],
        start=1
    ):

        if old_question.get("so_cau") != number:
            raise RuntimeError(
                f"JSON mau sai cau {number}."
            )

        question = replace_refs(
            deepcopy(old_question)
        )

        group = group_for(number)

        if number <= 10:
            question_image = None

        else:
            question_image = (
                "/static/media/luyen_thi/"
                "hsk3/de_03/questions/"
                f"cau_{number:02d}.png"
            )

        if group:
            group_image = (
                "/static/media/luyen_thi/"
                "hsk3/de_03/groups/"
                f"{group}.png"
            )

        else:
            group_image = None

        question.update({
            "so_cau": number,

            "ky_nang": skill(number),
            "phan": part(number),

            "loai_cau_hoi": kind(number),

            "noi_dung": None,

            "trang_pdf": page_for(number),

            "dap_an_dung": (
                pdf_answers[number]
            ),

            "lua_chon_json": choices(number),

            "da_duyet": False,

            "anh_cau_hoi": question_image,

            "anh_nhom_lua_chon": group_image,
        })

        # Dong bo cac truong loai cau.
        for field in (
            "dang",
            "dang_cau_hoi",
            "kieu_cau_hoi",
        ):

            if field in question:
                question[field] = kind(number)

        # Kiem tra dap an trac nghiem
        # phai nam trong lua chon.
        if number <= 70:

            if (
                pdf_answers[number]
                not in choice_values(number)
            ):
                raise RuntimeError(
                    f"Dap an cau {number} "
                    "khong thuoc lua chon."
                )

        questions.append(question)

    final["cau_hoi"] = questions


    # ================================================
    # 23. KIEM TRA SO CAU THEO KY NANG
    # ================================================

    counts = Counter(
        question["ky_nang"]
        for question in questions
    )

    if counts != {
        "nghe": 40,
        "doc": 30,
        "viet": 10,
    }:
        raise RuntimeError(
            "So cau Nghe/Doc/Viet khong dung."
        )


    # ================================================
    # 24. KIEM TRA JSON MOI
    # ================================================

    json_content = json.dumps(
        final,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    json_text = json_content.decode("utf-8")

    for old_ref in (
        "H31001",
        "/hsk3/de_01/",
        "de_01.json",
    ):

        if old_ref in json_text:
            raise RuntimeError(
                "JSON con tham chieu De 1: "
                + old_ref
            )

    if FINAL_FILE.exists():

        if FINAL_FILE.read_bytes() != json_content:
            raise RuntimeError(
                "JSON De 3 da ton tai "
                "voi noi dung khac.\n"
                "Khong ghi de:\n"
                + str(FINAL_FILE)
            )


    # ================================================
    # 25. KIEM TRA FILE DICH TRUOC KHI COPY
    # ================================================

    audio_destination = (
        MEDIA_ROOT / f"{CODE}.mp3"
    )

    media_copies = [
        *copies,
        (mp3_file, audio_destination),
    ]

    for source, destination in media_copies:

        if destination.exists():

            if not filecmp.cmp(
                source,
                destination,
                shallow=False
            ):
                raise RuntimeError(
                    "File dich khac noi dung.\n"
                    "Khong ghi de:\n"
                    + str(destination)
                )


    # ================================================
    # 26. SAO CHEP HINH VA MP3
    # ================================================

    print("\n===== SAO CHEP MEDIA =====")

    for source, destination in media_copies:

        if not destination.exists():

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(
                source,
                destination
            )


    # ================================================
    # 27. LUU JSON
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
    # 28. KET QUA
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH CHUAN HOA HSK3 DE 03")
    print("=" * 60)

    print("Ma de: H31003")
    print("Cap: HSK3")
    print("Tong cau: 80")

    print("Nghe: 40")
    print("Doc: 30")
    print("Viet: 10")

    print("Dap an: 80/80")
    print("Anh cau hoi: 70")
    print("Bang chung: 6")
    print("Tong anh: 76")

    print(f"MP3: {duration} giay")
    print("Thoi gian thi: 85 phut")

    print(f"\nJSON: {FINAL_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
