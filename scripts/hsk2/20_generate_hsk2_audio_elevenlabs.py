from __future__ import annotations

import argparse
import os
import sys

from contextlib import closing
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs


# ============================================================
# PROJECT
# File:
# D:\DATN1\scripts\hsk2\20_generate_hsk2_audio_elevenlabs.py
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

if not (ROOT_DIR / "database.py").exists():
    raise RuntimeError(
        f"Khong tim thay database.py tai:\n{ROOT_DIR}"
    )

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT_DIR)
    )

from database import get_connection


# ============================================================
# HSK2
# ============================================================

COURSE_CODE = "HSK2-CORE"

EXPECTED_VOCAB = 772
EXPECTED_HANZI = 299


# ============================================================
# ELEVENLABS
#
# Giu giong HSK1 de giao dien / giong doc dong nhat.
# ============================================================

MODEL_ID = "eleven_v4"

OUTPUT_FORMAT = "mp3_44100_128"

MIN_VALID_MP3_BYTES = 500


VOCAB_DIR = (
    ROOT_DIR
    / "static"
    / "audio"
    / "hsk2"
    / "tu_vung"
)

HANZI_DIR = (
    ROOT_DIR
    / "static"
    / "audio"
    / "hsk2"
    / "chu_han"
)


# ============================================================
# ENV
# ============================================================

load_dotenv(
    ROOT_DIR / ".env",
    interpolate=False
)

API_KEY = os.getenv(
    "ELEVENLABS_API_KEY",
    ""
).strip()

VOICE_ID = os.getenv(
    "ELEVENLABS_VOICE_ID",
    ""
).strip()


def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def fail(message):

    raise RuntimeError(
        message
    )


# ============================================================
# PUBLIC PATH -> FILE PROJECT
# ============================================================

def project_file_from_public_path(
    public_path
):

    value = clean(
        public_path
    ).replace(
        "\\",
        "/"
    )

    if value.startswith(
        "/static/"
    ):

        return (
            ROOT_DIR
            / value.lstrip("/")
        )

    if value.startswith(
        "static/"
    ):

        return (
            ROOT_DIR
            / value
        )

    return None


def is_valid_audio_file(
    path
):

    return (
        path.exists()
        and path.is_file()
        and path.stat().st_size
        >= MIN_VALID_MP3_BYTES
    )


# ============================================================
# ELEVENLABS -> MP3
# ============================================================

def generate_mp3(
    client,
    text,
    output_file
):

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_file = (
        output_file.with_suffix(
            output_file.suffix
            + ".part"
        )
    )

    if temp_file.exists():
        temp_file.unlink()

    audio = (
        client
        .text_to_speech
        .convert(
            text=text,
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
            output_format=OUTPUT_FORMAT,
        )
    )

    try:

        with temp_file.open(
            "wb"
        ) as file:

            for chunk in audio:

                if chunk:
                    file.write(
                        chunk
                    )

        if not is_valid_audio_file(
            temp_file
        ):

            size = (
                temp_file.stat().st_size
                if temp_file.exists()
                else 0
            )

            fail(
                "File MP3 tao ra "
                f"khong hop le: "
                f"{size} bytes"
            )

        temp_file.replace(
            output_file
        )

    finally:

        if temp_file.exists():
            temp_file.unlink()


# ============================================================
# DOC 772 TU VUNG HSK2
# ============================================================

