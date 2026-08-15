# Nexora

> An autonomous Internet society where AI-powered NPCs work, communicate,
> form relationships, remember events, and develop their own behavior.

Nexora is an experimental simulation of an autonomous digital society.

Instead of building another generic chatbot, Nexora models a world containing
independent NPCs with:

- Personality
- Goals
- Jobs
- Money
- Relationships
- Conversations
- Memory
- Social preferences
- Autonomous decisions
- Pluggable decision-making brains
- Structured observations
- Explicit action intents
- Job-value evaluation inside the observation layer
- LLM-backed decision making
- Provider abstraction for multiple LLM vendors

The long-term goal is to create NPCs that don't simply respond to a user,
but behave like independent inhabitants of an Internet-based world.

---

**Version:** V0.7  
**Milestone:** Multi-provider LLM brain

## Current capabilities

- Multiple autonomous NPCs
- Personality-driven utility decisions
- Economic goals
- Job marketplace
- Job completion and payment
- Social interactions
- Direct NPC-to-NPC messaging
- Conversation intents
- Incoming-message processing
- Conversational memory
- Contextual replies
- Relationship tracking
- Trust
- Respect
- Familiarity
- Reputation
- Relationship-aware contact selection
- Relationship consequences
- Social cooldowns
- Deterministic simulation
- Structured NPC observations
- Suitable-job discovery
- Job-value scores exposed to brains
- Pluggable NPC brain interface
- Deterministic rule-based brain
- Brain-driven action execution
- Provider-agnostic LLM brain
- Structured LLM action schema
- LLM action validation and safe target repair
- NVIDIA provider
- Gemini provider
- Groq provider
- Mistral provider
- Tavily research tool
- `.env` configuration for local API keys
- Automated tests
- Ruff linting/formatting
- Mypy type checking
- GitHub Actions CI

## Running Nexora

Install dependencies with uv:

```cmd
uv sync
```

Run the deterministic simulation:

```cmd
uv run nexora simulate --ticks 5
```

Run through the rule-based brain:

```cmd
uv run nexora simulate --ticks 5 --brain rule
```

Run through the local deterministic LLM-provider contract:

```cmd
uv run nexora simulate --ticks 5 --brain rule-llm
```

Run with a remote LLM provider:

```cmd
uv run nexora simulate --ticks 3 --brain nvidia
uv run nexora simulate --ticks 3 --brain gemini
uv run nexora simulate --ticks 3 --brain groq
uv run nexora simulate --ticks 3 --brain mistral
```

Run the complete test suite:

```cmd
uv run pytest
```

Run quality checks:

```cmd
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
```

## Environment configuration

Create a local `.env` from `.env.example` and keep real API keys out of Git.
Nexora loads the file at application startup.

Example model configuration:

```env
NVIDIA_API_KEY=
NVIDIA_MODEL=meta/llama-3.3-70b-instruct

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-120b

MISTRAL_API_KEY=
MISTRAL_MODEL=mistral-large-latest

TAVILY_API_KEY=
```

## Example NPCs

The current simulation contains:

| NPC | Occupation | Example behavior |
|---|---|---|
| Alice | Python Developer | Pursues income and communicates with contacts |
| Bob | Backend Developer | Searches for work and asks contacts for opportunities |
| Sarah | Product Designer | Socializes and develops relationships |

NPC behavior is not scripted as a fixed sequence.

Decisions depend on the NPC's current state, personality, goals,
available opportunities, and social environment.

## Architecture

```text
                         ┌──────────────────┐
                         │ Simulation World │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │      Agent       │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   Observation    │
                         │     Builder      │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             ┌─────────────┐          ┌──────────────┐
             │ World facts │          │ Job scoring  │
             │ goals/jobs/ │          │ payment +    │
             │ social/etc. │          │ difficulty   │
             └──────┬──────┘          └──────┬───────┘
                    └────────────┬────────────┘
                                 ▼
                        ┌──────────────────┐
                        │      Brain       │
                        └────────┬─────────┘
                                 │
               ┌─────────────────┼────────────────────┐
               │                 │                    │
               ▼                 ▼                    ▼
        ┌─────────────┐   ┌──────────────┐    ┌──────────────┐
        │  Rule Brain │   │   LLM Brain  │    │ Rule LLM     │
        │ deterministic│  │ provider     │    │ Provider     │
        └──────┬──────┘   │ abstraction  │    └──────────────┘
               │          └──────┬───────┘
               │                 │
               │        ┌────────┼────────┬────────┐
               │        │        │        │        │
               │        ▼        ▼        ▼        ▼
               │     NVIDIA   Gemini    Groq    Mistral
               │
               └─────────────────┬──────────────────────┘
                                 ▼
                         ┌──────────────────┐
                         │  ActionIntent    │
                         │ validation/repair│
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     Executor     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ World state /    │
                         │ social / memory  │
                         └──────────────────┘
```

The key architectural boundary is that brains **choose intents** while the
executor **performs actions**. LLMs therefore cannot directly mutate the world.

LLM providers return a structured action, which is validated against the
observation before execution. Missing job targets may be repaired only from
already-observed job IDs and scores; invented or unavailable targets remain
rejected.

Tavily is kept separate from the LLM provider interface because it is a web
research tool rather than a reasoning model.

## Milestones

### V0.3 — Social System

- Multiple NPCs
- Social interactions
- Relationships
- Direct messaging

### V0.4 — Memory & Conversation

- Conversation messages
- Message intents
- Inbox processing
- Conversational memory
- Contextual replies
- Social cooldowns
- Relationship-aware behavior
- Relationship consequences

### V0.5 — Structured Agent Runtime

- Runtime event contracts
- Structured observations
- Explicit action intents
- Event bus
- Pluggable brain interface

### V0.6 — Brain-Driven Simulation

- Rule-based brain
- Brain-driven agent execution
- Legacy decision path preserved
- CLI brain selection
- Structured observation → brain → action pipeline
- Structured job-value signals
- Deterministic job prioritization

### V0.7 — Multi-Provider LLM Brain

- Provider-agnostic LLM brain
- Structured LLM action schema
- Strict action validation
- Safe missing-target repair
- Environment-based API key loading
- NVIDIA provider
- Gemini provider
- Groq provider
- Mistral provider
- Tavily research tool
- Deterministic mock/rule provider for testing

### V0.8 — Planned: Autonomous Internet NPCs

Planned:

- Memory retrieval and long-term memory
- Tool-use loops
- Web research during decisions
- Reflection and self-review
- Personality persistence
- Provider fallback/routing
- Event-driven background simulation
- Real Internet activities and services

## Engineering Status

- Python 3.14
- uv
- pytest
- Ruff
- mypy
- Deterministic simulation
- 100+ automated tests
- GitHub Actions CI

## Development workflow

Nexora is developed in small, testable milestones.

1. A change is committed to GitHub.
2. Pull the change locally with git.
3. Run the pytest, Ruff, and mypy checks.
4. Run the simulation for behavioral verification.
5. Report the output.
6. Failures are diagnosed and the next correction is committed.

This keeps the architecture continuously validated while Nexora grows.
