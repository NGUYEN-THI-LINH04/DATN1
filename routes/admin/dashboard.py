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

admin_dashboard_bp = Blueprint(
    "admin_dashboard",
    __name__,
    url_prefix="/admin",
)


# =========================================================
# KIỂM TRA QUYỀN ADMIN
# =========================================================

@admin_dashboard_bp.before_request
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
            description="Bạn không có quyền truy cập khu vực quản trị."
        )


# =========================================================
# XỬ LÝ LỖI SQL
# =========================================================

@admin_dashboard_bp.errorhandler(
    pyodbc.Error
)
def handle_database_error(error):

    current_app.logger.error(
        "Loi SQL tai Dashboard Admin: %s",
        type(error).__name__
    )

    return (
        "Chưa thể tải dữ liệu quản trị. "
        "Vui lòng thử lại.",
        503
    )


# =========================================================
# DASHBOARD ADMIN
# URL:
# /admin/dashboard
# =========================================================

@admin_dashboard_bp.get(
    "/dashboard"
)
def index():

    stats = {
        "users": 0,
        "active_users": 0,

        "courses": 0,
        "published_courses": 0,
        "draft_courses": 0,

        "lessons": 0,
        "published_lessons": 0,
        "draft_lessons": 0,

        "vocabulary": 0,
        "grammar": 0,
        "hanzi": 0,

        "new_feedback": 0,

        "pending_knowledge": 0,

        "missing_words": 0,
    }


    recent_feedback = []


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            # =================================================
            # 1. NGƯỜI HỌC
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongNguoiHoc,

                    SUM(
                        CASE
                            WHEN DangHoatDong = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS DangHoatDong

                FROM dbo.NguoiDung;
                """
            )


            row = cursor.fetchone()


            if row:

                stats["users"] = int(
                    row[0]
                    or 0
                )

                stats["active_users"] = int(
                    row[1]
                    or 0
                )


            # =================================================
            # 2. KHÓA HỌC
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongKhoaHoc,

                    SUM(
                        CASE
                            WHEN TrangThai = 'da_xuat_ban'
                            THEN 1
                            ELSE 0
                        END
                    ) AS DaXuatBan,

                    SUM(
                        CASE
                            WHEN TrangThai = 'ban_nhap'
                            THEN 1
                            ELSE 0
                        END
                    ) AS BanNhap

                FROM dbo.KhoaHoc;
                """
            )


            row = cursor.fetchone()


            if row:

                stats["courses"] = int(
                    row[0]
                    or 0
                )

                stats["published_courses"] = int(
                    row[1]
                    or 0
                )

                stats["draft_courses"] = int(
                    row[2]
                    or 0
                )


            # =================================================
            # 3. BÀI HỌC
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongBaiHoc,

                    SUM(
                        CASE
                            WHEN TrangThai = 'da_xuat_ban'
                            THEN 1
                            ELSE 0
                        END
                    ) AS DaXuatBan,

                    SUM(
                        CASE
                            WHEN TrangThai = 'ban_nhap'
                            THEN 1
                            ELSE 0
                        END
                    ) AS BanNhap

                FROM dbo.BaiHoc;
                """
            )


            row = cursor.fetchone()


            if row:

                stats["lessons"] = int(
                    row[0]
                    or 0
                )

                stats["published_lessons"] = int(
                    row[1]
                    or 0
                )

                stats["draft_lessons"] = int(
                    row[2]
                    or 0
                )


            # =================================================
            # 4. TỪ VỰNG
            # =================================================

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dbo.TuVung;
                """
            )


            stats["vocabulary"] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 5. NGỮ PHÁP
            # =================================================

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dbo.NguPhap;
                """
            )


            stats["grammar"] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 6. CHỮ HÁN
            # =================================================

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dbo.ChuHan;
                """
            )


            stats["hanzi"] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 7. GÓP Ý MỚI
            #
            # Người học
            #     ↓
            # GopY
            #     ↓
            # Admin xử lý
            # =================================================

            cursor.execute(
                """
                SELECT COUNT(*)

                FROM dbo.GopY

                WHERE TrangThai = 'moi';
                """
            )


            stats["new_feedback"] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 8. KIẾN THỨC CHATBOT CHƯA DUYỆT
            #
            # Admin
            #     ↓
            # KhoKienThuc
            #     ↓
            # Chatbot
            # =================================================

            cursor.execute(
                """
                SELECT COUNT(*)

                FROM dbo.KhoKienThuc

                WHERE
                    DaDuyet = 0
                    AND DangHoatDong = 1;
                """
            )


            stats["pending_knowledge"] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 9. TỪ CHATBOT CHƯA XỬ LÝ
            #
            # Người học hỏi chatbot
            #     ↓
            # không có dữ liệu
            #     ↓
            # TuChuaCo
            #     ↓
            # Admin xử lý
            # =================================================

            cursor.execute(
                """
                SELECT COUNT(*)

                FROM dbo.TuChuaCo

                WHERE
                    TrangThai IN (
                        'moi',
                        'dang_duyet'
                    );
                """
            )


            stats["missing_words"] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 10. GÓP Ý GẦN ĐÂY
            # =================================================

            cursor.execute(
                """
                SELECT TOP 5
                    gy.MaGopY,
                    nd.HoTen,
                    gy.NoiDung,
                    gy.TrangThai,
                    gy.NgayTao,
                    bh.TieuDe

                FROM dbo.GopY AS gy

                INNER JOIN dbo.NguoiDung AS nd
                    ON nd.MaNguoiDung
                    = gy.MaNguoiDung

                LEFT JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc
                    = gy.MaBaiHoc

                ORDER BY
                    gy.NgayTao DESC,
                    gy.MaGopY DESC;
                """
            )


            for row in cursor.fetchall():

                recent_feedback.append(
                    {
                        "id": row[0],

                        "user_name": (
                            row[1]
                            or "Người học"
                        ),

                        "content": (
                            row[2]
                            or ""
                        ),

                        "status": (
                            row[3]
                            or ""
                        ),

                        "created_at": row[4],

                        "lesson_title": (
                            row[5]
                            or ""
                        ),
                    }
                )


    return render_template(
        "admin/dashboard.html",

        active_page="dashboard",

        stats=stats,

        recent_feedback=recent_feedback,
    )