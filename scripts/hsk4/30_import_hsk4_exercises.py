# -*- coding: utf-8 -*-

"""
BUOC 30 - IMPORT BAI TAP HSK4

Mac dinh:
- Doc file preview HSK4 da validate.
- INSERT thu trong 1 transaction.
- Kiem tra:
    + 20 BaiTap
    + 400 CauHoi
    + 640 LuaChonCauHoi
    + dung phan bo 7 dang
    + dung KyNang
    + dung DapAnJson
    + dung so dap an trac nghiem
- ROLLBACK.
- KHONG luu SQL.

Chi khi truyen --commit:
- COMMIT transaction.

LUU Y:
KHONG CHAY --commit TRUOC KHI DRY RUN THANH CONG.
"""

import argparse
import json
import sys

from collections import Counter
from contextlib import closing
from decimal import Decimal
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

PREVIEW_FILE = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
    / "exercises_hsk4_01_20_base_preview.json"
)


# ============================================================
# CAU HINH
# ============================================================

DATABASE_NAME = "HocTiengTrungDB"

COURSE_ID = 4

FIRST_LESSON = 1
LAST_LESSON = 20

EXPECTED_EXERCISES = 20
EXPECTED_QUESTIONS = 400

# Moi bai:
#
# 6 chon_mot
# 2 chon_nhieu
#
# Tong 8 cau co lua chon / bai
#
# Moi cau 4 lua chon
#
# 8 * 4 * 20 = 640

EXPECTED_CHOICES = 640


TARGET_COUNTS_PER_LESSON = {
    "chon_mot": 6,
    "chon_nhieu": 2,
    "dung_sai": 3,
    "dien_tu": 3,
    "ghep_cap": 2,
    "sap_xep": 2,
    "viet_ngan": 2,
}


EXPECTED_TOTAL_TYPES = {
    "chon_mot": 120,
    "chon_nhieu": 40,
    "dung_sai": 60,
    "dien_tu": 60,
    "ghep_cap": 40,
    "sap_xep": 40,
    "viet_ngan": 40,
}


QUESTION_TYPES = set(
    TARGET_COUNTS_PER_LESSON
)


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

    return "".join(
        txt(value)
        .lower()
        .split()
    )


# ============================================================
# DOC PREVIEW
# ============================================================

def load_preview():

    if not PREVIEW_FILE.exists():

        raise FileNotFoundError(
            f"Khong tim thay preview: "
            f"{PREVIEW_FILE}"
        )

    with PREVIEW_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(
            file
        )

    return data


# ============================================================
# VALIDATE PREVIEW TRUOC KHI INSERT
# ============================================================

