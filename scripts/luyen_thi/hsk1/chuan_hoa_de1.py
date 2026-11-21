
# -*- coding: utf-8 -*-
"""
MỘC HÁN - CHUẨN HÓA HSK1 ĐỀ 1 (H10000)

Ghép dữ liệu:
1. Câu hỏi và đáp án.
2. Hình ảnh đã tách từ PDF.
3. Audio MP3 toàn bài.

Kiểm tra đủ 40 câu, sao chép ảnh vào static
và tạo một JSON tổng hợp phục vụ nhập SQL.

Không thay đổi SQL Server.
Không chia MP3 thành từng câu.
"""

import hashlib
import json
import shutil
from pathlib import Path


# ==================================================
# 1. ĐƯỜNG DẪN
# ==================================================

ROOT = Path(__file__).resolve().parents[3]

BASE = ROOT / "scripts" / "luyen_thi" / "hsk1"

DATA = BASE / "data" / "de_01"
OUTPUT = BASE / "output" / "de_01"

STATIC = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk1"
)

MEDIA_IMAGES = STATIC / "de_01"
AUDIO_FILE = STATIC / "H10000.mp3"

PREVIEW_JSON = DATA / "preview_de1.json"
IMAGES_JSON = DATA / "hinh_40_cau.json"
AUDIO_JSON = DATA / "audio_de1.json"

FINAL_JSON = DATA / "de_01.json"


# ==================================================
# 2. ĐỌC JSON
# ==================================================

def load_json(path):
    if not path.is_file():
        raise SystemExit(f"Thiếu file: {path}")

    return json.loads(
        path.read_text(encoding="utf-8")
    )


preview = load_json(PREVIEW_JSON)
images = load_json(IMAGES_JSON)
audio = load_json(AUDIO_JSON)

if not AUDIO_FILE.is_file():
    raise SystemExit(
        "Chưa tìm thấy H10000.mp3 trong static."
    )

for data in (preview, images, audio):
    if data.get("ma_de_goc") != "H10000":
        raise SystemExit(
            "Mã đề không khớp H10000."
        )


# ==================================================
# 3. KIỂM TRA DANH SÁCH 40 CÂU
# ==================================================

def make_question_map(items):
    result = {}

    for item in items:
        number = item.get("so_cau")

        if type(number) is not int:
            raise SystemExit("Số câu không hợp lệ.")

        if number in result:
            raise SystemExit(
                f"Trùng câu số {number}."
            )

        result[number] = item

    if sorted(result) != list(range(1, 41)):
        raise SystemExit(
            "Danh sách câu phải đủ từ 1 đến 40."
        )

    return result


answer_map = make_question_map(
    preview["cau_hoi"]
)

image_map = make_question_map(
    images["cau_hoi"]
)

listening = audio.get("cau_nghe", [])

if sorted(
    q["so_cau"] for q in listening
) != list(range(1, 21)):
    raise SystemExit(
        "Audio chưa liên kết đủ 20 câu Nghe."
    )


# ==================================================
# 4. SAO CHÉP HÌNH VÀ TẠO ĐƯỜNG DẪN WEB
# ==================================================

MEDIA_IMAGES.mkdir(
    parents=True,
    exist_ok=True
)

copied = set()


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(
            lambda: file.read(65536),
            b""
        ):
            digest.update(block)

    return digest.digest()


def prepare_image(relative_path):
    if not relative_path:
        return None

    relative = Path(relative_path)

    if (
        relative.is_absolute()
        or ".." in relative.parts
        or relative.suffix.lower() != ".png"
        or relative.parts[0] not in ("questions", "groups")
    ):
        raise SystemExit(
            f"Đường dẫn ảnh không hợp lệ: {relative_path}"
        )

    source = OUTPUT / relative

    if not source.is_file():
        raise SystemExit(
            f"Thiếu ảnh câu hỏi: {source}"
        )

    destination = MEDIA_IMAGES / relative

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if (
        not destination.exists()
        or sha256(source) != sha256(destination)
    ):
        shutil.copy2(source, destination)

    copied.add(relative.as_posix())

    return (
        "/static/media/luyen_thi/hsk1/de_01/"
        + relative.as_posix()
    )


# ==================================================
# 5. GHÉP THÔNG TIN CÂU HỎI
# ==================================================

questions = []

for number in range(1, 41):

    answer_item = answer_map[number]
    image_item = image_map[number]

    skill = "nghe" if number <= 20 else "doc"

    if image_item["ky_nang"] != skill:
        raise SystemExit(
            f"Sai kỹ năng ở câu {number}."
        )

    answer = str(
        answer_item.get("dap_an_goc") or ""
    ).strip()

    if not answer:
        raise SystemExit(
            f"Thiếu đáp án câu {number}."
        )

    image = prepare_image(
        image_item.get("anh_cau_hoi")
    )

    group = prepare_image(
        image_item.get("anh_nhom_lua_chon")
    )

    if image is None and group is None:
        raise SystemExit(
            f"Câu {number} chưa có nội dung hình."
        )

    questions.append({
        "so_cau": number,
        "ky_nang": skill,
        "phan": image_item["phan"],
        "loai_cau_hoi": image_item["loai_cau_hoi"],
        "anh_cau_hoi": image,
        "anh_nhom_lua_chon": group,
        "dap_an_dung": answer,
        "da_duyet": False,
    })


# ==================================================
# 6. DỮ LIỆU ĐỀ THI TỔNG HỢP
#
# JSON này chỉ phục vụ xử lý nội bộ/nhập SQL.
# Không gửi nguyên JSON có đáp án cho người học.
# ==================================================

result = {
    "ma_de_goc": "H10000",
    "ten_hien_thi": "Đề 1",
    "cap_hsk": 1,
    "phien_ban_hsk": "chua_xac_minh",
    "so_cau": 40,
    "so_cau_nghe": 20,
    "so_cau_doc": 20,
    "so_cau_viet": 0,
    "audio": {
        "duong_dan": (
            "/static/media/luyen_thi/"
            "hsk1/H10000.mp3"
        ),
        "thoi_luong_giay": audio["thoi_luong_giay"],
        "che_do_phat": "toan_bai",
    },
    "trang_thai": "cho_kiem_tra_chua_nhap_sql",
    "cau_hoi": questions,
}


# ==================================================
# 7. LƯU JSON
# ==================================================

FINAL_JSON.write_text(
    json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)


# ==================================================
# 8. KẾT QUẢ
# ==================================================

print("\n========== HOÀN THÀNH ==========")
print("HSK1 - Đề 1 - H10000")
print("Tổng câu:", len(questions))
print("Câu Nghe:", 20)
print("Câu Đọc:", 20)
print("Câu Viết:", 0)
print("Ảnh được chuẩn bị:", len(copied))
print("Audio:", AUDIO_FILE.name)
print("Thời lượng:", audio["thoi_luong_giay"])
print("JSON:", FINAL_JSON)
print()
print("Chưa thay đổi SQL Server.")
print("Đáp án chỉ lưu trong JSON nội bộ.")
print("Chưa duyệt nội dung để đưa lên website.")
