
# -*- coding: utf-8 -*-

"""
MOC HAN - CHUAN HOA HSK2 DE 3 (H21003)

- 60 cau: 35 Nghe, 25 Doc
- Lay cau truc tu HSK2 De 2 da import thanh cong
- Lay dap an that cua H21003
- Su dung anh da kiem tra cua De 3
- Sao chep 50 anh cau hoi, 6 bang lua chon va MP3
- Tao JSON de_03.json

Khong thay doi SQL Server.
Khong sua cac de da hoan thanh.
"""

from pathlib import Path
from copy import deepcopy
import json
import shutil
import subprocess


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

HSK2 = ROOT / "scripts" / "luyen_thi" / "hsk2"

SOURCE = (
    ROOT / "scripts" / "luyen_thi"
    / "source" / "De_HSK" / "HSK2"
)

DATA = HSK2 / "data" / "de_03"

OUTPUT = HSK2 / "output" / "de_03"

# Mau JSON cua HSK2 De 2 da import SQL thanh cong
TEMPLATE = (
    HSK2 / "data" / "de_02" / "de_02.json"
)

ANSWER_FILE = DATA / "de_03_dap_an.json"

IMAGE_FILE = DATA / "hinh_60_cau_ung_vien.json"

PDF_SOURCE = SOURCE / "Đề HSK 2 số 3.pdf"

AUDIO_SOURCE = (
    SOURCE / "Đề HSK 2 số 3 file nghe.mp3"
)

STATIC = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk2"
)

MEDIA = STATIC / "de_03"

FINAL_JSON = DATA / "de_03.json"

MA_DE = "H21003"


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
    for group, numbers in GROUPS.items():
        if number in numbers:
            return group

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
# 4. DOI THAM CHIEU DE 2 SANG DE 3
# =====================================================

