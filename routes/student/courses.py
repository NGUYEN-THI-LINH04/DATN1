
from flask import Blueprint, render_template, abort, g, redirect, url_for
from contextlib import closing

from database import get_connection


# =========================================================
# BLUEPRINT
# Giữ đúng tên courses_bp vì app.py hiện tại import tên này
# =========================================================
courses_bp = Blueprint(
    "courses",
    __name__,
    url_prefix="/courses"
)


# =========================================================
# DANH SÁCH KHÓA HỌC
# URL: /courses/
# =========================================================
@courses_bp.route("/")
def index():

    courses = []

    with closing(get_connection()) as conn:

        with closing(conn.cursor()) as cursor:

            cursor.execute(
                """
                SELECT
                    kh.MaKhoaHoc,
                    kh.MaCapDo,
                    kh.MaKyHieu,
                    kh.TieuDe,
                    kh.MoTa,
                    kh.PhienBanChuanHSK,
                    kh.TrangThai,

                    (
                        SELECT COUNT(*)
                        FROM dbo.BaiHoc bh
                        WHERE bh.MaKhoaHoc = kh.MaKhoaHoc
                    ) AS SoBaiHoc

                FROM dbo.KhoaHoc kh

                ORDER BY
                    kh.MaCapDo,
                    kh.MaKhoaHoc;
                """
            )

            rows = cursor.fetchall()

            for row in rows:

                ma_khoa_hoc = row[0]
                ma_cap_do = row[1]
                ma_ky_hieu = row[2]
                tieu_de = row[3]
                mo_ta = row[4]
                phien_ban = row[5]
                trang_thai = row[6]
                so_bai_hoc = int(row[7] or 0)

                # Giữ tên field cũ và tên theo SQL
                # để không ảnh hưởng template hiện tại.
                course = {

                    # Tên field cũ
                    "id": ma_khoa_hoc,
                    "level": ma_cap_do,
                    "code": ma_ky_hieu,
                    "title": tieu_de,
                    "description": mo_ta,
                    "version": phien_ban,
                    "status": trang_thai,
                    "lesson_count": so_bai_hoc,

                    # Tên field theo SQL
                    "MaKhoaHoc": ma_khoa_hoc,
                    "MaCapDo": ma_cap_do,
                    "MaKyHieu": ma_ky_hieu,
                    "TieuDe": tieu_de,
                    "MoTa": mo_ta,
                    "PhienBanChuanHSK": phien_ban,
                    "TrangThai": trang_thai,
                    "SoBaiHoc": so_bai_hoc,
                }

                courses.append(course)

    return render_template(
        "student/courses.html",
        courses=courses
    )


