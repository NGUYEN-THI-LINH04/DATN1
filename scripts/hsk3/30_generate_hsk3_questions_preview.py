# -*- coding: utf-8 -*-

"""
HSK3 - tao PREVIEW cau hoi cho 20 bai.

Moi bai: 20 cau, du 7 dang:
- 6 chon_mot
- 2 chon_nhieu
- 3 dung_sai
- 3 dien_tu
- 2 ghep_cap
- 2 sap_xep
- 2 viet_ngan

CHI DOC SQL + GHI JSON PREVIEW.
KHONG INSERT / UPDATE / DELETE SQL.
"""

import json
import random
import re
import sys

from collections import Counter
from contextlib import closing
from pathlib import Path


# ============================================================
# DUONG DAN DU AN
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT)
)

from database import get_connection


# ============================================================
# FILE PREVIEW
# ============================================================

DATA_DIR = (
    ROOT
    / "scripts"
    / "hsk3"
    / "data"
    / "processed"
)

OUTPUT_FILE = (
    DATA_DIR
    / "exercises_hsk3_01_20_base_preview.json"
)


# ============================================================
# PHAN BO 20 CAU / BAI
# ============================================================

TARGET_COUNTS = {
    "chon_mot": 6,
    "chon_nhieu": 2,
    "dung_sai": 3,
    "dien_tu": 3,
    "ghep_cap": 2,
    "sap_xep": 2,
    "viet_ngan": 2,
}

QUESTION_TYPES = set(
    TARGET_COUNTS
)


# ============================================================
# HAM HO TRO
# ============================================================

def rows(
    cursor,
    statement,
    *params
):
    cursor.execute(
        statement,
        *params
    )

    columns = [
        column[0]
        for column
        in cursor.description
    ]

    return [
        dict(
            zip(
                columns,
                row
            )
        )
        for row
        in cursor.fetchall()
    ]


def txt(value):
    if value is None:
        return ""

    return str(
        value
    ).strip()


def dumps(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2
    )


def normalize(value):
    return re.sub(
        r"\s+",
        "",
        txt(value).lower()
    )


def unique_values(
    values,
    exclude=None
):
    exclude = set(
        exclude or []
    )

    result = []
    seen = set(
        exclude
    )

    for value in values:
        value = txt(
            value
        )

        if (
            value
            and value not in seen
        ):
            seen.add(
                value
            )

            result.append(
                value
            )

    return result


def pick_wrong(
    correct,
    pool,
    count,
    rng
):
    candidates = unique_values(
        pool,
        exclude=[correct]
    )

    if len(
        candidates
    ) < count:
        raise ValueError(
            f"Khong du {count} "
            f"phuong an sai cho dap an: "
            f"{correct}"
        )

    return rng.sample(
        candidates,
        count
    )


def source_values(value):
    if isinstance(
        value,
        list
    ):
        return [
            txt(item)
            for item in value
            if txt(item)
        ]

    if txt(value):
        return [
            txt(value)
        ]

    return []


# ============================================================
# TAO OBJECT CAU HOI CO BAN
# ============================================================

def base_question(
    question_type,
    skill,
    group,
    content,
    answer_json,
    explanation,
    source_type,
    source_value,
    questions,
    choices=None,
):
    questions.append({
        "LoaiCauHoi":
            question_type,

        "KyNang":
            skill,

        "NhomKienThuc":
            group,

        "NoiDungCauHoi":
            content,

        "DapAnJson":
            answer_json,

        "GiaiThich":
            explanation,

        "DiemToiDa":
            1,

        "ThuTu":
            len(questions) + 1,

        # Hai truong nay chi dung
        # cho PREVIEW + VALIDATE.
        # Khi import SQL se khong insert.
        "NguonLoai":
            source_type,

        "NguonGiaTri":
            source_value,

        "LuaChon":
            choices or [],
    })


# ============================================================
# 1 + 2. CHON MOT / CHON NHIEU
# ============================================================

def add_choice(
    questions,
    question_type,
    group,
    content,
    options,
    correct_values,
    explanation,
    source_type,
    source_value,
    rng,
):
    if question_type not in (
        "chon_mot",
        "chon_nhieu"
    ):
        raise ValueError(
            "Sai loai cau hoi lua chon"
        )

    options = unique_values(
        options
    )

    correct_values = unique_values(
        correct_values
    )

    # Theo giao dien Admin:
    # dung 4 lua chon.
    if len(
        options
    ) != 4:
        raise ValueError(
            f"{question_type}: "
            "phai co dung 4 lua chon"
        )

    if not set(
        correct_values
    ).issubset(
        set(options)
    ):
        raise ValueError(
            f"{question_type}: "
            "dap an dung khong nam "
            "trong lua chon"
        )

    if (
        question_type
        == "chon_mot"
        and len(
            correct_values
        ) != 1
    ):
        raise ValueError(
            "chon_mot phai co "
            "dung 1 dap an dung"
        )

    if (
        question_type
        == "chon_nhieu"
        and len(
            correct_values
        ) < 1
    ):
        raise ValueError(
            "chon_nhieu phai co "
            "it nhat 1 dap an dung"
        )

    rng.shuffle(
        options
    )

    correct_set = set(
        correct_values
    )

    choices = [
        {
            "NoiDungLuaChon":
                option,

            "LaDapAnDung":
                option
                in correct_set,

            "ThuTu":
                index + 1,
        }
        for index, option
        in enumerate(
            options
        )
    ]

    base_question(
        question_type=question_type,
        skill="doc",
        group=group,
        content=content,
        answer_json=None,
        explanation=explanation,
        source_type=source_type,
        source_value=source_value,
        questions=questions,
        choices=choices,
    )


# ============================================================
# 3. DUNG / SAI
# ============================================================

def add_true_false(
    questions,
    content,
    is_true,
    explanation,
    group,
    source_type,
    source_value,
):
    base_question(
        question_type="dung_sai",
        skill="doc",
        group=group,
        content=content,

        # Dung dung cau truc
        # questions.py:
        #
        # {"answer": "dung"}
        # {"answer": "sai"}
        answer_json={
            "answer":
                "dung"
                if is_true
                else "sai"
        },

        explanation=explanation,
        source_type=source_type,
        source_value=source_value,
        questions=questions,
    )


# ============================================================
# 4. DIEN TU
# ============================================================

def add_fill(
    questions,
    content,
    answers,
    explanation,
    group,
    source_type,
    source_value,
):
    answers = unique_values(
        answers
    )

    if not answers:
        raise ValueError(
            "dien_tu thieu dap an"
        )

    base_question(
        question_type="dien_tu",
        skill="doc",
        group=group,
        content=content,

        # Dung dung cau truc Admin:
        # {"answers": [...]}
        answer_json={
            "answers":
                answers
        },

        explanation=explanation,
        source_type=source_type,
        source_value=source_value,
        questions=questions,
    )


# ============================================================
# 5. GHEP CAP
# ============================================================

def add_matching(
    questions,
    content,
    pairs,
    explanation,
    group,
    source_type,
    source_value,
):
    if len(
        pairs
    ) < 2:
        raise ValueError(
            "ghep_cap can "
            "it nhat 2 cap"
        )

    base_question(
        question_type="ghep_cap",
        skill="doc",
        group=group,
        content=content,

        # Dung dung cau truc Admin:
        #
        # {
        #   "pairs": [
        #       {
        #           "left": "...",
        #           "right": "..."
        #       }
        #   ]
        # }
        answer_json={
            "pairs":
                pairs
        },

        explanation=explanation,
        source_type=source_type,
        source_value=source_value,
        questions=questions,
    )


# ============================================================
# 6. SAP XEP
# ============================================================

def add_sort(
    questions,
    content,
    items,
    explanation,
    group,
    source_type,
    source_value,
):
    items = [
        txt(item)
        for item in items
        if txt(item)
    ]

    if len(
        items
    ) < 2:
        raise ValueError(
            "sap_xep can "
            "it nhat 2 thanh phan"
        )

    base_question(
        question_type="sap_xep",
        skill="doc",
        group=group,
        content=content,

        # Dung dung cau truc Admin:
        # {"items": [...]}
        answer_json={
            "items":
                items
        },

        explanation=explanation,
        source_type=source_type,
        source_value=source_value,
        questions=questions,
    )


