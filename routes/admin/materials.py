from contextlib import closing

import pyodbc

from flask import (
    Blueprint,
    abort,
    current_app,
    g,
    redirect,
    render_template,
    url_for,
)

from database import get_connection


# =========================================================
# BLUEPRINT
# =========================================================

admin_materials_bp = Blueprint(
    "admin_materials",
    __name__,
    url_prefix="/admin/hoc-lieu",
)


# =========================================================
# KIỂM TRA QUYỀN ADMIN
# =========================================================

@admin_materials_bp.before_request
def require_admin():

    account = getattr(
        g,
        "account",
        None
    )

    if account is None:

        return redirect(
            url_for(
                "auth.admin_login"
            )
        )

    if account["role"] != "admin":

        abort(
            403,
            description="Bạn không có quyền quản lý học liệu."
        )


# =========================================================
# DATABASE ERROR
# =========================================================

@admin_materials_bp.errorhandler(
    pyodbc.Error
)
def handle_database_error(error):

    current_app.logger.error(
        "Loi SQL trong trang hoc lieu: %s",
        type(error).__name__
    )

    return (
        "Chưa thể tải dữ liệu học liệu. "
        "Vui lòng thử lại.",
        503
    )


# =========================================================
# TRANG TỔNG QUAN HỌC LIỆU
#
# URL:
# /admin/hoc-lieu/
# =========================================================

@admin_materials_bp.get("/")
def index():

    stats = {

        # Từ vựng
        "vocabulary_total": 0,
        "vocabulary_approved": 0,

        # Ngữ pháp
        "grammar_total": 0,
        "grammar_published": 0,

        # Chữ Hán
        "hanzi_total": 0,
        "hanzi_published": 0,

        # Pinyin
        "pinyin_total": 0,
        "pinyin_published": 0,

        # Bộ thủ
        "radical_total": 0,
        "radical_published": 0,

        # Quy tắc phát âm
        "pronunciation_total": 0,
        "pronunciation_published": 0,

        # Media
        "media_total": 0,
        "audio_total": 0,
        "image_total": 0,
        "video_total": 0,
    }


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # 1. TỪ VỰNG
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongSo,

                    SUM(
                        CASE
                            WHEN DaDuyet = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS DaDuyet

                FROM dbo.TuVung;
                """
            )


            row = cursor.fetchone()


            stats["vocabulary_total"] = int(
                row[0]
                or 0
            )

            stats["vocabulary_approved"] = int(
                row[1]
                or 0
            )


            # =================================================
            # 2. NGỮ PHÁP
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongSo,

                    SUM(
                        CASE
                            WHEN TrangThai = 'da_xuat_ban'
                            THEN 1
                            ELSE 0
                        END
                    ) AS DaXuatBan

                FROM dbo.NguPhap;
                """
            )


            row = cursor.fetchone()


            stats["grammar_total"] = int(
                row[0]
                or 0
            )

            stats["grammar_published"] = int(
                row[1]
                or 0
            )


            # =================================================
            # 3. CHỮ HÁN
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongSo,

                    SUM(
                        CASE
                            WHEN TrangThai = 'da_xuat_ban'
                            THEN 1
                            ELSE 0
                        END
                    ) AS DaXuatBan

                FROM dbo.ChuHan;
                """
            )


            row = cursor.fetchone()


            stats["hanzi_total"] = int(
                row[0]
                or 0
            )

            stats["hanzi_published"] = int(
                row[1]
                or 0
            )


            # =================================================
            # 4. PINYIN
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongSo,

                    SUM(
                        CASE
                            WHEN TrangThai = 'da_xuat_ban'
                            THEN 1
                            ELSE 0
                        END
                    ) AS DaXuatBan

                FROM dbo.BangPinyin;
                """
            )


            row = cursor.fetchone()


            stats["pinyin_total"] = int(
                row[0]
                or 0
            )

            stats["pinyin_published"] = int(
                row[1]
                or 0
            )


            # =================================================
            # 5. BỘ THỦ
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongSo,

                    SUM(
                        CASE
                            WHEN TrangThai = 'da_xuat_ban'
                            THEN 1
                            ELSE 0
                        END
                    ) AS DaXuatBan

                FROM dbo.BoThu;
                """
            )


            row = cursor.fetchone()


            stats["radical_total"] = int(
                row[0]
                or 0
            )

            stats["radical_published"] = int(
                row[1]
                or 0
            )


            # =================================================
            # 6. QUY TẮC PHÁT ÂM
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongSo,

                    SUM(
                        CASE
                            WHEN TrangThai = 'da_xuat_ban'
                            THEN 1
                            ELSE 0
                        END
                    ) AS DaXuatBan

                FROM dbo.QuyTacPhatAm;
                """
            )


            row = cursor.fetchone()


            stats["pronunciation_total"] = int(
                row[0]
                or 0
            )

            stats["pronunciation_published"] = int(
                row[1]
                or 0
            )


            # =================================================
            # 7. HÌNH ẢNH / ÂM THANH / VIDEO
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongSo,

                    SUM(
                        CASE
                            WHEN LoaiTep = 'am_thanh'
                            THEN 1
                            ELSE 0
                        END
                    ) AS AmThanh,

                    SUM(
                        CASE
                            WHEN LoaiTep = 'hinh_anh'
                            THEN 1
                            ELSE 0
                        END
                    ) AS HinhAnh,

                    SUM(
                        CASE
                            WHEN LoaiTep = 'video'
                            THEN 1
                            ELSE 0
                        END
                    ) AS Video

                FROM dbo.TepDaPhuongTien;
                """
            )


            row = cursor.fetchone()


            stats["media_total"] = int(
                row[0]
                or 0
            )

            stats["audio_total"] = int(
                row[1]
                or 0
            )

            stats["image_total"] = int(
                row[2]
                or 0
            )

            stats["video_total"] = int(
                row[3]
                or 0
            )


    return render_template(
        "admin/materials.html",

        active_page="materials",

        stats=stats,
    )