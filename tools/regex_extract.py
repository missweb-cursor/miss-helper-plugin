from collections.abc import Generator
from typing import Any
import re
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class RegexExtractTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Extract regex matches from text
        """
        text = tool_parameters.get("text", "")
        pattern = tool_parameters.get("pattern", "")
        flags_str = tool_parameters.get("flags", "")
        
        if not pattern:
            yield self.create_text_message("Pattern is required")
            return
        
        # Parse flags
        flag_map = {"I": re.IGNORECASE, "M": re.MULTILINE, "S": re.DOTALL, "U": re.UNICODE, "X": re.VERBOSE, "A": re.ASCII}
        flags = 0
        if flags_str:
            for f in flags_str.upper().split(","):
                f = f.strip()
                if f in flag_map:
                    flags |= flag_map[f]
        
        try:
            pat = re.compile(pattern, flags)
            matches = [m.group(0) for m in pat.finditer(text)]
            
            if not matches:
                yield self.create_text_message("No matches found")
            else:
                yield self.create_text_message("\n".join(matches))
        except Exception as e:
            yield self.create_text_message(f"Regex error: {str(e)}")