def get_hsk2_vocab(
    cursor
):

    cursor.execute(
        """
        SELECT
            tv.MaTuVung,
            tv.ChuHan,
            tv.PhienAm,
            tv.MaAmThanh,

            bh.SoThuTuBai,
            tvbh.ThuTu

        FROM dbo.TuVungBaiHoc AS tvbh

        INNER JOIN dbo.TuVung AS tv
            ON tvbh.MaTuVung =
               tv.MaTuVung

        INNER JOIN dbo.BaiHoc AS bh
            ON tvbh.MaBaiHoc =
               bh.MaBaiHoc

        INNER JOIN dbo.KhoaHoc AS kh
            ON bh.MaKhoaHoc =
               kh.MaKhoaHoc

        WHERE
            kh.MaKyHieu = ?

        ORDER BY
            bh.SoThuTuBai,
            tvbh.ThuTu,
            tv.MaTuVung;
        """,
        COURSE_CODE,
    )

    items = []

    seen = set()

    for row in cursor.fetchall():

        ma_tu_vung = int(
            row[0]
        )

        # Bao ve neu mot tu bi lien ket
        # nhieu lan.
        if ma_tu_vung in seen:
            continue

        seen.add(
            ma_tu_vung
        )

        items.append({

            "id":
                ma_tu_vung,

            "text":
                clean(row[1]),

            "pinyin":
                clean(row[2]),

            "media_id":
                row[3],

            "lesson":
                int(row[4]),

            "order":
                int(row[5]),
        })

    return items


# ============================================================
# DOC 299 CHU HAN HSK2
# ============================================================

def get_hsk2_hanzi(
    cursor
):

    cursor.execute(
        """
        SELECT
            ch.MaChuHan,
            ch.KyTu,
            ch.Pinyin,
            ch.MaTep,

            bh.SoThuTuBai,
            ch.ThuTu

        FROM dbo.ChuHan AS ch

        INNER JOIN dbo.BaiHoc AS bh
            ON ch.MaBaiHoc =
               bh.MaBaiHoc

        INNER JOIN dbo.KhoaHoc AS kh
            ON bh.MaKhoaHoc =
               kh.MaKhoaHoc

        WHERE
            kh.MaKyHieu = ?

        ORDER BY
            bh.SoThuTuBai,
            ch.ThuTu,
            ch.MaChuHan;
        """,
        COURSE_CODE,
    )

    result = []

    for row in cursor.fetchall():

        result.append({

            "id":
                int(row[0]),

            "text":
                clean(row[1]),

            "pinyin":
                clean(row[2]),

            "media_id":
                row[3],

            "lesson":
                int(row[4]),

            "order":
                int(row[5]),
        })

    return result


# ============================================================
# DOC MEDIA
# ============================================================

def get_media(
    cursor,
    media_id
):

    cursor.execute(
        """
        SELECT
            MaTep,
            LoaiTep,
            DuongDanTep,
            TieuDe,
            LoiThoai

        FROM dbo.TepDaPhuongTien

        WHERE
            MaTep = ?;
        """,
        media_id,
    )

    return cursor.fetchone()


# ============================================================
# INSERT MEDIA + GAN FK
# ============================================================

def insert_and_link_media(
    connection,
    cursor,
    *,
    kind,
    item_id,
    text,
    public_path
):

    if kind == "vocab":

        title = (
            f"Phat am tu vung HSK2: "
            f"{text}"
        )

    else:

        title = (
            f"Phat am chu Han HSK2: "
            f"{text}"
        )

    cursor.execute(
        """
        INSERT INTO dbo.TepDaPhuongTien
        (
            LoaiTep,
            DuongDanTep,
            TieuDe,
            LoiThoai,
            MaNguon
        )

        OUTPUT
            INSERTED.MaTep

        VALUES
        (
            'am_thanh',
            ?,
            ?,
            ?,
            NULL
        );
        """,

        public_path,
        title,
        text,
    )

    media_id = int(
        cursor.fetchone()[0]
    )

    # ========================================================
    # TU VUNG
    # ========================================================

    if kind == "vocab":

        cursor.execute(
            """
            UPDATE dbo.TuVung

            SET
                MaAmThanh = ?

            WHERE
                MaTuVung = ?
                AND MaAmThanh IS NULL;
            """,

            media_id,
            item_id,
        )

    # ========================================================
    # CHU HAN
    # ========================================================

    else:

        cursor.execute(
            """
            UPDATE dbo.ChuHan

            SET
                MaTep = ?

            WHERE
                MaChuHan = ?
                AND MaTep IS NULL;
            """,

            media_id,
            item_id,
        )

    if cursor.rowcount != 1:

        connection.rollback()

        fail(
            "Khong cap nhat duoc FK "
            f"cho {kind} ID={item_id}."
        )

    connection.commit()

    return media_id


