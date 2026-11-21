
from contextlib import closing
from decimal import Decimal, InvalidOperation
from math import ceil
import json

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


# =========================================================
# BLUEPRINT
# =========================================================

admin_exercises_bp = Blueprint(
    "admin_exercises",
    __name__,
    url_prefix="/admin/bai-tap",
)

STATUSES = {
    "ban_nhap": "Bản nháp",
    "da_xuat_ban": "Đã xuất bản",
    "luu_tru": "Lưu trữ",
}

PAGE_SIZE = 20


# =========================================================
# KIỂM TRA QUYỀN ADMIN
# =========================================================

@admin_exercises_bp.before_request
def require_admin():

    account = getattr(g, "account", None)

    if account is None:
        return redirect(
            url_for("auth.admin_login")
        )

    if account["role"] != "admin":
        abort(
            403,
            description="Bạn không có quyền quản lý bài tập.",
        )


@admin_exercises_bp.errorhandler(pyodbc.Error)
def handle_database_error(error):

    current_app.logger.exception(
        "Lỗi SQL trong phần quản lý bài tập"
    )

    return (
        "Chưa thể xử lý dữ liệu bài tập. "
        "Vui lòng kiểm tra kết nối SQL Server.",
        503,
    )


def current_admin_id():

    return int(g.account["id"])


# =========================================================
# GIỮ BỘ LỌC KHI THAO TÁC
#
# Chỉ đọc bộ lọc từ query string.
# Không đọc status trong POST vì đó là trạng thái mới
# của bài tập, không phải trạng thái lọc.
# =========================================================

def index_url(**changes):

    args = {
        key: value
        for key, value in request.args.items()
        if key in {
            "course_id",
            "lesson_id",
            "status",
            "q",
            "page",
        }
        and value
    }

    args.update(changes)

    return url_for(
        "admin_exercises.index",
        **args,
    )


# =========================================================
# ĐỌC VÀ KIỂM TRA FORM
# =========================================================

def parse_exercise_form():

    lesson_id = request.form.get(
        "lesson_id",
        type=int,
    )

    title = request.form.get(
        "title",
        "",
    ).strip()

    instruction = request.form.get(
        "instruction",
        "",
    ).strip()

    raw_minutes = request.form.get(
        "limit_minutes",
        "",
    ).strip()

    raw_percent = request.form.get(
        "pass_percent",
        "70",
    ).strip()

    if not lesson_id:
        raise ValueError(
            "Bạn cần chọn bài học."
        )

    if not title or len(title) > 200:
        raise ValueError(
            "Tên bài tập phải có từ 1 đến 200 ký tự."
        )

    limit_seconds = None

    if raw_minutes:

        try:
            minutes = Decimal(raw_minutes)

        except InvalidOperation:
            raise ValueError(
                "Thời gian giới hạn không hợp lệ."
            )

        if not minutes.is_finite() or minutes <= 0:
            raise ValueError(
                "Thời gian giới hạn phải lớn hơn 0."
            )

        limit_seconds = int(
            minutes * 60 + Decimal("0.5")
        )

        if (
            limit_seconds < 1
            or limit_seconds > 2147483647
        ):
            raise ValueError(
                "Thời gian giới hạn vượt phạm vi cho phép."
            )

    try:
        percent = Decimal(raw_percent)

    except InvalidOperation:
        raise ValueError(
            "Phần trăm đạt không hợp lệ."
        )

    if (
        not percent.is_finite()
        or percent < 0
        or percent > 100
    ):
        raise ValueError(
            "Phần trăm đạt phải từ 0 đến 100."
        )

    if percent.as_tuple().exponent < -2:
        raise ValueError(
            "Phần trăm đạt chỉ được có tối đa "
            "2 chữ số thập phân."
        )

    return {
        "lesson_id": lesson_id,
        "title": title,
        "instruction": instruction or None,
        "limit_seconds": limit_seconds,
        "percent": percent,
    }


