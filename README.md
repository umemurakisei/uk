# Video Job Platform Skeleton

- `backend/`: FastAPI API server (`/uploads`, `/jobs`, `/jobs/{id}`, `/jobs/{id}/result`)
- `worker/`: RQ worker that executes async video generation jobs
- `infra/`: Docker Compose for backend, worker, redis, and minio

## Run

```bash
cd infra
docker compose up --build
```

## API flow

1. `POST /uploads` with `multipart/form-data` (`file`) to upload an image and receive `job_id`.
2. `POST /jobs` with `upload_job_id`, `duration_seconds <= 600`, `style`, `bgm_enabled`.
3. Poll `GET /jobs/{id}` until status is `completed`.
4. Call `GET /jobs/{id}/result` to get the generated video URL.