# ============================================================
# XU LY 1 TU / 1 CHU HAN
# ============================================================

def process_item(
    connection,
    cursor,
    client,
    *,
    kind,
    item
):

    item_id = item[
        "id"
    ]

    text = item[
        "text"
    ]

    pinyin = item[
        "pinyin"
    ]

    current_media_id = item[
        "media_id"
    ]

    if not text:

        fail(
            f"{kind} ID={item_id} "
            "khong co noi dung tieng Trung."
        )

    # ========================================================
    # DUONG DAN HSK2
    # ========================================================

    if kind == "vocab":

        output_file = (
            VOCAB_DIR
            / f"tv_{item_id:04d}.mp3"
        )

        public_path = (
            "/static/audio/"
            "hsk2/tu_vung/"
            f"tv_{item_id:04d}.mp3"
        )

    else:

        output_file = (
            HANZI_DIR
            / f"ch_{item_id:04d}.mp3"
        )

        public_path = (
            "/static/audio/"
            "hsk2/chu_han/"
            f"ch_{item_id:04d}.mp3"
        )

    print(
        f"  ID={item_id:<5} "
        f"Bai={item['lesson']:<2} "
        f"Text={text} "
        f"| Pinyin={pinyin or '-'}"
    )

    # ========================================================
    # DA CO AUDIO TRONG SQL
    #
    # Co the la tu dung chung voi HSK1.
    # KHONG tao lai -> tiet kiem credits.
    # ========================================================

    if current_media_id is not None:

        media = get_media(
            cursor,
            int(
                current_media_id
            )
        )

        if media is None:

            fail(
                "FK audio="
                f"{current_media_id} "
                "khong ton tai."
            )

        if clean(
            media[1]
        ) != "am_thanh":

            fail(
                f"Media "
                f"{current_media_id} "
                "khong phai am_thanh."
            )

        existing_file = (
            project_file_from_public_path(
                clean(
                    media[2]
                )
            )
        )

        if existing_file is None:

            fail(
                "DuongDanTep khong thuoc "
                f"/static: {media[2]}"
            )

        # File da tot
        if is_valid_audio_file(
            existing_file
        ):

            print(
                "    SKIP: "
                "da co audio hop le "
                f"(MaTep={current_media_id})."
            )

            return "skip_linked"

        # SQL co media nhung file bi mat
        print(
            "    REPAIR: "
            "SQL co audio nhung file bi thieu."
        )

        generate_mp3(
            client,
            text,
            existing_file
        )

        print(
            "    OK: khoi phuc "
            f"{existing_file.name}"
        )

        return "repaired"

    # ========================================================
    # CHUA CO FK AUDIO
    # ========================================================

    if is_valid_audio_file(
        output_file
    ):

        print(
            "    REUSE: "
            "file MP3 da ton tai."
        )

    else:

        print(
            "    TTS: dang tao audio..."
        )

        generate_mp3(
            client,
            text,
            output_file
        )

        print(
            f"    OK file: "
            f"{output_file.name} "
            f"({output_file.stat().st_size} bytes)"
        )

    media_id = insert_and_link_media(
        connection,
        cursor,

        kind=kind,
        item_id=item_id,
        text=text,
        public_path=public_path,
    )

    print(
        "    OK SQL: "
        f"MaTep={media_id}"
    )

    return "created"


# ============================================================
# DEM AUDIO DA LIEN KET HSK2
# ============================================================

