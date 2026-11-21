
# -*- coding: utf-8 -*-
"""
MỘC HÁN - CHUẨN BỊ HSK1 ĐỀ 3 (H10902)

1. Kiểm tra PDF đề thi, PDF đáp án và MP3.
2. Đọc mã đề và nội dung đáp án.
3. Trích xuất đủ 40 đáp án nếu PDF có text.
4. Render các trang PDF để kiểm tra hình ảnh.
5. Tạo JSON đáp án cho bước tách câu hỏi.

Không sửa SQL Server.
Không thay đổi Đề 1 hoặc Đề 2.
"""

import json
import re
import unicodedata
from pathlib import Path

try:
    import fitz
except ImportError:
    raise SystemExit(
        "Thiếu PyMuPDF. "
        "Chạy: python -m pip install pymupdf"
    )


# ==================================================
# 1. CẤU HÌNH
# ==================================================

ROOT = Path(__file__).resolve().parents[3]

BASE = (
    ROOT / "scripts" / "luyen_thi" / "hsk1"
)

SOURCE = (
    ROOT / "scripts" / "luyen_thi"
    / "source" / "De_HSK" / "HSK1"
)

DATA = BASE / "data" / "de_03"

OUTPUT = BASE / "output" / "de_03"

PREVIEW = OUTPUT / "preview"

MA_DE = "H10902"

PDF_DE = SOURCE / "H10902.pdf"

PDF_DAP_AN = SOURCE / "H10902 答案.pdf"

MP3 = SOURCE / "H10902.mp3"

ANSWER_JSON = DATA / "de_03_dap_an.json"

ANSWER_TEXT = DATA / "de_03_dap_an_goc.txt"

REPORT_JSON = DATA / "de_03_kiem_tra.json"

EXPECTED_ANSWERS = 40


# ==================================================
# 2. CHUẨN HÓA VĂN BẢN
# ==================================================

def normalize_text(text):

    text = unicodedata.normalize(
        "NFKC", text
    )

    text = (
        text.replace("✓", "√")
            .replace("✔", "√")
            .replace("☑", "√")
            .replace("✗", "×")
            .replace("✘", "×")
            .replace("✕", "×")
            .replace("✖", "×")
    )

    return text


# ==================================================
# 3. KIỂM TRA FILE NGUỒN
# ==================================================

def check_sources():

    print("\n========== FILE NGUỒN ==========")

    for path in (
        PDF_DE,
        PDF_DAP_AN,
        MP3
    ):

        if not path.is_file():
            raise FileNotFoundError(
                f"Không tìm thấy: {path}"
            )

        if path.stat().st_size == 0:
            raise ValueError(
                f"File rỗng: {path}"
            )

        print(
            f"OK: {path.name} "
            f"({path.stat().st_size:,} bytes)"
        )


# ==================================================
# 4. ĐỌC PDF ĐÁP ÁN
# ==================================================

def read_answer_pdf():

    with fitz.open(PDF_DAP_AN) as doc:

        pages = [
            page.get_text("text", sort=True)
            for page in doc
        ]

    text = normalize_text(
        "\n".join(pages)
    )

    ANSWER_TEXT.write_text(
        text,
        encoding="utf-8"
    )

    print("\n========== PDF ĐÁP ÁN ==========")

    print("Số ký tự:", len(text))

    return text


# ==================================================
# 5. TRÍCH XUẤT ĐÁP ÁN
# ==================================================

def extract_answers(text):

    """
    Nhận dạng các dòng kiểu:
    1 √
    2 ×
    6 A
    7 B

    Hỗ trợ nhiều cặp số/đáp án trên cùng dòng.

    Không tự đoán nếu không tìm đủ 40 đáp án.
    """

    # Chỉ chấp nhận đáp án A-F, √, ×.
    # Tránh nhận nhầm số trong mã đề hoặc
    # nội dung khác bằng ranh giới số.
    pattern = re.compile(
        r"(?<![0-9A-Za-z])"
        r"(0?[1-9]|[1-3][0-9]|40)"
        r"\s*[\.\)、:：-]?\s*"
        r"([A-Fa-f√×])"
        r"(?![A-Za-z])"
    )

    found = {}

    conflicts = []

    for match in pattern.finditer(text):

        number = int(match.group(1))

        answer = match.group(2).upper()

        if number in found:

            if found[number] != answer:

                conflicts.append({
                    "so_cau": number,
                    "dap_an_cu": found[number],
                    "dap_an_moi": answer
                })

        else:

            found[number] = answer

    # Xác định nhóm đáp án hợp lệ.
    invalid = []

    for number, answer in found.items():

        if number in (
            *range(1, 6),
            *range(21, 26)
        ):

            valid = answer in ("√", "×")

        elif number in (
            *range(6, 11),
            *range(16, 21)
        ):

            valid = answer in "ABC"

        else:

            valid = answer in "ABCDEF"

        if not valid:

            invalid.append({
                "so_cau": number,
                "dap_an": answer
            })

    missing = [
        number
        for number in range(1, 41)
        if number not in found
    ]

    return found, missing, conflicts, invalid


