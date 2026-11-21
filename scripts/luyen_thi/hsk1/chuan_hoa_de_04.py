
# -*- coding: utf-8 -*-
"""
MỘC HÁN - CHUẨN HÓA ĐỀ THI HSK1

Mặc định: Đề 3 - H10902

Chức năng:
1. Đọc 40 câu đã tách và 40 đáp án.
2. Kiểm tra 35 ảnh câu riêng, 4 bảng chung.
3. Sao chép ảnh vào static/media.
4. Sao chép MP3 và lấy thời lượng thực tế.
5. Tạo de_03.json để chuẩn bị nhập SQL.

Không tự duyệt hoặc xuất bản đề.
Không thay đổi SQL Server.

Có thể dùng lại cho các đề HSK1 khác
với --ma-de và --de.
"""

import argparse
import hashlib
import json
import re
import shutil

from pathlib import Path, PurePosixPath

try:
    from mutagen.mp3 import MP3
except ImportError:
    raise SystemExit(
        "Thiếu mutagen. "
        "Chạy: python -m pip install mutagen"
    )


# ==================================================
# 1. ĐƯỜNG DẪN CHUNG
# ==================================================

HSK1 = Path(__file__).resolve().parent

BASE = HSK1.parent

ROOT = BASE.parent.parent

SOURCE = (
    BASE / "source" / "De_HSK" / "HSK1"
)

STATIC_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk1"
)


# ==================================================
# 2. CẤU TRÚC 40 CÂU HSK1
# ==================================================

INDIVIDUAL_QUESTIONS = (
    set(range(1, 11))
    | set(range(16, 41))
)

SHARED_GROUPS = {
    "nghe_phan_3": range(11, 16),
    "doc_phan_2": range(26, 31),
    "doc_phan_3": range(31, 36),
    "doc_phan_4": range(36, 41),
}


def skill_and_part(number):

    if number <= 20:
        return "nghe", (number - 1) // 5 + 1

    return "doc", (number - 21) // 5 + 1


def question_type(number):

    if number <= 5 or 21 <= number <= 25:
        return "dung_sai"

    if 11 <= number <= 15:
        return "ghep_hinh_theo_audio"

    if 26 <= number <= 30:
        return "ghep_hinh_theo_noi_dung"

    if number >= 31:
        return "ghep_cap"

    return "chon_mot"


def expected_group(number):

    for name, numbers in SHARED_GROUPS.items():

        if number in numbers:
            return f"groups/{name}.png"

    return None


# ==================================================
# 3. HÀM HỖ TRỢ
# ==================================================

def read_json(path):

    if not path.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy: {path}"
        )

    return json.loads(
        path.read_text(encoding="utf-8-sig")
    )


def normalize_answer(value):

    value = str(value).strip().upper()

    replacements = {
        "X": "×",
        "✗": "×",
        "✘": "×",
        "✕": "×",
        "✖": "×",
        "✓": "√",
        "✔": "√",
    }

    return replacements.get(value, value)


def sha256_file(path):

    digest = hashlib.sha256()

    with path.open("rb") as file:

        for block in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            digest.update(block)

    return digest.hexdigest()


def safe_relative_path(value):

    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError(
            "Đường dẫn ảnh phải là chuỗi."
        )

    value = value.replace("\\", "/").strip()

    path = PurePosixPath(value)

    if (
        path.is_absolute()
        or ".." in path.parts
        or len(path.parts) != 2
        or path.parts[0] not in (
            "questions", "groups"
        )
        or not path.name.endswith(".png")
    ):
        raise ValueError(
            f"Đường dẫn ảnh không hợp lệ: {value}"
        )

    return path.as_posix()


def check_png(path):

    if not path.is_file():
        raise FileNotFoundError(
            f"Thiếu ảnh: {path}"
        )

    if path.stat().st_size < 100:
        raise ValueError(
            f"Ảnh quá nhỏ hoặc rỗng: {path}"
        )

    with path.open("rb") as file:
        signature = file.read(8)

    if signature != b"\x89PNG\r\n\x1a\n":
        raise ValueError(
            f"File không phải PNG hợp lệ: {path}"
        )


