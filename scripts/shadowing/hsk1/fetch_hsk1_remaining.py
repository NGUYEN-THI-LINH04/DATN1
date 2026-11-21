
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[3]
PREVIEWS = ROOT / "scripts" / "shadowing" / "previews"

VIDEOS = [
    {
        "name": "一个下雨天",
        "id": "QwlhcsAMhT0",
        "file": "yi_ge_xia_yu_tian_generated_zh.json",
    },
    {
        "name": "我的新年计划",
        "id": "o6ilprwO6w0",
        "file": "wo_de_xin_nian_ji_hua_generated_zh.json",
    },
]

API_BASE = "https://api.supadata.ai/v1"
POLL_SECONDS = 10
MAX_POLLS = 30


def get_api_key():
    key = os.environ.get("SUPADATA_API_KEY")
    if key:
        return key.strip()

    env_file = ROOT / ".env"

    if not env_file.exists():
        raise FileNotFoundError("Khong tim thay .env")

    for line in env_file.read_text(
        encoding="utf-8-sig"
    ).splitlines():
        line = line.strip()

        if line.startswith("SUPADATA_API_KEY="):
            return (
                line.split("=", 1)[1]
                .strip()
                .strip('"')
                .strip("'")
            )

    raise ValueError("Khong tim thay SUPADATA_API_KEY")


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def api_get(url, api_key):
    req = Request(
        url,
        headers={
            "x-api-key": api_key,
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urlopen(req, timeout=240) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        message = error.read().decode(
            "utf-8", errors="replace"
        )
        raise RuntimeError(
            f"Supadata HTTP {error.code}: {message[:500]}"
        ) from error

    except URLError as error:
        raise RuntimeError(
            f"Loi ket noi: {error.reason}"
        ) from error


def create_transcript(video_id, api_key):
    params = urlencode({
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "lang": "zh",
        "text": "false",
        "mode": "generate",
    })

    url = f"{API_BASE}/transcript?{params}"

    print("[API] Tao transcript moi (1 yeu cau)")
    return api_get(url, api_key)


def get_job_status(job_id, api_key):
    # Chỉ kiểm tra job đã tồn tại.
    # Không tạo thêm transcript mới.
    safe_job_id = quote(job_id, safe="")
    url = f"{API_BASE}/transcript/{safe_job_id}"

    return api_get(url, api_key)


def resolve_response(data, cache_file, api_key):
    if not isinstance(data, dict):
        raise ValueError("Phan hoi API khong hop le")

    # Trường hợp nhận được transcript ngay.
    if isinstance(data.get("content"), list):
        return data

    # Trường hợp nhận kết quả từ một job hoàn tất.
    if data.get("status") == "completed":
        result = data.get("result")

        if isinstance(result, dict):
            if isinstance(result.get("content"), list):
                return result

    # Trường hợp Supadata trả jobId.
    job_id = data.get("jobId")

    if not job_id:
        print("Cac truong phan hoi:", list(data.keys()))
        print("Trang thai:", data.get("status"))
        print("Thong bao:", data.get("message"))
        raise ValueError(
            "Khong co content hoac jobId. "
            "Da giu file goc, khong goi lai generate."
        )

    if data.get("status") == "failed":
        raise RuntimeError(
            f"Job that bai: {data.get('error')}"
        )

    print("[ASYNC] Da co jobId, tiep tuc job cu.")
    print("Khong tao transcript moi.")

    for attempt in range(1, MAX_POLLS + 1):
        # Poll chỉ truy vấn kết quả công việc cũ.
        result = get_job_status(job_id, api_key)

        status = result.get("status")
        print(
            f"[POLL {attempt}/{MAX_POLLS}] "
            f"Trang thai: {status}"
        )

        # Lưu trạng thái kèm jobId để lần chạy
        # sau vẫn có thể tiếp tục.
        if status in ("queued", "active"):
            save_json(
                cache_file,
                {
                    "jobId": job_id,
                    "status": status,
                },
            )

            if attempt < MAX_POLLS:
                time.sleep(POLL_SECONDS)

            continue

        if status == "failed":
            save_json(
                cache_file,
                {
                    "jobId": job_id,
                    "status": "failed",
                    "error": result.get("error"),
                },
            )
            raise RuntimeError(
                f"Supadata job that bai: "
                f"{result.get('error')}"
            )

        if status == "completed":
            transcript = result.get("result")

            if not isinstance(transcript, dict):
                # Tương thích khi API trả content trực tiếp.
                transcript = result

            if not isinstance(
                transcript.get("content"), list
            ):
                raise ValueError(
                    "Job hoan thanh nhung khong co "
                    "danh sach content. "
                    "File jobId van duoc giu."
                )

            return transcript

        print("Cac truong phan hoi:", list(result.keys()))
        raise ValueError(
            f"Trang thai job khong ho tro: {status}"
        )

    raise RuntimeError(
        "Job van dang xu ly sau nhieu lan kiem tra. "
        "Hay chay lai sau, script se dung jobId cu."
    )


def validate_transcript(data):
    content = data.get("content")

    if not isinstance(content, list) or not content:
        raise ValueError("Transcript rong")

    for i, item in enumerate(content, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Doan {i} sai dinh dang")

        for field in ("text", "offset", "duration"):
            if field not in item:
                raise ValueError(
                    f"Doan {i} thieu {field}"
                )

    joined = " ".join(
        str(item["text"]) for item in content
    )

    hanzi_count = len(
        re.findall(r"[\u3400-\u9fff]", joined)
    )

    if hanzi_count < 30:
        raise ValueError(
            "Transcript co qua it chu Han. "
            "Can xem lai ngon ngu."
        )

    return content


def main():
    PREVIEWS.mkdir(parents=True, exist_ok=True)

    print("===== SUPADATA HSK1 =====")
    print("Ngon ngu: zh")
    print("Che do: generate")
    print("So video:", len(VIDEOS))

    for video in VIDEOS:
        output_file = PREVIEWS / video["file"]

        print("\n----------------------------")
        print("Video:", video["name"])
        print("YouTube ID:", video["id"])

        api_key = get_api_key()

        if output_file.exists():
            print("[CACHE] Tim thay file cu.")
            data = read_json(output_file)
        else:
            data = create_transcript(
                video["id"], api_key
            )

            # Lưu cả phản hồi jobId.
            save_json(output_file, data)

        transcript = resolve_response(
            data,
            output_file,
            api_key,
        )

        # Kiểm tra xong mới ghi đè cache bằng
        # transcript hoàn chỉnh.
        content = validate_transcript(transcript)

        save_json(output_file, transcript)

        print("\n===== THANH CONG =====")
        print("Video:", video["name"])
        print("So doan:", len(content))
        print("Ngon ngu:", transcript.get("lang"))
        print("File:", output_file)

        print("\n5 doan dau:")
        for item in content[:5]:
            print(
                item["offset"],
                "|",
                item["text"],
            )

    print("\n===== HOAN THANH HSK1 =====")
    print("Da lay transcript 2 video.")
    print("Chua chuan hoa cau.")
    print("Chua thay doi SQL Server.")


if __name__ == "__main__":
    main()
