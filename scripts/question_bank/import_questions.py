# =========================================================
# MỘC HÁN
# IMPORT BÀI TẬP + CÂU HỎI TỪ FILE PREVIEW V2 VÀO SQL
#
# File:
# scripts/question_bank/import_questions.py
#
# Có:
# - Backup trước khi import
# - Kiểm tra dữ liệu CSV
# - Tạo BaiTap cho Bài 1
# - Tạo CauHoi
# - Tạo LuaChonCauHoi
# - Transaction + rollback nếu lỗi
# - Chống import trùng
# =========================================================

from __future__ import annotations

import csv
import json
import sys

from contextlib import closing
from datetime import datetime
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

EXERCISE_TITLE = (
    "Bài luyện tập Bài 1 - 你好！"
)

EXERCISE_INSTRUCTION = (
    "Hoàn thành các câu hỏi về từ vựng, "
    "ngữ pháp và chữ Hán của Bài 1."
)

TIME_LIMIT_SECONDS = 15 * 60

PASS_PERCENT = 70

EXERCISE_STATUS = "ban_nhap"


# =========================================================
# FILE
# =========================================================

CSV_PATH = (
    CURRENT_FILE.parent
    / "preview"
    / "hsk1_bai1_questions_v2.csv"
)

BACKUP_DIR = (
    CURRENT_FILE.parent
    / "backups"
)

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# HELPER
# =========================================================

def clean_text(value):

    if value is None:
        return ""

    return str(value).strip()


# =========================================================
# ĐỌC CSV
# =========================================================

def load_questions():

    if not CSV_PATH.exists():

        raise FileNotFoundError(
            (
                "Không tìm thấy file preview:\n"
                f"{CSV_PATH}"
            )
        )


    questions = []


    with CSV_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )


        for row_number, row in enumerate(
            reader,
            start=2,
        ):

            question_type = clean_text(
                row.get(
                    "question_type"
                )
            )


            if question_type not in (
                "chon_mot",
                "chon_nhieu",
                "dung_sai",
                "dien_tu",
                "ghep_cap",
                "sap_xep",
                "viet_ngan",
            ):

                raise ValueError(
                    (
                        f"Dòng {row_number}: "
                        f"question_type không hợp lệ: "
                        f"{question_type}"
                    )
                )


            skill = clean_text(
                row.get(
                    "skill"
                )
            )


            if skill not in (
                "doc",
                "nghe",
                "viet",
                "tong_hop",
            ):

                raise ValueError(
                    (
                        f"Dòng {row_number}: "
                        f"skill không hợp lệ: "
                        f"{skill}"
                    )
                )


            content = clean_text(
                row.get(
                    "content"
                )
            )


            if not content:

                raise ValueError(
                    (
                        f"Dòng {row_number}: "
                        "nội dung câu hỏi đang trống."
                    )
                )


            try:

                order = int(
                    clean_text(
                        row.get(
                            "order"
                        )
                    )
                )

            except ValueError:

                raise ValueError(
                    (
                        f"Dòng {row_number}: "
                        "order không hợp lệ."
                    )
                )


            try:

                score = float(
                    clean_text(
                        row.get(
                            "score"
                        )
                    )
                )

            except ValueError:

                raise ValueError(
                    (
                        f"Dòng {row_number}: "
                        "score không hợp lệ."
                    )
                )


            if score <= 0:

                raise ValueError(
                    (
                        f"Dòng {row_number}: "
                        "score phải lớn hơn 0."
                    )
                )


            answer_json = clean_text(
                row.get(
                    "answer_json"
                )
            )


            if answer_json:

                try:

                    json.loads(
                        answer_json
                    )

                except json.JSONDecodeError as error:

                    raise ValueError(
                        (
                            f"Dòng {row_number}: "
                            "answer_json không hợp lệ."
                        )
                    ) from error


            choices = []


            for index in range(
                1,
                7,
            ):

                choice_text = clean_text(
                    row.get(
                        f"choice_{index}"
                    )
                )


                if choice_text:

                    choices.append(
                        {
                            "order":
                                index,

                            "text":
                                choice_text,

                            "correct":
                                False,
                        }
                    )


            correct_choices_raw = (
                clean_text(
                    row.get(
                        "correct_choices"
                    )
                )
            )


            correct_orders = set()


            if correct_choices_raw:

                for value in (
                    correct_choices_raw
                    .replace(
                        ";",
                        ",",
                    )
                    .split(",")
                ):

                    value = value.strip()

                    if not value:
                        continue

                    try:

                        correct_orders.add(
                            int(
                                value
                            )
                        )

                    except ValueError:

                        raise ValueError(
                            (
                                f"Dòng {row_number}: "
                                "correct_choices "
                                "không hợp lệ."
                            )
                        )


            for choice in choices:

                choice["correct"] = (
                    choice["order"]
                    in correct_orders
                )


            # =============================================
            # VALIDATE CHỌN MỘT
            # =============================================

            if question_type == "chon_mot":

                if len(choices) < 2:

                    raise ValueError(
                        (
                            f"Dòng {row_number}: "
                            "câu Chọn một cần "
                            "ít nhất 2 lựa chọn."
                        )
                    )


                correct_count = sum(
                    1
                    for choice in choices
                    if choice["correct"]
                )


                if correct_count != 1:

                    raise ValueError(
                        (
                            f"Dòng {row_number}: "
                            "câu Chọn một phải có "
                            "đúng 1 đáp án đúng."
                        )
                    )


            questions.append(
                {
                    "order":
                        order,

                    "question_type":
                        question_type,

                    "skill":
                        skill,

                    "content":
                        content,

                    "passage":
                        clean_text(
                            row.get(
                                "passage"
                            )
                        ),

                    "answer_json":
                        answer_json
                        or None,

                    "explanation":
                        clean_text(
                            row.get(
                                "explanation"
                            )
                        ),

                    "score":
                        score,

                    "choices":
                        choices,

                    "source_type":
                        clean_text(
                            row.get(
                                "source_type"
                            )
                        ),

                    "source_id":
                        clean_text(
                            row.get(
                                "source_id"
                            )
                        ),
                }
            )


    if not questions:

        raise RuntimeError(
            "File CSV không có câu hỏi."
        )


    orders = [
        item["order"]
        for item in questions
    ]


    if len(
        set(
            orders
        )
    ) != len(
        orders
    ):

        raise ValueError(
            "CSV đang có thứ tự câu hỏi bị trùng."
        )


    questions.sort(
        key=lambda item:
            item["order"]
    )


    return questions


