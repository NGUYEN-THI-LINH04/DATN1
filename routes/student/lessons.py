from flask import Blueprint, render_template, abort
from contextlib import closing

from database import get_connection


lessons_bp = Blueprint(
    "lessons",
    __name__,
    url_prefix="/bai-hoc"
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
        zip(columns, row)
    )


# =========================================================
# DANH SÁCH BÀI
# URL: /bai-hoc
# =========================================================
@lessons_bp.route("")
def index():

    lessons = []

    with closing(get_connection()) as conn:

        with closing(conn.cursor()) as cursor:

            cursor.execute(
                """
                SELECT
                    bh.MaBaiHoc,
                    bh.MaKhoaHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe,
                    bh.TomTat,
                    bh.TrangThai,

                    kh.MaCapDo,
                    kh.MaKyHieu,
                    kh.TieuDe AS TieuDeKhoaHoc

                FROM dbo.BaiHoc AS bh

                INNER JOIN dbo.KhoaHoc AS kh
                    ON bh.MaKhoaHoc = kh.MaKhoaHoc

                ORDER BY
                    kh.MaCapDo,
                    bh.SoThuTuBai;
                """
            )

            for row in cursor.fetchall():

                lessons.append(
                    row_to_dict(
                        cursor,
                        row
                    )
                )


    return render_template(
        "student/lessons.html",
        lessons=lessons
    )


