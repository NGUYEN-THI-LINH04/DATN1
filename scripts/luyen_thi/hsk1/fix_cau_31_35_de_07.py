# -*- coding: utf-8 -*-
"""
MỘC HÁN - FIX CÂU 31-35 HSK1 ĐỀ 7

Mục tiêu:
- Cắt lại câu 31-35 của phần Đọc - Phần 3
- Bỏ phần đáp án bên phải vì đã có "Bảng lựa chọn chung" ở phía trên
- Giữ lại phần câu hỏi bên trái và ô chọn

Không thay đổi SQL Server.
"""

from pathlib import Path
import shutil
import fitz


# =========================================================
# 1. ĐƯỜNG DẪN
# =========================================================

ROOT = Path(r"D:\DATN1")

PDF_PATH = (
    ROOT
    / "scripts"
    / "luyen_thi"
    / "source"
    / "De_HSK"
    / "HSK1"
    / "H11007.pdf"
)

QUESTIONS_DIR = (
    ROOT
    / "scripts"
    / "luyen_thi"
    / "hsk1"
    / "output"
    / "de_07"
    / "questions"
)

BACKUP_DIR = (
    ROOT
    / "scripts"
    / "luyen_thi"
    / "hsk1"
    / "output"
    / "de_07"
    / "backup_fix_31_35"
)


# =========================================================
# 2. TOẠ ĐỘ CẮT MỚI
# Chỉ lấy phần bên trái + ô tick, bỏ phần đáp án bên phải
# =========================================================

CROPS = {
    # so_cau: (trang_pdf, x0, y0, x1, y1)

    # Trang 9 của PDF gốc
    31: (9, 82, 245, 305, 302),
    32: (9, 82, 307, 305, 365),
    33: (9, 82, 400, 305, 458),
    34: (9, 82, 493, 305, 551),
    35: (9, 82, 556, 305, 615),
}


# =========================================================
# 3. HÀM PHỤ
# =========================================================

def backup_file(path: Path):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / path.name

    if not backup_path.exists():
        shutil.copy2(path, backup_path)

    return backup_path


def render_crop(page, rect, output_path: Path, scale=3):
    rect = fitz.Rect(rect)
    rect = rect & page.rect

    if rect.is_empty:
        raise RuntimeError(f"Vùng cắt rỗng: {rect}")

    pix = page.get_pixmap(
        matrix=fitz.Matrix(scale, scale),
        clip=rect,
        alpha=False,
    )
    pix.save(str(output_path))


# =========================================================
# 4. MAIN
# =========================================================

def main():
    print("=" * 60)
    print("FIX CÂU 31-35 - HSK1 ĐỀ 7 (H11007)")
    print("=" * 60)

    if not PDF_PATH.is_file():
        raise FileNotFoundError(f"Không tìm thấy PDF: {PDF_PATH}")

    if not QUESTIONS_DIR.is_dir():
        raise FileNotFoundError(
            f"Không tìm thấy thư mục câu hỏi: {QUESTIONS_DIR}"
        )

    with fitz.open(PDF_PATH) as doc:
        for so_cau, (page_number, x0, y0, x1, y1) in CROPS.items():
            output_file = QUESTIONS_DIR / f"cau_{so_cau:02d}.png"

            if output_file.exists():
                backup_file(output_file)

            page = doc[page_number - 1]

            render_crop(
                page,
                (x0, y0, x1, y1),
                output_file,
                scale=3,
            )

            print(
                f"Đã cắt lại câu {so_cau:02d} "
                f"-> trang {page_number}, "
                f"rect=({x0}, {y0}, {x1}, {y1})"
            )

    print()
    print("HOÀN THÀNH.")
    print("Đã cắt lại các câu 31-35.")
    print("Đã loại bỏ phần đáp án bên phải.")
    print(f"Backup cũ: {BACKUP_DIR}")
    print(f"Ảnh mới:   {QUESTIONS_DIR}")
    print("Không thay đổi SQL Server.")


if __name__ == "__main__":
    main()