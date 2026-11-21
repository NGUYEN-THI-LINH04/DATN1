
# -*- coding: utf-8 -*-

"""
MOC HAN - SUA KY NANG HSK3 DE 01 (H31001)

Sua loi:
    So cau nghe khong khop.

Nguyen nhan:
    JSON duoc tao tu mau HSK2, nhung
    truong ky_nang chua duoc doi cho
    tung cau HSK3.

Chi sua:
    cau_hoi[n]["ky_nang"]

Khong sua:
    - Dap an
    - Anh cau hoi
    - Anh lua chon chung
    - MP3
    - Thoi gian thi
    - Du lieu HSK1/HSK2
    - SQL Server
"""

from pathlib import Path
from collections import Counter
from copy import deepcopy
import json


# =====================================================
# 1. DUONG DAN
# =====================================================

DATA = Path(
    r"D:\DATN1\scripts\luyen_thi"
    r"\hsk3\data\de_01"
)

JSON_FILE = DATA / "de_01.json"

BACKUP_FILE = (
    DATA / "de_01_truoc_sua_ky_nang.json"
)

ANSWER_FILE = DATA / "de_01_dap_an.json"


# =====================================================
# 2. HAM HO TRO
# =====================================================

def load_json(path):

    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open(
        "r",
        encoding="utf-8-sig"
    ) as f:
        return json.load(f)


def expected_skill(number):

    if 1 <= number <= 40:
        return "nghe"

    if 41 <= number <= 70:
        return "doc"

    if 71 <= number <= 80:
        return "viet"

    raise RuntimeError(
        f"So cau khong hop le: {number}"
    )


def count_skills(questions):

    return Counter(
        question.get("ky_nang")
        for question in questions
    )


# =====================================================
# 3. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - SUA KY NANG HSK3 DE 01")
    print("MA DE H31001")
    print("=" * 60)

    data = load_json(JSON_FILE)

    answer_data = load_json(ANSWER_FILE)

    # ================================================
    # 4. KIEM TRA MA DE
    # ================================================

    if data.get("cap_hsk") != 3:
        raise RuntimeError(
            "JSON khong phai HSK3."
        )

    if data.get("ma_de_goc") != "H31001":
        raise RuntimeError(
            "JSON khong phai H31001."
        )

    if data.get("so_cau") != 80:
        raise RuntimeError(
            "Tong so cau phai la 80."
        )

    if (
        data.get("so_cau_nghe") != 40
        or data.get("so_cau_doc") != 30
        or data.get("so_cau_viet") != 10
    ):
        raise RuntimeError(
            "Thong tin so cau Nghe/Doc/Viet sai."
        )

    questions = data.get("cau_hoi", [])

    if len(questions) != 80:
        raise RuntimeError(
            "JSON khong du 80 cau."
        )

    numbers = [
        q.get("so_cau")
        for q in questions
    ]

    if numbers != list(range(1, 81)):
        raise RuntimeError(
            "So cau khong lien tuc tu 1-80."
        )

    # ================================================
    # 5. KIEM TRA DAP AN TRUOC KHI SUA
    # ================================================

    answers = answer_data.get(
        "dap_an", {}
    )

    if set(answers) != {
        str(n) for n in range(1, 81)
    }:
        raise RuntimeError(
            "JSON dap an nguon khong du 80 cau."
        )

    for question in questions:

        number = question["so_cau"]

        actual = str(
            question.get("dap_an_dung", "")
        ).strip()

        expected = str(
            answers[str(number)]
        ).strip()

        if actual != expected:
            raise RuntimeError(
                f"Dap an cau {number} khong khop."
            )

        if not (
            question.get("anh_cau_hoi")
            or question.get("anh_nhom_lua_chon")
            or question.get("noi_dung")
        ):
            raise RuntimeError(
                f"Cau {number} thieu noi dung/anh."
            )

    print("\n===== TRUOC KHI SUA =====")

    before = count_skills(questions)

    print(
        "Nghe:",
        before.get("nghe", 0)
    )

    print(
        "Doc:",
        before.get("doc", 0)
    )

    print(
        "Viet:",
        before.get("viet", 0)
    )

    # ================================================
    # 6. CHI SUA TRUONG KY_NANG
    # ================================================

    fixed = deepcopy(data)

    changed = []

    for question in fixed["cau_hoi"]:

        number = question["so_cau"]

        correct = expected_skill(number)

        old = question.get("ky_nang")

        if old != correct:

            question["ky_nang"] = correct

            changed.append(number)

    # ================================================
    # 7. KIEM TRA SAU KHI SUA
    # ================================================

    after = count_skills(
        fixed["cau_hoi"]
    )

    if (
        after.get("nghe", 0) != 40
        or after.get("doc", 0) != 30
        or after.get("viet", 0) != 10
    ):
        raise RuntimeError(
            "So cau sau khi sua khong dung."
        )

    # Bao dam dap an va hinh khong doi.
    for old_q, new_q in zip(
        data["cau_hoi"],
        fixed["cau_hoi"]
    ):

        number = old_q["so_cau"]

        # Xoa ky_nang khoi hai ban sao
        # de kiem tra cac truong khac.
        old_compare = dict(old_q)
        new_compare = dict(new_q)

        old_compare.pop("ky_nang", None)
        new_compare.pop("ky_nang", None)

        if old_compare != new_compare:
            raise RuntimeError(
                f"Cau {number} co truong khac "
                "bi thay doi."
            )

    if not changed:

        print("\nJSON da dung ky_nang.")
        print("Khong can ghi lai file.")

    else:

        # ============================================
        # 8. SAO LUU FILE GOC
        # ============================================

        if not BACKUP_FILE.exists():

            BACKUP_FILE.write_bytes(
                JSON_FILE.read_bytes()
            )

            print(
                "\nDa sao luu:",
                BACKUP_FILE
            )

        # ============================================
        # 9. LUU JSON DA SUA
        # ============================================

        new_content = json.dumps(
            fixed,
            ensure_ascii=False,
            indent=2
        )

        temp_file = DATA / "de_01.json.tmp"

        if temp_file.exists():
            raise RuntimeError(
                "File tam da ton tai: "
                + str(temp_file)
            )

        temp_file.write_text(
            new_content,
            encoding="utf-8"
        )

        temp_file.replace(JSON_FILE)

        print(
            "\nDa sua ky_nang cua",
            len(changed),
            "cau."
        )

    # ================================================
    # 10. KET QUA
    # ================================================

    print("\n===== SAU KHI SUA =====")

    print(
        "Nghe:",
        after["nghe"],
        "/40"
    )

    print(
        "Doc:",
        after["doc"],
        "/30"
    )

    print(
        "Viet:",
        after["viet"],
        "/10"
    )

    print("\nDap an: 80/80 KHONG THAY DOI")
    print("Anh: KHONG THAY DOI")
    print("MP3: KHONG THAY DOI")

    print("\n" + "=" * 60)
    print("HOAN THANH SUA JSON H31001")
    print("=" * 60)

    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
