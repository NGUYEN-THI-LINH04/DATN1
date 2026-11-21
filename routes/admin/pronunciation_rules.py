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

admin_pronunciation_rules_bp = Blueprint(
    "admin_pronunciation_rules",
    __name__,
    url_prefix="/admin/quy-tac-phat-am",
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

@admin_pronunciation_rules_bp.before_request
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
            description=(
                "Bạn không có quyền quản lý "
                "quy tắc phát âm."
            )
        )


# =========================================================
# LỖI DATABASE
# =========================================================

@admin_pronunciation_rules_bp.errorhandler(
    pyodbc.Error
)
def handle_database_error(error):

    current_app.logger.error(
        "Loi SQL trong quan ly quy tac phat am: %s",
        type(error).__name__
    )

    return (
        "Chưa thể xử lý dữ liệu quy tắc phát âm.",
        503
    )


# =========================================================
# DANH SÁCH QUY TẮC PHÁT ÂM
# =========================================================

@admin_pronunciation_rules_bp.get("/")
def index():

    # =====================================================
    # FILTER
    # =====================================================

    keyword = request.args.get(
        "q",
        ""
    ).strip()

    rule_type = request.args.get(
        "rule_type",
        "all"
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
    # TRẠNG THÁI
    # =====================================================

    if status not in {
        "all",
        "ban_nhap",
        "da_xuat_ban",
        "luu_tru",
    }:

        status = "all"


    rule_types = []

    rules = []

    editing_rule = None

    total_rules = 0

    total_pages = 1

    draft_count = 0


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # 1. CÁC LOẠI QUY TẮC ĐANG CÓ
            # =================================================

            cursor.execute(
                """
                SELECT DISTINCT
                    LoaiQuyTac

                FROM dbo.QuyTacPhatAm

                WHERE
                    LoaiQuyTac IS NOT NULL
                    AND LTRIM(
                        RTRIM(
                            LoaiQuyTac
                        )
                    ) <> ''

                ORDER BY
                    LoaiQuyTac;
                """
            )


            rule_types = [
                row[0]
                for row in cursor.fetchall()
            ]


            # =================================================
            # 2. ĐIỀU KIỆN LỌC
            # =================================================

            conditions = []

            params = []


            if rule_type != "all":

                conditions.append(
                    "qt.LoaiQuyTac = ?"
                )

                params.append(
                    rule_type
                )


            if status != "all":

                conditions.append(
                    "qt.TrangThai = ?"
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
                            qt.TenQuyTac
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            qt.LoaiQuyTac
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            qt.NoiDung
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                qt.ViDuTiengTrung,
                                N''
                            )
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                qt.ViDuPinyin,
                                N''
                            )
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                qt.NghiaTiengViet,
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
            # 3. ĐẾM TỔNG SAU LỌC
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.QuyTacPhatAm AS qt
                """
                + where_sql,
                *params
            )


            total_rules = int(
                cursor.fetchone()[0]
                or 0
            )


            total_pages = max(
                1,
                (
                    total_rules
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
            # 4. DANH SÁCH CÓ PHÂN TRANG
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
                    qt.MaQuyTac,
                    qt.TenQuyTac,
                    qt.LoaiQuyTac,
                    qt.NoiDung,
                    qt.ViDuTiengTrung,
                    qt.ViDuPinyin,
                    qt.NghiaTiengViet,
                    qt.MaTep,
                    qt.MaNguon,
                    qt.ThuTu,
                    qt.TrangThai,

                    tep.DuongDanTep,
                    tep.TieuDe

                FROM dbo.QuyTacPhatAm AS qt

                LEFT JOIN dbo.TepDaPhuongTien AS tep
                    ON tep.MaTep
                    = qt.MaTep
                """
                + where_sql
                + """
                ORDER BY
                    qt.ThuTu,
                    qt.MaQuyTac

                OFFSET ? ROWS

                FETCH NEXT ? ROWS ONLY;
                """,
                *list_params
            )


            for row in cursor.fetchall():

                rules.append(
                    {
                        "id": row[0],

                        "name": row[1],

                        "rule_type": row[2],

                        "content": row[3],

                        "example_zh": row[4]
                        or "",

                        "example_pinyin": row[5]
                        or "",

                        "example_vi": row[6]
                        or "",

                        "media_id": row[7],

                        "source_id": row[8],

                        "order": row[9],

                        "status": row[10],

                        "media_path": row[11]
                        or "",

                        "media_title": row[12]
                        or "",
                    }
                )


            # =================================================
            # 5. ĐẾM BẢN NHÁP
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.QuyTacPhatAm

                WHERE
                    TrangThai = 'ban_nhap';
                """
            )


            draft_count = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 6. QUY TẮC ĐANG SỬA
            # =================================================

            if edit_id is not None:

                cursor.execute(
                    """
                    SELECT
                        MaQuyTac,
                        TenQuyTac,
                        LoaiQuyTac,
                        NoiDung,
                        ViDuTiengTrung,
                        ViDuPinyin,
                        NghiaTiengViet,
                        MaTep,
                        ThuTu,
                        TrangThai,
                        MaQuanTriVienCapNhat,
                        NgayCapNhat

                    FROM dbo.QuyTacPhatAm

                    WHERE
                        MaQuyTac = ?;
                    """,
                    edit_id
                )


                row = cursor.fetchone()


                if row is None:

                    abort(
                        404,
                        description=(
                            "Không tìm thấy "
                            "quy tắc phát âm."
                        )
                    )


                editing_rule = {
                    "id": row[0],

                    "name": row[1],

                    "rule_type": row[2],

                    "content": row[3],

                    "example_zh": row[4]
                    or "",

                    "example_pinyin": row[5]
                    or "",

                    "example_vi": row[6]
                    or "",

                    "media_id": row[7],

                    "order": row[8],

                    "status": row[9],

                    "admin_updated_id": row[10],

                    "updated_at": row[11],
                }


    return render_template(
        "admin/pronunciation_rules.html",

        active_page="materials",

        rules=rules,

        editing_rule=
            editing_rule,

        rule_types=rule_types,

        statuses=STATUSES,

        selected_rule_type=
            rule_type,

        selected_status=status,

        keyword=keyword,

        draft_count=draft_count,

        page=page,

        per_page=per_page,

        total_pages=total_pages,

        total_rules=total_rules,
    )


# =========================================================
# SỬA QUY TẮC PHÁT ÂM
# =========================================================

@admin_pronunciation_rules_bp.post(
    "/<int:rule_id>/sua"
)
def edit(rule_id):

    name = request.form.get(
        "name",
        ""
    ).strip()

    rule_type = request.form.get(
        "rule_type",
        ""
    ).strip()

    content = request.form.get(
        "content",
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
    # GIỮ TRANG/BỘ LỌC
    # =====================================================

    return_page = request.form.get(
        "return_page",
        1,
        type=int
    )

    return_rule_type = request.form.get(
        "return_rule_type",
        "all"
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

    if not name:

        flash(
            "Tên quy tắc không được để trống.",
            "error"
        )

        return redirect(
            url_for(
                "admin_pronunciation_rules.index",

                edit=rule_id,

                page=return_page,

                rule_type=return_rule_type,

                status=return_status,

                q=return_keyword,
            )
        )


    if not rule_type:

        flash(
            "Loại quy tắc không được để trống.",
            "error"
        )

        return redirect(
            url_for(
                "admin_pronunciation_rules.index",

                edit=rule_id,

                page=return_page,

                rule_type=return_rule_type,

                status=return_status,

                q=return_keyword,
            )
        )


    if not content:

        flash(
            "Nội dung quy tắc không được để trống.",
            "error"
        )

        return redirect(
            url_for(
                "admin_pronunciation_rules.index",

                edit=rule_id,

                page=return_page,

                rule_type=return_rule_type,

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
                "admin_pronunciation_rules.index",

                edit=rule_id,

                page=return_page,

                rule_type=return_rule_type,

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
                UPDATE dbo.QuyTacPhatAm

                SET
                    TenQuyTac = ?,
                    LoaiQuyTac = ?,
                    NoiDung = ?,
                    ViDuTiengTrung = ?,
                    ViDuPinyin = ?,
                    NghiaTiengViet = ?,
                    ThuTu = ?,
                    TrangThai = ?,
                    MaQuanTriVienCapNhat = ?,
                    NgayCapNhat =
                        SYSDATETIME()

                WHERE
                    MaQuyTac = ?;
                """,

                name,

                rule_type,

                content,

                example_zh
                or None,

                example_pinyin
                or None,

                example_vi
                or None,

                order,

                status,

                admin_id,

                rule_id
            )


            if cursor.rowcount == 0:

                abort(
                    404,
                    description=(
                        "Không tìm thấy "
                        "quy tắc phát âm."
                    )
                )


        connection.commit()


    flash(
        (
            "Đã cập nhật quy tắc phát âm "
            "vào SQL Server."
        ),
        "success"
    )


    return redirect(
        url_for(
            "admin_pronunciation_rules.index",

            page=return_page,

            rule_type=return_rule_type,

            status=return_status,

            q=return_keyword,
        )
    )


