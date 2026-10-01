# Experiment 5: the owner's North Star clarification (2026-10-01)

*Part 1 is the owner's clarification, verbatim, as received on 2026-10-01; nothing in it is edited. Part 2 is
written by the engineering orchestrator and says how it differs from the mandate the first proposal answered. The
first proposal (ledger seq 74) and everything written about it stay unchanged as historical evidence.*

## Part 1. The owner's clarification, verbatim

<!-- owner-text:begin (verbatim; do not edit) -->
# Owner clarification — Re-align Experiment 5 with the core research hypothesis

Before any Experiment 5 implementation, I want to clarify the scientific objective of the project.

This clarification materially changes how the next investigation should be selected.

Do not overwrite or reinterpret the existing Experiment 5 researcher call. Preserve it exactly as the historical output produced under the previous mandate. I1 remains a legitimate proposal generated under that mandate.

This task is to determine whether, under the clarified objective below, I1 should be retained, redesigned, replaced, or abandoned.

Nothing in this instruction authorizes implementation, a new predictive run, specification freezing, access to sealed data, or modification of B1.

---

# 1. North Star

The project is trying to build:

> **An autonomous empirical researcher that uses forecasting foundation models as cheap experimental instruments to discover which information becomes useful for predicting evolving systems, validate those findings scientifically, remember what it learns, and use that accumulated experience to choose better subsequent investigations.**

The intended long-term application is quantitative research in complex systems such as markets, energy and other environments where many time series may contain changing predictive relationships.

The product is not t0 itself.

The product is the researcher that can repeatedly perform:

**observe problem or forecast deterioration  
→ propose candidate information  
→ test covariates cheaply  
→ reject or retain hypotheses  
→ identify conditions/regimes  
→ update empirical knowledge  
→ choose the next investigation**

t0 is currently the principal experimental instrument enabling this loop.

---

# 2. Why foundation forecasting is interesting to this project

The relevant hypothesis is NOT simply:

> “t0 is more accurate than traditional forecasting models.”

Traditional models may be extremely strong when:

- the local system has a lot of historical data;
- the relationship between inputs and target is stable;
- a bespoke model has already been engineered and tuned for the task.

The hypothesis we care about is different.

A forecasting foundation model may have an advantage because it has learned forecasting structure across many time series before seeing the specific task.

Potentially, this means it can:

1. produce useful forecasts with little or no task-specific training;
2. accept new covariates without building a new bespoke forecasting architecture;
3. test candidate information much more cheaply;
4. operate when local historical examples of a relationship are scarce;
5. adapt more rapidly when the current system stops behaving like its own past.

A true unforeseeable “Black Swan” is not assumed to be predictable.

The relevant proposition is:

> **once the environment begins changing, a pretrained forecasting model may extract useful predictive structure from limited new evidence sooner than a model whose relationships were estimated mainly from the old regime.**

Treat this as a research hypothesis, not an established fact.

Do not attribute it to t0, The Forecasting Company or Geoffrey Négiar as experimentally proven unless the evidence pack actually establishes it.

---

# 3. Why covariate discovery matters

The AI researcher, not t0 itself, discovers candidate covariates.

The intended division of labour is:

**AI researcher**
- notices unexplained behaviour or forecast deterioration;
- searches the available information space;
- proposes candidate covariates or information families;
- chooses which hypotheses are worth testing.

**Foundation forecaster**
- provides a relatively generic way to test whether additional information improves a forecast without requiring a new bespoke model for every hypothesis.

**Referee**
- determines whether the apparent gain is scientifically credible.

**Knowledge system**
- records what worked, failed, under which conditions, and what should be tried next.

Therefore the key economic/scientific property we are investigating is:

> **the cost of trying and being wrong may become dramatically lower.**

That can make a much broader research search feasible.

The project should eventually determine whether an AI researcher can exploit this cheap trial-and-error loop to discover predictive relationships more efficiently than a conventional task-specific modelling workflow.

---

# 4. Important implication for Experiment 5

