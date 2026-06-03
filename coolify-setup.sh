#!/usr/bin/env bash
# Coolify project creation script
COOLIFY_URL=***_URL:-http://178.156.135.237:8000}
TOKEN=***_TOKEN:-VpLNb5vWS44xj0s6BuySyRM4rbacCUssYe6NnYhZcfb39935}

echo "=== Creating Pacheco Mobile Mechanic project ==="
curl -s -X POST "$COOLIFY_URL/api/v1/projects" \
  -H "Authorization: Bearer ***  -H "Content-Type: application/json" \
  -d '{"name":"Pacheco Mobile Mechanic","description":"Mobile auto repair website - Barrie, ON"}'

echo ""
echo "=== Creating Carmens Maid Service project ==="
curl -s -X POST "$COOLIFY_URL/api/v1/projects" \
  -H "Authorization: Bearer ***  -H "Content-Type: application/json" \
  -d '{"name":"Carmens Maid Service","description":"Family-owned residential cleaning since 1987 - Barrie, ON"}'
