
from contextlib import closing
import math

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

admin_vocabulary_bp = Blueprint(
    "admin_vocabulary",
    __name__,
    url_prefix="/admin/tu-vung",
)


# =========================================================
# KIEM TRA QUYEN ADMIN
# =========================================================

@admin_vocabulary_bp.before_request
def require_admin():
    account = getattr(g, "account", None)

    if account is None:
        return redirect(url_for("auth.admin_login"))

    if account["role"] != "admin":
        abort(
            403,
            description="Bạn không có quyền quản lý từ vựng."
        )


@admin_vocabulary_bp.errorhandler(pyodbc.Error)
def handle_database_error(error):
    current_app.logger.exception(
        "Lỗi SQL trong quản lý từ vựng"
    )

    return (
        "Chưa thể xử lý dữ liệu từ vựng. "
        "Vui lòng thử lại.",
        503,
    )


# =========================================================
# 1. LAY DANH SACH KHOA VA BAI
# =========================================================

def get_filter_data():
    courses = []
    lessons = []

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:

            cursor.execute(
                """
                SELECT
                    MaKhoaHoc,
                    MaCapDo,
                    TieuDe
                FROM dbo.KhoaHoc
                ORDER BY MaCapDo, MaKhoaHoc
                """
            )

            for row in cursor.fetchall():
                courses.append({
                    "id": row[0],
                    "level": row[1],
                    "title": row[2],
                })

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
                    ON kh.MaKhoaHoc = bh.MaKhoaHoc
                ORDER BY
                    kh.MaCapDo,
                    bh.SoThuTuBai,
                    bh.MaBaiHoc
                """
            )

            for row in cursor.fetchall():
                lessons.append({
                    "id": row[0],
                    "course_id": row[1],
                    "order": row[2],
                    "title": row[3],
                    "level": row[4],
                })

    return courses, lessons


# =========================================================
# 2. LAY CHI TIET MOT TU
# =========================================================

def get_word(vocabulary_id):
    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    MaTuVung,
                    ChuHan,
                    ChuPhonThe,
                    PhienAm,
                    NghiaTiengViet,
                    TuLoai,
                    ViDuTiengTrung,
                    ViDuTiengViet,
                    MaAmThanh,
                    MaNguon,
                    DaDuyet,
                    NgayTao,
                    MaQuanTriVienCapNhat,
                    NgayCapNhat
                FROM dbo.TuVung
                WHERE MaTuVung = ?
                """,
                vocabulary_id,
            )

            row = cursor.fetchone()

    if row is None:
        abort(404, description="Không tìm thấy từ vựng.")

    return {
        "id": row[0],
        "hanzi": row[1] or "",
        "traditional": row[2] or "",
        "pinyin": row[3] or "",
        "meaning": row[4] or "",
        "word_type": row[5] or "",
        "example_zh": row[6] or "",
        "example_vi": row[7] or "",
        "audio_id": row[8],
        "source_id": row[9],
        "approved": bool(row[10]),
        "created_at": row[11],
        "admin_updated_id": row[12],
        "updated_at": row[13],
    }


# =========================================================
# 3. TRANG QUAN LY TU VUNG
# =========================================================

