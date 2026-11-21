
# -*- coding: utf-8 -*-
"""
BUOC 65 - TAO AUDIO HSK3 BANG ELEVENLABS

Dua tren quy trinh audio HSK2 da thanh cong.

PREVIEW (khong goi API, khong ghi SQL):
python scripts/hsk3/29_generate_hsk3_audio_elevenlabs.py --preview

TEST (mac dinh 5 tu + 5 chu):
python scripts/hsk3/29_generate_hsk3_audio_elevenlabs.py

FULL:
python scripts/hsk3/29_generate_hsk3_audio_elevenlabs.py --full

Khong sua audio HSK1/HSK2.
Khong tao lai audio da lien ket va con file hop le.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from contextlib import closing
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

COURSE_ID = 3
EXPECTED_VOCAB = 973
EXPECTED_HANZI = 300

MODEL_ID = "eleven_v4"
OUTPUT_FORMAT = "mp3_44100_128"
MIN_VALID_MP3_BYTES = 500

VOCAB_DIR = ROOT / "static/audio/hsk3/tu_vung"
HANZI_DIR = ROOT / "static/audio/hsk3/chu_han"

load_dotenv(ROOT / ".env", interpolate=False)

API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "").strip()


def clean(value):
    return str(value).strip() if value is not None else ""


def fail(message):
    raise RuntimeError(message)


def valid_mp3(path):
    return (
        path.is_file()
        and path.stat().st_size >= MIN_VALID_MP3_BYTES
    )


def project_file(public_path):
    value = clean(public_path).replace("\\", "/")

    if value.startswith("/static/"):
        value = value[1:]

    if not value.startswith("static/"):
        return None

    root = ROOT.resolve()
    path = (ROOT / value).resolve()

    if not path.is_relative_to(root):
        return None

    return path


def generate_mp3(client, text, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    temp = path.with_suffix(path.suffix + ".part")

    if path.exists():
        fail(f"Khong ghi de file MP3 cu: {path}")

    if temp.exists():
        fail(f"File tam dang ton tai: {temp}")

    try:
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
            output_format=OUTPUT_FORMAT,
        )

        with temp.open("xb") as file:
            for chunk in audio:
                if chunk:
                    file.write(chunk)

        if not valid_mp3(temp):
            fail(f"MP3 khong hop le: {temp}")

        temp.rename(path)

    finally:
        if temp.exists():
            temp.unlink()


def load_vocab(cursor):
    cursor.execute("""
        SELECT
            tv.MaTuVung,
            tv.ChuHan,
            tv.PhienAm,
            tv.MaAmThanh,
            bh.SoThuTuBai,
            tvbh.ThuTu
        FROM dbo.TuVungBaiHoc AS tvbh
        JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc = tvbh.MaBaiHoc
        JOIN dbo.TuVung AS tv
            ON tv.MaTuVung = tvbh.MaTuVung
        WHERE bh.MaKhoaHoc = ?
        ORDER BY
            bh.SoThuTuBai,
            tvbh.ThuTu,
            tv.MaTuVung;
    """, COURSE_ID)

    items = []
    seen = set()

    for r in cursor.fetchall():
        item_id = int(r[0])

        if item_id in seen:
            fail(
                f"MaTuVung={item_id} bi lien ket "
                "nhieu lan trong HSK3."
            )

        seen.add(item_id)

        items.append({
            "id": item_id,
            "text": clean(r[1]),
            "pinyin": clean(r[2]),
            "media_id": r[3],
            "lesson": int(r[4]),
        })

    return items


def load_hanzi(cursor):
    cursor.execute("""
        SELECT
            ch.MaChuHan,
            ch.KyTu,
            ch.Pinyin,
            ch.MaTep,
            bh.SoThuTuBai
        FROM dbo.ChuHan AS ch
        JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc = ch.MaBaiHoc
        WHERE bh.MaKhoaHoc = ?
        ORDER BY
            bh.SoThuTuBai,
            ch.ThuTu,
            ch.MaChuHan;
    """, COURSE_ID)

    return [
        {
            "id": int(r[0]),
            "text": clean(r[1]),
            "pinyin": clean(r[2]),
            "media_id": r[3],
            "lesson": int(r[4]),
        }
        for r in cursor.fetchall()
    ]


def get_media(cursor, media_id):
    cursor.execute("""
        SELECT
            MaTep,
            LoaiTep,
            DuongDanTep,
            LoiThoai
        FROM dbo.TepDaPhuongTien
        WHERE MaTep = ?;
    """, media_id)

    return cursor.fetchone()


def audio_target(kind, item_id):
    if kind == "vocab":
        name = f"tv_{item_id:04d}.mp3"
        return (
            VOCAB_DIR / name,
            "/static/audio/hsk3/tu_vung/" + name,
        )

    name = f"ch_{item_id:04d}.mp3"
    return (
        HANZI_DIR / name,
        "/static/audio/hsk3/chu_han/" + name,
    )


def plan_item(cursor, kind, item):
    text = item["text"]
    item_id = item["id"]
    media_id = item["media_id"]

    if not text or not item["pinyin"]:
        fail(
            f"{kind} ID={item_id}: "
            "thieu chu Han hoac Pinyin."
        )

    output_file, public_path = audio_target(
        kind, item_id
    )

    if media_id is not None:
        media = get_media(cursor, int(media_id))

        if media is None:
            fail(
                f"{kind} ID={item_id}: "
                f"MaTep={media_id} khong ton tai."
            )

        if clean(media[1]) != "am_thanh":
            fail(
                f"{kind} ID={item_id}: "
                "media khong phai am_thanh."
            )

        linked_file = project_file(media[2])

        if linked_file is None:
            fail(
                f"{kind} ID={item_id}: "
                "duong dan media khong an toan."
            )

        # Không động vào file HSK1/HSK2 bị thiếu:
        # để tránh sửa audio cấp khác ngoài ý muốn.
        if valid_mp3(linked_file):
            return "skip_linked", linked_file, public_path

        return "missing_linked", linked_file, public_path

    if valid_mp3(output_file):
        return "reuse_file", output_file, public_path

    if output_file.exists():
        return "invalid_file", output_file, public_path

    return "generate", output_file, public_path


def insert_media_and_link(
    conn, cursor, kind, item, public_path
):
    title = (
        "Phat am tu vung HSK3: "
        if kind == "vocab"
        else "Phat am chu Han HSK3: "
    ) + item["text"]

    try:
        cursor.execute("""
            INSERT INTO dbo.TepDaPhuongTien
            (
                LoaiTep,
                DuongDanTep,
                TieuDe,
                LoiThoai,
                MaNguon
            )
            OUTPUT INSERTED.MaTep
            VALUES
            (
                'am_thanh', ?, ?, ?, NULL
            );
        """,
            public_path,
            title,
            item["text"],
        )

        media_id = int(cursor.fetchone()[0])

        if kind == "vocab":
            cursor.execute("""
                UPDATE dbo.TuVung
                SET MaAmThanh = ?
                WHERE MaTuVung = ?
                  AND MaAmThanh IS NULL;
            """, media_id, item["id"])
        else:
            cursor.execute("""
                UPDATE dbo.ChuHan
                SET MaTep = ?
                WHERE MaChuHan = ?
                  AND MaTep IS NULL;
            """, media_id, item["id"])

        if cursor.rowcount != 1:
            fail(
                f"Khong gan duoc audio: "
                f"{kind} ID={item['id']}"
            )

        conn.commit()
        return media_id

    except Exception:
        conn.rollback()
        raise


def process_item(conn, cursor, client, kind, item):
    status, file, public_path = plan_item(
        cursor, kind, item
    )

    print(
        f"  ID={item['id']} "
        f"Bai={item['lesson']} "
        f"{item['text']} "
        f"[{item['pinyin']}] "
        f"-> {status}"
    )

    if status == "skip_linked":
        return status

    if status == "missing_linked":
        fail(
            f"MaTep cua {item['text']} da co "
            "nhung file MP3 bi thieu/hong: "
            f"{file}. "
            "Can xu ly rieng, khong tu ghi de."
        )

    if status == "invalid_file":
        fail(
            f"File MP3 ton tai nhung khong hop le: "
            f"{file}. Khong tu ghi de."
        )

    if status == "generate":
        generate_mp3(
            client,
            item["text"],
            file,
        )

        print(
            f"    MP3 OK: {file.name} "
            f"({file.stat().st_size} bytes)"
        )

    media_id = insert_media_and_link(
        conn,
        cursor,
        kind,
        item,
        public_path,
    )

    print(f"    SQL OK: MaTep={media_id}")

    return (
        "generated_and_linked"
        if status == "generate"
        else "reused_and_linked"
    )


def audio_stats(cursor):
    cursor.execute("""
        SELECT COUNT(DISTINCT tv.MaTuVung)
        FROM dbo.TuVungBaiHoc AS l
        JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc = l.MaBaiHoc
        JOIN dbo.TuVung AS tv
            ON tv.MaTuVung = l.MaTuVung
        JOIN dbo.TepDaPhuongTien AS m
            ON m.MaTep = tv.MaAmThanh
        WHERE bh.MaKhoaHoc = ?
          AND m.LoaiTep = 'am_thanh';
    """, COURSE_ID)

    vocab = int(cursor.fetchone()[0] or 0)

    cursor.execute("""
        SELECT COUNT(*)
        FROM dbo.ChuHan AS ch
        JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc = ch.MaBaiHoc
        JOIN dbo.TepDaPhuongTien AS m
            ON m.MaTep = ch.MaTep
        WHERE bh.MaKhoaHoc = ?
          AND m.LoaiTep = 'am_thanh';
    """, COURSE_ID)

    hanzi = int(cursor.fetchone()[0] or 0)

    return vocab, hanzi


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--preview",
        action="store_true",
        help="Chi kiem tra, khong goi ElevenLabs.",
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Xu ly toan bo HSK3.",
    )

    parser.add_argument(
        "--vocab-limit", type=int, default=5
    )

    parser.add_argument(
        "--hanzi-limit", type=int, default=5
    )

    args = parser.parse_args()

    if args.full and args.preview:
        fail("Chon --preview hoac --full.")

    if args.vocab_limit < 0 or args.hanzi_limit < 0:
        fail("Limit khong duoc am.")

    print("=" * 70)
    print("BUOC 65 - ELEVENLABS AUDIO HSK3")
    print("=" * 70)

    mode = (
        "PREVIEW" if args.preview
        else "FULL" if args.full
        else "TEST"
    )

    print("Mode:", mode)
    print("Model:", MODEL_ID)
    print("Output:", OUTPUT_FORMAT)

    with closing(get_connection()) as conn:
        if getattr(conn, "autocommit", False):
            fail("SQL dang autocommit=True.")

        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT DB_NAME();")
            database_name = clean(cursor.fetchone()[0])

            if database_name.lower() != "hoctiengtrungdb":
                fail(
                    "Dang ket noi sai database: "
                    + database_name
                )

            cursor.execute("""
                SELECT COUNT(*)
                FROM dbo.KhoaHoc
                WHERE MaKhoaHoc = ?;
            """, COURSE_ID)

            if int(cursor.fetchone()[0]) != 1:
                fail("Khong tim thay khoa HSK3.")

            vocab = load_vocab(cursor)
            hanzi = load_hanzi(cursor)

            print(
                f"TuVung HSK3: "
                f"{len(vocab)}/{EXPECTED_VOCAB}"
            )
            print(
                f"ChuHan HSK3: "
                f"{len(hanzi)}/{EXPECTED_HANZI}"
            )

            if len(vocab) != EXPECTED_VOCAB:
                fail("So luong tu vung HSK3 khong khop.")

            if len(hanzi) != EXPECTED_HANZI:
                fail("So luong chu Han HSK3 khong khop.")

            if args.preview:
                stats = Counter()

                for kind, items in (
                    ("vocab", vocab),
                    ("hanzi", hanzi),
                ):
                    for item in items:
                        status, _, _ = plan_item(
                            cursor, kind, item
                        )
                        stats[f"{kind}_{status}"] += 1

                print("\nTONG HOP PREVIEW")
                for key in sorted(stats):
                    print(f"{key}: {stats[key]}")

                conn.rollback()

                print("\nPREVIEW THANH CONG")
                print("KHONG GOI API ELEVENLABS")
                print("KHONG GHI SQL")
                return

            if not API_KEY or not VOICE_ID:
                fail(
                    "Thieu ELEVENLABS_API_KEY "
                    "hoac ELEVENLABS_VOICE_ID trong .env."
                )

            client = ElevenLabs(api_key=API_KEY)

            before_v, before_h = audio_stats(cursor)

            print("\nAUDIO TRUOC KHI CHAY")
            print(f"TuVung: {before_v}/973")
            print(f"ChuHan : {before_h}/300")

            if not args.full:
                vocab = vocab[:args.vocab_limit]
                hanzi = hanzi[:args.hanzi_limit]

            VOCAB_DIR.mkdir(parents=True, exist_ok=True)
            HANZI_DIR.mkdir(parents=True, exist_ok=True)

            stats = Counter()

            for kind, items in (
                ("vocab", vocab),
                ("hanzi", hanzi),
            ):
                print(
                    "\n" + (
                        "[1] TU VUNG"
                        if kind == "vocab"
                        else "[2] CHU HAN"
                    )
                )

                for index, item in enumerate(items, 1):
                    print(f"[{index}/{len(items)}]")

                    try:
                        result = process_item(
                            conn,
                            cursor,
                            client,
                            kind,
                            item,
                        )
                        stats[result] += 1

                    except Exception:
                        conn.rollback()
                        raise

            after_v, after_h = audio_stats(cursor)

    print("\n" + "=" * 70)
    print("HOAN TAT")
    print("=" * 70)

    for key in sorted(stats):
        print(f"{key}: {stats[key]}")

    print("\nAUDIO HSK3 HIEN TAI")
    print(f"TuVung: {after_v}/973")
    print(f"ChuHan : {after_h}/300")

    if args.full:
        if (
            after_v != EXPECTED_VOCAB
            or after_h != EXPECTED_HANZI
        ):
            fail("FULL chua du audio HSK3.")

        print("\nHSK3 DA LIEN KET DU AUDIO.")
    else:
        print("\nDAY LA CHE DO TEST.")
        print("Hay nghe thu audio truoc khi chay --full.")


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nDa dung theo yeu cau.")
        raise SystemExit(130)

    except Exception as error:
        print("\nCHUONG TRINH DUNG VI LOI:")
        print(error)
        raise SystemExit(1)
