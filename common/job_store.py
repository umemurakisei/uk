from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from redis import Redis


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _serialize(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def set_job(redis_client: Redis, job_id: str, payload: dict[str, Any]) -> None:
    key = f"job:{job_id}"
    data = {k: _serialize(v) for k, v in payload.items()}
    redis_client.hset(key, mapping=data)


def get_job(redis_client: Redis, job_id: str) -> dict[str, str] | None:
    key = f"job:{job_id}"
    data = redis_client.hgetall(key)
    if not data:
        return None
    return {
        (k.decode() if isinstance(k, bytes) else str(k)): (
            v.decode() if isinstance(v, bytes) else str(v)
        )
        for k, v in data.items()
    }


def update_job(redis_client: Redis, job_id: str, **fields: Any) -> None:
    fields["updated_at"] = utc_now()
    set_job(redis_client, job_id, fields)
