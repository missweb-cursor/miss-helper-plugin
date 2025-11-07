from collections.abc import Generator
from typing import Any
import re
import string
from collections import Counter
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class SummarizeTextTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Generate extractive summary using frequency scoring
        """
        text = tool_parameters.get("text", "")
        sentences_count = tool_parameters.get("sentences", 3)
        
        if not text:
            yield self.create_text_message("")
            return
        
        # Split into sentences
        sents = re.split(r'(?<=[.!?。！？])\s+', text.strip())
        
        # Extract words and calculate frequency
        words = [w.strip(string.punctuation).lower() for w in re.findall(r"\w+", text)]
        stop = set("""a an the and or of to in on at for with by is are was were be been being this that these those
                      i you he she it we they me him her us them my your his its our their from as not no yes do does did
                      will would can could should have has had than then very just about into over under out up down off
                      if else but so because while when where who whom which what how""".split())
        scores = Counter(w for w in words if w and w not in stop)
        
        # Rank sentences by word frequency
        ranked = sorted(sents, key=lambda s: sum(scores.get(x.lower().strip(string.punctuation), 0) for x in s.split()), reverse=True)
        summary = " ".join(ranked[:min(sentences_count, len(ranked))]) if sents else ""
        
        yield self.create_text_message(summary)
