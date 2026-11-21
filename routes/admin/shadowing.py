
import json
import re

from contextlib import closing
from urllib.parse import urlparse, parse_qs

from flask import (
    Blueprint,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from database import get_connection


# =========================================================
# BLUEPRINT - ADMIN SHADOWING
# =========================================================

admin_shadowing_bp = Blueprint(
    "admin_shadowing",
    __name__,
    url_prefix="/admin/shadowing",
)


# =========================================================
# KIEM TRA QUYEN ADMIN
# =========================================================

@admin_shadowing_bp.before_request
def require_admin():

    account = getattr(g, "account", None)

    if account is None:
        return redirect(
            url_for("auth.admin_login")
        )

    if account["role"] != "admin":
        abort(
            403,
            description=(
                "Bạn không có quyền quản lý Shadowing."
            ),
        )


# =========================================================
# LAY YOUTUBE ID TU LINK
# =========================================================

def get_youtube_id(value):

    if not isinstance(value, str):
        return None

    value = value.strip()

    # Cho phep nhap truc tiep YouTube ID.
    if re.fullmatch(
        r"[A-Za-z0-9_-]{11}",
        value
    ):
        return value

    if not value:
        return None

    parsed = urlparse(value)

    if parsed.scheme not in ("http", "https"):
        return None

    hostname = (parsed.hostname or "").lower()

    video_id = None

    if hostname in (
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
    ):

        path = parsed.path.strip("/")

        if path == "watch":

            video_id = parse_qs(
                parsed.query
            ).get("v", [None])[0]

        else:

            parts = path.split("/")

            if (
                len(parts) == 2
                and parts[0] in (
                    "shorts",
                    "embed",
                    "live",
                )
            ):
                video_id = parts[1]

    elif hostname in (
        "youtu.be",
        "www.youtu.be",
    ):

        video_id = (
            parsed.path.strip("/").split("/")[0]
        )

    elif hostname in (
        "youtube-nocookie.com",
        "www.youtube-nocookie.com",
    ):

        parts = parsed.path.strip("/").split("/")

        if len(parts) == 2 and parts[0] == "embed":
            video_id = parts[1]

    if video_id and re.fullmatch(
        r"[A-Za-z0-9_-]{11}",
        video_id
    ):
        return video_id

    return None


# =========================================================
# DOC JSON SHADOWING
# =========================================================

def parse_shadowing_json(raw):

    try:
        data = json.loads(raw or "{}")

    except (ValueError, TypeError):
        return None

    if not isinstance(data, dict):
        return None

    if data.get("module") != "shadowing":
        return None

    return data


# =========================================================
# DANH SACH VIDEO SHADOWING
# URL: /admin/shadowing/
# =========================================================

@admin_shadowing_bp.get("/")
def index():

    videos = []

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    MaNoiDung,
                    MaBaiHoc,
                    TieuDe,
                    NoiDung,
                    ThuTu

                FROM dbo.NoiDungBaiHoc

                WHERE LoaiNoiDung = 'nghe'

                ORDER BY
                    MaBaiHoc,
                    ThuTu,
                    MaNoiDung
                """
            )

            for row in cursor.fetchall():

                data = parse_shadowing_json(
                    row[3]
                )

                if data is None:
                    continue

                sentences = data.get(
                    "sentences",
                    []
                )

                if not isinstance(sentences, list):
                    sentences = []

                youtube_id = data.get(
                    "youtube_id",
                    ""
                )

                if not isinstance(youtube_id, str):
                    youtube_id = ""

                videos.append({
                    "id": row[0],
                    "lesson_id": row[1],
                    "title": row[2],
                    "youtube_id": youtube_id,
                    "order": row[4],
                    "count": len(sentences),
                })

    return render_template(
        "admin/shadowing.html",
        active_page="shadowing",
        videos=videos,
    )


# =========================================================
# THEM VIDEO YOUTUBE
# URL: POST /admin/shadowing/them
#
# Chi them video va thong tin co ban.
# KHONG tu dong lay phu de.
# KHONG tu dong tao pinyin.
# KHONG tu dong dich tieng Viet.
# =========================================================


@admin_shadowing_bp.post("/them")
def add_video():

    # 1. Lấy dữ liệu từ form
    lesson_id = request.form.get("lesson_id", type=int)
    title = request.form.get("title", "").strip()
    youtube_url = request.form.get("youtube_url", "").strip()
    youtube_id = get_youtube_id(youtube_url)

    # 2. Kiểm tra dữ liệu
    if lesson_id is None or lesson_id <= 0:
        flash("Vui lòng chọn mã bài học hợp lệ.", "error")
        return redirect(url_for("admin_shadowing.index"))

    if not title or len(title) > 200:
        flash("Tiêu đề video cần từ 1 đến 200 ký tự.", "error")
        return redirect(url_for("admin_shadowing.index"))

    if youtube_id is None:
        flash("Link YouTube không hợp lệ.", "error")
        return redirect(url_for("admin_shadowing.index"))

    # 3. Tạo JSON ban đầu
    # Video mới chưa có lời thoại.
    # Python sẽ xử lý và cập nhật sau.
    video_data = {
        "module": "shadowing",
        "youtube_id": youtube_id,
        "sentences": [],
    }

    json_content = json.dumps(
        video_data,
        ensure_ascii=False,
    )

    # 4. Kiểm tra và thêm vào SQL Server
    with closing(get_connection()) as connection:
        connection.autocommit = False

        try:
            with closing(connection.cursor()) as cursor:

                # Kiểm tra bài học có tồn tại
                cursor.execute(
                    """
                    SELECT MaBaiHoc
                    FROM dbo.BaiHoc
                    WHERE MaBaiHoc = ?
                    """,
                    lesson_id,
                )

                if cursor.fetchone() is None:
                    raise ValueError(
                        "Bài học không tồn tại trong SQL Server."
                    )

                # Kiểm tra video đã tồn tại trong bài học
                cursor.execute(
                    """
                    SELECT MaNoiDung, NoiDung
                    FROM dbo.NoiDungBaiHoc
                         WITH (UPDLOCK, HOLDLOCK)
                    WHERE MaBaiHoc = ?
                      AND LoaiNoiDung = 'nghe'
                    """,
                    lesson_id,
                )

                for row in cursor.fetchall():
                    existing = parse_shadowing_json(row[1])

                    if existing is None:
                        continue

                    if existing.get("youtube_id") == youtube_id:
                        raise ValueError(
                            "Video YouTube này đã có trong bài học."
                        )

                # Tự tính thứ tự video tiếp theo
                cursor.execute(
                    """
                    SELECT ISNULL(MAX(ThuTu), 0) + 1
                    FROM dbo.NoiDungBaiHoc
                         WITH (UPDLOCK, HOLDLOCK)
                    WHERE MaBaiHoc = ?
                    """,
                    lesson_id,
                )

                next_order = int(cursor.fetchone()[0])

                # Thêm video mới
                cursor.execute(
                    """
                    INSERT INTO dbo.NoiDungBaiHoc
                    (
                        MaBaiHoc,
                        LoaiNoiDung,
                        TieuDe,
                        NoiDung,
                        MaTep,
                        MaNguon,
                        ThuTu
                    )
                    OUTPUT INSERTED.MaNoiDung
                    VALUES
                    (
                        ?,
                        'nghe',
                        ?,
                        ?,
                        NULL,
                        NULL,
                        ?
                    )
                    """,
                    lesson_id,
                    title,
                    json_content,
                    next_order,
                )

                inserted = cursor.fetchone()

                if inserted is None:
                    raise RuntimeError(
                        "Không lấy được mã nội dung vừa thêm."
                    )

                new_video_id = int(inserted[0])

            # 5. Lưu thay đổi
            connection.commit()

        except ValueError as error:
            connection.rollback()
            flash(str(error), "error")
            return redirect(url_for("admin_shadowing.index"))

        except Exception:
            connection.rollback()
            raise

    # 6. Thông báo thành công
    flash(
        (
            f"Đã thêm video “{title}” "
            f"(Mã nội dung: {new_video_id}). "
            "Bạn có thể xử lý lời thoại bằng Python sau."
        ),
        "success",
    )

    return redirect(url_for("admin_shadowing.index"))

# =========================================================
# SUA VIDEO SHADOWING
# POST /admin/shadowing/sua/<video_id>
# =========================================================

@admin_shadowing_bp.post("/sua/<int:video_id>")
def edit_video(video_id):

    lesson_id = request.form.get("lesson_id", type=int)
    title = request.form.get("title", "").strip()
    youtube_url = request.form.get("youtube_url", "").strip()
    youtube_id = get_youtube_id(youtube_url)

    def back(message, category="error"):
        flash(message, category)
        return redirect(url_for("admin_shadowing.index"))

    if not lesson_id or lesson_id <= 0:
        return back("Mã bài học không hợp lệ.")

    if not title or len(title) > 200:
        return back("Tiêu đề phải có từ 1 đến 200 ký tự.")

    if not youtube_id:
        return back("Link YouTube không hợp lệ.")

    with closing(get_connection()) as connection:
        connection.autocommit = False

        try:
            with closing(connection.cursor()) as cursor:

                # Khóa bản ghi để tránh cập nhật đồng thời.
                cursor.execute(
                    """
                    SELECT MaBaiHoc, NoiDung
                    FROM dbo.NoiDungBaiHoc
                         WITH (UPDLOCK, HOLDLOCK)
                    WHERE MaNoiDung = ?
                      AND LoaiNoiDung = 'nghe'
                    """,
                    video_id,
                )

                row = cursor.fetchone()

                if row is None:
                    raise ValueError("Không tìm thấy video.")

                old_lesson_id = int(row[0])
                data = parse_shadowing_json(row[1])

                if data is None:
                    raise ValueError(
                        "Bản ghi này không phải video Shadowing."
                    )

                old_youtube_id = data.get("youtube_id")
                sentences = data.get("sentences", [])

                if not isinstance(sentences, list):
                    raise ValueError(
                        "Dữ liệu câu thoại không hợp lệ."
                    )

                # Video đã có phụ đề: không được thay ID
                # vì lời thoại vẫn gắn với video cũ.
                if sentences and youtube_id != old_youtube_id:
                    raise ValueError(
                        "Video đã có lời thoại nên không thể "
                        "đổi link YouTube trực tiếp. "
                        "Hãy thêm video mới và xử lý lại phụ đề."
                    )

                # Kiểm tra bài học đích.
                cursor.execute(
                    """
                    SELECT MaBaiHoc
                    FROM dbo.BaiHoc
                    WHERE MaBaiHoc = ?
                    """,
                    lesson_id,
                )

                if cursor.fetchone() is None:
                    raise ValueError(
                        "Mã bài học mới không tồn tại."
                    )

                # Không cho trùng YouTube ID trong bài học.
                cursor.execute(
                    """
                    SELECT MaNoiDung, NoiDung
                    FROM dbo.NoiDungBaiHoc
                         WITH (UPDLOCK, HOLDLOCK)
                    WHERE MaBaiHoc = ?
                      AND LoaiNoiDung = 'nghe'
                      AND MaNoiDung <> ?
                    """,
                    lesson_id,
                    video_id,
                )

                for other_id, other_raw in cursor.fetchall():

                    other = parse_shadowing_json(other_raw)

                    if (
                        other is not None
                        and other.get("youtube_id") == youtube_id
                    ):
                        raise ValueError(
                            "Video YouTube này đã tồn tại "
                            "trong bài học được chọn."
                        )

                # Chỉ thay YouTube ID khi video chưa có lời thoại.
                # Giữ nguyên tất cả trường JSON khác.
                data["youtube_id"] = youtube_id

                json_content = json.dumps(
                    data,
                    ensure_ascii=False,
                    separators=(",", ":"),
                )

                # Nếu chuyển bài học, xếp video ở cuối bài mới.
                if lesson_id != old_lesson_id:
                    cursor.execute(
                        """
                        SELECT ISNULL(MAX(ThuTu), 0) + 1
                        FROM dbo.NoiDungBaiHoc
                             WITH (UPDLOCK, HOLDLOCK)
                        WHERE MaBaiHoc = ?
                        """,
                        lesson_id,
                    )
                    new_order = int(cursor.fetchone()[0])
                else:
                    new_order = None

                # Chia JSON thành các đoạn Unicode
                # để tránh lỗi dữ liệu NVARCHAR lớn.
                chunks = [
                    json_content[i:i + 800]
                    for i in range(0, len(json_content), 800)
                ]

                expression = " + ".join(
                    "CONVERT(NVARCHAR(MAX), ?)"
                    for _ in chunks
                )

                if len(chunks) + 4 > 2100:
                    raise ValueError(
                        "Nội dung video vượt giới hạn cập nhật."
                    )

                if new_order is None:
                    sql = f"""
                        UPDATE dbo.NoiDungBaiHoc
                        SET MaBaiHoc = ?,
                            TieuDe = ?,
                            NoiDung = {expression}
                        WHERE MaNoiDung = ?
                          AND LoaiNoiDung = 'nghe'
                    """
                    params = [
                        lesson_id,
                        title,
                        *chunks,
                        video_id,
                    ]
                else:
                    sql = f"""
                        UPDATE dbo.NoiDungBaiHoc
                        SET MaBaiHoc = ?,
                            TieuDe = ?,
                            NoiDung = {expression},
                            ThuTu = ?
                        WHERE MaNoiDung = ?
                          AND LoaiNoiDung = 'nghe'
                    """
                    params = [
                        lesson_id,
                        title,
                        *chunks,
                        new_order,
                        video_id,
                    ]

                cursor.execute(sql, *params)

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "Không cập nhật được đúng một video."
                    )

                # Đọc lại để xác nhận trước COMMIT.
                cursor.execute(
                    """
                    SELECT MaBaiHoc, TieuDe, NoiDung
                    FROM dbo.NoiDungBaiHoc
                    WHERE MaNoiDung = ?
                    """,
                    video_id,
                )

                saved = cursor.fetchone()

                if (
                    saved is None
                    or int(saved[0]) != lesson_id
                    or saved[1] != title
                    or parse_shadowing_json(saved[2]) != data
                ):
                    raise RuntimeError(
                        "Dữ liệu đọc lại không khớp."
                    )

            connection.commit()

        except ValueError as error:
            connection.rollback()
            return back(str(error))

        except Exception:
            connection.rollback()
            raise

    return back(
        "Đã cập nhật thông tin video Shadowing.",
        "success",
    )


# =========================================================
# XOA VIDEO SHADOWING
# POST /admin/shadowing/xoa/<video_id>
# =========================================================

@admin_shadowing_bp.post("/xoa/<int:video_id>")
def delete_video(video_id):

    with closing(get_connection()) as connection:
        connection.autocommit = False

        try:
            with closing(connection.cursor()) as cursor:

                cursor.execute(
                    """
                    SELECT TieuDe, NoiDung
                    FROM dbo.NoiDungBaiHoc
                         WITH (UPDLOCK, HOLDLOCK)
                    WHERE MaNoiDung = ?
                      AND LoaiNoiDung = 'nghe'
                    """,
                    video_id,
                )

                row = cursor.fetchone()

                if row is None:
                    raise ValueError(
                        "Video không tồn tại hoặc đã bị xóa."
                    )

                title = row[0]
                data = parse_shadowing_json(row[1])

                if data is None:
                    raise ValueError(
                        "Không thể xóa vì bản ghi "
                        "không thuộc Shadowing."
                    )

                cursor.execute(
                    """
                    DELETE FROM dbo.NoiDungBaiHoc
                    WHERE MaNoiDung = ?
                      AND LoaiNoiDung = 'nghe'
                    """,
                    video_id,
                )

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "Không xóa được đúng một video."
                    )

            connection.commit()

        except ValueError as error:
            connection.rollback()
            flash(str(error), "error")
            return redirect(
                url_for("admin_shadowing.index")
            )

        except Exception:
            connection.rollback()
            raise

    flash(
        f"Đã xóa video “{title}” khỏi Shadowing.",
        "success",
    )

    return redirect(
        url_for("admin_shadowing.index")
    )
  