@admin_vocabulary_bp.get("/")
def index():

    keyword = request.args.get("q", "").strip()[:200]

    course_id = request.args.get(
        "course_id",
        type=int,
    )

    lesson_id = request.args.get(
        "lesson_id",
        type=int,
    )

    approval = request.args.get(
        "approval",
        "all",
    )

    edit_id = request.args.get(
        "edit",
        type=int,
    )

    page = max(
        request.args.get("page", 1, type=int),
        1,
    )

    page_size = 30

    if approval not in {
        "all",
        "approved",
        "pending",
    }:
        approval = "all"

    courses, lessons = get_filter_data()

    conditions = []
    params = []

    # -----------------------------------------------------
    # TIM KIEM
    # -----------------------------------------------------

    if keyword:
        conditions.append(
            """
            (
                CHARINDEX(?, tv.ChuHan) > 0
                OR CHARINDEX(?, tv.PhienAm) > 0
                OR CHARINDEX(?, tv.NghiaTiengViet) > 0
            )
            """
        )

        params.extend([
            keyword,
            keyword,
            keyword,
        ])

    # -----------------------------------------------------
    # LOC TRANG THAI DUYET
    # -----------------------------------------------------

    if approval == "approved":
        conditions.append("tv.DaDuyet = 1")

    elif approval == "pending":
        conditions.append("tv.DaDuyet = 0")

    # -----------------------------------------------------
    # LOC KHOA HOC
    # -----------------------------------------------------

    if course_id is not None:
        conditions.append(
            """
            EXISTS (
                SELECT 1
                FROM dbo.TuVungBaiHoc AS tvbh_filter
                INNER JOIN dbo.BaiHoc AS bh_filter
                    ON bh_filter.MaBaiHoc =
                       tvbh_filter.MaBaiHoc
                WHERE
                    tvbh_filter.MaTuVung = tv.MaTuVung
                    AND bh_filter.MaKhoaHoc = ?
            )
            """
        )

        params.append(course_id)

    # -----------------------------------------------------
    # LOC BAI HOC
    # -----------------------------------------------------

    if lesson_id is not None:
        conditions.append(
            """
            EXISTS (
                SELECT 1
                FROM dbo.TuVungBaiHoc AS tvbh_filter
                WHERE
                    tvbh_filter.MaTuVung = tv.MaTuVung
                    AND tvbh_filter.MaBaiHoc = ?
            )
            """
        )

        params.append(lesson_id)

    where_sql = ""

    if conditions:
        where_sql = " WHERE " + " AND ".join(conditions)

    vocabularies = []

    # -----------------------------------------------------
    # TRUY VAN SQL
    # -----------------------------------------------------

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:

            # THONG KE TOAN BO KHO TU VUNG
            # Khong phu thuoc bo loc tren giao dien.

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongSoTu,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN DaDuyet = 1 THEN 1
                                ELSE 0
                            END
                        ),
                        0
                    ) AS SoDaDuyet,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN DaDuyet = 0 THEN 1
                                ELSE 0
                            END
                        ),
                        0
                    ) AS SoChuaDuyet

                FROM dbo.TuVung
                """
            )

            stats = cursor.fetchone()

            vocabulary_total = int(stats[0] or 0)
            approved_count = int(stats[1] or 0)
            pending_count = int(stats[2] or 0)

            # DEM SO TU THEO BO LOC HIEN TAI

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dbo.TuVung AS tv
                """
                + where_sql,
                *params,
            )

            total_items = int(
                cursor.fetchone()[0] or 0
            )

            total_pages = max(
                math.ceil(total_items / page_size),
                1,
            )

            page = min(page, total_pages)

            offset = (page - 1) * page_size

            # LAY DANH SACH CO PHAN TRANG

            cursor.execute(
                """
                SELECT
                    tv.MaTuVung,
                    tv.ChuHan,
                    tv.PhienAm,
                    tv.NghiaTiengViet,
                    tv.TuLoai,
                    tv.DaDuyet,
                    tv.MaAmThanh,

                    (
                        SELECT COUNT(*)
                        FROM dbo.TuVungBaiHoc AS tvbh_count
                        WHERE
                            tvbh_count.MaTuVung =
                            tv.MaTuVung
                    ) AS SoBaiSuDung,

                    (
                        SELECT TOP 1
                            CONCAT(
                                N'HSK ',
                                kh.MaCapDo,
                                N' · Bài ',
                                bh.SoThuTuBai
                            )

                        FROM dbo.TuVungBaiHoc AS tvbh_first

                        INNER JOIN dbo.BaiHoc AS bh
                            ON bh.MaBaiHoc =
                               tvbh_first.MaBaiHoc

                        INNER JOIN dbo.KhoaHoc AS kh
                            ON kh.MaKhoaHoc =
                               bh.MaKhoaHoc

                        WHERE
                            tvbh_first.MaTuVung =
                            tv.MaTuVung

                        ORDER BY
                            kh.MaCapDo,
                            bh.SoThuTuBai
                    ) AS BaiDauTien

                FROM dbo.TuVung AS tv
                """
                + where_sql
                + """
                ORDER BY tv.MaTuVung

                OFFSET ? ROWS
                FETCH NEXT ? ROWS ONLY
                """,
                *params,
                offset,
                page_size,
            )

            for row in cursor.fetchall():
                vocabularies.append({
                    "id": row[0],
                    "hanzi": row[1] or "",
                    "pinyin": row[2] or "",
                    "meaning": row[3] or "",
                    "word_type": row[4] or "",
                    "approved": bool(row[5]),
                    "has_audio": row[6] is not None,
                    "lesson_count": int(row[7] or 0),
                    "first_lesson": (
                        row[8] or "Chưa gắn bài"
                    ),
                })

    # -----------------------------------------------------
    # TU DANG CHINH SUA
    # -----------------------------------------------------

    editing_word = None

    if edit_id is not None:
        editing_word = get_word(edit_id)

    return render_template(
        "admin/vocabulary.html",
        active_page="vocabulary",
        vocabularies=vocabularies,
        courses=courses,
        lessons=lessons,
        keyword=keyword,
        selected_course=course_id,
        selected_lesson=lesson_id,
        approval=approval,
        page=page,
        total_pages=total_pages,
        total_items=total_items,
        editing_word=editing_word,

        # Du lieu moi cho khoi duyet hang loat
        vocabulary_total=vocabulary_total,
        approved_count=approved_count,
        pending_count=pending_count,
    )


# =========================================================
# 4. CHINH SUA TU VUNG
# =========================================================

