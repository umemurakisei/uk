import os


def env(key: str, default: str) -> str:
    return os.getenv(key, default)


REDIS_URL = env("REDIS_URL", "redis://redis:6379/0")
MINIO_ENDPOINT = env("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = env("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = env("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = env("MINIO_BUCKET", "videos")
PUBLIC_BASE_URL = env("PUBLIC_BASE_URL", "http://localhost:9000")

JOB_MAX_TIMEOUT_SECONDS = int(env("JOB_MAX_TIMEOUT_SECONDS", "1800"))
SEGMENT_MAX_TIMEOUT_SECONDS = int(env("SEGMENT_MAX_TIMEOUT_SECONDS", "300"))
