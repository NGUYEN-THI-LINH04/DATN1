
# -*- coding: utf-8 -*-

"""
MOC HAN - CHUAN HOA HSK2 DE 7 (H21329)

- PDF de thi: 14 trang.
- Trang 8: khong co cau hoi.
- PDF dap an: 1 file rieng.
- Lay cau truc JSON tu HSK2 De 6.
- Doi chieu 60 dap an voi PDF goc.
- Sao chep 50 anh cau hoi.
- Sao chep 6 bang lua chon chung.
- Sao chep MP3 thanh H21329.mp3.
- Tao JSON de_07.json de import SQL.

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
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

HSK2 = ROOT / "scripts" / "luyen_thi" / "hsk2"

DATA = HSK2 / "data" / "de_07"
OUTPUT = HSK2 / "output" / "de_07"

# JSON De 6 da nhap SQL thanh cong
TEMPLATE = (
    HSK2 / "data" / "de_06" / "de_06.json"
)

ANSWER_FILE = DATA / "de_07_dap_an.json"

IMAGE_FILE = DATA / "hinh_60_cau_ung_vien.json"

STATIC = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk2"
)

MEDIA = STATIC / "de_07"

FINAL_JSON = DATA / "de_07.json"

EXAM_CODE = "H21329"


# =====================================================
# 2. BANG LUA CHON CHUNG
# =====================================================

GROUPS = {
    "nghe_11_15": range(11, 16),
    "nghe_16_20": range(16, 21),
    "doc_36_40": range(36, 41),
    "doc_41_45": range(41, 46),
    "doc_51_55": range(51, 56),
    "doc_56_60": range(56, 61),
}

PAGE_QUESTIONS = {
    2: list(range(1, 6)),
    3: list(range(6, 11)),
    4: list(range(11, 16)),
    5: list(range(16, 21)),
    6: list(range(21, 31)),
    7: list(range(31, 36)),
    9: list(range(36, 41)),
    10: list(range(41, 46)),
    11: [46, 47, 48],
    12: [49, 50],
    13: list(range(51, 56)),
    14: list(range(56, 61)),
}


def load_json(path):
    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def normalize_code(value):
    text = unicodedata.normalize(
        "NFKC", str(value)
    ).upper()

    return re.sub(r"[^A-Z0-9]", "", text)


def group_for(number):
    for name, numbers in GROUPS.items():
        if number in numbers:
            return name

    return None


# =====================================================
# 3. KIEM TRA DAP AN
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
            f"Dap an cau {number} khong hop le: {answer}"
        )


# =====================================================
# 4. DOC THOI LUONG MP3
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
            "Khong doc duoc thoi luong MP3. "
            "Hay cai mutagen: pip install mutagen"
        )


# =====================================================
# 5. DOC DAP AN TU PDF RIENG
# =====================================================

def extract_pdf_answers(page):

    text = unicodedata.normalize(
        "NFKC",
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
                f"Trung dap an cau {number} trong PDF."
            )

        answers[number] = answer

    if set(answers) != set(range(1, 61)):
        raise RuntimeError(
            "PDF dap an khong du 60 cau."
        )

    return answers


# =====================================================
# 6. KIEM TRA HAI FILE PDF
# =====================================================

def check_pdfs(pdf_file, answer_pdf, answers):

    with fitz.open(pdf_file) as doc:

        if len(doc) != 14:
            raise RuntimeError(
                "PDF De 7 phai co 14 trang."
            )

        cover = normalize_code(
            doc[0].get_text("text")
        )

        if EXAM_CODE not in cover:
            raise RuntimeError(
                "Trang bia khong phai H21329."
            )

        # Trang 9: cau 36-40.
        page_9 = unicodedata.normalize(
            "NFKC",
            doc[8].get_text("text")
        )

        if not re.search(
            r"第\s*36\s*[-–]\s*40\s*题",
            page_9
        ):
            raise RuntimeError(
                "Trang 9 khong co cau 36-40."
            )

        # Trang 14: cau 56-60.
        page_14 = unicodedata.normalize(
            "NFKC",
            doc[13].get_text("text")
        )

        if not re.search(
            r"第\s*56\s*[-–]\s*60\s*题",
            page_14
        ):
            raise RuntimeError(
                "Trang 14 khong co cau 56-60."
            )

    with fitz.open(answer_pdf) as doc:

        if len(doc) != 1:
            raise RuntimeError(
                "PDF dap an De 7 phai co 1 trang."
            )

        answer_code = normalize_code(
            doc[0].get_text("text")
        )

        if EXAM_CODE not in answer_code:
            raise RuntimeError(
                "PDF dap an khong phai H21329."
            )

        pdf_answers = extract_pdf_answers(doc[0])

    # Doi chieu JSON voi PDF dap an rieng.
    for number in range(1, 61):

        json_answer = str(
            answers[str(number)]
        ).strip()

        if pdf_answers[number] != json_answer:
            raise RuntimeError(
                f"Cau {number}: "
                f"JSON = {json_answer}, "
                f"PDF = {pdf_answers[number]}"
            )

    print("PDF de thi: 14 trang")
    print("Trang 8: bo qua")
    print("Trang cau hoi: 2-7 va 9-14")
    print("PDF dap an rieng: 1 trang")
    print("Doi chieu 60 dap an: KHOP")


# =====================================================
# 7. KIEM TRA DU LIEU NGUON
# =====================================================

def check_sources():

    template = load_json(TEMPLATE)
    answer_data = load_json(ANSWER_FILE)
    image_data = load_json(IMAGE_FILE)

    if template.get("ma_de_goc") != "H21006":
        raise RuntimeError(
            "JSON mau khong phai HSK2 De 6."
        )

    if answer_data.get("so_de") != 7:
        raise RuntimeError(
            "JSON dap an khong phai De 7."
        )

    if answer_data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "Ma de trong JSON dap an sai."
        )

    if image_data.get("ma_de_goc") != EXAM_CODE:
        raise RuntimeError(
            "Ma de trong JSON hinh sai."
        )

    answers = answer_data.get("dap_an", {})

    expected_keys = {
        str(n) for n in range(1, 61)
    }

    if set(answers) != expected_keys:
        raise RuntimeError(
            "Dap an chua du 60 cau."
        )

    images = image_data.get("cau_hoi", {})
    groups = image_data.get("bang_lua_chon", {})

    if set(images) != expected_keys:
        raise RuntimeError(
            "JSON hinh khong du 60 cau."
        )

    if set(groups) != set(GROUPS):
        raise RuntimeError(
            "JSON hinh khong du 6 bang lua chon."
        )

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
            "Thu tu cau hoi trong JSON mau sai."
        )

    for number in range(1, 61):
        validate_answer(
            number,
            str(answers[str(number)]).strip()
        )

    pdf_value = answer_data.get("file_pdf")
    answer_pdf_value = answer_data.get("file_dap_an")
    mp3_value = answer_data.get("file_mp3")

    if not all((
        pdf_value,
        answer_pdf_value,
        mp3_value
    )):
        raise RuntimeError(
            "JSON thieu duong dan PDF de thi, "
            "PDF dap an hoac MP3."
        )

    pdf_file = Path(pdf_value)
    answer_pdf = Path(answer_pdf_value)
    audio_source = Path(mp3_value)

    for path in (
        pdf_file,
        answer_pdf,
        audio_source
    ):
        if not path.is_file():
            raise FileNotFoundError(path)

    check_pdfs(
        pdf_file,
        answer_pdf,
        answers
    )

    # Kiem tra anh dung trang PDF.
    for page_no, page_numbers in PAGE_QUESTIONS.items():

        for number in page_numbers:

            page_in_manifest = (
                images[str(number)].get("trang_pdf")
            )

            if page_in_manifest != page_no:
                raise RuntimeError(
                    f"Cau {number} sai trang PDF: "
                    f"{page_in_manifest}"
                )

    # Chi su dung 50 anh cau hoi.
    # Cau 11-20 dung bang hinh chung.
    question_sources = {}

    for number in range(1, 61):

        if 11 <= number <= 20:
            continue

        path = (
            OUTPUT / "questions"
            / f"cau_{number:02d}.png"
        )

        if not path.is_file():
            raise FileNotFoundError(path)

        question_sources[number] = path

    group_sources = {}

    for group in GROUPS:

        path = (
            OUTPUT / "groups"
            / f"{group}.png"
        )

        if not path.is_file():
            raise FileNotFoundError(path)

        group_sources[group] = path

    return (
        template,
        answers,
        pdf_file,
        answer_pdf,
        audio_source,
        question_sources,
        group_sources
    )


# =====================================================
# 8. DOI THAM CHIEU DE 6 SANG DE 7
# =====================================================

def replace_references(value):

    if isinstance(value, str):
        return (
            value
            .replace("H21006", EXAM_CODE)
            .replace("de_06", "de_07")
            .replace("Đề 6", "Đề 7")
            .replace(
                "Đề HSK 2 số 6",
                "Đề HSK 2 số 7"
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
# 9. SAO CHEP FILE AN TOAN
# =====================================================

def copy_safe(source, destination):

    # Neu file dich da co va giong file nguon
    # thi giu nguyen, khong ghi de.
    if destination.exists():

        if filecmp.cmp(
            source,
            destination,
            shallow=False
        ):
            return

        raise RuntimeError(
            "File dich da ton tai nhung "
            "khac noi dung, khong ghi de:\n"
            + str(destination)
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    shutil.copy2(source, destination)


# =====================================================
# 10. CHUAN HOA DE 7
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - CHUAN HOA HSK2 DE 7")
    print("MA DE H21329")
    print("=" * 60)

    (
        template,
        answers,
        pdf_file,
        answer_pdf,
        audio_source,
        question_sources,
        group_sources
    ) = check_sources()

    duration = audio_duration(audio_source)

    print("\n===== KIEM TRA NGUON =====")
    print("Ma de: H21329")
    print("Dap an: 60/60")
    print(f"Anh cau hoi: {len(question_sources)}")
    print(f"Bang lua chon: {len(group_sources)}")
    print(f"MP3: {duration} giay")

    # Tao ban sao JSON De 6.
    result = replace_references(
        deepcopy(template)
    )

    # Thong tin chung.
    result["ma_de_goc"] = EXAM_CODE
    result["ten_hien_thi"] = "Đề 7"
    result["thu_tu"] = 7

    result["so_cau"] = 60
    result["so_cau_nghe"] = 35
    result["so_cau_doc"] = 25
    result["so_cau_viet"] = 0
    result["thoi_gian_phut"] = 50

    # Dung bo cuc PDF cua De 7.
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

    if "file_pdf" in result:
        result["file_pdf"] = str(pdf_file)

    if "file_dap_an" in result:
        result["file_dap_an"] = str(answer_pdf)

    if "file_mp3" in result:
        result["file_mp3"] = str(audio_source)

    # Audio H21329.
    if not isinstance(result.get("audio"), dict):
        raise RuntimeError(
            "Cau truc audio khong hop le."
        )

    result["audio"]["duong_dan"] = (
        "/static/media/luyen_thi/hsk2/"
        "H21329.mp3"
    )

    result["audio"]["thoi_luong_giay"] = duration

    # Cap nhat 60 dap an va hinh.
    for question in result["cau_hoi"]:

        number = question["so_cau"]

        answer = str(
            answers[str(number)]
        ).strip()

        question["dap_an_dung"] = answer
        question["da_duyet"] = False

        # Cau 11-20 khong co anh rieng.
        if 11 <= number <= 20:
            question["anh_cau_hoi"] = None

        else:
            question["anh_cau_hoi"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_07/questions/cau_{number:02d}.png"
            )

        group = group_for(number)

        if group:
            question["anh_nhom_lua_chon"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_07/groups/{group}.png"
            )

        else:
            question["anh_nhom_lua_chon"] = None

    # =================================================
    # 11. KIEM TRA JSON
    # =================================================

    if len(result["cau_hoi"]) != 60:
        raise RuntimeError(
            "JSON moi khong du 60 cau."
        )

    raw = json.dumps(
        result,
        ensure_ascii=False
    )

    if "H21006" in raw or "de_06" in raw:
        raise RuntimeError(
            "JSON van con tham chieu De 6."
        )

    if result["ma_de_goc"] != EXAM_CODE:
        raise RuntimeError(
            "Ma de trong JSON moi khong dung."
        )

    json_content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    )

    # Neu JSON da ton tai nhung khac noi dung
    # thi khong ghi de.
    if FINAL_JSON.exists():

        existing = FINAL_JSON.read_text(
            encoding="utf-8-sig"
        )

        if existing != json_content:
            raise RuntimeError(
                "JSON De 7 da ton tai voi noi dung khac. "
                "Khong tu ghi de."
            )

    # Kiem tra cac file dich co san
    # truoc khi sao chep.
    copies = []

    for number, source in question_sources.items():

        destination = (
            MEDIA / "questions"
            / f"cau_{number:02d}.png"
        )

        copies.append((source, destination))

    for group, source in group_sources.items():

        destination = (
            MEDIA / "groups"
            / f"{group}.png"
        )

        copies.append((source, destination))

    copies.append((
        audio_source,
        STATIC / "H21329.mp3"
    ))

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
                "File dich ton tai va khac noi dung:\n"
                + str(destination)
            )

    # =================================================
    # 12. SAO CHEP MEDIA
    # =================================================

    print("\n===== SAO CHEP MEDIA =====")

    for source, destination in copies:
        copy_safe(source, destination)

    # =================================================
    # 13. LUU JSON
    # =================================================

    DATA.mkdir(
        parents=True,
        exist_ok=True
    )

    if not FINAL_JSON.exists():
        FINAL_JSON.write_text(
            json_content,
            encoding="utf-8"
        )

    print("\n===== HOAN THANH =====")
    print("Ma de: H21329")
    print("HSK: 2")
    print("Tong cau: 60")
    print("Nghe: 35")
    print("Doc: 25")
    print("Dap an: 60")
    print("Anh cau hoi: 50")
    print("Bang lua chon: 6")
    print("Tong anh: 56")
    print(f"Thoi gian audio: {duration} giay")
    print("Thoi gian thi: 50 phut")
    print("PDF de thi: 14 trang")
    print("PDF dap an: file rieng")
    print(f"JSON: {FINAL_JSON}")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
