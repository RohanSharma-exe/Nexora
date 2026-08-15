"""Tavily web-research tool for Nexora information gathering."""

import os
from typing import Any

from tavily import TavilyClient  # type: ignore[import-untyped]


class TavilyResearchTool:
    """Search the web without coupling Tavily to the LLM provider interface."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        client: Any | None = None,
    ) -> None:
        key = api_key or os.getenv("TAVILY_API_KEY")
        if not key:
            raise ValueError("TAVILY_API_KEY is not configured.")

        self.client = client or TavilyClient(api_key=key)

    def search(self, query: str, *, max_results: int = 5) -> list[dict[str, Any]]:
        """Return Tavily search results for an NPC research query."""

        response = self.client.search(query=query, max_results=max_results)
        results = response.get("results", [])
        return [dict(result) for result in results]
