
import argparse
import json
import sys

from pathlib import Path
from datetime import datetime
from contextlib import closing

import pyodbc


# =====================================================
# 1. CẤU HÌNH DỰ ÁN
# =====================================================

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection


SCRIPT_DIR = Path(__file__).resolve().parent

JSON_FILE = (
    SCRIPT_DIR
    / "previews"
    / "emily_shadowing_cau_chuyen.json"
)

BACKUP_DIR = SCRIPT_DIR / "backups"

CONTENT_ID = 3
YOUTUBE_ID = "3G9eT9c2bP8"

EXPECTED_SENTENCES = 44
VIDEO_DURATION = 384.0


# =====================================================
# 2. ĐỌC VÀ KIỂM TRA FILE JSON
# =====================================================

def load_shadowing_json():

    if not JSON_FILE.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file JSON: {JSON_FILE}"
        )

    data = json.loads(
        JSON_FILE.read_text(encoding="utf-8-sig")
    )

    if data.get("youtube_id") != YOUTUBE_ID:
        raise ValueError(
            "YouTube ID trong JSON không khớp video Emily."
        )

    duration = float(data.get("duration_seconds", 0))

    if duration <= 0 or duration > VIDEO_DURATION + 1:
        raise ValueError(
            "Thời lượng video trong JSON không hợp lệ."
        )

    sentences = data.get("sentences")

    if not isinstance(sentences, list):
        raise ValueError(
            "Trường sentences phải là danh sách."
        )

    if len(sentences) != EXPECTED_SENTENCES:
        raise ValueError(
            f"Cần {EXPECTED_SENTENCES} câu, "
            f"nhưng nhận được {len(sentences)} câu."
        )

    previous_end = -1

    for index, sentence in enumerate(sentences, 1):

        for field in (
            "start",
            "end",
            "hanzi",
            "pinyin",
            "vi"
        ):
            if field not in sentence:
                raise ValueError(
                    f"Câu {index} thiếu trường {field}."
                )

        for field in ("hanzi", "pinyin", "vi"):
            if not isinstance(sentence[field], str):
                raise ValueError(
                    f"Câu {index}: {field} phải là chuỗi."
                )

            if not sentence[field].strip():
                raise ValueError(
                    f"Câu {index}: {field} đang trống."
                )

        start = float(sentence["start"])
        end = float(sentence["end"])

        if start < 0 or end <= start:
            raise ValueError(
                f"Câu {index} có timestamp không hợp lệ."
            )

        if start < previous_end - 0.001:
            raise ValueError(
                f"Câu {index} bị chồng thời gian."
            )

        if end > duration + 0.5:
            raise ValueError(
                f"Câu {index} vượt thời lượng video."
            )

        previous_end = end

    # Kiểm tra đúng đoạn bắt đầu và kết thúc câu chuyện.
    if abs(float(sentences[0]["start"]) - 18.9) > 0.1:
        raise ValueError(
            "Câu đầu không đúng vị trí câu chuyện Emily."
        )

    if abs(float(sentences[-1]["end"]) - 245.366) > 0.1:
        raise ValueError(
            "Câu cuối không đúng vị trí kết thúc câu chuyện."
        )

    return sentences


# =====================================================
# 3. SAO LƯU JSON GỐC TRONG SQL SERVER
# =====================================================

def backup_original_json(original_json):

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    backup_path = BACKUP_DIR / (
        f"emily_before_import_{timestamp}.json"
    )

    backup_path.write_text(
        original_json,
        encoding="utf-8"
    )

    return backup_path


# =====================================================
# 4. CHUYỂN JSON SANG DỮ LIỆU UNICODE
# =====================================================

def encode_sql_unicode(text):

    # SQL Server lưu NVARCHAR bằng UTF-16LE.
    # Truyền dưới dạng VARBINARY để tránh lỗi
    # pyodbc tự suy luận tham số thành TEXT/NTEXT.

    return pyodbc.Binary(
        text.encode("utf-16le")
    )


# =====================================================
# 5. NHẬP PHỤ ĐỀ VÀO SQL SERVER
# =====================================================

