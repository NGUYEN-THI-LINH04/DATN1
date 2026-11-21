
import argparse
import html
import json
import re
import sys

from contextlib import closing
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from pypinyin import lazy_pinyin, Style
from youtube_transcript_api import YouTubeTranscriptApi


# =====================================================
# CẤU HÌNH
# =====================================================

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

SCRIPT_DIR = Path(__file__).resolve().parent
BACKUP_DIR = SCRIPT_DIR / "backups"

YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
HANZI_RE = re.compile(r"[\u3400-\u9fff]")


# =====================================================
# 1. LẤY THÔNG TIN VIDEO TỪ SQL SERVER
# =====================================================

def get_video(cursor, content_id):
    cursor.execute(
        """
        SELECT MaNoiDung, TieuDe, NoiDung
        FROM dbo.NoiDungBaiHoc
        WHERE MaNoiDung = ?
          AND LoaiNoiDung = 'nghe'
        """,
        content_id
    )

    row = cursor.fetchone()

    if not row:
        raise ValueError(
            f"Không tìm thấy MaNoiDung={content_id}"
        )

    data = json.loads(row[2])

    if not isinstance(data, dict):
        raise ValueError("Dữ liệu JSON không hợp lệ.")

    if data.get("module") != "shadowing":
        raise ValueError("Nội dung không thuộc Shadowing.")

    youtube_id = data.get("youtube_id", "")

    if (
        not isinstance(youtube_id, str)
        or not YOUTUBE_ID_RE.fullmatch(youtube_id)
    ):
        raise ValueError("Mã YouTube không hợp lệ.")

    return {
        "id": row[0],
        "title": row[1],
        "youtube_id": youtube_id,
        "data": data,
        "raw_json": row[2]
    }


# =====================================================
# 2. THỬ LẤY PHỤ ĐỀ TIẾNG TRUNG TỪ YOUTUBE
# =====================================================

def fetch_youtube_subtitles(youtube_id):
    api = YouTubeTranscriptApi()

    tracks = list(api.list(youtube_id))

    chinese_tracks = [
        track
        for track in tracks
        if track.language_code.lower().startswith("zh")
    ]

    chinese_tracks.sort(
        key=lambda track: track.is_generated
    )

    if not chinese_tracks:
        raise ValueError(
            "Không tìm thấy phụ đề tiếng Trung "
            "có thể truy xuất."
        )

    track = chinese_tracks[0]

    print("Ngôn ngữ:", track.language_code)
    print(
        "Nguồn:",
        "Phụ đề tự động"
        if track.is_generated
        else "Phụ đề thủ công"
    )

    return track.fetch()


# =====================================================
# 3. ĐỌC FILE PHỤ ĐỀ SRT / VTT
# =====================================================

def read_subtitle_file(file_path):
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy file: {path}"
        )

    if path.suffix.lower() not in (".srt", ".vtt"):
        raise ValueError(
            "Chỉ hỗ trợ file .srt hoặc .vtt"
        )

    content = path.read_text(encoding="utf-8-sig")
    content = content.replace("\r\n", "\n")
    content = content.replace("\r", "\n")

    blocks = re.split(r"\n\s*\n", content)

    def to_seconds(value):
        value = value.strip().replace(",", ".")
        parts = value.split(":")

        if len(parts) == 3:
            hours, minutes, seconds = parts
            return (
                int(hours) * 3600
                + int(minutes) * 60
                + float(seconds)
            )

        if len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + float(seconds)

        raise ValueError(
            f"Mốc thời gian không hợp lệ: {value}"
        )

    result = []

    for block in blocks:
        lines = [
            line.strip()
            for line in block.splitlines()
        ]

        timing_index = next(
            (
                index
                for index, line in enumerate(lines)
                if "-->" in line
            ),
            None
        )

        if timing_index is None:
            continue

        timing = lines[timing_index]

        try:
            start_part, end_part = timing.split(
                "-->", 1
            )

            start = to_seconds(start_part)
            end = to_seconds(
                end_part.strip().split()[0]
            )

        except (ValueError, IndexError):
            continue

        if start < 0 or end <= start:
            continue

        text = " ".join(
            lines[timing_index + 1:]
        ).strip()

        if not text:
            continue

        result.append(
            SimpleNamespace(
                start=start,
                duration=end - start,
                text=text
            )
        )

    if not result:
        raise ValueError(
            "Không đọc được câu phụ đề nào."
        )

    return result


# =====================================================
# 4. CHUYỂN CHỮ HÁN SANG PINYIN
# =====================================================

def make_pinyin(text):
    result = lazy_pinyin(
        text,
        style=Style.TONE,
        errors="default"
    )

    pinyin = " ".join(result)

    pinyin = re.sub(
        r"\s+([，。！？；：,.!?])",
        r"\1",
        pinyin
    )

    return pinyin.strip()


# =====================================================
# 5. XỬ LÝ CÂU VÀ THỜI GIAN
# =====================================================

