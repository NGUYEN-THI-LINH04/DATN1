import re
from contextlib import closing
import hashlib
import secrets
import smtplib

from mail_service import send_reset_email
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
    session,
    url_for,
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from database import get_connection


auth_bp = Blueprint("auth", __name__)

USERNAME_PATTERN = re.compile(r"[A-Za-z0-9_.-]{3,50}")
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")

# Tên bảng và tên khóa chính chỉ lấy từ cấu hình cố định này.
ACCOUNT_TABLES = {
    "student": ("NguoiDung", "MaNguoiDung"),
    "admin": ("QuanTriVien", "MaQuanTriVien"),
}


def valid_email(value):
    return (
        len(value) <= 254
        and EMAIL_PATTERN.fullmatch(value) is not None
    )


def find_account(role, username=None, account_id=None):
    table, id_column = ACCOUNT_TABLES[role]

    if account_id is not None:
        condition = f"[{id_column}] = ?"
        parameter = account_id
    else:
        condition = "[TenDangNhap] = ?"
        parameter = username

    sql = f"""
        SELECT
            [{id_column}],
            [TenDangNhap],
            [ThuDienTu],
            [MatKhauBam],
            [HoTen],
            [DangHoatDong]
        FROM dbo.[{table}]
        WHERE {condition};
    """

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql, (parameter,))
            row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "password_hash": row[3],
        "full_name": row[4],
        "active": bool(row[5]),
        "role": role,
    }


def password_matches(stored_hash, password):
    try:
        return check_password_hash(stored_hash, password)
    except (ValueError, TypeError):
        return False


@auth_bp.before_app_request
def load_account_and_protect_admin():
    """Đọc tài khoản hiện tại và bảo vệ khu vực admin."""
    g.account = None

    if request.endpoint == "static":
        return None

    account_id = session.get("account_id")
    role = session.get("role")

    if account_id is not None and role in ACCOUNT_TABLES:
        try:
            account = find_account(role, account_id=account_id)
        except pyodbc.Error:
            current_app.logger.error(
                "Khong the doc tai khoan tu SQL Server."
            )
            abort(503, description="Database tạm thời không truy cập được.")

        if account is not None and account["active"]:
            current_stamp = hashlib.sha256(
                account["password_hash"].encode("utf-8")
            ).hexdigest()

            if session.get("password_stamp") == current_stamp:
                g.account = account
            else:
                session.clear()
        else:
            session.clear()

    # Chuyển các đường dẫn đăng nhập mẫu cũ sang chức năng thật.
    if request.endpoint == "preview.show":
        group = (request.view_args or {}).get("group")
        page = (request.view_args or {}).get("page")

        if group == "auth":
            destinations = {
                "login": "auth.login",
                "register": "auth.register",
                "admin_login": "auth.admin_login",
                "forgot_password": "auth.forgot_password",
                "reset_password": "auth.forgot_password",
            }

            if page in destinations:
                return redirect(url_for(destinations[page]))

        is_admin_page = group == "admin"
    else:
        # Dùng khi các Blueprint admin được triển khai sau này.
        blueprint_name = request.blueprint or ""
        is_admin_page = (
            blueprint_name == "admin"
            or blueprint_name.startswith("admin.")
            or blueprint_name.startswith("admin_")
        )

    if is_admin_page:
        if g.account is None:
            flash("Bạn cần đăng nhập admin trước.", "error")
            return redirect(url_for("auth.admin_login"))

        if g.account["role"] != "admin":
            abort(403, description="Bạn không có quyền truy cập trang admin.")

    return None


