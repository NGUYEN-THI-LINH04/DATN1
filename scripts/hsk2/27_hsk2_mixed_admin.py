
# -*- coding: utf-8 -*-
"""
BUOC 34 - TAO BAI TAP HSK2 HON HOP 7 LOAI

Pham vi:
- HSK2 bai 2 den bai 23
- 20 cau hoi / bai
- Giu nguyen HSK1 va HSK2 bai 1
- PREVIEW mac dinh, KHONG ghi SQL
- --commit de cap nhat sau khi duyet

Duong dan:
D:\\DATN1\\scripts\\hsk2\\27_hsk2_mixed_admin.py
"""

import argparse
import json
import re
import sys

from collections import Counter
from contextlib import closing
from pathlib import Path


# ==========================================================
# 1. CAU HINH DU AN
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT))

from database import get_connection


DATA = (
    ROOT
    / "scripts"
    / "hsk2"
    / "data"
    / "processed"
)

SOURCE = DATA / "exercises_hsk2_02_23_preview.json"

PREVIEW = DATA / "exercises_hsk2_02_23_mixed_preview.json"

BACKUP = DATA / "exercises_hsk2_02_23_before_mixed_sql.json"


# So luong cau hoi cho moi bai
KINDS = {
    "chon_mot": 5,
    "chon_nhieu": 2,
    "dung_sai": 3,
    "dien_tu": 3,
    "ghep_cap": 2,
    "sap_xep": 3,
    "viet_ngan": 2,
}


# ==========================================================
# 2. HAM HO TRO
# ==========================================================

def dumps(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
    )


def new_question(
    question_type,
    content,
    answer=None,
    choices=None,
    explanation="",
    skill="doc",
):
    return {
        "LoaiCauHoi": question_type,
        "KyNang": skill,
        "NoiDungCauHoi": content,
        "DapAnJson": answer,
        "GiaiThich": explanation,
        "DiemToiDa": 1,
        "LuaChon": choices or [],
    }


def make_option(text, is_correct, order):
    return {
        "NoiDungLuaChon": text,
        "LaDapAnDung": bool(is_correct),
        "ThuTu": order,
    }


def get_word(question):
    match = re.search(
        r"“([^”]+)”",
        question["NoiDungCauHoi"],
    )

    if match:
        return match.group(1)

    return None


def get_correct_answer(question):
    answers = [
        option["NoiDungLuaChon"]
        for option in question["LuaChon"]
        if option["LaDapAnDung"]
    ]

    if len(answers) != 1:
        raise ValueError(
            "Cau hoi goc phai co dung 1 dap an."
        )

    return answers[0]


def prepare_words(block):
    meanings = {}
    pinyins = {}

    for question in block["CauHoi"]:

        word = get_word(question)

        if not word:
            continue

        answer = get_correct_answer(question)

        if question["DangKiemTra"] == "nghia":
            meanings[word] = answer

        elif question["DangKiemTra"] == "pinyin":
            pinyins[word] = answer

    if len(meanings) < 9:
        raise ValueError(
            f"Bai {block['SoThuTuBai']} "
            "khong du tu vung tieng Viet."
        )

    if len(pinyins) < 9:
        raise ValueError(
            f"Bai {block['SoThuTuBai']} "
            "khong du du lieu Pinyin."
        )

    return (
        list(meanings.items()),
        list(pinyins.items()),
    )


# ==========================================================
# 3. TACH THANH PHAN CAU TIENG TRUNG
# ==========================================================

def split_sentence(sentence, vocabulary):

    sentence = sentence.strip()

    words = sorted(
        set(vocabulary),
        key=len,
        reverse=True,
    )

    result = []
    index = 0

    while index < len(sentence):

        if sentence[index].isspace():
            index += 1
            continue

        matched_word = next(
            (
                word
                for word in words
                if (
                    len(word) > 1
                    and sentence.startswith(
                        word,
                        index,
                    )
                )
            ),
            None,
        )

        if matched_word:
            result.append(matched_word)
            index += len(matched_word)

        else:
            result.append(sentence[index])
            index += 1

    return result