# ============================================================
# 7. VIET NGAN
# ============================================================

def add_short(
    questions,
    content,
    sample_answer,
    explanation,
    group,
    source_type,
    source_value,
):
    sample_answer = txt(
        sample_answer
    )

    if not sample_answer:
        raise ValueError(
            "viet_ngan thieu dap an mau"
        )

    base_question(
        question_type="viet_ngan",

        # Viet ngan -> ky nang viet.
        skill="viet",

        group=group,
        content=content,

        # Dung dung cau truc Admin:
        # {"sample_answer": "..."}
        answer_json={
            "sample_answer":
                sample_answer
        },

        explanation=explanation,
        source_type=source_type,
        source_value=source_value,
        questions=questions,
    )


# ============================================================
# NGU PHAP
# ============================================================

def grammar_description(item):
    return (
        txt(
            item.get(
                "CachDung"
            )
        )
        or
        txt(
            item.get(
                "MoTa"
            )
        )
    )


# ============================================================
# TAO UNG VIEN DIEN TU TU VI DU NGU PHAP
# ============================================================

def grammar_fill_candidates(
    grammar
):
    """
    Chi tao cau dien tu
    tu vi du ngu phap
    dang co trong SQL.

    Khong tu sang tac
    cau tieng Trung moi.
    """

    result = []
    seen = set()

    for item in grammar:
        pattern = txt(
            item.get(
                "TenCauTruc"
            )
        )

        sentence = txt(
            item.get(
                "ViDuTiengTrung"
            )
        )

        if (
            not pattern
            or not sentence
        ):
            continue

        pieces = [
            part.strip()
            for part
            in re.split(
                r"……|…+|\.{2,}",
                pattern
            )
            if part.strip()
        ]

        if not pieces:
            pieces = [
                pattern
            ]

        candidates = []

        for part in pieces:

            if (
                part
                in sentence
            ):
                candidates.append(
                    part
                )

            else:
                chunks = re.findall(
                    r"[\u3400-\u9fff]+",
                    part
                )

                for chunk in chunks:

                    if (
                        chunk
                        in sentence
                    ):
                        candidates.append(
                            chunk
                        )

                    else:
                        candidates.extend(
                            char
                            for char
                            in chunk
                            if char
                            in sentence
                        )

        for answer in candidates:

            if (
                not answer
                or answer
                not in sentence
            ):
                continue

            masked = sentence.replace(
                answer,
                "___",
                1
            )

            key = (
                masked,
                answer
            )

            if (
                masked
                == sentence
                or key
                in seen
            ):
                continue

            seen.add(
                key
            )

            vietnamese = txt(
                item.get(
                    "ViDuTiengViet"
                )
            )

            explanation = (
                f"Câu đầy đủ: "
                f"{sentence}"
            )

            if vietnamese:
                explanation += (
                    f"\nNghĩa: "
                    f"{vietnamese}"
                )

            elif grammar_description(
                item
            ):
                explanation += (
                    "\nCách dùng: "
                    + grammar_description(
                        item
                    )
                )

            result.append({
                "content":
                    "Điền phần còn thiếu "
                    "vào câu:\n"
                    + masked,

                "answer":
                    answer,

                "explanation":
                    explanation,

                "pattern":
                    pattern,
            })

    return result


# ============================================================
# CHON CAC CAP KHONG TRUNG
# ============================================================

def choose_distinct_pairs(
    items,
    left_key,
    right_key,
    max_count=4
):
    result = []

    seen_left = set()
    seen_right = set()

    for item in items:

        left = txt(
            item.get(
                left_key
            )
        )

        right = txt(
            item.get(
                right_key
            )
        )

        if (
            not left
            or not right
        ):
            continue

        # Tranh ghep cap mo ho
        # khi 2 ve phai giong nhau.
        if (
            left
            in seen_left
            or right
            in seen_right
        ):
            continue

        seen_left.add(
            left
        )

        seen_right.add(
            right
        )

        result.append(
            (
                item,
                left,
                right
            )
        )

        if len(
            result
        ) >= max_count:
            break

    return result


# ============================================================
# TAO DISTRACTOR TU VUNG
# ============================================================

def wrong_vocab_rows(
    all_vocab_rows,
    excluded_words,
    excluded_meanings,
    count,
    rng
):
    candidates = []
    seen = set()

    excluded_words = set(
        excluded_words
    )

    excluded_meanings = {
        normalize(
            item
        )
        for item
        in excluded_meanings
    }

    for item in all_vocab_rows:

        word = txt(
            item.get(
                "ChuHan"
            )
        )

        meaning = txt(
            item.get(
                "NghiaTiengViet"
            )
        )

        if (
            not word
            or not meaning
        ):
            continue

        if (
            word
            in excluded_words
        ):
            continue

        if (
            normalize(
                meaning
            )
            in excluded_meanings
        ):
            continue

        if word in seen:
            continue

        seen.add(
            word
        )

        candidates.append(
            item
        )

    if len(
        candidates
    ) < count:
        raise ValueError(
            "Khong du tu vung "
            "de tao phuong an "
            "chon_nhieu"
        )

    return rng.sample(
        candidates,
        count
    )


# ============================================================
# UNG VIEN SAP XEP
# ============================================================

def collect_sort_candidates(
    vocabulary,
    grammar
):
    result = []
    seen_items = set()

    # --------------------------------------------------------
    # Uu tien:
    # sap xep cac chu Han
    # de tao thanh mot TU VUNG THAT
    # cua chinh bai.
    # --------------------------------------------------------

    for item in vocabulary:

        word = txt(
            item.get(
                "ChuHan"
            )
        )

        meaning = txt(
            item.get(
                "NghiaTiengViet"
            )
        )

        chars = re.findall(
            r"[\u3400-\u9fff]",
            word
        )

        if (
            len(chars) < 2
            or len(chars) > 8
        ):
            continue

        key = tuple(
            chars
        )

        if (
            key
            in seen_items
        ):
            continue

        seen_items.add(
            key
        )

        result.append({
            "content": (
                "Sắp xếp các chữ Hán "
                "theo đúng thứ tự "
                "để tạo thành từ "
                f"có nghĩa: “{meaning}”."
            ),

            "items":
                chars,

            "explanation": (
                "Thứ tự đúng tạo thành từ: "
                f"{word} — {meaning}."
            ),

            "group":
                "tu_vung",

            "source_type":
                "tu_vung",

            "source_value":
                word,
        })

    # --------------------------------------------------------
    # Neu tu vung khong du,
    # lay cau VI DU THAT trong SQL.
    # --------------------------------------------------------

    if len(
        result
    ) < 2:

        example_sources = []

        # Vi du ngu phap
        for item in grammar:

            sentence = txt(
                item.get(
                    "ViDuTiengTrung"
                )
            )

            vietnamese = txt(
                item.get(
                    "ViDuTiengViet"
                )
            )

            pattern = txt(
                item.get(
                    "TenCauTruc"
                )
            )

            if (
                sentence
                and pattern
            ):
                example_sources.append(
                    (
                        sentence,
                        vietnamese,
                        "ngu_phap",
                        "ngu_phap",
                        pattern,
                    )
                )

        # Vi du tu vung
        for item in vocabulary:

            sentence = txt(
                item.get(
                    "ViDuTiengTrung"
                )
            )

            vietnamese = txt(
                item.get(
                    "ViDuTiengViet"
                )
            )

            word = txt(
                item.get(
                    "ChuHan"
                )
            )

            if (
                sentence
                and word
            ):
                example_sources.append(
                    (
                        sentence,
                        vietnamese,
                        "tu_vung",
                        "tu_vung",
                        word,
                    )
                )

        for (
            sentence,
            vietnamese,
            group,
            source_type,
            source_value,
        ) in example_sources:

            chars = re.findall(
                r"[\u3400-\u9fff]",
                sentence
            )

            if (
                len(chars) < 3
                or len(chars) > 12
            ):
                continue

            key = tuple(
                chars
            )

            if (
                key
                in seen_items
            ):
                continue

            seen_items.add(
                key
            )

            if vietnamese:
                clue = (
                    " Nghĩa gợi ý: "
                    f"“{vietnamese}”."
                )
            else:
                clue = ""

            result.append({
                "content": (
                    "Sắp xếp các chữ Hán "
                    "theo đúng thứ tự "
                    "để tạo lại câu mẫu "
                    f"trong bài.{clue}"
                ),

                "items":
                    chars,

                "explanation":
                    f"Câu đúng: {sentence}",

                "group":
                    group,

                "source_type":
                    source_type,

                "source_value":
                    source_value,
            })

            if len(
                result
            ) >= 2:
                break

    return result