def import_emily(apply=False):

    print("\n====================================")
    print("NHAP PHU DE SHADOWING - EMILY")
    print("====================================")

    sentences = load_shadowing_json()

    print("YouTube ID:", YOUTUBE_ID)
    print("MaNoiDung:", CONTENT_ID)
    print("So cau:", len(sentences))

    print("\n===== 5 CAU DAU =====")

    for sentence in sentences[:5]:
        print(
            f"{sentence['start']:.3f}s | "
            f"{sentence['hanzi']} | "
            f"{sentence['vi']}"
        )

    with closing(get_connection()) as conn:

        # Đảm bảo chỉ ghi khi commit thành công.
        conn.autocommit = False

        with closing(conn.cursor()) as cursor:

            try:

                # =================================================
                # ĐỌC BẢN GHI SQL
                # =================================================

                # Khi ghi, khóa bản ghi cho tới commit/rollback
                # để tránh thay đổi đồng thời.

                lock_hint = (
                    "WITH (UPDLOCK, HOLDLOCK)"
                    if apply
                    else ""
                )

                cursor.execute(
                    f"""
                    SELECT
                        MaNoiDung,
                        TieuDe,
                        NoiDung
                    FROM dbo.NoiDungBaiHoc
                    {lock_hint}
                    WHERE MaNoiDung = ?
                      AND LoaiNoiDung = 'nghe'
                    """,
                    CONTENT_ID
                )

                row = cursor.fetchone()

                if row is None:
                    raise ValueError(
                        "Không tìm thấy bài Emily trong SQL."
                    )

                original_json = row[2]

                original_data = json.loads(
                    original_json
                )

                if not isinstance(original_data, dict):
                    raise ValueError(
                        "JSON hiện tại trong SQL không hợp lệ."
                    )

                if original_data.get("module") != "shadowing":
                    raise ValueError(
                        "Bản ghi không thuộc Shadowing."
                    )

                if original_data.get("youtube_id") != YOUTUBE_ID:
                    raise ValueError(
                        "YouTube ID trong SQL không khớp."
                    )

                # Không ghi đè nếu đã có câu Shadowing.
                if original_data.get("sentences"):
                    raise ValueError(
                        "Video Emily đã có phụ đề trong SQL. "
                        "Dừng để tránh ghi đè."
                    )

                print("\n===== DU LIEU SQL HIEN TAI =====")
                print("Tieu de:", row[1])
                print("Module:", original_data["module"])
                print("YouTube ID:", original_data["youtube_id"])
                print(
                    "So cau cu:",
                    len(original_data.get("sentences") or [])
                )

                # =================================================
                # GHÉP 44 CÂU VÀO JSON HIỆN TẠI
                # =================================================

                # Giữ lại các trường sẵn có.
                updated_data = dict(original_data)

                updated_data["sentences"] = sentences

                updated_data["subtitle_source"] = {
                    "type": "timed_transcript",
                    "youtube_id": YOUTUBE_ID,
                    "sentence_count": len(sentences)
                }

                updated_json = json.dumps(
                    updated_data,
                    ensure_ascii=False
                )

                if not apply:

                    print("\n====================================")
                    print("KIEM TRA THANH CONG")
                    print("CHUA THAY DOI SQL SERVER")
                    print("====================================")

                    conn.rollback()
                    return

                # =================================================
                # SAO LƯU TRƯỚC KHI GHI
                # =================================================

                backup_path = backup_original_json(
                    original_json
                )

                print("\nDa sao luu:", backup_path)

                # =================================================
                # UPDATE SQL - XỬ LÝ LỖI 4189
                # =================================================

                # Không so sánh tham số JSON dài trong WHERE.
                # Bản ghi đang được khóa và đã kiểm tra
                # module, youtube_id, danh sách câu ở trên.
                #
                # Đưa UTF-16LE qua tham số VARBINARY,
                # SQL Server tự chuyển thành NVARCHAR(MAX).

                unicode_payload = encode_sql_unicode(
                    updated_json
                )

                cursor.execute(
                    """
                    UPDATE dbo.NoiDungBaiHoc
                    SET NoiDung = CONVERT(
                        NVARCHAR(MAX),
                        CAST(? AS VARBINARY(MAX))
                    )
                    WHERE MaNoiDung = ?
                      AND LoaiNoiDung = 'nghe'
                    """,
                    unicode_payload,
                    CONTENT_ID
                )

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "UPDATE không cập nhật đúng 1 bản ghi."
                    )

                # =================================================
                # ĐỌC LẠI ĐỂ XÁC NHẬN TRƯỚC COMMIT
                # =================================================

                cursor.execute(
                    """
                    SELECT NoiDung
                    FROM dbo.NoiDungBaiHoc
                    WHERE MaNoiDung = ?
                    """,
                    CONTENT_ID
                )

                verify_row = cursor.fetchone()

                if verify_row is None:
                    raise RuntimeError(
                        "Không đọc được dữ liệu sau UPDATE."
                    )

                saved_data = json.loads(verify_row[0])

                saved_sentences = saved_data.get(
                    "sentences", []
                )

                if (
                    saved_data.get("youtube_id") != YOUTUBE_ID
                    or len(saved_sentences) != EXPECTED_SENTENCES
                    or saved_sentences != sentences
                ):
                    raise RuntimeError(
                        "Dữ liệu sau UPDATE không khớp. "
                        "Hủy cập nhật."
                    )

                # =================================================
                # COMMIT
                # =================================================

                conn.commit()

                print("\n====================================")
                print("CAP NHAT SQL THANH CONG!")
                print("====================================")
                print("MaNoiDung:", CONTENT_ID)
                print("YouTube:", YOUTUBE_ID)
                print("So cau Shadowing:", len(saved_sentences))
                print("File sao luu:", backup_path)

                print("\nCau dau:")
                print(saved_sentences[0]["hanzi"])
                print(saved_sentences[0]["pinyin"])
                print(saved_sentences[0]["vi"])

            except Exception:
                conn.rollback()
                raise


# =====================================================
# 6. CHƯƠNG TRÌNH CHÍNH
# =====================================================

def main():

    parser = argparse.ArgumentParser(
        description="Nhap phu de video Emily vao Shadowing"
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Xac nhan ghi du lieu vao SQL Server"
    )

    args = parser.parse_args()

    import_emily(apply=args.apply)


if __name__ == "__main__":
    main()
