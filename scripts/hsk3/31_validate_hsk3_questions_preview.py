# -*- coding: utf-8 -*-

"""
BUOC 31 - VALIDATE PREVIEW CAU HOI HSK3

Kiem tra:
- 20 bai HSK3
- 400 cau hoi
- moi bai dung 20 cau
- du 7 dang cau hoi
- dung phan bo tung dang
- ThuTu 1 -> 20
- khong trung noi dung trong cung bai
- chon_mot / chon_nhieu co dung 4 lua chon
- DapAnJson dung cau truc cua Admin
- NguonLoai / NguonGiaTri thuoc CHINH bai hoc
- MaBaiHoc dung voi SQL
- khong co BaiTap HSK3 da ton tai
- schema cac bang can import van hop le

CHI DOC SQL.
KHONG INSERT / UPDATE / DELETE.
"""

import json
import re
import sys

from collections import Counter
from contextlib import closing
from pathlib import Path


# ============================================================
# DUONG DAN
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT)
)

from database import get_connection


PREVIEW_FILE = (
    ROOT
    / "scripts"
    / "hsk3"
    / "data"
    / "processed"
    / "exercises_hsk3_01_20_base_preview.json"
)


# ============================================================
# CAU HINH HSK3
# ============================================================

COURSE_ID = 3

FIRST_LESSON = 1

LAST_LESSON = 20

QUESTIONS_PER_LESSON = 20


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


KNOWLEDGE_GROUPS = {
    "tu_vung",
    "chu_han",
    "ngu_phap",
}


# ============================================================
# CAC COT CAN CO TRONG SQL
# ============================================================

REQUIRED_COLUMNS = {

    "BaiTap": {
        "MaBaiTap",
        "MaBaiHoc",
        "TieuDe",
        "HuongDan",
        "ThoiGianGioiHanGiay",
        "PhanTramDat",
        "TrangThai",
    },

    "CauHoi": {
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
        "MaQuanTriVienCapNhat",
        "NgayCapNhat",
    },

    "LuaChonCauHoi": {
        "MaLuaChon",
        "MaCauHoi",
        "NoiDungLuaChon",
        "LaDapAnDung",
        "ThuTu",
    },
}


# ============================================================
# HAM HO TRO
# ============================================================

def txt(value):
    if value is None:
        return ""

    return str(
        value
    ).strip()


def normalize(value):
    return re.sub(
        r"\s+",
        "",
        txt(value).lower()
    )


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


def source_values(value):
    """
    NguonGiaTri co the la:
    - string
    - list string

    VD:
    "学生"

    hoac:
    ["学生", "老师"]
    """

    if isinstance(
        value,
        list
    ):
        return [
            txt(item)
            for item
            in value
            if txt(item)
        ]

    value = txt(
        value
    )

    if value:
        return [
            value
        ]

    return []


# ============================================================
# KIEM TRA NGUON NGU PHAP
# ============================================================

def grammar_source_matches(
    value,
    grammar_names
):
    normalized_value = normalize(
        txt(value)
        .replace(
            "……",
            ""
        )
        .replace(
            "…",
            ""
        )
    )

    if not normalized_value:
        return False

    for name in grammar_names:

        normalized_name = normalize(
            txt(name)
            .replace(
                "……",
                ""
            )
            .replace(
                "…",
                ""
            )
        )

        if not normalized_name:
            continue

        if (
            normalized_value
            in normalized_name
            or
            normalized_name
            in normalized_value
        ):
            return True

    return False


# ============================================================
# VALIDATE LUA CHON
# ============================================================

