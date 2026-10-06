# Deep Research Prompt 2 — Quant Tool Stack & Competitor Reconstruction

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

Determine whether the proposed AI-native quant researcher is genuinely differentiated or whether its components are already solved by existing quant platforms, internal tools, open-source libraries and AI coding agents.

# Core question

> What does a modern quant research stack already do, and which parts of the proposed AI researcher / referee / research-memory system are still unsolved enough to support a product?

# Research tasks

## 1. Reconstruct the modern research stack

Map relevant tools across these layers:

- market and alternative data;
- time-series databases;
- point-in-time / vintage data;
- notebooks / IDEs;
- dataframes / compute;
- factor research;
- feature stores;
- experiment tracking;
- backtesting;
- model registry;
- statistical testing;
- explainability;
- portfolio construction;
- execution simulation;
- research knowledge management;
- monitoring;
- coding copilots and agents.

Include, where relevant:
- Bloomberg;
- LSEG / Refinitiv;
- FactSet;
- kdb+;
- ArcticDB;
- Databricks;
- Snowflake;
- MLflow;
- Weights & Biases;
- QuantConnect;
- QuantRocket;
- Numerai tooling;
- WorldQuant-style platforms;
- Hudson & Thames / mlfinlab;
- vectorbt;
- backtrader;
- Zipline;
- LEAN;
- OpenSTEF;
- Nixtla;
- tsfresh;
- Tigramite;
- Energy Quantified;
- Volue;
- Exabel;
- Kpler;
- power-market specialist tooling;
- relevant AI-native quant startups and agentic research products.

This list is illustrative, not exhaustive.

## 2. Search specifically for AI-native competitors

Find companies or open-source projects that claim to provide:

- autonomous quantitative research;
- AI-generated factors;
- AI portfolio research;
- autonomous backtesting;
- agentic financial research;
- quant copilots;
- natural-language-to-strategy;
- automated feature discovery;
- signal discovery;
- research agents;
- AI-native hedge fund tooling.

For each credible competitor determine:

- target customer;
- product scope;
- autonomy level;
- data model;
- point-in-time support;
- backtesting discipline;
- multiple-testing / leakage safeguards;
- research memory;
- deployment model;
- pricing if public;
- evidence of real professional adoption;
- whether the product is mainly marketing vs substantive capability.

## 3. Build a feature-by-feature matrix

Use these product concepts as columns or rows:

- hypothesis generation;
- data discovery;
- point-in-time reconstruction;
- experiment execution;
- automated leakage checks;
- multiple-testing ledger;
- sealed holdouts;
- model tournament;
- statistical referee;
- research memory;
- negative-result memory;
- claim/evidence graph;
- signal-decay monitoring;
- economic scorecard;
- customizable research mandate;
- permissions / compute budget;
- human review gates;
- internal-data operation;
- VPC / on-prem deployment.

Identify:
- commoditized;
- partially solved;
- genuinely weak / missing.

## 4. Internal-build threat

Investigate whether a sophisticated trading firm can easily assemble the proposed product using:

- Claude Code / Codex / Copilot;
- Databricks / Snowflake;
- internal backtesting infrastructure;
- MLflow / W&B;
- existing point-in-time data stores.

Ask:

> Is this a product, or merely an internal integration project that every capable firm can build itself?

Be adversarial.

## 5. Moat analysis

Evaluate potential moats:

- proprietary model;
- point-in-time data layer;
- research-control-plane methodology;
- accumulated research memory;
- validated track record;
- workflow integration;
- firm-specific configuration;
- network effects;
- benchmark dataset;
- regulatory / audit credibility.

State which, if any, are credible.

# Required output

Produce:

1. **Executive conclusion**
2. **Modern quant stack map**
3. **AI-native competitor landscape**
4. **Feature comparison matrix**
5. **What is already commoditized**
6. **What remains unsolved**
7. **Internal-build threat**
8. **Potential wedge**
9. **Potential moat**
10. **Strongest reason not to build**
11. **Implications for the AI Quant Researcher Thesis** as specified above.

If there is no meaningful whitespace, say so.