# =========================================================
# ĐỌC BỘ LỌC
# =========================================================

def read_filters(source):

    course_id = source.get(
        "course_id",
        type=int,
    )

    lesson_id = source.get(
        "lesson_id",
        type=int,
    )

    status = source.get(
        "status",
        "all",
    )

    keyword = source.get(
        "q",
        "",
    ).strip()

    if status not in STATUSES:
        status = "all"

    return (
        course_id,
        lesson_id,
        status,
        keyword,
    )


# =========================================================
# TẠO ĐIỀU KIỆN SQL CHO BỘ LỌC
# =========================================================

def build_filters(
    course_id,
    lesson_id,
    status,
    keyword,
):

    conditions = []
    params = []

    if course_id is not None:

        conditions.append(
            "kh.MaKhoaHoc = ?"
        )

        params.append(course_id)

    if lesson_id is not None:

        conditions.append(
            "bt.MaBaiHoc = ?"
        )

        params.append(lesson_id)

    if status != "all":

        conditions.append(
            "bt.TrangThai = ?"
        )

        params.append(status)

    if keyword:

        conditions.append("""
            (
                CHARINDEX(?, bt.TieuDe) > 0
                OR CHARINDEX(
                    ?,
                    ISNULL(bt.HuongDan, N'')
                ) > 0
                OR CHARINDEX(?, bh.TieuDe) > 0
            )
        """)

        params.extend([
            keyword,
            keyword,
            keyword,
        ])

    where_sql = ""

    if conditions:

        where_sql = (
            " WHERE "
            + " AND ".join(conditions)
        )

    return where_sql, params


# =========================================================
# KIỂM TRA ĐIỀU KIỆN XUẤT BẢN
#
# Chỉ kiểm tra tính đầy đủ cơ bản:
# - Có câu hỏi
# - Có nội dung
# - Câu chọn đáp án có lựa chọn đúng
# - Các loại còn lại có JSON đáp án
#
# Việc kiểm tra này không thay thế bước rà soát
# nội dung và đáp án HSK trước khi xuất bản.
# =========================================================

def publishable_exercise_ids(
    cursor,
    exercise_ids,
):

    eligible = []

    for exercise_id in exercise_ids:

        cursor.execute("""
            SELECT
                MaCauHoi,
                LoaiCauHoi,
                NoiDungCauHoi,
                DapAnJson
            FROM dbo.CauHoi
            WHERE MaBaiTap = ?;
        """, exercise_id)

        questions = cursor.fetchall()

        if not questions:
            continue

        valid = True

        for question in questions:

            question_id = question[0]
            question_type = question[1]
            content = question[2]
            answer_json = question[3]

            if (
                content is None
                or not str(content).strip()
            ):
                valid = False
                break

            if question_type in (
                "chon_mot",
                "chon_nhieu",
            ):

                cursor.execute("""
                    SELECT
                        COUNT(*),
                        SUM(
                            CASE
                                WHEN LaDapAnDung = 1
                                THEN 1
                                ELSE 0
                            END
                        )
                    FROM dbo.LuaChonCauHoi
                    WHERE MaCauHoi = ?;
                """, question_id)

                row = cursor.fetchone()

                total_choices = int(
                    row[0] or 0
                )

                correct_choices = int(
                    row[1] or 0
                )

                if (
                    total_choices < 2
                    or correct_choices < 1
                ):
                    valid = False
                    break

                if (
                    question_type == "chon_mot"
                    and correct_choices != 1
                ):
                    valid = False
                    break

            else:

                if not answer_json:
                    valid = False
                    break

                try:

                    answer_data = json.loads(
                        answer_json
                    )

                    if (
                        not isinstance(
                            answer_data,
                            dict,
                        )
                        or not answer_data
                    ):
                        valid = False
                        break

                except (
                    TypeError,
                    ValueError,
                ):
                    valid = False
                    break

        if valid:
            eligible.append(
                exercise_id
            )

    return eligible


