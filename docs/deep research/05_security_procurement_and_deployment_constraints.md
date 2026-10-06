# Deep Research Prompt 5 — Security, Procurement & Deployment Reality

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

Determine whether a professional trading organization could realistically allow an external AI-native quant researcher to access the data, code and compute required to be useful.

This research should identify architecture constraints **before** product development.

# Core question

> What security, confidentiality, procurement, compliance and deployment requirements would determine whether a trading firm can use an external AI research agent at all?

# Research tasks

## 1. Identify sensitive assets

Research which assets firms are likely to treat as highly confidential:

- proprietary datasets;
- raw orders / executions;
- positions;
- strategy code;
- feature definitions;
- alpha models;
- research notebooks;
- internal forecasts;
- licensed vendor data;
- counterparty information;
- market-access infrastructure.

Explain implications for AI access.

## 2. Research LLM / cloud restrictions

Find evidence about policies concerning:
- external LLM APIs;
- data retention;
- provider training;
- zero-data-retention;
- private endpoints;
- VPC deployment;
- on-prem models;
- regional data residency;
- encryption;
- secrets management;
- audit logs;
- role-based access;
- customer-managed keys.

Prioritize financial services and trading organizations.

## 3. Vendor procurement requirements

Research likely expectations around:
- SOC 2;
- ISO 27001;
- penetration testing;
- incident response;
- data-processing agreements;
- subcontractor disclosures;
- cyber insurance;
- business continuity;
- vendor-risk questionnaires;
- model-risk governance;
- source-code access;
- SLAs.

Distinguish requirements for:
- small hedge fund / prop shop;
- utility / energy trader;
- bank-affiliated trading desk;
- large institutional asset manager.

## 4. Licensed data constraints

This is critical.

Research how market-data and alternative-data licences restrict:
- redistribution;
- derived data;
- cloud processing;
- model training;
- third-party SaaS access;
- contractor access;
- retention.

Determine whether an external AI vendor can legally process a firm's licensed data.

## 5. Deployment models

Compare:

A. Multi-tenant SaaS  
B. Single-tenant cloud  
C. Customer VPC  
D. Customer-managed Kubernetes  
E. On-prem  
F. Agent shipped as software with no data leaving environment

For each assess:
- security acceptability;
- implementation complexity;
- sales-cycle impact;
- observability/support;
- IP protection;
- gross-margin implications.

## 6. Permission architecture

Define a plausible mandate system for an AI quant:

- data scopes;
- read/write permissions;
- execution sandbox;
- external network access;
- model-provider access;
- compute budget;
- approved libraries;
- approved research universe;
- human approval gates.

## 7. Kill conditions

Identify deployment constraints that could make the business unattractive for a solo founder / startup.

# Required output

Produce:

1. **Executive conclusion**
2. **Sensitive asset map**
3. **LLM/cloud policy reality**
4. **Procurement/security requirements**
5. **Licensed-data constraints**
6. **Deployment architecture comparison**
7. **Recommended default deployment**
8. **Permission model for the AI researcher**
9. **Likely sales / implementation friction**
10. **Potential kill conditions**
11. **Implications for the AI Quant Researcher Thesis** as specified above.

Do not hand-wave “enterprise security.” Be specific enough to influence architecture.
