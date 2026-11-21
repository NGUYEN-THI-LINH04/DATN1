
# -*- coding: utf-8 -*-
"""
MOC HAN - HO SO CA NHAN NGUOI HOC

Chuc nang:
- Hien thi thong tin tai khoan dang nhap.
- Cap nhat ho ten va email.
- Khong cho sua ten dang nhap.
- Khong thay doi mat khau.
- Giu nguyen lich su hoc va luyen thi.

SQL Server:
    dbo.NguoiDung

Khong tao bang SQL moi.
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
from routes.auth import valid_email


# =====================================================
# 1. BLUEPRINT
# =====================================================

profile_bp = Blueprint(
    "profile",
    __name__,
    url_prefix="/tai-khoan/ho-so"
)


# =====================================================
# 2. KIEM TRA QUYEN NGUOI HOC
# =====================================================

@profile_bp.before_request
def require_student():

    account = getattr(g, "account", None)

    if account is None:
        return redirect(
            url_for("auth.login")
        )

    if account.get("role") != "student":
        abort(403)


# =====================================================
# 3. THONG TIN HO SO HIEN TAI
# =====================================================

def get_profile(account):

    return {
        "username": account.get("username") or "",
        "full_name": account.get("full_name") or "",
        "email": account.get("email") or "",
    }


# =====================================================
# 4. TRANG HO SO CA NHAN
# =====================================================

@profile_bp.route(
    "/",
    methods=["GET", "POST"]
)
def index():

    account = g.account

    user_id = int(account["id"])

    profile = get_profile(account)

    # ================================================
    # 5. HIEN THI HO SO
    # ================================================

    if request.method == "GET":

        return render_template(
            "student/profile.html",
            profile=profile
        )

    # ================================================
    # 6. NHAN DU LIEU CAP NHAT
    # ================================================

    full_name = request.form.get(
        "full_name", ""
    ).strip()

    email = request.form.get(
        "email", ""
    ).strip().lower()

    profile["full_name"] = full_name
    profile["email"] = email

    # ================================================
    # 7. KIEM TRA HO TEN
    # ================================================

    if not 2 <= len(full_name) <= 150:

        flash(
            "Họ và tên phải có từ 2 đến 150 ký tự.",
            "error"
        )

        return render_template(
            "student/profile.html",
            profile=profile
        ), 400

    # ================================================
    # 8. KIEM TRA EMAIL
    # ================================================

    if not valid_email(email):

        flash(
            "Email không hợp lệ hoặc quá dài.",
            "error"
        )

        return render_template(
            "student/profile.html",
            profile=profile
        ), 400

    # ================================================
    # 9. CAP NHAT SQL SERVER
    # ================================================

    try:

        with closing(get_connection()) as conn:

            with closing(conn.cursor()) as cursor:

                # Kiem tra tai khoan con hoat dong.
                cursor.execute(
                    """
                    SELECT MaNguoiDung
                    FROM dbo.NguoiDung
                    WHERE MaNguoiDung = ?
                      AND DangHoatDong = 1
                    """,
                    user_id
                )

                if cursor.fetchone() is None:

                    raise RuntimeError(
                        "Tai khoan khong con hoat dong"
                    )

                # ====================================
                # 10. KIEM TRA EMAIL TRUNG
                # ====================================

                cursor.execute(
                    """
                    SELECT TOP (1)
                        MaNguoiDung
                    FROM dbo.NguoiDung
                    WHERE ThuDienTu = ?
                      AND MaNguoiDung <> ?
                    """,
                    email,
                    user_id
                )

                if cursor.fetchone() is not None:

                    flash(
                        "Email này đã được sử dụng "
                        "bởi tài khoản khác.",
                        "error"
                    )

                    return render_template(
                        "student/profile.html",
                        profile=profile
                    ), 409

                # ====================================
                # 11. LUU THONG TIN
                # ====================================

                cursor.execute(
                    """
                    UPDATE dbo.NguoiDung
                    SET
                        HoTen = ?,
                        ThuDienTu = ?
                    WHERE MaNguoiDung = ?
                      AND DangHoatDong = 1
                    """,
                    full_name,
                    email,
                    user_id
                )

                # Kiem tra so ban ghi duoc sua.
                cursor.execute(
                    "SELECT @@ROWCOUNT"
                )

                changed = int(
                    cursor.fetchone()[0]
                )

                if changed != 1:

                    raise RuntimeError(
                        "Khong cap nhat duoc tai khoan"
                    )

            conn.commit()

    # ================================================
    # 12. EMAIL TRUNG TRONG SQL
    # ================================================

    except pyodbc.IntegrityError:

        flash(
            "Email đã tồn tại trong hệ thống.",
            "error"
        )

        return render_template(
            "student/profile.html",
            profile=profile
        ), 409

    # ================================================
    # 13. LOI KET NOI HOAC CAP NHAT
    # ================================================

    except (pyodbc.Error, RuntimeError):

        current_app.logger.exception(
            "Loi cap nhat ho so nguoi hoc"
        )

        flash(
            "Không thể cập nhật hồ sơ. "
            "Bạn hãy thử lại.",
            "error"
        )

        return render_template(
            "student/profile.html",
            profile=profile
        ), 503

    # ================================================
    # 14. CAP NHAT THANH CONG
    # ================================================

    flash(
        "Cập nhật hồ sơ thành công.",
        "success"
    )

    return redirect(
        url_for("profile.index")
    )
