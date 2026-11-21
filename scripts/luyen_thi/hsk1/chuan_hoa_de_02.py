
# -*- coding: utf-8 -*-
"""
MỘC HÁN - CHUẨN HÓA HSK1 ĐỀ 2 (H10901)

Chức năng:
1. Đọc danh sách 40 câu hỏi đã tách từ PDF.
2. Ghép 40 đáp án từ PDF đáp án.
3. Kiểm tra hình ảnh riêng và bảng lựa chọn.
4. Sao chép ảnh vào static/media/luyen_thi/hsk1/de_02.
5. Sao chép MP3 toàn bài thành H10901.mp3.
6. Tự động lấy thời lượng MP3.
7. Tạo de_02.json cho import_de_thi.py.

Không thay đổi SQL Server.
Không thay đổi dữ liệu H10000.
Không chia MP3 thành từng câu.
Không tự duyệt câu hỏi.
"""

import hashlib
import json
import shutil

from pathlib import Path


# ==================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ==================================================

# D:\DATN1
ROOT = Path(__file__).resolve().parents[3]

# scripts/luyen_thi/hsk1
BASE = (
    ROOT
    / "scripts"
    / "luyen_thi"
    / "hsk1"
)

DATA = BASE / "data" / "de_02"

OUTPUT = BASE / "output" / "de_02"

SOURCE = (
    ROOT
    / "scripts"
    / "luyen_thi"
    / "source"
    / "De_HSK"
    / "HSK1"
    / "Đề 2"
)

# Nơi chứa media trên website.
STATIC = (
    ROOT
    / "static"
    / "media"
    / "luyen_thi"
    / "hsk1"
)

# Ảnh Đề 2 nằm riêng, không ảnh hưởng Đề 1.
MEDIA_IMAGES = STATIC / "de_02"

# MP3 nguồn.
AUDIO_SOURCE = (
    SOURCE
    / "Nghe H1 đề 2.mp3"
)

# MP3 dùng trên website.
AUDIO_FILE = STATIC / "H10901.mp3"

# JSON đáp án từ prepare_de_02.py.
ANSWERS_JSON = (
    DATA
    / "de_02_dap_an.json"
)

# JSON hình ảnh từ extract_remaining_de_02.py.
IMAGES_JSON = (
    DATA
    / "hinh_40_cau_ung_vien.json"
)

# JSON hoàn chỉnh cho importer.
FINAL_JSON = DATA / "de_02.json"


# ==================================================
# 2. THÔNG TIN ĐỀ THI
# ==================================================

MA_DE = "H10901"

CAP_HSK = 1

TEN_DE = "Đề 2"

THU_TU = 2

SO_CAU = 40

SO_CAU_NGHE = 20

SO_CAU_DOC = 20

SO_CAU_VIET = 0

# Thời gian luyện cả đề theo cấu hình HSK1
# hiện tại của Mộc Hán.
THOI_GIAN_PHUT = 32


# ==================================================
# 3. ĐỌC FILE JSON
# ==================================================

def load_json(path):

    if not path.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy JSON: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )


# ==================================================
# 4. KIỂM TRA FILE NGUỒN
# ==================================================

def check_source():

    print("\n========== KIỂM TRA NGUỒN ==========")

    required = [
        ANSWERS_JSON,
        IMAGES_JSON,
        AUDIO_SOURCE,
    ]

    for path in required:

        if not path.is_file():
            raise FileNotFoundError(
                f"Thiếu file: {path}"
            )

        if path.stat().st_size == 0:
            raise ValueError(
                f"File rỗng: {path}"
            )

        print("OK:", path.name)


# ==================================================
# 5. KIỂM TRA DANH SÁCH 40 CÂU
# ==================================================

def make_question_map(items):

    if not isinstance(items, list):
        raise ValueError(
            "Danh sách câu hỏi không hợp lệ."
        )

    result = {}

    for item in items:

        if not isinstance(item, dict):
            raise ValueError(
                "Dữ liệu một câu hỏi không hợp lệ."
            )

        number = item.get("so_cau")

        if type(number) is not int:
            raise ValueError(
                "Số câu phải là số nguyên."
            )

        if number in result:
            raise ValueError(
                f"Trùng câu {number}."
            )

        result[number] = item

    if sorted(result) != list(range(1, 41)):
        raise ValueError(
            "Danh sách phải đủ câu 1 đến 40."
        )

    return result


# ==================================================
# 6. KIỂM TRA VÀ ĐỌC 40 ĐÁP ÁN
# ==================================================

