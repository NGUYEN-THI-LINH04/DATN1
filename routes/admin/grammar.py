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


# =========================================================
# BLUEPRINT
# =========================================================

admin_grammar_bp = Blueprint(
    "admin_grammar",
    __name__,
    url_prefix="/admin/ngu-phap",
)


# =========================================================
# TRẠNG THÁI
# =========================================================

STATUSES = {
    "ban_nhap": "Bản nháp",
    "da_xuat_ban": "Đã xuất bản",
    "luu_tru": "Lưu trữ",
}


# =========================================================
# KIỂM TRA ADMIN
# =========================================================

@admin_grammar_bp.before_request
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
            description="Bạn không có quyền quản lý ngữ pháp."
        )


# =========================================================
# LỖI DATABASE
# =========================================================

@admin_grammar_bp.errorhandler(
    pyodbc.Error
)
def handle_database_error(error):

    current_app.logger.error(
        "Loi SQL trong quan ly ngu phap: %s",
        type(error).__name__
    )

    return (
        "Chưa thể xử lý dữ liệu ngữ pháp.",
        503
    )


# =========================================================
# DANH SÁCH NGỮ PHÁP
#
# URL:
# /admin/ngu-phap/
# =========================================================

@admin_grammar_bp.get("/")
def index():

    # =====================================================
    # BỘ LỌC
    # =====================================================

    course_id = request.args.get(
        "course_id",
        type=int
    )

    lesson_id = request.args.get(
        "lesson_id",
        type=int
    )

    status = request.args.get(
        "status",
        "all"
    )

    keyword = request.args.get(
        "q",
        ""
    ).strip()

    edit_id = request.args.get(
        "edit",
        type=int
    )


    # =====================================================
    # PHÂN TRANG
    # =====================================================

    page = request.args.get(
        "page",
        1,
        type=int
    )

    if page is None or page < 1:
        page = 1

    per_page = 30


    # =====================================================
    # KIỂM TRA TRẠNG THÁI
    # =====================================================

    if status not in {
        "all",
        "ban_nhap",
        "da_xuat_ban",
        "luu_tru",
    }:

        status = "all"


    # =====================================================
    # BIẾN DỮ LIỆU
    # =====================================================

    courses = []

    lessons = []

    grammars = []


    selected_course_info = None

    selected_course_draft_count = 0

    editing_grammar = None


    total_grammars = 0

    total_pages = 1


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # 1. KHÓA HỌC
            # =================================================

            cursor.execute(
                """
                SELECT
                    MaKhoaHoc,
                    MaCapDo,
                    TieuDe

                FROM dbo.KhoaHoc

                ORDER BY
                    MaCapDo,
                    MaKhoaHoc;
                """
            )


            for row in cursor.fetchall():

                course = {
                    "id": row[0],
                    "level": row[1],
                    "title": row[2],
                }


                courses.append(
                    course
                )


                if (
                    course_id is not None
                    and
                    course["id"] == course_id
                ):

                    selected_course_info = course


            # =================================================
            # 2. BÀI HỌC
            # =================================================

            cursor.execute(
                """
                SELECT
                    bh.MaBaiHoc,
                    bh.MaKhoaHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe,
                    kh.MaCapDo

                FROM dbo.BaiHoc AS bh

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc
                    = bh.MaKhoaHoc

                ORDER BY
                    kh.MaCapDo,
                    bh.SoThuTuBai,
                    bh.MaBaiHoc;
                """
            )


            for row in cursor.fetchall():

                lessons.append(
                    {
                        "id": row[0],
                        "course_id": row[1],
                        "order": row[2],
                        "title": row[3],
                        "level": row[4],
                    }
                )


            # =================================================
            # 3. TẠO ĐIỀU KIỆN LỌC
            # =================================================

            conditions = []

            params = []


            if course_id is not None:

                conditions.append(
                    "bh.MaKhoaHoc = ?"
                )

                params.append(
                    course_id
                )


            if lesson_id is not None:

                conditions.append(
                    "ng.MaBaiHoc = ?"
                )

                params.append(
                    lesson_id
                )


            if status != "all":

                conditions.append(
                    "ng.TrangThai = ?"
                )

                params.append(
                    status
                )


            if keyword:

                conditions.append(
                    """
                    (
                        CHARINDEX(
                            ?,
                            ng.TenCauTruc
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                ng.MoTa,
                                N''
                            )
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                ng.CachDung,
                                N''
                            )
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                ng.ViDuTiengTrung,
                                N''
                            )
                        ) > 0
                    )
                    """
                )

                params.extend(
                    [
                        keyword,
                        keyword,
                        keyword,
                        keyword,
                    ]
                )


            where_sql = ""


            if conditions:

                where_sql = (
                    " WHERE "
                    + " AND ".join(
                        conditions
                    )
                )


            # =================================================
            # 4. ĐẾM TỔNG NGỮ PHÁP SAU KHI LỌC
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.NguPhap AS ng

                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc
                    = ng.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc
                    = bh.MaKhoaHoc
                """
                + where_sql,
                *params
            )


            total_grammars = int(
                cursor.fetchone()[0]
                or 0
            )


            total_pages = max(
                1,
                (
                    total_grammars
                    + per_page
                    - 1
                )
                // per_page
            )


            # =================================================
            # NẾU PAGE LỚN HƠN TRANG CUỐI
            # =================================================

            if page > total_pages:

                page = total_pages


            offset = (
                page - 1
            ) * per_page


            # =================================================
            # 5. DANH SÁCH NGỮ PHÁP CÓ PHÂN TRANG
            # =================================================

            list_params = (
                params
                + [
                    offset,
                    per_page,
                ]
            )


            cursor.execute(
                """
                SELECT
                    ng.MaNguPhap,
                    ng.MaBaiHoc,
                    ng.TenCauTruc,
                    ng.MoTa,
                    ng.CachDung,
                    ng.ViDuTiengTrung,
                    ng.ViDuPinyin,
                    ng.ViDuTiengViet,
                    ng.ThuTu,
                    ng.TrangThai,

                    bh.SoThuTuBai,
                    bh.TieuDe,

                    kh.MaKhoaHoc,
                    kh.MaCapDo,
                    kh.TieuDe

                FROM dbo.NguPhap AS ng

                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc
                    = ng.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc
                    = bh.MaKhoaHoc
                """
                + where_sql
                + """
                ORDER BY
                    kh.MaCapDo,
                    bh.SoThuTuBai,
                    ng.ThuTu,
                    ng.MaNguPhap

                OFFSET ? ROWS

                FETCH NEXT ? ROWS ONLY;
                """,
                *list_params
            )


            for row in cursor.fetchall():

                grammars.append(
                    {
                        "id": row[0],

                        "lesson_id": row[1],

                        "structure": row[2]
                        or "",

                        "description": row[3]
                        or "",

                        "usage": row[4]
                        or "",

                        "example_zh": row[5]
                        or "",

                        "example_pinyin": row[6]
                        or "",

                        "example_vi": row[7]
                        or "",

                        "order": row[8],

                        "status": row[9],

                        "lesson_order": row[10],

                        "lesson_title": row[11],

                        "course_id": row[12],

                        "course_level": row[13],

                        "course_title": row[14],
                    }
                )


            # =================================================
            # 6. ĐẾM NGỮ PHÁP BẢN NHÁP CỦA KHÓA
            # =================================================

            if course_id is not None:

                cursor.execute(
                    """
                    SELECT
                        COUNT(*)

                    FROM dbo.NguPhap AS ng

                    INNER JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc
                        = ng.MaBaiHoc

                    WHERE
                        bh.MaKhoaHoc = ?
                        AND ng.TrangThai = 'ban_nhap';
                    """,
                    course_id
                )


                selected_course_draft_count = int(
                    cursor.fetchone()[0]
                    or 0
                )


            # =================================================
            # 7. NGỮ PHÁP ĐANG SỬA
            # =================================================

            if edit_id is not None:

                cursor.execute(
                    """
                    SELECT
                        MaNguPhap,
                        MaBaiHoc,
                        TenCauTruc,
                        MoTa,
                        CachDung,
                        ViDuTiengTrung,
                        ViDuPinyin,
                        ViDuTiengViet,
                        ThuTu,
                        TrangThai,
                        MaQuanTriVienCapNhat,
                        NgayCapNhat

                    FROM dbo.NguPhap

                    WHERE
                        MaNguPhap = ?;
                    """,
                    edit_id
                )


                row = cursor.fetchone()


                if row is None:

                    abort(
                        404,
                        description="Không tìm thấy ngữ pháp."
                    )


                editing_grammar = {
                    "id": row[0],
                    "lesson_id": row[1],
                    "structure": row[2] or "",
                    "description": row[3] or "",
                    "usage": row[4] or "",
                    "example_zh": row[5] or "",
                    "example_pinyin": row[6] or "",
                    "example_vi": row[7] or "",
                    "order": row[8],
                    "status": row[9],

                    "admin_updated_id":
                        row[10],

                    "updated_at":
                        row[11],
                }


    # =========================================================
    # RENDER
    # =========================================================

    return render_template(
        "admin/grammar.html",

        active_page="materials",

        courses=courses,

        lessons=lessons,

        grammars=grammars,

        selected_course=course_id,

        selected_lesson=lesson_id,

        selected_status=status,

        keyword=keyword,

        statuses=STATUSES,

        selected_course_info=
            selected_course_info,

        selected_course_draft_count=
            selected_course_draft_count,

        editing_grammar=
            editing_grammar,

        # =====================================================
        # PHÂN TRANG
        # =====================================================

        page=page,

        per_page=per_page,

        total_pages=total_pages,

        total_grammars=total_grammars,
    )


# =========================================================
# SỬA NGỮ PHÁP
# =========================================================

@admin_grammar_bp.post(
    "/<int:grammar_id>/sua"
)
def edit(grammar_id):

    structure = request.form.get(
        "structure",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    usage = request.form.get(
        "usage",
        ""
    ).strip()

    example_zh = request.form.get(
        "example_zh",
        ""
    ).strip()

    example_pinyin = request.form.get(
        "example_pinyin",
        ""
    ).strip()

    example_vi = request.form.get(
        "example_vi",
        ""
    ).strip()

    order = request.form.get(
        "order",
        type=int
    )

    status = request.form.get(
        "status",
        ""
    ).strip()


    # =====================================================
    # THÔNG TIN QUAY LẠI TRANG
    # =====================================================

    return_page = request.form.get(
        "return_page",
        1,
        type=int
    )

    return_course_id = request.form.get(
        "return_course_id",
        type=int
    )

    return_lesson_id = request.form.get(
        "return_lesson_id",
        type=int
    )

    return_status = request.form.get(
        "return_status",
        "all"
    )

    return_keyword = request.form.get(
        "return_keyword",
        ""
    ).strip()


    # =====================================================
    # VALIDATE
    # =====================================================

    if not structure:

        flash(
            "Tên cấu trúc không được để trống.",
            "error"
        )

        return redirect(
            url_for(
                "admin_grammar.index",

                edit=grammar_id,

                page=return_page,

                course_id=return_course_id,

                lesson_id=return_lesson_id,

                status=return_status,

                q=return_keyword,
            )
        )


    if order is None or order <= 0:

        flash(
            "Thứ tự phải lớn hơn 0.",
            "error"
        )

        return redirect(
            url_for(
                "admin_grammar.index",

                edit=grammar_id,

                page=return_page,

                course_id=return_course_id,

                lesson_id=return_lesson_id,

                status=return_status,

                q=return_keyword,
            )
        )


    if status not in STATUSES:

        abort(
            400,
            description="Trạng thái không hợp lệ."
        )


    # =====================================================
    # ADMIN ĐANG ĐĂNG NHẬP
    # =====================================================

    admin_id = int(
        g.account["id"]
    )


    # =====================================================
    # UPDATE SQL
    # =====================================================

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                UPDATE dbo.NguPhap

                SET
                    TenCauTruc = ?,
                    MoTa = ?,
                    CachDung = ?,
                    ViDuTiengTrung = ?,
                    ViDuPinyin = ?,
                    ViDuTiengViet = ?,
                    ThuTu = ?,
                    TrangThai = ?,

                    MaQuanTriVienCapNhat = ?,
                    NgayCapNhat =
                        SYSDATETIME()

                WHERE
                    MaNguPhap = ?;
                """,

                structure,

                description
                or None,

                usage
                or None,

                example_zh
                or None,

                example_pinyin
                or None,

                example_vi
                or None,

                order,

                status,

                admin_id,

                grammar_id
            )


            if cursor.rowcount == 0:

                abort(
                    404,
                    description="Không tìm thấy ngữ pháp."
                )


        connection.commit()


    flash(
        "Đã cập nhật ngữ pháp vào SQL Server.",
        "success"
    )


    return redirect(
        url_for(
            "admin_grammar.index",

            page=return_page,

            course_id=return_course_id,

            lesson_id=return_lesson_id,

            status=return_status,

            q=return_keyword,
        )
    )


