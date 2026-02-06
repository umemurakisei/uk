from pydantic import BaseModel, Field

from backend.models import JobStatus


class JobCreateRequest(BaseModel):
    upload_job_id: str = Field(..., description="ID returned by POST /uploads")
    duration_seconds: int = Field(..., ge=1, le=600)
    style: str = Field(..., min_length=1, max_length=64)
    bgm_enabled: bool = True
    edit_instruction: str = Field(
        default="",
        max_length=500,
        description="Natural-language instruction used to auto-select effects/transitions/telops/music",
    )


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = Field(..., ge=0, le=100)
    error_code: str | None = None
    error_message: str | None = None
    retryable: bool | None = None


class JobResultResponse(BaseModel):
    job_id: str
    status: JobStatus
    result_url: str
