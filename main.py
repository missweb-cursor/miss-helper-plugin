# main.py
import os
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from plugin import (
    echo_text, transform_text, translate_text, detect_language,
    summarize_text, extract_keywords, text_stats, http_get, regex_extract
)

PUBLISH_TOKEN = os.getenv("PUBLISH_TOKEN", "").strip()
APP_VERSION = "2.0.0"

app = FastAPI(title="miss_helper_plugin", version=APP_VERSION)

class InvokePayload(BaseModel):
    tool: str
    parameters: Dict[str, Any] = {}

def _auth(x_plugin_token: Optional[str]):
    if PUBLISH_TOKEN and (x_plugin_token or "") != PUBLISH_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/health")
def health():
    return {"ok": True, "status": "ok", "version": APP_VERSION}

@app.get("/tools")
def tools():
    # 简单静态返回，Dify 不强依赖这个接口
    return {"ok": True, "tools": [
        "echo_text","transform_text","translate_text","detect_language",
        "summarize_text","extract_keywords","text_stats","http_get","regex_extract"
    ]}

@app.post("/invoke")
def invoke(payload: InvokePayload, x_plugin_token: Optional[str] = Header(default=None)):
    _auth(x_plugin_token)
    t = (payload.tool or "").strip()
    p = payload.parameters or {}

    # Dify插件标准：直接返回工具的结果，不包装在{"ok": True, "result": ...}中
    if t == "echo_text":         return echo_text(p)
    if t == "transform_text":    return transform_text(p)
    if t == "translate_text":    return translate_text(p)
    if t == "detect_language":   return detect_language(p)
    if t == "summarize_text":    return summarize_text(p)
    if t == "extract_keywords":  return extract_keywords(p)
    if t == "text_stats":        return text_stats(p)
    if t == "http_get":          return http_get(p)
    if t == "regex_extract":     return regex_extract(p)

    raise HTTPException(status_code=404, detail=f"Unknown tool: {t}")

# 兼容某些运行环境把 entry 写成 main:run
run = app