def validate_choices(
    question,
    lesson_number
):
    qtype = question[
        "LoaiCauHoi"
    ]

    choices = question.get(
        "LuaChon"
    )

    if not isinstance(
        choices,
        list
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "LuaChon phai la list"
        )

    # --------------------------------------------------------
    # Phai dung 4 lua chon
    # --------------------------------------------------------

    if len(
        choices
    ) != 4:
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']} "
            f"({qtype}): "
            "phai co dung 4 lua chon"
        )

    # --------------------------------------------------------
    # ThuTu lua chon = 1,2,3,4
    # --------------------------------------------------------

    orders = [
        item.get(
            "ThuTu"
        )
        for item
        in choices
    ]

    if (
        orders
        != [
            1,
            2,
            3,
            4
        ]
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "ThuTu lua chon khong hop le"
        )

    # --------------------------------------------------------
    # Lua chon khong rong
    # --------------------------------------------------------

    texts = []

    for item in choices:

        content = txt(
            item.get(
                "NoiDungLuaChon"
            )
        )

        if not content:
            raise ValueError(
                f"Bai {lesson_number} "
                f"cau {question['ThuTu']}: "
                "co lua chon rong"
            )

        texts.append(
            content
        )

    # --------------------------------------------------------
    # Khong trung lua chon
    # --------------------------------------------------------

    normalized_texts = [
        normalize(
            item
        )
        for item
        in texts
    ]

    if len(
        set(
            normalized_texts
        )
    ) != 4:
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "lua chon bi trung"
        )

    # --------------------------------------------------------
    # Dem dap an dung
    # --------------------------------------------------------

    correct_count = sum(
        bool(
            item.get(
                "LaDapAnDung"
            )
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
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "chon_mot phai co "
            "dung 1 dap an"
        )

    if (
        qtype
        == "chon_nhieu"
        and correct_count
        != 2
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "chon_nhieu cua preview "
            "phai co dung 2 dap an"
        )

    # --------------------------------------------------------
    # Trac nghiem khong dung DapAnJson
    # --------------------------------------------------------

    if (
        question.get(
            "DapAnJson"
        )
        is not None
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            f"{qtype} "
            "khong duoc dung DapAnJson"
        )


# ============================================================
# VALIDATE DUNG / SAI
# ============================================================

def validate_true_false(
    question,
    lesson_number
):
    answer = question.get(
        "DapAnJson"
    )

    if not isinstance(
        answer,
        dict
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "dung_sai thieu DapAnJson"
        )

    if answer.get(
        "answer"
    ) not in (
        "dung",
        "sai"
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "dung_sai phai co "
            "answer = dung/sai"
        )

    if question.get(
        "LuaChon"
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "dung_sai khong dung "
            "LuaChon"
        )


# ============================================================
# VALIDATE DIEN TU
# ============================================================

def validate_fill(
    question,
    lesson_number
):
    answer = question.get(
        "DapAnJson"
    )

    if not isinstance(
        answer,
        dict
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "dien_tu thieu DapAnJson"
        )

    answers = answer.get(
        "answers"
    )

    if (
        not isinstance(
            answers,
            list
        )
        or not answers
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "dien_tu thieu answers"
        )

    for item in answers:

        if not txt(
            item
        ):
            raise ValueError(
                f"Bai {lesson_number} "
                f"cau {question['ThuTu']}: "
                "dien_tu co dap an rong"
            )

    if question.get(
        "LuaChon"
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "dien_tu khong dung LuaChon"
        )


# ============================================================
# VALIDATE GHEP CAP
# ============================================================

def validate_matching(
    question,
    lesson_number
):
    answer = question.get(
        "DapAnJson"
    )

    if not isinstance(
        answer,
        dict
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "ghep_cap thieu DapAnJson"
        )

    pairs = answer.get(
        "pairs"
    )

    if (
        not isinstance(
            pairs,
            list
        )
        or len(
            pairs
        ) < 2
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "ghep_cap can it nhat 2 cap"
        )

    left_values = []

    right_values = []

    for pair in pairs:

        if not isinstance(
            pair,
            dict
        ):
            raise ValueError(
                f"Bai {lesson_number} "
                f"cau {question['ThuTu']}: "
                "pair khong phai object"
            )

        left = txt(
            pair.get(
                "left"
            )
        )

        right = txt(
            pair.get(
                "right"
            )
        )

        if (
            not left
            or not right
        ):
            raise ValueError(
                f"Bai {lesson_number} "
                f"cau {question['ThuTu']}: "
                "ghep_cap co ve rong"
            )

        left_values.append(
            normalize(
                left
            )
        )

        right_values.append(
            normalize(
                right
            )
        )

    # Generator hien tai co chu dich
    # tao cac cap phan biet.
    if len(
        set(
            left_values
        )
    ) != len(
        left_values
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "ghep_cap trung ve trai"
        )

    if len(
        set(
            right_values
        )
    ) != len(
        right_values
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "ghep_cap trung ve phai"
        )

    if question.get(
        "LuaChon"
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "ghep_cap khong dung LuaChon"
        )


# ============================================================
# VALIDATE SAP XEP
# ============================================================

def validate_sorting(
    question,
    lesson_number
):
    answer = question.get(
        "DapAnJson"
    )

    if not isinstance(
        answer,
        dict
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "sap_xep thieu DapAnJson"
        )

    items = answer.get(
        "items"
    )

    if (
        not isinstance(
            items,
            list
        )
        or len(
            items
        ) < 2
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "sap_xep can it nhat "
            "2 thanh phan"
        )

    for item in items:

        if not txt(
            item
        ):
            raise ValueError(
                f"Bai {lesson_number} "
                f"cau {question['ThuTu']}: "
                "sap_xep co thanh phan rong"
            )

    if question.get(
        "LuaChon"
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "sap_xep khong dung LuaChon"
        )


# ============================================================
# VALIDATE VIET NGAN
# ============================================================

def validate_short_writing(
    question,
    lesson_number
):
    answer = question.get(
        "DapAnJson"
    )

    if not isinstance(
        answer,
        dict
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "viet_ngan thieu DapAnJson"
        )

    sample = txt(
        answer.get(
            "sample_answer"
        )
    )

    if not sample:
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "viet_ngan thieu "
            "sample_answer"
        )

    if (
        question.get(
            "KyNang"
        )
        != "viet"
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "viet_ngan phai co "
            "KyNang=viet"
        )

    if question.get(
        "LuaChon"
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "viet_ngan khong dung LuaChon"
        )


