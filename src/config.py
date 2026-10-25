"""Cấu hình dùng chung: kết nối DB và tham số gọi API."""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv() # Đọc file .env ở thư mục đang chạy

API_BASE = "https://pokeapi.co/api/v2"
CACHE_DIR = Path("data/cache")
REQUEST_DELAY = 0.1 # Số  giây nghỉ sau mỗi request
REQUEST_TIMEOUT = 15 # Thời gian chờ tối đa

def get_db_url() -> URL:
    """Dựng URL kết nối từ biến môi trường."""
    return URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_POST", "5432")),
        database=os.environ["POSTGRES_DB"],
    )