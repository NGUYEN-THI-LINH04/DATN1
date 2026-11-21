
import sys
import json
import math

from pathlib import Path
from datetime import datetime
from contextlib import closing


# ==================================================
# 1. CAU HINH HSK3 - VIDEO 5
# ==================================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "shadowing" / "hsk3"

SOURCE = (
    BASE / "data" / "processed"
    / "video5_translated_full.json"
)

BACKUP_DIR = BASE / "data" / "backup"

VIDEO_ID = "2EythZkR8w8"

MA_KHOA_HOC = 3

EXPECTED_COUNT = 146

sys.path.insert(0, str(ROOT))

from database import get_connection


# ==================================================
# 2. DOC VA KIEM TRA JSON
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
        raise ValueError("JSON khong hop le.")

    if data.get("module") != "shadowing":
        raise ValueError("Sai module Shadowing.")

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError(
            "Sai YouTube ID cua HSK3 video 5."
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

        except (KeyError, ValueError, TypeError):
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

    print("\n===== KIEM TRA FILE JSON =====")
    print("YouTube:", VIDEO_ID)
    print("So doan:", len(sentences))
    print("JSON: OK")

    return data


# ==================================================
# 3. TIM VIDEO DA THEM QUA ADMIN
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
            "CHUA TIM THAY VIDEO 5 TRONG ADMIN.\n"
            "Hay them video HSK3 truoc:\n"
            f"https://youtu.be/{VIDEO_ID}"
        )

    if len(matches) > 1:
        raise RuntimeError(
            "Co nhieu video HSK3 trung YouTube ID.\n"
            "Dung lai de kiem tra SQL."
        )

    return matches[0]


# ==================================================
# 4. CAP NHAT 146 DOAN VAO SQL SERVER
# ==================================================

def update_video(source):

    with closing(get_connection()) as connection:

        connection.autocommit = False

        try:
            with closing(connection.cursor()) as cursor:

                # ----------------------------------
                # TIM VIDEO TRONG SQL
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
                # KHONG GHI DE VIDEO DA CO LOI THOAI
                # ----------------------------------

                if old_sentences:
                    raise RuntimeError(
                        "Video 5 da co loi thoai trong SQL.\n"
                        "Khong ghi de de bao ve du lieu."
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
                    / f"video5_before_update_{stamp}.json"
                )

                backup_file.write_text(
                    old_json,
                    encoding="utf-8"
                )

                print("\n===== SAO LUU =====")
                print("Backup:", backup_file)

                # ----------------------------------
                # GHEP LOI THOAI MOI
                # ----------------------------------

                document = existing.copy()

                document["sentences"] = (
                    source["sentences"]
                )

                # Giu nguyen cac metadata khac
                # cua video da them qua Admin.

                json_text = json.dumps(
                    document,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    allow_nan=False
                )

                print("\n===== XAC NHAN CAP NHAT =====")
                print("Video:", VIDEO_ID)
                print("MaNoiDung:", video_id)
                print("So doan moi:", EXPECTED_COUNT)

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

                # Chia JSON Unicode de truyen qua
                # pyodbc ma khong mat chu Han.
                chunks = [
                    json_text[i:i + 800]
                    for i in range(0, len(json_text), 800)
                ]

                # SQL Server gioi han 2100 tham so.
                if len(chunks) + 3 > 2100:
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
                      AND JSON_VALUE(
                          NoiDung, '$.youtube_id'
                      ) = ?
                """

                cursor.execute(
                    sql,
                    *chunks,
                    video_id,
                    lesson_id,
                    VIDEO_ID
                )

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "UPDATE khong dung 1 ban ghi. "
                        f"rowcount={cursor.rowcount}"
                    )

                # ----------------------------------
                # DOC LAI TRUOC KHI COMMIT
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

                if (
                    saved.get("module") != "shadowing"
                    or saved.get("youtube_id") != VIDEO_ID
                ):
                    raise RuntimeError(
                        "Module hoac YouTube ID bi sai."
                    )

                if len(saved["sentences"]) != EXPECTED_COUNT:
                    raise RuntimeError(
                        "So doan trong SQL khong bang 146."
                    )

                # ----------------------------------
                # COMMIT KHI TAT CA DEU DUNG
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
        "===== SHADOWING HSK3 - UPDATE VIDEO 5 ====="
    )

    source = load_source()

    update_video(source)
