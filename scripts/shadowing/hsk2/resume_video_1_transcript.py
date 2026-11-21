
import json
import time

# Dùng lại đúng các hàm Supadata của HSK2 đã tạo.
from .fetch_video_1_transcript import (
    get_api_key,
    request_json,
    OUTPUT,
    VIDEO_ID,
)

JOB_ID = "f22e93a9-bba2-4355-878a-6f5f131812b7"
API_URL = "https://api.supadata.ai/v1/transcript"

MAX_CHECKS = 36
WAIT_SECONDS = 5


def validate_and_save(data):
    # Kiểm tra ngôn ngữ
    lang = data.get("lang")

    if lang not in ("zh", "zh-CN", "zh-TW"):
        raise RuntimeError(
            f"Ngon ngu khong hop le: {lang}"
        )

    # Kiểm tra dữ liệu có mốc thời gian
    content = data.get("content")

    if not isinstance(content, list) or not content:
        raise RuntimeError(
            "Job da xong nhung chua co transcript hop le."
        )

    # Lưu lại đúng thư mục cache HSK2
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

    print("\nKhong thay doi SQL Server.")


def main():
    print("===== TIEP TUC JOB SUPADATA CU =====")
    print("Video:", VIDEO_ID)
    print("Job ID:", JOB_ID)

    # Không gọi API nếu đã có transcript hợp lệ
    if OUTPUT.exists():
        with OUTPUT.open("r", encoding="utf-8") as f:
            cached = json.load(f)

        content = cached.get("content")

        if isinstance(content, list) and content:
            print("\nDa co transcript trong cache.")
            print("So doan:", len(content))
            print("File:", OUTPUT)
            print("Khong goi Supadata.")
            return

        raise RuntimeError(
            "File cache ton tai nhung khong hop le. "
            "Can kiem tra truoc khi tiep tuc."
        )

    api_key = get_api_key()
    job_url = f"{API_URL}/{JOB_ID}"

    for attempt in range(1, MAX_CHECKS + 1):
        # Chỉ kiểm tra job cũ, KHÔNG gọi generate
        _, data = request_json(job_url, api_key)

        status = str(
            data.get("status", "")
        ).lower()

        print(
            f"Kiem tra {attempt}/{MAX_CHECKS}: "
            f"{status or 'chua co trang thai'}"
        )

        if status in ("failed", "error", "canceled"):
            raise RuntimeError(
                f"Job Supadata that bai: {data}"
            )

        # Một số phản hồi có thể trả content trực tiếp.
        if status == "completed" or (
            isinstance(data.get("content"), list)
            and data["content"]
        ):
            # Nếu kết quả được bọc trong result
            result = data.get("result")

            if isinstance(result, dict) and result.get("content"):
                data = result

            validate_and_save(data)
            return

        if attempt < MAX_CHECKS:
            time.sleep(WAIT_SECONDS)

    print("\nJob van chua hoan tat.")
    print("Khong tao job moi.")
    print("Co the chay lai script resume sau.")


if __name__ == "__main__":
    main()
