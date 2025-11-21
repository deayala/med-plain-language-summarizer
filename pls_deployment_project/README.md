# PLS Deployment Project

End-to-end scaffold to serve the Plain Language Summarizer (PLS) via a managed Hugging Face Inference Endpoint. The layout mirrors `physionet-sepsis-forecasting-main` so the same automation (Makefile targets, Docker flows, Terraform plan) can be reused with minimal friction.

## Repository layout

```
pls_deployment_project/
├── Makefile                 # local tooling, Docker, ECR, Terraform helpers
├── app/                     # FastAPI service exposing /health and /summarize
├── services/alignscore/     # isolated AlignScore microservice (Python 3.10 + Torch 1.13)
├── artifacts/               # evaluation artifacts, curves, reports
├── aws/                     # IaC helpers / policy docs (placeholders)
├── data/                    # optional cached inputs (mirrors ref project)
├── docker-compose*.yml      # local + production compose stacks (GPU aware)
├── front/                   # reserved for UI (placeholder like reference)
├── infra/                   # Terraform stack targeting a cost-efficient t3.large EC2 instance
├── models/                  # production classifiers (TF-IDF logreg)
├── notebooks/               # notebooks + rendered reports
├── results/                 # eval summaries, readability metrics
├── scripts/                 # bash helpers (smoke tests, etc.)
├── src/                     # utility modules shared by the API
└── requirements*.txt        # runtime + tooling deps
```

Each Python module contains a lightweight validation section (`if __name__ == "__main__": ...`) so you can smoke-test the component after editing it. These self-checks never rewrite artifacts; they only read inputs and assert the environment looks sane to prevent accidental file clobbering.

## Quick start

1. **Set up env vars**
   ```bash
   cp .env.example .env
   # edit the following
   export AWS_REGION=us-east-1
   export HF_TOKEN=hf_xxx
    export HF_ENDPOINT_URL=https://xxx.aws.endpoints.huggingface.cloud
   # Optional: required only for OpenAI-compatible chat endpoints
   export HF_CHAT_MODEL_NAME=deayala/med-gemma-finetuned
   ```
2. **Create virtualenv and install deps**
   ```bash
   make install
   make checks  # runs pytest + mypy on lightweight stubs
   ```
3. **Serve locally** (FastAPI + HF endpoint)
   ```bash
   make serve  # uses uvicorn
   curl -X POST localhost:8080/api/v1/summarize -d '{"article": "..."}'
   ```
4. **Build + run container**
   ```bash
   make docker-build-api
   make docker-build-alignscore  # optional: local AlignScore service
   docker run -p 8080:80 \
     -e HF_ENDPOINT_URL=https://xxx.aws.endpoints.huggingface.cloud \
     -e HF_TOKEN=hf_xxx \
     pls-pls-api:latest
   ```
5. **Push to ECR & deploy on a CPU host**
   ```bash
   make ecr-push-api
   make ecr-push-alignscore
   # ALIGNSCORE_S3_URI defaults to s3://pls-deployment-artifacts/assets/alignscore/AlignScore-base.ckpt
   make ec2-deploy INSTANCE_TYPE=t3.large
   ```

> **Tip:** If `HF_ENDPOINT_URL` points to an OpenAI-compatible chat endpoint such as `vllm/vllm-openai` (`.../v1/chat/completions`), the API automatically switches to that payload and uses `HF_CHAT_MODEL_NAME` as the `model` parameter. No additional settings are required.

## Validations
- `app/config.py`: validates env vars + file paths on import.
- `app/generator.py`: runs device + dtype checks, exposes `/validate` endpoint for smoke testing.
- `scripts/smoke_test.sh`: hits `/health` and `/summarize` sequentially.
- Terraform user-data runs `docker compose ps` to ensure the stack is healthy before finishing cloud-init.

## API surface
- `POST /api/v1/summarize`: calls the managed HF endpoint (including OpenAI-compatible chat endpoints) and returns the generated PLS plus a Pydantic `ReadabilityBreakdown` with metrics for both the source article and generated PLS (Flesch, FKGL, Coleman-Liau, SMOG, Gunning Fog, Dale-Chall, average words per sentence, compression ratio, number recall, repetition ratio, jargon density).
- `POST /api/v1/classify`: loads `models/production/tfidf_logreg/model.joblib` to return whether an arbitrary text already looks like a PLS (`pls` vs `non_pls`) together with the probability score and threshold used.
- `POST /api/v1/classify/batch`: bulk classification (up to 128 snippets) backed by the same TF-IDF + logistic regression pipeline.

### AlignScore microservice
- Containerized separately under `services/alignscore/` to keep the main API on Python 3.11 while AlignScore runs on Python 3.10 + Torch 1.13.
- Build locally with `make docker-build-alignscore` (or `docker compose build alignscore`) and expose it via `docker compose up alignscore`. Mount the checkpoint file as a volume, e.g.:
  ```bash
  mkdir -p assets/alignscore && aws s3 cp s3://pls-deployment-artifacts/assets/alignscore/AlignScore-base.ckpt assets/alignscore/
  docker compose up -d alignscore \
    -e ALIGN_CHECKPOINT_PATH=/assets/AlignScore-base.ckpt \
    -v "$(pwd)/assets/alignscore/AlignScore-base.ckpt:/assets/AlignScore-base.ckpt:ro"
  ```
- Default endpoint: `POST /align` with JSON payload `{"technical_text": "...", "generation": "..."}` returns `{"align_score": 0.88, "model_name": "roberta-base", "device": "cpu", "batch_size": 4}`. The EC2 deployment exposes the service on `https://<host>:8443/align`.
- Configure the scorer through environment variables prefixed with `ALIGN_`:
  - `ALIGN_MODEL_NAME` (default `roberta-base`)
  - `ALIGN_BATCH_SIZE` (default `4`)
  - `ALIGN_DEVICE_PREFERENCE` (`cpu`, `cuda`, or `auto`)
  - `ALIGN_CHECKPOINT_PATH` (optional path inside the container to the AlignScore `.ckpt`; mount the checkpoint file or directory and point this variable to it).
- For infrastructure deployments, user data automatically downloads `s3://pls-deployment-artifacts/assets/alignscore/AlignScore-base.ckpt` into `/opt/alignscore/AlignScore-base.ckpt` (override via `ALIGNSCORE_S3_URI` or Terraform variables) and mounts it into the AlignScore container.

## Model inputs & outputs
- **Request** (`SummarizeRequest`): `article`, optional `best_of`, `temperature`, `max_new_tokens`.
- **Response**: `summary`, `latency_ms`, `generator` (gpu/cpu/hf-endpoint/dry-run), and `readability={source, generated}` where each entry mirrors the metrics collected in `notebooks/PLS_SFT_Colab_L4_Stable (3).ipynb`.

## Notes
- Hugging Face inference is the default, so the API can run on CPU-only EC2 instances; `DRY_RUN=1` keeps the readiness probes green when the endpoint or token is unavailable.
- The Terraform module provisions:
  - VPC + security group exposing 443
  - IAM instance profile granting access to CloudWatch + Secrets Manager (for the HF token)
  - A t3.large instance with a 100-GB gp3 volume, Docker, AWS CLI, and docker compose via user data
  - Systemd-managed Docker Compose stack pulling the image from ECR

- Refer to `docs/DEPLOYMENT.md` (to be added as artifacts evolve) for a step-by-step AWS console walkthrough.