def get_audio_stats(
    cursor
):

    cursor.execute(
        """
        SELECT
            COUNT(DISTINCT tv.MaTuVung)

        FROM dbo.TuVungBaiHoc AS tvbh

        INNER JOIN dbo.TuVung AS tv
            ON tvbh.MaTuVung =
               tv.MaTuVung

        INNER JOIN dbo.BaiHoc AS bh
            ON tvbh.MaBaiHoc =
               bh.MaBaiHoc

        INNER JOIN dbo.KhoaHoc AS kh
            ON bh.MaKhoaHoc =
               kh.MaKhoaHoc

        INNER JOIN dbo.TepDaPhuongTien AS tep
            ON tv.MaAmThanh =
               tep.MaTep

        WHERE
            kh.MaKyHieu = ?
            AND tep.LoaiTep =
                'am_thanh';
        """,
        COURSE_CODE,
    )

    vocab_audio = int(
        cursor.fetchone()[0]
        or 0
    )

    cursor.execute(
        """
        SELECT
            COUNT(*)

        FROM dbo.ChuHan AS ch

        INNER JOIN dbo.BaiHoc AS bh
            ON ch.MaBaiHoc =
               bh.MaBaiHoc

        INNER JOIN dbo.KhoaHoc AS kh
            ON bh.MaKhoaHoc =
               kh.MaKhoaHoc

        INNER JOIN dbo.TepDaPhuongTien AS tep
            ON ch.MaTep =
               tep.MaTep

        WHERE
            kh.MaKyHieu = ?
            AND tep.LoaiTep =
                'am_thanh';
        """,
        COURSE_CODE,
    )

    hanzi_audio = int(
        cursor.fetchone()[0]
        or 0
    )

    return (
        vocab_audio,
        hanzi_audio
    )


# ============================================================
# ARGUMENT
# ============================================================

