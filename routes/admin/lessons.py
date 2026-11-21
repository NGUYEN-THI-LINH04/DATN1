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

admin_lessons_bp = Blueprint(
    "admin_lessons",
    __name__,
    url_prefix="/admin/bai-hoc",
)


# =========================================================
# TRẠNG THÁI BÀI HỌC
# =========================================================

STATUSES = {
    "ban_nhap": "Bản nháp",
    "da_xuat_ban": "Đã xuất bản",
    "luu_tru": "Lưu trữ",
}


# =========================================================
# KIỂM TRA QUYỀN ADMIN
# =========================================================

@admin_lessons_bp.before_request
def require_admin():

    account = getattr(
        g,
        "account",
        None,
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
                "Bạn không có quyền "
                "quản lý bài học."
            ),
        )


# =========================================================
# XỬ LÝ LỖI DATABASE
# =========================================================

@admin_lessons_bp.errorhandler(
    pyodbc.Error
)
def handle_database_error(error):

    current_app.logger.error(
        "Loi SQL trong quan ly bai hoc: %s",
        type(error).__name__,
    )

    return (
        "Chưa thể xử lý dữ liệu bài học. "
        "Vui lòng thử lại.",
        503,
    )


# =========================================================
# LẤY DANH SÁCH KHÓA HỌC
#
# Không cho tạo bài mới vào khóa đã lưu trữ.
# =========================================================

def get_available_courses():

    courses = []


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    kh.MaKhoaHoc,
                    kh.MaCapDo,
                    kh.TieuDe,
                    kh.TrangThai

                FROM dbo.KhoaHoc AS kh

                WHERE
                    kh.TrangThai <> 'luu_tru'

                ORDER BY
                    kh.MaCapDo,
                    kh.MaKhoaHoc;
                """
            )


            for row in cursor.fetchall():

                courses.append(
                    {
                        "id": row[0],
                        "level": row[1],
                        "title": row[2],
                        "status": row[3],
                    }
                )


    return courses


# =========================================================
# KIỂM TRA KHÓA HỌC TỒN TẠI
# =========================================================

def get_course(
    course_id
):

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    MaKhoaHoc,
                    MaCapDo,
                    TieuDe,
                    TrangThai

                FROM dbo.KhoaHoc

                WHERE
                    MaKhoaHoc = ?;
                """,
                course_id,
            )


            row = cursor.fetchone()


    if row is None:

        return None


    return {
        "id": row[0],
        "level": row[1],
        "title": row[2],
        "status": row[3],
    }


# =========================================================
# LẤY SỐ THỨ TỰ BÀI TIẾP THEO
#
# Ví dụ:
# khóa đã có bài 1 → 23
# thì gợi ý bài mới là 24.
# =========================================================

def get_next_lesson_order(
    course_id
):

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    ISNULL(
                        MAX(SoThuTuBai),
                        0
                    ) + 1

                FROM dbo.BaiHoc

                WHERE
                    MaKhoaHoc = ?;
                """,
                course_id,
            )


            row = cursor.fetchone()


    return int(
        row[0]
        or 1
    )


# =========================================================
# DANH SÁCH BÀI HỌC
#
# URL:
# /admin/bai-hoc/
# =========================================================

@admin_lessons_bp.get("/")
def index():

    course_id = request.args.get(
        "course_id",
        type=int,
    )


    courses = []

    lessons = []


    selected_course_info = None

    selected_course_draft_count = 0

    selected_course_total = 0


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # 1. DANH SÁCH KHÓA HỌC
            # =================================================

            cursor.execute(
                """
                SELECT
                    kh.MaKhoaHoc,
                    kh.MaCapDo,
                    kh.TieuDe,
                    kh.TrangThai

                FROM dbo.KhoaHoc AS kh

                ORDER BY
                    kh.MaCapDo,
                    kh.MaKhoaHoc;
                """
            )


            for row in cursor.fetchall():

                course = {
                    "id": row[0],
                    "level": row[1],
                    "title": row[2],
                    "status": row[3],
                }


                courses.append(
                    course
                )


                if (
                    course_id is not None
                    and
                    course["id"]
                    == course_id
                ):

                    selected_course_info = (
                        course
                    )


            # =================================================
            # KHÓA KHÔNG TỒN TẠI
            # =================================================

            if (
                course_id is not None
                and
                selected_course_info is None
            ):

                abort(
                    404,
                    description=(
                        "Không tìm thấy khóa học."
                    ),
                )


            # =================================================
            # 2. DANH SÁCH BÀI HỌC
            # =================================================

            sql = """
                SELECT
                    bh.MaBaiHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe,

                    kh.MaKhoaHoc,
                    kh.MaCapDo,
                    kh.TieuDe
                        AS TenKhoaHoc,

                    bh.TrangThai,

                    (
                        SELECT COUNT(*)

                        FROM dbo.TuVungBaiHoc
                            AS tvbh

                        WHERE
                            tvbh.MaBaiHoc
                            = bh.MaBaiHoc
                    ) AS SoTuVung,

                    (
                        SELECT COUNT(*)

                        FROM dbo.NguPhap
                            AS ng

                        WHERE
                            ng.MaBaiHoc
                            = bh.MaBaiHoc
                    ) AS SoNguPhap,

                    (
                        SELECT COUNT(*)

                        FROM dbo.ChuHan
                            AS ch

                        WHERE
                            ch.MaBaiHoc
                            = bh.MaBaiHoc
                    ) AS SoChuHan

                FROM dbo.BaiHoc AS bh

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc
                    = bh.MaKhoaHoc
            """


            params = []


            if course_id is not None:

                sql += """
                    WHERE
                        bh.MaKhoaHoc = ?
                """

                params.append(
                    course_id
                )


            sql += """
                ORDER BY
                    kh.MaCapDo,
                    kh.MaKhoaHoc,
                    bh.SoThuTuBai,
                    bh.MaBaiHoc;
            """


            cursor.execute(
                sql,
                *params,
            )


            for row in cursor.fetchall():

                vocabulary_count = int(
                    row[7]
                    or 0
                )


                grammar_count = int(
                    row[8]
                    or 0
                )


                hanzi_count = int(
                    row[9]
                    or 0
                )


                lessons.append(
                    {
                        "id": row[0],

                        "order": row[1],

                        "title": row[2],

                        "course_id": row[3],

                        "course_level":
                            row[4],

                        "course_title":
                            row[5],

                        "status": row[6],

                        "vocabulary_count":
                            vocabulary_count,

                        "grammar_count":
                            grammar_count,

                        "hanzi_count":
                            hanzi_count,

                        "content_count":
                            vocabulary_count
                            + grammar_count
                            + hanzi_count,
                    }
                )


            # =================================================
            # 3. THỐNG KÊ KHÓA ĐANG CHỌN
            # =================================================

            if course_id is not None:

                selected_course_total = len(
                    lessons
                )


                selected_course_draft_count = sum(
                    1

                    for lesson in lessons

                    if lesson["status"]
                    == "ban_nhap"
                )


    return render_template(
        "admin/lessons.html",

        active_page="lessons",

        courses=courses,

        lessons=lessons,

        selected_course=
            course_id,

        selected_course_info=
            selected_course_info,

        selected_course_total=
            selected_course_total,

        selected_course_draft_count=
            selected_course_draft_count,

        statuses=STATUSES,
    )


# =========================================================
# THÊM BÀI HỌC
#
# Đây mới chỉ tạo KHUNG bài học.
#
# Sau khi tạo:
# - bài luôn ở trạng thái ban_nhap
# - chưa tự thêm từ vựng
# - chưa tự thêm ngữ pháp
# - chưa tự thêm chữ Hán
# - chưa tự tạo bài tập
#
# URL:
# /admin/bai-hoc/them
# =========================================================

@admin_lessons_bp.route(
    "/them",
    methods=[
        "GET",
        "POST",
    ],
)
def add():

    courses = (
        get_available_courses()
    )


    # =====================================================
    # KHÔNG CÓ KHÓA HỌC KHẢ DỤNG
    # =====================================================

    if not courses:

        flash(
            (
                "Chưa có khóa học phù hợp "
                "để tạo bài học."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.index"
            )
        )


    # =====================================================
    # DỮ LIỆU FORM BAN ĐẦU
    # =====================================================

    selected_course_id = (
        request.args.get(
            "course_id",
            type=int,
        )
    )


    lesson = {
        "course_id":
            selected_course_id,

        "order": "",

        "title": "",

        "summary": "",
    }


    # =====================================================
    # NẾU TỪ DANH SÁCH ĐANG LỌC MỘT KHÓA
    # THÌ GỢI Ý LUÔN SỐ BÀI TIẾP THEO
    # =====================================================

    if selected_course_id is not None:

        selected_course = (
            get_course(
                selected_course_id
            )
        )


        if (
            selected_course is not None
            and
            selected_course["status"]
            != "luu_tru"
        ):

            lesson["order"] = (
                get_next_lesson_order(
                    selected_course_id
                )
            )


        else:

            lesson["course_id"] = None


    # =====================================================
    # GET → CHỈ HIỂN THỊ FORM
    # =====================================================

    if request.method == "GET":

        return render_template(
            "admin/lesson_form.html",

            active_page="lessons",

            courses=courses,

            lesson=lesson,
        )


    # =====================================================
    # POST → LẤY DỮ LIỆU ADMIN NHẬP
    # =====================================================

    lesson["course_id"] = (
        request.form.get(
            "course_id",
            type=int,
        )
    )


    lesson["order"] = (
        request.form.get(
            "order",
            type=int,
        )
    )


    lesson["title"] = (
        request.form.get(
            "title",
            "",
        )
        .strip()
    )


    lesson["summary"] = (
        request.form.get(
            "summary",
            "",
        )
        .strip()
    )


    # =====================================================
    # VALIDATE KHÓA HỌC
    # =====================================================

    selected_course = None


    for course in courses:

        if (
            course["id"]
            == lesson["course_id"]
        ):

            selected_course = (
                course
            )

            break


    if selected_course is None:

        flash(
            (
                "Hãy chọn một khóa học "
                "đang hoạt động."
            ),
            "error",
        )


        return render_template(
            "admin/lesson_form.html",

            active_page="lessons",

            courses=courses,

            lesson=lesson,
        ), 400


    # =====================================================
    # VALIDATE SỐ THỨ TỰ
    # =====================================================

    if (
        lesson["order"] is None
        or
        lesson["order"] <= 0
    ):

        flash(
            (
                "Số thứ tự bài phải "
                "lớn hơn 0."
            ),
            "error",
        )


        return render_template(
            "admin/lesson_form.html",

            active_page="lessons",

            courses=courses,

            lesson=lesson,
        ), 400


    # =====================================================
    # VALIDATE TIÊU ĐỀ
    # =====================================================

    if not (
        1
        <= len(
            lesson["title"]
        )
        <= 200
    ):

        flash(
            (
                "Tên bài học cần từ "
                "1 đến 200 ký tự."
            ),
            "error",
        )


        return render_template(
            "admin/lesson_form.html",

            active_page="lessons",

            courses=courses,

            lesson=lesson,
        ), 400


    # =====================================================
    # VALIDATE TÓM TẮT
    # =====================================================

    if len(
        lesson["summary"]
    ) > 2000:

        flash(
            (
                "Tóm tắt bài học không được "
                "quá 2.000 ký tự."
            ),
            "error",
        )


        return render_template(
            "admin/lesson_form.html",

            active_page="lessons",

            courses=courses,

            lesson=lesson,
        ), 400


    # =====================================================
    # ADMIN ĐANG TẠO BÀI
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


                    # =========================================
                    # KIỂM TRA TRÙNG SỐ THỨ TỰ
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            MaBaiHoc,
                            TieuDe

                        FROM dbo.BaiHoc

                        WHERE
                            MaKhoaHoc = ?
                            AND SoThuTuBai = ?;
                        """,
                        lesson["course_id"],
                        lesson["order"],
                    )


                    duplicated = (
                        cursor.fetchone()
                    )


                    if duplicated is not None:

                        flash(
                            (
                                f"Khóa này đã có "
                                f"Bài {lesson['order']}: "
                                f"“{duplicated[1]}”. "
                                f"Hãy chọn số thứ tự khác."
                            ),
                            "error",
                        )


                        return render_template(
                            "admin/lesson_form.html",

                            active_page="lessons",

                            courses=courses,

                            lesson=lesson,
                        ), 409


                    # =========================================
                    # TẠO KHUNG BÀI HỌC
                    #
                    # Bài mới LUÔN là bản nháp.
                    # =========================================

                    cursor.execute(
                        """
                        INSERT INTO dbo.BaiHoc
                        (
                            MaKhoaHoc,
                            SoThuTuBai,
                            TieuDe,
                            TomTat,
                            TrangThai,
                            MaQuanTriVienCapNhat,
                            NgayCapNhat
                        )

                        OUTPUT
                            INSERTED.MaBaiHoc

                        VALUES
                        (
                            ?,
                            ?,
                            ?,
                            ?,
                            'ban_nhap',
                            ?,
                            SYSUTCDATETIME()
                        );
                        """,

                        lesson["course_id"],

                        lesson["order"],

                        lesson["title"],

                        lesson["summary"]
                        or None,

                        admin_id,
                    )


                    new_lesson_id = int(
                        cursor.fetchone()[0]
                    )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    # =====================================================
    # RÀNG BUỘC SQL
    # =====================================================

    except pyodbc.IntegrityError:

        flash(
            (
                "Không thể tạo bài học. "
                "Số thứ tự có thể đã tồn tại "
                "trong khóa học này."
            ),
            "error",
        )


        return render_template(
            "admin/lesson_form.html",

            active_page="lessons",

            courses=courses,

            lesson=lesson,
        ), 409


    # =====================================================
    # THÀNH CÔNG
    # =====================================================

    flash(
        (
            f"Đã tạo Bài {lesson['order']} "
            f"“{lesson['title']}” "
            f"ở trạng thái Bản nháp."
        ),
        "success",
    )


    return redirect(
        url_for(
            "admin_lessons.index",

            course_id=
                lesson["course_id"],
        )
    )