def replace_references(value):
    """
    Chi tao ban sao du lieu trong bo nho.
    Khong ghi de JSON De 2.
    """

    if isinstance(value, str):
        return (
            value
            .replace("H20902", "H21003")
            .replace("de_02", "de_03")
            .replace(
                "Đề HSK 2 số 2",
                "Đề HSK 2 số 3"
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

    except (OSError, ValueError, subprocess.CalledProcessError):
        raise RuntimeError(
            "Khong doc duoc thoi luong MP3. "
            "Co the cai mutagen bang: pip install mutagen"
        )


# =====================================================
# 6. KIEM TRA NGUON TRUOC KHI CHUAN HOA
# =====================================================

def check_sources():

    template = load_json(TEMPLATE)
    answer_data = load_json(ANSWER_FILE)
    image_data = load_json(IMAGE_FILE)

    if template.get("ma_de_goc") != "H20902":
        raise RuntimeError(
            "JSON mau khong phai HSK2 De 2."
        )

    if answer_data.get("ma_de_goc") != MA_DE:
        raise RuntimeError(
            "JSON dap an khong phai H21003."
        )

    if image_data.get("ma_de_goc") != MA_DE:
        raise RuntimeError(
            "JSON hinh khong phai H21003."
        )

    if not PDF_SOURCE.is_file():
        raise FileNotFoundError(PDF_SOURCE)

    if not AUDIO_SOURCE.is_file():
        raise FileNotFoundError(AUDIO_SOURCE)

    questions = template.get("cau_hoi", [])
    answers = answer_data.get("dap_an", {})
    images = image_data.get("cau_hoi", {})
    groups = image_data.get("bang_lua_chon", {})

    if len(questions) != 60:
        raise RuntimeError(
            "JSON mau khong du 60 cau."
        )

    question_numbers = [
        q.get("so_cau")
        for q in questions
    ]

    if question_numbers != list(range(1, 61)):
        raise RuntimeError(
            "Thu tu 60 cau trong JSON mau khong dung."
        )

    if set(answers.keys()) != {
        str(n) for n in range(1, 61)
    }:
        raise RuntimeError(
            "Dap an H21003 chua du 60 cau."
        )

    if set(images.keys()) != {
        str(n) for n in range(1, 61)
    }:
        raise RuntimeError(
            "Du lieu anh chua du 60 cau."
        )

    if set(groups.keys()) != set(GROUPS.keys()):
        raise RuntimeError(
            "Chua du 6 bang lua chon."
        )

    for number in range(1, 61):
        answer = str(
            answers[str(number)]
        ).strip()

        validate_answer(number, answer)

    # Nghe 11-20 dung bang hinh chung.
    # Chi su dung 50 anh cau hoi.
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
        template,
        answers,
        question_sources,
        group_sources
    )


# =====================================================
# 7. CHUAN HOA JSON
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - CHUAN HOA HSK2 DE 3")
    print("Ma de: H21003")
    print("=" * 60)

    (
        template,
        answers,
        question_sources,
        group_sources
    ) = check_sources()

    duration = audio_duration(AUDIO_SOURCE)

    print("\n===== KIEM TRA NGUON =====")
    print("Dap an: 60/60")
    print(
        f"Anh cau hoi su dung: {len(question_sources)}"
    )
    print(
        f"Bang lua chon: {len(group_sources)}"
    )
    print(f"MP3: {duration} giay")

    # Tao ban sao cua JSON De 2.
    result = replace_references(
        deepcopy(template)
    )

    # Thong tin De 3.
    result["ma_de_goc"] = MA_DE
    result["ten_hien_thi"] = "Đề 3"
    result["thu_tu"] = 3

    result["so_cau"] = 60
    result["so_cau_nghe"] = 35
    result["so_cau_doc"] = 25
    result["so_cau_viet"] = 0

    result["thoi_gian_phut"] = 50

    # Audio De 3.
    if not isinstance(result.get("audio"), dict):
        raise RuntimeError(
            "Cau truc audio khong hop le."
        )

    result["audio"]["duong_dan"] = (
        "/static/media/luyen_thi/hsk2/H21003.mp3"
    )

    result["audio"]["thoi_luong_giay"] = duration

    # =================================================
    # 8. CAP NHAT 60 CAU HOI
    # =================================================

    for question in result["cau_hoi"]:

        number = question["so_cau"]

        answer = str(
            answers[str(number)]
        ).strip()

        validate_answer(number, answer)

        question["dap_an_dung"] = answer

        # Tat ca cau hoi chua duyet.
        question["da_duyet"] = False

        # Cau 11-20 chi dung bang hinh chung.
        if 11 <= number <= 20:

            question["anh_cau_hoi"] = None

        else:

            question["anh_cau_hoi"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_03/questions/cau_{number:02d}.png"
            )

        group = group_for(number)

        if group:

            question["anh_nhom_lua_chon"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_03/groups/{group}.png"
            )

        else:

            question["anh_nhom_lua_chon"] = None

    # =================================================
    # 9. KIEM TRA JSON MOI
    # =================================================

    if len(result["cau_hoi"]) != 60:
        raise RuntimeError(
            "JSON moi khong du 60 cau."
        )

    raw = json.dumps(
        result,
        ensure_ascii=False
    )

    if "H20902" in raw or "de_02" in raw:
        raise RuntimeError(
            "JSON con tham chieu den De 2."
        )

    if "H20901" in raw or "de_01" in raw:
        raise RuntimeError(
            "JSON con tham chieu den De 1."
        )

    # =================================================
    # 10. SAO CHEP MEDIA
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
            group_dest
            / f"{group}.png"
        )

        shutil.copy2(source, destination)

    STATIC.mkdir(
        parents=True,
        exist_ok=True
    )

    shutil.copy2(
        AUDIO_SOURCE,
        STATIC / "H21003.mp3"
    )

    # =================================================
    # 11. LUU JSON
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
    print("Ma de: H21003")
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
