
# -*- coding: utf-8 -*-
"""
Mộc Hán - Chuẩn bị audio HSK1 Đề 1.

Đọc MP3 gốc, kiểm tra thời lượng và
tạo JSON liên kết 20 câu Nghe.

Chưa chia audio, chưa thay đổi SQL.
"""

import json
from pathlib import Path

try:
    from mutagen.mp3 import MP3
except ImportError:
    raise SystemExit(
        "Chạy: python -m pip install mutagen"
    )


BASE = Path(__file__).resolve().parents[1]

SOURCE = (
    BASE / "source" / "De_HSK"
    / "HSK1" / "H10000.mp3"
)

DATA = (
    BASE / "hsk1" / "data" / "de_01"
)

QUESTION_JSON = DATA / "hinh_40_cau.json"
OUTPUT_JSON = DATA / "audio_de1.json"


if not SOURCE.is_file():
    raise SystemExit(
        f"Không tìm thấy audio: {SOURCE}"
    )

if not QUESTION_JSON.is_file():
    raise SystemExit(
        "Chưa có hinh_40_cau.json."
    )

questions = json.loads(
    QUESTION_JSON.read_text(encoding="utf-8")
)["cau_hoi"]

listening = sorted(
    [
        q for q in questions
        if q["ky_nang"] == "nghe"
    ],
    key=lambda q: q["so_cau"]
)

if [q["so_cau"] for q in listening] != list(range(1, 21)):
    raise SystemExit(
        "Danh sách câu Nghe chưa đúng 1-20."
    )


audio = MP3(str(SOURCE))
duration = round(audio.info.length, 2)

data = {
    "ma_de_goc": "H10000",
    "cap_hsk": 1,
    "ten_de": "Đề 1",
    "file_audio": "H10000.mp3",
    "thoi_luong_giay": duration,
    "so_cau_nghe": 20,
    "che_do_phat": "toan_bai",
    "moc_thoi_gian_da_xac_minh": False,
    "cau_nghe": []
}

for q in listening:
    data["cau_nghe"].append({
        "so_cau": q["so_cau"],
        "phan": q["phan"],
        "bat_dau_giay": None,
        "ket_thuc_giay": None,
        "da_kiem_tra": False
    })


DATA.mkdir(parents=True, exist_ok=True)

OUTPUT_JSON.write_text(
    json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    ),
    encoding="utf-8"
)

minutes = int(duration // 60)
seconds = int(duration % 60)

print("\n===== HSK1 - DE 1 =====")
print("Audio:", SOURCE.name)
print("Thoi luong:", f"{minutes}:{seconds:02d}")
print("So cau nghe:", len(listening))
print("Da tao:", OUTPUT_JSON)
print("Chua xac dinh moc thoi gian tung cau.")
print("Chua thay doi SQL Server.")
