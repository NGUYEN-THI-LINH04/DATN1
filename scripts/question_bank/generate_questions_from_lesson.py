# =========================================================
# MỘC HÁN
# SINH PREVIEW CÂU HỎI TỪ DỮ LIỆU BÀI HỌC
#
# File:
# scripts/question_bank/generate_questions_from_lesson.py
#
# Giai đoạn này:
# - CHỈ ĐỌC SQL
# - KHÔNG INSERT
# - KHÔNG UPDATE
# - KHÔNG DELETE
#
# Kết quả:
# scripts/question_bank/preview/
#     hsk1_bai1_questions.csv
# =========================================================

from __future__ import annotations

import csv
import random
import sys

from contextlib import closing
from pathlib import Path


# =========================================================
# ĐƯA THƯ MỤC GỐC D:\DATN1 VÀO PYTHON PATH
#
# File hiện tại:
# D:\DATN1\scripts\question_bank\...
#
# parents[0] = question_bank
# parents[1] = scripts
# parents[2] = DATN1
# =========================================================

CURRENT_FILE = Path(__file__).resolve()

PROJECT_ROOT = CURRENT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


# =========================================================
# IMPORT DATABASE CỦA DỰ ÁN
# =========================================================

from database import get_connection


# =========================================================
# CẤU HÌNH
# =========================================================

LESSON_ID = 1

TARGET_QUESTION_COUNT = 20

RANDOM_SEED = 20261008


# =========================================================
# THƯ MỤC OUTPUT
# =========================================================

PREVIEW_DIR = (
    CURRENT_FILE.parent
    / "preview"
)

PREVIEW_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# HÀM CHUẨN HÓA TEXT
# =========================================================

def clean_text(value) -> str:

    if value is None:
        return ""

    return str(value).strip()


# =========================================================
# LOẠI BỎ GIÁ TRỊ TRÙNG
# NHƯNG VẪN GIỮ THỨ TỰ
# =========================================================

def unique_values(values):

    result = []

    seen = set()

    for value in values:

        value = clean_text(
            value
        )

        if not value:
            continue

        key = value.casefold()

        if key in seen:
            continue

        seen.add(
            key
        )

        result.append(
            value
        )

    return result


# =========================================================
# CHỌN ĐÁP ÁN NHIỄU
#
# correct:
#   đáp án đúng
#
# candidates:
#   danh sách các đáp án có thể dùng làm nhiễu
#
# count:
#   cần lấy bao nhiêu đáp án sai
# =========================================================

def choose_distractors(
    correct,
    candidates,
    count=3,
):

    correct_key = clean_text(
        correct
    ).casefold()

    pool = []

    for candidate in unique_values(
        candidates
    ):

        if (
            candidate.casefold()
            == correct_key
        ):
            continue

        pool.append(
            candidate
        )


    if len(pool) < count:

        return []


    return random.sample(
        pool,
        count,
    )


# =========================================================
# TẠO CÂU TRẮC NGHIỆM 4 ĐÁP ÁN
# =========================================================

def make_multiple_choice(
    *,
    source_type,
    source_id,
    question_group,
    content,
    correct_answer,
    distractors,
    explanation,
):

    choices = [
        clean_text(
            correct_answer
        ),
        *[
            clean_text(item)
            for item
            in distractors
        ],
    ]


    if (
        len(choices) != 4
        or
        len(
            unique_values(
                choices
            )
        ) != 4
    ):
        return None


    random.shuffle(
        choices
    )


    correct_index = (
        choices.index(
            clean_text(
                correct_answer
            )
        )
        + 1
    )


    return {
        "source_type":
            source_type,

        "source_id":
            source_id,

        "question_group":
            question_group,

        "question_type":
            "chon_mot",

        "skill":
            "doc",

        "content":
            clean_text(
                content
            ),

        "passage":
            "",

        "choice_1":
            choices[0],

        "choice_2":
            choices[1],

        "choice_3":
            choices[2],

        "choice_4":
            choices[3],

        "correct_choice":
            correct_index,

        "answer_text":
            clean_text(
                correct_answer
            ),

        "explanation":
            clean_text(
                explanation
            ),

        "score":
            1,
    }


