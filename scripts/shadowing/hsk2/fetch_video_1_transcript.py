
import json
import os
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# Thư mục gốc D:\DATN1
ROOT = Path(__file__).resolve().parents[3]

VIDEO_ID = "nxAfRmACtZs"

# Lưu transcript HSK2 riêng, không dùng thư mục HSK1
OUTPUT = (
    ROOT
    / "scripts"
    / "shadowing"
    / "hsk2"
    / "data"
    / "raw"
    / "video_1_native_zh.json"
)


def get_api_key():
    # Ưu tiên biến môi trường
    key = os.environ.get("SUPADATA_API_KEY")

    if key:
        return key

    # Đọc từ .env giống HSK1
    env_file = ROOT / ".env"

    if env_file.exists():
        for line in env_file.read_text(
            encoding="utf-8-sig"
        ).splitlines():

            line = line.strip()

            if line.startswith("SUPADATA_API_KEY="):
                return (
                    line.split("=", 1)[1]
                    .strip()
                    .strip("\"'")
                )

    raise RuntimeError(
        "Khong tim thay SUPADATA_API_KEY trong .env"
    )


def request_json(url, api_key):
    req = Request(
        url,
        headers={"x-api-key": api_key}
    )

    try:
        with urlopen(req, timeout=240) as response:
            return response.status, json.load(response)

    except HTTPError as error:
        detail = error.read().decode(
            "utf-8", errors="replace"
        )

        raise RuntimeError(
            f"Supadata HTTP {error.code}: {detail[:500]}"
        ) from error


def main():

    print("===== SHADOWING HSK2 - VIDEO 1 =====")
    print("YouTube ID:", VIDEO_ID)

    # BƯỚC 1: Kiểm tra cache trước khi gọi API
    if OUTPUT.exists():
        with OUTPUT.open("r", encoding="utf-8") as f:
            cached = json.load(f)

        content = cached.get("content")

        if not isinstance(content, list) or not content:
            raise RuntimeError(
                "File cache da ton tai nhung khong hop le. "
                "Can kiem tra thu cong, khong tu goi API lai."
            )

        print("\nDA CO TRANSCRIPT TRONG CACHE")
        print("Ngon ngu:", cached.get("lang"))
        print("So doan:", len(content))
        print("File:", OUTPUT)
        print("Khong goi Supadata lan nua.")
        return

    # BƯỚC 2: Chỉ gọi Supadata khi chưa có cache
    print("\nChua co cache. Bat dau lay transcript...")

    key = get_api_key()

    params = urlencode({
        "url": f"https://www.youtube.com/watch?v={VIDEO_ID}",
        "lang": "zh",
        "text": "false",
        "mode": "generate",
    })

    api_url = "https://api.supadata.ai/v1/transcript"

    status, data = request_json(
        f"{api_url}?{params}",
        key
    )

    # BƯỚC 3: Chờ Supadata xử lý (nếu có jobId)
    if status == 202 or data.get("jobId"):

        job_id = data.get("jobId")

        if not job_id:
            raise RuntimeError("Khong nhan duoc jobId.")

        print("Supadata dang xu ly job:", job_id)

        for attempt in range(30):
            time.sleep(3)

            _, data = request_json(
                f"{api_url}/{job_id}",
                key
            )

            job_status = data.get("status")

            if job_status == "failed":
                raise RuntimeError(
                    "Supadata xu ly that bai."
                )

            if job_status == "completed":
                print("Supadata da xu ly xong.")
                break

            print(
                f"Dang cho... {attempt + 1}/30"
            )

        else:
            raise RuntimeError(
                "Job chua hoan tat. Khong goi generate lai "
                "ngay vi co the tao job trung."
            )

    # BƯỚC 4: Kiểm tra transcript
    lang = data.get("lang")

    if lang not in ("zh", "zh-CN", "zh-TW"):
        raise RuntimeError(
            f"Transcript khong phai tieng Trung: {lang}"
        )

    content = data.get("content")

    if not isinstance(content, list) or not content:
        raise RuntimeError(
            "Khong co transcript kem moc thoi gian."
        )

    # BƯỚC 5: Lưu JSON gốc
    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\n===== LAY TRANSCRIPT THANH CONG =====")
    print("Video:", VIDEO_ID)
    print("Ngon ngu:", lang)
    print("So doan:", len(content))
    print("File:", OUTPUT)

    print("\n===== 5 DOAN DAU =====")
    for item in content[:5]:
        print(
            item.get("offset"),
            "|",
            item.get("text")
        )

    print("\nChua thay doi SQL Server.")


if __name__ == "__main__":
    main()
