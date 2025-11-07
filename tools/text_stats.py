from collections.abc import Generator
from typing import Any
import re
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class TextStatsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Count characters, words, and lines
        """
        text = tool_parameters.get("text", "")
        
        chars = len(text)
        words = len(re.findall(r"\w+", text))
        lines = len(text.splitlines()) if text else 0
        
        result = f"Characters: {chars}, Words: {words}, Lines: {lines}"
        yield self.create_text_message(result)
