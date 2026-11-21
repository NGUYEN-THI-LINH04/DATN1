
# -*- coding: utf-8 -*-

"""
MOC HAN - BO SUNG HO TRO HSK4

Sua dung 2 file:
1. routes/student/luyen_thi_lam_bai.py
2. static/js/student-luyen-thi-lam-bai.js

- Ho tro sap xep ABC cua HSK4.
- Ho tro nhieu dap an hop le khi sap xep cau.
- Khong lap anh bang lua chon chung.
- Tam khoa Ca de/Viet HSK4 khi chua co cham Viet mo.
- Giữ nguyen HSK1-HSK3.
- Tu dong sao luu 2 file.

KHONG sua SQL Server.
KHONG sua JSON de thi.
KHONG sua bang Bai tap.
"""

from pathlib import Path
import os
import shutil
import subprocess
import tempfile


ROOT = Path(
    os.environ.get(
        "MOC_HAN_ROOT",
        r"D:\DATN1"
    )
)

PY_FILE = (
    ROOT / "routes"
    / "student"
    / "luyen_thi_lam_bai.py"
)

JS_FILE = (
    ROOT / "static"
    / "js"
    / "student-luyen-thi-lam-bai.js"
)


# =====================================================
# 1. DOC FILE, GIU NGUYEN ENCODING
# =====================================================

def read_file(path):

    raw = path.read_bytes()

    bom = (
        b"\xef\xbb\xbf"
        if raw.startswith(b"\xef\xbb\xbf")
        else b""
    )

    data = raw[len(bom):].decode("utf-8")

    newline = (
        "\r\n" if "\r\n" in data else "\n"
    )

    return (
        data.replace("\r\n", "\n"),
        newline,
        bom
    )


# =====================================================
# 2. CHI THAY KHI KHOP CHINH XAC
# =====================================================

def replace_exact(
    content,
    before,
    after,
    label
):

    count = content.count(before)

    if count != 1:
        raise RuntimeError(
            f"{label}: can 1 vi tri, "
            f"tim duoc {count}.\n"
            "Khong sua file."
        )

    return content.replace(
        before,
        after,
        1
    )


# =====================================================
# 3. SUA BACKEND VA JAVASCRIPT
# =====================================================

def transform(py, js):

    if (
        "def match_hsk4_answer(" in py
        or "seenSharedPaths" in js
    ):
        raise RuntimeError(
            "Co dau hieu da sua HSK4. "
            "Khong sua trung."
        )

    # ================================================
    # 4. CHAN TAM THOI HSK4 VIET MO
    # ================================================

    guard = '''    if skill == "viet" and level < 3:
        abort(404)
'''

    addition = guard + '''
    # HSK4 Viet tranh chua co luong cham thu cong.
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

    py = replace_exact(
        py,
        guard,
        addition,
        "Bao ve HSK4"
    )

    # ================================================
    # 5. HAM CHAM DAP AN HSK4
    # ================================================

    helper = '''def match_hsk4_answer(given, correct_answer, kind):
    """
    Bo sung cham HSK4, giu logic HSK1-HSK3.
    """

    if kind == "viet_cau_theo_tranh":
        # Tuyet doi khong tu cho 0 diem.
        raise RuntimeError(
            "HSK4 Viet theo tranh chua co "
            "co che cham thu cong. "
            "Khong duoc tu chot ket qua."
        )

    actual = normalize_answer(
        given,
        kind,
    )

    if not actual:
        return False

    # Cau 56-65:
    # Nguoi hoc phai xep du A/B/C theo thu tu.
    if kind == "sap_xep_abc":

        if (
            len(actual) != 3
            or set(actual) != {"A", "B", "C"}
        ):
            return False

        return actual == normalize_answer(
            correct_answer,
            kind,
        )

    # Cau 86-95:
    # Co the co nhieu dap an hop le.
    if kind == "sap_xep":

        variants = correct_answer

        if (
            isinstance(variants, str)
            and variants.lstrip().startswith("[")
        ):
            try:
                variants = json.loads(variants)

            except (ValueError, TypeError):
                variants = correct_answer

        if not isinstance(variants, list):
            variants = [variants]

        return any(
            actual == normalize_answer(
                candidate,
                kind,
            )

            for candidate in variants

            if (
                isinstance(candidate, str)
                and candidate.strip()
            )
        )

    # Cac dang cau hoi cu giu nguyen.
    expected = normalize_answer(
        correct_answer,
        kind,
    )

    return (
        bool(actual)
        and actual == expected
    )


'''

    py = replace_exact(
        py,
        "def persist_answer(\n",
        helper + "def persist_answer(\n",
        "Bo sung ham cham"
    )

    # ================================================
    # 6. DOI HAM SO SANH DAP AN
    # ================================================

    old_match = '''    matched = False

    if graded:
        normalized = normalize_answer(
            given,
            question["LoaiCauHoi"],
        )

        expected = normalize_answer(
            correct_answer,
            question["LoaiCauHoi"],
        )

        matched = (
            bool(normalized)
            and normalized == expected
        )
'''

    new_match = '''    matched = False

    if graded:
        matched = match_hsk4_answer(
            given,
            correct_answer,
            question["LoaiCauHoi"],
        )
