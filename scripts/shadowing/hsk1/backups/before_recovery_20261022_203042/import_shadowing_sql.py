
import argparse
import json
import math
import sys
from pathlib import Path
from datetime import datetime
from contextlib import closing

import pyodbc


# ============================================
# CAU HINH CHUNG
# ============================================

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from database import get_connection

SCRIPT_DIR = Path(__file__).resolve().parent
BACKUP_DIR = SCRIPT_DIR / "backups"


# ============================================
# 1. DOC VA KIEM TRA JSON
# ============================================

def load_json(path, youtube_id, duration=None):
    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay JSON: {path}"
        )

    data = json.loads(
        path.read_text(encoding="utf-8-sig")
    )

    if not isinstance(data, dict):
        raise ValueError("JSON phai la object")

    if data.get("module") != "shadowing":
        raise ValueError("Module khong phai shadowing")

    if data.get("youtube_id") != youtube_id:
        raise ValueError("YouTube ID khong khop")

    sentences = data.get("sentences")

    if not isinstance(sentences, list) or not sentences:
        raise ValueError("Danh sach sentences rong")

    previous_end = -1.0
    cleaned = []

    for index, item in enumerate(sentences, 1):
        for key in ("start", "end", "hanzi", "pinyin", "vi"):
            if key not in item:
                raise ValueError(
                    f"Cau {index} thieu {key}"
                )

        if any(
            not isinstance(item[k], str)
            or not item[k].strip()
            for k in ("hanzi", "pinyin", "vi")
        ):
            raise ValueError(
                f"Cau {index} thieu Hanzi/Pinyin/Viet"
            )

        if (
            isinstance(item["start"], bool)
            or isinstance(item["end"], bool)
        ):
            raise ValueError(
                f"Cau {index}: timestamp khong hop le"
            )

        start = float(item["start"])
        end = float(item["end"])

        if not math.isfinite(start) or not math.isfinite(end):
            raise ValueError(
                f"Cau {index}: timestamp khong huu han"
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Cau {index}: timestamp sai"
            )

        if start < previous_end - 0.001:
            raise ValueError(
                f"Cau {index}: chong thoi gian"
            )

        if duration is not None and end > duration + 1.0:
            raise ValueError(
                f"Cau {index} vuot thoi luong video"
            )

        cleaned.append({
            "start": round(start, 3),
            "end": round(end, 3),
            "hanzi": item["hanzi"].strip(),
            "pinyin": item["pinyin"].strip(),
            "vi": item["vi"].strip()
        })

        previous_end = end

    return cleaned


# ============================================
# 2. SAO LUU DU LIEU CU
# ============================================

def backup_original(content_id, original_json):
    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    path = BACKUP_DIR / (
        f"shadowing_{content_id}_before_{timestamp}.json"
    )

    path.write_text(
        original_json,
        encoding="utf-8"
    )

    return path


# ============================================
# 3. CHUYEN UNICODE CHO SQL SERVER
# Giu dung cach da thanh cong voi Emily
# ============================================

def encode_sql_unicode(text):
    return pyodbc.Binary(
        text.encode("utf-16le")
    )


# ============================================
# 4. NHAP DU LIEU
# ============================================

