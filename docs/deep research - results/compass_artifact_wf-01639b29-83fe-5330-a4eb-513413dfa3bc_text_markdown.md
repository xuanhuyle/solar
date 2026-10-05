# Quant Research Workflow Archaeology: Would an AI-Native Junior Quant Researcher Remove a Real Bottleneck?

An AI junior quant researcher would remove a real bottleneck: repetitive work on data, code and backtests. But the most sophisticated firms, the ones with the most budget, are already building this themselves. For them the scarce resources are validation capacity, proprietary data and senior judgment, not hypotheses. The defensible opening is therefore not "an AI that generates more alphas." It is the **referee/control plane plus research memory**, sold first to mid-tier systematic teams and energy/commodity desks that cannot build what Man Group, Balyasny, D.E. Shaw, Citadel and HRT have built.

## TL;DR

- **The bottleneck is real but has moved.** [FACT] Man Group says off-the-shelf LLMs already handle "intern-level work effectively, writing code and summarising research." Its in-house AlphaGPT proposes signals, writes code and backtests them; Bloomberg (July 2025) reported that several dozen of its signals had passed Man's investment committee and were slated for live trading. Man's own list of problems (hallucination, lookahead bias, multiple testing, and the need to "expand monitoring infrastructure to handle increased signal volume") shows the constraint shifting from *generating* research to *validating and absorbing* it. [INFERENCE] More hypotheses are cheap. Trustworthy rejection is scarce.
- **Top firms are building in-house; the gap is below them.** [FACT] Balyasny (~95% of investment teams on its AI platform), D.E. Shaw (an internal Assistants/LLM Gateway/DocLab stack), Bridgewater (AIA Labs, fine-tuning its own model with Thinking Machines), HRT (pre-training its own LLMs) and Jane Street (training its own code model for OCaml) have all built their own tooling. Man Group expects agentic workflows to be commoditised and places its edge in proprietary data, infrastructure and "institutional memory." [INFERENCE] An external "AI researcher" is largely redundant at tier-1 firms. The buyable market is mid-tier systematic funds, discretionary funds with thin quant benches, and utility and commodity analytics desks.
- **Verdict: MIXED.** The evidence supports a narrowly scoped **Quant Research Referee + Research Knowledge System**, sold as leakage, multiple-testing and reproducibility enforcement around the customer's own humans and agents. It weakens the broad "hire an AI junior quant to find alpha" pitch. Ken Griffin's October 2025 verdict was that GenAI "just falls short" for uncovering alpha, though by May 2026 he said agents do PhD-level research work "over the course of hours or days." Alpha attribution to an external agent will be nearly impossible to prove, and LLMs carry structural lookahead contamination.

## Key Findings

### 1. Executive conclusion

- [FACT] Leading firms explicitly frame human bandwidth as a bottleneck. Man Group: "human bandwidth stays constant… human researchers can only examine a limited subset of possibilities at any given time." Man Numeric's Ziang Fang: "Previously, a researcher had to manually figure out how to handle all the alternative datasets, which took a long time and many steps are repetitive."
- [FACT] The same firms report that automated ideation creates new downstream load. Man says AlphaGPT's speed raises "the probability of discovering patterns that appear significant but represent statistical artefacts," and that it is "expanding our monitoring infrastructure to handle increased signal volume." Every AI signal still goes through Investment Committee review plus technology-team code review.
- [INFERENCE] The bottleneck an AI junior quant *creates* (review, validation, monitoring capacity) is as large as the one it removes (coding, data wrangling). A product that only increases hypothesis throughput makes the customer's real constraint worse. A product that makes rejection cheap, trustworthy and auditable relieves it.
- [INFERENCE] Buyers split into two groups. Tier-1 systematic and multi-strategy firms have the budget but are building in-house. Mid-tier, discretionary-with-quant-support and energy desks have the pain and lack internal AI platforms, but have smaller budgets, messier data and less standardised research processes.
- **Recommendation:** Do not build "an AI quant that finds alpha." Consider building the **referee/control plane + research memory**, with an embedded agent as a feature rather than the product. Validate it first with energy/commodity analytics desks and $1–20bn systematic managers.

### 2. End-to-end workflow map

Maturity differs sharply by firm type, so treat this as a composite. Time burdens are mostly UNKNOWN; credible quantitative time-allocation data for quant research specifically does not exist in the public record.