def validate_preview(data):

    if not isinstance(
        data,
        list
    ):
        raise ValueError(
            "Preview phai la list"
        )

    if len(
        data
    ) != EXPECTED_EXERCISES:
        raise ValueError(
            "Preview phai co dung "
            f"{EXPECTED_EXERCISES} bai"
        )

    lesson_numbers = []
    lesson_ids = []

    total_questions = 0
    total_choices = 0

    total_types = Counter()


    for exercise in data:

        # ====================================================
        # KHOA HOC HSK4
        # ====================================================

        if (
            exercise.get(
                "MaKhoaHoc"
            )
            != COURSE_ID
        ):
            raise ValueError(
                "Preview co bai "
                "khong thuoc HSK4"
            )


        lesson_id = exercise.get(
            "MaBaiHoc"
        )

        lesson_number = exercise.get(
            "SoThuTuBai"
        )


        if not isinstance(
            lesson_id,
            int
        ):
            raise ValueError(
                "MaBaiHoc khong hop le"
            )


        if not isinstance(
            lesson_number,
            int
        ):
            raise ValueError(
                "SoThuTuBai khong hop le"
            )


        lesson_ids.append(
            lesson_id
        )

        lesson_numbers.append(
            lesson_number
        )


        # ====================================================
        # TRANG THAI
        # ====================================================

        if (
            exercise.get(
                "TrangThai"
            )
            != "ban_nhap"
        ):
            raise ValueError(
                f"Bai {lesson_number}: "
                "TrangThai phai la ban_nhap"
            )


        # ====================================================
        # CAU HOI
        # ====================================================

        questions = exercise.get(
            "CauHoi"
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
                "khong co dung 20 cau"
            )


        if (
            exercise.get(
                "SoCauHoi"
            )
            != 20
        ):
            raise ValueError(
                f"Bai {lesson_number}: "
                "SoCauHoi khong bang 20"
            )


        # ====================================================
        # THU TU 1 -> 20
        # ====================================================

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
                "ThuTu cau hoi sai"
            )


        # ====================================================
        # KHONG TRUNG NOI DUNG
        # ====================================================

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


        # ====================================================
        # PHAN BO 7 DANG
        # ====================================================

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
                TARGET_COUNTS_PER_LESSON
            )
        ):
            raise ValueError(
                f"Bai {lesson_number}: "
                "sai phan bo 7 dang: "
                f"{dict(counts)}"
            )


        # ====================================================
        # VALIDATE TUNG CAU
        # ====================================================

        for question in questions:

            qtype = question.get(
                "LoaiCauHoi"
            )


            if (
                qtype
                not in QUESTION_TYPES
            ):
                raise ValueError(
                    f"Bai {lesson_number}: "
                    "LoaiCauHoi sai: "
                    f"{qtype}"
                )


            if not txt(
                question.get(
                    "NoiDungCauHoi"
                )
            ):
                raise ValueError(
                    f"Bai {lesson_number}: "
                    "co cau hoi rong"
                )


            if not txt(
                question.get(
                    "GiaiThich"
                )
            ):
                raise ValueError(
                    f"Bai {lesson_number}: "
                    "co cau thieu GiaiThich"
                )


            try:

                score = Decimal(
                    str(
                        question.get(
                            "DiemToiDa",
                            0
                        )
                    )
                )

            except Exception:

                raise ValueError(
                    f"Bai {lesson_number}: "
                    "DiemToiDa khong hop le"
                )


            if score <= 0:

                raise ValueError(
                    f"Bai {lesson_number}: "
                    "DiemToiDa phai > 0"
                )


            choices = (
                question.get(
                    "LuaChon"
                )
                or []
            )


            answer_json = question.get(
                "DapAnJson"
            )


            # =================================================
            # CHON MOT
            # =================================================

            if qtype == "chon_mot":

                if len(
                    choices
                ) != 4:

                    raise ValueError(
                        f"Bai {lesson_number}: "
                        "chon_mot phai co "
                        "4 lua chon"
                    )


                correct_count = sum(
                    bool(
                        item.get(
                            "LaDapAnDung"
                        )
                    )
                    for item
                    in choices
                )


                if correct_count != 1:

                    raise ValueError(
                        f"Bai {lesson_number}: "
                        "chon_mot phai co "
                        "1 dap an dung"
                    )


                if (
                    answer_json
                    is not None
                ):

                    raise ValueError(
                        f"Bai {lesson_number}: "
                        "chon_mot khong dung "
                        "DapAnJson"
                    )


            # =================================================
            # CHON NHIEU
            # =================================================

            elif qtype == "chon_nhieu":

                if len(
                    choices
                ) != 4:

                    raise ValueError(
                        f"Bai {lesson_number}: "
                        "chon_nhieu phai co "
                        "4 lua chon"
                    )


                correct_count = sum(
                    bool(
                        item.get(
                            "LaDapAnDung"
                        )
                    )
                    for item
                    in choices
                )


                if correct_count != 2:

                    raise ValueError(
                        f"Bai {lesson_number}: "
                        "chon_nhieu phai co "
                        "2 dap an dung"
                    )


                if (
                    answer_json
                    is not None
                ):

                    raise ValueError(
                        f"Bai {lesson_number}: "
                        "chon_nhieu khong dung "
                        "DapAnJson"
                    )


            # =================================================
            # 5 LOAI DUNG DapAnJson
            # =================================================

            else:

                if choices:

                    raise ValueError(
                        f"Bai {lesson_number}: "
                        f"{qtype} "
                        "khong duoc co LuaChon"
                    )


                if not isinstance(
                    answer_json,
                    dict
                ):

                    raise ValueError(
                        f"Bai {lesson_number}: "
                        f"{qtype} "
                        "thieu DapAnJson"
                    )


                if qtype == "dung_sai":

                    if answer_json.get(
                        "answer"
                    ) not in (
                        "dung",
                        "sai"
                    ):

                        raise ValueError(
                            f"Bai {lesson_number}: "
                            "dung_sai sai "
                            "DapAnJson"
                        )


                elif qtype == "dien_tu":

                    answers = answer_json.get(
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
                            f"Bai {lesson_number}: "
                            "dien_tu sai "
                            "DapAnJson"
                        )


                elif qtype == "ghep_cap":

                    pairs = answer_json.get(
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
                            f"Bai {lesson_number}: "
                            "ghep_cap sai "
                            "DapAnJson"
                        )


                elif qtype == "sap_xep":

                    items = answer_json.get(
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
                            f"Bai {lesson_number}: "
                            "sap_xep sai "
                            "DapAnJson"
                        )


                elif qtype == "viet_ngan":

                    if not txt(
                        answer_json.get(
                            "sample_answer"
                        )
                    ):

                        raise ValueError(
                            f"Bai {lesson_number}: "
                            "viet_ngan sai "
                            "DapAnJson"
                        )


            # =================================================
            # DEM
            # =================================================

            total_questions += 1

            total_choices += len(
                choices
            )

            total_types[
                qtype
            ] += 1


    # ========================================================
    # SO THU TU 20 BAI
    # ========================================================

    if (
        sorted(
            lesson_numbers
        )
        != list(
            range(
                FIRST_LESSON,
                LAST_LESSON + 1
            )
        )
    ):

        raise ValueError(
            "SoThuTuBai khong dung "
            "1 -> 20"
        )


    # ========================================================
    # MA BAI HOC KHONG TRUNG
    # ========================================================

    if len(
        set(
            lesson_ids
        )
    ) != EXPECTED_EXERCISES:

        raise ValueError(
            "MaBaiHoc bi trung"
        )


    # ========================================================
    # TONG CAU HOI
    # ========================================================

    if (
        total_questions
        != EXPECTED_QUESTIONS
    ):

        raise ValueError(
            "Tong cau hoi JSON sai: "
            f"{total_questions}"
        )


    # ========================================================
    # TONG LUA CHON
    # ========================================================

    if (
        total_choices
        != EXPECTED_CHOICES
    ):

        raise ValueError(
            "Tong LuaChon JSON sai: "
            f"{total_choices}"
        )


    # ========================================================
    # PHAN BO TOAN HSK4
    # ========================================================

    if (
        total_types
        != Counter(
            EXPECTED_TOTAL_TYPES
        )
    ):

        raise ValueError(
            "Phan bo 7 dang "
            "toan HSK4 sai: "
            f"{dict(total_types)}"
        )