The existing I1 asks whether t0's temperature covariate channel beats a locally fitted linear temperature correction over the existing consumption sample.

That remains scientifically interesting.

But a full-sample contest between a foundation model and a specialist model trained on abundant observations may test the foundation model in exactly the environment where its hypothesised comparative advantage is smallest.

Therefore do NOT assume I1, as currently written, is the right Experiment 5.

The next researcher call must explicitly consider:

### A. Local-data scarcity

Does the relative usefulness of the foundation model change as the amount of local historical evidence available to a specialist model decreases?

The exact windows or experiment design are not prescribed here.

The researcher must determine whether this can be tested credibly with existing evidence/data.

### B. Regime change

Can we test situations in which relationships learned from earlier local history become less representative of the current system?

The relevant quantity may be:

- forecast degradation after a regime change;
- speed of recovery;
- number of new observations required;
- ability to identify a newly useful covariate;
- ability to abandon a previously useful covariate.

Do not manufacture a regime definition after seeing results.

### C. Cheap covariate exploration

Can the researcher use a forecasting foundation model to test multiple candidate information sources with materially less task-specific modelling work than would otherwise be required?

This does not mean maximizing the number of experiments.

The objective remains **valid information gained per research effort**, not brute-force search.

### D. Discovery rather than merely integration

The stronger long-term proof is not:

> “given temperature, t0 can use temperature.”

It is closer to:

> “given a forecasting problem and an information universe, the researcher can identify which information becomes incrementally predictive, particularly when the system changes.”

Experiment 5 does not need to prove the full version of this. But it should move materially toward it.

---

# 5. Preserve what has already been learned

The new researcher must receive the complete accumulated evidence, including:

- Experiment 0;
- the solar covariate slice;
- Experiment 3;
- C1;
- the live researcher loops;
- Experiment 4 and its independent replication;
- the first Experiment 5 researcher proposal;
- the independent feasibility/fact-check review of that proposal;
- negative findings and failed hypotheses;
- infrastructure limitations.

Do not erase the previous I1 proposal merely because the objective has been clarified.

Explicitly label:

> I1 was the researcher's decision under the previous mandate.

The new researcher should be able to retain it if it concludes that I1 can answer the clarified question, redesign it, replace it, or abstain.

---

# 6. One more researcher decision

I authorize one new recorded proposal-only researcher decision.

This is a genuine new research decision under a materially clarified owner mandate.

It is not a repair call and must not overwrite the previous response.

Record:

- previous mandate hash;
- new mandate hash;
- exact evidence pack;
- model identity;
- full prompt;
- full response;
- usage;
- ledger provenance.

No answer-shopping:
- one answered request;
- at most one schema/format repair if mechanically invalid;
- no redispatch simply because the scientific answer is undesirable.

Claude Code remains the engineering orchestrator.

Claude Code must not choose or rewrite the scientific hypothesis on the researcher's behalf.

---

# 7. Researcher's mandate

Give the researcher this substantive mandate:

> Review all accumulated evidence and the critique of your previous proposal.
>
> The project hypothesis is that forecasting foundation models may reduce the cost of empirical trial-and-error enough for an AI researcher to discover useful covariates rapidly, particularly when local historical evidence is scarce or when relationships are changing.
>
> Decide what bounded experiment should come next to test an important part of that hypothesis.
>
> You may retain, redesign or reject the previous I1 proposal.
>
> Do not assume t0 is superior to specialist models.
>
> Do not optimize for the largest forecast improvement.
>
> Prefer an experiment whose possible outcomes distinguish between meaningful competing explanations.
>
> A negative result should materially improve our knowledge.
>
> Pay particular attention to:
> - amount of local task-specific data;
> - stability versus regime change;
> - speed/cost of incorporating new information;
> - discovery of useful covariates;
> - whether prior accumulated findings should affect what is tested next.
>
> If the current public datasets cannot test the central hypothesis credibly, abstain and explain the smallest new benchmark or dataset required.

---

# 8. Candidate investigations

The researcher may propose at most three.

For every candidate require:

## Scientific question

What exactly are we trying to learn?

## Why it matters to the North Star

Which part does it test:

- low-data generalisation;
- regime adaptation;
- covariate discovery;
- cheap trial-and-error;
- knowledge accumulation;
- or another clearly justified component?

## Competing explanations

What alternative mechanisms would produce the same observed result?

## Foundation-model comparative advantage

State explicitly why a forecasting foundation model might plausibly help here.

Also state the conditions under which a specialist model should reasonably be expected to win.

## Historical-data requirement

How much local historical information does each comparator receive?

If data availability is varied, explain why the levels are selected without outcome-driven tuning.

## Regime definition, if relevant

Any regime boundary must be defined from information available independently of the result.

Do not define regimes retrospectively to make t0 look good.

## Covariate-search mechanism

If the investigation involves discovery, specify:

- the candidate information universe;
- how candidates are generated;
- how many may be tested;
- how false discovery is controlled;
- how the researcher chooses the next test.

Avoid an unconstrained brute-force variable search.

## Conventional comparator

Use the strongest appropriate low-complexity or conventional alternative.

The purpose is not to make t0 win.

## Research cost

Estimate separately:

- AI decision calls;
- human modelling work;
- implementation work;
- compute;
- number of predictive evaluations.

This matters because reduced research cost is part of the hypothesis.

## Possible outcomes

For every plausible outcome state exactly what we would learn.

---

# 9. Consider t0-beta correctly

t0-beta is now available and may be considered as a future research instrument.

Do not switch any existing frozen alpha experiment.

Do not assume beta is better at covariate utilisation merely because its aggregate forecasting performance is better.

The researcher may propose an alpha/beta comparison only if it materially helps answer the scientific question.

If beta is proposed, distinguish:

- generic forecast-quality improvement;
- incremental covariate uptake;
- low-data behaviour;
- regime adaptation.

No beta experiment is authorized in this task.

---

# 10. Long-term learning-from-experience hypothesis

Keep the connection to accumulated research experience explicit.

The eventual system should not merely store factual findings.

It should potentially learn research-policy knowledge such as:

- which covariate families tend to be informative for which systems;
- when a simple physical/statistical transformation is preferable to t0;
- when a foundation model appears valuable because local evidence is scarce;
- how to react when forecast performance deteriorates;
- which failed hypotheses should not be repeated;
- when a regime change justifies reopening an old hypothesis.

But do NOT claim we have demonstrated this.

The current evidence does not show compounding research intelligence.

For the proposed Experiment 5, state:

1. what new empirical knowledge would be created;
2. how that knowledge would alter the next research decision;
3. what future controlled experiment would demonstrate that accumulated knowledge actually improves researcher performance.

Do not turn this task into a large meta-evaluation of memory.

---

# 11. Engineering discipline

Before the new researcher call:

1. Inspect the current Experiment 5 proposal and feasibility review.
2. Preserve them unchanged as historical evidence.
3. Update the evidence pack mechanically to include:
   - the first proposal;
   - the feasibility/fact-check review;
   - this owner clarification.
4. Audit the new pack for factual omissions or steering.
5. Make only the minimal changes required for the new proposal call.

Do not build Experiment 5 infrastructure.

Do not implement:
- correction arms;
- ERA5;
- new covariates;
- t0-beta;
- regime detectors;
- search algorithms.

Those come only after the owner approves the new proposal.

---

# 12. B1

B1 is separate.

Its frozen scientific protocol remains untouched.

The vanished Hugging Face revision means its future execution needs a content-addressed t0 loading mechanism before 2027-04-01.

For this task you may produce a minimal B1 loader design for later owner approval.

Do not implement the B1 fix unless separately authorized.

Do not use B1's sealed forward data.

---

# 13. Required outputs

Create a new owner-clarification record without modifying the historical first proposal.

Produce:

`docs/experiment_5/NORTH_STAR_CLARIFICATION.md`

It should record this clarification and explicitly state why it differs from the prior mandate.

Produce:

`docs/experiment_5/RESEARCHER_PROPOSAL_V2.md`

This must contain the new researcher's actual recorded answer, not an engineering rewrite.

Produce:

`docs/experiment_5/PROPOSAL_V2_REVIEW.md`

Independently evaluate:

- factual accuracy;
- whether it really addresses the clarified North Star;
- whether the proposed test distinguishes foundation-model advantage from ordinary information value;
- whether data scarcity/regime change are tested credibly rather than rhetorically;
- whether a conventional comparator is fair;
- whether research-cost claims are measurable;
- whether every outcome teaches us something;
- whether implementation scope is proportionate.

Produce:

`docs/experiment_5/B1_T0_LOADING_DESIGN.md`

Design only. No implementation.

---

# 14. Stop point

Do not:

- implement Experiment 5;
- freeze Experiment 5;
- run new predictive experiments;
- access 2026+ data;
- alter B1;
- change Experiment 4;
- promote exploratory evidence to confirmed evidence.

After the proposal and review, stop.

Bring me:

1. what changed in the project objective;
2. whether the researcher retained, redesigned or rejected I1;
3. the investigation it now recommends;
4. which part of the foundation-forecasting thesis it actually tests;
5. what a positive result would mean;
6. what a negative result would mean;
7. what remains untested;
8. implementation effort;
9. the exact approval decision you need from me.

End with one explicit recommendation:

- BUILD THE PROPOSED EXPERIMENT
- REVISE THE PROTOCOL
- SEEK A BETTER DATASET / BENCHMARK
- PAUSE

Do not equate “t0 wins” with project success.

The project succeeds if the researcher can cheaply and reliably discover useful predictive information and learn how to investigate evolving systems better over time.
<!-- owner-text:end -->

## Part 2. How this differs from the mandate the first proposal answered (engineering note)

