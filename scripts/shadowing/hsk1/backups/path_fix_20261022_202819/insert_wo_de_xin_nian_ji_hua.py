
import argparse
import json
from pathlib import Path

import pyodbc
from database import get_connection

ROOT = Path(r"D:\DATN1\scripts\shadowing\previews")
SOURCE = ROOT / "wo_de_xin_nian_ji_hua_final_preview.json"

MA_BAI_HOC = 1
THU_TU = 5
YOUTUBE_ID = "o6ilprwO6w0"
TIEU_DE = "我的新年计划 – Kế hoạch năm mới của tôi"


def load_and_validate():
    with SOURCE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("module") != "shadowing":
        raise ValueError("Module không đúng")

    if data.get("youtube_id") != YOUTUBE_ID:
        raise ValueError("YouTube ID không đúng")

    sentences = data.get("sentences", [])

    if len(sentences) != 70:
        raise ValueError(
            f"Cần đúng 70 câu, hiện có {len(sentences)}"
        )

    previous_end = 0

    for index, sentence in enumerate(sentences, start=1):
        start = sentence["start"]
        end = sentence["end"]

        if not (0 <= start < end <= 425):
            raise ValueError(
                f"Thời gian không hợp lệ tại câu {index}"
            )

        if start < previous_end:
            raise ValueError(
                f"Thời gian chồng lấn tại câu {index}"
            )

        for key in ("hanzi", "pinyin", "vi"):
            value = sentence.get(key)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Câu {index} thiếu {key}"
                )

        previous_end = end

    return data


def insert_video(apply=False):
    data = load_and_validate()

    json_text = json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":")
    )

    print("===== SHADOWING VIDEO 5 =====")
    print("Tieu de:", TIEU_DE)
    print("YouTube ID:", YOUTUBE_ID)
    print("MaBaiHoc:", MA_BAI_HOC)
    print("ThuTu:", THU_TU)
    print("So cau:", len(data["sentences"]))
    print("Thoi gian ket thuc:", data["sentences"][-1]["end"])

    conn = get_connection()
    conn.autocommit = False

    try:
        cursor = conn.cursor()

        # Kiểm tra vị trí ThuTu=5 có bị chiếm chưa.
        cursor.execute(
            """
            SELECT MaNoiDung, TieuDe
            FROM dbo.NoiDungBaiHoc
            WHERE MaBaiHoc = ? AND ThuTu = ?
            """,
            (MA_BAI_HOC, THU_TU)
        )

        existing = cursor.fetchone()

        if existing:
            raise ValueError(
                f"ThuTu={THU_TU} đã có MaNoiDung={existing[0]}, "
                f"TieuDe={existing[1]}. Không ghi đè."
            )

        # Kiểm tra YouTube ID đã được thêm trước đó chưa.
        cursor.execute(
            """
            SELECT TOP (1) MaNoiDung, MaBaiHoc, ThuTu
            FROM dbo.NoiDungBaiHoc
            WHERE LoaiNoiDung = 'nghe'
              AND NoiDung LIKE ?
            """,
            (f"%{YOUTUBE_ID}%",)
        )

        duplicate = cursor.fetchone()

        if duplicate:
            raise ValueError(
                f"Video đã tồn tại: MaNoiDung={duplicate[0]}, "
                f"MaBaiHoc={duplicate[1]}, ThuTu={duplicate[2]}"
            )

        if not apply:
            print()
            print("KET QUA: DU DIEU KIEN THEM MOI")
            print("Dang chay DRY-RUN, khong INSERT.")
            conn.rollback()
            return

        # SQL Server lưu chuỗi Unicode dạng UTF-16LE.
        # Truyền VARBINARY để tránh lỗi mã hóa tiếng Trung.
        title_bytes = pyodbc.Binary(
            TIEU_DE.encode("utf-16le")
        )
        json_bytes = pyodbc.Binary(
            json_text.encode("utf-16le")
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
                    CONVERT(NVARCHAR(200), CAST(? AS VARBINARY(MAX))),
                    CONVERT(NVARCHAR(MAX), CAST(? AS VARBINARY(MAX))),
                    NULL,
                    NULL,
                    ?
                )
            """,
            (
                MA_BAI_HOC,
                title_bytes,
                json_bytes,
                THU_TU,
            )
        )

        # Đọc lại bản ghi vừa thêm trước khi commit.
        cursor.execute(
            """
            SELECT MaNoiDung, TieuDe, NoiDung
            FROM dbo.NoiDungBaiHoc
            WHERE MaBaiHoc = ? AND ThuTu = ?
            """,
            (MA_BAI_HOC, THU_TU)
        )

        inserted = cursor.fetchone()

        if not inserted:
            raise RuntimeError("Không đọc được dữ liệu vừa INSERT")

        stored_data = json.loads(inserted[2])

        if stored_data != data:
            raise RuntimeError(
                "JSON đọc từ SQL khác với JSON nguồn"
            )

        if inserted[1] != TIEU_DE:
            raise RuntimeError(
                "Tiêu đề Unicode bị sai khi lưu"
            )

        conn.commit()

        print()
        print("===== INSERT THANH CONG =====")
        print("MaNoiDung:", inserted[0])
        print("MaBaiHoc:", MA_BAI_HOC)
        print("ThuTu:", THU_TU)
        print("So cau:", len(stored_data["sentences"]))
        print("Da xac minh JSON va Unicode sau INSERT.")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Cho phep INSERT vao SQL Server"
    )

    args = parser.parse_args()

    insert_video(apply=args.apply)
