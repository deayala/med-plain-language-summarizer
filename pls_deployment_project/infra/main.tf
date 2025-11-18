terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  docker_compose_yaml = templatefile("${path.module}/docker-compose.yml.tftpl", {
    image_uri_api                  = var.image_uri_api,
    image_uri_alignscore           = var.image_uri_alignscore,
    image_uri_front                = var.image_uri_front,
    host_port_api                  = var.host_port_api,
    host_port_alignscore           = var.host_port_alignscore,
    host_port_front                = var.host_port_front,
    hf_endpoint_url                = var.hf_endpoint_url,
    hf_token                       = var.hf_token,
    alignscore_ckpt_host_path      = var.alignscore_ckpt_host_path,
    alignscore_ckpt_container_path = var.alignscore_ckpt_container_path
  })
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "pls_api" {
  name_prefix = "pls-api-"
  description = "Allow HTTP ingress"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "API HTTP"
    from_port   = var.host_port_api
    to_port     = var.host_port_api
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "AlignScore HTTPS"
    from_port   = var.host_port_alignscore
    to_port     = var.host_port_alignscore
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Frontend HTTP"
    from_port   = var.host_port_front
    to_port     = var.host_port_front
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "pls_g5" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.pls_api.id]
  iam_instance_profile        = var.instance_profile_name
  key_name                    = var.key_name
  associate_public_ip_address = true
  # instance_market_options {
  #   market_type = "spot"
  #   spot_options {
  #     instance_interruption_behavior = "terminate"
  #     spot_instance_type             = "one-time"
  #   }
  # }
  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    image_uri_api                  = var.image_uri_api,
    image_uri_alignscore           = var.image_uri_alignscore,
    image_uri_front                = var.image_uri_front,
    image_registry                 = split("/", var.image_uri_api)[0],
    compose_project                = var.compose_project,
    host_port_api                  = var.host_port_api,
    host_port_alignscore           = var.host_port_alignscore,
    host_port_front                = var.host_port_front,
    hf_endpoint_url                = var.hf_endpoint_url,
    hf_token                       = var.hf_token,
    aws_region                     = var.aws_region,
    alignscore_s3_uri              = var.alignscore_s3_uri,
    alignscore_ckpt_host_path      = var.alignscore_ckpt_host_path,
    alignscore_ckpt_container_path = var.alignscore_ckpt_container_path,
    docker_compose_yaml            = local.docker_compose_yaml
  })

  root_block_device {
    volume_size = 50
    volume_type = "gp3"
  }

  tags = {
    Name = "pls-cpu"
  }
}

data "aws_ami" "ubuntu" {
  owners      = ["099720109477"]
  most_recent = true
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}
