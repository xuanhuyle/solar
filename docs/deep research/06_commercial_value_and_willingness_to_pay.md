# Deep Research Prompt 6 — Is Quant Research Labor Valuable Enough to Automate?

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

Test the economic and commercial case for an AI-native junior quant researcher.

This is the most important commercial investigation. It should not assume that faster research is valuable.

# Core question

> Is quantitative research capacity sufficiently expensive, scarce and bottlenecked that a professional trading organization would pay materially for an AI system that increases the number of valid research conclusions per senior-quant hour?

# Research tasks

## 1. Quantify research labor economics

Find evidence on:
- compensation of quant researchers;
- total loaded cost where possible;
- hiring difficulty;
- vacancy duration;
- team sizes;
- researcher-to-PM ratios;
- junior vs senior compensation;
- geographic differences;
- commodity/power vs hedge-fund contexts.

Do not overinterpret job-board salary estimates.

## 2. Estimate the economic value of research productivity

Research:
- how firms discuss research throughput;
- research backlogs;
- experimentation speed;
- time-to-production;
- number of ideas tested;
- capacity constraints;
- tooling investments;
- automation initiatives.

Look for evidence that research productivity directly matters to economics.

## 3. Test alternative bottlenecks

Actively investigate whether the true constraints are instead:
- proprietary data;
- execution quality;
- market access;
- risk capital;
- senior PM attention;
- infrastructure;
- scarce domain intuition;
- regulatory/compliance burden.

If so, explain why an AI junior quant might have low value.

## 4. Existing spending

Identify current spending categories that the product might replace or expand:

- quant salaries;
- contractors;
- research platforms;
- alternative data;
- market-data terminals;
- specialist analytics;
- consulting;
- internal engineering;
- cloud compute.

Estimate plausible budget ownership.

## 5. Buying personas

For each possible customer type:
- hedge fund;
- prop firm;
- commodity trading house;
- utility / energy merchant;
- systematic asset manager;
- bank trading desk;

identify:
- economic buyer;
- user;
- blocker;
- procurement owner;
- plausible problem statement;
- expected ROI logic.

## 6. Compare four possible products

Evaluate separately:

### Product A — AI Quant Researcher
Autonomously proposes and investigates hypotheses.

### Product B — Quant Research Referee / Control Plane
Enforces point-in-time, leakage-safe, reproducible research.

### Product C — Research Knowledge System
Stores experiments, failures, claims, evidence, conditions and decay.

### Product D — AI Research Workforce Platform
Lets firms create multiple specialized agents with mandates, permissions, budgets and track records.

For each assess:
- buyer urgency;
- willingness to pay;
- differentiation;
- integration burden;
- sales cycle;
- competition;
- initial wedge;
- expansion potential.

Do not assume Product A wins.

## 7. Pricing hypothesis

Using comparable software and labor economics, construct plausible pricing ranges for:
- pilot;
- team subscription;
- per-agent;
- enterprise deployment;
- success-based / usage-based alternatives.

Clearly label these as estimates, not observed market prices.

## 8. Evidence of AI adoption in trading firms

Find recent examples (2024–2026 preferred) of firms using AI to:
- reduce research labor;
- automate analysis;
- generate code;
- accelerate model development;
- support portfolio managers.

Distinguish real production adoption from PR.

## 9. Adversarial verdict

Answer:

> If this product did exactly what is promised, would firms actually care enough to buy it?

Then answer the harder question:

> What would need to be true for this to become a venture-scale company rather than consulting or niche research software?

# Required output

Produce:

1. **Executive conclusion**
2. **Research labor economics**
3. **Evidence that research throughput matters**
4. **Alternative bottlenecks**
5. **Current budget pools**
6. **Buyer/persona map**
7. **A/B/C/D product comparison**
8. **Pricing hypotheses**
9. **Venture-scale conditions**
10. **Strongest case for DO NOT BUILD**
11. **Exact remaining unknowns requiring interviews**
12. **Implications for the AI Quant Researcher Thesis** as specified above.

The final verdict should be commercially hard-nosed, not technologically enthusiastic.