# ==========================================================
# 4. TAO 20 CAU HOI HON HOP
# ==========================================================

def generate_exercise(block, grammar_examples):

    meanings, pinyins = prepare_words(block)

    lesson_number = block["SoThuTuBai"]

    questions = []

    # ------------------------------------------------------
    # LOAI 1 - CHON MOT: 5 CAU
    # ------------------------------------------------------

    selected = []

    for old_question in block["CauHoi"]:

        if len(selected) >= 5:
            break

        if old_question["LoaiCauHoi"] != "chon_mot":
            continue

        selected.append(
            new_question(
                question_type="chon_mot",
                content=old_question["NoiDungCauHoi"],
                choices=old_question["LuaChon"],
                explanation=old_question["GiaiThich"],
            )
        )

    questions.extend(selected)

    # ------------------------------------------------------
    # LOAI 2 - CHON NHIEU: 2 CAU
    # ------------------------------------------------------

    for k in range(2):

        a, b, c, d = [
            meanings[(4 * k + j) % len(meanings)]
            for j in range(4)
        ]

        wrong_1 = next(
            (
                meaning
                for word, meaning in meanings
                if (
                    word != c[0]
                    and meaning not in [
                        c[1],
                        a[1],
                        b[1],
                    ]
                )
            ),
            None,
        )

        wrong_2 = next(
            (
                meaning
                for word, meaning in reversed(meanings)
                if (
                    word != d[0]
                    and meaning not in [
                        d[1],
                        a[1],
                        b[1],
                        wrong_1,
                    ]
                )
            ),
            None,
        )

        if not wrong_1 or not wrong_2:
            raise ValueError(
                f"Bai {lesson_number}: "
                "khong du lua chon."
            )

        pairs = [
            (
                f"{a[0]} — {a[1]}",
                True,
            ),
            (
                f"{c[0]} — {wrong_1}",
                False,
            ),
            (
                f"{b[0]} — {b[1]}",
                True,
            ),
            (
                f"{d[0]} — {wrong_2}",
                False,
            ),
        ]

        choices = [
            make_option(text, correct, index)
            for index, (text, correct)
            in enumerate(pairs, start=1)
        ]

        questions.append(
            new_question(
                question_type="chon_nhieu",
                content=(
                    "Chọn đúng HAI cặp chữ Hán "
                    "và nghĩa tiếng Việt."
                ),
                choices=choices,
                explanation=(
                    f"Đúng: {a[0]} — {a[1]}; "
                    f"{b[0]} — {b[1]}."
                ),
            )
        )

    # ------------------------------------------------------
    # LOAI 3 - DUNG SAI: 3 CAU
    # ------------------------------------------------------

    for k in range(3):

        word, meaning = meanings[
            (k + 8) % len(meanings)
        ]

        is_true = k != 1

        other_meaning = meanings[
            (k + 4) % len(meanings)
        ][1]

        if other_meaning == meaning:
            other_meaning = next(
                value
                for _, value in meanings
                if value != meaning
            )

        shown_meaning = (
            meaning
            if is_true
            else other_meaning
        )

        answer = (
            "dung"
            if is_true
            else "sai"
        )

        questions.append(
            new_question(
                question_type="dung_sai",
                content=(
                    f"Nhận định: “{word}” "
                    f"có nghĩa là “{shown_meaning}”."
                ),
                answer=dumps({
                    "answer": answer,
                }),
                explanation=(
                    f"“{word}” có nghĩa là "
                    f"“{meaning}”."
                ),
            )
        )

    # ------------------------------------------------------
    # LOAI 4 - DIEN TU: 3 CAU
    # ------------------------------------------------------

    for k in range(3):

        word, meaning = meanings[
            (k + 3) % len(meanings)
        ]

        questions.append(
            new_question(
                question_type="dien_tu",
                content=(
                    "Điền chữ Hán phù hợp "
                    "với nghĩa tiếng Việt: "
                    f"“{meaning}”."
                ),
                answer=dumps({
                    "answers": [word],
                }),
                explanation=(
                    f"Đáp án: {word} — {meaning}."
                ),
                skill="viet",
            )
        )

    # ------------------------------------------------------
    # LOAI 5 - GHEP CAP: 2 CAU
    # ------------------------------------------------------

    for k in range(2):

        selected_pairs = [
            meanings[
                (k * 3 + j) % len(meanings)
            ]
            for j in range(3)
        ]

        pairs = [
            {
                "left": word,
                "right": meaning,
            }
            for word, meaning in selected_pairs
        ]

        # Khong tao nhieu cap co trung nghia.
        if len({
            pair["right"]
            for pair in pairs
        }) != 3:
            raise ValueError(
                f"Bai {lesson_number}: "
                "cau ghep cap bi trung nghia."
            )

        explanation = "; ".join(
            f"{word}: {meaning}"
            for word, meaning in selected_pairs
        )

        questions.append(
            new_question(
                question_type="ghep_cap",
                content=(
                    "Ghép từng từ tiếng Trung "
                    "với nghĩa tiếng Việt tương ứng."
                ),
                answer=dumps({
                    "pairs": pairs,
                }),
                explanation=explanation,
            )
        )

    # ------------------------------------------------------
    # LOAI 6 - SAP XEP: 3 CAU
    # ------------------------------------------------------

    if len(grammar_examples) < 2:
        raise ValueError(
            f"Bai {lesson_number} "
            "can it nhat 2 vi du ngu phap."
        )

    # 2 cau sap xep duoc lay tu bang NguPhap.
    for hanzi, vietnamese in grammar_examples[:2]:

        hanzi = hanzi.strip()

        vietnamese = (
            vietnamese or ""
        ).strip()

        vocabulary = (
            [word for word, _ in meanings]
            + [word for word, _ in pinyins]
        )

        items = split_sentence(
            hanzi,
            vocabulary,
        )

        if len(items) < 3:
            raise ValueError(
                f"Bai {lesson_number}: "
                "cau ngu phap qua ngan."
            )

        questions.append(
            new_question(
                question_type="sap_xep",
                content=(
                    "Sắp xếp các thành phần "
                    "thành câu đúng. "
                    f"Nghĩa gợi ý: {vietnamese}"
                ),
                answer=dumps({
                    "items": items,
                }),
                explanation=(
                    f"Câu đúng: {hanzi}"
                ),
            )
        )

    # 1 cau sap xep cac chu Han thanh tu.
    long_words = [
        (word, meaning)
        for word, meaning in meanings
        if (
            2 <= len(word) <= 4
            and all(
                "\u4e00" <= character <= "\u9fff"
                for character in word
            )
        )
    ]

    if not long_words:
        raise ValueError(
            f"Bai {lesson_number}: "
            "khong co tu Han de sap xep."
        )

    word, meaning = long_words[0]

    questions.append(
        new_question(
            question_type="sap_xep",
            content=(
                "Sắp xếp các chữ Hán "
                f"để được từ có nghĩa “{meaning}”."
            ),
            answer=dumps({
                "items": list(word),
            }),
            explanation=(
                f"Từ đúng: {word}."
            ),
        )
    )

    # ------------------------------------------------------
    # LOAI 7 - VIET NGAN: 2 CAU
    # ------------------------------------------------------

    for hanzi, vietnamese in grammar_examples[:2]:

        if not vietnamese or not vietnamese.strip():
            raise ValueError(
                f"Bai {lesson_number}: "
                "thieu ban dich tieng Viet."
            )

        sample_answer = vietnamese.strip()

        questions.append(
            new_question(
                question_type="viet_ngan",
                content=(
                    "Dịch câu sau sang "
                    f"tiếng Việt: {hanzi}"
                ),
                answer=dumps({
                    "sample_answer": sample_answer,
                }),
                explanation=(
                    "Đáp án tham khảo: "
                    + sample_answer
                ),
                skill="viet",
            )
        )

    # ------------------------------------------------------
    # KIEM TRA TONG SO CAU HOI
    # ------------------------------------------------------

    if len(questions) != 20:
        raise ValueError(
            f"Bai {lesson_number} "
            f"co {len(questions)} cau, "
            "khong phai 20."
        )

    actual_types = Counter(
        question["LoaiCauHoi"]
        for question in questions
    )

    if actual_types != KINDS:
        raise ValueError(
            f"Bai {lesson_number}: "
            "so luong cac loai cau hoi khong dung."
        )

    for index, question in enumerate(
        questions,
        start=1,
    ):
        question["ThuTu"] = index

    return {
        "MaBaiHoc": block["MaBaiHoc"],
        "SoThuTuBai": lesson_number,
        "TieuDe": block["TieuDe"],
        "CauHoi": questions,
    }


