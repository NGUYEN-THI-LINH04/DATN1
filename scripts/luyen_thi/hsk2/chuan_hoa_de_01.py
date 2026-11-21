# -*- coding: utf-8 -*-

"""
MOC HAN - CHUAN HOA HSK2 DE 1
Ma de: H20901

60 cau: 35 Nghe + 25 Doc.
Su dung cau truc JSON HSK1 da import thanh cong.
Khong thay doi SQL Server.
"""

from pathlib import Path
from copy import deepcopy
import json
import shutil
import subprocess

ROOT = Path(r"D:\DATN1")

HSK2 = ROOT / "scripts/luyen_thi/hsk2"
SOURCE = ROOT / "scripts/luyen_thi/source/De_HSK/HSK2"

DATA = HSK2 / "data/de_01"
OUTPUT = HSK2 / "output/de_01"

STATIC = ROOT / "static/media/luyen_thi/hsk2"
MEDIA = STATIC / "de_01"

TEMPLATE = (
    ROOT
    / "scripts/luyen_thi/hsk1/data/de_10/de_10.json"
)

ANSWER_FILE = DATA / "de_01_dap_an.json"
IMAGE_FILE = DATA / "hinh_60_cau_ung_vien.json"

AUDIO_SOURCE = SOURCE / "Đề HSK 2 số 1 file nghe.mp3"

FINAL_JSON = DATA / "de_01.json"


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


def get_section(number):
    if number <= 10:
        return "nghe", 1, "dung_sai"

    if number <= 20:
        return "nghe", 2, "ghep_hinh_theo_audio"

    if number <= 30:
        return "nghe", 3, "chon_mot"

    if number <= 35:
        return "nghe", 4, "chon_mot"

    if number <= 40:
        return "doc", 1, "ghep_hinh_theo_noi_dung"

    if number <= 45:
        return "doc", 2, "ghep_cap"

    if number <= 50:
        return "doc", 3, "dung_sai"

    return "doc", 4, "ghep_cap"


def group_for(number):
    for group, numbers in GROUPS.items():
        if number in numbers:
            return group

    return None


def audio_duration(path):
    try:
        from mutagen.mp3 import MP3
        return round(float(MP3(str(path)).info.length), 2)

    except ImportError:
        pass

    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return round(float(result.stdout.strip()), 2)