# =========================================================
# CHI TIẾT / QUẢN LÝ MỘT BÀI HỌC
#
# URL:
# /admin/bai-hoc/<lesson_id>
# =========================================================

@admin_lessons_bp.get(
    "/<int:lesson_id>"
)
def detail(
    lesson_id
):

    lesson = None


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # 1. THÔNG TIN BÀI HỌC
            # =================================================

            cursor.execute(
                """
                SELECT
                    bh.MaBaiHoc,
                    bh.MaKhoaHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe,
                    bh.TomTat,
                    bh.TrangThai,
                    bh.NgayTao,
                    bh.NgayCapNhat,

                    kh.MaCapDo,
                    kh.TieuDe

                FROM dbo.BaiHoc AS bh

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc
                    = bh.MaKhoaHoc

                WHERE
                    bh.MaBaiHoc = ?;
                """,
                lesson_id,
            )


            row = cursor.fetchone()


            if row is None:

                abort(
                    404,
                    description=(
                        "Không tìm thấy bài học."
                    ),
                )


            lesson = {
                "id": row[0],

                "course_id": row[1],

                "order": row[2],

                "title": row[3],

                "summary":
                    row[4]
                    or "",

                "status": row[5],

                "created_at": row[6],

                "updated_at": row[7],

                "course_level": row[8],

                "course_title": row[9],
            }


            # =================================================
            # 2. ĐẾM TỪ VỰNG
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.TuVungBaiHoc

                WHERE
                    MaBaiHoc = ?;
                """,
                lesson_id,
            )


            lesson[
                "vocabulary_count"
            ] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 3. ĐẾM NGỮ PHÁP
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.NguPhap

                WHERE
                    MaBaiHoc = ?;
                """,
                lesson_id,
            )


            lesson[
                "grammar_count"
            ] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 4. ĐẾM CHỮ HÁN
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.ChuHan

                WHERE
                    MaBaiHoc = ?;
                """,
                lesson_id,
            )


            lesson[
                "hanzi_count"
            ] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 5. ĐẾM BÀI TẬP
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.BaiTap

                WHERE
                    MaBaiHoc = ?;
                """,
                lesson_id,
            )


            lesson[
                "exercise_count"
            ] = int(
                cursor.fetchone()[0]
                or 0
            )


    return render_template(
        "admin/lesson_detail.html",

        active_page="lessons",

        lesson=lesson,

        statuses=STATUSES,
    )
# =========================================================
# TỪ VỰNG CỦA MỘT BÀI HỌC
#
# Chức năng:
# - xem từ đang thuộc bài
# - tìm từ trong kho chưa được gắn vào bài
#
# URL:
# /admin/bai-hoc/<lesson_id>/tu-vung
# =========================================================

