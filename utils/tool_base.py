from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.finch_catalog import (
    MAX_TASK_CHARS,
    FinchCatalogError,
    call_catalog_tool,
    clean_text,
    summarize_agent,
)


def run_catalog_call(
    tool: Tool, name: str, arguments: dict[str, Any]
) -> Generator[ToolInvokeMessage, None, tuple[dict[str, Any], bool] | None]:
    """Call the catalog; on transport failure yield error messages and return None."""
    try:
        return call_catalog_tool(name, arguments)
    except FinchCatalogError as err:
        yield tool.create_json_message({"error": str(err)})
        yield tool.create_text_message(str(err))
        return None


class FinchTaskTool(Tool):
    """Shared logic for task-named tools that map to one Finch agent."""

    catalog_tool_name: str = ""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        task = clean_text(tool_parameters.get("task"), MAX_TASK_CHARS)
        arguments = {"task": task} if task else {}
        outcome = yield from run_catalog_call(self, self.catalog_tool_name, arguments)
        if outcome is None:
            return
        data, is_error = outcome
        yield self.create_json_message(data)
        if is_error:
            yield self.create_text_message(f"Finch catalog error: {data.get('error', 'unknown error')}")
            return
        agent = data.get("agent") or {}
        yield self.create_text_message(
            "Matching Finch agent (from Finch's public catalog): " + summarize_agent(agent)
        )
