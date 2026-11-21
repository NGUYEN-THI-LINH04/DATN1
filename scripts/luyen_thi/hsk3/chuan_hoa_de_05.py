
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 05 - H31005

BUOC 3: CHUAN HOA DU LIEU

- Lay JSON HSK3 De 1 lam mau.
- Doc va doi chieu 80 dap an tu PDF.
- Kiem tra 70 anh cau hoi.
- Kiem tra 6 bang lua chon.
- Chuan hoa 40 Nghe, 30 Doc, 10 Viet.
- Kiem tra cum tu sap xep cau 71-75.
- Giu 2 dap an hop le cua cau 72.
- Sao chep 76 anh vao static.
- Sao chep MP3 H31005.
- Tao JSON de_05.json.

KHONG ket noi SQL Server.
KHONG ghi de file khac noi dung.
KHONG sua cac de cu.
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
# 1. CAU HINH DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "luyen_thi"

HSK3 = BASE / "hsk3"

SOURCE = (
    BASE / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 5"
)

DATA = HSK3 / "data" / "de_05"

OUTPUT = HSK3 / "output" / "de_05"

TEMPLATE_FILE = (
    HSK3 / "data" / "de_01" / "de_01.json"
)

ANSWER_FILE = DATA / "de_05_dap_an.json"

MANIFEST_FILE = (
    DATA / "hinh_80_cau_ung_vien.json"
)

FINAL_FILE = DATA / "de_05.json"

MEDIA_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk3"
)

MEDIA = MEDIA_ROOT / "de_05"

EXAM_CODE = "H31005"


# =====================================================
# 2. CUM TU SAP XEP CAU 71-75
# =====================================================

# Da doi chieu truc tiep voi PDF H31005.
# Khong lay tu de thi khac.

WRITING_TOKENS = {
    71: [
        "黑色",
        "李小姐的头发",
        "是",
        "的",
    ],

    72: [
        "时候",
        "举行",
        "会议",
        "什么",
    ],

    73: [
        "努力",
        "学习",
        "很",
        "他们班的学生",
    ],

    74: [
        "喜欢",
        "吃",
        "都",
        "马和羊",
        "草",
    ],

    75: [
        "自己的",
        "腿脚",
        "老年人",
        "要",
        "关心",
    ],
}


# =====================================================
# 3. SAU BANG LUA CHON CHUNG
# =====================================================

# Ten nhom: (trang, cau dau, cau cuoi, nhan)

GROUPS = {
    "nghe_01_05": (2, 1, 5, "ABCDEF"),
    "nghe_06_10": (3, 6, 10, "ABCDE"),

    "doc_41_45": (7, 41, 45, "ABCDEF"),
    "doc_46_50": (8, 46, 50, "ABCDE"),
    "doc_51_55": (9, 51, 55, "ABCDEF"),
    "doc_56_60": (10, 56, 60, "ABCDEF"),
}


# =====================================================
# 4. BO CUC TRANG PDF
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
            f"Thieu file hoac file rong:\n{path}"
        )

    return path


def read_json(path):

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
            .replace("H31001", EXAM_CODE)
            .replace("de_01", "de_05")
            .replace("Đề 1", "Đề 5")
            .replace("ĐỀ 1", "ĐỀ 5")
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
# 6. KY NANG
# =====================================================

def skill_for(number):

    if number <= 40:
        return "nghe"

    if number <= 70:
        return "doc"

    return "viet"


# =====================================================
# 7. LOAI CAU HOI
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
# 8. PHAN THI
# =====================================================

def part_for(number):

    if number <= 40:

        part_number = (
            (number - 1) // 10 + 1
        )

        return f"Nghe - Phần {part_number}"

    if number <= 50:
        return "Đọc - Phần 1"

    if number <= 60:
        return "Đọc - Phần 2"

    if number <= 70:
        return "Đọc - Phần 3"

    if number <= 75:
        return "Viết - Phần 1"

    return "Viết - Phần 2"


