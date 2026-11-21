
"""
BUOC 26 - TAO BAI TAP HSK2 TU BAI 2 DEN BAI 23

Mac dinh:
- Doc SQL
- Tao 22 bai tap, moi bai 20 cau
- Xuat JSON + CSV de xem truoc
- KHONG ghi database

--commit:
- Import tat ca trong mot transaction
- Chi them bai tap moi
- Trang thai ban_nhap
- Loi thi ROLLBACK toan bo
"""

import argparse
import csv
import json
import random
import re
import sys
from collections import Counter
from contextlib import closing
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

OUT_DIR = ROOT / "scripts" / "hsk2" / "data" / "processed"
PREVIEW_JSON = OUT_DIR / "exercises_hsk2_02_23_preview.json"
PREVIEW_CSV = OUT_DIR / "exercises_hsk2_02_23_review.csv"

COURSE_ID = 2
FIRST_LESSON = 2
LAST_LESSON = 23
PER_LESSON = 20
ADMIN_ID = 1

RANDOM_SEED = 20261010


# Nghia uu tien dung khi tao bai tap HSK2
# Chi thay doi dap an bai tap, KHONG sua bang TuVung.

MEANING_OVERRIDES = {
    "例子": "ví dụ",
    "复习": "ôn tập",
    "高中": "trường trung học phổ thông",
    "公交车": "xe buýt",
    "刚": "vừa mới",
    "接着": "tiếp theo",
    "克": "gam",
    "组": "nhóm; tổ",
    "题": "đề bài; câu hỏi",
    "太太": "vợ; bà",
    "长大": "lớn lên; trưởng thành",
    "算": "tính toán",
    "单位": "đơn vị",
    "体育馆": "nhà thi đấu thể thao",
    "复习": "ôn tập",
    
    "交通": "giao thông",
    "开心": "vui vẻ",
    "一般": "thông thường; bình thường",
    "不过": "nhưng; tuy nhiên",
    "听讲": "nghe giảng",
    "大声": "lớn tiếng",
    "态度": "thái độ",
    "度": "độ; mức độ",
    "笔记": "ghi chú; ghi chép",
    "练": "luyện tập",
    "越": "càng",

}


# Cac tu can kiem tra nghia/Pinyin theo ngu canh
# Tam thoi khong dung de tao cau hoi.
# KHONG xoa hay sua tu trong SQL.
WORDS_NEED_REVIEW = {
    "当",
    "面1",
    "封",
    "市",
    "得",
    "背",
    "或",
    "响",
}

# Nghia co nguy co la metadata tu dien
BAD_MEANING_FRAGMENTS = (
    "biến thể của",
    "cũng đọc",
    "viết tắt của",
    "từ tượng thanh",
    "lt:",
)


def meaning_parts(text):
    """Tach cac nghia tieng Viet de so sanh."""
    if not text:
        return []

    parts = re.split(
        r"\s*[;/|]\s*",
        str(text).lower()
    )

    result = []

    for part in parts:
        part = re.sub(
            r"\([^)]*\)", "", part
        )
        part = re.sub(
            r"\s+", " ", part
        ).strip(" .,:;")

        if part:
            result.append(part)

    return result


def meanings_overlap(a, b):
    """
    Phat hien cac lua chon co nghia giong
    hoac bao ham nhau.

    Day la bo loc than trong, khong phai
    bo nhan dang dong nghia hoan chinh.
    """
    a_parts = meaning_parts(a)
    b_parts = meaning_parts(b)

    for x in a_parts:
        for y in b_parts:
            if x == y:
                return True

            if len(x) >= 4 and len(y) >= 4:
                if x in y or y in x:
                    return True

    return False


