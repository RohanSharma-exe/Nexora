"""Models for Reddit-driven opportunity discovery."""

from pydantic import BaseModel, ConfigDict, Field

from nexora.reddit.client import RedditPost


class Opportunity(BaseModel):
    """A business opportunity inferred from multiple Reddit signals."""

    model_config = ConfigDict(extra="forbid")

    problem: str
    target_user: str
    solution: str
    why_now: str
    evidence: list[str] = Field(min_length=1)
    source_urls: list[str] = Field(min_length=1)
    score: float = Field(ge=0, le=100)
    research: list[str] = Field(default_factory=list)
    research_urls: list[str] = Field(default_factory=list)


class OpportunityReport(BaseModel):
    """Validated output from the discovery agent."""

    model_config = ConfigDict(extra="forbid")

    opportunities: list[Opportunity] = Field(min_length=1, max_length=5)


class DiscoveryResult(BaseModel):
    """Complete Reddit discovery result."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    subreddit: str
    posts: list[RedditPost]
    opportunities: list[Opportunity]
