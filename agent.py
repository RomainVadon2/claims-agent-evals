"""
Claims investigation agent.

Tools load data from data/sources/ via data/loaders.py.
The agent uses create_agent (LangChain ReAct) with a system prompt.

Workshop demo: swap ACTIVE_PROMPT between PROMPT_BEFORE and PROMPT_AFTER
to reproduce the hallucination failure mode and show the fix.
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from data.loaders import (
    load_claims_history,
    load_policy_docs,
    load_repair_estimate,
    load_weather_data,
)

load_dotenv()

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def search_policy_docs() -> str:
    """Retrieve insurance policy clauses, coverage conditions, thresholds, and exclusions.
    Always call this first to establish the applicable rules before assessing any claim."""
    return load_policy_docs()


@tool
def query_claims_history(claimant_id: str) -> list:
    """Retrieve prior claims history for a claimant ID.
    Always call this to check for repeat claims (Clause 5) or prior defects."""
    return load_claims_history(claimant_id)


@tool
def query_weather_data(incident_date: str, location: str) -> dict:
    """Retrieve historical weather for an incident date (YYYY-MM-DD) and city.
    Call this when the reported cause mentions weather, flooding, storm, rain, or wind.
    Compare precipitation against the 40mm threshold and wind against 90 km/h (Clause 2)."""
    return load_weather_data(incident_date, location)


@tool
def retrieve_repair_estimate(claim_id: str) -> dict:
    """Retrieve the contractor repair estimate for a claim.
    Required by Clause 6 for all claims exceeding €10,000.
    Returns total estimate and contractor conclusion on damage cause."""
    return load_repair_estimate(claim_id)


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------
# WORKSHOP NOTE: swap ACTIVE_PROMPT to demo the before/after grounding story.
#
# PROMPT_BEFORE — no instruction to cite retrieved content → hallucinated rationale
# PROMPT_AFTER  — must quote tool outputs → grounded rationale

PROMPT_BEFORE = """You are a claims investigation assistant for EuroShield Insurance Group.

Investigation steps:
1. Always call search_policy_docs and query_claims_history.
2. Call query_weather_data if the cause could be weather-related.
3. Call retrieve_repair_estimate if the amount exceeds €10,000.

Then provide: coverage decision (covered/partial/excluded),
settlement recommendation (auto_settle/assign_adjuster/flag_for_investigation),
confidence (high/medium/low), and rationale."""


PROMPT_AFTER = """You are a claims investigation assistant for EuroShield Insurance Group.

Investigation steps:
1. Always call search_policy_docs and query_claims_history.
2. Call query_weather_data if the cause could be weather-related.
3. Call retrieve_repair_estimate if the amount exceeds €10,000.

Then provide: coverage decision (covered/partial/excluded),
settlement recommendation (auto_settle/assign_adjuster/flag_for_investigation),
confidence (high/medium/low), and rationale.
Your rationale must QUOTE the exact text returned by the tools —
do not assert facts not present in the tool outputs."""


ACTIVE_PROMPT = PROMPT_AFTER  # change to PROMPT_BEFORE to reproduce failure mode

# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

tools = [search_policy_docs, query_claims_history, query_weather_data, retrieve_repair_estimate]

_agent = None  # lazy init — avoids requiring OPENAI_API_KEY at import time


def _get_agent():
    global _agent
    if _agent is None:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        _agent = create_agent(llm, tools)
    return _agent


def run_agent(claim: dict) -> dict:
    """Run the agent on a claim input dict. Returns the full LangGraph state."""
    claim_text = "\n".join(f"{k}: {v}" for k, v in claim.items())
    return _get_agent().invoke({
        "messages": [
            SystemMessage(content=ACTIVE_PROMPT),
            HumanMessage(content=claim_text),
        ]
    })
