# QA Credentials for Browser Automation

Agents can use stored credentials to log in and explore protected routes (e.g. `/reports`) during browser-based QA.

## Setup

1. Copy the example file:
   ```bash
   cp frontend/qa-credentials.example.json frontend/qa-credentials.json
   ```

2. Edit `frontend/qa-credentials.json` with valid test credentials:
   - **APP_PASSWORD_HASH mode**: Any email works; use the configured password.
   - **APP_USERS_JSON mode**: Use an email/password from the configured users.

3. `qa-credentials.json` is gitignored — never commit it.

## Usage

When running browser automation (e.g. Cursor IDE browser), the agent reads `frontend/qa-credentials.json` and uses it to fill the login form before navigating to protected pages.
