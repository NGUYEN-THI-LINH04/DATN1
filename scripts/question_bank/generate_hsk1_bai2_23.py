# =========================================================
# MỘC HÁN
# SINH NGÂN HÀNG CÂU HỎI HSK1
# BÀI 2 -> BÀI 23
#
# CHỈ ĐỌC SQL
# KHÔNG INSERT / UPDATE / DELETE
#
# OUTPUT DUY NHẤT:
# preview/hsk1_bai2_23_questions.csv
# =========================================================

from __future__ import annotations

import csv
import json
import random
import re
import sys

from contextlib import closing
from pathlib import Path


# =========================================================
# PROJECT ROOT
# =========================================================

CURRENT_FILE = Path(__file__).resolve()

PROJECT_ROOT = CURRENT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from database import get_connection


# =========================================================
# CONFIG
# =========================================================

HSK_LEVEL = 1

START_LESSON_ORDER = 2

END_LESSON_ORDER = 23

TARGET_PER_LESSON = 20

RANDOM_SEED = 20261008


PREVIEW_DIR = (
    CURRENT_FILE.parent
    / "preview"
)

PREVIEW_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUTPUT_FILE = (
    PREVIEW_DIR
    / "hsk1_bai2_23_questions.csv"
)


# =========================================================
# HELPER
# =========================================================

def clean_text(value):

    if value is None:
        return ""

    return str(value).strip()


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


def choose_distractors(
    correct,
    candidates,
    count=3,
):

    correct_key = clean_text(
        correct
    ).casefold()

    pool = []

    for item in unique_values(
        candidates
    ):

        if item.casefold() == correct_key:
            continue

        pool.append(
            item
        )


    if len(pool) < count:
        return []


    return random.sample(
        pool,
        count,
    )


# =========================================================
# TẠO CÂU CHỌN MỘT
# =========================================================

def make_mcq(
    *,
    source_type,
    source_id,
    group,
    content,
    correct_answer,
    distractors,
    explanation,
    skill="doc",
):

    choices = [
        clean_text(
            correct_answer
        ),
        *[
            clean_text(x)
            for x in distractors
        ],
    ]


    if len(
        unique_values(
            choices
        )
    ) != 4:

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
            group,

        "question_type":
            "chon_mot",

        "skill":
            skill,

        "content":
            content,

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

        "choice_5":
            "",

        "choice_6":
            "",

        "correct_choices":
            str(
                correct_index
            ),

        "answer_json":
            "",

        "explanation":
            explanation,

        "score":
            1,
    }


# =========================================================
# ĐỌC DANH SÁCH BÀI HSK1 - BÀI 2 -> 23
#
# Không giả định MaBaiHoc = số thứ tự bài.
# =========================================================

def load_lessons(
    cursor,
):

    cursor.execute(
        """
        SELECT
            bh.MaBaiHoc,
            bh.SoThuTuBai,
            bh.TieuDe,
            kh.MaCapDo,
            kh.TieuDe

        FROM dbo.BaiHoc AS bh

        INNER JOIN dbo.KhoaHoc AS kh
            ON kh.MaKhoaHoc
            = bh.MaKhoaHoc

        WHERE
            kh.MaCapDo = ?
            AND bh.SoThuTuBai
                BETWEEN ? AND ?

        ORDER BY
            bh.SoThuTuBai,
            bh.MaBaiHoc;
        """,

        HSK_LEVEL,
        START_LESSON_ORDER,
        END_LESSON_ORDER,
    )


    lessons = []


    for row in cursor.fetchall():

        lessons.append(
            {
                "lesson_id":
                    row[0],

                "lesson_order":
                    row[1],

                "lesson_title":
                    clean_text(
                        row[2]
                    ),

                "hsk_level":
                    row[3],

                "course_title":
                    clean_text(
                        row[4]
                    ),
            }
        )


    return lessons


