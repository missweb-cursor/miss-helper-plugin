# miss_helper_plugin

A ready-to-install Dify plugin (managed hosting).  
Tools: echo/transform/translate/detect/summarize/keywords/text-stats/http-get/regex.

## Endpoints
- `POST /invoke` — body: `{"tool": "<name>", "parameters": {...}}`
- `GET /health`

Auth (optional): set env `PUBLISH_TOKEN`; then send header `X-Plugin-Token: <token>`.
