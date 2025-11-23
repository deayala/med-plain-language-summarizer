# PLS Deployment Project Folder - README

Plantilla completa para desplegar el Plain Language Summarizer (PLS) con FastAPI, un microservicio AlignScore y un front Angular+nginx empaquetados en Docker y orquestados con Compose sobre EC2. Incluye automatizaciones para construir y publicar imagenes en ECR y para provisionar la instancia via Terraform.

## Arquitectura

![Arquitectura](assets/pls_architecture.drawio.png)

- El usuario consume el front Angular servido por nginx, que reenvia `/api/*` a FastAPI.
- FastAPI expone `/summarize` y `/classify`; delega la generacion al endpoint gestionado de Hugging Face o usa `DRY_RUN`.
- El clasificador TF-IDF+LogReg se carga desde `models/production`.
- El microservicio AlignScore (Python 3.10 + Torch 1.13) calcula la similitud via `/align` usando un checkpoint descargado desde S3.
- Las tres imagenes (api, front, alignscore) se publican en ECR y se despliegan en un EC2 t3.large con Docker Compose (ver `infra/`).

## Componentes clave

- `app/main.py`: define el router FastAPI (`/health`, `/summarize`, `/classify`), aplica CORS/GZip y usa `PLSGenerator` + `BinaryPLSClassifier`.
- `app/config.py`: `Settings` valida variables (HF_ENDPOINT_URL, HF_TOKEN, DRY_RUN, rutas de modelo) y resume configuracion.
- `app/generator.py`: `PLSGenerator` elige cliente HF (`HFInferenceClient` o `OpenAIChatClient`) o `DummyGenerator` en `DRY_RUN`; calcula metricas de legibilidad y puntua candidatos.
- `app/schemas.py`: Pydantic DTOs para requests/responses y validaciones (minimo de palabras, rangos de hiperparametros).
- `src/classifier.py`: `BinaryPLSClassifier` carga el pipeline joblib y aplica un umbral configurable (`meta.json`).
- `src/readability.py`: calculo de metricas de legibilidad y densidad de jerga; tolera ausencia de `textstat`.
- `services/alignscore/app`: FastAPI aislado con `AlignScoreEngine` (carga lazy, deteccion de device, checkpoint opcional); expones `/align`.
- `front/`: proyecto Angular servido por nginx (`front/Dockerfile` hace build y copia a `/usr/share/nginx/html`; `nginx.conf` proxya `/api/` al servicio `api` en la red de Compose).
- `infra/`: Terraform que genera `docker-compose.yml` con las tres imagenes, instala Docker/Compose via cloud-init y descarga el checkpoint de AlignScore desde S3.
- `Makefile`: objetivos para instalar deps, correr pruebas, construir imagenes y empujar a ECR, y aplicar/destroy Terraform.

## Estructura del repositorio

```
pls_deployment_project/
├── app/                     # FastAPI (/health, /summarize, /classify)
├── services/alignscore/     # Microservicio AlignScore (FastAPI)
├── front/                   # Angular + nginx
├── infra/                   # Terraform (EC2 + user data + Compose)
├── scripts/                 # utilidades (p. ej., smoke_test.sh)
├── docker-compose.yml       # stack local (build)
├── docker-compose-prod.yml  # stack productivo (imagenes ya publicadas)
├── models/                  # artefactos del clasificador
├── assets/                  # diagramas e imagenes
└── Makefile                 # helpers de build, ECR y Terraform
```

## Preparacion local

1) Variables de entorno  
   ```
   cp .env.example .env
   export AWS_REGION=us-east-1
   export HF_TOKEN=hf_xxx
   export HF_ENDPOINT_URL=https://xxx.aws.endpoints.huggingface.cloud
   export HF_CHAT_MODEL_NAME=deayala/med-gemma-finetuned  # solo para endpoints /chat/completions
   ```
   Usa `DRY_RUN=1` si no tienes endpoint HF pero quieres probar la API.

2) Instalacion y chequeos rapidos  
   ```
   make install
   make checks       # ruff + mypy via tox
   make test         # pytest (ligero)
   ```

