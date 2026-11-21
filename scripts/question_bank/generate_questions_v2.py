# =========================================================
# MỘC HÁN
# SINH PREVIEW CÂU HỎI V2 TỪ DỮ LIỆU BÀI HỌC
#
# CHỈ ĐỌC SQL
# KHÔNG INSERT / UPDATE / DELETE
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

LESSON_ID = 1

TARGET_COUNT = 20

RANDOM_SEED = 20261008


PREVIEW_DIR = (
    CURRENT_FILE.parent
    / "preview"
)

PREVIEW_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


random.seed(
    RANDOM_SEED
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
# THÔNG TIN BÀI
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
            "Không tìm thấy bài học."
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

        "hsk_level":
            row[3],

        "course_title":
            clean_text(
                row[4]
            ),
    }


# =========================================================
# TỪ VỰNG
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
# NGỮ PHÁP
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
# CHỮ HÁN
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
# CHỌN SOURCE KHÔNG TRÙNG
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
# 1. NGHĨA TỪ VỰNG
# =========================================================

def generate_vocab_meaning(
    selected,
    all_vocab,
):

    questions = []

    meanings = [
        x["meaning"]
        for x in all_vocab
    ]


    for item in selected:

        distractors = (
            choose_distractors(
                item["meaning"],
                meanings,
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

            questions.append(
                question
            )


    return questions


# =========================================================
# 2. PINYIN TỪ VỰNG
# =========================================================

def generate_vocab_pinyin(
    selected,
    all_vocab,
):

    questions = []

    pinyin_values = [
        x["pinyin"]
        for x in all_vocab
    ]


    for item in selected:

        distractors = (
            choose_distractors(
                item["pinyin"],
                pinyin_values,
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

            questions.append(
                question
            )


    return questions


# =========================================================
# 3. NGHĨA → CHỌN CHỮ HÁN
# =========================================================

def generate_reverse_vocab(
    selected,
    all_vocab,
):

    questions = []

    characters = [
        x["hanzi"]
        for x in all_vocab
    ]


    for item in selected:

        distractors = (
            choose_distractors(
                item["hanzi"],
                characters,
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

            questions.append(
                question
            )


    return questions


# =========================================================
# 4. NGỮ PHÁP NHẬN DIỆN
# =========================================================

def generate_grammar_recognition(
    selected,
    all_grammar,
):

    questions = []

    structures = [
        x["structure"]
        for x in all_grammar
    ]


    for item in selected:

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
                structures,
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

            questions.append(
                question
            )


    return questions


# =========================================================
# TÌM THÀNH PHẦN TIẾNG TRUNG TRONG
# TÊN CẤU TRÚC
#
# Ví dụ:
# A + 是 + B
# → 是
#
# 很 + tính từ
# → 很
# =========================================================

def extract_chinese_tokens(
    text,
):

    return re.findall(
        r"[\u4e00-\u9fff]+",
        text or "",
    )


# =========================================================
# 5. NGỮ PHÁP ĐIỀN TỪ
# =========================================================

def generate_grammar_fill(
    selected,
):

    questions = []


    for item in selected:

        sentence = (
            item["example_zh"]
        )


        if not sentence:
            continue


        tokens = (
            extract_chinese_tokens(
                item["structure"]
            )
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


        # Nếu thay xong vẫn y nguyên
        if blank_sentence == sentence:
            continue


        answer_json = json.dumps(
            {
                "answers": [
                    answer
                ]
            },
            ensure_ascii=False,
        )


        questions.append(
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
                    answer_json,

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


    return questions


# =========================================================
# 6. CHỮ HÁN
# =========================================================

def generate_hanzi_questions(
    selected,
    all_hanzi,
):

    result = []

    meanings = [
        x["meaning"]
        for x in all_hanzi
        if x["meaning"]
    ]


    for item in selected:

        if (
            not item["meaning"]
            or
            not item["character"]
        ):
            continue


        distractors = (
            choose_distractors(
                item["meaning"],
                meanings,
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
# 7. ĐÚNG / SAI TỪ VỰNG
# =========================================================

def generate_true_false(
    selected,
    all_vocab,
):

    questions = []


    meanings = [
        x["meaning"]
        for x in all_vocab
        if x["meaning"]
    ]


    for index, item in enumerate(
        selected
    ):

        # xen kẽ 1 câu đúng, 1 câu sai
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

            wrong = (
                choose_distractors(
                    item["meaning"],
                    meanings,
                    1,
                )
            )


            if not wrong:
                continue


            shown_meaning = wrong[0]

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


        answer_json = json.dumps(
            {
                "answer":
                    answer
            },
            ensure_ascii=False,
        )


        questions.append(
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
                    answer_json,

                "explanation":
                    explanation,

                "score":
                    1,
            }
        )


    return questions


# =========================================================
# 8. SẮP XẾP CÂU
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


        tokens = (
            extract_chinese_tokens(
                item["structure"]
            )
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
                .strip("。！？!?，,")
            )

            after = (
                after
                .strip()
                .strip("。！？!?，,")
            )


            if (
                not before
                or
                not after
            ):
                continue


            items = [
                before,
                token,
                after,
            ]


            answer_json = (
                json.dumps(
                    {
                        "items":
                            items
                    },
                    ensure_ascii=False,
                )
            )


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
                    answer_json,

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
# BUILD 20 QUESTIONS
# =========================================================

def build_questions(
    vocabulary,
    grammar,
    hanzi,
):

    questions = []


    used_vocab = set()

    used_grammar = set()

    used_hanzi = set()


    # =====================================================
    # 5 câu nghĩa từ vựng
    # =====================================================

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


    # =====================================================
    # 3 câu Pinyin từ vựng
    # =====================================================

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


    # =====================================================
    # 2 câu nghĩa → chọn chữ
    # =====================================================

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


    # =====================================================
    # 3 câu nhận diện ngữ pháp
    # =====================================================

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


    # =====================================================
    # 2 câu điền từ ngữ pháp
    # =====================================================

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


    # =====================================================
    # 2 câu Chữ Hán
    # =====================================================

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


    # =====================================================
    # 2 câu Đúng/Sai
    # =====================================================

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


    # =====================================================
    # 1 câu sắp xếp
    # =====================================================

    sorting = (
        generate_sorting_question(
            [
                item
                for item in grammar
                if item["id"]
                not in used_grammar
            ]
            or grammar
        )
    )


    if sorting:

        questions.append(
            sorting
        )


    # =====================================================
    # Nếu vì dữ liệu thiếu làm chưa đủ 20,
    # bổ sung bằng câu nghĩa từ vựng/chữ Hán
    # =====================================================

    if len(questions) < TARGET_COUNT:

        extras = []


        for item in vocabulary:

            if item["id"] in used_vocab:
                continue

            extra = generate_vocab_meaning(
                [item],
                vocabulary,
            )

            extras.extend(
                extra
            )


        for item in hanzi:

            if item["id"] in used_hanzi:
                continue

            extra = generate_hanzi_questions(
                [item],
                hanzi,
            )

            extras.extend(
                extra
            )


        for question in extras:

            if len(questions) >= TARGET_COUNT:
                break

            questions.append(
                question
            )


    questions = questions[
        :TARGET_COUNT
    ]


    # =====================================================
    # Xáo trộn toàn bộ bài để không gom cùng loại
    # =====================================================

    random.shuffle(
        questions
    )


    for index, question in enumerate(
        questions,
        start=1,
    ):

        question["order"] = index


    return questions


# =========================================================
# WRITE CSV
# =========================================================

def write_csv(
    path,
    lesson,
    questions,
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


    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=columns,
        )

        writer.writeheader()


        for question in questions:

            writer.writerow(
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


# =========================================================
# TERMINAL SUMMARY
# =========================================================

def print_summary(
    lesson,
    questions,
):

    print()
    print(
        "=" * 70
    )

    print(
        "MOC HAN - QUESTION GENERATOR V2"
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


    print()
    print(
        "Thong ke loai cau hoi:"
    )


    counts = {}


    for question in questions:

        key = question[
            "question_type"
        ]

        counts[key] = (
            counts.get(
                key,
                0,
            )
            + 1
        )


    labels = {
        "chon_mot":
            "Chon mot",

        "dien_tu":
            "Dien tu",

        "dung_sai":
            "Dung / Sai",

        "sap_xep":
            "Sap xep",
    }


    for key, count in counts.items():

        print(
            (
                f"  "
                f"{labels.get(key, key):<15}"
                f": {count}"
            )
        )


    print()
    print(
        (
            f"Tong cau hoi: "
            f"{len(questions)}"
        )
    )


    print()
    print(
        "-" * 70
    )


    for question in questions:

        print()

        print(
            (
                f"[{question['order']}] "
                f"[{question['question_type']}]"
            )
        )

        print(
            question[
                "content"
            ]
        )


        if (
            question["question_type"]
            == "chon_mot"
        ):

            print(
                f"  A. {question['choice_1']}"
            )

            print(
                f"  B. {question['choice_2']}"
            )

            print(
                f"  C. {question['choice_3']}"
            )

            print(
                f"  D. {question['choice_4']}"
            )

            print(
                (
                    f"  Dap an: "
                    f"{question['correct_choices']}"
                )
            )


        else:

            print(
                (
                    f"  Answer JSON: "
                    f"{question['answer_json']}"
                )
            )


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "Dang doc du lieu tu HocTiengTrungDB..."
    )


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            lesson = load_lesson(
                cursor,
                LESSON_ID,
            )


            vocabulary = load_vocabulary(
                cursor,
                LESSON_ID,
            )


            grammar = load_grammar(
                cursor,
                LESSON_ID,
            )


            hanzi = load_hanzi(
                cursor,
                LESSON_ID,
            )


    print()
    print(
        "Du lieu bai hoc:"
    )

    print(
        f"  Tu vung : {len(vocabulary)}"
    )

    print(
        f"  Ngu phap: {len(grammar)}"
    )

    print(
        f"  Chu Han : {len(hanzi)}"
    )


    questions = build_questions(
        vocabulary,
        grammar,
        hanzi,
    )


    output_file = (
        PREVIEW_DIR
        /
        (
            f"hsk{lesson['hsk_level']}"
            f"_bai{lesson['lesson_order']}"
            f"_questions_v2.csv"
        )
    )


    write_csv(
        output_file,
        lesson,
        questions,
    )


    print_summary(
        lesson,
        questions,
    )


    print()
    print(
        "=" * 70
    )

    print(
        "TAO PREVIEW V2 THANH CONG"
    )

    print(
        "=" * 70
    )

    print(
        f"File: {output_file}"
    )

    print()

    print(
        "CHUA CO DU LIEU NAO DUOC GHI VAO SQL."
    )


if __name__ == "__main__":

    main()