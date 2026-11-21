# -*- coding: utf-8 -*-

from pathlib import Path
import json
import fitz

ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

PDF = (
    ROOT / "source" / "De_HSK" / "HSK2"
    / "Đề HSK 2 số 1 file pdf.pdf"
)

MP3 = (
    ROOT / "source" / "De_HSK" / "HSK2"
    / "Đề HSK 2 số 1 file nghe.mp3"
)

DATA = ROOT / "hsk2" / "data" / "de_01"
PREVIEW = ROOT / "hsk2" / "output" / "de_01" / "preview"

# Đáp án từ trang 18 của H20901
# Mỗi chuỗi tương ứng 5 câu liên tiếp.
ANSWER_ROWS = [
    "×√××√",  # 1-5
    "√×√×√",  # 6-10
    "FACEB",  # 11-15
    "BECAD",  # 16-20
    "CBACA",  # 21-25
    "ABBCC",  # 26-30
    "AABBC",  # 31-35
    "FECBA",  # 36-40
    "DBACF",  # 41-45
    "√××√×",  # 46-50
    "CBFAD",  # 51-55
    "DCEBA",  # 56-60
]


def main():
    print("=" * 55)
    print("MOC HAN - CHUAN BI HSK2 DE 1 - H20901")
    print("=" * 55)

    if not PDF.is_file():
        raise FileNotFoundError(PDF)

    if not MP3.is_file():
        raise FileNotFoundError(MP3)

    answers = "".join(ANSWER_ROWS)

    if len(answers) != 60:
        raise ValueError("Dap an khong du 60 cau.")

    for index, value in enumerate(answers, 1):
        allowed = (
            {"√", "×"}
            if index <= 10 or 46 <= index <= 50
            else set("ABCDEF")
        )

        if value not in allowed:
            raise ValueError(
                f"Dap an khong hop le: cau {index} = {value}"
            )

    DATA.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)

    with fitz.open(PDF) as doc:
        print(f"PDF co {len(doc)} trang")

        if len(doc) < 18:
            raise ValueError(
                "PDF khong du 18 trang nhu ban goc."
            )

        print("\n===== XUAT ANH CAU HOI =====")

        for page_number in range(1, 16):
            page = doc[page_number - 1]

            pix = page.get_pixmap(
                matrix=fitz.Matrix(1.5, 1.5),
                alpha=False
            )

            name = f"trang_{page_number:02d}.png"
            pix.save(str(PREVIEW / name))

            print(f"Da tao: {name}")

    result = {
        "cap_hsk": 2,
        "so_de": 1,
        "ma_de_goc": "H20901",
        "file_pdf": PDF.name,
        "file_mp3": MP3.name,
        "tong_cau": 60,
        "so_cau_nghe": 35,
        "so_cau_doc": 25,
        "trang_cau_hoi": list(range(1, 16)),
        "trang_bo_qua": [16, 17],
        "trang_dap_an": 18,
        "dap_an": {
            str(i): answer
            for i, answer in enumerate(answers, 1)
        },
    }

    output_json = DATA / "de_01_dap_an.json"

    with output_json.open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("\n===== HOAN THANH =====")
    print("Ma de: H20901")
    print("HSK: 2")
    print("Dap an: 60/60")
    print("Anh cau hoi: 15 trang")
    print("Bo qua: trang 16, 17")
    print("Trang 18: chi dung lam dap an")
    print(f"JSON: {output_json}")
    print("Chua tach tung cau.")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