@admin_lessons_bp.get(
    "/<int:lesson_id>/tu-vung"
)
def vocabulary(
    lesson_id
):

    lesson = None

    vocabulary_items = []

    available_words = []


    # =====================================================
    # TỪ KHÓA TÌM TRONG KHO
    # =====================================================

    keyword = (
        request.args.get(
            "q",
            "",
        )
        .strip()[:200]
    )


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # 1. THÔNG TIN BÀI HỌC
            # =================================================

            cursor.execute(
                """
                SELECT
                    bh.MaBaiHoc,
                    bh.MaKhoaHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe,
                    bh.TomTat,
                    bh.TrangThai,

                    kh.MaCapDo,
                    kh.TieuDe

                FROM dbo.BaiHoc AS bh

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc
                    = bh.MaKhoaHoc

                WHERE
                    bh.MaBaiHoc = ?;
                """,
                lesson_id,
            )


            row = cursor.fetchone()


            if row is None:

                abort(
                    404,
                    description=(
                        "Không tìm thấy bài học."
                    ),
                )


            lesson = {
                "id": row[0],

                "course_id": row[1],

                "order": row[2],

                "title": row[3],

                "summary":
                    row[4]
                    or "",

                "status": row[5],

                "course_level":
                    row[6],

                "course_title":
                    row[7],
            }


            # =================================================
            # 2. TỪ VỰNG ĐANG THUỘC BÀI
            # =================================================

            cursor.execute(
                """
                SELECT
                    tv.MaTuVung,
                    tv.ChuHan,
                    tv.ChuPhonThe,
                    tv.PhienAm,
                    tv.NghiaTiengViet,
                    tv.TuLoai,
                    tv.ViDuTiengTrung,
                    tv.ViDuTiengViet,
                    tv.MaAmThanh,
                    tv.DaDuyet,

                    tvbh.ThuTu

                FROM dbo.TuVungBaiHoc
                    AS tvbh

                INNER JOIN dbo.TuVung
                    AS tv
                    ON tv.MaTuVung
                    = tvbh.MaTuVung

                WHERE
                    tvbh.MaBaiHoc = ?

                ORDER BY
                    tvbh.ThuTu,
                    tv.MaTuVung;
                """,
                lesson_id,
            )


            for row in cursor.fetchall():

                vocabulary_items.append(
                    {
                        "id": row[0],

                        "hanzi":
                            row[1]
                            or "",

                        "traditional":
                            row[2]
                            or "",

                        "pinyin":
                            row[3]
                            or "",

                        "meaning":
                            row[4]
                            or "",

                        "word_type":
                            row[5]
                            or "",

                        "example_zh":
                            row[6]
                            or "",

                        "example_vi":
                            row[7]
                            or "",

                        "audio_id":
                            row[8],

                        "approved":
                            bool(row[9]),

                        "order":
                            row[10],
                    }
                )


            lesson[
                "vocabulary_count"
            ] = len(
                vocabulary_items
            )


            # =================================================
            # 3. ĐẾM NGỮ PHÁP
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.NguPhap

                WHERE
                    MaBaiHoc = ?;
                """,
                lesson_id,
            )


            lesson["grammar_count"] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 4. ĐẾM CHỮ HÁN
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.ChuHan

                WHERE
                    MaBaiHoc = ?;
                """,
                lesson_id,
            )


            lesson["hanzi_count"] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 5. ĐẾM BÀI TẬP
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.BaiTap

                WHERE
                    MaBaiHoc = ?;
                """,
                lesson_id,
            )


            lesson["exercise_count"] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 6. TÌM TỪ TRONG KHO CHƯA CÓ TRONG BÀI
            #
            # Chỉ tìm khi Admin nhập từ khóa.
            # Tối đa 30 kết quả.
            # =================================================

            if keyword:

                cursor.execute(
                    """
                    SELECT TOP 30
                        tv.MaTuVung,
                        tv.ChuHan,
                        tv.PhienAm,
                        tv.NghiaTiengViet,
                        tv.TuLoai,
                        tv.DaDuyet,

                        (
                            SELECT COUNT(*)

                            FROM dbo.TuVungBaiHoc
                                AS other_usage

                            WHERE
                                other_usage.MaTuVung
                                = tv.MaTuVung
                        ) AS SoBaiDangDung

                    FROM dbo.TuVung AS tv

                    WHERE
                        tv.DaDuyet = 1

                        AND NOT EXISTS
                        (
                            SELECT 1

                            FROM dbo.TuVungBaiHoc
                                AS current_lesson

                            WHERE
                                current_lesson.MaBaiHoc = ?

                                AND current_lesson.MaTuVung
                                = tv.MaTuVung
                        )

                        AND
                        (
                            CHARINDEX(
                                ?,
                                tv.ChuHan
                            ) > 0

                            OR CHARINDEX(
                                ?,
                                tv.PhienAm
                            ) > 0

                            OR CHARINDEX(
                                ?,
                                tv.NghiaTiengViet
                            ) > 0
                        )

                    ORDER BY
                        tv.MaTuVung;
                    """,

                    lesson_id,

                    keyword,

                    keyword,

                    keyword,
                )


                for row in cursor.fetchall():

                    available_words.append(
                        {
                            "id": row[0],

                            "hanzi":
                                row[1]
                                or "",

                            "pinyin":
                                row[2]
                                or "",

                            "meaning":
                                row[3]
                                or "",

                            "word_type":
                                row[4]
                                or "",

                            "approved":
                                bool(row[5]),

                            "lesson_count":
                                int(
                                    row[6]
                                    or 0
                                ),
                        }
                    )


    return render_template(
        "admin/lesson_vocabulary.html",

        active_page="lessons",

        lesson=lesson,

        vocabulary_items=
            vocabulary_items,

        available_words=
            available_words,

        keyword=keyword,

        statuses=STATUSES,
    )
# =========================================================
# GẮN TỪ VỰNG VÀO BÀI HỌC
#
# POST:
# /admin/bai-hoc/<lesson_id>/tu-vung/<vocabulary_id>/gan
# =========================================================

@admin_lessons_bp.post(
    "/<int:lesson_id>/tu-vung/"
    "<int:vocabulary_id>/gan"
)
def attach_vocabulary(
    lesson_id,
    vocabulary_id,
):

    # =====================================================
    # TỪ KHÓA TÌM KIẾM ĐỂ QUAY LẠI
    # =====================================================

    return_keyword = (
        request.form.get(
            "return_keyword",
            "",
        )
        .strip()[:200]
    )


    try:

        with closing(
            get_connection()
        ) as connection:

            try:

                with closing(
                    connection.cursor()
                ) as cursor:


                    # =========================================
                    # 1. KIỂM TRA BÀI HỌC
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            MaBaiHoc,
                            TieuDe

                        FROM dbo.BaiHoc

                        WHERE
                            MaBaiHoc = ?;
                        """,
                        lesson_id,
                    )


                    lesson_row = (
                        cursor.fetchone()
                    )


                    if lesson_row is None:

                        abort(
                            404,
                            description=(
                                "Không tìm thấy bài học."
                            ),
                        )


                    # =========================================
                    # 2. KIỂM TRA TỪ VỰNG
                    #
                    # Chỉ cho gắn từ đã duyệt.
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            MaTuVung,
                            ChuHan,
                            DaDuyet

                        FROM dbo.TuVung

                        WHERE
                            MaTuVung = ?;
                        """,
                        vocabulary_id,
                    )


                    word_row = (
                        cursor.fetchone()
                    )


                    if word_row is None:

                        abort(
                            404,
                            description=(
                                "Không tìm thấy từ vựng."
                            ),
                        )


                    if not bool(
                        word_row[2]
                    ):

                        flash(
                            (
                                f"Từ “{word_row[1]}” "
                                f"chưa được duyệt nên "
                                f"không thể gắn vào bài."
                            ),
                            "error",
                        )


                        return redirect(
                            url_for(
                                "admin_lessons.vocabulary",

                                lesson_id=
                                    lesson_id,

                                q=
                                    return_keyword,
                            )
                        )


                    # =========================================
                    # 3. KIỂM TRA ĐÃ GẮN CHƯA
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            1

                        FROM dbo.TuVungBaiHoc

                        WHERE
                            MaBaiHoc = ?
                            AND MaTuVung = ?;
                        """,

                        lesson_id,

                        vocabulary_id,
                    )


                    if (
                        cursor.fetchone()
                        is not None
                    ):

                        flash(
                            (
                                f"Từ “{word_row[1]}” "
                                f"đã có trong bài học."
                            ),
                            "error",
                        )


                        return redirect(
                            url_for(
                                "admin_lessons.vocabulary",

                                lesson_id=
                                    lesson_id,

                                q=
                                    return_keyword,
                            )
                        )


                    # =========================================
                    # 4. LẤY THỨ TỰ TIẾP THEO
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            ISNULL(
                                MAX(ThuTu),
                                0
                            ) + 1

                        FROM dbo.TuVungBaiHoc

                        WHERE
                            MaBaiHoc = ?;
                        """,
                        lesson_id,
                    )


                    next_order = int(
                        cursor.fetchone()[0]
                        or 1
                    )


                    # =========================================
                    # 5. GẮN TỪ VÀO BÀI
                    # =========================================

                    cursor.execute(
                        """
                        INSERT INTO dbo.TuVungBaiHoc
                        (
                            MaBaiHoc,
                            MaTuVung,
                            ThuTu
                        )

                        VALUES
                        (
                            ?,
                            ?,
                            ?
                        );
                        """,

                        lesson_id,

                        vocabulary_id,

                        next_order,
                    )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except pyodbc.IntegrityError:

        flash(
            (
                "Không thể gắn từ vào bài. "
                "Liên kết có thể đã tồn tại."
            ),
            "error",
        )


    else:

        flash(
            (
                f"Đã gắn từ "
                f"“{word_row[1]}” "
                f"vào Bài học."
            ),
            "success",
        )


    return redirect(
        url_for(
            "admin_lessons.vocabulary",

            lesson_id=
                lesson_id,

            q=
                return_keyword,
        )
    )

# =========================================================
# BỎ TỪ VỰNG KHỎI BÀI HỌC
#
# CHỈ xóa liên kết trong TuVungBaiHoc.
# KHÔNG xóa từ khỏi bảng TuVung.
#
# POST:
# /admin/bai-hoc/<lesson_id>/tu-vung/<vocabulary_id>/bo
# =========================================================

@admin_lessons_bp.post(
    "/<int:lesson_id>/tu-vung/"
    "<int:vocabulary_id>/bo"
)
def detach_vocabulary(
    lesson_id,
    vocabulary_id,
):

    try:

        with closing(
            get_connection()
        ) as connection:

            try:

                with closing(
                    connection.cursor()
                ) as cursor:


                    # =========================================
                    # 1. KIỂM TRA BÀI HỌC
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            MaBaiHoc,
                            TieuDe

                        FROM dbo.BaiHoc

                        WHERE
                            MaBaiHoc = ?;
                        """,
                        lesson_id,
                    )


                    lesson_row = (
                        cursor.fetchone()
                    )


                    if lesson_row is None:

                        abort(
                            404,
                            description=(
                                "Không tìm thấy bài học."
                            ),
                        )


                    # =========================================
                    # 2. KIỂM TRA LIÊN KẾT
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            tvbh.ThuTu,
                            tv.ChuHan

                        FROM dbo.TuVungBaiHoc
                            AS tvbh

                        INNER JOIN dbo.TuVung
                            AS tv

                            ON tv.MaTuVung
                            = tvbh.MaTuVung

                        WHERE
                            tvbh.MaBaiHoc = ?
                            AND tvbh.MaTuVung = ?;
                        """,

                        lesson_id,

                        vocabulary_id,
                    )


                    relation = (
                        cursor.fetchone()
                    )


                    if relation is None:

                        flash(
                            (
                                "Từ này không còn "
                                "thuộc bài học."
                            ),
                            "error",
                        )


                        return redirect(
                            url_for(
                                "admin_lessons.vocabulary",

                                lesson_id=
                                    lesson_id,
                            )
                        )


                    removed_order = int(
                        relation[0]
                    )


                    word_hanzi = (
                        relation[1]
                        or ""
                    )


                    # =========================================
                    # 3. XÓA LIÊN KẾT
                    # =========================================

                    cursor.execute(
                        """
                        DELETE
                        FROM dbo.TuVungBaiHoc

                        WHERE
                            MaBaiHoc = ?
                            AND MaTuVung = ?;
                        """,

                        lesson_id,

                        vocabulary_id,
                    )


                    # =========================================
                    # 4. DỒN LẠI THỨ TỰ
                    #
                    # Ví dụ:
                    #
                    # 1 你
                    # 2 好
                    # 3 我
                    #
                    # Xóa 好
                    #
                    # => 1 你
                    #    2 我
                    # =========================================

                    cursor.execute(
                        """
                        UPDATE dbo.TuVungBaiHoc

                        SET
                            ThuTu =
                                ThuTu - 1

                        WHERE
                            MaBaiHoc = ?

                            AND ThuTu > ?;
                        """,

                        lesson_id,

                        removed_order,
                    )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except pyodbc.Error:

        current_app.logger.error(
            (
                "Loi SQL khi bo "
                "tu vung khoi bai hoc."
            )
        )


        flash(
            (
                "Chưa thể bỏ từ "
                "khỏi bài học."
            ),
            "error",
        )


    else:

        flash(
            (
                f"Đã bỏ từ "
                f"“{word_hanzi}” "
                f"khỏi bài học."
            ),
            "success",
        )


    return redirect(
        url_for(
            "admin_lessons.vocabulary",

            lesson_id=
                lesson_id,
        )
    )
# =========================================================
# ĐỔI THỨ TỰ TỪ VỰNG TRONG BÀI HỌC
#
# POST:
# /admin/bai-hoc/<lesson_id>/tu-vung/thu-tu
#
# Quy tắc:
# - phải nhập đủ thứ tự từ 1 -> N
# - không được trùng nhau
# - chỉ thay đổi TuVungBaiHoc.ThuTu
# - không sửa dữ liệu gốc trong TuVung
# =========================================================

@admin_lessons_bp.post(
    "/<int:lesson_id>/tu-vung/thu-tu"
)
def reorder_vocabulary(
    lesson_id
):

    # =====================================================
    # 1. LẤY TOÀN BỘ TỪ ĐANG THUỘC BÀI
    # =====================================================

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    tvbh.MaTuVung,
                    tvbh.ThuTu,
                    tv.ChuHan

                FROM dbo.TuVungBaiHoc
                    AS tvbh

                INNER JOIN dbo.TuVung
                    AS tv
                    ON tv.MaTuVung
                    = tvbh.MaTuVung

                WHERE
                    tvbh.MaBaiHoc = ?

                ORDER BY
                    tvbh.ThuTu,
                    tvbh.MaTuVung;
                """,
                lesson_id,
            )


            current_rows = (
                cursor.fetchall()
            )


    # =====================================================
    # 2. KHÔNG CÓ TỪ
    # =====================================================

    if not current_rows:

        flash(
            (
                "Bài học chưa có từ vựng "
                "để thay đổi thứ tự."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.vocabulary",
                lesson_id=lesson_id,
            )
        )


    # =====================================================
    # 3. ĐỌC THỨ TỰ ADMIN NHẬP
    #
    # form có dạng:
    # order_15 = 1
    # order_20 = 2
    # ...
    # =====================================================

    new_orders = {}


    for row in current_rows:

        vocabulary_id = int(
            row[0]
        )


        field_name = (
            f"order_{vocabulary_id}"
        )


        raw_value = (
            request.form.get(
                field_name,
                ""
            )
            .strip()
        )


        try:

            order_value = int(
                raw_value
            )

        except (
            TypeError,
            ValueError,
        ):

            flash(
                (
                    "Thứ tự từ vựng "
                    "phải là số nguyên."
                ),
                "error",
            )


            return redirect(
                url_for(
                    "admin_lessons.vocabulary",
                    lesson_id=lesson_id,
                )
            )


        new_orders[
            vocabulary_id
        ] = order_value


    # =====================================================
    # 4. KIỂM TRA PHẠM VI
    #
    # Nếu có 5 từ:
    # chỉ được dùng 1,2,3,4,5
    # =====================================================

    total_words = len(
        current_rows
    )


    expected_orders = set(
        range(
            1,
            total_words + 1,
        )
    )


    submitted_orders = set(
        new_orders.values()
    )


    if submitted_orders != expected_orders:

        flash(
            (
                "Thứ tự không hợp lệ. "
                f"Bài có {total_words} từ nên "
                f"cần dùng đủ các số từ "
                f"1 đến {total_words}, "
                f"không được trùng hoặc bỏ số."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.vocabulary",
                lesson_id=lesson_id,
            )
        )


    # =====================================================
    # 5. UPDATE TRONG TRANSACTION
    #
    # SQL có UNIQUE:
    # (MaBaiHoc, ThuTu)
    #
    # Vì vậy không thể đổi trực tiếp 1 <-> 2.
    #
    # Ta làm:
    #
    # Bước A:
    # 1 -> 1000001
    # 2 -> 1000002
    #
    # Bước B:
    # ghi lại 1,2,... theo thứ tự mới.
    # =====================================================

    try:

        with closing(
            get_connection()
        ) as connection:

            try:

                with closing(
                    connection.cursor()
                ) as cursor:


                    # =========================================
                    # KIỂM TRA BÀI HỌC
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            MaBaiHoc

                        FROM dbo.BaiHoc

                        WHERE
                            MaBaiHoc = ?;
                        """,
                        lesson_id,
                    )


                    if (
                        cursor.fetchone()
                        is None
                    ):

                        abort(
                            404,
                            description=(
                                "Không tìm thấy bài học."
                            ),
                        )


                    # =========================================
                    # BƯỚC A
                    # ĐẨY THỨ TỰ SANG VÙNG TẠM
                    # =========================================

                    temporary_offset = (
                        1000000
                    )


                    cursor.execute(
                        """
                        UPDATE dbo.TuVungBaiHoc

                        SET
                            ThuTu =
                                ThuTu + ?

                        WHERE
                            MaBaiHoc = ?;
                        """,

                        temporary_offset,

                        lesson_id,
                    )


                    # =========================================
                    # BƯỚC B
                    # GHI THỨ TỰ MỚI
                    # =========================================

                    for (
                        vocabulary_id,
                        new_order,
                    ) in new_orders.items():

                        cursor.execute(
                            """
                            UPDATE dbo.TuVungBaiHoc

                            SET
                                ThuTu = ?

                            WHERE
                                MaBaiHoc = ?
                                AND MaTuVung = ?;
                            """,

                            new_order,

                            lesson_id,

                            vocabulary_id,
                        )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except pyodbc.Error:

        current_app.logger.error(
            (
                "Loi SQL khi doi "
                "thu tu tu vung."
            )
        )


        flash(
            (
                "Chưa thể cập nhật "
                "thứ tự từ vựng."
            ),
            "error",
        )


    else:

        flash(
            (
                "Đã cập nhật thứ tự "
                "từ vựng trong bài học."
            ),
            "success",
        )


    return redirect(
        url_for(
            "admin_lessons.vocabulary",

            lesson_id=
                lesson_id,
        )
    )
# =========================================================
# NGỮ PHÁP CỦA MỘT BÀI HỌC
#
# Chức năng:
# - xem danh sách ngữ pháp trong bài
# - mở form thêm ngữ pháp mới
#
# URL:
# /admin/bai-hoc/<lesson_id>/ngu-phap
# =========================================================

@admin_lessons_bp.get(
    "/<int:lesson_id>/ngu-phap"
)
def grammar(
    lesson_id
):

    lesson = None

    grammar_items = []


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # 1. THÔNG TIN BÀI HỌC
            # =================================================

            cursor.execute(
                """
                SELECT
                    bh.MaBaiHoc,
                    bh.MaKhoaHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe,
                    bh.TomTat,
                    bh.TrangThai,

                    kh.MaCapDo,
                    kh.TieuDe

                FROM dbo.BaiHoc AS bh

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc
                    = bh.MaKhoaHoc

                WHERE
                    bh.MaBaiHoc = ?;
                """,
                lesson_id,
            )


            row = cursor.fetchone()


            if row is None:

                abort(
                    404,
                    description=(
                        "Không tìm thấy bài học."
                    ),
                )


            lesson = {
                "id": row[0],

                "course_id": row[1],

                "order": row[2],

                "title": row[3],

                "summary":
                    row[4]
                    or "",

                "status": row[5],

                "course_level":
                    row[6],

                "course_title":
                    row[7],
            }


            # =================================================
            # 2. DANH SÁCH NGỮ PHÁP
            # =================================================

            cursor.execute(
                """
                SELECT
                    ng.MaNguPhap,
                    ng.TenCauTruc,
                    ng.MoTa,
                    ng.CachDung,
                    ng.ViDuTiengTrung,
                    ng.ViDuPinyin,
                    ng.ViDuTiengViet,
                    ng.MaTep,
                    ng.ThuTu,
                    ng.TrangThai

                FROM dbo.NguPhap AS ng

                WHERE
                    ng.MaBaiHoc = ?

                ORDER BY
                    ng.ThuTu,
                    ng.MaNguPhap;
                """,
                lesson_id,
            )


            for row in cursor.fetchall():

                grammar_items.append(
                    {
                        "id": row[0],

                        "structure":
                            row[1]
                            or "",

                        "description":
                            row[2]
                            or "",

                        "usage":
                            row[3]
                            or "",

                        "example_zh":
                            row[4]
                            or "",

                        "example_pinyin":
                            row[5]
                            or "",

                        "example_vi":
                            row[6]
                            or "",

                        "media_id":
                            row[7],

                        "order":
                            row[8],

                        "status":
                            row[9],
                    }
                )


            lesson["grammar_count"] = len(
                grammar_items
            )


            # =================================================
            # 3. ĐẾM TỪ VỰNG
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.TuVungBaiHoc

                WHERE
                    MaBaiHoc = ?;
                """,
                lesson_id,
            )


            lesson["vocabulary_count"] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 4. ĐẾM CHỮ HÁN
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.ChuHan

                WHERE
                    MaBaiHoc = ?;
                """,
                lesson_id,
            )


            lesson["hanzi_count"] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 5. ĐẾM BÀI TẬP
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.BaiTap

                WHERE
                    MaBaiHoc = ?;
                """,
                lesson_id,
            )


            lesson["exercise_count"] = int(
                cursor.fetchone()[0]
                or 0
            )


    return render_template(
        "admin/lesson_grammar.html",

        active_page="lessons",

        lesson=lesson,

        grammar_items=
            grammar_items,

        statuses=STATUSES,
    )


