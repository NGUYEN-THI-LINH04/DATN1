
import sys
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from database import get_connection

CONTENT_ID = 1
OLD_ID = "Zrj1yyjEnrQ"
NEW_ID = "-hVHRNgDdNE"

BACKUP_DIR = (
    Path(__file__).resolve().parent / "backups"
)


def main():
    conn = get_connection()
    conn.autocommit = False

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT TieuDe, NoiDung
            FROM dbo.NoiDungBaiHoc WITH (UPDLOCK, HOLDLOCK)
            WHERE MaNoiDung = ?
              AND LoaiNoiDung = 'nghe'
        """, CONTENT_ID)

        row = cursor.fetchone()

        if row is None:
            raise ValueError("Không tìm thấy bài Tiểu Trương.")

        title, original_json = row
        data = json.loads(original_json)

        if data.get("module") != "shadowing":
            raise ValueError("Không phải bài Shadowing.")

        if data.get("youtube_id") != OLD_ID:
            raise ValueError(
                "YouTube ID hiện tại không khớp. "
                "Không tự động ghi đè."
            )

        if data.get("sentences"):
            raise ValueError(
                "Bài đã có phụ đề. "
                "Cần kiểm tra trước khi đổi video."
            )

        # Chỉ thay YouTube ID, giữ các trường khác.
        data["youtube_id"] = NEW_ID

        # Xóa metadata phụ đề cũ nếu có.
        data.pop("subtitle_source", None)

        updated_json = json.dumps(
            data,
            ensure_ascii=False
        )

        # Sao lưu trước khi cập nhật.
        BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        backup_file = BACKUP_DIR / (
            "xiaozhang_before_video_change_"
            + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            + ".json"
        )

        backup_file.write_text(
            original_json,
            encoding="utf-8"
        )

        # Truyền UTF-16LE qua VARBINARY để tránh lỗi 4189.
        unicode_payload = updated_json.encode("utf-16le")

        cursor.execute("""
            UPDATE dbo.NoiDungBaiHoc
            SET NoiDung = CONVERT(
                NVARCHAR(MAX),
                CAST(? AS VARBINARY(MAX))
            )
            WHERE MaNoiDung = ?
              AND LoaiNoiDung = 'nghe'
        """, unicode_payload, CONTENT_ID)

        if cursor.rowcount != 1:
            raise RuntimeError("Cập nhật không thành công.")

        cursor.execute("""
            SELECT NoiDung
            FROM dbo.NoiDungBaiHoc
            WHERE MaNoiDung = ?
        """, CONTENT_ID)

        saved = json.loads(cursor.fetchone()[0])

        if saved.get("youtube_id") != NEW_ID:
            raise RuntimeError("Kiểm tra YouTube ID thất bại.")

        conn.commit()

        print("\nCAP NHAT VIDEO THANH CONG!")
        print("Bai:", title)
        print("MaNoiDung:", CONTENT_ID)
        print("YouTube cu:", OLD_ID)
        print("YouTube moi:", NEW_ID)
        print("So cau:", len(saved.get("sentences") or []))
        print("Sao luu:", backup_file)

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()