# =========================================================
# BACKUP CÁC BẢNG LIÊN QUAN
# =========================================================

def backup_current_data(
    cursor,
):

    timestamp = (
        datetime.now()
        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )


    backup_file = (
        BACKUP_DIR
        / (
            "before_import_"
            f"hsk1_bai1_{timestamp}.json"
        )
    )


    data = {
        "BaiTap": [],
        "CauHoi": [],
        "LuaChonCauHoi": [],
    }


    # =====================================================
    # BaiTap
    # =====================================================

    cursor.execute(
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

        ORDER BY
            MaBaiTap;
        """
    )


    for row in cursor.fetchall():

        data["BaiTap"].append(
            [
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                float(row[5])
                if row[5] is not None
                else None,
                row[6],
            ]
        )


    # =====================================================
    # CauHoi
    # =====================================================

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
            DiemToiDa,
            ThuTu

        FROM dbo.CauHoi

        ORDER BY
            MaCauHoi;
        """
    )


    for row in cursor.fetchall():

        data["CauHoi"].append(
            [
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                float(row[9])
                if row[9] is not None
                else None,
                row[10],
            ]
        )


    # =====================================================
    # LuaChonCauHoi
    # =====================================================

    cursor.execute(
        """
        SELECT
            MaLuaChon,
            MaCauHoi,
            NoiDungLuaChon,
            LaDapAnDung,
            ThuTu

        FROM dbo.LuaChonCauHoi

        ORDER BY
            MaLuaChon;
        """
    )


    for row in cursor.fetchall():

        data[
            "LuaChonCauHoi"
        ].append(
            [
                row[0],
                row[1],
                row[2],
                bool(
                    row[3]
                ),
                row[4],
            ]
        )


    with backup_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


    return backup_file


# =========================================================
# KIỂM TRA BÀI HỌC
# =========================================================