# ============================================================
# UNG VIEN VIET NGAN
# ============================================================

def collect_short_candidates(
    vocabulary,
    grammar
):
    """
    Tao ung vien cho dang viet_ngan.

    Uu tien:
    1. ViDuTiengTrung THAT cua tu vung.
    2. ViDuTiengTrung THAT cua ngu phap.

    Neu SQL khong du 2 vi du:
    3. Viet ChuHan dua tren nghia tieng Viet.
    4. Viet Pinyin cua tu vung.
    5. Viet cau truc ngu phap theo mo ta.

    KHONG tu sang tac cau tieng Trung moi.
    Tat ca dap an deu lay truc tiep tu SQL
    cua CHINH bai hoc.
    """

    result = []

    seen_content = set()


    # ========================================================
    # HAM THEM UNG VIEN KHONG TRUNG NOI DUNG
    # ========================================================

    def append_candidate(candidate):

        content_key = normalize(
            candidate[
                "content"
            ]
        )

        if (
            not content_key
            or content_key
            in seen_content
        ):
            return False

        sample = txt(
            candidate.get(
                "sample"
            )
        )

        if not sample:
            return False

        seen_content.add(
            content_key
        )

        result.append(
            candidate
        )

        return True


    # ========================================================
    # 1. UU TIEN VI DU TU VUNG THAT TRONG SQL
    # ========================================================

    for item in vocabulary:

        word = txt(
            item.get(
                "ChuHan"
            )
        )

        meaning = txt(
            item.get(
                "NghiaTiengViet"
            )
        )

        sentence = txt(
            item.get(
                "ViDuTiengTrung"
            )
        )

        vietnamese = txt(
            item.get(
                "ViDuTiengViet"
            )
        )

        if (
            not word
            or not sentence
        ):
            continue

        content = (
            "Viết một câu ngắn "
            f"có sử dụng từ “{word}”"
        )

        if meaning:
            content += (
                f" (nghĩa: {meaning})"
            )

        content += "."

        explanation = (
            "Đáp án mẫu lấy từ "
            "ví dụ có sẵn trong SQL "
            f"của từ “{word}”: "
            f"{sentence}"
        )

        if vietnamese:
            explanation += (
                f"\nNghĩa: "
                f"{vietnamese}"
            )

        append_candidate({
            "content":
                content,

            "sample":
                sentence,

            "explanation":
                explanation,

            "group":
                "tu_vung",

            "source_type":
                "tu_vung",

            "source_value":
                word,
        })

        if len(
            result
        ) >= 2:
            return result


    # ========================================================
    # 2. UU TIEN VI DU NGU PHAP THAT TRONG SQL
    # ========================================================

    for item in grammar:

        pattern = txt(
            item.get(
                "TenCauTruc"
            )
        )

        sentence = txt(
            item.get(
                "ViDuTiengTrung"
            )
        )

        vietnamese = txt(
            item.get(
                "ViDuTiengViet"
            )
        )

        if (
            not pattern
            or not sentence
        ):
            continue

        explanation = (
            "Đáp án mẫu lấy từ "
            "ví dụ ngữ pháp có sẵn "
            "trong SQL của cấu trúc "
            f"“{pattern}”: "
            f"{sentence}"
        )

        if vietnamese:
            explanation += (
                f"\nNghĩa: "
                f"{vietnamese}"
            )

        append_candidate({
            "content": (
                "Viết một câu ngắn "
                "sử dụng cấu trúc "
                f"“{pattern}”."
            ),

            "sample":
                sentence,

            "explanation":
                explanation,

            "group":
                "ngu_phap",

            "source_type":
                "ngu_phap",

            "source_value":
                pattern,
        })

        if len(
            result
        ) >= 2:
            return result


    # ========================================================
    # 3. FALLBACK:
    # VIET CHU HAN THEO NGHIA TIENG VIET
    # ========================================================
    #
    # Khong sang tac du lieu.
    #
    # Cau hoi:
    #   Viet tu tieng Trung co nghia "..."
    #
    # Dap an mau:
    #   ChuHan that trong SQL.
    # ========================================================

    for item in vocabulary:

        word = txt(
            item.get(
                "ChuHan"
            )
        )

        meaning = txt(
            item.get(
                "NghiaTiengViet"
            )
        )

        pinyin = txt(
            item.get(
                "PhienAm"
            )
        )

        if (
            not word
            or not meaning
        ):
            continue

        explanation = (
            "Từ tiếng Trung tương ứng "
            f"với nghĩa “{meaning}” "
            f"là “{word}”"
        )

        if pinyin:
            explanation += (
                f" ({pinyin})"
            )

        explanation += "."

        append_candidate({
            "content": (
                "Viết từ tiếng Trung "
                "tương ứng với nghĩa "
                f"“{meaning}”."
            ),

            "sample":
                word,

            "explanation":
                explanation,

            "group":
                "tu_vung",

            "source_type":
                "tu_vung",

            "source_value":
                word,
        })

        if len(
            result
        ) >= 2:
            return result


    # ========================================================
    # 4. FALLBACK:
    # VIET PINYIN CUA TU VUNG
    # ========================================================

    for item in vocabulary:

        word = txt(
            item.get(
                "ChuHan"
            )
        )

        pinyin = txt(
            item.get(
                "PhienAm"
            )
        )

        meaning = txt(
            item.get(
                "NghiaTiengViet"
            )
        )

        if (
            not word
            or not pinyin
        ):
            continue

        explanation = (
            f"Pinyin của “{word}” "
            f"là {pinyin}."
        )

        if meaning:
            explanation += (
                f"\nNghĩa: {meaning}."
            )

        append_candidate({
            "content": (
                "Viết Pinyin "
                f"của từ “{word}”."
            ),

            "sample":
                pinyin,

            "explanation":
                explanation,

            "group":
                "tu_vung",

            "source_type":
                "tu_vung",

            "source_value":
                word,
        })

        if len(
            result
        ) >= 2:
            return result


    # ========================================================
    # 5. FALLBACK CUOI:
    # VIET CAU TRUC NGU PHAP
    # ========================================================

    for item in grammar:

        pattern = txt(
            item.get(
                "TenCauTruc"
            )
        )

        description = (
            grammar_description(
                item
            )
        )

        if (
            not pattern
            or not description
        ):
            continue

        append_candidate({
            "content": (
                "Viết cấu trúc ngữ pháp "
                "phù hợp với mô tả: "
                f"“{description}”."
            ),

            "sample":
                pattern,

            "explanation": (
                "Cấu trúc phù hợp là "
                f"“{pattern}”."
            ),

            "group":
                "ngu_phap",

            "source_type":
                "ngu_phap",

            "source_value":
                pattern,
        })

        if len(
            result
        ) >= 2:
            return result


    # ========================================================
    # KHONG THE TAO DU 2 CAU
    # ========================================================

    return result


# ============================================================
# VALIDATE NGUON NGU PHAP
# ============================================================

def grammar_source_matches(
    value,
    grammar_names
):
    normalized = normalize(
        value
        .replace(
            "……",
            ""
        )
        .replace(
            "…",
            ""
        )
    )

    if not normalized:
        return False

    for name in grammar_names:

        normalized_name = normalize(
            name
            .replace(
                "……",
                ""
            )
            .replace(
                "…",
                ""
            )
        )

        if (
            normalized
            in normalized_name
            or
            normalized_name
            in normalized
        ):
            return True

    return False


# ============================================================
# VALIDATE 20 CAU + 7 DANG
# ============================================================

