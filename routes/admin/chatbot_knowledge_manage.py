
"""
MỘC HÁN - ADMIN QUẢN LÝ KIẾN THỨC CHATBOT

File: routes/admin/chatbot_knowledge_manage.py

Chức năng:
- Xem danh sách kiến thức bổ sung.
- Tìm kiếm và lọc trạng thái.
- Thêm, sửa kiến thức.
- Duyệt hoặc bỏ duyệt.
- Bật hoặc ngừng sử dụng.
- Kiểm tra quyền Admin.

Sử dụng bảng dbo.KhoKienThuc hiện có.
Không tạo bảng SQL mới.
Không thay đổi học liệu TuVung, NguPhap, ChuHan.
"""

from contextlib import closing

import pyodbc

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from database import get_connection


# ==========================================================
# 01. BLUEPRINT
# ==========================================================

admin_chatbot_knowledge_bp = Blueprint(
    "admin_chatbot_knowledge",
    __name__,
    url_prefix="/admin/chatbot/kien-thuc",
)


# ==========================================================
# 02. KIỂM TRA QUYỀN ADMIN
# ==========================================================

@admin_chatbot_knowledge_bp.before_request
def require_admin():

    account = getattr(g, "account", None)

    if account is None:
        return redirect(
            url_for("auth.admin_login")
        )

    if account.get("role") != "admin":
        abort(
            403,
            description=(
                "Bạn không có quyền quản lý "
                "kiến thức chatbot."
            ),
        )


def current_admin_id():
    return int(g.account["id"])


# ==========================================================
# 03. KIỂM TRA ĐỘ DÀI CỘT SQL
#
# Không giả định TieuDe hoặc NoiDung có
# độ dài cố định.
# ==========================================================

def get_column_length(cursor, column_name):

    cursor.execute(
        """
        SELECT CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = 'KhoKienThuc'
          AND COLUMN_NAME = ?
        """,
        column_name,
    )

    row = cursor.fetchone()

    if row is None or row[0] is None:
        return None

    return int(row[0])


# ==========================================================
# 04. KIỂM TRA DỮ LIỆU FORM
# ==========================================================

def validate_knowledge_form(cursor):

    title = (
        request.form.get("tieu_de") or ""
    ).strip()

    content = (
        request.form.get("noi_dung") or ""
    ).strip()

    level_text = (
        request.form.get("ma_cap_do") or ""
    ).strip()

    if not title:
        raise ValueError(
            "Bạn chưa nhập tiêu đề kiến thức."
        )

    if not content:
        raise ValueError(
            "Bạn chưa nhập nội dung kiến thức."
        )

    title_length = get_column_length(
        cursor, "TieuDe"
    )

    content_length = get_column_length(
        cursor, "NoiDung"
    )

    if (
        len(title) > 200
        or (
            title_length is not None
            and title_length > 0
            and len(title) > title_length
        )
    ):
        raise ValueError(
            "Tiêu đề vượt quá độ dài cho phép."
        )

    if (
        len(content) > 8000
        or (
            content_length is not None
            and content_length > 0
            and len(content) > content_length
        )
    ):
        raise ValueError(
            "Nội dung vượt quá độ dài cho phép."
        )

    level_id = None

    if level_text:

        try:
            level_id = int(level_text)

        except ValueError as exc:
            raise ValueError(
                "Cấp độ HSK không hợp lệ."
            ) from exc

        cursor.execute(
            """
            SELECT 1
            FROM dbo.CapDoHSK
            WHERE MaCapDo = ?
            """,
            level_id,
        )

        if cursor.fetchone() is None:
            raise ValueError(
                "Cấp độ HSK không tồn tại."
            )

    return title, content, level_id


# ==========================================================
# 05. DANH SÁCH KIẾN THỨC
#
# GET /admin/chatbot/kien-thuc/
# ==========================================================