# =========================================================
# DANH SÁCH BÀI TẬP
# =========================================================

@admin_exercises_bp.get("/")
def index():

    (
        course_id,
        lesson_id,
        status,
        keyword,
    ) = read_filters(request.args)

    edit_id = request.args.get(
        "edit",
        type=int,
    )

    page = max(
        1,
        request.args.get(
            "page",
            1,
            type=int,
        ) or 1,
    )

    courses = []
    lessons = []
    exercises = []

    editing_exercise = None

    total_count = 0
    total_pages = 1

    draft_count = 0
    scope_total_count = 0

    with closing(get_connection()) as connection:

        with closing(connection.cursor()) as cursor:

            # =============================================
            # KHÓA HỌC
            # =============================================

            cursor.execute("""
                SELECT
                    MaKhoaHoc,
                    MaCapDo,
                    TieuDe,
                    TrangThai
                FROM dbo.KhoaHoc
                WHERE TrangThai <> 'luu_tru'
                ORDER BY
                    MaCapDo,
                    MaKhoaHoc;
            """)

            for row in cursor.fetchall():

                courses.append({
                    "id": row[0],
                    "level": row[1],
                    "title": row[2],
                    "status": row[3],
                })

            # =============================================
            # BÀI HỌC
            # =============================================

            lesson_sql = """
                SELECT
                    bh.MaBaiHoc,
                    bh.MaKhoaHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe,
                    bh.TrangThai,
                    kh.MaCapDo,
                    kh.TieuDe
                FROM dbo.BaiHoc AS bh
                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc = bh.MaKhoaHoc
                WHERE bh.TrangThai <> 'luu_tru'
            """

            lesson_params = []

            if course_id is not None:

                lesson_sql += """
                    AND bh.MaKhoaHoc = ?
                """

                lesson_params.append(
                    course_id
                )

            lesson_sql += """
                ORDER BY
                    kh.MaCapDo,
                    bh.SoThuTuBai,
                    bh.MaBaiHoc;
            """

            cursor.execute(
                lesson_sql,
                *lesson_params,
            )

            for row in cursor.fetchall():

                lessons.append({
                    "id": row[0],
                    "course_id": row[1],
                    "order": row[2],
                    "title": row[3],
                    "status": row[4],
                    "course_level": row[5],
                    "course_title": row[6],
                })

            # =============================================
            # SQL DÙNG CHUNG
            # =============================================

            from_sql = """
                FROM dbo.BaiTap AS bt
                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc = bt.MaBaiHoc
                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc = bh.MaKhoaHoc
            """

            # =============================================
            # ĐẾM BÀI TẬP THEO BỘ LỌC
            # =============================================

            where_sql, params = build_filters(
                course_id,
                lesson_id,
                status,
                keyword,
            )

            cursor.execute(
                "SELECT COUNT(*) "
                + from_sql
                + where_sql,
                *params,
            )

            total_count = int(
                cursor.fetchone()[0] or 0
            )

            # =============================================
            # ĐẾM TỔNG VÀ BẢN NHÁP TRONG PHẠM VI
            #
            # Không phụ thuộc trạng thái lọc.
            # =============================================

            scope_where, scope_params = build_filters(
                course_id,
                lesson_id,
                "all",
                keyword,
            )

            cursor.execute(
                "SELECT COUNT(*) "
                + from_sql
                + scope_where,
                *scope_params,
            )

            scope_total_count = int(
                cursor.fetchone()[0] or 0
            )

            draft_where, draft_params = build_filters(
                course_id,
                lesson_id,
                "ban_nhap",
                keyword,
            )

            cursor.execute(
                "SELECT COUNT(*) "
                + from_sql
                + draft_where,
                *draft_params,
            )

            draft_count = int(
                cursor.fetchone()[0] or 0
            )

            # =============================================
            # PHÂN TRANG
            # =============================================

            total_pages = max(
                1,
                ceil(
                    total_count / PAGE_SIZE
                ),
            )

            page = min(
                page,
                total_pages,
            )

            offset = (
                page - 1
            ) * PAGE_SIZE

            # =============================================
            # LẤY DANH SÁCH BÀI TẬP
            #
            # Không cần lấy cột ngày cập nhật
            # để hiển thị lên giao diện.
            # =============================================

            cursor.execute(
                """
                SELECT
                    bt.MaBaiTap,
                    bt.MaBaiHoc,
                    bt.TieuDe,
                    bt.HuongDan,
                    bt.ThoiGianGioiHanGiay,
                    bt.PhanTramDat,
                    bt.TrangThai,
                    bh.SoThuTuBai,
                    bh.TieuDe,
                    kh.MaKhoaHoc,
                    kh.MaCapDo,
                    kh.TieuDe,
                    (
                        SELECT COUNT(*)
                        FROM dbo.CauHoi AS ch
                        WHERE ch.MaBaiTap = bt.MaBaiTap
                    ) AS SoCauHoi
                """
                + from_sql
                + where_sql
                + """
                ORDER BY
                    kh.MaCapDo,
                    bh.SoThuTuBai,
                    bt.MaBaiTap
                OFFSET ? ROWS
                FETCH NEXT ? ROWS ONLY;
                """,
                *params,
                offset,
                PAGE_SIZE,
            )

            for row in cursor.fetchall():

                seconds = row[4]

                limit_minutes = None

                if seconds is not None:

                    limit_minutes = (
                        float(seconds) / 60
                    )

                exercises.append({
                    "id": row[0],
                    "lesson_id": row[1],
                    "title": row[2],
                    "instruction": row[3] or "",
                    "limit_seconds": seconds,
                    "limit_minutes": limit_minutes,
                    "pass_percent": row[5],
                    "status": row[6],
                    "lesson_order": row[7],
                    "lesson_title": row[8],
                    "course_id": row[9],
                    "course_level": row[10],
                    "course_title": row[11],
                    "question_count": int(
                        row[12] or 0
                    ),
                })

            # =============================================
            # BÀI TẬP ĐANG CHỈNH SỬA
            # =============================================

            if edit_id is not None:

                cursor.execute("""
                    SELECT
                        MaBaiTap,
                        MaBaiHoc,
                        TieuDe,
                        HuongDan,
                        ThoiGianGioiHanGiay,
                        PhanTramDat,
                        TrangThai
                    FROM dbo.BaiTap
                    WHERE MaBaiTap = ?;
                """, edit_id)

                row = cursor.fetchone()

                if row is None:

                    abort(
                        404,
                        description="Không tìm thấy bài tập.",
                    )

                edit_minutes = ""

                if row[4] is not None:

                    edit_minutes = (
                        float(row[4]) / 60
                    )

                editing_exercise = {
                    "id": row[0],
                    "lesson_id": row[1],
                    "title": row[2],
                    "instruction": row[3] or "",
                    "limit_minutes": edit_minutes,
                    "pass_percent": row[5],
                    "status": row[6],
                }

    return render_template(
        "admin/exercises.html",

        active_page="exercises",

        courses=courses,
        lessons=lessons,
        exercises=exercises,

        editing_exercise=editing_exercise,

        selected_course=course_id,
        selected_lesson=lesson_id,
        selected_status=status,

        keyword=keyword,
        statuses=STATUSES,

        page=page,
        page_size=PAGE_SIZE,

        total_count=total_count,
        total_pages=total_pages,

        draft_count=draft_count,
        scope_total_count=scope_total_count,
    )