def load_answers():

    data = load_json(ANSWERS_JSON)

    if data.get("ma_de_goc") != MA_DE:
        raise ValueError(
            "Mã đề trong JSON đáp án không khớp."
        )

    if data.get("so_cau") != SO_CAU:
        raise ValueError(
            "Số câu trong JSON đáp án không khớp."
        )

    raw_answers = data.get("dap_an")

    if not isinstance(raw_answers, dict):
        raise ValueError(
            "Không tìm thấy danh sách đáp án."
        )

    answers = {}

    for number, value in raw_answers.items():

        question_number = int(number)

        answer = str(value).strip().upper()

        if question_number in answers:
            raise ValueError(
                f"Trùng đáp án câu {question_number}."
            )

        answers[question_number] = answer

    if sorted(answers) != list(range(1, 41)):
        raise ValueError(
            "Đáp án chưa đủ câu 1 đến 40."
        )

    # Hai nhóm câu Đúng/Sai.
    for number in (
        list(range(1, 6))
        + list(range(21, 26))
    ):

        if answers[number] not in ("√", "×"):
            raise ValueError(
                f"Đáp án câu {number} phải là √ hoặc ×."
            )

    # Các câu lựa chọn A-F.
    for number in (
        list(range(6, 21))
        + list(range(26, 41))
    ):

        if answers[number] not in "ABCDEF":
            raise ValueError(
                f"Đáp án câu {number} không hợp lệ."
            )

    # Nghe phần 2 và phần 4 chỉ có A/B/C.
    for number in (
        list(range(6, 11))
        + list(range(16, 21))
    ):

        if answers[number] not in "ABC":
            raise ValueError(
                f"Câu {number} chỉ chấp nhận A/B/C."
            )

    print("\nĐã kiểm tra đủ 40 đáp án.")

    return answers


# ==================================================
# 7. ĐỌC 40 CÂU HỎI ĐÃ TÁCH
# ==================================================

def load_questions():

    data = load_json(IMAGES_JSON)

    if data.get("ma_de_goc") != MA_DE:
        raise ValueError(
            "Mã đề trong JSON hình ảnh không khớp."
        )

    if data.get("so_cau") != SO_CAU:
        raise ValueError(
            "Số câu trong JSON hình ảnh không khớp."
        )

    questions = make_question_map(
        data.get("cau_hoi", [])
    )

    for number in range(1, 41):

        item = questions[number]

        expected_skill = (
            "nghe" if number <= 20 else "doc"
        )

        if item.get("ky_nang") != expected_skill:
            raise ValueError(
                f"Sai kỹ năng ở câu {number}."
            )

        expected_part = (
            (number - 1) // 5 + 1
            if number <= 20
            else (number - 21) // 5 + 1
        )

        if item.get("phan") != expected_part:
            raise ValueError(
                f"Sai phần thi ở câu {number}."
            )

        if not item.get("loai_cau_hoi"):
            raise ValueError(
                f"Thiếu dạng câu hỏi ở câu {number}."
            )

        image = item.get("anh_cau_hoi")

        group = item.get("anh_nhom_lua_chon")

        if not image and not group:
            raise ValueError(
                f"Câu {number} không có hình "
                "hoặc nhóm lựa chọn."
            )

    print("Đã kiểm tra đủ 40 câu hỏi.")

    return questions


# ==================================================
# 8. TÍNH SHA256 FILE
# ==================================================

def sha256(path):

    digest = hashlib.sha256()

    with path.open("rb") as file:

        for block in iter(
            lambda: file.read(65536),
            b""
        ):
            digest.update(block)

    return digest.hexdigest()


# ==================================================
# 9. SAO CHÉP FILE NẾU CẦN
# ==================================================

def copy_if_changed(source, destination):

    if not source.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy: {source}"
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if destination.is_file():

        if sha256(source) == sha256(destination):
            return False

    shutil.copy2(
        source,
        destination
    )

    return True


# ==================================================
# 10. KIỂM TRA ĐƯỜNG DẪN ẢNH
# ==================================================

def check_image_path(relative_path):

    if not isinstance(relative_path, str):
        raise ValueError(
            "Đường dẫn ảnh phải là chuỗi."
        )

    relative = Path(relative_path)

    if (
        relative.is_absolute()
        or ".." in relative.parts
        or len(relative.parts) != 2
        or relative.parts[0] not in (
            "questions",
            "groups"
        )
        or relative.suffix.lower() != ".png"
    ):
        raise ValueError(
            f"Đường dẫn ảnh không hợp lệ: "
            f"{relative_path}"
        )

    return relative


# ==================================================
# 11. KIỂM TRA VÀ CHUẨN BỊ HÌNH ẢNH
# ==================================================

copied_images = set()


def prepare_image(relative_path):

    if not relative_path:
        return None

    relative = check_image_path(
        relative_path
    )

    source = OUTPUT / relative

    if not source.is_file():
        raise FileNotFoundError(
            f"Thiếu ảnh câu hỏi: {source}"
        )

    destination = (
        MEDIA_IMAGES / relative
    )

    copy_if_changed(
        source,
        destination
    )

    copied_images.add(
        relative.as_posix()
    )

    return (
        "/static/media/luyen_thi/"
        "hsk1/de_02/"
        + relative.as_posix()
    )


# ==================================================
# 12. ĐỌC THỜI LƯỢNG MP3
# ==================================================

