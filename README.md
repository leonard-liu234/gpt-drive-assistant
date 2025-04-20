
# GPT Drive Assistant (with OAuth Proxy)

## Features
- 📁 List all files recursively in a Google Drive folder
- 🧾 Generate confirmation letter PowerPoint
- 🌐 Proxy Google OAuth2 authentication
- 🔒 Works with GPT plugin authorization and ChatGPT Actions

## Deployment
1. Upload to Render or similar platform
2. Ensure `.well-known/ai-plugin.json` is served from `static/`
3. Set `GDRIVE_ACCESS_TOKEN` environment variable manually or via OAuth
4. Add `https://yourdomain.com/oauth/token` and `/authorize` to plugin auth endpoints

