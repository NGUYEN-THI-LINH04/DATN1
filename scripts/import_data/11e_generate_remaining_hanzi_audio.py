from __future__ import annotations

import json
import os
import sys
from contextlib import closing
from pathlib import Path

from dotenv import load_dotenv

from elevenlabs import (
    ElevenLabs,
    PronunciationDictionaryVersionLocator,
)


# ============================================================
# ROOT PROJECT
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from database import get_connection


# ============================================================
# CẤU HÌNH
# ============================================================

COURSE_CODE = "HSK1-CORE"

EXPECTED_TOTAL_HANZI = 301
EXPECTED_ALREADY_LINKED = 202
EXPECTED_REMAINING = 99

MODEL_ID = "eleven_v4"

OUTPUT_FORMAT = "mp3_44100_128"

MIN_VALID_MP3_BYTES = 500


# ============================================================
# THƯ MỤC
# ============================================================

HANZI_AUDIO_DIR = (
    ROOT_DIR
    / "static"
    / "audio"
    / "hsk1"
    / "chu_han"
)

CACHE_DIR = (
    ROOT_DIR
    / "data_sources"
)

DICTIONARY_CACHE = (
    CACHE_DIR
    / "elevenlabs_hsk1_hanzi_dictionary.json"
)


# ============================================================
# .ENV
# ============================================================

load_dotenv(
    ROOT_DIR / ".env",
    interpolate=False,
)

API_KEY = os.getenv(
    "ELEVENLABS_API_KEY",
    "",
).strip()

VOICE_ID = os.getenv(
    "ELEVENLABS_VOICE_ID",
    "",
).strip()


if not API_KEY:
    raise RuntimeError(
        "Khong tim thay ELEVENLABS_API_KEY."
    )

if not VOICE_ID:
    raise RuntimeError(
        "Khong tim thay ELEVENLABS_VOICE_ID."
    )


# ============================================================
# ELEVENLABS
# ============================================================

client = ElevenLabs(
    api_key=API_KEY
)


# ============================================================
# CÁC CHỮ ĐA ÂM / DỄ ĐỌC SAI
#
# Chỉ dùng dictionary khi:
# KyTu + Pinyin khớp đúng cặp bên dưới.
# ============================================================

SPECIAL_PRONUNCIATIONS = {
    ("谁", "shéi"): "/ʂeɪ˧˥/",
    ("什", "shén"): "/ʂən˧˥/",
    ("兴", "xìng"): "/ɕiŋ˥˩/",
    ("假", "jià"): "/tɕja˥˩/",
    ("得", "de"): "/tə/",
    ("觉", "jiào"): "/tɕjɑʊ˥˩/",
    ("系", "xì"): "/ɕi˥˩/",
}


# ============================================================
# HÀM PHỤ
# ============================================================

def clean(value) -> str:
    if value is None:
        return ""

    return str(value).strip()


def normalize_pinyin(value: str) -> str:
    return " ".join(
        clean(value).lower().split()
    )


def fail(message: str):
    raise RuntimeError(message)


def is_valid_audio_file(
    path: Path,
) -> bool:

    return (
        path.exists()
        and path.is_file()
        and path.stat().st_size
        >= MIN_VALID_MP3_BYTES
    )


# ============================================================
# XML ESCAPE
# ============================================================

def xml_escape(value: str) -> str:

    return (
        value
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


# ============================================================
# TẠO 1 PRONUNCIATION DICTIONARY
# CHỨA TẤT CẢ CHỮ ĐA ÂM CẦN ÉP
# ============================================================

def build_pls() -> bytes:

    rules = []

    for (
        text,
        pinyin
    ), ipa in SPECIAL_PRONUNCIATIONS.items():

        rules.append(
            f"""
    <lexeme>
        <grapheme>{xml_escape(text)}</grapheme>
        <phoneme>{xml_escape(ipa)}</phoneme>
    </lexeme>
"""
        )


    body = "".join(
        rules
    )


    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<lexicon
    version="1.0"
    xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="
        http://www.w3.org/2005/01/pronunciation-lexicon
        http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd
    "
    alphabet="ipa"
    xml:lang="zh-CN"
>
{body}
</lexicon>
"""

    return xml.encode(
        "utf-8"
    )


# ============================================================
# LẤY / TẠO DICTIONARY
# ============================================================

def get_dictionary_locator():

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    # --------------------------------------------------------
    # ĐÃ TẠO TỪ LẦN TRƯỚC
    # --------------------------------------------------------

    if DICTIONARY_CACHE.exists():

        try:

            data = json.loads(
                DICTIONARY_CACHE.read_text(
                    encoding="utf-8"
                )
            )

            dictionary_id = clean(
                data.get(
                    "dictionary_id"
                )
            )

            version_id = clean(
                data.get(
                    "version_id"
                )
            )


            if (
                dictionary_id
                and version_id
            ):

                print(
                    "Dung lai pronunciation "
                    "dictionary da tao."
                )

                print(
                    "Dictionary ID:",
                    dictionary_id
                )

                print(
                    "Version ID   :",
                    version_id
                )


                return (
                    PronunciationDictionaryVersionLocator(
                        pronunciation_dictionary_id=
                            dictionary_id,

                        version_id=
                            version_id,
                    )
                )

        except Exception:
            pass


    # --------------------------------------------------------
    # CHƯA CÓ -> TẠO MỚI
    # --------------------------------------------------------

    print(
        "Dang tao pronunciation "
        "dictionary HSK1..."
    )


    dictionary = (
        client.pronunciation_dictionaries
        .create_from_file(
            file=build_pls(),
            name=(
                "MocHan_HSK1_"
                "Hanzi_Polyphonic_v1"
            ),
        )
    )


    dictionary_id = dictionary.id

    version_id = dictionary.version_id


    DICTIONARY_CACHE.write_text(
        json.dumps(
            {
                "dictionary_id":
                    dictionary_id,

                "version_id":
                    version_id,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


    print(
        "Dictionary ID:",
        dictionary_id
    )

    print(
        "Version ID   :",
        version_id
    )


    return (
        PronunciationDictionaryVersionLocator(
            pronunciation_dictionary_id=
                dictionary_id,

            version_id=
                version_id,
        )
    )


# ============================================================
# LẤY 301 CHỮ HÁN
# ============================================================

def get_hanzi(cursor):

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

        WHERE kh.MaKyHieu = ?

        ORDER BY
            bh.SoThuTuBai,
            ch.ThuTu,
            ch.MaChuHan;
        """,
        COURSE_CODE,
    )


    return [
        {
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
        }

        for row in cursor.fetchall()
    ]