# ============================================================
# CHON ADMIN
# ============================================================

def choose_admin(
    cursor,
    requested_id
):

    cursor.execute(
        """
        SELECT
            MaQuanTriVien,
            TenDangNhap
        FROM dbo.QuanTriVien
        WHERE DangHoatDong = 1
        ORDER BY MaQuanTriVien
        """
    )


    admins = (
        cursor.fetchall()
    )


    if not admins:

        raise ValueError(
            "Khong co QuanTriVien "
            "dang hoat dong"
        )


    # ========================================================
    # USER DA CHI DINH --admin-id
    # ========================================================

    if (
        requested_id
        is not None
    ):

        for admin in admins:

            if (
                int(
                    admin[0]
                )
                == requested_id
            ):

                return (
                    requested_id,
                    txt(
                        admin[1]
                    )
                )


        raise ValueError(
            f"Admin ID "
            f"{requested_id} "
            "khong ton tai "
            "hoac khong hoat dong"
        )


    # ========================================================
    # NEU CHI CO 1 ADMIN
    # ========================================================

    if len(
        admins
    ) == 1:

        return (
            int(
                admins[0][0]
            ),
            txt(
                admins[0][1]
            )
        )


    # ========================================================
    # NEU CO NHIEU ADMIN
    # ========================================================

    print()

    print(
        "CO NHIEU ADMIN DANG HOAT DONG:"
    )


    for admin in admins:

        print(
            f"   ID={admin[0]} | "
            f"TenDangNhap={admin[1]}"
        )


    raise ValueError(
        "Hay chay lai voi "
        "--admin-id MA_ADMIN"
    )


