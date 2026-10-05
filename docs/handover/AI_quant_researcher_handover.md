# AI Quantitative Researcher — Conversation Handover

## Purpose

This file is a handover for a new ChatGPT conversation.

The next conversation should synthesize:

1. six independent Claude.ai Deep Research reports;
2. the latest Claude Code output on Experiment 1 / Stage 0;
3. the accumulated product thesis and technical decisions summarized below.

The goal is **not** to preserve prior conclusions. The goal is to evaluate the full evidence set adversarially and decide what, if anything, should be built next.

---

# 1. Founder context

Founder:
- Solo founder, Paris-based.
- ~12+ years strategy consulting / private equity / M&A / B2B infrastructure.
- Strong telecom / infrastructure / diligence / business strategy background.
- Non-technical by training.
- Completed a short coding bootcamp and builds with Claude Code / AI coding tools.
- No professional quant or trading background.
- Wants to determine whether a technically and commercially valuable company can be built before committing heavily.

Important constraint:
- Do **not** assume the founder should become a quant expert before acting.
- Deep research is being used to compress domain learning.
- Practitioner interviews should be used to resolve the residual tacit/commercial unknowns that desk research cannot answer.

---

# 2. Original technical starting point

The project began around **t0**, a time-series foundation model from The Forecasting Company.

Experiment 0:
- GitHub repo: `xuanhuyle/solar`
- Goal: predict next-day French national solar production using only past solar output, no weather forecasts.
- Forecast origin: noon D-1.
- Compared t0 against simple baselines.

Key result:
- t0 initially appeared to beat “same as yesterday” and “same as last week”.
- Once stronger simple baselines were added, t0 lost.
- EWMA / rolling-average-type baselines beat t0.
- Much of t0’s apparent edge came from information-age asymmetry.
- t0 also had a night-floor failure mode.

Core lesson:
> Model sophistication is not the value. Strong baselines, information timing, point-in-time correctness, and experimental discipline matter more.

Experiment 0 became a methodological ancestor rather than the product.

---

# 3. Product thesis evolution

The idea evolved through several stages.

## Stage A — Forecasting product

Initial idea:
- use t0 / time-series foundation models to build forecasting products.

Rejected / weakened because:
- raw forecasting is commoditized;
- model superiority is fragile;
- high-quality baselines can erase apparent gains.

## Stage B — Signal discovery / trading research

The idea shifted toward:
- discovering whether economic / physical / market variables add predictive information to high-frequency market variables;
- especially in power / energy markets;
- testing incremental predictive value, not simple correlation.

Important concept:
> “Does adding X improve out-of-sample forecasting of Y beyond a strong baseline information set?”

This introduced:
- point-in-time data;
- forecast revisions;
- lead/lag;
- regime stability;
- economic validation;
- multiple testing.

## Stage C — AI-native quant researcher

Best mental model developed:

> **An AI-native quantitative researcher for professional trading organizations.**

The firm could “hire” an AI junior quant and configure:

- market universe;
- target variables;
- horizons;
- permitted datasets;
- permitted models;
- research standards;
- significance thresholds;
- compute budget;
- risk / economic assumptions;
- permissions;
- escalation rules.

The agent could:
- formulate hypotheses;
- run experiments;
- reject weak relationships;
- produce evidence;
- accumulate research memory;
- monitor signal decay.

Humans retain:
- methodology approval;
- production approval;
- risk allocation;
- capital allocation.

## Stage D — Critical reframing

A major insight emerged:

> **Generating research is becoming cheap. Validating research is not.**

Therefore the architecture should separate:

### AI Researcher
Proposes and investigates hypotheses.

### Quant Research Referee / Control Plane
Independently enforces:
- point-in-time correctness;
- train/test separation;
- label availability;
- strong baselines;
- trial counting;
- multiple-testing control;
- sealed holdouts;
- reproducibility;
- economic assumptions.

The researcher cannot alter the referee.

### Research Knowledge System
Stores:
- hypotheses;
- experiments;
- failures;
- evidence;
- claims;
- counter-evidence;
- regimes;
- confidence;
- signal decay;
- provenance.

### Economic Scorecard
Tracks:
- prospective performance;
- false discovery rate;
- live / shadow results;
- research value per unit of compute / senior attention.

The emerging long-term product thesis is:

> **AI researcher + deterministic referee + institutional research memory + economic track record.**

---

# 4. Fundamental technical proof identified

The core technical proof is **not**:

> “Can t0 forecast a market?”

It is:

> **Can an AI research agent, given a noisy point-in-time dataset containing genuine and spurious candidate signals, autonomously identify genuinely predictive relationships, reject false ones, and produce reproducible conclusions that survive an unseen holdout?**

Suggested benchmark structure:

- target Y;
- several planted true signals;
- many decoys;
- look-ahead traps;
- revised-data traps;
- regime-dependent signals;
- signals that work in-sample but fail forward;
- null variables;
- realistic publication delays.

The agent should not know the planted truth.

Measure:
- precision;
- recall;
- false discovery rate;
- forecast uplift;
- methodological violations.

Key principle:
> The AI researcher should not control the scientific scoring system.

