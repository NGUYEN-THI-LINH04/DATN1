
import sys
import json
import math

from pathlib import Path
from contextlib import closing


# ==================================================
# 1. CAU HINH HSK4 VIDEO 3
# ==================================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "shadowing" / "hsk4"

SOURCE = (
    BASE
    / "data"
    / "processed"
    / "video3_translated_full.json"
)

VIDEO_ID = "KIMnS86vgPE"

MA_KHOA_HOC = 4
MA_BAI_HOC = 2057

EXPECTED_COUNT = 312

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
        raise ValueError("JSON khong hop le.")

    if data.get("module") != "shadowing":
        raise ValueError(
            "Sai module, phai la shadowing."
        )

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError(
            "Sai YouTube ID cua video 3."
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
                f"Doan {i} khong phai object."
            )

        # Kiem tra du chu Han, pinyin, tieng Viet
        for field in (
            "hanzi",
            "pinyin",
            "vi"
        ):

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

        if (
            i > 1
            and start < previous_end - 0.001
        ):
            raise ValueError(
                f"Timestamp chong nhau o doan {i}."
            )

        previous_end = end

    print("\n===== KIEM TRA JSON =====")
    print("YouTube:", VIDEO_ID)
    print("So doan:", len(sentences))
    print("Chu Han + Pinyin + Tieng Viet: OK")
    print("Timestamp: OK")
    print("JSON: OK")

    return data


# ==================================================
# 3. KIEM TRA MA BAI HOC THUOC HSK4
# ==================================================

def check_lesson(cursor):

    cursor.execute(
        """
        SELECT
            MaKhoaHoc,
            TieuDe
        FROM dbo.BaiHoc
        WHERE MaBaiHoc = ?
        """,
        MA_BAI_HOC
    )

    row = cursor.fetchone()

    if row is None:
        raise RuntimeError(
            f"Khong ton tai MaBaiHoc={MA_BAI_HOC}."
        )

    if int(row[0]) != MA_KHOA_HOC:
        raise RuntimeError(
            f"MaBaiHoc={MA_BAI_HOC} "
            "khong thuoc khoa HSK4."
        )

    print("\n===== KIEM TRA BAI HOC =====")
    print("MaKhoaHoc:", row[0])
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

        raw_json = row[4]

        if not raw_json:
            continue

        try:
            existing = json.loads(raw_json)
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
            "Khong tim thay video 3 trong Admin.\n"
            "Kiem tra xem video KIMnS86vgPE "
            "da them thanh cong hay chua."
        )

    if len(matches) > 1:
        raise RuntimeError(
            "Phat hien nhieu video cung YouTube ID.\n"
            "Da dung de tranh cap nhat nham."
        )

    row, existing = matches[0]

    if int(row[1]) != MA_BAI_HOC:
        raise RuntimeError(
            f"Video dang thuoc MaBaiHoc={row[1]}, "
            f"khong phai {MA_BAI_HOC}.\n"
            "Khong cap nhat khi ma bai hoc sai."
        )

    return row, existing


# ==================================================
# 5. CAP NHAT VAO SQL SERVER
# ==================================================

