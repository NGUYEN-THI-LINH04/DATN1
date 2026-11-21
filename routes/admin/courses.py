import re
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


admin_courses_bp = Blueprint(
    "admin_courses",
    __name__,
    url_prefix="/admin/khoa-hoc",
)


STATUSES = {
    "ban_nhap": "Bản nháp",
    "da_xuat_ban": "Đã xuất bản",
    "luu_tru": "Lưu trữ",
}


# =========================================================
# KIỂM TRA QUYỀN ADMIN
# =========================================================

@admin_courses_bp.before_request
def require_admin():
    account = getattr(g, "account", None)

    if account is None:
        return redirect(url_for("auth.admin_login"))

    if account["role"] != "admin":
        abort(
            403,
            description="Bạn không có quyền quản lý khóa học."
        )


# =========================================================
# XỬ LÝ LỖI DATABASE
# =========================================================

@admin_courses_bp.errorhandler(pyodbc.Error)
def handle_database_error(error):
    # Không đưa thông tin kết nối hoặc câu SQL ra trình duyệt.
    current_app.logger.error(
        "Loi SQL trong quan ly khoa hoc: %s",
        type(error).__name__,
    )

    return (
        "Chưa thể xử lý dữ liệu khóa học. "
        "Vui lòng thử lại.",
        503
    )


# =========================================================
# LẤY DANH SÁCH CẤP ĐỘ HSK
# =========================================================

def get_levels():
    """
    Giai đoạn hiện tại chỉ chọn HSK1–HSK4 đang mở.
    """

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    MaCapDo,
                    TieuDe
                FROM dbo.CapDoHSK
                WHERE MaCapDo BETWEEN 1 AND 4
                  AND DaMo = 1
                ORDER BY MaCapDo;
                """
            )

            return [
                {
                    "id": row[0],
                    "title": row[1],
                }
                for row in cursor.fetchall()
            ]


# =========================================================
# LẤY CHI TIẾT 1 KHÓA HỌC
# =========================================================

def get_course(course_id):
    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    MaKhoaHoc,
                    MaCapDo,
                    MaKyHieu,
                    TieuDe,
                    MoTa,
                    PhienBanChuanHSK,
                    TrangThai
                FROM dbo.KhoaHoc
                WHERE MaKhoaHoc = ?;
                """,
                (course_id,),
            )

            row = cursor.fetchone()

    if row is None:
        abort(
            404,
            description="Không tìm thấy khóa học."
        )

    return {
        "id": row[0],
        "level": row[1],
        "code": row[2],
        "title": row[3],
        "description": row[4] or "",
        "version": row[5] or "",
        "status": row[6],
    }


# =========================================================
# DANH SÁCH KHÓA HỌC
# =========================================================

