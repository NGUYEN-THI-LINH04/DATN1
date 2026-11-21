import os
from pathlib import Path
from dotenv import load_dotenv

# Đọc API Key từ file .env của dự án
load_dotenv(Path(r"D:\DATN1\.env"))

api_key = os.getenv("SUPADATA_API_KEY")

if not api_key:
    raise RuntimeError("Chưa tìm thấy SUPADATA_API_KEY trong .env")