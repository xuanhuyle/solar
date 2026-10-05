# Deep Research Prompt 3 — What Makes Quant Research Trustworthy?

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

Determine what a senior quant, PM, model-validation function or risk team requires before trusting a piece of quantitative research, and translate those requirements into a product-level **research referee specification**.

# Core question

> What causes experienced practitioners to reject quantitative research, and what controls would an AI research system need before its work deserves senior attention?

# Research tasks

## 1. Catalogue failure modes

Research real examples and practitioner discussions of:

- look-ahead bias;
- point-in-time errors;
- survivorship bias;
- revised-data leakage;
- publication-delay errors;
- timestamp mistakes;
- universe selection bias;
- target leakage;
- overfitting;
- multiple testing / data snooping;
- p-hacking;
- regime cherry-picking;
- hyperparameter tuning on test data;
- benchmark weakness;
- unrealistic transaction costs;
- unrealistic fills;
- market impact omission;
- overlap / dependence errors;
- non-stationarity;
- model decay;
- unstable feature importance;
- incorrect statistical inference;
- lack of reproducibility;
- undocumented manual intervention;
- backtest over-optimization.

Find evidence from:
- practitioner writing;
- academic finance;
- trading-firm engineering posts;
- model validation;
- regulatory guidance where relevant.

## 2. Reconstruct senior review

Find evidence of how senior quants / PMs review junior research.

What questions do they ask?

Examples:
- Why should this relationship exist?
- Was this information actually available at the time?
- What baseline does this beat?
- How many things did you try?
- How stable is it?
- What happens after costs?
- Which periods drive the result?
- Does it survive alternative definitions?
- How would we know when it dies?

Separate universal principles from firm-specific practices.

## 3. Define an independent “referee”

Translate the evidence into deterministic controls that should be outside the AI agent’s authority.

For each control state:
- what it protects against;
- whether it can be automated;
- whether it must be immutable;
- what audit evidence should be stored.

Consider:
- point-in-time snapshot construction;
- train/test boundary enforcement;
- label availability;
- trial counting;
- hypothesis-family registration;
- multiple-testing correction;
- holdout sealing;
- baseline competence;
- mutation / poisoning tests;
- transaction-cost assumptions;
- code/data/model versioning;
- experiment lineage;
- replication;
- live forward validation.

## 4. Determine what AI should NOT control

Explicitly identify what an AI researcher should never be permitted to alter after seeing results.

## 5. Determine trust threshold

What would make a senior quant willing to:
- read the result;
- spend human research time on it;
- promote it to shadow trading;
- consider production deployment?

Do not claim certainty where public evidence is unavailable.

## 6. Red-team the referee concept

Ask whether a rigorous control plane could itself become:
- too restrictive;
- statistically naive;
- slow;
- incompatible with creative research;
- easy to game;
- redundant with existing infrastructure.

# Required output

Produce:

1. **Executive conclusion**
2. **Top 20 research failure modes**
3. **How senior quants detect bad research**
4. **Trust checklist**
5. **Deterministic referee specification**
6. **Controls the AI must not own**
7. **Promotion gates: research → shadow → production**
8. **Limits of automation**
9. **How the referee itself could fail**
10. **MVP referee: minimum controls needed for credibility**
11. **Implications for the AI Quant Researcher Thesis** as specified above.

The final output should be usable as a product requirements document for the research-control-plane layer.