# =========================================================
# TẠO BÀI TẬP
# =========================================================

@admin_exercises_bp.post("/them")
def create():

    try:

        data = parse_exercise_form()

    except ValueError as error:

        flash(
            str(error),
            "error",
        )

        return redirect(
            url_for("admin_exercises.index")
        )

    with closing(get_connection()) as connection:

        try:

            with closing(connection.cursor()) as cursor:

                cursor.execute("""
                    SELECT MaBaiHoc
                    FROM dbo.BaiHoc
                    WHERE MaBaiHoc = ?;
                """, data["lesson_id"])

                if cursor.fetchone() is None:

                    abort(
                        400,
                        description="Bài học không tồn tại.",
                    )

                cursor.execute("""
                    INSERT INTO dbo.BaiTap
                    (
                        MaBaiHoc,
                        TieuDe,
                        HuongDan,
                        ThoiGianGioiHanGiay,
                        PhanTramDat,
                        TrangThai,
                        MaQuanTriVienCapNhat,
                        NgayCapNhat
                    )
                    VALUES
                    (
                        ?, ?, ?, ?, ?,
                        'ban_nhap',
                        ?, SYSDATETIME()
                    );
                """,
                    data["lesson_id"],
                    data["title"],
                    data["instruction"],
                    data["limit_seconds"],
                    data["percent"],
                    current_admin_id(),
                )

            connection.commit()

        except Exception:

            connection.rollback()
            raise

    flash(
        "Đã tạo bài tập ở trạng thái Bản nháp.",
        "success",
    )

    return redirect(
        url_for("admin_exercises.index")
    )