# =========================================================
# ĐỌC THÔNG TIN BÀI HỌC
# =========================================================

def load_lesson(
    cursor,
    lesson_id,
):

    cursor.execute(
        """
        SELECT
            bh.MaBaiHoc,
            bh.SoThuTuBai,
            bh.TieuDe,

            kh.MaKhoaHoc,
            kh.MaCapDo,
            kh.TieuDe

        FROM dbo.BaiHoc AS bh

        INNER JOIN dbo.KhoaHoc AS kh
            ON kh.MaKhoaHoc
            = bh.MaKhoaHoc

        WHERE
            bh.MaBaiHoc = ?;
        """,
        lesson_id,
    )


    row = cursor.fetchone()


    if row is None:

        raise RuntimeError(
            (
                f"Khong tim thay "
                f"MaBaiHoc = {lesson_id}."
            )
        )


    return {
        "lesson_id":
            row[0],

        "lesson_order":
            row[1],

        "lesson_title":
            clean_text(
                row[2]
            ),

        "course_id":
            row[3],

        "hsk_level":
            row[4],

        "course_title":
            clean_text(
                row[5]
            ),
    }


# =========================================================
# ĐỌC TỪ VỰNG CỦA BÀI
# =========================================================

def load_vocabulary(
    cursor,
    lesson_id,
):

    cursor.execute(
        """
        SELECT
            tv.MaTuVung,
            tv.ChuHan,
            tv.PhienAm,
            tv.NghiaTiengViet,
            tv.TuLoai,
            tv.ViDuTiengTrung,
            tv.ViDuTiengViet,
            tvbh.ThuTu

        FROM dbo.TuVungBaiHoc AS tvbh

        INNER JOIN dbo.TuVung AS tv
            ON tv.MaTuVung
            = tvbh.MaTuVung

        WHERE
            tvbh.MaBaiHoc = ?
            AND tv.DaDuyet = 1

        ORDER BY
            tvbh.ThuTu,
            tv.MaTuVung;
        """,
        lesson_id,
    )


    items = []


    for row in cursor.fetchall():

        items.append(
            {
                "id":
                    row[0],

                "hanzi":
                    clean_text(
                        row[1]
                    ),

                "pinyin":
                    clean_text(
                        row[2]
                    ),

                "meaning":
                    clean_text(
                        row[3]
                    ),

                "word_type":
                    clean_text(
                        row[4]
                    ),

                "example_zh":
                    clean_text(
                        row[5]
                    ),

                "example_vi":
                    clean_text(
                        row[6]
                    ),

                "order":
                    row[7],
            }
        )


    return items


# =========================================================
# ĐỌC NGỮ PHÁP CỦA BÀI
# =========================================================

def load_grammar(
    cursor,
    lesson_id,
):

    cursor.execute(
        """
        SELECT
            MaNguPhap,
            TenCauTruc,
            MoTa,
            CachDung,
            ViDuTiengTrung,
            ViDuPinyin,
            ViDuTiengViet,
            ThuTu,
            TrangThai

        FROM dbo.NguPhap

        WHERE
            MaBaiHoc = ?
            AND TrangThai = 'da_xuat_ban'

        ORDER BY
            ThuTu,
            MaNguPhap;
        """,
        lesson_id,
    )


    items = []


    for row in cursor.fetchall():

        items.append(
            {
                "id":
                    row[0],

                "structure":
                    clean_text(
                        row[1]
                    ),

                "description":
                    clean_text(
                        row[2]
                    ),

                "usage":
                    clean_text(
                        row[3]
                    ),

                "example_zh":
                    clean_text(
                        row[4]
                    ),

                "example_pinyin":
                    clean_text(
                        row[5]
                    ),

                "example_vi":
                    clean_text(
                        row[6]
                    ),

                "order":
                    row[7],

                "status":
                    row[8],
            }
        )


    return items


# =========================================================
# ĐỌC CHỮ HÁN CỦA BÀI
# =========================================================