# ==========================================================
# 5. LAY CAU VI DU NGU PHAP TU SQL
# ==========================================================

def read_grammar(cursor, lesson_id):

    cursor.execute(
        """
        SELECT
            ViDuTiengTrung,
            ViDuTiengViet
        FROM dbo.NguPhap
        WHERE
            MaBaiHoc = ?
            AND NULLIF(
                LTRIM(RTRIM(ViDuTiengTrung)),
                N''
            ) IS NOT NULL
        ORDER BY
            ThuTu,
            MaNguPhap;
        """,
        lesson_id,
    )

    return [
        (row[0], row[1])
        for row in cursor.fetchall()
    ]


# ==========================================================
# 6. SAO LUU CAU HOI HIEN TAI TU SQL
# ==========================================================

def backup_questions(cursor, exercise_ids):

    result = []

    fields = [
        "MaCauHoi",
        "MaBaiTap",
        "LoaiCauHoi",
        "KyNang",
        "NoiDungCauHoi",
        "DoanVan",
        "MaTep",
        "DapAnJson",
        "GiaiThich",
        "DiemToiDa",
        "ThuTu",
    ]

    for exercise_id in exercise_ids:

        cursor.execute(
            """
            SELECT
                MaCauHoi,
                MaBaiTap,
                LoaiCauHoi,
                KyNang,
                NoiDungCauHoi,
                DoanVan,
                MaTep,
                DapAnJson,
                GiaiThich,
                CAST(DiemToiDa AS float),
                ThuTu
            FROM dbo.CauHoi
            WHERE MaBaiTap = ?
            ORDER BY
                ThuTu,
                MaCauHoi;
            """,
            exercise_id,
        )

        questions = []

        for row in cursor.fetchall():

            question = dict(
                zip(fields, row)
            )

            cursor.execute(
                """
                SELECT
                    MaLuaChon,
                    NoiDungLuaChon,
                    LaDapAnDung,
                    ThuTu
                FROM dbo.LuaChonCauHoi
                WHERE MaCauHoi = ?
                ORDER BY
                    ThuTu,
                    MaLuaChon;
                """,
                question["MaCauHoi"],
            )

            question["LuaChon"] = [
                {
                    "MaLuaChon": choice[0],
                    "NoiDungLuaChon": choice[1],
                    "LaDapAnDung": bool(choice[2]),
                    "ThuTu": choice[3],
                }
                for choice in cursor.fetchall()
            ]

            questions.append(question)

        result.extend(questions)

    return result