def main():
    print("=" * 60)
    print("MOC HAN - CHUAN HOA HSK2 DE 1")
    print("Ma de: H20901")
    print("=" * 60)

    answers_data = load_json(ANSWER_FILE)
    images_data = load_json(IMAGE_FILE)
    template = load_json(TEMPLATE)

    answers = answers_data["dap_an"]
    images = images_data["cau_hoi"]
    groups = images_data["bang_lua_chon"]

    if len(answers) != 60:
        raise ValueError("Dap an khong du 60 cau.")

    if len(images) != 60:
        raise ValueError("Anh cau hoi khong du 60 cau.")

    if len(groups) != 6:
        raise ValueError("Bang lua chon khong du 6 nhom.")

    if not AUDIO_SOURCE.is_file():
        raise FileNotFoundError(AUDIO_SOURCE)

    # Lay mau theo loai cau hoi tu HSK1.
    profiles = {}

    for question in template["cau_hoi"]:
        question_type = question["loai_cau_hoi"]

        if question_type not in profiles:
            profiles[question_type] = question

    required_types = {
        get_section(n)[2]
        for n in range(1, 61)
    }

    missing_types = required_types - set(profiles)

    if missing_types:
        raise ValueError(
            "HSK1 chua co mau loai cau hoi: "
            + ", ".join(sorted(missing_types))
        )

    # Kiem tra file anh truoc khi sao chep.
    question_sources = {}

    for number in range(1, 61):
        if 11 <= number <= 20:
            continue

        source = (
            OUTPUT
            / "questions"
            / f"cau_{number:02d}.png"
        )

        if not source.is_file():
            raise FileNotFoundError(source)

        question_sources[number] = source

    group_sources = {}

    for group in GROUPS:
        source = OUTPUT / "groups" / f"{group}.png"

        if not source.is_file():
            raise FileNotFoundError(source)

        group_sources[group] = source

    duration = audio_duration(AUDIO_SOURCE)

    print("\n===== KIEM TRA NGUON =====")
    print(f"Dap an: {len(answers)}/60")
    print(f"Anh cau hoi su dung: {len(question_sources)}")
    print(f"Bang lua chon: {len(group_sources)}")
    print(f"MP3: {duration} giay")

    # Tao JSON dua tren cau truc da import thanh cong.
    result = deepcopy(template)

    result["ma_de_goc"] = "H20901"
    result["ten_hien_thi"] = "Đề 1"
    result["thu_tu"] = 1

    result["cap_hsk"] = (
        2
        if isinstance(template["cap_hsk"], int)
        else "HSK2"
    )

    result["so_cau"] = 60
    result["so_cau_nghe"] = 35
    result["so_cau_doc"] = 25
    result["so_cau_viet"] = 0

    # 55 phut tong thoi gian theo PDF,
    # bao gom 5 phut dien thong tin ca nhan.
    # Thoi gian lam bai: 50 phut.
    result["thoi_gian_phut"] = 50

    result["audio"] = deepcopy(template["audio"])

    result["audio"]["duong_dan"] = (
        "/static/media/luyen_thi/hsk2/H20901.mp3"
    )

    result["audio"]["thoi_luong_giay"] = duration

    questions = []

    for number in range(1, 61):
        skill, section, question_type = get_section(number)

        question = deepcopy(profiles[question_type])

        answer = answers.get(str(number))

        if answer is None:
            raise ValueError(
                f"Thieu dap an cau {number}"
            )

        answer = str(answer).strip()

        if number <= 10 or 46 <= number <= 50:
            allowed = {"√", "×"}
        elif 21 <= number <= 35:
            allowed = {"A", "B", "C"}
        else:
            allowed = set("ABCDEF")

        if answer not in allowed:
            raise ValueError(
                f"Dap an cau {number} khong hop le: {answer}"
            )

        question["so_cau"] = number
        question["ky_nang"] = skill
        question["phan"] = section
        question["loai_cau_hoi"] = question_type
        question["noi_dung"] = ""
        question["dap_an_dung"] = answer
        question["da_duyet"] = False

        # Nghe 11-20 chi dung bang hinh chung.
        if 11 <= number <= 20:
            question["anh_cau_hoi"] = None
        else:
            question["anh_cau_hoi"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_01/questions/cau_{number:02d}.png"
            )

        group = group_for(number)

        if group:
            question["anh_nhom_lua_chon"] = (
                "/static/media/luyen_thi/hsk2/"
                f"de_01/groups/{group}.png"
            )
        else:
            question["anh_nhom_lua_chon"] = None

        questions.append(question)

    result["cau_hoi"] = questions

    if len(result["cau_hoi"]) != 60:
        raise RuntimeError("Khong du 60 cau hoi.")

    # Khong duoc giu tham chieu ma de HSK1 cu.
    raw_json = json.dumps(
        result,
        ensure_ascii=False
    )

    if "H11332" in raw_json or "/hsk1/" in raw_json:
        raise RuntimeError(
            "JSON con tham chieu den de HSK1. "
            "Chua sao chep hoac ghi file."
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
        destination = question_dest / source.name
        shutil.copy2(source, destination)

    for group, source in group_sources.items():
        destination = group_dest / source.name
        shutil.copy2(source, destination)

    STATIC.mkdir(
        parents=True,
        exist_ok=True
    )

    shutil.copy2(
        AUDIO_SOURCE,
        STATIC / "H20901.mp3"
    )

    print(
        f"Da sao chep {len(question_sources) + len(group_sources)} file PNG"
    )
    print("Da sao chep H20901.mp3")

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
    print("HSK: 2")
    print("De: 1")
    print("Ma de: H20901")
    print("Tong cau: 60")
    print("Nghe: 35")
    print("Doc: 25")
    print("Thoi gian thi: 50 phut")
    print(f"Audio: {duration} giay")
    print(f"JSON: {FINAL_JSON}")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