def load_hanzi(
    cursor,
    lesson_id,
):

    cursor.execute(
        """
        SELECT
            ch.MaChuHan,
            ch.KyTu,
            ch.Pinyin,
            ch.NghiaTiengViet,
            ch.SoNet,
            ch.CachGhiNho,
            ch.ViDuTiengTrung,
            ch.ViDuPinyin,
            ch.ViDuTiengViet,
            ch.ThuTu,
            ch.TrangThai,

            bt.KyHieu,
            bt.TenBoThu

        FROM dbo.ChuHan AS ch

        LEFT JOIN dbo.BoThu AS bt
            ON bt.MaBoThu
            = ch.MaBoThu

        WHERE
            ch.MaBaiHoc = ?
            AND ch.TrangThai = 'da_xuat_ban'

        ORDER BY
            ch.ThuTu,
            ch.MaChuHan;
        """,
        lesson_id,
    )


    items = []


    for row in cursor.fetchall():

        items.append(
            {
                "id":
                    row[0],

                "character":
                    clean_text(
                        row[1]
                    ),

                "pinyin":
                    clean_text(
                        row[2]
                    ),

                "meaning":
                    clean_text(
                        row[3]
                    ),

                "stroke_count":
                    row[4],

                "memory_tip":
                    clean_text(
                        row[5]
                    ),

                "example_zh":
                    clean_text(
                        row[6]
                    ),

                "example_pinyin":
                    clean_text(
                        row[7]
                    ),

                "example_vi":
                    clean_text(
                        row[8]
                    ),

                "order":
                    row[9],

                "status":
                    row[10],

                "radical_symbol":
                    clean_text(
                        row[11]
                    ),

                "radical_name":
                    clean_text(
                        row[12]
                    ),
            }
        )


    return items


# =========================================================
# SINH CÂU TỪ VỰNG:
# CHỮ HÁN → NGHĨA
# =========================================================

def generate_vocab_meaning_questions(
    vocabulary,
):

    result = []

    all_meanings = [
        item["meaning"]
        for item
        in vocabulary
        if item["meaning"]
    ]


    for item in vocabulary:

        if (
            not item["hanzi"]
            or
            not item["meaning"]
        ):
            continue


        distractors = (
            choose_distractors(
                item["meaning"],
                all_meanings,
                3,
            )
        )


        if len(distractors) != 3:
            continue


        question = (
            make_multiple_choice(
                source_type="tu_vung",

                source_id=
                    item["id"],

                question_group=
                    "tu_vung_nghia",

                content=(
                    f'“{item["hanzi"]}” '
                    f'có nghĩa là gì?'
                ),

                correct_answer=
                    item["meaning"],

                distractors=
                    distractors,

                explanation=(
                    f'{item["hanzi"]} '
                    f'({item["pinyin"]}) '
                    f'có nghĩa là '
                    f'“{item["meaning"]}”.'
                ),
            )
        )


        if question:

            result.append(
                question
            )


    return result


# =========================================================
# SINH CÂU TỪ VỰNG:
# CHỮ HÁN → PINYIN
# =========================================================

def generate_vocab_pinyin_questions(
    vocabulary,
):

    result = []

    all_pinyin = [
        item["pinyin"]
        for item
        in vocabulary
        if item["pinyin"]
    ]


    for item in vocabulary:

        if (
            not item["hanzi"]
            or
            not item["pinyin"]
        ):
            continue


        distractors = (
            choose_distractors(
                item["pinyin"],
                all_pinyin,
                3,
            )
        )


        if len(distractors) != 3:
            continue


        question = (
            make_multiple_choice(
                source_type="tu_vung",

                source_id=
                    item["id"],

                question_group=
                    "tu_vung_pinyin",

                content=(
                    f'Pinyin đúng của '
                    f'“{item["hanzi"]}” '
                    f'là gì?'
                ),

                correct_answer=
                    item["pinyin"],

                distractors=
                    distractors,

                explanation=(
                    f'“{item["hanzi"]}” '
                    f'được đọc là '
                    f'{item["pinyin"]}.'
                ),
            )
        )


        if question:

            result.append(
                question
            )


    return result


# =========================================================
# SINH CÂU CHỮ HÁN:
# KÝ TỰ → PINYIN
# =========================================================

