
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 07 (H31007)
BUOC 3: CHUAN HOA DU LIEU

- PDF de thi 14 trang.
- PDF dap an rieng 2 trang.
- Doi chieu 80 dap an.
- Kiem tra 70 anh cau hoi va 6 bang lua chon.
- Cau 72: dung dap an khop cum tu trong PDF de.
- Cau 77: giu 2 dap an 元 / 圆.
- Sao chep 76 anh va MP3 sang static.
- Tao JSON de_07.json.

KHONG ket noi SQL Server.
KHONG sua cac de thi cu.
KHONG ghi de file khac noi dung.
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
    / "HSK3" / "ĐỀ 7"
)

DATA = HSK3 / "data" / "de_07"

OUTPUT = HSK3 / "output" / "de_07"

MEDIA_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk3"
)

MEDIA = MEDIA_ROOT / "de_07"

TEMPLATE_FILE = (
    HSK3 / "data" / "de_01" / "de_01.json"
)

ANSWER_FILE = DATA / "de_07_dap_an.json"

MANIFEST_FILE = (
    DATA / "hinh_80_cau_ung_vien.json"
)

FINAL_FILE = DATA / "de_07.json"

CODE = "H31007"


# =====================================================
# 2. CAC BANG LUA CHON CHUNG
# =====================================================

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
# 4. HAI DAP AN DAC BIET
# =====================================================

# Cau 72:
# PDF de ghi "他的姓名".
# PDF dap an ghi "他的名字".
# Dap an moi phai ghep duoc tu cum tu trong de.

MAIN_72 = "他的姓名被写错了。"

PDF_72 = "他的名字被写错了。"

# Cau 77: PDF chap nhan hai chu Han.

MAIN_77 = "元"
ALT_77 = "圆"


# =====================================================
# 5. HAM HO TRO
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


def load_json(path):

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
# 6. DOI THAM CHIEU DE 1 SANG DE 7
# =====================================================