| Stage | Typical owner | Typical tools | Manual vs automated | Common failure modes | Senior judgment? | AI-automatable? |
|---|---|---|---|---|---|---|
| Idea / market observation | PM, senior QR, trader; increasingly LLM "idea agents" | Papers, sell-side, conversations, internal dashboards | Mostly manual; AlphaGPT's "Idea Person" automates part of it at Man [FACT] | Crowded or published ideas (post-publication decay) | High (choosing what's worth testing) | Partly; ideas are cheap, selection isn't |
| Research question formulation | Senior QR / PM | Notes, research committee | Manual | Vague hypotheses that invite p-hacking | High | Low–medium (agent can draft; human approves) |
| Dataset discovery / procurement | Data strategy team, data engineers, PM | Vendor catalogs, trials, legal/compliance review | Manual, contract-heavy | Survivorship/backfill in vendor trials; licensing limits | Medium–high (buy decisions) | Low for procurement; medium for evaluation |
| Historical reconstruction (point-in-time) | Quant devs / data engineers | Internal time-series stores, vintage databases | Largely engineered at top firms; manual at small ones [INFERENCE] | Restatements, revised fundamentals, weather-forecast vintages not stored | Medium | Medium; hard to verify without ground truth |
| Cleaning / timestamp alignment | Junior QR, quant dev | Python/pandas, SQL, internal libraries | Manual and repetitive | Timezone, DST, delivery-period, and publication-lag mismatches | Low–medium | **High** |
| Feature engineering | QR | Python, internal factor libraries; WorldQuant-style operator grammars | Increasingly templated [FACT: WorldQuant BRAIN operator/field combinatorics] | Leakage via future-dated features; redundant features | Medium | **High** |
| Exploratory analysis | QR | Notebooks | Manual | Garden-of-forking-paths searching | Medium | High (with logging) |
| Model / factor construction | QR | Internal libs, ML frameworks | Mixed | Overfitting; spurious complexity | Medium–high | Medium–high |
| Backtesting | QR, platform team | Internal backtesters | Automated engine; manual setup | Unrealistic costs, lookahead, wrong universe | Medium | **High** (setup) |
| Robustness checks | QR, reviewer | Internal harnesses | Mixed | Selective reporting of passing variants | High | **High** for execution; judgment remains human |
| Peer / senior review / committee | Senior QR, PM, investment committee | Memos, meetings | Manual | Reviewer fatigue; unseen trial counts | **Very high** | Low (support only) |
| Paper / shadow trading | QR + platform | Production-like sim | Automated once set up | Insufficient duration to judge | Medium | Medium |
| Productionization | Quant devs, tech teams | Code review, unit/integration tests | Manual engineering | Research-prod code divergence | Medium | Medium (Man uses tech review of AI code [FACT]) |
| Live monitoring | QR, risk, PM | Dashboards, alerts | Semi-automated | Slow detection of decay; alert fatigue | Medium–high | High for detection; low for kill decisions |
| Retirement / post-mortem | PM, senior QR | Informal notes | Largely manual and often skipped [INFERENCE] | Lost institutional memory; re-testing failed ideas | High | **High** for documentation/memory |

[FACT] Man's AlphaGPT maps onto this chain directly: an "Idea Person" (hypothesis generation), an "Implementer" (production-grade Python against proprietary databases) and an "Evaluator" (statistical significance, risk, economic-reasoning checks). Output then goes into dual-track human validation: Investment Committee for hypothesis and rationale, technology teams for code review and tests. [INFERENCE] This is the clearest public evidence of which stages a leading firm considers automatable (idea → code → first-pass evaluation) and which it keeps human (committee approval, production review).

### 3. Who does what

- **Interns / junior QRs** [INFERENCE from job descriptions and practitioner accounts]: data cleaning, replicating papers, running backtest variants, building features, writing research memos. [ANECDOTE] A systematic hedge fund QR who tracked his hours for a year averaged 10.7 hours/day and said "some grind work was unavoidable, including data cleaning and reporting, anything that was not pure research or production trading code."
- **Quant developers**: data pipelines, feeds, infrastructure, productionization. [ANECDOTE] A QuantStart author describing a hedge fund quant-dev role said that connecting to data sources, storing, cleaning and presenting pricing data "was about 80% of my job." [ANECDOTE] A Mayfair quant dev's day starts with checking that overnight data-download cron jobs ran and fixing incomplete jobs.
- **Senior QRs / PMs**: choose questions, approve methodology, judge economic rationale, allocate risk. [FACT] Man keeps Investment Committee approval human, and Citadel's CTO said "We don't want PMs offloading their human investment judgment to AI" (reported secondhand in a Substack; treat as ANECDOTE-grade sourcing).
- **Energy/utility quants** [FACT from job postings]: ENGIE's Senior Quantitative Analyst role (power markets forecasting and pricing) includes partnering with senior analysts to "productionize forecasting models," troubleshooting production issues, and supporting budget and margin-forecasting tools. Statkraft's systematic-trading quant must "design, backtest and implement systematic trading strategies," maintain trading infrastructure, and "collaborate with IT to develop and maintain historical price database." Trafigura's data science track includes "managing a large data platform containing 100's of data sources such as market data, weather data, vessel tracking information." [INFERENCE] Energy quants spend much more time on production support, fundamental forecasting and data plumbing than equity-alpha researchers do. They are hybrid analyst-engineer-support roles.

