
# -*- coding: utf-8 -*-

"""
MOC HAN - CHUAN HOA HSK2 DE 6 (H21006)

- PDF nguon co 14 trang.
- Trang 2-13: cau hoi.
- Trang 14: dap an.
- Lay cau truc JSON tu HSK2 De 5.
- Lay 60 dap an cua De 6.
- Sao chep 50 anh cau hoi.
- Sao chep 6 bang lua chon chung.
- Sao chep MP3 theo ma de H21006.
- Tao de_06.json de kiem tra va import SQL.

KHONG thay doi SQL Server.
KHONG sua cac de da hoan thanh.
"""

from pathlib import Path
from copy import deepcopy
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

DATA = HSK2 / "data" / "de_06"
OUTPUT = HSK2 / "output" / "de_06"

TEMPLATE = (
    HSK2 / "data" / "de_05" / "de_05.json"
)

ANSWER_FILE = DATA / "de_06_dap_an.json"

IMAGE_FILE = (
    DATA / "hinh_60_cau_ung_vien.json"
)

STATIC = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk2"
)

MEDIA = STATIC / "de_06"

FINAL_JSON = DATA / "de_06.json"

EXPECTED_CODE = "H21006"


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


def load_json(path):
    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


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
# 4. THOI LUONG MP3
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
# 5. KIEM TRA PDF 14 TRANG
# =====================================================

def normalize_code(text):
    text = unicodedata.normalize(
        "NFKC", str(text)
    ).upper()

    return re.sub(r"[^A-Z0-9]", "", text)


def check_pdf(pdf_file, exam_code, answers):

    with fitz.open(pdf_file) as doc:

        if len(doc) != 14:
            raise RuntimeError(
                f"PDF co {len(doc)} trang, "
                "De 6 phai co 14 trang."
            )

        cover = normalize_code(
            doc[0].get_text("text")
        )

        answer_text = doc[13].get_text("text")

        if exam_code not in cover:
            raise RuntimeError(
                "Ma de khong khop trang bia PDF."
            )

        if exam_code not in normalize_code(answer_text):
            raise RuntimeError(
                "Ma de khong khop trang dap an PDF."
            )

        if "答案" not in answer_text:
            raise RuntimeError(
                "Trang 14 khong phai trang dap an."
            )

        # Doi chieu 60 dap an JSON voi PDF goc.
        text = unicodedata.normalize(
            "NFKC", answer_text
        )

        pattern = re.compile(
            r"(?<!\d)(\d{1,2})\s*[.、]\s*([A-F√×])"
        )

        pdf_answers = {}

        for match in pattern.finditer(text):
            number = int(match.group(1))

            if 1 <= number <= 60:
                if number in pdf_answers:
                    raise RuntimeError(
                        f"Trung dap an cau {number} trong PDF."
                    )

                pdf_answers[number] = match.group(2)

        if set(pdf_answers) != set(range(1, 61)):
            raise RuntimeError(
                "Trang 14 khong doc du 60 dap an."
            )

        for number in range(1, 61):
            expected = str(
                answers[str(number)]
            ).strip()

            if pdf_answers[number] != expected:
                raise RuntimeError(
                    f"Cau {number}: JSON = {expected}, "
                    f"PDF = {pdf_answers[number]}"
                )

    print("PDF: 14 trang")
    print("Trang cau hoi: 2-13")
    print("Trang dap an: 14")
    print("Doi chieu dap an PDF: 60/60 KHOP")


# =====================================================
# 6. KIEM TRA DU LIEU NGUON
# =====================================================

