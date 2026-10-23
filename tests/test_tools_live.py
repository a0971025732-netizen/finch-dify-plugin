"""Exercise every tool's _invoke against the live Finch catalog endpoint.

The Dify runtime is replaced by ``Tool.from_credentials({})``, which builds a
tool with an empty session; messages are collected from the generator.
Run from the plugin root:  .venv/bin/python -m pytest -v tests
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml
from dify_plugin import Tool
from dify_plugin.core.utils.class_loader import load_single_subclass_from_source
from dify_plugin.entities.tool import ToolInvokeMessage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TASK_TOOLS = {
    "trace_crypto_funds": "MistTrack",
    "analyze_hyperliquid_us_stock_perp": "Maneki",
    "screen_wheel_strategy_options": "Wheel-strategy",
    "tailor_resume_to_job": "LittlePinkPotato",
}
ALL_TOOLS = ["search_finch_agents", "get_finch_agent", *TASK_TOOLS]


def load_tool(name: str) -> Tool:
    spec = yaml.safe_load((ROOT / "tools" / f"{name}.yaml").read_text())
    source = ROOT / spec["extra"]["python"]["source"]
    cls = load_single_subclass_from_source(
        module_name=f"tools.{name}", script_path=str(source), parent_type=Tool
    )
    return cls.from_credentials({})


def invoke(name: str, params: dict) -> tuple[list[dict], list[str]]:
    messages = list(load_tool(name)._invoke(params))
    jsons, texts = [], []
    for m in messages:
        if m.type == ToolInvokeMessage.MessageType.JSON:
            jsons.append(m.message.json_object)
        elif m.type == ToolInvokeMessage.MessageType.TEXT:
            texts.append(m.message.text)
    return jsons, texts


def test_provider_lists_all_tools_and_each_loads_one_subclass():
    provider = yaml.safe_load((ROOT / "provider" / "finch_agent_catalog.yaml").read_text())
    listed = [Path(p).stem for p in provider["tools"]]
    assert listed == ALL_TOOLS
    for name in ALL_TOOLS:
        assert isinstance(load_tool(name), Tool)


def test_search_finch_agents():
    jsons, texts = invoke("search_finch_agents", {"query": "trace stolen crypto", "limit": 3})
    assert len(jsons) == 1 and len(texts) == 1
    results = jsons[0]["results"]
    assert 1 <= len(results) <= 3
    first = results[0]
    for key in ("slug", "name", "summary", "price", "free_runs", "run_url"):
        assert key in first
    assert first["run_url"].startswith("https://www.finchtech.ai/")
    assert first["free_runs"] in texts[0]
    print("\n" + texts[0])


def test_search_limit_is_clamped():
    jsons, _ = invoke("search_finch_agents", {"query": "", "limit": 999})
    assert 1 <= len(jsons[0]["results"]) <= 14


def test_get_finch_agent():
    jsons, _ = invoke("search_finch_agents", {"query": "tailor resume", "limit": 1})
    slug = jsons[0]["results"][0]["slug"]
    jsons, texts = invoke("get_finch_agent", {"slug": slug})
    assert jsons[0]["slug"] == slug
    assert jsons[0]["summary"]
    assert jsons[0]["run_url"] in texts[0]
    print("\n" + texts[0])


def test_get_finch_agent_unknown_slug_reports_error():
    jsons, texts = invoke("get_finch_agent", {"slug": "agent-does-not-exist"})
    assert "error" in jsons[0]
    assert texts[0].startswith("Finch catalog error:")


def test_get_finch_agent_rejects_invalid_slug_without_network():
    jsons, texts = invoke("get_finch_agent", {"slug": "../../etc"})
    assert "error" in jsons[0]
    assert "valid agent slug" in texts[0]


@pytest.mark.parametrize("name,expected", TASK_TOOLS.items())
def test_task_tools(name, expected):
    task = "Example request for testing"
    jsons, texts = invoke(name, {"task": task})
    data = jsons[0]
    assert expected in data["agent"]["name"]
    assert data["ready_to_send_request"] == task
    assert data["agent"]["free_runs"]
    assert data["agent"]["run_url"] in texts[0]
    print("\n" + texts[0])


@pytest.mark.parametrize("name", TASK_TOOLS)
def test_task_tools_without_task(name):
    jsons, texts = invoke(name, {})
    assert jsons[0]["agent"]["slug"].startswith("agent-")
    assert texts


def test_yaml_files_parse_with_sdk_models():
    from dify_plugin.core.entities.plugin.setup import PluginConfiguration
    from dify_plugin.entities.tool import ToolConfiguration, ToolProviderConfiguration

    manifest = PluginConfiguration(**yaml.safe_load((ROOT / "manifest.yaml").read_text()))
    assert manifest.name == "finch_agent_catalog"
    assert manifest.author == "a0971025732-netizen"
    provider = yaml.safe_load((ROOT / "provider" / "finch_agent_catalog.yaml").read_text())
    ToolProviderConfiguration(**provider)
    for path in provider["tools"]:
        ToolConfiguration(**yaml.safe_load((ROOT / path).read_text()))
