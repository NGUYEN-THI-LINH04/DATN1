
import argparse
import json
import sys
from pathlib import Path

# ==========================================================
# CAU HINH
# ==========================================================

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from database import get_connection

BASE = Path(__file__).resolve().parent

JSON_FILE = (
    BASE / "data" / "processed" / "video_1_final.json"
)

MA_BAI_HOC = 25
YOUTUBE_ID = "nxAfRmACtZs"
TITLE = "用中文讲故事 - Kể chuyện bằng tiếng Trung"

EXPECTED_SENTENCES = 231

# Chia JSON thanh cac chuoi nho de tranh loi ODBC.
CHUNK_SIZE = 800


# ==========================================================
# 1. DOC VA KIEM TRA JSON
# ==========================================================

def load_json():
    if not JSON_FILE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {JSON_FILE}"
        )

    with JSON_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("JSON goc khong phai object")

    if data.get("module") != "shadowing":
        raise ValueError("Sai module")

    if data.get("youtube_id") != YOUTUBE_ID:
        raise ValueError("Sai YouTube ID")

    sentences = data.get("sentences")

    if not isinstance(sentences, list):
        raise ValueError("Thieu sentences")

    if len(sentences) != EXPECTED_SENTENCES:
        raise ValueError(
            f"Can {EXPECTED_SENTENCES} cau, "
            f"nhung co {len(sentences)} cau"
        )

    previous_end = -1

    for i, item in enumerate(sentences, 1):
        if not isinstance(item, dict):
            raise ValueError(f"Cau {i}: sai cau truc")

        start = item.get("start")
        end = item.get("end")

        if (
            not isinstance(start, (int, float))
            or isinstance(start, bool)
        ):
            raise ValueError(f"Cau {i}: start sai")

        if (
            not isinstance(end, (int, float))
            or isinstance(end, bool)
            or end <= start
        ):
            raise ValueError(f"Cau {i}: end sai")

        if start < previous_end - 0.01:
            raise ValueError(f"Cau {i}: thoi gian chong")

        for key in ("hanzi", "pinyin", "vi"):
            value = item.get(key)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Cau {i}: thieu {key}"
                )

        previous_end = end

    return data


# ==========================================================
# 2. TAO JSON UNICODE
# ==========================================================

def make_json_text(data):
    # NoiDung hien tai la NVARCHAR(MAX).
    # Luu truc tiep Unicode, khong can ASCII escape.

    text = json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":")
    )

    if json.loads(text) != data:
        raise ValueError("Loi chuyen doi JSON")

    return text


def split_chunks(text):
    return [
        text[i:i + CHUNK_SIZE]
        for i in range(0, len(text), CHUNK_SIZE)
    ]


# ==========================================================
# 3. KIEM TRA COT SQL
# ==========================================================

def check_sql_column(cursor):
    cursor.execute("""
        SELECT
            TYPE_NAME(user_type_id),
            max_length
        FROM sys.columns
        WHERE object_id = OBJECT_ID(
            N'dbo.NoiDungBaiHoc'
        )
        AND name = N'NoiDung'
    """)

    row = cursor.fetchone()

    if row is None:
        raise RuntimeError(
            "Khong tim thay cot NoiDung"
        )

    column_type = str(row[0]).lower()
    max_length = int(row[1])

    print("Kieu cot NoiDung:", column_type)
    print("Kich thuoc cot:", max_length)

    if column_type != "nvarchar" or max_length != -1:
        raise RuntimeError(
            "Script nay yeu cau NoiDung NVARCHAR(MAX). "
            "Khong tu thay doi cau truc SQL."
        )


# ==========================================================
# 4. KIEM TRA VIDEO CU
# ==========================================================