def check_sources():

    template = load_json(TEMPLATE)
    answer_data = load_json(ANSWER_FILE)
    image_data = load_json(IMAGE_FILE)

    exam_code = str(
        answer_data.get("ma_de_goc", "")
    ).strip().upper()

    if exam_code != EXPECTED_CODE:
        raise RuntimeError(
            f"Ma de khong dung: {exam_code}"
        )

    if answer_data.get("so_de") != 6:
        raise RuntimeError(
            "JSON dap an khong phai De 6."
        )

    if template.get("ma_de_goc") != "H21005":
        raise RuntimeError(
            "JSON mau khong phai HSK2 De 5."
        )

    if image_data.get("ma_de_goc") != exam_code:
        raise RuntimeError(
            "Ma de trong JSON hinh khong khop."
        )

    answers = answer_data.get("dap_an", {})
    images = image_data.get("cau_hoi", {})
    groups = image_data.get("bang_lua_chon", {})
    questions = template.get("cau_hoi", [])

    expected_keys = {
        str(n) for n in range(1, 61)
    }

    if set(answers) != expected_keys:
        raise RuntimeError(
            "JSON dap an khong du 60 cau."
        )

    if set(images) != expected_keys:
        raise RuntimeError(
            "JSON hinh khong du 60 cau."
        )

    if set(groups) != set(GROUPS):
        raise RuntimeError(
            "Chua du 6 bang lua chon."
        )

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
            "Thu tu 60 cau trong JSON mau sai."
        )

    for number in range(1, 61):
        validate_answer(
            number,
            str(answers[str(number)]).strip()
        )

    pdf_value = answer_data.get("file_pdf")
    mp3_value = answer_data.get("file_mp3")

    if not pdf_value or not mp3_value:
        raise RuntimeError(
            "JSON thieu duong dan PDF hoac MP3."
        )

    pdf_file = Path(pdf_value)
    audio_source = Path(mp3_value)

    if not pdf_file.is_file():
        raise FileNotFoundError(pdf_file)

    if not audio_source.is_file():
        raise FileNotFoundError(audio_source)

    check_pdf(pdf_file, exam_code, answers)

    # 50 anh su dung: 1-10 va 21-60.
    # Cau 11-20 chi hien thi bang hinh chung.
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
        exam_code,
        template,
        answers,
        pdf_file,
        audio_source,
        question_sources,
        group_sources
    )


# =====================================================
# 7. DOI THAM CHIEU DE 5 SANG DE 6
# =====================================================

def replace_references(value, exam_code):

    if isinstance(value, str):
        return (
            value
            .replace("H21005", exam_code)
            .replace("de_05", "de_06")
            .replace("Đề 5", "Đề 6")
            .replace(
                "Đề HSK 2 số 5",
                "Đề HSK 2 số 6"
            )
        )

    if isinstance(value, list):
        return [
            replace_references(item, exam_code)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: replace_references(item, exam_code)
            for key, item in value.items()
        }

    return value


# =====================================================
# 8. CHUAN HOA DE 6
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - CHUAN HOA HSK2 DE 6")
    print("=" * 60)

    (
        exam_code,
        template,
        answers,
        pdf_file,
        audio_source,
        question_sources,
        group_sources
    ) = check_sources()

    duration = audio_duration(audio_source)

    print("\n===== KIEM TRA NGUON =====")
    print(f"Ma de: {exam_code}")
    print("Dap an: 60/60")
    print(f"Anh cau hoi: {len(question_sources)}")
    print(f"Bang lua chon: {len(group_sources)}")
    print(f"MP3: {duration} giay")

    # Tao ban sao JSON De 5.
    result = replace_references(
        deepcopy(template),
        exam_code
    )

    # Thong tin chung.
    result["ma_de_goc"] = exam_code
    result["ten_hien_thi"] = "Đề 6"
    result["thu_tu"] = 6

    result["so_cau"] = 60
    result["so_cau_nghe"] = 35
    result["so_cau_doc"] = 25
    result["so_cau_viet"] = 0
    result["thoi_gian_phut"] = 50

    # Cap nhat thong tin trang neu JSON mau co.
    if "trang_dap_an" in result:
        result["trang_dap_an"] = 14

    if "trang_bo_qua" in result:
        result["trang_bo_qua"] = [1]

    if "trang_cau_hoi" in result:
        result["trang_cau_hoi"] = list(range(2, 14))

    if "file_pdf" in result:
        result["file_pdf"] = str(pdf_file)

    if "file_mp3" in result:
        result["file_mp3"] = str(audio_source)

    # Audio De 6.
    if not isinstance(result.get("audio"), dict):
        raise RuntimeError(
            "Cau truc audio khong hop le."
        )

    result["audio"]["duong_dan"] = (
        "/static/media/luyen_thi/hsk2/"
        f"{exam_code}.mp3"
    )

    result["audio"]["thoi_luong_giay"] = duration

    # =================================================
    # 9. CAP NHAT 60 CAU HOI
    # =================================================

    for question in result["cau_hoi"]:

        number = question["so_cau"]

        answer = str(
            answers[str(number)]
        ).strip()

        question["dap_an_dung"] = answer
        question["da_duyet"] = False

        # Cau 11-20 chi co hinh lua chon chung.
        if 11 <= number <= 20:
            question["anh_cau_hoi"] = None

        else:
            question["anh_cau_hoi"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_06/questions/cau_{number:02d}.png"
            )

        group = group_for(number)

        if group:
            question["anh_nhom_lua_chon"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_06/groups/{group}.png"
            )

        else:
            question["anh_nhom_lua_chon"] = None

    # =================================================
    # 10. KIEM TRA JSON
    # =================================================

    if len(result["cau_hoi"]) != 60:
        raise RuntimeError(
            "JSON moi khong du 60 cau."
        )

    raw = json.dumps(
        result,
        ensure_ascii=False
    )

    if "H21005" in raw or "de_05" in raw:
        raise RuntimeError(
            "JSON van con tham chieu De 5."
        )

    if result["ma_de_goc"] != exam_code:
        raise RuntimeError(
            "Ma de trong JSON khong dung."
        )

    # Khong ghi de JSON va MP3 neu da ton tai.
    audio_destination = STATIC / f"{exam_code}.mp3"

    if audio_destination.exists():
        raise RuntimeError(
            "MP3 dich da ton tai, khong ghi de: "
            + str(audio_destination)
        )

    if FINAL_JSON.exists():
        raise RuntimeError(
            "JSON dich da ton tai, khong ghi de: "
            + str(FINAL_JSON)
        )

    # =================================================
    # 11. SAO CHEP MEDIA
    # =================================================

    print("\n===== SAO CHEP MEDIA =====")

    question_dest = MEDIA / "questions"
    group_dest = MEDIA / "groups"

    question_dest.mkdir(
        parents=True,
        exist_ok=True
    )

    group_dest.mkdir(
        parents=True,
        exist_ok=True
    )

    for number, source in question_sources.items():
        destination = (
            question_dest / f"cau_{number:02d}.png"
        )

        shutil.copy2(source, destination)

    for group, source in group_sources.items():
        destination = (
            group_dest / f"{group}.png"
        )

        shutil.copy2(source, destination)

    STATIC.mkdir(
        parents=True,
        exist_ok=True
    )

    shutil.copy2(
        audio_source,
        audio_destination
    )

    # =================================================
    # 12. LUU JSON
    # =================================================

    DATA.mkdir(
        parents=True,
        exist_ok=True
    )

    FINAL_JSON.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\n===== HOAN THANH =====")
    print(f"Ma de: {exam_code}")
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
    print("PDF nguon: 14 trang")
    print(f"JSON: {FINAL_JSON}")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-

