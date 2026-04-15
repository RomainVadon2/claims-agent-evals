# Claims Investigation Agent — Eval-Driven Development Workshop

A technical workshop showing how to build a grounding evaluator for a multi-tool
LangGraph agent in an insurance context. The core demo: one prompt change, measured
by a LangSmith eval, with a before/after comparison in the experiment view.

## Setup

```bash
cp .env.example .env
# Fill in OPENAI_API_KEY and LANGSMITH_API_KEY
uv sync
```

## Run the workshop notebook

```bash
uv run jupyter notebook
```

Open `notebooks/workshop_demo.ipynb`.

## Run evals from the command line

```bash
uv run python evals/grounding.py
```

## Structure

```
agent.py                   # tools + BEFORE/AFTER prompts + create_react_agent
data/
  loaders.py               # file parsers (policy, claims history, weather, estimates)
  sources/                 # policy_docs.md, claims_history.csv, weather_data.json, repair_estimates.md
evals/
  dataset.py               # 5 claim inputs
  grounding.py             # LLM-as-judge grounding evaluator + evaluate() runner
notebooks/
  workshop_demo.ipynb      # guided walkthrough
```

## Before / after demo

In `agent.py`, swap `ACTIVE_PROMPT` between `PROMPT_BEFORE` and `PROMPT_AFTER`,
then re-run `evals/grounding.py`. Compare the two experiments in LangSmith.
