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

admin_hanzi_bp = Blueprint(
    "admin_hanzi",
    __name__,
    url_prefix="/admin/chu-han",
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

@admin_hanzi_bp.before_request
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
            description="Bạn không có quyền quản lý Chữ Hán."
        )


# =========================================================
# XỬ LÝ LỖI DATABASE
# =========================================================

@admin_hanzi_bp.errorhandler(
    pyodbc.Error
)
def handle_database_error(error):

    current_app.logger.error(
        "Loi SQL trong quan ly Chu Han: %s",
        type(error).__name__
    )

    return (
        "Chưa thể xử lý dữ liệu Chữ Hán. "
        "Vui lòng thử lại.",
        503
    )


# =========================================================
# DANH SÁCH CHỮ HÁN
#
# URL:
# /admin/chu-han/
# =========================================================

@admin_hanzi_bp.get("/")
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
    # DATA
    # =====================================================

    courses = []

    lessons = []

    radicals = []

    hanzis = []


    selected_course_info = None

    selected_course_draft_count = 0

    editing_hanzi = None


    total_hanzis = 0

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
            # 3. BỘ THỦ
            # =================================================

            cursor.execute(
                """
                SELECT
                    MaBoThu,
                    KyHieu,
                    TenBoThu,
                    YNghia,
                    SoNet

                FROM dbo.BoThu

                ORDER BY
                    ISNULL(SoNet, 999),
                    MaBoThu;
                """
            )


            for row in cursor.fetchall():

                radicals.append(
                    {
                        "id": row[0],
                        "symbol": row[1],
                        "name": row[2],
                        "meaning": row[3] or "",
                        "stroke_count": row[4],
                    }
                )


            # =================================================
            # 4. TẠO ĐIỀU KIỆN LỌC
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
                    "ch.MaBaiHoc = ?"
                )

                params.append(
                    lesson_id
                )


            if status != "all":

                conditions.append(
                    "ch.TrangThai = ?"
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
                            ch.KyTu
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                ch.Pinyin,
                                N''
                            )
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                ch.NghiaTiengViet,
                                N''
                            )
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                ch.CachGhiNho,
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
            # 5. ĐẾM TỔNG CHỮ HÁN SAU KHI LỌC
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.ChuHan AS ch

                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc
                    = ch.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc
                    = bh.MaKhoaHoc
                """
                + where_sql,
                *params
            )


            total_hanzis = int(
                cursor.fetchone()[0]
                or 0
            )


            total_pages = max(
                1,
                (
                    total_hanzis
                    + per_page
                    - 1
                )
                // per_page
            )


            if page > total_pages:

                page = total_pages


            offset = (
                page - 1
            ) * per_page


            # =================================================
            # 6. DANH SÁCH CHỮ HÁN CÓ PHÂN TRANG
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
                    ch.MaChuHan,
                    ch.MaBaiHoc,
                    ch.MaBoThu,
                    ch.KyTu,
                    ch.Pinyin,
                    ch.NghiaTiengViet,
                    ch.SoNet,
                    ch.CachGhiNho,
                    ch.ViDuTiengTrung,
                    ch.ViDuPinyin,
                    ch.ViDuTiengViet,
                    ch.MaTep,
                    ch.ThuTu,
                    ch.TrangThai,

                    bh.SoThuTuBai,
                    bh.TieuDe,

                    kh.MaKhoaHoc,
                    kh.MaCapDo,
                    kh.TieuDe,

                    bt.KyHieu,
                    bt.TenBoThu,

                    tep.DuongDanTep

                FROM dbo.ChuHan AS ch

                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc
                    = ch.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc
                    = bh.MaKhoaHoc

                LEFT JOIN dbo.BoThu AS bt
                    ON bt.MaBoThu
                    = ch.MaBoThu

                LEFT JOIN dbo.TepDaPhuongTien AS tep
                    ON tep.MaTep
                    = ch.MaTep
                """
                + where_sql
                + """
                ORDER BY
                    kh.MaCapDo,
                    bh.SoThuTuBai,
                    ch.ThuTu,
                    ch.MaChuHan

                OFFSET ? ROWS

                FETCH NEXT ? ROWS ONLY;
                """,
                *list_params
            )


            for row in cursor.fetchall():

                hanzis.append(
                    {
                        "id": row[0],

                        "lesson_id": row[1],

                        "radical_id": row[2],

                        "character": row[3],

                        "pinyin": row[4] or "",

                        "meaning": row[5] or "",

                        "stroke_count": row[6],

                        "memory_tip": row[7] or "",

                        "example_zh": row[8] or "",

                        "example_pinyin": row[9] or "",

                        "example_vi": row[10] or "",

                        "media_id": row[11],

                        "order": row[12],

                        "status": row[13],

                        "lesson_order": row[14],

                        "lesson_title": row[15],

                        "course_id": row[16],

                        "course_level": row[17],

                        "course_title": row[18],

                        "radical_symbol": row[19] or "",

                        "radical_name": row[20] or "",

                        "media_path": row[21] or "",
                    }
                )


            # =================================================
            # 7. ĐẾM BẢN NHÁP CỦA KHÓA
            # =================================================

            if course_id is not None:

                cursor.execute(
                    """
                    SELECT
                        COUNT(*)

                    FROM dbo.ChuHan AS ch

                    INNER JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc
                        = ch.MaBaiHoc

                    WHERE
                        bh.MaKhoaHoc = ?
                        AND ch.TrangThai = 'ban_nhap';
                    """,
                    course_id
                )


                selected_course_draft_count = int(
                    cursor.fetchone()[0]
                    or 0
                )


            # =================================================
            # 8. DỮ LIỆU CHỮ HÁN ĐANG SỬA
            # =================================================

            if edit_id is not None:

                cursor.execute(
                    """
                    SELECT
                        MaChuHan,
                        MaBaiHoc,
                        MaBoThu,
                        KyTu,
                        Pinyin,
                        NghiaTiengViet,
                        SoNet,
                        CachGhiNho,
                        ViDuTiengTrung,
                        ViDuPinyin,
                        ViDuTiengViet,
                        MaTep,
                        ThuTu,
                        TrangThai,
                        MaQuanTriVienCapNhat,
                        NgayCapNhat

                    FROM dbo.ChuHan

                    WHERE
                        MaChuHan = ?;
                    """,
                    edit_id
                )


                row = cursor.fetchone()


                if row is None:

                    abort(
                        404,
                        description="Không tìm thấy Chữ Hán."
                    )


                editing_hanzi = {
                    "id": row[0],

                    "lesson_id": row[1],

                    "radical_id": row[2],

                    "character": row[3],

                    "pinyin": row[4] or "",

                    "meaning": row[5] or "",

                    "stroke_count": row[6],

                    "memory_tip": row[7] or "",

                    "example_zh": row[8] or "",

                    "example_pinyin": row[9] or "",

                    "example_vi": row[10] or "",

                    "media_id": row[11],

                    "order": row[12],

                    "status": row[13],

                    "admin_updated_id": row[14],

                    "updated_at": row[15],
                }


    # =========================================================
    # RENDER
    # =========================================================

    return render_template(
        "admin/hanzi.html",

        active_page="materials",

        courses=courses,

        lessons=lessons,

        radicals=radicals,

        hanzis=hanzis,

        selected_course=course_id,

        selected_lesson=lesson_id,

        selected_status=status,

        keyword=keyword,

        statuses=STATUSES,

        selected_course_info=
            selected_course_info,

        selected_course_draft_count=
            selected_course_draft_count,

        editing_hanzi=
            editing_hanzi,

        # =====================================================
        # PHÂN TRANG
        # =====================================================

        page=page,

        per_page=per_page,

        total_pages=total_pages,

        total_hanzis=total_hanzis,
    )