"""
MOC HAN - CHUAN HOA HSK2 DE 6 (H21006)

- PDF nguon co 14 trang.
- Trang 2-13: cau hoi.
- Trang 14: dap an.
- Lay cau truc JSON tu HSK2 De 5.
- Lay 60 dap an cua De 6.
- Sao chep 50 anh cau hoi.
- Sao chep 6 bang lua chon chung.
- Sao chep MP3 theo ma de H21006.
- Tao de_06.json de kiem tra va import SQL.

KHONG thay doi SQL Server.
KHONG sua cac de da hoan thanh.
"""

from pathlib import Path
from copy import deepcopy
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

DATA = HSK2 / "data" / "de_06"
OUTPUT = HSK2 / "output" / "de_06"

TEMPLATE = (
    HSK2 / "data" / "de_05" / "de_05.json"
)

ANSWER_FILE = DATA / "de_06_dap_an.json"

IMAGE_FILE = (
    DATA / "hinh_60_cau_ung_vien.json"
)

STATIC = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk2"
)

MEDIA = STATIC / "de_06"

FINAL_JSON = DATA / "de_06.json"

EXPECTED_CODE = "H21006"


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


def load_json(path):
    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


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
# 4. THOI LUONG MP3
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
# 5. KIEM TRA PDF 14 TRANG
# =====================================================

def normalize_code(text):
    text = unicodedata.normalize(
        "NFKC", str(text)
    ).upper()

    return re.sub(r"[^A-Z0-9]", "", text)


