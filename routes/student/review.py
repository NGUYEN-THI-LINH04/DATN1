
from contextlib import closing

from flask import (
    Blueprint,
    render_template,
    request,
    abort,
    jsonify,
    g,
    current_app,
)

from database import get_connection


# =========================================================
# BLUEPRINT TỔNG ÔN
# =========================================================

review_bp = Blueprint(
    "review",
    __name__,
    url_prefix="/review"
)


# =========================================================
# HÀM HỖ TRỢ
# =========================================================

def row_to_dict(cursor, row):
    columns = [
        column[0]
        for column in cursor.description
    ]

    return dict(zip(columns, row))


def parse_lesson_ids(raw_value):
    """
    Chuyển lesson_ids=1,3,5 thành [1, 3, 5].
    Loại bỏ giá trị không hợp lệ và ID trùng.
    """

    lesson_ids = []

    if not raw_value:
        return lesson_ids

    for value in raw_value.split(","):
        value = value.strip()

        if not value:
            continue

        try:
            lesson_id = int(value)
        except (TypeError, ValueError):
            continue

        if lesson_id <= 0:
            continue

        if lesson_id not in lesson_ids:
            lesson_ids.append(lesson_id)

    return lesson_ids


# =========================================================
# 1. TRANG TỔNG ÔN TỪ VỰNG
#
# Ví dụ:
# /review/vocabulary?course_id=1
#
# /review/vocabulary?course_id=1&lesson_ids=1,3,5
# =========================================================