def replace_refs(value):

    if isinstance(value, str):

        return (
            value
            .replace("H31001", CODE)
            .replace("de_01", "de_07")
            .replace("Đề 1", "Đề 7")
            .replace("ĐỀ 1", "ĐỀ 7")
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
# 7. XAC DINH KY NANG
# =====================================================

def skill_for(number):

    if number <= 40:
        return "nghe"

    if number <= 70:
        return "doc"

    return "viet"


# =====================================================
# 8. XAC DINH LOAI CAU HOI
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
# 9. XAC DINH PHAN THI
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


# =====================================================
# 10. XAC DINH TRANG PDF
# =====================================================

def page_for(number):

    for page, numbers in (
        PAGE_QUESTIONS.items()
    ):

        if number in numbers:
            return page

    raise RuntimeError(
        f"Khong tim thay trang cau {number}."
    )


# =====================================================
# 11. XAC DINH NHOM LUA CHON
# =====================================================

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
# 12. TAO LUA CHON THEO DANG CAU
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


# =====================================================
# 13. DOC HAI PDF VA DAP AN
# =====================================================

def read_pdf_answers(
    exam_pdf,
    answer_pdf
):

    with (
        fitz.open(exam_pdf) as exam,
        fitz.open(answer_pdf) as key
    ):

        if len(exam) != 14:
            raise RuntimeError(
                "PDF de H31007 phai co 14 trang."
            )

        if len(key) != 2:
            raise RuntimeError(
                "PDF dap an phai co 2 trang."
            )

        if CODE not in exam[0].get_text("text"):
            raise RuntimeError(
                "PDF de khong phai H31007."
            )

        if CODE not in key[0].get_text("text"):
            raise RuntimeError(
                "PDF dap an khong phai H31007."
            )

        text1 = unicodedata.normalize(
            "NFKC",
            key[0].get_text("text")
        )

        text2 = key[1].get_text("text")

        # ============================================
        # 14. DOC 70 DAP AN NGHE/DOC
        # ============================================

        objective = {}

        pattern = re.compile(
            r"(?<!\d)(\d{1,2})\s*[.．、]"
            r"\s*([A-F√×])(?=\s|$)"
        )

        for match in pattern.finditer(text1):

            number = int(match.group(1))

            if not 1 <= number <= 70:
                continue

            if number in objective:
                raise RuntimeError(
                    f"Trung dap an cau {number}."
                )

            objective[number] = match.group(2)

        if set(objective) != set(range(1, 71)):
            raise RuntimeError(
                "PDF khong du 70 dap an Nghe/Doc."
            )

        # ============================================
        # 15. DOC 10 DAP AN VIET
        # ============================================

        writing = {}

        writing_pattern = re.compile(
            r"^\s*(7[1-9]|80)\s*[.．、]"
            r"\s*([^\n]+)",
            re.MULTILINE
        )

        for match in writing_pattern.finditer(
            text2
        ):

            number = int(match.group(1))

            if number in writing:
                raise RuntimeError(
                    f"Trung dap an Viet cau {number}."
                )

            writing[number] = [
                item.strip()

                for item in (
                    match.group(2).split("/")
                )

                if item.strip()
            ]

        if set(writing) != set(range(71, 81)):
            raise RuntimeError(
                "PDF khong du 10 dap an Viet."
            )

        # ============================================
        # 16. KIEM TRA CAU 72 VA 77
        # ============================================

        if writing[72] != [PDF_72]:
            raise RuntimeError(
                "PDF dap an cau 72 "
                "khac nguon da doi chieu."
            )

        if writing[77] != [
            MAIN_77,
            ALT_77
        ]:
            raise RuntimeError(
                "PDF dap an cau 77 "
                "khong co du 元 / 圆."
            )

        for number, values in writing.items():

            expected_count = (
                2 if number == 77 else 1
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
                for number, values
                in writing.items()
            }
        }

        # ============================================
        # 17. DOC CUM TU SAP XEP 71-75
        # ============================================

        tokens = {}

        text_questions = (
            exam[12].get_text("text")
        )

        for line in text_questions.splitlines():

            match = re.match(
                r"^\s*(7[1-5])\s*[.．、]"
                r"\s*(.+)",
                line
            )

            if not match:
                continue

            number = int(match.group(1))

            if number in tokens:
                raise RuntimeError(
                    f"Trung cum tu cau {number}."
                )

            tokens[number] = [
                item.strip()

                for item in re.split(
                    r"\s{2,}",
                    match.group(2)
                )

                if item.strip()
            ]

        if set(tokens) != set(range(71, 76)):
            raise RuntimeError(
                "PDF de khong du cum tu 71-75."
            )

        # ============================================
        # 18. KIEM TRA DAP AN SAP XEP
        # ============================================

        if (
            "他的姓名" not in tokens[72]
            or "他的名字" in tokens[72]
        ):
            raise RuntimeError(
                "Cum tu cau 72 khac du kien."
            )

        for number in range(71, 76):

            answer = (
                MAIN_72
                if number == 72
                else answers[number]
            )

            valid = any(
                compact("".join(order))
                == compact(answer)

                for order in permutations(
                    tokens[number]
                )
            )

            if not valid:
                raise RuntimeError(
                    f"Cau {number} khong ghep "
                    "duoc dap an tu PDF de."
                )

        # ============================================
        # 19. KIEM TRA DANG DIEN CHU HAN
        # ============================================

        for number in range(76, 81):

            if len(
                compact(answers[number])
            ) != 1:
                raise RuntimeError(
                    f"Cau {number} "
                    "khong phai mot chu Han."
                )

    return answers, tokens


# =====================================================
# 20. KIEM TRA FILE TRUOC KHI COPY
# =====================================================

