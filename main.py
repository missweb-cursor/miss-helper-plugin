import os, json
from pathlib import Path
from typing import Any, Dict, Optional, List
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from plugin import (
    echo_text, transform_text, translate_text, detect_language,
    summarize_text, extract_keywords, text_stats, http_get, regex_extract
)

API_VERSION = "2.0.0"
PUBLISH_TOKEN = os.getenv("PUBLISH_TOKEN", "").strip()
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
PORT = int(os.getenv("PORT", "8000"))
CORS_ALLOW_ORIGINS = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")]

app = FastAPI(
    title="miss_砖哥助手 — Route B All-in-One",
    description="Managed-hosting plugin: echo, transform, translate, detect language, summarize, keywords, http_get, regex_extract, stats.",
    version=API_VERSION,
)

if CORS_ALLOW_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ALLOW_ORIGINS if CORS_ALLOW_ORIGINS != ["*"] else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

class InvokePayload(BaseModel):
    tool: str
    parameters: Dict[str, Any] = {}

def require_token(x_plugin_token: Optional[str]) -> None:
    if PUBLISH_TOKEN and (x_plugin_token or "") != PUBLISH_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized: invalid X-Plugin-Token")

@app.exception_handler(HTTPException)
async def http_exc_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"ok": False, "error": "http_error", "details": exc.detail})

@app.exception_handler(Exception)
async def any_exc_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"ok": False, "error": "server_error", "details": str(exc)})

@app.get("/")
def root():
    return {"ok": True, "app": "miss_砖哥助手", "version": API_VERSION}

@app.get("/health")
def health():
    return {"ok": True, "status": "ok", "mode": "managed", "version": API_VERSION, "port": PORT}

@app.get("/tools")
def tools():
    try:
        manifest = json.loads(Path(__file__).with_name("manifest.json").read_text(encoding="utf-8"))
        return {"ok": True, "tools": manifest.get("tools", [])}
    except Exception:
        return {"ok": True, "tools": [
            {"name": "echo_text"}, {"name": "transform_text"}, {"name": "translate_text"},
            {"name": "detect_language"}, {"name": "summarize_text"}, {"name": "extract_keywords"},
            {"name": "text_stats"}, {"name": "http_get"}, {"name": "regex_extract"}
        ]}

@app.post("/invoke")
def invoke(payload: InvokePayload, x_plugin_token: Optional[str] = Header(default=None)):
    require_token(x_plugin_token)
    tool = (payload.tool or "").strip()
    params = payload.parameters or {}

    if tool == "echo_text":
        return {"ok": True, "result": echo_text(params)}
    if tool == "transform_text":
        return {"ok": True, "result": transform_text(params)}
    if tool == "translate_text":
        return {"ok": True, "result": translate_text(params)}
    if tool == "detect_language":
        return {"ok": True, "result": detect_language(params)}
    if tool == "summarize_text":
        return {"ok": True, "result": summarize_text(params)}
    if tool == "extract_keywords":
        return {"ok": True, "result": extract_keywords(params)}
    if tool == "text_stats":
        return {"ok": True, "result": text_stats(params)}
    if tool == "http_get":
        return {"ok": True, "result": http_get(params)}
    if tool == "regex_extract":
        return {"ok": True, "result": regex_extract(params)}

    raise HTTPException(status_code=404, detail=f"Unknown tool: {tool}")

if __name__ == "__main__":
    import uvicorn
    print("=== miss_砖哥助手 插件 (Route B All-in-One) 启动 ===")
    print(f"端口: {PORT} | 日志: {LOG_LEVEL}")
    print("健康检查: http://127.0.0.1:{}/health".format(PORT))
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level=LOG_LEVEL)
