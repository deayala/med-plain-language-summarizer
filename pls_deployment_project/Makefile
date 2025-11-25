# ---------- VARS ----------
PY=python3
PIP=pip3
VENV=.venv
ACTIVATE=. $(VENV)/bin/activate
UVICORN=uvicorn

API_IMAGE=pls-pls-api
API_TAG=latest
ALIGN_IMAGE=pls-alignscore
ALIGN_TAG=latest
FRONT_IMAGE=pls-front
FRONT_TAG=latest
API_ECR_REPO=$(API_IMAGE)
ALIGN_ECR_REPO=$(ALIGN_IMAGE)
FRONT_ECR_REPO=$(FRONT_IMAGE)
AWS_REGION?=us-east-1
AWS_ACCOUNT_ID?=819245732164
ECR_URI=$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
API_IMAGE_URI=$(ECR_URI)/$(API_ECR_REPO):$(API_TAG)
ALIGN_IMAGE_URI=$(ECR_URI)/$(ALIGN_ECR_REPO):$(ALIGN_TAG)
FRONT_IMAGE_URI=$(ECR_URI)/$(FRONT_ECR_REPO):$(FRONT_TAG)
INSTANCE_TYPE?=t3.large
INSTANCE_PROFILE_NAME?=LabInstanceProfile
KEY_NAME?=PLS_DEPLOYMENT
PROJECT_NAME=pls
HOST_PORT_API?=8080
HOST_PORT_ALIGNSCORE?=8081
HOST_PORT_FRONT?=80
ALIGNSCORE_S3_URI?=s3://pls-deployment-artifacts/assets/alignscore/AlignScore-base.ckpt

DOCKER_COMPOSE=docker compose

.PHONY: help venv install serve docker-build-api docker-build-alignscore docker-build-front docker-run up down logs ps test checks clean \
 ecr-login ecr-create-api ecr-create-alignscore ecr-create-front ecr-push-api ecr-push-alignscore ecr-push-front ecr-push-all ec2-deploy ec2-destroy destroy-infra smoke

help:
	@echo "PLS deployment helper targets"
	@echo "make install                   # create venv + install deps"
	@echo "make serve                     # run FastAPI locally"
	@echo "make test/checks               # tox wrappers"
	@echo "make docker-build-api          # build inference image"
	@echo "make docker-build-alignscore   # build AlignScore microservice image"
	@echo "make docker-build-front        # build Angular front-end image"
	@echo "make up/down                   # docker compose up/down"
	@echo "make ecr-push-api              # push API image to ECR"
	@echo "make ecr-push-alignscore       # push AlignScore image to ECR"
	@echo "make ecr-push-front            # push front-end image to ECR"
	@echo "make ec2-deploy                # terraform apply targeting CPU t3.large"
	@echo "make destroy-infra             # terraform destroy for all infra resources"

venv:
	$(PY) -m venv $(VENV)

install: venv
	$(ACTIVATE) && $(PIP) install --upgrade pip
	$(ACTIVATE) && $(PIP) install -r requirements.txt

serve:
	$(ACTIVATE) && $(UVICORN) app.main:app --host 0.0.0.0 --port 8080 --reload

smoke:
	./scripts/smoke_test.sh

# ---------- Docker ----------
docker-build-api:
	docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t $(API_IMAGE):$(API_TAG) -f app/Dockerfile .

docker-build-alignscore:
	docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t $(ALIGN_IMAGE):$(ALIGN_TAG) -f services/alignscore/Dockerfile .

docker-build-front:
	docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t $(FRONT_IMAGE):$(FRONT_TAG) -f front/Dockerfile front

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

ps:
	$(DOCKER_COMPOSE) ps

docker-run:
	docker run --rm -p 8080:80 \
		-e HF_ENDPOINT_URL=$${HF_ENDPOINT_URL} \
		-e HF_TOKEN=$${HF_TOKEN} \
		$(API_IMAGE):$(API_TAG)

# ---------- Testing ----------
test:
	$(ACTIVATE) && tox -e test_app

checks:
	$(ACTIVATE) && tox -e checks

# ---------- ECR ----------
ecr-login:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_URI)