# =========================================================
# CHI TIẾT KHÓA HỌC
# Ví dụ: /courses/1
# =========================================================
@courses_bp.route("/<int:course_id>")
def detail(course_id):

    course = None
    lessons = []

    total_vocabulary = 0
    total_grammar = 0
    total_hanzi = 0

    with closing(get_connection()) as conn:

        with closing(conn.cursor()) as cursor:

            # =====================================================
            # 1. THÔNG TIN KHÓA HỌC
            # =====================================================
            cursor.execute(
                """
                SELECT
                    kh.MaKhoaHoc,
                    kh.MaCapDo,
                    kh.MaKyHieu,
                    kh.TieuDe,
                    kh.MoTa,
                    kh.PhienBanChuanHSK,
                    kh.TrangThai

                FROM dbo.KhoaHoc kh

                WHERE kh.MaKhoaHoc = ?;
                """,
                course_id
            )

            row = cursor.fetchone()

            if row is None:
                abort(404)

            ma_khoa_hoc = row[0]
            ma_cap_do = row[1]
            ma_ky_hieu = row[2]
            tieu_de = row[3]
            mo_ta = row[4]
            phien_ban = row[5]
            trang_thai = row[6]

            course = {

                # Key cũ
                "id": ma_khoa_hoc,
                "level": ma_cap_do,
                "code": ma_ky_hieu,
                "title": tieu_de,
                "description": mo_ta,
                "version": phien_ban,
                "status": trang_thai,

                # Key SQL
                "MaKhoaHoc": ma_khoa_hoc,
                "MaCapDo": ma_cap_do,
                "MaKyHieu": ma_ky_hieu,
                "TieuDe": tieu_de,
                "MoTa": mo_ta,
                "PhienBanChuanHSK": phien_ban,
                "TrangThai": trang_thai,
            }

            # =====================================================
            # 2. DANH SÁCH BÀI HỌC
            # =====================================================
            cursor.execute(
                """
                SELECT
                    bh.MaBaiHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe,
                    bh.TomTat,
                    bh.TrangThai,

                    (
                        SELECT COUNT(*)
                        FROM dbo.TuVungBaiHoc tvbh
                        WHERE tvbh.MaBaiHoc = bh.MaBaiHoc
                    ) AS SoTuVung,

                    (
                        SELECT COUNT(*)
                        FROM dbo.NguPhap ng
                        WHERE ng.MaBaiHoc = bh.MaBaiHoc
                    ) AS SoNguPhap,

                    (
                        SELECT COUNT(*)
                        FROM dbo.ChuHan ch
                        WHERE ch.MaBaiHoc = bh.MaBaiHoc
                    ) AS SoChuHan

                FROM dbo.BaiHoc bh

                WHERE bh.MaKhoaHoc = ?

                ORDER BY bh.SoThuTuBai;
                """,
                course_id
            )

            lesson_rows = cursor.fetchall()

            for row in lesson_rows:

                ma_bai_hoc = row[0]
                so_thu_tu = row[1]
                tieu_de_bai = row[2]
                tom_tat = row[3]
                trang_thai_bai = row[4]

                so_tu_vung = int(row[5] or 0)
                so_ngu_phap = int(row[6] or 0)
                so_chu_han = int(row[7] or 0)

                lesson = {

                    # Key cũ
                    "id": ma_bai_hoc,
                    "order": so_thu_tu,
                    "title": tieu_de_bai,
                    "summary": tom_tat,
                    "status": trang_thai_bai,

                    "vocabulary_count": so_tu_vung,
                    "grammar_count": so_ngu_phap,
                    "hanzi_count": so_chu_han,

                    # Key SQL
                    "MaBaiHoc": ma_bai_hoc,
                    "SoThuTuBai": so_thu_tu,
                    "TieuDe": tieu_de_bai,
                    "TomTat": tom_tat,
                    "TrangThai": trang_thai_bai,

                    "SoTuVung": so_tu_vung,
                    "SoNguPhap": so_ngu_phap,
                    "SoChuHan": so_chu_han,
                }

                lessons.append(lesson)

            # =====================================================
            # 3. TỔNG TỪ VỰNG
            # =====================================================
            cursor.execute(
                """
                SELECT COUNT(*)

                FROM dbo.TuVungBaiHoc tvbh

                INNER JOIN dbo.BaiHoc bh
                    ON tvbh.MaBaiHoc = bh.MaBaiHoc

                WHERE bh.MaKhoaHoc = ?;
                """,
                course_id
            )

            total_vocabulary = int(
                cursor.fetchone()[0] or 0
            )

            # =====================================================
            # 4. TỔNG NGỮ PHÁP
            # =====================================================
            cursor.execute(
                """
                SELECT COUNT(*)

                FROM dbo.NguPhap ng

                INNER JOIN dbo.BaiHoc bh
                    ON ng.MaBaiHoc = bh.MaBaiHoc

                WHERE bh.MaKhoaHoc = ?;
                """,
                course_id
            )

            total_grammar = int(
                cursor.fetchone()[0] or 0
            )

            # =====================================================
            # 5. TỔNG CHỮ HÁN
            # =====================================================
            cursor.execute(
                """
                SELECT COUNT(*)

                FROM dbo.ChuHan ch

                INNER JOIN dbo.BaiHoc bh
                    ON ch.MaBaiHoc = bh.MaBaiHoc

                WHERE bh.MaKhoaHoc = ?;
                """,
                course_id
            )

            total_hanzi = int(
                cursor.fetchone()[0] or 0
            )

    # =========================================================
    # 6. TIẾN ĐỘ HỌC TẬP
    # Chỉ tính các bài đã được đánh dấu hoàn thành.
    # =====================================================
    total_lessons = len(lessons)
    completed_lessons = 0

    account = getattr(g, "account", None)

    if account is not None and account.get("role") == "student":

        with closing(get_connection()) as conn:

            with closing(conn.cursor()) as cursor:

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.TienDoBaiHoc
                    WHERE MaNguoiDung = ?
                      AND MaKhoaHoc = ?
                      AND TrangThai = 'hoan_thanh';
                    """,
                    int(account["id"]),
                    course_id
                )

                completed_lessons = int(
                    cursor.fetchone()[0] or 0
                )

    completed_lessons = min(
        completed_lessons,
        total_lessons
    )

    progress_percent = (
        round(completed_lessons * 100 / total_lessons)
        if total_lessons else 0
    )

    # =========================================================
    # TRẢ VỀ GIAO DIỆN CHI TIẾT KHÓA HỌC
    # =========================================================
    return render_template(
        "student/courses_detail.html",

        course=course,
        lessons=lessons,

        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        progress_percent=progress_percent,

        total_vocabulary=total_vocabulary,
        total_grammar=total_grammar,
        total_hanzi=total_hanzi
    )


# =========================================================
# 7. ĐÁNH DẤU HOÀN THÀNH BÀI HỌC
# =========================================================
@courses_bp.post(
    "/<int:course_id>/bai-hoc/<int:lesson_id>/hoan-thanh"
)
def complete_lesson(course_id, lesson_id):

    account = getattr(g, "account", None)

    # Chỉ người học đã đăng nhập được đánh dấu
    if not account or account.get("role") != "student":
        return redirect(url_for("auth.login"))

    user_id = int(account["id"])

    with closing(get_connection()) as conn:

        with closing(conn.cursor()) as cursor:

            # Kiểm tra bài học có thuộc khóa này không
            cursor.execute(
                """
                SELECT 1
                FROM dbo.BaiHoc
                WHERE MaBaiHoc = ?
                  AND MaKhoaHoc = ?;
                """,
                lesson_id,
                course_id
            )

            if cursor.fetchone() is None:
                abort(404)

            # Đã có tiến độ thì cập nhật.
            # Chưa có thì tạo mới.
            cursor.execute(
                """
                UPDATE dbo.TienDoBaiHoc
                SET
                    TrangThai = 'hoan_thanh',
                    NgayHoanThanh = COALESCE(
                        NgayHoanThanh,
                        SYSUTCDATETIME()
                    ),
                    LanTruyCapCuoi = SYSUTCDATETIME()
                WHERE MaNguoiDung = ?
                  AND MaBaiHoc = ?;

                IF @@ROWCOUNT = 0
                BEGIN
                    INSERT INTO dbo.TienDoBaiHoc
                    (
                        MaNguoiDung,
                        MaKhoaHoc,
                        MaBaiHoc,
                        TrangThai,
                        LanTruyCapCuoi,
                        NgayHoanThanh
                    )
                    VALUES
                    (
                        ?, ?, ?,
                        'hoan_thanh',
                        SYSUTCDATETIME(),
                        SYSUTCDATETIME()
                    );
                END;
                """,
                user_id,
                lesson_id,
                user_id,
                course_id,
                lesson_id
            )

        conn.commit()

    return redirect(
        url_for(
            "courses.detail",
            course_id=course_id
        )
    )
