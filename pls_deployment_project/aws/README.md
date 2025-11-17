# AWS assets

- `infra/` contains Terraform targeting a single t3.large EC2 instance (adjust `INSTANCE_TYPE` as needed).
- Create an IAM instance profile named in `.env` with the following policies:
  - AmazonSSMManagedInstanceCore (optional but recommended)
  - SecretsManagerReadWrite or a scoped policy to retrieve the HF token
  - CloudWatchAgentServerPolicy (optional for logs)

The EC2 security group exposes HTTPS (443). Update `infra/main.tf` if you need SSH ingress for debugging.
