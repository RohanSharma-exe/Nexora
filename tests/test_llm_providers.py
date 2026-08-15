from types import SimpleNamespace

import pytest

from nexora.llm.gemini_provider import GeminiProvider
from nexora.llm.groq_provider import GroqProvider
from nexora.llm.mistral_provider import MistralProvider
from nexora.llm.nvidia_provider import NVIDIAProvider
from nexora.llm.tavily import TavilyResearchTool
from nexora.models.runtime import ActionType, Observation

OBSERVATION = Observation(
    subject_id="alice",
    tick=1,
    available_actions=(ActionType.WAIT.value,),
)


class FakeOpenAIClient:
    def __init__(self) -> None:
        message = SimpleNamespace(
            content='{"action":"wait","target_id":null,"content":null,"reasoning":"rest"}'
        )
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_: SimpleNamespace(choices=[SimpleNamespace(message=message)])
            )
        )


class FakeGeminiClient:
    def __init__(self) -> None:
        self.models = SimpleNamespace(
            generate_content=lambda **_: SimpleNamespace(
                text='{"action":"wait","target_id":null,"content":null,"reasoning":"rest"}'
            )
        )


class FakeMistralClient:
    def __init__(self) -> None:
        message = SimpleNamespace(
            content='{"action":"wait","target_id":null,"content":null,"reasoning":"rest"}'
        )
        self.chat = SimpleNamespace(
            parse=lambda **_: SimpleNamespace(choices=[SimpleNamespace(message=message)])
        )


class FakeTavilyClient:
    def search(self, **_: object) -> dict[str, list[dict[str, str]]]:
        return {"results": [{"title": "Nexora", "url": "https://example.com"}]}


def test_nvidia_provider_uses_structured_action() -> None:
    provider = NVIDIAProvider(api_key="test", model="test-model")
    provider.client = FakeOpenAIClient()

    intent = provider.decide(OBSERVATION)

    assert intent.actor_id == "alice"
    assert intent.action_type == ActionType.WAIT


def test_groq_provider_uses_structured_action() -> None:
    provider = GroqProvider(api_key="test", model="test-model")
    provider.client = FakeOpenAIClient()

    intent = provider.decide(OBSERVATION)

    assert intent.action_type == ActionType.WAIT


def test_gemini_provider_uses_structured_action() -> None:
    provider = GeminiProvider(api_key="test", model="test-model", client=FakeGeminiClient())

    intent = provider.decide(OBSERVATION)

    assert intent.action_type == ActionType.WAIT


def test_mistral_provider_uses_structured_action() -> None:
    provider = MistralProvider(api_key="test", model="test-model", client=FakeMistralClient())

    intent = provider.decide(OBSERVATION)

    assert intent.action_type == ActionType.WAIT


def test_tavily_research_tool_returns_results() -> None:
    tool = TavilyResearchTool(api_key="test", client=FakeTavilyClient())

    results = tool.search("Nexora")

    assert results == [{"title": "Nexora", "url": "https://example.com"}]


@pytest.mark.parametrize(
    ("provider", "environment_variable"),
    [
        (NVIDIAProvider, "NVIDIA_API_KEY"),
        (GeminiProvider, "GEMINI_API_KEY"),
        (GroqProvider, "GROQ_API_KEY"),
        (MistralProvider, "MISTRAL_API_KEY"),
        (TavilyResearchTool, "TAVILY_API_KEY"),
    ],
)
def test_provider_requires_api_key(
    provider: object,
    environment_variable: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(environment_variable, raising=False)

    with pytest.raises(ValueError, match="not configured"):
        provider()  # type: ignore[operator]