@admin_courses_bp.get("/")
def index():
    keyword = request.args.get(
        "q",
        ""
    ).strip()[:200]

    selected_status = request.args.get(
        "status",
        ""
    )

    selected_level = request.args.get(
        "level",
        ""
    )

    # Kiểm tra trạng thái.
    if selected_status not in STATUSES:
        selected_status = ""

    # Hiện tại chỉ dùng HSK1–HSK4.
    if selected_level not in {
        "1",
        "2",
        "3",
        "4",
    }:
        selected_level = ""

    conditions = []
    params = []

    # Tìm kiếm theo tiêu đề hoặc mã khóa học.
    if keyword:
        conditions.append(
            "(CHARINDEX(?, k.TieuDe) > 0 "
            "OR CHARINDEX(?, k.MaKyHieu) > 0)"
        )

        params.extend([
            keyword,
            keyword,
        ])

    # Lọc theo trạng thái.
    if selected_status:
        conditions.append(
            "k.TrangThai = ?"
        )

        params.append(
            selected_status
        )

    # Lọc theo cấp độ.
    if selected_level:
        conditions.append(
            "k.MaCapDo = ?"
        )

        params.append(
            int(selected_level)
        )

    where_sql = ""

    if conditions:
        where_sql = (
            " WHERE "
            + " AND ".join(conditions)
        )

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    k.MaKhoaHoc,
                    k.MaKyHieu,
                    k.TieuDe,
                    c.TieuDe,
                    k.TrangThai
                FROM dbo.KhoaHoc AS k
                INNER JOIN dbo.CapDoHSK AS c
                    ON c.MaCapDo = k.MaCapDo
                """
                + where_sql
                + """
                ORDER BY
                    k.MaCapDo,
                    k.MaKhoaHoc DESC;
                """,
                tuple(params),
            )

            courses = [
                {
                    "id": row[0],
                    "code": row[1],
                    "title": row[2],
                    "level_title": row[3],
                    "status": row[4],
                }
                for row in cursor.fetchall()
            ]

    return render_template(
        "admin/courses.html",
        active_page="courses",
        courses=courses,
        statuses=STATUSES,
        keyword=keyword,
        selected_status=selected_status,
        selected_level=selected_level,
    )


# =========================================================
# THÊM / SỬA KHÓA HỌC
# =========================================================

@admin_courses_bp.route(
    "/them",
    methods=["GET", "POST"],
)
@admin_courses_bp.route(
    "/<int:course_id>/sua",
    methods=["GET", "POST"],
)
def edit(course_id=None):
    levels = get_levels()

    # =====================================================
    # DỮ LIỆU BAN ĐẦU
    # =====================================================

    if course_id is None:
        course = {
            "id": None,
            "level": "",
            "code": "",
            "title": "",
            "description": "",
            "version": "",
            "status": "ban_nhap",
        }

    else:
        course = get_course(
            course_id
        )

    # =====================================================
    # HÀM HIỂN THỊ FORM
    # =====================================================

    def show_form(status_code=200):
        return render_template(
            "admin/course_form.html",
            active_page="courses",
            course=course,
            levels=levels,
            statuses=STATUSES,
        ), status_code

    # Nếu là GET thì chỉ hiển thị form.
    if request.method == "GET":
        return show_form()

    # =====================================================
    # LẤY DỮ LIỆU TỪ FORM
    # =====================================================

    course.update(
        {
            "level": request.form.get(
                "level",
                type=int,
            ),
            "code": request.form.get(
                "code",
                "",
            ).strip(),
            "title": request.form.get(
                "title",
                "",
            ).strip(),
            "description": request.form.get(
                "description",
                "",
            ).strip(),
            "version": request.form.get(
                "version",
                "",
            ).strip(),
            "status": request.form.get(
                "status",
                "",
            ),
        }
    )

    # =====================================================
    # KIỂM TRA DỮ LIỆU
    # =====================================================

    error = None

    allowed_levels = {
        level["id"]
        for level in levels
    }

    if course["level"] not in allowed_levels:
        error = (
            "Hãy chọn cấp độ HSK1–HSK4 "
            "đang được mở."
        )

    elif re.fullmatch(
        r"[A-Za-z0-9_-]{1,40}",
        course["code"],
    ) is None:
        error = (
            "Mã khóa học cần 1–40 ký tự, "
            "chỉ gồm chữ không dấu, số, "
            "gạch dưới hoặc gạch ngang."
        )

    elif not 1 <= len(
        course["title"]
    ) <= 200:
        error = (
            "Tên khóa học cần từ "
            "1 đến 200 ký tự."
        )

    elif len(
        course["version"]
    ) > 100:
        error = (
            "Phiên bản chuẩn HSK "
            "không được quá 100 ký tự."
        )

    elif len(
        course["description"]
    ) > 20000:
        error = (
            "Mô tả không được quá "
            "20.000 ký tự."
        )

    elif course["status"] not in STATUSES:
        error = (
            "Trạng thái khóa học "
            "không hợp lệ."
        )

    if error:
        flash(
            error,
            "error",
        )

        return show_form(400)

    # =====================================================
    # LẤY ADMIN ĐANG ĐĂNG NHẬP
    # =====================================================

    admin_id = int(
        g.account["id"]
    )

    # =====================================================
    # DỮ LIỆU DÙNG CHUNG
    # =====================================================

    values = (
        course["level"],
        course["code"],
        course["title"],
        course["description"] or None,
        course["version"] or None,
        course["status"],
    )

    # =====================================================
    # GHI DỮ LIỆU VÀO SQL SERVER
    # =====================================================

    try:
        with closing(
            get_connection()
        ) as connection:

            with closing(
                connection.cursor()
            ) as cursor:

                # =========================================
                # THÊM KHÓA HỌC MỚI
                # =========================================

                if course_id is None:

                    cursor.execute(
                        """
                        INSERT INTO dbo.KhoaHoc
                        (
                            MaCapDo,
                            MaKyHieu,
                            TieuDe,
                            MoTa,
                            PhienBanChuanHSK,
                            TrangThai,
                            MaQuanTriVienCapNhat,
                            NgayCapNhat
                        )
                        VALUES
                        (
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            SYSUTCDATETIME()
                        );
                        """,
                        values + (
                            admin_id,
                        ),
                    )

                # =========================================
                # CẬP NHẬT KHÓA HỌC
                # =========================================

                else:

                    cursor.execute(
                        """
                        UPDATE dbo.KhoaHoc
                        SET
                            MaCapDo = ?,
                            MaKyHieu = ?,
                            TieuDe = ?,
                            MoTa = ?,
                            PhienBanChuanHSK = ?,
                            TrangThai = ?,
                            MaQuanTriVienCapNhat = ?,
                            NgayCapNhat =
                                SYSDATETIME()

                        OUTPUT
                            INSERTED.MaKhoaHoc

                        WHERE
                            MaKhoaHoc = ?;
                        """,
                        values
                        + (
                            admin_id,
                            course_id,
                        ),
                    )

                    updated = (
                        cursor.fetchone()
                    )

                    if updated is None:
                        abort(
                            404,
                            description=(
                                "Khóa học "
                                "không còn tồn tại."
                            ),
                        )

            # Ghi dữ liệu thật.
            connection.commit()

    # =====================================================
    # TRÙNG DỮ LIỆU / VI PHẠM RÀNG BUỘC
    # =====================================================

    except pyodbc.IntegrityError:

        flash(
            (
                "Không lưu được: "
                "mã khóa học có thể đã trùng "
                "hoặc dữ liệu không còn phù hợp "
                "với ràng buộc SQL."
            ),
            "error",
        )

        return show_form(409)

    # =====================================================
    # THÔNG BÁO THÀNH CÔNG
    # =====================================================

    flash(
        (
            "Đã thêm khóa học."
            if course_id is None
            else "Đã cập nhật khóa học."
        ),
        "success",
    )

    return redirect(
        url_for(
            "admin_courses.index"
        )
    )


# =========================================================
# XÓA KHÓA HỌC
#
# Chỉ cho xóa khi:
# - chưa có bài học
# - chưa có người học đăng ký
#
# Nếu đã phát sinh dữ liệu:
# dùng trạng thái "luu_tru" thay vì DELETE.
# =========================================================

@admin_courses_bp.post(
    "/<int:course_id>/xoa"
)
def delete(course_id):

    try:

        with closing(
            get_connection()
        ) as connection:

            with closing(
                connection.cursor()
            ) as cursor:

                # =========================================
                # 1. KIỂM TRA KHÓA HỌC TỒN TẠI
                # =========================================

                cursor.execute(
                    """
                    SELECT
                        MaKhoaHoc,
                        TieuDe,
                        TrangThai
                    FROM dbo.KhoaHoc
                    WHERE MaKhoaHoc = ?;
                    """,
                    (
                        course_id,
                    ),
                )

                course = (
                    cursor.fetchone()
                )

                if course is None:

                    abort(
                        404,
                        description=(
                            "Không tìm thấy "
                            "khóa học."
                        ),
                    )

                # =========================================
                # 2. ĐẾM SỐ BÀI HỌC
                # =========================================

                cursor.execute(
                    """
                    SELECT
                        COUNT(*)
                    FROM dbo.BaiHoc
                    WHERE MaKhoaHoc = ?;
                    """,
                    (
                        course_id,
                    ),
                )

                lesson_count = int(
                    cursor.fetchone()[0]
                    or 0
                )

                # =========================================
                # 3. ĐẾM NGƯỜI HỌC ĐÃ ĐĂNG KÝ
                # =========================================

                cursor.execute(
                    """
                    SELECT
                        COUNT(*)
                    FROM dbo.DangKyKhoaHoc
                    WHERE MaKhoaHoc = ?;
                    """,
                    (
                        course_id,
                    ),
                )

                enrollment_count = int(
                    cursor.fetchone()[0]
                    or 0
                )

                # =========================================
                # 4. KHÔNG CHO XÓA NẾU ĐÃ CÓ DỮ LIỆU
                # =========================================

                if (
                    lesson_count > 0
                    or enrollment_count > 0
                ):

                    flash(
                        (
                            f"Không thể xóa khóa "
                            f"“{course[1]}”. "
                            f"Khóa hiện có "
                            f"{lesson_count} bài học "
                            f"và "
                            f"{enrollment_count} "
                            f"lượt đăng ký. "
                            f"Hãy chuyển khóa sang "
                            f"trạng thái “Lưu trữ” "
                            f"nếu không muốn "
                            f"hiển thị cho người học."
                        ),
                        "error",
                    )

                    return redirect(
                        url_for(
                            "admin_courses.index"
                        )
                    )

                # =========================================
                # 5. XÓA KHÓA HỌC
                # =========================================

                cursor.execute(
                    """
                    DELETE FROM dbo.KhoaHoc

                    OUTPUT
                        DELETED.MaKhoaHoc

                    WHERE
                        MaKhoaHoc = ?;
                    """,
                    (
                        course_id,
                    ),
                )

                deleted = (
                    cursor.fetchone()
                )

                if deleted is None:

                    abort(
                        404,
                        description=(
                            "Khóa học "
                            "không còn tồn tại."
                        ),
                    )

            # =============================================
            # GHI THẬT VÀO SQL SERVER
            # =============================================

            connection.commit()

    except pyodbc.IntegrityError:

        flash(
            (
                "Không thể xóa khóa học vì "
                "vẫn còn dữ liệu liên kết "
                "trong hệ thống."
            ),
            "error",
        )

    else:

        flash(
            (
                f"Đã xóa khóa học "
                f"“{course[1]}”."
            ),
            "success",
        )

    return redirect(
        url_for(
            "admin_courses.index"
        )
    )