def get_lesson(
    cursor,
):

    cursor.execute(
        """
        SELECT
            bh.MaBaiHoc,
            bh.SoThuTuBai,
            bh.TieuDe,
            kh.MaCapDo

        FROM dbo.BaiHoc AS bh

        INNER JOIN dbo.KhoaHoc AS kh
            ON kh.MaKhoaHoc
            = bh.MaKhoaHoc

        WHERE
            bh.MaBaiHoc = ?;
        """,
        LESSON_ID,
    )


    row = cursor.fetchone()


    if row is None:

        raise RuntimeError(
            (
                f"Không tìm thấy "
                f"MaBaiHoc = {LESSON_ID}."
            )
        )


    return {
        "id":
            row[0],

        "order":
            row[1],

        "title":
            row[2],

        "level":
            row[3],
    }


# =========================================================
# KIỂM TRA ĐÃ IMPORT CHƯA
# =========================================================

def check_existing_exercise(
    cursor,
):

    cursor.execute(
        """
        SELECT
            MaBaiTap

        FROM dbo.BaiTap

        WHERE
            MaBaiHoc = ?
            AND TieuDe = ?;
        """,
        LESSON_ID,
        EXERCISE_TITLE,
    )


    row = cursor.fetchone()


    if row is None:
        return None


    return int(
        row[0]
    )


# =========================================================
# TẠO BÀI TẬP
# =========================================================

def create_exercise(
    cursor,
):

    cursor.execute(
        """
        INSERT INTO dbo.BaiTap
        (
            MaBaiHoc,
            TieuDe,
            HuongDan,
            ThoiGianGioiHanGiay,
            PhanTramDat,
            TrangThai
        )

        OUTPUT
            INSERTED.MaBaiTap

        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        );
        """,

        LESSON_ID,

        EXERCISE_TITLE,

        EXERCISE_INSTRUCTION,

        TIME_LIMIT_SECONDS,

        PASS_PERCENT,

        EXERCISE_STATUS,
    )


    return int(
        cursor.fetchone()[0]
    )


# =========================================================
# IMPORT QUESTIONS
# =========================================================

def import_questions(
    cursor,
    exercise_id,
    questions,
):

    inserted_questions = 0

    inserted_choices = 0


    for question in questions:

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
                ThuTu
            )

            OUTPUT
                INSERTED.MaCauHoi

            VALUES
            (
                ?,
                ?,
                ?,
                ?,
                ?,
                NULL,
                ?,
                ?,
                ?,
                ?
            );
            """,

            exercise_id,

            question[
                "question_type"
            ],

            question[
                "skill"
            ],

            question[
                "content"
            ],

            question[
                "passage"
            ]
            or None,

            question[
                "answer_json"
            ],

            question[
                "explanation"
            ]
            or None,

            question[
                "score"
            ],

            question[
                "order"
            ],
        )


        question_id = int(
            cursor.fetchone()[0]
        )


        inserted_questions += 1


        for choice in question[
            "choices"
        ]:

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
                    ?,
                    ?,
                    ?,
                    ?
                );
                """,

                question_id,

                choice[
                    "text"
                ],

                1
                if choice[
                    "correct"
                ]
                else 0,

                choice[
                    "order"
                ],
            )


            inserted_choices += 1


    return (
        inserted_questions,
        inserted_choices,
    )


# =========================================================
# VERIFY
# =========================================================