### 4. Where time is actually spent

- [FACT] No credible public survey measures time allocation for quant researchers specifically. The famous "80% of time cleaning data" claim is largely a myth even for general data science. Leigh Dodds traced it to CrowdFlower surveys that only reach 80% when data collection is included. Kaggle's 2018 survey found ~15% on cleaning and ~11% on gathering data. Anaconda's 2020 survey found ~45% on data preparation.
- [ANECDOTE] Practitioner accounts consistently place data and pipeline work as the largest non-research time sink (QuantStart quant dev "about 80%"; the systematic QR above citing unavoidable data cleaning and reporting).
- [FACT] Man Group claims AlphaGPT compresses coding "what might take a human researcher hours or days to code and debug" into minutes, and ideation from days to minutes. These are vendor-of-itself claims with no disclosed measurement.
- [FACT] Balyasny reports deep research tasks going from days to hours, and OpenAI's March 2026 case study says a "Central Bank Speech Analyst" agent cut macroeconomic scenario analysis "from 2 days to about 30 minutes." Its applied-AI lead Charlie Flanagan anticipated the bot would relieve about 10% of analyst workload. This is discretionary analyst work, not quant research.
- [FACT] Ken Griffin (May 2026, Stanford) put AI gains in software engineering at 15–25%. He said research work that took "people with master's and PhDs in finance… weeks or months is being done by AI agents over the course of hours or days."
- [FACT] Counterweight: METR's randomized trial found experienced open-source developers were 19% *slower* with early-2025 AI tools while believing they were 20% faster. METR's own February 2026 update estimated a −4% speedup (CI −15% to +9%) among newly recruited developers, which METR calls "an unreliable signal" and "likely a lower-bound." [INFERENCE] Self-reported AI productivity claims from funds should be discounted. Customers will overestimate gains, which helps early sales and hurts renewals.

### 5. Bottleneck ranking

Scores are INFERENCE, synthesised from the evidence above; treat them as hypotheses to test in interviews.

| Rank | Bottleneck | Frequency | Cost | Seniority consumed | Agentic suitability | Notes |
|---|---|---|---|---|---|---|
| 1 | **Validation capacity** (review, multiple-testing control, leakage audit) | Every idea | Very high (false positives reach capital) | Senior | Medium–high (enforcement automatable; judgment not) | Man explicitly scaling oversight for AI signal volume [FACT] |
| 2 | **Data wrangling / timestamp alignment / PIT reconstruction** | Constant | High | Junior + quant dev | High (execution) / low (verification without ground truth) | Energy: weather-forecast vintages, delivery periods |
| 3 | **Repetitive coding + backtest setup** | Constant | Medium | Junior–mid | **Very high** | Already the most-adopted LLM use case [FACT] |
| 4 | **Duplicated / forgotten research, irreproducible old work** | Periodic | Medium–high (hidden) | Mid–senior | High | Man cites "institutional memory" as its edge [FACT]; no public measurement [UNKNOWN] |
| 5 | **Monitoring & signal decay** | Continuous | High | Mid–senior | High for detection | Post-publication anomaly returns fall ~58% [FACT, McLean–Pontiff] |
| 6 | **Production handoff** | Per promoted signal | Medium | Quant dev | Medium | Man requires unit/integration tests of AI code [FACT] |
| 7 | **Documentation** | Constant | Low–medium | All | Very high | Low willingness-to-pay alone [INFERENCE] |
| 8 | **Dataset discovery / procurement** | Periodic | High $ | Senior + legal | Low–medium | Contract/legal-bound |
| 9 | **Idea generation** | — | Low marginal value | Senior | Very high | Oversupplied: WorldQuant had "millions" of alphas [FACT] |

### 6. Current AI usage

