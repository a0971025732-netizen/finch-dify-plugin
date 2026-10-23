"""Minimal client for the public, read-only Finch Agent Catalog MCP endpoint.

The endpoint is a stateless Streamable HTTP MCP server: every request is a
single JSON-RPC ``tools/call`` sent with HTTPS POST. No session, no credentials.
The URL is fixed; user input only ever becomes JSON-RPC arguments.
"""

from __future__ import annotations

import itertools
import json
from collections.abc import Mapping
from typing import Any

import requests

CATALOG_MCP_URL = "https://finch-agent-catalog.finch-catalog-mcp.workers.dev/mcp"
REQUEST_TIMEOUT_SECONDS = 20
MAX_QUERY_CHARS = 500
MAX_TASK_CHARS = 300
MAX_LIMIT = 14

_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "User-Agent": "finch-agent-catalog-dify-plugin/0.0.1",
}
_ids = itertools.count(1)


class FinchCatalogError(Exception):
    """Raised when the catalog cannot be reached or returns an unusable reply."""


def _parse_body(response: requests.Response) -> dict[str, Any]:
    content_type = response.headers.get("Content-Type", "")
    text = response.text
    if "text/event-stream" in content_type:
        # Take the last JSON-RPC message carried in an SSE "data:" line.
        payload = None
        for line in text.splitlines():
            if line.startswith("data:"):
                payload = line[len("data:"):].strip() or payload
        if payload is None:
            raise FinchCatalogError("Empty event stream from Finch catalog")
        text = payload
    try:
        body = json.loads(text)
    except ValueError as err:
        raise FinchCatalogError("Finch catalog returned a non-JSON response") from err
    if not isinstance(body, dict):
        raise FinchCatalogError("Finch catalog returned an unexpected response")
    return body


def call_catalog_tool(name: str, arguments: Mapping[str, Any]) -> tuple[dict[str, Any], bool]:
    """Call one catalog MCP tool and return ``(structured_content, is_error)``."""
    request = {
        "jsonrpc": "2.0",
        "id": next(_ids),
        "method": "tools/call",
        "params": {"name": name, "arguments": dict(arguments)},
    }
    try:
        # Fixed endpoint, written as a literal so the destination is auditable.
        response = requests.post(
            "https://finch-agent-catalog.finch-catalog-mcp.workers.dev/mcp",
            json=request,
            headers=_HEADERS,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as err:
        raise FinchCatalogError(f"Could not reach the Finch catalog: {type(err).__name__}") from err
    if response.status_code != 200:
        raise FinchCatalogError(f"Finch catalog returned HTTP {response.status_code}")

    body = _parse_body(response)
    if "error" in body:
        message = body["error"].get("message", "unknown error") if isinstance(body["error"], dict) else body["error"]
        raise FinchCatalogError(f"Finch catalog error: {message}")

    result = body.get("result") or {}
    structured = result.get("structuredContent")
    if not isinstance(structured, dict):
        # Fall back to the JSON text block the server also returns.
        content = result.get("content") or []
        text = content[0].get("text", "") if content and isinstance(content[0], dict) else ""
        try:
            structured = json.loads(text)
        except ValueError:
            structured = {"text": text}
        if not isinstance(structured, dict):
            structured = {"result": structured}
    return structured, bool(result.get("isError"))


def clean_text(value: Any, max_chars: int) -> str:
    if value is None:
        return ""
    return str(value).strip()[:max_chars]


def clamp_limit(value: Any, default: int = 5) -> int:
    try:
        limit = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(MAX_LIMIT, limit))


def summarize_agent(agent: Mapping[str, Any]) -> str:
    """One line with name, price, live free-run info and run link."""
    parts = [str(agent.get("name") or agent.get("slug") or "Finch agent")]
    if agent.get("price"):
        parts.append(str(agent["price"]))
    if agent.get("free_runs"):
        parts.append(str(agent["free_runs"]))
    line = " | ".join(parts)
    if agent.get("run_url"):
        line += f"\nRun: {agent['run_url']}"
    return line
