# Human1: the lesson-only researcher on human-supplied two-candidate hypotheses (frozen specification)

*Owner instruction: [`NEXT_HUMAN_HYPOTHESIS_MILESTONE_PROMPT.md`](NEXT_HUMAN_HYPOTHESIS_MILESTONE_PROMPT.md). This
document is frozen before the preflight and the scored run. The frozen files are listed in
`research_loop_proof/human1/truth/spec.py`, which includes everything discovery1's hash covers. Their combined hash is
`human1_spec_sha`; the three scored worlds' seeds are derived from it, and the scored run refuses unless the preflight
passed under the same hash. Phase 0, beta1, learn1, policy1 and discovery1 are unchanged; Human1 reuses their code by
import.*

## 1. The frozen question

The assumption under test:

> If a human supplies a small, genuinely relevant hypothesis set, the existing researcher can turn it into a
> scientifically supported conclusion under a tight experimental budget, rather than merely choosing a good forecast set
> or relying on an obvious deterministic test script.

It has two separate parts, kept apart throughout:
- **A. Competence:** does the researcher reach a correct, evidence-supported conclusion from the supplied hypothesis?
- **B. Residual agentic value:** does adaptive planning add anything beyond a fixed protocol, once the hypothesis has
  been supplied?

**Scope:**
- The question is about predictive information, not causation.
- Hypothesis generation is not tested. That E is in every packet is a benchmark condition (a good hypothesis supplied
  by an external human), not a discovery claim. The packet is a frozen evaluator construction, not engineering
  steering of the researcher.

## 2. The worlds and the human-supplied packet (`truth/world.py`)

**The world** is the frozen Phase 0 world with beta1's "phase_b" parameters, as beta1, learn1 and policy1 used:
- 154 days; the change on day 86 + U{0..6}; the same target and effect calibration;
- the roles: R (useful before the change, then retires), E (useful from the change on), D = 0.8·E + 0.6·independent (a
  correlated proxy of E, with no incremental value once E is known) and N (pure noise), each with a random sign.

**The packet.** The evaluator supplies two roles per world, by a predeclared pair type:

| world | pair |
|---|---|
| w1 | E + D |
| w2 | E + N (pure noise) |
| w3 | E + R |

- A seeded order, from a new child stream of the seed, maps the two roles to X01 and X02.
- The research job receives only the target and those two series for days 1–126. Days 127–154, the other candidates,
  the roles and the pair type never leave the truth side.
- The non-scored preflight world uses the E + D pair type.

**Seeds:**
- scored world w*k*: `int(sha256('human1:<human1_spec_sha>:<run id>:w<k>')[:16], 16)`;
- preflight: `human1-preflight:<run id>`.

## 3. The researcher L2: learn1's lesson-only L, adapted mechanically

**Unchanged from learn1's L**, the strongest researcher of Discovery1:
- beta1's brief, including the owner's set-evidence rule and the notes line;
- the frozen beta1-derived lesson (`learn1/lab/lesson.json`, sha256 `1c38b101…`), in its labelled section;
- Phase 0's prompts and notebook rendering; one repair turn per call; the pinned model and effort; the 80k token cap;
- the instrument: beta1's pinned t0-beta, 7-day context, the same result fields and windows of 7, 14 or 28 days.

**The adaptation**, which is only what presenting the pair, two rounds and four experiments requires:
- four brief lines are changed, each exactly once:
  - the candidate sentence names "two candidate covariate series, X01 and X02";
  - the rounds line becomes "Round 1: days 1-112 have been observed. Round 2: days 1-126. Then a final call with no
    experiments.";
  - the budget line becomes "4 experiments in total, at most 2 per round";
  - the beliefs line says "(X01-X02)";
- one line is inserted after the candidate sentence: the owner's packet text, verbatim. "A human analyst has supplied
  two anonymous candidate variables as a hypothesis worth testing after forecast behaviour changed. You are not being
  asked to search outside this pair. Determine what the evidence supports about each candidate's current predictive
  usefulness, including whether one adds value given the other. Use the experiment budget as you judge appropriate.
  Your final conclusion must distinguish supported evidence from uncertainty.";
- the schema's id enums are X01 and X02;
- the call plan, budget, user prompt and checks use the two rounds (cutoffs 112 and 126), the 4-experiment budget
  (at most 2 per round) and the two ids, which makes 3 calls in all.

**What L2 is not told:** either candidate's role, that either is guaranteed to be useful, or any advice about which
tests to run. The "1 to 4" covariate and "0 to 2" reference limits stay as they were; they remain true upper bounds.