def check_pdf(pdf_file, exam_code, answers):

    with fitz.open(pdf_file) as doc:

        if len(doc) != 14:
            raise RuntimeError(
                f"PDF co {len(doc)} trang, "
                "De 6 phai co 14 trang."
            )

        cover = normalize_code(
            doc[0].get_text("text")
        )

        answer_text = doc[13].get_text("text")

        if exam_code not in cover:
            raise RuntimeError(
                "Ma de khong khop trang bia PDF."
            )

        if exam_code not in normalize_code(answer_text):
            raise RuntimeError(
                "Ma de khong khop trang dap an PDF."
            )

        if "答案" not in answer_text:
            raise RuntimeError(
                "Trang 14 khong phai trang dap an."
            )

        # Doi chieu 60 dap an JSON voi PDF goc.
        text = unicodedata.normalize(
            "NFKC", answer_text
        )

        pattern = re.compile(
            r"(?<!\d)(\d{1,2})\s*[.、]\s*([A-F√×])"
        )

        pdf_answers = {}

        for match in pattern.finditer(text):
            number = int(match.group(1))

            if 1 <= number <= 60:
                if number in pdf_answers:
                    raise RuntimeError(
                        f"Trung dap an cau {number} trong PDF."
                    )

                pdf_answers[number] = match.group(2)

        if set(pdf_answers) != set(range(1, 61)):
            raise RuntimeError(
                "Trang 14 khong doc du 60 dap an."
            )

        for number in range(1, 61):
            expected = str(
                answers[str(number)]
            ).strip()

            if pdf_answers[number] != expected:
                raise RuntimeError(
                    f"Cau {number}: JSON = {expected}, "
                    f"PDF = {pdf_answers[number]}"
                )

    print("PDF: 14 trang")
    print("Trang cau hoi: 2-13")
    print("Trang dap an: 14")
    print("Doi chieu dap an PDF: 60/60 KHOP")


# =====================================================
# 6. KIEM TRA DU LIEU NGUON
# =====================================================

def check_sources():

    template = load_json(TEMPLATE)
    answer_data = load_json(ANSWER_FILE)
    image_data = load_json(IMAGE_FILE)

    exam_code = str(
        answer_data.get("ma_de_goc", "")
    ).strip().upper()

    if exam_code != EXPECTED_CODE:
        raise RuntimeError(
            f"Ma de khong dung: {exam_code}"
        )

    if answer_data.get("so_de") != 6:
        raise RuntimeError(
            "JSON dap an khong phai De 6."
        )

    if template.get("ma_de_goc") != "H21005":
        raise RuntimeError(
            "JSON mau khong phai HSK2 De 5."
        )

    if image_data.get("ma_de_goc") != exam_code:
        raise RuntimeError(
            "Ma de trong JSON hinh khong khop."
        )

    answers = answer_data.get("dap_an", {})
    images = image_data.get("cau_hoi", {})
    groups = image_data.get("bang_lua_chon", {})
    questions = template.get("cau_hoi", [])

    expected_keys = {
        str(n) for n in range(1, 61)
    }

    if set(answers) != expected_keys:
        raise RuntimeError(
            "JSON dap an khong du 60 cau."
        )

    if set(images) != expected_keys:
        raise RuntimeError(
            "JSON hinh khong du 60 cau."
        )

    if set(groups) != set(GROUPS):
        raise RuntimeError(
            "Chua du 6 bang lua chon."
        )

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
            "Thu tu 60 cau trong JSON mau sai."
        )

    for number in range(1, 61):
        validate_answer(
            number,
            str(answers[str(number)]).strip()
        )

    pdf_value = answer_data.get("file_pdf")
    mp3_value = answer_data.get("file_mp3")

    if not pdf_value or not mp3_value:
        raise RuntimeError(
            "JSON thieu duong dan PDF hoac MP3."
        )

    pdf_file = Path(pdf_value)
    audio_source = Path(mp3_value)

    if not pdf_file.is_file():
        raise FileNotFoundError(pdf_file)

    if not audio_source.is_file():
        raise FileNotFoundError(audio_source)

    check_pdf(pdf_file, exam_code, answers)

    # 50 anh su dung: 1-10 va 21-60.
    # Cau 11-20 chi hien thi bang hinh chung.
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
        exam_code,
        template,
        answers,
        pdf_file,
        audio_source,
        question_sources,
        group_sources
    )


# =====================================================
# 7. DOI THAM CHIEU DE 5 SANG DE 6
# =====================================================

def replace_references(value, exam_code):

    if isinstance(value, str):
        return (
            value
            .replace("H21005", exam_code)
            .replace("de_05", "de_06")
            .replace("Đề 5", "Đề 6")
            .replace(
                "Đề HSK 2 số 5",
                "Đề HSK 2 số 6"
            )
        )

    if isinstance(value, list):
        return [
            replace_references(item, exam_code)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: replace_references(item, exam_code)
            for key, item in value.items()
        }

    return value