# ==================================================
# 4. KIỂM TRA 40 ĐÁP ÁN
# ==================================================

def load_answers(path, ma_de):

    data = read_json(path)

    if data.get("ma_de_goc") != ma_de:
        raise ValueError(
            "Mã đề trong JSON đáp án không khớp."
        )

    raw = data.get("dap_an")

    if not isinstance(raw, dict):
        raise ValueError(
            "JSON đáp án sai cấu trúc."
        )

    answers = {
        int(key): normalize_answer(value)
        for key, value in raw.items()
    }

    if set(answers) != set(range(1, 41)):
        raise ValueError(
            "Phải có đủ 40 đáp án."
        )

    for number, answer in answers.items():

        if number <= 5 or 21 <= number <= 25:
            allowed = {"√", "×"}

        elif 6 <= number <= 10 or 16 <= number <= 20:
            allowed = {"A", "B", "C"}

        else:
            allowed = set("ABCDEF")

        if answer not in allowed:
            raise ValueError(
                f"Câu {number}: đáp án "
                f"'{answer}' không hợp lệ."
            )

    return answers


# ==================================================
# 5. KIỂM TRA DỮ LIỆU CÂU HỎI
# ==================================================

def validate_questions(
    data,
    answers,
    ma_de,
    output_dir
):

    if data.get("ma_de_goc") != ma_de:
        raise ValueError(
            "Mã đề trong JSON hình không khớp."
        )

    raw_questions = data.get("cau_hoi")

    if not isinstance(raw_questions, list):
        raise ValueError(
            "Thiếu danh sách câu hỏi."
        )

    if len(raw_questions) != 40:
        raise ValueError(
            "Số câu hỏi phải là 40."
        )

    numbers = [
        int(item["so_cau"])
        for item in raw_questions
    ]

    if numbers != list(range(1, 41)):
        raise ValueError(
            "Thứ tự câu hỏi phải từ 1 đến 40."
        )

    questions = []
    image_paths = set()

    for item in raw_questions:

        number = int(item["so_cau"])

        skill, part = skill_and_part(number)

        kind = question_type(number)

        if (
            item.get("ky_nang") != skill
            or int(item.get("phan", 0)) != part
            or item.get("loai_cau_hoi") != kind
        ):
            raise ValueError(
                f"Câu {number}: thông tin "
                "kỹ năng, phần hoặc loại câu sai."
            )

        answer = normalize_answer(
            item.get("dap_an_goc", "")
        )

        if answer != answers[number]:
            raise ValueError(
                f"Câu {number}: đáp án "
                "không khớp file đáp án gốc."
            )

        image = safe_relative_path(
            item.get("anh_cau_hoi")
        )

        group = safe_relative_path(
            item.get("anh_nhom_lua_chon")
        )

        # 35 câu có ảnh riêng.
        if number in INDIVIDUAL_QUESTIONS:

            expected_image = (
                f"questions/cau_{number:02d}.png"
            )

            if image != expected_image:
                raise ValueError(
                    f"Câu {number}: thiếu "
                    "hoặc sai ảnh câu hỏi."
                )

        else:

            if image is not None:
                raise ValueError(
                    f"Câu {number}: phần này "
                    "chỉ sử dụng ảnh nhóm."
                )

        # Kiểm tra 4 bảng lựa chọn.
        required_group = expected_group(number)

        if group != required_group:
            raise ValueError(
                f"Câu {number}: "
                "ảnh nhóm không đúng."
            )

        for path in (image, group):

            if path:
                image_paths.add(path)

        questions.append({
            "so_cau": number,
            "ky_nang": skill,
            "phan": part,
            "loai_cau_hoi": kind,
            "anh_cau_hoi": image,
            "anh_nhom_lua_chon": group,
            "dap_an_dung": answer,
            "da_duyet": False,
        })

    # Kiểm tra các file ảnh thực tế.
    for relative in sorted(image_paths):

        file_path = output_dir / relative

        check_png(file_path)

    image_count = sum(
        bool(q["anh_cau_hoi"])
        for q in questions
    )

    group_count = len({
        q["anh_nhom_lua_chon"]
        for q in questions
        if q["anh_nhom_lua_chon"]
    })

    if image_count != 35 or group_count != 4:
        raise ValueError(
            "Phải có 35 ảnh câu riêng "
            "và 4 ảnh nhóm."
        )

    print("Đáp án: 40/40")
    print("Câu hỏi: 40/40")
    print("Ảnh câu riêng:", image_count)
    print("Bảng lựa chọn chung:", group_count)

    return questions, image_paths


