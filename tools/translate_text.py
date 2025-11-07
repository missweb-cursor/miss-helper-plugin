from collections.abc import Generator
from typing import Any
import requests
import os
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class TranslateTextTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Translate text using LibreTranslate API
        """
        text = tool_parameters.get("text", "")
        target_lang = tool_parameters.get("target_lang", "")
        source_lang = tool_parameters.get("source_lang", "auto")
        
        if not text or not target_lang:
            yield self.create_text_message("Text and target language are required")
            return
        
        api_url = os.getenv("TRANSLATE_API_URL", "https://libretranslate.com/translate").strip()
        payload = {
            "q": text,
            "source": source_lang or "auto",
            "target": target_lang,
            "format": "text"
        }
        
        api_key = os.getenv("TRANSLATE_API_KEY", "").strip()
        if api_key:
            payload["api_key"] = api_key
        
        try:
            response = requests.post(api_url, json=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
            translated = data.get("translatedText") or data.get("translated_text") or ""
            yield self.create_text_message(translated)
        except Exception as e:
            yield self.create_text_message(f"Translation failed: {str(e)}")
