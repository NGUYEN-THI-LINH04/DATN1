
# -*- coding: utf-8 -*-
"""
MỘC HÁN - CHUẨN BỊ HSK1 ĐỀ 2 (H10901)

Chức năng:
1. Kiểm tra PDF đề, PDF đáp án và MP3.
2. Xác định mã đề từ PDF đáp án.
3. Trích xuất tự động 40 đáp án.
4. Kiểm tra đáp án Nghe và Đọc.
5. Xuất 10 trang PDF thành ảnh PNG.
6. Tạo JSON đáp án trung gian.

Không thay đổi SQL Server.
Không chỉnh sửa PDF và MP3 gốc.
Không ghi đè de_02.json hoặc dữ liệu Đề 1.
"""

import json
import re
import unicodedata

from pathlib import Path

import fitz


# ==================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ==================================================

# scripts/luyen_thi/hsk1
HSK1_DIR = Path(__file__).resolve().parent

# scripts/luyen_thi
LUYEN_THI_DIR = HSK1_DIR.parent

# Thư mục chứa tài liệu nguồn
SOURCE_DIR = (
    LUYEN_THI_DIR
    / "source"
    / "De_HSK"
    / "HSK1"
    / "Đề 2"
)

# Thư mục dữ liệu JSON
DATA_DIR = (
    HSK1_DIR
    / "data"
    / "de_02"
)

# Thư mục xuất kết quả xử lý
OUTPUT_DIR = (
    HSK1_DIR
    / "output"
    / "de_02"
)

PREVIEW_DIR = OUTPUT_DIR / "preview"

# File PDF nguồn
PDF_DE = SOURCE_DIR / "H1 ĐỀ 2.pdf"

PDF_DAP_AN = (
    SOURCE_DIR
    / "Đề 2  答案.pdf"
)

# File JSON đáp án trung gian
JSON_DAP_AN = (
    DATA_DIR
    / "de_02_dap_an.json"
)

# Thông tin đề
MA_DE = "H10901"
CAP_HSK = 1
THU_TU = 2
TEN_DE = "Đề 2"

TONG_CAU = 40
SO_CAU_NGHE = 20
SO_CAU_DOC = 20


# ==================================================
# 2. KIỂM TRA FILE NGUỒN
# ==================================================

def kiem_tra_nguon():

    print("\n========== KIỂM TRA NGUỒN ==========")

    for file_path in (PDF_DE, PDF_DAP_AN):

        if not file_path.is_file():
            raise FileNotFoundError(
                f"Không tìm thấy: {file_path}"
            )

        print("PDF OK:", file_path.name)

    # Tìm đúng file MP3 của Đề 2.
    mp3_files = [
        path
        for path in SOURCE_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".mp3"
    ]

    if len(mp3_files) != 1:
        raise ValueError(
            "Đề 2 cần có đúng một file MP3. "
            f"Hiện tìm thấy: {len(mp3_files)}"
        )

    mp3_file = mp3_files[0]

    if mp3_file.stat().st_size == 0:
        raise ValueError(
            "File MP3 đang rỗng."
        )

    print("MP3 OK:", mp3_file.name)

    return mp3_file


# ==================================================
# 3. ĐỌC PDF ĐÁP ÁN
# ==================================================

def doc_pdf_dap_an():

    print("\n========== ĐỌC PDF ĐÁP ÁN ==========")

    with fitz.open(PDF_DAP_AN) as document:

        text = "\n".join(
            page.get_text(
                "text",
                sort=True
            )
            for page in document
        )

    # Chuẩn hóa ký tự Unicode.
    text = unicodedata.normalize(
        "NFKC",
        text
    )

    # Lấy các mã HSK xuất hiện trong đáp án.
    codes = set(
        re.findall(
            r"\bH\d{5}\b",
            text,
            flags=re.IGNORECASE
        )
    )

    codes = {
        code.upper()
        for code in codes
    }

    if codes != {MA_DE}:
        raise ValueError(
            "Mã đề trong PDF đáp án không khớp. "
            f"Tìm thấy: {sorted(codes)}"
        )

    print("Mã đề từ đáp án:", MA_DE)

    return text


# ==================================================
# 4. TRÍCH XUẤT 40 ĐÁP ÁN
# ==================================================

