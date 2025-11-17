variable "aws_region" {
  type = string
}

variable "instance_type" {
  type    = string
  default = "g5.xlarge"
}

variable "instance_profile_name" {
  type = string
}

variable "key_name" {
  type = string
}

variable "image_uri_api" {
  type = string
}

variable "image_uri_alignscore" {
  type = string
}

variable "compose_project" {
  type    = string
  default = "pls"
}

variable "host_port_api" {
  type    = number
  default = 443
}

variable "host_port_alignscore" {
  type    = number
  default = 8443
}

variable "hf_endpoint_url" {
  type = string
}

variable "hf_token" {
  type = string
}

variable "alignscore_s3_uri" {
  type = string
}

variable "alignscore_ckpt_host_path" {
  type    = string
  default = "/opt/alignscore/AlignScore-base.ckpt"
}

variable "alignscore_ckpt_container_path" {
  type    = string
  default = "/assets/AlignScore-base.ckpt"
}