ecr-create-api:
	-aws ecr describe-repositories --repository-names $(API_ECR_REPO) --region $(AWS_REGION) >/dev/null 2>&1 || \
	  aws ecr create-repository --repository-name $(API_ECR_REPO) --region $(AWS_REGION)

ecr-create-alignscore:
	-aws ecr describe-repositories --repository-names $(ALIGN_ECR_REPO) --region $(AWS_REGION) >/dev/null 2>&1 || \
	  aws ecr create-repository --repository-name $(ALIGN_ECR_REPO) --region $(AWS_REGION)

ecr-create-front:
	-aws ecr describe-repositories --repository-names $(FRONT_ECR_REPO) --region $(AWS_REGION) >/dev/null 2>&1 || \
	  aws ecr create-repository --repository-name $(FRONT_ECR_REPO) --region $(AWS_REGION)

ecr-push-api: docker-build-api ecr-create-api ecr-login
	docker tag $(API_IMAGE):$(API_TAG) $(API_IMAGE_URI)
	docker push $(API_IMAGE_URI)

ecr-push-alignscore: docker-build-alignscore ecr-create-alignscore ecr-login
	docker tag $(ALIGN_IMAGE):$(ALIGN_TAG) $(ALIGN_IMAGE_URI)
	docker push $(ALIGN_IMAGE_URI)

ecr-push-front: docker-build-front ecr-create-front ecr-login
	docker tag $(FRONT_IMAGE):$(FRONT_TAG) $(FRONT_IMAGE_URI)
	docker push $(FRONT_IMAGE_URI)

ecr-push-all: ecr-push-api ecr-push-alignscore ecr-push-front
	@echo "Pushed API -> $(API_IMAGE_URI)"
	@echo "Pushed AlignScore -> $(ALIGN_IMAGE_URI)"
	@echo "Pushed Front -> $(FRONT_IMAGE_URI)"

# ---------- Terraform ----------
ec2-deploy:
	terraform -chdir=infra init -upgrade
	terraform -chdir=infra apply -auto-approve \
		-var "aws_region=$(AWS_REGION)" \
		-var "instance_type=$(INSTANCE_TYPE)" \
		-var "instance_profile_name=$(INSTANCE_PROFILE_NAME)" \
		-var "key_name=$(KEY_NAME)" \
		-var "image_uri_api=$(API_IMAGE_URI)" \
		-var "image_uri_alignscore=$(ALIGN_IMAGE_URI)" \
		-var "image_uri_front=$(FRONT_IMAGE_URI)" \
		-var "host_port_api=$(HOST_PORT_API)" \
		-var "host_port_alignscore=$(HOST_PORT_ALIGNSCORE)" \
		-var "host_port_front=$(HOST_PORT_FRONT)" \
		-var "compose_project=$(PROJECT_NAME)" \
		-var "hf_endpoint_url=$(HF_ENDPOINT_URL)" \
		-var "hf_token=$(HF_TOKEN)" \
		-var "alignscore_s3_uri=$(ALIGNSCORE_S3_URI)"

ec2-destroy:
	terraform -chdir=infra destroy -auto-approve -var "aws_region=$(AWS_REGION)"

destroy-infra:
	terraform -chdir=infra destroy -auto-approve \
		-var "aws_region=$(AWS_REGION)" \
		-var "instance_type=$(INSTANCE_TYPE)" \
		-var "instance_profile_name=$(INSTANCE_PROFILE_NAME)" \
		-var "key_name=$(KEY_NAME)" \
		-var "image_uri_api=$(API_IMAGE_URI)" \
		-var "image_uri_alignscore=$(ALIGN_IMAGE_URI)" \
		-var "image_uri_front=$(FRONT_IMAGE_URI)" \
		-var "host_port_api=$(HOST_PORT_API)" \
		-var "host_port_alignscore=$(HOST_PORT_ALIGNSCORE)" \
		-var "host_port_front=$(HOST_PORT_FRONT)" \
		-var "compose_project=$(PROJECT_NAME)" \
		-var "hf_endpoint_url=$(HF_ENDPOINT_URL)" \
		-var "hf_token=$(HF_TOKEN)" \
		-var "alignscore_s3_uri=$(ALIGNSCORE_S3_URI)"

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache __pycache__
	docker image prune -f >/dev/null 2>&1 || true
