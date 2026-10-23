# Privacy Policy

Finch Agent Catalog (Dify plugin, author: a0971025732-netizen)

## Data collected

This plugin does not collect, store, log or retain any user data. It has no database, writes no files, and does not use credentials, cookies or analytics.

## Data sent to third parties

When a tool runs, the plugin sends only the input text of that call to the Finch Agent Catalog endpoint (`https://finch-agent-catalog.finch-catalog-mcp.workers.dev/mcp`) over HTTPS:

- `search_finch_agents`: the `query` text and `limit` number
- `get_finch_agent`: the `slug`
- task tools (`trace_crypto_funds`, `analyze_hyperliquid_us_stock_perp`, `screen_wheel_strategy_options`, `tailor_resume_to_job`): the optional `task` text

Nothing else is sent: no Dify user ID, conversation history, files, or credentials.

The catalog endpoint is a stateless service hosted on Cloudflare Workers. It does not store requests. To answer `search_finch_agents`, it forwards the `query` text to Finch's public marketplace search API (`https://www.finchtech.ai/api/market/search`). Task text is truncated to 300 characters and is not forwarded. Cloudflare and Finch may keep standard request logs under their own privacy policies.

The task text is echoed back in the response so it can be pasted into a Finch agent. Do not put private documents, personal data, secrets, private keys or seed phrases in `query` or `task`.

## Data returned

Responses contain only public catalog information: agent names, official descriptions, prices, free-run offers and run links.

## Contact

Questions: https://github.com/a0971025732-netizen/finch-dify-plugin/issues
