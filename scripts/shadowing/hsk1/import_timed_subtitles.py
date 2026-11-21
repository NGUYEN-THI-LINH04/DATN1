
import argparse
import hashlib
import html
import json
import re
import sys

from contextlib import closing
from datetime import datetime
from pathlib import Path

from pypinyin import lazy_pinyin, Style


# =====================================================
# CẤU HÌNH
# =====================================================

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from database import get_connection

SCRIPT_DIR = Path(__file__).resolve().parent

MANIFEST_FILE = SCRIPT_DIR / "subtitle_manifest.json"
PREVIEW_DIR = SCRIPT_DIR / "previews"
BACKUP_DIR = SCRIPT_DIR / "backups"

HANZI_RE = re.compile(r"[\u3400-\u9fff]")
YOUTUBE_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


# =====================================================
# 1. CHUYỂN THỜI GIAN THÀNH GIÂY
# =====================================================

def time_to_seconds(value):
    value = value.strip().replace(",", ".")
    parts = value.split(":")

    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)

    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)

    raise ValueError(f"Sai định dạng thời gian: {value}")


# =====================================================
# 2. ĐỌC FILE PHỤ ĐỀ SRT / VTT
# =====================================================

def read_subtitles(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy file phụ đề: {path}"
        )

    if path.suffix.lower() not in (".srt", ".vtt"):
        raise ValueError(
            "File phụ đề phải có đuôi .srt hoặc .vtt"
        )

    content = path.read_text(encoding="utf-8-sig")
    content = content.replace("\r\n", "\n")
    content = content.replace("\r", "\n")

    blocks = re.split(r"\n\s*\n", content)
    result = []

    for block in blocks:
        lines = [
            line.strip()
            for line in block.splitlines()
        ]

        timing_index = next(
            (
                i for i, line in enumerate(lines)
                if "-->" in line
            ),
            None
        )

        if timing_index is None:
            continue

        timing = lines[timing_index]
        start_text, end_text = timing.split("-->", 1)

        # File VTT có thể chứa thêm thuộc tính.
        end_text = end_text.strip().split()[0]

        start = time_to_seconds(start_text)
        end = time_to_seconds(end_text)

        text = " ".join(lines[timing_index + 1:])

        # Loại bỏ thẻ định dạng phụ đề.
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            continue

        # Chỉ lấy những đoạn có chữ Hán.
        if not HANZI_RE.search(text):
            continue

        result.append({
            "start": round(start, 3),
            "end": round(end, 3),
            "hanzi": text
        })

    return result


# =====================================================
# 3. KIỂM TRA TIMESTAMP
# =====================================================

def validate_timestamps(sentences, duration):
    if not sentences:
        raise ValueError(
            "File không có câu tiếng Trung hợp lệ."
        )

    previous = None

    for index, sentence in enumerate(sentences, 1):
        start = sentence["start"]
        end = sentence["end"]

        if start < 0 or end <= start:
            raise ValueError(
                f"Câu {index} có thời gian không hợp lệ."
            )

        if end > duration + 0.5:
            raise ValueError(
                f"Câu {index} kết thúc ở {end}s, "
                f"vượt quá thời lượng {duration}s."
            )

        if previous is not None:
            if start < previous["start"]:
                raise ValueError(
                    f"Câu {index} không đúng thứ tự thời gian."
                )

            # Phát hiện các đoạn chồng chéo đáng kể.
            if start < previous["end"] - 0.2:
                raise ValueError(
                    f"Câu {index} chồng thời gian "
                    f"với câu trước. Cần kiểm tra SRT."
                )

        previous = sentence


# =====================================================
# 4. TẠO PINYIN
# =====================================================

def make_pinyin(text):
    parts = lazy_pinyin(
        text,
        style=Style.TONE,
        errors="default"
    )

    result = " ".join(parts)

    result = re.sub(
        r"\s+([，。！？；：,.!?])",
        r"\1",
        result
    )

    return result.strip()


# =====================================================
# 5. DỊCH TIẾNG VIỆT (TÙY CHỌN)
# =====================================================


def translate_sentences(sentences):
    import time
    from deep_translator import GoogleTranslator
    from deep_translator.exceptions import TooManyRequests

    translator = GoogleTranslator(
        source="zh-CN",
        target="vi"
    )

    total = len(sentences)

    for i, sentence in enumerate(sentences, 1):
        # Giữ nguyên bản dịch nếu đã có
        if sentence.get("vi"):
            continue

        # Thử lại tối đa 3 lần nếu bị giới hạn
        for attempt in range(3):
            try:
                translation = translator.translate(
                    sentence["hanzi"]
                )

                if not translation:
                    raise RuntimeError(
                        f"Không dịch được câu {i}"
                    )

                sentence["vi"] = translation

                print(
                    f"Đã dịch {i}/{total}: {translation}"
                )

                # Nghỉ giữa các yêu cầu dịch
                time.sleep(2)
                break

            except TooManyRequests:
                if attempt == 2:
                    raise RuntimeError(
                        "Google Translate vẫn giới hạn yêu cầu. "
                        "Hãy dừng và thử lại sau."
                    )

                wait_seconds = 30 * (attempt + 1)

                print(
                    f"Google giới hạn yêu cầu. "
                    f"Chờ {wait_seconds} giây..."
                )

                time.sleep(wait_seconds)


# =====================================================
# 6. XỬ LÝ MỘT VIDEO
# =====================================================

