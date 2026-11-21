# =========================================================
# MỘC HÁN
# IMPORT HSK1 - BÀI 2 -> BÀI 23
#
# ĐỌC 1 FILE DUY NHẤT:
# preview/hsk1_bai2_23_questions.csv
#
# TỰ ĐỘNG:
# - Backup dữ liệu trước khi import
# - Tạo 22 BaiTap
# - Tạo 440 CauHoi
# - Tạo LuaChonCauHoi
# - Kiểm tra số lượng
# - Transaction + rollback nếu lỗi
#
# KHÔNG ĐỤNG TỚI BÀI 1
# =========================================================

from __future__ import annotations

import csv
import json
import sys

from collections import defaultdict
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

HSK_LEVEL = 1

START_LESSON_ORDER = 2

END_LESSON_ORDER = 23

EXPECTED_LESSON_COUNT = 22

EXPECTED_QUESTION_PER_LESSON = 20

EXPECTED_TOTAL_QUESTIONS = (
    EXPECTED_LESSON_COUNT
    * EXPECTED_QUESTION_PER_LESSON
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
    / "hsk1_bai2_23_questions.csv"
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

def load_csv():

    if not CSV_PATH.exists():

        raise FileNotFoundError(
            (
                "Không tìm thấy file:\n"
                f"{CSV_PATH}"
            )
        )


    rows = []


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

            try:

                lesson_id = int(
                    clean_text(
                        row.get(
                            "lesson_id"
                        )
                    )
                )

                lesson_order = int(
                    clean_text(
                        row.get(
                            "lesson_order"
                        )
                    )
                )

                question_order = int(
                    clean_text(
                        row.get(
                            "order"
                        )
                    )
                )

                score = float(
                    clean_text(
                        row.get(
                            "score"
                        )
                    )
                )

            except ValueError as error:

                raise ValueError(
                    (
                        f"Dòng {row_number}: "
                        "lesson_id / lesson_order / "
                        "order / score không hợp lệ."
                    )
                ) from error


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
                        "nội dung câu hỏi trống."
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


            # =================================================
            # CHOICES
            # =================================================

            choices = []


            for index in range(
                1,
                7,
            ):

                text = clean_text(
                    row.get(
                        f"choice_{index}"
                    )
                )


                if text:

                    choices.append(
                        {
                            "order":
                                index,

                            "text":
                                text,

                            "correct":
                                False,
                        }
                    )


            correct_raw = clean_text(
                row.get(
                    "correct_choices"
                )
            )


            correct_orders = set()


            if correct_raw:

                normalized = (
                    correct_raw
                    .replace(
                        ";",
                        ",",
                    )
                )


                for part in normalized.split(
                    ","
                ):

                    part = part.strip()

                    if not part:
                        continue


                    try:

                        correct_orders.add(
                            int(
                                part
                            )
                        )

                    except ValueError as error:

                        raise ValueError(
                            (
                                f"Dòng {row_number}: "
                                "correct_choices không hợp lệ."
                            )
                        ) from error


            for choice in choices:

                choice["correct"] = (
                    choice["order"]
                    in correct_orders
                )


            # =================================================
            # VALIDATE CHỌN MỘT
            # =================================================

            if question_type == "chon_mot":

                if len(choices) < 2:

                    raise ValueError(
                        (
                            f"Dòng {row_number}: "
                            "câu chọn một cần "
                            "ít nhất 2 lựa chọn."
                        )
                    )


                correct_count = sum(
                    1
                    for item in choices
                    if item["correct"]
                )


                if correct_count != 1:

                    raise ValueError(
                        (
                            f"Dòng {row_number}: "
                            "câu chọn một phải có "
                            "đúng 1 đáp án đúng."
                        )
                    )


            rows.append(
                {
                    "hsk_level":
                        int(
                            clean_text(
                                row.get(
                                    "hsk_level"
                                )
                            )
                        ),

                    "lesson_id":
                        lesson_id,

                    "lesson_order":
                        lesson_order,

                    "lesson_title":
                        clean_text(
                            row.get(
                                "lesson_title"
                            )
                        ),

                    "question_order":
                        question_order,

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


    return rows


# =========================================================
# GROUP THEO BÀI
# =========================================================

def group_by_lesson(
    rows,
):

    grouped = defaultdict(
        list
    )


    for row in rows:

        grouped[
            row["lesson_id"]
        ].append(
            row
        )


    for lesson_id in grouped:

        grouped[
            lesson_id
        ].sort(
            key=lambda item:
                item[
                    "question_order"
                ]
        )


    return grouped


# =========================================================
# VALIDATE TOÀN FILE
# =========================================================

def validate_all(
    rows,
    grouped,
):

    if len(rows) != EXPECTED_TOTAL_QUESTIONS:

        raise RuntimeError(
            (
                f"File phải có "
                f"{EXPECTED_TOTAL_QUESTIONS} câu, "
                f"nhưng hiện có "
                f"{len(rows)} câu."
            )
        )


    if len(grouped) != EXPECTED_LESSON_COUNT:

        raise RuntimeError(
            (
                f"File phải có "
                f"{EXPECTED_LESSON_COUNT} bài, "
                f"nhưng hiện có "
                f"{len(grouped)} bài."
            )
        )


    lesson_orders = set()


    for lesson_id, questions in grouped.items():

        lesson_order = (
            questions[0][
                "lesson_order"
            ]
        )


        lesson_orders.add(
            lesson_order
        )


        if (
            len(questions)
            != EXPECTED_QUESTION_PER_LESSON
        ):

            raise RuntimeError(
                (
                    f"Bài {lesson_order} "
                    f"(MaBaiHoc={lesson_id}) "
                    f"có {len(questions)} câu, "
                    f"không phải "
                    f"{EXPECTED_QUESTION_PER_LESSON}."
                )
            )


        orders = [
            item[
                "question_order"
            ]
            for item in questions
        ]


        if set(
            orders
        ) != set(
            range(
                1,
                EXPECTED_QUESTION_PER_LESSON
                + 1,
            )
        ):

            raise RuntimeError(
                (
                    f"Bài {lesson_order} "
                    "có thứ tự câu hỏi "
                    "không liên tục từ 1 đến 20."
                )
            )


    expected_orders = set(
        range(
            START_LESSON_ORDER,
            END_LESSON_ORDER + 1,
        )
    )


    if lesson_orders != expected_orders:

        raise RuntimeError(
            (
                "Danh sách bài trong CSV "
                "không đúng từ Bài 2 đến Bài 23."
            )
        )


# =========================================================
# BACKUP
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


    backup_path = (
        BACKUP_DIR
        / (
            "before_import_"
            f"hsk1_bai2_23_"
            f"{timestamp}.json"
        )
    )


    data = {
        "BaiTap": [],
        "CauHoi": [],
        "LuaChonCauHoi": [],
    }


    # =====================================================
    # BÀI TẬP HSK1 BÀI 2 -> 23
    # =====================================================

    cursor.execute(
        """
        SELECT
            bt.MaBaiTap,
            bt.MaBaiHoc,
            bt.TieuDe,
            bt.HuongDan,
            bt.ThoiGianGioiHanGiay,
            bt.PhanTramDat,
            bt.TrangThai

        FROM dbo.BaiTap AS bt

        INNER JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc
            = bt.MaBaiHoc

        INNER JOIN dbo.KhoaHoc AS kh
            ON kh.MaKhoaHoc
            = bh.MaKhoaHoc

        WHERE
            kh.MaCapDo = ?
            AND bh.SoThuTuBai
                BETWEEN ? AND ?

        ORDER BY
            bt.MaBaiTap;
        """,

        HSK_LEVEL,
        START_LESSON_ORDER,
        END_LESSON_ORDER,
    )


    for row in cursor.fetchall():

        data[
            "BaiTap"
        ].append(
            [
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                float(
                    row[5]
                )
                if row[5] is not None
                else None,
                row[6],
            ]
        )


    # =====================================================
    # CÂU HỎI LIÊN QUAN
    # =====================================================

    cursor.execute(
        """
        SELECT
            ch.MaCauHoi,
            ch.MaBaiTap,
            ch.LoaiCauHoi,
            ch.KyNang,
            ch.NoiDungCauHoi,
            ch.DoanVan,
            ch.MaTep,
            ch.DapAnJson,
            ch.GiaiThich,
            ch.DiemToiDa,
            ch.ThuTu

        FROM dbo.CauHoi AS ch

        INNER JOIN dbo.BaiTap AS bt
            ON bt.MaBaiTap
            = ch.MaBaiTap

        INNER JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc
            = bt.MaBaiHoc

        INNER JOIN dbo.KhoaHoc AS kh
            ON kh.MaKhoaHoc
            = bh.MaKhoaHoc

        WHERE
            kh.MaCapDo = ?
            AND bh.SoThuTuBai
                BETWEEN ? AND ?

        ORDER BY
            ch.MaCauHoi;
        """,

        HSK_LEVEL,
        START_LESSON_ORDER,
        END_LESSON_ORDER,
    )


    question_ids = []


    for row in cursor.fetchall():

        question_ids.append(
            row[0]
        )


        data[
            "CauHoi"
        ].append(
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
                float(
                    row[9]
                )
                if row[9] is not None
                else None,
                row[10],
            ]
        )


    # =====================================================
    # LỰA CHỌN
    # =====================================================

    if question_ids:

        placeholders = ",".join(
            "?"
            for _ in question_ids
        )


        cursor.execute(
            f"""
            SELECT
                MaLuaChon,
                MaCauHoi,
                NoiDungLuaChon,
                LaDapAnDung,
                ThuTu

            FROM dbo.LuaChonCauHoi

            WHERE
                MaCauHoi IN (
                    {placeholders}
                )

            ORDER BY
                MaLuaChon;
            """,

            *question_ids,
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


    with backup_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


    return backup_path


# =========================================================
# KIỂM TRA BÀI HỌC TRONG SQL
# =========================================================

def validate_lessons_in_database(
    cursor,
    grouped,
):

    for lesson_id, questions in grouped.items():

        lesson_order = (
            questions[0][
                "lesson_order"
            ]
        )


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
            lesson_id,
        )


        row = cursor.fetchone()


        if row is None:

            raise RuntimeError(
                (
                    f"Không tìm thấy "
                    f"MaBaiHoc={lesson_id}."
                )
            )


        if int(
            row[1]
        ) != lesson_order:

            raise RuntimeError(
                (
                    f"MaBaiHoc={lesson_id}: "
                    "SoThuTuBai trong SQL "
                    "không khớp CSV."
                )
            )


        if int(
            row[3]
        ) != HSK_LEVEL:

            raise RuntimeError(
                (
                    f"MaBaiHoc={lesson_id} "
                    "không thuộc HSK1."
                )
            )


# =========================================================
# KIỂM TRA BÀI TẬP ĐÃ TỒN TẠI CHƯA
# =========================================================

def find_existing_exercises(
    cursor,
    grouped,
):

    existing = []


    for lesson_id, questions in grouped.items():

        lesson_order = (
            questions[0][
                "lesson_order"
            ]
        )


        title = (
            f"Bài luyện tập Bài "
            f"{lesson_order}"
        )


        cursor.execute(
            """
            SELECT
                MaBaiTap,
                TieuDe

            FROM dbo.BaiTap

            WHERE
                MaBaiHoc = ?
                AND TieuDe LIKE ?;
            """,

            lesson_id,
            (
                f"Bài luyện tập Bài "
                f"{lesson_order}%"
            ),
        )


        rows = cursor.fetchall()


        for row in rows:

            existing.append(
                {
                    "lesson_order":
                        lesson_order,

                    "exercise_id":
                        row[0],

                    "title":
                        row[1],
                }
            )


    return existing


# =========================================================
# TẠO BÀI TẬP
# =========================================================

def create_exercise(
    cursor,
    lesson_order,
    lesson_title,
    lesson_id,
):

    chinese_title = (
        lesson_title.split(
            " - ",
            1,
        )[0].strip()
    )


    title = (
        f"Bài luyện tập Bài "
        f"{lesson_order}"
    )


    if chinese_title:

        title += (
            f" - {chinese_title}"
        )


    instruction = (
        f"Hoàn thành các câu hỏi về "
        f"từ vựng, ngữ pháp và chữ Hán "
        f"của Bài {lesson_order}."
    )


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

        lesson_id,

        title,

        instruction,

        TIME_LIMIT_SECONDS,

        PASS_PERCENT,

        EXERCISE_STATUS,
    )


    return int(
        cursor.fetchone()[0]
    )


# =========================================================
# INSERT CÂU HỎI
# =========================================================

def insert_questions(
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
                "question_order"
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
# VERIFY TỪNG BÀI
# =========================================================

def verify_exercise(
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
        "=" * 74
    )

    print(
        "MOC HAN - IMPORT HSK1 BAI 2 -> 23"
    )

    print(
        "=" * 74
    )


    # =====================================================
    # CSV
    # =====================================================

    rows = load_csv()

    grouped = group_by_lesson(
        rows
    )

    validate_all(
        rows,
        grouped,
    )


    print()
    print(
        f"CSV: {CSV_PATH}"
    )

    print(
        (
            f"So bai: "
            f"{len(grouped)}"
        )
    )

    print(
        (
            f"Tong cau hoi: "
            f"{len(rows)}"
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


                # =========================================
                # KIỂM TRA LESSON
                # =========================================

                validate_lessons_in_database(
                    cursor,
                    grouped,
                )


                # =========================================
                # KHÔNG IMPORT TRÙNG
                # =========================================

                existing = (
                    find_existing_exercises(
                        cursor,
                        grouped,
                    )
                )


                if existing:

                    print()
                    print(
                        "DUNG IMPORT."
                    )

                    print(
                        (
                            "Phat hien bai tap "
                            "da ton tai:"
                        )
                    )


                    for item in existing:

                        print(
                            (
                                f"  Bai "
                                f"{item['lesson_order']}: "
                                f"MaBaiTap="
                                f"{item['exercise_id']} "
                                f"- "
                                f"{item['title']}"
                            )
                        )


                    print()
                    print(
                        (
                            "Hay kiem tra du lieu "
                            "truoc khi chay lai."
                        )
                    )

                    return


                # =========================================
                # BACKUP
                # =========================================

                backup_path = (
                    backup_current_data(
                        cursor
                    )
                )


                print()
                print(
                    "Da tao backup:"
                )

                print(
                    backup_path
                )


                # =========================================
                # PREVIEW
                # =========================================

                print()
                print(
                    "SE TAO:"
                )

                print(
                    (
                        f"  Bai tap       : "
                        f"{EXPECTED_LESSON_COUNT}"
                    )
                )

                print(
                    (
                        f"  Cau hoi       : "
                        f"{EXPECTED_TOTAL_QUESTIONS}"
                    )
                )

                print(
                    (
                        f"  Moi bai       : "
                        f"{EXPECTED_QUESTION_PER_LESSON} cau"
                    )
                )

                print(
                    (
                        f"  Thoi gian/bai : "
                        f"{TIME_LIMIT_SECONDS} giay"
                    )
                )

                print(
                    (
                        f"  Dat           : "
                        f"{PASS_PERCENT}%"
                    )
                )

                print(
                    (
                        f"  Trang thai    : "
                        f"{EXERCISE_STATUS}"
                    )
                )


                print()
                print(
                    (
                        "Bai 2 -> Bai 23"
                    )
                )


                # =========================================
                # CONFIRM
                # =========================================

                print()
                print(
                    (
                        "Nhap IMPORT_HSK1 "
                        "de ghi du lieu vao SQL."
                    )
                )


                confirmation = input(
                    "\nXac nhan: "
                ).strip()


                if (
                    confirmation
                    != "IMPORT_HSK1"
                ):

                    connection.rollback()

                    print()
                    print(
                        (
                            "Da huy. "
                            "SQL khong thay doi."
                        )
                    )

                    return


                # =========================================
                # IMPORT
                # =========================================

                total_questions = 0

                total_choices = 0

                created_exercises = []


                lesson_groups = sorted(
                    grouped.items(),
                    key=lambda item:
                        item[1][0][
                            "lesson_order"
                        ],
                )


                for (
                    lesson_id,
                    questions,
                ) in lesson_groups:

                    first = (
                        questions[0]
                    )


                    lesson_order = (
                        first[
                            "lesson_order"
                        ]
                    )

                    lesson_title = (
                        first[
                            "lesson_title"
                        ]
                    )


                    exercise_id = (
                        create_exercise(
                            cursor,
                            lesson_order,
                            lesson_title,
                            lesson_id,
                        )
                    )


                    (
                        inserted_questions,
                        inserted_choices,
                    ) = insert_questions(
                        cursor,
                        exercise_id,
                        questions,
                    )


                    (
                        verified_questions,
                        verified_choices,
                    ) = verify_exercise(
                        cursor,
                        exercise_id,
                    )


                    if (
                        verified_questions
                        != EXPECTED_QUESTION_PER_LESSON
                    ):

                        raise RuntimeError(
                            (
                                f"Bài {lesson_order}: "
                                f"verify chỉ có "
                                f"{verified_questions} câu."
                            )
                        )


                    total_questions += (
                        inserted_questions
                    )

                    total_choices += (
                        inserted_choices
                    )


                    created_exercises.append(
                        {
                            "lesson_order":
                                lesson_order,

                            "exercise_id":
                                exercise_id,

                            "questions":
                                verified_questions,

                            "choices":
                                verified_choices,
                        }
                    )


                    print(
                        (
                            f"  Bai "
                            f"{lesson_order:>2}: "
                            f"MaBaiTap="
                            f"{exercise_id} "
                            f"| "
                            f"{verified_questions} cau "
                            f"| "
                            f"{verified_choices} lua chon"
                        )
                    )


                # =========================================
                # FINAL VERIFY
                # =========================================

                if (
                    total_questions
                    != EXPECTED_TOTAL_QUESTIONS
                ):

                    raise RuntimeError(
                        (
                            "Tong so cau hoi "
                            "sau import khong dung."
                        )
                    )


                if (
                    len(
                        created_exercises
                    )
                    != EXPECTED_LESSON_COUNT
                ):

                    raise RuntimeError(
                        (
                            "Tong so bai tap "
                            "sau import khong dung."
                        )
                    )


                # =========================================
                # COMMIT
                # =========================================

                connection.commit()


                print()
                print(
                    "=" * 74
                )

                print(
                    "IMPORT HSK1 BAI 2 -> 23 THANH CONG"
                )

                print(
                    "=" * 74
                )

                print(
                    (
                        f"Bai tap da tao : "
                        f"{len(created_exercises)}"
                    )
                )

                print(
                    (
                        f"Cau hoi        : "
                        f"{total_questions}"
                    )
                )

                print(
                    (
                        f"Lua chon       : "
                        f"{total_choices}"
                    )
                )

                print(
                    (
                        f"Trang thai     : "
                        f"{EXERCISE_STATUS}"
                    )
                )


        except Exception:

            connection.rollback()

            print()
            print(
                "=" * 74
            )

            print(
                "CO LOI - DA ROLLBACK TOAN BO"
            )

            print(
                "=" * 74
            )

            print(
                (
                    "Khong co BaiTap/CauHoi/"
                    "LuaChonCauHoi import do "
                    "dang nao duoc giu lai."
                )
            )

            raise


if __name__ == "__main__":

    main()