# =========================================================
# THÊM NGỮ PHÁP VÀO BÀI HỌC
#
# POST:
# /admin/bai-hoc/<lesson_id>/ngu-phap/them
# =========================================================

@admin_lessons_bp.post(
    "/<int:lesson_id>/ngu-phap/them"
)
def add_grammar(
    lesson_id
):

    # =====================================================
    # 1. LẤY DỮ LIỆU FORM
    # =====================================================

    structure = (
        request.form.get(
            "structure",
            "",
        )
        .strip()
    )


    description = (
        request.form.get(
            "description",
            "",
        )
        .strip()
    )


    usage = (
        request.form.get(
            "usage",
            "",
        )
        .strip()
    )


    example_zh = (
        request.form.get(
            "example_zh",
            "",
        )
        .strip()
    )


    example_pinyin = (
        request.form.get(
            "example_pinyin",
            "",
        )
        .strip()
    )


    example_vi = (
        request.form.get(
            "example_vi",
            "",
        )
        .strip()
    )


    # =====================================================
    # 2. VALIDATE
    # =====================================================

    if not structure:

        flash(
            (
                "Tên cấu trúc ngữ pháp "
                "không được để trống."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.grammar",
                lesson_id=lesson_id,
            )
        )


    if len(structure) > 300:

        flash(
            (
                "Tên cấu trúc ngữ pháp "
                "không được vượt quá 300 ký tự."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.grammar",
                lesson_id=lesson_id,
            )
        )


    if len(example_zh) > 1000:

        flash(
            (
                "Ví dụ tiếng Trung không được "
                "vượt quá 1.000 ký tự."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.grammar",
                lesson_id=lesson_id,
            )
        )


    if len(example_pinyin) > 1000:

        flash(
            (
                "Pinyin ví dụ không được "
                "vượt quá 1.000 ký tự."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.grammar",
                lesson_id=lesson_id,
            )
        )


    if len(example_vi) > 1000:

        flash(
            (
                "Nghĩa ví dụ không được "
                "vượt quá 1.000 ký tự."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.grammar",
                lesson_id=lesson_id,
            )
        )


    # =====================================================
    # 3. ADMIN ĐANG THÊM
    # =====================================================

    admin_id = int(
        g.account["id"]
    )


    # =====================================================
    # 4. INSERT
    # =====================================================

    try:

        with closing(
            get_connection()
        ) as connection:

            try:

                with closing(
                    connection.cursor()
                ) as cursor:


                    # =========================================
                    # KIỂM TRA BÀI HỌC
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            MaBaiHoc,
                            TieuDe

                        FROM dbo.BaiHoc

                        WHERE
                            MaBaiHoc = ?;
                        """,
                        lesson_id,
                    )


                    lesson_row = (
                        cursor.fetchone()
                    )


                    if lesson_row is None:

                        abort(
                            404,
                            description=(
                                "Không tìm thấy bài học."
                            ),
                        )


                    # =========================================
                    # THỨ TỰ TIẾP THEO
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            ISNULL(
                                MAX(ThuTu),
                                0
                            ) + 1

                        FROM dbo.NguPhap

                        WHERE
                            MaBaiHoc = ?;
                        """,
                        lesson_id,
                    )


                    next_order = int(
                        cursor.fetchone()[0]
                        or 1
                    )


                    # =========================================
                    # THÊM NGỮ PHÁP
                    #
                    # - trạng thái ban_nhap
                    # - chưa gắn media
                    # - chưa gắn nguồn
                    # =========================================

                    cursor.execute(
                        """
                        INSERT INTO dbo.NguPhap
                        (
                            MaBaiHoc,
                            TenCauTruc,
                            MoTa,
                            CachDung,
                            ViDuTiengTrung,
                            ViDuPinyin,
                            ViDuTiengViet,
                            MaTep,
                            MaNguon,
                            ThuTu,
                            TrangThai,
                            MaQuanTriVienCapNhat,
                            NgayCapNhat
                        )

                        OUTPUT
                            INSERTED.MaNguPhap

                        VALUES
                        (
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            NULL,
                            NULL,
                            ?,
                            'ban_nhap',
                            ?,
                            SYSUTCDATETIME()
                        );
                        """,

                        lesson_id,

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

                        next_order,

                        admin_id,
                    )


                    grammar_id = int(
                        cursor.fetchone()[0]
                    )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except pyodbc.Error:

        current_app.logger.error(
            (
                "Loi SQL khi them "
                "ngu phap vao bai hoc."
            )
        )


        flash(
            (
                "Chưa thể thêm ngữ pháp "
                "vào bài học."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.grammar",
                lesson_id=lesson_id,
            )
        )


    # =====================================================
    # 5. THÀNH CÔNG
    # =====================================================

    flash(
        (
            f"Đã thêm ngữ pháp "
            f"“{structure}” "
            f"vào bài học ở trạng thái Bản nháp."
        ),
        "success",
    )


    return redirect(
        url_for(
            "admin_lessons.grammar",
            lesson_id=lesson_id,
        )
    )
# =========================================================
# SỬA NGỮ PHÁP TRONG BÀI HỌC
#
# GET:
# /admin/bai-hoc/<lesson_id>/ngu-phap/<grammar_id>/sua
#
# POST:
# /admin/bai-hoc/<lesson_id>/ngu-phap/<grammar_id>/sua
#
# Chức năng:
# - sửa tên cấu trúc
# - sửa mô tả
# - sửa cách dùng
# - sửa ví dụ
#
# Không sửa:
# - thứ tự
# - trạng thái
# =========================================================

