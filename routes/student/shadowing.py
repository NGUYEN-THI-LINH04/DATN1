
import json
import re
from contextlib import closing

from flask import Blueprint, abort, render_template, url_for
from database import get_connection


# =========================================================
# 1. BLUEPRINT SHADOWING
# =========================================================

shadowing_bp = Blueprint(
    "shadowing",
    __name__,
    url_prefix="/shadowing"
)

# Mã YouTube hợp lệ thường gồm 11 ký tự.
YOUTUBE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")


# =========================================================
# 2. HÀM XỬ LÝ DỮ LIỆU JSON
# =========================================================

def parse_shadowing_data(raw_data):
    """
    Đọc dữ liệu JSON từ cột NoiDung.

    Chỉ chấp nhận nội dung thuộc module shadowing.
    """

    try:
        data = json.loads(raw_data)
    except (ValueError, TypeError):
        return None

    if not isinstance(data, dict):
        return None

    if data.get("module") != "shadowing":
        return None

    youtube_id = data.get("youtube_id")

    if not isinstance(youtube_id, str):
        return None

    if not YOUTUBE_ID_PATTERN.fullmatch(youtube_id):
        return None

    return data


# =========================================================
# 3. HÀM XỬ LÝ DANH SÁCH CÂU
# =========================================================

def parse_sentences(data):
    """
    Lấy danh sách câu từ JSON.

    Mỗi câu có:
        start  : thời điểm bắt đầu
        end    : thời điểm kết thúc
        hanzi  : chữ Hán
        pinyin : phiên âm
        vi     : nghĩa tiếng Việt

    Bỏ qua những câu không hợp lệ.
    """

    sentences = []

    raw_sentences = data.get("sentences", [])

    if not isinstance(raw_sentences, list):
        return sentences

    for item in raw_sentences:

        if not isinstance(item, dict):
            continue

        hanzi = item.get("hanzi")
        start = item.get("start")
        end = item.get("end")

        # Kiểm tra nội dung câu.
        if not isinstance(hanzi, str):
            continue

        if not hanzi.strip():
            continue

        # Kiểm tra mốc thời gian.
        if (
            not isinstance(start, (int, float))
            or not isinstance(end, (int, float))
            or isinstance(start, bool)
            or isinstance(end, bool)
        ):
            continue

        if start < 0 or end <= start:
            continue

        pinyin = item.get("pinyin", "")
        vietnamese = item.get("vi", "")

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi.strip(),
            "pinyin": (
                pinyin if isinstance(pinyin, str) else ""
            ),
            "vi": (
                vietnamese
                if isinstance(vietnamese, str)
                else ""
            )
        })

    # Sắp xếp câu theo thời gian xuất hiện.
    sentences.sort(key=lambda item: item["start"])

    return sentences


# =========================================================
# 4. TRANG CHỦ SHADOWING
# URL: /shadowing/
# =========================================================

@shadowing_bp.get("/")
def index():

    levels = [
        {
            "level": 1,
            "title": "HSK 1",
            "description": (
                "Luyện nghe những câu giao tiếp cơ bản"
            )
        },
        {
            "level": 2,
            "title": "HSK 2",
            "description": (
                "Luyện nghe các tình huống thường ngày"
            )
        },
        {
            "level": 3,
            "title": "HSK 3",
            "description": (
                "Luyện nghe các đoạn hội thoại dài hơn"
            )
        },
        {
            "level": 4,
            "title": "HSK 4",
            "description": (
                "Luyện nghe các tình huống nâng cao"
            )
        }
    ]

    return render_template(
        "student/shadowing_home.html",
        levels=levels
    )


# =========================================================
# 5. DANH SÁCH VIDEO THEO CẤP HSK
# URL: /shadowing/hsk/1
# URL: /shadowing/hsk/2
# URL: /shadowing/hsk/3
# URL: /shadowing/hsk/4
# =========================================================