def import_shadowing(
    content_id,
    youtube_id,
    input_file,
    duration=None,
    expected=None,
    apply=False
):
    sentences = load_json(
        input_file,
        youtube_id,
        duration
    )

    if expected is not None and len(sentences) != expected:
        raise ValueError(
            f"Yeu cau {expected} cau, "
            f"nhung co {len(sentences)} cau"
        )

    print("\n===== SHADOWING SQL IMPORT =====")
    print("MaNoiDung:", content_id)
    print("YouTube:", youtube_id)
    print("So cau:", len(sentences))
    print("File:", input_file)

    print("\n===== 3 CAU DAU =====")
    for item in sentences[:3]:
        print(
            f"{item['start']:.2f}s | "
            f"{item['hanzi']} | {item['vi']}"
        )

    with closing(get_connection()) as conn:
        conn.autocommit = False

        with closing(conn.cursor()) as cursor:
            try:
                lock = (
                    "WITH (UPDLOCK, HOLDLOCK)"
                    if apply
                    else ""
                )

                cursor.execute(
                    f"""
                    SELECT
                        MaNoiDung,
                        TieuDe,
                        NoiDung
                    FROM dbo.NoiDungBaiHoc
                    {lock}
                    WHERE MaNoiDung = ?
                      AND LoaiNoiDung = 'nghe'
                    """,
                    content_id
                )

                row = cursor.fetchone()

                if row is None:
                    raise ValueError(
                        "Khong tim thay bai trong SQL"
                    )

                original_json = row[2]

                if not isinstance(original_json, str):
                    raise ValueError(
                        "NoiDung trong SQL khong phai JSON chuoi"
                    )

                original_data = json.loads(original_json)

                if not isinstance(original_data, dict):
                    raise ValueError(
                        "JSON SQL khong hop le"
                    )

                if original_data.get("module") != "shadowing":
                    raise ValueError(
                        "Ban ghi khong thuoc Shadowing"
                    )

                if original_data.get("youtube_id") != youtube_id:
                    raise ValueError(
                        "YouTube ID trong SQL khong khop"
                    )

                if not isinstance(
                    original_data.get("sentences", []),
                    list
                ):
                    raise ValueError(
                        "Danh sach cau trong SQL khong hop le"
                    )

                if original_data.get("sentences"):
                    raise ValueError(
                        "Bai da co phu de. "
                        "Dung de tranh ghi de."
                    )

                print("\n===== DU LIEU SQL HIEN TAI =====")
                print("Tieu de:", row[1])
                print("Module:", original_data["module"])
                print("YouTube ID:", original_data["youtube_id"])
                print(
                    "So cau cu:",
                    len(original_data.get("sentences", []))
                )

                # Giu nguyen cac truong du lieu goc
                updated_data = dict(original_data)

                updated_data["sentences"] = sentences

                updated_data["subtitle_source"] = {
                    "type": "supadata_timed_transcript_reviewed",
                    "youtube_id": youtube_id,
                    "sentence_count": len(sentences)
                }

                updated_json = json.dumps(
                    updated_data,
                    ensure_ascii=False
                )

                if not apply:
                    print("\n===== KIEM TRA THANH CONG =====")
                    print("CHUA CAP NHAT SQL SERVER")
                    conn.rollback()
                    return

                # Sao luu JSON cu truoc khi UPDATE
                backup_path = backup_original(
                    content_id,
                    original_json
                )

                print("\nDa sao luu:", backup_path)

                # Truyen UTF-16LE qua VARBINARY
                # Tranh loi 4189 nhu bai Emily
                unicode_payload = encode_sql_unicode(
                    updated_json
                )

                cursor.execute(
                    """
                    UPDATE dbo.NoiDungBaiHoc
                    SET NoiDung = CONVERT(
                        NVARCHAR(MAX),
                        CAST(? AS VARBINARY(MAX))
                    )
                    WHERE MaNoiDung = ?
                      AND LoaiNoiDung = 'nghe'
                    """,
                    unicode_payload,
                    content_id
                )

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "UPDATE khong dung 1 ban ghi"
                    )

                # Doc lai truoc khi commit
                cursor.execute(
                    """
                    SELECT NoiDung
                    FROM dbo.NoiDungBaiHoc
                    WHERE MaNoiDung = ?
                      AND LoaiNoiDung = 'nghe'
                    """,
                    content_id
                )

                verify_row = cursor.fetchone()

                if verify_row is None:
                    raise RuntimeError(
                        "Khong doc duoc du lieu sau UPDATE"
                    )

                saved = json.loads(verify_row[0])

                if (
                    saved.get("module") != "shadowing"
                    or saved.get("youtube_id") != youtube_id
                    or saved.get("sentences") != sentences
                ):
                    raise RuntimeError(
                        "Du lieu xac minh khong khop"
                    )

                conn.commit()

                print("\n===== CAP NHAT THANH CONG =====")
                print("MaNoiDung:", content_id)
                print("YouTube:", youtube_id)
                print("So cau:", len(sentences))
                print("Backup:", backup_path)

            except Exception:
                conn.rollback()
                raise


# ============================================
# 5. CHUONG TRINH CHINH
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description="Nhap phu de Shadowing vao SQL Server"
    )

    parser.add_argument(
        "--ma-noi-dung",
        type=int,
        required=True
    )

    parser.add_argument(
        "--youtube-id",
        required=True
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True
    )

    parser.add_argument(
        "--duration-seconds",
        type=float,
        default=None
    )

    parser.add_argument(
        "--expected",
        type=int,
        default=None
    )

    parser.add_argument(
        "--apply",
        action="store_true"
    )

    args = parser.parse_args()

    if args.ma_noi_dung <= 0:
        parser.error("MaNoiDung phai lon hon 0")

    if (
        args.duration_seconds is not None
        and (
            not math.isfinite(args.duration_seconds)
            or args.duration_seconds <= 0
        )
    ):
        parser.error("Thoi luong video khong hop le")

    import_shadowing(
        content_id=args.ma_noi_dung,
        youtube_id=args.youtube_id,
        input_file=args.input,
        duration=args.duration_seconds,
        expected=args.expected,
        apply=args.apply
    )


if __name__ == "__main__":
    main()
