from contextlib import closing
from datetime import timedelta

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


admin_users_bp = Blueprint(
    "admin_users",
    __name__,
    url_prefix="/admin/nguoi-hoc",
)


@admin_users_bp.before_request
def require_admin():
    account = getattr(g, "account", None)

    if account is None:
        return redirect(url_for("auth.admin_login"))

    if account["role"] != "admin":
        abort(403, description="Bạn không có quyền quản lý người học.")


@admin_users_bp.get("/")
def index():
    keyword = request.args.get("q", "").strip()[:150]
    status = request.args.get("status", "all")

    if status not in {"all", "active", "locked"}:
        status = "all"

    page = max(request.args.get("page", 1, type=int), 1)
    page_size = 20

    conditions = []
    params = []

    if keyword:
        # CHARINDEX tìm chuỗi trực tiếp.
        # Các ký tự %, _ không được hiểu thành ký tự đại diện.
        conditions.append(
            """
            (
                CHARINDEX(?, TenDangNhap) > 0
                OR CHARINDEX(?, HoTen) > 0
                OR CHARINDEX(?, ThuDienTu) > 0
            )
            """
        )
        params.extend([keyword, keyword, keyword])

    if status == "active":
        conditions.append("DangHoatDong = ?")
        params.append(1)
    elif status == "locked":
        conditions.append("DangHoatDong = ?")
        params.append(0)

    where_sql = ""

    if conditions:
        where_sql = " WHERE " + " AND ".join(conditions)

    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM dbo.NguoiDung" + where_sql,
                    tuple(params),
                )
                total = cursor.fetchone()[0]

                total_pages = max(
                    (total + page_size - 1) // page_size,
                    1,
                )
                page = min(page, total_pages)
                offset = (page - 1) * page_size

                cursor.execute(
                    """
                    SELECT
                        MaNguoiDung,
                        TenDangNhap,
                        HoTen,
                        ThuDienTu,
                        DangHoatDong,
                        NgayTao
                    FROM dbo.NguoiDung
                    """
                    + where_sql
                    + """
                    ORDER BY MaNguoiDung DESC
                    OFFSET ? ROWS
                    FETCH NEXT ? ROWS ONLY;
                    """,
                    tuple(params + [offset, page_size]),
                )

                rows = cursor.fetchall()

    except pyodbc.Error:
        current_app.logger.error("Loi SQL khi doc danh sach nguoi hoc.")
        abort(
            503,
            description="Chưa thể tải danh sách người học. Hãy thử lại.",
        )

    users = []

    for row in rows:
        # NgayTao trong SQL được lưu theo UTC.
        # Chuyển sang UTC+7 để hiển thị giờ Việt Nam.
        created_at = row[5] + timedelta(hours=7)

        users.append(
            {
                "id": row[0],
                "username": row[1],
                "full_name": row[2],
                "email": row[3],
                "active": bool(row[4]),
                "created_at": created_at.strftime("%d/%m/%Y %H:%M"),
            }
        )

    return render_template(
        "admin/users.html",
        active_page="users",
        users=users,
        keyword=keyword,
        status=status,
        total=total,
        page=page,
        total_pages=total_pages,
    )


@admin_users_bp.post("/<int:user_id>/trang-thai")
def set_status(user_id):
    requested_status = request.form.get("active")

    if requested_status not in {"0", "1"}:
        abort(400, description="Trạng thái tài khoản không hợp lệ.")

    active = int(requested_status)

    keyword = request.form.get("q", "").strip()[:150]
    status = request.form.get("status", "all")
    page = max(request.form.get("page", 1, type=int), 1)

    if status not in {"all", "", "active", "locked"}:
        status = "all"

    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(
                    """
                    UPDATE dbo.NguoiDung
                    SET DangHoatDong = ?
                    OUTPUT INSERTED.MaNguoiDung
                    WHERE MaNguoiDung = ?;
                    """,
                    (active, user_id),
                )

                updated = cursor.fetchone()

                if updated is None:
                    abort(404, description="Không tìm thấy người học.")

            connection.commit()

    except pyodbc.Error:
        current_app.logger.error("Loi SQL khi doi trang thai nguoi hoc.")
        flash(
            "Chưa thể cập nhật trạng thái. Bạn hãy thử lại.",
            "error",
        )
    else:
        if active:
            flash("Đã mở khóa tài khoản người học.", "success")
        else:
            flash("Đã khóa tài khoản người học.", "success")

    return redirect(
        url_for(
            "admin_users.index",
            q=keyword,
            status=status,
            page=page,
        )
    )