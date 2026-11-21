
from pathlib import Path
import sys
import json

# ==========================================
# 1. CAU HINH VIDEO 4
# ==========================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "shadowing" / "hsk2"

SOURCE = (
    BASE / "data" / "processed"
    / "video4_ready_for_review.json"
)

VIDEO_ID = "O_kkptuQPY8"

MA_BAI_HOC = 25
THU_TU = 4

TIEU_DE = (
    "中文口语练习 - Luyện nói về đồ ăn và cảm xúc"
)

MO_TA = (
    "Hội thoại tiếng Trung về các món ăn yêu thích, "
    "ẩm thực Trung Quốc, hương vị và cảm xúc."
)

sys.path.insert(0, str(ROOT))

from database import get_connection


# ==========================================
# 2. DOC VA KIEM TRA JSON
# ==========================================

def prepare_data():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError("Sai YouTube ID!")

    original = data.get("sentences", [])

    if len(original) != 171:
        raise ValueError(
            f"Can 171 doan, hien co {len(original)}"
        )

    sentences = []

    for i, item in enumerate(original, 1):

        start = float(item["start"])
        end = float(item["end"])

        hanzi = str(item["hanzi"]).strip()
        pinyin = str(item["pinyin"]).strip()
        vi = str(item["vi"]).strip()

        if start < 0 or end <= start:
            raise ValueError(
                f"Timestamp sai o doan {i}"
            )

        if not all([hanzi, pinyin, vi]):
            raise ValueError(
                f"Thieu noi dung o doan {i}"
            )

        if sentences:
            previous_end = sentences[-1]["end"]

            if start < previous_end - 0.001:
                raise ValueError(
                    f"Timestamp chong nhau o doan {i}"
                )

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": vi
        })

    # Cau truc dang duoc Flask su dung.
    document = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "description": MO_TA,
        "sentences": sentences
    }

    return document


# ==========================================
# 3. KIEM TRA VIDEO TRONG SQL
# ==========================================

def check_existing(cursor):

    cursor.execute(
        """
        SELECT MaNoiDung, ThuTu, TieuDe, NoiDung
        FROM dbo.NoiDungBaiHoc WITH (UPDLOCK, HOLDLOCK)
        WHERE MaBaiHoc = ?
        ORDER BY ThuTu, MaNoiDung
        """,
        MA_BAI_HOC
    )

    print("\n===== VIDEO HSK2 HIEN CO =====")

    for row in cursor.fetchall():

        ma_noi_dung, order, title, raw = row

        print(
            f"MaNoiDung={ma_noi_dung} | "
            f"ThuTu={order} | {title}"
        )

        if order == THU_TU:
            raise RuntimeError(
                f"ThuTu={THU_TU} da ton tai. "
                "Khong them trung."
            )

        if isinstance(raw, str):
            try:
                existing = json.loads(raw)
            except (ValueError, TypeError):
                existing = None

            if isinstance(existing, dict):
                if existing.get("youtube_id") == VIDEO_ID:
                    raise RuntimeError(
                        "Video 4 da ton tai trong SQL! "
                        f"MaNoiDung={ma_noi_dung}"
                    )

    print("\nKhong phat hien video trung.")


# ==========================================
# 4. THEM VIDEO VA 171 DOAN
# ==========================================

def insert_video(document):

    connection = get_connection()
    connection.autocommit = False

    try:
        cursor = connection.cursor()

        check_existing(cursor)

        print("\n===== VIDEO SAP THEM =====")
        print("MaBaiHoc:", MA_BAI_HOC)
        print("ThuTu:", THU_TU)
        print("YouTube:", VIDEO_ID)
        print("TieuDe:", TIEU_DE)
        print("So doan:", len(document["sentences"]))

        confirm = input(
            "\nNhap THEM de luu vao SQL: "
        ).strip()

        if confirm != "THEM":
            connection.rollback()
            print("Da huy. SQL khong thay doi.")
            return

        json_text = json.dumps(
            document,
            ensure_ascii=False,
            separators=(",", ":")
        )

        # Chia JSON thanh cac doan nho de
        # tranh loi Unicode dai voi pyodbc.
        chunks = [
            json_text[i:i + 900]
            for i in range(0, len(json_text), 900)
        ]

        expression = " + ".join(
            "CONVERT(NVARCHAR(MAX), ?)"
            for _ in chunks
        )

        sql = f"""
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
                {expression},
                NULL,
                NULL,
                ?
            )
        """

        params = [
            MA_BAI_HOC,
            TIEU_DE,
            *chunks,
            THU_TU
        ]

        cursor.execute(sql, *params)

        inserted = cursor.fetchone()

        if inserted is None:
            raise RuntimeError(
                "Khong lay duoc MaNoiDung."
            )

        new_id = int(inserted[0])

        # ==================================
        # 5. DOC LAI TRUOC COMMIT
        # ==================================

        cursor.execute(
            """
            SELECT
                MaBaiHoc,
                LoaiNoiDung,
                TieuDe,
                NoiDung,
                ThuTu
            FROM dbo.NoiDungBaiHoc
            WHERE MaNoiDung = ?
            """,
            new_id
        )

        row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "Khong tim thay ban ghi vua them."
            )

        saved = json.loads(row[3])

        if (
            row[0] != MA_BAI_HOC
            or row[1] != "nghe"
            or row[2] != TIEU_DE
            or row[4] != THU_TU
        ):
            raise RuntimeError(
                "Thong tin video trong SQL khong khop."
            )

        if saved != document:
            raise RuntimeError(
                "JSON trong SQL khong khop file goc."
            )

        if len(saved["sentences"]) != 171:
            raise RuntimeError(
                "So doan sau khi luu khong bang 171."
            )

        connection.commit()

        print("\n===== INSERT THANH CONG =====")
        print("MaNoiDung moi:", new_id)
        print("MaBaiHoc:", MA_BAI_HOC)
        print("ThuTu:", THU_TU)
        print("YouTube:", VIDEO_ID)
        print("So doan:", len(saved["sentences"]))
        print("Doc lai SQL: OK")
        print("COMMIT: THANH CONG")

    except Exception:
        connection.rollback()
        print("\nCo loi. Da ROLLBACK.")
        raise

    finally:
        connection.close()


# ==========================================
# 6. CHUONG TRINH CHINH
# ==========================================

if __name__ == "__main__":

    print("===== SHADOWING HSK2 - VIDEO 4 =====")

    document = prepare_data()

    print("File:", SOURCE)
    print("So doan hop le:", len(document["sentences"]))

    insert_video(document)