def generate_hanzi_pinyin_questions(
    hanzi_items,
):

    result = []

    all_pinyin = [
        item["pinyin"]
        for item
        in hanzi_items
        if item["pinyin"]
    ]


    for item in hanzi_items:

        if (
            not item["character"]
            or
            not item["pinyin"]
        ):
            continue


        distractors = (
            choose_distractors(
                item["pinyin"],
                all_pinyin,
                3,
            )
        )


        if len(distractors) != 3:
            continue


        question = (
            make_multiple_choice(
                source_type="chu_han",

                source_id=
                    item["id"],

                question_group=
                    "chu_han_pinyin",

                content=(
                    f'Pinyin của chữ '
                    f'“{item["character"]}” '
                    f'là gì?'
                ),

                correct_answer=
                    item["pinyin"],

                distractors=
                    distractors,

                explanation=(
                    f'Chữ '
                    f'“{item["character"]}” '
                    f'được đọc là '
                    f'{item["pinyin"]}.'
                ),
            )
        )


        if question:

            result.append(
                question
            )


    return result


# =========================================================
# SINH CÂU CHỮ HÁN:
# KÝ TỰ → NGHĨA
# =========================================================

def generate_hanzi_meaning_questions(
    hanzi_items,
):

    result = []

    all_meanings = [
        item["meaning"]
        for item
        in hanzi_items
        if item["meaning"]
    ]


    for item in hanzi_items:

        if (
            not item["character"]
            or
            not item["meaning"]
        ):
            continue


        distractors = (
            choose_distractors(
                item["meaning"],
                all_meanings,
                3,
            )
        )


        if len(distractors) != 3:
            continue


        question = (
            make_multiple_choice(
                source_type="chu_han",

                source_id=
                    item["id"],

                question_group=
                    "chu_han_nghia",

                content=(
                    f'Chữ '
                    f'“{item["character"]}” '
                    f'có nghĩa là gì?'
                ),

                correct_answer=
                    item["meaning"],

                distractors=
                    distractors,

                explanation=(
                    f'Chữ '
                    f'“{item["character"]}” '
                    f'({item["pinyin"]}) '
                    f'có nghĩa là '
                    f'“{item["meaning"]}”.'
                ),
            )
        )


        if question:

            result.append(
                question
            )


    return result


# =========================================================
# SINH CÂU NGỮ PHÁP:
# MÔ TẢ → CHỌN CẤU TRÚC
#
# Cách này an toàn hơn tự bịa câu điền từ.
# Script chỉ dùng đúng mô tả + tên cấu trúc
# đã có trong SQL.
# =========================================================

def generate_grammar_questions(
    grammar_items,
):

    result = []

    all_structures = [
        item["structure"]
        for item
        in grammar_items
        if item["structure"]
    ]


    for item in grammar_items:

        if not item["structure"]:
            continue


        description = (
            item["description"]
            or
            item["usage"]
        )


        if not description:
            continue


        distractors = (
            choose_distractors(
                item["structure"],
                all_structures,
                3,
            )
        )


        if len(distractors) != 3:
            continue


        explanation_parts = [
            f'Cấu trúc đúng là '
            f'“{item["structure"]}”.'
        ]


        if item["usage"]:

            explanation_parts.append(
                item["usage"]
            )


        if item["example_zh"]:

            example_text = (
                f'Ví dụ: '
                f'{item["example_zh"]}'
            )

            if item["example_vi"]:

                example_text += (
                    f' — '
                    f'{item["example_vi"]}'
                )

            explanation_parts.append(
                example_text
            )


        question = (
            make_multiple_choice(
                source_type="ngu_phap",

                source_id=
                    item["id"],

                question_group=
                    "ngu_phap_nhan_dien",

                content=(
                    "Cấu trúc ngữ pháp nào "
                    "phù hợp với mô tả sau?\n"
                    f"{description}"
                ),

                correct_answer=
                    item["structure"],

                distractors=
                    distractors,

                explanation=" ".join(
                    explanation_parts
                ),
            )
        )


        if question:

            result.append(
                question
            )


    return result


