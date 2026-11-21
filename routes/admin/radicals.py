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

admin_radicals_bp = Blueprint(
    "admin_radicals",
    __name__,
    url_prefix="/admin/bo-thu",
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

@admin_radicals_bp.before_request
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
            description="Bạn không có quyền quản lý Bộ thủ."
        )


# =========================================================
# XỬ LÝ LỖI DATABASE
# =========================================================

@admin_radicals_bp.errorhandler(
    pyodbc.Error
)
def handle_database_error(error):

    current_app.logger.error(
        "Loi SQL trong quan ly Bo Thu: %s",
        type(error).__name__
    )

    return (
        "Chưa thể xử lý dữ liệu Bộ thủ. "
        "Vui lòng thử lại.",
        503
    )


# =========================================================
# DANH SÁCH BỘ THỦ
#
# URL:
# /admin/bo-thu/
# =========================================================

@admin_radicals_bp.get("/")
def index():

    # =====================================================
    # BỘ LỌC
    # =====================================================

    keyword = request.args.get(
        "q",
        ""
    ).strip()

    status = request.args.get(
        "status",
        "all"
    )

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


    radicals = []

    editing_radical = None

    total_radicals = 0

    total_pages = 1

    draft_count = 0


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # 1. TẠO ĐIỀU KIỆN LỌC
            # =================================================

            conditions = []

            params = []


            if status != "all":

                conditions.append(
                    "bt.TrangThai = ?"
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
                            bt.KyHieu
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            bt.TenBoThu
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                bt.YNghia,
                                N''
                            )
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                bt.MoTa,
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
            # 2. ĐẾM TỔNG SAU KHI LỌC
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.BoThu AS bt
                """
                + where_sql,
                *params
            )


            total_radicals = int(
                cursor.fetchone()[0]
                or 0
            )


            total_pages = max(
                1,
                (
                    total_radicals
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
            # 3. DANH SÁCH BỘ THỦ CÓ PHÂN TRANG
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
                    bt.MaBoThu,
                    bt.KyHieu,
                    bt.TenBoThu,
                    bt.YNghia,
                    bt.SoNet,
                    bt.MoTa,
                    bt.MaTep,
                    bt.MaNguon,
                    bt.TrangThai,

                    tep.DuongDanTep,
                    tep.TieuDe,

                    (
                        SELECT
                            COUNT(*)

                        FROM dbo.ChuHan AS ch

                        WHERE
                            ch.MaBoThu
                            = bt.MaBoThu
                    ) AS SoChuHan

                FROM dbo.BoThu AS bt

                LEFT JOIN dbo.TepDaPhuongTien AS tep
                    ON tep.MaTep
                    = bt.MaTep
                """
                + where_sql
                + """
                ORDER BY
                    ISNULL(
                        bt.SoNet,
                        999
                    ),

                    bt.MaBoThu

                OFFSET ? ROWS

                FETCH NEXT ? ROWS ONLY;
                """,
                *list_params
            )


            for row in cursor.fetchall():

                radicals.append(
                    {
                        "id": row[0],

                        "symbol": row[1],

                        "name": row[2],

                        "meaning": row[3]
                        or "",

                        "stroke_count": row[4],

                        "description": row[5]
                        or "",

                        "media_id": row[6],

                        "source_id": row[7],

                        "status": row[8],

                        "media_path": row[9]
                        or "",

                        "media_title": row[10]
                        or "",

                        "hanzi_count": int(
                            row[11]
                            or 0
                        ),
                    }
                )


            # =================================================
            # 4. ĐẾM TỔNG BẢN NHÁP
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.BoThu

                WHERE
                    TrangThai = 'ban_nhap';
                """
            )


            draft_count = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 5. BỘ THỦ ĐANG SỬA
            # =================================================

            if edit_id is not None:

                cursor.execute(
                    """
                    SELECT
                        MaBoThu,
                        KyHieu,
                        TenBoThu,
                        YNghia,
                        SoNet,
                        MoTa,
                        MaTep,
                        TrangThai,
                        MaQuanTriVienCapNhat,
                        NgayCapNhat

                    FROM dbo.BoThu

                    WHERE
                        MaBoThu = ?;
                    """,
                    edit_id
                )


                row = cursor.fetchone()


                if row is None:

                    abort(
                        404,
                        description="Không tìm thấy Bộ thủ."
                    )


                editing_radical = {
                    "id": row[0],

                    "symbol": row[1],

                    "name": row[2],

                    "meaning": row[3]
                    or "",

                    "stroke_count": row[4],

                    "description": row[5]
                    or "",

                    "media_id": row[6],

                    "status": row[7],

                    "admin_updated_id": row[8],

                    "updated_at": row[9],
                }


    # =========================================================
    # RENDER
    # =========================================================

    return render_template(
        "admin/radicals.html",

        active_page="materials",

        radicals=radicals,

        editing_radical=
            editing_radical,

        statuses=STATUSES,

        selected_status=status,

        keyword=keyword,

        draft_count=draft_count,

        page=page,

        per_page=per_page,

        total_pages=total_pages,

        total_radicals=total_radicals,
    )


# =========================================================
# SỬA BỘ THỦ
# =========================================================

@admin_radicals_bp.post(
    "/<int:radical_id>/sua"
)
def edit(radical_id):

    symbol = request.form.get(
        "symbol",
        ""
    ).strip()

    name = request.form.get(
        "name",
        ""
    ).strip()

    meaning = request.form.get(
        "meaning",
        ""
    ).strip()

    stroke_count = request.form.get(
        "stroke_count",
        type=int
    )

    description = request.form.get(
        "description",
        ""
    ).strip()

    status = request.form.get(
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

    if not symbol:

        flash(
            "Ký hiệu Bộ thủ không được để trống.",
            "error"
        )

        return redirect(
            url_for(
                "admin_radicals.index",

                edit=radical_id,

                page=return_page,

                status=return_status,

                q=return_keyword,
            )
        )


    if not name:

        flash(
            "Tên Bộ thủ không được để trống.",
            "error"
        )

        return redirect(
            url_for(
                "admin_radicals.index",

                edit=radical_id,

                page=return_page,

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
                "admin_radicals.index",

                edit=radical_id,

                page=return_page,

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
    # UPDATE
    # =====================================================

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                UPDATE dbo.BoThu

                SET
                    KyHieu = ?,
                    TenBoThu = ?,
                    YNghia = ?,
                    SoNet = ?,
                    MoTa = ?,
                    TrangThai = ?,
                    MaQuanTriVienCapNhat = ?,
                    NgayCapNhat =
                        SYSDATETIME()

                WHERE
                    MaBoThu = ?;
                """,

                symbol,

                name,

                meaning
                or None,

                stroke_count,

                description
                or None,

                status,

                admin_id,

                radical_id
            )


            if cursor.rowcount == 0:

                abort(
                    404,
                    description="Không tìm thấy Bộ thủ."
                )


        connection.commit()


    flash(
        "Đã cập nhật Bộ thủ vào SQL Server.",
        "success"
    )


    return redirect(
        url_for(
            "admin_radicals.index",

            page=return_page,

            status=return_status,

            q=return_keyword,
        )
    )


