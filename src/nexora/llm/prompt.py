"""Prompt construction shared by remote LLM providers."""

import json

from nexora.models.runtime import Observation


SYSTEM_PROMPT = """You are the decision-making brain of an NPC in Nexora.
Choose exactly one action from the available actions.
Return only the requested structured action.
Never invent jobs, contacts, or other targets that are not present in the observation.
For `complete_job`, `target_id` MUST be one of the exact IDs in
`available_jobs` and MUST NOT be null.
For `send_message`, `target_id` MUST be one of the exact IDs in
`contacts` and MUST NOT be null.
For actions that do not need a target, use `target_id: null`.
Use the exact action names and exact target IDs supplied by the observation;
never use titles instead of IDs.
Prefer actions that make meaningful progress toward active goals while respecting personality,
risk tolerance, available resources, and current events.
"""


def build_decision_prompt(observation: Observation) -> str:
    """Serialize an observation into a deterministic model prompt."""

    payload = {
        "subject_id": observation.subject_id,
        "tick": observation.tick,
        "money": observation.money,
        "energy": observation.energy,
        "reputation": observation.reputation,
        "skills": observation.skills,
        "personality": dict(observation.personality),
        "events": observation.events,
        "memories": observation.memories,
        "goals": observation.goals,
        "goal_details": [
            {
                "description": goal.description,
                "priority": goal.priority,
                "progress": goal.progress,
                "target_amount": goal.target_amount,
            }
            for goal in observation.goal_details
        ],
        "contacts": observation.contacts,
        "available_actions": observation.available_actions,
        "available_jobs": observation.available_jobs,
        "available_job_scores": dict(observation.available_job_scores),
        "available_job_risks": dict(observation.available_job_risks),
    }

    return (
        "Decide the NPC's next action from this observation.\n\n"
        f"{json.dumps(payload, ensure_ascii=False, sort_keys=True)}"
    )
