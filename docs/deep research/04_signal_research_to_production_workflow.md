# Deep Research Prompt 4 — From Research Notebook to Real Capital

# Context

I am evaluating whether to build an **AI-native quantitative researcher** for professional trading organizations.

The product hypothesis is not “an AI trading bot” and not “a better forecasting model.” The envisioned system is closer to a **junior quant researcher that a trading firm can hire and configure**:

- it works on the firm’s approved datasets and research universe;
- it proposes and tests quantitative hypotheses;
- it operates inside a deterministic research control plane that enforces point-in-time data, leakage prevention, strong baselines, sealed holdouts, multiple-testing controls and reproducibility;
- it accumulates structured research memory: what was tested, what failed, what survived, under which regimes, and with what evidence;
- it is evaluated on an auditable track record rather than on persuasive prose;
- humans remain responsible for methodology approval, capital allocation and production deployment.

A central design principle is the separation between:

1. **AI Quant Researcher** — proposes and investigates hypotheses;
2. **Quant Research Referee / Control Plane** — independently enforces valid experimentation;
3. **Research Knowledge System** — stores claims, evidence, failures, conditions, provenance and signal decay;
4. **Economic Scorecard** — tracks whether promoted research creates durable economic value prospectively.

The possible initial customers include hedge funds, commodity trading houses, utilities, power/gas trading desks, proprietary trading firms, systematic funds and quantitative teams.

I am a solo founder with a strategy/finance background rather than a professional quant background. I therefore want this research to eliminate as much domain ignorance as possible **before** customer interviews.

# Research standards

Use an adversarial research style.

- Actively search for evidence that this product should **not** be built.
- Prefer primary sources: engineering blogs, conference talks, practitioner interviews, job descriptions, open-source repositories, vendor documentation, regulatory/model-risk material, academic-industry papers and public technical documentation.
- Use secondary sources only where primary evidence is unavailable.
- Distinguish clearly between:
  - **FACT** — directly supported by a source;
  - **INFERENCE** — reasoned from facts;
  - **UNKNOWN** — not established;
  - **ANECDOTE** — practitioner statement or example that may not generalize.
- Do not manufacture certainty about private trading-firm workflows.
- Where evidence is thin or conflicting, say so explicitly.
- Include source links for every material factual claim.
- Prefer evidence from 2023–2026 where the topic may have changed because of LLM adoption.
- Compare sophisticated firms and smaller teams separately where relevant.
- Do not assume the product thesis is correct.
- Recommend **DO NOT BUILD** if the evidence warrants it.

# Required final section

End with a section titled **Implications for the AI Quant Researcher Thesis** containing:

1. What the evidence supports.
2. What the evidence weakens.
3. What remains unknown and cannot be resolved through desk research.
4. The 5 most important questions to ask practitioners.
5. A verdict: **SUPPORTS / MIXED / WEAKENS / DO NOT BUILD**.


# Objective

Understand how quantitative signals actually progress from research to real-money use, so the proposed AI quant researcher can be designed around real organizational gates rather than an academic backtest workflow.

# Core question

> What must happen inside a professional trading organization between “this result looks interesting” and “we are willing to let this influence capital”?

# Research tasks

## 1. Reconstruct the lifecycle

Map:

hypothesis  
→ preliminary evidence  
→ robust backtest  
→ peer / senior review  
→ independent validation  
→ paper trading / simulation  
→ shadow production  
→ limited-capital deployment  
→ scaling  
→ live monitoring  
→ intervention  
→ retirement.

For each stage identify:
- owner;
- evidence required;
- code/data standards;
- review process;
- typical failure modes;
- whether the stage can be automated.

## 2. Find documented examples

Look for:
- hedge-fund engineering blogs;
- market-maker research infrastructure;
- systematic trading talks;
- commodity / power trading workflows;
- model-risk practices;
- open-source production frameworks;
- practitioner interviews.

Prefer examples with explicit promotion or deployment processes.

## 3. Research paper/shadow trading

Clarify:
- what firms mean by paper trading, shadow trading, simulation and canary deployment;
- how long signals may be observed before capital;
- what metrics matter;
- how transaction costs / slippage / market impact are estimated;
- how live results are compared with backtests.

## 4. Model monitoring and signal decay

Research:
- drift;
- feature decay;
- regime shifts;
- live-vs-backtest degradation;
- alerting;
- strategy retirement;
- post-mortems.

Ask:

> Could continuous signal monitoring be a first-class product feature rather than an afterthought?

## 5. Organizational responsibilities

Identify where responsibilities lie among:
- junior quant;
- senior quant;
- PM;
- quant developer;
- risk;
- model validation;
- compliance;
- data engineering;
- trading technology.

## 6. Map our proposed product to the lifecycle

For each stage state whether the AI researcher could:
- own;
- assist;
- observe;
- never control.

## 7. Identify product wedge

Which transition is most painful and underserved?

Candidates include:
- notebook → robust experiment;
- experiment → review package;
- validated signal → live shadow monitor;
- active signal → decay / invalidation monitor.

# Required output

Produce:

1. **Executive conclusion**
2. **Signal lifecycle map**
3. **Promotion gates**
4. **Evidence required at each gate**
5. **Paper / shadow trading practices**
6. **Live monitoring and retirement**
7. **Role map**
8. **Where an AI agent fits**
9. **Where human authority must remain**
10. **Best product insertion point**
11. **Implications for the AI Quant Researcher Thesis** as specified above.

Focus on actual professional practice, not theoretical best practice alone.
