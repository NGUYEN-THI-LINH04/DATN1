
from pathlib import Path
import sys
import json

# ==========================================
# 1. CAU HINH
# ==========================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "shadowing" / "hsk2"

SOURCE = (
    BASE / "data" / "processed"
    / "video3_ready_for_review.json"
)

MA_BAI_HOC = 25
THU_TU = 3

VIDEO_ID = "uv8KNcXpels"

TIEU_DE = (
    "每日学习法 - "
    "Phương pháp học tiếng Trung mỗi ngày"
)

MO_TA = (
    "Hội thoại về các phương pháp học tiếng Trung "
    "mỗi ngày: tạo môi trường học tập, luyện nghe, "
    "luyện nói và luyện viết."
)

sys.path.insert(0, str(ROOT))

from database import get_connection


# ==========================================
# 2. DOC VA KIEM TRA JSON
# ==========================================

def prepare_data():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError(
            "YouTube ID trong JSON khong khop!"
        )

    sentences = data.get("sentences", [])

    if len(sentences) != 252:
        raise ValueError(
            f"Can 252 cau, hien co {len(sentences)}"
        )

    clean_sentences = []

    for i, item in enumerate(sentences, 1):

        start = float(item["start"])
        end = float(item["end"])

        hanzi = str(item["hanzi"]).strip()
        pinyin = str(item["pinyin"]).strip()
        vi = str(item["vi"]).strip()

        if start < 0 or end <= start:
            raise ValueError(
                f"Timestamp sai o cau {i}"
            )

        if not all([hanzi, pinyin, vi]):
            raise ValueError(
                f"Thieu du lieu o cau {i}"
            )

        if clean_sentences:
            previous_end = clean_sentences[-1]["end"]

            if start < previous_end - 0.001:
                raise ValueError(
                    f"Chong timestamp o cau {i}"
                )

        clean_sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": vi
        })

    # Cau truc giong hai video Shadowing cu.
    document = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "description": MO_TA,
        "sentences": clean_sentences
    }

    return document


# ==========================================
# 3. KIEM TRA SQL HIEN CO
# ==========================================

def check_existing(cursor):

    cursor.execute(
        """
        SELECT
            MaNoiDung,
            ThuTu,
            TieuDe,
            NoiDung
        FROM dbo.NoiDungBaiHoc
             WITH (UPDLOCK, HOLDLOCK)
        WHERE MaBaiHoc = ?
        ORDER BY ThuTu, MaNoiDung
        """,
        MA_BAI_HOC
    )

    rows = cursor.fetchall()

    print("\n===== VIDEO HSK2 HIEN CO =====")

    for row in rows:

        ma_noi_dung = row[0]
        thu_tu = row[1]
        title = row[2]
        raw = row[3]

        print(
            f"MaNoiDung={ma_noi_dung} | "
            f"ThuTu={thu_tu} | "
            f"{title}"
        )

        if thu_tu == THU_TU:
            raise RuntimeError(
                "ThuTu=3 da duoc su dung. "
                "Khong them de tranh trung thu tu."
            )

        if title == TIEU_DE:
            raise RuntimeError(
                "Tieu de video da ton tai!"
            )

        # Chan trung YouTube ID, ke ca khi
        # chuoi JSON cu bi loi.
        if isinstance(raw, str) and VIDEO_ID in raw:
            raise RuntimeError(
                "YouTube ID da ton tai trong SQL! "
                f"MaNoiDung={ma_noi_dung}"
            )

    print("\nDa kiem tra: khong trung video.")
    print("ThuTu=3 chua duoc su dung.")


# ==========================================
# 4. KIEM TRA COT NOI DUNG
# ==========================================

def check_json_column(cursor):

    cursor.execute(
        """
        SELECT max_length
        FROM sys.columns
        WHERE object_id = OBJECT_ID(
            'dbo.NoiDungBaiHoc'
        )
        AND name = 'NoiDung'
        """
    )

    row = cursor.fetchone()

    if row is None:
        raise RuntimeError(
            "Khong tim thay cot NoiDung."
        )

    # -1 la NVARCHAR(MAX) / VARCHAR(MAX).
    # JSON 252 cau can cot du dai.
    if row[0] != -1:
        raise RuntimeError(
            "Cot NoiDung khong phai kieu MAX. "
            "Can kiem tra dung luong truoc khi INSERT."
        )


# ==========================================
# 5. INSERT VIDEO MOI
# ==========================================

def insert_video(document):

    connection = get_connection()
    connection.autocommit = False

    try:
        cursor = connection.cursor()

        check_json_column(cursor)
        check_existing(cursor)

        print("\n===== VIDEO SAP THEM =====")
        print("MaBaiHoc:", MA_BAI_HOC)
        print("ThuTu:", THU_TU)
        print("TieuDe:", TIEU_DE)
        print("YouTube:", VIDEO_ID)
        print(
            "So cau:",
            len(document["sentences"])
        )

        confirm = input(
            "\nNhap THEM de tao video moi: "
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

        # Chia JSON thanh nhieu doan.
        # Tranh loi pyodbc voi Unicode dai.
        chunks = [
            json_text[i:i + 900]
            for i in range(0, len(json_text), 900)
        ]

        json_expression = " + ".join(
            "CONVERT(NVARCHAR(MAX), ?)"
            for _ in chunks
        )

        # MaNoiDung la IDENTITY.
        # SQL Server se tu sinh.
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
                ?,
                ?,
                {json_expression},
                NULL,
                NULL,
                ?
            )
        """

        params = [
            MA_BAI_HOC,
            "nghe",
            TIEU_DE,
            *chunks,
            THU_TU
        ]

        cursor.execute(sql, *params)

        inserted = cursor.fetchone()

        if inserted is None:
            raise RuntimeError(
                "INSERT khong tra ve MaNoiDung."
            )

        new_id = int(inserted[0])

        # ==================================
        # 6. DOC LAI DE XAC MINH
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
                "Khong doc lai duoc video moi."
            )

        if row[0] != MA_BAI_HOC:
            raise RuntimeError(
                "MaBaiHoc khong khop!"
            )

        if row[1] != "nghe":
            raise RuntimeError(
                "LoaiNoiDung khong khop!"
            )

        if row[2] != TIEU_DE:
            raise RuntimeError(
                "TieuDe khong khop!"
            )

        if row[4] != THU_TU:
            raise RuntimeError(
                "ThuTu khong khop!"
            )

        saved_document = json.loads(row[3])

        if saved_document != document:
            raise RuntimeError(
                "JSON luu vao SQL khong khop!"
            )

        if len(saved_document["sentences"]) != 252:
            raise RuntimeError(
                "So cau trong SQL khong bang 252!"
            )

        # Chi COMMIT khi moi thu deu dung.
        connection.commit()

        print("\n===== INSERT THANH CONG =====")
        print("MaNoiDung moi:", new_id)
        print("MaBaiHoc:", MA_BAI_HOC)
        print("ThuTu:", THU_TU)
        print("YouTube ID:", VIDEO_ID)
        print("So cau:", 252)
        print("Doc lai SQL: OK")
        print("COMMIT: THANH CONG")

    except Exception:
        connection.rollback()

        print(
            "\nCo loi. Da ROLLBACK, "
            "khong luu ban ghi moi."
        )

        raise

    finally:
        connection.close()


# ==========================================
# 7. CHUONG TRINH CHINH
# ==========================================

if __name__ == "__main__":

    print("===== SHADOWING HSK2 - VIDEO 3 =====")

    document = prepare_data()

    print("File JSON:", SOURCE)
    print(
        "So cau hop le:",
        len(document["sentences"])
    )

    insert_video(document)
