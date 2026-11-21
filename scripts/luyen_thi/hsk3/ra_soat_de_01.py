
# -*- coding: utf-8 -*-

"""
MOC HAN - RA SOAT JSON HSK3 DE 01 (H31001)

- Kiem tra 80 cau va dap an.
- Sua lua chon dung theo PDF HSK3.
- Sua phan thi de giao dien chia nhom.
- Cau 71-75: sap_xep, co cac cum tu.
- Cau 76-80: dien_tu, khong co lua chon.
- Xoa noi dung van ban ke thua tu HSK2
  khi cau hoi da co hinh anh day du.
- Giu nguyen duong dan anh va MP3.
- Sao luu JSON truoc khi thay doi.

KHONG SUA SQL SERVER.
KHONG SUA HSK1 / HSK2.
"""

from pathlib import Path
from copy import deepcopy
import json
import re


ROOT = Path(r"D:\DATN1")

DATA = (
    ROOT / "scripts" / "luyen_thi"
    / "hsk3" / "data" / "de_01"
)

JSON_FILE = DATA / "de_01.json"
ANSWER_FILE = DATA / "de_01_dap_an.json"

BACKUP_FILE = (
    DATA / "de_01_truoc_ra_soat.json"
)


# Cac cum tu goc trong PDF cau 71-75.
WRITING_TOKENS = {
    71: ["弟弟", "笑了", "高兴地"],
    72: ["简单", "上午的考试", "比较"],
    73: [
        "越来越好", "变得",
        "这个城市的环境", "了"
    ],
    74: [
        "送给他", "那位",
        "医生", "一个礼物"
    ],
    75: [
        "其他班的成绩", "有",
        "也", "很大", "提高"
    ],
}

# Thu tu dung de doi chieu dap an Viet.
CORRECT_ORDER = {
    71: ["弟弟", "高兴地", "笑了"],
    72: ["上午的考试", "比较", "简单"],
    73: [
        "这个城市的环境", "变得",
        "越来越好", "了"
    ],
    74: [
        "那位", "医生",
        "送给他", "一个礼物"
    ],
    75: [
        "其他班的成绩", "也",
        "有", "很大", "提高"
    ],
}


def load_json(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    return json.loads(
        path.read_text(encoding="utf-8-sig")
    )


def skill_for(n):

    if n <= 40:
        return "nghe"

    if n <= 70:
        return "doc"

    return "viet"


def part_for(n):

    ranges = [
        (1, 10, "Nghe - Phần 1"),
        (11, 20, "Nghe - Phần 2"),
        (21, 30, "Nghe - Phần 3"),
        (31, 40, "Nghe - Phần 4"),

        (41, 50, "Đọc - Phần 1"),
        (51, 60, "Đọc - Phần 2"),
        (61, 70, "Đọc - Phần 3"),

        (71, 75, "Viết - Phần 1"),
        (76, 80, "Viết - Phần 2"),
    ]

    for first, last, name in ranges:

        if first <= n <= last:
            return name

    raise ValueError(f"So cau sai: {n}")


def type_for(n):

    if n <= 10:
        return "chon_hinh"

    if n <= 20:
        return "dung_sai"

    if n <= 40:
        return "chon_mot"

    if n <= 60:
        return "ghep_lua_chon"

    if n <= 70:
        return "chon_mot"

    if n <= 75:
        return "sap_xep"

    return "dien_tu"


def make_choices(values):

    return [
        {"ma": value, "nhan": value}
        for value in values
    ]


def options_for(n):

    if 1 <= n <= 5:
        return make_choices("ABCDEF")

    if 6 <= n <= 10:
        return make_choices("ABCDE")

    if 11 <= n <= 20:
        return make_choices(["√", "×"])

    if 21 <= n <= 40:
        return make_choices("ABC")

    if 41 <= n <= 45:
        return make_choices("ABCDEF")

    if 46 <= n <= 50:
        return make_choices("ABCDE")

    if 51 <= n <= 60:
        return make_choices("ABCDEF")

    if 61 <= n <= 70:
        return make_choices("ABC")

    if 71 <= n <= 75:
        return make_choices(WRITING_TOKENS[n])

    return []


def normalize_answer(value):

    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "",
        str(value)
    )


def media_exists(url):

    if not url:
        return False

    if not isinstance(url, str):
        return False

    prefix = "/static/media/luyen_thi/hsk3/"

    if not url.startswith(prefix):
        return False

    path = ROOT / url.lstrip("/")

    return path.is_file() and path.stat().st_size > 0


