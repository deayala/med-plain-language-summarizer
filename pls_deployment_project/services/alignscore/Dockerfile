FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /service

COPY services/alignscore/requirements.txt /tmp/requirements.txt

RUN python -m pip install --upgrade pip wheel setuptools && \
    python -m pip install -r /tmp/requirements.txt && \
    python -m spacy download en_core_web_sm && \
    python -m nltk.downloader punkt && \
    rm /tmp/requirements.txt

COPY services /service/services

ENV PYTHONPATH=/service

EXPOSE 8090
CMD ["uvicorn", "services.alignscore.app.main:app", "--host", "0.0.0.0", "--port", "8090"]
