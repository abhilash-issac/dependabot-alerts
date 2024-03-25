FROM alpine:latest

LABEL "com.github.actions.name"="Dependabot Alerts Fetcher"
LABEL "com.github.actions.description"="Fetch Dependabot alerts for an organization or repository"
LABEL "com.github.actions.icon"="inbox"
LABEL "com.github.actions.color"="blue"

LABEL "repository"="https://github.com/CanarysPlayground/dependabot-alerts"
LABEL "maintainer"="Abhilash Issac <abhilash.issac@ecanarys.com>"

RUN apk --no-cache add curl jq

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
