
# -*- coding: utf-8 -*-

"""
MOC HAN - CHUAN HOA HSK2 DE 10 (H21332)

- Lay JSON De 9 da nhap SQL thanh cong lam mau.
- Kiem tra PDF de thi 14 trang.
- Bo qua trang PDF so 8.
- Kiem tra PDF dap an rieng 1 trang.
- Doi chieu 60 dap an.
- Kiem tra 60 anh va 6 bang lua chon.
- Sao chep 50 anh cau hoi + 6 bang lua chon.
- Sao chep MP3 thanh H21332.mp3.
- Tao de_10.json de kiem tra va import SQL.

KHONG thay doi SQL Server.
KHONG ghi de cac de da hoan thanh.
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
# 1. CAU HINH DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

HSK2 = (
    ROOT / "scripts" / "luyen_thi" / "hsk2"
)

DATA = HSK2 / "data" / "de_10"
OUTPUT = HSK2 / "output" / "de_10"

# De 9 da nhap SQL thanh cong.
TEMPLATE = (
    HSK2 / "data" / "de_09" / "de_09.json"
)

ANSWER_FILE = DATA / "de_10_dap_an.json"

IMAGE_FILE = (
    DATA / "hinh_60_cau_ung_vien.json"
)

STATIC = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk2"
)

MEDIA = STATIC / "de_10"

FINAL_JSON = DATA / "de_10.json"

EXAM_CODE = "H21332"
EXAM_NUMBER = 10


# =====================================================
# 2. SO DO TRANG PDF CHINH XAC
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
# 3. DAP AN CHINH THUC H21332
# =====================================================

EXPECTED_ROWS = [
    "√ × × √ ×",
    "× √ √ × √",
    "F E B C A",
    "B E C D A",
    "A C A A B",
    "A B B B C",
    "C C B A C",
    "B A F C E",
    "C A D B F",
    "× √ √ √ ×",
    "A D C B F",
    "B A D E C",
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

            number = (
                row_index * 5 + offset + 1
            )

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

    value = normalize(text).upper()

    return re.sub(
        r"[^A-Z0-9]",
        "",
        value
    )


def check_file(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    if path.stat().st_size == 0:
        raise RuntimeError(
            f"File rong: {path}"
        )


def group_for(number):

    for name, numbers in GROUPS.items():

        if number in numbers:
            return name

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
# 6. DOC DAP AN TU PDF RIENG
# =====================================================

def extract_pdf_answers(page):

    text = normalize(
        page.get_text("text")
    )

    if "答案" not in text:
        raise RuntimeError(
            "PDF dap an khong co tieu de 答案."
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
            "PDF dap an khong du 60 cau."
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

    return bool(
        re.search(pattern, text)
    )


def check_pdfs(pdf_file, answer_pdf, answers):

    with fitz.open(pdf_file) as doc:

        if len(doc) != 14:
            raise RuntimeError(
                "PDF H21332 phai co 14 trang."
            )

        cover = normalize_code(
            doc[0].get_text("text")
        )

        if EXAM_CODE not in cover:
            raise RuntimeError(
                "Trang bia khong phai H21332."
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
                    f"Trang PDF {page_no} "
                    f"khong co nhom cau "
                    f"{first}-{last}."
                )

        # Trang 8 chi co footer.
        for first, last in [
            (36, 40),
            (41, 45),
            (46, 50),
            (51, 55),
            (56, 60),
        ]:

            if has_heading(
                doc[7],
                first,
                last
            ):
                raise RuntimeError(
                    "Trang 8 co cau hoi. "
                    "Can kiem tra lai PDF."
                )

    # PDF dap an rieng.
    with fitz.open(answer_pdf) as doc:

        if len(doc) != 1:
            raise RuntimeError(
                "PDF dap an phai co 1 trang."
            )

        answer_text = normalize_code(
            doc[0].get_text("text")
        )

        if EXAM_CODE not in answer_text:
            raise RuntimeError(
                "PDF dap an khong phai H21332."
            )

        pdf_answers = extract_pdf_answers(
            doc[0]
        )

    # Doi chieu JSON + PDF + dap an goc.
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

    print("PDF de thi: 14 trang")
    print("Trang 8: bo qua")
    print("Trang cau hoi: 2-7 va 9-14")
    print("PDF dap an: 1 trang rieng")
    print("Doi chieu dap an: 60/60 KHOP")


# =====================================================
# 8. DOC THOI LUONG MP3
# =====================================================

def audio_duration(path):

    try:
        from mutagen.mp3 import MP3

        duration = float(
            MP3(str(path)).info.length
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
# 9. KIEM TRA DU LIEU NGUON
# =====================================================

def check_sources():

    template = load_json(TEMPLATE)
    answer_data = load_json(ANSWER_FILE)
    image_data = load_json(IMAGE_FILE)

    # JSON mau phai la De 9.
    if template.get("ma_de_goc") != "H21331":
        raise RuntimeError(
            "JSON mau khong phai De 9 H21331."
        )

    if answer_data.get("so_de") != EXAM_NUMBER:
        raise RuntimeError(
            "JSON dap an khong phai De 10."
        )

    if answer_data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "JSON dap an khong phai H21332."
        )

    if image_data.get("so_de") != EXAM_NUMBER:
        raise RuntimeError(
            "JSON hinh khong phai De 10."
        )

    if image_data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "JSON hinh khong phai H21332."
        )

    answers = answer_data.get("dap_an", {})

    expected_keys = {
        str(n) for n in range(1, 61)
    }

    if set(answers) != expected_keys:
        raise RuntimeError(
            "JSON dap an khong du 60 cau."
        )

    for number in range(1, 61):

        validate_answer(
            number,
            str(answers[str(number)]).strip()
        )

    # Kiem tra 60 cau cua JSON mau.
    questions = template.get("cau_hoi", [])

    if len(questions) != 60:
        raise RuntimeError(
            "JSON mau khong du 60 cau."
        )

    numbers = [
        question.get("so_cau")
        for question in questions
    ]

    if numbers != list(range(1, 61)):
        raise RuntimeError(
            "Thu tu cau hoi trong JSON mau sai."
        )

    # Kiem tra manifest anh.
    images = image_data.get("cau_hoi", {})
    groups = image_data.get("bang_lua_chon", {})

    if set(images) != expected_keys:
        raise RuntimeError(
            "Manifest khong du 60 cau."
        )

    if set(groups) != set(GROUPS):
        raise RuntimeError(
            "Manifest khong du 6 bang lua chon."
        )

    # Kiem tra tung cau dung trang PDF.
    for page_no, page_numbers in PAGE_QUESTIONS.items():

        for number in page_numbers:

            actual = (
                images[str(number)].get("trang_pdf")
            )

            if actual != page_no:
                raise RuntimeError(
                    f"Cau {number} sai trang PDF: "
                    f"{actual}, can {page_no}"
                )

    # Kiem tra trang PDF cua cac bang chung.
    for group, page_no in GROUP_PAGES.items():

        actual = groups[group].get("trang_pdf")

        if actual != page_no:
            raise RuntimeError(
                f"Bang {group} sai trang PDF."
            )

    # Duong dan PDF, PDF dap an va MP3.
    pdf_value = answer_data.get("file_pdf")
    answer_value = answer_data.get("file_dap_an")
    mp3_value = answer_data.get("file_mp3")

    if not all((
        pdf_value,
        answer_value,
        mp3_value
    )):
        raise RuntimeError(
            "JSON thieu duong dan PDF de thi, "
            "PDF dap an hoac MP3."
        )

    pdf_file = Path(pdf_value)
    answer_pdf = Path(answer_value)
    mp3_file = Path(mp3_value)

    for path in (
        pdf_file,
        answer_pdf,
        mp3_file
    ):
        check_file(path)

    check_pdfs(
        pdf_file,
        answer_pdf,
        answers
    )

    # Chi copy 50 anh:
    # Cau 1-10 va cau 21-60.
    question_sources = {}

    for number in range(1, 61):

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
        answer_pdf,
        mp3_file,
        question_sources,
        group_sources
    )


# =====================================================
# 10. DOI THAM CHIEU DE 9 SANG DE 10
# =====================================================

def replace_references(value):

    if isinstance(value, str):

        return (
            value
            .replace("H21331", EXAM_CODE)
            .replace("de_09", "de_10")
            .replace(
                "Đề HSK 2 số 9",
                "Đề HSK 2 số 10"
            )
            .replace("Đề 9", "Đề 10")
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
# 11. SAO CHEP FILE AN TOAN
# =====================================================

def copy_safe(source, destination):

    # Neu file dich da co va giong file nguon,
    # khong can sao chep lai.
    if destination.exists():

        if filecmp.cmp(
            source,
            destination,
            shallow=False
        ):
            return

        raise RuntimeError(
            "File dich da ton tai "
            "nhung khac noi dung.\n"
            "Khong ghi de:\n"
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
# 12. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - CHUAN HOA HSK2 DE 10")
    print("MA DE H21332")
    print("=" * 60)

    (
        template,
        answers,
        pdf_file,
        answer_pdf,
        mp3_file,
        question_sources,
        group_sources
    ) = check_sources()

    duration = audio_duration(mp3_file)

    print("\n===== KIEM TRA NGUON =====")
    print("Ma de: H21332")
    print("Dap an: 60/60")
    print(f"Anh cau hoi: {len(question_sources)}")
    print(f"Bang lua chon: {len(group_sources)}")
    print(f"MP3: {duration} giay")

    # ================================================
    # 13. TAO JSON DE 10 TU JSON DE 9
    # ================================================

    result = replace_references(
        deepcopy(template)
    )

    result["ma_de_goc"] = EXAM_CODE
    result["ten_hien_thi"] = "Đề 10"
    result["thu_tu"] = 10

    result["so_cau"] = 60
    result["so_cau_nghe"] = 35
    result["so_cau_doc"] = 25
    result["so_cau_viet"] = 0

    result["thoi_gian_phut"] = 50

    # Bo cuc PDF De 10.
    result["trang_bo_qua"] = [1, 8]

    result["trang_cau_hoi"] = sorted(
        PAGE_QUESTIONS.keys()
    )

    result["trang_dap_an"] = 1
    result["nguon_dap_an"] = "pdf_rieng"
    result["so_trang_pdf_de"] = 14

    result["file_pdf"] = str(pdf_file)
    result["file_dap_an"] = str(answer_pdf)
    result["file_mp3"] = str(mp3_file)

    # ================================================
    # 14. CAP NHAT AUDIO
    # ================================================

    if not isinstance(result.get("audio"), dict):
        raise RuntimeError(
            "Cau truc audio cua JSON mau sai."
        )

    result["audio"]["duong_dan"] = (
        "/static/media/luyen_thi/hsk2/"
        "H21332.mp3"
    )

    result["audio"]["thoi_luong_giay"] = duration

    # ================================================
    # 15. CAP NHAT 60 CAU HOI
    # ================================================

    for question in result["cau_hoi"]:

        number = question["so_cau"]

        answer = str(
            answers[str(number)]
        ).strip()

        question["dap_an_dung"] = answer

        # Cau hoi chua duyet.
        question["da_duyet"] = False

        # Cau 11-20 khong co anh rieng.
        if 11 <= number <= 20:

            question["anh_cau_hoi"] = None

        else:

            question["anh_cau_hoi"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_10/questions/cau_{number:02d}.png"
            )

        group = group_for(number)

        if group:

            question["anh_nhom_lua_chon"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_10/groups/{group}.png"
            )

        else:

            question["anh_nhom_lua_chon"] = None

    # ================================================
    # 16. KIEM TRA JSON MOI
    # ================================================

    if len(result["cau_hoi"]) != 60:
        raise RuntimeError(
            "JSON moi khong du 60 cau."
        )

    if result["ma_de_goc"] != EXAM_CODE:
        raise RuntimeError(
            "Ma de trong JSON moi sai."
        )

    raw = json.dumps(
        result,
        ensure_ascii=False
    )

    if "H21331" in raw or "de_09" in raw:
        raise RuntimeError(
            "JSON van con tham chieu De 9."
        )

    json_content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    )

    # Neu JSON De 10 da ton tai,
    # chi chap nhan khi noi dung giong nhau.
    if FINAL_JSON.exists():

        existing = FINAL_JSON.read_text(
            encoding="utf-8-sig"
        )

        if existing != json_content:
            raise RuntimeError(
                "JSON De 10 da ton tai voi "
                "noi dung khac.\n"
                "Khong tu ghi de:\n"
                + str(FINAL_JSON)
            )

    # ================================================
    # 17. CHUAN BI DANH SACH MEDIA
    # ================================================

    copies = []

    # 50 anh cau hoi.
    for number, source in question_sources.items():

        destination = (
            MEDIA / "questions"
            / f"cau_{number:02d}.png"
        )

        copies.append((source, destination))

    # 6 bang lua chon.
    for group, source in group_sources.items():

        destination = (
            MEDIA / "groups"
            / f"{group}.png"
        )

        copies.append((source, destination))

    # 1 file MP3.
    copies.append((
        mp3_file,
        STATIC / "H21332.mp3"
    ))

    # Kiem tra truoc khi sao chep.
    # Khong ghi de file da co voi noi dung khac.
    for source, destination in copies:

        if destination.exists():

            if not filecmp.cmp(
                source,
                destination,
                shallow=False
            ):
                raise RuntimeError(
                    "File dich da co nhung khac "
                    "noi dung:\n"
                    + str(destination)
                )

    # ================================================
    # 18. SAO CHEP MEDIA
    # ================================================

    print("\n===== SAO CHEP MEDIA =====")

    for source, destination in copies:

        copy_safe(
            source,
            destination
        )

    # ================================================
    # 19. LUU JSON
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
    # 20. KET QUA
    # ================================================

    print("\n===== HOAN THANH =====")

    print("Ma de: H21332")
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

    print("PDF de thi: 14 trang")
    print("Trang 8: bo qua")
    print("PDF dap an: 1 trang rieng")

    print(f"JSON: {FINAL_JSON}")

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
