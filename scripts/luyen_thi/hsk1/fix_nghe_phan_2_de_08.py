
# -*- coding: utf-8 -*-
"""
MỘC HÁN - HSK1 ĐỀ 8 (H11008)

Sửa Nghe hiểu - Phần 2: câu 6-10.

Cách xử lý:
- Đọc trực tiếp PDF H11008.
- Tìm đường kẻ ngang của từng hàng bảng.
- Cắt trọn hình A, B, C và nhãn lựa chọn.
- Không lấy hình của câu bên cạnh.
- Sao lưu 5 ảnh trước khi sửa.
- Cập nhật JSON 40 câu.

Giữ nguyên các câu còn lại.
Không thay đổi SQL Server.
"""

import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import fitz


# ==================================================
# 1. CẤU HÌNH
# ==================================================

HERE = Path(__file__).resolve().parent

PDF_FILE = (
    HERE.parent
    / "source"
    / "De_HSK"
    / "HSK1"
    / "H11008.pdf"
)

DATA = HERE / "data" / "de_08"
OUTPUT = HERE / "output" / "de_08"

QUESTIONS = OUTPUT / "questions"

RESULT_FILE = (
    DATA / "hinh_40_cau_ung_vien.json"
)

BACKUP = (
    DATA / "backup_nghe_phan_2"
)

REPORT_FILE = (
    DATA / "toa_do_nghe_phan_2.json"
)

MA_DE = "H11008"

RENDER_SCALE = 3.0


# ==================================================
# 2. VỊ TRÍ SỐ CÂU ĐÃ KIỂM TRA
#
# Đây là vị trí thực tế từ H11008.pdf,
# không phải tọa độ cắt.
# ==================================================

QUESTION_POSITIONS = {

    6:  (3, 367.2),
    7:  (3, 511.7),
    8:  (3, 656.4),

    9:  (4, 168.0),
    10: (4, 312.5),

}


# ==================================================
# 3. ĐỌC JSON
# ==================================================

def read_json(path):

    if not path.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy: {path}"
        )

    return json.loads(
        path.read_text(encoding="utf-8-sig")
    )


def write_json(path, data):

    temp = path.with_suffix(".json.tmp")

    temp.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    temp.replace(path)


# ==================================================
# 4. TÌM ĐƯỜNG KẺ NGANG TRONG BẢNG
# ==================================================

def find_horizontal_lines(page):

    """
    Phân tích ảnh xám của trang PDF.

    Đường kẻ ngang đi qua gần hết chiều rộng
    bảng sẽ có nhiều pixel tối trên cùng
    một hàng.

    Không dùng OCR và không đoán tọa độ.
    """

    zoom = 2.0

    pix = page.get_pixmap(
        matrix=fitz.Matrix(zoom, zoom),
        colorspace=fitz.csGRAY,
        alpha=False
    )

    pixels = pix.samples
    stride = pix.stride

    # Quét phần bên trong bảng.
    left = int(95 * zoom)
    right = min(
        int(475 * zoom),
        pix.width - 1
    )

    step = 3

    xs = list(range(left, right, step))

    required = int(
        len(xs) * 0.70
    )

    matches = []

    for y in range(
        int(10 * zoom),
        min(int(760 * zoom), pix.height)
    ):

        offset = y * stride

        dark_count = 0

        for x in xs:

            if pixels[offset + x] < 210:
                dark_count += 1

        if dark_count >= required:
            matches.append(y / zoom)

    # Gộp các pixel thuộc cùng một đường kẻ.
    groups = []

    for y in matches:

        if (
            not groups
            or y - groups[-1][-1] > 2.5
        ):
            groups.append([y])
        else:
            groups[-1].append(y)

    lines = [
        round(
            sum(group) / len(group),
            2
        )
        for group in groups
    ]

    return lines


# ==================================================
# 5. LẤY ĐÚNG HÀNG CHỨA MỘT CÂU
# ==================================================

def get_question_rect(
    page,
    question_number,
    label_y,
    lines
):

    """
    Số câu nằm bên trong một hàng bảng.

    Tìm đường kẻ gần nhất phía trên
    và phía dưới số câu.

    Thu nhẹ viền để ảnh gọn,
    nhưng không cắt phần hình hoặc chữ.
    """

    upper_lines = [
        y for y in lines
        if y < label_y - 12
    ]

    lower_lines = [
        y for y in lines
        if y > label_y + 12
    ]

    if not upper_lines or not lower_lines:

        raise RuntimeError(
            f"Câu {question_number}: "
            "không tìm được đủ hai "
            "đường kẻ phân hàng."
        )

    top = max(upper_lines)
    bottom = min(lower_lines)

    row_height = bottom - top

    if not 95 <= row_height <= 220:

        raise RuntimeError(
            f"Câu {question_number}: "
            f"chiều cao hàng {row_height:.1f} "
            "không hợp lệ. "
            "Cần kiểm tra đường kẻ PDF."
        )

    # Bỏ cột số câu ở mép trái.
    # Giữ ba hình cùng nhãn A, B, C.
    rect = fitz.Rect(
        96,
        top + 3,
        505,
        bottom - 3
    ) & page.rect

    if rect.is_empty:
        raise RuntimeError(
            f"Câu {question_number}: "
            "vùng cắt rỗng."
        )

    return rect, top, bottom


# ==================================================
# 6. KIỂM TRA ĐẦU VÀO
# ==================================================

