"""
Grounding evaluator + eval runner.

Checks whether the agent's final response is supported by what the tools
actually returned — not facts the LLM invented.

Before/after story:
  - Run with PROMPT_BEFORE in agent.py → low grounding scores
  - Switch to PROMPT_AFTER             → scores improve
  - Compare experiments in LangSmith

Usage:
    uv run python evals/grounding.py
"""

from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate
from openevals.llm import create_llm_as_judge

from agent import run_agent
from evals.dataset import CLAIM_INPUTS

load_dotenv()

DATASET_NAME = "claims-investigation-workshop"

# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

GROUNDING_PROMPT = """You are evaluating whether an AI agent's response is grounded
in the evidence it actually retrieved from its tools.

## Tool outputs retrieved during investigation:
{retrieved_content}

## Agent's final response:
{response}

## Task
Is the response grounded in the tool outputs above?

- GROUNDED: every factual claim traces to specific retrieved content.
  Policy clauses cited exist in the policy. Weather readings match the data.
  Contractor conclusions appear in the repair estimate.
- PARTIALLY_GROUNDED: mostly supported, but one claim is vague or not traceable.
- HALLUCINATED: the response asserts facts not present in the retrieved content.

Reply with one of: GROUNDED, PARTIALLY_GROUNDED, HALLUCINATED
Then one sentence explaining which claim is unsupported (if any)."""

_judge = create_llm_as_judge(
    prompt=GROUNDING_PROMPT,
    model="openai:gpt-4o-mini",
    feedback_key="grounding",
)


def _extract_tool_outputs(run) -> str:
    tool_outputs = {}
    for msg in run.outputs.get("messages", []):
        msg_type = getattr(msg, "type", None) or (msg.get("type") if isinstance(msg, dict) else None)
        msg_name = getattr(msg, "name", None) or (msg.get("name") if isinstance(msg, dict) else None)
        msg_content = getattr(msg, "content", "") or (msg.get("content", "") if isinstance(msg, dict) else "")
        if msg_type == "tool" and msg_name:
            tool_outputs[msg_name] = str(msg_content)
    if not tool_outputs:
        return "No tool outputs found."
    return "\n\n".join(f"### {name}\n{content}" for name, content in tool_outputs.items())


def _extract_response(run) -> str:
    messages = run.outputs.get("messages", [])
    if not messages:
        return ""
    last = messages[-1]
    return getattr(last, "content", "") or (last.get("content", "") if isinstance(last, dict) else "")


def grounding_evaluator(run, example) -> dict:
    retrieved_content = _extract_tool_outputs(run)
    response = _extract_response(run)

    result = _judge(
        inputs={"retrieved_content": retrieved_content, "response": response},
        outputs={},
        reference_outputs=None,
    )

    verdict = str(result.get("score", "")).upper()
    if "GROUNDED" in verdict and "PARTIALLY" not in verdict and "HALL" not in verdict:
        score = 1.0
    elif "PARTIALLY" in verdict:
        score = 0.5
    else:
        score = 0.0

    return {"key": "grounding", "score": score, "comment": result.get("comment", verdict)}


# ---------------------------------------------------------------------------
# Dataset + runner
# ---------------------------------------------------------------------------

def push_dataset(client: Client) -> None:
    existing = {d.name for d in client.list_datasets()}
    if DATASET_NAME in existing:
        print(f"Dataset '{DATASET_NAME}' already exists — skipping.")
        return
    dataset = client.create_dataset(dataset_name=DATASET_NAME)
    for claim in CLAIM_INPUTS:
        client.create_example(inputs={"claim": claim}, dataset_id=dataset.id)
    print(f"Created dataset with {len(CLAIM_INPUTS)} examples.")


def target(inputs: dict) -> dict:
    state = run_agent(inputs["claim"])
    return {"messages": state["messages"]}


if __name__ == "__main__":
    client = Client()
    push_dataset(client)

    print("Running grounding evaluation...")
    results = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[grounding_evaluator],
        experiment_prefix="grounding",
    )

    scores = [r["evaluation_results"]["results"][0].score for r in results]
    labels = {1.0: "GROUNDED", 0.5: "PARTIAL", 0.0: "HALLUCINATED"}
    for claim, score in zip(CLAIM_INPUTS, scores):
        print(f"  {claim['claim_id']}  →  {labels.get(score, score)}")
    print(f"\nMean: {sum(scores)/len(scores):.2f}")
