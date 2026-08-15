"""Reddit-to-opportunity discovery agent."""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from nexora.llm.tavily import TavilyResearchTool
from nexora.reddit.client import RedditPost
from nexora.reddit.models import DiscoveryResult, Opportunity, OpportunityReport


DISCOVERY_PROMPT = """You are Nexora, an autonomous startup opportunity discovery agent.

Analyze the supplied Reddit posts as market signals, not as a list of topics.
Find recurring painful problems people actually experience. Prefer problems that are:
- repeated by multiple users;
- expensive, time-consuming, or frustrating;
- currently solved with manual work or bad software;
- plausibly solvable with software, AI, or a focused SaaS product.

Do not invent evidence. Every opportunity must cite exact Reddit URLs from the input.
Score each opportunity from 0 to 100 using pain, frequency, urgency, buyer clarity, and
solution feasibility. Return at most three opportunities, ranked by score.

Return JSON matching this shape exactly:
{
  "opportunities": [
    {
      "problem": "...",
      "target_user": "...",
      "solution": "...",
      "why_now": "...",
      "evidence": ["short evidence statement"],
      "source_urls": ["https://www.reddit.com/..."],
      "score": 0
    }
  ]
}
"""


class RedditOpportunityAgent:
    """Use Reddit signals, an LLM, and optional web research to find opportunities."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        client: Any | None = None,
        researcher: TavilyResearchTool | None = None,
    ) -> None:
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY is not configured for Reddit discovery.")
        self.model = model or os.getenv("GROQ_MODEL") or "openai/gpt-oss-120b"
        self.client = client or OpenAI(
            api_key=key,
            base_url="https://api.groq.com/openai/v1",
            timeout=120.0,
        )
        self.researcher = researcher

    def discover(
        self,
        subreddit: str,
        posts: list[RedditPost],
        *,
        research: bool = True,
    ) -> DiscoveryResult:
        """Turn Reddit posts into validated opportunities and research them."""
        if not posts:
            raise ValueError(f"No Reddit posts were returned from r/{subreddit}.")

        material = "\n\n".join(
            f"POST {index}:\nTitle: {post.title}\nURL: {post.url}\n"
            f"Text: {post.text[:1200]}"
            for index, post in enumerate(posts, start=1)
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": DISCOVERY_PROMPT},
                {"role": "user", "content": material},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Discovery model returned an empty response.")
        report = OpportunityReport.model_validate(json.loads(content))

        allowed_urls = {post.url for post in posts}
        opportunities: list[Opportunity] = []
        for opportunity in report.opportunities:
            source_urls = [url for url in opportunity.source_urls if url in allowed_urls]
            if not source_urls:
                source_urls = [posts[0].url]
            opportunities.append(opportunity.model_copy(update={"source_urls": source_urls}))

        if research and self.researcher is not None:
            opportunities = [self._research(opportunity) for opportunity in opportunities]

        return DiscoveryResult(
            subreddit=subreddit,
            posts=posts,
            opportunities=opportunities,
        )

    def _research(self, opportunity: Opportunity) -> Opportunity:
        """Add a small amount of external validation to one opportunity."""
        if self.researcher is None:
            return opportunity
        query = f"{opportunity.target_user} {opportunity.solution} competitors market software"
        results = self.researcher.search(query, max_results=3)
        evidence: list[str] = []
        urls: list[str] = []
        for result in results:
            title = str(result.get("title", "")).strip()
            content = str(result.get("content", "")).strip()
            url = str(result.get("url", "")).strip()
            if title or content:
                evidence.append(f"{title}: {content[:300]}".strip())
            if url:
                urls.append(url)
        return opportunity.model_copy(update={"research": evidence, "research_urls": urls})


def create_discovery_agent(*, research: bool = True) -> RedditOpportunityAgent:
    """Create the demo discovery agent from environment configuration."""
    researcher = None
    if research and os.getenv("TAVILY_API_KEY"):
        researcher = TavilyResearchTool()
    return RedditOpportunityAgent(researcher=researcher)
