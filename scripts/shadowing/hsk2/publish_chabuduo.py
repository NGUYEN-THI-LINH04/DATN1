
from pathlib import Path
from datetime import datetime
import sys
import json
import re

# ==========================================
# 1. CAU HINH
# ==========================================

ROOT = Path(r"D:\DATN1")
BASE = ROOT / "scripts" / "shadowing" / "hsk2"

PROCESSED = BASE / "data" / "processed"
BACKUP_DIR = BASE / "data" / "backup"

BACKUP_DIR.mkdir(parents=True, exist_ok=True)

SOURCE = PROCESSED / "video_chabuduo_review_v3.json"
FINAL = PROCESSED / "video_chabuduo_final.json"

MA_BAI_HOC = 25
MA_NOI_DUNG = 2

# Video da co 241 cau, dung de kiem tra cau truc SQL.
MA_NOI_DUNG_MAU = 8

VIDEO_ID = "VkEYoXw7jD0"

sys.path.insert(0, str(ROOT))

from database import get_connection


# ==========================================
# 2. CHUAN HOA PINYIN
# ==========================================

def clean_pinyin(value):
    value = str(value or "").strip()

    # Loai bo dau cau trong pinyin.
    value = re.sub(
        r"[，。！？；：、,.!?;:]+",
        " ",
        value
    )

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def prepare_sentences():
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError("Sai YouTube ID!")

    original = data.get("sentences", [])

    if len(original) != 36:
        raise ValueError(
            f"Can 36 cau, nhung co {len(original)} cau."
        )

    sentences = []

    for i, item in enumerate(original, 1):
        start = float(item["start"])
        end = float(item["end"])

        hanzi = str(item["hanzi"]).strip()
        pinyin = clean_pinyin(item["pinyin"])
        vi = str(item["vi"]).strip()

        if start < 0 or end <= start:
            raise ValueError(
                f"Timestamp khong hop le o cau {i}"
            )

        if not all([hanzi, pinyin, vi]):
            raise ValueError(
                f"Thieu noi dung o cau {i}"
            )

        if sentences and start < sentences[-1]["end"]:
            raise ValueError(
                f"Timestamp chong nhau o cau {i}"
            )

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": vi,
        })

    result = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "title": "差不多 - Gần giống nhau",
        "sentences": sentences,
    }

    FINAL.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    return result


# ==========================================
# 3. HAM DOC DU LIEU SQL
# ==========================================

def quote_column(name):
    return "[" + name.replace("]", "]]") + "]"


def get_one_row(cursor, ma_noi_dung):
    cursor.execute(
        """
        SELECT TOP (2) *
        FROM dbo.NoiDungBaiHoc
        WHERE MaBaiHoc = ?
          AND MaNoiDung = ?
        """,
        MA_BAI_HOC,
        ma_noi_dung
    )

    column_names = [
        desc[0] for desc in cursor.description
    ]

    rows = cursor.fetchall()

    if len(rows) != 1:
        raise RuntimeError(
            f"MaNoiDung={ma_noi_dung}: "
            f"tim thay {len(rows)} dong, can dung 1 dong."
        )

    return dict(zip(column_names, rows[0]))


def parse_json(value):
    if not isinstance(value, str):
        return None

    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return None


def find_json_column(sample_row):
    """
    Tim cot JSON dua tren video HSK2 da luu 241 cau.
    Khong doan ten cot.
    """

    candidates = []

    for column, value in sample_row.items():
        parsed = parse_json(value)

        if (
            isinstance(parsed, dict)
            and isinstance(parsed.get("sentences"), list)
            and len(parsed["sentences"]) >= 100
        ):
            candidates.append(column)

    if len(candidates) != 1:
        raise RuntimeError(
            "Khong xac dinh duoc duy nhat cot JSON "
            "theo video mau MaNoiDung=8.\n"
            f"Cac cot phat hien: {candidates}\n"
            "Dung lai de tranh cap nhat nham."
        )

    return candidates[0]


# ==========================================
# 4. CAP NHAT CO SAO LUU
# ==========================================

