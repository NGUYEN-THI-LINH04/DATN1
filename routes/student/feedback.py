
# -*- coding: utf-8 -*-
"""
MỘC HÁN - GÓP Ý DÀNH CHO NGƯỜI HỌC

File: routes/student/feedback.py

Chức năng:
- Hiển thị trang Góp ý.
- Người học gửi góp ý vào SQL Server.
- Xem lịch sử góp ý của chính mình.
- Xem trạng thái và phản hồi của Admin.

Bảng sử dụng:
    dbo.GopY
    dbo.NguoiDung

Trạng thái đúng theo SQL:
    moi
    dang_xu_ly
    da_xu_ly

Không tạo bảng SQL mới.
"""

from contextlib import closing

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

student_feedback_bp = Blueprint(
    "student_feedback",
    __name__,
    url_prefix="/student/feedback",
)

MIN_CONTENT_LENGTH = 10
MAX_CONTENT_LENGTH = 4000
MAX_HISTORY_ITEMS = 50

STATUS_LABELS = {
    "moi": "Chờ xử lý",
    "dang_xu_ly": "Đang xử lý",
    "da_xu_ly": "Đã xử lý",
}


# ==========================================================
# 2. KIỂM TRA TÀI KHOẢN NGƯỜI HỌC
# ==========================================================

@student_feedback_bp.before_request
def require_student():

    account = getattr(g, "account", None)

    if account is None:

        if request.path.startswith(
            "/student/feedback/api/"
        ):
            return jsonify({
                "success": False,
                "message": "Bạn cần đăng nhập trước.",
            }), 401

        return redirect(
            url_for("auth.login")
        )

    if account["role"] != "student":

        if request.path.startswith(
            "/student/feedback/api/"
        ):
            return jsonify({
                "success": False,
                "message": (
                    "Chức năng chỉ dành cho Người học."
                ),
            }), 403

        abort(403)


def get_student_id():
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


def format_datetime(value):

    if value is None:
        return None

    # SQL đang lưu thời gian UTC.
    return value.isoformat() + "Z"


def database_error():

    current_app.logger.exception(
        "Lỗi SQL Server tại chức năng Góp ý"
    )

    return jsonify({
        "success": False,
        "message": (
            "Không thể xử lý dữ liệu góp ý. "
            "Vui lòng thử lại sau."
        ),
    }), 500


# ==========================================================
# 4. TRANG GÓP Ý NGƯỜI HỌC
#
# GET /student/feedback/
# ==========================================================

@student_feedback_bp.get("/")
def index():

    return render_template(
        "student/feedback.html"
    )


# ==========================================================
# 5. API LẤY LỊCH SỬ GÓP Ý
#
# GET /student/feedback/api/list
#
# Chỉ lấy góp ý của tài khoản đang đăng nhập.
# ==========================================================

@student_feedback_bp.get("/api/list")
def api_list():

    student_id = get_student_id()

    try:

        with closing(get_connection()) as conn:

            with closing(conn.cursor()) as cursor:

                cursor.execute(
                    """
                    SELECT TOP (50)
                        g.MaGopY,
                        g.MaBaiHoc,
                        g.NoiDung,
                        g.TrangThai,
                        g.TraLoiQuanTri,
                        g.NgayTao,
                        g.NgayXuLyXong
                    FROM dbo.GopY AS g
                    WHERE g.MaNguoiDung = ?
                    ORDER BY
                        g.NgayTao DESC,
                        g.MaGopY DESC
                    """,
                    student_id
                )

                rows = fetch_all(cursor)

        feedback_items = []

        for row in rows:

            status = row["TrangThai"]

            feedback_items.append({
                "id": int(row["MaGopY"]),
                "lesson_id": row["MaBaiHoc"],
                "content": row["NoiDung"],
                "status": status,
                "status_label": STATUS_LABELS.get(
                    status,
                    "Chưa xác định"
                ),
                "admin_reply": (
                    row["TraLoiQuanTri"] or ""
                ),
                "created_at": format_datetime(
                    row["NgayTao"]
                ),
                "resolved_at": format_datetime(
                    row["NgayXuLyXong"]
                ),
            })

        return jsonify({
            "success": True,
            "total": len(feedback_items),
            "limit": MAX_HISTORY_ITEMS,
            "items": feedback_items,
        })

    except pyodbc.Error:
        return database_error()


# ==========================================================
# 6. API GỬI GÓP Ý
#
# POST /student/feedback/api/send
#
# JSON:
# {
#     "content": "Nội dung góp ý của người học"
# }
#
# CSRF được Flask-WTF kiểm tra tự động.
# ==========================================================

@student_feedback_bp.post("/api/send")
def api_send():

    student_id = get_student_id()

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return jsonify({
            "success": False,
            "message": "Dữ liệu gửi lên không hợp lệ.",
        }), 400

    content = data.get("content", "")

    if not isinstance(content, str):

        return jsonify({
            "success": False,
            "message": "Nội dung góp ý không hợp lệ.",
        }), 400

    content = content.strip()

    if len(content) < MIN_CONTENT_LENGTH:

        return jsonify({
            "success": False,
            "message": (
                "Nội dung góp ý phải có "
                "ít nhất 10 ký tự."
            ),
        }), 400

    if len(content) > MAX_CONTENT_LENGTH:

        return jsonify({
            "success": False,
            "message": (
                "Nội dung góp ý không được "
                "vượt quá 4000 ký tự."
            ),
        }), 400

    # Không cho phép ký tự điều khiển bất thường.
    if any(
        ord(char) < 32
        and char not in "\n\r\t"
        for char in content
    ):

        return jsonify({
            "success": False,
            "message": (
                "Nội dung chứa ký tự không hợp lệ."
            ),
        }), 400

    try:

        with closing(get_connection()) as conn:

            try:

                with closing(conn.cursor()) as cursor:

                    # Hạn chế gửi lặp cùng nội dung
                    # trong vòng 30 giây.
                    cursor.execute(
                        """
                        SELECT TOP (1) MaGopY
                        FROM dbo.GopY
                        WHERE MaNguoiDung = ?
                          AND NoiDung = ?
                          AND NgayTao >= DATEADD(
                              SECOND,
                              -30,
                              SYSUTCDATETIME()
                          )
                        """,
                        student_id,
                        content
                    )

                    if cursor.fetchone() is not None:

                        return jsonify({
                            "success": False,
                            "message": (
                                "Bạn vừa gửi góp ý này. "
                                "Vui lòng không gửi lặp."
                            ),
                        }), 409

                    # Góp ý chung không bắt buộc
                    # liên kết với một bài học.
                    #
                    # Trạng thái 'moi' phù hợp
                    # CHECK constraint của SQL.
                    cursor.execute(
                        """
                        INSERT INTO dbo.GopY
                        (
                            MaNguoiDung,
                            MaBaiHoc,
                            NoiDung,
                            TrangThai,
                            NgayTao
                        )
                        OUTPUT INSERTED.MaGopY
                        VALUES
                        (
                            ?,
                            NULL,
                            ?,
                            'moi',
                            SYSUTCDATETIME()
                        )
                        """,
                        student_id,
                        content
                    )

                    result = cursor.fetchone()

                    feedback_id = int(result[0])

                conn.commit()

            except Exception:

                conn.rollback()
                raise

        return jsonify({
            "success": True,
            "message": (
                "Đã gửi góp ý thành công. "
                "Bạn có thể theo dõi phản hồi "
                "trong lịch sử góp ý."
            ),
            "feedback_id": feedback_id,
            "status": "moi",
        }), 201

    except pyodbc.Error:
        return database_error()
