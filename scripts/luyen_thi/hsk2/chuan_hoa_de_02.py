
# -*- coding: utf-8 -*-

"""
MOC HAN - CHUAN HOA HSK2 DE 2 (H20902)

- 60 cau: 35 Nghe, 25 Doc
- Lay cau truc JSON tu HSK2 De 1
- Su dung dap an that cua H20902
- Su dung anh da kiem tra cua De 2
- Sao chep MP3 va 56 anh can su dung
- Chua thay doi SQL Server
"""

from pathlib import Path
import json
import shutil
import subprocess


ROOT = Path(r"D:\DATN1")

HSK2 = ROOT / "scripts" / "luyen_thi" / "hsk2"

SOURCE = (
    ROOT / "scripts" / "luyen_thi"
    / "source" / "De_HSK" / "HSK2"
)

DATA = HSK2 / "data" / "de_02"
OUTPUT = HSK2 / "output" / "de_02"

# JSON De 1 da nhap SQL thanh cong
TEMPLATE = (
    HSK2 / "data" / "de_01" / "de_01.json"
)

ANSWER_FILE = DATA / "de_02_dap_an.json"

IMAGE_FILE = (
    DATA / "hinh_60_cau_ung_vien.json"
)

AUDIO_SOURCE = (
    SOURCE / "Đề HSK 2 số 2 file nghe.mp3"
)

STATIC = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk2"
)

MEDIA = STATIC / "de_02"

FINAL_JSON = DATA / "de_02.json"


# =====================================================
# 1. BANG LUA CHON CHUNG
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


def replace_old_references(value):
    """
    Doi cac tham chieu De 1 thanh De 2.
    Khong thay doi noi dung cac file cua De 1.
    """
    if isinstance(value, str):
        return (
            value
            .replace("H20901", "H20902")
            .replace("de_01", "de_02")
        )

    if isinstance(value, list):
        return [
            replace_old_references(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: replace_old_references(item)
            for key, item in value.items()
        }

    return value


def audio_duration(path):
    try:
        from mutagen.mp3 import MP3
        return round(
            float(MP3(str(path)).info.length),
            2
        )

    except (ImportError, Exception):
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
            "Hay cai mutagen: pip install mutagen"
        )


# =====================================================
# 2. KIEM TRA DU LIEU
# =====================================================

def check_sources():
    template = load_json(TEMPLATE)
    answer_data = load_json(ANSWER_FILE)
    image_data = load_json(IMAGE_FILE)

    if template.get("ma_de_goc") != "H20901":
        raise RuntimeError(
            "JSON mau khong phai HSK2 De 1."
        )

    if answer_data.get("ma_de_goc") != "H20902":
        raise RuntimeError(
            "JSON dap an khong phai H20902."
        )

    if image_data.get("ma_de_goc") != "H20902":
        raise RuntimeError(
            "JSON hinh khong phai H20902."
        )

    questions = template.get("cau_hoi", [])
    answers = answer_data.get("dap_an", {})
    images = image_data.get("cau_hoi", {})
    groups = image_data.get("bang_lua_chon", {})

    if len(questions) != 60:
        raise RuntimeError(
            "JSON De 1 khong du 60 cau."
        )

    if set(answers) != {
        str(n) for n in range(1, 61)
    }:
        raise RuntimeError(
            "Dap an De 2 chua du 60 cau."
        )

    if set(images) != {
        str(n) for n in range(1, 61)
    }:
        raise RuntimeError(
            "Thong tin anh De 2 chua du 60 cau."
        )

    if set(groups) != set(GROUPS):
        raise RuntimeError(
            "Bang lua chon De 2 khong du 6 nhom."
        )

    template_numbers = [
        question.get("so_cau")
        for question in questions
    ]

    if template_numbers != list(range(1, 61)):
        raise RuntimeError(
            "Thu tu cau hoi trong JSON mau khong dung."
        )

    for number in range(1, 61):
        validate_answer(
            number,
            str(answers[str(number)]).strip()
        )

    if not AUDIO_SOURCE.is_file():
        raise FileNotFoundError(AUDIO_SOURCE)

    # Cau 11-20 su dung bang hinh chung,
    # nen chi can sao chep 50 anh cau hoi.
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
            OUTPUT / "groups" / f"{group}.png"
        )

        if not path.is_file():
            raise FileNotFoundError(path)

        group_sources[group] = path

    return (
        template,
        answers,
        question_sources,
        group_sources
    )


# =====================================================
# 3. CHUAN HOA
# =====================================================

def main():
    print("=" * 60)
    print("MOC HAN - CHUAN HOA HSK2 DE 2")
    print("Ma de: H20902")
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
    print(f"Anh cau hoi su dung: {len(question_sources)}")
    print(f"Bang lua chon: {len(group_sources)}")
    print(f"MP3: {duration} giay")

    # Su dung dung cau truc JSON cua HSK2 De 1.
    result = replace_old_references(template)

    result["ma_de_goc"] = "H20902"
    result["ten_hien_thi"] = "Đề 2"
    result["thu_tu"] = 2
    result["so_cau"] = 60
    result["so_cau_nghe"] = 35
    result["so_cau_doc"] = 25
    result["so_cau_viet"] = 0
    result["thoi_gian_phut"] = 50

    if not isinstance(result.get("audio"), dict):
        raise RuntimeError(
            "Cau truc audio trong JSON mau khong hop le."
        )

    result["audio"]["duong_dan"] = (
        "/static/media/luyen_thi/hsk2/H20902.mp3"
    )

    result["audio"]["thoi_luong_giay"] = duration

    # Cap nhat dap an va anh cua 60 cau.
    for question in result["cau_hoi"]:
        number = question["so_cau"]
        answer = str(answers[str(number)]).strip()

        question["dap_an_dung"] = answer
        question["da_duyet"] = False

        if 11 <= number <= 20:
            question["anh_cau_hoi"] = None
        else:
            question["anh_cau_hoi"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_02/questions/cau_{number:02d}.png"
            )

        group = group_for(number)

        if group:
            question["anh_nhom_lua_chon"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_02/groups/{group}.png"
            )
        else:
            question["anh_nhom_lua_chon"] = None

    # Kiem tra JSON moi khong con tham chieu De 1.
    raw = json.dumps(
        result,
        ensure_ascii=False
    )

    if "H20901" in raw or "de_01" in raw:
        raise RuntimeError(
            "JSON van con tham chieu De 1."
        )

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
        shutil.copy2(
            source,
            question_dest / source.name
        )

    for group, source in group_sources.items():
        shutil.copy2(
            source,
            group_dest / source.name
        )

    STATIC.mkdir(
        parents=True,
        exist_ok=True
    )

    shutil.copy2(
        AUDIO_SOURCE,
        STATIC / "H20902.mp3"
    )

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
    print("Ma de: H20902")
    print("HSK: 2")
    print("Tong cau: 60")
    print("Nghe: 35")
    print("Doc: 25")
    print("Anh cau hoi: 50")
    print("Bang lua chon: 6")
    print("Tong anh: 56")
    print(f"Thoi gian audio: {duration} giay")
    print("Thoi gian thi: 50 phut")
    print(f"JSON: {FINAL_JSON}")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
