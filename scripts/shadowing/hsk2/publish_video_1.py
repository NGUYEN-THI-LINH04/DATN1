
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from database import get_connection

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "data" / "processed" / "video_1_final.json"
BACKUP_DIR = BASE / "data" / "backups"

MA_BAI_HOC = 25
MA_NOI_DUNG = 2
YOUTUBE_ID = "nxAfRmACtZs"


def validate(data):
    if data.get("module") != "shadowing":
        raise ValueError("Sai module")

    if data.get("youtube_id") != YOUTUBE_ID:
        raise ValueError("Sai YouTube ID")

    sentences = data.get("sentences")

    if not isinstance(sentences, list) or len(sentences) < 200:
        raise ValueError("Danh sach cau chua day du")

    previous_end = None
    warnings = []

    for i, sentence in enumerate(sentences, 1):
        start = sentence.get("start")
        end = sentence.get("end")

        if not isinstance(start, (int, float)):
            raise ValueError(f"Cau {i}: start sai")

        if not isinstance(end, (int, float)) or end <= start:
            raise ValueError(f"Cau {i}: end sai")

        for field in ("hanzi", "pinyin", "vi"):
            if not str(sentence.get(field) or "").strip():
                raise ValueError(f"Cau {i}: thieu {field}")

        if previous_end is not None and start < previous_end - 0.01:
            raise ValueError(f"Cau {i}: thoi gian chong nhau")

        duration = end - start
        if duration < 0.5 or duration > 15:
            warnings.append(
                f"Cau {i}: thoi luong {duration:.2f}s"
            )

        previous_end = end

    if sentences[-1]["end"] > 1185:
        raise ValueError("Vuot qua thoi luong video")

    return warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Thuc su cap nhat SQL Server"
    )
    args = parser.parse_args()

    with SOURCE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    warnings = validate(data)

    content = json.dumps(data, ensure_ascii=False)

    print("=== HSK2 VIDEO 1 ===")
    print("So cau:", len(data["sentences"]))
    print("YouTube:", data["youtube_id"])
    print("MaBaiHoc:", MA_BAI_HOC)
    print("MaNoiDung:", MA_NOI_DUNG)
    print("Canh bao thoi luong:", len(warnings))

    for warning in warnings[:10]:
        print("  ", warning)

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT MaBaiHoc, LoaiNoiDung, TieuDe, NoiDung
            FROM dbo.NoiDungBaiHoc
            WHERE MaNoiDung = ?
            """,
            MA_NOI_DUNG
        )

        row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "Khong tim thay MaNoiDung=2. Khong tao ban ghi moi."
            )

        ma_bai_hoc, loai, tieu_de, old_content = row

        print("Tieu de SQL:", tieu_de)
        print("Loai noi dung:", loai)

        if ma_bai_hoc != MA_BAI_HOC or loai != "nghe":
            raise RuntimeError(
                "Ban ghi SQL khong dung bai HSK2 hoac loai nghe."
            )

        if not args.commit:
            print("\nKIEM TRA THANH CONG.")
            print("Chua cap nhat SQL Server.")
            print(
                "Neu dung bai hoc, chay lai voi --commit "
                "de cap nhat."
            )
            return

        # Sao luu noi dung cu truoc khi cap nhat
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )
        backup_path = BACKUP_DIR / (
            f"video_1_sql_before_{timestamp}.json"
        )

        backup_path.write_text(
            json.dumps(
                {
                    "MaNoiDung": MA_NOI_DUNG,
                    "MaBaiHoc": MA_BAI_HOC,
                    "LoaiNoiDung": loai,
                    "TieuDe": tieu_de,
                    "NoiDung": old_content,
                },
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print("Da sao luu SQL cu:", backup_path)

        cursor.execute(
            """
            UPDATE dbo.NoiDungBaiHoc
            SET NoiDung = ?
            WHERE MaNoiDung = ?
              AND MaBaiHoc = ?
              AND LoaiNoiDung = 'nghe'
            """,
            content,
            MA_NOI_DUNG,
            MA_BAI_HOC
        )

        if cursor.rowcount != 1:
            raise RuntimeError(
                "Cap nhat khong dung 1 ban ghi, huy giao dich."
            )

        # Doc lai de kiem tra truoc khi commit
        cursor.execute(
            """
            SELECT NoiDung
            FROM dbo.NoiDungBaiHoc
            WHERE MaNoiDung = ?
            """,
            MA_NOI_DUNG
        )

        saved = cursor.fetchone()[0]
        saved_data = json.loads(saved)

        if saved_data != data:
            raise RuntimeError(
                "Du lieu doc lai khong khop, huy giao dich."
            )

        conn.commit()

        print("\nCAP NHAT SQL SERVER THANH CONG!")
        print("Da luu:", len(saved_data["sentences"]), "cau")
        print("Khong thay doi HSK1.")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
