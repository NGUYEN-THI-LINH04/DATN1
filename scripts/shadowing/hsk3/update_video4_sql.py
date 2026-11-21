
import sys
import json
import math

from pathlib import Path
from datetime import datetime
from contextlib import closing


# ==================================================
# 1. CAU HINH HSK3 - VIDEO 4
# ==================================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "shadowing" / "hsk3"

SOURCE = (
    BASE / "data" / "processed"
    / "video4_translated_full.json"
)

BACKUP_DIR = BASE / "data" / "backup"

VIDEO_ID = "yaeECV1JRjM"
MA_KHOA_HOC = 3
EXPECTED_COUNT = 396

sys.path.insert(0, str(ROOT))

from database import get_connection


# ==================================================
# 2. DOC VA KIEM TRA FILE JSON
# ==================================================

def load_source():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if not isinstance(data, dict):
        raise ValueError(
            "JSON khong hop le."
        )

    if data.get("module") != "shadowing":
        raise ValueError(
            "Sai module Shadowing."
        )

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError(
            "Sai YouTube ID cua video 4."
        )

    sentences = data.get("sentences")

    if not isinstance(sentences, list):
        raise ValueError(
            "Khong co danh sach sentences."
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

        for field in ("hanzi", "pinyin", "vi"):

            value = item.get(field)

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                raise ValueError(
                    f"Doan {i} thieu {field}."
                )

        try:
            start = float(item["start"])
            end = float(item["end"])

        except (KeyError, TypeError, ValueError):
            raise ValueError(
                f"Timestamp sai o doan {i}."
            )

        if not (
            math.isfinite(start)
            and math.isfinite(end)
        ):
            raise ValueError(
                f"Timestamp khong hop le o doan {i}."
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Thoi gian sai o doan {i}."
            )

        if i > 1 and start < previous_end - 0.001:
            raise ValueError(
                f"Timestamp chong nhau o doan {i}."
            )

        previous_end = end

    return data


# ==================================================
# 3. TIM VIDEO 4 DA THEM QUA ADMIN
# ==================================================

def find_admin_video(cursor):

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
            existing = json.loads(row[4])

        except (ValueError, TypeError):
            continue

        if not isinstance(existing, dict):
            continue

        if (
            existing.get("module") == "shadowing"
            and existing.get("youtube_id") == VIDEO_ID
        ):
            matches.append((row, existing))

    if len(matches) == 0:
        raise RuntimeError(
            "CHUA TIM THAY VIDEO 4 TRONG ADMIN.\n"
            "Hay them video vao HSK3 truoc:\n"
            f"https://youtu.be/{VIDEO_ID}"
        )

    if len(matches) > 1:
        raise RuntimeError(
            "Co nhieu video trung YouTube ID "
            "trong HSK3. Can kiem tra SQL."
        )

    return matches[0]


# ==================================================
# 4. CAP NHAT LOI THOAI VAO SQL SERVER
# ==================================================

def update_video(source):

    with closing(get_connection()) as connection:

        connection.autocommit = False

        try:

            with closing(connection.cursor()) as cursor:

                # ----------------------------------
                # TIM BAN GHI VIDEO
                # ----------------------------------

                row, existing = find_admin_video(
                    cursor
                )

                video_id = int(row[0])
                lesson_id = int(row[1])
                title = row[2]
                order = row[3]
                old_json = row[4]

                old_sentences = existing.get(
                    "sentences", []
                )

                if not isinstance(old_sentences, list):
                    raise ValueError(
                        "JSON cu co sentences khong hop le."
                    )

                print(
                    "\n===== VIDEO TIM THAY TRONG ADMIN ====="
                )

                print("MaNoiDung:", video_id)
                print("MaKhoaHoc:", MA_KHOA_HOC)
                print("MaBaiHoc:", lesson_id)
                print("ThuTu:", order)
                print("TieuDe:", title)
                print("YouTube:", VIDEO_ID)
                print("So doan cu:", len(old_sentences))
                print("So doan moi:", EXPECTED_COUNT)

                # ----------------------------------
                # KHONG GHI DE NEU DA CO LOI THOAI
                # ----------------------------------

                if old_sentences:
                    raise RuntimeError(
                        "Video da co loi thoai trong SQL.\n"
                        "Dung lai de tranh ghi de du lieu."
                    )

                # ----------------------------------
                # SAO LUU JSON CU
                # ----------------------------------

                BACKUP_DIR.mkdir(
                    parents=True,
                    exist_ok=True
                )

                stamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S_%f"
                )

                backup_file = (
                    BACKUP_DIR
                    / f"video4_before_update_{stamp}.json"
                )

                backup_file.write_text(
                    old_json,
                    encoding="utf-8"
                )

                print("\n===== SAO LUU =====")
                print("Backup:", backup_file)

                # ----------------------------------
                # GHEP 396 DOAN VAO JSON CU
                # ----------------------------------

                document = existing.copy()

                document["sentences"] = (
                    source["sentences"]
                )

                # Giu nguyen metadata va YouTube ID
                # cua ban ghi da tao tren Admin.

                json_text = json.dumps(
                    document,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    allow_nan=False
                )

                print("\n===== XAC NHAN =====")
                print("Video:", VIDEO_ID)
                print("MaNoiDung:", video_id)
                print("So doan:", EXPECTED_COUNT)

                confirm = input(
                    "\nNhap CAPNHAT de luu SQL: "
                ).strip()

                if confirm != "CAPNHAT":

                    connection.rollback()

                    print(
                        "Da huy. SQL khong thay doi."
                    )

                    return

                # ----------------------------------
                # UPDATE NVARCHAR(MAX)
                # ----------------------------------

                # Chia chuoi Unicode thanh cac phan
                # nho de truyen qua pyodbc.
                chunks = [
                    json_text[i:i + 800]
                    for i in range(0, len(json_text), 800)
                ]

                # SQL Server toi da 2100 tham so.
                # Tru 2 tham so cho WHERE.
                if len(chunks) > 2000:
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

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "UPDATE khong dung 1 ban ghi. "
                        f"rowcount={cursor.rowcount}"
                    )

                # ----------------------------------
                # DOC LAI DU LIEU TRUOC COMMIT
                # ----------------------------------

                cursor.execute(
                    """
                    SELECT
                        MaBaiHoc,
                        ThuTu,
                        NoiDung

                    FROM dbo.NoiDungBaiHoc

                    WHERE MaNoiDung = ?
                      AND LoaiNoiDung = 'nghe'
                    """,
                    video_id
                )

                saved_row = cursor.fetchone()

                if saved_row is None:
                    raise RuntimeError(
                        "Khong tim thay video sau UPDATE."
                    )

                saved = json.loads(saved_row[2])

                if saved != document:
                    raise RuntimeError(
                        "JSON doc lai tu SQL khong khop."
                    )

                if (
                    int(saved_row[0]) != lesson_id
                    or saved_row[1] != order
                ):
                    raise RuntimeError(
                        "MaBaiHoc hoac ThuTu da thay doi."
                    )

                if len(saved["sentences"]) != EXPECTED_COUNT:
                    raise RuntimeError(
                        "So doan sau UPDATE khong bang 396."
                    )

                # ----------------------------------
                # COMMIT
                # ----------------------------------

                connection.commit()

                print("\n===== UPDATE THANH CONG =====")
                print("MaNoiDung:", video_id)
                print("MaKhoaHoc:", MA_KHOA_HOC)
                print("MaBaiHoc:", lesson_id)
                print("ThuTu:", order)
                print("YouTube:", VIDEO_ID)
                print("So doan:", len(saved["sentences"]))
                print("Doc lai SQL: OK")
                print("COMMIT: THANH CONG")

        except Exception:

            connection.rollback()

            print(
                "\nCO LOI - DA ROLLBACK SQL."
            )

            raise


# ==================================================
# 5. MAIN
# ==================================================

if __name__ == "__main__":

    print(
        "===== SHADOWING HSK3 - UPDATE VIDEO 4 ====="
    )

    source = load_source()

    print("File:", SOURCE)

    print(
        "So doan hop le:",
        len(source["sentences"])
    )

    update_video(source)
