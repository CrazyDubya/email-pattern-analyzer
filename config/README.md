# Configuration Directory

This directory is for storing configuration files and credentials.

## Files That Go Here

### OAuth Credentials

- `credentials.json` - Gmail OAuth 2.0 credentials (from Google Cloud Console)
- `token.json` / `token.pickle` - Gmail authentication tokens (auto-generated)
- `outlook_token_cache.bin` - Outlook authentication cache (auto-generated)

### Custom Configurations

- Additional YAML configuration files
- Environment-specific configs (dev, prod, etc.)
- Custom category definitions

## Security Notes

⚠️ **IMPORTANT**: This directory may contain sensitive credentials!

- All credential files are in `.gitignore` and will NOT be committed
- Never share your `credentials.json` or token files
- If credentials are compromised, revoke them in:
  - Google Cloud Console (for Gmail)
  - Azure Portal (for Outlook)

## Setup Instructions

1. **Gmail Credentials**:
   - Download OAuth credentials from Google Cloud Console
   - Save as `config/credentials.json` or in project root
   - See `docs/configuration.md` for detailed setup

2. **Outlook Credentials**:
   - Get Client ID and Secret from Azure Portal
   - Add to `config.yaml` in project root
   - See `docs/configuration.md` for detailed setup

## File Permissions

On Unix-like systems, restrict access:

```bash
chmod 600 config/credentials.json
chmod 600 config/*.json
```

## Example Structure

```
config/
├── README.md (this file)
├── credentials.json (your Gmail OAuth credentials)
├── token.json (auto-generated Gmail token)
└── custom_categories.yaml (optional)
```
