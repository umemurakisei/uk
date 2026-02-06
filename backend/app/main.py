from __future__ import annotations

import uuid
from datetime import datetime, timezone

import boto3
from botocore.client import Config
from fastapi import FastAPI, File, HTTPException, UploadFile
from redis import Redis
from rq import Queue
from rq.retry import Retry

from backend.models import JobStatus
from common.config import (
    JOB_MAX_TIMEOUT_SECONDS,
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    PUBLIC_BASE_URL,
    REDIS_URL,
)
from common.job_store import get_job, set_job
from .schemas import JobCreateRequest, JobCreateResponse, JobResultResponse, JobStatusResponse

app = FastAPI(title="Video Generation Backend")

redis_client = Redis.from_url(REDIS_URL)
queue = Queue("video", connection=redis_client)

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)


def ensure_bucket() -> None:
    existing = [bucket["Name"] for bucket in s3_client.list_buckets().get("Buckets", [])]
    if MINIO_BUCKET not in existing:
        s3_client.create_bucket(Bucket=MINIO_BUCKET)


@app.on_event("startup")
def startup_event() -> None:
    ensure_bucket()


@app.post("/uploads")
async def create_upload_job(file: UploadFile = File(...)) -> dict[str, str]:
    upload_job_id = str(uuid.uuid4())
    object_key = f"uploads/{upload_job_id}_{file.filename}"
    payload = await file.read()
    s3_client.put_object(Bucket=MINIO_BUCKET, Key=object_key, Body=payload, ContentType=file.content_type)

    set_job(
        redis_client,
        upload_job_id,
        {
            "id": upload_job_id,
            "type": "upload",
            "status": "uploaded",
            "progress": 100,
            "source_object": object_key,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    return {"job_id": upload_job_id}


@app.post("/jobs", response_model=JobCreateResponse)
def create_video_job(request: JobCreateRequest) -> JobCreateResponse:
    source_job = get_job(redis_client, request.upload_job_id)
    if not source_job or source_job.get("type") != "upload":
        raise HTTPException(status_code=404, detail="upload_job_id not found")

    job_id = str(uuid.uuid4())
    set_job(
        redis_client,
        job_id,
        {
            "id": job_id,
            "type": "video",
            "status": JobStatus.QUEUED,
            "progress": 0,
            "source_upload_job_id": request.upload_job_id,
            "source_object": source_job["source_object"],
            "duration_seconds": request.duration_seconds,
            "style": request.style,
            "bgm_enabled": request.bgm_enabled,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    queue.enqueue(
        "worker.app.tasks.generate_video",
        job_id,
        source_job["source_object"],
        request.duration_seconds,
        request.style,
        request.bgm_enabled,
        job_timeout=JOB_MAX_TIMEOUT_SECONDS,
        retry=Retry(max=3, interval=[2, 4, 8]),
    )

    return JobCreateResponse(job_id=job_id, status=JobStatus.QUEUED)


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str) -> JobStatusResponse:
    job = get_job(redis_client, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    retryable = job.get("retryable")
    status_raw = job.get("status", JobStatus.FAILED)
    status = JobStatus(status_raw) if status_raw in JobStatus._value2member_map_ else JobStatus.FAILED
    return JobStatusResponse(
        job_id=job_id,
        status=status,
        progress=int(job.get("progress", 0)),
        error_code=job.get("error_code"),
        error_message=job.get("error_message"),
        retryable=(retryable.lower() == "true") if retryable is not None else None,
    )


@app.get("/jobs/{job_id}/result", response_model=JobResultResponse)
def get_job_result(job_id: str) -> JobResultResponse:
    job = get_job(redis_client, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job.get("status") != JobStatus.SUCCEEDED:
        raise HTTPException(status_code=409, detail="job is not succeeded")

    result_object = job.get("result_object")
    if not result_object:
        raise HTTPException(status_code=500, detail="result not found")

    result_url = f"{PUBLIC_BASE_URL}/{MINIO_BUCKET}/{result_object}"
    return JobResultResponse(job_id=job_id, status=JobStatus.SUCCEEDED, result_url=result_url)