3) Ejecucion local  
   - API en caliente: `make serve` y prueba con `curl -X POST localhost:8080/api/v1/summarize -d '{"article": "..."}'`.
   - Stack Docker: `docker compose up -d` (construye api/front/alignscore). Ajusta `HF_ENDPOINT_URL`, `HF_TOKEN` y `ALIGN_CHECKPOINT_PATH` en tu entorno.
   - Microservicio AlignScore: monta el checkpoint (`ALIGN_CHECKPOINT_PATH`) o deja `DRY_RUN` en la API si no necesitas scoring.

## Construccion de imagenes y publicacion en ECR

- Variables principales en `Makefile`:
  - `API_IMAGE/ALIGN_IMAGE/FRONT_IMAGE` y `*_TAG` para nombres locales.
  - `AWS_ACCOUNT_ID`, `AWS_REGION` y `ECR_URI` para apuntar a tu cuenta.
  - `*_ECR_REPO` controla el nombre de cada repo en ECR (por defecto coincide con el nombre local).
- Login en ECR: `make ecr-login`.
- Construccion local:
  ```
  make docker-build-api
  make docker-build-alignscore
  make docker-build-front   # Angular -> nginx (usa front/Dockerfile)
  ```
- Publicar en ECR (incluye el front-end, faltante anteriormente):
  ```
  make ecr-push-api
  make ecr-push-alignscore
  make ecr-push-front
  # o todo de una: make ecr-push-all
  ```
- Las variables `API_IMAGE_URI`, `ALIGN_IMAGE_URI` y `FRONT_IMAGE_URI` se derivan de cuenta/region/tag y se pasan a Terraform y a `docker-compose-prod.yml`.

## Despliegue en AWS (Terraform + Makefile)

Requisitos: AWS CLI configurado, rol/instance profile con acceso a ECR + S3 (para el checkpoint AlignScore) y par de llaves EC2 (`KEY_NAME`).

1) Prepara las imagenes en ECR (ver seccion anterior) y define `HF_ENDPOINT_URL` y `HF_TOKEN` en tu shell.  
2) Lanza la instancia via Makefile (usa t3.large por defecto; puedes cambiar `INSTANCE_TYPE`):
   ```
   make ec2-deploy \
     HF_ENDPOINT_URL=https://xxx.aws.endpoints.huggingface.cloud \
     HF_TOKEN=hf_xxx \
     INSTANCE_TYPE=t3.large \
     ALIGNSCORE_S3_URI=s3://.../AlignScore-base.ckpt \
     HOST_PORT_FRONT=80 HOST_PORT_API=8080 HOST_PORT_ALIGNSCORE=8081
   ```
   - Terraform renderiza `infra/docker-compose.yml.tftpl` con las URIs de las tres imagenes.
   - El user-data instala Docker/Compose, hace login en ECR, descarga el checkpoint a `alignscore_ckpt_host_path` (por defecto `/opt/alignscore/AlignScore-base.ckpt`) y levanta el stack en `/opt/${compose_project}`.
   - Seguridad: el SG abre los puertos `HOST_PORT_FRONT`, `HOST_PORT_API` y `HOST_PORT_ALIGNSCORE`; ajusta si necesitas HTTPS/ALB.
3) Validación remota: `ssh` a la instancia y ejecuta `docker compose -f /opt/pls/docker-compose.yml ps` y `curl http://localhost:8080/api/v1/health`.
4) Para destruir: `make destroy-infra` (o `make ec2-destroy` si solo se desea borrar la instancia).

## Endpoints y pruebas rapidas

- API:
  - `GET /api/v1/health`
  - `POST /api/v1/summarize` (recibe `article`, acepta overrides de hiperparametros)
  - `POST /api/v1/classify` (usa `BinaryPLSClassifier`)
- AlignScore: `POST /align` con `technical_text` y `generation`; responde `align_score`, `model_name`, `device`, `batch_size`.
- Smoke test: `./scripts/smoke_test.sh` golpea `/health` y `/summarize`.

## Notas y buenas practicas

- `.env` carga secretos (HF_TOKEN, credenciales) via `app/config.py`; no se deben subir secretos al repositorio.
- El modelo de clasificacion se encuentra en `models/production/tfidf_logreg`; si se desea usar otro bucket, se debe montar y descarga antes de levantar el contenedor.
- `DRY_RUN=1` mantiene liveness aun sin endpoint HF para pruebas sin inferir en altos costos.
- Ajusta `HOST_PORT_*` y `compose_project` en `Makefile`/Terraform para evitar conflictos de puertos en EC2.