# ==================================================
# 6. RENDER ẢNH PDF
# ==================================================

def render_pdf():

    PREVIEW.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\n========== RENDER PDF ==========")

    with fitz.open(PDF_DE) as doc:

        total_pages = len(doc)

        print("Số trang PDF:", total_pages)

        for index, page in enumerate(doc):

            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False
            )

            filename = (
                PREVIEW
                / f"trang_{index + 1:02d}.png"
            )

            pix.save(str(filename))

            print("Đã tạo:", filename.name)

    return total_pages


# ==================================================
# 7. LƯU BÁO CÁO
# ==================================================

def save_report(
    answers,
    missing,
    conflicts,
    invalid,
    total_pages
):

    report = {
        "ma_de_goc": MA_DE,
        "cap_hsk": 1,
        "ten_hien_thi": "Đề 3",
        "so_trang_pdf": total_pages,
        "so_dap_an_tim_thay": len(answers),
        "cau_thieu": missing,
        "dap_an_mau_thuan": conflicts,
        "dap_an_khong_hop_le": invalid,
        "can_kiem_tra_pdf_goc": True
    }

    REPORT_JSON.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


# ==================================================
# 8. LƯU JSON ĐÁP ÁN
# ==================================================

def save_answers(answers):

    result = {
        "ma_de_goc": MA_DE,
        "cap_hsk": 1,
        "ten_hien_thi": "Đề 3",
        "so_cau": EXPECTED_ANSWERS,
        "dap_an": {
            str(number): answers[number]
            for number in range(1, 41)
        }
    }

    ANSWER_JSON.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


# ==================================================
# 9. HÀM CHÍNH
# ==================================================

def main():

    print("=" * 55)
    print("MỘC HÁN - HSK1 ĐỀ 3 - H10902")
    print("=" * 55)

    DATA.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.mkdir(
        parents=True,
        exist_ok=True
    )

    check_sources()

    text = read_answer_pdf()

    answers, missing, conflicts, invalid = (
        extract_answers(text)
    )

    total_pages = render_pdf()

    save_report(
        answers,
        missing,
        conflicts,
        invalid,
        total_pages
    )

    print("\n========== KIỂM TRA ĐÁP ÁN ==========")

    print(
        "Đã tìm thấy:",
        len(answers),
        "/40"
    )

    print("Câu thiếu:", missing)
    print("Mâu thuẫn:", conflicts)
    print("Không hợp lệ:", invalid)

    if (
        len(answers) != EXPECTED_ANSWERS
        or missing
        or conflicts
        or invalid
    ):

        print(
            "\nChưa tạo JSON đáp án cuối "
            "vì cần kiểm tra PDF gốc."
        )

        print("Văn bản đáp án:", ANSWER_TEXT)
        print("Báo cáo:", REPORT_JSON)

        raise SystemExit(
            "\nCHƯA ĐẠT: Cần kiểm tra cách "
            "trình bày PDF đáp án H10902."
        )

    save_answers(answers)

    print("\n========== HOÀN THÀNH ==========")

    print("Mã đề:", MA_DE)
    print("Tổng đáp án:", len(answers))
    print("PDF:", PDF_DE.name)
    print("MP3:", MP3.name)
    print("JSON:", ANSWER_JSON)
    print("Ảnh xem trước:", PREVIEW)

    print("\nChưa thay đổi SQL Server.")
    print("Chưa tạo JSON nhập SQL.")
    print("Cần đối chiếu đáp án với PDF gốc.")


if __name__ == "__main__":
    main()