# =========================================================
# SỬA BÀI TẬP
# =========================================================

@admin_exercises_bp.post("/<int:exercise_id>/sua")
def edit(exercise_id):

    try:

        data = parse_exercise_form()

    except ValueError as error:

        flash(
            str(error),
            "error",
        )

        return redirect(
            url_for(
                "admin_exercises.index",
                edit=exercise_id,
            )
        )

    with closing(get_connection()) as connection:

        try:

            with closing(connection.cursor()) as cursor:

                cursor.execute("""
                    SELECT MaBaiTap
                    FROM dbo.BaiTap WITH (
                        UPDLOCK,
                        HOLDLOCK
                    )
                    WHERE MaBaiTap = ?;
                """, exercise_id)

                if cursor.fetchone() is None:

                    abort(
                        404,
                        description="Không tìm thấy bài tập.",
                    )

                cursor.execute("""
                    SELECT MaBaiHoc
                    FROM dbo.BaiHoc
                    WHERE MaBaiHoc = ?;
                """, data["lesson_id"])

                if cursor.fetchone() is None:

                    abort(
                        400,
                        description="Bài học không tồn tại.",
                    )

                cursor.execute("""
                    UPDATE dbo.BaiTap
                    SET
                        MaBaiHoc = ?,
                        TieuDe = ?,
                        HuongDan = ?,
                        ThoiGianGioiHanGiay = ?,
                        PhanTramDat = ?,
                        MaQuanTriVienCapNhat = ?,
                        NgayCapNhat = SYSDATETIME()
                    WHERE MaBaiTap = ?;
                """,
                    data["lesson_id"],
                    data["title"],
                    data["instruction"],
                    data["limit_seconds"],
                    data["percent"],
                    current_admin_id(),
                    exercise_id,
                )

            connection.commit()

        except Exception:

            connection.rollback()
            raise

    flash(
        "Đã cập nhật bài tập.",
        "success",
    )

    return redirect(
        url_for(
            "admin_exercises.index",
            edit=exercise_id,
        )
    )


# =========================================================
# ĐỔI TRẠNG THÁI MỘT BÀI TẬP
#
# Bộ lọc nằm ở request.args.
# Trạng thái mới nằm ở request.form.
# Hai giá trị không được trộn với nhau.
# =========================================================

