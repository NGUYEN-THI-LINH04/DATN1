from __future__ import annotations

import os
import sys
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
        "Khong tim thay ELEVENLABS_API_KEY"
    )

if not VOICE_ID:
    raise RuntimeError(
        "Khong tim thay ELEVENLABS_VOICE_ID"
    )


# ============================================================
# ELEVENLABS
# ============================================================

client = ElevenLabs(
    api_key=API_KEY
)

MODEL_ID = "eleven_v4"

OUTPUT_FORMAT = "mp3_44100_128"


# ============================================================
# AUDIO CẦN SỬA
# ============================================================

ITEMS = [
    {
        "text": "地",
        "pinyin": "de",

        # 地 khi là trợ từ de
        # Mandarin IPA gần đúng:
        # /tə/
        "ipa": "/tə/",

        "file": (
            ROOT_DIR
            / "static"
            / "audio"
            / "hsk1"
            / "tu_vung"
            / "tv_0079.mp3"
        ),
    },

    {
        "text": "还",
        "pinyin": "huán",

        # 还 khi đọc huán
        # Tone 2: rising
        "ipa": "/xwan˧˥/",

        "file": (
            ROOT_DIR
            / "static"
            / "audio"
            / "hsk1"
            / "tu_vung"
            / "tv_0163.mp3"
        ),
    },
]


# ============================================================
# TẠO PLS DICTIONARY
# ============================================================

def build_pls(
    text: str,
    ipa: str,
) -> bytes:

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
    <lexeme>
        <grapheme>{text}</grapheme>
        <phoneme>{ipa}</phoneme>
    </lexeme>
</lexicon>
"""

    return xml.encode("utf-8")


# ============================================================
# TẠO AUDIO
# ============================================================

def generate_audio(
    text: str,
    pinyin: str,
    ipa: str,
    output_file: Path,
):

    print()
    print("=" * 70)

    print(
        f"Dang sua: {text} | "
        f"Pinyin={pinyin} | "
        f"IPA={ipa}"
    )

    print(
        "File:",
        output_file
    )


    # --------------------------------------------------------
    # TẠO PRONUNCIATION DICTIONARY
    # --------------------------------------------------------

    pls_data = build_pls(
        text,
        ipa,
    )

    dictionary = (
        client.pronunciation_dictionaries.create_from_file(
            file=pls_data,
            name=(
                f"MocHan_"
                f"{text}_"
                f"{pinyin}"
            ),
        )
    )

    print(
        "Dictionary ID:",
        dictionary.id
    )

    print(
        "Dictionary version:",
        dictionary.version_id
    )


    locator = (
        PronunciationDictionaryVersionLocator(
            pronunciation_dictionary_id=
                dictionary.id,

            version_id=
                dictionary.version_id,
        )
    )


    # --------------------------------------------------------
    # TẠO AUDIO VÀO FILE TẠM
    # --------------------------------------------------------

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_file = output_file.with_suffix(
        ".mp3.part"
    )

    if temp_file.exists():
        temp_file.unlink()


    audio = client.text_to_speech.convert(
        text=text,

        voice_id=VOICE_ID,

        model_id=MODEL_ID,

        output_format=OUTPUT_FORMAT,

        language_code="zh",

        pronunciation_dictionary_locators=[
            locator
        ],
    )


    with temp_file.open("wb") as file:

        for chunk in audio:

            if chunk:
                file.write(chunk)


    size = temp_file.stat().st_size


    if size < 500:

        temp_file.unlink(
            missing_ok=True
        )

        raise RuntimeError(
            f"Audio loi: chi co {size} bytes"
        )


    # --------------------------------------------------------
    # GHI ĐÈ FILE SAI
    # --------------------------------------------------------

    temp_file.replace(
        output_file
    )


    print(
        "OK:",
        output_file.name
    )

    print(
        "Dung luong:",
        size,
        "bytes",
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 70
    )

    print(
        "11B - SUA AUDIO CHU DA AM"
    )

    print(
        "=" * 70
    )


    for item in ITEMS:

        generate_audio(
            text=item["text"],
            pinyin=item["pinyin"],
            ipa=item["ipa"],
            output_file=item["file"],
        )


    print()

    print(
        "=" * 70
    )

    print(
        "HOAN TAT SUA 2 AUDIO"
    )

    print(
        "=" * 70
    )

    print(
        "Hay nghe lai:"
    )

    print(
        "tv_0079.mp3 -> 地 -> de"
    )

    print(
        "tv_0163.mp3 -> 还 -> huan (thanh 2)"
    )


if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print(
            "LOI:",
            error,
        )

        raise SystemExit(1)