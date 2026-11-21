from pathlib import Path
import shutil
import fitz

# ==========================================
# MOC HAN - SUA DOC PHAN 2 VA 3 - HSK1 DE 7
# Chi sua anh cau 26-35
# ==========================================

ROOT = Path(r"D:\DATN1")

PDF_PATH = (
    ROOT
    / "scripts/luyen_thi/source/De_HSK/HSK1/H11007.pdf"
)

OUTPUT_DIR = (
    ROOT
    / "scripts/luyen_thi/hsk1/output/de_07/questions"
)

BACKUP_DIR = (
    ROOT
    / "scripts/luyen_thi/hsk1/output/de_07/backup_doc_phan_2_3"
)

# Toa do theo PDF H11007 thuc te.
# Dinh dang:
# cau: (trang_pdf, x0, y0, x1, y1)

CROPS = {
    # DOC PHAN 2 - TRANG PDF 8
    26: (8, 74, 548, 535, 590),
    27: (8, 74, 589, 535, 624),
    28: (8, 74, 624, 535, 658),
    29: (8, 74, 658, 535, 693),
    30: (8, 74, 693, 535, 741),

    # DOC PHAN 3 - TRANG PDF 9
    31: (9, 70, 238, 535, 303),
    32: (9, 70, 303, 535, 399),
    33: (9, 70, 399, 535, 495),
    34: (9, 70, 495, 535, 558),
    35: (9, 70, 558, 535, 646),
}


def main():
    print("=" * 55)
    print("MOC HAN - SUA CAU 26-35 - H11007")
    print("=" * 55)

    if not PDF_PATH.is_file():
        raise FileNotFoundError(
            f"Khong tim thay PDF: {PDF_PATH}"
        )

    if not OUTPUT_DIR.is_dir():
        raise FileNotFoundError(
            f"Khong tim thay thu muc anh: {OUTPUT_DIR}"
        )

    # Kiem tra du 10 anh truoc khi sua
    for so_cau in CROPS:
        image_path = OUTPUT_DIR / f"cau_{so_cau:02d}.png"

        if not image_path.is_file():
            raise FileNotFoundError(
                f"Thieu anh cau {so_cau}: {image_path}"
            )

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\n========== SAO LUU ANH CU ==========")

    for so_cau in CROPS:
        image_path = OUTPUT_DIR / f"cau_{so_cau:02d}.png"
        backup_path = BACKUP_DIR / image_path.name

        # Khong ghi de ban sao luu goc
        if not backup_path.exists():
            shutil.copy2(
                image_path,
                backup_path
            )

        print(f"Da sao luu: cau_{so_cau:02d}.png")

    print("\n========== CAT LAI ANH ==========")

    with fitz.open(PDF_PATH) as doc:
        for so_cau, (
            page_number,
            x0,
            y0,
            x1,
            y1
        ) in CROPS.items():

            page = doc[page_number - 1]

            rect = fitz.Rect(
                x0, y0, x1, y1
            )

            if not page.rect.contains(rect):
                raise ValueError(
                    f"Cau {so_cau}: Toa do nam ngoai PDF"
                )

            pix = page.get_pixmap(
                matrix=fitz.Matrix(3, 3),
                clip=rect,
                alpha=False
            )

            output_file = (
                OUTPUT_DIR
                / f"cau_{so_cau:02d}.png"
            )

            pix.save(str(output_file))

            print(
                f"Cau {so_cau:02d}: "
                f"trang {page_number}, "
                f"y={y0}-{y1}, "
                f"{pix.width}x{pix.height}px"
            )

    print("\n========== HOAN THANH ==========")
    print("Da cat lai: 10 anh cau 26-35")
    print(f"Anh moi: {OUTPUT_DIR}")
    print(f"Anh sao luu: {BACKUP_DIR}")
    print("Khong thay doi JSON hoac SQL Server.")


if __name__ == "__main__":
    main()
