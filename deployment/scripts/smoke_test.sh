#!/usr/bin/env bash
set -euo pipefail
HOST=${HOST:-http://localhost:8080}
HEALTH=$(curl -sS "$HOST/api/v1/health" | jq -r '.status')
if [[ "$HEALTH" != "ok" ]]; then
  echo "Health check failed" >&2
  exit 1
fi
PAYLOAD='{ "article": "'"Medical text "$(printf 'repeat ' %.0s {1..40})"'" }'
curl -sS -X POST "$HOST/api/v1/summarize" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD" | jq '.summary' >/dev/null
printf "Smoke test passed\n"
