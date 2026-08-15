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

The long-term goal is to create NPCs that don't simply respond to a user,
but behave like independent inhabitants of an Internet-based world.

---

**Version:** V0.6.2  
**Milestone:** Brain-driven simulation

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
- Rule brain selects the highest-value available job
- Brain-driven action execution
- Legacy decision engine preserved
- Automated tests
- Ruff linting/formatting
- Mypy type checking
- GitHub Actions CI

## Running Nexora

Install dependencies with uv:

```cmd
uv sync
```

Run the existing simulation:

```cmd
uv run nexora simulate --ticks 5
```

Run the simulation through the rule-based brain:

```cmd
uv run nexora simulate --ticks 5 --brain rule
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
                     ┌────────────┴────────────┐
                     │                         │
                     ▼                         ▼
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
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             ┌─────────────┐             ┌─────────────┐
             │ Rule Brain  │             │ Future LLM  │
             │             │             │    Brain    │
             └──────┬──────┘             └─────────────┘
                    │
                    ▼
             ┌─────────────┐
             │ ActionIntent│
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │   Executor  │
             └──────┬──────┘
                    │
                    ▼
             ┌──────────────────┐
             │ World state /    │
             │ social / memory │
             └──────────────────┘
```

The key architectural boundary is that brains **choose intents** while the
executor **performs actions**. A future LLM brain therefore cannot directly
mutate the world.

The observation layer also keeps world-state perception separate from
reasoning. Brains receive job IDs and normalized job-value scores rather than
reaching directly into the job board. This makes it easier to replace the rule
brain with an LLM brain later without coupling the LLM to simulation internals.

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

### V0.7 — Planned: LLM Brain

Planned:

- LLM-backed reasoning
- Natural conversations
- Structured tool/action output
- Memory retrieval
- Reflection
- Self-review
- Personality-preserving prompts
- Provider abstraction
- Configurable model selection

## Engineering Status

- Python 3.14
- uv
- pytest
- Ruff
- mypy
- Deterministic simulation
- 77+ automated tests
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
