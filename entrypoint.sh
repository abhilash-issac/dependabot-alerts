#!/bin/sh

ORG_OR_REPO=$1
GITHUB_TOKEN=$2

if [ -z "$ORG_OR_REPO" ]; then
  echo "Organization or repository name not provided."
  exit 1
fi

if [ -z "$GITHUB_TOKEN" ]; then
  echo "GitHub token not provided."
  exit 1
fi

# Fetch Dependabot alerts
DEPENDABOT_ALERTS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/$ORG_OR_REPO/security/alerts" | jq '.')

echo "$DEPENDABOT_ALERTS"
