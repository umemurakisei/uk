from __future__ import annotations

import time
from pathlib import Path
from tempfile import TemporaryDirectory

import boto3
from botocore.client import Config
from redis import Redis

from common.config import (
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    REDIS_URL,
)
from common.job_store import update_job
from worker.pipeline import generate_video_from_image

redis_client = Redis.from_url(REDIS_URL)

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)


def generate_video(
    job_id: str,
    source_object: str,
    duration_seconds: int,
    style: str,
    bgm_enabled: bool,
) -> None:
    try:
        update_job(redis_client, job_id, status="processing", progress=10)
        time.sleep(1)
        update_job(redis_client, job_id, progress=40)

        source = s3_client.get_object(Bucket=MINIO_BUCKET, Key=source_object)["Body"].read()
        time.sleep(1)
        update_job(redis_client, job_id, progress=70)

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            image_path = temp_path / "source_image.jpg"
            image_path.write_bytes(source)
            output_path = temp_path / "result.mp4"

            generate_video_from_image(
                {
                    "duration_sec": duration_seconds,
                    "style": style,
                    "bgm_enabled": bgm_enabled,
                    "image_path": str(image_path),
                    "output_path": str(output_path),
                }
            )
            result_bytes = output_path.read_bytes()

        result_key = f"results/{job_id}.mp4"
        s3_client.put_object(Bucket=MINIO_BUCKET, Key=result_key, Body=result_bytes, ContentType="video/mp4")

        update_job(redis_client, job_id, status="completed", progress=100, result_object=result_key)
    except Exception as exc:
        update_job(redis_client, job_id, status="failed", error=str(exc), progress=100)
        raise
