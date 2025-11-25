#!/usr/bin/env bash
set -euo pipefail

ACTION="ec2:RunInstances"
REGION="${AWS_REGION:-us-east-1}"
RESOURCE=""
VERBOSE=0

usage() {
  cat <<'EOF'
Usage: scripts/find_roles_with_runinstances.sh [-a action] [-r region] [-R resource_arn] [-v]

Lists IAM role ARNs that are allowed to call the specified AWS action (defaults to ec2:RunInstances)
by running `aws iam simulate-principal-policy` for every role in the account.

Options:
  -a action        AWS action to check (default: ec2:RunInstances)
  -r region        Region for the simulation / AWS CLI (default: $AWS_REGION or us-east-1)
  -R resource_arn  Optional resource ARN to include in the simulation
  -v               Verbose mode (print roles that are denied)
  -h               Show this help message

Requires AWS CLI credentials with permission to call iam:list-roles and iam:simulate-principal-policy.
EOF
}

while getopts ":a:r:R:vh" opt; do
  case "$opt" in
    a) ACTION="$OPTARG" ;;
    r) REGION="$OPTARG" ;;
    R) RESOURCE="$OPTARG" ;;
    v) VERBOSE=1 ;;
    h) usage; exit 0 ;;
    \?) echo "Invalid option: -$OPTARG" >&2; usage; exit 1 ;;
    :) echo "Option -$OPTARG requires an argument." >&2; usage; exit 1 ;;
  esac
done

if ! command -v aws >/dev/null 2>&1; then
  echo "aws CLI is required on PATH." >&2
  exit 1
fi

echo "Scanning IAM roles for '$ACTION' permission..."
role_arns=$(aws iam list-roles --query 'Roles[].Arn' --output text --no-paginate --region "$REGION" | tr '\t' '\n' | sed '/^$/d')

if [[ -z "$role_arns" ]]; then
  echo "No IAM roles found."
  exit 0
fi

allowed=()
denied=()

for role_arn in $role_arns; do
  args=(iam simulate-principal-policy --policy-source-arn "$role_arn" --action-names "$ACTION" --query 'EvaluationResults[0].EvalDecision' --output text --region "$REGION")
  if [[ -n "$RESOURCE" ]]; then
    args+=(--resource-arns "$RESOURCE")
  fi
  decision=$(aws "${args[@]}" 2>/dev/null || echo "error")
  if [[ "$decision" == "allowed" ]]; then
    allowed+=("$role_arn")
  else
    denied+=("$role_arn")
    if [[ $VERBOSE -eq 1 ]]; then
      echo "DENY: $role_arn ($decision)"
    fi
  fi
done

if [[ ${#allowed[@]} -eq 0 ]]; then
  echo "No roles allow $ACTION."
else
  echo "Roles allowing $ACTION:"
  for role in "${allowed[@]}"; do
    echo "  $role"
  done
fi

if [[ $VERBOSE -eq 1 && ${#denied[@]} -gt 0 ]]; then
  echo
  echo "Roles without permission:"
  for role in "${denied[@]}"; do
    echo "  $role"
  done
fi