---

# 5. Knowledge / memory thesis

The product should not rely on “Claude remembering”.

Instead it should build structured, durable knowledge:

Observation
→ Experiment
→ Finding
→ Claim
→ Conditions
→ Counter-evidence
→ Confidence
→ Status

A model-generated statement does not become knowledge automatically.

Knowledge should require:
- provenance;
- evidence;
- validation status;
- conditions;
- timestamp;
- ability to be superseded or invalidated.

Important concept:
> Negative knowledge is valuable.

Example:
> “We have tested gas-storage level variants against this target 14 times; none survived holdout. Do not revisit without a material regime change.”

Potential moat:
- institutional research memory;
- experiment history;
- accumulated evidence;
- signal decay history;
- firm-specific methodology.

---

# 6. Incentive / economic scorecard concept

The AI researcher should not simply maximize P&L.

That would encourage:
- overfitting;
- hidden risk;
- leakage exploitation;
- unstable strategies;
- reward hacking.

Potential reward structure includes:
- out-of-sample validity;
- prospective economic value;
- stability;
- simplicity;
- false-discovery penalties;
- novelty;
- useful negative findings;
- compute / data efficiency.

Possible progression:

Research account
→ paper portfolio
→ shadow portfolio
→ production portfolio

Possible agent scorecard:
- hypotheses investigated;
- hypotheses promoted;
- holdout pass rate;
- forward survival;
- false discovery rate;
- economic contribution;
- research ROI.

Potential objective:
> **Validated research value per unit of research budget / senior-quant attention.**

---

# 7. Claude Code — Experiment 1 investigation result

Claude Code ran a large read-only research workflow.

High-level conclusion:

> **RESEARCH MORE BEFORE CODING**

It concluded:
- broad automated discovery is not credible as stated;
- realistic effects may be small;
- lag / regime identification is difficult;
- repeated adaptive holdout use is dangerous;
- point-in-time data availability is the gating issue;
- t0 is not relevant for Experiment 1;
- classical models are more appropriate.

It selected, conditionally:

> **Great Britain imbalance-price forecasting at +2h using NESO wind-forecast revisions**

Reason:
- potentially free;
- machine-checkable timestamps;
- revisions;
- economically relevant target;
- better point-in-time feasibility than Germany / France.

But this depends on Stage 0 confirming Elexon archive semantics:
1. archive start date;
2. whether first imbalance-price publication is actually near-real-time;
3. whether UploadTime is genuine first availability.

If those fail, the historical free-data experiment may not exist.

Repository architecture recommendation:
> Option C — preserve Experiment 0 and build Experiment 1 alongside it; extract shared core later only after real reuse exists.

Important interpretation:
Claude Code mostly designed a **scientifically valid referee/harness**, not yet an autonomous AI researcher.

---

# 8. Six Claude.ai Deep Research investigations

Six independent Deep Research prompts were launched.

The six topics were:

1. Quant Research Workflow Archaeology
2. Quant Tool Stack & Competitor Reconstruction
3. Quant Trust / Validation / Failure Modes
4. Signal Research → Production Workflow
5. Security / Procurement / Deployment Constraints
6. Commercial Value / Willingness to Pay

Four early reports already showed strong convergence:

## Repeated finding A — the “AI junior quant” itself is increasingly commoditized

Evidence cited across reports includes:
- Man Group AlphaGPT;
- Balyasny BAMAgent;
- Bridgewater AIA Labs;
- Microsoft RD-Agent(Q);
- QuantConnect Mia;
- KelAI;
- frontier coding agents;
- Anthropic/OpenAI financial-services tooling.

Common conclusion:
> Hypothesis generation, coding and backtesting are becoming commodity capabilities.

## Repeated finding B — the bottleneck shifts downstream

Repeatedly identified bottlenecks:
- validation;
- multiple testing;
- leakage;
- point-in-time correctness;
- reviewer fatigue;
- signal monitoring;
- institutional memory.

Common phrase emerging from reports:
> More hypotheses are cheap; trustworthy rejection is scarce.

## Repeated finding C — top-tier firms are poor initial customers

Top firms:
- have money;
- have strong internal platforms;
- treat research methodology as core IP;
- are building AI internally.

Potential external buyer segment:
- mid-tier systematic funds;
- commodity / energy desks;
- utilities;
- smaller prop / research teams.

But:
- budgets are smaller;
- data is messier;
- integration burden is higher.

## Repeated finding D — likely wedge is referee + ledger + memory

The four reports broadly converged on:
- Quant Research Referee / Control Plane;
- Research Ledger;
- Research Knowledge System;
- prospective signal-decay monitoring.

Agentic research becomes an expansion layer rather than the initial wedge.

## Repeated finding E — commercial risk remains high

Main concerns:
- sophisticated firms build internally;
- smaller firms may not pay enough;
- methodology enforcement may feel like something quants should own themselves;
- founder lacks quant-native credibility;
- internal-build threat is strong;
- “more alpha ideas” has low marginal value.

The remaining two reports should be used to confirm or overturn this convergence.

---

# 9. Important distinction to preserve