# =========================================================
# CHỌN 20 CÂU CÂN ĐỐI
#
# Mục tiêu cho Bài 1:
# - 8 câu nghĩa từ vựng
# - 4 câu pinyin từ vựng
# - 3 câu chữ Hán pinyin
# - 2 câu chữ Hán nghĩa
# - 3 câu ngữ pháp
#
# Nếu nhóm nào thiếu,
# script sẽ lấy bổ sung từ các nhóm còn lại.
# =========================================================

def select_questions(
    question_groups,
    target_count,
):

    plan = [
        (
            "vocab_meaning",
            8,
        ),
        (
            "vocab_pinyin",
            4,
        ),
        (
            "hanzi_pinyin",
            3,
        ),
        (
            "hanzi_meaning",
            2,
        ),
        (
            "grammar",
            3,
        ),
    ]


    selected = []

    used_keys = set()


    # =====================================================
    # LẤY THEO KẾ HOẠCH
    # =====================================================

    for (
        group_name,
        wanted_count,
    ) in plan:

        pool = list(
            question_groups.get(
                group_name,
                [],
            )
        )

        random.shuffle(
            pool
        )


        added = 0


        for question in pool:

            key = (
                question[
                    "question_group"
                ],
                question[
                    "source_id"
                ],
            )


            if key in used_keys:
                continue


            selected.append(
                question
            )

            used_keys.add(
                key
            )

            added += 1


            if (
                added
                >= wanted_count
            ):
                break


    # =====================================================
    # NẾU CHƯA ĐỦ 20
    # → LẤY BỔ SUNG
    # =====================================================

    if len(selected) < target_count:

        remaining = []


        for pool in (
            question_groups.values()
        ):

            for question in pool:

                key = (
                    question[
                        "question_group"
                    ],
                    question[
                        "source_id"
                    ],
                )


                if key in used_keys:
                    continue


                remaining.append(
                    question
                )


        random.shuffle(
            remaining
        )


        for question in remaining:

            if (
                len(selected)
                >= target_count
            ):
                break


            key = (
                question[
                    "question_group"
                ],
                question[
                    "source_id"
                ],
            )


            if key in used_keys:
                continue


            selected.append(
                question
            )

            used_keys.add(
                key
            )


    # =====================================================
    # GÁN THỨ TỰ
    # =====================================================

    for index, question in enumerate(
        selected,
        start=1,
    ):

        question["order"] = index


    return selected[
        :target_count
    ]


# =========================================================
# GHI CSV UTF-8-SIG
#
# utf-8-sig giúp Excel Windows
# mở tiếng Việt + tiếng Trung đúng hơn.
# =========================================================

def write_csv(
    output_path,
    lesson,
    questions,
):

    fieldnames = [
        "hsk_level",
        "lesson_id",
        "lesson_order",
        "lesson_title",
        "order",
        "source_type",
        "source_id",
        "question_group",
        "question_type",
        "skill",
        "content",
        "passage",
        "choice_1",
        "choice_2",
        "choice_3",
        "choice_4",
        "correct_choice",
        "answer_text",
        "explanation",
        "score",
    ]


    with output_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()


        for question in questions:

            row = {
                "hsk_level":
                    lesson[
                        "hsk_level"
                    ],

                "lesson_id":
                    lesson[
                        "lesson_id"
                    ],

                "lesson_order":
                    lesson[
                        "lesson_order"
                    ],

                "lesson_title":
                    lesson[
                        "lesson_title"
                    ],

                **question,
            }


            writer.writerow(
                row
            )


# =========================================================
# IN PREVIEW RA TERMINAL
# =========================================================

