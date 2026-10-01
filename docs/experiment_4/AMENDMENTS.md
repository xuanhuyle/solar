# Experiment 4: amendments

The frozen specification (`solarbench/price_spec.py`, `PRICE_SPEC_SHA256`) and the one-pager are unchanged.
An amendment is an owner-approved change to how one frozen rule is carried out. It is recorded here, beside the
frozen text and never inside it, following the specification's convention for owner decisions ("reported as an
amendment", "never a silent edit", "reported as amended"). It is named in each command's meta file
(`k1_attempt.json`, `smoke.json`, `check.json`, `run_meta.json`), in the K1 attempt record and in `summary.md`.
This file's sha256 is pinned by `tests/test_price_spec.py`.

## A1 (2026-09-30): the LEAR penalty is chosen as scikit-learn ≤ 0.23.1 chose it

**Owner's approval (2026-09-30), verbatim:** "Approve “Amend, use attempt 3.” Make the amendment narrowly reproduce
the verified 2020 scikit-learn behaviour, document the independent evidence and historical cause, change no
thresholds or other Experiment 4 rules, and treat attempt 3 as final regardless of outcome."

**Superseded frozen text:** `PRICE_SPEC["lear"]["penalty"]`, step (1) only:

> (1) alpha_h = LassoLarsIC(criterion='aic', fit_intercept=True, max_iter=2500, noise_variance=np.var(y_h, ddof=0))
> fitted on X with each column centred on its mean and divided by the L2 norm of the centred column (a zero-norm
> column is divided by 1): scikit-learn < 1.2's LassoLarsIC with its default normalize=True, whose criterion
> n*MSE/var(y) + 2*df has the same argmin

**Replacement for step (1):**

> (1) alpha_h = the penalty that scikit-learn 0.22's LassoLarsIC(criterion='aic', max_iter=2500) (normalize=True,
> precompute='auto') selects on X. This is the behaviour of every release from 0.22 to 0.23.1, the releases the
> toolbox could use when the published EPF forecasts were made. It works as follows: each column is centred and divided by the L2 norm of the centred column (a zero norm is
> replaced by 1); y_h is centred; the lasso LARS path is computed (Gram 'auto', eps = machine epsilon,
> max_iter 2500); and alpha_h is the path point minimising n*MSE/(var(y_h) + eps) + 2*df. When the training rows
> number no more than the columns, the MSE is computed on the design as LARS leaves it (its columns permuted in
> place), as 0.22 does.

Steps (2) and (3) of the penalty, and every other rule, stay as frozen.

**Historical cause.**
- Every scikit-learn release from at least 0.18.2 to 0.23.1 has the same flaw. `lars_path` with `Gram='auto'` does not copy X when
  n_samples ≤ n_features, and swaps its columns in place as variables enter and leave the path. `LassoLarsIC.fit`
  then scores every path point with `y - X @ coef_path_`, pairing coefficients in the original column order with the
  permuted matrix. The set of candidate penalties is the same; the AIC's choice among them can differ.