def page_for(number):

    for page, numbers in (
        PAGE_QUESTIONS.items()
    ):

        if number in numbers:
            return page

    raise RuntimeError(
        f"Khong tim thay trang cau {number}."
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
# 9. TAO LUA CHON CHO MOI CAU
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


def choices_for(number):

    return [
        {
            "ma": value,
            "nhan": value,
        }
        for value in choice_values(number)
    ]


# =====================================================
# 10. DOC 80 DAP AN TU PDF
# =====================================================

def read_pdf_answers(pdf_path):

    with fitz.open(pdf_path) as doc:

        if len(doc) != 22:
            raise RuntimeError(
                "PDF H31005 phai co 22 trang."
            )

        for page_no in (1, 21, 22):

            text = normalize(
                doc[page_no - 1].get_text(
                    "text"
                )
            )

            if EXAM_CODE not in text:
                raise RuntimeError(
                    f"Trang {page_no} "
                    "khong phai H31005."
                )

        page21 = normalize(
            doc[20].get_text("text")
        )

        page22 = doc[21].get_text("text")

        if (
            "答案" not in page21
            or "书" not in page22
        ):
            raise RuntimeError(
                "Trang 21-22 khong dung "
                "bo cuc dap an."
            )

        # ============================================
        # 11. DAP AN NGHE/DOC
        # ============================================

        objective = {}

        pattern = re.compile(
            r"(?<!\d)(\d{1,2})\s*[.、]"
            r"\s*([A-F√×])(?=\s|$)"
        )

        for match in pattern.finditer(
            page21
        ):

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
                "PDF khong du 70 dap an Nghe/Doc."
            )

        # ============================================
        # 12. DAP AN VIET
        # ============================================

        writing = {}

        writing_pattern = re.compile(
            r"^\s*(7[1-9]|80)\s*[.．、]"
            r"\s*([^\n]+)",
            re.MULTILINE
        )

        for match in (
            writing_pattern.finditer(page22)
        ):

            number = int(
                match.group(1)
            )

            if number in writing:
                raise RuntimeError(
                    f"Trung dap an Viet cau {number}."
                )

            writing[number] = [
                value.strip()

                for value in (
                    match.group(2).split("/")
                )

                if value.strip()
            ]

        if set(writing) != set(range(71, 81)):
            raise RuntimeError(
                "PDF khong du 10 dap an Viet."
            )

        # Chi cau 72 co hai dap an.
        for number, values in writing.items():

            expected_count = (
                2 if number == 72 else 1
            )

            if len(values) != expected_count:
                raise RuntimeError(
                    f"Cau {number} sai "
                    "so luong dap an."
                )

        if (
            compact(writing[72][0])
            == compact(writing[72][1])
        ):
            raise RuntimeError(
                "Hai dap an cau 72 bi trung."
            )

        answers = {
            **objective,

            **{
                number: values[0]
                for number, values
                in writing.items()
            }
        }

        alternatives = {
            "72": writing[72][1:]
        }

        # ============================================
        # 13. KIEM TRA CUM TU GOC CAU 71-75
        # ============================================

        writing_text = normalize(
            doc[12].get_text("text")
        )

        pdf_tokens = {}

        for line in writing_text.splitlines():

            match = re.match(
                r"^\s*(7[1-5])\s*[.．、]"
                r"\s*(.*)",
                line
            )

            if not match:
                continue

            number = int(
                match.group(1)
            )

            values = [
                value.strip()

                for value in re.split(
                    r"\s{2,}",
                    match.group(2)
                )

                if value.strip()
            ]

            pdf_tokens[number] = values

        if set(pdf_tokens) != set(
            range(71, 76)
        ):
            raise RuntimeError(
                "Khong doc du 5 cau sap xep "
                "tu PDF."
            )

        for number in range(71, 76):

            if Counter(
                pdf_tokens[number]
            ) != Counter(
                WRITING_TOKENS[number]
            ):
                raise RuntimeError(
                    f"Cac cum tu cau {number} "
                    "khong khop PDF goc."
                )

    return (
        answers,
        alternatives
    )


# =====================================================
# 14. KIEM TRA DAP AN PHAN VIET
# =====================================================

def validate_writing(
    answers,
    alternatives
):

    for number in range(71, 76):

        valid_sentences = [
            answers[number]
        ]

        valid_sentences.extend(
            alternatives.get(
                str(number), []
            )
        )

        possible_answers = {
            compact("".join(order))

            for order in permutations(
                WRITING_TOKENS[number]
            )
        }

        for sentence in valid_sentences:

            if (
                compact(sentence)
                not in possible_answers
            ):
                raise RuntimeError(
                    f"Cau {number} khong ghep "
                    f"duoc dap an: {sentence}"
                )

    for number in range(76, 81):

        if len(
            compact(answers[number])
        ) != 1:
            raise RuntimeError(
                f"Cau {number} khong phai "
                "dien mot chu Han."
            )


# =====================================================
# 15. KIEM TRA FILE TRUOC KHI COPY
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
                    "nhung khac noi dung:\n"
                    + str(destination)
                )