def check_existing(cursor):
    cursor.execute("""
        SELECT
            MaNoiDung,
            ThuTu,
            TieuDe
        FROM dbo.NoiDungBaiHoc
        WHERE MaBaiHoc = ?
        ORDER BY ThuTu, MaNoiDung
    """, MA_BAI_HOC)

    rows = cursor.fetchall()

    print("\n=== NOI DUNG HSK2 HIEN CO ===")

    for row in rows:
        print(
            f"MaNoiDung={row[0]} | "
            f"ThuTu={row[1]} | "
            f"TieuDe={row[2]}"
        )

    if not rows:
        raise RuntimeError(
            "Chua co noi dung nao thuoc MaBaiHoc=25."
        )

    cursor.execute("""
        SELECT MaNoiDung
        FROM dbo.NoiDungBaiHoc
        WHERE MaBaiHoc = ?
          AND NoiDung LIKE ?
    """, MA_BAI_HOC, f"%{YOUTUBE_ID}%")

    found = cursor.fetchone()

    if found:
        print(
            "\nVideo da ton tai, MaNoiDung:",
            found[0]
        )
        return True

    return False


# ==========================================================
# 5. KIEM TRA MA NOI DUNG TU TANG
# ==========================================================

def is_identity(cursor):
    cursor.execute("""
        SELECT COLUMNPROPERTY(
            OBJECT_ID(N'dbo.NoiDungBaiHoc'),
            N'MaNoiDung',
            'IsIdentity'
        )
    """)

    row = cursor.fetchone()

    if not row or row[0] is None:
        raise RuntimeError(
            "Khong xac dinh duoc IDENTITY"
        )

    return int(row[0]) == 1


# ==========================================================
# 6. INSERT JSON THANH NHIEU DOAN
# ==========================================================

def insert_video(cursor, json_text):
    chunks = split_chunks(json_text)

    if not chunks:
        raise RuntimeError("JSON rong")

    # Khoa bang trong giao dich, tranh sinh trung ID/ThuTu.
    cursor.execute("""
        SELECT ISNULL(MAX(MaNoiDung), 0) + 1
        FROM dbo.NoiDungBaiHoc WITH (TABLOCKX, HOLDLOCK)
    """)

    next_id = int(cursor.fetchone()[0])

    cursor.execute("""
        SELECT ISNULL(MAX(ThuTu), 0) + 1
        FROM dbo.NoiDungBaiHoc
        WHERE MaBaiHoc = ?
    """, MA_BAI_HOC)

    new_order = int(cursor.fetchone()[0])

    # Kiem tra trung lan nua sau khi da khoa bang.
    cursor.execute("""
        SELECT MaNoiDung
        FROM dbo.NoiDungBaiHoc
        WHERE MaBaiHoc = ?
          AND NoiDung LIKE ?
    """, MA_BAI_HOC, f"%{YOUTUBE_ID}%")

    if cursor.fetchone():
        raise RuntimeError(
            "Video da duoc them boi giao dich khac."
        )

    identity = is_identity(cursor)

    print("\n=== INSERT ===")
    print("MaNoiDung IDENTITY:", identity)
    print("ThuTu moi:", new_order)
    print("So doan JSON:", len(chunks))

    # Chi truyen 800 ky tu Unicode moi lan.
    # CAST sang NVARCHAR(MAX) ngay trong SQL.
    first_chunk = chunks[0]

    if identity:
        cursor.execute("""
            INSERT INTO dbo.NoiDungBaiHoc
            (
                MaBaiHoc,
                LoaiNoiDung,
                TieuDe,
                NoiDung,
                ThuTu
            )
            OUTPUT INSERTED.MaNoiDung
            VALUES
            (
                ?, ?, ?,
                CAST(? AS NVARCHAR(MAX)),
                ?
            )
        """,
            MA_BAI_HOC,
            "nghe",
            TITLE,
            first_chunk,
            new_order
        )

        new_id = int(cursor.fetchone()[0])

    else:
        new_id = next_id

        cursor.execute("""
            INSERT INTO dbo.NoiDungBaiHoc
            (
                MaNoiDung,
                MaBaiHoc,
                LoaiNoiDung,
                TieuDe,
                NoiDung,
                ThuTu
            )
            VALUES
            (
                ?, ?, ?, ?,
                CAST(? AS NVARCHAR(MAX)),
                ?
            )
        """,
            new_id,
            MA_BAI_HOC,
            "nghe",
            TITLE,
            first_chunk,
            new_order
        )

    # Noi cac phan JSON con lai.
    for index, chunk in enumerate(chunks[1:], 2):
        cursor.execute("""
            UPDATE dbo.NoiDungBaiHoc
            SET NoiDung =
                CAST(NoiDung AS NVARCHAR(MAX))
                + CAST(? AS NVARCHAR(MAX))
            WHERE MaNoiDung = ?
              AND MaBaiHoc = ?
        """,
            chunk,
            new_id,
            MA_BAI_HOC
        )

        if index % 20 == 0 or index == len(chunks):
            print(
                f"Da ghi {index}/{len(chunks)} doan JSON"
            )

    return new_id, new_order


