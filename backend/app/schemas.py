from pydantic import BaseModel, Field


class JobCreateRequest(BaseModel):
    upload_job_id: str = Field(..., description="ID returned by POST /uploads")
    duration_seconds: int = Field(..., ge=1, le=600)
    style: str = Field(..., min_length=1, max_length=64)
    bgm_enabled: bool = True


class JobCreateResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    error: str | None = None


class JobResultResponse(BaseModel):
    job_id: str
    status: str
    result_url: str