def get_audio_duration(path):
    """
    Đọc thời lượng thực của file MP3.

    Sử dụng thư viện mutagen.
    Không lấy thời lượng của Đề 1.
    Không tự đoán thời lượng MP3.
    """

    try:
        from mutagen.mp3 import MP3

    except ImportError as error:

        raise RuntimeError(
            "Chưa cài mutagen. "
            "Chạy: python -m pip install mutagen"
        ) from error

    try:
        audio = MP3(str(path))

        duration = round(
            float(audio.info.length),
            2
        )

    except Exception as error:

        raise RuntimeError(
            "Không đọc được thời lượng MP3: "
            f"{path.name}"
        ) from error

    if duration <= 0:
        raise ValueError(
            "Thời lượng MP3 phải lớn hơn 0."
        )

    return duration


# ==================================================
# 13. SAO CHÉP MP3
# ==================================================

def prepare_audio():

    duration = get_audio_duration(
        AUDIO_SOURCE
    )

    STATIC.mkdir(
        parents=True,
        exist_ok=True
    )

    copy_if_changed(
        AUDIO_SOURCE,
        AUDIO_FILE
    )

    url = (
        "/static/media/luyen_thi/"
        "hsk1/H10901.mp3"
    )

    return {
        "duong_dan": url,
        "thoi_luong_giay": duration,
        "che_do_phat": "toan_bai",
    }


# ==================================================
# 14. GHÉP 40 CÂU HỎI HOÀN CHỈNH
# ==================================================

def build_questions(
    answers,
    image_map
):

    questions = []

    for number in range(1, 41):

        item = image_map[number]

        skill = (
            "nghe" if number <= 20 else "doc"
        )

        answer = answers[number]

        image = prepare_image(
            item.get("anh_cau_hoi")
        )

        group = prepare_image(
            item.get("anh_nhom_lua_chon")
        )

        if image is None and group is None:
            raise ValueError(
                f"Câu {number} thiếu nội dung."
            )

        question = {
            "so_cau": number,
            "ky_nang": skill,
            "phan": item["phan"],
            "loai_cau_hoi": item["loai_cau_hoi"],
            "anh_cau_hoi": image,
            "anh_nhom_lua_chon": group,
            "dap_an_dung": answer,
            "da_duyet": False,
        }

        questions.append(question)

    if len(questions) != 40:
        raise ValueError(
            "Danh sách câu hỏi chưa đủ 40."
        )

    return questions


# ==================================================
# 15. TẠO JSON TỔNG HỢP
# ==================================================

def create_final_json(
    questions,
    audio
):

    result = {
        "ma_de_goc": MA_DE,
        "ten_hien_thi": TEN_DE,
        "cap_hsk": CAP_HSK,
        "thu_tu": THU_TU,
        "phien_ban_hsk": "chua_xac_minh",
        "so_cau": SO_CAU,
        "so_cau_nghe": SO_CAU_NGHE,
        "so_cau_doc": SO_CAU_DOC,
        "so_cau_viet": SO_CAU_VIET,
        "thoi_gian_phut": THOI_GIAN_PHUT,
        "audio": audio,
        "trang_thai": "cho_kiem_tra_chua_nhap_sql",
        "cau_hoi": questions,
    }

    DATA.mkdir(
        parents=True,
        exist_ok=True
    )

    FINAL_JSON.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    return result


# ==================================================
# 16. HÀM CHÍNH
# ==================================================

def main():

    print("=" * 50)
    print("MỘC HÁN - CHUẨN HÓA HSK1 ĐỀ 2")
    print("=" * 50)

    # Bước 1: Kiểm tra dữ liệu nguồn.
    check_source()

    # Bước 2: Đọc 40 đáp án.
    answers = load_answers()

    # Bước 3: Đọc 40 câu hỏi.
    image_map = load_questions()

    # Bước 4: Đọc thời lượng MP3 trước
    # khi ghi dữ liệu ra thư mục static.
    duration = get_audio_duration(
        AUDIO_SOURCE
    )

    print("\nThời lượng MP3:", duration)

    # Bước 5: Ghép câu hỏi và sao chép ảnh.
    questions = build_questions(
        answers,
        image_map
    )

    # Bước 6: Sao chép MP3.
    audio = prepare_audio()

    # Bước 7: Tạo JSON tổng hợp.
    result = create_final_json(
        questions,
        audio
    )

    print("\n========== HOÀN THÀNH ==========")

    print("Mã đề:", result["ma_de_goc"])
    print("Tên đề:", result["ten_hien_thi"])
    print("Cấp HSK:", result["cap_hsk"])
    print("Thứ tự đề:", result["thu_tu"])

    print("Tổng câu:", len(questions))
    print("Nghe:", SO_CAU_NGHE)
    print("Đọc:", SO_CAU_DOC)
    print("Viết:", SO_CAU_VIET)

    print(
        "Số ảnh riêng/nhóm:",
        len(copied_images)
    )

    print("MP3:", AUDIO_FILE.name)

    print(
        "Thời lượng MP3:",
        audio["thoi_luong_giay"],
        "giây"
    )

    print(
        "Thời gian thi dự kiến:",
        THOI_GIAN_PHUT,
        "phút"
    )

    print("\nJSON hoàn chỉnh:")
    print(FINAL_JSON)

    print("\nChưa nhập hoặc thay đổi SQL Server.")
    print("Chưa duyệt câu hỏi để xuất bản.")


if __name__ == "__main__":
    main()