def update_video(source):

    with closing(get_connection()) as connection:

        connection.autocommit = False

        try:

            with closing(connection.cursor()) as cursor:

                # ----------------------------------
                # A. KIEM TRA BAI HOC
                # ----------------------------------

                check_lesson(cursor)

                # ----------------------------------
                # B. TIM VIDEO ADMIN
                # ----------------------------------

                row, existing = find_admin_video(
                    cursor
                )

                ma_noi_dung = int(row[0])
                ma_bai_hoc = int(row[1])
                tieu_de = row[2]
                thu_tu = row[3]

                old_sentences = existing.get(
                    "sentences", []
                )

                if not isinstance(
                    old_sentences, list
                ):
                    raise RuntimeError(
                        "sentences trong SQL "
                        "khong hop le."
                    )

                print(
                    "\n===== VIDEO TIM THAY ====="
                )

                print(
                    "MaNoiDung:",
                    ma_noi_dung
                )

                print(
                    "MaKhoaHoc:",
                    MA_KHOA_HOC
                )

                print(
                    "MaBaiHoc:",
                    ma_bai_hoc
                )

                print("ThuTu:", thu_tu)
                print("TieuDe:", tieu_de)
                print("YouTube:", VIDEO_ID)

                print(
                    "So doan cu:",
                    len(old_sentences)
                )

                print(
                    "So doan moi:",
                    EXPECTED_COUNT
                )

                # ----------------------------------
                # C. KHONG GHI DE DU LIEU CU
                # ----------------------------------

                if len(old_sentences) > 0:
                    raise RuntimeError(
                        "Video da co sentences trong SQL.\n"
                        "Da dung de tranh ghi de."
                    )

                # ----------------------------------
                # D. GIU NGUYEN JSON ADMIN
                # ----------------------------------

                document = existing.copy()

                # Chi thay danh sach cau thoai
                document["sentences"] = (
                    source["sentences"]
                )

                json_text = json.dumps(
                    document,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    allow_nan=False
                )

                # ----------------------------------
                # E. XAC NHAN TRUOC UPDATE
                # ----------------------------------

                print(
                    "\n===== XAC NHAN CAP NHAT ====="
                )

                print(
                    "MaNoiDung:",
                    ma_noi_dung
                )
                print(
                    "MaBaiHoc:",
                    ma_bai_hoc
                )
                print(
                    "YouTube:",
                    VIDEO_ID
                )
                print(
                    "So doan:",
                    EXPECTED_COUNT
                )

                print(
                    "Khong thay doi cac video khac."
                )

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
                # F. CHIA JSON UNICODE THANH CHUNK
                # ----------------------------------

                chunks = [
                    json_text[i:i + 800]
                    for i in range(
                        0,
                        len(json_text),
                        800
                    )
                ]

                # SQL Server gioi han
                # toi da 2100 parameters.
                if len(chunks) + 3 > 2100:
                    raise RuntimeError(
                        "JSON qua lon de UPDATE."
                    )

                expression = " + ".join(
                    "CONVERT(NVARCHAR(MAX), ?)"
                    for _ in chunks
                )

                # ----------------------------------
                # G. UPDATE DUNG 1 BAN GHI
                # ----------------------------------

                sql = f"""
                    UPDATE dbo.NoiDungBaiHoc
                    SET NoiDung = {expression}
                    WHERE MaNoiDung = ?
                      AND MaBaiHoc = ?
                      AND LoaiNoiDung = 'nghe'
                      AND JSON_VALUE(
                          NoiDung,
                          '$.youtube_id'
                      ) = ?
                """

                cursor.execute(
                    sql,
                    *chunks,
                    ma_noi_dung,
                    ma_bai_hoc,
                    VIDEO_ID
                )

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "UPDATE khong dung 1 ban ghi. "
                        f"rowcount={cursor.rowcount}"
                    )

                # ----------------------------------
                # H. DOC LAI TRUOC COMMIT
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
                    ma_noi_dung
                )

                saved_row = cursor.fetchone()

                if saved_row is None:
                    raise RuntimeError(
                        "Khong tim thay video "
                        "sau UPDATE."
                    )

                saved = json.loads(
                    saved_row[2]
                )

                # Kiem tra lai toan bo JSON
                if saved != document:
                    raise RuntimeError(
                        "JSON doc lai khong "
                        "khop JSON can luu."
                    )

                if (
                    int(saved_row[0]) != ma_bai_hoc
                    or saved_row[1] != thu_tu
                ):
                    raise RuntimeError(
                        "MaBaiHoc hoac ThuTu "
                        "bi thay doi."
                    )

                if (
                    saved.get("module") != "shadowing"
                    or saved.get("youtube_id") != VIDEO_ID
                ):
                    raise RuntimeError(
                        "Module hoac YouTube ID "
                        "khong khop."
                    )

                saved_sentences = saved.get(
                    "sentences"
                )

                if (
                    not isinstance(
                        saved_sentences, list
                    )
                    or len(saved_sentences)
                    != EXPECTED_COUNT
                ):
                    raise RuntimeError(
                        "So doan sau UPDATE "
                        "khong bang 312."
                    )

                # ----------------------------------
                # I. COMMIT
                # ----------------------------------

                connection.commit()

                print(
                    "\n===== UPDATE THANH CONG ====="
                )

                print(
                    "MaNoiDung:",
                    ma_noi_dung
                )

                print(
                    "MaKhoaHoc:",
                    MA_KHOA_HOC
                )

                print(
                    "MaBaiHoc:",
                    ma_bai_hoc
                )

                print(
                    "ThuTu:",
                    thu_tu
                )

                print(
                    "YouTube:",
                    VIDEO_ID
                )

                print(
                    "So doan:",
                    len(saved_sentences)
                )

                print("Doc lai SQL: OK")
                print("COMMIT: THANH CONG")

        except Exception:

            connection.rollback()

            print(
                "\nCO LOI - DA ROLLBACK SQL."
            )

            raise


# ==================================================
# 6. MAIN
# ==================================================

if __name__ == "__main__":

    print(
        "===== SHADOWING HSK4 - UPDATE VIDEO 3 ====="
    )

    source = load_source()

    update_video(source)