@auth_bp.route("/dang-ky", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        error = None

        if not 2 <= len(full_name) <= 150:
            error = "Họ tên cần từ 2 đến 150 ký tự."
        elif USERNAME_PATTERN.fullmatch(username) is None:
            error = (
                "Tên đăng nhập cần từ 3 đến 50 ký tự, "
                "chỉ gồm chữ không dấu, số, dấu chấm, gạch dưới hoặc gạch ngang."
            )
        elif not valid_email(email):
            error = "Email không hợp lệ hoặc dài quá 254 ký tự."
        elif not 8 <= len(password) <= 128:
            error = "Mật khẩu cần từ 8 đến 128 ký tự."
        elif password != confirm_password:
            error = "Mật khẩu nhập lại không khớp."

        if error is not None:
            flash(error, "error")
            return render_template("auth/register.html"), 400

        password_hash = generate_password_hash(password)

        try:
            with closing(get_connection()) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(
                        """
                        INSERT INTO dbo.NguoiDung
                            (
                                TenDangNhap,
                                ThuDienTu,
                                MatKhauBam,
                                HoTen
                            )
                        VALUES (?, ?, ?, ?);
                        """,
                        (
                            username,
                            email,
                            password_hash,
                            full_name,
                        ),
                    )

                connection.commit()

        except pyodbc.IntegrityError:
            flash(
                "Tên đăng nhập hoặc email đã được sử dụng.",
                "error",
            )
            return render_template("auth/register.html"), 409

        except pyodbc.Error:
            current_app.logger.error("Loi SQL khi dang ky nguoi hoc.")
            flash(
                "Chưa thể tạo tài khoản. Bạn thử lại sau nhé.",
                "error",
            )
            return render_template("auth/register.html"), 503

        flash("Đăng ký thành công. Bạn hãy đăng nhập.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


def handle_login(role, template):
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or len(username) > 50 or not 1 <= len(password) <= 128:
            flash("Tên đăng nhập hoặc mật khẩu không đúng.", "error")
            return render_template(template), 400

        try:
            account = find_account(role, username=username)
        except pyodbc.Error:
            current_app.logger.error("Loi SQL khi dang nhap.")
            flash("Chưa thể đăng nhập. Bạn thử lại sau nhé.", "error")
            return render_template(template), 503

        if (
            account is None
            or not account["active"]
            or not password_matches(account["password_hash"], password)
        ):
            flash("Tên đăng nhập hoặc mật khẩu không đúng.", "error")
            return render_template(template), 401

        # Xóa phiên cũ trước khi tạo phiên mới.
        session.clear()
        session["account_id"] = account["id"]
        session["role"] = role
        session["password_stamp"] = hashlib.sha256(
            account["password_hash"].encode("utf-8")
        ).hexdigest()
        session.permanent = True

        if role == "admin":

            return redirect(
                url_for(
            "admin_dashboard.index"
        )
    )
        return redirect(url_for("home.index"))

    return render_template(template)


@auth_bp.route("/dang-nhap", methods=["GET", "POST"])
def login():
    return handle_login("student", "auth/login.html")


@auth_bp.route("/admin/dang-nhap", methods=["GET", "POST"])
def admin_login():
    return handle_login("admin", "auth/admin_login.html")


@auth_bp.post("/dang-xuat")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

RESET_REQUEST_MESSAGE = (
    "Nếu email thuộc tài khoản đang hoạt động, hệ thống sẽ gửi "
    "hướng dẫn đặt lại mật khẩu. Bạn hãy kiểm tra hộp thư và thư rác. "
    "Nếu vừa yêu cầu, vui lòng chờ ít nhất 1 phút trước khi thử lại."
)


def reset_token_hash(token):
    """Token gốc nằm trong email; SQL chỉ lưu bản băm 32 byte."""
    if re.fullmatch(r"[A-Za-z0-9_-]{43}", token) is None:
        return None

    return hashlib.sha256(token.encode("utf-8")).digest()


def issue_reset_token(email):
    """Tạo mã với giới hạn 1 lần/phút và tối đa 5 lần/giờ/tài khoản."""
    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            # Khóa hàng tài khoản trong giao dịch để các yêu cầu đồng thời
            # không vượt qua giới hạn tạo mã.
            cursor.execute(
                """
                SELECT MaNguoiDung, ThuDienTu
                FROM dbo.NguoiDung WITH (UPDLOCK, ROWLOCK)
                WHERE ThuDienTu = ?
                  AND DangHoatDong = 1;
                """,
                (email,),
            )
            account = cursor.fetchone()

            if account is None:
                return None

            account_id, recipient = account

            cursor.execute(
                """
                SELECT
                    COUNT(*),
                    COALESCE(
                        SUM(
                            CASE
                                WHEN NgayTao > DATEADD(
                                    SECOND, -60, SYSUTCDATETIME()
                                )
                                THEN 1 ELSE 0
                            END
                        ),
                        0
                    )
                FROM dbo.MaDatLaiMatKhau
                WHERE MaNguoiDung = ?
                  AND NgayTao > DATEADD(HOUR, -1, SYSUTCDATETIME());
                """,
                (account_id,),
            )
            hourly_count, recent_count = cursor.fetchone()

            if hourly_count >= 5 or recent_count > 0:
                return None

            token = secrets.token_urlsafe(32)
            token_hash = reset_token_hash(token)

            cursor.execute(
                """
                INSERT INTO dbo.MaDatLaiMatKhau
                    (
                        MaNguoiDung,
                        MaBaoMatBam,
                        NgayHetHan,
                        NgayTao
                    )
                VALUES
                    (
                        ?,
                        ?,
                        DATEADD(MINUTE, 15, SYSUTCDATETIME()),
                        SYSUTCDATETIME()
                    );
                """,
                (account_id, token_hash),
            )

        connection.commit()

    return recipient, token


def reset_link_is_valid(token_hash):
    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                """
                SELECT TOP (1) m.MaDatLai
                FROM dbo.MaDatLaiMatKhau AS m
                INNER JOIN dbo.NguoiDung AS n
                    ON n.MaNguoiDung = m.MaNguoiDung
                WHERE m.MaBaoMatBam = ?
                  AND m.NgaySuDung IS NULL
                  AND m.NgayHetHan > SYSUTCDATETIME()
                  AND n.DangHoatDong = 1;
                """,
                (token_hash,),
            )

            return cursor.fetchone() is not None


def update_password_with_token(token_hash, password_hash):
    """Đổi mật khẩu và vô hiệu hóa các mã trong cùng một giao dịch."""
    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                """
                SELECT MaNguoiDung
                FROM dbo.MaDatLaiMatKhau
                WHERE MaBaoMatBam = ?;
                """,
                (token_hash,),
            )
            token_row = cursor.fetchone()

            if token_row is None:
                return False

            account_id = token_row[0]

            # Các lần đổi mật khẩu của cùng người học được xử lý tuần tự.
            cursor.execute(
                """
                SELECT MaNguoiDung
                FROM dbo.NguoiDung WITH (UPDLOCK, ROWLOCK)
                WHERE MaNguoiDung = ?
                  AND DangHoatDong = 1;
                """,
                (account_id,),
            )

            if cursor.fetchone() is None:
                return False

            # Kiểm tra lại ngay khi cập nhật:
            # mã phải chưa dùng và vẫn còn hạn.
            cursor.execute(
                """
                UPDATE dbo.MaDatLaiMatKhau
                SET NgaySuDung = SYSUTCDATETIME()
                OUTPUT INSERTED.MaDatLai
                WHERE MaBaoMatBam = ?
                  AND MaNguoiDung = ?
                  AND NgaySuDung IS NULL
                  AND NgayHetHan > SYSUTCDATETIME();
                """,
                (token_hash, account_id),
            )

            if cursor.fetchone() is None:
                return False

            cursor.execute(
                """
                UPDATE dbo.NguoiDung
                SET MatKhauBam = ?
                WHERE MaNguoiDung = ?;
                """,
                (password_hash, account_id),
            )

            # Đổi thành công thì mọi liên kết cũ của người học hết hiệu lực.
            cursor.execute(
                """
                UPDATE dbo.MaDatLaiMatKhau
                SET NgaySuDung = SYSUTCDATETIME()
                WHERE MaNguoiDung = ?
                  AND NgaySuDung IS NULL;
                """,
                (account_id,),
            )

        connection.commit()

    return True


