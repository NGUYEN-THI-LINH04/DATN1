
# -*- coding: utf-8 -*-
"""
MỘC HÁN - CHUẨN BỊ ĐỀ THI HSK1

Mặc định:
    Đề 4 - H11003

Chức năng:
1. Kiểm tra PDF đề, PDF đáp án, MP3.
2. Tự tìm file PDF đáp án theo mã đề.
3. Trích xuất và kiểm tra 40 đáp án.
4. Render toàn bộ trang PDF thành PNG.
5. Tạo JSON đáp án và báo cáo kiểm tra.

Dùng lại cho đề HSK1 khác bằng:
    --ma-de H11004 --de 5

Không sửa SQL Server.
Không thay đổi dữ liệu các đề trước.
"""

import argparse
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
# 1. ĐƯỜNG DẪN CHUNG
# ==================================================

HSK1 = Path(__file__).resolve().parent

SOURCE = (
    HSK1.parent
    / "source"
    / "De_HSK"
    / "HSK1"
)

RENDER_SCALE = 2.0


# ==================================================
# 2. HÀM CHUẨN HÓA
# ==================================================

def normalize_text(text):

    text = unicodedata.normalize(
        "NFKC",
        text
    )

    replacements = {
        "✓": "√",
        "✔": "√",
        "☑": "√",
        "✗": "×",
        "✘": "×",
        "✕": "×",
        "✖": "×",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# ==================================================
# 3. TÌM FILE PDF ĐÁP ÁN
# ==================================================

def find_answer_pdf(ma_de):

    if not SOURCE.is_dir():
        raise FileNotFoundError(
            f"Không tìm thấy thư mục: {SOURCE}"
        )

    candidates = []

    for path in SOURCE.iterdir():

        if not path.is_file():
            continue

        if path.suffix.lower() != ".pdf":
            continue

        if not path.name.startswith(ma_de):
            continue

        if (
            "答案" in path.stem
            or "答" in path.stem
        ):
            candidates.append(path)

    if not candidates:
        raise FileNotFoundError(
            f"Không tìm thấy PDF đáp án "
            f"của {ma_de} trong {SOURCE}"
        )

    if len(candidates) > 1:
        names = "\n".join(
            f"- {path.name}"
            for path in candidates
        )

        raise ValueError(
            "Tìm thấy nhiều PDF đáp án. "
            "Cần kiểm tra để tránh lấy nhầm:\n"
            + names
        )

    return candidates[0]


# ==================================================
# 4. KIỂM TRA FILE NGUỒN
# ==================================================

def check_file(path):

    if not path.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy: {path}"
        )

    size = path.stat().st_size

    if size <= 0:
        raise ValueError(
            f"File rỗng: {path}"
        )

    print(
        f"OK: {path.name} "
        f"({size:,} bytes)"
    )


# ==================================================
# 5. TRÍCH TEXT PDF ĐÁP ÁN
# ==================================================

def read_answer_pdf(pdf_path):

    with fitz.open(pdf_path) as doc:

        texts = []

        for page in doc:

            texts.append(
                page.get_text(
                    "text",
                    sort=True
                )
            )

        page_count = len(doc)

    text = normalize_text(
        "\n".join(texts)
    )

    return text, page_count


# ==================================================
# 6. TÁCH 40 ĐÁP ÁN
# ==================================================

def extract_answers(text):

    """
    Nhận dạng đáp án kiểu:

        1 √
        2 ×
        6 A
        7 B

    Hỗ trợ nhiều cặp số - đáp án
    trên cùng một dòng.

    Không tự điền đáp án bị thiếu.
    """

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

        number = int(
            match.group(1)
        )

        answer = (
            match.group(2).upper()
        )

        if number in found:

            if found[number] != answer:

                conflicts.append({
                    "so_cau": number,
                    "dap_an_cu": found[number],
                    "dap_an_moi": answer,
                })

        else:

            found[number] = answer

    missing = [
        number
        for number in range(1, 41)
        if number not in found
    ]

    invalid = []

    for number, answer in found.items():

        if (
            1 <= number <= 5
            or 21 <= number <= 25
        ):
            allowed = {"√", "×"}

        elif (
            6 <= number <= 10
            or 16 <= number <= 20
        ):
            allowed = set("ABC")

        else:
            allowed = set("ABCDEF")

        if answer not in allowed:

            invalid.append({
                "so_cau": number,
                "dap_an": answer,
            })

    return (
        found,
        missing,
        conflicts,
        invalid
    )


# ==================================================
# 7. RENDER CÁC TRANG PDF
# ==================================================

def render_pdf(
    pdf_path,
    preview_dir
):

    preview_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "\n========== RENDER PDF =========="
    )

    with fitz.open(pdf_path) as doc:

        total_pages = len(doc)

        if total_pages == 0:
            raise ValueError(
                "PDF đề thi không có trang."
            )

        print(
            "Số trang PDF:",
            total_pages
        )

        for index, page in enumerate(doc):

            filename = (
                preview_dir
                / f"trang_{index + 1:02d}.png"
            )

            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(
                    RENDER_SCALE,
                    RENDER_SCALE
                ),
                colorspace=fitz.csRGB,
                alpha=False
            )

            pixmap.save(
                str(filename)
            )

            print(
                "Đã tạo:",
                filename.name
            )

    return total_pages


# ==================================================
# 8. HÀM LƯU JSON
# ==================================================