**Coding productivity** (most widespread):
- [FACT] Griffin (2023) described Citadel seeking an enterprise ChatGPT licence for "helping our developers write better code to translating software between languages."
- [FACT] Jane Street trained its own code model because off-the-shelf LLMs handle OCaml poorly (talk notes by Shekhar Gulati).
- [FACT] Goldman rolled GitHub Copilot and Gemini Code Assist out to engineers first.

**Data work / alternative data**:
- [FACT] Man's Fang describes agents automating the repetitive steps of processing alternative datasets.
- [FACT] Trafigura's graduate data-science track lists "deploying agentic AI" alongside managing hundreds of data sources.

**Literature review / document research**:
- [FACT] Balyasny's BAM ChatGPT and agent platform are used by ~95% of investment teams, with an evaluation pipeline across 12+ dimensions (OpenAI case study, March 2026).
- [FACT] D.E. Shaw's Assistants/LLM Gateway/DocLab stack lets desks build tools "with as little as ten lines of code," with central prompt logging (reported by Resonanz Capital from Business Insider). Treat details as secondary.

**Factor generation / experiment automation**:
- [FACT] Man AlphaGPT (idea→code→backtest), most successful in systematic equities.
- [FACT] The academic Alpha-GPT system ranked top-10 among 41,000+ teams in WorldQuant's IQC 2024.
- [FACT] Open-source repos automate LLM-driven alpha mining against WorldQuant BRAIN's API.
- [FACT] Bloomberg (April 2025) reports that machine learning "now powers about a fifth of the trading signals" in AQR's flagship multi-strategy fund. This is ML, not LLM agents.

**Model research**:
- [FACT] HRT's HAIL team builds LLMs "from scratch — pretraining, post-training, and serving" deployed "to accelerate research, engineering, and trading workflows."
- [FACT] Bridgewater fine-tuned an open-weight model with Thinking Machines on examples labelled by its investment experts.

**Production use**:
- [FACT] Bridgewater's AIA Labs macro strategy (launched July 2024 with ~$2bn) uses machine intelligence as the primary decision-maker, with humans overseeing risk management, data acquisition and trade execution.
- [FACT] Man has AI-generated signals that passed its investment committee and were slated for live trading (Bloomberg, July 2025).

**Energy/commodities**:
- [FACT] Uniper rolled out Microsoft Copilot to all employees and describes an energy trading use case where AI evaluates past transactions to recommend timing, but "the final decision is still made by the trader or trading team."
- [FACT] Mercuria is hiring to fine-tune and pre-train "large-scale AI models (e.g., transformers, latent diffusion models, graph neural networks)" for energy trading on GPU clusters.
- [FACT] Vitol CEO Russell Hardy (March 2025): AI is "a very valuable add on, but for us, it's not going to change the business in the end."

**Where LLMs fail** (practitioner and academic evidence):
- [FACT] Man lists hallucination, idea-implementation drift ("might conceptualise one research idea but implement something different"), lookahead bias and multiple testing.
- [FACT] Sarkar and Vafa found Llama 2, when asked about risks in September–November 2019 earnings calls, mentioned Covid-19 in over 25% of cases. This is lookahead contamination from training data.
- [FACT] Gao, Jiang and Yan (2025) find "a non-trivial share of the apparent predictive content of LLM-based forecasts in finance reflects memorization."
- [FACT] HRT's Marc Khoury: "LLMs are good at predicting one minute out, but not fast enough to monetize it."

### 7. Tasks suitable for an AI junior quant (no capital authority)