def validate_input():

    if not PDF_FILE.is_file():
        raise FileNotFoundError(
            f"Thiếu PDF: {PDF_FILE}"
        )

    data = read_json(RESULT_FILE)

    if data.get("ma_de_goc") != MA_DE:
        raise ValueError(
            "JSON không thuộc H11008."
        )

    questions = data.get("cau_hoi", [])

    numbers = [
        int(item["so_cau"])
        for item in questions
    ]

    if numbers != list(range(1, 41)):
        raise ValueError(
            "JSON chưa đủ 40 câu liên tục."
        )

    for number in QUESTION_POSITIONS:

        image_file = (
            QUESTIONS
            / f"cau_{number:02d}.png"
        )

        if not image_file.is_file():
            raise FileNotFoundError(
                f"Thiếu ảnh câu {number}"
            )

    return data


# ==================================================
# 7. SAO LƯU
# ==================================================

def backup_files():

    BACKUP.mkdir(
        parents=True,
        exist_ok=True
    )

    json_backup = (
        BACKUP / RESULT_FILE.name
    )

    if not json_backup.exists():
        shutil.copy2(
            RESULT_FILE,
            json_backup
        )

    for number in QUESTION_POSITIONS:

        filename = (
            f"cau_{number:02d}.png"
        )

        source = QUESTIONS / filename
        destination = BACKUP / filename

        if not destination.exists():
            shutil.copy2(
                source,
                destination
            )


# ==================================================
# 8. CHƯƠNG TRÌNH CHÍNH
# ==================================================

def main():

    print("=" * 55)
    print("MỘC HÁN - HSK1 ĐỀ 8")
    print("SỬA NGHE HIỂU PHẦN 2")
    print("=" * 55)

    data = validate_input()

    print(
        "Đã kiểm tra JSON 40 câu."
    )

    # Chỉ sửa sau khi kiểm tra đủ đầu vào.
    plans = {}
    detected_lines = {}

    with fitz.open(PDF_FILE) as document:

        if len(document) != 10:
            raise ValueError(
                "PDF H11008 phải có 10 trang."
            )

        for page_number in (3, 4):

            page = document[
                page_number - 1
            ]

            lines = find_horizontal_lines(page)

            detected_lines[page_number] = lines

            print(
                f"\nTrang {page_number}: "
                f"tìm được {len(lines)} "
                "đường kẻ ngang."
            )

            print(
                "Vị trí:",
                lines
            )

        # Tính vùng cắt 5 câu.
        for number, (
            page_number,
            label_y
        ) in QUESTION_POSITIONS.items():

            page = document[
                page_number - 1
            ]

            rect, top, bottom = get_question_rect(
                page,
                number,
                label_y,
                detected_lines[page_number]
            )

            plans[number] = {
                "trang_pdf": page_number,
                "rect": rect,
                "top": top,
                "bottom": bottom,
            }

            print(
                f"Câu {number:02d}: "
                f"trang {page_number}, "
                f"hàng y={top:.1f}-{bottom:.1f}"
            )

        # Kiểm tra không có hai câu
        # dùng nhầm cùng một hàng.
        for first, second in (
            (6, 7),
            (7, 8),
            (9, 10)
        ):

            a = plans[first]
            b = plans[second]

            if (
                a["trang_pdf"] == b["trang_pdf"]
                and a["top"] == b["top"]
            ):
                raise RuntimeError(
                    "Hai câu bị nhận nhầm "
                    f"cùng hàng: {first}, {second}"
                )

        # Tạo đủ ảnh tạm trước khi ghi đè.
        with TemporaryDirectory(
            prefix="h11004_fix_",
            dir=str(OUTPUT)
        ) as temp_dir:

            temp_dir = Path(temp_dir)

            for number, plan in plans.items():

                page = document[
                    plan["trang_pdf"] - 1
                ]

                destination = (
                    temp_dir
                    / f"cau_{number:02d}.png"
                )

                pix = page.get_pixmap(
                    matrix=fitz.Matrix(
                        RENDER_SCALE,
                        RENDER_SCALE
                    ),
                    clip=plan["rect"],
                    colorspace=fitz.csRGB,
                    alpha=False
                )

                pix.save(str(destination))

                if destination.stat().st_size < 100:
                    raise RuntimeError(
                        f"Ảnh câu {number} không hợp lệ."
                    )

            backup_files()

            # Ghi đè đúng 5 ảnh.
            for number in plans:

                filename = (
                    f"cau_{number:02d}.png"
                )

                shutil.copy2(
                    temp_dir / filename,
                    QUESTIONS / filename
                )

    # ==================================================
    # 9. CẬP NHẬT JSON
    # ==================================================

    by_number = {
        int(item["so_cau"]): item
        for item in data["cau_hoi"]
    }

    report = {
        "ma_de_goc": MA_DE,
        "phuong_phap": "cat_theo_duong_ke_bang",
        "regions": {},
    }

    for number, plan in plans.items():

        rect = plan["rect"]

        item = by_number[number]

        # Chỉ sửa thông tin ảnh.
        # Không động đến đáp án.
        item["trang_pdf"] = plan["trang_pdf"]

        item["anh_cau_hoi"] = (
            f"questions/cau_{number:02d}.png"
        )

        item["vung_cat_pdf"] = [
            round(float(value), 2)
            for value in rect
        ]

        item["da_kiem_tra_hinh"] = False

        report["regions"][str(number)] = {
            "trang_pdf": plan["trang_pdf"],
            "vung_cat_pdf": item["vung_cat_pdf"],
        }

    write_json(
        RESULT_FILE,
        data
    )

    write_json(
        REPORT_FILE,
        report
    )

    print(
        "\n========== HOÀN THÀNH =========="
    )

    print(
        "Đã sửa:",
        "6, 7, 8, 9, 10"
    )

    print(
        "Giữ nguyên 35 câu còn lại."
    )

    print(
        "Giữ nguyên toàn bộ đáp án."
    )

    print(
        "Chưa thay đổi SQL Server."
    )

    print(
        "\nMở lại HTML để kiểm tra ảnh."
    )


if __name__ == "__main__":
    main()