def prepare_video(cursor, entry, translate=False):
    content_id = entry["content_id"]
    youtube_id = entry["youtube_id"]
    duration = float(entry["duration_seconds"])

    if not YOUTUBE_RE.fullmatch(youtube_id):
        raise ValueError("YouTube ID không hợp lệ.")

    if duration <= 0:
        raise ValueError("Thời lượng video không hợp lệ.")

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

    if row is None:
        raise ValueError(
            f"Không tìm thấy MaNoiDung={content_id}"
        )

    original_json = row[2]
    data = json.loads(original_json)

    if not isinstance(data, dict):
        raise ValueError("JSON SQL không hợp lệ.")

    if data.get("module") != "shadowing":
        raise ValueError(
            "Bản ghi không thuộc module Shadowing."
        )

    if data.get("youtube_id") != youtube_id:
        raise ValueError(
            "Mã YouTube trong SQL khác mã trong manifest. "
            "Dừng để tránh ghép sai phụ đề."
        )

    path = Path(entry["subtitle_file"])

    if not path.is_absolute():
        path = SCRIPT_DIR / path

    # Tên file phải trùng mã YouTube.
    if path.stem != youtube_id:
        raise ValueError(
            "Tên file phụ đề phải trùng YouTube ID."
        )

    sentences = read_subtitles(path)

    validate_timestamps(
        sentences,
        duration
    )

    for sentence in sentences:
        sentence["pinyin"] = make_pinyin(
            sentence["hanzi"]
        )
        sentence["vi"] = ""

    if translate:
        translate_sentences(sentences)

    # Giữ nguyên các thông tin JSON hiện có.
    updated_data = dict(data)
    updated_data["sentences"] = sentences

    source_hash = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()

    updated_data["subtitle_source"] = {
        "type": "timed_file",
        "sha256": source_hash
    }

    return {
        "content_id": content_id,
        "title": row[1],
        "youtube_id": youtube_id,
        "duration": duration,
        "source": str(path),
        "original_json": original_json,
        "updated_json": json.dumps(
            updated_data,
            ensure_ascii=False
        ),
        "sentences": sentences
    }


# =====================================================
# 7. LƯU FILE XEM TRƯỚC
# =====================================================

def save_preview(video):
    PREVIEW_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    path = PREVIEW_DIR / (
        f"{video['youtube_id']}.json"
    )

    path.write_text(
        json.dumps(
            {
                "youtube_id": video["youtube_id"],
                "duration_seconds": video["duration"],
                "sentences": video["sentences"]
            },
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("File xem trước:", path)


# =====================================================
# 8. SAO LƯU DỮ LIỆU CŨ
# =====================================================

def backup_video(video):
    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    path = BACKUP_DIR / (
        f"shadowing_{video['content_id']}_{timestamp}.json"
    )

    path.write_text(
        video["original_json"],
        encoding="utf-8"
    )

    print("Đã sao lưu:", path)


# =====================================================
# 9. CHƯƠNG TRÌNH CHÍNH
# =====================================================

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--translate",
        action="store_true",
        help="Tạo bản dịch tiếng Việt"
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Ghi dữ liệu đã xử lý vào SQL"
    )

    parser.add_argument(
        "--reviewed",
        action="store_true",
        help="Xác nhận đã kiểm tra khớp video"
    )

    args = parser.parse_args()

    if args.apply and not args.reviewed:
        parser.error(
            "Trước khi --apply cần xem trước, "
            "đối chiếu với video và thêm --reviewed."
        )

    entries = json.loads(
        MANIFEST_FILE.read_text(encoding="utf-8")
    )

    if not isinstance(entries, list):
        raise ValueError(
            "subtitle_manifest.json phải là danh sách."
        )

    if not entries:
        raise ValueError("Manifest chưa có video.")

    prepared = []
    seen_ids = set()

    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cursor:
            try:
                # Kiểm tra tất cả trước khi cập nhật.
                for entry in entries:
                    if not isinstance(entry, dict):
                        raise ValueError(
                            "Dữ liệu manifest không hợp lệ."
                        )

                    content_id = entry["content_id"]

                    if content_id in seen_ids:
                        raise ValueError(
                            f"Trùng content_id={content_id}"
                        )

                    seen_ids.add(content_id)

                    video = prepare_video(
                        cursor,
                        entry,
                        args.translate
                    )

                    prepared.append(video)

                    print("\n==========================")
                    print("Video:", video["title"])
                    print("YouTube:", video["youtube_id"])
                    print("Số câu:", len(video["sentences"]))

                    # Xem một số câu đầu tiên.
                    for sentence in video["sentences"][:5]:
                        print(
                            f"{sentence['start']:.2f}s - "
                            f"{sentence['end']:.2f}s | "
                            f"{sentence['hanzi']}"
                        )

                    save_preview(video)

                if not args.apply:
                    print(
                        "\nCHỈ XEM TRƯỚC. "
                        "SQL chưa bị thay đổi."
                    )
                    return

                # Chống ghi đè bản chép đã có.
                for video in prepared:
                    current = json.loads(
                        video["original_json"]
                    )

                    if current.get("sentences"):
                        raise ValueError(
                            "Video đã có bản chép: "
                            f"{video['content_id']}. "
                            "Dừng để tránh ghi đè."
                        )

                for video in prepared:
                    backup_video(video)

                    cursor.execute(
                        """
                        UPDATE dbo.NoiDungBaiHoc
                        SET NoiDung = ?
                        WHERE MaNoiDung = ?
                          AND NoiDung = ?
                        """,
                        video["updated_json"],
                        video["content_id"],
                        video["original_json"]
                    )

                    if cursor.rowcount != 1:
                        raise RuntimeError(
                            "Dữ liệu SQL đã thay đổi. "
                            "Hủy cập nhật."
                        )

                conn.commit()

                print(
                    "\nĐÃ CẬP NHẬT THÀNH CÔNG "
                    f"{len(prepared)} VIDEO."
                )

            except Exception:
                conn.rollback()
                raise


if __name__ == "__main__":
    main()
