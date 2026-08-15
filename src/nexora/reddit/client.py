"""Small Reddit RSS client used by the discovery demo."""

from __future__ import annotations

import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import unescape


@dataclass(frozen=True, slots=True)
class RedditPost:
    """A minimal Reddit post representation."""

    subreddit: str
    title: str
    url: str
    author: str
    score: int
    published: str
    text: str


def _clean_html(value: str) -> str:
    value = unescape(value)
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(value.split())


class RedditRSSClient:
    """Fetch public subreddit RSS feeds without requiring Reddit credentials."""

    def __init__(self, *, timeout: float = 15.0) -> None:
        self.timeout = timeout

    def hot(self, subreddit: str, *, limit: int = 10) -> list[RedditPost]:
        """Return recent posts from a subreddit RSS feed."""
        name = subreddit.strip().lstrip("r/").strip("/")
        if not name:
            raise ValueError("Subreddit must not be empty.")
        limit = max(1, min(limit, 25))
        query = urllib.parse.urlencode({"limit": limit})
        url = f"https://www.reddit.com/r/{name}/hot/.rss?{query}"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Nexora/0.7 Reddit discovery demo"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = response.read()
        except Exception as exc:
            raise RuntimeError(
                f"Could not read Reddit RSS for r/{name}: {exc}"
            ) from exc

        root = ET.fromstring(payload)
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        posts: list[RedditPost] = []
        for entry in root.findall("atom:entry", namespace)[:limit]:
            title = entry.findtext("atom:title", default="", namespaces=namespace).strip()
            link = entry.find("atom:link", namespace)
            url_value = link.attrib.get("href", "") if link is not None else ""
            author = entry.findtext(
                "atom:author/atom:name", default="unknown", namespaces=namespace
            )
            published = entry.findtext("atom:updated", default="", namespaces=namespace)
            content = entry.findtext("atom:content", default="", namespaces=namespace)
            posts.append(
                RedditPost(
                    subreddit=name,
                    title=title,
                    url=url_value,
                    author=author,
                    score=0,
                    published=published,
                    text=_clean_html(content),
                )
            )
        return posts
