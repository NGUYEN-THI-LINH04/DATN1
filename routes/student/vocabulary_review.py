
from contextlib import closing

from flask import (
    Blueprint,
    abort,
    current_app,
    g,
    jsonify,
    render_template,
    request,
)

from database import get_connection


# ============================================================
# MỘC HÁN - ÔN TẬP TỪ VỰNG CÁ NHÂN
#
# Sử dụng các bảng SQL Server:
#   dbo.TuVung
#   dbo.TuVungBaiHoc
#   dbo.TuVungDaLuu
#   dbo.LichSuOnTap
#   dbo.TepDaPhuongTien
#
# Không sử dụng localStorage để lưu danh sách từ.
# Không can thiệp vào Tổng ôn HSK.
# ============================================================

vocabulary_review_bp = Blueprint(
    "vocabulary_review",
    __name__,
    url_prefix="/vocabulary-review"
)


# ============================================================
# HÀM HỖ TRỢ
# ============================================================

def get_student_id():
    """Lấy mã người học đang đăng nhập."""

    account = getattr(g, "account", None)

    if not account or account.get("role") != "student":
        abort(
            401,
            description="Bạn cần đăng nhập bằng tài khoản người học."
        )

    return int(account["id"])


def get_json_data():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        abort(400, description="Dữ liệu JSON không hợp lệ.")

    return data


def positive_int(value):
    """Chỉ nhận số nguyên dương."""

    if isinstance(value, bool):
        return None

    try:
        number = int(value)
    except (TypeError, ValueError, OverflowError):
        return None

    return number if number > 0 else None


def row_to_dict(cursor, row):
    columns = [column[0] for column in cursor.description]
    return dict(zip(columns, row))


def database_error(error):
    current_app.logger.exception(
        "Lỗi SQL trong chức năng ôn tập từ vựng"
    )

    return jsonify({
        "success": False,
        "message": "Không thể xử lý dữ liệu SQL Server."
    }), 500


# ============================================================
# 1. TRANG ÔN TẬP CÁ NHÂN
#
# GET /vocabulary-review/
# ============================================================

@vocabulary_review_bp.get("/")
def index():
    get_student_id()

    return render_template(
        "student/vocabulary_review.html"
    )


# ============================================================
# 2. DANH SÁCH TỪ VỰNG ĐÃ LƯU
#
# GET /vocabulary-review/api/words
# ============================================================

@vocabulary_review_bp.get("/api/words")
def get_saved_words():

    user_id = get_student_id()

    try:
        with closing(get_connection()) as conn:
            with closing(conn.cursor()) as cursor:

                cursor.execute(
                    """
                    SELECT
                        tv.MaTuVung AS id,
                        tv.ChuHan AS hanzi,
                        tv.ChuPhonThe AS traditional,
                        tv.PhienAm AS pinyin,
                        tv.NghiaTiengViet AS meaning,
                        tv.TuLoai AS wordType,
                        tv.ViDuTiengTrung AS exampleChinese,
                        tv.ViDuTiengViet AS exampleVietnamese,
                        audio.DuongDanTep AS audioUrl,

                        saved.NgayLuu AS savedAt,
                        saved.NgayOnTiepTheo AS nextReviewAt,
                        saved.KhoangCachNgay AS intervalDays,

                        (
                            SELECT COUNT(*)
                            FROM dbo.LichSuOnTap AS history
                            WHERE history.MaNguoiDung =
                                  saved.MaNguoiDung
                              AND history.MaTuVung =
                                  saved.MaTuVung
                        ) AS reviewCount

                    FROM dbo.TuVungDaLuu AS saved

                    INNER JOIN dbo.TuVung AS tv
                        ON tv.MaTuVung = saved.MaTuVung

                    LEFT JOIN dbo.TepDaPhuongTien AS audio
                        ON audio.MaTep = tv.MaAmThanh
                       AND audio.LoaiTep = 'am_thanh'

                    WHERE saved.MaNguoiDung = ?

                    ORDER BY
                        CASE
                            WHEN saved.NgayOnTiepTheo IS NULL
                                THEN 0
                            WHEN saved.NgayOnTiepTheo
                                 <= SYSUTCDATETIME()
                                THEN 0
                            ELSE 1
                        END,
                        saved.NgayOnTiepTheo,
                        saved.NgayLuu DESC,
                        tv.MaTuVung
                    """,
                    user_id
                )

                words = []

                for row in cursor.fetchall():
                    word = row_to_dict(cursor, row)

                    for key in ("savedAt", "nextReviewAt"):
                        value = word.get(key)

                        word[key] = (
                            value.isoformat()
                            if value is not None
                            else None
                        )

                    word["intervalDays"] = int(
                        word["intervalDays"] or 0
                    )

                    word["reviewCount"] = int(
                        word["reviewCount"] or 0
                    )

                    words.append(word)

        return jsonify({
            "success": True,
            "total": len(words),
            "words": words
        })

    except Exception as error:
        return database_error(error)


