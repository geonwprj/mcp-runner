# config/minio_setting.py

import os

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "access_key")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "secret_key")
MINIO_REGION = os.getenv("MINIO_REGION", "us-east-1")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() in ("true", "1", "t")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "bucket_name")
MINIO_WORKING_PATH = os.getenv("MINIO_WORKING_PATH", "tmp")
MINIO_PUBLIC_URL = os.getenv("MINIO_PUBLIC_URL", "http://localhost:9000")

MINIO_BUCKET_EXPIRATION = int(os.getenv("MINIO_BUCKET_EXPIRATION", "1"))
MINIO_BUCKET_ANONYMOUS = os.getenv("MINIO_BUCKET_ANONYMOUS", "true").lower() in ("true", "1", "t")