# ============================================================
# TẠO AUDIO
# ============================================================

def generate_audio(
    *,
    text: str,
    pinyin: str,
    output_file: Path,
    dictionary_locator,
):

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    temp_file = output_file.with_suffix(
        output_file.suffix + ".part"
    )


    if temp_file.exists():
        temp_file.unlink()


    special_key = (
        text,
        normalize_pinyin(
            pinyin
        ),
    )


    # --------------------------------------------------------
    # CHỮ ĐA ÂM -> DÙNG PRONUNCIATION DICTIONARY
    # --------------------------------------------------------

    if (
        special_key
        in SPECIAL_PRONUNCIATIONS
    ):

        print(
            "    TTS + DICTIONARY: "
            f"ep doc {pinyin}"
        )


        audio = (
            client.text_to_speech.convert(
                text=text,

                voice_id=VOICE_ID,

                model_id=MODEL_ID,

                output_format=
                    OUTPUT_FORMAT,

                language_code="zh",

                pronunciation_dictionary_locators=[
                    dictionary_locator
                ],
            )
        )


    # --------------------------------------------------------
    # CHỮ THÔNG THƯỜNG
    # --------------------------------------------------------

    else:

        print(
            "    TTS: doc mac dinh."
        )


        audio = (
            client.text_to_speech.convert(
                text=text,

                voice_id=VOICE_ID,

                model_id=MODEL_ID,

                output_format=
                    OUTPUT_FORMAT,

                language_code="zh",
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
                "Audio khong hop le: "
                f"{size} bytes."
            )


        temp_file.replace(
            output_file
        )


    finally:

        if temp_file.exists():
            temp_file.unlink()


# ============================================================
# GHI MEDIA + GẮN ChuHan.MaTep
# ============================================================

def insert_media_and_link(
    connection,
    cursor,
    *,
    hanzi_id: int,
    text: str,
    public_path: str,
):

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

        OUTPUT INSERTED.MaTep

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
        f"Phat am chu Han: {text}",
        text,
    )


    media_id = int(
        cursor.fetchone()[0]
    )


    cursor.execute(
        """
        UPDATE dbo.ChuHan

        SET MaTep = ?

        WHERE MaChuHan = ?
          AND MaTep IS NULL;
        """,
        media_id,
        hanzi_id,
    )


    if cursor.rowcount != 1:

        connection.rollback()

        fail(
            "Khong gan duoc MaTep "
            f"cho ChuHanID={hanzi_id}."
        )


    connection.commit()

    return media_id


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 100)

    print(
        "11E - TAO AUDIO "
        "99 CHU HAN CON LAI"
    )

    print("=" * 100)

    print(
        "Model:",
        MODEL_ID
    )

    print()


    HANZI_AUDIO_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # DATABASE
            # =================================================

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
            # DỮ LIỆU
            # =================================================

            all_hanzi = get_hanzi(
                cursor
            )


            if (
                len(all_hanzi)
                != EXPECTED_TOTAL_HANZI
            ):

                fail(
                    "Tong ChuHan "
                    "khong bang 301."
                )


            already_linked = [
                item
                for item in all_hanzi
                if item["media_id"]
                is not None
            ]


            remaining = [
                item
                for item in all_hanzi
                if item["media_id"]
                is None
            ]


            print(
                "Da co MaTep :",
                len(already_linked),
                "/",
                EXPECTED_TOTAL_HANZI,
            )


            print(
                "Con thieu   :",
                len(remaining)
            )


            # -------------------------------------------------
            # BẢO VỆ TRƯỚC KHI CHẠY LẦN ĐẦU
            # -------------------------------------------------

            if len(remaining) == 0:

                print()

                print(
                    "301/301 ChuHan "
                    "da co audio."
                )

                return


            if (
                len(already_linked)
                == EXPECTED_ALREADY_LINKED
                and len(remaining)
                != EXPECTED_REMAINING
            ):

                fail(
                    "Trang thai DB "
                    "khong dung voi "
                    "ket qua 11D."
                )


            # =================================================
            # PRONUNCIATION DICTIONARY
            # =================================================

            dictionary_locator = (
                get_dictionary_locator()
            )


            # =================================================
            # THỐNG KÊ
            # =================================================

            stats = {
                "created": 0,
                "reused_file": 0,
                "special": 0,
                "failed": 0,
            }


            # =================================================
            # XỬ LÝ
            # =================================================

            print()

            print("=" * 100)

            print(
                "BAT DAU XU LY"
            )

            print("=" * 100)


            for index, item in enumerate(
                remaining,
                start=1,
            ):

                hanzi_id = item["id"]

                text = item["text"]

                pinyin = item["pinyin"]


                output_file = (
                    HANZI_AUDIO_DIR
                    / f"ch_{hanzi_id:04d}.mp3"
                )


                public_path = (
                    "/static/audio/hsk1/"
                    "chu_han/"
                    f"ch_{hanzi_id:04d}.mp3"
                )


                print()

                print(
                    f"[{index}/"
                    f"{len(remaining)}] "
                    f"ID={hanzi_id:<4} "
                    f"Bai="
                    f"{item['lesson']:<2} "
                    f"{text} "
                    f"| {pinyin}"
                )


                try:

                    special_key = (
                        text,
                        normalize_pinyin(
                            pinyin
                        ),
                    )


                    # -----------------------------------------
                    # FILE ĐÃ CÓ DO LẦN CHẠY DỞ
                    # -----------------------------------------

                    if is_valid_audio_file(
                        output_file
                    ):

                        print(
                            "    REUSE FILE: "
                            "MP3 da ton tai."
                        )

                        stats[
                            "reused_file"
                        ] += 1


                    # -----------------------------------------
                    # CHƯA CÓ FILE
                    # -----------------------------------------

                    else:

                        generate_audio(
                            text=text,
                            pinyin=pinyin,
                            output_file=
                                output_file,
                            dictionary_locator=
                                dictionary_locator,
                        )


                        print(
                            "    OK file: "
                            f"{output_file.name} "
                            "("
                            f"{output_file.stat().st_size}"
                            " bytes)"
                        )


                    if (
                        special_key
                        in SPECIAL_PRONUNCIATIONS
                    ):

                        stats[
                            "special"
                        ] += 1


                    # -----------------------------------------
                    # SQL
                    # -----------------------------------------

                    media_id = (
                        insert_media_and_link(
                            connection,
                            cursor,
                            hanzi_id=hanzi_id,
                            text=text,
                            public_path=
                                public_path,
                        )
                    )


                    stats[
                        "created"
                    ] += 1


                    print(
                        "    OK SQL: "
                        f"MaTep={media_id}"
                    )


                except Exception as error:

                    connection.rollback()

                    stats[
                        "failed"
                    ] += 1


                    print(
                        "    LOI:",
                        error
                    )


                    raise


            # =================================================
            # AUDIT CUỐI
            # =================================================

            cursor.execute(
                """
                SELECT COUNT(*)

                FROM dbo.ChuHan AS ch

                INNER JOIN dbo.BaiHoc AS bh
                    ON ch.MaBaiHoc =
                       bh.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON bh.MaKhoaHoc =
                       kh.MaKhoaHoc

                WHERE kh.MaKyHieu = ?
                  AND ch.MaTep IS NOT NULL;
                """,
                COURSE_CODE,
            )


            total_linked = int(
                cursor.fetchone()[0]
            )


            print()

            print("=" * 100)

            print(
                "HOAN TAT 11E"
            )

            print("=" * 100)


            print(
                "Tao/lien ket moi      :",
                stats["created"]
            )

            print(
                "File cu duoc dung lai :",
                stats["reused_file"]
            )

            print(
                "Chu ep cach doc       :",
                stats["special"]
            )

            print(
                "Loi                   :",
                stats["failed"]
            )


            print(
                "ChuHan co MaTep       :",
                total_linked,
                "/",
                EXPECTED_TOTAL_HANZI,
            )


            if (
                total_linked
                != EXPECTED_TOTAL_HANZI
            ):

                fail(
                    "Sau 11E van chua "
                    "du 301/301 ChuHan."
                )


            print()

            print(
                "OK: 301/301 ChuHan "
                "da co audio."
            )


if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\nDa dung chuong trinh."
        )

        raise SystemExit(130)


    except Exception as error:

        print()

        print(
            "CHUONG TRINH DUNG VI LOI:"
        )

        print(
            error
        )

        raise SystemExit(1)