# =========================================================
# ĐỔI TRẠNG THÁI MỘT BỘ THỦ
# =========================================================

@admin_radicals_bp.post(
    "/<int:radical_id>/trang-thai"
)
def set_status(radical_id):

    new_status = request.form.get(
        "status",
        ""
    ).strip()


    return_page = request.form.get(
        "return_page",
        1,
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
                UPDATE dbo.BoThu

                SET
                    TrangThai = ?,
                    MaQuanTriVienCapNhat = ?,
                    NgayCapNhat =
                        SYSUTCDATETIME()

                WHERE
                    MaBoThu = ?;
                """,
                new_status,
                admin_id,
                radical_id
            )


            if cursor.rowcount == 0:

                abort(
                    404,
                    description="Không tìm thấy Bộ thủ."
                )


        connection.commit()


    flash(
        (
            "Đã chuyển Bộ thủ sang trạng thái "
            f"“{STATUSES[new_status]}”."
        ),
        "success"
    )


    return redirect(
        url_for(
            "admin_radicals.index",

            page=return_page,

            status=return_status,

            q=return_keyword,
        )
    )


# =========================================================
# XUẤT BẢN TOÀN BỘ BỘ THỦ
# =========================================================

@admin_radicals_bp.post(
    "/xuat-ban-tat-ca"
)
def publish_all():

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
                UPDATE dbo.BoThu

                SET
                    TrangThai = 'da_xuat_ban',
                    MaQuanTriVienCapNhat = ?,
                    NgayCapNhat =
                        SYSUTCDATETIME()

                OUTPUT
                    INSERTED.MaBoThu

                WHERE
                    TrangThai = 'ban_nhap';
                """,
                admin_id
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
                "Bộ thủ."
            ),
            "success"
        )

    else:

        flash(
            "Không còn Bộ thủ bản nháp cần xuất bản.",
            "success"
        )


    return redirect(
        url_for(
            "admin_radicals.index"
        )
    )