# =====================================================
# 16. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 05")
    print("BUOC 3 - CHUAN HOA H31005")
    print("=" * 60)

    # ================================================
    # 17. DOC JSON MAU VA DU LIEU NGUON
    # ================================================

    template = read_json(
        TEMPLATE_FILE
    )

    source_answers = read_json(
        ANSWER_FILE
    )

    manifest = read_json(
        MANIFEST_FILE
    )

    if (
        template.get("ma_de_goc") != "H31001"
        or len(
            template.get("cau_hoi", [])
        ) != 80
    ):
        raise RuntimeError(
            "JSON mau HSK3 De 1 "
            "khong hop le."
        )

    if (
        source_answers.get("cap_hsk"),
        source_answers.get("so_de"),
        source_answers.get("ma_de_goc")
    ) != (3, 5, EXAM_CODE):
        raise RuntimeError(
            "JSON dap an buoc 1 "
            "khong phai H31005."
        )

    if (
        manifest.get("cap_hsk"),
        manifest.get("so_de"),
        manifest.get("ma_de_goc"),
        manifest.get("so_cau")
    ) != (3, 5, EXAM_CODE, 80):
        raise RuntimeError(
            "Manifest buoc 2 "
            "khong phai H31005."
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
            "Thu muc DE 5 phai co "
            "dung 1 PDF va 1 MP3."
        )

    pdf_file = check_file(
        pdfs[0]
    )

    mp3_file = check_file(
        mp3s[0]
    )

    source_pdf = Path(
        source_answers.get(
            "file_pdf", ""
        )
    )

    if (
        source_pdf.resolve()
        != pdf_file.resolve()
    ):
        raise RuntimeError(
            "PDF buoc 1 khong khop "
            "PDF trong thu muc goc."
        )

    # ================================================
    # 19. DOI CHIEU 80 DAP AN
    # ================================================

    pdf_answers, pdf_alternatives = (
        read_pdf_answers(pdf_file)
    )

    answers = source_answers.get(
        "dap_an", {}
    )

    if set(answers) != {
        str(n) for n in range(1, 81)
    }:
        raise RuntimeError(
            "JSON buoc 1 thieu 80 dap an."
        )

    for number in range(1, 81):

        actual = compact(
            answers[str(number)]
        )

        expected = compact(
            pdf_answers[number]
        )

        if actual != expected:
            raise RuntimeError(
                f"Sai dap an cau {number} "
                "so voi PDF."
            )

    # ================================================
    # 20. KIEM TRA DAP AN THAY THE
    # ================================================

    source_alternatives = (
        source_answers.get(
            "dap_an_thay_the", {}
        )
    )

    if (
        set(source_alternatives) != {"72"}
        or source_alternatives["72"]
        != pdf_alternatives["72"]
    ):
        raise RuntimeError(
            "Dap an thay the cau 72 "
            "khong khop PDF."
        )

    validate_writing(
        pdf_answers,
        pdf_alternatives
    )

    print("\n===== KIEM TRA DAP AN =====")
    print("Nghe/Doc: 70/70")
    print("Viet: 10/10")
    print("Tong: 80/80")
    print("Cau 72: 2 dap an hop le")

    # ================================================
    # 21. KIEM TRA MANIFEST
    # ================================================

    question_manifest = (
        manifest.get("cau_hoi", {})
    )

    group_manifest = (
        manifest.get(
            "bang_lua_chon", {}
        )
    )

    if set(question_manifest) != {
        str(n) for n in range(1, 81)
    }:
        raise RuntimeError(
            "Manifest khong du 80 cau."
        )

    if set(group_manifest) != set(
        GROUPS
    ):
        raise RuntimeError(
            "Manifest khong du 6 bang."
        )

    # ================================================
    # 22. KIEM TRA 70 ANH CAU HOI
    # ================================================

    copies = []

    for number in range(1, 81):

        info = question_manifest[
            str(number)
        ]

        if (
            info.get("trang_pdf")
            != page_for(number)
        ):
            raise RuntimeError(
                f"Cau {number} sai trang PDF."
            )

        if (
            info.get("nhom_lua_chon")
            != group_for(number)
        ):
            raise RuntimeError(
                f"Cau {number} sai nhom "
                "lua chon."
            )

        if number <= 10:

            if info.get("anh") is not None:
                raise RuntimeError(
                    f"Cau {number} khong "
                    "dung anh rieng."
                )

            continue

        relative = (
            f"questions/cau_{number:02d}.png"
        )

        if info.get("anh") != relative:
            raise RuntimeError(
                f"Manifest sai anh cau {number}."
            )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    # ================================================
    # 23. KIEM TRA 6 BANG LUA CHON
    # ================================================

    for name, (
        page,
        first,
        last,
        labels
    ) in GROUPS.items():

        info = group_manifest[name]

        actual = (
            info.get("trang_pdf"),
            info.get("cau_tu"),
            info.get("cau_den"),
            info.get("lua_chon"),
        )

        expected = (
            page,
            first,
            last,
            labels,
        )

        if actual != expected:
            raise RuntimeError(
                f"Manifest sai bang {name}."
            )

        relative = (
            f"groups/{name}.png"
        )

        if info.get("anh") != relative:
            raise RuntimeError(
                f"Manifest sai anh bang {name}."
            )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    if len(copies) != 76:
        raise RuntimeError(
            f"Khong du 76 anh: {len(copies)}"
        )

    print("\n===== KIEM TRA HINH =====")
    print("Anh cau hoi: 70/70")
    print("Bang chung: 6/6")
    print("Tong anh: 76")

    # ================================================
    # 24. DOC THOI LUONG MP3
    # ================================================

    duration = round(
        float(
            MP3(str(mp3_file)).info.length
        ),
        2
    )

    if not 0 < duration < 99999999:
        raise RuntimeError(
            "Thoi luong MP3 khong hop le."
        )

    # ================================================
    # 25. TAO JSON TU MAU H31001
    # ================================================

    result = replace_refs(
        deepcopy(template)
    )

    result.update({
        "cap_hsk": 3,
        "so_de": 5,
        "ma_de_goc": EXAM_CODE,

        "ten_hien_thi": "Đề 5",
        "thu_tu": 5,

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

        # Bao toan dap an thu hai cau 72.
        "dap_an_thay_the": (
            pdf_alternatives
        ),
    })

    result.pop(
        "file_dap_an",
        None
    )

    # ================================================
    # 26. CAP NHAT AUDIO
    # ================================================

    if not isinstance(
        result.get("audio"),
        dict
    ):
        raise RuntimeError(
            "JSON mau thieu cau truc audio."
        )

    result["audio"]["duong_dan"] = (
        "/static/media/luyen_thi/"
        f"hsk3/{EXAM_CODE}.mp3"
    )

    result["audio"]["thoi_luong_giay"] = (
        duration
    )

    # ================================================
    # 27. TAO 80 CAU HOI
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
                "hsk3/de_05/questions/"
                f"cau_{number:02d}.png"
            )

        if group:

            group_image = (
                "/static/media/luyen_thi/"
                "hsk3/de_05/groups/"
                f"{group}.png"
            )

        else:

            group_image = None

        question.update({
            "so_cau": number,

            "ky_nang": skill_for(number),

            "phan": part_for(number),

            "loai_cau_hoi": kind_for(number),

            # Noi dung goc da co trong anh.
            # Khong sao chep text De 1.
            "noi_dung": None,

            "trang_pdf": page_for(number),

            "dap_an_dung": (
                pdf_answers[number]
            ),

            "lua_chon_json": (
                choices_for(number)
            ),

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
                question[field] = kind_for(
                    number
                )

        # Khong ke thua dap an thay the
        # cua cac de khac.
        question.pop(
            "dap_an_thay_the",
            None
        )

        # Cau 72 co hai dap an dung.
        if number == 72:

            question["dap_an_thay_the"] = (
                list(
                    pdf_alternatives["72"]
                )
            )

        # Dap an trac nghiem phai
        # nam trong cac lua chon.
        if number <= 70:

            allowed = {
                item["ma"]

                for item in choices_for(
                    number
                )
            }

            if (
                pdf_answers[number]
                not in allowed
            ):
                raise RuntimeError(
                    f"Dap an cau {number} "
                    "khong nam trong lua chon."
                )

        questions.append(question)

    result["cau_hoi"] = questions

    # ================================================
    # 28. KIEM TRA KY NANG
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
            "So cau Nghe/Doc/Viet sai."
        )

    # ================================================
    # 29. KIEM TRA JSON MOI
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
        "de_01.json",
    ):

        if old_ref in raw:
            raise RuntimeError(
                "JSON con tham chieu De 1: "
                + old_ref
            )

    if FINAL_FILE.exists():

        if (
            FINAL_FILE.read_bytes()
            != json_content
        ):
            raise RuntimeError(
                "JSON De 5 da ton tai "
                "voi noi dung khac.\n"
                "Khong ghi de:\n"
                + str(FINAL_FILE)
            )

    # ================================================
    # 30. KIEM TRA FILE MEDIA DICH
    # ================================================

    copies.append((
        mp3_file,
        MEDIA_ROOT / f"{EXAM_CODE}.mp3"
    ))

    check_copy_pairs(
        copies
    )

    # ================================================
    # 31. SAO CHEP MEDIA
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
    # 32. LUU JSON
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
    # 33. KET QUA
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH CHUAN HOA HSK3 DE 05")
    print("=" * 60)

    print("Ma de: H31005")
    print("Cap: HSK3")

    print("Tong cau: 80")
    print("Nghe: 40")
    print("Doc: 30")
    print("Viet: 10")

    print("Dap an: 80/80")
    print("Anh cau hoi: 70/70")
    print("Bang chung: 6/6")
    print("Tong anh: 76")

    print(
        "Cau 72: da luu 2 dap an "
        "hop le trong JSON"
    )

    print(f"MP3: {duration} giay")
    print("Thoi gian thi: 85 phut")

    print(f"\nJSON: {FINAL_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