@admin_lessons_bp.route(
    "/<int:lesson_id>/ngu-phap/"
    "<int:grammar_id>/sua",
    methods=[
        "GET",
        "POST",
    ],
)
def edit_lesson_grammar(
    lesson_id,
    grammar_id,
):

    lesson = None

    grammar_item = None


    # =====================================================
    # 1. LẤY BÀI HỌC + NGỮ PHÁP
    # =====================================================

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # BÀI HỌC
            # =================================================

            cursor.execute(
                """
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
                    ON kh.MaKhoaHoc
                    = bh.MaKhoaHoc

                WHERE
                    bh.MaBaiHoc = ?;
                """,
                lesson_id,
            )


            row = cursor.fetchone()


            if row is None:

                abort(
                    404,
                    description=(
                        "Không tìm thấy bài học."
                    ),
                )


            lesson = {
                "id": row[0],

                "course_id":
                    row[1],

                "order":
                    row[2],

                "title":
                    row[3],

                "status":
                    row[4],

                "course_level":
                    row[5],

                "course_title":
                    row[6],
            }


            # =================================================
            # NGỮ PHÁP
            #
            # Phải thuộc đúng bài đang mở.
            # =================================================

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
                    TrangThai

                FROM dbo.NguPhap

                WHERE
                    MaNguPhap = ?
                    AND MaBaiHoc = ?;
                """,

                grammar_id,

                lesson_id,
            )


            row = cursor.fetchone()


            if row is None:

                abort(
                    404,
                    description=(
                        "Không tìm thấy ngữ pháp "
                        "trong bài học này."
                    ),
                )


            grammar_item = {
                "id": row[0],

                "lesson_id":
                    row[1],

                "structure":
                    row[2]
                    or "",

                "description":
                    row[3]
                    or "",

                "usage":
                    row[4]
                    or "",

                "example_zh":
                    row[5]
                    or "",

                "example_pinyin":
                    row[6]
                    or "",

                "example_vi":
                    row[7]
                    or "",

                "order":
                    row[8],

                "status":
                    row[9],
            }


    # =====================================================
    # 2. GET → HIỂN THỊ FORM
    # =====================================================

    if request.method == "GET":

        return render_template(
            "admin/lesson_grammar_edit.html",

            active_page="lessons",

            lesson=lesson,

            grammar=
                grammar_item,

            statuses=STATUSES,
        )


    # =====================================================
    # 3. POST → ĐỌC FORM
    # =====================================================

    structure = (
        request.form.get(
            "structure",
            "",
        )
        .strip()
    )


    description = (
        request.form.get(
            "description",
            "",
        )
        .strip()
    )


    usage = (
        request.form.get(
            "usage",
            "",
        )
        .strip()
    )


    example_zh = (
        request.form.get(
            "example_zh",
            "",
        )
        .strip()
    )


    example_pinyin = (
        request.form.get(
            "example_pinyin",
            "",
        )
        .strip()
    )


    example_vi = (
        request.form.get(
            "example_vi",
            "",
        )
        .strip()
    )


    # =====================================================
    # 4. VALIDATE
    # =====================================================

    if not structure:

        flash(
            (
                "Tên cấu trúc ngữ pháp "
                "không được để trống."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.edit_lesson_grammar",

                lesson_id=
                    lesson_id,

                grammar_id=
                    grammar_id,
            )
        )


    if len(structure) > 300:

        flash(
            (
                "Tên cấu trúc không được "
                "vượt quá 300 ký tự."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.edit_lesson_grammar",

                lesson_id=
                    lesson_id,

                grammar_id=
                    grammar_id,
            )
        )


    if len(example_zh) > 1000:

        flash(
            (
                "Ví dụ tiếng Trung không được "
                "vượt quá 1.000 ký tự."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.edit_lesson_grammar",

                lesson_id=
                    lesson_id,

                grammar_id=
                    grammar_id,
            )
        )


    if len(example_pinyin) > 1000:

        flash(
            (
                "Pinyin không được "
                "vượt quá 1.000 ký tự."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.edit_lesson_grammar",

                lesson_id=
                    lesson_id,

                grammar_id=
                    grammar_id,
            )
        )


    if len(example_vi) > 1000:

        flash(
            (
                "Nghĩa tiếng Việt không được "
                "vượt quá 1.000 ký tự."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.edit_lesson_grammar",

                lesson_id=
                    lesson_id,

                grammar_id=
                    grammar_id,
            )
        )


    # =====================================================
    # 5. ADMIN ĐANG SỬA
    # =====================================================

    admin_id = int(
        g.account["id"]
    )


    # =====================================================
    # 6. UPDATE SQL
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
                        UPDATE dbo.NguPhap

                        SET
                            TenCauTruc = ?,
                            MoTa = ?,
                            CachDung = ?,
                            ViDuTiengTrung = ?,
                            ViDuPinyin = ?,
                            ViDuTiengViet = ?,

                            MaQuanTriVienCapNhat = ?,

                            NgayCapNhat =
                                SYSUTCDATETIME()

                        WHERE
                            MaNguPhap = ?
                            AND MaBaiHoc = ?;
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

                        admin_id,

                        grammar_id,

                        lesson_id,
                    )


                    if cursor.rowcount == 0:

                        abort(
                            404,
                            description=(
                                "Không tìm thấy ngữ pháp."
                            ),
                        )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except pyodbc.Error:

        current_app.logger.error(
            (
                "Loi SQL khi sua "
                "ngu phap trong bai hoc."
            )
        )


        flash(
            (
                "Chưa thể cập nhật "
                "ngữ pháp."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.edit_lesson_grammar",

                lesson_id=
                    lesson_id,

                grammar_id=
                    grammar_id,
            )
        )


    # =====================================================
    # 7. THÀNH CÔNG
    # =====================================================

    flash(
        (
            f"Đã cập nhật ngữ pháp "
            f"“{structure}”."
        ),
        "success",
    )


    return redirect(
        url_for(
            "admin_lessons.grammar",

            lesson_id=
                lesson_id,
        )
    )


# =========================================================
# ĐỔI THỨ TỰ NGỮ PHÁP TRONG BÀI
#
# POST:
# /admin/bai-hoc/<lesson_id>/ngu-phap/thu-tu
#
# Quy tắc:
# Nếu bài có 7 cấu trúc:
#
# phải dùng đủ:
# 1, 2, 3, 4, 5, 6, 7
#
# không trùng
# không bỏ số
# =========================================================

@admin_lessons_bp.post(
    "/<int:lesson_id>/ngu-phap/thu-tu"
)
def reorder_grammar(
    lesson_id
):

    grammar_rows = []


    # =====================================================
    # 1. LẤY NGỮ PHÁP CỦA BÀI
    # =====================================================

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    MaNguPhap,
                    ThuTu,
                    TenCauTruc

                FROM dbo.NguPhap

                WHERE
                    MaBaiHoc = ?

                ORDER BY
                    ThuTu,
                    MaNguPhap;
                """,
                lesson_id,
            )


            grammar_rows = (
                cursor.fetchall()
            )


    # =====================================================
    # 2. KHÔNG CÓ NGỮ PHÁP
    # =====================================================

    if not grammar_rows:

        flash(
            (
                "Bài học chưa có ngữ pháp "
                "để thay đổi thứ tự."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.grammar",

                lesson_id=
                    lesson_id,
            )
        )


    # =====================================================
    # 3. ĐỌC THỨ TỰ MỚI
    #
    # grammar_order_1 = 1
    # grammar_order_2 = 2
    # ...
    # =====================================================

    new_orders = {}


    for row in grammar_rows:

        grammar_id = int(
            row[0]
        )


        field_name = (
            f"grammar_order_{grammar_id}"
        )


        raw_value = (
            request.form.get(
                field_name,
                "",
            )
            .strip()
        )


        try:

            new_order = int(
                raw_value
            )

        except (
            TypeError,
            ValueError,
        ):

            flash(
                (
                    "Thứ tự ngữ pháp "
                    "phải là số nguyên."
                ),
                "error",
            )


            return redirect(
                url_for(
                    "admin_lessons.grammar",

                    lesson_id=
                        lesson_id,
                )
            )


        new_orders[
            grammar_id
        ] = new_order


    # =====================================================
    # 4. KIỂM TRA 1 → N
    # =====================================================

    total_items = len(
        grammar_rows
    )


    expected_orders = set(
        range(
            1,
            total_items + 1,
        )
    )


    submitted_orders = set(
        new_orders.values()
    )


    if submitted_orders != expected_orders:

        flash(
            (
                "Thứ tự ngữ pháp không hợp lệ. "
                f"Bài có {total_items} cấu trúc nên "
                f"cần dùng đủ các số từ "
                f"1 đến {total_items}, "
                f"không được trùng hoặc bỏ số."
            ),
            "error",
        )


        return redirect(
            url_for(
                "admin_lessons.grammar",

                lesson_id=
                    lesson_id,
            )
        )


    # =====================================================
    # 5. ADMIN ĐANG SỬA
    # =====================================================

    admin_id = int(
        g.account["id"]
    )


    # =====================================================
    # 6. UPDATE
    # =====================================================

    try:

        with closing(
            get_connection()
        ) as connection:

            try:

                with closing(
                    connection.cursor()
                ) as cursor:


                    # =========================================
                    # KIỂM TRA BÀI
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            MaBaiHoc

                        FROM dbo.BaiHoc

                        WHERE
                            MaBaiHoc = ?;
                        """,
                        lesson_id,
                    )


                    if (
                        cursor.fetchone()
                        is None
                    ):

                        abort(
                            404,
                            description=(
                                "Không tìm thấy bài học."
                            ),
                        )


                    # =========================================
                    # UPDATE TỪNG NGỮ PHÁP
                    # =========================================

                    for (
                        grammar_id,
                        new_order,
                    ) in new_orders.items():

                        cursor.execute(
                            """
                            UPDATE dbo.NguPhap

                            SET
                                ThuTu = ?,

                                MaQuanTriVienCapNhat = ?,

                                NgayCapNhat =
                                    SYSUTCDATETIME()

                            WHERE
                                MaNguPhap = ?
                                AND MaBaiHoc = ?;
                            """,

                            new_order,

                            admin_id,

                            grammar_id,

                            lesson_id,
                        )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except pyodbc.Error:

        current_app.logger.error(
            (
                "Loi SQL khi doi "
                "thu tu ngu phap."
            )
        )


        flash(
            (
                "Chưa thể cập nhật "
                "thứ tự ngữ pháp."
            ),
            "error",
        )


    else:

        flash(
            (
                "Đã cập nhật thứ tự "
                "ngữ pháp trong bài học."
            ),
            "success",
        )


    return redirect(
        url_for(
            "admin_lessons.grammar",

            lesson_id=
                lesson_id,
        )
    )

# =========================================================
# ĐỔI TRẠNG THÁI NGỮ PHÁP TRONG BÀI
#
# POST:
# /admin/bai-hoc/<lesson_id>/ngu-phap/<grammar_id>/trang-thai
#
# Trạng thái:
# - ban_nhap
# - da_xuat_ban
# - luu_tru
# =========================================================

@admin_lessons_bp.post(
    "/<int:lesson_id>/ngu-phap/"
    "<int:grammar_id>/trang-thai"
)
def set_grammar_status(
    lesson_id,
    grammar_id,
):

    # =====================================================
    # 1. LẤY TRẠNG THÁI MỚI
    # =====================================================

    new_status = (
        request.form.get(
            "status",
            "",
        )
        .strip()
    )


    # =====================================================
    # 2. KIỂM TRA TRẠNG THÁI
    # =====================================================

    if new_status not in STATUSES:

        abort(
            400,
            description=(
                "Trạng thái ngữ pháp "
                "không hợp lệ."
            ),
        )


    admin_id = int(
        g.account["id"]
    )


    # =====================================================
    # 3. UPDATE SQL
    # =====================================================

    try:

        with closing(
            get_connection()
        ) as connection:

            try:

                with closing(
                    connection.cursor()
                ) as cursor:


                    # =========================================
                    # KIỂM TRA NGỮ PHÁP THUỘC ĐÚNG BÀI
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            MaNguPhap,
                            TenCauTruc,
                            TrangThai

                        FROM dbo.NguPhap

                        WHERE
                            MaNguPhap = ?
                            AND MaBaiHoc = ?;
                        """,

                        grammar_id,

                        lesson_id,
                    )


                    grammar_row = (
                        cursor.fetchone()
                    )


                    if grammar_row is None:

                        abort(
                            404,
                            description=(
                                "Không tìm thấy ngữ pháp "
                                "trong bài học này."
                            ),
                        )


                    grammar_name = (
                        grammar_row[1]
                        or ""
                    )


                    # =========================================
                    # CẬP NHẬT TRẠNG THÁI
                    # =========================================

                    cursor.execute(
                        """
                        UPDATE dbo.NguPhap

                        SET
                            TrangThai = ?,

                            MaQuanTriVienCapNhat = ?,

                            NgayCapNhat =
                                SYSUTCDATETIME()

                        WHERE
                            MaNguPhap = ?
                            AND MaBaiHoc = ?;
                        """,

                        new_status,

                        admin_id,

                        grammar_id,

                        lesson_id,
                    )


                    if cursor.rowcount == 0:

                        abort(
                            404,
                            description=(
                                "Không tìm thấy ngữ pháp."
                            ),
                        )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except pyodbc.Error:

        current_app.logger.error(
            (
                "Loi SQL khi cap nhat "
                "trang thai ngu phap."
            )
        )


        flash(
            (
                "Chưa thể cập nhật "
                "trạng thái ngữ pháp."
            ),
            "error",
        )


    else:

        flash(
            (
                f"Đã chuyển ngữ pháp "
                f"“{grammar_name}” "
                f"sang trạng thái "
                f"“{STATUSES[new_status]}”."
            ),
            "success",
        )


    return redirect(
        url_for(
            "admin_lessons.grammar",

            lesson_id=
                lesson_id,
        )
    )

