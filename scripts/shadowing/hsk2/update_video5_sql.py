
import sys
import json
from pathlib import Path
from datetime import datetime
from contextlib import closing

# ==========================================
# 1. CAU HINH
# ==========================================

ROOT = Path(r"D:\DATN1")
BASE = ROOT / "scripts" / "shadowing" / "hsk2"

SOURCE = (
    BASE / "data" / "processed"
    / "video5_translated_full.json"
)

BACKUP_DIR = BASE / "data" / "backup"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_ID = "MYQrQvbR8Vk"
LESSON_ID = 25
EXPECTED_COUNT = 121

sys.path.insert(0, str(ROOT))

from database import get_connection


# ==========================================
# 2. DOC FILE JSON
# ==========================================

def load_source():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay JSON: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if not isinstance(data, dict):
        raise ValueError("JSON khong hop le.")

    if data.get("module") != "shadowing":
        raise ValueError("Sai module.")

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError("Sai YouTube ID!")

    sentences = data.get("sentences")

    if not isinstance(sentences, list):
        raise ValueError(
            "sentences phai la danh sach."
        )

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

            if not isinstance(
                item.get(key), str
            ) or not item[key].strip():

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
                f"Timestamp chong o doan {i}."
            )

        previous_end = end

    return data


# ==========================================
# 3. TIM VIDEO DA THEM QUA ADMIN
# ==========================================

def find_admin_video(cursor):

    cursor.execute(
        """
        SELECT
            MaNoiDung,
            TieuDe,
            ThuTu,
            NoiDung

        FROM dbo.NoiDungBaiHoc
             WITH (UPDLOCK, HOLDLOCK)

        WHERE MaBaiHoc = ?
          AND LoaiNoiDung = 'nghe'
        """,
        LESSON_ID
    )

    matches = []

    for row in cursor.fetchall():

        try:
            existing = json.loads(row[3])
        except (TypeError, ValueError):
            continue

        if not isinstance(existing, dict):
            continue

        if (
            existing.get("module") == "shadowing"
            and existing.get("youtube_id") == VIDEO_ID
        ):
            matches.append((row, existing))

    if not matches:

        raise RuntimeError(
            "\nCHUA TIM THAY VIDEO 5 TRONG ADMIN.\n"
            "Hay vao /admin/shadowing/ them video:\n"
            f"https://youtu.be/{VIDEO_ID}\n"
            "Sau do chay lai script."
        )

    if len(matches) != 1:
        raise RuntimeError(
            "Phat hien nhieu ban ghi cung YouTube ID. "
            "Can kiem tra SQL truoc khi cap nhat."
        )

    return matches[0]


# ==========================================
# 4. CAP NHAT LOI THOAI
# ==========================================

def update_sentences(source):

    with closing(get_connection()) as connection:

        connection.autocommit = False

        try:
            with closing(connection.cursor()) as cursor:

                # Tim dung ban ghi Admin da tao.
                row, existing = find_admin_video(cursor)

                video_id = int(row[0])
                title = row[1]
                order = row[2]

                current_sentences = existing.get(
                    "sentences", []
                )

                if not isinstance(
                    current_sentences, list
                ):
                    raise ValueError(
                        "Du lieu sentences trong SQL khong hop le."
                    )

                print(
                    "\n===== VIDEO TIM THAY TRONG SQL ====="
                )

                print("MaNoiDung:", video_id)
                print("MaBaiHoc:", LESSON_ID)
                print("ThuTu:", order)
                print("TieuDe:", title)
                print("YouTube:", VIDEO_ID)

                print(
                    "So cau hien tai:",
                    len(current_sentences)
                )

                print(
                    "So cau sap cap nhat:",
                    EXPECTED_COUNT
                )

                # Khong ghi de du lieu da co.
                if current_sentences:

                    raise RuntimeError(
                        "Video nay da co loi thoai trong SQL.\n"
                        "Dung lai de tranh ghi de du lieu cu."
                    )

                # ==================================
                # 5. SAO LUU DU LIEU SQL CU
                # ==================================

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S_%f"
                )

                backup_file = (
                    BACKUP_DIR
                    / f"video5_before_update_{timestamp}.json"
                )

                backup_file.write_text(
                    row[3],
                    encoding="utf-8"
                )

                print("\nDa sao luu:")
                print(backup_file)

                # ==================================
                # 6. GHEP LOI THOAI VAO JSON CU
                # ==================================

                document = existing.copy()

                document["sentences"] = source["sentences"]

                # Giu nguyen module, YouTube ID
                # va cac metadata hien tai cua video.

                json_text = json.dumps(
                    document,
                    ensure_ascii=False,
                    separators=(",", ":")
                )

                confirm = input(
                    "\nNhap CAPNHAT de luu 121 cau: "
                ).strip()

                if confirm != "CAPNHAT":

                    connection.rollback()

                    print(
                        "Da huy. SQL khong thay doi."
                    )

                    return

                # ==================================
                # 7. UPDATE NVARCHAR(MAX)
                # ==================================

                # Chia JSON de tranh van de
                # truyen chuoi Unicode dai qua pyodbc.
                chunks = [
                    json_text[i:i + 900]
                    for i in range(0, len(json_text), 900)
                ]

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
                    LESSON_ID
                )

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "UPDATE khong dung 1 ban ghi."
                    )

                # ==================================
                # 8. DOC LAI TRUOC KHI COMMIT
                # ==================================

                cursor.execute(
                    """
                    SELECT
                        MaNoiDung,
                        MaBaiHoc,
                        ThuTu,
                        NoiDung
                    FROM dbo.NoiDungBaiHoc
                    WHERE MaNoiDung = ?
                    """,
                    video_id
                )

                saved_row = cursor.fetchone()

                if saved_row is None:
                    raise RuntimeError(
                        "Khong tim thay du lieu sau UPDATE."
                    )

                saved = json.loads(saved_row[3])

                if saved != document:
                    raise RuntimeError(
                        "JSON trong SQL khong khop."
                    )

                if len(saved["sentences"]) != 121:
                    raise RuntimeError(
                        "So doan khong khop."
                    )

                if (
                    saved_row[1] != LESSON_ID
                    or saved_row[2] != order
                ):
                    raise RuntimeError(
                        "Thong tin bai hoc hoac thu tu bi thay doi."
                    )

                connection.commit()

                print(
                    "\n===== CAP NHAT THANH CONG ====="
                )

                print("MaNoiDung:", video_id)
                print("YouTube:", VIDEO_ID)
                print("ThuTu:", order)
                print("So cau:", len(saved["sentences"]))
                print("Kiem tra SQL: OK")
                print("COMMIT: THANH CONG")

        except Exception:

            connection.rollback()

            print(
                "\nCo loi. SQL da ROLLBACK."
            )

            raise


# ==========================================
# 9. CHUONG TRINH CHINH
# ==========================================

if __name__ == "__main__":

    print(
        "===== SHADOWING HSK2 - UPDATE VIDEO 5 ====="
    )

    source = load_source()

    print("File:", SOURCE)
    print(
        "So doan hop le:",
        len(source["sentences"])
    )

    update_sentences(source)