@admin_vocabulary_bp.post("/<int:vocabulary_id>/sua")
def edit(vocabulary_id):

    get_word(vocabulary_id)

    hanzi = request.form.get(
        "hanzi", ""
    ).strip()

    traditional = request.form.get(
        "traditional", ""
    ).strip()

    pinyin = request.form.get(
        "pinyin", ""
    ).strip()

    meaning = request.form.get(
        "meaning", ""
    ).strip()

    word_type = request.form.get(
        "word_type", ""
    ).strip()

    example_zh = request.form.get(
        "example_zh", ""
    ).strip()

    example_vi = request.form.get(
        "example_vi", ""
    ).strip()

    # -----------------------------------------------------
    # KIEM TRA DU LIEU
    # -----------------------------------------------------

    if not hanzi:
        flash(
            "Chữ Hán không được để trống.",
            "error",
        )
        return redirect(
            url_for(
                "admin_vocabulary.index",
                edit=vocabulary_id,
            )
        )

    if not pinyin:
        flash(
            "Pinyin không được để trống.",
            "error",
        )
        return redirect(
            url_for(
                "admin_vocabulary.index",
                edit=vocabulary_id,
            )
        )

    if not meaning:
        flash(
            "Nghĩa tiếng Việt không được để trống.",
            "error",
        )
        return redirect(
            url_for(
                "admin_vocabulary.index",
                edit=vocabulary_id,
            )
        )

    validations = [
        (hanzi, 100, "Chữ Hán"),
        (traditional, 100, "Chữ phồn thể"),
        (pinyin, 200, "Pinyin"),
        (meaning, 2000, "Nghĩa tiếng Việt"),
    ]

    for value, limit, label in validations:
        if len(value) > limit:
            flash(
                f"{label} không được quá {limit} ký tự.",
                "error",
            )
            return redirect(
                url_for(
                    "admin_vocabulary.index",
                    edit=vocabulary_id,
                )
            )

    admin_id = int(g.account["id"])

    # -----------------------------------------------------
    # CAP NHAT SQL
    # -----------------------------------------------------

    with closing(get_connection()) as connection:
        try:
            with closing(connection.cursor()) as cursor:

                cursor.execute(
                    """
                    UPDATE dbo.TuVung

                    SET
                        ChuHan = ?,
                        ChuPhonThe = ?,
                        PhienAm = ?,
                        NghiaTiengViet = ?,
                        TuLoai = ?,
                        ViDuTiengTrung = ?,
                        ViDuTiengViet = ?,
                        MaQuanTriVienCapNhat = ?,
                        NgayCapNhat = SYSDATETIME()

                    WHERE MaTuVung = ?
                    """,
                    hanzi,
                    traditional or None,
                    pinyin,
                    meaning,
                    word_type or None,
                    example_zh or None,
                    example_vi or None,
                    admin_id,
                    vocabulary_id,
                )

                if cursor.rowcount == 0:
                    abort(
                        404,
                        description="Không tìm thấy từ vựng.",
                    )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    flash(
        "Đã cập nhật từ vựng vào SQL Server.",
        "success",
    )

    return redirect(
        url_for("admin_vocabulary.index")
    )


# =========================================================
# 5. DUYET / BO DUYET MOT TU
# =========================================================

@admin_vocabulary_bp.post(
    "/<int:vocabulary_id>/duyet"
)
def toggle_approval(vocabulary_id):

    word = get_word(vocabulary_id)

    new_value = 0 if word["approved"] else 1

    admin_id = int(g.account["id"])

    with closing(get_connection()) as connection:
        try:
            with closing(connection.cursor()) as cursor:

                cursor.execute(
                    """
                    UPDATE dbo.TuVung

                    SET
                        DaDuyet = ?,
                        MaQuanTriVienCapNhat = ?,
                        NgayCapNhat = SYSUTCDATETIME()

                    WHERE MaTuVung = ?
                    """,
                    new_value,
                    admin_id,
                    vocabulary_id,
                )

                if cursor.rowcount == 0:
                    abort(
                        404,
                        description="Không tìm thấy từ vựng.",
                    )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    if new_value == 1:
        message = "Đã duyệt từ vựng."
    else:
        message = "Đã chuyển từ vựng về chưa duyệt."

    flash(message, "success")

    return redirect(
        request.referrer
        or url_for("admin_vocabulary.index")
    )


# =========================================================
# 6. DUYET TOAN BO TU CHUA DUYET
# =========================================================

@admin_vocabulary_bp.post("/duyet-tat-ca")
def approve_all():

    admin_id = int(g.account["id"])

    with closing(get_connection()) as connection:
        try:
            with closing(connection.cursor()) as cursor:

                cursor.execute(
                    """
                    UPDATE dbo.TuVung

                    SET
                        DaDuyet = 1,
                        MaQuanTriVienCapNhat = ?,
                        NgayCapNhat = SYSUTCDATETIME()

                    OUTPUT INSERTED.MaTuVung

                    WHERE DaDuyet = 0
                    """,
                    admin_id,
                )

                updated_count = len(
                    cursor.fetchall()
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    if updated_count > 0:
        flash(
            f"Đã duyệt thành công "
            f"{updated_count} từ vựng.",
            "success",
        )
    else:
        flash(
            "Không còn từ vựng nào cần duyệt.",
            "success",
        )

    return redirect(
        url_for("admin_vocabulary.index")
    )
