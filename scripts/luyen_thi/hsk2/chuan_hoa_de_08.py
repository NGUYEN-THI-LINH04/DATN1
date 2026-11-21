
# -*- coding: utf-8 -*-

"""
MOC HAN - CHUAN HOA HSK2 DE 8 (H21330)

- Dung JSON De 7 da nhap SQL thanh cong lam mau.
- PDF de thi 14 trang, bo qua trang 8.
- PDF dap an rieng 1 trang.
- Doi chieu 60 dap an voi PDF chinh thuc.
- Sao chep 50 anh cau hoi va 6 bang lua chon.
- Sao chep MP3 voi ten H21330.mp3.
- Tao de_08.json de kiem tra va import SQL.

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
# 1. CAU HINH DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

HSK2 = ROOT / "scripts" / "luyen_thi" / "hsk2"

DATA = HSK2 / "data" / "de_08"
OUTPUT = HSK2 / "output" / "de_08"

# De 7 da import thanh cong.
TEMPLATE = (
    HSK2 / "data" / "de_07" / "de_07.json"
)

ANSWER_FILE = DATA / "de_08_dap_an.json"

IMAGE_FILE = DATA / "hinh_60_cau_ung_vien.json"

STATIC = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk2"
)

MEDIA = STATIC / "de_08"

FINAL_JSON = DATA / "de_08.json"

EXAM_CODE = "H21330"


# =====================================================
# 2. SO DO TRANG CUA DE 8
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
# 3. CAC HAM HO TRO
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

    text = normalize(text).upper()

    return re.sub(
        r"[^A-Z0-9]",
        "",
        text
    )


def group_for(number):

    for group, numbers in GROUPS.items():

        if number in numbers:
            return group

    return None


def check_file(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    if path.stat().st_size == 0:
        raise RuntimeError(
            f"File rong: {path}"
        )


# =====================================================
# 4. KIEM TRA DAP AN
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
            f"Dap an cau {number} sai: {answer}"
        )


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
# 5. DOC THOI LUONG MP3
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
            "Chay: pip install mutagen"
        )


# =====================================================
# 6. KIEM TRA PDF DE THI VA PDF DAP AN
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


def check_pdfs(
    pdf_file,
    answer_pdf,
    answers
):

    with fitz.open(pdf_file) as doc:

        if len(doc) != 14:
            raise RuntimeError(
                "PDF De 8 phai co 14 trang."
            )

        cover = normalize_code(
            doc[0].get_text("text")
        )

        if EXAM_CODE not in cover:
            raise RuntimeError(
                "Trang bia khong phai H21330."
            )

        expected_headings = [
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

        for page_no, first, last in expected_headings:

            if not has_heading(
                doc[page_no - 1],
                first,
                last
            ):
                raise RuntimeError(
                    f"Trang {page_no} khong co "
                    f"nhom cau {first}-{last}."
                )

        # Trang 8 khong duoc chua cau hoi.
        page_8_text = normalize(
            doc[7].get_text("text")
        )

        if re.search(
            r"第\s*(36|41|46|51|56)\s*[-–—]",
            page_8_text
        ):
            raise RuntimeError(
                "Trang 8 co cau hoi. "
                "Can kiem tra lai PDF."
            )

    with fitz.open(answer_pdf) as doc:

        if len(doc) != 1:
            raise RuntimeError(
                "PDF dap an De 8 phai co 1 trang."
            )

        answer_text = normalize_code(
            doc[0].get_text("text")
        )

        if EXAM_CODE not in answer_text:
            raise RuntimeError(
                "PDF dap an khong phai H21330."
            )

        pdf_answers = extract_pdf_answers(
            doc[0]
        )

    for number in range(1, 61):

        actual = str(
            answers[str(number)]
        ).strip()

        expected = pdf_answers[number]

        if actual != expected:
            raise RuntimeError(
                f"Cau {number} khong khop PDF: "
                f"JSON={actual}, PDF={expected}"
            )

    print("PDF de thi: 14 trang")
    print("Trang 8: bo qua")
    print("Trang cau hoi: 2-7 va 9-14")
    print("PDF dap an: 1 trang rieng")
    print("Doi chieu 60 dap an: KHOP")


# =====================================================
# 7. KIEM TRA DU LIEU NGUON
# =====================================================

def check_sources():

    template = load_json(TEMPLATE)
    answer_data = load_json(ANSWER_FILE)
    image_data = load_json(IMAGE_FILE)

    if template.get("ma_de_goc") != "H21329":
        raise RuntimeError(
            "JSON mau khong phai De 7 H21329."
        )

    if answer_data.get("so_de") != 8:
        raise RuntimeError(
            "JSON dap an khong phai De 8."
        )

    if answer_data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "JSON dap an khong phai H21330."
        )

    if image_data.get("so_de") != 8:
        raise RuntimeError(
            "JSON hinh khong phai De 8."
        )

    if image_data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "Ma de trong JSON hinh khong dung."
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

    images = image_data.get("cau_hoi", {})
    groups = image_data.get("bang_lua_chon", {})

    if set(images) != expected_keys:
        raise RuntimeError(
            "JSON hinh khong du 60 cau."
        )

    if set(groups) != set(GROUPS):
        raise RuntimeError(
            "JSON hinh khong du 6 bang."
        )

    # Kiem tra anh thuoc dung trang.
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

    pdf_value = answer_data.get("file_pdf")
    answer_value = answer_data.get("file_dap_an")
    mp3_value = answer_data.get("file_mp3")

    if not all((
        pdf_value,
        answer_value,
        mp3_value
    )):
        raise RuntimeError(
            "JSON thieu duong dan "
            "PDF de, PDF dap an hoac MP3."
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

    # Chi copy 50 anh cau hoi.
    # Cau 11-20 chi dung bang lua chon chung.
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
# 8. CHUYEN JSON DE 7 SANG DE 8
# =====================================================

def replace_references(value):

    if isinstance(value, str):

        return (
            value
            .replace("H21329", EXAM_CODE)
            .replace("de_07", "de_08")
            .replace(
                "Đề HSK 2 số 7",
                "Đề HSK 2 số 8"
            )
            .replace("Đề 7", "Đề 8")
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
# 9. KIEM TRA GHI DE FILE
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
            "File dich da ton tai nhung "
            "khac file nguon, khong ghi de:\n"
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
# 10. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - CHUAN HOA HSK2 DE 8")
    print("MA DE H21330")
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
    print(f"Ma de: {EXAM_CODE}")
    print("Dap an: 60/60")
    print(f"Anh cau hoi: {len(question_sources)}")
    print(f"Bang lua chon: {len(group_sources)}")
    print(f"MP3: {duration} giay")

    # ================================================
    # 11. TAO JSON DE 8
    # ================================================

    result = replace_references(
        deepcopy(template)
    )

    result["ma_de_goc"] = EXAM_CODE
    result["ten_hien_thi"] = "Đề 8"
    result["thu_tu"] = 8

    result["so_cau"] = 60
    result["so_cau_nghe"] = 35
    result["so_cau_doc"] = 25
    result["so_cau_viet"] = 0

    result["thoi_gian_phut"] = 50

    # Bo cuc PDF de thi.
    if "trang_bo_qua" in result:
        result["trang_bo_qua"] = [1, 8]

    if "trang_cau_hoi" in result:
        result["trang_cau_hoi"] = sorted(
            PAGE_QUESTIONS.keys()
        )

    if "trang_dap_an" in result:
        result["trang_dap_an"] = 1

    if "nguon_dap_an" in result:
        result["nguon_dap_an"] = "pdf_rieng"

    if "so_trang_pdf_de" in result:
        result["so_trang_pdf_de"] = 14

    if "file_pdf" in result:
        result["file_pdf"] = str(pdf_file)

    if "file_dap_an" in result:
        result["file_dap_an"] = str(answer_pdf)

    if "file_mp3" in result:
        result["file_mp3"] = str(mp3_file)

    # ================================================
    # 12. CAP NHAT AUDIO
    # ================================================

    if not isinstance(result.get("audio"), dict):
        raise RuntimeError(
            "Cau truc audio trong JSON mau sai."
        )

    result["audio"]["duong_dan"] = (
        "/static/media/luyen_thi/hsk2/"
        "H21330.mp3"
    )

    result["audio"]["thoi_luong_giay"] = duration

    # ================================================
    # 13. CAP NHAT 60 CAU HOI
    # ================================================

    for question in result["cau_hoi"]:

        number = question["so_cau"]

        answer = str(
            answers[str(number)]
        ).strip()

        question["dap_an_dung"] = answer

        # Tat ca cau hoi chua duyet.
        question["da_duyet"] = False

        # Cau 11-20 chi hien thi so cau
        # va bang lua chon chung.
        if 11 <= number <= 20:

            question["anh_cau_hoi"] = None

        else:

            question["anh_cau_hoi"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_08/questions/cau_{number:02d}.png"
            )

        group = group_for(number)

        if group:

            question["anh_nhom_lua_chon"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_08/groups/{group}.png"
            )

        else:

            question["anh_nhom_lua_chon"] = None

    # ================================================
    # 14. KIEM TRA JSON TRUOC KHI LUU
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

    if "H21329" in raw or "de_07" in raw:
        raise RuntimeError(
            "JSON van con tham chieu De 7."
        )

    json_content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    )

    # Neu da co JSON, chi chap nhan
    # neu noi dung hoan toan giong nhau.
    if FINAL_JSON.exists():

        existing = FINAL_JSON.read_text(
            encoding="utf-8-sig"
        )

        if existing != json_content:
            raise RuntimeError(
                "JSON De 8 da ton tai voi "
                "noi dung khac.\n"
                "Khong tu ghi de: "
                + str(FINAL_JSON)
            )

    # ================================================
    # 15. CHUAN BI 57 FILE MEDIA
    # ================================================

    copies = []

    for number, source in question_sources.items():

        destination = (
            MEDIA / "questions"
            / f"cau_{number:02d}.png"
        )

        copies.append((
            source,
            destination
        ))

    for group, source in group_sources.items():

        destination = (
            MEDIA / "groups"
            / f"{group}.png"
        )

        copies.append((
            source,
            destination
        ))

    copies.append((
        mp3_file,
        STATIC / "H21330.mp3"
    ))

    # Kiem tra tat ca file dich truoc khi copy.
    for source, destination in copies:

        if (
            destination.exists()
            and not filecmp.cmp(
                source,
                destination,
                shallow=False
            )
        ):
            raise RuntimeError(
                "File dich da ton tai "
                "nhung khac noi dung:\n"
                + str(destination)
            )

    # ================================================
    # 16. SAO CHEP MEDIA
    # ================================================

    print("\n===== SAO CHEP MEDIA =====")

    for source, destination in copies:

        copy_safe(
            source,
            destination
        )

    # ================================================
    # 17. LUU JSON
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
    # 18. KET QUA
    # ================================================

    print("\n===== HOAN THANH =====")

    print("Ma de: H21330")
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