# ============================================================
# VALIDATE CAU HOI
# ============================================================

def validate_question(
    question,
    lesson_number
):
    required_fields = {
        "LoaiCauHoi",
        "KyNang",
        "NhomKienThuc",
        "NoiDungCauHoi",
        "DapAnJson",
        "GiaiThich",
        "DiemToiDa",
        "ThuTu",
        "NguonLoai",
        "NguonGiaTri",
        "LuaChon",
    }

    missing = (
        required_fields
        - set(
            question
        )
    )

    if missing:
        raise ValueError(
            f"Bai {lesson_number} "
            f"co cau hoi thieu field: "
            f"{sorted(missing)}"
        )

    qtype = question[
        "LoaiCauHoi"
    ]

    if (
        qtype
        not in QUESTION_TYPES
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"co LoaiCauHoi sai: "
            f"{qtype}"
        )

    if (
        question[
            "NhomKienThuc"
        ]
        not in KNOWLEDGE_GROUPS
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "NhomKienThuc khong hop le"
        )

    if (
        question[
            "NguonLoai"
        ]
        not in KNOWLEDGE_GROUPS
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "NguonLoai khong hop le"
        )

    if not txt(
        question[
            "NoiDungCauHoi"
        ]
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "NoiDungCauHoi rong"
        )

    if not txt(
        question[
            "GiaiThich"
        ]
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "thieu GiaiThich"
        )

    try:
        score = float(
            question[
                "DiemToiDa"
            ]
        )
    except (
        TypeError,
        ValueError
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "DiemToiDa khong phai so"
        )

    if score <= 0:
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "DiemToiDa phai > 0"
        )

    # --------------------------------------------------------
    # Ky nang
    # --------------------------------------------------------

    if (
        qtype
        != "viet_ngan"
        and question[
            "KyNang"
        ]
        != "doc"
    ):
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            f"{qtype} hien tai "
            "phai co KyNang=doc"
        )

    # --------------------------------------------------------
    # Theo tung loai
    # --------------------------------------------------------

    if qtype in (
        "chon_mot",
        "chon_nhieu"
    ):
        validate_choices(
            question,
            lesson_number
        )

    elif (
        qtype
        == "dung_sai"
    ):
        validate_true_false(
            question,
            lesson_number
        )

    elif (
        qtype
        == "dien_tu"
    ):
        validate_fill(
            question,
            lesson_number
        )

    elif (
        qtype
        == "ghep_cap"
    ):
        validate_matching(
            question,
            lesson_number
        )

    elif (
        qtype
        == "sap_xep"
    ):
        validate_sorting(
            question,
            lesson_number
        )

    elif (
        qtype
        == "viet_ngan"
    ):
        validate_short_writing(
            question,
            lesson_number
        )


