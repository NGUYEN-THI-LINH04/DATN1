
from pathlib import Path
from datetime import datetime
import json
import sys

ROOT = Path(r"D:\DATN1")
BASE = ROOT / "scripts" / "shadowing" / "hsk2"

SOURCE = BASE / "data" / "processed" / "video3_ready_for_review.json"
BACKUP_DIR = BASE / "data" / "backup"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

MA_BAI_HOC = 25
VIDEO_ID = "uv8KNcXpels"

sys.path.insert(0, str(ROOT))
from database import get_connection


def load_data():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError("Sai YouTube ID trong JSON!")

    sentences = data.get("sentences", [])

    if len(sentences) != 252:
        raise ValueError(
            f"So cau khong dung: {len(sentences)}"
        )

    for i, s in enumerate(sentences, 1):
        for key in ("start", "end", "hanzi", "pinyin", "vi"):
            if key not in s or s[key] in ("", None):
                raise ValueError(f"Cau {i} thieu {key}")

        if float(s["end"]) <= float(s["start"]):
            raise ValueError(f"Timestamp sai o cau {i}")

        if i > 1 and float(s["start"]) < float(
            sentences[i - 2]["end"]
        ) - 0.001:
            raise ValueError(f"Chong timestamp o cau {i}")

    return data


def find_target(cursor):
    """
    Tim video trong HSK2 theo YouTube ID.
    Khong tu doan MaNoiDung = 3.
    """
    cursor.execute(
        """
        SELECT MaNoiDung, NoiDung
        FROM dbo.NoiDungBaiHoc
        WHERE MaBaiHoc = ?
        ORDER BY MaNoiDung
        """,
        MA_BAI_HOC
    )

    rows = cursor.fetchall()
    matches = []

    print("\n===== KIEM TRA VIDEO HSK2 =====")

    for row in rows:
        ma_noi_dung = row[0]
        raw = row[1]

        print("MaNoiDung:", ma_noi_dung)

        if isinstance(raw, str) and VIDEO_ID in raw:
            try:
                document = json.loads(raw)
            except json.JSONDecodeError:
                raise RuntimeError(
                    f"MaNoiDung={ma_noi_dung}: "
                    "Co video ID nhung JSON khong hop le."
                )

            if not isinstance(document, dict):
                raise RuntimeError(
                    f"MaNoiDung={ma_noi_dung}: "
                    "NoiDung khong phai JSON object."
                )

            if not isinstance(document.get("sentences"), list):
                raise RuntimeError(
                    f"MaNoiDung={ma_noi_dung}: "
                    "Chua co truong sentences. "
                    "Can kiem tra cau truc truoc khi ghi."
                )

            matches.append((ma_noi_dung, raw, document))

    if len(matches) == 0:
        print("\nCHUA TIM THAY VIDEO THU 3.")
        print("YouTube ID:", VIDEO_ID)
        print(
            "Hay them video vao HSK2 trong Admin "
            "truoc, roi chay lai script."
        )
        return None

    if len(matches) > 1:
        raise RuntimeError(
            "Tim thay nhieu ban ghi cung YouTube ID. "
            "Dung lai de tranh cap nhat nham."
        )

    return matches[0]


def publish():
    data = load_data()

    print("===== VIDEO 3 =====")
    print("YouTube:", VIDEO_ID)
    print("So cau:", len(data["sentences"]))
    print("File:", SOURCE)

    conn = get_connection()
    conn.autocommit = False

    try:
        cursor = conn.cursor()
        target = find_target(cursor)

        if target is None:
            conn.rollback()
            return

        ma_noi_dung, old_raw, old_document = target

        print("\n===== DA TIM THAY =====")
        print("MaBaiHoc:", MA_BAI_HOC)
        print("MaNoiDung:", ma_noi_dung)
        print("So cau cu:", len(old_document["sentences"]))
        print("So cau moi:", len(data["sentences"]))

        # Giu nguyen metadata va chi thay sentences.
        new_document = old_document.copy()
        new_document["sentences"] = data["sentences"]

        if "youtube_id" in new_document:
            if new_document["youtube_id"] != VIDEO_ID:
                raise RuntimeError(
                    "YouTube ID trong SQL khong khop."
                )

        # Sao luu ban goc.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / (
            f"video3_sql_before_{timestamp}.json"
        )

        backup_file.write_text(
            json.dumps(
                {
                    "MaBaiHoc": MA_BAI_HOC,
                    "MaNoiDung": ma_noi_dung,
                    "old_value": old_raw,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        print("Da sao luu:", backup_file)

        confirm = input(
            "\nNhap CAP NHAT de luu 252 cau vao SQL: "
        ).strip()

        if confirm != "CAP NHAT":
            print("Da huy. SQL khong thay doi.")
            conn.rollback()
            return

        new_json = json.dumps(
            new_document,
            ensure_ascii=False,
            separators=(",", ":")
        )

        # Chia chuoi tranh loi truyen JSON dai.
        chunks = [
            new_json[i:i + 900]
            for i in range(0, len(new_json), 900)
        ]

        expression = " + ".join(
            "CONVERT(NVARCHAR(MAX), ?)" for _ in chunks
        )

        sql = f"""
            UPDATE dbo.NoiDungBaiHoc
            SET NoiDung = {expression}
            WHERE MaBaiHoc = ?
              AND MaNoiDung = ?
        """

        cursor.execute(
            sql,
            *chunks,
            MA_BAI_HOC,
            ma_noi_dung
        )

        if cursor.rowcount not in (1, -1):
            raise RuntimeError(
                f"UPDATE khong hop le: {cursor.rowcount}"
            )

        # Doc lai truoc khi COMMIT.
        cursor.execute(
            """
            SELECT NoiDung
            FROM dbo.NoiDungBaiHoc
            WHERE MaBaiHoc = ?
              AND MaNoiDung = ?
            """,
            MA_BAI_HOC,
            ma_noi_dung
        )

        rows = cursor.fetchall()

        if len(rows) != 1:
            raise RuntimeError(
                "Khong xac minh duoc duy nhat 1 ban ghi."
            )

        saved_document = json.loads(rows[0][0])

        if saved_document != new_document:
            raise RuntimeError(
                "JSON doc lai khong khop! ROLLBACK."
            )

        conn.commit()

        print("\n===== THANH CONG =====")
        print("MaBaiHoc:", MA_BAI_HOC)
        print("MaNoiDung:", ma_noi_dung)
        print("Video:", VIDEO_ID)
        print("So cau:", len(saved_document["sentences"]))
        print("Kiem tra SQL: OK")

    except Exception:
        conn.rollback()
        print("\nDa ROLLBACK. Khong luu thay doi loi.")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    publish()