# ==========================================================
# 7. DOC LAI VA XAC MINH
# ==========================================================

def verify_saved(cursor, new_id, new_order, data):
    cursor.execute("""
        SELECT
            MaBaiHoc,
            LoaiNoiDung,
            TieuDe,
            NoiDung,
            ThuTu
        FROM dbo.NoiDungBaiHoc
        WHERE MaNoiDung = ?
    """, new_id)

    row = cursor.fetchone()

    if row is None:
        raise RuntimeError("Khong thay ban ghi vua them")

    ma_bai, loai, title, content, thu_tu = row

    if ma_bai != MA_BAI_HOC:
        raise RuntimeError("Sai MaBaiHoc")

    if loai != "nghe":
        raise RuntimeError("Sai LoaiNoiDung")

    if title != TITLE:
        raise RuntimeError("Sai TieuDe")

    if thu_tu != new_order:
        raise RuntimeError("Sai ThuTu")

    try:
        saved_data = json.loads(content)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(
            "SQL tra ve JSON khong hop le"
        ) from exc

    # So sanh toan bo du lieu voi file goc.
    if saved_data != data:
        raise RuntimeError(
            "JSON luu trong SQL khong khop file goc"
        )

    count = len(saved_data["sentences"])

    if count != EXPECTED_SENTENCES:
        raise RuntimeError(
            f"SQL chi co {count} cau"
        )

    return count


# ==========================================================
# 8. MAIN
# ==========================================================

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--commit",
        action="store_true",
        help="Thuc su ghi SQL"
    )

    args = parser.parse_args()

    data = load_json()
    json_text = make_json_text(data)

    print("\n=== HSK2 VIDEO 1 ===")
    print("Tieu de:", TITLE)
    print("YouTube:", YOUTUBE_ID)
    print("MaBaiHoc:", MA_BAI_HOC)
    print("So cau:", len(data["sentences"]))
    print("Do dai JSON:", len(json_text))

    conn = get_connection()

    try:
        conn.autocommit = False
        cursor = conn.cursor()

        check_sql_column(cursor)

        if check_existing(cursor):
            conn.rollback()
            print("Khong ghi them ban trung.")
            return

        if not args.commit:
            conn.rollback()

            print("\n=== KIEM TRA THANH CONG ===")
            print("Chua thay doi SQL.")
            print("Chay --commit de them video.")
            return

        new_id, new_order = insert_video(
            cursor,
            json_text
        )

        count = verify_saved(
            cursor,
            new_id,
            new_order,
            data
        )

        # Chi luu khi doc lai dung toan bo JSON.
        conn.commit()

        print("\n==============================")
        print("THEM SQL THANH CONG")
        print("==============================")
        print("MaNoiDung moi:", new_id)
        print("MaBaiHoc:", MA_BAI_HOC)
        print("ThuTu:", new_order)
        print("So cau:", count)
        print("YouTube:", YOUTUBE_ID)
        print("Da kiem tra toan bo JSON.")
        print("Khong sua bai 差不多.")
        print("Khong thay doi HSK1.")

    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass

        print("\n=== LOI ===")
        print("Da yeu cau rollback giao dich.")
        print("Chi tiet:", exc)
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()