# ==========================================================
# 7. HAM CHINH
# ==========================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--commit",
        action="store_true",
    )

    args = parser.parse_args()

    print("=" * 65)
    print("BUOC 34 - TAO BAI TAP HON HOP HSK2")
    print("=" * 65)

    # ------------------------------------------------------
    # KIEM TRA JSON GOC
    # ------------------------------------------------------

    if not SOURCE.is_file():
        raise SystemExit(
            f"KHONG TIM THAY FILE JSON GOC:\n{SOURCE}"
        )

    blocks = json.loads(
        SOURCE.read_text(
            encoding="utf-8-sig"
        )
    )

    lesson_numbers = sorted(
        block["SoThuTuBai"]
        for block in blocks
    )

    if lesson_numbers != list(range(2, 24)):
        raise SystemExit(
            "JSON goc phai gom dung "
            "22 bai HSK2 tu bai 2 den bai 23."
        )

    DATA.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------
    # TAO DU LIEU MOI
    # ------------------------------------------------------

    with closing(get_connection()) as connection:

        with closing(connection.cursor()) as cursor:

            exercises = [
                generate_exercise(
                    block,
                    read_grammar(
                        cursor,
                        block["MaBaiHoc"],
                    ),
                )
                for block in blocks
            ]

            encoded = dumps(exercises) + "\n"

            # --------------------------------------------------
            # CHE DO PREVIEW
            # --------------------------------------------------

            if not args.commit:

                PREVIEW.write_text(
                    encoded,
                    encoding="utf-8",
                )

                print(
                    "\nPREVIEW HOAN THANH - CHUA GHI SQL"
                )

                for exercise in exercises:

                    print(
                        f"Bai "
                        f"{exercise['SoThuTuBai']:02} "
                        "| 20 cau | 7 loai"
                    )

                print("\nTong bai:", len(exercises))

                print(
                    "Tong cau:",
                    sum(
                        len(item["CauHoi"])
                        for item in exercises
                    ),
                )

                print("\nJSON:", PREVIEW)

                return

            # --------------------------------------------------
            # CHE DO COMMIT
            # --------------------------------------------------

            if (
                not PREVIEW.is_file()
                or PREVIEW.read_text(
                    encoding="utf-8"
                ) != encoded
            ):
                raise SystemExit(
                    "PREVIEW KHONG KHOP. "
                    "Hay chay PREVIEW lai truoc khi COMMIT."
                )

            exercise_ids = []

            # --------------------------------------------------
            # KIEM TRA TOAN BO BAI TAP
            # --------------------------------------------------

            for exercise in exercises:

                cursor.execute(
                    """
                    SELECT
                        bt.MaBaiTap,
                        bt.TrangThai,
                        bh.MaKhoaHoc,
                        bh.SoThuTuBai
                    FROM dbo.BaiTap AS bt
                        WITH (UPDLOCK, HOLDLOCK)
                    INNER JOIN dbo.BaiHoc AS bh
                        ON bt.MaBaiHoc = bh.MaBaiHoc
                    WHERE bt.MaBaiHoc = ?;
                    """,
                    exercise["MaBaiHoc"],
                )

                rows = cursor.fetchall()

                if len(rows) != 1:
                    raise RuntimeError(
                        f"Bai {exercise['SoThuTuBai']} "
                        "khong co dung 1 bai tap."
                    )

                (
                    exercise_id,
                    status,
                    course_id,
                    lesson_number,
                ) = rows[0]

                if (
                    int(course_id) != 2
                    or int(lesson_number)
                    != exercise["SoThuTuBai"]
                    or status != "ban_nhap"
                ):
                    raise RuntimeError(
                        f"Bai {lesson_number}: "
                        "sai khoa hoc hoac "
                        "khong o trang thai ban_nhap."
                    )

                # Kiem tra lich su lam bai.
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.LanLamBai
                    WHERE MaBaiTap = ?;
                    """,
                    exercise_id,
                )

                if cursor.fetchone()[0] > 0:
                    raise RuntimeError(
                        f"Bai {lesson_number} "
                        "da co lich su lam bai."
                    )

                # Kiem tra chi tiet bai lam.
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.ChiTietBaiLam AS ct
                    INNER JOIN dbo.CauHoi AS ch
                        ON ch.MaCauHoi = ct.MaCauHoi
                    WHERE ch.MaBaiTap = ?;
                    """,
                    exercise_id,
                )

                if cursor.fetchone()[0] > 0:
                    raise RuntimeError(
                        f"Bai {lesson_number} "
                        "da co chi tiet bai lam."
                    )

                # Chi thay 20 cau cu cua moi bai.
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.CauHoi
                    WHERE MaBaiTap = ?;
                    """,
                    exercise_id,
                )

                if cursor.fetchone()[0] != 20:
                    raise RuntimeError(
                        f"Bai {lesson_number} "
                        "khong con dung 20 cau goc."
                    )

                exercise_ids.append(
                    int(exercise_id)
                )

            # --------------------------------------------------
            # SAO LUU 440 CAU GOC
            # --------------------------------------------------

            old_questions = backup_questions(
                cursor,
                exercise_ids,
            )

            if len(old_questions) != 440:
                raise RuntimeError(
                    "Khong sao luu du 440 cau goc."
                )

            if BACKUP.exists():
                raise RuntimeError(
                    "Da ton tai file backup cu. "
                    "Dung de tranh ghi de ban sao luu."
                )

            BACKUP.write_text(
                dumps(old_questions) + "\n",
                encoding="utf-8",
            )

            print(
                "\nDA SAO LUU 440 CAU GOC:",
                BACKUP,
            )

            # --------------------------------------------------
            # CAP NHAT CAU HOI TRONG TRANSACTION
            # --------------------------------------------------

            try:

                for exercise_id, exercise in zip(
                    exercise_ids,
                    exercises,
                ):

                    cursor.execute(
                        """
                        SELECT MaCauHoi
                        FROM dbo.CauHoi
                        WHERE MaBaiTap = ?
                        ORDER BY
                            ThuTu,
                            MaCauHoi;
                        """,
                        exercise_id,
                    )

                    question_ids = [
                        row[0]
                        for row in cursor.fetchall()
                    ]

                    for question_id, question in zip(
                        question_ids,
                        exercise["CauHoi"],
                    ):

                        cursor.execute(
                            """
                            UPDATE dbo.CauHoi
                            SET
                                LoaiCauHoi = ?,
                                KyNang = ?,
                                NoiDungCauHoi = ?,
                                DoanVan = NULL,
                                MaTep = NULL,
                                DapAnJson = ?,
                                GiaiThich = ?,
                                DiemToiDa = 1,
                                ThuTu = ?
                            WHERE MaCauHoi = ?;
                            """,
                            question["LoaiCauHoi"],
                            question["KyNang"],
                            question["NoiDungCauHoi"],
                            question["DapAnJson"],
                            question["GiaiThich"],
                            question["ThuTu"],
                            question_id,
                        )

                        # Xoa lua chon cu cua cau hoi.
                        cursor.execute(
                            """
                            DELETE FROM dbo.LuaChonCauHoi
                            WHERE MaCauHoi = ?;
                            """,
                            question_id,
                        )

                        # Them lua chon moi.
                        for option in question["LuaChon"]:

                            cursor.execute(
                                """
                                INSERT INTO dbo.LuaChonCauHoi
                                (
                                    MaCauHoi,
                                    NoiDungLuaChon,
                                    LaDapAnDung,
                                    ThuTu
                                )
                                VALUES (?, ?, ?, ?);
                                """,
                                question_id,
                                option["NoiDungLuaChon"],
                                int(
                                    option["LaDapAnDung"]
                                ),
                                option["ThuTu"],
                            )

                connection.commit()

            except Exception:

                connection.rollback()
                raise

            print("\nCOMMIT THANH CONG!")

            print(
                "Da cap nhat 22 bai HSK2 "
                "voi 440 cau hoi hon hop."
            )

            print(
                "Da giu nguyen MaCauHoi "
                "va MaBaiTap hien tai."
            )

            print("\nBACKUP:", BACKUP)


if __name__ == "__main__":
    main()
