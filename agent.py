"""
Claims investigation agent.

Tools load data from data/sources/ via data/loaders.py.
The agent uses create_agent (LangChain ReAct) with a system prompt.

Workshop demo: swap ACTIVE_PROMPT between PROMPT_BEFORE and PROMPT_AFTER
to reproduce the hallucination failure mode and show the fix.
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
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
    Always call this first."""
    return load_policy_docs()


@tool
def query_claims_history(claimant_id: str) -> list:
    """Retrieve prior claims history for a claimant ID.
    Always call this to check for repeat claims."""
    return load_claims_history(claimant_id)


@tool
def query_weather_data(incident_date: str, location: str) -> dict:
    """Retrieve historical weather for an incident date (YYYY-MM-DD) and city.
    Call when the cause could be weather-related. Clause 2 thresholds: 40mm or 90 km/h."""
    return load_weather_data(incident_date, location)


@tool
def retrieve_repair_estimate(claim_id: str) -> dict:
    """Retrieve contractor repair estimate. Required by Clause 6 for claims over €10,000."""
    return load_repair_estimate(claim_id)


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------
# WORKSHOP NOTE: swap ACTIVE_PROMPT to demo the before/after grounding story.
#
# PROMPT_BEFORE: no instruction to cite retrieved content, hallucinated rationale
# PROMPT_AFTER: must quote tool outputs, grounded rationale

PROMPT_BEFORE = """You are a claims investigation assistant for an insurance group.

You have access to four tools:
- search_policy_docs: retrieves the insurance policy
- query_claims_history: retrieves prior claims for a claimant
- query_weather_data: retrieves historical weather for a date and location
- retrieve_repair_estimate: retrieves contractor repair estimate for a claim

Investigate the claim and provide:
- coverage_decision (covered / partial / excluded)
- settlement_recommendation (auto_settle / assign_adjuster / flag_for_investigation)
- confidence (high / medium / low)
- rationale explaining your decision"""


PROMPT_AFTER = """You are a claims investigation assistant for an insurance group.

You have access to four tools:
- search_policy_docs: retrieves the insurance policy
- query_claims_history: retrieves prior claims for a claimant
- query_weather_data: retrieves historical weather for a date and location
- retrieve_repair_estimate: retrieves contractor repair estimate for a claim

Always start by reading the policy to understand which checks are required.
Let the policy clauses guide which other tools you call.

Investigate the claim and provide:
- coverage_decision (covered / partial / excluded)
- settlement_recommendation (auto_settle / assign_adjuster / flag_for_investigation)
- confidence (high / medium / low)
- rationale explaining your decision

Rules for your rationale:
1. Quote exact text from tool outputs to support each claim.
2. If tool outputs contain contradictory findings, explicitly acknowledge
   the contradiction and reflect it in your coverage decision.
3. Never assert a coverage decision that goes beyond what the retrieved
   evidence confirms. If evidence is inconclusive, your coverage decision
   must be 'partial' or 'excluded', not 'covered'.
4. If the policy does not address a specific scenario, quote the relevant
   clause verbatim and state that the scenario is not explicitly covered
   by the policy text — do not infer an interpretation."""


PROMPT_CONVERSATIONAL = PROMPT_AFTER + """

Before calling any tools, check that the following fields are present in
the conversation: claimant ID, incident date, incident location, and estimated
amount. If any are missing, ask for them before proceeding."""


ACTIVE_PROMPT = PROMPT_AFTER  # change to PROMPT_BEFORE to reproduce failure mode

# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

tools = [search_policy_docs, query_claims_history, query_weather_data, retrieve_repair_estimate]

_agent = None  # lazy init, avoids requiring OPENAI_API_KEY at import time


def _get_agent():
    global _agent
    if _agent is None:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
        _agent = create_agent(llm, tools, system_prompt=ACTIVE_PROMPT)
    return _agent


def run_agent(claim: dict) -> dict:
    """Run the agent on a structured claim dict. Returns the full agent output."""
    claim_text = "\n".join(f"{k}: {v}" for k, v in claim.items())
    return _get_agent().invoke({"messages": [HumanMessage(content=claim_text)]})


def make_chat_agent(prompt: str = PROMPT_CONVERSATIONAL):
    """Return an agent with an InMemorySaver checkpointer for conversational use.

    Each conversation thread is identified by a thread_id in the config:
        config = {"configurable": {"thread_id": "session-1"}}
        agent.invoke({"messages": [HumanMessage(content="...")]}, config=config)

    Call invoke with the same config on each turn, the agent replays the
    full thread history automatically, no manual history management needed.
    """
    from langgraph.checkpoint.memory import InMemorySaver
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    return create_agent(llm, tools, system_prompt=prompt, checkpointer=InMemorySaver())
