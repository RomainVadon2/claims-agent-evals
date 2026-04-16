# Claims Investigation Agent — Eval-Driven Development Workshop

A technical workshop showing how to build a grounding evaluator for a multi-tool
LangChain agent in an insurance context.

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

## Structure

```
agent.py                   # tools + BEFORE/AFTER prompts + create_agent
data/
  dataset.py               # 5 claim inputs used by the notebook and evaluate()
  loaders.py               # file parsers (policy, claims history, weather, estimates)
  sources/                 # policy_docs.md, claims_history.csv, weather_data.json, repair_estimates.md
notebooks/
  assets/                  # agent_diagram.png, grounding_eval_diagram.png
  workshop_demo.ipynb      # guided walkthrough
```