def is_safe_word(word):
    hanzi = str(
        word.get("ChuHan") or ""
    ).strip()

    pinyin = str(
        word.get("PhienAm") or ""
    ).strip()

    if not hanzi or not pinyin:
        return False

    if hanzi in WORDS_NEED_REVIEW:
        return False

    # Loai ky tu so bat thuong trong ChuHan
    if re.search(r"[0-9]", hanzi):
        return False

    raw_meaning = str(
        word.get("NghiaTiengViet") or ""
    )

    # Tu da duoc kiem duyet bang override
    # co the dung nghia uu tien.
    if hanzi in MEANING_OVERRIDES:
        return True

    lower = raw_meaning.lower()

    if any(
        fragment in lower
        for fragment in BAD_MEANING_FRAGMENTS
    ):
        return False

    return True


def select_distractors(correct, candidates, rng,
                       check_meaning=False):
    """Chon 3 dap an sai khong trung/ngan nghia."""
    pool = []

    shuffled = list(candidates)
    rng.shuffle(shuffled)

    for candidate in shuffled:
        if normalize(candidate) == normalize(correct):
            continue

        if check_meaning and meanings_overlap(
            candidate, correct
        ):
            continue

        if check_meaning and any(
            meanings_overlap(candidate, old)
            for old in pool
        ):
            continue

        if any(
            normalize(candidate) == normalize(old)
            for old in pool
        ):
            continue

        pool.append(candidate)

        if len(pool) == 3:
            break

    if len(pool) < 3:
        return None

    choices = pool + [correct]
    rng.shuffle(choices)
    return choices


def clean_meaning(raw):
    if not raw:
        return None

    text = str(raw).strip()

    # Chi lay nghia dau tien, khong lay metadata tu dien
    text = re.split(r"\s*/\s*|\s*\|\|\s*", text)[0]
    text = text.strip(" ;. ")

    bad_fragments = [
        "biến thể",
        "cũng đọc",
        "lt:",
        "[",
        "]",
        "xem thêm",
    ]

    lower = text.lower()

    if any(bad in lower for bad in bad_fragments):
        return None

    if not 2 <= len(text) <= 65:
        return None

    return text


def normalize(text):
    return re.sub(r"\s+", "", str(text).strip().lower())


def fetch_all(cur, sql, *params):
    cur.execute(sql, *params)
    cols = [c[0] for c in cur.description]
    return [
        dict(zip(cols, row))
        for row in cur.fetchall()
    ]


def load_lessons(cur):
    return fetch_all(
        cur,
        """
        SELECT
            MaBaiHoc,
            MaKhoaHoc,
            SoThuTuBai,
            TieuDe
        FROM dbo.BaiHoc
        WHERE MaKhoaHoc = ?
          AND SoThuTuBai BETWEEN ? AND ?
        ORDER BY SoThuTuBai
        """,
        COURSE_ID,
        FIRST_LESSON,
        LAST_LESSON
    )


def load_vocabulary(cur, lesson_id):
    return fetch_all(
        cur,
        """
        SELECT
            tv.MaTuVung,
            tv.ChuHan,
            tv.PhienAm,
            tv.NghiaTiengViet
        FROM dbo.TuVungBaiHoc AS tvbh
        INNER JOIN dbo.TuVung AS tv
            ON tv.MaTuVung = tvbh.MaTuVung
        WHERE tvbh.MaBaiHoc = ?
        ORDER BY tvbh.ThuTu, tv.MaTuVung
        """,
        lesson_id
    )


