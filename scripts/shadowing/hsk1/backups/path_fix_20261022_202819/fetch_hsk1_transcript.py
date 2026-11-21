
import json
import os
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[2]
VIDEO_ID = "6YGJswSorYw"

OUTPUT = (
    ROOT / "scripts" / "shadowing" / "previews"
    / "jian_dan_sheng_huo_native_zh.json"
)


def get_api_key():
    key = os.environ.get("SUPADATA_API_KEY")
    if key:
        return key

    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(
            encoding="utf-8-sig"
        ).splitlines():
            line = line.strip()
            if line.startswith("SUPADATA_API_KEY="):
                return line.split("=", 1)[1].strip().strip("\"'")

    raise RuntimeError("Khong tim thay SUPADATA_API_KEY trong .env")


def request_json(url, api_key):
    req = Request(url, headers={"x-api-key": api_key})

    try:
        with urlopen(req, timeout=240) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Supadata HTTP {error.code}: {detail[:500]}"
        ) from error


def main():
    key = get_api_key()

    params = urlencode({
        "url": f"https://www.youtube.com/watch?v={VIDEO_ID}",
        "lang": "zh",
        "text": "false",
        "mode": "generate",
    })

    api_url = "https://api.supadata.ai/v1/transcript"
    status, data = request_json(f"{api_url}?{params}", key)

    if status == 202 or data.get("jobId"):
        job_id = data.get("jobId")
        if not job_id:
            raise RuntimeError("Khong nhan duoc jobId.")

        for _ in range(30):
            time.sleep(3)
            _, data = request_json(
                f"{api_url}/{job_id}", key
            )
            if data.get("status") == "failed":
                raise RuntimeError("Supadata xu ly that bai.")
            if data.get("status") == "completed":
                break
        else:
            raise RuntimeError("Job chua hoan tat. Thu lai sau.")
    if data.get("lang") not in ("zh", "zh-CN", "zh-TW"):
        raise RuntimeError(
        f"Transcript khong phai tieng Trung: {data.get('lang')}"
    )
    content = data.get("content")

    if not isinstance(content, list) or not content:
        raise RuntimeError("Khong co phu de kem moc thoi gian.")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("===== LAY TRANSCRIPT THANH CONG =====")
    print("Video:", VIDEO_ID)
    print("Ngon ngu:", data.get("lang"))
    print("So doan:", len(content))
    print("File:", OUTPUT)

    print("\n===== 5 DOAN DAU =====")
    for item in content[:5]:
        print(item.get("offset"), "|", item.get("text"))


if __name__ == "__main__":
    main()
