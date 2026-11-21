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

admin_pinyin_bp = Blueprint(
    "admin_pinyin",
    __name__,
    url_prefix="/admin/pinyin",
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
# LOẠI ÂM
# =========================================================

SOUND_TYPES = {
    "thanh_mau": "Thanh mẫu",
    "van_mau": "Vận mẫu",
    "am_ghep": "Âm ghép",
}


# =========================================================
# KIỂM TRA ADMIN
# =========================================================

@admin_pinyin_bp.before_request
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
            description="Bạn không có quyền quản lý Pinyin."
        )


# =========================================================
# DATABASE ERROR
# =========================================================

@admin_pinyin_bp.errorhandler(
    pyodbc.Error
)
def handle_database_error(error):

    current_app.logger.error(
        "Loi SQL trong quan ly Pinyin: %s",
        type(error).__name__
    )

    return (
        "Chưa thể xử lý dữ liệu Pinyin. "
        "Vui lòng thử lại.",
        503
    )


# =========================================================
# DANH SÁCH PINYIN
# =========================================================

@admin_pinyin_bp.get("/")
def index():

    # =====================================================
    # BỘ LỌC
    # =====================================================

    keyword = request.args.get(
        "q",
        ""
    ).strip()

    sound_type = request.args.get(
        "sound_type",
        "all"
    )

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
    # VALIDATE FILTER
    # =====================================================

    if sound_type not in {
        "all",
        "thanh_mau",
        "van_mau",
        "am_ghep",
    }:

        sound_type = "all"


    if status not in {
        "all",
        "ban_nhap",
        "da_xuat_ban",
        "luu_tru",
    }:

        status = "all"


    pinyins = []

    editing_pinyin = None

    total_pinyins = 0

    total_pages = 1

    draft_count = 0


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # 1. ĐIỀU KIỆN LỌC
            # =================================================

            conditions = []

            params = []


            if sound_type != "all":

                conditions.append(
                    "bp.LoaiAm = ?"
                )

                params.append(
                    sound_type
                )


            if status != "all":

                conditions.append(
                    "bp.TrangThai = ?"
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
                            bp.KyHieu
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                bp.CachDoc,
                                N''
                            )
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                bp.ViDu,
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

                FROM dbo.BangPinyin AS bp
                """
                + where_sql,
                *params
            )


            total_pinyins = int(
                cursor.fetchone()[0]
                or 0
            )


            total_pages = max(
                1,
                (
                    total_pinyins
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
            # 3. DANH SÁCH CÓ PHÂN TRANG
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
                    bp.MaPinyin,
                    bp.LoaiAm,
                    bp.KyHieu,
                    bp.CachDoc,
                    bp.ViDu,
                    bp.MaTep,
                    bp.MaNguon,
                    bp.ThuTu,
                    bp.TrangThai,

                    tep.DuongDanTep,
                    tep.TieuDe

                FROM dbo.BangPinyin AS bp

                LEFT JOIN dbo.TepDaPhuongTien AS tep
                    ON tep.MaTep
                    = bp.MaTep
                """
                + where_sql
                + """
                ORDER BY
                    CASE bp.LoaiAm
                        WHEN 'thanh_mau' THEN 1
                        WHEN 'van_mau' THEN 2
                        WHEN 'am_ghep' THEN 3
                        ELSE 4
                    END,

                    bp.ThuTu,
                    bp.MaPinyin

                OFFSET ? ROWS

                FETCH NEXT ? ROWS ONLY;
                """,
                *list_params
            )


            for row in cursor.fetchall():

                pinyins.append(
                    {
                        "id": row[0],

                        "sound_type": row[1],

                        "symbol": row[2],

                        "pronunciation": row[3]
                        or "",

                        "example": row[4]
                        or "",

                        "media_id": row[5],

                        "source_id": row[6],

                        "order": row[7],

                        "status": row[8],

                        "media_path": row[9]
                        or "",

                        "media_title": row[10]
                        or "",
                    }
                )


            # =================================================
            # 4. ĐẾM TỔNG BẢN NHÁP
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.BangPinyin

                WHERE
                    TrangThai = 'ban_nhap';
                """
            )


            draft_count = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 5. PINYIN ĐANG SỬA
            # =================================================

            if edit_id is not None:

                cursor.execute(
                    """
                    SELECT
                        MaPinyin,
                        LoaiAm,
                        KyHieu,
                        CachDoc,
                        ViDu,
                        MaTep,
                        ThuTu,
                        TrangThai,
                        MaQuanTriVienCapNhat,
                        NgayCapNhat

                    FROM dbo.BangPinyin

                    WHERE
                        MaPinyin = ?;
                    """,
                    edit_id
                )


                row = cursor.fetchone()


                if row is None:

                    abort(
                        404,
                        description="Không tìm thấy Pinyin."
                    )


                editing_pinyin = {
                    "id": row[0],

                    "sound_type": row[1],

                    "symbol": row[2],

                    "pronunciation": row[3]
                    or "",

                    "example": row[4]
                    or "",

                    "media_id": row[5],

                    "order": row[6],

                    "status": row[7],

                    "admin_updated_id": row[8],

                    "updated_at": row[9],
                }


    return render_template(
        "admin/pinyin.html",

        active_page="materials",

        pinyins=pinyins,

        editing_pinyin=
            editing_pinyin,

        statuses=STATUSES,

        sound_types=SOUND_TYPES,

        selected_sound_type=
            sound_type,

        selected_status=status,

        keyword=keyword,

        draft_count=draft_count,

        page=page,

        per_page=per_page,

        total_pages=total_pages,

        total_pinyins=total_pinyins,
    )


# =========================================================
# SỬA PINYIN
# =========================================================

@admin_pinyin_bp.post(
    "/<int:pinyin_id>/sua"
)
def edit(pinyin_id):

    sound_type = request.form.get(
        "sound_type",
        ""
    ).strip()

    symbol = request.form.get(
        "symbol",
        ""
    ).strip()

    pronunciation = request.form.get(
        "pronunciation",
        ""
    ).strip()

    example = request.form.get(
        "example",
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
    # THÔNG TIN QUAY LẠI
    # =====================================================

    return_page = request.form.get(
        "return_page",
        1,
        type=int
    )

    return_sound_type = request.form.get(
        "return_sound_type",
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

    if sound_type not in SOUND_TYPES:

        abort(
            400,
            description="Loại âm không hợp lệ."
        )


    if not symbol:

        flash(
            "Ký hiệu Pinyin không được để trống.",
            "error"
        )

        return redirect(
            url_for(
                "admin_pinyin.index",

                edit=pinyin_id,

                page=return_page,

                sound_type=return_sound_type,

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
                "admin_pinyin.index",

                edit=pinyin_id,

                page=return_page,

                sound_type=return_sound_type,

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
                UPDATE dbo.BangPinyin

                SET
                    LoaiAm = ?,
                    KyHieu = ?,
                    CachDoc = ?,
                    ViDu = ?,
                    ThuTu = ?,
                    TrangThai = ?,
                    MaQuanTriVienCapNhat = ?,
                    NgayCapNhat =
                        SYSDATETIME()

                WHERE
                    MaPinyin = ?;
                """,

                sound_type,

                symbol,

                pronunciation
                or None,

                example
                or None,

                order,

                status,

                admin_id,

                pinyin_id
            )


            if cursor.rowcount == 0:

                abort(
                    404,
                    description="Không tìm thấy Pinyin."
                )


        connection.commit()


    flash(
        "Đã cập nhật Pinyin vào SQL Server.",
        "success"
    )


    return redirect(
        url_for(
            "admin_pinyin.index",

            page=return_page,

            sound_type=return_sound_type,

            status=return_status,

            q=return_keyword,
        )
    )