@admin_chatbot_knowledge_bp.get("/")
def index():

    keyword = (
        request.args.get("q") or ""
    ).strip()[:100]

    status = (
        request.args.get("status") or "all"
    ).strip()

    if status not in {
        "all",
        "approved",
        "pending",
        "inactive",
    }:
        status = "all"

    try:

        with closing(get_connection()) as conn:

            with closing(conn.cursor()) as cursor:

                # ------------------------------------------
                # THỐNG KÊ KHO KIẾN THỨC
                # ------------------------------------------

                cursor.execute(
                    """
                    SELECT
                        (
                            SELECT COUNT(*)
                            FROM dbo.KhoKienThuc
                        ),
                        (
                            SELECT COUNT(*)
                            FROM dbo.KhoKienThuc
                            WHERE DaDuyet = 1
                              AND DangHoatDong = 1
                        ),
                        (
                            SELECT COUNT(*)
                            FROM dbo.KhoKienThuc
                            WHERE DaDuyet = 0
                        ),
                        (
                            SELECT COUNT(*)
                            FROM dbo.KhoKienThuc
                            WHERE DangHoatDong = 0
                        )
                    """
                )

                row = cursor.fetchone()

                counts = {
                    "total": int(row[0]),
                    "approved": int(row[1]),
                    "pending": int(row[2]),
                    "inactive": int(row[3]),
                }

                # ------------------------------------------
                # LẤY DANH SÁCH
                # ------------------------------------------

                cursor.execute(
                    """
                    SELECT TOP (100)
                        MaKienThuc,
                        TieuDe,
                        NoiDung,
                        MaCapDo,
                        DaDuyet,
                        DangHoatDong,
                        NgayCapNhat
                    FROM dbo.KhoKienThuc
                    WHERE
                        (
                            ? = ''
                            OR TieuDe LIKE '%' + ? + '%'
                            OR NoiDung LIKE '%' + ? + '%'
                        )
                        AND
                        (
                            ? = 'all'
                            OR (
                                ? = 'approved'
                                AND DaDuyet = 1
                                AND DangHoatDong = 1
                            )
                            OR (
                                ? = 'pending'
                                AND DaDuyet = 0
                            )
                            OR (
                                ? = 'inactive'
                                AND DangHoatDong = 0
                            )
                        )
                    ORDER BY
                        NgayCapNhat DESC,
                        MaKienThuc DESC
                    """,
                    keyword,
                    keyword,
                    keyword,
                    status,
                    status,
                    status,
                    status,
                )

                items = []

                for row in cursor.fetchall():

                    items.append({
                        "id": int(row[0]),
                        "title": row[1],
                        "content": row[2],
                        "level": row[3],
                        "approved": bool(row[4]),
                        "active": bool(row[5]),
                        "updated_at": row[6],
                    })

    except (pyodbc.Error, RuntimeError):

        current_app.logger.exception(
            "Lỗi đọc kho kiến thức chatbot"
        )

        abort(
            503,
            description=(
                "Không đọc được kho kiến thức chatbot."
            ),
        )

    return render_template(
        "admin/chatbot_knowledge.html",
        active_page="chatbot_knowledge",
        items=items,
        counts=counts,
        keyword=keyword,
        status=status,
    )


# ==========================================================
# 06. THÊM VÀ SỬA KIẾN THỨC
#
# POST /admin/chatbot/kien-thuc/luu
#
# MaKienThuc KHÔNG tự tăng.
# Khóa bảng khi cấp mã để tránh trùng ID.
#
# Kiến thức mới mặc định CHỜ DUYỆT.
# Nội dung sửa cũng cần duyệt lại.
# ==========================================================

