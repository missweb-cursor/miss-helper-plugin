from collections.abc import Generator
from typing import Any
from langdetect import detect
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DetectLanguageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Detect language of text
        """
        text = tool_parameters.get("text", "")
        
        try:
            lang_code = detect(text)
            yield self.create_text_message(lang_code)
        except Exception:
            yield self.create_text_message("unknown")