def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Tao audio ElevenLabs "
            "cho TuVung + ChuHan HSK2."
        )
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help=(
            "Chay toan bo "
            "772 tu + 299 Chu Han."
        ),
    )

    parser.add_argument(
        "--vocab-limit",
        type=int,
        default=5,
        help=(
            "So tu test. "
            "Mac dinh 5."
        ),
    )

    parser.add_argument(
        "--hanzi-limit",
        type=int,
        default=5,
        help=(
            "So Chu Han test. "
            "Mac dinh 5."
        ),
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main():

    args = parse_args()

    print("=" * 100)
    print(
        "BUOC 20 - ELEVENLABS AUDIO HSK2"
    )
    print("=" * 100)

    print(
        "Mode:",
        (
            "FULL 772 TU + 299 CHU"
            if args.full
            else "TEST"
        )
    )

    print(
        "Model:",
        MODEL_ID
    )

    print(
        "Output:",
        OUTPUT_FORMAT
    )

    print()

    if not API_KEY:

        fail(
            "Khong tim thay "
            "ELEVENLABS_API_KEY trong .env"
        )

    if not VOICE_ID:

        fail(
            "Khong tim thay "
            "ELEVENLABS_VOICE_ID trong .env"
        )

    VOCAB_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    HANZI_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    client = ElevenLabs(
        api_key=API_KEY
    )

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                "SELECT DB_NAME();"
            )

            db_name = clean(
                cursor.fetchone()[0]
            )

            print(
                "Database:",
                db_name
            )

            if (
                db_name.lower()
                != "hoctiengtrungdb"
            ):

                fail(
                    "Dang ket noi "
                    "nham database."
                )

            # =================================================
            # DOC DU LIEU
            # =================================================

            vocab = get_hsk2_vocab(
                cursor
            )

            hanzi = get_hsk2_hanzi(
                cursor
            )

            print(
                f"HSK2 TuVung: "
                f"{len(vocab)} / "
                f"{EXPECTED_VOCAB}"
            )

            print(
                f"HSK2 ChuHan : "
                f"{len(hanzi)} / "
                f"{EXPECTED_HANZI}"
            )

            if len(vocab) != EXPECTED_VOCAB:

                fail(
                    "So luong TuVung HSK2 "
                    "khong dung 772."
                )

            if len(hanzi) != EXPECTED_HANZI:

                fail(
                    "So luong ChuHan HSK2 "
                    "khong dung 299."
                )

            before_vocab, before_hanzi = (
                get_audio_stats(
                    cursor
                )
            )

            print()
            print(
                "Audio truoc khi chay:"
            )

            print(
                f"  TuVung: "
                f"{before_vocab}/772"
            )

            print(
                f"  ChuHan : "
                f"{before_hanzi}/299"
            )

            # =================================================
            # TEST
            # =================================================

            if not args.full:

                vocab = vocab[
                    :
                    max(
                        0,
                        args.vocab_limit
                    )
                ]

                hanzi = hanzi[
                    :
                    max(
                        0,
                        args.hanzi_limit
                    )
                ]

            stats = {
                "created": 0,
                "skip_linked": 0,
                "repaired": 0,
                "failed": 0,
            }

            # =================================================
            # TU VUNG
            # =================================================

            print()
            print(
                "[1] TU VUNG"
            )

            print(
                "-" * 100
            )

            for index, item in enumerate(
                vocab,
                start=1
            ):

                print(
                    f"[{index}/"
                    f"{len(vocab)}]"
                )

                try:

                    result = process_item(
                        connection,
                        cursor,
                        client,

                        kind="vocab",
                        item=item,
                    )

                    stats[result] += 1

                except Exception:

                    connection.rollback()

                    stats[
                        "failed"
                    ] += 1

                    raise

            # =================================================
            # CHU HAN
            # =================================================

            print()
            print(
                "[2] CHU HAN"
            )

            print(
                "-" * 100
            )

            for index, item in enumerate(
                hanzi,
                start=1
            ):

                print(
                    f"[{index}/"
                    f"{len(hanzi)}]"
                )

                try:

                    result = process_item(
                        connection,
                        cursor,
                        client,

                        kind="hanzi",
                        item=item,
                    )

                    stats[result] += 1

                except Exception:

                    connection.rollback()

                    stats[
                        "failed"
                    ] += 1

                    raise

            after_vocab, after_hanzi = (
                get_audio_stats(
                    cursor
                )
            )

    # ========================================================
    # KET QUA
    # ========================================================

    print()
    print("=" * 100)
    print(
        "HOAN TAT"
    )
    print("=" * 100)

    print(
        "Tao + lien ket moi :",
        stats["created"]
    )

    print(
        "Da co, bo qua      :",
        stats["skip_linked"]
    )

    print(
        "Khoi phuc file     :",
        stats["repaired"]
    )

    print(
        "Loi                :",
        stats["failed"]
    )

    print()
    print(
        "AUDIO HSK2 HIEN TAI:"
    )

    print(
        f"  TuVung: "
        f"{after_vocab}/772"
    )

    print(
        f"  ChuHan : "
        f"{after_hanzi}/299"
    )

    if args.full:

        if (
            after_vocab
            != EXPECTED_VOCAB
            or
            after_hanzi
            != EXPECTED_HANZI
        ):

            fail(
                "FULL da chay xong "
                "nhung chua du audio."
            )

        print()
        print(
            "HSK2 DA DU "
            "772/772 AUDIO TU VUNG "
            "VA 299/299 AUDIO CHU HAN."
        )

    else:

        print()
        print(
            "DAY MOI LA CHE DO TEST."
        )

        print(
            "Mo giao dien HSK2 "
            "kiem tra nut Nghe truoc."
        )

        print()
        print(
            "Neu nghe OK moi chay:"
        )

        print(
            "python scripts\\hsk2\\"
            "20_generate_hsk2_audio_elevenlabs.py "
            "--full"
        )


if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\nDa dung theo yeu cau."
        )

        raise SystemExit(
            130
        )

    except Exception as error:

        print()
        print(
            "CHUONG TRINH DUNG VI LOI:"
        )

        print(
            error
        )

        raise SystemExit(
            1
        )