# =========================================================
# CHI TIẾT BÀI HỌC
# URL:
# /bai-hoc/1
# =========================================================
@lessons_bp.route("/<int:lesson_id>")
def detail(lesson_id):

    lesson = None
    course = None

    vocabularies = []
    grammars = []
    hanzis = []

    previous_lesson = None
    next_lesson = None


    with closing(get_connection()) as conn:

        with closing(conn.cursor()) as cursor:

            # =================================================
            # 1. THÔNG TIN BÀI + KHÓA
            # =================================================
            cursor.execute(
                """
                SELECT
                    bh.MaBaiHoc,
                    bh.MaKhoaHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe,
                    bh.TomTat,
                    bh.TrangThai,

                    kh.MaCapDo,
                    kh.MaKyHieu,
                    kh.TieuDe AS TieuDeKhoaHoc,
                    kh.MoTa AS MoTaKhoaHoc

                FROM dbo.BaiHoc AS bh

                INNER JOIN dbo.KhoaHoc AS kh
                    ON bh.MaKhoaHoc = kh.MaKhoaHoc

                WHERE
                    bh.MaBaiHoc = ?;
                """,
                lesson_id
            )

            row = cursor.fetchone()

            if row is None:
                abort(404)

            lesson = row_to_dict(
                cursor,
                row
            )


            course = {
                "MaKhoaHoc":
                    lesson["MaKhoaHoc"],

                "MaCapDo":
                    lesson["MaCapDo"],

                "MaKyHieu":
                    lesson["MaKyHieu"],

                "TieuDe":
                    lesson["TieuDeKhoaHoc"],
            }


            # =================================================
            # 2. TỪ VỰNG
            # =================================================
            cursor.execute(
                """
                SELECT
                    tv.MaTuVung,
                    tv.ChuHan,
                    tv.ChuPhonThe,
                    tv.PhienAm,
                    tv.NghiaTiengViet,
                    tv.TuLoai,
                    tv.ViDuTiengTrung,
                    tv.ViDuTiengViet,

                    tv.MaAmThanh,

                    audio_tv.DuongDanTep
                        AS DuongDanAudio,

                    tv.MaNguon,
                    tv.DaDuyet,

                    tvbh.ThuTu

                FROM dbo.TuVungBaiHoc AS tvbh

                INNER JOIN dbo.TuVung AS tv
                    ON tvbh.MaTuVung = tv.MaTuVung

                LEFT JOIN dbo.TepDaPhuongTien AS audio_tv
                    ON tv.MaAmThanh = audio_tv.MaTep
                    AND audio_tv.LoaiTep = 'am_thanh'

                WHERE
                    tvbh.MaBaiHoc = ?

                ORDER BY
                    tvbh.ThuTu,
                    tv.MaTuVung;
                """,
                lesson_id
            )

            for row in cursor.fetchall():

                vocabularies.append(
                    row_to_dict(
                        cursor,
                        row
                    )
                )


            # =================================================
            # 3. NGỮ PHÁP
            # =================================================
            cursor.execute(
                """
                SELECT
                    ng.MaNguPhap,
                    ng.TenCauTruc,
                    ng.MoTa,
                    ng.CachDung,
                    ng.ViDuTiengTrung,
                    ng.ViDuPinyin,
                    ng.ViDuTiengViet,
                    ng.MaTep,
                    ng.MaNguon,
                    ng.ThuTu,
                    ng.TrangThai

                FROM dbo.NguPhap AS ng

                WHERE
                    ng.MaBaiHoc = ?

                ORDER BY
                    ng.ThuTu,
                    ng.MaNguPhap;
                """,
                lesson_id
            )

            for row in cursor.fetchall():

                grammars.append(
                    row_to_dict(
                        cursor,
                        row
                    )
                )


            # =================================================
            # 4. CHỮ HÁN
            # =================================================
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

                    ch.MaBoThu,
                    ch.MaTep,

                    audio_hanzi.DuongDanTep
                        AS DuongDanAudio,

                    ch.MaNguon,
                    ch.ThuTu,
                    ch.TrangThai,

                    bt.KyHieu AS KyHieuBoThu,
                    bt.TenBoThu,
                    bt.YNghia AS YNghiaBoThu

                FROM dbo.ChuHan AS ch

                LEFT JOIN dbo.BoThu AS bt
                    ON ch.MaBoThu = bt.MaBoThu

                LEFT JOIN dbo.TepDaPhuongTien AS audio_hanzi
                    ON ch.MaTep = audio_hanzi.MaTep
                    AND audio_hanzi.LoaiTep = 'am_thanh'

                WHERE
                    ch.MaBaiHoc = ?

                ORDER BY
                    ch.ThuTu,
                    ch.MaChuHan;
                """,
                lesson_id
            )

            for row in cursor.fetchall():

                hanzis.append(
                    row_to_dict(
                        cursor,
                        row
                    )
                )


            # =================================================
            # 5. BÀI TRƯỚC
            # =================================================
            cursor.execute(
                """
                SELECT TOP 1
                    MaBaiHoc,
                    SoThuTuBai,
                    TieuDe

                FROM dbo.BaiHoc

                WHERE
                    MaKhoaHoc = ?
                    AND SoThuTuBai < ?

                ORDER BY
                    SoThuTuBai DESC;
                """,
                lesson["MaKhoaHoc"],
                lesson["SoThuTuBai"]
            )

            row = cursor.fetchone()

            if row:

                previous_lesson = (
                    row_to_dict(
                        cursor,
                        row
                    )
                )


            # =================================================
            # 6. BÀI TIẾP
            # =================================================
            cursor.execute(
                """
                SELECT TOP 1
                    MaBaiHoc,
                    SoThuTuBai,
                    TieuDe

                FROM dbo.BaiHoc

                WHERE
                    MaKhoaHoc = ?
                    AND SoThuTuBai > ?

                ORDER BY
                    SoThuTuBai ASC;
                """,
                lesson["MaKhoaHoc"],
                lesson["SoThuTuBai"]
            )

            row = cursor.fetchone()

            if row:

                next_lesson = (
                    row_to_dict(
                        cursor,
                        row
                    )
                )


    return render_template(
        "student/lesson.html",

        lesson=lesson,
        course=course,

        vocabularies=vocabularies,
        grammars=grammars,
        hanzis=hanzis,

        previous_lesson=previous_lesson,
        next_lesson=next_lesson,

        total_vocabulary=len(vocabularies),
        total_grammar=len(grammars),
        total_hanzi=len(hanzis)
    )