@review_bp.get("/vocabulary")
def vocabulary():

    # -----------------------------------------------------
    # 1.1. LẤY MÃ KHÓA HỌC
    # -----------------------------------------------------

    course_id = request.args.get(
        "course_id",
        type=int
    )

    if course_id is None or course_id <= 0:
        abort(
            400,
            description="Thiếu hoặc sai course_id."
        )

    raw_lesson_ids = (
        request.args.get("lesson_ids", "") or ""
    ).strip()

    requested_lesson_ids = parse_lesson_ids(
        raw_lesson_ids
    )

    # -----------------------------------------------------
    # 1.2. KHAI BÁO DỮ LIỆU
    # -----------------------------------------------------

    course = None

    all_lessons = []
    all_vocabularies = []

    selected_lessons = []
    selected_vocabularies = []
    selected_lesson_ids = []

    total_grammar = 0
    total_hanzi = 0

    # -----------------------------------------------------
    # 1.3. ĐỌC SQL SERVER
    # -----------------------------------------------------

    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cursor:

            # =============================================
            # THÔNG TIN KHÓA HỌC
            # =============================================

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

                FROM dbo.KhoaHoc AS kh

                WHERE kh.MaKhoaHoc = ?
                """,
                course_id
            )

            row = cursor.fetchone()

            if row is None:
                abort(
                    404,
                    description="Không tìm thấy khóa học."
                )

            course = row_to_dict(cursor, row)

            # =============================================
            # DANH SÁCH BÀI HỌC CỦA KHÓA
            # =============================================

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
                        FROM dbo.TuVungBaiHoc AS tvbh
                        WHERE tvbh.MaBaiHoc = bh.MaBaiHoc
                    ) AS SoTuVung,

                    (
                        SELECT COUNT(*)
                        FROM dbo.NguPhap AS np
                        WHERE np.MaBaiHoc = bh.MaBaiHoc
                    ) AS SoNguPhap,

                    (
                        SELECT COUNT(*)
                        FROM dbo.ChuHan AS ch
                        WHERE ch.MaBaiHoc = bh.MaBaiHoc
                    ) AS SoChuHan

                FROM dbo.BaiHoc AS bh

                WHERE bh.MaKhoaHoc = ?

                ORDER BY
                    bh.SoThuTuBai,
                    bh.MaBaiHoc
                """,
                course_id
            )

            for row in cursor.fetchall():
                lesson = row_to_dict(cursor, row)

                lesson["SoTuVung"] = int(
                    lesson["SoTuVung"] or 0
                )

                lesson["SoNguPhap"] = int(
                    lesson["SoNguPhap"] or 0
                )

                lesson["SoChuHan"] = int(
                    lesson["SoChuHan"] or 0
                )

                all_lessons.append(lesson)

            # =============================================
            # TỪ VỰNG THEO KHÓA HỌC
            #
            # TuVungBaiHoc -> TuVung
            # BaiHoc -> KhoaHoc
            # TuVung -> TepDaPhuongTien
            # =============================================

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

                    audio_tv.DuongDanTep
                        AS DuongDanAudio,

                    tv.MaNguon,
                    tv.DaDuyet,

                    tvbh.ThuTu,

                    bh.MaBaiHoc,
                    bh.SoThuTuBai,

                    bh.TieuDe AS TieuDeBaiHoc

                FROM dbo.TuVungBaiHoc AS tvbh

                INNER JOIN dbo.TuVung AS tv
                    ON tvbh.MaTuVung = tv.MaTuVung

                INNER JOIN dbo.BaiHoc AS bh
                    ON tvbh.MaBaiHoc = bh.MaBaiHoc

                LEFT JOIN dbo.TepDaPhuongTien AS audio_tv
                    ON tv.MaAmThanh = audio_tv.MaTep
                    AND audio_tv.LoaiTep = 'am_thanh'

                WHERE bh.MaKhoaHoc = ?

                ORDER BY
                    bh.SoThuTuBai,
                    tvbh.ThuTu,
                    tv.MaTuVung
                """,
                course_id
            )

            for row in cursor.fetchall():
                all_vocabularies.append(
                    row_to_dict(cursor, row)
                )

    # -----------------------------------------------------
    # 1.4. KIỂM TRA BÀI HỌC THUỘC KHÓA
    # -----------------------------------------------------

    valid_lesson_ids = {
        int(lesson["MaBaiHoc"])
        for lesson in all_lessons
    }

    if requested_lesson_ids:
        selected_lesson_ids = [
            lesson_id
            for lesson_id in requested_lesson_ids
            if lesson_id in valid_lesson_ids
        ]

        if not selected_lesson_ids:
            abort(
                400,
                description=(
                    "Không có bài học hợp lệ "
                    "trong khóa học này."
                )
            )

    elif raw_lesson_ids:
        # Có truyền lesson_ids nhưng nội dung sai.
        abort(
            400,
            description="Danh sách bài học không hợp lệ."
        )

    else:
        # Mặc định ôn toàn bộ khóa.
        selected_lesson_ids = [
            int(lesson["MaBaiHoc"])
            for lesson in all_lessons
        ]

    selected_lesson_id_set = set(
        selected_lesson_ids
    )

    # -----------------------------------------------------
    # 1.5. LỌC BÀI HỌC
    # -----------------------------------------------------

    selected_lessons = [
        lesson
        for lesson in all_lessons
        if int(lesson["MaBaiHoc"])
        in selected_lesson_id_set
    ]

    # -----------------------------------------------------
    # 1.6. LỌC TỪ VỰNG
    # -----------------------------------------------------

    selected_vocabularies = [
        word
        for word in all_vocabularies
        if int(word["MaBaiHoc"])
        in selected_lesson_id_set
    ]

    # -----------------------------------------------------
    # 1.7. TÍNH THỐNG KÊ
    # -----------------------------------------------------

    total_grammar = sum(
        int(lesson["SoNguPhap"] or 0)
        for lesson in selected_lessons
    )

    total_hanzi = sum(
        int(lesson["SoChuHan"] or 0)
        for lesson in selected_lessons
    )

    # -----------------------------------------------------
    # 1.8. TRẢ DỮ LIỆU VỀ HTML
    # -----------------------------------------------------

    return render_template(
        "student/review_vocab.html",

        course=course,
        lessons=selected_lessons,
        vocabularies=selected_vocabularies,

        selected_lesson_ids=selected_lesson_ids,

        total_lessons=len(selected_lessons),
        total_vocabulary=len(selected_vocabularies),
        total_grammar=total_grammar,
        total_hanzi=total_hanzi,
    )


# =========================================================
# 2. API LƯU KẾT QUẢ ÔN TẬP
#
# URL:
# POST /review/api/vocabulary-result
#
# Dữ liệu JS gửi:
# {
#     "word_id": 123,
#     "grade": 3
# }
#
# MỨC ĐỘ NHỚ:
# 1 = Quên rồi
# 2 = Khó
# 3 = Tốt
# 4 = Dễ
#
# SQL:
# TuVung
# TuVungDaLuu
# LichSuOnTap
# =========================================================

@review_bp.post("/api/vocabulary-result")
def save_vocabulary_result():

    # -----------------------------------------------------
    # 2.1. KIỂM TRA ĐĂNG NHẬP
    #
    # Hệ thống Mộc Hán lưu tài khoản trong g.account.
    # Chỉ lấy ID từ tài khoản đang đăng nhập.
    # -----------------------------------------------------

    account = getattr(g, "account", None)

    if (
        not account
        or account.get("role") != "student"
    ):
        return jsonify({
            "success": False,
            "message": (
                "Bạn cần đăng nhập bằng "
                "tài khoản người học."
            )
        }), 401

    try:
        user_id = int(account["id"])
    except (KeyError, TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Không xác định được người học."
        }), 401

    # -----------------------------------------------------
    # 2.2. NHẬN JSON
    # -----------------------------------------------------

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Dữ liệu gửi lên không hợp lệ."
        }), 400

    # Không chấp nhận boolean hay số thập phân.
    raw_word_id = data.get("word_id")
    raw_grade = data.get("grade")

    if (
        isinstance(raw_word_id, bool)
        or isinstance(raw_grade, bool)
    ):
        return jsonify({
            "success": False,
            "message": "Mã từ hoặc mức độ nhớ không hợp lệ."
        }), 400

    try:
        word_id = int(raw_word_id)
        grade = int(raw_grade)
    except (TypeError, ValueError, OverflowError):
        return jsonify({
            "success": False,
            "message": "Thiếu mã từ hoặc mức độ nhớ."
        }), 400

    if word_id <= 0 or grade not in (1, 2, 3, 4):
        return jsonify({
            "success": False,
            "message": "Mã từ hoặc mức độ nhớ không hợp lệ."
        }), 400

    # -----------------------------------------------------
    # 2.3. KHOẢNG CÁCH ÔN TẬP
    #
    # TuVungDaLuu.KhoangCachNgay là kiểu INT.
    # Đây là lịch ôn đơn giản theo ngày.
    # -----------------------------------------------------

    interval_days = {
        1: 0,    # Quên rồi
        2: 0,    # Khó
        3: 1,    # Tốt
        4: 4,    # Dễ
    }[grade]

    conn = None

    try:
        conn = get_connection()

        # Bảo đảm INSERT/UPDATE và ghi lịch sử
        # cùng thành công hoặc cùng rollback.
        conn.autocommit = False

        with closing(conn.cursor()) as cursor:

            # =============================================
            # BƯỚC 1: KIỂM TRA TỪ VỰNG
            # =============================================

            cursor.execute(
                """
                SELECT 1
                FROM dbo.TuVung
                WHERE MaTuVung = ?
                  AND DaDuyet = 1
                """,
                word_id
            )

            if cursor.fetchone() is None:
                conn.rollback()

                return jsonify({
                    "success": False,
                    "message": (
                        "Từ vựng không tồn tại "
                        "hoặc chưa được duyệt."
                    )
                }), 404

            # =============================================
            # BƯỚC 2: KIỂM TRA TỪ ĐÃ LƯU CHƯA
            #
            # TuVungDaLuu có khóa chính:
            # (MaNguoiDung, MaTuVung)
            #
            # Khóa truy vấn để hạn chế INSERT trùng
            # khi hai yêu cầu đến gần cùng lúc.
            # =============================================

            cursor.execute(
                """
                SELECT 1
                FROM dbo.TuVungDaLuu
                    WITH (UPDLOCK, HOLDLOCK)

                WHERE MaNguoiDung = ?
                  AND MaTuVung = ?
                """,
                user_id,
                word_id
            )

            already_saved = (
                cursor.fetchone() is not None
            )

            # =============================================
            # BƯỚC 3: THÊM HOẶC CẬP NHẬT TỪ ĐÃ LƯU
            # =============================================

            if already_saved:

                cursor.execute(
                    """
                    UPDATE dbo.TuVungDaLuu

                    SET
                        NgayOnTiepTheo = DATEADD(
                            DAY,
                            ?,
                            SYSUTCDATETIME()
                        ),

                        KhoangCachNgay = ?

                    WHERE MaNguoiDung = ?
                      AND MaTuVung = ?
                    """,
                    interval_days,
                    interval_days,
                    user_id,
                    word_id
                )

            else:

                cursor.execute(
                    """
                    INSERT INTO dbo.TuVungDaLuu
                    (
                        MaNguoiDung,
                        MaTuVung,
                        NgayLuu,
                        NgayOnTiepTheo,
                        KhoangCachNgay
                    )

                    VALUES
                    (
                        ?,
                        ?,
                        SYSUTCDATETIME(),
                        DATEADD(
                            DAY,
                            ?,
                            SYSUTCDATETIME()
                        ),
                        ?
                    )
                    """,
                    user_id,
                    word_id,
                    interval_days,
                    interval_days
                )

            # =============================================
            # BƯỚC 4: GHI LỊCH SỬ ÔN TẬP
            #
            # LichSuOnTap có khóa ngoại đến
            # TuVungDaLuu.
            #
            # Vì thế phải thực hiện sau bước 3.
            # =============================================

            cursor.execute(
                """
                INSERT INTO dbo.LichSuOnTap
                (
                    MaNguoiDung,
                    MaTuVung,
                    MucDoNho,
                    NgayOn
                )

                VALUES
                (
                    ?,
                    ?,
                    ?,
                    SYSUTCDATETIME()
                )
                """,
                user_id,
                word_id,
                grade
            )

            # =============================================
            # BƯỚC 5: ĐẾM SỐ TỪ KHÁC NHAU ĐÃ ÔN
            #
            # Ôn một từ nhiều lần chỉ tính 1 từ.
            # =============================================

            cursor.execute(
                """
                SELECT
                    COUNT(DISTINCT MaTuVung)

                FROM dbo.LichSuOnTap

                WHERE MaNguoiDung = ?
                """,
                user_id
            )

            row = cursor.fetchone()

            reviewed_count = int(
                row[0] if row and row[0] is not None else 0
            )

        # =============================================
        # BƯỚC 6: XÁC NHẬN GIAO DỊCH
        # =============================================

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Đã lưu kết quả ôn tập.",
            "word_id": word_id,
            "grade": grade,
            "reviewed_count": reviewed_count,
        }), 200

    # -----------------------------------------------------
    # 2.4. XỬ LÝ LỖI SQL SERVER
    # -----------------------------------------------------

    except Exception:

        if conn is not None:
            try:
                conn.rollback()
            except Exception:
                pass

        current_app.logger.exception(
            "Lỗi lưu lịch sử ôn tập từ vựng"
        )

        return jsonify({
            "success": False,
            "message": (
                "Không thể lưu kết quả ôn tập "
                "vào SQL Server."
            )
        }), 500

    finally:

        if conn is not None:
            conn.close()