def publish(data):
    connection = get_connection()
    connection.autocommit = False

    try:
        cursor = connection.cursor()

        sample_row = get_one_row(
            cursor, MA_NOI_DUNG_MAU
        )

        target_row = get_one_row(
            cursor, MA_NOI_DUNG
        )

        json_column = find_json_column(sample_row)

        print("\n===== KIEM TRA SQL =====")
        print("Bang: dbo.NoiDungBaiHoc")
        print("MaBaiHoc:", MA_BAI_HOC)
        print("MaNoiDung:", MA_NOI_DUNG)
        print("Cot JSON:", json_column)

        old_value = target_row[json_column]
        old_document = parse_json(old_value)

        # Khong ghi de mot noi dung dang la chuoi
        # khong phai JSON.
        if old_value not in (None, ""):
            if not isinstance(old_document, dict):
                raise RuntimeError(
                    "Cot dich dang co noi dung "
                    "khong phai JSON object. "
                    "Dung lai de kiem tra."
                )

        # Giu lai metadata JSON cua video dich.
        if isinstance(old_document, dict):
            updated = old_document.copy()

            old_video_id = updated.get("youtube_id")

            if (
                old_video_id
                and old_video_id != VIDEO_ID
            ):
                raise RuntimeError(
                    "YouTube ID trong JSON SQL "
                    "khong khop video dich!"
                )

            updated["sentences"] = data["sentences"]

            if "youtube_id" in updated:
                updated["youtube_id"] = VIDEO_ID

        else:
            # Truong hop cot JSON hien dang NULL.
            updated = data.copy()

        new_value = json.dumps(
            updated,
            ensure_ascii=False,
            separators=(",", ":")
        )

        # --------------------------------------
        # Sao luu noi dung truoc khi cap nhat
        # --------------------------------------

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_file = (
            BACKUP_DIR /
            f"chabuduo_sql_before_{timestamp}.json"
        )

        backup = {
            "MaBaiHoc": MA_BAI_HOC,
            "MaNoiDung": MA_NOI_DUNG,
            "column": json_column,
            "old_value": old_value,
        }

        backup_file.write_text(
            json.dumps(
                backup,
                ensure_ascii=False,
                indent=2,
                default=str
            ),
            encoding="utf-8"
        )

        print("Da sao luu:", backup_file)

        # --------------------------------------
        # Ghi JSON theo tung doan ngan.
        # Tranh loi truyen chuoi Unicode dai
        # cua pyodbc / SQL Server.
        # --------------------------------------

        chunks = [
            new_value[i:i + 900]
            for i in range(0, len(new_value), 900)
        ]

        expression = " + ".join(
            "CONVERT(NVARCHAR(MAX), ?)"
            for _ in chunks
        )

        sql = f"""
            UPDATE dbo.NoiDungBaiHoc
            SET {quote_column(json_column)} = {expression}
            WHERE MaBaiHoc = ?
              AND MaNoiDung = ?
        """

        cursor.execute(
            sql,
            *chunks,
            MA_BAI_HOC,
            MA_NOI_DUNG
        )

        if cursor.rowcount not in (1, -1):
            raise RuntimeError(
                "So dong UPDATE khong hop le: "
                f"{cursor.rowcount}"
            )

        # --------------------------------------
        # Doc lai de kiem tra truoc COMMIT.
        # --------------------------------------

        verify_sql = f"""
            SELECT {quote_column(json_column)}
            FROM dbo.NoiDungBaiHoc
            WHERE MaBaiHoc = ?
              AND MaNoiDung = ?
        """

        cursor.execute(
            verify_sql,
            MA_BAI_HOC,
            MA_NOI_DUNG
        )

        saved_value = cursor.fetchone()[0]
        saved_document = parse_json(saved_value)

        if saved_document != updated:
            raise RuntimeError(
                "Du lieu doc lai khong khop. "
                "Tu dong ROLLBACK."
            )

        if len(saved_document.get("sentences", [])) != 36:
            raise RuntimeError(
                "So cau trong SQL khong bang 36."
            )

        connection.commit()

        print("\n===== THANH CONG =====")
        print("Da cap nhat SQL Server.")
        print("MaBaiHoc:", MA_BAI_HOC)
        print("MaNoiDung:", MA_NOI_DUNG)
        print("YouTube:", VIDEO_ID)
        print("So cau:", len(data["sentences"]))
        print("Da kiem tra du lieu doc lai: OK")

    except Exception:
        connection.rollback()
        print("\nDa ROLLBACK hoac khong ghi thay doi.")
        raise

    finally:
        connection.close()


# ==========================================
# 5. CHUONG TRINH CHINH
# ==========================================

def main():
    data = prepare_sentences()

    print("===== FILE JSON CHINH THUC =====")
    print("File:", FINAL)
    print("So cau:", len(data["sentences"]))
    print("Video:", data["youtube_id"])

    print("\nDang kiem tra va cap nhat SQL...")

    publish(data)


if __name__ == "__main__":
    main()
