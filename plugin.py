from typing import Any, Dict, List
from pydantic import BaseModel, Field, ValidationError
from collections import Counter
import os, re, requests

# --------- Param Models ---------
class EchoParams(BaseModel):
    text: str = Field(..., description="Text to echo back")

class TransformParams(BaseModel):
    text: str = Field(..., description="Text to transform")
    mode: str = Field("upper", description="Transform mode: upper|lower|reverse")

class TranslateParams(BaseModel):
    text: str = Field(..., description="Text to translate")
    target_lang: str = Field(..., description="Target language code, e.g. en, zh, ja, es")
    source_lang: str | None = Field(None, description="Source language code (optional), e.g. auto, en")

class DetectLangParams(BaseModel):
    text: str = Field(..., description="Text to detect language for")

class SummarizeParams(BaseModel):
    text: str = Field(..., description="Text to summarize")
    sentences: int = Field(3, ge=1, le=10, description="Number of summary sentences (1-10)")

class KeywordsParams(BaseModel):
    text: str = Field(..., description="Text to extract keywords from")
    top_k: int = Field(10, ge=1, le=50, description="How many keywords to return")

class TextStatsParams(BaseModel):
    text: str = Field(..., description="Text to analyze")

class HttpGetParams(BaseModel):
    url: str = Field(..., description="HTTP/HTTPS URL to fetch")
    timeout: int = Field(15, ge=1, le=60, description="Request timeout seconds")

class RegexExtractParams(BaseModel):
    text: str = Field(..., description="Text to search")
    pattern: str = Field(..., description="Python regex pattern")
    flags: List[str] = Field(default_factory=list, description="Regex flags: I,M,S,U,X,A (case, multiline, dotall, unicode, verbose, ascii)")

# --------- Helpers ---------
_STOPWORDS = set("""
a an the and or but if while of in on at to for with from by as is are was were be been being
I you he she it we they me him her us them this that these those here there then now so because
的 了 和 是 在 有 我 你 他 她 我们 你们 他们 这些 那些 这种 那种
""".split())

def _tokenize(text: str) -> List[str]:
    # Simple tokenizer: words & CJK chars
    tokens = re.findall(r"[A-Za-z0-9_]+|[一-鿿]", text)
    return [t.lower() for t in tokens if t.strip()]

def _score_sentences(text: str) -> List[tuple]:
    sentences = re.split(r"(?<=[。！？.!?])\s*", text.strip())
    tokens = _tokenize(text)
    freqs = Counter(t for t in tokens if t not in _STOPWORDS and not t.isdigit())
    scores = []
    for s in sentences:
        if not s.strip():
            continue
        s_tokens = _tokenize(s)
        score = sum(freqs.get(t, 0) for t in s_tokens)
        scores.append((score, s))
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores

def _compile_flags(flags: List[str]) -> int:
    f = 0
    mapping = {"I": re.IGNORECASE, "M": re.MULTILINE, "S": re.DOTALL, "U": re.UNICODE, "X": re.VERBOSE, "A": re.ASCII}
    for fl in flags:
        up = fl.upper()
        if up in mapping:
            f |= mapping[up]
    return f

# --------- Tool Implementations ---------
def echo_text(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        p = EchoParams(**(params or {}))
    except ValidationError as e:
        return {"error": "validation_error", "details": e.errors()}
    return {"echo": p.text}

def transform_text(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        p = TransformParams(**(params or {}))
    except ValidationError as e:
        return {"error": "validation_error", "details": e.errors()}
    t = p.text or ""
    m = (p.mode or "upper").lower()
    if m == "upper":
        out = t.upper()
    elif m == "lower":
        out = t.lower()
    elif m == "reverse":
        out = t[::-1]
    else:
        return {"error": "unsupported_mode", "details": {"mode": p.mode, "allowed": ["upper","lower","reverse"]}}
    return {"text": out}

def translate_text(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    LibreTranslate-compatible translation.
    Works out-of-the-box using public demo endpoint unless TRANSLATE_API_URL is set.
    """
    try:
        p = TranslateParams(**(params or {}))
    except ValidationError as e:
        return {"error": "validation_error", "details": e.errors()}

    api_url = os.getenv("TRANSLATE_API_URL", "https://libretranslate.de/translate").strip()
    payload = {"q": p.text, "source": p.source_lang or "auto", "target": p.target_lang, "format": "text"}
    api_key = os.getenv("TRANSLATE_API_KEY", "").strip()
    if api_key:
        payload["api_key"] = api_key

    try:
        resp = requests.post(api_url, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as ex:
        return {"error": "http_error", "details": str(ex)}

    translated = data.get("translatedText") or data.get("translated_text")
    if not translated:
        return {"error": "unexpected_response", "details": data}
    return {"translated": translated, "source_lang": payload["source"], "target_lang": payload["target"]}

def detect_language(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        p = DetectLangParams(**(params or {}))
    except ValidationError as e:
        return {"error": "validation_error", "details": e.errors()}
    try:
        from langdetect import detect, detect_langs
        code = detect(p.text)
        candidates = [str(x) for x in detect_langs(p.text)]
        return {"language": code, "candidates": candidates}
    except Exception as ex:
        return {"error": "langdetect_error", "details": str(ex)}

def summarize_text(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        p = SummarizeParams(**(params or {}))
    except ValidationError as e:
        return {"error": "validation_error", "details": e.errors()}
    ranked = _score_sentences(p.text)
    if not ranked:
        return {"summary": ""}
    summary_sents = [s for _, s in ranked[:p.sentences]]
    return {"summary": " ".join(summary_sents)}

def extract_keywords(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        p = KeywordsParams(**(params or {}))
    except ValidationError as e:
        return {"error": "validation_error", "details": e.errors()}
    tokens = [t for t in _tokenize(p.text) if t not in _STOPWORDS and not t.isdigit()]
    common = Counter(tokens).most_common(p.top_k)
    return {"keywords": [{"token": t, "count": int(c)} for t, c in common]}

def text_stats(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        p = TextStatsParams(**(params or {}))
    except ValidationError as e:
        return {"error": "validation_error", "details": e.errors()}
    chars = len(p.text)
    words = len(re.findall(r"\w+", p.text, flags=re.UNICODE))
    lines = len(p.text.splitlines())
    return {"chars": chars, "words": words, "lines": lines}

def http_get(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        p = HttpGetParams(**(params or {}))
    except ValidationError as e:
        return {"error": "validation_error", "details": e.errors()}
    if not (p.url.startswith("http://") or p.url.startswith("https://")):
        return {"error": "invalid_url", "details": "Only http/https is allowed"}
    try:
        r = requests.get(p.url, timeout=p.timeout)
        preview = r.text[:2000] if isinstance(r.text, str) else ""
        return {
            "status": r.status_code,
            "headers": dict(list(r.headers.items())[:20]),
            "text_preview": preview
        }
    except requests.RequestException as ex:
        return {"error": "http_error", "details": str(ex)}

def regex_extract(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        p = RegexExtractParams(**(params or {}))
    except ValidationError as e:
        return {"error": "validation_error", "details": e.errors()}
    flags = _compile_flags(p.flags)
    try:
        matches = re.findall(p.pattern, p.text, flags)
        return {"matches": matches, "count": len(matches)}
    except re.error as ex:
        return {"error": "regex_error", "details": str(ex)}