# =========================================================
# TỪ VỰNG THEO BÀI
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


    result = []


    for row in cursor.fetchall():

        result.append(
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


    return result


# =========================================================
# NGỮ PHÁP THEO BÀI
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
            ThuTu

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


    result = []


    for row in cursor.fetchall():

        result.append(
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
            }
        )


    return result


# =========================================================
# CHỮ HÁN THEO BÀI
# =========================================================

def load_hanzi(
    cursor,
    lesson_id,
):

    cursor.execute(
        """
        SELECT
            MaChuHan,
            KyTu,
            Pinyin,
            NghiaTiengViet,
            SoNet,
            ViDuTiengTrung,
            ViDuPinyin,
            ViDuTiengViet,
            ThuTu

        FROM dbo.ChuHan

        WHERE
            MaBaiHoc = ?
            AND TrangThai = 'da_xuat_ban'

        ORDER BY
            ThuTu,
            MaChuHan;
        """,
        lesson_id,
    )


    result = []


    for row in cursor.fetchall():

        result.append(
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

                "example_zh":
                    clean_text(
                        row[5]
                    ),

                "example_pinyin":
                    clean_text(
                        row[6]
                    ),

                "example_vi":
                    clean_text(
                        row[7]
                    ),

                "order":
                    row[8],
            }
        )


    return result


# =========================================================
# CHỌN ITEM CHƯA DÙNG
# =========================================================

def pick_unused(
    items,
    count,
    used_ids,
):

    available = [
        item
        for item in items
        if item["id"]
        not in used_ids
    ]


    random.shuffle(
        available
    )


    selected = available[
        :count
    ]


    for item in selected:

        used_ids.add(
            item["id"]
        )


    return selected


# =========================================================
# TỪ VỰNG - NGHĨA
# =========================================================

