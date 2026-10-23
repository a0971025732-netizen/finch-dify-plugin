# Finch Agent Catalog

**Author:** a0971025732-netizen
**Version:** 0.0.1
**Type:** Tool plugin
**Source repository:** https://github.com/a0971025732-netizen/finch-dify-plugin

## Overview

[Finch](https://www.finchtech.ai) is a marketplace of third-party AI agents. This plugin lets a Dify app, agent or workflow find the right Finch agent for a task and get that agent's official description, price, current free-run offer and run link.

All results come from Finch's public, read-only agent catalog. The plugin does not run agents, does not create accounts and does not move money. Agent descriptions are returned as published by Finch; the plugin adds nothing to them.

## Tools

| Tool | Inputs | What it returns |
| --- | --- | --- |
| `search_finch_agents` | `query` (string, optional), `limit` (1-14, default 5) | Agents matching a task phrase such as "trace stolen crypto", "covered call" or "tailor resume": slug, name, category, official summary, price, free runs and run link. An empty query lists all agents. |
| `get_finch_agent` | `slug` (string, required) | The full official description, price, free runs and run link of one agent, by the slug returned from `search_finch_agents`. |
| `trace_crypto_funds` | `task` (string, optional) | The Finch agent for tracing where crypto funds went from a wallet address or transaction hash (MistTrack by SlowMist). |
| `analyze_hyperliquid_us_stock_perp` | `task` (string, optional) | The Finch agent for analyzing U.S. equity perpetuals on Hyperliquid: trend, volume, open interest, funding rate and news (Maneki AI). |
| `screen_wheel_strategy_options` | `task` (string, optional) | The Finch agent for screening cash-secured puts or covered calls on a US stock, options expiring in 3 to 9 days, with an OPEN or SKIP decision (Wheel-strategy Option Desk). |
| `tailor_resume_to_job` | `task` (string, optional) | The Finch agent for tailoring a resume to a job description with ATS keyword-match analysis, writing a cover letter, or interview prep (LittlePinkPotato). |

The four task tools return the agent record plus `ready_to_send_request` (your `task` text, ready to paste into the agent) and `how_to_run` instructions.

Every tool emits two messages:

- a **JSON message** with the catalog's structured response, for use in workflow variables, and
- a short **text message** with the agent name, price, free-run info and run link.

Prices and free-run offers (for example "10 free runs per account until <date>") are read live from the catalog API on every call. They are never hard-coded in the plugin, so they always reflect what Finch currently publishes.

## Setup

1. Install **Finch Agent Catalog** from the Dify Marketplace (or upload the `.difypkg` under **Plugins > Install from local package file**).
2. No configuration is needed. Add the tools to an Agent, Chatflow or Workflow.

### Required APIs or credentials

None. The catalog is public and read-only; no API key, token or other credential is used or stored.

### Connection requirements

The plugin makes HTTPS POST requests to a single fixed endpoint:

```
https://finch-agent-catalog.finch-catalog-mcp.workers.dev/mcp
```

This is a stateless MCP (Streamable HTTP, JSON-RPC) server. The Dify plugin runtime needs outbound network access to `finch-agent-catalog.finch-catalog-mcp.workers.dev` (port 443). Requests time out after 20 seconds. No other host is contacted.

## Usage examples

- Agent prompt: "Find me a Finch agent that can trace stolen crypto" -> the model calls `search_finch_agents` with `query="trace stolen crypto"`.
- Workflow: a Tool node runs `tailor_resume_to_job` with `task="Tailor my resume for a data analyst role"`, then an Answer node shows `run_url` and `free_runs` from the JSON output.
- Follow-up: pass a `slug` from a search result to `get_finch_agent` for the full description.

To actually run an agent, open its `run_url`, sign in to Finch (passkey or wallet) and send the request there.

## Running Finch agents from Dify (power users)

This plugin only reads the public catalog. If you want Dify to run Finch agents directly, you can add Finch's full, authenticated MCP server through Dify's built-in MCP settings (**Tools > MCP > Add MCP Server (HTTP)**):

```
https://www.finchtech.ai/mcp
```

That server uses OAuth 2.1 with your own Finch account. Follow Finch's connection guide for the authorization steps: https://github.com/a0971025732-netizen/finch-agents/blob/main/CONNECT.md

## Privacy

See [PRIVACY.md](PRIVACY.md). In short: the plugin collects and stores nothing; only the query, slug or task text you provide is sent to the catalog endpoint.

## Support

Open an issue at https://github.com/a0971025732-netizen/finch-dify-plugin/issues