# ============================================================
# 3. LẤY DANH SÁCH ID TỪ ĐÃ LƯU
#
# GET /vocabulary-review/api/saved-ids
#
# Dùng để đồng bộ trạng thái dấu sao trong bài học.
# ============================================================

@vocabulary_review_bp.get("/api/saved-ids")
def get_saved_ids():

    user_id = get_student_id()

    try:
        with closing(get_connection()) as conn:
            with closing(conn.cursor()) as cursor:

                cursor.execute(
                    """
                    SELECT MaTuVung
                    FROM dbo.TuVungDaLuu
                    WHERE MaNguoiDung = ?
                    """,
                    user_id
                )

                word_ids = [
                    int(row[0])
                    for row in cursor.fetchall()
                ]

        return jsonify({
            "success": True,
            "word_ids": word_ids
        })

    except Exception as error:
        return database_error(error)


# ============================================================
# 4. THÊM MỘT TỪ VÀO ÔN TẬP
#
# POST /vocabulary-review/api/save-word
#
# JSON:
# {
#     "word_id": 123
# }
# ============================================================

@vocabulary_review_bp.post("/api/save-word")
def save_word():

    user_id = get_student_id()
    data = get_json_data()

    word_id = positive_int(data.get("word_id"))

    if word_id is None:
        return jsonify({
            "success": False,
            "message": "Mã từ vựng không hợp lệ."
        }), 400

    try:
        with closing(get_connection()) as conn:
            try:
                with closing(conn.cursor()) as cursor:

                    # Chỉ cho phép lưu từ đã duyệt.
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
                        return jsonify({
                            "success": False,
                            "message": "Không tìm thấy từ vựng hợp lệ."
                        }), 404

                    # Không thêm trùng từ.
                    cursor.execute(
                        """
                        IF NOT EXISTS (
                            SELECT 1
                            FROM dbo.TuVungDaLuu
                                WITH (UPDLOCK, HOLDLOCK)
                            WHERE MaNguoiDung = ?
                              AND MaTuVung = ?
                        )
                        BEGIN
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
                                SYSUTCDATETIME(),
                                0
                            )
                        END
                        """,
                        user_id,
                        word_id,
                        user_id,
                        word_id
                    )

                conn.commit()

            except Exception:
                conn.rollback()
                raise

        return jsonify({
            "success": True,
            "message": "Đã thêm từ vào ôn tập.",
            "word_id": word_id
        })

    except Exception as error:
        return database_error(error)


# ============================================================
# 5. THÊM TOÀN BỘ TỪ VỰNG CỦA MỘT BÀI
#
# POST /vocabulary-review/api/save-lesson
#
# JSON:
# {
#     "lesson_id": 12
# }
#
# Lấy dữ liệu từ TuVungBaiHoc.
# Không cần JS gửi toàn bộ nội dung từ.
# ============================================================

