
# -*- coding: utf-8 -*-

"""
MOC HAN - KIEM TRA BO CUC HSK4

Lay H41001 lam cau truc tham chieu.
Dung cho H41002-H41010.

- Khong sua PDF goc.
- Khong sao chep dap an De 1.
- Khong ket noi SQL.
- Tu dong tao bao cao va anh xem truoc.
"""

import argparse
import re
from pathlib import Path

import fitz


ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "luyen_thi"

SOURCE = BASE / "source" / "De_HSK" / "HSK4"

OUTPUT = BASE / "hsk4" / "output"


def page_text(doc, page_number):
    if not 1 <= page_number <= len(doc):
        return ""

    return doc[page_number - 1].get_text("text")


def question_numbers(text):

    found = re.findall(
        r"(?m)^\s*(\d{1,3})\s*[.．、]",
        text
    )

    return sorted({
        int(n)
        for n in found
        if 1 <= int(n) <= 100
    })


def render_page(doc, page_number, target):

    if not 1 <= page_number <= len(doc):
        return

    page = doc[page_number - 1]

    pix = page.get_pixmap(
        matrix=fitz.Matrix(2, 2),
        alpha=False
    )

    pix.save(str(target))


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--de",
        type=int,
        required=True
    )

    args = parser.parse_args()

    if not 2 <= args.de <= 10:
        raise RuntimeError(
            "Chi kiem tra De 2 den De 10."
        )

    code = f"H410{args.de:02d}"

    baseline_path = SOURCE / "H41001.pdf"

    pdf_path = SOURCE / f"{code}.pdf"

    mp3_path = SOURCE / f"{code}.mp3"

    for path in (
        baseline_path,
        pdf_path,
        mp3_path
    ):
        if not path.is_file():
            raise RuntimeError(
                f"Khong tim thay: {path}"
            )

    out_dir = (
        OUTPUT / f"de_{args.de:02d}"
        / "kiem_tra_bo_cuc"
    )

    out_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    report = []

    with (
        fitz.open(baseline_path) as baseline,
        fitz.open(pdf_path) as current
    ):

        if code not in page_text(current, 1):
            raise RuntimeError(
                "Ma de tren bia PDF "
                "khong khop."
            )

        report.append(
            f"MA DE: {code}"
        )

        report.append(
            f"PDF DE 1: {len(baseline)} trang"
        )

        report.append(
            f"PDF DE {args.de}: "
            f"{len(current)} trang"
        )

        report.append(
            f"MP3: {mp3_path.name}"
        )

        report.append(
            f"MP3 bytes: {mp3_path.stat().st_size}"
        )

        report.append(
            "\n=== SO SANH CAC TRANG ==="
        )

        for page_number in range(
            1,
            max(
                len(baseline),
                len(current)
            ) + 1
        ):

            old_text = page_text(
                baseline,
                page_number
            )

            new_text = page_text(
                current,
                page_number
            )

            old_numbers = question_numbers(
                old_text
            )

            new_numbers = question_numbers(
                new_text
            )

            # Chi de tham chieu bo cuc.
            # So cau o hai cot co the khong
            # nam dau dong trong text PDF.
            report.append(
                f"\nTRANG {page_number}"
            )

            report.append(
                f"De 1 - so cau nhan dien: "
                f"{old_numbers}"
            )

            report.append(
                f"De {args.de} - so cau "
                f"nhan dien: {new_numbers}"
            )

            report.append(
                f"De 1 - so ky tu: "
                f"{len(old_text)}"
            )

            report.append(
                f"De {args.de} - so ky tu: "
                f"{len(new_text)}"
            )

            if (
                page_number <= len(baseline)
                and page_number <= len(current)
            ):

                old_images = len(
                    baseline[
                        page_number - 1
                    ].get_images(full=True)
                )

                new_images = len(
                    current[
                        page_number - 1
                    ].get_images(full=True)
                )

                report.append(
                    f"Anh nhung PDF: "
                    f"De 1={old_images}, "
                    f"De {args.de}={new_images}"
                )

        # ====================================
        # CAC TRANG CAN DOC NOI DUNG THAT
        # ====================================

        inspect_pages = [
            7, 8, 9, 10,
            15, 16,
            23, 24
        ]

        for number in inspect_pages:

            if number > len(current):
                continue

            report.append(
                "\n" + "=" * 50
            )

            report.append(
                f"NOI DUNG TRANG {number}"
            )

            report.append(
                "=" * 50
            )

            report.append(
                page_text(current, number)
            )

        # ====================================
        # XUAT ANH XEM TRUOC
        # ====================================

        for number in (
            7, 8, 15, 16, 23, 24
        ):

            if number <= len(current):

                render_page(
                    current,
                    number,
                    out_dir
                    / f"trang_{number:02d}.png"
                )

    # ========================================
    # LUU BAO CAO
    # ========================================

    report_file = (
        out_dir / "bao_cao_bo_cuc.txt"
    )

    report_file.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("=" * 55)
    print(
        f"KIEM TRA BO CUC HSK4 "
        f"DE {args.de}"
    )
    print("=" * 55)

    print(f"Ma de: {code}")
    print(f"PDF: {pdf_path}")
    print(f"MP3: {mp3_path}")

    print(
        f"Bao cao: {report_file}"
    )

    print(
        "Da tao anh xem truoc "
        "trang 07, 08, 15, 16, 23, 24 "
        "(neu cac trang ton tai)."
    )

    print(
        "\nKHONG thay doi SQL Server."
    )


if __name__ == "__main__":
    main()
