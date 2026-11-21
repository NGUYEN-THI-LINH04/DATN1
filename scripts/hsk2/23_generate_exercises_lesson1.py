
"""
BUOC 23 - TAO BAN NHAP 20 CAU HOI HSK2 BAI 1

Dau vao:
 exercise_hsk2_lesson1_source.json

Dau ra:
 exercise_hsk2_lesson1_preview.json

CHI TAO JSON - KHONG GHI SQL.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "scripts" / "hsk2" / "data" / "processed"

SOURCE_FILE = DATA_DIR / "exercise_hsk2_lesson1_source.json"
OUTPUT_FILE = DATA_DIR / "exercise_hsk2_lesson1_preview.json"

questions = []


def add_choice(group, content, correct, wrong, explanation,
               source_type, source_value):
    """Them cau trac nghiem mot dap an."""
    if len(wrong) != 3 or correct in wrong:
        raise ValueError("Lua chon khong hop le")

    if len(set([correct] + wrong)) != 4:
        raise ValueError("Cac lua chon bi trung")

    # Phan bo vi tri dap an dung luan phien
    position = len(questions) % 4
    options = list(wrong)
    options.insert(position, correct)

    questions.append({
        "LoaiCauHoi": "chon_mot",
        "KyNang": "doc",
        "NhomKienThuc": group,
        "NoiDungCauHoi": content,
        "DapAnJson": None,
        "GiaiThich": explanation,
        "DiemToiDa": 1,
        "ThuTu": len(questions) + 1,
        "NguonLoai": source_type,
        "NguonGiaTri": source_value,
        "LuaChon": [
            {
                "NoiDungLuaChon": option,
                "LaDapAnDung": option == correct,
                "ThuTu": index + 1
            }
            for index, option in enumerate(options)
        ]
    })


def add_fill(content, answer, explanation, grammar):
    """Them cau dien tu."""
    questions.append({
        "LoaiCauHoi": "dien_tu",
        "KyNang": "doc",
        "NhomKienThuc": "ngu_phap",
        "NoiDungCauHoi": content,
        "DapAnJson": {"answers": [answer]},
        "GiaiThich": explanation,
        "DiemToiDa": 1,
        "ThuTu": len(questions) + 1,
        "NguonLoai": "ngu_phap",
        "NguonGiaTri": grammar,
        "LuaChon": []
    })


def build_questions():
    # ===== 12 CAU TU VUNG =====

    vocab = [
        (
            "半夜", "nửa đêm",
            ["buổi trưa", "buổi sáng", "tuần sau"]
        ),
        (
            "多久", "bao lâu",
            ["lúc nào", "tuần trước", "một lát"]
        ),
        (
            "经常", "thường xuyên",
            ["hiếm khi", "vừa nãy", "ngày mai"]
        ),
        (
            "上周", "tuần trước",
            ["tuần sau", "buổi sáng", "mỗi ngày"]
        ),
        (
            "下周", "tuần sau",
            ["tuần trước", "nửa đêm", "vừa nãy"]
        ),
        (
            "午睡", "ngủ trưa",
            ["tắm", "chờ đợi", "sống"]
        ),
        (
            "洗澡", "tắm",
            ["ngủ trưa", "đợi", "học"]
        ),
        (
            "早晨", "buổi sáng sớm",
            ["nửa đêm", "buổi tối", "tuần trước"]
        ),
        (
            "随时", "bất kỳ lúc nào",
            ["tuần sau", "lúc đó", "một lát"]
        ),
        (
            "习惯", "thói quen",
            ["tuần lễ", "phút", "đêm khuya"]
        ),
        (
            "一会儿", "một lát",
            ["cả tuần", "nửa đêm", "một năm"]
        ),
        (
            "晚安", "chúc ngủ ngon",
            ["chào buổi sáng", "cảm ơn", "tạm biệt"]
        ),
    ]

    for word, meaning, wrong in vocab:
        add_choice(
            "tu_vung",
            f"Từ “{word}” có nghĩa là gì?",
            meaning,
            wrong,
            f"“{word}” có nghĩa là “{meaning}”.",
            "tu_vung",
            word
        )

    # ===== 4 CAU CHU HAN =====

    hanzi_data = [
        ("夜", "yè", ["yě", "yuè", "yī"]),
        ("久", "jiǔ", ["jiù", "jǐ", "jiā"]),
        ("钟", "zhōng", ["zhòng", "zōng", "chōng"]),
        ("晨", "chén", ["chěn", "chéng", "chēn"])
    ]

    for character, pinyin, wrong in hanzi_data:
        add_choice(
            "chu_han",
            f"Pinyin đúng của chữ “{character}” là gì?",
            pinyin,
            wrong,
            f"Chữ “{character}” đọc là {pinyin}.",
            "chu_han",
            character
        )

    # ===== 2 CAU TRAC NGHIEM NGU PHAP =====

    add_choice(
        "ngu_phap",
        "Cấu trúc 先……再…… dùng để diễn đạt điều gì?",
        "Thứ tự thực hiện hai hành động",
        [
            "So sánh hai người",
            "Hỏi về số lượng",
            "Diễn tả sự sở hữu"
        ],
        "先……再…… diễn tả làm hành động "
        "thứ nhất trước, sau đó làm hành động thứ hai.",
        "ngu_phap",
        "先……再……"
    )

    add_choice(
        "ngu_phap",
        "Cấu trúc 每……都…… diễn tả ý nghĩa nào?",
        "Mỗi đối tượng đều có chung đặc điểm hoặc hành động",
        [
            "Một hành động sắp xảy ra",
            "Một việc chưa hoàn thành",
            "Hai hành động đối lập"
        ],
        "每……都…… biểu thị tất cả các thành viên "
        "trong phạm vi được nói đến đều có chung "
        "đặc điểm hoặc hành động.",
        "ngu_phap",
        "每……都……"
    )

    # ===== 2 CAU DIEN TU NGU PHAP =====

    add_fill(
        "Điền một chữ Hán vào chỗ trống:\n"
        "我们先吃饭，___去看电影。",
        "再",
        "Câu đầy đủ: 我们先吃饭，再去看电影。\n"
        "Nghĩa: Chúng ta ăn cơm trước, "
        "sau đó đi xem phim.",
        "先……再……"
    )

    add_fill(
        "Điền một chữ Hán vào chỗ trống:\n"
        "每个学生___来了。",
        "都",
        "Câu đầy đủ: 每个学生都来了。\n"
        "Nghĩa: Mỗi học sinh đều đã đến.",
        "每……都……"
    )


def validate(source):
    lesson = source["lesson"]

    if lesson["MaKhoaHoc"] != 2:
        raise ValueError("Khong phai khoa HSK2")

    if lesson["SoThuTuBai"] != 1:
        raise ValueError("Khong phai bai 1")

    if source["existing_exercises"]:
        raise ValueError(
            "Bai 1 da co bai tap. Dung de kiem tra trung lap."
        )

    vocab_set = {
        item["ChuHan"]
        for item in source["vocabulary"]
    }

    hanzi_map = {
        item["KyTu"]: item["Pinyin"]
        for item in source["hanzi"]
    }

    grammar_names = [
        item["TenCauTruc"]
        for item in source["grammar"]
    ]

    if len(questions) != 20:
        raise ValueError("So cau hoi khong bang 20")

    for q in questions:
        kind = q["NguonLoai"]
        value = q["NguonGiaTri"]

        if kind == "tu_vung" and value not in vocab_set:
            raise ValueError(f"Tu ngoai bai: {value}")

        if kind == "chu_han":
            if value not in hanzi_map:
                raise ValueError(f"Chu ngoai bai: {value}")

            correct = next(
                x["NoiDungLuaChon"]
                for x in q["LuaChon"]
                if x["LaDapAnDung"]
            )

            if correct != hanzi_map[value]:
                raise ValueError(
                    f"Sai Pinyin: {value}"
                )

        if kind == "ngu_phap":
            normalized = value.replace("……", "")
            matched = any(
                normalized in name.replace("……", "")
                for name in grammar_names
            )
            if not matched:
                raise ValueError(
                    f"Ngu phap ngoai bai: {value}"
                )

        if q["LoaiCauHoi"] == "chon_mot":
            if len(q["LuaChon"]) != 4:
                raise ValueError("Trac nghiem thieu lua chon")

            count_correct = sum(
                x["LaDapAnDung"]
                for x in q["LuaChon"]
            )
            if count_correct != 1:
                raise ValueError("Dap an dung khong hop le")

        elif q["LoaiCauHoi"] == "dien_tu":
            if not q["DapAnJson"]["answers"]:
                raise ValueError("Cau dien tu thieu dap an")

    if len({
        q["NoiDungCauHoi"]
        for q in questions
    }) != 20:
        raise ValueError("Co cau hoi trung lap")


def main():
    print("=" * 65)
    print("BUOC 23 - TAO BAN NHAP BAI TAP HSK2 BAI 1")
    print("=" * 65)

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(SOURCE_FILE)

    with open(SOURCE_FILE, encoding="utf-8") as file:
        source = json.load(file)

    build_questions()
    validate(source)

    output = {
        "MaKhoaHoc": 2,
        "MaBaiHoc": source["lesson"]["MaBaiHoc"],
        "TieuDe": (
            "Bài luyện tập Bài 1 - "
            + source["lesson"]["TieuDe"]
        ),
        "HuongDan": (
            "Hoàn thành các câu hỏi về từ vựng, "
            "ngữ pháp và chữ Hán của Bài 1."
        ),
        "ThoiGianGioiHanGiay": 900,
        "PhanTramDat": 70,
        "TrangThai": "ban_nhap",
        "SoCauHoi": len(questions),
        "CauHoi": questions
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE, "w", encoding="utf-8"
    ) as file:
        json.dump(
            output, file,
            ensure_ascii=False,
            indent=2
        )

    print("MaBaiHoc:", output["MaBaiHoc"])
    print("Tong cau hoi:", len(questions))

    for group in ["tu_vung", "ngu_phap", "chu_han"]:
        count = sum(
            q["NhomKienThuc"] == group
            for q in questions
        )
        print(f"{group}: {count}")

    print("\nFILE PREVIEW:")
    print(OUTPUT_FILE)

    print("\n20 CAU HOI:")
    for q in questions:
        print(
            f"{q['ThuTu']:02d}. "
            f"[{q['LoaiCauHoi']}] "
            f"{q['NoiDungCauHoi'].replace(chr(10), ' ')}"
        )

    print("\nHOAN TAT - CHUA GHI SQL")


if __name__ == "__main__":
    main()
