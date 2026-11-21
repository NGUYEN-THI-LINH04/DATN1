
# -*- coding: utf-8 -*-

"""
MOC HAN - CHUAN HOA HSK2 DE 11 (H21335)

- Su dung JSON De 10 lam mau.
- PDF De 11 co 19 trang.
- Trang 8: bo qua.
- Trang 15-18: loi thoai Nghe.
- Trang 19: bang dap an.
- Doi chieu du 60 dap an.
- Kiem tra 60 anh va 6 bang lua chon.
- Sao chep 50 anh cau hoi + 6 bang lua chon.
- Sao chep MP3 thanh H21335.mp3.
- Tao de_11.json de import SQL.

Khong thay doi SQL Server.
Khong sua cac de da hoan thanh.
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
# 1. CAU HINH
# =====================================================

ROOT = Path(r"D:\DATN1")

HSK2 = ROOT / "scripts" / "luyen_thi" / "hsk2"

SOURCE = (
    ROOT / "scripts" / "luyen_thi"
    / "source" / "De_HSK" / "HSK2"
)

DATA = HSK2 / "data" / "de_11"

OUTPUT = HSK2 / "output" / "de_11"

TEMPLATE = (
    HSK2 / "data" / "de_10" / "de_10.json"
)

ANSWER_FILE = DATA / "de_11_dap_an.json"

IMAGE_FILE = DATA / "hinh_60_cau_ung_vien.json"

STATIC = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk2"
)

MEDIA = STATIC / "de_11"

FINAL_JSON = DATA / "de_11.json"

EXAM_CODE = "H21335"
EXAM_NUMBER = 11


# =====================================================
# 2. SO DO TRANG PDF
# =====================================================

PAGE_QUESTIONS = {
    2: list(range(1, 6)),
    3: list(range(6, 11)),
    4: list(range(11, 16)),
    5: list(range(16, 21)),
    6: list(range(21, 31)),
    7: list(range(31, 36)),

    # Trang 8 khong co cau hoi.

    9: list(range(36, 41)),
    10: list(range(41, 46)),
    11: [46, 47, 48],
    12: [49, 50],
    13: list(range(51, 56)),
    14: list(range(56, 61)),
}

GROUP_PAGES = {
    "nghe_11_15": 4,
    "nghe_16_20": 5,
    "doc_36_40": 9,
    "doc_41_45": 10,
    "doc_51_55": 13,
    "doc_56_60": 14,
}

GROUPS = {
    "nghe_11_15": range(11, 16),
    "nghe_16_20": range(16, 21),
    "doc_36_40": range(36, 41),
    "doc_41_45": range(41, 46),
    "doc_51_55": range(51, 56),
    "doc_56_60": range(56, 61),
}


# =====================================================
# 3. DAP AN CHINH THUC H21335
# =====================================================

EXPECTED_ROWS = [
    "√ × × √ ×",
    "√ √ √ × ×",
    "B E F A C",
    "A C D B E",
    "A A C B A",
    "C B A C B",
    "B B C C A",
    "F A E B C",
    "C D A F B",
    "× √ × √ ×",
    "F C B A D",
    "E D A B C",
]


def build_expected_answers():

    result = {}

    for row_index, row in enumerate(EXPECTED_ROWS):

        values = row.split()

        if len(values) != 5:
            raise RuntimeError(
                "Bang dap an goc sai dinh dang."
            )

        for offset, answer in enumerate(values):

            number = row_index * 5 + offset + 1
            result[number] = answer

    if set(result) != set(range(1, 61)):
        raise RuntimeError(
            "Bang dap an goc khong du 60 cau."
        )

    return result


EXPECTED_ANSWERS = build_expected_answers()


# =====================================================
# 4. CAC HAM HO TRO
# =====================================================

def load_json(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8-sig") as f:
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


def check_file(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    if path.stat().st_size == 0:
        raise RuntimeError(
            f"File rong: {path}"
        )


def group_for(number):

    for group, numbers in GROUPS.items():

        if number in numbers:
            return group

    return None


# =====================================================
# 5. KIEM TRA KIEU DAP AN
# =====================================================

def validate_answer(number, answer):

    if number <= 10 or 46 <= number <= 50:
        allowed = {"√", "×"}

    elif 21 <= number <= 35:
        allowed = set("ABC")

    elif 16 <= number <= 20 or 56 <= number <= 60:
        allowed = set("ABCDE")

    else:
        allowed = set("ABCDEF")

    if answer not in allowed:
        raise RuntimeError(
            f"Dap an cau {number} khong hop le: "
            f"{answer}"
        )


# =====================================================
# 6. DOC DAP AN TU TRANG 19
# =====================================================

def extract_pdf_answers(page):

    text = normalize(
        page.get_text("text")
    )

    if "答案" not in text:
        raise RuntimeError(
            "Trang 19 khong co bang 答案."
        )

    pattern = re.compile(
        r"(?<!\d)(\d{1,2})\s*[.、]\s*([A-F√×])"
    )

    answers = {}

    for match in pattern.finditer(text):

        number = int(match.group(1))
        answer = match.group(2)

        if not 1 <= number <= 60:
            continue

        if number in answers:
            raise RuntimeError(
                f"Trung dap an cau {number}."
            )

        validate_answer(number, answer)

        answers[number] = answer

    if set(answers) != set(range(1, 61)):
        raise RuntimeError(
            "Trang 19 khong du 60 dap an."
        )

    return answers


# =====================================================
# 7. KIEM TRA BO CUC PDF
# =====================================================

def has_heading(page, first, last):

    text = normalize(
        page.get_text("text")
    )

    pattern = (
        rf"第\s*{first}\s*[-–—]\s*"
        rf"{last}\s*题"
    )

    return bool(re.search(pattern, text))


def check_pdf(pdf_file, answers):

    with fitz.open(pdf_file) as doc:

        if len(doc) != 19:
            raise RuntimeError(
                f"PDF co {len(doc)} trang. "
                "De 11 H21335 phai co 19 trang."
            )

        cover = normalize_code(
            doc[0].get_text("text")
        )

        answer_code = normalize_code(
            doc[18].get_text("text")
        )

        if EXAM_CODE not in cover:
            raise RuntimeError(
                "Trang bia khong phai H21335."
            )

        if EXAM_CODE not in answer_code:
            raise RuntimeError(
                "Trang 19 khong phai dap an H21335."
            )

        checks = [
            (2, 1, 10),
            (4, 11, 15),
            (5, 16, 20),
            (6, 21, 30),
            (7, 31, 35),
            (9, 36, 40),
            (10, 41, 45),
            (11, 46, 50),
            (13, 51, 55),
            (14, 56, 60),
        ]

        for page_no, first, last in checks:

            if not has_heading(
                doc[page_no - 1],
                first,
                last
            ):
                raise RuntimeError(
                    f"Trang {page_no} khong co "
                    f"nhom cau {first}-{last}."
                )

        # Trang 8 khong chua cau hoi phan Doc.
        for first, last in [
            (36, 40),
            (41, 45),
            (46, 50),
            (51, 55),
            (56, 60),
        ]:

            if has_heading(doc[7], first, last):
                raise RuntimeError(
                    "Trang 8 co cau hoi."
                )

        # Trang 15-18 la loi thoai Nghe.
        transcript = normalize(
            doc[14].get_text("text")
        )

        if "听力材料" not in transcript:
            raise RuntimeError(
                "Trang 15 khong phai loi thoai Nghe."
            )

        # Trang 19 la dap an.
        pdf_answers = extract_pdf_answers(
            doc[18]
        )

    # Doi chieu JSON - PDF - bang dap an goc.
    for number in range(1, 61):

        json_answer = str(
            answers[str(number)]
        ).strip()

        pdf_answer = pdf_answers[number]

        expected = EXPECTED_ANSWERS[number]

        if not (
            json_answer == pdf_answer == expected
        ):
            raise RuntimeError(
                f"Cau {number} khong khop: "
                f"JSON={json_answer}, "
                f"PDF={pdf_answer}, "
                f"goc={expected}"
            )

    print("PDF de thi: 19 trang")
    print("Trang 8: bo qua")
    print("Trang cau hoi: 2-7 va 9-14")
    print("Trang loi thoai Nghe: 15-18")
    print("Trang dap an: 19")
    print("Doi chieu dap an: 60/60 KHOP")


# =====================================================
# 8. TIM FILE MP3 DE 11
# =====================================================

def normalize_filename(text):

    value = unicodedata.normalize(
        "NFD",
        str(text)
    ).lower()

    value = "".join(
        char for char in value
        if unicodedata.category(char) != "Mn"
    )

    return value.replace("đ", "d")


def find_mp3(answer_data):

    # Uu tien duong dan trong JSON.
    value = answer_data.get("file_mp3")

    if value:
        path = Path(value)

        if path.is_file():
            return path

    names = [
        "Đề HSK 2 số 11.mp3",
        "Đề HSK 2 số 11 file nghe.mp3",
        "Đề HSK 2 số 11 (1).mp3",
    ]

    for name in names:

        path = SOURCE / name

        if path.is_file():
            return path

    candidates = []

    for path in SOURCE.glob("*.mp3"):

        name = normalize_filename(path.stem)

        if re.search(
            r"\bso\s*0?11(?!\d)",
            name
        ):
            candidates.append(path)

    if len(candidates) == 1:
        return candidates[0]

    if len(candidates) > 1:
        raise RuntimeError(
            "Co nhieu file MP3 De 11. "
            "Khong tu chon nham:\n"
            + "\n".join(
                str(path) for path in candidates
            )
        )

    raise RuntimeError(
        "Chua tim thay MP3 De 11 H21335.\n"
        "Hay them file nghe dung cua De 11 vao:\n"
        + str(SOURCE)
    )


# =====================================================
# 9. DOC THOI LUONG MP3
# =====================================================

def audio_duration(path):

    try:
        from mutagen.mp3 import MP3

        return round(
            float(MP3(str(path)).info.length),
            2
        )

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

        return round(
            float(result.stdout.strip()),
            2
        )

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
# 10. KIEM TRA DU LIEU NGUON
# =====================================================

def check_sources():

    template = load_json(TEMPLATE)

    answer_data = load_json(ANSWER_FILE)

    image_data = load_json(IMAGE_FILE)

    # JSON mau phai la De 10.
    if template.get("ma_de_goc") != "H21332":
        raise RuntimeError(
            "JSON mau khong phai H21332."
        )

    # JSON dap an phai la De 11.
    if answer_data.get("so_de") != EXAM_NUMBER:
        raise RuntimeError(
            "JSON dap an khong phai De 11."
        )

    if answer_data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "JSON dap an khong phai H21335."
        )

    # Manifest hinh phai la De 11.
    if image_data.get("so_de") != EXAM_NUMBER:
        raise RuntimeError(
            "Manifest khong phai De 11."
        )

    if image_data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "Manifest khong phai H21335."
        )

    answers = answer_data.get("dap_an", {})

    expected = {
        str(n) for n in range(1, 61)
    }

    if set(answers) != expected:
        raise RuntimeError(
            "JSON dap an khong du 60 cau."
        )

    for number in range(1, 61):

        validate_answer(
            number,
            str(answers[str(number)]).strip()
        )

    # Kiem tra cau truc JSON mau.
    questions = template.get("cau_hoi", [])

    if len(questions) != 60:
        raise RuntimeError(
            "JSON mau khong du 60 cau."
        )

    numbers = [
        q.get("so_cau")
        for q in questions
    ]

    if numbers != list(range(1, 61)):
        raise RuntimeError(
            "Thu tu 60 cau trong JSON mau sai."
        )

    # Kiem tra manifest.
    images = image_data.get("cau_hoi", {})
    groups = image_data.get("bang_lua_chon", {})

    if set(images) != expected:
        raise RuntimeError(
            "Manifest khong du 60 cau."
        )

    if set(groups) != set(GROUPS):
        raise RuntimeError(
            "Manifest khong du 6 bang."
        )

    for page_no, page_numbers in PAGE_QUESTIONS.items():

        for number in page_numbers:

            actual_page = (
                images[str(number)].get("trang_pdf")
            )

            if actual_page != page_no:
                raise RuntimeError(
                    f"Cau {number} sai trang PDF: "
                    f"{actual_page}, can {page_no}"
                )

    for group, page_no in GROUP_PAGES.items():

        actual_page = (
            groups[group].get("trang_pdf")
        )

        if actual_page != page_no:
            raise RuntimeError(
                f"Bang {group} sai trang PDF."
            )

    # Kiem tra PDF va dap an.
    pdf_value = answer_data.get("file_pdf")

    if not pdf_value:
        raise RuntimeError(
            "JSON dap an thieu duong dan PDF."
        )

    pdf_file = Path(pdf_value)

    check_file(pdf_file)

    check_pdf(
        pdf_file,
        answers
    )

    # Tim file MP3 dung De 11.
    mp3_file = find_mp3(answer_data)

    check_file(mp3_file)

    # 50 anh cau hoi.
    question_sources = {}

    for number in range(1, 61):

        # Cau 11-20 chi dung bang hinh chung.
        if 11 <= number <= 20:
            continue

        path = (
            OUTPUT / "questions"
            / f"cau_{number:02d}.png"
        )

        check_file(path)

        question_sources[number] = path

    # 6 bang lua chon chung.
    group_sources = {}

    for group in GROUPS:

        path = (
            OUTPUT / "groups"
            / f"{group}.png"
        )

        check_file(path)

        group_sources[group] = path

    return (
        template,
        answers,
        pdf_file,
        mp3_file,
        question_sources,
        group_sources
    )


# =====================================================
# 11. CHUYEN JSON DE 10 SANG DE 11
# =====================================================

def replace_references(value):

    if isinstance(value, str):

        return (
            value
            .replace("H21332", EXAM_CODE)
            .replace("de_10", "de_11")
            .replace(
                "Đề HSK 2 số 10",
                "Đề HSK 2 số 11"
            )
            .replace("Đề 10", "Đề 11")
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
# 12. SAO CHEP FILE AN TOAN
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
            "File dich da co nhung "
            "khac noi dung. Khong ghi de:\n"
            + str(destination)
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    shutil.copy2(source, destination)


# =====================================================
# 13. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - CHUAN HOA HSK2 DE 11")
    print("MA DE H21335")
    print("=" * 60)

    (
        template,
        answers,
        pdf_file,
        mp3_file,
        question_sources,
        group_sources
    ) = check_sources()

    duration = audio_duration(mp3_file)

    print("\n===== KIEM TRA NGUON =====")
    print("Ma de: H21335")
    print("Dap an: 60/60")
    print(f"Anh cau hoi: {len(question_sources)}")
    print(f"Bang lua chon: {len(group_sources)}")
    print(f"MP3: {duration} giay")

    # ================================================
    # 14. TAO JSON DE 11
    # ================================================

    result = replace_references(
        deepcopy(template)
    )

    result["ma_de_goc"] = EXAM_CODE

    result["ten_hien_thi"] = "Đề 11"
    result["thu_tu"] = 11

    if "so_de" in result:
        result["so_de"] = 11

    result["so_cau"] = 60
    result["so_cau_nghe"] = 35
    result["so_cau_doc"] = 25
    result["so_cau_viet"] = 0

    result["thoi_gian_phut"] = 50

    # PDF De 11 co 19 trang.
    result["so_trang_pdf_de"] = 19

    result["trang_cau_hoi"] = sorted(
        PAGE_QUESTIONS.keys()
    )

    result["trang_bo_qua"] = [
        1, 8, 15, 16, 17, 18
    ]

    result["trang_loi_thoai"] = [
        15, 16, 17, 18
    ]

    result["trang_dap_an"] = 19

    result["nguon_dap_an"] = "pdf_chung"

    result["file_pdf"] = str(pdf_file)
    result["file_mp3"] = str(mp3_file)

    # De 11 khong co file dap an rieng.
    result.pop("file_dap_an", None)

    # ================================================
    # 15. CAP NHAT AUDIO
    # ================================================

    if not isinstance(result.get("audio"), dict):
        raise RuntimeError(
            "Cau truc audio JSON mau khong dung."
        )

    result["audio"]["duong_dan"] = (
        "/static/media/luyen_thi/hsk2/"
        "H21335.mp3"
    )

    result["audio"]["thoi_luong_giay"] = duration

    # ================================================
    # 16. CAP NHAT 60 CAU HOI
    # ================================================

    for question in result["cau_hoi"]:

        number = question["so_cau"]

        question["dap_an_dung"] = str(
            answers[str(number)]
        ).strip()

        question["da_duyet"] = False

        # Cau 11-20 chi co bang hinh chung.
        if 11 <= number <= 20:

            question["anh_cau_hoi"] = None

        else:

            question["anh_cau_hoi"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_11/questions/cau_{number:02d}.png"
            )

        group = group_for(number)

        if group:

            question["anh_nhom_lua_chon"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_11/groups/{group}.png"
            )

        else:

            question["anh_nhom_lua_chon"] = None

    # ================================================
    # 17. KIEM TRA JSON MOI
    # ================================================

    if len(result["cau_hoi"]) != 60:
        raise RuntimeError(
            "JSON moi khong du 60 cau."
        )

    if result["ma_de_goc"] != EXAM_CODE:
        raise RuntimeError(
            "Ma de JSON moi sai."
        )

    raw = json.dumps(
        result,
        ensure_ascii=False
    )

    if "H21332" in raw or "de_10" in raw:
        raise RuntimeError(
            "JSON van con tham chieu De 10."
        )

    json_content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    )

    # Bao ve JSON neu da ton tai.
    if FINAL_JSON.exists():

        existing = FINAL_JSON.read_text(
            encoding="utf-8-sig"
        )

        if existing != json_content:
            raise RuntimeError(
                "JSON De 11 da ton tai voi "
                "noi dung khac.\n"
                "Khong tu ghi de:\n"
                + str(FINAL_JSON)
            )

    # ================================================
    # 18. CHUAN BI MEDIA
    # ================================================

    copies = []

    # 50 anh cau hoi.
    for number, source in question_sources.items():

        destination = (
            MEDIA / "questions"
            / f"cau_{number:02d}.png"
        )

        copies.append((source, destination))

    # 6 bang lua chon chung.
    for group, source in group_sources.items():

        destination = (
            MEDIA / "groups"
            / f"{group}.png"
        )

        copies.append((source, destination))

    # MP3 H21335.
    copies.append((
        mp3_file,
        STATIC / "H21335.mp3"
    ))

    # Kiem tra file dich truoc khi copy.
    for source, destination in copies:

        if destination.exists():

            if not filecmp.cmp(
                source,
                destination,
                shallow=False
            ):
                raise RuntimeError(
                    "File dich da ton tai nhung "
                    "khac noi dung:\n"
                    + str(destination)
                )

    # ================================================
    # 19. SAO CHEP MEDIA
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

    print("\n===== HOAN THANH =====")
    print("Ma de: H21335")
    print("HSK: 2")

    print("Tong cau: 60")
    print("Nghe: 35")
    print("Doc: 25")
    print("Viet: 0")

    print("Dap an: 60/60")
    print("Anh cau hoi: 50")
    print("Bang lua chon: 6")
    print("Tong anh: 56")

    print(f"Thoi gian audio: {duration} giay")
    print("Thoi gian thi: 50 phut")

    print("PDF de thi: 19 trang")
    print("Trang 8: bo qua")
    print("Trang loi thoai: 15-18")
    print("Trang dap an: 19")

    print(f"JSON: {FINAL_JSON}")
    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
