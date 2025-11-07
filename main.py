# main.py
import os
from typing import Any, Callable, Dict, Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from plugin import (
    echo_text, transform_text, translate_text, detect_language,
    summarize_text, extract_keywords, text_stats, http_get, regex_extract
)

# 环境变量配置
PUBLISH_TOKEN = os.getenv("PUBLISH_TOKEN", "").strip()
APP_VERSION = "2.0.0"
CORS_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*").strip()

app = FastAPI(title="miss_helper_plugin", version=APP_VERSION)

# CORS 配置
origins = [origin.strip() for origin in CORS_ORIGINS.split(",")] if CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InvokePayload(BaseModel):
    tool: Optional[str] = None
    tool_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    arguments: Optional[Dict[str, Any]] = None

    def resolved_tool(self) -> str:
        return (self.tool or self.tool_name or "").strip()

    def resolved_params(self) -> Dict[str, Any]:
        for candidate in (self.parameters, self.arguments):
            if isinstance(candidate, dict) and candidate:
                return candidate
        return {}


TOOL_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    "echo_text": echo_text,
    "transform_text": transform_text,
    "translate_text": translate_text,
    "detect_language": detect_language,
    "summarize_text": summarize_text,
    "extract_keywords": extract_keywords,
    "text_stats": text_stats,
    "http_get": http_get,
    "regex_extract": regex_extract,
}

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
    tool_name = payload.resolved_tool()
    if not tool_name:
        raise HTTPException(status_code=422, detail="`tool` (or `tool_name`) is required")

    handler = TOOL_REGISTRY.get(tool_name)
    if handler is None:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")

    try:
        result = handler(payload.resolved_params())
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={"message": "Invalid parameters", "errors": exc.errors()},
        ) from exc

    return {"type": "object", "result": result, "tool_name": tool_name}
    main

    # 兼容某些运行环境把 entry 写成 main:run
    run = app