# ==================================================
# 6. KIỂM TRA MP3
# ==================================================

def get_mp3_duration(path):

    if not path.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy MP3: {path}"
        )

    if path.stat().st_size == 0:
        raise ValueError(
            "File MP3 rỗng."
        )

    try:
        audio = MP3(str(path))

        duration = round(
            float(audio.info.length), 2
        )

    except Exception as exc:
        raise RuntimeError(
            f"Không đọc được thời lượng MP3: {exc}"
        ) from exc

    if duration <= 0:
        raise ValueError(
            "Thời lượng MP3 không hợp lệ."
        )

    return duration


# ==================================================
# 7. SAO CHÉP MEDIA VÀ KIỂM TRA
# ==================================================

def copy_and_verify(source, destination):

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)

    if sha256_file(source) != sha256_file(destination):
        raise RuntimeError(
            "File sao chép không trùng nội dung: "
            f"{destination}"
        )


def copy_media(
    output_dir,
    image_paths,
    mp3_source,
    ma_de,
    de_folder
):

    media_de = STATIC_ROOT / de_folder

    print(
        "\n========== SAO CHÉP ẢNH =========="
    )

    for relative in sorted(image_paths):

        source = output_dir / relative

        destination = media_de / relative

        copy_and_verify(
            source,
            destination
        )

    print(
        "Đã sao chép:",
        len(image_paths),
        "file PNG"
    )

    audio_destination = (
        STATIC_ROOT / f"{ma_de}.mp3"
    )

    print(
        "\n========== SAO CHÉP MP3 =========="
    )

    copy_and_verify(
        mp3_source,
        audio_destination
    )

    print(
        "Đã sao chép:",
        audio_destination.name
    )


# ==================================================
# 8. CHUYỂN ĐƯỜNG DẪN ẢNH SANG STATIC
# ==================================================

def static_image_path(relative, de_folder):

    if relative is None:
        return None

    return (
        f"/static/media/luyen_thi/hsk1/"
        f"{de_folder}/{relative}"
    )


