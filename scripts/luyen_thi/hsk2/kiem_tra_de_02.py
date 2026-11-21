import fitz
from pathlib import Path

pdf = Path(
    r"D:\DATN1\scripts\luyen_thi\source\De_HSK\HSK2\Đề HSK 2 số 2.pdf"
)

with fitz.open(pdf) as doc:
    print("TONG SO TRANG:", len(doc))

    for i, page in enumerate(doc, 1):
        text = page.get_text("text")

        print(f"\n===== TRANG {i} =====")
        print("Ky tu:", len(text))

        if "答案" in text:
            print("*** CO TU KHOA DAP AN ***")

        if "听力材料" in text:
            print("*** CO LOI THOAI NGHE ***")

        print(text[:180].replace("\n", " "))
