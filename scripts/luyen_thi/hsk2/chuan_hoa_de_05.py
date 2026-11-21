
# -*- coding: utf-8 -*-

"""
MOC HAN - CHUAN HOA HSK2 DE 5

- Doc ma de goc tu JSON dap an De 5.
- Lay cau truc tu HSK2 De 4 da import thanh cong.
- Cap nhat 60 dap an cua De 5.
- Sao chep 50 anh cau hoi.
- Sao chep 6 bang lua chon chung.
- Sao chep MP3 theo ma de that.
- Tao JSON de_05.json de kiem tra va import.

Khong ket noi SQL Server.
Khong sua cac de HSK1 va HSK2 De 1-4.
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

HSK2 = (
    ROOT / "scripts" / "luyen_thi" / "hsk2"
)

DATA = HSK2 / "data" / "de_05"
OUTPUT = HSK2 / "output" / "de_05"

# JSON De 4 da nhap SQL thanh cong
TEMPLATE = (
    HSK2 / "data" / "de_04" / "de_04.json"
)

ANSWER_FILE = DATA / "de_05_dap_an.json"

IMAGE_FILE = (
    DATA / "hinh_60_cau_ung_vien.json"
)

STATIC = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk2"
)

MEDIA = STATIC / "de_05"

FINAL_JSON = DATA / "de_05.json"


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
        raise ValueError(
            f"Dap an cau {number} khong hop le: {answer}"
        )


# =====================================================
# 3. THOI LUONG MP3
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
            check=True,
        )

        return round(
            float(result.stdout.strip()),
            2
        )

    except (
        OSError,
        ValueError,
        subprocess.CalledProcessError,
    ):
        raise RuntimeError(
            "Khong doc duoc thoi luong MP3. "
            "Hay cai mutagen: pip install mutagen"
        )


# =====================================================
# 4. KIEM TRA PDF VA MA DE
# =====================================================

def normalize_code(text):
    text = unicodedata.normalize(
        "NFKC", str(text)
    ).upper()

    return re.sub(r"[^A-Z0-9]", "", text)


def check_pdf(pdf_file, exam_code):
    with fitz.open(pdf_file) as doc:
        if len(doc) != 18:
            raise RuntimeError(
                "PDF khong du 18 trang."
            )

        cover = normalize_code(
            doc[0].get_text("text")
        )

        answer_page = normalize_code(
            doc[17].get_text("text")
        )

        if exam_code not in cover:
            raise RuntimeError(
                "Ma de khong khop trang bia PDF."
            )

        if exam_code not in answer_page:
            raise RuntimeError(
                "Ma de khong khop trang dap an PDF."
            )

        if "答案" not in doc[17].get_text("text"):
            raise RuntimeError(
                "Trang 18 khong phai trang dap an."
            )


# =====================================================
# 5. KIEM TRA DU LIEU NGUON
# =====================================================

def check_sources():
    template = load_json(TEMPLATE)
    answer_data = load_json(ANSWER_FILE)
    image_data = load_json(IMAGE_FILE)

    exam_code = str(
        answer_data.get("ma_de_goc", "")
    ).strip().upper()

    if not re.fullmatch(r"H2\d{4}", exam_code):
        raise RuntimeError(
            f"Ma de khong hop le: {exam_code}"
        )

    if answer_data.get("so_de") != 5:
        raise RuntimeError(
            "JSON dap an khong phai HSK2 De 5."
        )

    if template.get("ma_de_goc") != "H21004":
        raise RuntimeError(
            "JSON mau khong phai HSK2 De 4."
        )

    used_codes = {
        "H20901",
        "H20902",
        "H21003",
        "H21004",
    }

    if exam_code in used_codes:
        raise RuntimeError(
            f"Ma de {exam_code} da duoc su dung."
        )

    if image_data.get("ma_de_goc") != exam_code:
        raise RuntimeError(
            "Ma de trong JSON hinh khong khop."
        )

    answers = answer_data.get("dap_an", {})
    images = image_data.get("cau_hoi", {})
    groups = image_data.get("bang_lua_chon", {})
    questions = template.get("cau_hoi", [])

    expected = {
        str(n) for n in range(1, 61)
    }

    if set(answers) != expected:
        raise RuntimeError(
            "Dap an chua du 60 cau."
        )

    if set(images) != expected:
        raise RuntimeError(
            "JSON hinh chua du 60 cau."
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
    mp3_value = answer_data.get("file_mp3")

    if not pdf_value or not mp3_value:
        raise RuntimeError(
            "Thieu duong dan PDF hoac MP3."
        )

    pdf_file = Path(pdf_value)
    audio_source = Path(mp3_value)

    if not pdf_file.is_file():
        raise FileNotFoundError(pdf_file)

    if not audio_source.is_file():
        raise FileNotFoundError(audio_source)

    check_pdf(pdf_file, exam_code)

    # 50 anh cau hoi su dung:
    # 1-10 va 21-60.
    question_sources = {}

    for number in range(1, 61):
        if 11 <= number <= 20:
            continue

        source = (
            OUTPUT / "questions"
            / f"cau_{number:02d}.png"
        )

        if not source.is_file():
            raise FileNotFoundError(source)

        question_sources[number] = source

    # 6 bang lua chon chung.
    group_sources = {}

    for group in GROUPS:
        source = (
            OUTPUT / "groups"
            / f"{group}.png"
        )

        if not source.is_file():
            raise FileNotFoundError(source)

        group_sources[group] = source

    return (
        exam_code,
        template,
        answers,
        audio_source,
        question_sources,
        group_sources,
    )


# =====================================================
# 6. DOI THAM CHIEU DE 4 THANH DE 5
# =====================================================

def replace_references(value, exam_code):
    if isinstance(value, str):
        return (
            value
            .replace("H21004", exam_code)
            .replace("de_04", "de_05")
            .replace("Đề 4", "Đề 5")
            .replace("Đề HSK 2 số 4", "Đề HSK 2 số 5")
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
# 7. CHUAN HOA DE 5
# =====================================================

def main():
    print("=" * 60)
    print("MOC HAN - CHUAN HOA HSK2 DE 5")
    print("=" * 60)

    (
        exam_code,
        template,
        answers,
        audio_source,
        question_sources,
        group_sources,
    ) = check_sources()

    duration = audio_duration(audio_source)

    print("\n===== KIEM TRA NGUON =====")
    print(f"Ma de: {exam_code}")
    print("Dap an: 60/60")
    print(
        f"Anh cau hoi su dung: {len(question_sources)}"
    )
    print(
        f"Bang lua chon: {len(group_sources)}"
    )
    print(f"MP3: {duration} giay")

    # Lay ban sao JSON De 4.
    # Khong sua file De 4.
    result = replace_references(
        deepcopy(template),
        exam_code
    )

    # Thong tin chung.
    result["ma_de_goc"] = exam_code
    result["ten_hien_thi"] = "Đề 5"
    result["thu_tu"] = 5

    result["so_cau"] = 60
    result["so_cau_nghe"] = 35
    result["so_cau_doc"] = 25
    result["so_cau_viet"] = 0
    result["thoi_gian_phut"] = 50

    # Audio De 5.
    if not isinstance(result.get("audio"), dict):
        raise RuntimeError(
            "Cau truc audio khong hop le."
        )

    result["audio"]["duong_dan"] = (
        "/static/media/luyen_thi/hsk2/"
        f"{exam_code}.mp3"
    )

    result["audio"]["thoi_luong_giay"] = duration

    # Cap nhat 60 cau hoi.
    for question in result["cau_hoi"]:
        number = question["so_cau"]

        answer = str(
            answers[str(number)]
        ).strip()

        question["dap_an_dung"] = answer
        question["da_duyet"] = False

        if 11 <= number <= 20:
            # Cau 11-20 su dung hinh nhom.
            question["anh_cau_hoi"] = None
        else:
            question["anh_cau_hoi"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_05/questions/cau_{number:02d}.png"
            )

        group = group_for(number)

        if group:
            question["anh_nhom_lua_chon"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_05/groups/{group}.png"
            )
        else:
            question["anh_nhom_lua_chon"] = None

    # =================================================
    # 8. KIEM TRA JSON TRUOC KHI GHI FILE
    # =================================================

    if len(result["cau_hoi"]) != 60:
        raise RuntimeError(
            "JSON moi khong du 60 cau."
        )

    raw = json.dumps(
        result,
        ensure_ascii=False
    )

    if "H21004" in raw or "de_04" in raw:
        raise RuntimeError(
            "JSON van con tham chieu De 4."
        )

    if result["ma_de_goc"] != exam_code:
        raise RuntimeError(
            "Ma de trong JSON khong khop."
        )

    # Khong ghi de MP3 da ton tai.
    audio_destination = (
        STATIC / f"{exam_code}.mp3"
    )

    if audio_destination.exists():
        raise RuntimeError(
            "MP3 dich da ton tai, khong ghi de: "
            + str(audio_destination)
        )

    if FINAL_JSON.exists():
        raise RuntimeError(
            "JSON De 5 da ton tai, khong ghi de: "
            + str(FINAL_JSON)
        )

    # =================================================
    # 9. SAO CHEP MEDIA
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
            question_dest
            / f"cau_{number:02d}.png"
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
    # 10. LUU JSON
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
    print(f"JSON: {FINAL_JSON}")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
