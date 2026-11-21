
import sys
import json
from pathlib import Path
from datetime import datetime
from contextlib import closing

# ==================================================
# 1. CAU HINH DU AN
# ==================================================

ROOT = Path(r"D:\DATN1")
BASE = ROOT / "scripts" / "shadowing" / "hsk3"

SOURCE = (
    BASE / "data" / "processed"
    / "video1_translated_full.json"
)

BACKUP_DIR = BASE / "data" / "backup"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_ID = "wZDej3Logc4"
MA_KHOA_HOC = 3
EXPECTED_COUNT = 244

sys.path.insert(0, str(ROOT))

from database import get_connection


# ==================================================
# 2. DOC VA KIEM TRA FILE JSON
# ==================================================

def load_json():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if not isinstance(data, dict):
        raise ValueError("JSON khong hop le.")

    if data.get("module") != "shadowing":
        raise ValueError("Sai module.")

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError("Sai YouTube ID.")

    sentences = data.get("sentences")

    if not isinstance(sentences, list):
        raise ValueError("sentences phai la list.")

    if len(sentences) != EXPECTED_COUNT:
        raise ValueError(
            f"Can {EXPECTED_COUNT} doan, "
            f"hien co {len(sentences)}."
        )

    previous_end = 0.0

    for i, item in enumerate(sentences, 1):

        if not isinstance(item, dict):
            raise ValueError(
                f"Doan {i} khong hop le."
            )

        for key in ("hanzi", "pinyin", "vi"):
            value = item.get(key)

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                raise ValueError(
                    f"Doan {i} thieu {key}."
                )

        start = float(item["start"])
        end = float(item["end"])

        if start < 0 or end <= start:
            raise ValueError(
                f"Timestamp sai o doan {i}."
            )

        if i > 1 and start < previous_end - 0.001:
            raise ValueError(
                f"Timestamp chong nhau o doan {i}."
            )

        previous_end = end

    return data


# ==================================================
# 3. TIM VIDEO HSK3 DA THEM QUA ADMIN
# ==================================================

def find_video(cursor):

    cursor.execute(
        """
        SELECT
            nd.MaNoiDung,
            nd.MaBaiHoc,
            nd.TieuDe,
            nd.ThuTu,
            nd.NoiDung

        FROM dbo.NoiDungBaiHoc AS nd
             WITH (UPDLOCK, HOLDLOCK)

        INNER JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc = nd.MaBaiHoc

        WHERE bh.MaKhoaHoc = ?
          AND nd.LoaiNoiDung = 'nghe'
        """,
        MA_KHOA_HOC
    )

    matches = []

    for row in cursor.fetchall():

        try:
            data = json.loads(row[4])
        except (ValueError, TypeError):
            continue

        if not isinstance(data, dict):
            continue

        if (
            data.get("module") == "shadowing"
            and data.get("youtube_id") == VIDEO_ID
        ):
            matches.append((row, data))

    if len(matches) == 0:
        raise RuntimeError(
            "Chua tim thay video HSK3 trong Admin.\n"
            f"Hay them video: https://youtu.be/{VIDEO_ID}"
        )

    if len(matches) > 1:
        raise RuntimeError(
            "Co nhieu video trung YouTube ID "
            "trong HSK3. Can kiem tra SQL."
        )

    return matches[0]


# ==================================================
# 4. CAP NHAT SQL SERVER
# ==================================================

