# Security Policy

## Credentials

X browser cookies are authentication credentials. In particular, treat these values like passwords:

- `auth_token`
- `ct0`
- full `Cookie:` request headers

Do not post them in GitHub Issues, screenshots, logs, pull requests or chat transcripts.

## Reporting a security issue

If you discover a security problem, open an Issue only if the report can be written without exposing live credentials or private account data. Redact tokens, cookies, email addresses, phone numbers and private feed content.

## Repository policy

This repository does not intentionally contain:

- user cookies or tokens
- passwords or API secrets
- private recommendation-feed screenshots
- adult/sensitive media used as project presentation material

If a credential is accidentally exposed, revoke/rotate it before sharing any related logs publicly.
