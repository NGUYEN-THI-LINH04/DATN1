
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pyodbc

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection


MA_NOI_DUNG = 1
OLD_ID = "-hVHRNgDdNE"
NEW_ID = "Zrj1yyjEnrQ"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT TieuDe, LoaiNoiDung, NoiDung
            FROM dbo.NoiDungBaiHoc
            WHERE MaNoiDung = ?
            """,
            MA_NOI_DUNG,
        )

        row = cursor.fetchone()
        if not row:
            raise ValueError("Khong tim thay bai Tieu Truong.")

        if row.LoaiNoiDung != "nghe":
            raise ValueError("Loai noi dung khong phai 'nghe'.")

        data = json.loads(row.NoiDung)

        if data.get("module") != "shadowing":
            raise ValueError("Module khong phai shadowing.")

        if data.get("youtube_id") != OLD_ID:
            raise ValueError(
                f"YouTube ID hien tai khong dung: {data.get('youtube_id')}"
            )

        sentences = data.get("sentences", [])
        if len(sentences) != 26:
            raise ValueError(
                f"Du kien 26 cau, hien co {len(sentences)} cau."
            )

        print("===== THAY VIDEO SHADOWING =====")
        print("Bai:", row.TieuDe)
        print("Video cu:", OLD_ID)
        print("Video moi:", NEW_ID)
        print("So cau giu nguyen:", len(sentences))

        if not args.apply:
            print("\nKIEM TRA THANH CONG")
            print("CHUA CAP NHAT SQL SERVER")
            return

        # Sao luu JSON cu truoc khi sua.
        backup_dir = Path(__file__).resolve().parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"shadowing_1_before_video_change_{stamp}.json"
        backup_path.write_text(
            row.NoiDung,
            encoding="utf-8",
        )

        # Chi thay video, khong sua 26 cau.
        data["youtube_id"] = NEW_ID

        # Cap nhat cac URL neu chung ton tai trong JSON.
        for key in ("youtube_url", "video_url", "embed_url"):
            value = data.get(key)
            if isinstance(value, str):
                data[key] = value.replace(OLD_ID, NEW_ID)

        updated_json = json.dumps(
            data,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        # Ghi NVARCHAR(MAX) bang UTF-16LE.
        binary = pyodbc.Binary(updated_json.encode("utf-16le"))

        cursor.execute(
            """
            UPDATE dbo.NoiDungBaiHoc
            SET NoiDung = CONVERT(
                NVARCHAR(MAX),
                CAST(? AS VARBINARY(MAX))
            )
            WHERE MaNoiDung = ?
            """,
            binary,
            MA_NOI_DUNG,
        )

        # Doc lai de kiem tra truoc khi commit.
        cursor.execute(
            """
            SELECT NoiDung
            FROM dbo.NoiDungBaiHoc
            WHERE MaNoiDung = ?
            """,
            MA_NOI_DUNG,
        )

        saved = json.loads(cursor.fetchone()[0])

        if saved.get("youtube_id") != NEW_ID:
            raise ValueError("Xac minh YouTube ID that bai.")

        if saved.get("sentences") != sentences:
            raise ValueError("Du lieu 26 cau da bi thay doi.")

        conn.commit()

        print("\n===== CAP NHAT THANH CONG =====")
        print("YouTube ID:", saved["youtube_id"])
        print("So cau:", len(saved["sentences"]))
        print("Backup:", backup_path)

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
