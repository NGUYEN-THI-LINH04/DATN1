
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK4 CHAM TU DONG THEO DAP AN

- Mo HSK4 Ca de va Viet.
- Cham cau 96-100 theo dap an tham khao.
- Chap nhan nhieu dap an mau neu co.
- Cau sai / bo trong: 0 diem.
- Khong can Admin cham thu cong.
- Giu logic HSK1-HSK3.
- Khong sua SQL, JS hoac JSON.
"""

from pathlib import Path
import ast
import json
import os
import re
import shutil


ROOT = Path(
    os.environ.get(
        "MOC_HAN_ROOT",
        r"D:\DATN1"
    )
)

FILE = (
    ROOT / "routes"
    / "student"
    / "luyen_thi_lam_bai.py"
)


# =====================================================
# 1. NHANH CHAM VIET MO CU
# =====================================================

OPEN_OLD = '''    if kind == "viet_cau_theo_tranh":
        # Tuyet doi khong tu cho 0 diem.
        raise RuntimeError(
            "HSK4 Viet theo tranh chua co "
            "co che cham thu cong. "
            "Khong duoc tu chot ket qua."
        )
'''


# =====================================================
# 2. NHANH CHAM VIET MO MOI
# =====================================================

OPEN_NEW = '''    if kind == "viet_cau_theo_tranh":
        # Cham theo dap an tham khao trong JSON.
        # Bo khoang trang va dau cau nhu cac
        # dang cau Viet dang co cua he thong.

        if not isinstance(given, str):
            return False

        actual = normalize_answer(
            given,
            "viet_ngan"
        )

        if not actual:
            return False

        data = correct_answer

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (TypeError, ValueError):
                return False

        if not isinstance(data, dict):
            return False

        references = data.get(
            "dap_an_tham_khao"
        )

        if isinstance(references, str):
            references = [references]

        if not isinstance(references, list):
            return False

        return any(
            isinstance(candidate, str)
            and candidate.strip()
            and actual == normalize_answer(
                candidate,
                "viet_ngan"
            )
            for candidate in references
        )
'''


# =====================================================
# 3. KHOA HSK4 O BAN VA DAU
# =====================================================

GUARD = '''    # HSK4 Viet tranh chua co luong cham thu cong.
    # Khong chot diem Ca de/Viet khi chua ho tro.
    if level == 4 and skill in ("tat_ca", "viet"):
        abort(
            409,
            description=(
                "HSK4 phan Viet theo tranh "
                "dang hoan thien cham diem; "
                "tam thoi chi mo Nghe va Doc."
            ),
        )
'''


# =====================================================
# 4. LOGIC CHAM TU DONG
# =====================================================

AUTO_SCORING = '''    matched = False

    if graded:
        matched = match_hsk4_answer(
            given,
            correct_answer,
            question["LoaiCauHoi"],
        )

    points = (
        maximum
        if matched
        else Decimal("0")
    )

'''


# =====================================================
# 5. CHINH CODE
# =====================================================

def transform(source):

    if source.count(
        "def match_hsk4_answer("
    ) != 1:
        raise RuntimeError(
            "Khong tim thay ham cham HSK4 "
            "tu ban va truoc."
        )

    if source.count(OPEN_OLD) != 1:
        raise RuntimeError(
            "Nhanh cham Viet mo khong khop. "
            "Dung de tranh sua nham."
        )

    # -----------------------------------------------
    # 5.1. CHAM VIET MO THEO DAP AN MAU
    # -----------------------------------------------

    source = source.replace(
        OPEN_OLD,
        OPEN_NEW,
        1
    )

    # -----------------------------------------------
    # 5.2. MO LAI HSK4 CA DE / VIET
    # -----------------------------------------------

    if GUARD in source:
        source = source.replace(
            GUARD,
            "",
            1
        )

    # -----------------------------------------------
    # 5.3. KIEM TRA PHAN LUU / CHAM DIEM
    # -----------------------------------------------

    p0 = source.index(
        "def persist_answer("
    )

    p1 = source.index(
        "def finalize(",
        p0
    )

    block = source[p0:p1]

    # Truong hop da ap dung
    # ban va cho Admin cham.
    if "pending_open" in block:

        start = block.index(
            "    # Cau Viet theo tranh co noi dung:"
        )

        end = block.index(
            "    # Cập nhật nếu câu trả lời đã tồn tại.",
            start
        )

        block = (
            block[:start]
            + AUTO_SCORING
            + block[end:]
        )

        # Phuc hoi luu dap an luc cham.
        pattern = (
            r'None if pending_open\s+'
            r'else "Đáp án mở, chấm theo tranh" '
            r'if graded and question\["LoaiCauHoi"\] '
            r'== "viet_cau_theo_tranh"\s+'
            r'else str\(correct_answer\) if graded\s+'
            r'else None'
        )

        block, count = re.subn(
            pattern,
            "str(correct_answer) if graded else None",
            block
        )

        if count != 2:
            raise RuntimeError(
                "Khong phuc hoi duoc "
                "hai vi tri luu dap an."
            )

        # Phuc hoi co dung/sai.
        flag = (
            "None if pending_open "
            "else int(matched) if graded "
            "else None"
        )

        if block.count(flag) != 2:
            raise RuntimeError(
                "Khong phuc hoi duoc "
                "hai vi tri LaDapAnDung."
            )

        block = block.replace(
            flag,
            "int(matched) if graded else None"
        )

    elif AUTO_SCORING.strip() not in block:

        raise RuntimeError(
            "Khong tim thay logic cham diem "
            "cua ban va HSK4 truoc."
        )

    source = (
        source[:p0]
        + block
        + source[p1:]
    )

    if "pending_open" in source:
        raise RuntimeError(
            "Van con logic cho cham cu."
        )

    compile(
        source,
        str(FILE),
        "exec"
    )

    return source


# =====================================================
# 6. KIEM TRA LOGIC CHAM DIEM
# =====================================================

def smoke_test(source):

    module = ast.parse(source)

    names = {
        "normalize_answer",
        "match_hsk4_answer"
    }

    funcs = [
        node
        for node in module.body

        if isinstance(
            node,
            ast.FunctionDef
        )

        and node.name in names
    ]

    if len(funcs) != 2:
        raise RuntimeError(
            "Thieu ham kiem tra cham diem."
        )

    scope = {
        "json": json,
        "re": re
    }

    exec(
        compile(
            ast.Module(
                body=funcs,
                type_ignores=[]
            ),
            "<test_hsk4>",
            "exec"
        ),
        scope
    )

    match = scope[
        "match_hsk4_answer"
    ]

    # Hai dap an mau cho cau Viet tranh.
    refs = json.dumps({
        "che_do": "cham_thu_cong",
        "tu_cho_san": "日记",

        "dap_an_tham_khao": [
            "我每天写日记。",
            "她喜欢写日记。"
        ]
    }, ensure_ascii=False)

    tests = [
        (
            match(
                "A", "A", "chon_mot"
            ) is True,
            "Trac nghiem dung"
        ),
        (
            match(
                "B", "A", "chon_mot"
            ) is False,
            "Trac nghiem sai"
        ),
        (
            match(
                ["B", "A", "C"],
                "BAC",
                "sap_xep_abc"
            ) is True,
            "Sap xep ABC dung"
        ),
        (
            match(
                ["A", "B", "C"],
                "BAC",
                "sap_xep_abc"
            ) is False,
            "Sap xep ABC sai"
        ),
        (
            match(
                ["我", "很好"],
                json.dumps(
                    ["我很好。", "我也很好。"],
                    ensure_ascii=False
                ),
                "sap_xep"
            ) is True,
            "Viet sap xep"
        ),
        (
            match(
                "我每天写日记",
                refs,
                "viet_cau_theo_tranh"
            ) is True,
            "Viet theo tranh dung"
        ),
        (
            match(
                "她喜欢写日记。",
                refs,
                "viet_cau_theo_tranh"
            ) is True,
            "Viet theo tranh dap an thay the"
        ),
        (
            match(
                "我不写日记",
                refs,
                "viet_cau_theo_tranh"
            ) is False,
            "Viet theo tranh sai"
        ),
        (
            match(
                "",
                refs,
                "viet_cau_theo_tranh"
            ) is False,
            "Viet theo tranh bo trong"
        ),
    ]

    errors = [
        name
        for passed, name in tests
        if not passed
    ]

    if errors:
        raise RuntimeError(
            "Test cham diem loi: "
            + ", ".join(errors)
        )

    print(
        f"Test cham dap an: "
        f"{len(tests)}/{len(tests)} DAT."
    )


# =====================================================
# 7. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 55)
    print(
        "MOC HAN - HSK4 CHAM TU DONG"
    )
    print("=" * 55)

    if not FILE.is_file():
        raise RuntimeError(
            f"Khong tim thay file: {FILE}"
        )

    raw = FILE.read_bytes()

    bom = (
        b"\xef\xbb\xbf"
        if raw.startswith(b"\xef\xbb\xbf")
        else b""
    )

    content = raw[len(bom):].decode(
        "utf-8"
    )

    eol = (
        "\r\n"
        if "\r\n" in content
        else "\n"
    )

    updated = transform(
        content.replace(
            "\r\n",
            "\n"
        )
    )

    # Kiem tra truoc khi ghi.
    smoke_test(updated)

    backup = FILE.with_name(
        FILE.name + ".before_hsk4_auto.bak"
    )

    if backup.exists():
        raise RuntimeError(
            "Backup da ton tai. "
            "Khong ghi de:\n"
            + str(backup)
        )

    shutil.copy2(
        FILE,
        backup
    )

    temporary = FILE.with_name(
        FILE.name + ".hsk4_auto.tmp"
    )

    try:

        temporary.write_bytes(
            bom + updated.replace(
                "\n",
                eol
            ).encode("utf-8")
        )

        os.replace(
            temporary,
            FILE
        )

    finally:
        temporary.unlink(
            missing_ok=True
        )

    print(
        "\nDA MO HSK4 CA DE / VIET."
    )

    print(
        "CAU 96-100: CHAM TU DONG "
        "THEO DAP AN THAM KHAO."
    )

    print(
        "KHONG CAN ADMIN CHAM."
    )

    print(
        "Khong thay doi SQL Server."
    )

    print(
        "Backup:", backup
    )


if __name__ == "__main__":
    main()