def trich_xuat_dap_an(text):
    """
    Nhận dạng các dạng đáp án:

    1．√
    2．×
    6．A
    11．D
    40．C
    """

    print("\n========== TRÍCH ĐÁP ÁN ==========")

    pattern = (
        r"(?<!\d)"
        r"(\d{1,2})"
        r"\s*[.．]"
        r"\s*([A-F√×])"
    )

    matches = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    answers = {}

    for number_text, answer in matches:

        number = int(number_text)
        answer = answer.upper()

        if not 1 <= number <= TONG_CAU:
            continue

        if number in answers:
            raise ValueError(
                f"Trùng đáp án câu {number}"
            )

        answers[number] = answer

    # Kiểm tra đủ câu 1 đến 40.
    expected = set(
        range(1, TONG_CAU + 1)
    )

    actual = set(answers)

    if actual != expected:

        missing = sorted(expected - actual)

        extra = sorted(actual - expected)

        raise ValueError(
            f"Đáp án không hợp lệ. "
            f"Thiếu: {missing}, "
            f"Thừa: {extra}"
        )

    # Kiểm tra các phần Đúng/Sai.
    for number in list(range(1, 6)) + list(
        range(21, 26)
    ):
        if answers[number] not in ("√", "×"):
            raise ValueError(
                f"Câu {number} phải là √ hoặc ×."
            )

    # Kiểm tra các câu chọn A-F.
    for number in (
        list(range(6, 21))
        + list(range(26, 41))
    ):
        if answers[number] not in "ABCDEF":
            raise ValueError(
                f"Đáp án câu {number} không hợp lệ."
            )

    # Các phần trắc nghiệm A/B/C.
    for number in (
        list(range(6, 11))
        + list(range(16, 21))
    ):
        if answers[number] not in "ABC":
            raise ValueError(
                f"Câu {number} chỉ nhận A/B/C."
            )

    print("Tổng số đáp án:", len(answers))
    print("Trích xuất đáp án đạt.")

    return answers


# ==================================================
# 5. HIỂN THỊ ĐÁP ÁN ĐỂ KIỂM TRA
# ==================================================

def hien_thi_dap_an(answers):

    print("\n========== PHẦN NGHE ==========")

    for number in range(1, 21):

        print(
            f"{number:02d}: {answers[number]}",
            end="   "
        )

        if number % 5 == 0:
            print()

    print("\n========== PHẦN ĐỌC ==========")

    for number in range(21, 41):

        print(
            f"{number:02d}: {answers[number]}",
            end="   "
        )

        if number % 5 == 0:
            print()


# ==================================================
# 6. XUẤT ẢNH TỪ PDF ĐỀ THI
# ==================================================

def xuat_anh_pdf():

    print("\n========== XUẤT ẢNH PDF ==========")

    PREVIEW_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with fitz.open(PDF_DE) as document:

        total_pages = len(document)

        if total_pages != 10:
            raise ValueError(
                "Đề 2 dự kiến có 10 trang, "
                f"nhưng hiện có {total_pages}."
            )

        for index, page in enumerate(document):

            page_number = index + 1

            output_file = (
                PREVIEW_DIR
                / f"trang_{page_number:02d}.png"
            )

            # Render PDF thành ảnh để giữ:
            # - Chữ Hán
            # - Hình minh họa
            # - Nội dung dạng vector
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                colorspace=fitz.csRGB,
                alpha=False
            )

            pixmap.save(
                str(output_file)
            )

            print(
                f"Đã xuất trang {page_number:02d}"
                f"/{total_pages}"
            )

    return total_pages


# ==================================================
# 7. LƯU JSON ĐÁP ÁN TRUNG GIAN
# ==================================================

def luu_json_dap_an(answers, mp3_file):

    print("\n========== LƯU JSON ==========")

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    data = {
        "ma_de_goc": MA_DE,
        "cap_hsk": CAP_HSK,
        "ten_hien_thi": TEN_DE,
        "thu_tu": THU_TU,
        "so_cau": TONG_CAU,
        "so_cau_nghe": SO_CAU_NGHE,
        "so_cau_doc": SO_CAU_DOC,
        "so_cau_viet": 0,
        "nguon": {
            "pdf_de": PDF_DE.name,
            "pdf_dap_an": PDF_DAP_AN.name,
            "mp3": mp3_file.name
        },
        "dap_an": {
            str(number): answers[number]
            for number in range(1, 41)
        }
    }

    JSON_DAP_AN.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("Đã tạo:", JSON_DAP_AN)


# ==================================================
# 8. HÀM CHÍNH
# ==================================================

def main():

    print("=" * 50)
    print("MỘC HÁN - CHUẨN BỊ HSK1 ĐỀ 2")
    print("=" * 50)

    # Bước 1: Kiểm tra file nguồn.
    mp3_file = kiem_tra_nguon()

    # Bước 2: Đọc PDF đáp án.
    answer_text = doc_pdf_dap_an()

    # Bước 3: Trích 40 đáp án.
    answers = trich_xuat_dap_an(
        answer_text
    )

    # Bước 4: In để đối chiếu.
    hien_thi_dap_an(answers)

    # Bước 5: Xuất ảnh 10 trang PDF.
    total_pages = xuat_anh_pdf()

    # Bước 6: Lưu JSON trung gian.
    luu_json_dap_an(
        answers,
        mp3_file
    )

    print("\n" + "=" * 50)
    print("HOÀN THÀNH CHUẨN BỊ ĐỀ 2")
    print("=" * 50)

    print("Mã đề:", MA_DE)
    print("Số trang:", total_pages)
    print("Số câu:", TONG_CAU)
    print("Nghe:", SO_CAU_NGHE)
    print("Đọc:", SO_CAU_DOC)

    print("\nẢnh PDF:")
    print(PREVIEW_DIR)

    print("\nJSON đáp án:")
    print(JSON_DAP_AN)

    print("\nChưa nhập hoặc thay đổi SQL Server.")


if __name__ == "__main__":
    main()