# =========================================================
# ĐỔI TRẠNG THÁI MỘT PINYIN
# =========================================================

@admin_pinyin_bp.post(
    "/<int:pinyin_id>/trang-thai"
)
def set_status(pinyin_id):

    new_status = request.form.get(
        "status",
        ""
    ).strip()


    return_page = request.form.get(
        "return_page",
        1,
        type=int
    )

    return_sound_type = request.form.get(
        "return_sound_type",
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
                UPDATE dbo.BangPinyin

                SET
                    TrangThai = ?,
                    MaQuanTriVienCapNhat = ?,
                    NgayCapNhat =
                        SYSUTCDATETIME()

                WHERE
                    MaPinyin = ?;
                """,
                new_status,
                admin_id,
                pinyin_id
            )


            if cursor.rowcount == 0:

                abort(
                    404,
                    description="Không tìm thấy Pinyin."
                )


        connection.commit()


    flash(
        (
            "Đã chuyển Pinyin sang trạng thái "
            f"“{STATUSES[new_status]}”."
        ),
        "success"
    )


    return redirect(
        url_for(
            "admin_pinyin.index",

            page=return_page,

            sound_type=return_sound_type,

            status=return_status,

            q=return_keyword,
        )
    )


# =========================================================
# XUẤT BẢN TOÀN BỘ PINYIN
# =========================================================

@admin_pinyin_bp.post(
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
                UPDATE dbo.BangPinyin

                SET
                    TrangThai =
                        'da_xuat_ban',

                    MaQuanTriVienCapNhat = ?,

                    NgayCapNhat =
                        SYSUTCDATETIME()

                OUTPUT
                    INSERTED.MaPinyin

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
                "mục Pinyin."
            ),
            "success"
        )

    else:

        flash(
            "Không còn Pinyin bản nháp cần xuất bản.",
            "success"
        )


    return redirect(
        url_for(
            "admin_pinyin.index"
        )
    )