@admin_chatbot_knowledge_bp.post("/luu")
def save():

    raw_id = (
        request.form.get("ma_kien_thuc") or ""
    ).strip()

    try:

        record_id = (
            int(raw_id) if raw_id else None
        )

        if (
            record_id is not None
            and record_id <= 0
        ):
            raise ValueError(
                "Mã kiến thức không hợp lệ."
            )

        with closing(get_connection()) as conn:

            try:

                with closing(conn.cursor()) as cursor:

                    title, content, level_id = (
                        validate_knowledge_form(cursor)
                    )

                    # --------------------------------------
                    # THÊM KIẾN THỨC MỚI
                    # --------------------------------------

                    
                    # --------------------------------------
                    # THÊM KIẾN THỨC MỚI
                    #
                    # MaKienThuc được SQL Server tự cấp.
                    # Không tự tính MAX(MaKienThuc) + 1.
                    # Không bật IDENTITY_INSERT.
                    #
                    # Kiến thức mới mặc định chờ duyệt.
                    # --------------------------------------

                    if record_id is None:

                        cursor.execute(
                            """
                            INSERT INTO dbo.KhoKienThuc
                            (
                                TieuDe,
                                NoiDung,
                                MaCapDo,
                                MaBaiHoc,
                                MaNguon,
                                DaDuyet,
                                DangHoatDong,
                                NgayCapNhat,
                                MaQuanTriVienCapNhat
                            )
                            VALUES
                            (
                                ?, ?, ?,
                                NULL, NULL,
                                0, 1,
                                SYSUTCDATETIME(), ?
                            )
                            """,
                            title,
                            content,
                            level_id,
                            current_admin_id(),
                        )

                        message = (
                            "Đã thêm kiến thức mới. "
                            "Nội dung đang chờ duyệt."
                        )

                    # --------------------------------------
                    # SỬA KIẾN THỨC
                    # --------------------------------------

                    else:


                        cursor.execute(
                            """
                            UPDATE dbo.KhoKienThuc
                            SET
                                TieuDe = ?,
                                NoiDung = ?,
                                MaCapDo = ?,
                                DaDuyet = 0,
                                NgayCapNhat =
                                    SYSUTCDATETIME(),
                                MaQuanTriVienCapNhat = ?
                            WHERE MaKienThuc = ?
                            """,
                            title,
                            content,
                            level_id,
                            current_admin_id(),
                            record_id,
                        )

                        if cursor.rowcount == 0:
                            raise ValueError(
                                "Không tìm thấy kiến thức cần sửa."
                            )

                        message = (
                            "Đã sửa nội dung. "
                            "Kiến thức cần được duyệt lại."
                        )

                conn.commit()

            except Exception:

                conn.rollback()
                raise

    except (ValueError, TypeError) as exc:

        flash(
            str(exc),
            "error",
        )

    except (pyodbc.Error, RuntimeError):

        current_app.logger.exception(
            "Lỗi lưu kiến thức chatbot"
        )

        flash(
            "Không thể lưu kiến thức chatbot.",
            "error",
        )

    else:

        flash(
            message,
            "success",
        )

    return redirect(
        url_for("admin_chatbot_knowledge.index")
    )


# ==========================================================
# 07. DUYỆT / BỎ DUYỆT / BẬT / TẮT
#
# POST /admin/chatbot/kien-thuc/<id>/trang-thai
#
# Không xóa dữ liệu.
# Chỉ thay đổi các cột trạng thái.
# ==========================================================

@admin_chatbot_knowledge_bp.post(
    "/<int:knowledge_id>/trang-thai"
)
def change_status(knowledge_id):

    action = (
        request.form.get("action") or ""
    ).strip()

    allowed_actions = {
        "approve": ("DaDuyet", 1),
        "unapprove": ("DaDuyet", 0),
        "enable": ("DangHoatDong", 1),
        "disable": ("DangHoatDong", 0),
    }

    if action not in allowed_actions:

        abort(
            400,
            description="Thao tác không hợp lệ.",
        )

    column, value = allowed_actions[action]

    try:

        with closing(get_connection()) as conn:

            try:

                with closing(conn.cursor()) as cursor:

                    # Tên cột chỉ lấy từ danh sách
                    # allowed_actions cố định.
                    # Không lấy tên cột tùy ý từ form.

                    cursor.execute(
                        f"""
                        UPDATE dbo.KhoKienThuc
                        SET
                            {column} = ?,
                            NgayCapNhat =
                                SYSUTCDATETIME(),
                            MaQuanTriVienCapNhat = ?
                        WHERE MaKienThuc = ?
                        """,
                        value,
                        current_admin_id(),
                        knowledge_id,
                    )

                    if cursor.rowcount == 0:
                        raise ValueError(
                            "Không tìm thấy kiến thức."
                        )

                conn.commit()

            except Exception:

                conn.rollback()
                raise

    except ValueError as exc:

        flash(str(exc), "error")

    except (pyodbc.Error, RuntimeError):

        current_app.logger.exception(
            "Lỗi cập nhật trạng thái kiến thức"
        )

        flash(
            "Không thể cập nhật trạng thái.",
            "error",
        )

    else:

        flash(
            "Đã cập nhật trạng thái kiến thức.",
            "success",
        )

    return redirect(
        url_for("admin_chatbot_knowledge.index")
    )
