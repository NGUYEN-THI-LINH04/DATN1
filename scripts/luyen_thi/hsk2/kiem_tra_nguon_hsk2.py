# -*- coding: utf-8 -*-
"""
MOC HAN - KIEM TRA NGUON DE HSK2

- Kiem tra 12 file PDF
- Kiem tra MP3 tuong ung
- Tim trang co tu khoa dap an
- Xuat anh xem truoc De 1
- Khong thay doi SQL Server
"""

from pathlib import Path
import re
import fitz


ROOT = Path(r"D:\DATN1\scripts\luyen_thi")

SOURCE = ROOT / "source" / "De_HSK" / "HSK2"

OUTPUT = (
    ROOT / "hsk2" / "output"
    / "de_01" / "preview_nguon"
)


def get_so_de(filename):
    match = re.search(
        r"Đề\s*HSK\s*2\s*số\s*(\d+)",
        filename,
        re.IGNORECASE
    )
    return int(match.group(1)) if match else None


def main():
    print("=" * 60)
    print("MOC HAN - KIEM TRA 12 BO DE HSK2")
    print("=" * 60)

    pdfs = sorted(
        SOURCE.glob("*.pdf"),
        key=lambda p: get_so_de(p.name) or 999
    )

    audios = list(SOURCE.glob("*.mp3"))

    print(f"\nSo file PDF: {len(pdfs)}")
    print(f"So file MP3: {len(audios)}")

    for pdf in pdfs:
        so_de = get_so_de(pdf.name)

        matched_audio = [
            a for a in audios
            if get_so_de(a.name) == so_de
        ]

        with fitz.open(pdf) as doc:
            pages_with_text = 0
            possible_answer_pages = []

            for idx, page in enumerate(doc):
                text = page.get_text("text")

                if text.strip():
                    pages_with_text += 1

                if re.search(
                    r"答案|参考答案|Đáp\s*án|Answer\s*Key",
                    text,
                    re.IGNORECASE
                ):
                    possible_answer_pages.append(idx + 1)

            print(f"\nDE {so_de:02d}")
            print(f"PDF: {pdf.name}")
            print(f"Trang PDF: {len(doc)}")
            print(f"Trang co text: {pages_with_text}")

            if matched_audio:
                print(f"MP3: {matched_audio[0].name}")
            else:
                print("MP3: THIEU")

            print(
                "Trang co tu khoa dap an:",
                possible_answer_pages
            )

    # ==========================================
    # KIEM TRA CHI TIET DE 1
    # ==========================================

    de_01 = next(
        (p for p in pdfs if get_so_de(p.name) == 1),
        None
    )

    if de_01 is None:
        raise FileNotFoundError("Khong tim thay De HSK2 so 1")

    OUTPUT.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("KIEM TRA CHI TIET DE HSK2 SO 1")
    print("=" * 60)

    with fitz.open(de_01) as doc:

        # Xuat trang dau va 3 trang cuoi
        selected_pages = sorted(set(
            [0] + list(range(max(0, len(doc) - 3), len(doc)))
        ))

        for idx in selected_pages:
            page = doc[idx]

            pix = page.get_pixmap(
                matrix=fitz.Matrix(1.8, 1.8),
                alpha=False
            )

            output_file = (
                OUTPUT / f"trang_{idx + 1:02d}.png"
            )

            pix.save(str(output_file))

            print(f"\n===== TRANG PDF {idx + 1} =====")

            text = page.get_text("text").strip()

            if text:
                print(text[:2500])
            else:
                print(
                    "Khong trich xuat duoc text. "
                    "Can kiem tra anh trang PDF."
                )

            print(f"Anh: {output_file}")

    print("\nHOAN THANH KIEM TRA")
    print("Chua tach cau hoi.")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
