from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import utils.finch_catalog as catalog
import utils.tool_base as tool_base


class SearchFinchAgentsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        query = catalog.clean_text(tool_parameters.get("query"), catalog.MAX_QUERY_CHARS)
        limit = catalog.clamp_limit(tool_parameters.get("limit"))
        outcome = yield from tool_base.run_catalog_call(
            self, "search_finch_agents", {"query": query, "limit": limit}
        )
        if outcome is None:
            return
        data, is_error = outcome
        yield self.create_json_message(data)
        if is_error:
            yield self.create_text_message(f"Finch catalog error: {data.get('error', 'unknown error')}")
            return
        results = data.get("results") or []
        if not results:
            yield self.create_text_message(f"No Finch agents matched '{query}'.")
            return
        lines = [f"{len(results)} Finch agent(s) from Finch's public catalog for '{query}':"]
        lines += [f"{i}. {catalog.summarize_agent(agent)}" for i, agent in enumerate(results, 1)]
        yield self.create_text_message("\n".join(lines))
