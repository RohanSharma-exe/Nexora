from types import SimpleNamespace

from nexora.reddit.agent import RedditOpportunityAgent
from nexora.reddit.client import RedditPost


def posts() -> list[RedditPost]:
    return [
        RedditPost(
            subreddit="startups",
            title="I spend hours doing this manually",
            url="https://www.reddit.com/r/startups/comments/abc/problem/",
            author="alice",
            score=0,
            published="2026-08-15T00:00:00Z",
            text="I wish there were a simple tool for this workflow.",
        )
    ]


class FakeCompletions:
    def create(self, **_: object) -> SimpleNamespace:
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=(
                            '{"opportunities":[{"problem":"Manual workflow",'
                            '"target_user":"small teams","solution":"Workflow assistant",'
                            '"why_now":"Teams are using manual processes",'
                            '"evidence":["Users report repeated manual work"],'
                            '"source_urls":["https://www.reddit.com/r/startups/comments/abc/problem/"],'
                            '"score":82}]}'
                        )
                    )
                )
            ]
        )


class FakeClient:
    def __init__(self) -> None:
        self.chat = SimpleNamespace(completions=FakeCompletions())


def test_discovery_agent_validates_model_output() -> None:
    agent = RedditOpportunityAgent(api_key="test", client=FakeClient())

    result = agent.discover("startups", posts(), research=False)

    assert result.subreddit == "startups"
    assert len(result.posts) == 1
    assert result.opportunities[0].score == 82
    assert result.opportunities[0].source_urls[0].startswith("https://www.reddit.com/")
