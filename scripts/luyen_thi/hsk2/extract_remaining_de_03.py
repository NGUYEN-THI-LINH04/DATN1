
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK2 DE 3 - H21003

Tach cau 11-60 va 6 bang lua chon.
Tai su dung bo tach anh HSK2 De 2 da kiem tra.

- Giu nguyen 10 anh dau.
- Khong sua De 1, De 2.
- Khong thay doi SQL Server.
"""

from pathlib import Path
import fitz


ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

HSK2 = ROOT / "hsk2"

SOURCE_SCRIPT = HSK2 / "extract_remaining_de_02.py"

PDF_FILE = (
    ROOT / "source" / "De_HSK" / "HSK2"
    / "Đề HSK 2 số 3.pdf"
)

ANSWER_FILE = (
    HSK2 / "data" / "de_03"
    / "de_03_dap_an.json"
)

QUESTION_DIR = (
    HSK2 / "output" / "de_03" / "questions"
)

EXPECTED_CODE = "H21003"


def main():
    print("=" * 60)
    print("MOC HAN - HSK2 DE 3")
    print("TACH CAU 11-60")
    print("=" * 60)

    # Kiem tra file nguon
    for path in (
        SOURCE_SCRIPT,
        PDF_FILE,
        ANSWER_FILE,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)

    # Kiem tra 10 anh dau, khong ghi de.
    for number in range(1, 11):
        path = QUESTION_DIR / f"cau_{number:02d}.png"

        if not path.is_file():
            raise FileNotFoundError(path)

    # Kiem tra ma de that trong PDF.
    with fitz.open(PDF_FILE) as doc:
        if len(doc) != 18:
            raise RuntimeError(
                "PDF khong du 18 trang."
            )

        cover = doc[0].get_text("text")
        answer_page = doc[17].get_text("text")

        if (
            EXPECTED_CODE not in cover
            or EXPECTED_CODE not in answer_page
        ):
            raise RuntimeError(
                "PDF khong dung ma H21003."
            )

    # Doc script De 2 da chay thanh cong.
    source = SOURCE_SCRIPT.read_text(
        encoding="utf-8-sig"
    )

    # Kiem tra dung script mau.
    required = [
        "H20902",
        "de_02",
        "Đề HSK 2 số 2.pdf",
    ]

    for value in required:
        if value not in source:
            raise RuntimeError(
                f"Script mau thieu: {value}"
            )

    # Chuyen toan bo tham chieu sang De 3.
    replacements = {
        "H20902": "H21003",
        "de_02": "de_03",
        "Đề HSK 2 số 2.pdf": "Đề HSK 2 số 3.pdf",
        "Đề 2": "Đề 3",
        "DE 2": "DE 3",
        "De 2": "De 3",
    }

    for old, new in replacements.items():
        source = source.replace(old, new)

    # Dam bao khong con tham chieu De 2.
    for old in required:
        if old in source:
            raise RuntimeError(
                f"Con tham chieu De 2: {old}"
            )

    # Kiem tra cu phap.
    compiled = compile(
        source,
        "hsk2_extract_remaining_H21003",
        "exec"
    )

    print("\nDa kiem tra PDF H21003.")
    print("Da co 10 anh dau tien.")
    print("Da chuyen script sang du lieu De 3.")

    print("\n===== BAT DAU TACH ANH =====")

    # Chay bo tach anh voi duong dan De 3.
    namespace = {
        "__name__": "__main__",
        "__file__": str(
            HSK2 / "extract_remaining_de_03.py"
        ),
    }

    exec(compiled, namespace)


if __name__ == "__main__":
    main()