# =====================================================
# 8. CHUAN HOA DE 6
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - CHUAN HOA HSK2 DE 6")
    print("=" * 60)

    (
        exam_code,
        template,
        answers,
        pdf_file,
        audio_source,
        question_sources,
        group_sources
    ) = check_sources()

    duration = audio_duration(audio_source)

    print("\n===== KIEM TRA NGUON =====")
    print(f"Ma de: {exam_code}")
    print("Dap an: 60/60")
    print(f"Anh cau hoi: {len(question_sources)}")
    print(f"Bang lua chon: {len(group_sources)}")
    print(f"MP3: {duration} giay")

    # Tao ban sao JSON De 5.
    result = replace_references(
        deepcopy(template),
        exam_code
    )

    # Thong tin chung.
    result["ma_de_goc"] = exam_code
    result["ten_hien_thi"] = "Đề 6"
    result["thu_tu"] = 6

    result["so_cau"] = 60
    result["so_cau_nghe"] = 35
    result["so_cau_doc"] = 25
    result["so_cau_viet"] = 0
    result["thoi_gian_phut"] = 50

    # Cap nhat thong tin trang neu JSON mau co.
    if "trang_dap_an" in result:
        result["trang_dap_an"] = 14

    if "trang_bo_qua" in result:
        result["trang_bo_qua"] = [1]

    if "trang_cau_hoi" in result:
        result["trang_cau_hoi"] = list(range(2, 14))

    if "file_pdf" in result:
        result["file_pdf"] = str(pdf_file)

    if "file_mp3" in result:
        result["file_mp3"] = str(audio_source)

    # Audio De 6.
    if not isinstance(result.get("audio"), dict):
        raise RuntimeError(
            "Cau truc audio khong hop le."
        )

    result["audio"]["duong_dan"] = (
        "/static/media/luyen_thi/hsk2/"
        f"{exam_code}.mp3"
    )

    result["audio"]["thoi_luong_giay"] = duration

    # =================================================
    # 9. CAP NHAT 60 CAU HOI
    # =================================================

    for question in result["cau_hoi"]:

        number = question["so_cau"]

        answer = str(
            answers[str(number)]
        ).strip()

        question["dap_an_dung"] = answer
        question["da_duyet"] = False

        # Cau 11-20 chi co hinh lua chon chung.
        if 11 <= number <= 20:
            question["anh_cau_hoi"] = None

        else:
            question["anh_cau_hoi"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_06/questions/cau_{number:02d}.png"
            )

        group = group_for(number)

        if group:
            question["anh_nhom_lua_chon"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_06/groups/{group}.png"
            )

        else:
            question["anh_nhom_lua_chon"] = None

    # =================================================
    # 10. KIEM TRA JSON
    # =================================================

    if len(result["cau_hoi"]) != 60:
        raise RuntimeError(
            "JSON moi khong du 60 cau."
        )

    raw = json.dumps(
        result,
        ensure_ascii=False
    )

    if "H21005" in raw or "de_05" in raw:
        raise RuntimeError(
            "JSON van con tham chieu De 5."
        )

    if result["ma_de_goc"] != exam_code:
        raise RuntimeError(
            "Ma de trong JSON khong dung."
        )

    # Khong ghi de JSON va MP3 neu da ton tai.
    audio_destination = STATIC / f"{exam_code}.mp3"

    if audio_destination.exists():
        raise RuntimeError(
            "MP3 dich da ton tai, khong ghi de: "
            + str(audio_destination)
        )

    if FINAL_JSON.exists():
        raise RuntimeError(
            "JSON dich da ton tai, khong ghi de: "
            + str(FINAL_JSON)
        )

    # =================================================
    # 11. SAO CHEP MEDIA
    # =================================================

    print("\n===== SAO CHEP MEDIA =====")

    question_dest = MEDIA / "questions"
    group_dest = MEDIA / "groups"

    question_dest.mkdir(
        parents=True,
        exist_ok=True
    )

    group_dest.mkdir(
        parents=True,
        exist_ok=True
    )

    for number, source in question_sources.items():
        destination = (
            question_dest / f"cau_{number:02d}.png"
        )

        shutil.copy2(source, destination)

    for group, source in group_sources.items():
        destination = (
            group_dest / f"{group}.png"
        )

        shutil.copy2(source, destination)

    STATIC.mkdir(
        parents=True,
        exist_ok=True
    )

    shutil.copy2(
        audio_source,
        audio_destination
    )

    # =================================================
    # 12. LUU JSON
    # =================================================

    DATA.mkdir(
        parents=True,
        exist_ok=True
    )

    FINAL_JSON.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\n===== HOAN THANH =====")
    print(f"Ma de: {exam_code}")
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
    print("PDF nguon: 14 trang")
    print(f"JSON: {FINAL_JSON}")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
