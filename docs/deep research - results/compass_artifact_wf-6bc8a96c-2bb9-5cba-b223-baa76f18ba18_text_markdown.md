# Is Quant Research Labor Valuable Enough to Automate? A Hard-Nosed Commercial Test of the AI Quant Researcher Thesis

Quant research labor is expensive and scarce enough that firms are already automating it, but the firms that feel the pain most acutely (Man Group, Balyasny, Bridgewater) are building it themselves. The public evidence suggests that "more valid research conclusions per senior-quant hour" is a real but second-order value driver next to proprietary data, capital, PM talent and execution. An autonomous AI junior quant sold as a standalone product (Product A) is therefore a weak venture wedge. The more defensible opening is a research referee and evidence ledger (Products B and C) sold to mid-tier systematic funds and energy/commodity desks, with agentic research as the expansion.

## TL;DR

- **Labor is costly but not the binding constraint at the top.** Junior quant researchers cost roughly $200–300k in US total compensation and up to £144k in London. Pay is extreme at the PM tier (nine-figure multi-manager packages; Jane Street averaged about $2.68m per employee in 2025). But elite firms openly say their edge is data, infrastructure and institutional memory, and they are building AI research agents in-house (Man Group's AlphaGPT, Balyasny's 20-person Applied AI team, Bridgewater's AIA Labs).
- **Faster hypothesis generation is becoming commoditized; valid evaluation is not.** Man Group itself says the binding risk of AI-generated research is multiple testing and signal-volume oversight. WorldQuant pays its best crowdsourced alpha contributors on the order of $8,000 per quarter. Ken Griffin says GenAI "falls short" for alpha. All three point to low marginal value for raw idea volume and higher value for the control plane that decides what is real.
- **Verdict: WEAKENS for the thesis as framed (Product A first).** A venture-scale path exists only if (a) the referee/knowledge layer (B+C) becomes the system of record for research governance at hundreds of mid-tier firms and energy desks that cannot build it, and (b) agent throughput is layered on top once trust exists. Validate that in interviews before writing code.

## 1. Executive conclusion

**Core question:** Is quant research capacity expensive, scarce and bottlenecked enough that a professional trading organization would pay materially for an AI system that increases valid research conclusions per senior-quant hour?

**Answer: Partially, and not for the buyers you would most like to sell to.**

- **FACT:** Research labor is expensive. In London, eFinancialCareers survey data put hedge-fund quant researchers with 1–3 years' experience at up to £144k total compensation, and quant research team leads at up to £750k ($1m).
- **FACT:** The most sophisticated firms say research bandwidth is a bottleneck. Man Group writes that "Quantitative research now faces more data and potential market relationships than human researchers can possibly explore" and that "human bandwidth stays constant."
- **FACT:** Those same firms treat the solution as proprietary. Man says its edge lies in "proprietary data sources and technology infrastructure built over decades" plus "institutional memory." It expects "LLMs and agentic workflows are likely to see widespread adoption" and that "early-mover technology advantages are inherently temporary."
- **INFERENCE:** The top tier (Citadel, Jane Street, Man, Bridgewater, Balyasny, Two Sigma, D. E. Shaw) is not a buyer for Product A. They are competitors or, at best, buyers of components.
- **INFERENCE:** The addressable buyer is the long tail: sub-$10bn systematic funds, prop firms without large research platforms, utilities, and commodity desks building quant capability. These firms feel labor scarcity but have smaller budgets, messier data and higher integration burdens.
- **INFERENCE:** The economic value of an extra valid conclusion is highly convex and highly uncertain. Most tested ideas fail. Signal decay and crowding erode what survives, and capacity limits cap monetization. Throughput matters only if the evaluation process is trustworthy. That makes the referee (B) and evidence ledger (C) more valuable, and easier to trust, than the researcher (A).

## 2. Research labor economics

### Compensation (treat all non-filing figures as indicative)

| Segment | Figure | Source type | Label |
|---|---|---|---|
| US QR base salary, national average | $190,310 (New York $197,753) | H1B-derived, via a quant-careers Substack | FACT (secondary aggregation) |
| US QR/QD base at top funds | Median $200k, p90 $300k; Bridgewater senior quant roles $350–600k | H1B LCA + ATS postings (Recruiting from Scratch) | FACT, but excludes firms that don't post pay |
| US entry-level QR (New York hedge funds) | Base $125–150k, bonus 50–100% → $200–300k TC | Mergers & Inquisitions | ANECDOTE/secondary |
| US junior → senior QR TC | $150–280k junior; $500k–$1m+ senior; principal $600k in a flat year to $1.5m in a good one | Quantt aggregation (explicitly "illustrative") | Estimate |
| London QR 1–3 yrs | Up to £144k TC at hedge funds vs £117k sell-side | eFinancialCareers survey | FACT (survey) |
| London QR team head | Up to £750k ($1m) TC, hedge funds or sell-side | eFinancialCareers survey | FACT (survey) |
| London mid-career QR at top fund | £250–400k TC | Quantt | Estimate |
| Quant interns (Citadel, D. E. Shaw, Point72) | ~$5k/week | eFinancialCareers, reported via Hedge Fund Interview | ANECDOTE |
| Geneva commodity traders | Graduates CHF 90–130k; established traders CHF 150–300k base + 100–300% variable | Upreer career guide | Estimate |
| Commodity-house profit share | Vitol: 450 employee-shareholders shared $6.5bn (~$14m avg); Trafigura: 1,400 shareholders shared $5.9bn for 2023 (~$4m avg) | Bloomberg via eFinancialCareers | FACT (secondary) |
| London energy-trading business analyst | Median £102,500 (only 5 salaries quoted) | ITJobsWatch | FACT, but too thin to generalize |

**Loaded cost (INFERENCE).** Add benefits, payroll taxes, recruiter fees (typically a share of first-year pay), data seats, compute and management time. The fully loaded cost of a junior QR is plausibly $250–400k per year in New York and £180–250k in London. A senior QR is $700k–$2m+. Paris and Geneva sit below London on cash pay for most roles. I found no sourced Paris-specific QR survey; that is **UNKNOWN**. Paris has meaningful quant employers (e.g., CFM, and QRT's Paris presence), but I could not verify their pay data.

**The real scarcity is at the PM/alpha-owner tier, not the junior tier.**
- **FACT:** Hedgeweek, citing the Wall Street Journal, reports multi-manager packages "exceeding $100m."
- **FACT:** With Intelligence states: "Demand for top talent remains greater than the supply of quality PMs."
- **FACT:** Jane Street reportedly paid $9.38bn in compensation on $39.6bn of 2025 trading revenue, about $2.68m per employee (Bloomberg, May 2026), more than double 2024 and almost seven times Goldman Sachs' per-employee figure.
- **INFERENCE:** At firms where revenue per head is $10m+ (Jane Street, HRT; XTX reportedly about $19m per head), the cost of a junior researcher is trivial next to the revenue at stake. The constraint is finding people who produce edge, not paying for hours. That cuts against a "cheaper junior labor" pitch at elite firms and in favor of an "edge-producing capacity" pitch, which is much harder to prove.

**Hiring difficulty and vacancy duration.**
- **FACT:** Quant research hiring "operates almost entirely through referrals, research networks, and specialist recruiting — not job boards" (Recruiting from Scratch).
- **FACT:** Geneva commodity houses hire "through referrals and headhunting."
- **UNKNOWN:** I found no credible public data on quant vacancy duration. Treat any number you hear as anecdote and ask for it in interviews.

**Team sizes and ratios.**
- **FACT:** Balyasny runs about 180 investment teams and built a centralized Applied AI team of 20 researchers, engineers and domain experts (OpenAI case study).
- **FACT:** Bridgewater's AIA Lab was reported as comprising 20 seasoned investors and machine-learning experts, led by chief scientist Jasjeet Sekhon (Business Insider).
- **FACT:** Numerai runs a crowdsourced fund with a core team reported at under 50.
- **UNKNOWN:** Researcher-to-PM ratios are not publicly documented in any reliable way. They vary from pod structures (a PM with a few analysts/QRs) to centralized research at systematic firms.

**Commodity/power vs hedge funds.**
- **FACT:** Trafigura is building a power trading business; Citadel hired a former head of North American power and gas at Energy Aspects; Jane Street has been "amassing power traders" (eFinancialCareers).
- **FACT:** Gunvor advertised a quant developer role on its Cross Barrel desk to maintain infrastructure and work "closely with quant traders and researchers" on execution algorithms.
- **INFERENCE:** Energy desks are building quant capability later than equity quant funds and from a smaller base. That fits the "can't build it all ourselves" profile. But their edge is typically fundamental/physical (assets, flows, weather, grid), not cross-sectional signal mining, which is where Man says AlphaGPT works best ("most successful in systematic equity research").

## 3. Evidence that research throughput matters

**Supporting evidence.**
- **FACT — Man Group (AlphaGPT, Man Numeric):**
  - It "has been observed to produce dozens of viable concepts within minutes rather than days."
  - Coding that "might take a human researcher hours or days" happens "in minutes."
  - "Several dozen" AI-generated signals passed the investment committee and were slated for live trading (Bloomberg, 10 July 2025, citing senior PM Ziang Fang).
  - Man has since published AlphaTrend (trend-following) and an "Alpha Assistant." This is sustained investment, not a one-off.
- **FACT — Balyasny:** About 95% of investment teams use its AI platform. "Deep research tasks that once required days are now completed in hours." A Central Bank Speech Analyst agent cut scenario analysis from about 2 days to about 30 minutes (OpenAI case study). Its head of applied AI said the aim was "to move from junior analysts to senior analysts" (Business Insider).
- **FACT — Bridgewater:** Launched a fund in July 2024 with almost $2bn from more than a half-dozen clients, run by co-CIO Greg Jensen (Bloomberg), where machine learning is "the primary decision-maker." It first tested the strategy on about a $100m sleeve of Pure Alpha, and it uses models from OpenAI, Anthropic and Perplexity alongside proprietary technology.
- **FACT — Industry adoption:** AIMA's "Charting the course" report (September 2025) says 95% of fund-manager respondents use GenAI (up from 86% in 2023). 58% expect to increase its use inside the investment process, versus 20% in 2023.

**Evidence that throughput is not the main economic driver.**
- **FACT — Ken Griffin (Citadel), 15 October 2025, JPMorgan Robin Hood Investors Conference (Bloomberg):** "With GenAI there are clearly ways it enhances productivity, but for uncovering alpha it just falls short." He said it has not replaced in-depth research at Citadel.
- **FACT — Man Group's own risk framing:** Speed "can create specific statistical risks… This is the multiple testing problem." Man is "expanding our monitoring infrastructure to handle increased signal volume." The bottleneck moves from generation to validation and oversight.
- **FACT — Price of crowdsourced alpha labor:** WorldQuant BRAIN says "Grandmaster level consultants can potentially earn upwards of $8,000 or more in a quarterly payment amount" and Master level "upwards of $2,000." BRAIN had more than 700 consultants and more than 21,000 users with access to more than 65,000 data fields by December 2022.
- **FACT — Numerai:** Reported cumulative payments to participants exceeding $43m, with $532,447 distributed in April 2025.
- **INFERENCE:** When a sophisticated quant firm opened the market for incremental alpha ideas, it priced the marginal contribution at thousands of dollars per quarter, not hundreds of thousands. Formulaic signal mining on standardized data is already cheap. An AI that produces more of it competes with a crowd that is paid little.
- **FACT — Signal decay:** McLean and Pontiff (Journal of Finance, 2016), studying 97 predictors, found portfolio returns "26% lower out-of-sample and 58% lower post-publication." BlackRock's Jeff Rosenberg calls quant equity "an arms race around new data, new techniques, alpha discovery, and then they quickly get arbed away."
- **INFERENCE:** More throughput raises the treadmill speed for everyone. The durable value sits in knowing which signals are decaying, which is Product C's decay tracking, and in not fooling yourself, which is Product B.
- **FACT — Current LLM quality:** Man says off-the-shelf LLMs handle "intern-level work." A practitioner newsletter (Quant Arb) says ChatGPT "will cause lookahead and then get excited and think this should go into production" and recommends "not let it backtest anything itself."
- **FACT — Academic evidence:** LLMs memorize historical financial outcomes, which inflates backtests. Gao, Jiang and Yan show a model assigning near-certain "up" probability to Kodak's July 2020 spike from the ticker and date alone.
- **ANECDOTE:** A newsletter tracking the space counts "over 100 startups" building AI-for-hedge-funds.

**Net read (INFERENCE):** Throughput matters economically only when three things hold: (i) the research universe is large and data-rich (cross-sectional equities, alt data); (ii) evaluation is rigorous enough that extra tests do not simply manufacture false discoveries; and (iii) the firm has capital capacity to deploy extra signals. Most mid-tier firms satisfy (i) partially, (ii) poorly, and (iii) variably.

## 4. Alternative bottlenecks

| Bottleneck | Evidence | Implication for an AI junior quant |
|---|---|---|
| **Proprietary data** | FACT: Neudata estimates alternative-data spend at $2.8bn in 2025 (+17%). Buyers average about 20 vendors and $1.6m/year (~$80k per dataset). Man names proprietary data as its sustainable edge. | Agents running on the same vendor data as competitors converge on the same signals. Value depends on the customer's data, which you don't control. |
| **Senior PM talent** | FACT: Nine-figure PM packages; "demand for top talent remains greater than the supply of quality PMs." | The scarcest input is alpha ownership and judgment, which the thesis explicitly leaves to humans. AI adds research supply to a constraint that is on the demand/decision side. |
| **Capital and capacity** | INFERENCE: Many strategies degrade as capital scales. Platforms allocate risk capital to PMs, not to signals. | Extra valid signals without extra risk budget have low marginal value, unless they diversify or replace decaying ones. |
| **Infrastructure/compute** | FACT: Jane Street committed about $6bn to CoreWeave's AI cloud plus a $1bn equity investment. | Top firms' binding spend is infrastructure. Your product becomes one more workload on their stack, not a separate budget. |
| **Execution** | FACT: Gunvor's quant hiring centers on execution algorithms and infrastructure. Industry commentary stresses latency and crowding. | For prop/HFT and physical desks, research is less binding than execution and market access. Product A is low-value there. |
| **Domain intuition** | FACT: Man says AlphaGPT works best in systematic equity, and extending it needs "customising data sources, research methodologies and analytical frameworks for each asset class." | Power/gas/physical commodity research is idiosyncratic (assets, grid, weather, contracts). A generic agent will underperform without heavy domain configuration, which pulls you toward consulting. |
| **Regulation/model risk** | FACT: The PRA's SS1/23 (effective 17 May 2024) applies model risk management principles explicitly to AI/ML at UK banks. The PRA held AI/ML roundtables with 21 firms in October 2025. | For bank desks, AI-generated models add validation burden. This raises demand for Product B (auditability) and lowers appetite for Product A (autonomy). |

**Conclusion (INFERENCE):** For elite firms, the binding constraints are PM talent, data and infrastructure. For HFT/prop, it is execution. For energy desks, it is domain data and fundamental modeling. Research-labor throughput is binding mainly for mid-tier systematic funds with more data than researchers. That is a real but narrower segment.

## 5. Current budget pools

| Pool | Scale evidence | Who owns it | Replace or expand? |
|---|---|---|---|
| Quant salaries | Junior QR TC ~$200–300k US; £144k London 1–3 yrs | CIO / Head of Research / PM (pod budgets) | **Hardest to capture.** Firms rarely cut headcount for software; they reallocate. Pitch as capacity, not replacement. |
| Alternative data | $2.8bn industry spend in 2025; ~$1.6m per buyer per year | Head of Data / data strategy team | **Expansion angle:** "evaluate datasets faster and more rigorously before renewal." This is a strong, measurable ROI hook. |
| Market-data terminals | Bloomberg $31,980/yr single seat, $28,320 multi-seat (2025 pricing) | COO / market data manager | Anchor for per-seat pricing psychology, not a pool you replace. |
| Research AI assistants | AlphaSense surpassed $600m ARR (2026); Hebbia ~$13m ARR (2024), ~$15k per licence; Rogo ~$3,300 per seat (Sacra estimate); LinqAlpha 70+ institutions | Head of Research / CTO / innovation | Shows willingness to pay for document-centric AI. Quant-specific research agents are much less proven. |
| Quant platforms / databases | KX ARR £73m (FY24) with "lengthened sales cycles"; QuantConnect Institution tier from $96/user/month; SigTech ~$8.7m revenue (third-party estimate) | CTO / Head of Quant Tech | **Warning signal:** backtesting/research platforms are a small, slow market. Low price points and long cycles. |
| Internal engineering | Balyasny Applied AI team of 20; Man, Bridgewater in-house | CTO | Primary competitor. For large firms, your price is benchmarked against a few internal engineers. |
| Cloud/LLM compute | Jane Street $7bn CoreWeave commitment | CTO / infra | Usage-based pass-through; low margin unless bundled. |
| Consulting / contractors | UNKNOWN public data for quant contractors | COO / Head of Research | Possible pilot budget: discretionary, and easier than a new software line. |
| Crowdsourced research | WorldQuant pays top contributors ~$8k+/quarter; Numerai >$43m cumulative | CIO | **Brutal price anchor** for marginal alpha ideas. |

**Plausible budget ownership (INFERENCE):**
- **Product A:** Head of Research/CIO, funded from research headcount or innovation budget.
- **Product B:** Head of Quant Research plus the model risk/CRO function (at banks and regulated utilities).
- **Product C:** Head of Research/CTO.
- **Product D:** CTO/COO.
- **Data-evaluation use case:** The Head of Data, whose budget is the most clearly quantified pool in the evidence.

## 6. Buyer/persona map

| Customer type | Economic buyer | User | Blocker | Procurement owner | Plausible problem statement | ROI logic |
|---|---|---|---|---|---|---|
| **Multi-manager hedge fund** | Central Head of Quant/Applied AI, or pod PM (own budget) | Pod QRs/analysts | In-house AI team (e.g., Balyasny-style) sees you as competition; compliance on data leaving the perimeter | CTO + vendor risk | "Our pods run inconsistent research processes; we can't compare evidence across teams." | Fewer false positives reaching risk capital; faster dataset evaluation. Weak for top 5 platforms, plausible for mid-size. |
| **Systematic fund (mid-tier, <$10bn)** | CIO / Head of Research | QRs | Senior quants who own "the process"; IP paranoia | COO/CTO | "We have more data and ideas than researchers; our backtests aren't reproducible when people leave." | Research capacity per QR; institutional memory retention after turnover. **Best-fit segment.** |
| **Prop trading firm** | Founders/partners | Quant traders | Culture of building everything; latency/execution focus | Partners directly | "Mid-frequency research is slow." | Weak: edge is execution and speed; research labor is less binding. Small firms have low budgets. |
| **Commodity trading house** | Head of Trading Analytics / desk head (e.g., new power desks) | Quant analysts, fundamental analysts | Traders who distrust black boxes; physical-market data messiness | IT + risk | "We're building quant capability fast and can't hire enough; our models aren't governed." | Accelerate capability build; governance for model sign-off. High comp pools (Vitol/Trafigura profit shares) mean budget exists, but decisions are desk-driven. |
| **Utility / energy merchant** | Head of Trading / Head of Quant Analytics | Quant analysts, risk | Market risk/model validation; IT security; procurement rigidity | Central procurement (long cycles) | "Forecasting/trading models proliferate without audit trails; regulators and auditors ask for lineage." | Governance and auditability (Product B) > throughput. Lower pay levels reduce the labor-substitution ROI. |
| **Bank trading desk** | Desk head + Head of Model Risk | Desk quants, strats | SS1/23-type model validation; vendor risk; IT | Central procurement | "AI/ML models must meet model risk standards; we need lineage and reproducibility." | Compliance-driven ROI for B/C; A is actively disfavored because autonomy raises validation burden. |
| **Systematic asset manager (long-only/quant equity)** | CIO / Head of Quant Equity | QRs | Investment committee conservatism | Procurement + compliance | "We need more uncorrelated signals and better research documentation for clients/consultants." | Closest to Man's AlphaGPT use case; auditable research is also a client-reporting asset. |

## 7. A/B/C/D product comparison

Scores are INFERENCE on a 1–5 scale (5 = best for you).

| Dimension | A — AI Quant Researcher | B — Referee / Control Plane | C — Research Knowledge System | D — AI Research Workforce Platform |
|---|---|---|---|---|
| Buyer urgency | 3 (interest high, proof low) | 3 (rising with AI signal volume; high at banks) | 2 (important, rarely urgent) | 1 (premature) |
| Willingness to pay | 2–4 (high if proven edge; near zero otherwise) | 3 | 2 | 2 |
| Differentiation | 1–2 (Man, Balyasny, Microsoft RD-Agent/Qlib, QuantConnect's "Mia," 100+ startups) | 4 (few focused players; hard to do well) | 3 | 2 (horizontal agent platforms will compete) |
| Integration burden | 5 = worst (needs data, compute, research libraries, permissions) | 4 (must hook into data and backtest stack) | 3 (can start as a ledger over existing outputs) | 5 = worst |
| Sales cycle | Long (IP, trust, performance proof takes quarters) | Medium-long | Medium | Long |
| Competition | Internal teams + open source + crowdsourcing | Internal tooling, model-risk vendors (ValidMind, Yields — bank-oriented) | Experiment trackers, notebooks, wikis | LLM vendors, agent platforms |
| Initial wedge | "Evaluate this new dataset for us in 2 weeks" | "Every AI- or human-generated signal passes the same sealed, logged tests" | "Never re-test what already failed; survive researcher turnover" | None standalone |
| Expansion potential | High if trusted | High: becomes gatekeeper for every signal, human or AI, and the natural place to plug in A | Medium-high: accumulates proprietary switching cost | High but only after B+C |

**Key reasoning:**
- **Product A fails the adversarial test as a first product.** Its value is unprovable within a sales cycle, because prospective live performance takes months to years. The firms that most need it build it. Its outputs compete with crowdsourced alpha priced at thousands of dollars per quarter. Man's own experience says the hard part is not generation but "monitoring infrastructure to handle increased signal volume."
- **Product B is what Man describes needing once AI is generating signals.** Man insists "every strategy entering live trading must pass identical thresholds." The LLM look-ahead literature makes leakage enforcement a technical necessity, not a nice-to-have. For banks and utilities, model-risk expectations (SS1/23) create a compliance budget. The risk is that B looks like "backtesting infrastructure," a category with low prices (QuantConnect) and slow growth (KX's lengthened sales cycles). It must be positioned as a governance and evidence product, not a backtester.
- **Product C carries the most switching cost but the least urgency.** It is best bundled into B as the evidence ledger.
- **Product D is a feature, not a company, at your stage.**

**Recommended sequencing (INFERENCE):** Lead with B+C, sold as a single "research integrity and memory" layer. Run a narrow, supervised version of A inside it as a demo of value, for example automated dataset triage for data teams. Earn the right to sell A as throughput later.

## 8. Pricing hypotheses (ESTIMATES, not observed market prices)

Anchors:
- Loaded junior QR cost: ~$250–400k/yr (INFERENCE).
- Bloomberg seat: ~$28–32k/yr.
- AI research assistant seats: ~$3k (Rogo) to ~$15k (Hebbia).
- Alt dataset: ~$80k/yr average.
- Crowdsourced alpha contributor: ~$8k+/quarter at the top tier.

| Model | Estimated range | Rationale |
|---|---|---|
| **Paid pilot (8–12 weeks)** | €40–150k | Comparable to a mid-priced alt dataset trial or a small consulting engagement. Must be tied to one concrete deliverable, such as a dataset evaluation or a research-process audit. |
| **Team subscription (B+C, one research team of 5–15 quants)** | €120–350k/yr | Roughly the cost of 0.5–1 junior QR. It is a defensible "cheaper than a hire" line item and above the price of document-AI seats because it touches the core research process. |
| **Per-agent (Product A/D)** | €25–100k per agent per year, plus compute pass-through | Must sit well below a loaded junior QR and above a Bloomberg seat. Above ~€100k, buyers will benchmark against a human hire and demand proof of P&L. |
| **Enterprise deployment (on-prem/VPC, multi-team, governance integrations)** | €400k–1.5m/yr | Comparable to the upper end of alt-data vendor relationships and to KX-style infrastructure contracts (KX added £14m ACV across 19 new logos in FY24, i.e., sub-£1m average new ACV including expansions). |
| **Usage-based** | Per validated experiment or per compute-hour with margin | Fits variable research loads, but creates unpredictable bills that procurement dislikes. Better as an overage than a primary model. |
| **Success-based** | Share of P&L from promoted signals, or bonus per signal passing the sealed holdout and surviving N months live | **Mostly unworkable** at hedge funds: attribution is disputed, P&L is confidential, and WorldQuant's payouts anchor the per-signal price low. Possible only as a small kicker. |

**INFERENCE:** A realistic early ACV is €100–300k. Reaching venture scale (e.g., €50–100m ARR) would need roughly 250–500 paying institutional customers, or fewer, larger enterprise contracts. That is a large share of the plausible mid-tier systematic plus energy-desk universe.

## 9. Venture-scale conditions

What would need to be true for this to be a venture-scale company rather than consulting or niche research software:

1. **Research governance becomes a mandated category.** Model-risk expectations (SS1/23 for UK banks; comparable US guidance) or investor/LP due diligence must start requiring auditable lineage for AI-generated signals. AIMA reports 60% of institutional investors would be more likely to invest in a fund with a meaningful GenAI budget. The question is whether allocators will also demand evidence of research integrity. **UNKNOWN.**
2. **Mid-tier firms cannot build what Man and Balyasny built.** A 20-person Applied AI team plus decades of research infrastructure is out of reach for most sub-$10bn funds, utilities and commodity desks. This is plausible but unproven.
3. **The product is data-agnostic and deploys inside the customer perimeter.** IP paranoia is universal. Anything that requires data to leave the firm will stall.
4. **Low per-customer configuration.** If every energy desk needs bespoke domain modeling, you are a consultancy. Man itself notes each new asset class needs custom data sources and frameworks.
5. **A measurable, fast ROI proxy exists.** Candidates include dataset evaluation time and cost, false-discovery rate caught by sealed holdouts, and research re-work avoided. Live P&L takes too long to prove.
6. **Expansion from B/C to A/D raises ACV 3–5x.** The referee must become the default place where agent research runs.
7. **Foundation-model vendors do not absorb the category.** Anthropic launched Claude for Financial Services with data connectors; OpenAI co-designs with Balyasny. If horizontal vendors ship "quant research agent + guardrails," the differentiation shrinks to the control plane and memory. That is another reason to lead there.

## 10. Strongest case for DO NOT BUILD

1. **The best customers are your competitors.** Man, Balyasny, Bridgewater, Citadel and Jane Street build in-house, and AIMA finds larger managers "are also more likely than their smaller peers to invest in building in-house generative AI tools."
2. **The residual market is price-sensitive and slow.** Quant research platforms show low list prices (QuantConnect Institution from $96/user/month), small revenue (SigTech ~$8.7m estimated) and "lengthened sales cycles" (KX).
3. **Marginal alpha ideas are cheap.** WorldQuant's crowdsourced consultants earn thousands per quarter. Numerai's entire payout history is about $43m. Idea volume is not a scarce good.
4. **Alpha is not the bottleneck at the top; PMs, data and capital are.** Griffin: GenAI "falls short" for alpha.
5. **Your core differentiator is replicable.** Man describes the same architecture you propose (idea generator, implementer, evaluator, orchestrator, logging, identical thresholds). Microsoft open-sourced RD-Agent on Qlib. Dozens of GitHub projects implement agent-plus-backtest loops.
6. **Trust barrier plus founder profile.** Selling research methodology to senior quants requires a credible quant. As a solo non-quant founder, you face a credibility tax in exactly the room that decides.
7. **Proof takes too long.** An "auditable prospective track record" needs months to years of live evidence per customer. That is longer than a seed runway.

**Counter-case (why not to abandon):** None of these kills Products B/C for mid-tier and energy buyers. They kill the idea of leading with an autonomous researcher.

## 11. Exact remaining unknowns requiring interviews

1. How many hypotheses does a typical QR test per month, and what share is killed for methodological reasons (leakage, overfitting) versus economic ones?
2. Who owns research methodology sign-off today, and does a written, enforced standard exist?
3. What happens to research knowledge when a QR leaves? Is there any quantified cost (re-work, lost signals)?
4. How are new datasets evaluated, how long does it take, and what does a failed evaluation cost?
5. What is the realistic vacancy duration for a QR, and would a hiring freeze or budget cap make software the only option?
6. Would data and code be allowed to run in a vendor-deployed environment inside the VPC? What security review is required?
7. At energy desks: is quant research cross-sectional (agent-friendly) or asset/fundamental-specific (bespoke)?
8. At banks and utilities: do model risk teams already require lineage for trading/forecasting models, and is it painful?
9. What did they try already (internal LLM agents, open source, vendors), and why did it stop?
10. Which budget would fund this, and what is the largest unapproved discretionary spend the buyer controls?

## Implications for the AI Quant Researcher Thesis

### 1. What the evidence supports

- Research bandwidth is a real bottleneck at data-rich systematic firms. Man Group says so explicitly and has moved AI-generated signals through its investment committee.
- Agentic research workflows produce production-grade signals under strict human-in-the-loop governance: Man's AlphaGPT, Balyasny's agent platform, Bridgewater's AIA fund.
- The separation of generator from evaluator is the correct architecture. Man uses the same structure and names multiple testing and hallucination drift as the central risks.
- LLM-specific leakage (memorized outcomes) is a documented, academically studied failure mode. That makes an independent, point-in-time-enforcing referee a technical necessity for AI-generated research.
- Labor is expensive: junior QRs cost roughly $200–300k in US total compensation and up to £144k in London. Adoption intent is broad: AIMA's September 2025 "Charting the course" survey reports 95% GenAI usage among fund managers.

### 2. What the evidence weakens

- The idea that sophisticated firms will buy an external AI junior quant. They are building their own and see the technology as commoditizing.
- The idea that more research conclusions translate directly into economic value. PM talent, proprietary data, capital capacity and execution appear more binding. Signal decay erodes marginal discoveries. Crowdsourced alpha labor is priced very cheaply.
- The idea that the labor-substitution pitch works. Firms with $10m+ revenue per head don't optimize junior salaries, and lower-paying segments (utilities) have less labor ROI to capture.
- The idea that quant research software is a fast-growing, high-ACV market. The public comparables (KX, QuantConnect, SigTech) show modest prices and slow cycles. The high-ARR AI winners (AlphaSense, Hebbia, Rogo) are document/fundamental research tools, not quant research agents.

### 3. What remains unknown and cannot be resolved through desk research

- Actual false-discovery and re-work rates inside private firms, and their cost.
- Whether mid-tier systematic funds and energy desks would allow an external agent to run on proprietary data, and under what deployment model.
- Whether allocators or regulators will require auditable research lineage for AI-generated signals, turning Product B into a mandated purchase.
- Realistic QR vacancy durations and whether hiring constraints are binding in 2026.
- Paris/Geneva-specific compensation and team structures (no reliable public data found).
- Whether any buyer would accept a non-quant founder as the vendor of research methodology, or whether a quant co-founder is a precondition.

### 4. The 5 most important questions to ask practitioners

1. "Walk me through the last three research ideas your team killed. Why did each die, how long did it take, and how many were killed for methodological rather than economic reasons?"
2. "If you had twice as many validated signals tomorrow, would you have the risk capital and capacity to trade them? What would actually limit P&L?"
3. "When a researcher leaves, what research knowledge do you lose, and have you ever re-tested something a departed colleague had already disproved?"
4. "Have you built or tried an internal LLM research agent? What broke, and who owns fixing it?"
5. "If a vendor enforced point-in-time data, sealed holdouts and multiple-testing controls on every signal, human or AI, inside your environment, whose budget pays for it, and what would it have to prove in 90 days?"

### 5. Verdict: **WEAKENS**

The evidence weakens the thesis as framed: an AI-native junior quant researcher sold first to professional trading firms. Research labor is expensive, but it is not the dominant bottleneck for elite firms, and those firms build the capability in-house. The marginal value of extra hypotheses is low and falling, and the category's software comparables are small and slow. This is not a DO NOT BUILD, because a narrower, more defensible opportunity survives: an independent research referee plus evidence ledger (B+C) for mid-tier systematic funds, energy/commodity desks and model-risk-constrained bank desks, with supervised agentic research (A) as expansion. Proceed only if interviews show (i) paid demand for B+C from at least 5–10 mid-tier buyers with named budgets, and (ii) willingness to deploy inside their environment. Otherwise, the most likely outcome is a consulting business or a niche tool.