**Tests check** that the system text maps back to learn1's L text exactly once the five edits are reversed, and that
every adapted function is Phase 0's with the substitution only.

## 4. Timing and budget

- **Round 1:** days 1–112 observed (the earlier, mixed or recent cutoff).
- **Round 2:** days 1–126 observed (the fresher, wholly post-change cutoff).
- **Then:** a final call.
- **Budget:** 4 experiments per world, at most 2 per round; unused budget is allowed.
- **Confirmation:** days 127–154, hidden, as in Discovery1.

## 5. The fixed comparator (`lab/comparator.py`; frozen before any world, not optimised)

The owner's sequence: the same lab and instrument, the same cutoffs, and 4 experiments (2 per round). Every window is
the last 28 revealed days, as in Discovery1's comparator, so it uses no knowledge of when the change happened.

| # | Round | Test |
|---|---|---|
| C1 | 1 (day 112) | X01 against no covariate |
| C2 | 1 (day 112) | X02 against no covariate |
| C3 | 2 (day 126) | X01 given X02 |
| C4 | 2 (day 126) | X02 given X01 |

**Decision for each candidate X with partner Y,** from the 95% lower bounds:
1. accepted if X given Y is above 0;
2. otherwise redundant if Y given X is above 0;
3. otherwise promising if X alone is above 0;
4. otherwise rejected.

The selection is the accepted candidates.

**Disclosed before the run:**
- C3 and C4 are exactly the contrasts the informativeness check runs (section 6). So in an informative E + D world the
  script resolves the pair by construction; that is the competence floor the owner asked for.
- In the E + N and E + R worlds the script succeeds exactly when E given its partner is detectable over days 99–126.
- C1 and C2 score days 85–112, which always contain pre-change days. Under the rules below they never support a claim.
- The rules below always find the script's claims supported, whatever its results (tested).

## 6. Evaluation

**Integrity, per world:**
- the observed-data hash;
- L2's system text equal to the frozen text;
- every prompt rebuilt byte for byte from that world's record;
- every L2 experiment recomputed from that world's data;
- the comparator recomputed (experiments, results, statuses, selection);
- all three canaries; the model hash; the guard; the job results.

**Informative world.** Direct t0-beta on the observed data, computed from the world and the instrument alone, before any
record is read. E must be detectable: E alone has a lower bound above 0 on days 99–112 or days 99–126. The supplied
contrast must also be present:
- **E + D:** E given D above 0, and D given E at or below 0, over days 99–126. The pair is then distinguishable;
  without this, symmetric evidence would make any verdict arbitrary.
- **E + N:** N alone, and N given E, at or below 0 on days 99–112 and on days 99–126.
- **E + R:** R alone, and R given E, at or below 0 on days 99–112 and on days 99–126.

D alone, R alone on days 57–84 and 85–112, and E given N or R are reported, not required. An uninformative world is
labelled as such, and no success or failure is counted in it. The E + D world may well be uninformative: across the
seven earlier worlds, E given D had a lower bound at or below 0 on confirmation in three. A two-world reading, or
BENCHMARK FAILURE, is therefore plausible.

**Adjudication** (`truth/adjudicate.py`: a pure function of the record, applied alike to L2 and the comparator):
- **The scored claims:** each candidate's final status, in the existing vocabulary (untested, promising, accepted,
  rejected, deteriorated, redundant), and the final selection. The prose conclusion is reported verbatim; any
  contradiction between it and the table is listed in the results, never scored. Prose cannot be scored
  deterministically.
- **Evidence:** the searcher's own experiments that are both
  - **fresh:** scored entirely after the change, so the first scored day is 93 or later (the latest possible change day
    is 92). In practice that is every window except the 28-day window at day 112;
  - **non-indicative:** at least 14 days. The brief itself calls intervals under 14 days indicative only.
- **Test shapes,** for candidate c with partner p:
  - A(c): c against no covariate;
  - C(c): c given p;
  - S: c and p against no covariate.
- **The governing result** of each shape is the longest window, then the later cutoff, then the later experiment. This
  settles conflicting results. A lower bound of exactly 0 counts as null.
- **Positive evidence:**
  - alone: the governing A(c) is above 0;
  - conditional: the governing C(c) is above 0.
- **Elimination,** allowed only where no direct test of that shape exists. It relies on an exact identity: on identical
  scored days, skill is a ratio of pooled errors, so:
  - c alone beats no covariate exactly when skill(p given c) < skill(S). The derived positive needs S's lower bound
    above 0 and p-given-c's upper bound below it;
  - c adds given p exactly when skill(p alone) < skill(S). The derived positive needs S's lower bound above 0 and
    p-alone's upper bound below it.

  A null conditional alone never licenses elimination: a null interval is not proof of zero effect.