# ============================================================
# DOC NGUON DU LIEU SQL CUA TUNG BAI
# ============================================================

def load_sql_sources(
    cursor,
    lesson_id
):

    # --------------------------------------------------------
    # TU VUNG
    # --------------------------------------------------------

    vocabulary = rows(
        cursor,
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
        ORDER BY
            tvbh.ThuTu,
            tv.MaTuVung
        """,
        lesson_id,
    )

    # --------------------------------------------------------
    # CHU HAN
    # --------------------------------------------------------

    hanzi = rows(
        cursor,
        """
        SELECT
            MaChuHan,
            KyTu,
            Pinyin
        FROM dbo.ChuHan
        WHERE MaBaiHoc = ?
        ORDER BY
            ThuTu,
            MaChuHan
        """,
        lesson_id,
    )

    # --------------------------------------------------------
    # NGU PHAP
    # --------------------------------------------------------

    grammar = rows(
        cursor,
        """
        SELECT
            MaNguPhap,
            TenCauTruc
        FROM dbo.NguPhap
        WHERE MaBaiHoc = ?
        ORDER BY
            ThuTu,
            MaNguPhap
        """,
        lesson_id,
    )

    return {
        "vocabulary":
            vocabulary,

        "hanzi":
            hanzi,

        "grammar":
            grammar,
    }


# ============================================================
# VALIDATE NGUON CAU HOI VOI SQL
# ============================================================

def validate_question_source(
    question,
    sql_source,
    lesson_number
):
    source_type = question[
        "NguonLoai"
    ]

    values = source_values(
        question[
            "NguonGiaTri"
        ]
    )

    if not values:
        raise ValueError(
            f"Bai {lesson_number} "
            f"cau {question['ThuTu']}: "
            "NguonGiaTri rong"
        )

    vocabulary_set = {
        txt(
            item.get(
                "ChuHan"
            )
        )
        for item
        in sql_source[
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
        in sql_source[
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
        in sql_source[
            "grammar"
        ]
        if txt(
            item.get(
                "TenCauTruc"
            )
        )
    ]

    for value in values:

        if (
            source_type
            == "tu_vung"
            and value
            not in vocabulary_set
        ):
            raise ValueError(
                f"Bai {lesson_number} "
                f"cau {question['ThuTu']}: "
                "tu vung khong thuoc bai: "
                f"{value}"
            )

        if (
            source_type
            == "chu_han"
            and value
            not in hanzi_set
        ):
            raise ValueError(
                f"Bai {lesson_number} "
                f"cau {question['ThuTu']}: "
                "chu Han khong thuoc bai: "
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
                f"Bai {lesson_number} "
                f"cau {question['ThuTu']}: "
                "ngu phap khong thuoc bai: "
                f"{value}"
            )


# ============================================================
# VALIDATE SCHEMA SQL
# ============================================================

def validate_schema(
    cursor
):
    print()

    print(
        "3. KIEM TRA SCHEMA SQL"
    )

    for table, required in (
        REQUIRED_COLUMNS.items()
    ):

        cursor.execute(
            """
            SELECT
                COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE
                TABLE_SCHEMA = 'dbo'
                AND TABLE_NAME = ?
            """,
            table,
        )

        actual = {
            row[0]
            for row
            in cursor.fetchall()
        }

        missing = (
            required
            - actual
        )

        if missing:
            raise ValueError(
                f"Bang {table} "
                "thieu cot: "
                f"{sorted(missing)}"
            )

        print(
            f"   {table}: OK"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 78
    )

    print(
        "BUOC 31 - "
        "VALIDATE PREVIEW CAU HOI HSK3"
    )

    print(
        "20 BAI - 400 CAU - "
        "DU 7 DANG"
    )

    print(
        "CHI DOC SQL - "
        "KHONG INSERT / UPDATE / DELETE"
    )

    print(
        "=" * 78
    )


    # ========================================================
    # 1. DOC FILE JSON
    # ========================================================

    if not PREVIEW_FILE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: "
            f"{PREVIEW_FILE}"
        )

    with open(
        PREVIEW_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(
            file
        )

    if not isinstance(
        data,
        list
    ):
        raise ValueError(
            "JSON goc phai la list"
        )

    if len(
        data
    ) != 20:
        raise ValueError(
            "Preview phai co dung "
            f"20 bai; hien co "
            f"{len(data)}"
        )

    print()

    print(
        "1. DOC JSON: OK"
    )

    print(
        "   Tong bai:",
        len(
            data
        )
    )


    # ========================================================
    # 2. VALIDATE CAU TRUC JSON
    # ========================================================

    lesson_orders = []

    lesson_ids = []

    all_questions = []

    print()

    print(
        "2. KIEM TRA 20 BAI"
    )

    for item in data:

        if not isinstance(
            item,
            dict
        ):
            raise ValueError(
                "Object bai tap "
                "khong phai dict"
            )

        course_id = item.get(
            "MaKhoaHoc"
        )

        lesson_id = item.get(
            "MaBaiHoc"
        )

        lesson_number = item.get(
            "SoThuTuBai"
        )

        questions = item.get(
            "CauHoi"
        )

        if (
            course_id
            != COURSE_ID
        ):
            raise ValueError(
                f"Bai {lesson_number}: "
                "MaKhoaHoc khong phai 3"
            )

        if not isinstance(
            lesson_number,
            int
        ):
            raise ValueError(
                "SoThuTuBai "
                "khong phai int"
            )

        if not isinstance(
            lesson_id,
            int
        ):
            raise ValueError(
                f"Bai {lesson_number}: "
                "MaBaiHoc "
                "khong phai int"
            )

        lesson_orders.append(
            lesson_number
        )

        lesson_ids.append(
            lesson_id
        )

        if (
            item.get(
                "TrangThai"
            )
            != "ban_nhap"
        ):
            raise ValueError(
                f"Bai {lesson_number}: "
                "TrangThai phai la "
                "ban_nhap"
            )

        if not isinstance(
            questions,
            list
        ):
            raise ValueError(
                f"Bai {lesson_number}: "
                "CauHoi khong phai list"
            )

        if len(
            questions
        ) != 20:
            raise ValueError(
                f"Bai {lesson_number}: "
                f"co {len(questions)} cau, "
                "can dung 20"
            )

        if (
            item.get(
                "SoCauHoi"
            )
            != 20
        ):
            raise ValueError(
                f"Bai {lesson_number}: "
                "SoCauHoi khong bang 20"
            )

        # ----------------------------------------------------
        # ThuTu cau
        # ----------------------------------------------------

        orders = [
            question.get(
                "ThuTu"
            )
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
                f"Bai {lesson_number}: "
                "ThuTu phai la 1 -> 20"
            )

        # ----------------------------------------------------
        # Khong trung noi dung
        # ----------------------------------------------------

        contents = [
            normalize(
                question.get(
                    "NoiDungCauHoi"
                )
            )
            for question
            in questions
        ]

        if len(
            set(
                contents
            )
        ) != 20:
            raise ValueError(
                f"Bai {lesson_number}: "
                "co cau hoi trung noi dung"
            )

        # ----------------------------------------------------
        # Dung phan bo 7 dang
        # ----------------------------------------------------

        counts = Counter(
            question.get(
                "LoaiCauHoi"
            )
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
                f"Bai {lesson_number}: "
                "sai phan bo 7 dang: "
                f"{dict(counts)}"
            )

        # ----------------------------------------------------
        # Validate tung cau
        # ----------------------------------------------------

        for question in questions:

            validate_question(
                question,
                lesson_number
            )

            all_questions.append(
                question
            )

        print(
            f"   Bai {lesson_number:02d} | "
            f"MaBaiHoc={lesson_id} | "
            "20 cau | "
            "7 dang: OK"
        )


    # ========================================================
    # KIEM TRA SO THU TU BAI
    # ========================================================

    if (
        sorted(
            lesson_orders
        )
        != list(
            range(
                FIRST_LESSON,
                LAST_LESSON + 1
            )
        )
    ):
        raise ValueError(
            "SoThuTuBai "
            "khong dung 1 -> 20"
        )

    if len(
        set(
            lesson_ids
        )
    ) != 20:
        raise ValueError(
            "MaBaiHoc bi trung"
        )

    if len(
        all_questions
    ) != 400:
        raise ValueError(
            f"Tong cau hoi "
            f"khong bang 400: "
            f"{len(all_questions)}"
        )


    # ========================================================
    # 3. SQL
    # ========================================================

    with closing(
        get_connection()
    ) as conn:

        with closing(
            conn.cursor()
        ) as cursor:


            # =================================================
            # SCHEMA
            # =================================================

            validate_schema(
                cursor
            )


            # =================================================
            # 4. KIEM TRA BAI HOC HSK3
            # =================================================

            print()

            print(
                "4. KIEM TRA BAI HOC HSK3"
            )

            sql_lessons = rows(
                cursor,
                """
                SELECT
                    MaBaiHoc,
                    MaKhoaHoc,
                    SoThuTuBai,
                    TieuDe
                FROM dbo.BaiHoc
                WHERE
                    MaKhoaHoc = ?
                    AND SoThuTuBai
                        BETWEEN ? AND ?
                ORDER BY
                    SoThuTuBai,
                    MaBaiHoc
                """,
                COURSE_ID,
                FIRST_LESSON,
                LAST_LESSON,
            )

            if len(
                sql_lessons
            ) != 20:
                raise ValueError(
                    "SQL khong co dung "
                    "20 bai HSK3"
                )

            sql_lesson_map = {
                int(
                    item[
                        "SoThuTuBai"
                    ]
                ):
                int(
                    item[
                        "MaBaiHoc"
                    ]
                )
                for item
                in sql_lessons
            }

            for item in data:

                number = int(
                    item[
                        "SoThuTuBai"
                    ]
                )

                lesson_id = int(
                    item[
                        "MaBaiHoc"
                    ]
                )

                expected_id = (
                    sql_lesson_map.get(
                        number
                    )
                )

                if (
                    expected_id
                    != lesson_id
                ):
                    raise ValueError(
                        f"Bai {number}: "
                        "MaBaiHoc trong JSON "
                        f"= {lesson_id}, "
                        "nhung SQL = "
                        f"{expected_id}"
                    )

            print(
                "   20 MaBaiHoc "
                "khop SQL: OK"
            )


            # =================================================
            # 5. KIEM TRA CHUA CO BAI TAP
            # =================================================

            print()

            print(
                "5. KIEM TRA BAI TAP HIEN CO"
            )

            cursor.execute(
                """
                SELECT
                    bt.MaBaiTap,
                    bt.MaBaiHoc,
                    bh.SoThuTuBai,
                    bt.TieuDe,
                    bt.TrangThai
                FROM dbo.BaiTap AS bt
                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc
                    = bt.MaBaiHoc
                WHERE
                    bh.MaKhoaHoc = ?
                    AND bh.SoThuTuBai
                        BETWEEN ? AND ?
                ORDER BY
                    bh.SoThuTuBai,
                    bt.MaBaiTap
                """,
                COURSE_ID,
                FIRST_LESSON,
                LAST_LESSON,
            )

            existing = (
                cursor.fetchall()
            )

            if existing:

                print()

                print(
                    "   PHAT HIEN BAI TAP "
                    "HSK3 DA TON TAI:"
                )

                for row in existing:

                    print(
                        "   ",
                        tuple(
                            row
                        )
                    )

                raise ValueError(
                    "HSK3 da co BaiTap. "
                    "DUNG de tranh import trung."
                )

            print(
                "   Chua co BaiTap HSK3: OK"
            )


            # =================================================
            # 6. KIEM TRA NGUON TUNG CAU
            # =================================================

            print()

            print(
                "6. KIEM TRA NGUON "
                "400 CAU VOI SQL"
            )

            for item in data:

                lesson_id = int(
                    item[
                        "MaBaiHoc"
                    ]
                )

                lesson_number = int(
                    item[
                        "SoThuTuBai"
                    ]
                )

                sql_source = (
                    load_sql_sources(
                        cursor,
                        lesson_id
                    )
                )

                for question in item[
                    "CauHoi"
                ]:

                    validate_question_source(
                        question,
                        sql_source,
                        lesson_number
                    )

                print(
                    f"   Bai "
                    f"{lesson_number:02d}: "
                    "nguon dung bai: OK"
                )


        # ====================================================
        # KHONG GHI SQL
        # ====================================================

        conn.rollback()


    # ========================================================
    # THONG KE TOAN BO
    # ========================================================

    total_counts = Counter(
        question[
            "LoaiCauHoi"
        ]
        for question
        in all_questions
    )

    expected_total_counts = {
        key:
            value * 20
        for key, value
        in TARGET_COUNTS.items()
    }

    if (
        total_counts
        != Counter(
            expected_total_counts
        )
    ):
        raise ValueError(
            "Tong phan bo "
            "7 dang khong dung"
        )


    # ========================================================
    # KET QUA
    # ========================================================

    print()

    print(
        "=" * 78
    )

    print(
        "VALIDATE HSK3: THANH CONG"
    )

    print(
        "=" * 78
    )

    print(
        "Tong bai:",
        len(
            data
        )
    )

    print(
        "Tong cau hoi:",
        len(
            all_questions
        )
    )

    print()

    print(
        "Phan bo toan HSK3:"
    )

    for qtype in TARGET_COUNTS:

        print(
            f"   {qtype}: "
            f"{total_counts[qtype]}"
        )

    print()

    print(
        "Tat ca cau hoi "
        "thuoc dung HSK3 "
        "va dung bai hoc."
    )

    print(
        "Cau truc dap an "
        "phu hop 7 dang Admin."
    )

    print(
        "KHONG CO DU LIEU "
        "NAO DUOC GHI VAO SQL."
    )

    print()

    print(
        "=> PREVIEW SAN SANG "
        "CHO BUOC DRY RUN IMPORT."
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

        print()

        print(
            "LOI:",
            exc
        )

        raise SystemExit(
            1
        )