# =========================================================
# ĐỔI TRẠNG THÁI MỘT NGỮ PHÁP
# =========================================================

@admin_grammar_bp.post(
    "/<int:grammar_id>/trang-thai"
)
def set_status(grammar_id):

    new_status = request.form.get(
        "status",
        ""
    ).strip()


    # =====================================================
    # THÔNG TIN QUAY LẠI
    # =====================================================

    return_page = request.form.get(
        "return_page",
        1,
        type=int
    )

    return_course_id = request.form.get(
        "return_course_id",
        type=int
    )

    return_lesson_id = request.form.get(
        "return_lesson_id",
        type=int
    )

    return_status = request.form.get(
        "return_status",
        "all"
    )

    return_keyword = request.form.get(
        "return_keyword",
        ""
    ).strip()


    if new_status not in STATUSES:

        abort(
            400,
            description="Trạng thái không hợp lệ."
        )


    # =====================================================
    # ADMIN ĐANG ĐĂNG NHẬP
    # =====================================================

    admin_id = int(
        g.account["id"]
    )


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                UPDATE dbo.NguPhap

                SET
                    TrangThai = ?,
                    MaQuanTriVienCapNhat = ?,
                    NgayCapNhat =
                        SYSUTCDATETIME()

                WHERE
                    MaNguPhap = ?;
                """,
                new_status,
                admin_id,
                grammar_id
            )


            if cursor.rowcount == 0:

                abort(
                    404,
                    description="Không tìm thấy ngữ pháp."
                )


        connection.commit()


    flash(
        (
            "Đã chuyển ngữ pháp sang trạng thái "
            f"“{STATUSES[new_status]}”."
        ),
        "success"
    )


    return redirect(
        url_for(
            "admin_grammar.index",

            page=return_page,

            course_id=return_course_id,

            lesson_id=return_lesson_id,

            status=return_status,

            q=return_keyword,
        )
    )


# =========================================================
# XUẤT BẢN TOÀN BỘ NGỮ PHÁP CỦA KHÓA
# =========================================================

@admin_grammar_bp.post(
    "/khoa/<int:course_id>/xuat-ban"
)
def publish_course(course_id):

    # =====================================================
    # ADMIN ĐANG ĐĂNG NHẬP
    # =====================================================

    admin_id = int(
        g.account["id"]
    )


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # KIỂM TRA KHÓA
            # =================================================

            cursor.execute(
                """
                SELECT
                    MaKhoaHoc,
                    TieuDe

                FROM dbo.KhoaHoc

                WHERE
                    MaKhoaHoc = ?;
                """,
                course_id
            )


            course = cursor.fetchone()


            if course is None:

                abort(
                    404,
                    description="Không tìm thấy khóa học."
                )


            # =================================================
            # XUẤT BẢN TOÀN BỘ BẢN NHÁP
            # =================================================

            cursor.execute(
                """
                UPDATE ng

                SET
                    TrangThai =
                        'da_xuat_ban',

                    MaQuanTriVienCapNhat = ?,

                    NgayCapNhat =
                        SYSUTCDATETIME()

                OUTPUT
                    INSERTED.MaNguPhap

                FROM dbo.NguPhap AS ng

                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc
                    = ng.MaBaiHoc

                WHERE
                    bh.MaKhoaHoc = ?
                    AND ng.TrangThai =
                        'ban_nhap';
                """,
                admin_id,
                course_id
            )


            updated_rows = cursor.fetchall()

            updated_count = len(
                updated_rows
            )


        connection.commit()


    if updated_count > 0:

        flash(
            (
                f"Đã xuất bản {updated_count} "
                f"ngữ pháp của khóa “{course[1]}”."
            ),
            "success"
        )

    else:

        flash(
            "Không còn ngữ pháp bản nháp cần xuất bản.",
            "success"
        )


    return redirect(
        url_for(
            "admin_grammar.index",
            course_id=course_id
        )
    )

# =========================================================
# XUAT BAN TAT CA NGU PHAP BAN NHAP
# =========================================================

@admin_grammar_bp.post("/xuat-ban-tat-ca")
def publish_all():

    admin_id = int(g.account["id"])

    with closing(get_connection()) as connection:
        try:
            with closing(connection.cursor()) as cursor:
                cursor.execute(
                    """
                    UPDATE dbo.NguPhap
                    SET
                        TrangThai = 'da_xuat_ban',
                        MaQuanTriVienCapNhat = ?,
                        NgayCapNhat = SYSUTCDATETIME()
                    WHERE TrangThai = 'ban_nhap'
                    """,
                    admin_id
                )

                updated_count = cursor.rowcount

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    flash(
        f"Đã xuất bản {updated_count} mục ngữ pháp.",
        "success"
    )

    return redirect(
        url_for("admin_grammar.index")
    )