def validate(
    source,
    questions
):
    lesson = source[
        "lesson"
    ]

    number = int(
        lesson[
            "SoThuTuBai"
        ]
    )

    # --------------------------------------------------------
    # Dung HSK3
    # --------------------------------------------------------

    if (
        lesson[
            "MaKhoaHoc"
        ]
        != 3
    ):
        raise ValueError(
            "Khong phai khoa HSK3"
        )

    # --------------------------------------------------------
    # Khong tao neu bai da co BaiTap
    # --------------------------------------------------------

    if source[
        "existing_exercises"
    ]:
        raise ValueError(
            f"Bai {number} "
            "da co bai tap; "
            "dung de tranh tao trung"
        )

    # --------------------------------------------------------
    # Dung 20 cau
    # --------------------------------------------------------

    if len(
        questions
    ) != 20:
        raise ValueError(
            f"Bai {number}: "
            "phai co dung 20 cau"
        )

    # --------------------------------------------------------
    # Dung phan bo 7 dang
    # --------------------------------------------------------

    counts = Counter(
        question[
            "LoaiCauHoi"
        ]
        for question
        in questions
    )

    if (
        counts
        != Counter(
            TARGET_COUNTS
        )
    ):
        raise ValueError(
            f"Bai {number}: "
            "sai phan bo 7 dang: "
            f"{dict(counts)}"
        )

    if (
        set(counts)
        != QUESTION_TYPES
    ):
        raise ValueError(
            f"Bai {number}: "
            "chua du 7 dang cau hoi"
        )

    # --------------------------------------------------------
    # ThuTu 1 -> 20
    # --------------------------------------------------------

    orders = [
        question[
            "ThuTu"
        ]
        for question
        in questions
    ]

    if (
        orders
        != list(
            range(
                1,
                21
            )
        )
    ):
        raise ValueError(
            f"Bai {number}: "
            "ThuTu khong hop le"
        )

    # --------------------------------------------------------
    # Khong trung noi dung
    # --------------------------------------------------------

    contents = [
        normalize(
            question[
                "NoiDungCauHoi"
            ]
        )
        for question
        in questions
    ]

    if len(
        set(contents)
    ) != 20:
        raise ValueError(
            f"Bai {number}: "
            "co NoiDungCauHoi bi trung"
        )

    # --------------------------------------------------------
    # Nguon kien thuc cua CHINH bai
    # --------------------------------------------------------

    vocabulary_set = {
        txt(
            item.get(
                "ChuHan"
            )
        )
        for item
        in source[
            "vocabulary"
        ]
        if txt(
            item.get(
                "ChuHan"
            )
        )
    }

    hanzi_set = {
        txt(
            item.get(
                "KyTu"
            )
        )
        for item
        in source[
            "hanzi"
        ]
        if txt(
            item.get(
                "KyTu"
            )
        )
    }

    grammar_names = [
        txt(
            item.get(
                "TenCauTruc"
            )
        )
        for item
        in source[
            "grammar"
        ]
        if txt(
            item.get(
                "TenCauTruc"
            )
        )
    ]

    # --------------------------------------------------------
    # Validate tung cau
    # --------------------------------------------------------

    for question in questions:

        qtype = question[
            "LoaiCauHoi"
        ]

        if (
            qtype
            not in QUESTION_TYPES
        ):
            raise ValueError(
                "Loai cau hoi "
                "khong hop le: "
                f"{qtype}"
            )

        if not txt(
            question.get(
                "NoiDungCauHoi"
            )
        ):
            raise ValueError(
                "Co cau hoi rong"
            )

        if not txt(
            question.get(
                "GiaiThich"
            )
        ):
            raise ValueError(
                "Co cau hoi "
                "thieu giai thich"
            )

        # ----------------------------------------------------
        # Validate nguon
        # ----------------------------------------------------

        source_type = question.get(
            "NguonLoai"
        )

        values = source_values(
            question.get(
                "NguonGiaTri"
            )
        )

        for value in values:

            if (
                source_type
                == "tu_vung"
                and value
                not in vocabulary_set
            ):
                raise ValueError(
                    f"Tu ngoai bai: "
                    f"{value}"
                )

            if (
                source_type
                == "chu_han"
                and value
                not in hanzi_set
            ):
                raise ValueError(
                    f"Chu Han ngoai bai: "
                    f"{value}"
                )

            if (
                source_type
                == "ngu_phap"
                and not grammar_source_matches(
                    value,
                    grammar_names
                )
            ):
                raise ValueError(
                    "Ngu phap ngoai bai: "
                    f"{value}"
                )

        choices = (
            question.get(
                "LuaChon"
            )
            or []
        )

        answer = question.get(
            "DapAnJson"
        )

        # ====================================================
        # CHON MOT / CHON NHIEU
        # ====================================================

        if qtype in (
            "chon_mot",
            "chon_nhieu"
        ):

            if (
                answer
                is not None
            ):
                raise ValueError(
                    f"{qtype}: "
                    "DapAnJson phai la None"
                )

            if len(
                choices
            ) != 4:
                raise ValueError(
                    f"{qtype}: "
                    "phai co 4 lua chon"
                )

            option_texts = [
                item[
                    "NoiDungLuaChon"
                ]
                for item
                in choices
            ]

            if len(
                set(
                    option_texts
                )
            ) != 4:
                raise ValueError(
                    f"{qtype}: "
                    "lua chon bi trung"
                )

            correct_count = sum(
                bool(
                    item[
                        "LaDapAnDung"
                    ]
                )
                for item
                in choices
            )

            if (
                qtype
                == "chon_mot"
                and correct_count
                != 1
            ):
                raise ValueError(
                    "chon_mot: "
                    "sai so dap an dung"
                )

            # Preview HSK3 nay
            # tao dung 2 dap an dung.
            if (
                qtype
                == "chon_nhieu"
                and correct_count
                != 2
            ):
                raise ValueError(
                    "chon_nhieu: "
                    "phai co dung "
                    "2 dap an dung"
                )

        # ====================================================
        # DUNG / SAI
        # ====================================================

        elif (
            qtype
            == "dung_sai"
        ):

            if choices:
                raise ValueError(
                    "dung_sai "
                    "khong dung "
                    "LuaChonCauHoi"
                )

            if (
                not isinstance(
                    answer,
                    dict
                )
                or answer.get(
                    "answer"
                )
                not in (
                    "dung",
                    "sai"
                )
            ):
                raise ValueError(
                    "dung_sai: "
                    "DapAnJson "
                    "khong hop le"
                )

        # ====================================================
        # DIEN TU
        # ====================================================

        elif (
            qtype
            == "dien_tu"
        ):

            if choices:
                raise ValueError(
                    "dien_tu "
                    "khong dung "
                    "LuaChonCauHoi"
                )

            if (
                not isinstance(
                    answer,
                    dict
                )
                or not answer.get(
                    "answers"
                )
            ):
                raise ValueError(
                    "dien_tu: "
                    "DapAnJson "
                    "khong hop le"
                )

        # ====================================================
        # GHEP CAP
        # ====================================================

        elif (
            qtype
            == "ghep_cap"
        ):

            if choices:
                raise ValueError(
                    "ghep_cap "
                    "khong dung "
                    "LuaChonCauHoi"
                )

            if isinstance(
                answer,
                dict
            ):
                pairs = answer.get(
                    "pairs"
                )
            else:
                pairs = None

            if (
                not pairs
                or len(
                    pairs
                ) < 2
            ):
                raise ValueError(
                    "ghep_cap: "
                    "thieu cap"
                )

            for pair in pairs:

                if (
                    not txt(
                        pair.get(
                            "left"
                        )
                    )
                    or
                    not txt(
                        pair.get(
                            "right"
                        )
                    )
                ):
                    raise ValueError(
                        "ghep_cap: "
                        "cap rong"
                    )

        # ====================================================
        # SAP XEP
        # ====================================================

        elif (
            qtype
            == "sap_xep"
        ):

            if choices:
                raise ValueError(
                    "sap_xep "
                    "khong dung "
                    "LuaChonCauHoi"
                )

            if isinstance(
                answer,
                dict
            ):
                items = answer.get(
                    "items"
                )
            else:
                items = None

            if (
                not items
                or len(
                    items
                ) < 2
            ):
                raise ValueError(
                    "sap_xep: "
                    "thieu thanh phan"
                )

        # ====================================================
        # VIET NGAN
        # ====================================================

        elif (
            qtype
            == "viet_ngan"
        ):

            if choices:
                raise ValueError(
                    "viet_ngan "
                    "khong dung "
                    "LuaChonCauHoi"
                )

            if isinstance(
                answer,
                dict
            ):
                sample = answer.get(
                    "sample_answer"
                )
            else:
                sample = None

            if not txt(
                sample
            ):
                raise ValueError(
                    "viet_ngan: "
                    "thieu sample_answer"
                )

            if (
                question.get(
                    "KyNang"
                )
                != "viet"
            ):
                raise ValueError(
                    "viet_ngan: "
                    "KyNang phai la viet"
                )