# =========================================================
# CHỮ HÁN CỦA MỘT BÀI HỌC
#
# Chức năng:
# - xem Chữ Hán
# - thêm Chữ Hán
# - sửa Chữ Hán
# - đổi thứ tự
# - đổi trạng thái
# =========================================================


# =========================================================
# LẤY DANH SÁCH BỘ THỦ
# =========================================================

def get_lesson_radicals():

    radicals = []


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    MaBoThu,
                    KyHieu,
                    TenBoThu,
                    YNghia,
                    SoNet

                FROM dbo.BoThu

                WHERE
                    TrangThai <> 'luu_tru'

                ORDER BY
                    SoBoThu,
                    MaBoThu;
                """
            )


            for row in cursor.fetchall():

                radicals.append(
                    {
                        "id": row[0],

                        "symbol":
                            row[1]
                            or "",

                        "name":
                            row[2]
                            or "",

                        "meaning":
                            row[3]
                            or "",

                        "stroke_count":
                            row[4],
                    }
                )


    return radicals


# =========================================================
# XEM CHỮ HÁN CỦA BÀI
#
# GET:
# /admin/bai-hoc/<lesson_id>/chu-han
# =========================================================

@admin_lessons_bp.get(
    "/<int:lesson_id>/chu-han"
)
def hanzi(
    lesson_id
):

    lesson = None

    hanzi_items = []

    radicals = (
        get_lesson_radicals()
    )


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # 1. THÔNG TIN BÀI
            # =================================================

            cursor.execute(
                """
                SELECT
                    bh.MaBaiHoc,
                    bh.MaKhoaHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe,
                    bh.TomTat,
                    bh.TrangThai,

                    kh.MaCapDo,
                    kh.TieuDe

                FROM dbo.BaiHoc AS bh

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc
                    = bh.MaKhoaHoc

                WHERE
                    bh.MaBaiHoc = ?;
                """,
                lesson_id,
            )


            row = cursor.fetchone()


            if row is None:

                abort(
                    404,
                    description=(
                        "Không tìm thấy bài học."
                    ),
                )


            lesson = {
                "id": row[0],

                "course_id":
                    row[1],

                "order":
                    row[2],

                "title":
                    row[3],

                "summary":
                    row[4]
                    or "",

                "status":
                    row[5],

                "course_level":
                    row[6],

                "course_title":
                    row[7],
            }


            # =================================================
            # 2. DANH SÁCH CHỮ HÁN
            # =================================================

            cursor.execute(
                """
                SELECT
                    ch.MaChuHan,
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

                    bt.KyHieu,
                    bt.TenBoThu,
                    bt.YNghia

                FROM dbo.ChuHan AS ch

                LEFT JOIN dbo.BoThu AS bt
                    ON bt.MaBoThu
                    = ch.MaBoThu

                WHERE
                    ch.MaBaiHoc = ?

                ORDER BY
                    ch.ThuTu,
                    ch.MaChuHan;
                """,
                lesson_id,
            )


            for row in cursor.fetchall():

                hanzi_items.append(
                    {
                        "id": row[0],

                        "radical_id":
                            row[1],

                        "character":
                            row[2]
                            or "",

                        "pinyin":
                            row[3]
                            or "",

                        "meaning":
                            row[4]
                            or "",

                        "stroke_count":
                            row[5],

                        "memory_tip":
                            row[6]
                            or "",

                        "example_zh":
                            row[7]
                            or "",

                        "example_pinyin":
                            row[8]
                            or "",

                        "example_vi":
                            row[9]
                            or "",

                        "media_id":
                            row[10],

                        "order":
                            row[11],

                        "status":
                            row[12],

                        "radical_symbol":
                            row[13]
                            or "",

                        "radical_name":
                            row[14]
                            or "",

                        "radical_meaning":
                            row[15]
                            or "",
                    }
                )


            lesson["hanzi_count"] = len(
                hanzi_items
            )


            # =================================================
            # 3. ĐẾM TỪ VỰNG
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.TuVungBaiHoc

                WHERE
                    MaBaiHoc = ?;
                """,
                lesson_id,
            )


            lesson["vocabulary_count"] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 4. ĐẾM NGỮ PHÁP
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.NguPhap

                WHERE
                    MaBaiHoc = ?;
                """,
                lesson_id,
            )


            lesson["grammar_count"] = int(
                cursor.fetchone()[0]
                or 0
            )


            # =================================================
            # 5. ĐẾM BÀI TẬP
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)

                FROM dbo.BaiTap

                WHERE
                    MaBaiHoc = ?;
                """,
                lesson_id,
            )


            lesson["exercise_count"] = int(
                cursor.fetchone()[0]
                or 0
            )


    return render_template(
        "admin/lesson_hanzi.html",

        active_page="lessons",

        lesson=lesson,

        hanzi_items=
            hanzi_items,

        radicals=
            radicals,

        statuses=
            STATUSES,
    )


# =========================================================
# THÊM CHỮ HÁN VÀO BÀI
#
# POST:
# /admin/bai-hoc/<lesson_id>/chu-han/them
# =========================================================

@admin_lessons_bp.post(
    "/<int:lesson_id>/chu-han/them"
)
def add_hanzi(
    lesson_id
):

    # =====================================================
    # 1. FORM
    # =====================================================

    character = (
        request.form.get(
            "character",
            "",
        )
        .strip()
    )


    pinyin = (
        request.form.get(
            "pinyin",
            "",
        )
        .strip()
    )


    meaning = (
        request.form.get(
            "meaning",
            "",
        )
        .strip()
    )


    radical_id = (
        request.form.get(
            "radical_id",
            type=int,
        )
    )


    stroke_count = (
        request.form.get(
            "stroke_count",
            type=int,
        )
    )


    memory_tip = (
        request.form.get(
            "memory_tip",
            "",
        )
        .strip()
    )


    example_zh = (
        request.form.get(
            "example_zh",
            "",
        )
        .strip()
    )


    example_pinyin = (
        request.form.get(
            "example_pinyin",
            "",
        )
        .strip()
    )


    example_vi = (
        request.form.get(
            "example_vi",
            "",
        )
        .strip()
    )


    # =====================================================
    # 2. VALIDATE
    # =====================================================

    if not character:

        flash(
            "Ký tự Chữ Hán không được để trống.",
            "error",
        )

        return redirect(
            url_for(
                "admin_lessons.hanzi",
                lesson_id=lesson_id,
            )
        )


    if stroke_count is not None and stroke_count <= 0:

        flash(
            "Số nét phải lớn hơn 0.",
            "error",
        )

        return redirect(
            url_for(
                "admin_lessons.hanzi",
                lesson_id=lesson_id,
            )
        )


    admin_id = int(
        g.account["id"]
    )


    # =====================================================
    # 3. INSERT
    # =====================================================

    try:

        with closing(
            get_connection()
        ) as connection:

            try:

                with closing(
                    connection.cursor()
                ) as cursor:


                    # =========================================
                    # BÀI HỌC
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            MaBaiHoc

                        FROM dbo.BaiHoc

                        WHERE
                            MaBaiHoc = ?;
                        """,
                        lesson_id,
                    )


                    if cursor.fetchone() is None:

                        abort(
                            404,
                            description=(
                                "Không tìm thấy bài học."
                            ),
                        )


                    # =========================================
                    # BỘ THỦ
                    # =========================================

                    if radical_id is not None:

                        cursor.execute(
                            """
                            SELECT
                                MaBoThu

                            FROM dbo.BoThu

                            WHERE
                                MaBoThu = ?
                                AND TrangThai
                                    <> 'luu_tru';
                            """,
                            radical_id,
                        )


                        if cursor.fetchone() is None:

                            abort(
                                400,
                                description=(
                                    "Bộ thủ không hợp lệ."
                                ),
                            )


                    # =========================================
                    # THỨ TỰ TIẾP THEO
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            ISNULL(
                                MAX(ThuTu),
                                0
                            ) + 1

                        FROM dbo.ChuHan

                        WHERE
                            MaBaiHoc = ?;
                        """,
                        lesson_id,
                    )


                    next_order = int(
                        cursor.fetchone()[0]
                        or 1
                    )


                    # =========================================
                    # INSERT
                    # =========================================

                    cursor.execute(
                        """
                        INSERT INTO dbo.ChuHan
                        (
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
                            MaNguon,
                            ThuTu,
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
                            ?,
                            ?,
                            ?,
                            NULL,
                            NULL,
                            ?,
                            'ban_nhap',
                            ?,
                            SYSUTCDATETIME()
                        );
                        """,

                        lesson_id,

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

                        next_order,

                        admin_id,
                    )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except pyodbc.Error:

        current_app.logger.error(
            "Loi SQL khi them Chu Han vao bai."
        )

        flash(
            "Chưa thể thêm Chữ Hán vào bài học.",
            "error",
        )


    else:

        flash(
            (
                f"Đã thêm chữ “{character}” "
                f"vào bài học ở trạng thái Bản nháp."
            ),
            "success",
        )


    return redirect(
        url_for(
            "admin_lessons.hanzi",
            lesson_id=lesson_id,
        )
    )