def make_question(word, choices, correct, kind, order):
    if kind == "nghia":
        content = (
            f'Từ “{word["ChuHan"]}” có nghĩa là gì?'
        )
        explanation = (
            f'“{word["ChuHan"]}” '
            f'({word["PhienAm"]}) có nghĩa là '
            f'“{word["NghiaDaChon"]}”.'
        )
    else:
        content = (
            f'Pinyin đúng của từ “{word["ChuHan"]}” '
            f'là gì?'
        )
        explanation = (
            f'“{word["ChuHan"]}” '
            f'đọc là {word["PhienAm"]}. '
            f'Nghĩa: {word["NghiaDaChon"]}.'
        )

    if len(choices) != 4:
        raise ValueError("Cau hoi phai co 4 lua chon")

    if len({normalize(x) for x in choices}) != 4:
        raise ValueError("Lua chon bi trung")

    if sum(x == correct for x in choices) != 1:
        raise ValueError("Dap an dung khong duy nhat")

    return {
        "LoaiCauHoi": "chon_mot",
        "KyNang": "doc",
        "NhomKienThuc": "tu_vung",
        "DangKiemTra": kind,
        "MaTuVungNguon": word["MaTuVung"],
        "NoiDungCauHoi": content,
        "DapAnJson": None,
        "GiaiThich": explanation,
        "DiemToiDa": 1,
        "ThuTu": order,
        "LuaChon": [
            {
                "NoiDungLuaChon": value,
                "LaDapAnDung": value == correct,
                "ThuTu": i + 1
            }
            for i, value in enumerate(choices)
        ]
    }



def generate_lesson(lesson, vocabulary):
    """
    Tao 20 cau hoi:
    - 10 cau nhan biet nghia
    - 10 cau nhan biet Pinyin

    Neu khong du du lieu an toan thi bao loi.
    Khong tu y lay tu cua bai khac.
    """

    lesson_number = int(lesson["SoThuTuBai"])

    rng = random.Random(
        RANDOM_SEED + lesson_number
    )

    usable = []
    rejected = []

    # 1. Loc du lieu dau vao
    for word in vocabulary:
        if not is_safe_word(word):
            rejected.append(word["ChuHan"])
            continue

        meaning = MEANING_OVERRIDES.get(
            word["ChuHan"]
        )

        if meaning is None:
            meaning = clean_meaning(
                word["NghiaTiengViet"]
            )

        if not meaning:
            rejected.append(word["ChuHan"])
            continue

        item = dict(word)
        item["NghiaDaChon"] = meaning.strip()
        usable.append(item)

    print(
        f"  Duoc dung={len(usable)}"
        f" | Can ra soat={len(rejected)}"
    )

    if rejected:
        print(
            "  Tu can ra soat:",
            ", ".join(map(str, rejected))
        )

    # 2. Tao danh sach tu co nghia duy nhat
    meaning_unique = {}

    for word in usable:
        key = normalize(
            word["NghiaDaChon"]
        )

        meaning_unique.setdefault(key, word)

    meaning_words = list(
        meaning_unique.values()
    )

    # 3. Tao danh sach tu co Pinyin duy nhat
    pinyin_unique = {}

    for word in usable:
        key = normalize(
            word["PhienAm"]
        )

        pinyin_unique.setdefault(key, word)

    pinyin_words = list(
        pinyin_unique.values()
    )

    rng.shuffle(meaning_words)
    rng.shuffle(pinyin_words)

    questions = []
    used_meaning_sources = set()
    used_pinyin_sources = set()

    # 4. Tao 10 cau hoi ve nghia
    for word in meaning_words:
        if len(questions) >= 10:
            break

        correct = word["NghiaDaChon"]

        candidates = [
            other["NghiaDaChon"]
            for other in meaning_words
            if other["MaTuVung"] != word["MaTuVung"]
        ]

        choices = select_distractors(
            correct,
            candidates,
            rng,
            check_meaning=True
        )

        if choices is None:
            continue

        if word["MaTuVung"] in used_meaning_sources:
            continue

        question = make_question(
            word,
            choices,
            correct,
            "nghia",
            len(questions) + 1
        )

        questions.append(question)
        used_meaning_sources.add(
            word["MaTuVung"]
        )

    count_meaning = len(questions)

    if count_meaning != 10:
        raise ValueError(
            f"Bai {lesson_number}: "
            f"chi tao duoc {count_meaning}/10 "
            "cau nghia an toan. "
            "Can ra soat du lieu bai nay."
        )

    # 5. Tao 10 cau hoi Pinyin
    for word in pinyin_words:
        if len(questions) >= PER_LESSON:
            break

        correct = word["PhienAm"]

        candidates = [
            other["PhienAm"]
            for other in pinyin_words
            if other["MaTuVung"] != word["MaTuVung"]
        ]

        choices = select_distractors(
            correct,
            candidates,
            rng,
            check_meaning=False
        )

        if choices is None:
            continue

        if word["MaTuVung"] in used_pinyin_sources:
            continue

        question = make_question(
            word,
            choices,
            correct,
            "pinyin",
            len(questions) + 1
        )

        questions.append(question)
        used_pinyin_sources.add(
            word["MaTuVung"]
        )

    if len(questions) != PER_LESSON:
        raise ValueError(
            f"Bai {lesson_number}: "
            f"chi tao duoc {len(questions)}/20 cau. "
            "Can kiem tra du lieu."
        )

    # 6. Kiem tra tat ca cac cau hoi
    for q in questions:
        options = q["LuaChon"]

        if len(options) != 4:
            raise ValueError(
                "Cau hoi khong du 4 lua chon"
            )

        correct_options = [
            x for x in options
            if x["LaDapAnDung"]
        ]

        if len(correct_options) != 1:
            raise ValueError(
                "Cau hoi khong co dung 1 dap an"
            )

        if q["DangKiemTra"] == "nghia":
            correct = correct_options[0][
                "NoiDungLuaChon"
            ]

            for option in options:
                if option["LaDapAnDung"]:
                    continue

                if meanings_overlap(
                    correct,
                    option["NoiDungLuaChon"]
                ):
                    raise ValueError(
                        "Phat hien lua chon gan nghia: "
                        + q["NoiDungCauHoi"]
                    )

    # 7. Dao thu tu va danh so
    rng.shuffle(questions)

    for index, question in enumerate(
        questions, start=1
    ):
        question["ThuTu"] = index

    # 8. Tra ve bai tap
    return {
        "MaKhoaHoc": COURSE_ID,
        "MaBaiHoc": lesson["MaBaiHoc"],
        "SoThuTuBai": lesson_number,
        "TieuDe": (
            f"Bài luyện tập Bài {lesson_number}"
            f' - {lesson["TieuDe"]}'
        ),
        "HuongDan": (
            "Hoàn thành các câu hỏi về từ vựng "
            "và Pinyin của bài học."
        ),
        "ThoiGianGioiHanGiay": 900,
        "PhanTramDat": 70,
        "TrangThai": "ban_nhap",
        "CauHoi": questions
    }


