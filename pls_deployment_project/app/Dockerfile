FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3.11 python3.11-venv python3-pip git curl && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m api-user
WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

USER api-user

COPY app /app/app
COPY src /app/src
COPY models/production /app/models/production

ENV HF_HOME=/app/.cache/huggingface

EXPOSE 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