@vocabulary_review_bp.post("/api/save-lesson")
def save_lesson():

    user_id = get_student_id()
    data = get_json_data()

    lesson_id = positive_int(data.get("lesson_id"))

    if lesson_id is None:
        return jsonify({
            "success": False,
            "message": "Mã bài học không hợp lệ."
        }), 400

    try:
        with closing(get_connection()) as conn:
            try:
                with closing(conn.cursor()) as cursor:

                    cursor.execute(
                        """
                        SELECT 1
                        FROM dbo.BaiHoc
                        WHERE MaBaiHoc = ?
                        """,
                        lesson_id
                    )

                    if cursor.fetchone() is None:
                        return jsonify({
                            "success": False,
                            "message": "Không tìm thấy bài học."
                        }), 404

                    # Lấy những từ đã duyệt thuộc bài học.
                    cursor.execute(
                        """
                        SELECT DISTINCT tv.MaTuVung
                        FROM dbo.TuVungBaiHoc AS tvbh
                        INNER JOIN dbo.TuVung AS tv
                            ON tv.MaTuVung = tvbh.MaTuVung
                        WHERE tvbh.MaBaiHoc = ?
                          AND tv.DaDuyet = 1
                        """,
                        lesson_id
                    )

                    word_ids = [
                        int(row[0])
                        for row in cursor.fetchall()
                    ]

                    # Lưu từng từ trong cùng giao dịch.
                    # Không ghi đè lịch ôn của từ đã có.
                    for word_id in word_ids:
                        cursor.execute(
                            """
                            IF NOT EXISTS (
                                SELECT 1
                                FROM dbo.TuVungDaLuu
                                    WITH (UPDLOCK, HOLDLOCK)
                                WHERE MaNguoiDung = ?
                                  AND MaTuVung = ?
                            )
                            BEGIN
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
                                    SYSUTCDATETIME(),
                                    0
                                )
                            END
                            """,
                            user_id,
                            word_id,
                            user_id,
                            word_id
                        )

                conn.commit()

            except Exception:
                conn.rollback()
                raise

        return jsonify({
            "success": True,
            "message": "Đã thêm từ vựng của bài vào ôn tập.",
            "lesson_id": lesson_id,
            "total": len(word_ids),
            "word_ids": word_ids
        })

    except Exception as error:
        return database_error(error)


# ============================================================
# 6. BỎ MỘT TỪ KHỎI DANH SÁCH ÔN TẬP
#
# POST /vocabulary-review/api/remove-word
#
# JSON:
# {
#     "word_id": 123
# }
#
# LƯU Ý:
# LichSuOnTap tham chiếu tới TuVungDaLuu.
# Không được xóa trực tiếp khi đã có lịch sử.
#
# Để bảo toàn Tiến độ học, API từ chối xóa
# những từ đã có lịch sử ôn.
# ============================================================

@vocabulary_review_bp.post("/api/remove-word")
def remove_word():

    user_id = get_student_id()
    data = get_json_data()

    word_id = positive_int(data.get("word_id"))

    if word_id is None:
        return jsonify({
            "success": False,
            "message": "Mã từ vựng không hợp lệ."
        }), 400

    try:
        with closing(get_connection()) as conn:
            try:
                with closing(conn.cursor()) as cursor:

                    cursor.execute(
                        """
                        SELECT 1
                        FROM dbo.LichSuOnTap
                        WHERE MaNguoiDung = ?
                          AND MaTuVung = ?
                        """,
                        user_id,
                        word_id
                    )

                    if cursor.fetchone() is not None:
                        return jsonify({
                            "success": False,
                            "message": (
                                "Từ này đã có lịch sử ôn tập. "
                                "Hệ thống giữ lại để bảo toàn "
                                "dữ liệu Tiến độ học."
                            )
                        }), 409

                    cursor.execute(
                        """
                        DELETE FROM dbo.TuVungDaLuu
                        WHERE MaNguoiDung = ?
                          AND MaTuVung = ?
                        """,
                        user_id,
                        word_id
                    )

                conn.commit()

            except Exception:
                conn.rollback()
                raise

        return jsonify({
            "success": True,
            "message": "Đã bỏ từ khỏi danh sách ôn tập.",
            "word_id": word_id
        })

    except Exception as error:
        return database_error(error)


# ============================================================
# 7. LƯU KẾT QUẢ ÔN TẬP
#
# POST /vocabulary-review/api/review
#
# JSON:
# {
#     "word_id": 123,
#     "grade": 3
# }
#
# MucDoNho:
# 1 - Quên rồi
# 2 - Khó
# 3 - Tốt
# 4 - Dễ
#
# Chỉ cho phép ôn những từ đã lưu.
# ============================================================