def check_copy_pairs(pairs):

    for source, destination in pairs:

        require_file(source)

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
# 21. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 07")
    print("BUOC 3 - CHUAN HOA H31007")
    print("=" * 60)

    # ================================================
    # 22. DOC DU LIEU CAC BUOC TRUOC
    # ================================================

    template = load_json(
        TEMPLATE_FILE
    )

    source = load_json(
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
            "JSON mau H31001 khong hop le."
        )

    if (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc")
    ) != (3, 7, CODE):

        raise RuntimeError(
            "JSON buoc 1 khong phai H31007."
        )

    if (
        manifest.get("cap_hsk"),
        manifest.get("so_de"),
        manifest.get("ma_de_goc"),
        manifest.get("so_cau")
    ) != (3, 7, CODE, 80):

        raise RuntimeError(
            "Manifest buoc 2 khong hop le."
        )

    if (
        manifest.get("so_trang_pdf"),
        manifest.get("so_trang_pdf_dap_an"),
        manifest.get("trang_dap_an")
    ) != (14, 2, [1, 2]):

        raise RuntimeError(
            "Manifest sai so trang PDF."
        )

    # ================================================
    # 23. TIM PDF VA MP3 GOC
    # ================================================

    exam_files = []
    answer_files = []

    mp3_files = sorted(
        SOURCE.glob("*.mp3")
    )

    for path in SOURCE.glob("*.pdf"):

        with fitz.open(
            require_file(path)
        ) as doc:

            if len(doc) == 14:
                exam_files.append(path)

            elif len(doc) == 2:
                answer_files.append(path)

            else:
                raise RuntimeError(
                    f"PDF co so trang sai: {path}"
                )

    if (
        len(exam_files) != 1
        or len(answer_files) != 1
        or len(mp3_files) != 1
    ):
        raise RuntimeError(
            "Thu muc DE 7 can dung:"
            "\n- 1 PDF de thi 14 trang"
            "\n- 1 PDF dap an 2 trang"
            "\n- 1 file MP3"
        )

    exam_pdf = exam_files[0]
    answer_pdf = answer_files[0]

    mp3_file = require_file(
        mp3_files[0]
    )

    # ================================================
    # 24. KIEM TRA DUONG DAN NGUON
    # ================================================

    for field, path in (
        ("file_pdf", exam_pdf),
        ("file_dap_an", answer_pdf)
    ):

        source_path = source.get(field)

        if (
            not source_path
            or Path(source_path).resolve()
            != path.resolve()
        ):
            raise RuntimeError(
                f"File {field} khong khop "
                "nguon buoc 1."
            )

    if source.get("file_mp3"):

        if (
            Path(source["file_mp3"]).resolve()
            != mp3_file.resolve()
        ):
            raise RuntimeError(
                "MP3 trong JSON buoc 1 "
                "khong khop file goc."
            )

    # ================================================
    # 25. DOI CHIEU 80 DAP AN
    # ================================================

    pdf_answers, pdf_tokens = (
        read_pdf_answers(
            exam_pdf,
            answer_pdf
        )
    )

    source_answers = source.get(
        "dap_an", {}
    )

    if set(source_answers) != {
        str(number)
        for number in range(1, 81)
    }:
        raise RuntimeError(
            "JSON buoc 1 khong du 80 dap an."
        )

    for number in range(1, 81):

        if compact(
            source_answers[str(number)]
        ) != compact(
            pdf_answers[number]
        ):
            raise RuntimeError(
                f"Dap an cau {number} "
                "khong khop PDF."
            )

    # ================================================
    # 26. BAO TOAN DAP AN THAY THE 77
    # ================================================

    expected_alt = {
        "77": [ALT_77]
    }

    if (
        source.get("dap_an_thay_the")
        != expected_alt
    ):
        raise RuntimeError(
            "JSON buoc 1 thieu "
            "dap an thay the cau 77."
        )

    if (
        manifest.get("dap_an_thay_the")
        != expected_alt
    ):
        raise RuntimeError(
            "Manifest buoc 2 thieu "
            "dap an thay the cau 77."
        )

    # ================================================
    # 27. DOI CHIEU CUM TU SAP XEP
    # ================================================

    expected_tokens = {
        str(number): pdf_tokens[number]
        for number in range(71, 76)
    }

    if (
        source.get("cum_tu_sap_xep")
        != expected_tokens
    ):
        raise RuntimeError(
            "Cum tu sap xep khong khop PDF."
        )

    # ================================================
    # 28. KIEM TRA CANH BAO CAU 72
    # ================================================

    issues = source.get(
        "can_ra_soat", []
    )

    if (
        issues
        != manifest.get("can_ra_soat")
    ):
        raise RuntimeError(
            "Canh bao cau 72 giua "
            "hai buoc khong khop."
        )

    if not isinstance(issues, list):
        raise RuntimeError(
            "Danh sach can_ra_soat sai."
        )

    matched_issue = any(
        item.get("so_cau") == 72
        and compact(
            item.get("dap_an_trong_pdf")
        ) == compact(PDF_72)
        and compact(
            item.get("goi_y_theo_cum_tu")
        ) == compact(MAIN_72)

        for item in issues
    )

    if not matched_issue:
        raise RuntimeError(
            "Thieu ghi chu doi chieu cau 72."
        )

    # ================================================
    # 29. CHON DAP AN SU DUNG
    # ================================================

    selected_answers = dict(
        pdf_answers
    )

    # Chi thay dap an cau 72 trong JSON moi.
    # Khong sua PDF goc.
    selected_answers[72] = MAIN_72

    print("\n===== KIEM TRA DAP AN =====")

    print("Nghe/Doc: 70/70")
    print("Viet: 10/10")
    print("Tong: 80/80")

    print(
        "Cau 72: da chon dap an "
        "khop cum tu PDF de."
    )

    print(
        "Cau 77: 2 dap an hop le "
        "(元 / 圆)"
    )

    # ================================================
    # 30. KIEM TRA MANIFEST 80 CAU
    # ================================================

    question_manifest = manifest.get(
        "cau_hoi", {}
    )

    group_manifest = manifest.get(
        "bang_lua_chon", {}
    )

    if set(question_manifest) != {
        str(number)
        for number in range(1, 81)
    }:
        raise RuntimeError(
            "Manifest khong du 80 cau."
        )

    if set(group_manifest) != set(GROUPS):
        raise RuntimeError(
            "Manifest khong du 6 bang."
        )

    copies = []

    # ================================================
    # 31. KIEM TRA 70 ANH CAU HOI
    # ================================================

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
                f"Cau {number} sai nhom hinh."
            )

        if number <= 10:

            if item.get("anh") is not None:
                raise RuntimeError(
                    f"Cau {number} khong "
                    "dung anh rieng."
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
    # 32. KIEM TRA 6 BANG LUA CHON
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
            item.get("anh")
        )

        expected = (
            page,
            first,
            last,
            labels,
            f"groups/{name}.png"
        )

        if actual != expected:
            raise RuntimeError(
                f"Manifest sai bang {name}."
            )

        relative = (
            f"groups/{name}.png"
        )

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
    print("Tong anh: 76")

    # ================================================
    # 33. DOC THOI LUONG MP3
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

    if not 0 < duration < 99999999:
        raise RuntimeError(
            "Thoi luong MP3 khong hop le."
        )

    # ================================================
    # 34. TAO JSON TU MAU H31001
    # ================================================

    result = replace_refs(
        deepcopy(template)
    )

    result.update({
        "ma_de_goc": CODE,

        "cap_hsk": 3,
        "so_de": 7,
        "thu_tu": 7,

        "ten_hien_thi": "Đề 7",

        "so_cau": 80,
        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "thoi_gian_phut": 85,

        "so_trang_pdf_de": 14,
        "so_trang_pdf_dap_an": 2,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        "trang_loi_thoai": [],

        "trang_dap_an": [1, 2],

        "nguon_dap_an": "pdf_rieng",

        "file_pdf": str(exam_pdf),
        "file_dap_an": str(answer_pdf),

        "file_mp3": str(mp3_file),

        "dap_an_thay_the": {
            "77": [ALT_77]
        },

        # Giu lai thong tin sai khac nguon.
        "can_ra_soat": [
            {
                "so_cau": 72,

                "loai": (
                    "dieu_chinh_dap_an_"
                    "theo_pdf_de"
                ),

                "dap_an_pdf_goc": PDF_72,

                "dap_an_duoc_su_dung": MAIN_72,

                "trang_thai": (
                    "da_chon_theo_de_"
                    "can_duyet_truoc_xuat_ban"
                ),

                "ghi_chu": (
                    "PDF de dung 他的姓名, "
                    "PDF dap an dung 他的名字. "
                    "Khong sua PDF goc."
                ),
            }
        ],
    })

    # ================================================
    # 35. CAP NHAT AUDIO
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
    # 36. TAO 80 CAU HOI
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
                "hsk3/de_07/questions/"
                f"cau_{number:02d}.png"
            )

        if group:

            group_image = (
                "/static/media/luyen_thi/"
                "hsk3/de_07/groups/"
                f"{group}.png"
            )

        else:

            group_image = None

        options = choice_values(
            number,
            pdf_tokens
        )

        question.update({
            "so_cau": number,

            "ky_nang": skill_for(number),

            "phan": part_for(number),

            "loai_cau_hoi": kind_for(number),

            "noi_dung": None,

            "trang_pdf": page_for(number),

            "dap_an_dung": (
                selected_answers[number]
            ),

            "lua_chon_json": [
                {
                    "ma": item,
                    "nhan": item
                }
                for item in options
            ],

            "da_duyet": False,

            "anh_cau_hoi": question_image,

            "anh_nhom_lua_chon": group_image,
        })

        # Dong bo cac truong dang cau neu co.
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
        # tu cac de khac.
        question.pop(
            "dap_an_thay_the",
            None
        )

        # Cau 77 chap nhan 元 va 圆.
        if number == 77:

            question["dap_an_thay_the"] = [
                ALT_77
            ]

        # Ghi chu thay doi dap an cau 72.
        if number == 72:

            question[
                "ghi_chu_dieu_chinh_dap_an"
            ] = (
                "PDF de ghi 他的姓名; "
                "PDF dap an ghi 他的名字."
            )

        # Kiem tra dap an trac nghiem.
        if number <= 70:

            if (
                selected_answers[number]
                not in options
            ):
                raise RuntimeError(
                    f"Dap an cau {number} "
                    "khong nam trong lua chon."
                )

        questions.append(question)

    result["cau_hoi"] = questions

    # ================================================
    # 37. KIEM TRA KY NANG
    # ================================================

    counts = Counter(
        question["ky_nang"]
        for question in questions
    )

    if counts != {
        "nghe": 40,
        "doc": 30,
        "viet": 10
    }:
        raise RuntimeError(
            "Sai so cau theo ky nang."
        )

    # ================================================
    # 38. KIEM TRA JSON MOI
    # ================================================

    json_content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    text = json_content.decode("utf-8")

    for old_ref in (
        "H31001",
        "/hsk3/de_01/"
    ):

        if old_ref in text:
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
                "JSON De 7 da ton tai "
                "voi noi dung khac:\n"
                + str(FINAL_FILE)
            )

    # ================================================
    # 39. KIEM TRA MEDIA DICH
    # ================================================

    copies.append((
        mp3_file,
        MEDIA_ROOT / f"{CODE}.mp3"
    ))

    check_copy_pairs(
        copies
    )

    # ================================================
    # 40. SAO CHEP 76 ANH VA MP3
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
    # 41. LUU JSON
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
    # 42. KET QUA
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH CHUAN HOA HSK3 DE 07"
    )

    print("=" * 60)

    print("Ma de: H31007")
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
        "Cau 72: da dieu chinh "
        "dap an theo PDF de"
    )

    print(
        "Cau 77: da luu "
        "2 dap an 元 / 圆"
    )

    print("PDF de: 14 trang")
    print("PDF dap an: 2 trang")

    print(f"MP3: {duration} giay")
    print("Thoi gian thi: 85 phut")

    print(f"\nJSON: {FINAL_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