def save_json(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_path = path.with_suffix(
        path.suffix + ".tmp"
    )

    temp_path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    temp_path.replace(path)


# ==================================================
# 9. CHƯƠNG TRÌNH CHÍNH
# ==================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Chuẩn bị PDF và đáp án HSK1."
        )
    )

    parser.add_argument(
        "--ma-de",
        default="H11003",
        help="Mã đề gốc."
    )

    parser.add_argument(
        "--de",
        type=int,
        default=4,
        help="Số thứ tự đề."
    )

    args = parser.parse_args()

    ma_de = args.ma_de.strip().upper()
    so_de = args.de

    if not re.fullmatch(
        r"H\d{5}",
        ma_de
    ):
        raise ValueError(
            "Mã đề không đúng định dạng."
        )

    if so_de < 1:
        raise ValueError(
            "Số đề phải lớn hơn 0."
        )

    folder_name = (
        f"de_{so_de:02d}"
    )

    data_dir = (
        HSK1 / "data" / folder_name
    )

    output_dir = (
        HSK1 / "output" / folder_name
    )

    preview_dir = (
        output_dir / "preview"
    )

    pdf_de = (
        SOURCE / f"{ma_de}.pdf"
    )

    mp3 = (
        SOURCE / f"{ma_de}.mp3"
    )

    pdf_dap_an = find_answer_pdf(
        ma_de
    )

    answer_json = (
        data_dir
        / f"{folder_name}_dap_an.json"
    )

    answer_text = (
        data_dir
        / f"{folder_name}_dap_an_goc.txt"
    )

    report_json = (
        data_dir
        / f"{folder_name}_kiem_tra.json"
    )

    print("=" * 55)

    print(
        f"MỘC HÁN - HSK1 ĐỀ {so_de}"
    )

    print(
        "Mã đề:", ma_de
    )

    print("=" * 55)

    # ----------------------------------------------
    # 9.1. KIỂM TRA FILE NGUỒN
    # ----------------------------------------------

    print(
        "\n========== FILE NGUỒN =========="
    )

    for path in (
        pdf_de,
        pdf_dap_an,
        mp3
    ):
        check_file(path)

    data_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # ----------------------------------------------
    # 9.2. ĐỌC ĐÁP ÁN
    # ----------------------------------------------

    text, answer_pages = (
        read_answer_pdf(pdf_dap_an)
    )

    answer_text.write_text(
        text,
        encoding="utf-8"
    )

    print(
        "\n========== PDF ĐÁP ÁN =========="
    )

    print(
        "Số trang:",
        answer_pages
    )

    print(
        "Số ký tự:",
        len(text)
    )

    # ----------------------------------------------
    # 9.3. KIỂM TRA 40 ĐÁP ÁN
    # ----------------------------------------------

    (
        answers,
        missing,
        conflicts,
        invalid
    ) = extract_answers(text)

    # ----------------------------------------------
    # 9.4. RENDER ĐỀ THI
    # ----------------------------------------------

    page_count = render_pdf(
        pdf_de,
        preview_dir
    )

    # ----------------------------------------------
    # 9.5. LƯU BÁO CÁO
    # ----------------------------------------------

    report = {
        "ma_de_goc": ma_de,
        "ten_de": f"Đề {so_de}",
        "cap_hsk": 1,
        "pdf_de": pdf_de.name,
        "pdf_dap_an": pdf_dap_an.name,
        "mp3": mp3.name,
        "so_trang_pdf": page_count,
        "so_dap_an_tim_thay": len(answers),
        "cau_thieu": missing,
        "dap_an_mau_thuan": conflicts,
        "dap_an_khong_hop_le": invalid,
        "da_kiem_tra_pdf_goc": False,
    }

    save_json(
        report_json,
        report
    )

    print(
        "\n========== KIỂM TRA ĐÁP ÁN =========="
    )

    print(
        "Đã tìm thấy:",
        len(answers),
        "/40"
    )

    print(
        "Câu thiếu:",
        missing
    )

    print(
        "Mâu thuẫn:",
        conflicts
    )

    print(
        "Không hợp lệ:",
        invalid
    )

    # ----------------------------------------------
    # 9.6. CHỈ TẠO JSON NẾU ĐỦ 40
    # ----------------------------------------------

    if (
        len(answers) != 40
        or missing
        or conflicts
        or invalid
    ):

        print(
            "\nCHƯA ĐẠT: "
            "Cần kiểm tra PDF đáp án."
        )

        print(
            "Văn bản đáp án:",
            answer_text
        )

        print(
            "Báo cáo:",
            report_json
        )

        raise SystemExit(1)

    result = {
        "ma_de_goc": ma_de,
        "cap_hsk": 1,
        "ten_hien_thi": f"Đề {so_de}",
        "so_cau": 40,
        "dap_an": {
            str(number): answers[number]
            for number in range(1, 41)
        }
    }

    save_json(
        answer_json,
        result
    )

    # ----------------------------------------------
    # 9.7. KẾT QUẢ
    # ----------------------------------------------

    print(
        "\n========== HOÀN THÀNH =========="
    )

    print(
        "Mã đề:", ma_de
    )

    print(
        "Tổng đáp án:",
        len(answers)
    )

    print(
        "PDF:",
        pdf_de.name
    )

    print(
        "MP3:",
        mp3.name
    )

    print(
        "JSON đáp án:",
        answer_json
    )

    print(
        "Ảnh PDF:",
        preview_dir
    )

    print(
        "\nChưa tách ảnh từng câu."
    )

    print(
        "Chưa thay đổi SQL Server."
    )


if __name__ == "__main__":
    main()