Do not conflate:

> “The standalone autonomous AI junior quant product is weak”

with:

> “There is no valuable product here.”

The current hypothesis is that value may live one layer below:

> **Research governance / referee / memory infrastructure for humans and agents**

Possible sequencing:

### Product B first
Quant Research Referee / Control Plane

### Product C alongside
Research Knowledge / Evidence Ledger

### Product A later
AI Quant Researcher operating inside the control plane

### Product D eventually
AI Research Workforce Platform:
- multiple agents;
- mandates;
- permissions;
- budgets;
- track records.

The next synthesis must decide whether this sequencing is actually supported.

---

# 10. Current founder-level question

The founder wants to know:

> **Are we converging toward a valuable company, or merely discovering a technically interesting but commercially weak research tool?**

This is the central decision question.

---

# 11. How the next conversation should process the evidence

Please do NOT immediately summarize everything.

Use the following process.

## Step 1 — Ingest all evidence

Read:
- all 6 Claude.ai Deep Research reports;
- the latest Claude Code output / memo;
- any relevant Experiment 0 / Experiment 1 material supplied.

Do not rely only on excerpts.

## Step 2 — Build an evidence matrix

For each major thesis, classify:

- supported;
- partially supported;
- contradicted;
- still unknown.

At minimum assess:

1. Research throughput is a real bottleneck.
2. AI hypothesis generation is differentiated.
3. A referee/control plane solves a real problem.
4. Research memory solves a real problem.
5. Signal-decay monitoring has standalone value.
6. Mid-tier systematic funds will buy.
7. Energy / commodity desks are a better wedge.
8. Top-tier firms are not viable first customers.
9. Internal-build risk is acceptable.
10. A solo founder can build the first credible MVP.
11. Security / deployment does not kill the model.
12. The business can become venture-scale.

## Step 3 — Separate technical and commercial truth

Produce separate verdicts on:

### Technical feasibility
Can this system be built?

### User value
Does it solve an actual painful workflow?

### Buyer willingness
Will someone pay?

### Defensibility
Can it avoid becoming a feature?

### Founder feasibility
Can this founder credibly reach first pilots?

### Venture potential
Can it become a large company?

Do not collapse these into one score.

## Step 4 — Compare four product forms

Evaluate independently:

### A. AI Quant Researcher
Autonomous hypothesis generation and experimentation.

### B. Quant Research Referee / Control Plane
Point-in-time, leakage-safe, statistically disciplined experiment governance.

### C. Research Knowledge System
Experiment memory, negative results, claims, evidence, decay.

### D. AI Research Workforce Platform
Multiple configurable research agents with mandates, permissions, budgets and track records.

For each assess:
- pain;
- buyer;
- urgency;
- differentiation;
- implementation complexity;
- internal-build threat;
- sales friction;
- pricing potential;
- expansion path.

Do NOT assume B or C wins merely because earlier reports leaned that way.

## Step 5 — Identify the narrowest falsifiable wedge

If a business remains credible, define:

- exact initial customer;
- exact user;
- exact workflow;
- exact pain;
- exact input data;
- exact output;
- exact proof of value;
- exact MVP;
- what is explicitly NOT in MVP.

## Step 6 — Define kill criteria

State what evidence should cause:
- STOP;
- PIVOT;
- CONTINUE;
- BUILD PILOT.

These should include practitioner interview results, technical proof results and willingness-to-pay evidence.

## Step 7 — Recommend immediate next actions

The answer should end with a concrete 2–4 week plan.

Likely ingredients:
- finish / assess Stage 0;
- practitioner interviews;
- technical referee benchmark;
- zero or minimal product coding until commercial unknowns are reduced.

But do not assume this is correct before reading the evidence.

---

# 12. Desired reasoning style

Be:
- skeptical;
- explicit about uncertainty;
- commercially hard-nosed;
- technically rigorous;
- willing to recommend STOP.

Do not:
- flatter the founder;
- confuse a technically elegant problem with a valuable company;
- assume a venture-scale outcome;
- overvalue LLM novelty;
- let the existence of competitors automatically imply either validation or saturation;
- assume all hedge funds are alike.

Most important:
> Distinguish what the sources actually establish from inference.

---

# 13. Desired final output of the synthesis

The final synthesis should answer:

1. **What have we actually learned?**
2. **What thesis has been killed?**
3. **What thesis survives?**
4. **What remains unproven?**
5. **What is the best current product wedge?**
6. **Who exactly is the first customer?**
7. **What is the fundamental technical proof?**
8. **What is the fundamental commercial proof?**
9. **Should the founder continue?**
10. **What should happen next, in order?**

End with one of:

- **STOP**
- **PIVOT AND TEST**
- **CONTINUE RESEARCH**
- **BUILD MVP**
- **BUILD PILOT**

No blended verdict.

---

# 14. Important files expected in the new conversation

The founder should upload:

- all six Claude.ai Deep Research outputs;
- latest Claude Code Experiment 1 / Stage 0 result;
- optionally the Experiment 1 decision memo if not already contained in the Claude Code result.

If filenames are opaque, identify each report by content rather than filename.

