
# -*- coding: utf-8 -*-

"""
MOC HAN - CHUAN HOA HSK2 DE 4

- Lay ma de goc tu JSON dap an.
- Lay cau truc tu HSK2 De 3 da import thanh cong.
- Giu dung 60 dap an cua De 4.
- Sao chep 50 anh cau hoi.
- Sao chep 6 bang lua chon chung.
- Sao chep MP3 theo ma de goc.
- Tao de_04.json de import SQL.

Khong thay doi SQL Server.
Khong sua HSK1 va HSK2 De 1-3.
"""

from pathlib import Path
from copy import deepcopy
import json
import re
import shutil
import subprocess


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

HSK2 = (
    ROOT / "scripts" / "luyen_thi" / "hsk2"
)

DATA = HSK2 / "data" / "de_04"

OUTPUT = HSK2 / "output" / "de_04"

TEMPLATE = (
    HSK2 / "data" / "de_03" / "de_03.json"
)

ANSWER_FILE = DATA / "de_04_dap_an.json"

IMAGE_FILE = (
    DATA / "hinh_60_cau_ung_vien.json"
)

STATIC = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk2"
)

MEDIA = STATIC / "de_04"

FINAL_JSON = DATA / "de_04.json"


# =====================================================
# 2. CAC BANG LUA CHON CHUNG
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

    with path.open(
        "r", encoding="utf-8-sig"
    ) as f:
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
        allowed = {"A", "B", "C"}

    elif 16 <= number <= 20 or 56 <= number <= 60:
        allowed = set("ABCDE")

    else:
        allowed = set("ABCDEF")

    if answer not in allowed:
        raise ValueError(
            f"Dap an cau {number} khong hop le: {answer}"
        )


# =====================================================
# 4. DOC THOI LUONG AUDIO
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
                str(path)
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
            "Hay cai mutagen bang: pip install mutagen"
        )


# =====================================================
# 5. KIEM TRA DU LIEU NGUON
# =====================================================

def check_sources():

    template = load_json(TEMPLATE)

    answer_data = load_json(ANSWER_FILE)

    image_data = load_json(IMAGE_FILE)

    # Lay ma de that tu JSON De 4
    exam_code = str(
        answer_data.get("ma_de_goc", "")
    ).strip().upper()

    if not re.fullmatch(r"H2\d{4}", exam_code):
        raise RuntimeError(
            f"Ma de goc khong hop le: {exam_code}"
        )

    if answer_data.get("so_de") != 4:
        raise RuntimeError(
            "JSON dap an khong phai HSK2 De 4."
        )

    if template.get("ma_de_goc") != "H21003":
        raise RuntimeError(
            "JSON mau khong phai HSK2 De 3."
        )

    if image_data.get("ma_de_goc") != exam_code:
        raise RuntimeError(
            "Ma de trong JSON hinh khong khop."
        )

    if exam_code == "H21003":
        raise RuntimeError(
            "Ma de De 4 trung voi De 3."
        )

    answers = answer_data.get("dap_an", {})

    expected_keys = {
        str(n) for n in range(1, 61)
    }

    if set(answers) != expected_keys:
        raise RuntimeError(
            "Dap an De 4 chua du 60 cau."
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
            "Thu tu 60 cau trong JSON mau khong dung."
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

    for number in range(1, 61):
        answer = str(
            answers[str(number)]
        ).strip()

        validate_answer(number, answer)

    # Su dung file MP3 duoc ghi trong JSON nguon.
    mp3_value = answer_data.get("file_mp3")

    if not mp3_value:
        raise RuntimeError(
            "JSON dap an chua co duong dan MP3."
        )

    audio_source = Path(mp3_value)

    if not audio_source.is_file():
        raise FileNotFoundError(audio_source)

    # Kiem tra PDF nguon co ton tai.
    pdf_value = answer_data.get("file_pdf")

    if not pdf_value:
        raise RuntimeError(
            "JSON dap an chua co duong dan PDF."
        )

    pdf_source = Path(pdf_value)

    if not pdf_source.is_file():
        raise FileNotFoundError(pdf_source)

    # 50 anh cau hoi su dung.
    # Cau 11-20 chi hien thi bang hinh chung.
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
        group_sources
    )


# =====================================================
# 6. CHUYEN DU LIEU DE 3 SANG DE 4
# =====================================================

def replace_references(value, exam_code):

    if isinstance(value, str):

        return (
            value
            .replace("H21003", exam_code)
            .replace("de_03", "de_04")
            .replace("Đề 3", "Đề 4")
            .replace("Đề HSK 2 số 3", "Đề HSK 2 số 4")
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
# 7. CHUAN HOA
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - CHUAN HOA HSK2 DE 4")
    print("=" * 60)

    (
        exam_code,
        template,
        answers,
        audio_source,
        question_sources,
        group_sources
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

    # Tao ban sao JSON De 3.
    # Khong thay doi file goc.
    result = replace_references(
        deepcopy(template),
        exam_code
    )

    # Thong tin De 4.
    result["ma_de_goc"] = exam_code

    result["ten_hien_thi"] = "Đề 4"

    result["thu_tu"] = 4

    result["so_cau"] = 60

    result["so_cau_nghe"] = 35

    result["so_cau_doc"] = 25

    result["so_cau_viet"] = 0

    result["thoi_gian_phut"] = 50

    # =================================================
    # 8. AUDIO
    # =================================================

    if not isinstance(result.get("audio"), dict):
        raise RuntimeError(
            "Cau truc audio trong JSON mau khong hop le."
        )

    audio_url = (
        "/static/media/luyen_thi/hsk2/"
        f"{exam_code}.mp3"
    )

    result["audio"]["duong_dan"] = audio_url

    result["audio"]["thoi_luong_giay"] = duration

    # =================================================
    # 9. CAP NHAT 60 CAU HOI
    # =================================================

    for question in result["cau_hoi"]:

        number = question["so_cau"]

        answer = str(
            answers[str(number)]
        ).strip()

        validate_answer(number, answer)

        question["dap_an_dung"] = answer

        question["da_duyet"] = False

        # Cau 11-20 khong can anh rieng.
        if 11 <= number <= 20:

            question["anh_cau_hoi"] = None

        else:

            question["anh_cau_hoi"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_04/questions/cau_{number:02d}.png"
            )

        group = group_for(number)

        if group:

            question["anh_nhom_lua_chon"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_04/groups/{group}.png"
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

    if "H21003" in raw or "de_03" in raw:
        raise RuntimeError(
            "JSON van con tham chieu De 3."
        )

    if result["ma_de_goc"] != exam_code:
        raise RuntimeError(
            "Ma de goc trong JSON sai."
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

    # Sao chep 50 anh cau hoi.
    for number, source in question_sources.items():

        destination = (
            question_dest
            / f"cau_{number:02d}.png"
        )

        shutil.copy2(source, destination)

    # Sao chep 6 bang lua chon.
    for group, source in group_sources.items():

        destination = (
            group_dest
            / f"{group}.png"
        )

        shutil.copy2(source, destination)

    # Sao chep MP3.
    STATIC.mkdir(
        parents=True,
        exist_ok=True
    )

    audio_destination = (
        STATIC / f"{exam_code}.mp3"
    )

    if audio_destination.exists():
        raise RuntimeError(
            "MP3 dich da ton tai, khong tu ghi de: "
            + str(audio_destination)
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
    print(f"JSON: {FINAL_JSON}")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
