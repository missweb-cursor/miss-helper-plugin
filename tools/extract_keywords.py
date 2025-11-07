from collections.abc import Generator
from typing import Any
import re
from collections import Counter
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ExtractKeywordsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Extract top keywords by frequency
        """
        text = tool_parameters.get("text", "")
        top_k = tool_parameters.get("top_k", 10)
        
        words = [w.lower() for w in re.findall(r"\w+", text)]
        stop = set("""a an the and or of to in on at for with by is are was were be been being this that these those
                      i you he she it we they me him her us them my your his its our their from as not no yes do does did
                      will would can could should have has had than then very just about into over under out up down off
                      if else but so because while when where who whom which what how""".split())
        freq = Counter(w for w in words if w and w not in stop)
        top = [f"{w}({c})" for w, c in freq.most_common(max(1, top_k))]
        
        yield self.create_text_message(", ".join(top))