# =========================================================
# ĐỔI TRẠNG THÁI MỘT QUY TẮC
# =========================================================

@admin_pronunciation_rules_bp.post(
    "/<int:rule_id>/trang-thai"
)
def set_status(rule_id):

    new_status = request.form.get(
        "status",
        ""
    ).strip()


    return_page = request.form.get(
        "return_page",
        1,
        type=int
    )

    return_rule_type = request.form.get(
        "return_rule_type",
        "all"
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
                UPDATE dbo.QuyTacPhatAm

                SET
                    TrangThai = ?,
                    MaQuanTriVienCapNhat = ?,
                    NgayCapNhat =
                        SYSUTCDATETIME()

                WHERE
                    MaQuyTac = ?;
                """,
                new_status,
                admin_id,
                rule_id
            )


            if cursor.rowcount == 0:

                abort(
                    404,
                    description=(
                        "Không tìm thấy "
                        "quy tắc phát âm."
                    )
                )


        connection.commit()


    flash(
        (
            "Đã chuyển quy tắc sang trạng thái "
            f"“{STATUSES[new_status]}”."
        ),
        "success"
    )


    return redirect(
        url_for(
            "admin_pronunciation_rules.index",

            page=return_page,

            rule_type=return_rule_type,

            status=return_status,

            q=return_keyword,
        )
    )


# =========================================================
# XUẤT BẢN TOÀN BỘ
# =========================================================

@admin_pronunciation_rules_bp.post(
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
                UPDATE dbo.QuyTacPhatAm

                SET
                    TrangThai =
                        'da_xuat_ban',

                    MaQuanTriVienCapNhat = ?,

                    NgayCapNhat =
                        SYSUTCDATETIME()

                OUTPUT
                    INSERTED.MaQuyTac

                WHERE
                    TrangThai =
                        'ban_nhap';
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
                "quy tắc phát âm."
            ),
            "success"
        )

    else:

        flash(
            (
                "Không còn quy tắc phát âm "
                "bản nháp cần xuất bản."
            ),
            "success"
        )


    return redirect(
        url_for(
            "admin_pronunciation_rules.index"
        )
    )