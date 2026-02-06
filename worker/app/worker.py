from redis import Redis
from rq import Connection, Worker

from common.config import REDIS_URL


def run() -> None:
    redis_client = Redis.from_url(REDIS_URL)
    with Connection(redis_client):
        worker = Worker(["video"])
        worker.work()


if __name__ == "__main__":
    run()