@shadowing_bp.get("/hsk/<int:level>")
def level_detail(level):

    # Chỉ hỗ trợ HSK1 đến HSK4.
    if level not in (1, 2, 3, 4):
        abort(404)

    videos = []

    # Kết nối SQL Server.
    with closing(get_connection()) as conn:

        with closing(conn.cursor()) as cursor:

            cursor.execute(
                """
                SELECT
                    nd.MaNoiDung,
                    nd.TieuDe,
                    nd.NoiDung

                FROM dbo.NoiDungBaiHoc AS nd

                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc = nd.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc = bh.MaKhoaHoc

                WHERE
                    kh.MaCapDo = ?

                    AND nd.LoaiNoiDung = 'nghe'

                    AND JSON_VALUE(
                        CASE
                            WHEN ISJSON(nd.NoiDung) = 1
                            THEN nd.NoiDung
                            ELSE N'{}'
                        END,
                        '$.module'
                    ) = N'shadowing'

                ORDER BY
                    bh.SoThuTuBai,
                    nd.ThuTu,
                    nd.MaNoiDung
                """,
                level
            )

            rows = cursor.fetchall()

            for row in rows:

                content_id = row[0]
                title = row[1]
                raw_data = row[2]

                # Chỉ lấy JSON Shadowing hợp lệ.
                data = parse_shadowing_data(raw_data)

                if data is None:
                    continue

                youtube_id = data["youtube_id"]

                description = data.get("description", "")

                if not isinstance(description, str):
                    description = ""

                # Thumbnail từ YouTube.
                thumbnail_url = (
                    "https://img.youtube.com/vi/"
                    + youtube_id
                    + "/hqdefault.jpg"
                )

                # Link trang luyện tập ngay trong Mộc Hán.
                detail_url = url_for(
                    "shadowing.video_detail",
                    content_id=content_id
                )

                videos.append({
                    "id": content_id,
                    "title": title,
                    "description": description,
                    "thumbnail": thumbnail_url,
                    "url": detail_url,
                    "modes": (
                        "shadowing,dictation,assemble"
                    )
                })

    return render_template(
        "student/shadowing_level.html",
        level=level,
        videos=videos
    )


# =========================================================
# 6. TRANG XEM VIDEO SHADOWING
# URL: /shadowing/video/<content_id>
# =========================================================

@shadowing_bp.get("/video/<int:content_id>")
def video_detail(content_id):

    # Lấy thông tin video từ SQL Server.
    with closing(get_connection()) as conn:

        with closing(conn.cursor()) as cursor:

            cursor.execute(
                """
                SELECT
                    nd.MaNoiDung,
                    nd.TieuDe,
                    nd.NoiDung,
                    kh.MaCapDo

                FROM dbo.NoiDungBaiHoc AS nd

                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc = nd.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc = bh.MaKhoaHoc

                WHERE
                    nd.MaNoiDung = ?
                    AND nd.LoaiNoiDung = 'nghe'
                """,
                content_id
            )

            row = cursor.fetchone()

    # Không tìm thấy nội dung.
    if row is None:
        abort(404)

    # Thông tin lấy từ database.
    video_id = row[0]
    video_title = row[1]
    raw_data = row[2]
    level = row[3]

    # Đọc JSON và kiểm tra module.
    data = parse_shadowing_data(raw_data)

    if data is None:
        abort(404)

    # Chỉ chấp nhận HSK1 đến HSK4.
    if level not in (1, 2, 3, 4):
        abort(404)

    youtube_id = data["youtube_id"]

    # Lấy danh sách câu đã được kiểm tra.
    sentences = parse_sentences(data)

    description = data.get("description", "")

    if not isinstance(description, str):
        description = ""

    # Chuẩn bị dữ liệu để truyền sang HTML.
    video = {
        "id": video_id,
        "title": video_title,
        "youtube_id": youtube_id,
        "description": description,
        "level": level,
        "sentences": sentences
    }

    return render_template(
        "student/shadowing_detail.html",
        video=video
    )