# ============================================================
# KIEM TRA DATABASE
# ============================================================

def validate_database(
    cursor
):

    cursor.execute(
        "SELECT DB_NAME()"
    )


    database_name = txt(
        cursor.fetchone()[0]
    )


    if (
        database_name.lower()
        != DATABASE_NAME.lower()
    ):

        raise ValueError(
            "DANG KET NOI NHAM DATABASE: "
            f"{database_name}"
        )


    print(
        "Database:",
        database_name
    )


# ============================================================
# KIEM TRA 20 BAI HOC HSK4
# ============================================================

def validate_lessons(
    cursor,
    exercises
):

    cursor.execute(
        """
        SELECT
            MaBaiHoc,
            SoThuTuBai
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


    sql_rows = (
        cursor.fetchall()
    )


    if len(
        sql_rows
    ) != EXPECTED_EXERCISES:

        raise ValueError(
            "SQL khong co dung "
            "20 bai HSK4"
        )


    sql_map = {
        int(
            row[1]
        ):
        int(
            row[0]
        )
        for row
        in sql_rows
    }


    for exercise in exercises:

        number = int(
            exercise[
                "SoThuTuBai"
            ]
        )

        lesson_id = int(
            exercise[
                "MaBaiHoc"
            ]
        )


        if (
            sql_map.get(
                number
            )
            != lesson_id
        ):

            raise ValueError(
                f"Bai {number}: "
                "MaBaiHoc preview "
                "khong khop SQL"
            )


# ============================================================
# LOCK + KIEM TRA KHONG CO BAI TAP CU
# ============================================================

def verify_no_existing(
    cursor,
    exercises
):

    for exercise in exercises:

        lesson_id = int(
            exercise[
                "MaBaiHoc"
            ]
        )


        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.BaiTap
                WITH (
                    UPDLOCK,
                    HOLDLOCK
                )
            WHERE MaBaiHoc = ?
            """,
            lesson_id,
        )


        count = int(
            cursor.fetchone()[0]
        )


        if count != 0:

            raise ValueError(
                "MaBaiHoc="
                f"{lesson_id} "
                "da co BaiTap. "
                "DUNG IMPORT "
                "de tranh trung du lieu."
            )


# ============================================================
# INSERT 20 BAI TAP + 400 CAU HOI + 640 LUA CHON
# ============================================================

def import_exercises(
    cursor,
    exercises,
    admin_id
):

    inserted_exercises = 0
    inserted_questions = 0
    inserted_choices = 0


    for exercise in exercises:

        # ====================================================
        # 1. INSERT BAI TAP
        # ====================================================

        cursor.execute(
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
            (
                ?, ?, ?, ?, ?, ?, ?,
                SYSDATETIME()
            )
            """,

            exercise[
                "MaBaiHoc"
            ],

            exercise[
                "TieuDe"
            ],

            exercise.get(
                "HuongDan"
            ),

            exercise.get(
                "ThoiGianGioiHanGiay"
            ),

            Decimal(
                str(
                    exercise[
                        "PhanTramDat"
                    ]
                )
            ),

            "ban_nhap",

            admin_id,
        )


        exercise_id = int(
            cursor.fetchone()[0]
        )


        inserted_exercises += 1


        # ====================================================
        # 2. INSERT 20 CAU HOI
        # ====================================================

        for question in exercise[
            "CauHoi"
        ]:

            answer_json = (
                question.get(
                    "DapAnJson"
                )
            )


            # ------------------------------------------------
            # DICT PYTHON -> JSON STRING
            # ------------------------------------------------

            if (
                answer_json
                is not None
            ):

                answer_json = (
                    json.dumps(
                        answer_json,
                        ensure_ascii=False
                    )
                )


            cursor.execute(
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
                (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    SYSDATETIME()
                )
                """,

                exercise_id,

                question[
                    "LoaiCauHoi"
                ],

                question[
                    "KyNang"
                ],

                question[
                    "NoiDungCauHoi"
                ],

                # Preview HSK4 hien tai
                # khong dung DoanVan rieng.
                None,

                # Chua gan media
                None,

                answer_json,

                question[
                    "GiaiThich"
                ],

                Decimal(
                    str(
                        question[
                            "DiemToiDa"
                        ]
                    )
                ),

                question[
                    "ThuTu"
                ],

                admin_id,
            )


            question_id = int(
                cursor.fetchone()[0]
            )


            inserted_questions += 1


            # =================================================
            # 3. INSERT LUA CHON
            #
            # Chi chon_mot va chon_nhieu co LuaChon.
            # =================================================

            for option in (
                question.get(
                    "LuaChon"
                )
                or []
            ):

                cursor.execute(
                    """
                    INSERT INTO dbo.LuaChonCauHoi
                    (
                        MaCauHoi,
                        NoiDungLuaChon,
                        LaDapAnDung,
                        ThuTu
                    )
                    VALUES
                    (
                        ?, ?, ?, ?
                    )
                    """,

                    question_id,

                    option[
                        "NoiDungLuaChon"
                    ],

                    (
                        1
                        if option[
                            "LaDapAnDung"
                        ]
                        else 0
                    ),

                    option[
                        "ThuTu"
                    ],
                )


                inserted_choices += 1


        print(
            f"INSERT Bai "
            f"{exercise['SoThuTuBai']:02d}"
            f" | MaBaiHoc="
            f"{exercise['MaBaiHoc']}"
            f" | MaBaiTap tam="
            f"{exercise_id}"
        )


    return (
        inserted_exercises,
        inserted_questions,
        inserted_choices,
    )


