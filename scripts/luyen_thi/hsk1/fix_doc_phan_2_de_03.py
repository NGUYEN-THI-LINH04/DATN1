
# -*- coding: utf-8 -*-
"""
MỘC HÁN - HSK1 ĐỀ 3 (H10902)
SỬA ẢNH ĐỌC HIỂU PHẦN 2: CÂU 26-30

Đã xác định vùng cắt từ ảnh trang 8 PDF gốc.

Lưu ý:
- PDF gốc in nhầm số câu 29 thành 28.
- Khi lưu dữ liệu vẫn đánh số 26, 27, 28, 29, 30.
- Bỏ số câu in trên PDF vì HTML đã có tiêu đề.
- Không sửa 35 câu còn lại.
- Không sửa 4 bảng lựa chọn chung.
- Không sửa đáp án.
- Không nhập SQL Server.
"""

import json
import shutil

from pathlib import Path
from tempfile import TemporaryDirectory

import fitz


# ==================================================
# 1. CẤU HÌNH
# ==================================================

HSK1 = Path(__file__).resolve().parent

PDF_FILE = (
    HSK1.parent
    / "source"
    / "De_HSK"
    / "HSK1"
    / "H10902.pdf"
)

DATA = HSK1 / "data" / "de_03"

OUTPUT = HSK1 / "output" / "de_03"

QUESTIONS = OUTPUT / "questions"

JSON_FILE = (
    DATA / "hinh_40_cau_ung_vien.json"
)

CONFIG_FILE = (
    DATA / "toa_do_doc_phan_2.json"
)

BACKUP = (
    DATA / "sao_luu_truoc_sua_doc_phan_2"
)

MA_DE = "H10902"

PAGE_NUMBER = 8

RENDER_SCALE = 3.0


# ==================================================
# 2. TỌA ĐỘ ĐÃ ĐỐI CHIẾU VỚI TRANG 8
# ==================================================

# Hệ tọa độ tham chiếu 595 x 842.
#
# Phần bên trái được thu vào để loại bỏ
# số thứ tự in sẵn trên PDF.
#
# Giữ nguyên pinyin, chữ Hán và ô trả lời.
#
# (trang, x0, y0, x1, y1)

REGIONS = {

    26: (8, 110, 560, 510, 597),

    27: (8, 110, 598, 510, 632),

    28: (8, 110, 633, 510, 665),

    # PDF in nhầm dòng này thành câu 28.
    # Trong hệ thống đây vẫn là câu 29.
    29: (8, 110, 666, 510, 699),

    30: (8, 110, 700, 510, 738),

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
        path.read_text(
            encoding="utf-8-sig"
        )
    )


# ==================================================
# 4. KIỂM TRA ĐẦU VÀO
# ==================================================

def validate_input():

    if not PDF_FILE.is_file():

        raise FileNotFoundError(
            f"Thiếu PDF: {PDF_FILE}"
        )

    data = read_json(
        JSON_FILE
    )

    if data.get("ma_de_goc") != MA_DE:

        raise ValueError(
            "JSON không phải đề H10902."
        )

    questions = data.get(
        "cau_hoi", []
    )

    if (
        len(questions) != 40
        or [
            int(item["so_cau"])
            for item in questions
        ] != list(range(1, 41))
    ):

        raise ValueError(
            "JSON phải chứa đủ "
            "40 câu theo đúng thứ tự."
        )

    if not QUESTIONS.is_dir():

        raise FileNotFoundError(
            f"Thiếu thư mục ảnh: {QUESTIONS}"
        )

    for number in REGIONS:

        image_file = (
            QUESTIONS
            / f"cau_{number:02d}.png"
        )

        if not image_file.is_file():

            raise FileNotFoundError(
                f"Thiếu ảnh câu {number}: "
                f"{image_file}"
            )

    return data


# ==================================================
# 5. QUY ĐỔI TỌA ĐỘ
# ==================================================

def to_pdf_rect(page, region):

    _, x0, y0, x1, y1 = region

    scale_x = (
        page.rect.width / 595.0
    )

    scale_y = (
        page.rect.height / 842.0
    )

    rect = fitz.Rect(

        x0 * scale_x,

        y0 * scale_y,

        x1 * scale_x,

        y1 * scale_y

    ) & page.rect

    if (
        rect.is_empty
        or rect.width < 30
        or rect.height < 20
    ):

        raise ValueError(
            f"Vùng cắt không hợp lệ: {region}"
        )

    return rect


# ==================================================
# 6. SAO LƯU KẾT QUẢ CŨ
# ==================================================

def backup_old_files():

    BACKUP.mkdir(
        parents=True,
        exist_ok=True
    )

    json_backup = (
        BACKUP
        / "hinh_40_cau_ung_vien.json"
    )

    if not json_backup.exists():

        shutil.copy2(
            JSON_FILE,
            json_backup
        )

    for number in REGIONS:

        filename = (
            f"cau_{number:02d}.png"
        )

        original = (
            QUESTIONS / filename
        )

        backup_file = (
            BACKUP / filename
        )

        if not backup_file.exists():

            shutil.copy2(
                original,
                backup_file
            )

    print(
        "Đã sao lưu 5 ảnh cũ và JSON."
    )


