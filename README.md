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

## Current Status

**Version:** V0.4.1  
**Milestone:** Relationship-aware social behavior

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
- Social cooldowns
- Relationship-aware contact selection
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