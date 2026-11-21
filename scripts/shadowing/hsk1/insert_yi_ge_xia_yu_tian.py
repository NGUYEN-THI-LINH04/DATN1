
import json
import argparse
from pathlib import Path

from database import get_connection


BASE_DIR = Path(__file__).resolve().parents[3]

JSON_FILE = (
    BASE_DIR
    / "scripts"
    / "shadowing"
    / "previews"
    / "yi_ge_xia_yu_tian_checked_preview.json"
)

MA_BAI_HOC = 1
TIEU_DE = "一个下雨天 - Một ngày mưa"
YOUTUBE_ID = "QwlhcsAMhT0"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Thuc su ghi du lieu vao SQL Server",
    )
    args = parser.parse_args()

    # 1. Đọc JSON đã hoàn thiện
    with JSON_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    sentences = data.get("sentences", [])

    if data.get("module") != "shadowing":
        raise ValueError("Sai module")

    if data.get("youtube_id") != YOUTUBE_ID:
        raise ValueError("Sai YouTube ID")

    if len(sentences) != 54:
        raise ValueError("So cau phai bang 54")

    for i, sentence in enumerate(sentences, start=1):
        for field in ("start", "end", "hanzi", "pinyin", "vi"):
            if field not in sentence:
                raise ValueError(
                    f"Cau {i} thieu truong {field}"
                )

            if sentence[field] == "":
                raise ValueError(
                    f"Cau {i} co truong {field} rong"
                )

        if sentence["end"] <= sentence["start"]:
            raise ValueError(
                f"Cau {i} co timestamp khong hop le"
            )

    # Giữ nguyên nội dung JSON
    json_text = json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    conn = get_connection()
    conn.autocommit = False

    try:
        cursor = conn.cursor()

        # 2. Kiểm tra bài học HSK1 tồn tại
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.BaiHoc
            WHERE MaBaiHoc = ?
              AND MaKhoaHoc = 1
            """,
            MA_BAI_HOC,
        )

        if cursor.fetchone()[0] != 1:
            raise ValueError(
                "Khong tim thay bai hoc HSK1"
            )

        # 3. Chống nhập trùng video
        cursor.execute(
            """
            SELECT MaNoiDung, TieuDe
            FROM dbo.NoiDungBaiHoc
            WHERE LoaiNoiDung = 'nghe'
              AND (
                    TieuDe = ?
                    OR NoiDung LIKE ?
                  )
            """,
            TIEU_DE,
            f'%{YOUTUBE_ID}%',
        )

        existing = cursor.fetchall()

        if existing:
            print("Video da ton tai trong SQL Server:")
            for row in existing:
                print(row)
            print("Khong them trung.")
            return

        # 4. Tự tìm thứ tự tiếp theo
        cursor.execute(
            """
            SELECT ISNULL(MAX(ThuTu), 0) + 1
            FROM dbo.NoiDungBaiHoc
            WHERE MaBaiHoc = ?
            """,
            MA_BAI_HOC,
        )

        thu_tu = cursor.fetchone()[0]

        print("===== THONG TIN BAI MOI =====")
        print("MaBaiHoc:", MA_BAI_HOC)
        print("ThuTu:", thu_tu)
        print("TieuDe:", TIEU_DE)
        print("YouTube ID:", YOUTUBE_ID)
        print("So cau:", len(sentences))

        if not args.apply:
            print("\nDRY-RUN: Chua ghi SQL Server.")
            print("Neu dung, chay lai voi --apply")
            return

        # 5. Chuyển JSON Unicode sang UTF-16LE
        # để tránh lỗi tham số NVARCHAR(MAX).
        json_bytes = json_text.encode("utf-16le")

        # 6. Thêm bản ghi mới
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
                CONVERT(
                    NVARCHAR(MAX),
                    CAST(? AS VARBINARY(MAX))
                ),
                NULL,
                NULL,
                ?
            )
            """,
            MA_BAI_HOC,
            TIEU_DE,
            json_bytes,
            thu_tu,
        )

        new_id = cursor.fetchone()[0]

        # Kết thúc OUTPUT trước khi kiểm tra.
        cursor.nextset()

        cursor.execute(
            """
            SELECT NoiDung
            FROM dbo.NoiDungBaiHoc
            WHERE MaNoiDung = ?
            """,
            new_id,
        )

        saved_json = cursor.fetchone()[0]
        saved_data = json.loads(saved_json)

        if saved_data.get("youtube_id") != YOUTUBE_ID:
            raise ValueError(
                "YouTube ID sau khi luu khong khop"
            )

        if len(saved_data.get("sentences", [])) != 54:
            raise ValueError(
                "So cau sau khi luu khong khop"
            )

        conn.commit()

        print("\n===== THEM THANH CONG =====")
        print("MaNoiDung moi:", new_id)
        print("MaBaiHoc:", MA_BAI_HOC)
        print("ThuTu:", thu_tu)
        print("So cau:", 54)
        print("Da COMMIT vao SQL Server.")

    except Exception:
        conn.rollback()
        print("Da ROLLBACK, khong luu thay doi.")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()