# =========================================================
# SỬA CHỮ HÁN
# =========================================================

@admin_hanzi_bp.post(
    "/<int:hanzi_id>/sua"
)
def edit(hanzi_id):

    character = request.form.get(
        "character",
        ""
    ).strip()

    pinyin = request.form.get(
        "pinyin",
        ""
    ).strip()

    meaning = request.form.get(
        "meaning",
        ""
    ).strip()

    radical_id = request.form.get(
        "radical_id",
        type=int
    )

    stroke_count = request.form.get(
        "stroke_count",
        type=int
    )

    memory_tip = request.form.get(
        "memory_tip",
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

    if not character:

        flash(
            "Ký tự Chữ Hán không được để trống.",
            "error"
        )

        return redirect(
            url_for(
                "admin_hanzi.index",

                edit=hanzi_id,

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
                "admin_hanzi.index",

                edit=hanzi_id,

                page=return_page,

                course_id=return_course_id,

                lesson_id=return_lesson_id,

                status=return_status,

                q=return_keyword,
            )
        )


    if (
        stroke_count is not None
        and
        stroke_count <= 0
    ):

        flash(
            "Số nét phải lớn hơn 0.",
            "error"
        )

        return redirect(
            url_for(
                "admin_hanzi.index",

                edit=hanzi_id,

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


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # KIỂM TRA BỘ THỦ
            # =================================================

            if radical_id is not None:

                cursor.execute(
                    """
                    SELECT
                        MaBoThu

                    FROM dbo.BoThu

                    WHERE
                        MaBoThu = ?;
                    """,
                    radical_id
                )


                if cursor.fetchone() is None:

                    abort(
                        400,
                        description="Bộ thủ không tồn tại."
                    )


            # =================================================
            # UPDATE
            # =================================================

            cursor.execute(
                """
                UPDATE dbo.ChuHan

                SET
                    MaBoThu = ?,
                    KyTu = ?,
                    Pinyin = ?,
                    NghiaTiengViet = ?,
                    SoNet = ?,
                    CachGhiNho = ?,
                    ViDuTiengTrung = ?,
                    ViDuPinyin = ?,
                    ViDuTiengViet = ?,
                    ThuTu = ?,
                    TrangThai = ?,
                    MaQuanTriVienCapNhat = ?,
                    NgayCapNhat =
                        SYSDATETIME()

                WHERE
                    MaChuHan = ?;
                """,

                radical_id,

                character,

                pinyin
                or None,

                meaning
                or None,

                stroke_count,

                memory_tip
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

                hanzi_id
            )


            if cursor.rowcount == 0:

                abort(
                    404,
                    description="Không tìm thấy Chữ Hán."
                )


        connection.commit()


    flash(
        "Đã cập nhật Chữ Hán vào SQL Server.",
        "success"
    )


    return redirect(
        url_for(
            "admin_hanzi.index",

            page=return_page,

            course_id=return_course_id,

            lesson_id=return_lesson_id,

            status=return_status,

            q=return_keyword,
        )
    )


# =========================================================
# ĐỔI TRẠNG THÁI MỘT CHỮ HÁN
# =========================================================

@admin_hanzi_bp.post(
    "/<int:hanzi_id>/trang-thai"
)
def set_status(hanzi_id):

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
                UPDATE dbo.ChuHan

                SET
                    TrangThai = ?,
                    MaQuanTriVienCapNhat = ?,
                    NgayCapNhat =
                        SYSUTCDATETIME()

                WHERE
                    MaChuHan = ?;
                """,
                new_status,
                admin_id,
                hanzi_id
            )


            if cursor.rowcount == 0:

                abort(
                    404,
                    description="Không tìm thấy Chữ Hán."
                )


        connection.commit()


    flash(
        (
            "Đã chuyển Chữ Hán sang trạng thái "
            f"“{STATUSES[new_status]}”."
        ),
        "success"
    )


    return redirect(
        url_for(
            "admin_hanzi.index",

            page=return_page,

            course_id=return_course_id,

            lesson_id=return_lesson_id,

            status=return_status,

            q=return_keyword,
        )
    )


# =========================================================
# XUẤT BẢN TOÀN BỘ CHỮ HÁN CỦA KHÓA
# =========================================================

@admin_hanzi_bp.post(
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
            # KIỂM TRA KHÓA HỌC
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
            # UPDATE HÀNG LOẠT
            # =================================================

            cursor.execute(
                """
                UPDATE ch

                SET
                    ch.TrangThai =
                        'da_xuat_ban',

                    ch.MaQuanTriVienCapNhat = ?,

                    ch.NgayCapNhat =
                        SYSUTCDATETIME()

                OUTPUT
                    INSERTED.MaChuHan

                FROM dbo.ChuHan AS ch

                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc
                    = ch.MaBaiHoc

                WHERE
                    bh.MaKhoaHoc = ?
                    AND ch.TrangThai =
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
                f"Chữ Hán của khóa “{course[1]}”."
            ),
            "success"
        )

    else:

        flash(
            "Không còn Chữ Hán bản nháp cần xuất bản.",
            "success"
        )


    return redirect(
        url_for(
            "admin_hanzi.index",
            course_id=course_id
        )
    )

# =========================================================
# XUAT BAN TAT CA CHU HAN BAN NHAP
# =========================================================

@admin_hanzi_bp.post("/xuat-ban-tat-ca")
def publish_all():

    admin_id = int(g.account["id"])

    with closing(get_connection()) as connection:
        try:
            with closing(connection.cursor()) as cursor:
                cursor.execute(
                    """
                    UPDATE dbo.ChuHan
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
        f"Đã xuất bản {updated_count} chữ Hán.",
        "success"
    )

    return redirect(
        url_for("admin_hanzi.index")
    )
