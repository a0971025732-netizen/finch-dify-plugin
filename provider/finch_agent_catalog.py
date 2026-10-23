from typing import Any

from dify_plugin import ToolProvider


class FinchAgentCatalogProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # The Finch Agent Catalog is public and read-only: no credentials are needed.
        return None