def verify_questions(data, answers):

    questions = data["cau_hoi"]

    if len(questions) != 80:
        raise RuntimeError("Khong du 80 cau.")

    numbers = [
        q.get("so_cau") for q in questions
    ]

    if numbers != list(range(1, 81)):
        raise RuntimeError(
            "Thu tu cau hoi khong dung."
        )

    counts = {"nghe": 0, "doc": 0, "viet": 0}

    for q in questions:

        n = q["so_cau"]

        expected = str(answers[str(n)]).strip()

        if str(q["dap_an_dung"]).strip() != expected:
            raise RuntimeError(
                f"Sai dap an cau {n}."
            )

        if q["ky_nang"] != skill_for(n):
            raise RuntimeError(
                f"Sai ky nang cau {n}."
            )

        if q["loai_cau_hoi"] != type_for(n):
            raise RuntimeError(
                f"Sai loai cau {n}."
            )

        if q["phan"] != part_for(n):
            raise RuntimeError(
                f"Sai phan thi cau {n}."
            )

        image = q.get("anh_cau_hoi")
        group = q.get("anh_nhom_lua_chon")

        if image and not media_exists(image):
            raise RuntimeError(
                f"Anh cau {n} khong ton tai."
            )

        if group and not media_exists(group):
            raise RuntimeError(
                f"Anh nhom cau {n} khong ton tai."
            )

        if not (
            image or group or q.get("noi_dung")
        ):
            raise RuntimeError(
                f"Cau {n} thieu noi dung/anh."
            )

        expected_options = options_for(n)

        if q.get("lua_chon_json") != expected_options:
            raise RuntimeError(
                f"Sai lua chon cau {n}."
            )

        codes = {
            option["ma"] for option in expected_options
        }

        if n <= 70 and expected not in codes:
            raise RuntimeError(
                f"Dap an cau {n} nam ngoai lua chon."
            )

        counts[q["ky_nang"]] += 1

    if counts != {
        "nghe": 40,
        "doc": 30,
        "viet": 10
    }:
        raise RuntimeError(
            f"So cau sai: {counts}"
        )

    for n in range(71, 76):

        correct = "".join(CORRECT_ORDER[n])

        if normalize_answer(correct) != normalize_answer(
            answers[str(n)]
        ):
            raise RuntimeError(
                f"Cac cum tu cau {n} khong ghep "
                "thanh dap an chinh thuc."
            )

    audio = data.get("audio", {})
    audio_url = audio.get("duong_dan")

    if not media_exists(audio_url):
        raise RuntimeError(
            "Khong tim thay MP3 H31001."
        )

    return counts


def main():

    print("=" * 60)
    print("MOC HAN - RA SOAT HSK3 DE 01")
    print("H31001")
    print("=" * 60)

    original = load_json(JSON_FILE)
    source = load_json(ANSWER_FILE)

    if (
        original.get("cap_hsk") != 3
        or original.get("ma_de_goc") != "H31001"
        or original.get("so_cau") != 80
    ):
        raise RuntimeError(
            "Khong phai JSON HSK3 H31001."
        )

    answers = source.get("dap_an", {})

    if set(answers) != {
        str(n) for n in range(1, 81)
    }:
        raise RuntimeError(
            "Nguon dap an khong du 80 cau."
        )

    fixed = deepcopy(original)

    # Chi sua cac truong lien quan hien thi
    # va lua chon cua 80 cau hoi.
    for q in fixed["cau_hoi"]:

        n = q["so_cau"]

        if str(q.get("dap_an_dung", "")).strip() != str(
            answers[str(n)]
        ).strip():
            raise RuntimeError(
                f"Dap an cau {n} da bi sai."
            )

        q["ky_nang"] = skill_for(n)
        q["phan"] = part_for(n)
        q["loai_cau_hoi"] = type_for(n)

        if "dang" in q:
            q["dang"] = type_for(n)

        q["lua_chon_json"] = options_for(n)

        # Moi cau HSK3 deu da co hinh anh
        # the hien noi dung goc.
        # Khong de sot text cua HSK2.
        q["noi_dung"] = None

    counts = verify_questions(
        fixed,
        answers
    )

    new_content = json.dumps(
        fixed,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    old_content = JSON_FILE.read_bytes()

    if new_content != old_content:

        # Sao luu ban JSON truoc khi sua.
        if not BACKUP_FILE.exists():

            BACKUP_FILE.write_bytes(
                old_content
            )

        temp_file = DATA / "de_01.json.tmp"

        if temp_file.exists():
            raise RuntimeError(
                "File tam dang ton tai: "
                + str(temp_file)
            )

        temp_file.write_bytes(new_content)

        temp_file.replace(JSON_FILE)

        print("\nDa cap nhat JSON H31001.")

    else:

        print("\nJSON da duoc ra soat truoc do.")

    # Doc lai de kiem tra sau khi ghi.
    saved = load_json(JSON_FILE)

    verify_questions(saved, answers)

    print("\n===== KET QUA =====")

    print("Ma de: H31001")
    print("Tong cau: 80")
    print(f"Nghe: {counts['nghe']}/40")
    print(f"Doc: {counts['doc']}/30")
    print(f"Viet: {counts['viet']}/10")

    print("Dap an: 80/80")
    print("Hinh va MP3: DAY DU")

    print("Cau 71-75: sap_xep")
    print("Cau 76-80: dien_tu")

    print(f"\nJSON: {JSON_FILE}")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
