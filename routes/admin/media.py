from contextlib import closing
from pathlib import Path, PurePosixPath
from uuid import uuid4
import re

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

admin_media_bp = Blueprint(
    "admin_media",
    __name__,
    url_prefix="/admin/media",
)


# =========================================================
# LOẠI TỆP
# =========================================================

MEDIA_TYPES = {
    "am_thanh": "Âm thanh",
    "hinh_anh": "Hình ảnh",
    "video": "Video",
}


# =========================================================
# TRẠNG THÁI SỬ DỤNG
# =========================================================

USAGE_FILTERS = {
    "all": "Tất cả",
    "used": "Đang được sử dụng",
    "unused": "Chưa được sử dụng",
}


# =========================================================
# ĐỊNH DẠNG FILE CHO PHÉP
# =========================================================

ALLOWED_EXTENSIONS = {

    "am_thanh": {
        ".mp3",
        ".wav",
        ".ogg",
        ".m4a",
    },

    "hinh_anh": {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    },

    "video": {
        ".mp4",
        ".webm",
    },
}


# =========================================================
# GIỚI HẠN DUNG LƯỢNG
#
# Âm thanh : 30 MB
# Hình ảnh : 10 MB
# Video    : 200 MB
# =========================================================

MAX_FILE_SIZES = {

    "am_thanh":
        30 * 1024 * 1024,

    "hinh_anh":
        10 * 1024 * 1024,

    "video":
        200 * 1024 * 1024,
}


# =========================================================
# THƯ MỤC LƯU THEO LOẠI
# =========================================================

UPLOAD_SUBFOLDERS = {
    "am_thanh": "audio",
    "hinh_anh": "images",
    "video": "video",
}


# =========================================================
# CÁC BẢNG ĐANG THAM CHIẾU TepDaPhuongTien
# =========================================================

USAGE_EXISTS_SQL = """
(
    EXISTS (
        SELECT 1
        FROM dbo.TuVung AS tv
        WHERE tv.MaAmThanh = media.MaTep
    )

    OR EXISTS (
        SELECT 1
        FROM dbo.ChuHan AS ch
        WHERE ch.MaTep = media.MaTep
    )

    OR EXISTS (
        SELECT 1
        FROM dbo.BangPinyin AS bp
        WHERE bp.MaTep = media.MaTep
    )

    OR EXISTS (
        SELECT 1
        FROM dbo.BoThu AS bt
        WHERE bt.MaTep = media.MaTep
    )

    OR EXISTS (
        SELECT 1
        FROM dbo.NguPhap AS np
        WHERE np.MaTep = media.MaTep
    )

    OR EXISTS (
        SELECT 1
        FROM dbo.QuyTacPhatAm AS qt
        WHERE qt.MaTep = media.MaTep
    )

    OR EXISTS (
        SELECT 1
        FROM dbo.NoiDungBaiHoc AS nd
        WHERE nd.MaTep = media.MaTep
    )

    OR EXISTS (
        SELECT 1
        FROM dbo.CauHoi AS chq
        WHERE chq.MaTep = media.MaTep
    )
)
"""


# =========================================================
# KIỂM TRA ADMIN
# =========================================================

@admin_media_bp.before_request
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
                "tệp đa phương tiện."
            )
        )


# =========================================================
# DATABASE ERROR
# =========================================================

@admin_media_bp.errorhandler(
    pyodbc.Error
)
def handle_database_error(error):

    current_app.logger.error(
        "Loi SQL trong quan ly media: %s",
        type(error).__name__
    )

    return (
        "Chưa thể xử lý dữ liệu media. "
        "Vui lòng thử lại.",
        503
    )


# =========================================================
# KIỂM TRA ĐƯỜNG DẪN MEDIA
# =========================================================