@admin_exercises_bp.post(
    "/<int:exercise_id>/trang-thai"
)
def set_status(exercise_id):

    new_status = request.form.get(
        "status",
        "",
    ).strip()

    if new_status not in STATUSES:

        flash(
            "Trạng thái không hợp lệ.",
            "error",
        )

        return redirect(
            index_url()
        )

    with closing(get_connection()) as connection:

        try:

            with closing(connection.cursor()) as cursor:

                cursor.execute("""
                    SELECT TrangThai
                    FROM dbo.BaiTap WITH (
                        UPDLOCK,
                        HOLDLOCK
                    )
                    WHERE MaBaiTap = ?;
                """, exercise_id)

                row = cursor.fetchone()

                if row is None:

                    abort(
                        404,
                        description="Không tìm thấy bài tập.",
                    )

                old_status = row[0]

                if old_status == new_status:

                    flash(
                        "Trạng thái không thay đổi.",
                        "success",
                    )

                    return redirect(
                        index_url()
                    )

                if new_status == "da_xuat_ban":

                    eligible = publishable_exercise_ids(
                        cursor,
                        [exercise_id],
                    )

                    if exercise_id not in eligible:

                        flash(
                            "Bài tập chưa đủ câu hỏi "
                            "hoặc đáp án hợp lệ để xuất bản.",
                            "error",
                        )

                        return redirect(
                            index_url()
                        )

                cursor.execute("""
                    UPDATE dbo.BaiTap
                    SET
                        TrangThai = ?,
                        MaQuanTriVienCapNhat = ?,
                        NgayCapNhat = SYSDATETIME()
                    WHERE MaBaiTap = ?;
                """,
                    new_status,
                    current_admin_id(),
                    exercise_id,
                )

            connection.commit()

        except Exception:

            connection.rollback()
            raise

    flash(
        "Đã cập nhật trạng thái bài tập.",
        "success",
    )

    return redirect(
        index_url()
    )


# =========================================================
# XUẤT BẢN TOÀN BỘ BÀI NHÁP
#
# Phải chọn khóa học hoặc bài học.
# Không xuất bản hàng loạt toàn hệ thống
# khi chưa xác định phạm vi.
# =========================================================


# =========================================================
# XUẤT BẢN TOÀN BỘ BÀI NHÁP
#
# Phải chọn khóa học hoặc bài học.
# Không xuất bản hàng loạt toàn hệ thống
# khi chưa xác định phạm vi.
# =========================================================

@admin_exercises_bp.post("/xuat-ban-tat-ca")
def publish_all():

    (
        course_id,
        lesson_id,
        _,
        keyword,
    ) = read_filters(request.form)

    # Bắt buộc xác định phạm vi xuất bản.
    if course_id is None and lesson_id is None:
        flash(
            "Bạn cần chọn khóa học hoặc bài học "
            "trước khi xuất bản hàng loạt.",
            "error",
        )

        return redirect(
            url_for("admin_exercises.index")
        )

    # Chỉ lấy các bài tập đang ở trạng thái bản nháp.
    where_sql, params = build_filters(
        course_id,
        lesson_id,
        "ban_nhap",
        keyword,
    )

    updated_count = 0
    skipped = 0

    with closing(get_connection()) as connection:

        try:

            with closing(connection.cursor()) as cursor:

                # Lấy các bài tập bản nháp trong phạm vi chọn.
                cursor.execute(
                    """
                    SELECT bt.MaBaiTap
                    FROM dbo.BaiTap AS bt
                        WITH (UPDLOCK, HOLDLOCK)
                    INNER JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = bt.MaBaiHoc
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON kh.MaKhoaHoc = bh.MaKhoaHoc
                    """
                    + where_sql,
                    *params,
                )

                ids = [
                    int(row[0])
                    for row in cursor.fetchall()
                ]

                # Kiểm tra bài tập có đủ điều kiện xuất bản.
                eligible = publishable_exercise_ids(
                    cursor,
                    ids,
                )

                # Chỉ xuất bản những bài tập hợp lệ.
                for exercise_id in eligible:

                    cursor.execute(
                        """
                        UPDATE dbo.BaiTap
                        SET
                            TrangThai = 'da_xuat_ban',
                            MaQuanTriVienCapNhat = ?,
                            NgayCapNhat = SYSDATETIME()
                        WHERE
                            MaBaiTap = ?
                            AND TrangThai = 'ban_nhap';
                        """,
                        current_admin_id(),
                        exercise_id,
                    )

                    updated_count += cursor.rowcount

                skipped = len(ids) - updated_count

            # Chỉ COMMIT khi tất cả câu lệnh SQL thành công.
            connection.commit()

        except Exception:

            # Nếu có lỗi thì hoàn tác toàn bộ transaction.
            connection.rollback()
            raise

    flash(
        f"Đã xuất bản {updated_count} bài tập. "
        f"Bỏ qua {skipped} bài chưa đủ điều kiện.",
        "success",
    )

    return redirect(
        url_for(
            "admin_exercises.index",
            course_id=course_id,
            lesson_id=lesson_id,
            q=keyword,
        )
    )



