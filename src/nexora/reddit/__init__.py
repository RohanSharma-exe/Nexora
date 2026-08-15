"""Reddit discovery components for Nexora."""

from nexora.reddit.agent import RedditOpportunityAgent, create_discovery_agent
from nexora.reddit.client import RedditPost, RedditRSSClient
from nexora.reddit.models import DiscoveryResult, Opportunity

__all__ = [
    "DiscoveryResult",
    "Opportunity",
    "RedditOpportunityAgent",
    "RedditPost",
    "RedditRSSClient",
    "create_discovery_agent",
]
