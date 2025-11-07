from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class TransformTextTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Transform text to upper/lower/reverse
        """
        text = tool_parameters.get("text", "")
        mode = tool_parameters.get("mode", "upper").lower()
        
        if mode == "upper":
            result = text.upper()
        elif mode == "lower":
            result = text.lower()
        elif mode == "reverse":
            result = text[::-1]
        else:
            result = text
            
        yield self.create_text_message(result)