# =========================================================
# SỬA CHỮ HÁN
#
# GET + POST
# =========================================================

@admin_lessons_bp.route(
    "/<int:lesson_id>/chu-han/"
    "<int:hanzi_id>/sua",
    methods=[
        "GET",
        "POST",
    ],
)
def edit_lesson_hanzi(
    lesson_id,
    hanzi_id,
):

    radicals = (
        get_lesson_radicals()
    )


    lesson = None

    hanzi_item = None


    # =====================================================
    # 1. LOAD
    # =====================================================

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            cursor.execute(
                """
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
                    ON kh.MaKhoaHoc
                    = bh.MaKhoaHoc

                WHERE
                    bh.MaBaiHoc = ?;
                """,
                lesson_id,
            )


            row = cursor.fetchone()


            if row is None:

                abort(
                    404,
                    description=(
                        "Không tìm thấy bài học."
                    ),
                )


            lesson = {
                "id": row[0],

                "course_id":
                    row[1],

                "order":
                    row[2],

                "title":
                    row[3],

                "status":
                    row[4],

                "course_level":
                    row[5],

                "course_title":
                    row[6],
            }


            cursor.execute(
                """
                SELECT
                    MaChuHan,
                    MaBoThu,
                    KyTu,
                    Pinyin,
                    NghiaTiengViet,
                    SoNet,
                    CachGhiNho,
                    ViDuTiengTrung,
                    ViDuPinyin,
                    ViDuTiengViet,
                    ThuTu,
                    TrangThai

                FROM dbo.ChuHan

                WHERE
                    MaChuHan = ?
                    AND MaBaiHoc = ?;
                """,

                hanzi_id,

                lesson_id,
            )


            row = cursor.fetchone()


            if row is None:

                abort(
                    404,
                    description=(
                        "Không tìm thấy Chữ Hán "
                        "trong bài học này."
                    ),
                )


            hanzi_item = {
                "id": row[0],

                "radical_id":
                    row[1],

                "character":
                    row[2]
                    or "",

                "pinyin":
                    row[3]
                    or "",

                "meaning":
                    row[4]
                    or "",

                "stroke_count":
                    row[5],

                "memory_tip":
                    row[6]
                    or "",

                "example_zh":
                    row[7]
                    or "",

                "example_pinyin":
                    row[8]
                    or "",

                "example_vi":
                    row[9]
                    or "",

                "order":
                    row[10],

                "status":
                    row[11],
            }


    # =====================================================
    # GET
    # =====================================================

    if request.method == "GET":

        return render_template(
            "admin/lesson_hanzi_edit.html",

            active_page="lessons",

            lesson=lesson,

            hanzi=
                hanzi_item,

            radicals=
                radicals,

            statuses=
                STATUSES,
        )


    # =====================================================
    # POST
    # =====================================================

    character = (
        request.form.get(
            "character",
            "",
        )
        .strip()
    )


    pinyin = (
        request.form.get(
            "pinyin",
            "",
        )
        .strip()
    )


    meaning = (
        request.form.get(
            "meaning",
            "",
        )
        .strip()
    )


    radical_id = (
        request.form.get(
            "radical_id",
            type=int,
        )
    )


    stroke_count = (
        request.form.get(
            "stroke_count",
            type=int,
        )
    )


    memory_tip = (
        request.form.get(
            "memory_tip",
            "",
        )
        .strip()
    )


    example_zh = (
        request.form.get(
            "example_zh",
            "",
        )
        .strip()
    )


    example_pinyin = (
        request.form.get(
            "example_pinyin",
            "",
        )
        .strip()
    )


    example_vi = (
        request.form.get(
            "example_vi",
            "",
        )
        .strip()
    )


    if not character:

        flash(
            "Ký tự Chữ Hán không được để trống.",
            "error",
        )

        return redirect(
            url_for(
                "admin_lessons.edit_lesson_hanzi",

                lesson_id=
                    lesson_id,

                hanzi_id=
                    hanzi_id,
            )
        )


    if stroke_count is not None and stroke_count <= 0:

        flash(
            "Số nét phải lớn hơn 0.",
            "error",
        )

        return redirect(
            url_for(
                "admin_lessons.edit_lesson_hanzi",

                lesson_id=
                    lesson_id,

                hanzi_id=
                    hanzi_id,
            )
        )


    admin_id = int(
        g.account["id"]
    )


    try:

        with closing(
            get_connection()
        ) as connection:

            try:

                with closing(
                    connection.cursor()
                ) as cursor:


                    if radical_id is not None:

                        cursor.execute(
                            """
                            SELECT
                                MaBoThu

                            FROM dbo.BoThu

                            WHERE
                                MaBoThu = ?
                                AND TrangThai
                                    <> 'luu_tru';
                            """,
                            radical_id,
                        )


                        if cursor.fetchone() is None:

                            abort(
                                400,
                                description=(
                                    "Bộ thủ không hợp lệ."
                                ),
                            )


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

                            MaQuanTriVienCapNhat = ?,

                            NgayCapNhat =
                                SYSUTCDATETIME()

                        WHERE
                            MaChuHan = ?
                            AND MaBaiHoc = ?;
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

                        admin_id,

                        hanzi_id,

                        lesson_id,
                    )


                    if cursor.rowcount == 0:

                        abort(
                            404,
                            description=(
                                "Không tìm thấy Chữ Hán."
                            ),
                        )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except pyodbc.Error:

        current_app.logger.error(
            "Loi SQL khi sua Chu Han."
        )

        flash(
            "Chưa thể cập nhật Chữ Hán.",
            "error",
        )


    else:

        flash(
            (
                f"Đã cập nhật chữ "
                f"“{character}”."
            ),
            "success",
        )


    return redirect(
        url_for(
            "admin_lessons.hanzi",
            lesson_id=lesson_id,
        )
    )


# =========================================================
# ĐỔI THỨ TỰ CHỮ HÁN
# =========================================================

@admin_lessons_bp.post(
    "/<int:lesson_id>/chu-han/thu-tu"
)
def reorder_hanzi(
    lesson_id
):

    hanzi_rows = []


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    MaChuHan,
                    ThuTu,
                    KyTu

                FROM dbo.ChuHan

                WHERE
                    MaBaiHoc = ?

                ORDER BY
                    ThuTu,
                    MaChuHan;
                """,
                lesson_id,
            )


            hanzi_rows = (
                cursor.fetchall()
            )


    if not hanzi_rows:

        flash(
            (
                "Bài học chưa có Chữ Hán "
                "để thay đổi thứ tự."
            ),
            "error",
        )

        return redirect(
            url_for(
                "admin_lessons.hanzi",
                lesson_id=lesson_id,
            )
        )


    new_orders = {}


    for row in hanzi_rows:

        hanzi_id = int(
            row[0]
        )


        raw_value = (
            request.form.get(
                f"hanzi_order_{hanzi_id}",
                "",
            )
            .strip()
        )


        try:

            new_order = int(
                raw_value
            )

        except (
            TypeError,
            ValueError,
        ):

            flash(
                "Thứ tự Chữ Hán phải là số nguyên.",
                "error",
            )

            return redirect(
                url_for(
                    "admin_lessons.hanzi",
                    lesson_id=lesson_id,
                )
            )


        new_orders[
            hanzi_id
        ] = new_order


    total_items = len(
        hanzi_rows
    )


    expected_orders = set(
        range(
            1,
            total_items + 1,
        )
    )


    if set(
        new_orders.values()
    ) != expected_orders:

        flash(
            (
                "Thứ tự Chữ Hán không hợp lệ. "
                f"Cần dùng đủ các số từ "
                f"1 đến {total_items}, "
                f"không được trùng hoặc bỏ số."
            ),
            "error",
        )

        return redirect(
            url_for(
                "admin_lessons.hanzi",
                lesson_id=lesson_id,
            )
        )


    admin_id = int(
        g.account["id"]
    )


    try:

        with closing(
            get_connection()
        ) as connection:

            try:

                with closing(
                    connection.cursor()
                ) as cursor:


                    for (
                        hanzi_id,
                        new_order,
                    ) in new_orders.items():

                        cursor.execute(
                            """
                            UPDATE dbo.ChuHan

                            SET
                                ThuTu = ?,

                                MaQuanTriVienCapNhat = ?,

                                NgayCapNhat =
                                    SYSUTCDATETIME()

                            WHERE
                                MaChuHan = ?
                                AND MaBaiHoc = ?;
                            """,

                            new_order,

                            admin_id,

                            hanzi_id,

                            lesson_id,
                        )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except pyodbc.Error:

        current_app.logger.error(
            "Loi SQL khi doi thu tu Chu Han."
        )

        flash(
            "Chưa thể cập nhật thứ tự Chữ Hán.",
            "error",
        )


    else:

        flash(
            (
                "Đã cập nhật thứ tự "
                "Chữ Hán trong bài học."
            ),
            "success",
        )


    return redirect(
        url_for(
            "admin_lessons.hanzi",
            lesson_id=lesson_id,
        )
    )


# =========================================================
# ĐỔI TRẠNG THÁI CHỮ HÁN
# =========================================================

@admin_lessons_bp.post(
    "/<int:lesson_id>/chu-han/"
    "<int:hanzi_id>/trang-thai"
)
def set_hanzi_status(
    lesson_id,
    hanzi_id,
):

    new_status = (
        request.form.get(
            "status",
            "",
        )
        .strip()
    )


    if new_status not in STATUSES:

        abort(
            400,
            description=(
                "Trạng thái Chữ Hán "
                "không hợp lệ."
            ),
        )


    admin_id = int(
        g.account["id"]
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
                            KyTu

                        FROM dbo.ChuHan

                        WHERE
                            MaChuHan = ?
                            AND MaBaiHoc = ?;
                        """,

                        hanzi_id,

                        lesson_id,
                    )


                    row = cursor.fetchone()


                    if row is None:

                        abort(
                            404,
                            description=(
                                "Không tìm thấy Chữ Hán."
                            ),
                        )


                    character = (
                        row[0]
                        or ""
                    )


                    cursor.execute(
                        """
                        UPDATE dbo.ChuHan

                        SET
                            TrangThai = ?,

                            MaQuanTriVienCapNhat = ?,

                            NgayCapNhat =
                                SYSUTCDATETIME()

                        WHERE
                            MaChuHan = ?
                            AND MaBaiHoc = ?;
                        """,

                        new_status,

                        admin_id,

                        hanzi_id,

                        lesson_id,
                    )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except pyodbc.Error:

        current_app.logger.error(
            (
                "Loi SQL khi cap nhat "
                "trang thai Chu Han."
            )
        )

        flash(
            (
                "Chưa thể cập nhật "
                "trạng thái Chữ Hán."
            ),
            "error",
        )


    else:

        flash(
            (
                f"Đã chuyển chữ “{character}” "
                f"sang trạng thái "
                f"“{STATUSES[new_status]}”."
            ),
            "success",
        )


    return redirect(
        url_for(
            "admin_lessons.hanzi",
            lesson_id=lesson_id,
        )
    )

