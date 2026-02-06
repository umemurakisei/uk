FROM python:3.11-slim

WORKDIR /app
COPY worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY common /app/common
COPY worker/app /app/worker/app

ENV PYTHONPATH=/app
CMD ["python", "-m", "worker.app.worker"]