def update_video(source):

    with closing(get_connection()) as connection:

        connection.autocommit = False

        try:
            with closing(connection.cursor()) as cursor:

                row, existing = find_video(cursor)

                video_id = int(row[0])
                lesson_id = int(row[1])
                title = row[2]
                order = row[3]
                old_raw = row[4]

                old_sentences = existing.get(
                    "sentences", []
                )

                if not isinstance(old_sentences, list):
                    raise ValueError(
                        "sentences cu khong hop le."
                    )

                print("\n===== VIDEO TRONG ADMIN =====")
                print("MaNoiDung:", video_id)
                print("MaKhoaHoc:", MA_KHOA_HOC)
                print("MaBaiHoc:", lesson_id)
                print("ThuTu:", order)
                print("TieuDe:", title)
                print("YouTube:", VIDEO_ID)
                print("So cau cu:", len(old_sentences))
                print("So cau moi:", EXPECTED_COUNT)

                # Khong ghi de neu da co loi thoai
                if old_sentences:
                    raise RuntimeError(
                        "Video da co loi thoai trong SQL. "
                        "Dung de tranh ghi de."
                    )

                # ==================================
                # 5. SAO LUU JSON CU
                # ==================================

                stamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S_%f"
                )

                backup_file = (
                    BACKUP_DIR
                    / f"video1_before_update_{stamp}.json"
                )

                backup_file.write_text(
                    old_raw,
                    encoding="utf-8"
                )

                print("\nDa backup:")
                print(backup_file)

                # ==================================
                # 6. GHEP LOI THOAI VAO BAN GHI CU
                # ==================================

                document = existing.copy()

                document["sentences"] = (
                    source["sentences"]
                )

                json_text = json.dumps(
                    document,
                    ensure_ascii=False,
                    separators=(",", ":")
                )

                print("\n===== XAC NHAN =====")
                print("Chi UPDATE video:", VIDEO_ID)
                print("So cau:", EXPECTED_COUNT)

                confirm = input(
                    "\nNhap CAPNHAT de tiep tuc: "
                ).strip()

                if confirm != "CAPNHAT":
                    connection.rollback()
                    print("Da huy. SQL khong thay doi.")
                    return

                # ==================================
                # 7. UPDATE NVARCHAR(MAX)
                # ==================================

                # Chia nho chuoi Unicode khi truyen
                # qua pyodbc / SQL Server.
                chunks = [
                    json_text[i:i + 800]
                    for i in range(0, len(json_text), 800)
                ]

                if len(chunks) > 1800:
                    raise RuntimeError(
                        "JSON qua lon cho cach UPDATE nay."
                    )

                expression = " + ".join(
                    "CONVERT(NVARCHAR(MAX), ?)"
                    for _ in chunks
                )

                sql = f"""
                    UPDATE dbo.NoiDungBaiHoc
                    SET NoiDung = {expression}
                    WHERE MaNoiDung = ?
                      AND MaBaiHoc = ?
                      AND LoaiNoiDung = 'nghe'
                """

                cursor.execute(
                    sql,
                    *chunks,
                    video_id,
                    lesson_id
                )

                # ==================================
                # 8. DOC LAI DE KIEM TRA
                # ==================================

                cursor.execute(
                    """
                    SELECT NoiDung
                    FROM dbo.NoiDungBaiHoc
                    WHERE MaNoiDung = ?
                      AND MaBaiHoc = ?
                    """,
                    video_id,
                    lesson_id
                )

                saved_row = cursor.fetchone()

                if saved_row is None:
                    raise RuntimeError(
                        "Khong tim thay video sau UPDATE."
                    )

                saved = json.loads(saved_row[0])

                if saved != document:
                    raise RuntimeError(
                        "JSON doc lai khong khop."
                    )

                if len(saved["sentences"]) != EXPECTED_COUNT:
                    raise RuntimeError(
                        "So cau sau UPDATE khong khop."
                    )

                connection.commit()

                print("\n===== UPDATE THANH CONG =====")
                print("MaNoiDung:", video_id)
                print("MaBaiHoc:", lesson_id)
                print("YouTube:", VIDEO_ID)
                print("So cau:", len(saved["sentences"]))
                print("Kiem tra SQL: OK")
                print("COMMIT: THANH CONG")

        except Exception:
            connection.rollback()
            print("\nCO LOI - DA ROLLBACK SQL.")
            raise


# ==================================================
# 9. MAIN
# ==================================================

if __name__ == "__main__":

    print(
        "===== SHADOWING HSK3 - UPDATE VIDEO 1 ====="
    )

    source = load_json()

    print("File:", SOURCE)
    print("So doan:", len(source["sentences"]))

    update_video(source)