def print_preview(
    lesson,
    questions,
):

    print()
    print(
        "=" * 70
    )

    print(
        "PREVIEW CAU HOI - MOC HAN"
    )

    print(
        "=" * 70
    )

    print(
        (
            f"HSK {lesson['hsk_level']} "
            f"- Bai {lesson['lesson_order']} "
            f"- {lesson['lesson_title']}"
        )
    )

    print(
        (
            f"So cau duoc sinh: "
            f"{len(questions)}"
        )
    )

    print(
        "-" * 70
    )


    for question in questions:

        print()

        print(
            (
                f"[{question['order']}] "
                f"{question['content']}"
            )
        )

        print(
            (
                f"    A. "
                f"{question['choice_1']}"
            )
        )

        print(
            (
                f"    B. "
                f"{question['choice_2']}"
            )
        )

        print(
            (
                f"    C. "
                f"{question['choice_3']}"
            )
        )

        print(
            (
                f"    D. "
                f"{question['choice_4']}"
            )
        )

        print(
            (
                f"    Dap an dung: "
                f"{question['correct_choice']} "
                f"- "
                f"{question['answer_text']}"
            )
        )

        print(
            (
                f"    Nguon: "
                f"{question['source_type']} "
                f"#{question['source_id']}"
            )
        )


# =========================================================
# MAIN
# =========================================================

def main():

    random.seed(
        RANDOM_SEED
    )


    print(
        "Dang ket noi HocTiengTrungDB..."
    )


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # ĐỌC DỮ LIỆU
            # =================================================

            lesson = load_lesson(
                cursor,
                LESSON_ID,
            )


            vocabulary = load_vocabulary(
                cursor,
                LESSON_ID,
            )


            grammar_items = load_grammar(
                cursor,
                LESSON_ID,
            )


            hanzi_items = load_hanzi(
                cursor,
                LESSON_ID,
            )


    # =====================================================
    # KIỂM TRA SỐ LƯỢNG
    # =====================================================

    print()
    print(
        "Du lieu doc tu SQL:"
    )

    print(
        (
            f"  Tu vung : "
            f"{len(vocabulary)}"
        )
    )

    print(
        (
            f"  Ngu phap: "
            f"{len(grammar_items)}"
        )
    )

    print(
        (
            f"  Chu Han : "
            f"{len(hanzi_items)}"
        )
    )


    if not vocabulary:

        raise RuntimeError(
            (
                "Bai hoc khong co "
                "tu vung da duyet."
            )
        )


    # =====================================================
    # SINH CÁC NHÓM CÂU HỎI
    # =====================================================

    question_groups = {
        "vocab_meaning":
            generate_vocab_meaning_questions(
                vocabulary
            ),

        "vocab_pinyin":
            generate_vocab_pinyin_questions(
                vocabulary
            ),

        "hanzi_pinyin":
            generate_hanzi_pinyin_questions(
                hanzi_items
            ),

        "hanzi_meaning":
            generate_hanzi_meaning_questions(
                hanzi_items
            ),

        "grammar":
            generate_grammar_questions(
                grammar_items
            ),
    }


    print()
    print(
        "So cau co the sinh:"
    )


    for (
        group_name,
        pool,
    ) in question_groups.items():

        print(
            (
                f"  {group_name:<15}: "
                f"{len(pool)}"
            )
        )


    # =====================================================
    # CHỌN 20 CÂU
    # =====================================================

    questions = select_questions(
        question_groups,
        TARGET_QUESTION_COUNT,
    )


    if not questions:

        raise RuntimeError(
            (
                "Khong sinh duoc "
                "cau hoi nao."
            )
        )


    # =====================================================
    # TÊN FILE
    # =====================================================

    output_name = (
        f"hsk{lesson['hsk_level']}"
        f"_bai{lesson['lesson_order']}"
        f"_questions.csv"
    )


    output_path = (
        PREVIEW_DIR
        / output_name
    )


    # =====================================================
    # GHI FILE
    # =====================================================

    write_csv(
        output_path,
        lesson,
        questions,
    )


    # =====================================================
    # TERMINAL PREVIEW
    # =====================================================

    print_preview(
        lesson,
        questions,
    )


    print()
    print(
        "=" * 70
    )

    print(
        "DA TAO PREVIEW THANH CONG"
    )

    print(
        "=" * 70
    )

    print(
        f"File: {output_path}"
    )

    print()
    print(
        "LUU Y:"
    )

    print(
        (
            "- Script nay CHUA ghi "
            "vao BaiTap/CauHoi/"
            "LuaChonCauHoi."
        )
    )

    print(
        (
            "- Hay mo file CSV "
            "kiem tra noi dung "
            "truoc khi import."
        )
    )


if __name__ == "__main__":

    main()