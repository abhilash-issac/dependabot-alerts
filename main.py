import os
import requests
import json

# Setup
ORG_NAME = os.getenv('INPUT_ORG_NAME')
REPO_NAME = os.getenv('INPUT_REPO_NAME')
GITHUB_TOKEN = os.getenv('INPUT_GITHUB_TOKEN')

headers = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.vixen-preview+json',
    'Content-Type': 'application/json'
}

def execute_graphql_query(query, variables):
    request = requests.post('https://api.github.com/graphql', headers=headers, json={'query': query, 'variables': variables})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(f"Query failed to run by returning code of {request.status_code}. {request.text}")

def fetch_dependabot_alerts(owner, name):
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            vulnerabilityAlerts(first: 100) {
                edges {
                    node {
                        createdAt
                        dismissedAt
                        securityVulnerability {
                            package {
                                name
                            }
                            advisory {
                                summary
                                severity
                            }
                        }
                    }
                }
            }
        }
    }
    """
    variables = {
        "owner": owner,
        "name": name
    }
    data = execute_graphql_query(query, variables)
    alerts = data['data']['repository']['vulnerabilityAlerts']['edges']
    return alerts

def generate_markdown_summary(org_name, repo_name, alerts, org_owners, repo_admins):
    markdown_lines = [
        "## Dependabot Vulnerability Report",
        "| S.No | Org/Repo Name | Org Owners | Repo Admins | Package Name | Severity | Summary | Created At | Dismissed At |",
        "| ---- | ------------- | ---------- | ----------- | ------------ | -------- | ------- | ---------- | ------------ |"
    ]
    for index, edge in enumerate(alerts, start=1):
        node = edge['node']
        package_name = node['securityVulnerability']['package']['name']
        severity = node['securityVulnerability']['advisory']['severity']
        summary = node['securityVulnerability']['advisory']['summary']
        created_at = node['createdAt']
        dismissed_at = node['dismissedAt'] or "Not dismissed"

        org_owners_str = ', '.join([f"{o['login']} ({o['email'] if o['email'] else 'No email'})" for o in org_owners])
        repo_admins_str = ', '.join([f"{a['login']} ({a['email'] if a['email'] else 'No email'})" for a in repo_admins])

        markdown_lines.append(
            f"| {index} | {org_name}/{repo_name} | {org_owners_str} | {repo_admins_str} | "
            f"{package_name} | {severity} | {summary} | {created_at} | {dismissed_at} |"
        )
    return "\n".join(markdown_lines)

# The rest of the functions (fetch_user_details, fetch_org_owners, fetch_repo_admins) remain the same.

def main():
    alerts = fetch_dependabot_alerts(ORG_NAME, REPO_NAME)
    if not alerts:
        print("No Dependabot alerts to report.")
        return

    # Assuming org_owners and repo_admins are fetched similarly as before.
    org_owners = []  # Placeholder for actual call to fetch_org_owners
    repo_admins = []  # Placeholder for actual call to fetch_repo_admins

    markdown_summary = generate_markdown_summary(ORG_NAME, REPO_NAME, alerts, org_owners, repo_admins)
    print(markdown_summary)
    # Assume write_markdown_to_file function is defined similarly as before.
    write_markdown_to_file(markdown_summary, "dependabot_vulnerability_report.md")

if __name__ == '__main__':
    main()
