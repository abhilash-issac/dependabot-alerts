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

# Initialize markdown summary
MARKDOWN_SUMMARY="| S.No | Org/Repo Name | Org Owners | Repo Admins | Alert Number | Secret Type | State | Alert URL |\n| ---- | ------------- | ---------- | ----------- | ------------ | ----------- | ----- | --------- |\n"

# Parse Dependabot alerts and add rows to the markdown summary
alert_number=1
for row in $(echo "${DEPENDABOT_ALERTS}" | jq -r '.[] | @base64'); do
    _jq() {
      echo ${row} | base64 --decode | jq -r ${1}
    }

    org_repo_name=$(echo "$ORG_OR_REPO" | tr '/' '|')
    alert_url=$(_jq '.html_url')
    secret_type=$(_jq '.security_advisory.vulnerability.package.ecosystem')
    state=$(_jq '.state')

    MARKDOWN_SUMMARY+="| $alert_number | $org_repo_name | | | $alert_number | $secret_type | $state | $alert_url |\n"
    alert_number=$((alert_number+1))
done

# Output the markdown summary
echo "::set-output name=summary::$MARKDOWN_SUMMARY"
