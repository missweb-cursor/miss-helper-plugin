from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class HttpGetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Perform HTTP GET request
        """
        url = tool_parameters.get("url", "")
        timeout = tool_parameters.get("timeout", 15)
        
        if not url:
            yield self.create_text_message("URL is required")
            return
        
        try:
            response = requests.get(url, timeout=max(1, min(60, timeout)))
            text_preview = response.text[:2000] if isinstance(response.text, str) else ""
            result = f"Status: {response.status_code}\n\nContent Preview:\n{text_preview}"
            yield self.create_text_message(result)
        except Exception as e:
            yield self.create_text_message(f"HTTP request failed: {str(e)}")