# =========================================================
# XÓA BÀI TẬP
#
# Chỉ xóa Bản nháp.
# Không xóa nếu đã có lịch sử làm bài.
# Các thao tác DELETE cùng một transaction.
# SQL sẽ chặn nếu còn khóa ngoại liên kết.
# =========================================================

@admin_exercises_bp.post(
    "/<int:exercise_id>/xoa"
)
def delete(exercise_id):

    with closing(get_connection()) as connection:

        try:

            with closing(connection.cursor()) as cursor:

                cursor.execute("""
                    SELECT
                        TieuDe,
                        TrangThai
                    FROM dbo.BaiTap WITH (
                        UPDLOCK,
                        HOLDLOCK
                    )
                    WHERE MaBaiTap = ?;
                """, exercise_id)

                row = cursor.fetchone()

                if row is None:

                    abort(
                        404,
                        description="Không tìm thấy bài tập.",
                    )

                title = row[0]
                status = row[1]

                if status != "ban_nhap":

                    flash(
                        "Chỉ có thể xóa bài tập Bản nháp. "
                        "Bài đã xuất bản nên chuyển sang Lưu trữ.",
                        "error",
                    )

                    return redirect(
                        index_url()
                    )

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM dbo.LanLamBai
                    WHERE MaBaiTap = ?;
                """, exercise_id)

                history_count = int(
                    cursor.fetchone()[0] or 0
                )

                if history_count > 0:

                    flash(
                        "Không thể xóa vì bài tập "
                        "đã có lịch sử làm bài.",
                        "error",
                    )

                    return redirect(
                        index_url()
                    )

                # Xóa lựa chọn của các câu hỏi
                # thuộc bài tập này.

                cursor.execute("""
                    DELETE lc
                    FROM dbo.LuaChonCauHoi AS lc
                    INNER JOIN dbo.CauHoi AS ch
                        ON ch.MaCauHoi = lc.MaCauHoi
                    WHERE ch.MaBaiTap = ?;
                """, exercise_id)

                # Xóa câu hỏi của bài tập.

                cursor.execute("""
                    DELETE FROM dbo.CauHoi
                    WHERE MaBaiTap = ?;
                """, exercise_id)

                # Xóa bài tập.

                cursor.execute("""
                    DELETE FROM dbo.BaiTap
                    WHERE MaBaiTap = ?;
                """, exercise_id)

            connection.commit()

        except pyodbc.IntegrityError:

            connection.rollback()

            flash(
                "Không thể xóa vì bài tập "
                "còn dữ liệu liên kết trong SQL.",
                "error",
            )

            return redirect(
                index_url()
            )

        except Exception:

            connection.rollback()
            raise

    flash(
        f"Đã xóa bài tập “{title}”.",
        "success",
    )

    return redirect(
        index_url()
    )
