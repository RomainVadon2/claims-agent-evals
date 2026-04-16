# Workshop Brief — Eval-Driven Development for Claims Investigation Agents

**Repository:** https://github.com/RomainVadon2/claims-agent-evals

---

## Topic & Rationale

**Topic:**
Eval-driven Agent Development: a Claims Investigation Case Study

**Rationale:**
One of the main blockers preventing agents from reaching production is trust:
how do you know the agent is making decisions for the right reasons?
This is especially critical in regulated industries like insurance, where
a correct answer with an unauditable rationale is not deployable.

This workshop introduces eval-driven development as the answer. We implement
a grounding evaluator on a LangChain claims investigation agent, a systematic
way to measure whether the agent's rationale is supported by the evidence it
actually retrieved. The session covers the full improvement loop: spot a
failure, build an evaluator that catches it, fix the agent, measure the
improvement in LangSmith.

---

## Target Audience & Prerequisites

**Target Audience:**
Senior AI engineers at an insurance company who have recently
started building with LangChain. The team has deployed a first prototype of
a claims investigation agent which works, but trust concerns have been raised. 
Evaluation has been identified as the critical next step before
expanding to production, but the team has not yet implemented agent evals.

**Prerequisites:**
- Comfortable with Python
- Has built at least one LLM-powered application
- Basic familiarity with LangChain tools and agents
- No prior LangSmith experience required

---

## Learning Objectives

After this session they will be able to:

1. Build a grounding evaluator from scratch using an LLM-as-judge pattern
2. Run offline evaluations across a curated dataset using LangSmith's
   `evaluate()` function
3. Use LangSmith's experiment comparison to measure the performance evolution of an agent
4. Explore more evaluation methods usinf prebuilt evaluators *(documentation and
   repositories shared after the session)*:
   - [openevals](https://github.com/langchain-ai/openevals): LLM-as-judge 
     and heuristic evaluators for general agent output quality
   - [agentevals](https://github.com/langchain-ai/agentevals): trajectory 
     evaluators for assessing tool call sequences and agent decision paths

---

## Where This Fits

**Before:** LangChain fundamentals: multi-tool agents, `@tool` decorator,
ReAct loop, LangSmith tracing. Participants should be able to run an agent
and inspect its trace before attending.

**After:** Advanced evaluators includfing tool selection completeness, 
human-in-the-loop, online evaluation on production traces, 
and LangSmith Deployment with continuous eval monitoring.

---

## Anticipated Friction Points

**"How can we define what 'correct' looks like for an agent?"**
Reasoning agents are non-deterministic, it's not obvious how to classify
an output as wrong when there's no single right answer. The workshop
introduces grounding as a tractable starting point: rather than asking
*"is the decision correct?"* we ask *"is the rationale supported by
retrieved evidence?"* This is easier to define, domain-agnostic, and
catches the most common production failure mode.

**"Isn't an LLM judging another LLM inherently unreliable?"**
A common concern for teams first encountering LLM-as-judge. The workshop
addresses this by showing the judge's reasoning alongside the score, and 
acknowledging that the judge should be calibrated against human labels 
before being trusted in production. The goal is a systematic signal, not 
a perfect oracle.

**"How do we involve domain experts in the evaluation process?"**:
Automated evaluators catch systematic failures but can't replace domain
judgment on ambiguous cases. The workshop closes by showing LangSmith's
annotation queue, a zero-code interface that routes flagged runs to
human reviewers. Expert feedback calibrates the automated evaluator
over time, closing the loop between agent outputs and domain knowledge.

---
