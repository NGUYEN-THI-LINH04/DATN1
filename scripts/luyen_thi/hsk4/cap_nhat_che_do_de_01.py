
# -*- coding: utf-8 -*-

import json
from pathlib import Path

path = Path(
    r"D:\DATN1\scripts\luyen_thi"
    r"\hsk4\data\de_01\de_01.json"
)

backup = path.with_name(
    "de_01.before_auto.json"
)

if backup.exists():
    raise RuntimeError(
        f"File sao luu da ton tai: {backup}"
    )

data = json.loads(
    path.read_text(encoding="utf-8-sig")
)

if data.get("ma_de_goc") != "H41001":
    raise RuntimeError("Sai ma de.")

questions = {
    int(q["so_cau"]): q
    for q in data["cau_hoi"]
}

if len(questions) != 100:
    raise RuntimeError("Khong du 100 cau.")

for number in range(96, 101):
    question = questions[number]

    if question["loai_cau_hoi"] != "viet_cau_theo_tranh":
        raise RuntimeError(f"Sai dang cau {number}")

    answer = question["dap_an_dung"]

    if not isinstance(answer, dict):
        raise RuntimeError(f"Sai JSON cau {number}")

    refs = answer.get("dap_an_tham_khao")

    if not isinstance(refs, list) or not refs:
        raise RuntimeError(f"Thieu dap an mau cau {number}")

# Sao luu truoc khi sua.
backup.write_bytes(path.read_bytes())

for number in range(96, 101):
    question = questions[number]

    question["dap_an_dung"]["che_do"] = (
        "cham_tu_dong_theo_mau"
    )

    question["cham_thu_cong"] = False

data["cau_can_cham_thu_cong"] = []

path.write_text(
    json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    ),
    encoding="utf-8"
)

print("DA DONG BO JSON H41001.")
print("Cau 96-100: cham tu dong theo dap an mau.")
print("Khong thay doi dap an tham khao.")
print("Backup:", backup)