# ============================================================
# KIEM TRA DU LIEU TRONG TRANSACTION
# ============================================================

def verify_transaction(
    cursor,
    inserted_exercises,
    inserted_questions,
    inserted_choices,
):

    # ========================================================
    # 1. SO BAN GHI INSERT
    # ========================================================

    if (
        inserted_exercises
        != EXPECTED_EXERCISES
    ):

        raise ValueError(
            "Sai so BaiTap INSERT: "
            f"{inserted_exercises}"
        )


    if (
        inserted_questions
        != EXPECTED_QUESTIONS
    ):

        raise ValueError(
            "Sai so CauHoi INSERT: "
            f"{inserted_questions}"
        )


    if (
        inserted_choices
        != EXPECTED_CHOICES
    ):

        raise ValueError(
            "Sai so LuaChon INSERT: "
            f"{inserted_choices}"
        )


    # ========================================================
    # 2. DEM TOAN HSK4 TRONG TRANSACTION
    # ========================================================

    cursor.execute(
        """
        SELECT
            COUNT(
                DISTINCT bt.MaBaiTap
            ),
            COUNT(
                DISTINCT ch.MaCauHoi
            )

        FROM dbo.BaiHoc AS bh

        LEFT JOIN dbo.BaiTap AS bt
            ON bt.MaBaiHoc
            = bh.MaBaiHoc

        LEFT JOIN dbo.CauHoi AS ch
            ON ch.MaBaiTap
            = bt.MaBaiTap

        WHERE
            bh.MaKhoaHoc = ?
            AND bh.SoThuTuBai
                BETWEEN ? AND ?
        """,
        COURSE_ID,
        FIRST_LESSON,
        LAST_LESSON,
    )


    (
        exercise_count,
        question_count
    ) = cursor.fetchone()


    exercise_count = int(
        exercise_count
    )

    question_count = int(
        question_count
    )


    if (
        exercise_count
        != EXPECTED_EXERCISES
    ):

        raise ValueError(
            "Trong transaction "
            "HSK4 khong co dung "
            "20 BaiTap: "
            f"{exercise_count}"
        )


    if (
        question_count
        != EXPECTED_QUESTIONS
    ):

        raise ValueError(
            "Trong transaction "
            "HSK4 khong co dung "
            "400 CauHoi: "
            f"{question_count}"
        )


    # ========================================================
    # 3. DEM LUA CHON HSK4
    # ========================================================

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM dbo.LuaChonCauHoi AS lc

        INNER JOIN dbo.CauHoi AS ch
            ON ch.MaCauHoi
            = lc.MaCauHoi

        INNER JOIN dbo.BaiTap AS bt
            ON bt.MaBaiTap
            = ch.MaBaiTap

        INNER JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc
            = bt.MaBaiHoc

        WHERE
            bh.MaKhoaHoc = ?
            AND bh.SoThuTuBai
                BETWEEN ? AND ?
        """,
        COURSE_ID,
        FIRST_LESSON,
        LAST_LESSON,
    )


    choice_count = int(
        cursor.fetchone()[0]
    )


    if (
        choice_count
        != EXPECTED_CHOICES
    ):

        raise ValueError(
            "Trong transaction "
            "HSK4 sai so LuaChon: "
            f"{choice_count}"
        )


    # ========================================================
    # 4. MOI BAI DUNG 20 CAU
    # ========================================================

    cursor.execute(
        """
        SELECT
            bh.SoThuTuBai,
            bt.MaBaiTap,
            COUNT(
                ch.MaCauHoi
            ) AS SoCauHoi

        FROM dbo.BaiHoc AS bh

        INNER JOIN dbo.BaiTap AS bt
            ON bt.MaBaiHoc
            = bh.MaBaiHoc

        LEFT JOIN dbo.CauHoi AS ch
            ON ch.MaBaiTap
            = bt.MaBaiTap

        WHERE
            bh.MaKhoaHoc = ?
            AND bh.SoThuTuBai
                BETWEEN ? AND ?

        GROUP BY
            bh.SoThuTuBai,
            bt.MaBaiTap

        ORDER BY
            bh.SoThuTuBai
        """,
        COURSE_ID,
        FIRST_LESSON,
        LAST_LESSON,
    )


    per_lesson = (
        cursor.fetchall()
    )


    if len(
        per_lesson
    ) != EXPECTED_EXERCISES:

        raise ValueError(
            "Khong dem du "
            "20 BaiTap HSK4"
        )


    for row in per_lesson:

        lesson_number = int(
            row[0]
        )

        count = int(
            row[2]
        )


        if count != 20:

            raise ValueError(
                f"Bai {lesson_number}: "
                f"SQL dang co "
                f"{count} cau"
            )


    # ========================================================
    # 5. PHAN BO 7 DANG
    # ========================================================

    cursor.execute(
        """
        SELECT
            ch.LoaiCauHoi,
            COUNT(*)

        FROM dbo.CauHoi AS ch

        INNER JOIN dbo.BaiTap AS bt
            ON bt.MaBaiTap
            = ch.MaBaiTap

        INNER JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc
            = bt.MaBaiHoc

        WHERE
            bh.MaKhoaHoc = ?
            AND bh.SoThuTuBai
                BETWEEN ? AND ?

        GROUP BY
            ch.LoaiCauHoi
        """,
        COURSE_ID,
        FIRST_LESSON,
        LAST_LESSON,
    )


    sql_types = {
        txt(
            row[0]
        ):
        int(
            row[1]
        )
        for row
        in cursor.fetchall()
    }


    if (
        sql_types
        != EXPECTED_TOTAL_TYPES
    ):

        raise ValueError(
            "Phan bo 7 dang "
            "trong SQL transaction sai: "
            f"{sql_types}"
        )


    # ========================================================
    # 6. KY NANG
    #
    # 18 cau doc / bai * 20 = 360
    # 2 cau viet / bai * 20 = 40
    # ========================================================

    cursor.execute(
        """
        SELECT
            ch.KyNang,
            COUNT(*)

        FROM dbo.CauHoi AS ch

        INNER JOIN dbo.BaiTap AS bt
            ON bt.MaBaiTap
            = ch.MaBaiTap

        INNER JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc
            = bt.MaBaiHoc

        WHERE
            bh.MaKhoaHoc = ?
            AND bh.SoThuTuBai
                BETWEEN ? AND ?

        GROUP BY
            ch.KyNang
        """,
        COURSE_ID,
        FIRST_LESSON,
        LAST_LESSON,
    )


    skills = {
        txt(
            row[0]
        ):
        int(
            row[1]
        )
        for row
        in cursor.fetchall()
    }


    expected_skills = {
        "doc": 360,
        "viet": 40,
    }


    if (
        skills
        != expected_skills
    ):

        raise ValueError(
            "Phan bo KyNang sai: "
            f"{skills}"
        )


    # ========================================================
    # 7. DAP AN JSON
    #
    # 120 chon_mot
    # 40 chon_nhieu
    #
    # => 160 cau DapAnJson = NULL
    #
    # 240 cau con lai DapAnJson != NULL
    # ========================================================

    cursor.execute(
        """
        SELECT
            SUM(
                CASE
                    WHEN ch.DapAnJson
                        IS NULL
                    THEN 1
                    ELSE 0
                END
            ),

            SUM(
                CASE
                    WHEN ch.DapAnJson
                        IS NOT NULL
                    THEN 1
                    ELSE 0
                END
            )

        FROM dbo.CauHoi AS ch

        INNER JOIN dbo.BaiTap AS bt
            ON bt.MaBaiTap
            = ch.MaBaiTap

        INNER JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc
            = bt.MaBaiHoc

        WHERE
            bh.MaKhoaHoc = ?
            AND bh.SoThuTuBai
                BETWEEN ? AND ?
        """,
        COURSE_ID,
        FIRST_LESSON,
        LAST_LESSON,
    )


    (
        null_answer_count,
        json_answer_count
    ) = cursor.fetchone()


    null_answer_count = int(
        null_answer_count
        or 0
    )

    json_answer_count = int(
        json_answer_count
        or 0
    )


    if (
        null_answer_count
        != 160
    ):

        raise ValueError(
            "Sai so cau "
            "DapAnJson=NULL: "
            f"{null_answer_count}"
        )


    if (
        json_answer_count
        != 240
    ):

        raise ValueError(
            "Sai so cau "
            "co DapAnJson: "
            f"{json_answer_count}"
        )


    # ========================================================
    # 8. DEM DAP AN DUNG
    #
    # chon_mot:
    # 120 * 1 = 120
    #
    # chon_nhieu:
    # 40 * 2 = 80
    #
    # Tong = 200
    # ========================================================

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM dbo.LuaChonCauHoi AS lc

        INNER JOIN dbo.CauHoi AS ch
            ON ch.MaCauHoi
            = lc.MaCauHoi

        INNER JOIN dbo.BaiTap AS bt
            ON bt.MaBaiTap
            = ch.MaBaiTap

        INNER JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc
            = bt.MaBaiHoc

        WHERE
            bh.MaKhoaHoc = ?
            AND bh.SoThuTuBai
                BETWEEN ? AND ?
            AND lc.LaDapAnDung = 1
        """,
        COURSE_ID,
        FIRST_LESSON,
        LAST_LESSON,
    )


    correct_choice_count = int(
        cursor.fetchone()[0]
    )


    if (
        correct_choice_count
        != 200
    ):

        raise ValueError(
            "Sai tong LuaChon "
            "LaDapAnDung=1: "
            f"{correct_choice_count}"
        )


    # ========================================================
    # 9. TAT CA BAI TAP = BAN NHAP
    # ========================================================

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM dbo.BaiTap AS bt

        INNER JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc
            = bt.MaBaiHoc

        WHERE
            bh.MaKhoaHoc = ?
            AND bh.SoThuTuBai
                BETWEEN ? AND ?
            AND bt.TrangThai
                = 'ban_nhap'
        """,
        COURSE_ID,
        FIRST_LESSON,
        LAST_LESSON,
    )


    draft_count = int(
        cursor.fetchone()[0]
    )


    if (
        draft_count
        != EXPECTED_EXERCISES
    ):

        raise ValueError(
            "Khong phai tat ca "
            "BaiTap HSK4 deu ban_nhap"
        )


    # ========================================================
    # KET QUA
    # ========================================================

    print()

    print(
        "KIEM TRA TRONG TRANSACTION: OK"
    )

    print(
        "   BaiTap:",
        exercise_count
    )

    print(
        "   CauHoi:",
        question_count
    )

    print(
        "   LuaChonCauHoi:",
        choice_count
    )

    print(
        "   LuaChon dung:",
        correct_choice_count
    )

    print(
        "   DapAnJson NULL:",
        null_answer_count
    )

    print(
        "   DapAnJson co gia tri:",
        json_answer_count
    )

    print(
        "   KyNang:",
        skills
    )

    print(
        "   7 dang:",
        sql_types
    )


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Import 20 BaiTap "
            "HSK4 vao SQL Server"
        )
    )


    parser.add_argument(
        "--commit",
        action="store_true",
        help=(
            "Ghi that du lieu vao SQL. "
            "Khong truyen thi se "
            "DRY RUN + ROLLBACK."
        ),
    )


    parser.add_argument(
        "--admin-id",
        type=int,
        default=None,
        help=(
            "MaQuanTriVien dung cho import."
        ),
    )


    args = parser.parse_args()


    # ========================================================
    # DOC + VALIDATE PREVIEW
    # ========================================================

    exercises = load_preview()

    validate_preview(
        exercises
    )


    # ========================================================
    # HEADER
    # ========================================================

    print(
        "=" * 78
    )

    print(
        "BUOC 30 - "
        "IMPORT BAI TAP HSK4"
    )

    print(
        "=" * 78
    )

    print(
        "CHE DO:",
        (
            "COMMIT"
            if args.commit
            else
            "DRY RUN + ROLLBACK"
        )
    )

    print(
        "Preview:",
        PREVIEW_FILE
    )

    print(
        "BaiTap:",
        len(
            exercises
        )
    )

    print(
        "CauHoi:",
        sum(
            len(
                item[
                    "CauHoi"
                ]
            )
            for item
            in exercises
        )
    )

    print(
        "LuaChon du kien:",
        sum(
            len(
                question.get(
                    "LuaChon"
                )
                or []
            )
            for exercise
            in exercises
            for question
            in exercise[
                "CauHoi"
            ]
        )
    )

    print(
        "=" * 78
    )


    # ========================================================
    # TRANSACTION
    # ========================================================

    with closing(
        get_connection()
    ) as conn:

        # Bat buoc tat autocommit

        conn.autocommit = False


        try:

            with closing(
                conn.cursor()
            ) as cursor:


                # =============================================
                # DATABASE
                # =============================================

                validate_database(
                    cursor
                )


                # =============================================
                # ADMIN
                # =============================================

                (
                    admin_id,
                    admin_username
                ) = choose_admin(
                    cursor,
                    args.admin_id
                )


                print(
                    "Admin:",
                    f"ID={admin_id}",
                    f"| {admin_username}"
                )


                # =============================================
                # 20 BAI HOC HSK4
                # =============================================

                validate_lessons(
                    cursor,
                    exercises
                )


                print(
                    "20 bai hoc HSK4: OK"
                )


                # =============================================
                # LOCK + KIEM TRA TRUNG
                # =============================================

                verify_no_existing(
                    cursor,
                    exercises
                )


                print(
                    "Chua co BaiTap HSK4: OK"
                )


                # =============================================
                # INSERT THU
                # =============================================

                (
                    inserted_exercises,
                    inserted_questions,
                    inserted_choices,
                ) = import_exercises(
                    cursor,
                    exercises,
                    admin_id
                )


                # =============================================
                # VERIFY TRONG TRANSACTION
                # =============================================

                verify_transaction(
                    cursor,
                    inserted_exercises,
                    inserted_questions,
                    inserted_choices,
                )


                # =============================================
                # COMMIT HOAC ROLLBACK
                # =============================================

                if args.commit:

                    conn.commit()

                    print()

                    print(
                        "=" * 78
                    )

                    print(
                        "COMMIT THANH CONG"
                    )

                    print(
                        "DA LUU DU LIEU HSK4 "
                        "VAO SQL"
                    )

                    print(
                        "BaiTap:",
                        inserted_exercises
                    )

                    print(
                        "CauHoi:",
                        inserted_questions
                    )

                    print(
                        "LuaChonCauHoi:",
                        inserted_choices
                    )

                    print(
                        "=" * 78
                    )


                else:

                    conn.rollback()

                    print()

                    print(
                        "=" * 78
                    )

                    print(
                        "DRY RUN THANH CONG"
                    )

                    print(
                        "ROLLBACK THANH CONG"
                    )

                    print(
                        "SQL KHONG BI THAY DOI"
                    )

                    print(
                        "=" * 78
                    )


        except Exception:

            conn.rollback()

            print()

            print(
                "DA ROLLBACK TOAN BO "
                "TRANSACTION"
            )

            raise


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

        print(
            "KHONG COMMIT DU LIEU."
        )

        raise SystemExit(
            1
        )