def generate_vocab_meaning(
    selected,
    all_vocab,
):

    result = []

    meanings = [
        item["meaning"]
        for item in all_vocab
        if item["meaning"]
    ]


    for item in selected:

        if (
            not item["hanzi"]
            or
            not item["meaning"]
        ):
            continue


        distractors = (
            choose_distractors(
                item["meaning"],
                meanings,
                3,
            )
        )


        if len(distractors) != 3:
            continue


        question = make_mcq(
            source_type="tu_vung",

            source_id=
                item["id"],

            group=
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


        if question:
            result.append(
                question
            )


    return result


# =========================================================
# TỪ VỰNG - PINYIN
# =========================================================

def generate_vocab_pinyin(
    selected,
    all_vocab,
):

    result = []

    pinyin_values = [
        item["pinyin"]
        for item in all_vocab
        if item["pinyin"]
    ]


    for item in selected:

        if (
            not item["hanzi"]
            or
            not item["pinyin"]
        ):
            continue


        distractors = (
            choose_distractors(
                item["pinyin"],
                pinyin_values,
                3,
            )
        )


        if len(distractors) != 3:
            continue


        question = make_mcq(
            source_type="tu_vung",

            source_id=
                item["id"],

            group=
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


        if question:
            result.append(
                question
            )


    return result


# =========================================================
# TỪ VỰNG - NGHĨA -> CHỮ HÁN
# =========================================================

def generate_reverse_vocab(
    selected,
    all_vocab,
):

    result = []

    characters = [
        item["hanzi"]
        for item in all_vocab
        if item["hanzi"]
    ]


    for item in selected:

        if (
            not item["meaning"]
            or
            not item["hanzi"]
        ):
            continue


        distractors = (
            choose_distractors(
                item["hanzi"],
                characters,
                3,
            )
        )


        if len(distractors) != 3:
            continue


        question = make_mcq(
            source_type="tu_vung",

            source_id=
                item["id"],

            group=
                "tu_vung_chon_chu",

            content=(
                f'Từ nào có nghĩa là '
                f'“{item["meaning"]}”?'
            ),

            correct_answer=
                item["hanzi"],

            distractors=
                distractors,

            explanation=(
                f'{item["hanzi"]} '
                f'({item["pinyin"]}) '
                f'có nghĩa là '
                f'“{item["meaning"]}”.'
            ),
        )


        if question:
            result.append(
                question
            )


    return result


# =========================================================
# NGỮ PHÁP - NHẬN DIỆN
# =========================================================

def generate_grammar_recognition(
    selected,
    all_grammar,
):

    result = []

    structures = [
        item["structure"]
        for item in all_grammar
        if item["structure"]
    ]


    for item in selected:

        description = (
            item["description"]
            or
            item["usage"]
        )


        if (
            not item["structure"]
            or
            not description
        ):
            continue


        distractors = (
            choose_distractors(
                item["structure"],
                structures,
                3,
            )
        )


        if len(distractors) != 3:
            continue


        question = make_mcq(
            source_type="ngu_phap",

            source_id=
                item["id"],

            group=
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

            explanation=(
                f'Cấu trúc đúng là '
                f'“{item["structure"]}”. '
                f'{item["usage"]}'
            ),
        )


        if question:
            result.append(
                question
            )


    return result


# =========================================================
# TÁCH CHỮ TRUNG QUỐC TRONG CẤU TRÚC
# =========================================================

def extract_chinese_tokens(
    text,
):

    return re.findall(
        r"[\u4e00-\u9fff]+",
        text or "",
    )


# =========================================================
# NGỮ PHÁP - ĐIỀN TỪ
# =========================================================

def generate_grammar_fill(
    selected,
):

    result = []


    for item in selected:

        sentence = (
            item["example_zh"]
        )


        if not sentence:
            continue


        tokens = extract_chinese_tokens(
            item["structure"]
        )


        answer = None


        for token in tokens:

            if token in sentence:

                answer = token
                break


        if not answer:
            continue


        blank_sentence = sentence.replace(
            answer,
            "___",
            1,
        )


        if blank_sentence == sentence:
            continue


        result.append(
            {
                "source_type":
                    "ngu_phap",

                "source_id":
                    item["id"],

                "question_group":
                    "ngu_phap_dien_tu",

                "question_type":
                    "dien_tu",

                "skill":
                    "doc",

                "content":
                    (
                        "Điền từ thích hợp "
                        "vào chỗ trống:\n"
                        f"{blank_sentence}"
                    ),

                "passage":
                    "",

                "choice_1":
                    "",

                "choice_2":
                    "",

                "choice_3":
                    "",

                "choice_4":
                    "",

                "choice_5":
                    "",

                "choice_6":
                    "",

                "correct_choices":
                    "",

                "answer_json":
                    json.dumps(
                        {
                            "answers": [
                                answer
                            ]
                        },
                        ensure_ascii=False,
                    ),

                "explanation":
                    (
                        f'Câu đầy đủ là: '
                        f'{sentence} '
                        f'Cấu trúc: '
                        f'{item["structure"]}.'
                    ),

                "score":
                    1,
            }
        )


    return result


# =========================================================
# CHỮ HÁN
# =========================================================

def generate_hanzi_questions(
    selected,
    all_hanzi,
):

    result = []

    meanings = [
        item["meaning"]
        for item in all_hanzi
        if item["meaning"]
    ]


    for item in selected:

        if (
            not item["character"]
            or
            not item["meaning"]
        ):
            continue


        distractors = (
            choose_distractors(
                item["meaning"],
                meanings,
                3,
            )
        )


        if len(distractors) != 3:
            continue


        question = make_mcq(
            source_type="chu_han",

            source_id=
                item["id"],

            group=
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
                f'“{item["character"]}” '
                f'đọc là '
                f'{item["pinyin"]}, '
                f'có nghĩa là '
                f'“{item["meaning"]}”.'
            ),
        )


        if question:
            result.append(
                question
            )


    return result


# =========================================================
# ĐÚNG / SAI
# =========================================================

def generate_true_false(
    selected,
    all_vocab,
):

    result = []

    meanings = [
        item["meaning"]
        for item in all_vocab
        if item["meaning"]
    ]


    for index, item in enumerate(
        selected
    ):

        if (
            not item["hanzi"]
            or
            not item["meaning"]
        ):
            continue


        make_true = (
            index % 2 == 0
        )


        if make_true:

            shown_meaning = (
                item["meaning"]
            )

            answer = "dung"

            explanation = (
                f'{item["hanzi"]} '
                f'({item["pinyin"]}) '
                f'có nghĩa là '
                f'“{item["meaning"]}”.'
            )

        else:

            wrong = choose_distractors(
                item["meaning"],
                meanings,
                1,
            )


            if not wrong:
                continue


            shown_meaning = (
                wrong[0]
            )

            answer = "sai"

            explanation = (
                f'Phát biểu sai. '
                f'{item["hanzi"]} '
                f'({item["pinyin"]}) '
                f'có nghĩa là '
                f'“{item["meaning"]}”, '
                f'không phải '
                f'“{shown_meaning}”.'
            )


        result.append(
            {
                "source_type":
                    "tu_vung",

                "source_id":
                    item["id"],

                "question_group":
                    "tu_vung_dung_sai",

                "question_type":
                    "dung_sai",

                "skill":
                    "doc",

                "content":
                    (
                        f'“{item["hanzi"]}” '
                        f'có nghĩa là '
                        f'“{shown_meaning}”.'
                    ),

                "passage":
                    "",

                "choice_1":
                    "",

                "choice_2":
                    "",

                "choice_3":
                    "",

                "choice_4":
                    "",

                "choice_5":
                    "",

                "choice_6":
                    "",

                "correct_choices":
                    "",

                "answer_json":
                    json.dumps(
                        {
                            "answer":
                                answer
                        },
                        ensure_ascii=False,
                    ),

                "explanation":
                    explanation,

                "score":
                    1,
            }
        )


    return result


# =========================================================
# SẮP XẾP CÂU
# =========================================================

def generate_sorting_question(
    grammar_items,
):

    for item in grammar_items:

        sentence = (
            item["example_zh"]
        )


        if not sentence:
            continue


        tokens = extract_chinese_tokens(
            item["structure"]
        )


        for token in tokens:

            if token not in sentence:
                continue


            before, after = sentence.split(
                token,
                1,
            )


            before = (
                before
                .strip()
                .strip(
                    "。！？!?，,"
                )
            )

            after = (
                after
                .strip()
                .strip(
                    "。！？!?，,"
                )
            )


            if (
                not before
                or
                not after
            ):
                continue


            parts = [
                before,
                token,
                after,
            ]


            return {
                "source_type":
                    "ngu_phap",

                "source_id":
                    item["id"],

                "question_group":
                    "ngu_phap_sap_xep",

                "question_type":
                    "sap_xep",

                "skill":
                    "doc",

                "content":
                    (
                        "Sắp xếp các thành phần "
                        "thành câu đúng."
                    ),

                "passage":
                    "",

                "choice_1":
                    "",

                "choice_2":
                    "",

                "choice_3":
                    "",

                "choice_4":
                    "",

                "choice_5":
                    "",

                "choice_6":
                    "",

                "correct_choices":
                    "",

                "answer_json":
                    json.dumps(
                        {
                            "items":
                                parts
                        },
                        ensure_ascii=False,
                    ),

                "explanation":
                    (
                        f'Câu đúng là: '
                        f'{sentence}'
                    ),

                "score":
                    1,
            }


    return None


# =========================================================
# SINH CÂU CHO MỘT BÀI
# =========================================================

def build_questions_for_lesson(
    lesson,
    vocabulary,
    grammar,
    hanzi,
):

    # Seed riêng từng bài để kết quả ổn định.
    random.seed(
        RANDOM_SEED
        + int(
            lesson["lesson_order"]
        )
    )


    questions = []


    used_vocab = set()

    used_grammar = set()

    used_hanzi = set()


    # =====================================================
    # KẾ HOẠCH CHÍNH
    #
    # Nếu bài thiếu dữ liệu,
    # phần cuối sẽ tự bổ sung.
    # =====================================================


    # 5 câu nghĩa từ vựng
    selected = pick_unused(
        vocabulary,
        5,
        used_vocab,
    )

    questions.extend(
        generate_vocab_meaning(
            selected,
            vocabulary,
        )
    )


    # 3 câu Pinyin
    selected = pick_unused(
        vocabulary,
        3,
        used_vocab,
    )

    questions.extend(
        generate_vocab_pinyin(
            selected,
            vocabulary,
        )
    )


    # 2 câu nghĩa -> chữ Hán
    selected = pick_unused(
        vocabulary,
        2,
        used_vocab,
    )

    questions.extend(
        generate_reverse_vocab(
            selected,
            vocabulary,
        )
    )


    # 3 câu nhận diện ngữ pháp
    selected = pick_unused(
        grammar,
        3,
        used_grammar,
    )

    questions.extend(
        generate_grammar_recognition(
            selected,
            grammar,
        )
    )


    # 2 câu điền từ
    selected = pick_unused(
        grammar,
        2,
        used_grammar,
    )

    questions.extend(
        generate_grammar_fill(
            selected
        )
    )


    # 2 chữ Hán
    selected = pick_unused(
        hanzi,
        2,
        used_hanzi,
    )

    questions.extend(
        generate_hanzi_questions(
            selected,
            hanzi,
        )
    )


    # 2 đúng sai
    selected = pick_unused(
        vocabulary,
        2,
        used_vocab,
    )

    questions.extend(
        generate_true_false(
            selected,
            vocabulary,
        )
    )


    # 1 sắp xếp
    sorting = generate_sorting_question(
        [
            item
            for item in grammar
            if item["id"]
            not in used_grammar
        ]
        or grammar
    )


    if sorting:

        questions.append(
            sorting
        )


    # =====================================================
    # BỔ SUNG NẾU CHƯA ĐỦ 20
    #
    # Cho phép dùng cùng source ở dạng câu khác
    # nhưng không tạo câu hoàn toàn trùng nội dung.
    # =====================================================

    candidate_extras = []


    candidate_extras.extend(
        generate_vocab_meaning(
            vocabulary,
            vocabulary,
        )
    )


    candidate_extras.extend(
        generate_vocab_pinyin(
            vocabulary,
            vocabulary,
        )
    )


    candidate_extras.extend(
        generate_reverse_vocab(
            vocabulary,
            vocabulary,
        )
    )


    candidate_extras.extend(
        generate_grammar_recognition(
            grammar,
            grammar,
        )
    )


    candidate_extras.extend(
        generate_grammar_fill(
            grammar
        )
    )


    candidate_extras.extend(
        generate_hanzi_questions(
            hanzi,
            hanzi,
        )
    )


    # =====================================================
    # KHÔNG CHO TRÙNG NỘI DUNG CÂU HỎI
    # =====================================================

    existing_contents = {
        clean_text(
            item["content"]
        ).casefold()
        for item in questions
    }


    random.shuffle(
        candidate_extras
    )


    for question in candidate_extras:

        if len(
            questions
        ) >= TARGET_PER_LESSON:
            break


        content_key = (
            clean_text(
                question["content"]
            )
            .casefold()
        )


        if content_key in existing_contents:
            continue


        questions.append(
            question
        )

        existing_contents.add(
            content_key
        )


    # =====================================================
    # GIỚI HẠN 20
    # =====================================================

    questions = questions[
        :TARGET_PER_LESSON
    ]


    random.shuffle(
        questions
    )


    for index, question in enumerate(
        questions,
        start=1,
    ):

        question["order"] = (
            index
        )


    return questions


# =========================================================
# GHI 1 FILE CSV DUY NHẤT
# =========================================================

def write_csv(
    rows,
):

    columns = [
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
        "choice_5",
        "choice_6",

        "correct_choices",

        "answer_json",

        "explanation",

        "score",
    ]


    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=columns,
        )

        writer.writeheader()


        for row in rows:

            writer.writerow(
                row
            )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print(
        "=" * 72
    )

    print(
        "MOC HAN - GENERATE HSK1 BAI 2 -> 23"
    )

    print(
        "=" * 72
    )


    all_rows = []

    lesson_summaries = []


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            lessons = load_lessons(
                cursor
            )


            print()
            print(
                (
                    "So bai tim thay: "
                    f"{len(lessons)}"
                )
            )


            if not lessons:

                raise RuntimeError(
                    (
                        "Không tìm thấy bài "
                        "HSK1 từ Bài 2 đến Bài 23."
                    )
                )


            for lesson in lessons:

                lesson_id = (
                    lesson[
                        "lesson_id"
                    ]
                )


                vocabulary = (
                    load_vocabulary(
                        cursor,
                        lesson_id,
                    )
                )


                grammar = (
                    load_grammar(
                        cursor,
                        lesson_id,
                    )
                )


                hanzi = (
                    load_hanzi(
                        cursor,
                        lesson_id,
                    )
                )


                questions = (
                    build_questions_for_lesson(
                        lesson,
                        vocabulary,
                        grammar,
                        hanzi,
                    )
                )


                type_counts = {}


                for question in questions:

                    type_name = (
                        question[
                            "question_type"
                        ]
                    )

                    type_counts[
                        type_name
                    ] = (
                        type_counts.get(
                            type_name,
                            0,
                        )
                        + 1
                    )


                    all_rows.append(
                        {
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
                    )


                lesson_summaries.append(
                    {
                        "lesson":
                            lesson[
                                "lesson_order"
                            ],

                        "title":
                            lesson[
                                "lesson_title"
                            ],

                        "vocab":
                            len(
                                vocabulary
                            ),

                        "grammar":
                            len(
                                grammar
                            ),

                        "hanzi":
                            len(
                                hanzi
                            ),

                        "questions":
                            len(
                                questions
                            ),

                        "types":
                            type_counts,
                    }
                )


    # =====================================================
    # WRITE
    # =====================================================

    write_csv(
        all_rows
    )


    # =====================================================
    # SUMMARY
    # =====================================================

    print()
    print(
        "-" * 72
    )

    print(
        "KET QUA TUNG BAI"
    )

    print(
        "-" * 72
    )


    incomplete = []


    for item in lesson_summaries:

        print()
        print(
            (
                f"Bai {item['lesson']:>2}: "
                f"{item['title']}"
            )
        )

        print(
            (
                f"  Tu vung : "
                f"{item['vocab']}"
            )
        )

        print(
            (
                f"  Ngu phap: "
                f"{item['grammar']}"
            )
        )

        print(
            (
                f"  Chu Han : "
                f"{item['hanzi']}"
            )
        )

        print(
            (
                f"  Cau hoi : "
                f"{item['questions']}"
            )
        )

        print(
            (
                f"  Loai    : "
                f"{item['types']}"
            )
        )


        if (
            item["questions"]
            < TARGET_PER_LESSON
        ):

            incomplete.append(
                item
            )


    print()
    print(
        "=" * 72
    )

    print(
        "TAO PREVIEW HSK1 BAI 2 -> 23 THANH CONG"
    )

    print(
        "=" * 72
    )


    print(
        (
            f"Tong so bai: "
            f"{len(lesson_summaries)}"
        )
    )

    print(
        (
            f"Tong so cau: "
            f"{len(all_rows)}"
        )
    )

    print(
        (
            f"File duy nhat:"
            f"\n{OUTPUT_FILE}"
        )
    )


    if incomplete:

        print()
        print(
            "CAN KIEM TRA:"
        )

        for item in incomplete:

            print(
                (
                    f"  - Bai "
                    f"{item['lesson']}: "
                    f"chi sinh duoc "
                    f"{item['questions']} cau."
                )
            )

    else:

        print()
        print(
            (
                "Tat ca bai deu sinh du "
                f"{TARGET_PER_LESSON} cau."
            )
        )


    print()
    print(
        (
            "CHUA CO DU LIEU NAO "
            "DUOC GHI VAO SQL."
        )
    )


if __name__ == "__main__":

    main()