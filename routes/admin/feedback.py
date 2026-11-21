
# -*- coding: utf-8 -*-
"""
MỘC HÁN - QUẢN LÝ GÓP Ý BÊN ADMIN

File:
    routes/admin/feedback.py

Chức năng:
    1. Hiển thị trang quản lý góp ý.
    2. Lấy danh sách góp ý từ SQL Server.
    3. Thống kê theo trạng thái.
    4. Tìm kiếm và lọc góp ý.
    5. Cập nhật trạng thái xử lý.
    6. Trả lời góp ý của người học.

Bảng SQL Server:
    dbo.GopY
    dbo.NguoiDung
    dbo.QuanTriVien (khóa ngoại NguoiXuLy)

Trạng thái:
    moi
    dang_xu_ly
    da_xu_ly

Ngày giờ:
    SQL lưu UTC.
    JavaScript sẽ hiển thị giờ Việt Nam.

Không tạo bảng SQL mới.
Không ảnh hưởng chức năng Góp ý Student.
"""

from contextlib import closing
from math import ceil

import pyodbc

from flask import (
    Blueprint,
    abort,
    current_app,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from database import get_connection


# ==========================================================
# 1. BLUEPRINT
# ==========================================================

admin_feedback_bp = Blueprint(
    "admin_feedback",
    __name__,
    url_prefix="/admin/gop-y",
)

PAGE_SIZE = 15
MAX_REPLY_LENGTH = 4000
MAX_SEARCH_LENGTH = 100

STATUS_LABELS = {
    "moi": "Chờ xử lý",
    "dang_xu_ly": "Đang xử lý",
    "da_xu_ly": "Đã xử lý",
}


# ==========================================================
# 2. XÁC THỰC QUẢN TRỊ VIÊN
# ==========================================================

@admin_feedback_bp.before_request
def require_admin():

    account = getattr(g, "account", None)

    is_api = request.path.startswith(
        "/admin/gop-y/api/"
    )

    if account is None:

        if is_api:
            return jsonify({
                "success": False,
                "message": (
                    "Phiên đăng nhập đã hết hạn. "
                    "Vui lòng đăng nhập lại."
                ),
            }), 401

        return redirect(
            url_for("auth.admin_login")
        )

    if account["role"] != "admin":

        if is_api:
            return jsonify({
                "success": False,
                "message": (
                    "Bạn không có quyền quản lý góp ý."
                ),
            }), 403

        abort(403)


def get_admin_id():
    """
    Lấy mã quản trị viên từ tài khoản thật.

    ID này tương ứng với:
        dbo.QuanTriVien.MaQuanTriVien
    """
    return int(g.account["id"])


# ==========================================================
# 3. HÀM HỖ TRỢ
# ==========================================================

def fetch_all(cursor):
    columns = [
        column[0]
        for column in cursor.description
    ]

    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def format_datetime_utc(value):
    """
    SQL Server lưu DATETIME2 theo UTC.

    Gắn ký hiệu Z để JavaScript có thể
    chuyển đúng sang giờ Việt Nam.
    """
    if value is None:
        return None

    return value.isoformat() + "Z"


def database_error():
    current_app.logger.exception(
        "Lỗi SQL Server trong Admin Góp ý"
    )

    return jsonify({
        "success": False,
        "message": (
            "Không thể xử lý dữ liệu góp ý. "
            "Vui lòng kiểm tra kết nối SQL Server."
        ),
    }), 500


def positive_int(value, default=1):

    try:
        number = int(value)

        if number > 0:
            return number

    except (TypeError, ValueError, OverflowError):
        pass

    return default


def format_feedback(row):
    """
    Chuyển một bản ghi SQL thành dữ liệu JSON
    cho trang quản lý góp ý.
    """

    status = row["TrangThai"]

    return {
        "id": int(row["MaGopY"]),

        "student_id": int(
            row["MaNguoiDung"]
        ),

        "student_name": (
            row["HoTen"] or
            row["TenDangNhap"] or
            "Người học"
        ),

        "username": (
            row["TenDangNhap"] or ""
        ),

        "email": (
            row["ThuDienTu"] or ""
        ),

        "lesson_id": row["MaBaiHoc"],

        "content": row["NoiDung"],

        "status": status,

        "status_label": STATUS_LABELS.get(
            status,
            "Không xác định"
        ),

        "admin_reply": (
            row["TraLoiQuanTri"] or ""
        ),

        "admin_id": row["NguoiXuLy"],

        "created_at": format_datetime_utc(
            row["NgayTao"]
        ),

        "resolved_at": format_datetime_utc(
            row["NgayXuLyXong"]
        ),
    }


# ==========================================================
# 4. TRANG QUẢN LÝ GÓP Ý
#
# GET /admin/gop-y/
# ==========================================================

@admin_feedback_bp.get("/")
def index():

    return render_template(
        "admin/feedback.html",
        active_page="feedback",
    )


# ==========================================================
# 5. DANH SÁCH GÓP Ý
#
# GET /admin/gop-y/api/list
#
# Query:
#     status=all|moi|dang_xu_ly|da_xu_ly
#     q=...
#     page=1
#
# Có:
#     - Thống kê tổng số
#     - Bộ lọc trạng thái
#     - Tìm kiếm
#     - Phân trang
# ==========================================================

@admin_feedback_bp.get("/api/list")
def api_list():

    status = (
        request.args.get("status", "all") or "all"
    ).strip()

    keyword = (
        request.args.get("q", "") or ""
    ).strip()

    page = positive_int(
        request.args.get("page"),
        default=1,
    )

    if status != "all" and status not in STATUS_LABELS:

        return jsonify({
            "success": False,
            "message": "Trạng thái lọc không hợp lệ.",
        }), 400

    if len(keyword) > MAX_SEARCH_LENGTH:

        return jsonify({
            "success": False,
            "message": (
                "Từ khóa tìm kiếm quá dài."
            ),
        }), 400

    conditions = []
    parameters = []

    # ------------------------------------------------------
    # LỌC TRẠNG THÁI
    # ------------------------------------------------------

    if status != "all":

        conditions.append(
            "gy.TrangThai = ?"
        )

        parameters.append(status)

    # ------------------------------------------------------
    # TÌM KIẾM
    # ------------------------------------------------------

    if keyword:

        search_value = f"%{keyword}%"

        conditions.append(
            """
            (
                gy.NoiDung LIKE ?
                OR nd.HoTen LIKE ?
                OR nd.TenDangNhap LIKE ?
                OR nd.ThuDienTu LIKE ?
            )
            """
        )

        parameters.extend([
            search_value,
            search_value,
            search_value,
            search_value,
        ])

    where_clause = ""

    if conditions:

        where_clause = (
            "WHERE " + " AND ".join(conditions)
        )

    try:

        with closing(get_connection()) as conn:

            with closing(conn.cursor()) as cursor:

                # ==========================================
                # 1. THỐNG KÊ TẤT CẢ GÓP Ý
                #
                # Không bị ảnh hưởng bởi bộ lọc.
                # ==========================================

                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS Tong,

                        COALESCE(
                            SUM(
                                CASE
                                    WHEN TrangThai = 'moi'
                                    THEN 1 ELSE 0
                                END
                            ),
                            0
                        ) AS ChoXuLy,

                        COALESCE(
                            SUM(
                                CASE
                                    WHEN TrangThai = 'dang_xu_ly'
                                    THEN 1 ELSE 0
                                END
                            ),
                            0
                        ) AS DangXuLy,

                        COALESCE(
                            SUM(
                                CASE
                                    WHEN TrangThai = 'da_xu_ly'
                                    THEN 1 ELSE 0
                                END
                            ),
                            0
                        ) AS DaXuLy

                    FROM dbo.GopY
                    """
                )

                summary_row = cursor.fetchone()

                summary = {
                    "total": int(
                        summary_row[0] or 0
                    ),
                    "moi": int(
                        summary_row[1] or 0
                    ),
                    "dang_xu_ly": int(
                        summary_row[2] or 0
                    ),
                    "da_xu_ly": int(
                        summary_row[3] or 0
                    ),
                }

                # ==========================================
                # 2. ĐẾM KẾT QUẢ SAU KHI LỌC
                # ==========================================

                count_sql = f"""
                    SELECT COUNT(*)

                    FROM dbo.GopY AS gy

                    INNER JOIN dbo.NguoiDung AS nd
                        ON gy.MaNguoiDung = nd.MaNguoiDung

                    {where_clause}
                """

                cursor.execute(
                    count_sql,
                    *parameters
                )

                total = int(
                    cursor.fetchone()[0] or 0
                )

                total_pages = max(
                    1,
                    ceil(total / PAGE_SIZE)
                )

                page = min(
                    page,
                    total_pages
                )

                offset = (
                    page - 1
                ) * PAGE_SIZE

                # ==========================================
                # 3. DANH SÁCH GÓP Ý
                # ==========================================

                list_sql = f"""
                    SELECT
                        gy.MaGopY,
                        gy.MaNguoiDung,
                        gy.MaBaiHoc,
                        gy.NoiDung,
                        gy.TrangThai,
                        gy.TraLoiQuanTri,
                        gy.NguoiXuLy,
                        gy.NgayTao,
                        gy.NgayXuLyXong,

                        nd.HoTen,
                        nd.TenDangNhap,
                        nd.ThuDienTu

                    FROM dbo.GopY AS gy

                    INNER JOIN dbo.NguoiDung AS nd
                        ON gy.MaNguoiDung = nd.MaNguoiDung

                    {where_clause}

                    ORDER BY
                        gy.NgayTao DESC,
                        gy.MaGopY DESC

                    OFFSET ? ROWS
                    FETCH NEXT ? ROWS ONLY
                """

                cursor.execute(
                    list_sql,
                    *parameters,
                    offset,
                    PAGE_SIZE,
                )

                rows = fetch_all(cursor)

        items = [
            format_feedback(row)
            for row in rows
        ]

        return jsonify({
            "success": True,
            "summary": summary,
            "items": items,
            "total": total,
            "page": page,
            "page_size": PAGE_SIZE,
            "total_pages": total_pages,
            "status": status,
            "q": keyword,
        })

    except pyodbc.Error:

        return database_error()


# ==========================================================
# 6. CẬP NHẬT / PHẢN HỒI GÓP Ý
#
# POST /admin/gop-y/api/update/<feedback_id>
#
# JSON:
# {
#     "status": "dang_xu_ly",
#     "reply": "Cảm ơn bạn đã góp ý..."
# }
#
# Có thể:
#     - Chuyển sang đang xử lý.
#     - Gửi phản hồi.
#     - Đánh dấu đã xử lý.
#     - Chỉnh sửa nội dung phản hồi.
#
# CSRF được Flask-WTF kiểm tra tự động.
# ==========================================================

@admin_feedback_bp.post(
    "/api/update/<int:feedback_id>"
)
def api_update(feedback_id):

    admin_id = get_admin_id()

    if feedback_id <= 0:

        return jsonify({
            "success": False,
            "message": "Mã góp ý không hợp lệ.",
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return jsonify({
            "success": False,
            "message": "Dữ liệu gửi lên không hợp lệ.",
        }), 400

    status = data.get("status")
    reply = data.get("reply", "")

    # ------------------------------------------------------
    # KIỂM TRA TRẠNG THÁI
    # ------------------------------------------------------

    if not isinstance(status, str):
        return jsonify({
            "success": False,
            "message": "Trạng thái không hợp lệ.",
        }), 400

    status = status.strip()

    if status not in STATUS_LABELS:

        return jsonify({
            "success": False,
            "message": (
                "Chỉ chấp nhận trạng thái: "
                "Chờ xử lý, Đang xử lý hoặc Đã xử lý."
            ),
        }), 400

    # ------------------------------------------------------
    # KIỂM TRA PHẢN HỒI
    # ------------------------------------------------------

    if reply is None:
        reply = ""

    if not isinstance(reply, str):

        return jsonify({
            "success": False,
            "message": (
                "Nội dung phản hồi không hợp lệ."
            ),
        }), 400

    reply = reply.strip()

    if len(reply) > MAX_REPLY_LENGTH:

        return jsonify({
            "success": False,
            "message": (
                "Nội dung phản hồi không được "
                "vượt quá 4000 ký tự."
            ),
        }), 400

    if any(
        ord(character) < 32
        and character not in "\n\r\t"
        for character in reply
    ):

        return jsonify({
            "success": False,
            "message": (
                "Phản hồi chứa ký tự không hợp lệ."
            ),
        }), 400

    # Khi hoàn tất xử lý, yêu cầu có phản hồi
    # để người học biết kết quả.
    if status == "da_xu_ly" and not reply:

        return jsonify({
            "success": False,
            "message": (
                "Bạn cần nhập phản hồi trước khi "
                "đánh dấu góp ý đã xử lý."
            ),
        }), 400

    try:

        with closing(get_connection()) as conn:

            try:

                with closing(conn.cursor()) as cursor:

                    # ======================================
                    # 1. KIỂM TRA GÓP Ý CÓ TỒN TẠI
                    # ======================================

                    cursor.execute(
                        """
                        SELECT MaGopY
                        FROM dbo.GopY
                        WHERE MaGopY = ?
                        """,
                        feedback_id
                    )

                    if cursor.fetchone() is None:

                        return jsonify({
                            "success": False,
                            "message": (
                                "Không tìm thấy góp ý này."
                            ),
                        }), 404

                    # ======================================
                    # 2. CẬP NHẬT SQL
                    #
                    # - Không thay đổi nội dung góp ý.
                    # - Không thay đổi người gửi.
                    # - Ghi lại Admin xử lý.
                    # - Ngày hoàn tất lưu UTC.
                    # ======================================

                    cursor.execute(
                        """
                        UPDATE dbo.GopY

                        SET
                            TrangThai = ?,

                            TraLoiQuanTri = ?,

                            NguoiXuLy = ?,

                            NgayXuLyXong =
                                CASE
                                    WHEN ? = 'da_xu_ly'
                                    THEN COALESCE(
                                        NgayXuLyXong,
                                        SYSUTCDATETIME()
                                    )
                                    ELSE NULL
                                END

                        WHERE MaGopY = ?
                        """,
                        status,
                        reply if reply else None,
                        admin_id,
                        status,
                        feedback_id,
                    )

                    if cursor.rowcount == 0:

                        conn.rollback()

                        return jsonify({
                            "success": False,
                            "message": (
                                "Không thể cập nhật góp ý."
                            ),
                        }), 409

                conn.commit()

            except Exception:

                conn.rollback()
                raise

        return jsonify({
            "success": True,
            "message": (
                "Đã cập nhật góp ý thành công."
            ),
            "feedback_id": feedback_id,
            "status": status,
            "status_label": STATUS_LABELS[status],
            "admin_reply": reply,
        })

    except pyodbc.Error:

        return database_error()