def prepare_sentences(transcript, limit):
    sentences = []

    last_text = None

    for item in transcript:
        text = html.unescape(
            re.sub(r"<[^>]+>", "", item.text)
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        # Chỉ lấy câu có chữ Hán.
        if not text or not HANZI_RE.search(text):
            continue

        # Bỏ đoạn trùng liên tiếp.
        if text == last_text:
            continue

        start = float(item.start)
        end = start + float(item.duration)

        if start < 0 or end <= start:
            continue

        sentences.append({
            "start": round(start, 2),
            "end": round(end, 2),
            "hanzi": text,
            "pinyin": make_pinyin(text),
            "vi": ""
        })

        last_text = text

        if len(sentences) >= limit:
            break

    return sentences


# =====================================================
# 6. DỊCH TIẾNG VIỆT
# =====================================================

def translate_sentences(sentences):
    from deep_translator import GoogleTranslator

    translator = GoogleTranslator(
        source="zh-CN",
        target="vi"
    )

    for index, sentence in enumerate(
        sentences, start=1
    ):
        try:
            result = translator.translate(
                sentence["hanzi"]
            )

            sentence["vi"] = result or ""

        except Exception as exc:
            print(
                f"Lỗi dịch câu {index}: {exc}"
            )

        print(
            f"Đã dịch {index}/{len(sentences)} câu"
        )


# =====================================================
# 7. SAO LƯU DỮ LIỆU SQL CŨ
# =====================================================

def backup_data(video):
    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    path = BACKUP_DIR / (
        f"shadowing_{video['id']}_{timestamp}.json"
    )

    path.write_text(
        video["raw_json"],
        encoding="utf-8"
    )

    print("Đã sao lưu:", path)


# =====================================================
# 8. CHƯƠNG TRÌNH CHÍNH
# =====================================================

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Cập nhật phụ đề Shadowing "
            "vào SQL Server"
        )
    )

    parser.add_argument(
        "--id",
        type=int,
        required=True,
        help="MaNoiDung của video"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=12,
        help="Số câu muốn lấy thử"
    )

    parser.add_argument(
        "--subtitle-file",
        type=str,
        help="File SRT/VTT tiếng Trung trên máy"
    )

    parser.add_argument(
        "--translate",
        action="store_true",
        help="Dịch câu sang tiếng Việt"
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Ghi kết quả vào SQL Server"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Cho phép thay lời thoại đã có"
    )

    args = parser.parse_args()

    if not 1 <= args.limit <= 200:
        parser.error(
            "--limit phải nằm trong khoảng 1-200."
        )

    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cursor:

            video = get_video(
                cursor,
                args.id
            )

            print("\n========== VIDEO ==========")
            print("ID:", video["id"])
            print("Tiêu đề:", video["title"])
            print("YouTube:", video["youtube_id"])

            existing = video["data"].get(
                "sentences", []
            )

            if existing and not args.force:
                print(
                    "\nVideo đã có lời thoại."
                )
                print(
                    "Thêm --force nếu muốn thay."
                )
                return

            # Chọn nguồn phụ đề.
            try:
                if args.subtitle_file:
                    print(
                        "\nĐang đọc phụ đề từ file..."
                    )

                    transcript = read_subtitle_file(
                        args.subtitle_file
                    )

                else:
                    print(
                        "\nĐang thử lấy phụ đề YouTube..."
                    )

                    transcript = fetch_youtube_subtitles(
                        video["youtube_id"]
                    )

            except Exception as exc:
                print("\nKhông lấy được phụ đề.")
                print(exc)
                print(
                    "\nSQL Server chưa bị thay đổi."
                )
                print(
                    "Bạn có thể dùng --subtitle-file "
                    "với file SRT/VTT hợp lệ."
                )
                return

            sentences = prepare_sentences(
                transcript,
                args.limit
            )

            if not sentences:
                print(
                    "\nKhông tìm thấy câu chữ Hán."
                )
                print(
                    "Hãy kiểm tra ngôn ngữ phụ đề."
                )
                return

            if args.translate:
                translate_sentences(sentences)

            print(
                "\n========== XEM TRƯỚC =========="
            )

            for index, sentence in enumerate(
                sentences, start=1
            ):
                print(
                    f"\n#{index} "
                    f"{sentence['start']:.2f}s - "
                    f"{sentence['end']:.2f}s"
                )

                print(
                    "Hanzi:",
                    sentence["hanzi"]
                )

                print(
                    "Pinyin:",
                    sentence["pinyin"]
                )

                print(
                    "Tiếng Việt:",
                    sentence["vi"]
                )

            print(
                "\nTổng số câu:",
                len(sentences)
            )

            if not args.apply:
                print(
                    "\nCHẾ ĐỘ XEM TRƯỚC"
                )
                print(
                    "Chưa cập nhật SQL Server."
                )
                return

            updated_data = dict(
                video["data"]
            )

            updated_data["sentences"] = sentences

            updated_json = json.dumps(
                updated_data,
                ensure_ascii=False
            )

            backup_data(video)

            try:
                cursor.execute(
                    """
                    UPDATE dbo.NoiDungBaiHoc
                    SET NoiDung = ?
                    WHERE MaNoiDung = ?
                      AND NoiDung = ?
                    """,
                    updated_json,
                    video["id"],
                    video["raw_json"]
                )

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "Dữ liệu SQL đã thay đổi. "
                        "Hủy cập nhật."
                    )

                conn.commit()

            except Exception:
                conn.rollback()
                raise

            print(
                "\n========== THÀNH CÔNG =========="
            )

            print(
                f"Đã cập nhật {len(sentences)} câu "
                f"cho video ID {video['id']}."
            )


if __name__ == "__main__":
    main()