- **Negative evidence:** the governing A(c) or C(c) exists with a lower bound at or below 0.
- **Claim support:**

  | status | supported when |
  |---|---|
  | accepted | there is positive evidence, alone or conditional. If both candidates are accepted, each needs positive conditional evidence (a joint claim that each adds given the other) |
  | promising | always (it states uncertainty) |
  | redundant | there is negative conditional evidence |
  | rejected or deteriorated | there is negative evidence and no positive evidence |
  | untested | no claim |

- **The selection is supported** when it is empty, when every selected candidate has positive evidence of its own, or
  when it is exactly the pair and the governing S is positive.
- **Incoherence,** counted as unsupported: a selected candidate whose status is rejected, deteriorated or untested; an
  accepted candidate that is not selected.

**Success** (the owner's required conclusions, applied alike to both searchers) needs all of:
1. the world is informative;
2. **completeness:** neither status is untested, and each candidate entered a fresh, non-indicative experiment as a
   covariate. The packet asks for a determination about each candidate;
3. E is accepted with a supported claim, and selected;
4. the distractor is treated correctly for its pair type:
   - **E + D:** a fresh, non-indicative test of D given E exists (resolving the proxy ambiguity), and D is not accepted
     unless D given E is positive. D may still be selected if its status is redundant or promising and the selection
     is supported;
   - **E + N:** N is neither accepted nor selected;
   - **E + R:** R is accepted or selected only with fresh positive evidence of its own;
5. every claim and the selection are supported, and there is no incoherence.

**Reported for each world:**
- every experiment of both searchers in order, with windows, references and the candidates in each test;
- the final conclusion verbatim, and the support of each claim;
- unsupported acceptances, and unsupported rejection or zero-effect claims;
- confirmation (days 127–154, t0-beta, with ridge for context only): {E}, {Z}, {E, Z}, Z given E, E given Z, and both
  selections. It is reported separately and never rescues an unsupported conclusion;
- experiments used, API attempts, refusals, repairs, tokens, t0-beta forecasts and wall time.

**The residual arbitrary case, disclosed:** an informative E + D world in which the searcher's own conditionals both
come back null.

## 7. Programme reading (the owner's labels; the first match wins; never reinterpreted)

| # | Reading | Condition |
|---|---|---|
| 1 | INFRASTRUCTURE FAILURE | an integrity issue, or an L2 call without a valid response after its repair (execution integrity), in any world |
| 2 | BENCHMARK FAILURE | fewer than 2 informative worlds |
| 3 | NARROW RESEARCHER FAILURE | L2 fails in at least 2 informative worlds |
| 4 | SCRIPTABLE NARROW KERNEL | L2 and the comparator both succeed in every informative world, and L2 used more than 0.75 times the comparator's experiments over the informative worlds (no efficiency advantage) |
| 5 | AGENTIC VALUE SIGNAL | L2 succeeds in every informative world, and either the comparator fails in at least one, or L2 used at most 0.75 times the comparator's experiments over the informative worlds (materially fewer, with evidence quality preserved by the success rules) |
| 6 | MIXED | anything else |

**Closing line, predeclared:**

| Reading | Closing line |
|---|---|
| INFRASTRUCTURE FAILURE or BENCHMARK FAILURE | BENCHMARK/INFRASTRUCTURE RESULT ONLY |
| NARROW RESEARCHER FAILURE | STOP THIS RESEARCHER LINE |
| SCRIPTABLE NARROW KERNEL | USE A SCRIPT / HUMAN-DRIVEN WORKFLOW (not evidence for autonomous research) |
| AGENTIC VALUE SIGNAL | AUTONOMOUS RESEARCH KERNEL SURVIVES |
| MIXED | STOP THIS RESEARCHER LINE if the comparator succeeded in every informative world where L2 failed (the owner's kill logic), otherwise USE A SCRIPT / HUMAN-DRIVEN WORKFLOW |

**Always stated:** three worlds with one trajectory each are not a rate estimate.

## 8. Process

1. Freeze this spec.
2. One focused independent check (a single agent): truth separation, pair construction, prompt reconstruction,
   adjudication-rule determinism, comparator budget matching. Fix only confirmed defects, and re-pin if needed.
3. One non-scored operational preflight. It is not read for scientific tuning.
4. The frozen three-world scored batch, once. No reroll, no prompt change between worlds, no second trajectory.
