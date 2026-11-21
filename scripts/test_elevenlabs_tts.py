from pathlib import Path
import os

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs


ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(ROOT_DIR / ".env")


API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")


if not API_KEY:
    raise RuntimeError(
        "Không tìm thấy ELEVENLABS_API_KEY trong .env"
    )

if not VOICE_ID:
    raise RuntimeError(
        "Không tìm thấy ELEVENLABS_VOICE_ID trong .env"
    )


OUTPUT_DIR = (
    ROOT_DIR
    / "static"
    / "audio"
    / "test"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "nihao.mp3"
)


client = ElevenLabs(
    api_key=API_KEY
)


print("=" * 70)
print("TEST ELEVENLABS TTS")
print("=" * 70)

print("Text: 你好")
print("Đang tạo audio...")


audio = client.text_to_speech.convert(
    text="你好",
    voice_id=VOICE_ID,
    model_id="eleven_v4",
    output_format="mp3_44100_128",
)


with OUTPUT_FILE.open("wb") as file:

    for chunk in audio:

        if chunk:
            file.write(chunk)


if not OUTPUT_FILE.exists():
    raise RuntimeError(
        "Không tạo được file MP3."
    )


size = OUTPUT_FILE.stat().st_size


if size < 500:
    raise RuntimeError(
        f"File MP3 quá nhỏ: {size} bytes"
    )


print()
print("✅ TẠO AUDIO THÀNH CÔNG")
print("File:", OUTPUT_FILE)
print("Dung lượng:", size, "bytes")