def verify_import(
    cursor,
    exercise_id,
):

    cursor.execute(
        """
        SELECT
            COUNT(*)

        FROM dbo.CauHoi

        WHERE
            MaBaiTap = ?;
        """,
        exercise_id,
    )


    question_count = int(
        cursor.fetchone()[0]
        or 0
    )


    cursor.execute(
        """
        SELECT
            COUNT(*)

        FROM dbo.LuaChonCauHoi AS lc

        INNER JOIN dbo.CauHoi AS ch
            ON ch.MaCauHoi
            = lc.MaCauHoi

        WHERE
            ch.MaBaiTap = ?;
        """,
        exercise_id,
    )


    choice_count = int(
        cursor.fetchone()[0]
        or 0
    )


    return (
        question_count,
        choice_count,
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print(
        "=" * 70
    )

    print(
        "MOC HAN - IMPORT QUESTION BANK"
    )

    print(
        "=" * 70
    )


    questions = (
        load_questions()
    )


    print()
    print(
        f"CSV: {CSV_PATH}"
    )

    print(
        (
            f"So cau hoi doc duoc: "
            f"{len(questions)}"
        )
    )


    if len(questions) != 20:

        raise RuntimeError(
            (
                "File V2 hiện không có "
                "đúng 20 câu. "
                "Dừng import để kiểm tra."
            )
        )


    # =====================================================
    # DB
    # =====================================================

    with closing(
        get_connection()
    ) as connection:

        try:

            with closing(
                connection.cursor()
            ) as cursor:


                lesson = get_lesson(
                    cursor
                )


                print()
                print(
                    (
                        f"HSK {lesson['level']} "
                        f"- Bai {lesson['order']} "
                        f"- {lesson['title']}"
                    )
                )


                existing_id = (
                    check_existing_exercise(
                        cursor
                    )
                )


                if existing_id:

                    print()
                    print(
                        "DUNG IMPORT."
                    )

                    print(
                        (
                            "Da ton tai bai tap:"
                            f" MaBaiTap = "
                            f"{existing_id}"
                        )
                    )

                    print(
                        EXERCISE_TITLE
                    )

                    print()
                    print(
                        (
                            "Script khong import "
                            "lan 2 de tranh trung du lieu."
                        )
                    )

                    return


                # =========================================
                # BACKUP
                # =========================================

                backup_file = (
                    backup_current_data(
                        cursor
                    )
                )


                print()
                print(
                    (
                        "Da tao backup:"
                        f"\n{backup_file}"
                    )
                )


                # =========================================
                # PREVIEW
                # =========================================

                print()
                print(
                    "Se tao:"
                )

                print(
                    (
                        f"  Bai tap: "
                        f"{EXERCISE_TITLE}"
                    )
                )

                print(
                    (
                        f"  Bai hoc: "
                        f"MaBaiHoc = "
                        f"{LESSON_ID}"
                    )
                )

                print(
                    (
                        f"  Cau hoi: "
                        f"{len(questions)}"
                    )
                )

                print(
                    (
                        f"  Thoi gian: "
                        f"{TIME_LIMIT_SECONDS} giay"
                    )
                )

                print(
                    (
                        f"  Phan tram dat: "
                        f"{PASS_PERCENT}%"
                    )
                )

                print(
                    (
                        f"  Trang thai: "
                        f"{EXERCISE_STATUS}"
                    )
                )


                # =========================================
                # CONFIRM
                # =========================================

                print()
                print(
                    "Nhap:"
                )

                print(
                    "IMPORT"
                )

                print(
                    "de xac nhan ghi vao SQL."
                )


                confirmation = input(
                    "\nXac nhan: "
                ).strip()


                if confirmation != "IMPORT":

                    print()
                    print(
                        (
                            "Da huy. "
                            "SQL khong thay doi."
                        )
                    )

                    connection.rollback()

                    return


                # =========================================
                # CREATE EXERCISE
                # =========================================

                exercise_id = (
                    create_exercise(
                        cursor
                    )
                )


                # =========================================
                # IMPORT
                # =========================================

                (
                    inserted_questions,
                    inserted_choices,
                ) = import_questions(
                    cursor,
                    exercise_id,
                    questions,
                )


                # =========================================
                # VERIFY BEFORE COMMIT
                # =========================================

                (
                    question_count,
                    choice_count,
                ) = verify_import(
                    cursor,
                    exercise_id,
                )


                if (
                    question_count
                    != len(
                        questions
                    )
                ):

                    raise RuntimeError(
                        (
                            "So cau hoi sau import "
                            "khong khop file CSV."
                        )
                    )


                # =========================================
                # COMMIT
                # =========================================

                connection.commit()


                print()
                print(
                    "=" * 70
                )

                print(
                    "IMPORT THANH CONG"
                )

                print(
                    "=" * 70
                )

                print(
                    (
                        f"MaBaiTap: "
                        f"{exercise_id}"
                    )
                )

                print(
                    (
                        f"Cau hoi: "
                        f"{inserted_questions}"
                    )
                )

                print(
                    (
                        f"Lua chon: "
                        f"{inserted_choices}"
                    )
                )

                print(
                    (
                        f"Kiem tra CauHoi: "
                        f"{question_count}"
                    )
                )

                print(
                    (
                        f"Kiem tra LuaChon: "
                        f"{choice_count}"
                    )
                )

                print(
                    (
                        f"Trang thai: "
                        f"{EXERCISE_STATUS}"
                    )
                )


        except Exception:

            connection.rollback()

            print()
            print(
                (
                    "CO LOI - DA ROLLBACK."
                )
            )

            print(
                (
                    "Khong co du lieu "
                    "import do dang nao "
                    "duoc giu lai."
                )
            )

            raise


if __name__ == "__main__":

    main()