# ==================================================
# 7. LƯU CẤU HÌNH ĐỂ TÁI SỬ DỤNG
# ==================================================

def save_config():

    config = {

        "ma_de_goc": MA_DE,

        "ghi_chu": (
            "Tọa độ câu 26-30 đã đối chiếu "
            "với preview trang 8. "
            "PDF in nhầm câu 29 thành 28."
        ),

        "regions": {

            str(number): list(region)

            for number, region
            in REGIONS.items()

        },

        "shared": {}

    }

    CONFIG_FILE.write_text(

        json.dumps(
            config,
            ensure_ascii=False,
            indent=2
        ),

        encoding="utf-8"

    )


# ==================================================
# 8. CẮT LẠI 5 CÂU
# ==================================================

def main():

    print("=" * 55)

    print(
        "MỘC HÁN - H10902"
    )

    print(
        "SỬA ĐỌC HIỂU PHẦN 2"
    )

    print("=" * 55)

    data = validate_input()

    by_number = {

        int(item["so_cau"]): item

        for item in data["cau_hoi"]

    }

    # Lưu ảnh cũ để có thể khôi phục.
    backup_old_files()

    print(
        "\n========== CẮT LẠI 5 CÂU =========="
    )

    # Tạo ảnh tạm trước.
    # Nếu có lỗi, ảnh cũ chưa bị ghi đè.

    with TemporaryDirectory(
        prefix="h10902_doc2_",
        dir=str(OUTPUT)
    ) as temp_dir:

        temp_path = Path(
            temp_dir
        )

        prepared = {}

        with fitz.open(
            PDF_FILE
        ) as document:

            if len(document) < PAGE_NUMBER:

                raise ValueError(
                    "PDF không đủ 8 trang."
                )

            page = document[
                PAGE_NUMBER - 1
            ]

            for number, region in (
                REGIONS.items()
            ):

                rect = to_pdf_rect(
                    page,
                    region
                )

                filename = (
                    f"cau_{number:02d}.png"
                )

                temp_image = (
                    temp_path / filename
                )

                pixmap = page.get_pixmap(

                    matrix=fitz.Matrix(
                        RENDER_SCALE,
                        RENDER_SCALE
                    ),

                    clip=rect,

                    colorspace=fitz.csRGB,

                    alpha=False

                )

                pixmap.save(
                    str(temp_image)
                )

                prepared[number] = (
                    temp_image,
                    rect
                )

                print(
                    f"Đã chuẩn bị câu {number:02d}"
                )

        # Tất cả vùng cắt đã tạo thành công.
        # Chỉ thay thế đúng 5 ảnh.

        for number, (
            temp_image,
            rect
        ) in prepared.items():

            final_image = (

                QUESTIONS
                / f"cau_{number:02d}.png"

            )

            temp_image.replace(
                final_image
            )

            item = by_number[
                number
            ]

            # Chỉ cập nhật thông tin hình ảnh.
            # Giữ nguyên đáp án, loại câu,
            # kỹ năng và phần thi.

            item["trang_pdf"] = PAGE_NUMBER

            item["anh_cau_hoi"] = (
                f"questions/cau_{number:02d}.png"
            )

            item["vung_cat_pdf"] = [

                round(float(value), 2)

                for value in rect

            ]

            item["da_kiem_tra_hinh"] = False

            print(
                f"Đã cập nhật câu {number:02d}"
            )

    # ==================================================
    # 9. LƯU JSON 40 CÂU
    # ==================================================

    # Không thay đổi các câu khác.

    temp_json = (
        DATA / "_hinh_40_cau_tam.json"
    )

    temp_json.write_text(

        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),

        encoding="utf-8"

    )

    temp_json.replace(
        JSON_FILE
    )

    # Lưu tọa độ mới để nếu cần chạy lại
    # file extract_remaining_de_03.py,
    # có thể sử dụng tham số --config.

    save_config()

    print(
        "\n========== HOÀN THÀNH =========="
    )

    print(
        "Đề:", MA_DE
    )

    print(
        "Đã sửa các câu:",
        list(REGIONS)
    )

    print(
        "Tổng câu trong JSON:",
        len(data["cau_hoi"])
    )

    print(
        "JSON:", JSON_FILE
    )

    print(
        "Cấu hình:", CONFIG_FILE
    )

    print(
        "Sao lưu:", BACKUP
    )

    print(
        "\nGiữ nguyên 35 câu khác."
    )

    print(
        "Giữ nguyên 4 bảng lựa chọn."
    )

    print(
        "Giữ nguyên 40 đáp án."
    )

    print(
        "HTML hiện tại có thể mở lại "
        "để xem các ảnh mới."
    )

    print(
        "\nChưa thay đổi SQL Server."
    )


if __name__ == "__main__":
    main()