# ==================================================
# 9. CHƯƠNG TRÌNH CHÍNH
# ==================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Chuẩn hóa HSK1 để chuẩn bị nhập SQL."
        )
    )

    parser.add_argument(
        "--ma-de",
        default="H10902"
    )

    parser.add_argument(
        "--de",
        type=int,
        default=3
    )

    parser.add_argument(
        "--phut",
        type=int,
        default=32,
        help="Thời gian làm bài, mặc định 32 phút."
    )

    args = parser.parse_args()

    ma_de = args.ma_de.strip().upper()

    so_de = args.de

    if not re.fullmatch(r"H\d{5}", ma_de):
        raise ValueError(
            "Mã đề phải có dạng H10902."
        )

    if so_de < 1:
        raise ValueError(
            "Số đề phải lớn hơn 0."
        )

    if not 1 <= args.phut <= 300:
        raise ValueError(
            "Thời gian làm bài không hợp lệ."
        )

    de_folder = f"de_{so_de:02d}"

    data_dir = HSK1 / "data" / de_folder

    output_dir = HSK1 / "output" / de_folder

    mp3_source = SOURCE / f"{ma_de}.mp3"

    answer_file = (
        data_dir / f"{de_folder}_dap_an.json"
    )

    images_file = (
        data_dir / "hinh_40_cau_ung_vien.json"
    )

    result_file = (
        data_dir / f"{de_folder}.json"
    )

    print("=" * 55)
    print("MỘC HÁN - CHUẨN HÓA ĐỀ THI HSK1")
    print("Đề:", so_de)
    print("Mã đề:", ma_de)
    print("=" * 55)

    # ----------------------------------------------
    # 9.1. KIỂM TRA 40 ĐÁP ÁN
    # ----------------------------------------------

    answers = load_answers(
        answer_file,
        ma_de
    )

    # ----------------------------------------------
    # 9.2. KIỂM TRA 40 CÂU VÀ ẢNH
    # ----------------------------------------------

    source_data = read_json(
        images_file
    )

    questions, image_paths = (
        validate_questions(
            source_data,
            answers,
            ma_de,
            output_dir
        )
    )

    # ----------------------------------------------
    # 9.3. KIỂM TRA MP3
    # ----------------------------------------------

    duration = get_mp3_duration(
        mp3_source
    )

    print(
        "\nThời lượng MP3:",
        duration,
        "giây"
    )

    # ----------------------------------------------
    # 9.4. SAO CHÉP MEDIA
    # ----------------------------------------------

    copy_media(
        output_dir,
        image_paths,
        mp3_source,
        ma_de,
        de_folder
    )

    # ----------------------------------------------
    # 9.5. TẠO ĐƯỜNG DẪN STATIC
    # ----------------------------------------------

    final_questions = []

    for item in questions:

        final_item = dict(item)

        final_item["anh_cau_hoi"] = (
            static_image_path(
                item["anh_cau_hoi"],
                de_folder
            )
        )

        final_item["anh_nhom_lua_chon"] = (
            static_image_path(
                item["anh_nhom_lua_chon"],
                de_folder
            )
        )

        final_questions.append(final_item)

    # ----------------------------------------------
    # 9.6. GHÉP JSON CUỐI
    # ----------------------------------------------

    result = {

        "ma_de_goc": ma_de,

        "ten_hien_thi": f"Đề {so_de}",

        "cap_hsk": 1,

        "thu_tu": so_de,

        "phien_ban_hsk": "chua_xac_minh",

        "so_cau": 40,

        "so_cau_nghe": 20,

        "so_cau_doc": 20,

        "so_cau_viet": 0,

        "thoi_gian_phut": args.phut,

        "audio": {

            "duong_dan": (
                "/static/media/luyen_thi/"
                f"hsk1/{ma_de}.mp3"
            ),

            "thoi_luong_giay": duration,

            "che_do_phat": "toan_bai"

        },

        "trang_thai": (
            "cho_kiem_tra_chua_nhap_sql"
        ),

        "cau_hoi": final_questions

    }

    # Ghi file tạm trước để tránh
    # để lại JSON bị ghi dở.

    result_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_file = result_file.with_suffix(
        ".json.tmp"
    )

    temp_file.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    temp_file.replace(
        result_file
    )

    # ----------------------------------------------
    # 9.7. THÔNG BÁO KẾT QUẢ
    # ----------------------------------------------

    print(
        "\n========== HOÀN THÀNH =========="
    )

    print("Mã đề:", ma_de)
    print("Tên hiển thị:", f"Đề {so_de}")
    print("HSK:", 1)

    print("Số câu:", len(final_questions))
    print("Nghe:", 20)
    print("Đọc:", 20)

    print(
        "Thời gian làm bài:",
        args.phut,
        "phút"
    )

    print(
        "Ảnh PNG:",
        len(image_paths)
    )

    print(
        "MP3:",
        f"{ma_de}.mp3"
    )

    print(
        "\nJSON hoàn chỉnh:",
        result_file
    )

    print(
        "\nChưa nhập SQL Server."
    )

    print(
        "Chưa duyệt hoặc xuất bản đề."
    )


if __name__ == "__main__":
    main()
