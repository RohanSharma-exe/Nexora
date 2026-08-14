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

The long-term goal is to create NPCs that don't simply respond to a user,
but behave like independent inhabitants of an Internet-based world.

---

**Version:** V0.4.2  
**Milestone:** Relationship consequences

Current capabilities:

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
- Relationship tracking
- Trust
- Respect
- Familiarity
- Relationship-aware contact selection
- Relationship consequences
- Trust increases when NPCs provide useful help
- Trust decreases when NPCs fail to help
- Social cooldowns
- Deterministic simulation
- Automated tests
- Ruff linting/formatting
- Mypy type checking

---

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

---

## Architecture

```text
                    ┌──────────────────┐
                    │  Simulation      │
                    │     World        │
                    └────────┬─────────┘
                             │
             ┌───────────────┼────────────────┐
             │               │                │
             ▼               ▼                ▼
       ┌──────────┐    ┌──────────┐    ┌────────────┐
       │   NPC    │    │   Jobs   │    │   Social   │
       │  Agents  │    │  System  │    │   System   │
       └────┬─────┘    └──────────┘    └─────┬──────┘
            │                                  │
            ▼                                  ▼
      ┌────────────┐                    ┌────────────┐
      │ Decision   │                    │Relationship│
      │   Engine   │                    │   Memory   │
      └─────┬──────┘                    └────────────┘
            │
            ▼
      ┌────────────┐
      │  Actions   │
      └────────────┘

### V0.4 — Memory & Conversation

- Conversation messages
- Message intents
- Inbox processing
- Conversational memory
- Contextual replies
- Social cooldowns
- Relationship-aware behavior
- Relationship consequences

### V0.5 — LLM Brain

Planned:

- LLM-backed reasoning
- Natural conversations
- Structured tool calls
- Long-term memory retrieval
- Reflection
- Self-review
- Personality-preserving prompts

## Current Milestone — V0.4.2

### Relationship Consequences

Nexora NPC relationships now have consequences.

NPC interactions can modify:

- Trust
- Respect
- Familiarity

Helpful interactions can increase trust and respect.

Unhelpful interactions can decrease trust.

Relationship values are bounded between 0 and 1.

This creates the first social feedback loop:

NPC action
→ conversation
→ outcome
→ relationship change
→ future social preference

### Engineering Status

- Python 3.14
- uv
- pytest
- Ruff
- mypy
- Deterministic simulation
- 30+ automated tests