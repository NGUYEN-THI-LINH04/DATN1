
from collections import defaultdict
from contextlib import closing
from datetime import datetime, timedelta, timezone
import math
from routes.exam_statistics import get_admin_exam_stats
from flask import (
    Blueprint,
    abort,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from database import get_connection


admin_statistics_bp = Blueprint(
    "admin_statistics",
    __name__,
    url_prefix="/admin/thong-ke",
)

VN_TZ = timezone(timedelta(hours=7))
PAGE_SIZE = 15


@admin_statistics_bp.before_request
def require_admin():
    account = getattr(g, "account", None)

    if account is None:
        return redirect(url_for("auth.admin_login"))

    if account.get("role") != "admin":
        abort(403)


def count_sql(cursor, sql, *params):
    cursor.execute(sql, *params)
    row = cursor.fetchone()
    return int(row[0] or 0) if row else 0


def format_vn_time(value):
    if value is None:
        return "—"

    # ThoiDiemLam trong Shadowing được lưu dưới dạng UTC.
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.astimezone(VN_TZ).strftime(
        "%d/%m/%Y %H:%M"
    )


def percentage(part, total):
    return round(part * 100 / total, 1) if total else 0


@admin_statistics_bp.get("/")
def index():

    # ==========================================
    # 1. ĐỌC BỘ LỌC SHADOWING
    # ==========================================

    days = request.args.get("days", "30")

    if days not in ("7", "30", "90", "all"):
        days = "30"

    mode = request.args.get("mode", "all")

    if mode not in ("all", "dictation", "assemble"):
        mode = "all"

    keyword = request.args.get("q", "").strip()[:100]

    video_id = request.args.get(
        "video_id",
        default=None,
        type=int,
    )

    if video_id is not None and video_id <= 0:
        video_id = None

    page = request.args.get("page", 1, type=int) or 1
    page = max(1, page)

    today = datetime.now(VN_TZ).date()

    conditions = []
    parameters = []

    if days != "all":
        start_date = today - timedelta(
            days=int(days) - 1
        )

        start_utc = (
            datetime.combine(
                start_date,
                datetime.min.time(),
            )
            - timedelta(hours=7)
        )

        conditions.append("k.ThoiDiemLam >= ?")
        parameters.append(start_utc)

    if mode != "all":
        conditions.append("k.CheDo = ?")
        parameters.append(mode)

    if video_id is not None:
        conditions.append("k.MaNoiDung = ?")
        parameters.append(video_id)

    if keyword:
        conditions.append("""
            (
                CHARINDEX(?, u.HoTen) > 0
                OR CHARINDEX(?, u.TenDangNhap) > 0
                OR CHARINDEX(?, nd.TieuDe) > 0
            )
        """)

        parameters.extend([keyword] * 3)

    where_sql = (
        " WHERE " + " AND ".join(conditions)
        if conditions
        else ""
    )

    shadowing_from = """
        FROM dbo.KetQuaShadowing AS k
        INNER JOIN dbo.NguoiDung AS u
            ON u.MaNguoiDung = k.MaNguoiDung
        INNER JOIN dbo.NoiDungBaiHoc AS nd
            ON nd.MaNoiDung = k.MaNoiDung
    """

    # ==========================================
    # 2. LẤY DỮ LIỆU SQL SERVER
    # ==========================================

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:

            # ==================================
            # TỔNG QUAN
            # ==================================

            overview = {
                "students": count_sql(
                    cursor,
                    "SELECT COUNT(*) FROM dbo.NguoiDung",
                ),
                "courses": count_sql(
                    cursor,
                    "SELECT COUNT(*) FROM dbo.KhoaHoc",
                ),
                "lessons": count_sql(
                    cursor,
                    "SELECT COUNT(*) FROM dbo.BaiHoc",
                ),
                "exercise_submissions": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.LanLamBai
                    WHERE NgayNop IS NOT NULL
                    """,
                ),
                "shadowing_attempts": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.KetQuaShadowing
                    """,
                ),
                "saved_words": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.TuVungDaLuu
                    """,
                ),
                "conversations": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.CuocHoiThoai
                    """,
                ),
            }

            # ==================================
            # KHÓA HỌC VÀ TIẾN ĐỘ
            # ==================================

            progress = {
                "course_published": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.KhoaHoc
                    WHERE TrangThai = 'da_xuat_ban'
                    """,
                ),
                "lesson_published": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.BaiHoc
                    WHERE TrangThai = 'da_xuat_ban'
                    """,
                ),
                "completed": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.TienDoBaiHoc
                    WHERE TrangThai = 'hoan_thanh'
                    """,
                ),
                "learners": count_sql(
                    cursor,
                    """
                    SELECT COUNT(DISTINCT MaNguoiDung)
                    FROM dbo.TienDoBaiHoc
                    """,
                ),
                "levels": [],
            }

            cursor.execute("""
                SELECT kh.MaCapDo, COUNT(bh.MaBaiHoc)
                FROM dbo.KhoaHoc AS kh
                LEFT JOIN dbo.BaiHoc AS bh
                    ON bh.MaKhoaHoc = kh.MaKhoaHoc
                WHERE kh.MaCapDo BETWEEN 1 AND 4
                GROUP BY kh.MaCapDo
            """)

            lesson_levels = {
                int(row[0]): int(row[1])
                for row in cursor.fetchall()
            }

            progress["levels"] = [
                {
                    "level": level,
                    "count": lesson_levels.get(level, 0),
                }
                for level in range(1, 5)
            ]

            # ==================================
            # HỌC LIỆU
            # ==================================

            materials = {
                "vocabulary": count_sql(
                    cursor,
                    "SELECT COUNT(*) FROM dbo.TuVung",
                ),
                "vocab_approved": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.TuVung
                    WHERE DaDuyet = 1
                    """,
                ),
                "grammar": count_sql(
                    cursor,
                    "SELECT COUNT(*) FROM dbo.NguPhap",
                ),
                "grammar_published": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.NguPhap
                    WHERE TrangThai = 'da_xuat_ban'
                    """,
                ),
                "hanzi": count_sql(
                    cursor,
                    "SELECT COUNT(*) FROM dbo.ChuHan",
                ),
                "hanzi_published": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.ChuHan
                    WHERE TrangThai = 'da_xuat_ban'
                    """,
                ),
                "radicals": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.BoThu
                    WHERE TrangThai = 'da_xuat_ban'
                    """,
                ),
                "pinyin": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.BangPinyin
                    WHERE TrangThai = 'da_xuat_ban'
                    """,
                ),
                "pronunciation": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.QuyTacPhatAm
                    WHERE TrangThai = 'da_xuat_ban'
                    """,
                ),
                "reviews": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.LichSuOnTap
                    """,
                ),
                "levels": [],
            }

            # Đếm từ khác nhau theo cấp HSK,
            # thông qua bài học và khóa học.
            cursor.execute("""
                SELECT
                    kh.MaCapDo,
                    COUNT(DISTINCT tvbh.MaTuVung)
                FROM dbo.TuVungBaiHoc AS tvbh
                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc = tvbh.MaBaiHoc
                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc = bh.MaKhoaHoc
                WHERE kh.MaCapDo BETWEEN 1 AND 4
                GROUP BY kh.MaCapDo
            """)

            vocab_levels = {
                int(row[0]): int(row[1])
                for row in cursor.fetchall()
            }

            max_vocab = max(
                vocab_levels.values(),
                default=0,
            ) or 1

            materials["levels"] = [
                {
                    "level": level,
                    "count": vocab_levels.get(level, 0),
                    "percent": percentage(
                        vocab_levels.get(level, 0),
                        max_vocab,
                    ),
                }
                for level in range(1, 5)
            ]

            # ==================================
            # BÀI TẬP
            # ==================================

            cursor.execute("""
                SELECT
                    COUNT(*),
                    COUNT(DISTINCT MaNguoiDung),
                    AVG(
                        CASE
                            WHEN Diem IS NOT NULL
                                 AND DiemToiDaLucLam > 0
                            THEN
                                CAST(Diem AS FLOAT)
                                * 100
                                / DiemToiDaLucLam
                        END
                    )
                FROM dbo.LanLamBai
                WHERE NgayNop IS NOT NULL
            """)

            ex = cursor.fetchone()

            exercises = {
                "total": count_sql(
                    cursor,
                    "SELECT COUNT(*) FROM dbo.BaiTap",
                ),
                "published": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.BaiTap
                    WHERE TrangThai = 'da_xuat_ban'
                    """,
                ),
                "questions": count_sql(
                    cursor,
                    "SELECT COUNT(*) FROM dbo.CauHoi",
                ),
                "submissions": int(ex[0] or 0),
                "learners": int(ex[1] or 0),
                "average": (
                    round(float(ex[2]), 1)
                    if ex[2] is not None
                    else None
                ),
            }

            # ==================================
            # VIDEO SHADOWING
            # ==================================

            # Chỉ chọn nội dung có module shadowing.
            # CASE bảo vệ JSON_VALUE khi dữ liệu
            # NoiDung không phải JSON hợp lệ.
            cursor.execute("""
                SELECT MaNoiDung, TieuDe
                FROM dbo.NoiDungBaiHoc
                WHERE LoaiNoiDung = 'nghe'
                  AND CASE
                      WHEN ISJSON(NoiDung) = 1
                      THEN JSON_VALUE(
                          NoiDung,
                          '$.module'
                      )
                      ELSE NULL
                  END = 'shadowing'
                ORDER BY TieuDe, MaNoiDung
            """)

            videos = [
                {
                    "id": int(row[0]),
                    "title": row[1],
                }
                for row in cursor.fetchall()
            ]

            overview["shadowing_videos"] = len(videos)

            # ==================================
            # TỔNG HỢP KẾT QUẢ SHADOWING
            # ==================================

            cursor.execute(
                """
                SELECT
                    COUNT(*),
                    COUNT(DISTINCT k.MaNguoiDung),
                    COUNT(DISTINCT k.MaNoiDung),
                    AVG(CAST(k.Diem AS FLOAT)),
                    SUM(
                        CASE WHEN k.LaDapAnDung = 1
                        THEN 1 ELSE 0 END
                    ),
                    SUM(
                        CASE WHEN k.CheDo = 'dictation'
                        THEN 1 ELSE 0 END
                    ),
                    SUM(
                        CASE WHEN k.CheDo = 'assemble'
                        THEN 1 ELSE 0 END
                    )
                """
                + shadowing_from
                + where_sql,
                *parameters,
            )

            row = cursor.fetchone()

            shadowing = {
                "attempts": int(row[0] or 0),
                "students": int(row[1] or 0),
                "videos": int(row[2] or 0),
                "average": (
                    round(float(row[3]), 1)
                    if row[3] is not None
                    else None
                ),
                "correct": int(row[4] or 0),
                "dictation": int(row[5] or 0),
                "assemble": int(row[6] or 0),
            }

            mode_total = (
                shadowing["dictation"]
                + shadowing["assemble"]
            )

            shadowing["dictation_percent"] = percentage(
                shadowing["dictation"],
                mode_total,
            )

            shadowing["correct_percent"] = percentage(
                shadowing["correct"],
                shadowing["attempts"],
            )

            # ==================================
            # BIỂU ĐỒ SHADOWING 14 NGÀY
            # ==================================

            chart_start = today - timedelta(days=13)

            chart_start_utc = (
                datetime.combine(
                    chart_start,
                    datetime.min.time(),
                )
                - timedelta(hours=7)
            )

            chart_conditions = conditions + [
                "k.ThoiDiemLam >= ?"
            ]

            chart_parameters = parameters + [
                chart_start_utc
            ]

            chart_where = (
                " WHERE "
                + " AND ".join(chart_conditions)
            )

            cursor.execute(
                """
                SELECT
                    CONVERT(
                        date,
                        DATEADD(
                            HOUR,
                            7,
                            k.ThoiDiemLam
                        )
                    ),
                    k.CheDo,
                    COUNT(*)
                """
                + shadowing_from
                + chart_where
                + """
                GROUP BY
                    CONVERT(
                        date,
                        DATEADD(
                            HOUR,
                            7,
                            k.ThoiDiemLam
                        )
                    ),
                    k.CheDo
                """,
                *chart_parameters,
            )

            chart_counts = defaultdict(
                lambda: {
                    "dictation": 0,
                    "assemble": 0,
                }
            )

            for day, kind, amount in cursor.fetchall():
                if kind in ("dictation", "assemble"):
                    chart_counts[day][kind] += int(amount)

            trend = []

            for index in range(14):
                day = chart_start + timedelta(
                    days=index
                )

                dictation_count = chart_counts[day][
                    "dictation"
                ]

                assemble_count = chart_counts[day][
                    "assemble"
                ]

                trend.append({
                    "label": day.strftime("%d/%m"),
                    "dictation": dictation_count,
                    "assemble": assemble_count,
                    "total": (
                        dictation_count
                        + assemble_count
                    ),
                })

            chart_max = max(
                (item["total"] for item in trend),
                default=0,
            ) or 1

            for item in trend:
                item["d_pct"] = percentage(
                    item["dictation"],
                    chart_max,
                )
                item["a_pct"] = percentage(
                    item["assemble"],
                    chart_max,
                )

            # ==================================
            # TOP VIDEO SHADOWING
            # ==================================

            cursor.execute(
                """
                SELECT TOP (5)
                    k.MaNoiDung,
                    nd.TieuDe,
                    COUNT(*) AS SoLuot
                """
                + shadowing_from
                + where_sql
                + """
                GROUP BY
                    k.MaNoiDung,
                    nd.TieuDe
                ORDER BY
                    SoLuot DESC,
                    k.MaNoiDung DESC
                """,
                *parameters,
            )

            top_videos = [
                {
                    "id": int(row[0]),
                    "title": row[1],
                    "count": int(row[2]),
                }
                for row in cursor.fetchall()
            ]

            top_max = max(
                (
                    item["count"]
                    for item in top_videos
                ),
                default=0,
            ) or 1

            for item in top_videos:
                item["percent"] = percentage(
                    item["count"],
                    top_max,
                )

            # ==================================
            # LỊCH SỬ SHADOWING
            # ==================================

            total_pages = max(
                1,
                math.ceil(
                    shadowing["attempts"] / PAGE_SIZE
                ),
            )

            page = min(page, total_pages)

            offset = (page - 1) * PAGE_SIZE

            cursor.execute(
                """
                SELECT
                    k.MaKetQuaShadowing,
                    k.MaNguoiDung,
                    u.HoTen,
                    u.TenDangNhap,
                    nd.TieuDe,
                    k.MaNoiDung,
                    k.CheDo,
                    k.ViTriCau,
                    k.CauTraLoi,
                    k.Diem,
                    k.SoLoi,
                    k.LaDapAnDung,
                    k.SoLanNgheLai,
                    k.ThoiDiemLam
                """
                + shadowing_from
                + where_sql
                + """
                ORDER BY
                    k.ThoiDiemLam DESC,
                    k.MaKetQuaShadowing DESC
                OFFSET ? ROWS
                FETCH NEXT ? ROWS ONLY
                """,
                *(parameters + [offset, PAGE_SIZE]),
            )

            history = []

            for row in cursor.fetchall():
                history.append({
                    "id": int(row[0]),
                    "user_id": int(row[1]),
                    "student": row[2] or "Người học",
                    "username": row[3] or "",
                    "video": row[4] or "Video",
                    "video_id": int(row[5]),
                    "mode": row[6],

                    # ViTriCau lưu từ 0.
                    # Giao diện hiển thị từ Câu 1.
                    "sentence": int(row[7]) + 1,

                    "answer": row[8],
                    "score": float(row[9] or 0),
                    "errors": int(row[10] or 0),
                    "correct": bool(row[11]),
                    "replays": int(row[12] or 0),
                    "time": format_vn_time(row[13]),
                })

            # ==================================
            # CHATBOT
            # ==================================

            chatbot = {
                "sessions": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.CuocHoiThoai
                    """,
                ),
                "questions": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.TinNhan
                    WHERE VaiTro = 'nguoi_dung'
                    """,
                ),
                "replies": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.TinNhan
                    WHERE VaiTro = 'tro_ly'
                    """,
                ),
                "knowledge": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.KhoKienThuc
                    WHERE DaDuyet = 1
                    """,
                ),
                "pending": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.KhoKienThuc
                    WHERE DaDuyet = 0
                    """,
                ),
                "missing": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.TuChuaCo
                    WHERE TrangThai = 'moi'
                    """,
                ),
            }

            
            # ==================================
            # GOP Y
            # ==================================

            feedback = {
                "total": count_sql(
                    cursor,
                    "SELECT COUNT(*) FROM dbo.GopY",
                ),
                "new": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.GopY
                    WHERE TrangThai = 'moi'
                    """,
                ),
                "done": count_sql(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.GopY
                    WHERE TrangThai = 'da_xu_ly'
                    """,
                ),
            }

            # ==================================
            # THONG KE LUYEN THI HSK1-HSK4
            # ==================================

            # Phai nam TRONG khoi with cursor.
            # Tranh loi Attempt to use a closed cursor.

            exam_stats = get_admin_exam_stats(cursor)

    # ==========================================
    # 3. TRUYEN DU LIEU SANG HTML
    # ==========================================

    return render_template(
        "admin/statistics.html",
        active_page="statistics",

        overview=overview,
        progress=progress,
        materials=materials,
        exercises=exercises,
        chatbot=chatbot,
        feedback=feedback,

        shadowing=shadowing,
        videos=videos,
        trend=trend,
        top_videos=top_videos,
        history=history,

        days=days,
        mode=mode,
        keyword=keyword,
        selected_video=video_id,
        page=page,
        total_pages=total_pages,

        exam_stats=exam_stats,
    )