# =========================================================
# SỬA THÔNG TIN BÀI HỌC
#
# Chỉ sửa:
# - số thứ tự
# - tiêu đề
# - tóm tắt
#
# Không chuyển bài sang khóa khác.
# Trạng thái được quản lý bằng chức năng riêng.
#
# URL:
# /admin/bai-hoc/<lesson_id>/sua
# =========================================================

@admin_lessons_bp.route(
    "/<int:lesson_id>/sua",
    methods=[
        "GET",
        "POST",
    ],
)
def edit(
    lesson_id
):

    # =====================================================
    # 1. LẤY BÀI HỌC HIỆN TẠI
    # =====================================================

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    bh.MaBaiHoc,
                    bh.MaKhoaHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe,
                    bh.TomTat,
                    bh.TrangThai,

                    kh.MaCapDo,
                    kh.TieuDe

                FROM dbo.BaiHoc AS bh

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc
                    = bh.MaKhoaHoc

                WHERE
                    bh.MaBaiHoc = ?;
                """,
                lesson_id,
            )


            row = cursor.fetchone()


    if row is None:

        abort(
            404,
            description=(
                "Không tìm thấy bài học."
            ),
        )


    lesson = {
        "id": row[0],

        "course_id": row[1],

        "order": row[2],

        "title": row[3],

        "summary":
            row[4]
            or "",

        "status": row[5],

        "course_level":
            row[6],

        "course_title":
            row[7],
    }


    # =====================================================
    # 2. GET → HIỂN THỊ FORM
    # =====================================================

    if request.method == "GET":

        return render_template(
            "admin/lesson_edit.html",

            active_page="lessons",

            lesson=lesson,

            statuses=STATUSES,
        )


    # =====================================================
    # 3. POST → LẤY DỮ LIỆU FORM
    # =====================================================

    lesson["order"] = (
        request.form.get(
            "order",
            type=int,
        )
    )


    lesson["title"] = (
        request.form.get(
            "title",
            "",
        )
        .strip()
    )


    lesson["summary"] = (
        request.form.get(
            "summary",
            "",
        )
        .strip()
    )


    # =====================================================
    # 4. VALIDATE SỐ THỨ TỰ
    # =====================================================

    if (
        lesson["order"] is None
        or
        lesson["order"] <= 0
    ):

        flash(
            (
                "Số thứ tự bài phải "
                "lớn hơn 0."
            ),
            "error",
        )


        return render_template(
            "admin/lesson_edit.html",

            active_page="lessons",

            lesson=lesson,

            statuses=STATUSES,
        ), 400


    # =====================================================
    # 5. VALIDATE TIÊU ĐỀ
    # =====================================================

    if not (
        1
        <= len(
            lesson["title"]
        )
        <= 200
    ):

        flash(
            (
                "Tên bài học cần từ "
                "1 đến 200 ký tự."
            ),
            "error",
        )


        return render_template(
            "admin/lesson_edit.html",

            active_page="lessons",

            lesson=lesson,

            statuses=STATUSES,
        ), 400


    # =====================================================
    # 6. VALIDATE TÓM TẮT
    # =====================================================

    if len(
        lesson["summary"]
    ) > 2000:

        flash(
            (
                "Tóm tắt bài học không được "
                "quá 2.000 ký tự."
            ),
            "error",
        )


        return render_template(
            "admin/lesson_edit.html",

            active_page="lessons",

            lesson=lesson,

            statuses=STATUSES,
        ), 400


    # =====================================================
    # 7. ADMIN ĐANG CẬP NHẬT
    # =====================================================

    admin_id = int(
        g.account["id"]
    )


    # =====================================================
    # 8. UPDATE SQL
    # =====================================================

    try:

        with closing(
            get_connection()
        ) as connection:

            try:

                with closing(
                    connection.cursor()
                ) as cursor:


                    # =========================================
                    # KIỂM TRA TRÙNG SỐ THỨ TỰ
                    #
                    # Chỉ tìm bài KHÁC lesson_id.
                    # =========================================

                    cursor.execute(
                        """
                        SELECT
                            MaBaiHoc,
                            TieuDe

                        FROM dbo.BaiHoc

                        WHERE
                            MaKhoaHoc = ?
                            AND SoThuTuBai = ?
                            AND MaBaiHoc <> ?;
                        """,

                        lesson["course_id"],

                        lesson["order"],

                        lesson_id,
                    )


                    duplicated = (
                        cursor.fetchone()
                    )


                    if duplicated is not None:

                        flash(
                            (
                                f"Khóa này đã có "
                                f"Bài {lesson['order']}: "
                                f"“{duplicated[1]}”. "
                                f"Hãy chọn số thứ tự khác."
                            ),
                            "error",
                        )


                        return render_template(
                            "admin/lesson_edit.html",

                            active_page="lessons",

                            lesson=lesson,

                            statuses=STATUSES,
                        ), 409


                    # =========================================
                    # CẬP NHẬT BÀI
                    # =========================================

                    cursor.execute(
                        """
                        UPDATE dbo.BaiHoc

                        SET
                            SoThuTuBai = ?,
                            TieuDe = ?,
                            TomTat = ?,

                            MaQuanTriVienCapNhat = ?,

                            NgayCapNhat =
                                SYSUTCDATETIME()

                        OUTPUT
                            INSERTED.MaBaiHoc

                        WHERE
                            MaBaiHoc = ?;
                        """,

                        lesson["order"],

                        lesson["title"],

                        lesson["summary"]
                        or None,

                        admin_id,

                        lesson_id,
                    )


                    updated = (
                        cursor.fetchone()
                    )


                    if updated is None:

                        abort(
                            404,
                            description=(
                                "Bài học không còn tồn tại."
                            ),
                        )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


    except pyodbc.IntegrityError:

        flash(
            (
                "Không thể cập nhật bài học. "
                "Số thứ tự có thể đã trùng "
                "với bài khác trong cùng khóa."
            ),
            "error",
        )


        return render_template(
            "admin/lesson_edit.html",

            active_page="lessons",

            lesson=lesson,

            statuses=STATUSES,
        ), 409


    # =====================================================
    # 9. THÀNH CÔNG
    # =====================================================

    flash(
        (
            f"Đã cập nhật "
            f"Bài {lesson['order']} "
            f"“{lesson['title']}”."
        ),
        "success",
    )


    return redirect(
        url_for(
            "admin_lessons.index",

            course_id=
                lesson["course_id"],
        )
    )

# =========================================================
# ĐỔI TRẠNG THÁI MỘT BÀI HỌC
# =========================================================

@admin_lessons_bp.post(
    "/<int:lesson_id>/trang-thai"
)
def set_status(
    lesson_id
):

    new_status = (
        request.form.get(
            "status",
            "",
        )
        .strip()
    )


    if new_status not in STATUSES:

        abort(
            400,
            description=(
                "Trạng thái bài học "
                "không hợp lệ."
            ),
        )


    return_course_id = (
        request.form.get(
            "course_id",
            type=int,
        )
    )


    admin_id = int(
        g.account["id"]
    )


    try:

        with closing(
            get_connection()
        ) as connection:

            with closing(
                connection.cursor()
            ) as cursor:

                cursor.execute(
                    """
                    UPDATE dbo.BaiHoc

                    SET
                        TrangThai = ?,
                        MaQuanTriVienCapNhat = ?,
                        NgayCapNhat =
                            SYSUTCDATETIME()

                    OUTPUT
                        INSERTED.MaBaiHoc,
                        INSERTED.TieuDe,
                        INSERTED.TrangThai

                    WHERE
                        MaBaiHoc = ?;
                    """,

                    new_status,

                    admin_id,

                    lesson_id,
                )


                updated = (
                    cursor.fetchone()
                )


                if updated is None:

                    abort(
                        404,
                        description=(
                            "Không tìm thấy bài học."
                        ),
                    )


            connection.commit()


    except pyodbc.Error:

        current_app.logger.error(
            (
                "Loi SQL khi cap nhat "
                "trang thai bai hoc."
            )
        )


        flash(
            (
                "Chưa thể cập nhật "
                "trạng thái bài học."
            ),
            "error",
        )


    else:

        flash(
            (
                f"Đã chuyển “{updated[1]}” "
                f"sang trạng thái "
                f"“{STATUSES[new_status]}”."
            ),
            "success",
        )


    if return_course_id is not None:

        return redirect(
            url_for(
                "admin_lessons.index",

                course_id=
                    return_course_id,
            )
        )


    return redirect(
        url_for(
            "admin_lessons.index"
        )
    )


# =========================================================
# XUẤT BẢN TOÀN BỘ BÀI NHÁP TRONG KHÓA
# =========================================================

@admin_lessons_bp.post(
    "/khoa/<int:course_id>/xuat-ban"
)
def publish_course(
    course_id
):

    admin_id = int(
        g.account["id"]
    )


    try:

        with closing(
            get_connection()
        ) as connection:

            with closing(
                connection.cursor()
            ) as cursor:


                # =========================================
                # KIỂM TRA KHÓA
                # =========================================

                cursor.execute(
                    """
                    SELECT
                        MaKhoaHoc,
                        TieuDe

                    FROM dbo.KhoaHoc

                    WHERE
                        MaKhoaHoc = ?;
                    """,
                    course_id,
                )


                course = (
                    cursor.fetchone()
                )


                if course is None:

                    abort(
                        404,
                        description=(
                            "Không tìm thấy khóa học."
                        ),
                    )


                # =========================================
                # XUẤT BẢN BÀI NHÁP
                # =========================================

                cursor.execute(
                    """
                    UPDATE dbo.BaiHoc

                    SET
                        TrangThai =
                            'da_xuat_ban',

                        MaQuanTriVienCapNhat = ?,

                        NgayCapNhat =
                            SYSUTCDATETIME()

                    OUTPUT
                        INSERTED.MaBaiHoc

                    WHERE
                        MaKhoaHoc = ?
                        AND TrangThai =
                            'ban_nhap';
                    """,

                    admin_id,

                    course_id,
                )


                updated_rows = (
                    cursor.fetchall()
                )


                updated_count = len(
                    updated_rows
                )


            connection.commit()


    except pyodbc.Error:

        current_app.logger.error(
            (
                "Loi SQL khi xuat ban "
                "toan bo bai hoc."
            )
        )


        flash(
            (
                "Chưa thể xuất bản "
                "các bài học."
            ),
            "error",
        )


    else:

        if updated_count > 0:

            flash(
                (
                    f"Đã xuất bản "
                    f"{updated_count} bài "
                    f"trong khóa "
                    f"“{course[1]}”."
                ),
                "success",
            )


        else:

            flash(
                (
                    f"Khóa “{course[1]}” "
                    f"không còn bài nháp "
                    f"cần xuất bản."
                ),
                "success",
            )


    return redirect(
        url_for(
            "admin_lessons.index",

            course_id=
                course_id,
        )
    )