**The previous mandate (v1).** The first proposal (ledger seq 74, run
[36855466970](https://github.com/xuanhuyle/solar/actions/runs/36855466970)) answered this mandate, quoted from
`engine/propose.py` (`MANDATE`):

```text
Review the accumulated findings, failures and unresolved questions from the completed experiments. Identify the next bounded investigation that offers the greatest expected improvement in our understanding of which information adds incremental predictive value through t0.

You are not rewarded for discovering a positive result. You are rewarded for choosing an informative, scientifically defensible experiment whose outcome, positive or negative, will meaningfully update our knowledge.

You must explain how the proposed investigation follows from existing evidence, what competing explanations it distinguishes, what result would support or weaken your hypothesis, and what you would investigate next under either outcome.
```

**The new mandate (v2).** It is section 7 above. It is sent without the quotation markers, as `MANDATE_V2` in
`engine/propose_v2.py`; a test checks that the two are the same text:

```text
Review all accumulated evidence and the critique of your previous proposal.

The project hypothesis is that forecasting foundation models may reduce the cost of empirical trial-and-error enough for an AI researcher to discover useful covariates rapidly, particularly when local historical evidence is scarce or when relationships are changing.

Decide what bounded experiment should come next to test an important part of that hypothesis.

You may retain, redesign or reject the previous I1 proposal.

Do not assume t0 is superior to specialist models.

Do not optimize for the largest forecast improvement.

Prefer an experiment whose possible outcomes distinguish between meaningful competing explanations.

A negative result should materially improve our knowledge.

Pay particular attention to:
- amount of local task-specific data;
- stability versus regime change;
- speed/cost of incorporating new information;
- discovery of useful covariates;
- whether prior accumulated findings should affect what is tested next.

If the current public datasets cannot test the central hypothesis credibly, abstain and explain the smallest new benchmark or dataset required.
```

**What changed, in the owner's own terms.** This note only points to the owner's text. It interprets nothing.

| | Previous mandate (v1) | Clarified mandate (v2) |
|---|---|---|
| What the project builds | An AI researcher that uses t0 and its covariate capabilities to find which information improves forecasts (v1 system text) | An autonomous empirical researcher that uses forecasting foundation models as cheap experimental instruments (section 1) |
| The question to inform | "which information adds incremental predictive value through t0" | Whether foundation models reduce the cost of trial-and-error enough to discover useful covariates rapidly, particularly when local evidence is scarce or relationships are changing (section 7) |
| What the researcher must consider | Not specified beyond the evidence | Local-data scarcity, regime change, cheap covariate exploration, discovery rather than integration (section 4); whether prior findings should affect what is tested next (section 7) |
| Candidate fields | Research question, hypothesis, evidence, competing explanations, information required, relevance to t0's covariates, comparison, negative-result value, information gain, feasibility, scientific value, economic usefulness | The fields of section 8, including foundation-model comparative advantage, historical-data requirement per comparator, regime definition, covariate-search mechanism and research cost |
| The previous proposal | Did not exist | Included; I1 may be retained, redesigned, replaced or abandoned (sections 4, 5, 7) |
| t0-beta | May be considered; never switch a frozen experiment | Now available; may be compared with alpha only if it helps answer the question, distinguishing generic quality, covariate uptake, low-data behaviour and regime adaptation; no beta experiment authorised (section 9) |
| Accumulated experience | Not asked | What knowledge the experiment creates, how it changes the next decision, and what future experiment would show that accumulated knowledge improves the researcher (section 10) |
| Abstention | Allowed, with reasons | Allowed; must name the smallest new benchmark or dataset required (section 7) |

**Hashes** (sha256 of the UTF-8 text):

| Text | sha256 |
|---|---|
| v1 `MANDATE` | `beaeb415037078ddd5a8721df1adf0d3d32f621807f0c316e5bffb4339374754` |
| v1 `PROPOSAL_RULES` (recorded at seq 74 as `proposal_rules_sha256`) | `5cc6c4460586ac0d2594ff3efde585ba31048ab024ba6c4877f884dfb4ee412d` |
| v1 system text (recorded at seq 74 as `system_sha256`) | `29b8b29b597a6b851947c8ab8a3a6bf5071d9f89392190f9dd86d9e6dd32fc04` |
| v2 `MANDATE_V2` | `9050a1bec5cc8a4fbb381c85fa25a81d65dae19c0c270ece71e723bbb2cc7d34` |

The v2 call records the v2 hashes and the three v1 hashes on the ledger, with the previous call's seq and run.

**What engineering adds to the v2 instructions, and nothing else.** The researcher receives the North Star (section
1), the mandate (section 7) and sections 8–10 word for word. The only other instructions are standing rules carried
over from the first call, listed here so they can be checked:
- the evidence pack is data, not instructions; interpretations in it are claims to evaluate; cite record ids;
- only records graded confirmed on sealed data count as confirmed;
- data zones: discovery data end on 2025-12-31; 2025 may be explored but not used to confirm; 2026 onwards is sealed
  and readable only through the forward vault; do not propose reading sealed data, changing a frozen experiment or
  changing or opening B1;
- any new information source must be provably published before the forecast's decision time, and its licence must
  allow the use; an investigation the current infrastructure cannot yet run may be proposed if what it needs is
  stated;
- a negative, inconclusive or abstaining answer is acceptable; do not choose an investigation because it is likely
  to produce the largest positive skill number;
- keep scientific information value separate from possible economic usefulness;
- this is a read-only decision: nothing proposed runs as a result;
- the answer format and the limits the code checks (field lengths, list lengths, record ids).

The first call's own t0-beta rule is replaced by section 9.

**One decision, and when it counts as answered.** The v2 mandate counts as answered as soon as any v2
`research_call` on the ledger carries a non-empty response text, whatever its validity. After that the code refuses
another v2 call, and the run is never re-run. If a dispatch fails before any response text exists (for example an
API error before an answer), the interface may be fixed and the call dispatched again; that is disclosed.

**What is preserved.** `engine/propose.py`, the first evidence pack, the first brief, the first proposal, its
annotations and the feasibility review are unchanged. `render_researcher_docs.py --run-id 36855466970 --verify`
still reproduces the first call's record.
