import re
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import utils.finch_catalog as catalog
import utils.tool_base as tool_base

_SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")


class GetFinchAgentTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        slug = catalog.clean_text(tool_parameters.get("slug"), 128)
        if not _SLUG_RE.match(slug):
            yield self.create_json_message({"error": "A valid agent slug is required (from search_finch_agents)."})
            yield self.create_text_message("A valid agent slug is required (from search_finch_agents).")
            return
        outcome = yield from tool_base.run_catalog_call(self, "get_finch_agent", {"slug": slug})
        if outcome is None:
            return
        data, is_error = outcome
        yield self.create_json_message(data)
        if is_error:
            yield self.create_text_message(f"Finch catalog error: {data.get('error', 'unknown error')}")
            return
        yield self.create_text_message("Finch agent (from Finch's public catalog): " + catalog.summarize_agent(data))