@vocabulary_review_bp.post("/api/review")
def save_review_result():

    user_id = get_student_id()
    data = get_json_data()

    word_id = positive_int(data.get("word_id"))
    grade = positive_int(data.get("grade"))

    if word_id is None or grade not in (1, 2, 3, 4):
        return jsonify({
            "success": False,
            "message": "Mã từ hoặc mức độ nhớ không hợp lệ."
        }), 400

    # Lịch ôn theo ngày, tương thích SQL hiện tại.
    # Chưa thể lưu chính xác phút vì bảng chỉ có
    # KhoangCachNgay kiểu INT.
    intervals = {
        1: 0,
        2: 0,
        3: 1,
        4: 4
    }

    interval_days = intervals[grade]

    try:
        with closing(get_connection()) as conn:
            try:
                with closing(conn.cursor()) as cursor:

                    # Khóa bản ghi từ đã lưu.
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

                    if cursor.fetchone() is None:
                        return jsonify({
                            "success": False,
                            "message": (
                                "Bạn cần thêm từ vào danh sách "
                                "ôn tập trước khi luyện."
                            )
                        }), 404

                    # Cập nhật lịch ôn tiếp theo.
                    cursor.execute(
                        """
                        UPDATE dbo.TuVungDaLuu
                        SET
                            KhoangCachNgay = ?,
                            NgayOnTiepTheo = DATEADD(
                                DAY,
                                ?,
                                SYSUTCDATETIME()
                            )
                        WHERE MaNguoiDung = ?
                          AND MaTuVung = ?
                        """,
                        interval_days,
                        interval_days,
                        user_id,
                        word_id
                    )

                    # Ghi lịch sử thực tế.
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

                    # Đếm số từ khác nhau đã ôn.
                    cursor.execute(
                        """
                        SELECT COUNT(DISTINCT MaTuVung)
                        FROM dbo.LichSuOnTap
                        WHERE MaNguoiDung = ?
                        """,
                        user_id
                    )

                    reviewed_count = int(
                        cursor.fetchone()[0] or 0
                    )

                conn.commit()

            except Exception:
                conn.rollback()
                raise

        return jsonify({
            "success": True,
            "message": "Đã lưu kết quả ôn tập.",
            "word_id": word_id,
            "grade": grade,
            "interval_days": interval_days,
            "reviewed_count": reviewed_count
        })

    except Exception as error:
        return database_error(error)


# ============================================================
# 8. THỐNG KÊ ÔN TẬP CÁ NHÂN
#
# GET /vocabulary-review/api/stats
# ============================================================

@vocabulary_review_bp.get("/api/stats")
def get_review_stats():

    user_id = get_student_id()

    try:
        with closing(get_connection()) as conn:
            with closing(conn.cursor()) as cursor:

                cursor.execute(
                    """
                    SELECT
                        (
                            SELECT COUNT(*)
                            FROM dbo.TuVungDaLuu
                            WHERE MaNguoiDung = ?
                        ) AS savedCount,

                        (
                            SELECT COUNT(DISTINCT MaTuVung)
                            FROM dbo.LichSuOnTap
                            WHERE MaNguoiDung = ?
                        ) AS reviewedCount,

                        (
                            SELECT COUNT(*)
                            FROM dbo.TuVungDaLuu
                            WHERE MaNguoiDung = ?
                              AND (
                                  NgayOnTiepTheo IS NULL
                                  OR NgayOnTiepTheo
                                     <= SYSUTCDATETIME()
                              )
                        ) AS dueCount,

                        (
                            SELECT COUNT(*)
                            FROM dbo.LichSuOnTap
                            WHERE MaNguoiDung = ?
                        ) AS totalReviews
                    """,
                    user_id,
                    user_id,
                    user_id,
                    user_id
                )

                row = cursor.fetchone()

        return jsonify({
            "success": True,
            "saved_count": int(row[0] or 0),
            "reviewed_count": int(row[1] or 0),
            "due_count": int(row[2] or 0),
            "total_reviews": int(row[3] or 0)
        })

    except Exception as error:
        return database_error(error)