'''

    py = replace_exact(
        py,
        old_match,
        new_match,
        "So sanh dap an"
    )

    # ================================================
    # 7. JAVASCRIPT: THEM SAP XEP ABC
    # ================================================

    old_js = '''            type === "sap_xep" &&
            options.length > 0'''

    new_js = '''            ["sap_xep", "sap_xep_abc"].includes(type) &&
            options.length > 0'''

    js = replace_exact(
        js,
        old_js,
        new_js,
        "Giao dien sap xep ABC"
    )

    # ================================================
    # 8. JAVASCRIPT: KHONG LAP BANG CHUNG
    # ================================================

    old_group = '''        el("lt-question-area").innerHTML =
            group.questions.map(
                q => questionMarkup(
                    q,
                    Boolean(shared)
                )
            ).join("");'''

    new_group = '''        // Moi bang chung chi hien thi mot lan.
        const seenSharedPaths = new Set();

        el("lt-question-area").innerHTML =
            group.questions.map(q => {

                const path = q.AnhNhomLuaChon;

                const skipGroupImage = Boolean(shared) ||
                    Boolean(
                        path &&
                        seenSharedPaths.has(path)
                    );

                if (path) {
                    seenSharedPaths.add(path);
                }

                return questionMarkup(
                    q,
                    skipGroupImage
                );

            }).join("");'''

    js = replace_exact(
        js,
        old_group,
        new_group,
        "Bang lua chon chung"
    )

    return py, js


# =====================================================
# 9. KIEM TRA VA SAO LUU
# =====================================================

def main():

    print("=" * 55)
    print("MOC HAN - BO SUNG HSK4")
    print("=" * 55)

    for path in (PY_FILE, JS_FILE):

        if not path.is_file():
            raise RuntimeError(
                f"Khong tim thay: {path}"
            )

    original_py, eol_py, bom_py = read_file(
        PY_FILE
    )

    original_js, eol_js, bom_js = read_file(
        JS_FILE
    )

    revised_py, revised_js = transform(
        original_py,
        original_js
    )

    # Kiem tra Python truoc khi ghi.
    compile(
        revised_py,
        str(PY_FILE),
        "exec"
    )

    # Kiem tra JavaScript neu co Node.js.
    with tempfile.TemporaryDirectory() as tmp:

        js_check = (
            Path(tmp) / "hsk4_check.js"
        )

        js_check.write_text(
            revised_js,
            encoding="utf-8"
        )

        node = shutil.which("node")

        if node:

            subprocess.run(
                [
                    node,
                    "--check",
                    str(js_check)
                ],
                check=True
            )

        else:
            print(
                "Chua co Node.js de kiem tra JS."
            )

    # ================================================
    # 10. SAO LUU HAI FILE GOC
    # ================================================

    for path in (PY_FILE, JS_FILE):

        backup = path.with_name(
            path.name + ".before_hsk4.bak"
        )

        if backup.exists():
            raise RuntimeError(
                "Da co file backup. "
                "Khong ghi de:\n"
                + str(backup)
            )

    for path in (PY_FILE, JS_FILE):

        shutil.copy2(
            path,
            path.with_name(
                path.name + ".before_hsk4.bak"
            )
        )

    # ================================================
    # 11. GIU NGUYEN XUONG DONG CU
    # ================================================

    def packed(text, eol, bom):

        return (
            bom +
            text.replace(
                "\n",
                eol
            ).encode("utf-8")
        )

    temp_py = PY_FILE.with_name(
        PY_FILE.name + ".hsk4.tmp"
    )

    temp_js = JS_FILE.with_name(
        JS_FILE.name + ".hsk4.tmp"
    )

    # ================================================
    # 12. GHI HAI FILE DA SUA
    # ================================================

    try:

        temp_py.write_bytes(
            packed(
                revised_py,
                eol_py,
                bom_py
            )
        )

        temp_js.write_bytes(
            packed(
                revised_js,
                eol_js,
                bom_js
            )
        )

        os.replace(
            temp_py,
            PY_FILE
        )

        os.replace(
            temp_js,
            JS_FILE
        )

    except Exception:

        # Neu ghi loi, khoi phuc ca hai file.
        shutil.copy2(
            PY_FILE.with_name(
                PY_FILE.name + ".before_hsk4.bak"
            ),
            PY_FILE
        )

        shutil.copy2(
            JS_FILE.with_name(
                JS_FILE.name + ".before_hsk4.bak"
            ),
            JS_FILE
        )

        raise

    finally:

        temp_py.unlink(
            missing_ok=True
        )

        temp_js.unlink(
            missing_ok=True
        )

    print("\nDA SUA THANH CONG HAI FILE")

    print("Python: OK")
    print("JavaScript: OK")

    print(
        "Da sao luu file goc "
        "voi duoi .before_hsk4.bak"
    )

    print(
        "HSK4 Nghe/Doc: "
        "co the kiem tra."
    )

    print(
        "HSK4 Ca de/Viet: "
        "tam khoa de tranh cham sai."
    )

    print(
        "\nKhong thay doi SQL Server."
    )


if __name__ == "__main__":
    main()
