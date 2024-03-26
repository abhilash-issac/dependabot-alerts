import os
import requests

# Setup
ORG_NAME = os.getenv('INPUT_ORG_NAME')
REPO_NAME = os.getenv('INPUT_REPO_NAME')
GITHUB_TOKEN = os.getenv('INPUT_GITHUB_TOKEN')

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def fetch_paginated_api_data(url):
    all_data = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            all_data.extend(response.json())
            if 'next' in response.links.keys():
                url = response.links['next']['url']
            else:
                url = None
        else:
            print(f'Failed to fetch data: {response.status_code}')
            break
    return all_data

def fetch_user_details(users):
    user_details = []
    for user in users:
        url = f'https://api.github.com/users/{user["login"]}'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            user_details.append({
                'login': user_data.get('login'),
                'email': user_data.get('email')  # May be None if the email is not public
            })
        else:
            print(f'Failed to fetch user details for {user["login"]}: {response.status_code}')
    return user_details

def fetch_org_owners(org_name):
    owners = fetch_paginated_api_data(f'https://api.github.com/orgs/{org_name}/members?role=admin&per_page=100')
    return fetch_user_details(owners)

def fetch_repo_admins(full_repo_name):
    # Fetch direct collaborators with admin permissions
    admins = fetch_paginated_api_data(f'https://api.github.com/repos/{full_repo_name}/collaborators?affiliation=direct&per_page=100')
    return fetch_user_details(admins)

def fetch_dependabot_alerts(full_repo_name):
    return fetch_paginated_api_data(f'https://api.github.com/repos/{full_repo_name}/vulnerability-alerts')
    # return fetch_paginated_api_data(f'https://api.github.com/repos/{org_name}/{repo_name}/alerts')

def generate_markdown_summary(org_name, repo_name, dependabot_alerts, org_owners, repo_admins):
    markdown_lines = [
        "## Dependabot Alerts",
        "| SI No | Org/Repo Name | Org Owners | Repo Admins | Package Name | Severity | Summary | Status |\n")
        "|-------| ------------- | ---------- | ----------- |--------------|----------|---------|--------|\n")
    ]
    for index, alert in enumerate(dependabot_alerts, start=1):
        org_owners_str = ', '.join([f"{o['login']} ({o['email'] if o['email'] else 'No email'})" for o in org_owners])
        repo_admins_str = ', '.join([f"{a['login']} ({a['email'] if a['email'] else 'No email'})" for a in repo_admins])
        package_name = alert.get('repository').get('name')
        severity = alert.get('severity')
        summary = alert.get('vulnerability').get('title')
        status = alert.get('dismissed_at') or "Open"
        markdown_lines.append(
            f"| {index} | {org_name}/{repo_name} | {org_owners_str} | {repo_admins_str} | {package_name} | {severity} | {summary} | {status} |"
        )
    return "\n".join(markdown_lines)

def write_markdown_to_file(content, filename):
    with open(filename, 'w') as file:
        file.write(content)

def main():
    full_repo_name = f'{ORG_NAME}/{REPO_NAME}'
    dependabot_alerts = fetch_dependabot_alerts(full_repo_name)
    org_owners = fetch_org_owners(ORG_NAME)
    repo_admins = fetch_repo_admins(full_repo_name)
    
    markdown_summary = generate_markdown_summary(ORG_NAME, REPO_NAME, dependabot_alerts, org_owners, repo_admins)
    
    print(markdown_summary)
    write_markdown_to_file(markdown_summary, "security_report.md")

if __name__ == '__main__':
    main()
