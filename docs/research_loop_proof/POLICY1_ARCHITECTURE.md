# policy1: a minimal structured research-policy layer

*Owner instruction: [`NEXT_POLICY_ARCHITECTURE_PROMPT.md`](NEXT_POLICY_ARCHITECTURE_PROMPT.md). This is the one
architecture note. The frozen run specification is [`POLICY1_SPEC.md`](POLICY1_SPEC.md).*

**Hypothesis.** beta1 failed on evidence validity: it kept pre-change rejections as if they were current. learn1
failed on attribution and budget: it found a positive group, could not decompose it with the budget left, and selected
a member it could not distinguish. Both are failures to keep track of three things:
- whether each piece of evidence still holds;
- what is still unresolved for the final decision;
- what the remaining experiments can still resolve.

policy1 makes the researcher write these down every call, as a small structured state, and reads that state back to it
the next call.

## The state (condition S; every field is filled by the researcher)

| Field | What it holds | Why it exists, and the failure it addresses |
|---|---|---|
| `regime_assessment` {status: stable / possible_change / changed / unknown, cites, justification} | whether the process looks to have changed, and on what evidence | beta1 saw an incumbent decay but never stated that the regime had changed, so it never asked what else that invalidated |
| `decision_uncertainties` (at most 3: id, uncertainty, why_it_matters; in the final call, what remains unresolved) | what blocks a defensible final selection | learn1 ended with an unresolved attribution it never treated as decision-critical until the budget was gone |
| `budget_needs` (one sentence) | what must still be resolved, given the experiments remaining | learn1 spent its last experiment on a split that could not finish the decomposition |
| per candidate: `freshness` (current / possibly_stale / stale / unknown), `evidence_type` (none / direct / grouped / conditional), `last_scored_day`, `attribution` | when and how each status was established, and what is unresolved about the candidate's own contribution | beta1: "rejected" carried no date or regime. learn1: "promising" made no distinction between evidence about a member and evidence about its group |
| per experiment: `targets_uncertainty`, `possible_followup`, `budget_rationale` | which uncertainty it addresses, what it may leave to do next, and why it is worth a budget slot now | both runs chose experiments without stating the follow-up they might require |

**The existing fields stay:** notes, beliefs (status, cites, reason), experiments, final selection and conclusion.

**The S notebook:** it shows the researcher its own earlier state, verbatim, with every result.

**The loop:** evidence → state update → decision-critical uncertainty → experiments within the budget → results →
repeat → final selection with the remaining uncertainty stated.

**Division of labour:** the model does the state, the uncertainty, the choice and the final selection. The software
only:
- validates the fields (types, enums, lengths; an experiment must name one of the listed uncertainties);
- enforces the budget;
- runs the experiments;
- records everything;
- keeps the truth out.

## What is deliberately not encoded

There is no code or text that:
- re-tests rejected candidates after a change;
- reserves an experiment;
- splits a positive group;
- forbids selecting a candidate without a single-variable test;
- imposes quotas or sequences;
- infers any field from the data or the truth.

The model decides whether evidence is stale, which uncertainty matters, whether a re-test or a grouped experiment is
worth the budget, and what to select. The fields ask for short summaries and decisions, never for a chain of thought.

## The comparison

**L** is learn1's learned condition, unchanged: beta1's brief, the frozen beta1-derived lesson, and beta1's schema and
notebook.

**S** is the same brief and the same lesson, with only these differences:
- the research-state section added to the brief;
- the extended schema;
- the extended notebook rendering;
- the checks for the new fields.

Everything else is identical: model, effort, budget, menu, rounds, token cap, repair turn, world and evaluation.
