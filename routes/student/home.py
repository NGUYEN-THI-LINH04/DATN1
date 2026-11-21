from flask import Blueprint, render_template
from contextlib import closing

from database import get_connection


home_bp = Blueprint(
    "home",
    __name__
)


# =========================================================
# HELPER
# =========================================================
def row_to_dict(cursor, row):

    columns = [
        column[0]
        for column in cursor.description
    ]

    return dict(
        zip(
            columns,
            row
        )
    )


# =========================================================
# TRANG CHỦ
# URL: /
# =========================================================
@home_bp.get("/")
def index():

    courses = []


    with closing(
        get_connection()
    ) as conn:

        with closing(
            conn.cursor()
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    kh.MaKhoaHoc,
                    kh.MaCapDo,
                    kh.MaKyHieu,
                    kh.TieuDe,
                    kh.MoTa,
                    kh.PhienBanChuanHSK,
                    kh.TrangThai,

                    (
                        SELECT COUNT(*)

                        FROM dbo.BaiHoc AS bh

                        WHERE
                            bh.MaKhoaHoc = kh.MaKhoaHoc
                    ) AS SoBaiHoc,

                    (
                        SELECT COUNT(*)

                        FROM dbo.TuVungBaiHoc AS tvbh

                        INNER JOIN dbo.BaiHoc AS bh2
                            ON tvbh.MaBaiHoc = bh2.MaBaiHoc

                        WHERE
                            bh2.MaKhoaHoc = kh.MaKhoaHoc
                    ) AS SoTuVung

                FROM dbo.KhoaHoc AS kh

                WHERE
                    kh.MaCapDo BETWEEN 1 AND 4

                ORDER BY
                    kh.MaCapDo,
                    kh.MaKhoaHoc;
                """
            )


            for row in cursor.fetchall():

                course = row_to_dict(
                    cursor,
                    row
                )


                course["SoBaiHoc"] = int(
                    course["SoBaiHoc"]
                    or 0
                )


                course["SoTuVung"] = int(
                    course["SoTuVung"]
                    or 0
                )


                courses.append(
                    course
                )


    return render_template(
        "student/home.html",
        courses=courses
    )