[INFERENCE, grounded in Man's split between automated and human stages and in job-description evidence]
1. **Paper and idea replication**: turn a paper or memo into a pre-registered test spec plus code on the firm's data.
2. **Data onboarding**: profile a new dataset, test point-in-time integrity (publication lags, revisions, coverage, survivorship), align timestamps, and write a data-quality report.
3. **Backtest setup and variant sweeps inside a locked harness**, with every trial logged so multiple-testing corrections see the true trial count.
4. **Robustness batteries**: subperiods, regimes, cost sensitivity, universe perturbations, placebo/permutation tests, and deflated-Sharpe-style adjustments.
5. **Research memo drafting** from logged evidence, not free prose.
6. **Research memory curation**: tag what was tested, what failed and under what conditions; flag duplicates of past work before a human spends time on it.
7. **Monitoring**: decay detection, live-vs-backtest attribution, and drafted retirement recommendations.
8. **Energy-specific**: rebuild forecast-vintage datasets (weather, load, renewables), maintain fundamentals pipelines, and backtest bidding rules against the forecasts the market actually saw.

### 8. Tasks that should remain human

- Choosing research direction and what the firm's edge is (Man: humans provide "strategic direction, market context, and final decision-making") [FACT].
- Methodology approval, including holdout policy, significance hurdles and acceptable data.
- Judging economic rationale. AQR's Bryan Kelly argues it can be "bad science" to discard reliably predictive signals lacking intuition [FACT], so this is contested judgment, not a rule.
- Promotion to production, sizing, capital allocation, kill decisions.
- Data procurement and licensing decisions.
- Any live execution decision on physical/energy books (Uniper: final decision stays with traders) [FACT].

### 9. Evidence against the product thesis

1. **Top firms build, not buy.** [FACT] Man, Balyasny, D.E. Shaw, Bridgewater, HRT and Jane Street all have internal stacks; HRT spent $1 billion per year on AI as of 2025 and 2026 (Wikipedia, citing Bloomberg), and Disruption Banking reports its head of AI "works with a budget of approximately $1 billion per year." Man expects agentic workflows to be commoditised and says its edge is proprietary data, infrastructure and institutional memory. [INFERENCE] An external vendor's agent would be outclassed at the top and would face data-security objections to touching proprietary data.
2. **Ideas are not scarce.** [FACT] WorldQuant set a million-alpha target in 2010, hit it in 2016, and now has "millions," with 1,400+ datasets and a crowdsourced consultant base. [INFERENCE] Hypothesis volume is an oversupplied input at scale-oriented firms.
3. **Most "discoveries" are false or decay.** [FACT] Harvey, Liu and Zhu argue new factors need t > 3.0 and that "most claimed research findings in financial economics are likely false." McLean and Pontiff find anomaly returns 26% lower out-of-sample and 58% lower post-publication. [INFERENCE] An agent that tests more hypotheses raises false-discovery risk unless a referee controls it. This supports the referee component and weakens the generator component.
4. **Alpha scepticism from the most credible voice (but shifting).** [FACT] Griffin, October 2025: "With GenAI there are clearly ways it enhances productivity, but for uncovering alpha it just falls short." By May 2026 he described agents doing PhD-level research in hours or days. [INFERENCE] Productivity value is accepted; alpha value is disputed. Price on productivity and validation, not alpha share.
5. **LLM lookahead contamination is structural.** [FACT] Memorisation of post-period outcomes is documented, and mitigations (entity masking, post-cutoff-only evaluation, time-stamped models like ChronoBERT/ChronoGPT) are "useful but partial" per Gao, Jiang and Yan. [INFERENCE] Any LLM-generated hypothesis tested on pre-cutoff data is contaminated in a way no deterministic control plane fully removes. The real fix is prospective (post-cutoff, sealed forward) evaluation, which is slow.
6. **Energy/commodity bottlenecks are data, physical operations and trader judgment.** [FACT] Vitol's CEO frames AI as an efficiency add-on that won't change a physical-supply business. Trafigura's and Statkraft's quant roles centre on data platforms and infrastructure. [INFERENCE] In energy, the product must be a data and forecast-vintage machine first.
7. **Productivity perceptions are unreliable.** [FACT] METR's 19% slowdown against a 20% perceived speedup.
8. **Trust and liability.** [INFERENCE] Firms are secretive about signals; exposing research logs and hypotheses to a vendor is a governance hurdle. D.E. Shaw's emphasis on central prompt logging and model-use policy suggests firms want control of the audit trail themselves [FACT for the policy; INFERENCE for the implication].

### 10. Narrowest workflow worth automating first

**"Point-in-time dataset onboarding + leakage-audited backtest harness with a trial ledger" for power & gas / commodity analytics desks and mid-tier systematic teams.**

- Input: a new dataset (vendor or internal) plus a hypothesis spec.
- The system checks point-in-time integrity (publication times, revisions, forecast vintages), aligns to the trading calendar and delivery periods, runs a pre-registered baseline and robustness battery in a sealed harness, logs every trial, applies multiple-testing adjustments using the true trial count, and writes a structured evidence record to research memory.
- The agent does the work; the control plane is the product.

Why this wedge [INFERENCE]:
- It targets the #1–#4 bottlenecks rather than the oversupplied idea stage.
- It is valuable whether or not the customer uses LLMs, and it also referees *their own* humans and in-house agents. That is the one thing Man says it had to build for AlphaGPT.
- Energy desks have the clearest data pain (weather/load/renewables vintages, hundreds of sources per Trafigura) and the least in-house AI platform depth, based on the absence of public evidence of LLM agents in their analytics teams (UNKNOWN whether that absence is real or just undisclosed).
- The output is auditable, which suits model-risk-minded buyers.

## Caveats

- Almost all evidence of AI inside top firms is self-reported by the firms (Man, Balyasny via OpenAI, Bridgewater) or via journalism and Substack intermediaries (D.E. Shaw, Citadel CTO quote). None disclose measured productivity or alpha attribution. Treat efficiency claims as marketing-adjacent.
- There is no public, credible time-allocation data for quant researchers. The bottleneck ranking is inference.
- Energy/commodity workflow evidence comes mostly from job postings and executive soundbites. No named practitioner at RWE, EDF Trading, Axpo, Ørsted, Gunvor or BP described internal research workflows or LLM use in sources found.
- The Man "several dozen signals" figure comes from Bloomberg (July 2025), which reported they had passed the investment committee and were "slated to be deployed in live trading." Man's own article says only that signals "meet our standards."
- METR itself calls its February 2026 follow-up data "an unreliable signal"; the original 19% result is from its 2025 randomized trial.

## Implications for the AI Quant Researcher Thesis

**1. What the evidence supports**
- Repetitive coding, data onboarding and backtest execution are real, recognised burdens that LLM agents can already do at "intern level" (Man) [FACT].
- The referee concept is validated by the leader: Man had to build validation stages, consistency checks between idea and implementation, full decision logging, and expanded monitoring to make agentic research safe [FACT]. Separating proposer from enforcer mirrors what practitioners built.
- Research memory and institutional knowledge are named as durable edges (Man) [FACT]. Post-publication decay (McLean–Pontiff) and false-discovery rates (Harvey–Liu–Zhu) make trial ledgers and decay tracking economically meaningful [FACT/INFERENCE].
- Energy/commodity desks show heavy data-platform and production-support burdens (Trafigura, Statkraft, ENGIE postings) [FACT].

**2. What the evidence weakens**
- "Firms want more hypotheses": weakened. Ideas are oversupplied (WorldQuant's millions of alphas), and more tests raise false-discovery risk [FACT/INFERENCE].
- "Top systematic funds will hire an external AI researcher": weakened. They are building their own, down to pre-training models (HRT, Jane Street, Bridgewater, Mercuria) [FACT].
- "Track record proves value": weakened. Alpha attribution to one contributor inside a firm's portfolio is hard to establish, and LLM lookahead contamination undermines historical evidence [FACT/INFERENCE].
- "The AI can do end-to-end research": weakened for now. Man still "can't leave it unsupervised just yet," and success so far is concentrated in systematic equities [FACT].

**3. What remains unknown (not resolvable through desk research)**
- Actual hours per stage at mid-tier and energy firms, and who does them.
- Whether mid-tier firms already track trial counts and research lineage, or would pay for it.
- Security and procurement tolerance for a vendor agent running inside their data environment (on-prem/VPC requirements).
- Whether energy desks' bottleneck is research validation at all, or mainly production support and data plumbing.
- Budget owner: head of research, CTO, CRO/model risk, or PM pods.
- How often old research is unknowingly repeated, and what it costs.

**4. The 5 most important questions to ask practitioners**
1. "Walk me through the last three ideas your team killed. How long did each take from proposal to rejection, and which step consumed the most senior hours?"
2. "When someone reports a backtest, can you tell me how many variants were tried before it? Where is that recorded, and has a false positive ever reached production because it wasn't?"
3. "If you had twice as many tested hypotheses next quarter, could your review, committee and monitoring process absorb them? What would break first?"
4. "How do you reconstruct what data was known at each historical timestamp (revisions, forecast vintages, publication lags)? Who maintains it, and how often does it fail?"
5. "Have you built, or are you building, internal LLM/agent tooling for research? What did it fail at, and what would you never let an external system touch?"

**5. Verdict: MIXED**
The broad thesis, an external AI junior quant hired to generate and test alpha, is weakened: top firms are building it themselves, ideas are not scarce, and alpha value is disputed. The narrower thesis, a deterministic **referee/control plane plus research knowledge system** with an embedded agent, sold first to energy/commodity analytics desks and mid-tier systematic teams, is supported by the leader's own experience of what agentic research requires. Build only if customer interviews confirm that validation capacity and research lineage, not data procurement or execution, are what those buyers will pay to fix. Otherwise, do not build.