def inspect_media_path(
    database_path,
):

    raw_path = (
        database_path
        or ""
    ).strip()


    if not raw_path:

        return {
            "url": "",
            "state": "unknown",
        }


    # =====================================================
    # URL NGOÀI
    # =====================================================

    if re.match(
        r"^https?://",
        raw_path,
        flags=re.IGNORECASE,
    ):

        return {
            "url": raw_path,
            "state": "external",
        }


    normalized = raw_path.replace(
        "\\",
        "/"
    )


    # =====================================================
    # FILE NẰM TRONG STATIC
    # =====================================================

    if normalized.startswith(
        "/static/"
    ):

        relative_path = (
            normalized
            .lstrip("/")
        )

    elif normalized.startswith(
        "static/"
    ):

        relative_path = normalized

    else:

        return {
            "url": normalized,
            "state": "unknown",
        }


    local_path = (
        Path(
            current_app.root_path
        )
        .joinpath(
            *PurePosixPath(
                relative_path
            ).parts
        )
    )


    preview_url = (
        "/"
        + relative_path
    )


    if local_path.is_file():

        state = "exists"

    else:

        state = "missing"


    return {
        "url": preview_url,
        "state": state,
    }


# =========================================================
# THÔNG TIN QUAY LẠI TRANG
# =========================================================

def get_return_args():

    page = request.form.get(
        "return_page",
        1,
        type=int
    )


    if page is None or page < 1:

        page = 1


    return {

        "page": page,

        "q": request.form.get(
            "return_keyword",
            ""
        ).strip(),

        "file_type": request.form.get(
            "return_file_type",
            "all"
        ).strip(),

        "usage": request.form.get(
            "return_usage",
            "all"
        ).strip(),
    }


# =========================================================
# LẤY KÍCH THƯỚC FILE
# =========================================================

def get_uploaded_file_size(
    uploaded_file
):

    stream = uploaded_file.stream


    current_position = (
        stream.tell()
    )


    stream.seek(
        0,
        2
    )


    size = (
        stream.tell()
    )


    stream.seek(
        current_position
    )


    return size


# =========================================================
# DANH SÁCH MEDIA
# =========================================================