# ============================================================
# TAO 20 CAU CHO MOT BAI
# ============================================================

def build_questions(
    source,
    all_vocab_rows,
    all_hanzi_rows,
    all_grammar_rows
):
    lesson = source[
        "lesson"
    ]

    number = int(
        lesson[
            "SoThuTuBai"
        ]
    )

    rng = random.Random(
        7300 + number
    )

    questions = []

    # ========================================================
    # DU LIEU TU VUNG CUA CHINH BAI
    # ========================================================

    vocabulary = []

    seen_words = set()

    for item in source[
        "vocabulary"
    ]:

        word = txt(
            item.get(
                "ChuHan"
            )
        )

        meaning = txt(
            item.get(
                "NghiaTiengViet"
            )
        )

        if (
            not word
            or not meaning
            or word
            in seen_words
        ):
            continue

        seen_words.add(
            word
        )

        vocabulary.append(
            item
        )

    # ========================================================
    # CHU HAN CUA CHINH BAI
    # ========================================================

    hanzi = []

    seen_hanzi = set()

    for item in source[
        "hanzi"
    ]:

        char = txt(
            item.get(
                "KyTu"
            )
        )

        pinyin = txt(
            item.get(
                "Pinyin"
            )
        )

        if (
            not char
            or not pinyin
            or char
            in seen_hanzi
        ):
            continue

        seen_hanzi.add(
            char
        )

        hanzi.append(
            item
        )

    # ========================================================
    # NGU PHAP CUA CHINH BAI
    # ========================================================

    grammar = [
        item
        for item
        in source[
            "grammar"
        ]
        if txt(
            item.get(
                "TenCauTruc"
            )
        )
    ]

    if len(
        vocabulary
    ) < 6:
        raise ValueError(
            f"Bai {number}: "
            "can it nhat "
            "6 tu vung hop le"
        )

    if not grammar:
        raise ValueError(
            f"Bai {number}: "
            "chua co ngu phap"
        )

    # ========================================================
    # POOL TOAN HSK3
    # Chi dung lam phuong an sai.
    # Dap an dung van lay tu CHINH bai.
    # ========================================================

    all_meanings = [
        txt(
            item.get(
                "NghiaTiengViet"
            )
        )
        for item
        in all_vocab_rows
        if txt(
            item.get(
                "NghiaTiengViet"
            )
        )
    ]

    all_vocab_pinyins = [
        txt(
            item.get(
                "PhienAm"
            )
        )
        for item
        in all_vocab_rows
        if txt(
            item.get(
                "PhienAm"
            )
        )
    ]

    all_hanzi_pinyins = [
        txt(
            item.get(
                "Pinyin"
            )
        )
        for item
        in all_hanzi_rows
        if txt(
            item.get(
                "Pinyin"
            )
        )
    ]

    all_patterns = [
        txt(
            item.get(
                "TenCauTruc"
            )
        )
        for item
        in all_grammar_rows
        if txt(
            item.get(
                "TenCauTruc"
            )
        )
    ]

    all_descriptions = [
        grammar_description(
            item
        )
        for item
        in all_grammar_rows
        if grammar_description(
            item
        )
    ]


    # ========================================================
    # 1. CHON MOT - 6 CAU
    # ========================================================

    # --------------------------------------------------------
    # 4 cau nghia tu vung
    # --------------------------------------------------------

    for item in vocabulary[:4]:

        word = txt(
            item[
                "ChuHan"
            ]
        )

        meaning = txt(
            item[
                "NghiaTiengViet"
            ]
        )

        pinyin = txt(
            item.get(
                "PhienAm"
            )
        )

        wrong = pick_wrong(
            meaning,
            all_meanings,
            3,
            rng
        )

        if pinyin:
            explanation = (
                f"“{word}” "
                f"({pinyin}) "
                "có nghĩa là "
                f"“{meaning}”."
            )

        else:
            explanation = (
                f"“{word}” "
                "có nghĩa là "
                f"“{meaning}”."
            )

        add_choice(
            questions=questions,
            question_type="chon_mot",
            group="tu_vung",

            content=(
                f"Từ “{word}” "
                "có nghĩa là gì?"
            ),

            options=[
                meaning
            ] + wrong,

            correct_values=[
                meaning
            ],

            explanation=
                explanation,

            source_type=
                "tu_vung",

            source_value=
                word,

            rng=rng,
        )

    # --------------------------------------------------------
    # Cau chon mot thu 5:
    # Pinyin Chu Han.
    #
    # Bai 13/14/16/17 it Chu Han van OK
    # vi chi can 1 chu Han cho cau nay.
    # --------------------------------------------------------

    if hanzi:

        item = hanzi[0]

        char = txt(
            item[
                "KyTu"
            ]
        )

        pinyin = txt(
            item[
                "Pinyin"
            ]
        )

        wrong = pick_wrong(
            pinyin,
            all_hanzi_pinyins,
            3,
            rng
        )

        add_choice(
            questions,
            "chon_mot",
            "chu_han",

            (
                "Pinyin đúng của "
                f"chữ “{char}” "
                "là gì?"
            ),

            [
                pinyin
            ] + wrong,

            [
                pinyin
            ],

            (
                f"Chữ “{char}” "
                f"đọc là {pinyin}."
            ),

            "chu_han",
            char,
            rng,
        )

    else:

        item = next(
            (
                item
                for item
                in vocabulary
                if txt(
                    item.get(
                        "PhienAm"
                    )
                )
            ),
            None
        )

        if item is None:
            raise ValueError(
                f"Bai {number}: "
                "khong co du lieu Pinyin"
            )

        word = txt(
            item[
                "ChuHan"
            ]
        )

        pinyin = txt(
            item[
                "PhienAm"
            ]
        )

        wrong = pick_wrong(
            pinyin,
            all_vocab_pinyins,
            3,
            rng
        )

        add_choice(
            questions,
            "chon_mot",
            "tu_vung",

            (
                "Pinyin đúng của "
                f"từ “{word}” "
                "là gì?"
            ),

            [
                pinyin
            ] + wrong,

            [
                pinyin
            ],

            (
                f"“{word}” "
                f"đọc là {pinyin}."
            ),

            "tu_vung",
            word,
            rng,
        )

    # --------------------------------------------------------
    # Cau chon mot thu 6:
    # ngu phap
    # --------------------------------------------------------

    first_grammar = grammar[
        0
    ]

    pattern = txt(
        first_grammar.get(
            "TenCauTruc"
        )
    )

    description = (
        grammar_description(
            first_grammar
        )
    )

    if description:

        wrong = pick_wrong(
            description,
            all_descriptions,
            3,
            rng
        )

        add_choice(
            questions,
            "chon_mot",
            "ngu_phap",

            (
                f"Cấu trúc “{pattern}” "
                "dùng để diễn đạt "
                "điều gì?"
            ),

            [
                description
            ] + wrong,

            [
                description
            ],

            (
                f"{pattern}: "
                f"{description}"
            ),

            "ngu_phap",
            pattern,
            rng,
        )

    else:

        wrong = pick_wrong(
            pattern,
            all_patterns,
            3,
            rng
        )

        add_choice(
            questions,
            "chon_mot",
            "ngu_phap",

            (
                "Chọn cấu trúc "
                "ngữ pháp được "
                "giới thiệu "
                "trong bài này."
            ),

            [
                pattern
            ] + wrong,

            [
                pattern
            ],

            (
                "Cấu trúc đúng "
                f"của bài: {pattern}."
            ),

            "ngu_phap",
            pattern,
            rng,
        )


    # ========================================================
    # 2. CHON NHIEU - 2 CAU
    # ========================================================

    # --------------------------------------------------------
    # Cau 1:
    # Chon 2 tu dung theo 2 nghia
    # --------------------------------------------------------

    word_item_1 = vocabulary[
        0
    ]

    word_item_2 = vocabulary[
        1
    ]

    word1 = txt(
        word_item_1[
            "ChuHan"
        ]
    )

    word2 = txt(
        word_item_2[
            "ChuHan"
        ]
    )

    meaning1 = txt(
        word_item_1[
            "NghiaTiengViet"
        ]
    )

    meaning2 = txt(
        word_item_2[
            "NghiaTiengViet"
        ]
    )

    distractors = wrong_vocab_rows(
        all_vocab_rows=
            all_vocab_rows,

        excluded_words=[
            word1,
            word2
        ],

        excluded_meanings=[
            meaning1,
            meaning2
        ],

        count=2,
        rng=rng,
    )

    wrong_words = [
        txt(
            item[
                "ChuHan"
            ]
        )
        for item
        in distractors
    ]

    add_choice(
        questions,
        "chon_nhieu",
        "tu_vung",

        (
            "Chọn 2 từ có nghĩa "
            "tương ứng với: "
            f"“{meaning1}” "
            f"và “{meaning2}”."
        ),

        [
            word1,
            word2
        ] + wrong_words,

        [
            word1,
            word2
        ],

        (
            "Hai từ đúng là "
            f"“{word1}” "
            f"và “{word2}”."
        ),

        "tu_vung",

        [
            word1,
            word2
        ],

        rng,
    )

    # --------------------------------------------------------
    # Cau 2:
    # Chon 2 cap ChuHan/Tu - Pinyin dung.
    #
    # Dung 2 cap dung
    # + 2 cap dao Pinyin de tao dap an sai.
    # --------------------------------------------------------

    pronunciation_pairs = (
        choose_distinct_pairs(
            hanzi,
            "KyTu",
            "Pinyin",
            4
        )
    )

    pair_source_type = (
        "chu_han"
    )

    pair_group = (
        "chu_han"
    )

    # Neu bai qua it Chu Han/Pinyin,
    # dung tu vung cua chinh bai.
    if len(
        pronunciation_pairs
    ) < 2:

        pronunciation_pairs = (
            choose_distinct_pairs(
                vocabulary,
                "ChuHan",
                "PhienAm",
                4
            )
        )

        pair_source_type = (
            "tu_vung"
        )

        pair_group = (
            "tu_vung"
        )

    if len(
        pronunciation_pairs
    ) < 2:
        raise ValueError(
            f"Bai {number}: "
            "khong du 2 cap "
            "Pinyin de tao "
            "chon_nhieu"
        )

    (
        _,
        left1,
        right1
    ) = pronunciation_pairs[
        0
    ]

    (
        _,
        left2,
        right2
    ) = pronunciation_pairs[
        1
    ]

    correct_pair1 = (
        f"{left1} — {right1}"
    )

    correct_pair2 = (
        f"{left2} — {right2}"
    )

    wrong_pair1 = (
        f"{left1} — {right2}"
    )

    wrong_pair2 = (
        f"{left2} — {right1}"
    )

    if len({
        correct_pair1,
        correct_pair2,
        wrong_pair1,
        wrong_pair2
    }) != 4:
        raise ValueError(
            f"Bai {number}: "
            "cap Pinyin "
            "khong du phan biet"
        )

    add_choice(
        questions,
        "chon_nhieu",
        pair_group,

        (
            "Chọn 2 cặp "
            "chữ/từ — Pinyin đúng."
        ),

        [
            correct_pair1,
            correct_pair2,
            wrong_pair1,
            wrong_pair2
        ],

        [
            correct_pair1,
            correct_pair2
        ],

        (
            "Các cặp đúng: "
            f"{correct_pair1}; "
            f"{correct_pair2}."
        ),

        pair_source_type,

        [
            left1,
            left2
        ],

        rng,
    )


    # ========================================================
    # 3. DUNG / SAI - 3 CAU
    # ========================================================

    # --------------------------------------------------------
    # Dung/Sai 1:
    # nghia tu vung
    # --------------------------------------------------------

    item = vocabulary[
        4
    ]

    word = txt(
        item[
            "ChuHan"
        ]
    )

    meaning = txt(
        item[
            "NghiaTiengViet"
        ]
    )

    # De cac bai khong bi
    # cung mot dap an het.
    truth = (
        number % 2
        == 1
    )

    if truth:
        shown_meaning = (
            meaning
        )

    else:
        shown_meaning = pick_wrong(
            meaning,
            all_meanings,
            1,
            rng
        )[0]

    add_true_false(
        questions,

        (
            f"Nhận định: “{word}” "
            "có nghĩa là "
            f"“{shown_meaning}”. "
            "Đúng hay Sai?"
        ),

        truth,

        (
            "Nghĩa đúng của "
            f"“{word}” là "
            f"“{meaning}”."
        ),

        "tu_vung",
        "tu_vung",
        word,
    )

    # --------------------------------------------------------
    # Dung/Sai 2:
    # Pinyin
    # --------------------------------------------------------

    if hanzi:

        item = hanzi[
            -1
        ]

        label = txt(
            item[
                "KyTu"
            ]
        )

        correct_pron = txt(
            item[
                "Pinyin"
            ]
        )

        pool = (
            all_hanzi_pinyins
        )

        source_type = (
            "chu_han"
        )

        group = (
            "chu_han"
        )

    else:

        item = next(
            (
                item
                for item
                in vocabulary
                if txt(
                    item.get(
                        "PhienAm"
                    )
                )
            ),
            None
        )

        if item is None:
            raise ValueError(
                f"Bai {number}: "
                "khong co Pinyin "
                "cho dung_sai"
            )

        label = txt(
            item[
                "ChuHan"
            ]
        )

        correct_pron = txt(
            item[
                "PhienAm"
            ]
        )

        pool = (
            all_vocab_pinyins
        )

        source_type = (
            "tu_vung"
        )

        group = (
            "tu_vung"
        )

    truth2 = (
        number % 3
        == 0
    )

    if truth2:
        shown_pron = (
            correct_pron
        )

    else:
        shown_pron = pick_wrong(
            correct_pron,
            pool,
            1,
            rng
        )[0]

    add_true_false(
        questions,

        (
            f"Nhận định: “{label}” "
            f"đọc là “{shown_pron}”. "
            "Đúng hay Sai?"
        ),

        truth2,

        (
            "Pinyin đúng của "
            f"“{label}” là "
            f"{correct_pron}."
        ),

        group,
        source_type,
        label,
    )

    # --------------------------------------------------------
    # Dung/Sai 3:
    # ngu phap
    # --------------------------------------------------------

    truth3 = (
        not truth
    )

    if description:

        if truth3:
            shown_description = (
                description
            )

        else:
            shown_description = (
                pick_wrong(
                    description,
                    all_descriptions,
                    1,
                    rng
                )[0]
            )

        content = (
            "Nhận định: cấu trúc "
            f"“{pattern}” "
            "có cách dùng: "
            f"“{shown_description}”. "
            "Đúng hay Sai?"
        )

        explanation = (
            "Cách dùng đúng của "
            f"“{pattern}”: "
            f"{description}"
        )

    else:

        if truth3:
            shown_pattern = (
                pattern
            )

        else:
            shown_pattern = (
                pick_wrong(
                    pattern,
                    all_patterns,
                    1,
                    rng
                )[0]
            )

        content = (
            f"Nhận định: “{shown_pattern}” "
            "là cấu trúc ngữ pháp "
            "được giới thiệu "
            "trong bài này. "
            "Đúng hay Sai?"
        )

        explanation = (
            "Cấu trúc ngữ pháp "
            f"của bài: {pattern}."
        )

    add_true_false(
        questions,
        content,
        truth3,
        explanation,
        "ngu_phap",
        "ngu_phap",
        pattern,
    )


    # ========================================================
    # 4. DIEN TU - 3 CAU
    # ========================================================

    grammar_fills = (
        grammar_fill_candidates(
            grammar
        )
    )

    used_fill_contents = set()

    # Uu tien toi da
    # 2 cau ngu phap that.
    for candidate in (
        grammar_fills[:2]
    ):

        add_fill(
            questions,

            candidate[
                "content"
            ],

            [
                candidate[
                    "answer"
                ]
            ],

            candidate[
                "explanation"
            ],

            "ngu_phap",
            "ngu_phap",

            candidate[
                "pattern"
            ],
        )

        used_fill_contents.add(
            normalize(
                candidate[
                    "content"
                ]
            )
        )

    # Neu ngu phap khong du
    # thi bu bang tu vung
    # cua chinh bai.

    fill_index = 0

    while sum(
        question[
            "LoaiCauHoi"
        ]
        == "dien_tu"

        for question
        in questions
    ) < 3:

        if (
            fill_index
            >= len(
                vocabulary
            )
        ):
            raise ValueError(
                f"Bai {number}: "
                "khong du du lieu "
                "tao 3 cau dien_tu"
            )

        item = vocabulary[
            fill_index
        ]

        fill_index += 1

        word = txt(
            item[
                "ChuHan"
            ]
        )

        meaning = txt(
            item[
                "NghiaTiengViet"
            ]
        )

        content = (
            "Điền chữ Hán "
            "phù hợp với "
            "nghĩa tiếng Việt: "
            f"“{meaning}”."
        )

        if (
            normalize(
                content
            )
            in used_fill_contents
        ):
            continue

        add_fill(
            questions,

            content,

            [
                word
            ],

            (
                f"Đáp án: "
                f"{word} — "
                f"{meaning}."
            ),

            "tu_vung",
            "tu_vung",
            word,
        )

        used_fill_contents.add(
            normalize(
                content
            )
        )


    # ========================================================
    # 5. GHEP CAP - 2 CAU
    # ========================================================

    # --------------------------------------------------------
    # Ghep tu vung -> nghia
    # --------------------------------------------------------

    vocab_pairs = (
        choose_distinct_pairs(
            vocabulary,
            "ChuHan",
            "NghiaTiengViet",
            4
        )
    )

    if len(
        vocab_pairs
    ) < 2:
        raise ValueError(
            f"Bai {number}: "
            "khong du cap "
            "tu vung - nghia"
        )

    pairs1 = [
        {
            "left":
                left,

            "right":
                right
        }

        for (
            _,
            left,
            right
        )
        in vocab_pairs
    ]

    add_matching(
        questions,

        (
            "Ghép mỗi từ vựng "
            "với nghĩa "
            "tiếng Việt đúng."
        ),

        pairs1,

        (
            "Mỗi từ phải được "
            "ghép với đúng nghĩa "
            "đã học trong bài."
        ),

        "tu_vung",
        "tu_vung",

        [
            left
            for (
                _,
                left,
                _
            )
            in vocab_pairs
        ],
    )

    # --------------------------------------------------------
    # Ghep Chu Han -> Pinyin
    # Neu bai co <2 cap thi
    # ghep Tu Vung -> Pinyin.
    # --------------------------------------------------------

    hanzi_pairs = (
        choose_distinct_pairs(
            hanzi,
            "KyTu",
            "Pinyin",
            4
        )
    )

    if len(
        hanzi_pairs
    ) >= 2:

        pairs2 = [
            {
                "left":
                    left,

                "right":
                    right
            }

            for (
                _,
                left,
                right
            )
            in hanzi_pairs
        ]

        add_matching(
            questions,

            (
                "Ghép mỗi chữ Hán "
                "với Pinyin đúng."
            ),

            pairs2,

            (
                "Ghép chữ Hán "
                "với cách đọc "
                "Pinyin tương ứng "
                "trong bài."
            ),

            "chu_han",
            "chu_han",

            [
                left
                for (
                    _,
                    left,
                    _
                )
                in hanzi_pairs
            ],
        )

    else:

        vocab_pinyin_pairs = (
            choose_distinct_pairs(
                vocabulary,
                "ChuHan",
                "PhienAm",
                4
            )
        )

        if len(
            vocab_pinyin_pairs
        ) < 2:
            raise ValueError(
                f"Bai {number}: "
                "khong du cap "
                "Pinyin cho ghep_cap"
            )

        pairs2 = [
            {
                "left":
                    left,

                "right":
                    right
            }

            for (
                _,
                left,
                right
            )
            in vocab_pinyin_pairs
        ]

        add_matching(
            questions,

            (
                "Ghép mỗi từ vựng "
                "với Pinyin đúng."
            ),

            pairs2,

            (
                "Ghép từ vựng "
                "với cách đọc "
                "Pinyin tương ứng "
                "trong bài."
            ),

            "tu_vung",
            "tu_vung",

            [
                left
                for (
                    _,
                    left,
                    _
                )
                in vocab_pinyin_pairs
            ],
        )


    # ========================================================
    # 6. SAP XEP - 2 CAU
    # ========================================================

    sort_candidates = (
        collect_sort_candidates(
            vocabulary,
            grammar
        )
    )

    if len(
        sort_candidates
    ) < 2:
        raise ValueError(
            f"Bai {number}: "
            "khong du "
            "2 du lieu sap_xep"
        )

    for candidate in (
        sort_candidates[:2]
    ):

        add_sort(
            questions,

            candidate[
                "content"
            ],

            candidate[
                "items"
            ],

            candidate[
                "explanation"
            ],

            candidate[
                "group"
            ],

            candidate[
                "source_type"
            ],

            candidate[
                "source_value"
            ],
        )


    # ========================================================
    # 7. VIET NGAN - 2 CAU
    # ========================================================

    short_candidates = (
        collect_short_candidates(
            vocabulary,
            grammar
        )
    )

    if len(
        short_candidates
    ) < 2:
        raise ValueError(
            f"Bai {number}: "
            "can it nhat "
            "2 vi du SQL "
            "de tao viet_ngan"
        )

    for candidate in (
        short_candidates[:2]
    ):

        add_short(
            questions,

            candidate[
                "content"
            ],

            candidate[
                "sample"
            ],

            candidate[
                "explanation"
            ],

            candidate[
                "group"
            ],

            candidate[
                "source_type"
            ],

            candidate[
                "source_value"
            ],
        )


    # ========================================================
    # DANH LAI THU TU 1 -> 20
    # ========================================================

    for index, question in enumerate(
        questions,
        start=1
    ):
        question[
            "ThuTu"
        ] = index


    # ========================================================
    # VALIDATE TRUOC KHI TRA VE
    # ========================================================

    validate(
        source,
        questions
    )

    return questions


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 78
    )

    print(
        "TAO PREVIEW CAU HOI HSK3 "
        "- 20 BAI - DU 7 DANG"
    )

    print(
        "Moi bai: "
        "6 chon_mot + "
        "2 chon_nhieu + "
        "3 dung_sai + "
        "3 dien_tu + "
        "2 ghep_cap + "
        "2 sap_xep + "
        "2 viet_ngan "
        "= 20"
    )

    print(
        "CHI DOC SQL - "
        "KHONG INSERT / UPDATE / DELETE"
    )

    print(
        "=" * 78
    )


    # ========================================================
    # KET NOI SQL
    # ========================================================

    with closing(
        get_connection()
    ) as conn:

        with closing(
            conn.cursor()
        ) as cur:


            # =================================================
            # DOC 20 BAI HSK3
            # =================================================

            lessons = rows(
                cur,
                """
                SELECT
                    MaBaiHoc,
                    MaKhoaHoc,
                    SoThuTuBai,
                    TieuDe,
                    TomTat,
                    TrangThai
                FROM dbo.BaiHoc
                WHERE MaKhoaHoc = ?
                ORDER BY
                    SoThuTuBai,
                    MaBaiHoc
                """,
                3,
            )

            if (
                len(
                    lessons
                ) != 20
                or
                [
                    int(
                        item[
                            "SoThuTuBai"
                        ]
                    )
                    for item
                    in lessons
                ]
                != list(
                    range(
                        1,
                        21
                    )
                )
            ):
                raise RuntimeError(
                    "Can dung "
                    "20 bai HSK3 "
                    "so 1-20, "
                    f"tim thay "
                    f"{len(lessons)} bai"
                )


            # =================================================
            # DOC TOAN BO TU VUNG HSK3
            # =================================================

            all_vocab_rows = rows(
                cur,
                """
                SELECT
                    tvbh.MaBaiHoc,
                    tvbh.ThuTu,

                    tv.MaTuVung,
                    tv.ChuHan,
                    tv.PhienAm,
                    tv.NghiaTiengViet,
                    tv.TuLoai,
                    tv.ViDuTiengTrung,
                    tv.ViDuTiengViet

                FROM dbo.TuVungBaiHoc
                    AS tvbh

                INNER JOIN dbo.TuVung
                    AS tv
                    ON tv.MaTuVung
                    = tvbh.MaTuVung

                INNER JOIN dbo.BaiHoc
                    AS bh
                    ON bh.MaBaiHoc
                    = tvbh.MaBaiHoc

                WHERE
                    bh.MaKhoaHoc = ?

                ORDER BY
                    bh.SoThuTuBai,
                    tvbh.ThuTu,
                    tv.MaTuVung
                """,
                3,
            )


            # =================================================
            # DOC TOAN BO NGU PHAP HSK3
            # =================================================

            all_grammar_rows = rows(
                cur,
                """
                SELECT
                    ng.MaNguPhap,
                    ng.MaBaiHoc,
                    ng.ThuTu,
                    ng.TenCauTruc,
                    ng.MoTa,
                    ng.CachDung,
                    ng.ViDuTiengTrung,
                    ng.ViDuPinyin,
                    ng.ViDuTiengViet,
                    ng.TrangThai

                FROM dbo.NguPhap
                    AS ng

                INNER JOIN dbo.BaiHoc
                    AS bh
                    ON bh.MaBaiHoc
                    = ng.MaBaiHoc

                WHERE
                    bh.MaKhoaHoc = ?

                ORDER BY
                    bh.SoThuTuBai,
                    ng.ThuTu,
                    ng.MaNguPhap
                """,
                3,
            )


            # =================================================
            # DOC TOAN BO CHU HAN HSK3
            # =================================================

            all_hanzi_rows = rows(
                cur,
                """
                SELECT
                    ch.MaChuHan,
                    ch.MaBaiHoc,
                    ch.ThuTu,
                    ch.KyTu,
                    ch.Pinyin,
                    ch.NghiaTiengViet,
                    ch.ViDuTiengTrung,
                    ch.ViDuPinyin,
                    ch.ViDuTiengViet,
                    ch.TrangThai

                FROM dbo.ChuHan
                    AS ch

                INNER JOIN dbo.BaiHoc
                    AS bh
                    ON bh.MaBaiHoc
                    = ch.MaBaiHoc

                WHERE
                    bh.MaKhoaHoc = ?

                ORDER BY
                    bh.SoThuTuBai,
                    ch.ThuTu,
                    ch.MaChuHan
                """,
                3,
            )


            # =================================================
            # OUTPUT PREVIEW
            # =================================================

            output = []


            # =================================================
            # TAO 20 BAI
            # =================================================

            for lesson in lessons:

                lesson_id = (
                    lesson[
                        "MaBaiHoc"
                    ]
                )

                number = int(
                    lesson[
                        "SoThuTuBai"
                    ]
                )


                # ---------------------------------------------
                # Tu vung cua rieng bai
                # ---------------------------------------------

                vocabulary = [
                    item
                    for item
                    in all_vocab_rows
                    if (
                        item[
                            "MaBaiHoc"
                        ]
                        == lesson_id
                    )
                ]


                # ---------------------------------------------
                # Ngu phap cua rieng bai
                # ---------------------------------------------

                grammar = [
                    item
                    for item
                    in all_grammar_rows
                    if (
                        item[
                            "MaBaiHoc"
                        ]
                        == lesson_id
                    )
                ]


                # ---------------------------------------------
                # Chu Han cua rieng bai
                # ---------------------------------------------

                hanzi = [
                    item
                    for item
                    in all_hanzi_rows
                    if (
                        item[
                            "MaBaiHoc"
                        ]
                        == lesson_id
                    )
                ]


                # ---------------------------------------------
                # Kiem tra BaiTap da ton tai hay chua
                # ---------------------------------------------

                existing_exercises = rows(
                    cur,
                    """
                    SELECT
                        MaBaiTap,
                        MaBaiHoc,
                        TieuDe,
                        HuongDan,
                        ThoiGianGioiHanGiay,
                        PhanTramDat,
                        TrangThai
                    FROM dbo.BaiTap
                    WHERE MaBaiHoc = ?
                    ORDER BY MaBaiTap
                    """,
                    lesson_id,
                )


                source = {
                    "lesson":
                        lesson,

                    "vocabulary":
                        vocabulary,

                    "grammar":
                        grammar,

                    "hanzi":
                        hanzi,

                    "existing_exercises":
                        existing_exercises,
                }


                # ---------------------------------------------
                # Tao dung 20 cau
                # ---------------------------------------------

                questions = build_questions(
                    source,
                    all_vocab_rows,
                    all_hanzi_rows,
                    all_grammar_rows,
                )


                # ---------------------------------------------
                # Object BaiTap PREVIEW
                # ---------------------------------------------

                output.append({
                    "MaKhoaHoc":
                        3,

                    "MaBaiHoc":
                        lesson_id,

                    "SoThuTuBai":
                        number,

                    "TieuDe": (
                        "Bài luyện tập "
                        f"Bài {number} - "
                        f"{txt(lesson.get('TieuDe'))}"
                    ),

                    "HuongDan": (
                        "Hoàn thành 20 câu hỏi "
                        "gồm 7 dạng về từ vựng, "
                        "ngữ pháp và chữ Hán "
                        "của bài học."
                    ),

                    "ThoiGianGioiHanGiay":
                        900,

                    "PhanTramDat":
                        70,

                    "TrangThai":
                        "ban_nhap",

                    "SoCauHoi":
                        len(
                            questions
                        ),

                    "CauHoi":
                        questions,
                })


                # ---------------------------------------------
                # Thong ke 7 dang
                # ---------------------------------------------

                counts = Counter(
                    question[
                        "LoaiCauHoi"
                    ]
                    for question
                    in questions
                )

                print(
                    f"Bai {number:02d} | "
                    f"MaBaiHoc={lesson_id} | "
                    f"chon_mot={counts['chon_mot']} | "
                    f"chon_nhieu={counts['chon_nhieu']} | "
                    f"dung_sai={counts['dung_sai']} | "
                    f"dien_tu={counts['dien_tu']} | "
                    f"ghep_cap={counts['ghep_cap']} | "
                    f"sap_xep={counts['sap_xep']} | "
                    f"viet_ngan={counts['viet_ngan']} | "
                    f"Tong={len(questions)}"
                )


            # =================================================
            # KHONG GHI SQL
            # =================================================

            conn.rollback()


    # ========================================================
    # CHI GHI JSON PREVIEW
    # ========================================================

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        dumps(
            output
        ) + "\n",
        encoding="utf-8"
    )


    # ========================================================
    # KET QUA
    # ========================================================

    print()

    print(
        "=" * 78
    )

    print(
        "Tong bai:",
        len(
            output
        )
    )

    print(
        "Tong cau hoi:",
        sum(
            item[
                "SoCauHoi"
            ]
            for item
            in output
        )
    )

    print(
        "File preview:",
        OUTPUT_FILE
    )

    print(
        "HOAN TAT - "
        "CHI TAO JSON PREVIEW, "
        "CHUA GHI SQL"
    )

    print(
        "=" * 78
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    try:
        main()

    except Exception as exc:

        print(
            f"LOI: {exc}"
        )

        raise SystemExit(
            1
        )