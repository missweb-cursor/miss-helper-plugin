# plugin.py
import os, re, string, requests
from typing import Any, Dict, List
from collections import Counter
from pydantic import BaseModel, Field, ValidationError
from langdetect import detect  # 纯 Python，轻量

# -------- 参数模型 --------
class EchoParams(BaseModel):
    text: str = Field(..., description="Text to echo")

class TransformParams(BaseModel):
    text: str = Field(..., description="Text to transform")
    mode: str = Field("upper", description="upper|lower|reverse")

class TranslateParams(BaseModel):
    text: str = Field(..., description="Text to translate")
    target_lang: str = Field(..., description="Target language code")
    source_lang: str | None = Field(None, description="Source code (optional)")

class TextOnly(BaseModel):
    text: str = Field(..., description="Text")

class SummarizeParams(BaseModel):
    text: str
    sentences: int = 3

class KeywordParams(BaseModel):
    text: str
    top_k: int = 10

class HttpGetParams(BaseModel):
    url: str
    timeout: int = 15

class RegexParams(BaseModel):
    text: str
    pattern: str
    flags: List[str] = []

# -------- 工具实现 --------
def echo_text(params: Dict[str, Any]) -> Dict[str, Any]:
    p = EchoParams(**(params or {}))
    return {"echo": p.text}

def transform_text(params: Dict[str, Any]) -> Dict[str, Any]:
    p = TransformParams(**(params or {}))
    t = p.text or ""
    m = (p.mode or "upper").lower()
    if m == "upper":   out = t.upper()
    elif m == "lower": out = t.lower()
    elif m == "reverse": out = t[::-1]
    else: out = t
    return {"text": out, "mode": m}

def translate_text(params: Dict[str, Any]) -> Dict[str, Any]:
    p = TranslateParams(**(params or {}))
    api_url = os.getenv("TRANSLATE_API_URL", "https://libretranslate.com/translate").strip()
    payload = {"q": p.text, "source": p.source_lang or "auto", "target": p.target_lang, "format": "text"}
    api_key = os.getenv("TRANSLATE_API_KEY", "").strip()
    if api_key: payload["api_key"] = api_key
    r = requests.post(api_url, json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()
    txt = data.get("translatedText") or data.get("translated_text") or ""
    return {"translated": txt, "source_lang": payload["source"], "target_lang": payload["target"]}

def detect_language(params: Dict[str, Any]) -> Dict[str, Any]:
    p = TextOnly(**(params or {}))
    try:
        code = detect(p.text)
    except Exception:
        code = "unknown"
    return {"language": code}

def summarize_text(params: Dict[str, Any]) -> Dict[str, Any]:
    p = SummarizeParams(**(params or {}))
    sents = re.split(r'(?<=[.!?。！？])\s+', p.text.strip())
    if p.sentences <= 0: p.sentences = 1
    words = [w.strip(string.punctuation).lower() for w in re.findall(r"\w+", p.text)]
    stop = set("""a an the and or of to in on at for with by is are was were be been being this that these those
                  i you he she it we they me him her us them my your his its our their from as not no yes do does did
                  will would can could should have has had than then very just about into over under out up down off
                  if else but so because while when where who whom which what how""".split())
    scores = Counter(w for w in words if w and w not in stop)
    ranked = sorted(sents, key=lambda s: sum(scores.get(x.lower().strip(string.punctuation),0) for x in s.split()), reverse=True)
    summary = " ".join(ranked[:min(p.sentences, len(ranked))]) if sents else ""
    return {"summary": summary}

def extract_keywords(params: Dict[str, Any]) -> Dict[str, Any]:
    p = KeywordParams(**(params or {}))
    words = [w.lower() for w in re.findall(r"\w+", p.text)]
    stop = set("""a an the and or of to in on at for with by is are was were be been being this that these those
                  i you he she it we they me him her us them my your his its our their from as not no yes do does did
                  will would can could should have has had than then very just about into over under out up down off
                  if else but so because while when where who whom which what how""".split())
    freq = Counter(w for w in words if w and w not in stop)
    top = [{"keyword": w, "count": c} for w, c in freq.most_common(max(1, p.top_k))]
    return {"keywords": top}

def text_stats(params: Dict[str, Any]) -> Dict[str, Any]:
    p = TextOnly(**(params or {}))
    chars = len(p.text)
    words = len(re.findall(r"\w+", p.text))
    lines = len(p.text.splitlines()) if p.text else 0
    return {"characters": chars, "words": words, "lines": lines}

def http_get(params: Dict[str, Any]) -> Dict[str, Any]:
    p = HttpGetParams(**(params or {}))
    r = requests.get(p.url, timeout=max(1, min(60, p.timeout)))
    headers = {k: v for k, v in r.headers.items()}
    text_preview = r.text[:2000] if isinstance(r.text, str) else ""
    return {"status": r.status_code, "headers": headers, "text": text_preview}

def regex_extract(params: Dict[str, Any]) -> Dict[str, Any]:
    p = RegexParams(**(params or {}))
    flag_map = {"I": re.IGNORECASE, "M": re.MULTILINE, "S": re.DOTALL, "U": re.UNICODE,
                "X": re.VERBOSE, "A": re.ASCII}
    flags = 0
    for f in (p.flags or []):
        flags |= flag_map.get(f.upper(), 0)
    pat = re.compile(p.pattern, flags)
    matches = [m.group(0) for m in pat.finditer(p.text)]
    return {"matches": matches, "count": len(matches)}