def build_preview(cur):
    lessons = load_lessons(cur)

    expected = list(
        range(FIRST_LESSON, LAST_LESSON + 1)
    )

    actual = [
        int(x["SoThuTuBai"])
        for x in lessons
    ]

    if actual != expected:
        raise ValueError(
            f"Danh sach bai hoc khong khop: {actual}"
        )

    results = []

    for lesson in lessons:
        vocab = load_vocabulary(
            cur, lesson["MaBaiHoc"]
        )

        exercise = generate_lesson(
            lesson, vocab
        )

        results.append(exercise)

        print(
            f'Bai {lesson["SoThuTuBai"]:02d} | '
            f'MaBaiHoc={lesson["MaBaiHoc"]} | '
            f'Tu={len(vocab)} | '
            f'CauHoi={len(exercise["CauHoi"])}'
        )

    return results


def export_preview(exercises):
    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    PREVIEW_JSON.write_text(
        json.dumps(
            exercises,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    with open(
        PREVIEW_CSV,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        writer = csv.writer(f)

        writer.writerow([
            "Bai",
            "MaBaiHoc",
            "ThuTuCau",
            "DangKiemTra",
            "MaTuVungNguon",
            "NoiDungCauHoi",
            "A",
            "B",
            "C",
            "D",
            "DapAnDung",
            "GiaiThich"
        ])

        for exercise in exercises:
            for q in exercise["CauHoi"]:
                opts = q["LuaChon"]

                correct_index = next(
                    i
                    for i, opt in enumerate(opts)
                    if opt["LaDapAnDung"]
                )

                writer.writerow([
                    exercise["SoThuTuBai"],
                    exercise["MaBaiHoc"],
                    q["ThuTu"],
                    q["DangKiemTra"],
                    q["MaTuVungNguon"],
                    q["NoiDungCauHoi"],
                    *[
                        opt["NoiDungLuaChon"]
                        for opt in opts
                    ],
                    "ABCD"[correct_index],
                    q["GiaiThich"]
                ])


def verify_no_existing(cur, exercises):
    # Kiem tra lai trong transaction
    for exercise in exercises:
        lesson_id = exercise["MaBaiHoc"]

        cur.execute(
            """
            SELECT COUNT(*)
            FROM dbo.BaiTap WITH (
                UPDLOCK, HOLDLOCK
            )
            WHERE MaBaiHoc = ?
            """,
            lesson_id
        )

        if int(cur.fetchone()[0]) != 0:
            raise ValueError(
                f"MaBaiHoc={lesson_id} da co bai tap. "
                "Dung import de tranh trung lap."
            )


def import_exercises(cur, exercises):
    total_questions = 0
    total_choices = 0

    for exercise in exercises:
        cur.execute(
            """
            INSERT INTO dbo.BaiTap
            (
                MaBaiHoc,
                TieuDe,
                HuongDan,
                ThoiGianGioiHanGiay,
                PhanTramDat,
                TrangThai,
                MaQuanTriVienCapNhat,
                NgayCapNhat
            )
            OUTPUT INSERTED.MaBaiTap
            VALUES
            (?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
            """,
            exercise["MaBaiHoc"],
            exercise["TieuDe"],
            exercise["HuongDan"],
            exercise["ThoiGianGioiHanGiay"],
            Decimal(str(exercise["PhanTramDat"])),
            "ban_nhap",
            ADMIN_ID
        )

        exercise_id = int(
            cur.fetchone()[0]
        )

        for q in exercise["CauHoi"]:
            cur.execute(
                """
                INSERT INTO dbo.CauHoi
                (
                    MaBaiTap,
                    LoaiCauHoi,
                    KyNang,
                    NoiDungCauHoi,
                    DoanVan,
                    MaTep,
                    DapAnJson,
                    GiaiThich,
                    DiemToiDa,
                    ThuTu,
                    MaQuanTriVienCapNhat,
                    NgayCapNhat
                )
                OUTPUT INSERTED.MaCauHoi
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                 SYSDATETIME())
                """,
                exercise_id,
                q["LoaiCauHoi"],
                q["KyNang"],
                q["NoiDungCauHoi"],
                None,
                None,
                None,
                q["GiaiThich"],
                Decimal(str(q["DiemToiDa"])),
                q["ThuTu"],
                ADMIN_ID
            )

            question_id = int(
                cur.fetchone()[0]
            )

            total_questions += 1

            for opt in q["LuaChon"]:
                cur.execute(
                    """
                    INSERT INTO dbo.LuaChonCauHoi
                    (
                        MaCauHoi,
                        NoiDungLuaChon,
                        LaDapAnDung,
                        ThuTu
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    question_id,
                    opt["NoiDungLuaChon"],
                    1 if opt["LaDapAnDung"] else 0,
                    opt["ThuTu"]
                )

                total_choices += 1

        print(
            f'INSERT Bai {exercise["SoThuTuBai"]:02d}'
            f' | MaBaiTap={exercise_id}'
        )

    if total_questions != 440:
        raise ValueError(
            f"Sai tong cau hoi: {total_questions}"
        )

    if total_choices != 1760:
        raise ValueError(
            f"Sai tong lua chon: {total_choices}"
        )

    # Kiem tra tong du lieu HSK2 trong transaction
    cur.execute(
        """
        SELECT
            COUNT(DISTINCT bt.MaBaiTap),
            COUNT(DISTINCT ch.MaCauHoi)
        FROM dbo.BaiHoc bh
        LEFT JOIN dbo.BaiTap bt
            ON bt.MaBaiHoc = bh.MaBaiHoc
        LEFT JOIN dbo.CauHoi ch
            ON ch.MaBaiTap = bt.MaBaiTap
        WHERE bh.MaKhoaHoc = 2
        """
    )

    count_exercises, count_questions = cur.fetchone()

    if int(count_exercises) != 23:
        raise ValueError(
            f"HSK2 phai co 23 bai tap, "
            f"hien co {count_exercises}"
        )

    if int(count_questions) != 460:
        raise ValueError(
            f"HSK2 phai co 460 cau hoi, "
            f"hien co {count_questions}"
        )

    print("\nTONG KET TRONG TRANSACTION:")
    print("Bai tap HSK2:", count_exercises)
    print("Cau hoi HSK2:", count_questions)
    print("Lua chon moi:", total_choices)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--commit",
        action="store_true"
    )

    args = parser.parse_args()

    print("=" * 68)
    print("BUOC 26 - BAI TAP HSK2 BAI 2 DEN 23")
    print("=" * 68)

    if args.commit:
        print("CHE DO: COMMIT")
    else:
        print("CHE DO: PREVIEW - KHONG GHI SQL")

    with closing(get_connection()) as conn:
        conn.autocommit = False

        try:
            with closing(conn.cursor()) as cur:
                cur.execute("SELECT DB_NAME()")
                db_name = cur.fetchone()[0]

                if db_name.lower() != "hoctiengtrungdb":
                    raise ValueError(
                        f"Sai database: {db_name}"
                    )

                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.QuanTriVien
                    WHERE MaQuanTriVien = ?
                      AND DangHoatDong = 1
                    """,
                    ADMIN_ID
                )

                if int(cur.fetchone()[0]) != 1:
                    raise ValueError(
                        "Admin ID=1 khong hoat dong"
                    )

                exercises = build_preview(cur)

                if len(exercises) != 22:
                    raise ValueError(
                        "Phai co dung 22 bai tap"
                    )

                total = sum(
                    len(x["CauHoi"])
                    for x in exercises
                )

                if total != 440:
                    raise ValueError(
                        f"Sai tong cau hoi: {total}"
                    )

                verify_no_existing(cur, exercises)

                if args.commit:
                    # Phai co file preview da xem
                    if not PREVIEW_JSON.exists():
                        raise ValueError(
                            "Chua co preview. "
                            "Hay chay khong co --commit truoc."
                        )

                    previous = json.loads(
                        PREVIEW_JSON.read_text(
                            encoding="utf-8"
                        )
                    )

                    if previous != exercises:
                        raise ValueError(
                            "Du lieu khac ban preview. "
                            "Hay tao va kiem tra preview lai."
                        )

                    import_exercises(
                        cur, exercises
                    )

                    conn.commit()

                    print("\nCOMMIT THANH CONG")
                    print("DA LUU 22 BAI TAP HSK2")
                else:
                    export_preview(exercises)

                    conn.rollback()

                    print("\nPREVIEW THANH CONG")
                    print("Bai tap:", len(exercises))
                    print("Cau hoi:", total)
                    print("Lua chon:", total * 4)
                    print("JSON:", PREVIEW_JSON)
                    print("CSV:", PREVIEW_CSV)
                    print("\nCHUA GHI SQL")

        except Exception:
            conn.rollback()
            print("\nDA ROLLBACK NEU CO THAY DOI")
            raise


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nLOI:", exc)
        raise SystemExit(1)
