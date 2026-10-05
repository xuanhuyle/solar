# Deep Research Prompt 1 — Quant Research Workflow Archaeology

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

Reconstruct, as concretely as possible, **how quantitative research is actually performed inside professional trading organizations today**, and identify where human time, judgment and coordination are consumed.

I do not want a generic “day in the life of a quant.” I want an operational map that can be used to decide whether an AI-native junior quant researcher would remove a real bottleneck.

# Core question

> From the moment a trading idea is proposed to the moment it is either rejected, monitored, paper-traded or deployed, what work is actually performed, by whom, with which tools, and where are the costly bottlenecks?

# Research tasks

## 1. Reconstruct the end-to-end workflow

Map the real workflow from:

idea / market observation  
→ research question  
→ dataset discovery / procurement  
→ historical data reconstruction  
→ cleaning / alignment  
→ feature engineering  
→ exploratory analysis  
→ hypothesis formulation  
→ model / factor construction  
→ backtesting  
→ robustness checks  
→ peer review / senior review  
→ paper or shadow trading  
→ productionization  
→ live monitoring  
→ retirement / post-mortem.

For each stage identify:

- typical owner;
- typical tools;
- manual vs automated work;
- common failure modes;
- approximate time burden where credible evidence exists;
- whether senior judgment is required;
- whether the work is repetitive enough for AI automation.

## 2. Segment by firm type

Where evidence allows, distinguish:

- top systematic hedge funds;
- discretionary hedge funds with quant support;
- commodity trading houses;
- utilities / energy merchants;
- prop firms / market makers;
- smaller specialist trading teams.

Do not assume their workflows are identical.

## 3. Identify actual research bottlenecks

Look specifically for evidence around:

- data discovery and access;
- cleaning and timestamp alignment;
- point-in-time reconstruction;
- feature generation;
- repetitive coding;
- backtest setup;
- leakage checks;
- validation;
- experiment tracking;
- documentation;
- senior review;
- production handoff;
- monitoring and signal decay;
- duplicated / forgotten research;
- inability to reproduce old work.

Rank bottlenecks by:
- frequency;
- cost;
- seniority of labor consumed;
- suitability for agentic automation.

## 4. Find evidence of existing AI usage

Research how quant teams are already using:

- Claude;
- ChatGPT;
- GitHub Copilot;
- internal LLMs;
- code agents;
- notebook agents;
- autonomous research systems.

Separate:
- coding productivity;
- data work;
- literature review;
- factor generation;
- experiment automation;
- model research;
- production use.

Look for practitioner commentary on where LLMs help and where they fail.

## 5. Identify the “junior quant” task bundle

Based on evidence, define the subset of tasks typically assigned to:

- interns;
- junior quant researchers;
- quant developers;
- senior quants / PMs.

Then answer:

> Which junior-quant tasks could plausibly be delegated to an AI agent without giving it capital-allocation authority?

## 6. Find counterevidence

Actively search for evidence that:

- research throughput is not a meaningful bottleneck;
- data or execution dominates;
- senior judgment is the only scarce resource;
- research is already heavily automated;
- firms do not want more hypotheses;
- internal tooling makes an external AI researcher redundant.

# Required output

Produce:

1. **Executive conclusion**
2. **End-to-end workflow map**
3. **Who does what**
4. **Where time is actually spent**
5. **Bottleneck ranking**
6. **Current AI usage**
7. **Tasks suitable for an AI junior quant**
8. **Tasks that should remain human**
9. **Evidence against the product thesis**
10. **Narrowest workflow worth automating first**
11. **Implications for the AI Quant Researcher Thesis** as specified above.

Be concrete. Avoid generic descriptions of quantitative finance.