- The 0.23.2 release fixed it (2020-08-03; changelog `doc/whats_new/v0.23.rst`: "linear_model.lars_path does not
  overwrite X when X_copy=True and Gram='auto'", PR #17914).
- The published LEAR forecasts that K1 compares with (`epftoolbox forecasts/Forecasts_FR_DNN_LEAR_ensembles.csv`)
  were first committed on 2020-06-25 (epftoolbox d8dad5b). Their values are unchanged since, to within 6e-14 (at most 4e-16 relative; float formatting only). At that
  date the toolbox required `scikit-learn>=0.22` and imported `sklearn.utils._testing` (0.22 onwards). No fixed
  release existed yet.
- The frozen step (1) describes the corrected computation (0.23.2 onwards). Its claim that the two share "the same
  argmin" does not hold in general for the releases that made the published forecasts when a window has no more
  training rows than columns.

**Independent evidence** (none of it uses EPF-FR data or any K1 number; audit `wf_ec1b4a41-118`, 9 agents, each
lens checked by a skeptic):
- The real released wheels on a known-answer case, `RandomState(0)`, x 49×247,
  y = x0 − 2·x3 + 0.5·x100 + N(0, 0.5):

  | computation | penalty (12 significant digits) |
  |---|---|
  | scikit-learn 0.22.2.post1 and 0.23.1 | 0.269903704353 |
  | scikit-learn 0.23.2, and the frozen step (1) on 1.7.2 | 0.0335489881715 |
  | this amendment on 1.7.2 | 0.269903704353 |

  The last one or two digits of the full doubles depend on the BLAS kernel. With the audit container's default
  OpenBLAS kernel, the real 0.22.2.post1 and 0.23.1 wheels give 0.26990370435295313, bit-identical to this
  amendment, and 0.23.2 gives 0.03354898817147152. With OPENBLAS_CORETYPE=Prescott they give 0.2699037043529531
  and 0.03354898817147161.

- With more rows than columns (60×30, 300×247), all of them agree to 1e-14 relative.
- On synthetic designs built with our own `features` and `InvariantScaler`, the amendment reproduces the real
  0.22.2.post1:
  - 34,944 short-window fits: forecasts equal to within 9.8e-12;
  - 960 of 960 penalties equal in both column orders;
  - long windows unchanged (≤ 1.3e-11 relative).
- An independent pre-flight check (`wf_192709f5-d27`) repeated this against the real 0.22.2.post1 and 0.23.1
  wheels on 35,136 fits of K1-shaped (247-column) and Experiment 4-shaped (104-column) designs: the same path point
  in every fit (relative alpha difference ≤ 3.4e-11), and forecasts equal to within 7e-11 EUR/MWh.
- Where it acts, and where it doesn't:
  - It acts only when a calibration window has no more training rows than columns: windows 56 and 84 (49 and 77
    rows). That is 247 columns in K1 and 104 in Experiment 4's `lear_ens`.
  - Windows 1092 and 1456 use a Gram matrix; X is never touched there, and nothing changes.

**Consistency with the logged attempts** (K1 numbers, not part of the evidence above). In attempts 1 and 2 the MAE
deviations were largest in the 56- and 84-day windows (−1.60% and −0.36%, unchanged by the column reorder),
consistent with A1's mechanism. The long windows also departed (+0.02% / +0.02% in attempt 1, +0.14% / +0.21% in
attempt 2); A1 does not address that (L1, below).

**What A1 changes.** Only `solarbench/lear.py::aic_alpha`, and so the penalty of the 56- and 84-day windows:
- in K1;
- in Experiment 4's `lear_ens` (and `lear_ens_eq`, its bands), because `lear.scored_only_if` requires the scored
  `lear.py` to be the one K1 validated. There is no K1-only switch.

**What A1 does not change:**
- no threshold or tolerance of K1 or of any probe;
- no feature, lag or column order (the hour-major order of 47d6e06 stays);
- no window, transform, or Lasso refit (penalty steps 2 and 3);
- no other rule of Experiment 4;
- the long windows.

**K1 under A1.** Attempt 3 (the last of `gates.K1.attempts`) runs the amended `lear.py`, and is final regardless of
its outcome.
- If it passes, P2 is scored and reported as amended (A1).
- If it fails, K1 has failed and P2 reads "not runnable", as the frozen rules say.

An unexplained difference in the long windows (audit finding L1) may remain. It has no fix within the
specification and is reported with the result.

**Outcome (2026-09-30).** Attempt 3 ran the amended `lear.py` (sha256 `7770361a…`) at commit 62bcf38 in Actions run
[36780460835](https://github.com/xuanhuyle/solar/actions/runs/36780460835).
- Every hour was forecast. Every MAE tolerance passed: 56 +0.53%, 84 +0.36%, 1092 +0.14%, 1456 +0.21%, ensemble +0.09%.
- The mean absolute difference from the published ensemble forecasts was 0.408 EUR/MWh (attempt 2: 0.558), above the
  0.25 limit.
- As predicted, A1 moved the short windows (−1.60% / −0.36% → +0.53% / +0.36%) and left the long windows unchanged.
- The attempt is final. K1 has failed, so `lear_ens` and `lear_ens_eq` are not scored: P2 reads "not runnable" and the
  LEAR secondaries read "not run", as the frozen rules say.
- A1 therefore affects no scored arm of Experiment 4. It stays recorded because the K1 attempt it governed counts.
