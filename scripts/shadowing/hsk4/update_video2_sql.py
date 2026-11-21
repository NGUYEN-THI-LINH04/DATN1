
import sys
import json
import math

from pathlib import Path
from contextlib import closing


# ==================================================
# 1. CAU HINH HSK4 - VIDEO 2
# ==================================================

ROOT = Path(r"D:\DATN1")
BASE = ROOT / "scripts" / "shadowing" / "hsk4"

SOURCE = (
    BASE / "data" / "processed"
    / "video2_translated_full.json"
)

VIDEO_ID = "rTOwIJeG7sM"

MA_KHOA_HOC = 4
MA_BAI_HOC = 2051

EXPECTED_COUNT = 528

sys.path.insert(0, str(ROOT))

from database import get_connection


# ==================================================
# 2. DOC VA KIEM TRA JSON DA XU LY
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
            "Sai YouTube ID cua HSK4 video 2."
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

    print("\n===== KIEM TRA JSON =====")
    print("YouTube:", VIDEO_ID)
    print("So doan:", len(sentences))
    print("JSON: OK")

    return data


# ==================================================
# 3. KIEM TRA BAI HOC THUOC HSK4
# ==================================================

def check_lesson(cursor):

    cursor.execute(
        """
        SELECT MaKhoaHoc, TieuDe
        FROM dbo.BaiHoc
        WHERE MaBaiHoc = ?
        """,
        MA_BAI_HOC
    )

    row = cursor.fetchone()

    if row is None:
        raise RuntimeError(
            f"MaBaiHoc {MA_BAI_HOC} khong ton tai."
        )

    if int(row[0]) != MA_KHOA_HOC:
        raise RuntimeError(
            "MaBaiHoc khong thuoc HSK4."
        )

    print("\n===== KIEM TRA BAI HOC =====")
    print("MaKhoaHoc:", MA_KHOA_HOC)
    print("MaBaiHoc:", MA_BAI_HOC)
    print("TieuDe:", row[1])


# ==================================================
# 4. TIM VIDEO DA THEM TREN ADMIN
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

    if not matches:
        raise RuntimeError(
            "Khong tim thay video HSK4 so 2 "
            "trong SQL Server.\n"
            "Hay kiem tra video da duoc them "
            "thanh cong qua Admin chua."
        )

    if len(matches) != 1:
        raise RuntimeError(
            "Co nhieu video HSK4 trung YouTube ID. "
            "Khong cap nhat."
        )

    row, existing = matches[0]

    if int(row[1]) != MA_BAI_HOC:
        raise RuntimeError(
            f"Video dang thuoc MaBaiHoc={row[1]}, "
            f"khong phai {MA_BAI_HOC}.\n"
            "Can kiem tra truoc khi cap nhat."
        )

    return row, existing


# ==================================================
# 5. CAP NHAT SQL SERVER
# ==================================================

def update_video(source):

    with closing(get_connection()) as connection:

        connection.autocommit = False

        try:
            with closing(connection.cursor()) as cursor:

                # ----------------------------------
                # KIEM TRA MA BAI HOC
                # ----------------------------------

                check_lesson(cursor)

                # ----------------------------------
                # TIM VIDEO
                # ----------------------------------

                row, existing = find_admin_video(
                    cursor
                )

                video_id = int(row[0])
                lesson_id = int(row[1])
                title = row[2]
                order = row[3]

                old_sentences = existing.get(
                    "sentences", []
                )

                if not isinstance(old_sentences, list):
                    raise ValueError(
                        "JSON trong SQL co sentences "
                        "khong hop le."
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
                # CHAN GHI DE NOI DUNG DA CO
                # ----------------------------------

                if old_sentences:
                    raise RuntimeError(
                        "Video da co loi thoai trong SQL.\n"
                        "Dung lai de tranh ghi de du lieu."
                    )

                # ----------------------------------
                # GHEP 528 DOAN VAO JSON ADMIN
                # ----------------------------------

                document = existing.copy()

                document["sentences"] = (
                    source["sentences"]
                )

                # Giu nguyen cac thong tin khac
                # cua video da tao tren Admin.

                json_text = json.dumps(
                    document,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    allow_nan=False
                )

                print("\n===== XAC NHAN CAP NHAT =====")
                print("MaNoiDung:", video_id)
                print("MaBaiHoc:", lesson_id)
                print("YouTube:", VIDEO_ID)
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

                # Chia chuoi Unicode thanh tung phan
                # nho de truyen qua pyodbc.
                chunks = [
                    json_text[i:i + 800]
                    for i in range(0, len(json_text), 800)
                ]

                # SQL Server gioi han 2100 tham so.
                # Can 3 tham so cho WHERE.
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
                        "JSON doc lai khong khop JSON nguon."
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
                        "So doan trong SQL khong bang 528."
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

            print("\nCO LOI - DA ROLLBACK SQL.")

            raise


# ==================================================
# 6. MAIN
# ==================================================

if __name__ == "__main__":

    print(
        "===== SHADOWING HSK4 - UPDATE VIDEO 2 ====="
    )

    source = load_source()

    update_video(source)
