
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 01 - H31001

BUOC 3: CHUAN HOA DU LIEU

- Su dung cau truc JSON HSK2 De 11 lam mau.
- Doc JSON 80 dap an cua HSK3.
- Kiem tra PDF goc H31001 (22 trang).
- Kiem tra 70 dap an Nghe/Doc va 10 dap an Viet.
- Kiem tra 70 anh cau hoi va 6 bang lua chon.
- Giu dung noi dung cau Viet 71-80.
- Sao chep anh sang static/media/luyen_thi/hsk3.
- Sao chep MP3 sang H31001.mp3.
- Tao de_01.json cho buoc kiem tra.

KHONG ket noi SQL Server.
KHONG sua HSK1/HSK2.
"""

from pathlib import Path
from copy import deepcopy
import filecmp
import json
import re
import shutil
import subprocess
import unicodedata

import fitz


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

HSK3 = (
    ROOT / "scripts" / "luyen_thi" / "hsk3"
)

SOURCE = (
    ROOT / "scripts" / "luyen_thi"
    / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 1"
)

DATA = HSK3 / "data" / "de_01"
OUTPUT = HSK3 / "output" / "de_01"

PDF_FILE = (
    SOURCE / "Đề thi tiếng Trung HSK3 SỐ 1.pdf"
)

MP3_FILE = (
    SOURCE / "Đề thi tiếng Trung HSK3 SỐ 1.mp3"
)

ANSWER_JSON = DATA / "de_01_dap_an.json"

IMAGE_JSON = (
    DATA / "hinh_80_cau_ung_vien.json"
)

# JSON HSK2 De 11 da nhap thanh cong.
TEMPLATE = (
    ROOT / "scripts" / "luyen_thi"
    / "hsk2" / "data" / "de_11"
    / "de_11.json"
)

STATIC = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk3"
)

MEDIA = STATIC / "de_01"

FINAL_JSON = DATA / "de_01.json"

EXAM_CODE = "H31001"
EXAM_NUMBER = 1


# =====================================================
# 2. BO CUC PDF HSK3 DE 1
# =====================================================

PAGE_QUESTIONS = {
    2: list(range(1, 6)),
    3: list(range(6, 11)),
    4: list(range(11, 21)),
    5: list(range(21, 31)),
    6: list(range(31, 41)),
    7: list(range(41, 46)),
    8: list(range(46, 51)),
    9: list(range(51, 56)),
    10: list(range(56, 61)),
    11: list(range(61, 65)),
    12: list(range(65, 71)),
    13: list(range(71, 76)),
    14: list(range(76, 81)),
}

GROUPS = {
    "nghe_01_05": range(1, 6),
    "nghe_06_10": range(6, 11),
    "doc_41_45": range(41, 46),
    "doc_46_50": range(46, 51),
    "doc_51_55": range(51, 56),
    "doc_56_60": range(56, 61),
}

GROUP_PAGES = {
    "nghe_01_05": 2,
    "nghe_06_10": 3,
    "doc_41_45": 7,
    "doc_46_50": 8,
    "doc_51_55": 9,
    "doc_56_60": 10,
}


# =====================================================
# 3. DAP AN H31001
# =====================================================

OBJECTIVE_ROWS = [
    "B C E F A",
    "B C A D E",
    "× √ × √ √",
    "× √ √ × ×",
    "B C C C B",
    "C A A B C",
    "B B B C A",
    "C A C A A",
    "C B A D F",
    "B D E A C",
    "F D C B A",
    "A B E F C",
    "A A C B B",
    "A A B B C",
]

WRITING_ANSWERS = {
    71: "弟弟高兴地笑了。",
    72: "上午的考试比较简单。",
    73: "这个城市的环境变得越来越好了。",
    74: "那位医生送给他一个礼物。",
    75: "其他班的成绩也有很大提高。",
    76: "出",
    77: "元",
    78: "叫",
    79: "中",
    80: "米",
}


# =====================================================
# 4. CAC HAM HO TRO
# =====================================================

def check_file(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    if path.stat().st_size == 0:
        raise RuntimeError(
            f"File rong: {path}"
        )


def load_json(path):

    check_file(path)

    with path.open(
        "r",
        encoding="utf-8-sig"
    ) as f:
        return json.load(f)


def normalize(text):

    return unicodedata.normalize(
        "NFKC",
        str(text)
    )


def normalize_code(text):

    return re.sub(
        r"[^A-Z0-9]",
        "",
        normalize(text).upper()
    )


def group_for(number):

    for name, numbers in GROUPS.items():

        if number in numbers:
            return name

    return None


def page_for(number):

    for page_no, numbers in PAGE_QUESTIONS.items():

        if number in numbers:
            return page_no

    raise RuntimeError(
        f"Khong tim thay trang cau {number}."
    )


def section_for(number):

    if number <= 40:
        return "nghe"

    if number <= 70:
        return "doc"

    return "viet"


def type_for(number):

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
        return "sap_xep_tu"

    return "dien_chu_han"


# =====================================================
# 5. TAO BANG 80 DAP AN CHINH THUC
# =====================================================

def expected_answers():

    result = {}

    for row_index, row in enumerate(
        OBJECTIVE_ROWS
    ):

        values = row.split()

        if len(values) != 5:
            raise RuntimeError(
                "Bang dap an sai dinh dang."
            )

        for index, answer in enumerate(values):

            number = row_index * 5 + index + 1

            result[number] = answer

    result.update(WRITING_ANSWERS)

    if set(result) != set(range(1, 81)):
        raise RuntimeError(
            "Bang dap an khong du 80 cau."
        )

    return result


EXPECTED = expected_answers()


# =====================================================
# 6. KIEM TRA PDF GOC
# =====================================================

def check_pdf():

    with fitz.open(PDF_FILE) as doc:

        if len(doc) != 22:
            raise RuntimeError(
                "PDF H31001 phai co 22 trang."
            )

        cover = normalize_code(
            doc[0].get_text("text")
        )

        if EXAM_CODE not in cover:
            raise RuntimeError(
                "Trang bia khong phai H31001."
            )

        answer_page = normalize(
            doc[20].get_text("text")
        )

        writing_page = normalize(
            doc[21].get_text("text")
        )

        if (
            "答案" not in answer_page
            or "书" not in writing_page
        ):
            raise RuntimeError(
                "Trang dap an 21-22 khong dung."
            )

        # Kiem tra 70 dap an Nghe/Doc.
        pattern = re.compile(
            r"(?<!\d)(\d{1,2})\s*[.、]"
            r"\s*([A-F√×])"
        )

        pdf_answers = {}

        for match in pattern.finditer(answer_page):

            number = int(match.group(1))
            answer = match.group(2)

            if not 1 <= number <= 70:
                continue

            if number in pdf_answers:
                raise RuntimeError(
                    f"Trung dap an cau {number}."
                )

            pdf_answers[number] = answer

        if set(pdf_answers) != set(range(1, 71)):
            raise RuntimeError(
                "Trang 21 khong du 70 dap an."
            )

        for number in range(1, 71):

            if pdf_answers[number] != EXPECTED[number]:
                raise RuntimeError(
                    f"Sai dap an PDF cau {number}."
                )

        # Kiem tra 10 dap an Viet.
        writing_pattern = re.compile(
            r"^\s*(7[1-9]|80)\s*[.、]"
            r"\s*([^\n]+)",
            re.MULTILINE
        )

        pdf_writing = {}

        for match in writing_pattern.finditer(
            writing_page
        ):

            number = int(match.group(1))

            pdf_writing[number] = (
                match.group(2).strip()
            )

        if set(pdf_writing) != set(range(71, 81)):
            raise RuntimeError(
                "Trang 22 khong du 10 dap an Viet."
            )

        for number in range(71, 81):

            if (
                pdf_writing[number]
                != EXPECTED[number]
            ):
                raise RuntimeError(
                    f"Sai dap an Viet cau {number}."
                )

    print("PDF: 22 trang")
    print("Dap an Nghe/Doc: 70/70")
    print("Dap an Viet: 10/10")


# =====================================================
# 7. KIEM TRA JSON NGUON
# =====================================================

def check_sources():

    check_file(PDF_FILE)
    check_file(MP3_FILE)

    answers_data = load_json(ANSWER_JSON)
    images_data = load_json(IMAGE_JSON)

    template = load_json(TEMPLATE)

    if template.get("ma_de_goc") != "H21335":
        raise RuntimeError(
            "JSON mau khong phai HSK2 De 11."
        )

    if answers_data.get("cap_hsk") != 3:
        raise RuntimeError(
            "JSON dap an khong phai HSK3."
        )

    if answers_data.get("so_de") != 1:
        raise RuntimeError(
            "JSON dap an khong phai De 1."
        )

    if (
        answers_data.get("ma_de_goc")
        != EXAM_CODE
    ):
        raise RuntimeError(
            "JSON dap an khong phai H31001."
        )

    if (
        images_data.get("ma_de_goc")
        != EXAM_CODE
    ):
        raise RuntimeError(
            "Manifest khong phai H31001."
        )

    if images_data.get("cap_hsk") != 3:
        raise RuntimeError(
            "Manifest khong phai HSK3."
        )

    if images_data.get("so_de") != 1:
        raise RuntimeError(
            "Manifest khong phai De 1."
        )

    answers = answers_data.get("dap_an", {})

    if set(answers) != {
        str(n) for n in range(1, 81)
    }:
        raise RuntimeError(
            "JSON khong du 80 dap an."
        )

    for number in range(1, 81):

        actual = str(
            answers[str(number)]
        ).strip()

        if actual != EXPECTED[number]:
            raise RuntimeError(
                f"JSON sai dap an cau {number}."
            )

    # Kiem tra manifest 80 cau.
    questions = images_data.get("cau_hoi", {})
    groups = images_data.get("bang_lua_chon", {})

    if set(questions) != {
        str(n) for n in range(1, 81)
    }:
        raise RuntimeError(
            "Manifest khong du 80 cau."
        )

    if set(groups) != set(GROUPS):
        raise RuntimeError(
            "Manifest khong du 6 bang."
        )

    for number in range(1, 81):

        item = questions[str(number)]

        if item.get("trang_pdf") != page_for(number):
            raise RuntimeError(
                f"Cau {number} sai trang PDF."
            )

        if item.get("nhom_lua_chon") != group_for(number):
            raise RuntimeError(
                f"Cau {number} sai nhom lua chon."
            )

    for name, page_no in GROUP_PAGES.items():

        if groups[name].get("trang_pdf") != page_no:
            raise RuntimeError(
                f"Bang {name} sai trang PDF."
            )

    check_pdf()

    # Kiem tra 70 anh cau hoi.
    question_sources = {}

    for number in range(11, 81):

        path = (
            OUTPUT / "questions"
            / f"cau_{number:02d}.png"
        )

        check_file(path)

        question_sources[number] = path

    # Kiem tra 6 bang lua chon.
    group_sources = {}

    for name in GROUPS:

        path = (
            OUTPUT / "groups"
            / f"{name}.png"
        )

        check_file(path)

        group_sources[name] = path

    if len(template.get("cau_hoi", [])) != 60:
        raise RuntimeError(
            "JSON mau khong co 60 cau."
        )

    return (
        template,
        answers,
        question_sources,
        group_sources
    )


# =====================================================
# 8. DOC THOI LUONG MP3
# =====================================================

def audio_duration(path):

    try:
        from mutagen.mp3 import MP3

        duration = float(
            MP3(str(path)).info.length
        )

        if duration <= 0:
            raise RuntimeError(
                "Thoi luong MP3 khong hop le."
            )

        return round(duration, 2)

    except ImportError:
        pass

    try:

        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True
        )

        duration = float(
            result.stdout.strip()
        )

        if duration <= 0:
            raise ValueError(
                "MP3 khong co thoi luong."
            )

        return round(duration, 2)

    except (
        OSError,
        ValueError,
        subprocess.CalledProcessError
    ):

        raise RuntimeError(
            "Khong doc duoc thoi luong MP3.\n"
            "Hay chay: pip install mutagen"
        )


# =====================================================
# 9. CHUYEN THAM CHIEU HSK2 SANG HSK3
# =====================================================

def replace_references(value):

    if isinstance(value, str):

        return (
            value
            .replace("H21335", EXAM_CODE)
            .replace("hsk2", "hsk3")
            .replace("HSK2", "HSK3")
            .replace("HSK 2", "HSK 3")
            .replace("de_11", "de_01")
            .replace("Đề 11", "Đề 1")
            .replace(
                "Đề HSK 2 số 11",
                "Đề HSK 3 số 1"
            )
        )

    if isinstance(value, list):

        return [
            replace_references(item)
            for item in value
        ]

    if isinstance(value, dict):

        return {
            key: replace_references(item)
            for key, item in value.items()
        }

    return value


# =====================================================
# 10. CHON CAU MAU THEO DANG
# =====================================================

def template_number_for(number):

    # HSK2 cau 11: lua chon hinh chung.
    if number <= 10:
        return 11

    # HSK2 cau 1: dung/sai.
    if number <= 20:
        return 1

    # HSK2 cau 21: chon mot A/B/C.
    if number <= 40:
        return 21

    # HSK2 cau 36: lua chon chung A-F.
    if number <= 60:
        return 36

    # HSK2 cau 21: trac nghiem A/B/C.
    if number <= 70:
        return 21

    # HSK2 chua co phan Viet.
    # Lay khung cau hoi, sau do doi dang.
    return 21


# =====================================================
# 11. TAO 80 CAU HOI
# =====================================================

def build_questions(template, answers):

    source_questions = template["cau_hoi"]

    template_map = {
        q["so_cau"]: q
        for q in source_questions
    }

    if set(template_map) != set(range(1, 61)):
        raise RuntimeError(
            "JSON mau thieu so cau."
        )

    result = []

    for number in range(1, 81):

        source_number = template_number_for(
            number
        )

        question = replace_references(
            deepcopy(
                template_map[source_number]
            )
        )

        question["so_cau"] = number

        question["phan"] = section_for(
            number
        )

        question["dang"] = type_for(
            number
        )

        question["trang_pdf"] = page_for(
            number
        )

        question["dap_an_dung"] = str(
            answers[str(number)]
        ).strip()

        question["da_duyet"] = False

        # Cau 1-10 chi co bang hinh chung.
        if number <= 10:

            question["anh_cau_hoi"] = None

        else:

            question["anh_cau_hoi"] = (
                "/static/media/luyen_thi/hsk3/"
                f"de_01/questions/cau_{number:02d}.png"
            )

        group = group_for(number)

        if group:

            question["anh_nhom_lua_chon"] = (
                "/static/media/luyen_thi/hsk3/"
                f"de_01/groups/{group}.png"
            )

        else:

            question["anh_nhom_lua_chon"] = None

        # Ghi ro loai cau Viet neu JSON mau
        # co cac truong loai tuong ung.
        for field in (
            "loai_cau_hoi",
            "dang_cau_hoi",
            "kieu_cau_hoi",
        ):

            if field in question:
                question[field] = type_for(
                    number
                )

        # Cau 71-80 la cau nhap van ban,
        # khong phai trac nghiem.
        if number >= 71:

            for field in (
                "lua_chon",
                "cac_lua_chon",
                "phuong_an",
            ):

                if field in question:
                    question[field] = []

        result.append(question)

    if len(result) != 80:
        raise RuntimeError(
            "Tao cau hoi khong du 80."
        )

    return result


# =====================================================
# 12. COPY MEDIA KHONG GHI DE FILE KHAC
# =====================================================

def copy_safe(source, destination):

    if destination.exists():

        if filecmp.cmp(
            source,
            destination,
            shallow=False
        ):
            return

        raise RuntimeError(
            "File dich da ton tai "
            "nhung khac noi dung:\n"
            + str(destination)
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    shutil.copy2(
        source,
        destination
    )


# =====================================================
# 13. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - CHUAN HOA HSK3 DE 01")
    print("MA DE H31001")
    print("=" * 60)

    (
        template,
        answers,
        question_sources,
        group_sources
    ) = check_sources()

    duration = audio_duration(
        MP3_FILE
    )

    print("\n===== KIEM TRA NGUON =====")
    print("Ma de: H31001")
    print("Nghe: 40")
    print("Doc: 30")
    print("Viet: 10")
    print("Dap an: 80/80")
    print("Anh cau hoi: 70")
    print("Bang lua chon: 6")
    print(f"MP3: {duration} giay")

    # ================================================
    # 14. TAO JSON TU MAU HSK2
    # ================================================

    result = replace_references(
        deepcopy(template)
    )

    result["cap_hsk"] = 3

    if "so_de" in result:
        result["so_de"] = 1

    result["ma_de_goc"] = EXAM_CODE
    result["ten_hien_thi"] = "Đề 1"
    result["thu_tu"] = 1

    result["so_cau"] = 80
    result["so_cau_nghe"] = 40
    result["so_cau_doc"] = 30
    result["so_cau_viet"] = 10

    # PDF tong 90 phut, bao gom 5 phut
    # dien thong tin ca nhan.
    result["thoi_gian_phut"] = 85

    result["so_trang_pdf_de"] = 22

    result["trang_cau_hoi"] = list(
        range(2, 15)
    )

    result["trang_loi_thoai"] = list(
        range(15, 21)
    )

    result["trang_dap_an"] = [21, 22]

    result["nguon_dap_an"] = "pdf_chung"

    result["file_pdf"] = str(PDF_FILE)
    result["file_mp3"] = str(MP3_FILE)

    result.pop(
        "file_dap_an",
        None
    )

    # ================================================
    # 15. CAP NHAT AUDIO
    # ================================================

    if not isinstance(
        result.get("audio"),
        dict
    ):
        raise RuntimeError(
            "JSON mau thieu cau truc audio."
        )

    result["audio"]["duong_dan"] = (
        "/static/media/luyen_thi/hsk3/"
        "H31001.mp3"
    )

    result["audio"]["thoi_luong_giay"] = (
        duration
    )

    # ================================================
    # 16. TAO 80 CAU HOI
    # ================================================

    result["cau_hoi"] = build_questions(
        template,
        answers
    )

    # Kiem tra 10 dap an Viet.
    for number in range(71, 81):

        question = result["cau_hoi"][
            number - 1
        ]

        if (
            question["dap_an_dung"]
            != WRITING_ANSWERS[number]
        ):
            raise RuntimeError(
                f"Sai cau Viet {number}."
            )

        if question["phan"] != "viet":
            raise RuntimeError(
                f"Cau {number} chua la phan Viet."
            )

    # ================================================
    # 17. KIEM TRA DU LIEU MOI
    # ================================================

    raw = json.dumps(
        result,
        ensure_ascii=False
    )

    if any(
        old in raw
        for old in (
            "H21335",
            "/hsk2/",
            "de_11",
        )
    ):
        raise RuntimeError(
            "JSON moi van con tham chieu "
            "HSK2 De 11."
        )

    if result["ma_de_goc"] != EXAM_CODE:
        raise RuntimeError(
            "Ma de JSON moi khong dung."
        )

    if len(result["cau_hoi"]) != 80:
        raise RuntimeError(
            "JSON moi khong du 80 cau."
        )

    json_content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    )

    if FINAL_JSON.exists():

        existing = FINAL_JSON.read_text(
            encoding="utf-8-sig"
        )

        if existing != json_content:
            raise RuntimeError(
                "JSON De 1 da ton tai "
                "voi noi dung khac.\n"
                "Khong ghi de:\n"
                + str(FINAL_JSON)
            )

    # ================================================
    # 18. CHUAN BI MEDIA
    # ================================================

    copies = []

    for number, source in (
        question_sources.items()
    ):

        destination = (
            MEDIA / "questions"
            / f"cau_{number:02d}.png"
        )

        copies.append((
            source,
            destination
        ))

    for name, source in (
        group_sources.items()
    ):

        destination = (
            MEDIA / "groups"
            / f"{name}.png"
        )

        copies.append((
            source,
            destination
        ))

    copies.append((
        MP3_FILE,
        STATIC / "H31001.mp3"
    ))

    # Kiem tra tat ca file truoc khi copy.
    for source, destination in copies:

        if destination.exists():

            if not filecmp.cmp(
                source,
                destination,
                shallow=False
            ):
                raise RuntimeError(
                    "File dich khac noi dung:\n"
                    + str(destination)
                )

    # ================================================
    # 19. COPY FILE
    # ================================================

    print("\n===== SAO CHEP MEDIA =====")

    for source, destination in copies:

        copy_safe(
            source,
            destination
        )

    # ================================================
    # 20. LUU JSON
    # ================================================

    DATA.mkdir(
        parents=True,
        exist_ok=True
    )

    if not FINAL_JSON.exists():

        FINAL_JSON.write_text(
            json_content,
            encoding="utf-8"
        )

    # ================================================
    # 21. KET QUA
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH CHUAN HOA HSK3 DE 01")
    print("=" * 60)

    print("Ma de: H31001")
    print("Cap: HSK3")
    print("Tong cau: 80")
    print("Nghe: 40")
    print("Doc: 30")
    print("Viet: 10")

    print("Dap an: 80/80")
    print("Anh cau hoi: 70")
    print("Bang lua chon: 6")
    print("Tong anh: 76")

    print(f"Audio: {duration} giay")
    print("Thoi gian lam bai: 85 phut")

    print(f"\nJSON: {FINAL_JSON}")

    print("\nCAN KIEM TRA HO TRO CHAM PHAN VIET.")
    print("CHUA NHAP SQL SERVER.")


if __name__ == "__main__":
    main()
