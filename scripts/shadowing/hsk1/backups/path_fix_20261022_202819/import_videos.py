
import json
import re
import sys
from pathlib import Path
from contextlib import closing

# Cho phép import database.py từ thư mục D:\DATN1
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection


DATA_FILE = Path(__file__).with_name("videos.json")

YOUTUBE_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9_-]{11}$"
)


def load_videos():
    """Đọc danh sách video từ file JSON."""

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        videos = json.load(file)

    if not isinstance(videos, list):
        raise ValueError("videos.json phải là một danh sách.")

    return videos


def find_lesson(cursor, level):
    """
    Tìm bài học đầu tiên thuộc cấp HSK tương ứng.
    Không sử dụng MaBaiHoc cố định.
    """

    cursor.execute(
        """
        SELECT TOP (1)
            bh.MaBaiHoc

        FROM dbo.BaiHoc AS bh

        INNER JOIN dbo.KhoaHoc AS kh
            ON kh.MaKhoaHoc = bh.MaKhoaHoc

        WHERE kh.MaCapDo = ?

        ORDER BY
            bh.SoThuTuBai,
            bh.MaBaiHoc
        """,
        level
    )

    row = cursor.fetchone()

    return row[0] if row else None


def video_exists(cursor, youtube_id):
    """Kiểm tra video Shadowing đã có trong SQL chưa."""

    cursor.execute(
        """
        SELECT TOP (1)
            MaNoiDung

        FROM dbo.NoiDungBaiHoc

        WHERE LoaiNoiDung = 'nghe'

          AND JSON_VALUE(
              CASE
                  WHEN ISJSON(NoiDung) = 1
                  THEN NoiDung
                  ELSE N'{}'
              END,
              '$.module'
          ) = N'shadowing'

          AND JSON_VALUE(
              CASE
                  WHEN ISJSON(NoiDung) = 1
                  THEN NoiDung
                  ELSE N'{}'
              END,
              '$.youtube_id'
          ) = ?
        """,
        youtube_id
    )

    return cursor.fetchone() is not None


def get_next_order(cursor, lesson_id):
    """Tính thứ tự nội dung mới trong bài học."""

    cursor.execute(
        """
        SELECT ISNULL(MAX(ThuTu), 0) + 1
        FROM dbo.NoiDungBaiHoc
        WHERE MaBaiHoc = ?
        """,
        lesson_id
    )

    return cursor.fetchone()[0]


def import_videos():
    videos = load_videos()

    inserted = 0
    skipped = 0

    with closing(get_connection()) as conn:

        try:
            with closing(conn.cursor()) as cursor:

                for video in videos:

                    if not isinstance(video, dict):
                        skipped += 1
                        continue

                    level = video.get("level")
                    youtube_id = video.get("youtube_id")
                    title = video.get("title")

                    # Kiểm tra cấp HSK.
                    if type(level) is not int or level not in (1, 2, 3, 4):
                        print("Bỏ qua: cấp HSK không hợp lệ")
                        skipped += 1
                        continue

                    # Kiểm tra mã YouTube.
                    if (
                        not isinstance(youtube_id, str)
                        or not YOUTUBE_ID_PATTERN.fullmatch(youtube_id)
                    ):
                        print(f"Bỏ qua: thiếu hoặc sai ID YouTube - {title}")
                        skipped += 1
                        continue

                    # Kiểm tra tiêu đề.
                    if not isinstance(title, str) or not title.strip():
                        print("Bỏ qua: tiêu đề không hợp lệ")
                        skipped += 1
                        continue

                    title = title.strip()

                    if len(title) > 200:
                        print(f"Bỏ qua: tiêu đề quá dài - {title}")
                        skipped += 1
                        continue

                    # Kiểm tra trùng.
                    if video_exists(cursor, youtube_id):
                        print(f"Đã tồn tại: {title}")
                        skipped += 1
                        continue

                    # Tìm bài học tương ứng.
                    lesson_id = find_lesson(cursor, level)

                    if lesson_id is None:
                        print(f"Không tìm thấy bài học HSK{level}")
                        skipped += 1
                        continue

                    order = get_next_order(cursor, lesson_id)

                    description = video.get("description", "")
                    sentences = video.get("sentences", [])

                    if not isinstance(description, str):
                        description = ""

                    if not isinstance(sentences, list):
                        sentences = []

                    # JSON lưu trong cột NoiDung.
                    content = {
                        "module": "shadowing",
                        "youtube_id": youtube_id,
                        "description": description,
                        "sentences": sentences
                    }

                    content_json = json.dumps(
                        content,
                        ensure_ascii=False
                    )

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
                        content_json,
                        order
                    )

                    inserted += 1
                    print(f"Đã nhập HSK{level}: {title}")

            conn.commit()

        except Exception:
            conn.rollback()
            print("Có lỗi. Đã rollback giao dịch.")
            raise

    print("\n========== KẾT QUẢ ==========")
    print(f"Đã thêm: {inserted} video")
    print(f"Bỏ qua: {skipped} video")


if __name__ == "__main__":
    import_videos()