@auth_bp.route("/quen-mat-khau", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not valid_email(email):
            flash("Bạn hãy nhập email hợp lệ.", "error")
            return render_template("auth/forgot_password.html"), 400

        try:
            issued = issue_reset_token(email)

            if issued is not None:
                recipient, token = issued

                # Dùng địa chỉ cấu hình cố định, không lấy tên miền
                # từ thông tin gửi lên của trình duyệt.
                reset_url = (
                    current_app.config["APP_BASE_URL"]
                    + url_for("auth.reset_password", token=token)
                )

                send_reset_email(recipient, reset_url)

        except (
            pyodbc.Error,
            smtplib.SMTPException,
            OSError,
            RuntimeError,
        ) as error:
            # Không ghi mật khẩu, email hay token vào log.
            current_app.logger.error(
                "Khong xu ly duoc yeu cau dat lai mat khau: %s",
                type(error).__name__,
            )

        # Cùng thông báo cho email tồn tại và không tồn tại.
        flash(RESET_REQUEST_MESSAGE, "info")
        return redirect(url_for("auth.forgot_password"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/dat-lai-mat-khau", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token", "")
    token_hash = reset_token_hash(token)

    valid_link = False

    try:
        if token_hash is not None:
            valid_link = reset_link_is_valid(token_hash)
    except pyodbc.Error:
        abort(503, description="Database tạm thời không truy cập được.")

    if not valid_link:
        return render_template(
            "auth/reset_password.html",
            valid_link=False,
            token="",
        ), 400

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        error = None

        if not 8 <= len(password) <= 128:
            error = "Mật khẩu cần từ 8 đến 128 ký tự."
        elif password != confirm_password:
            error = "Mật khẩu nhập lại không khớp."

        if error is not None:
            flash(error, "error")
            return render_template(
                "auth/reset_password.html",
                valid_link=True,
                token=token,
            ), 400

        password_hash = generate_password_hash(password)

        try:
            updated = update_password_with_token(
                token_hash,
                password_hash,
            )
        except pyodbc.Error:
            current_app.logger.error("Loi SQL khi dat lai mat khau.")
            abort(503, description="Chưa thể cập nhật mật khẩu. Hãy thử lại.")

        if not updated:
            return render_template(
                "auth/reset_password.html",
                valid_link=False,
                token="",
            ), 400

        session.clear()
        flash(
            "Đặt lại mật khẩu thành công. Hãy đăng nhập bằng mật khẩu mới.",
            "success",
        )
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/reset_password.html",
        valid_link=True,
        token=token,
    )


@auth_bp.after_app_request
def protect_password_pages(response):
    if request.endpoint in {
        "auth.forgot_password",
        "auth.reset_password",
    }:
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"

    return response