@admin_media_bp.get("/")
def index():

    # =====================================================
    # FILTER
    # =====================================================

    keyword = request.args.get(
        "q",
        ""
    ).strip()


    file_type = request.args.get(
        "file_type",
        "all"
    ).strip()


    usage = request.args.get(
        "usage",
        "all"
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
    # VALIDATE FILTER
    # =====================================================

    if (
        file_type != "all"
        and
        file_type not in MEDIA_TYPES
    ):

        file_type = "all"


    if usage not in USAGE_FILTERS:

        usage = "all"


    media_items = []

    editing_media = None


    stats = {
        "total": 0,
        "audio": 0,
        "image": 0,
        "video": 0,
    }


    total_items = 0

    total_pages = 1


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # THỐNG KÊ
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*),

                    SUM(
                        CASE
                            WHEN LoaiTep = 'am_thanh'
                            THEN 1
                            ELSE 0
                        END
                    ),

                    SUM(
                        CASE
                            WHEN LoaiTep = 'hinh_anh'
                            THEN 1
                            ELSE 0
                        END
                    ),

                    SUM(
                        CASE
                            WHEN LoaiTep = 'video'
                            THEN 1
                            ELSE 0
                        END
                    )

                FROM dbo.TepDaPhuongTien;
                """
            )


            row = cursor.fetchone()


            stats = {

                "total":
                    int(row[0] or 0),

                "audio":
                    int(row[1] or 0),

                "image":
                    int(row[2] or 0),

                "video":
                    int(row[3] or 0),
            }


            # =================================================
            # WHERE
            # =================================================

            conditions = []

            params = []


            if keyword:

                conditions.append(
                    """
                    (
                        CHARINDEX(
                            ?,
                            media.TieuDe
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            media.DuongDanTep
                        ) > 0

                        OR CHARINDEX(
                            ?,
                            ISNULL(
                                media.LoiThoai,
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


            if file_type != "all":

                conditions.append(
                    "media.LoaiTep = ?"
                )

                params.append(
                    file_type
                )


            if usage == "used":

                conditions.append(
                    USAGE_EXISTS_SQL
                )


            elif usage == "unused":

                conditions.append(
                    "NOT "
                    + USAGE_EXISTS_SQL
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
            # ĐẾM SAU FILTER
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.TepDaPhuongTien
                    AS media
                """
                + where_sql,
                *params
            )


            total_items = int(
                cursor.fetchone()[0]
                or 0
            )


            total_pages = max(
                1,
                (
                    total_items
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


            list_params = (
                params
                + [
                    offset,
                    per_page,
                ]
            )


            # =================================================
            # DANH SÁCH
            # =================================================

            cursor.execute(
                """
                SELECT
                    media.MaTep,
                    media.LoaiTep,
                    media.DuongDanTep,
                    media.TieuDe,
                    media.LoiThoai,
                    media.MaNguon,
                    media.NgayTao,

                    (
                        SELECT COUNT(*)
                        FROM dbo.TuVung AS tv
                        WHERE
                            tv.MaAmThanh
                            = media.MaTep
                    ),

                    (
                        SELECT COUNT(*)
                        FROM dbo.ChuHan AS ch
                        WHERE
                            ch.MaTep
                            = media.MaTep
                    ),

                    (
                        SELECT COUNT(*)
                        FROM dbo.BangPinyin AS bp
                        WHERE
                            bp.MaTep
                            = media.MaTep
                    ),

                    (
                        SELECT COUNT(*)
                        FROM dbo.BoThu AS bt
                        WHERE
                            bt.MaTep
                            = media.MaTep
                    ),

                    (
                        SELECT COUNT(*)
                        FROM dbo.NguPhap AS np
                        WHERE
                            np.MaTep
                            = media.MaTep
                    ),

                    (
                        SELECT COUNT(*)
                        FROM dbo.QuyTacPhatAm AS qt
                        WHERE
                            qt.MaTep
                            = media.MaTep
                    ),

                    (
                        SELECT COUNT(*)
                        FROM dbo.NoiDungBaiHoc AS nd
                        WHERE
                            nd.MaTep
                            = media.MaTep
                    ),

                    (
                        SELECT COUNT(*)
                        FROM dbo.CauHoi AS chq
                        WHERE
                            chq.MaTep
                            = media.MaTep
                    )

                FROM dbo.TepDaPhuongTien
                    AS media
                """
                + where_sql
                + """
                ORDER BY
                    media.NgayTao DESC,
                    media.MaTep DESC

                OFFSET ? ROWS

                FETCH NEXT ? ROWS ONLY;
                """,
                *list_params
            )


            for row in cursor.fetchall():

                usage_data = [

                    (
                        "Từ vựng",
                        int(row[7] or 0),
                    ),

                    (
                        "Chữ Hán",
                        int(row[8] or 0),
                    ),

                    (
                        "Pinyin",
                        int(row[9] or 0),
                    ),

                    (
                        "Bộ thủ",
                        int(row[10] or 0),
                    ),

                    (
                        "Ngữ pháp",
                        int(row[11] or 0),
                    ),

                    (
                        "Quy tắc phát âm",
                        int(row[12] or 0),
                    ),

                    (
                        "Nội dung bài học",
                        int(row[13] or 0),
                    ),

                    (
                        "Câu hỏi",
                        int(row[14] or 0),
                    ),
                ]


                usage_items = [

                    {
                        "label": label,
                        "count": count,
                    }

                    for (
                        label,
                        count
                    )
                    in usage_data

                    if count > 0
                ]


                usage_total = sum(
                    count
                    for (
                        _,
                        count
                    )
                    in usage_data
                )


                path_info = (
                    inspect_media_path(
                        row[2]
                    )
                )


                media_items.append(
                    {

                        "id": row[0],

                        "type": row[1],

                        "type_label":
                            MEDIA_TYPES.get(
                                row[1],
                                row[1]
                            ),

                        "path": row[2],

                        "title": row[3],

                        "transcript":
                            row[4]
                            or "",

                        "source_id":
                            row[5],

                        "created_at":
                            row[6],

                        "usage_items":
                            usage_items,

                        "usage_total":
                            usage_total,

                        "preview_url":
                            path_info["url"],

                        "path_state":
                            path_info["state"],
                    }
                )


            # =================================================
            # MEDIA ĐANG SỬA
            # =================================================

            if edit_id is not None:

                cursor.execute(
                    """
                    SELECT
                        MaTep,
                        LoaiTep,
                        DuongDanTep,
                        TieuDe,
                        LoiThoai,
                        MaNguon,
                        NgayTao,
                        MaQuanTriVienCapNhat,
                        NgayCapNhat

                    FROM dbo.TepDaPhuongTien

                    WHERE
                        MaTep = ?;
                    """,
                    edit_id
                )


                row = cursor.fetchone()


                if row is None:

                    abort(
                        404,
                        description=(
                            "Không tìm thấy tệp media."
                        )
                    )


                path_info = (
                    inspect_media_path(
                        row[2]
                    )
                )


                editing_media = {

                    "id": row[0],

                    "type": row[1],

                    "type_label":
                        MEDIA_TYPES.get(
                            row[1],
                            row[1]
                        ),

                    "path": row[2],

                    "title": row[3],

                    "transcript":
                        row[4]
                        or "",

                    "source_id":
                        row[5],

                    "created_at":
                        row[6],

                    "admin_updated_id":
                        row[7],

                    "updated_at":
                        row[8],

                    "preview_url":
                        path_info["url"],

                    "path_state":
                        path_info["state"],
                }


    return render_template(
        "admin/media.html",

        active_page="materials",

        media_items=media_items,

        editing_media=
            editing_media,

        media_types=MEDIA_TYPES,

        usage_filters=
            USAGE_FILTERS,

        selected_file_type=
            file_type,

        selected_usage=
            usage,

        keyword=keyword,

        stats=stats,

        page=page,

        per_page=per_page,

        total_pages=total_pages,

        total_items=total_items,
    )


# =========================================================
# THÊM TỆP MỚI
#
# File thật:
#
# static/uploads/media/audio/
# static/uploads/media/images/
# static/uploads/media/video/
#
# SQL:
#
# TepDaPhuongTien
# =========================================================

@admin_media_bp.post(
    "/them"
)
def add():

    # =====================================================
    # FORM
    # =====================================================

    file_type = request.form.get(
        "file_type",
        ""
    ).strip()


    title = request.form.get(
        "title",
        ""
    ).strip()


    transcript = request.form.get(
        "transcript",
        ""
    ).strip()


    uploaded_file = request.files.get(
        "file"
    )


    # =====================================================
    # KIỂM TRA LOẠI
    # =====================================================

    if file_type not in MEDIA_TYPES:

        flash(
            "Loại tệp không hợp lệ.",
            "error"
        )

        return redirect(
            url_for(
                "admin_media.index"
            )
        )


    # =====================================================
    # KIỂM TRA FILE
    # =====================================================

    if (
        uploaded_file is None
        or
        not uploaded_file.filename
    ):

        flash(
            "Bạn chưa chọn tệp để tải lên.",
            "error"
        )

        return redirect(
            url_for(
                "admin_media.index"
            )
        )


    original_filename = (
        uploaded_file.filename
        .strip()
    )


    extension = (
        Path(
            original_filename
        )
        .suffix
        .lower()
    )


    # =====================================================
    # KIỂM TRA EXTENSION
    # =====================================================

    if extension not in (
        ALLOWED_EXTENSIONS[
            file_type
        ]
    ):

        allowed_text = ", ".join(
            sorted(
                ALLOWED_EXTENSIONS[
                    file_type
                ]
            )
        )


        flash(
            (
                "Định dạng tệp không phù hợp với "
                f"“{MEDIA_TYPES[file_type]}”. "
                f"Cho phép: {allowed_text}"
            ),
            "error"
        )


        return redirect(
            url_for(
                "admin_media.index"
            )
        )


    # =====================================================
    # KIỂM TRA DUNG LƯỢNG
    # =====================================================

    try:

        file_size = (
            get_uploaded_file_size(
                uploaded_file
            )
        )

    except Exception:

        flash(
            "Không thể kiểm tra dung lượng tệp.",
            "error"
        )

        return redirect(
            url_for(
                "admin_media.index"
            )
        )


    max_size = (
        MAX_FILE_SIZES[
            file_type
        ]
    )


    if file_size <= 0:

        flash(
            "Tệp được chọn đang rỗng.",
            "error"
        )

        return redirect(
            url_for(
                "admin_media.index"
            )
        )


    if file_size > max_size:

        max_mb = (
            max_size
            // (
                1024 * 1024
            )
        )


        flash(
            (
                f"Tệp quá lớn. "
                f"{MEDIA_TYPES[file_type]} "
                f"tối đa {max_mb} MB."
            ),
            "error"
        )


        return redirect(
            url_for(
                "admin_media.index"
            )
        )


    # =====================================================
    # TỰ LẤY TÊN FILE LÀM TIÊU ĐỀ
    # NẾU ADMIN ĐỂ TRỐNG
    # =====================================================

    if not title:

        title = (
            Path(
                original_filename
            )
            .stem
            .strip()
        )


    if not title:

        title = (
            f"Media {MEDIA_TYPES[file_type]}"
        )


    if len(title) > 200:

        flash(
            "Tiêu đề không được vượt quá 200 ký tự.",
            "error"
        )

        return redirect(
            url_for(
                "admin_media.index"
            )
        )


    # =====================================================
    # TẠO TÊN FILE AN TOÀN
    #
    # Không dùng trực tiếp tên file do người dùng upload.
    # =====================================================

    unique_filename = (
        f"{uuid4().hex}"
        f"{extension}"
    )


    subfolder = (
        UPLOAD_SUBFOLDERS[
            file_type
        ]
    )


    # =====================================================
    # THƯ MỤC THẬT
    # =====================================================

    upload_directory = (
        Path(
            current_app.static_folder
        )
        / "uploads"
        / "media"
        / subfolder
    )


    upload_directory.mkdir(
        parents=True,
        exist_ok=True
    )


    destination = (
        upload_directory
        / unique_filename
    )


    # =====================================================
    # ĐƯỜNG DẪN LƯU VÀO SQL
    # =====================================================

    public_path = (
        "/static/"
        "uploads/"
        "media/"
        f"{subfolder}/"
        f"{unique_filename}"
    )


    # =====================================================
    # LƯU FILE
    # =====================================================

    try:

        uploaded_file.stream.seek(
            0
        )

        uploaded_file.save(
            destination
        )


        if (
            not destination.is_file()
            or
            destination.stat().st_size
            <= 0
        ):

            raise OSError(
                "File sau khi lưu không hợp lệ."
            )


    except OSError as error:

        current_app.logger.error(
            "Loi khi luu file media: %s",
            error
        )


        if destination.exists():

            try:
                destination.unlink()
            except OSError:
                pass


        flash(
            "Không thể lưu tệp vào thư mục static.",
            "error"
        )


        return redirect(
            url_for(
                "admin_media.index"
            )
        )


    # =====================================================
    # ADMIN ĐANG ĐĂNG NHẬP
    # =====================================================

    admin_id = int(
        g.account["id"]
    )


    # =====================================================
    # INSERT SQL
    # =====================================================

    try:

        with closing(
            get_connection()
        ) as connection:

            try:

                with closing(
                    connection.cursor()
                ) as cursor:

                    cursor.execute(
                        """
                        INSERT INTO dbo.TepDaPhuongTien
                        (
                            LoaiTep,
                            DuongDanTep,
                            TieuDe,
                            LoiThoai,
                            MaNguon,
                            MaQuanTriVienCapNhat,
                            NgayCapNhat
                        )

                        OUTPUT
                            INSERTED.MaTep

                        VALUES
                        (
                            ?,
                            ?,
                            ?,
                            ?,
                            NULL,
                            ?,
                            SYSUTCDATETIME()
                        );
                        """,

                        file_type,

                        public_path,

                        title,

                        transcript
                        or None,

                        admin_id,
                    )


                    row = cursor.fetchone()


                    if row is None:

                        raise RuntimeError(
                            "Không lấy được MaTep sau INSERT."
                        )


                    media_id = int(
                        row[0]
                    )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except Exception:

        # =================================================
        # SQL lỗi -> xóa file vừa lưu
        # để không tạo file rác.
        # =================================================

        if destination.exists():

            try:

                destination.unlink()

            except OSError:

                current_app.logger.warning(
                    (
                        "Khong xoa duoc file media "
                        "sau khi INSERT SQL that bai: %s"
                    ),
                    destination
                )


        raise


    flash(
        (
            f"Đã tải lên "
            f"{MEDIA_TYPES[file_type].lower()} "
            f"“{title}” "
            f"(MaTep = {media_id})."
        ),
        "success"
    )


    # =====================================================
    # LỌC THEO LOẠI VỪA THÊM
    # =====================================================

    return redirect(
        url_for(
            "admin_media.index",

            file_type=file_type,
        )
    )


# =========================================================
# SỬA METADATA
# =========================================================

@admin_media_bp.post(
    "/<int:media_id>/sua"
)
def edit(media_id):

    title = request.form.get(
        "title",
        ""
    ).strip()


    path = request.form.get(
        "path",
        ""
    ).strip()


    transcript = request.form.get(
        "transcript",
        ""
    ).strip()


    return_args = (
        get_return_args()
    )


    if not title:

        flash(
            "Tiêu đề tệp không được để trống.",
            "error"
        )

        return redirect(
            url_for(
                "admin_media.index",

                edit=media_id,

                **return_args,
            )
        )


    if len(title) > 200:

        flash(
            "Tiêu đề không được vượt quá 200 ký tự.",
            "error"
        )

        return redirect(
            url_for(
                "admin_media.index",

                edit=media_id,

                **return_args,
            )
        )


    if not path:

        flash(
            "Đường dẫn tệp không được để trống.",
            "error"
        )

        return redirect(
            url_for(
                "admin_media.index",

                edit=media_id,

                **return_args,
            )
        )


    if len(path) > 1000:

        flash(
            "Đường dẫn tệp không được vượt quá 1000 ký tự.",
            "error"
        )

        return redirect(
            url_for(
                "admin_media.index",

                edit=media_id,

                **return_args,
            )
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

        try:

            with closing(
                connection.cursor()
            ) as cursor:

                cursor.execute(
                    """
                    UPDATE dbo.TepDaPhuongTien

                    SET
                        TieuDe = ?,
                        DuongDanTep = ?,
                        LoiThoai = ?,
                        MaQuanTriVienCapNhat = ?,
                        NgayCapNhat =
                            SYSDATETIME()

                    WHERE
                        MaTep = ?;
                    """,

                    title,

                    path,

                    transcript
                    or None,

                    admin_id,

                    media_id,
                )


                if cursor.rowcount == 0:

                    abort(
                        404,
                        description=(
                            "Không tìm thấy tệp media."
                        )
                    )


            connection.commit()


        except Exception:

            connection.rollback()

            raise


    flash(
        (
            "Đã cập nhật thông tin media "
            "vào SQL Server."
        ),
        "success"
    )


    return redirect(
        url_for(
            "admin_media.index",
            **return_args,
        )
    )


# =========================================================
# XÓA MEDIA AN TOÀN
#
# Hiện tại:
# - chỉ xóa record SQL
# - chỉ xóa khi media chưa được nội dung nào dùng
# - chưa xóa file vật lý
# =========================================================

@admin_media_bp.post(
    "/<int:media_id>/xoa"
)
def delete(media_id):

    return_args = (
        get_return_args()
    )


    try:

        with closing(
            get_connection()
        ) as connection:

            try:

                with closing(
                    connection.cursor()
                ) as cursor:

                    cursor.execute(
                        """
                        SELECT
                            media.MaTep,
                            media.TieuDe,

                            (
                                SELECT COUNT(*)
                                FROM dbo.TuVung AS tv
                                WHERE
                                    tv.MaAmThanh
                                    = media.MaTep
                            )

                            +

                            (
                                SELECT COUNT(*)
                                FROM dbo.ChuHan AS ch
                                WHERE
                                    ch.MaTep
                                    = media.MaTep
                            )

                            +

                            (
                                SELECT COUNT(*)
                                FROM dbo.BangPinyin AS bp
                                WHERE
                                    bp.MaTep
                                    = media.MaTep
                            )

                            +

                            (
                                SELECT COUNT(*)
                                FROM dbo.BoThu AS bt
                                WHERE
                                    bt.MaTep
                                    = media.MaTep
                            )

                            +

                            (
                                SELECT COUNT(*)
                                FROM dbo.NguPhap AS np
                                WHERE
                                    np.MaTep
                                    = media.MaTep
                            )

                            +

                            (
                                SELECT COUNT(*)
                                FROM dbo.QuyTacPhatAm AS qt
                                WHERE
                                    qt.MaTep
                                    = media.MaTep
                            )

                            +

                            (
                                SELECT COUNT(*)
                                FROM dbo.NoiDungBaiHoc AS nd
                                WHERE
                                    nd.MaTep
                                    = media.MaTep
                            )

                            +

                            (
                                SELECT COUNT(*)
                                FROM dbo.CauHoi AS chq
                                WHERE
                                    chq.MaTep
                                    = media.MaTep
                            )

                            AS TongNoiDangDung

                        FROM dbo.TepDaPhuongTien
                            AS media

                        WHERE
                            media.MaTep = ?;
                        """,
                        media_id
                    )


                    row = cursor.fetchone()


                    if row is None:

                        abort(
                            404,
                            description=(
                                "Không tìm thấy tệp media."
                            )
                        )


                    usage_total = int(
                        row[2]
                        or 0
                    )


                    if usage_total > 0:

                        flash(
                            (
                                "Không thể xóa media "
                                f"“{row[1]}” vì đang được "
                                f"{usage_total} nội dung sử dụng."
                            ),
                            "error"
                        )


                        return redirect(
                            url_for(
                                "admin_media.index",
                                **return_args,
                            )
                        )


                    cursor.execute(
                        """
                        DELETE FROM dbo.TepDaPhuongTien

                        WHERE
                            MaTep = ?;
                        """,
                        media_id
                    )


                    if cursor.rowcount == 0:

                        abort(
                            404,
                            description=(
                                "Không tìm thấy tệp media."
                            )
                        )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except pyodbc.IntegrityError:

        flash(
            (
                "Không thể xóa media vì vẫn còn "
                "dữ liệu đang liên kết tới tệp này."
            ),
            "error"
        )


        return redirect(
            url_for(
                "admin_media.index",
                **return_args,
            )
        )


    flash(
        (
            "Đã xóa bản ghi media khỏi SQL Server. "
            "File vật lý vẫn được giữ lại để an toàn."
        ),
        "success"
    )


    return redirect(
        url_for(
            "admin_media.index",
            **return_args,
        )
    )