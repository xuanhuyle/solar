"""The two Phase 0 instruments, given exactly the same information.

A forecast of day d (1-based) is made at the end of day d-1 from the L days d-L..d-1 of the target and, for each
covariate named, its values over those L days plus day d (covariates are known in advance).

- ``T0``: t0-alpha zero-shot, batched, using the call pattern of ``solarbench/price_gates.py`` (k2_reference).
  Outputs t0 silently sanitised are caught (``_NonFiniteWatcher``, copied from ``solarbench/forecasters.py``).
- ``ridge_forecast``: a linear ARX fitted on the same L days only: 24 hour dummies (unpenalised), the target 24
  and 48 hours earlier (only rows whose lags fall inside the window), each covariate (and its square if asked).
  The penalty is chosen by generalised cross-validation.
"""
from __future__ import annotations

import logging

import numpy as np

H = 24
ALPHAS = np.logspace(-3, 3, 13)


def window(y: np.ndarray, x: list[np.ndarray], day: int, context_days: int):
    """Context of the target and covariate blocks (context plus the forecast day) for forecasting ``day``."""
    start, origin, end = (day - context_days - 1) * H, (day - 1) * H, day * H
    if start < 0 or end > len(y):
        raise ValueError(f"day {day} with a {context_days}-day context is outside the data")
    ctx = y[start:origin]
    block = np.stack([xi[start:end] for xi in x]) if x else None
    return ctx, block


# ----------------------------------------------------------------- ridge

def _design(y, x, rows, hours, square):
    cols = [y[rows - H], y[rows - 2 * H]]
    for xi in x:
        cols.append(xi[rows])
        if square:
            cols.append(xi[rows] ** 2)
    pen = np.column_stack(cols)
    dummies = np.zeros((len(rows), H))
    dummies[np.arange(len(rows)), hours] = 1.0
    return dummies, pen


def ridge_forecast(y: np.ndarray, x: list[np.ndarray], day: int, context_days: int, *, square: bool = False):
    """24 hourly forecasts of ``day`` from the ``context_days`` days before it, nothing else."""
    first = day - context_days  # first context day
    train = np.arange((first + 1) * H, (day - 1) * H)  # days first+2 .. day-1 (0-based hour index)
    if len(train) < 2 * H:
        raise ValueError("context too short for the ridge lags")
    target = np.arange((day - 1) * H, day * H)
    if train[0] - 2 * H < (first - 1) * H:
        raise AssertionError("a lag reaches outside the context window")
    d_tr, p_tr = _design(y, x, train, train % H, square)
    d_te, p_te = _design(y, x, target, target % H, square)
    mu, sd = p_tr.mean(0), p_tr.std(0)
    sd[sd == 0] = 1.0
    p_tr, p_te = (p_tr - mu) / sd, (p_te - mu) / sd
    a_tr, a_te = np.hstack([d_tr, p_tr]), np.hstack([d_te, p_te])
    yt = y[train]
    n, k = a_tr.shape
    penal = np.r_[np.zeros(H), np.ones(k - H)]
    gram, rhs = a_tr.T @ a_tr, a_tr.T @ yt
    best = None
    for alpha in ALPHAS:
        mat = gram + alpha * np.diag(penal)
        beta = np.linalg.solve(mat, rhs)
        rss = float(np.sum((yt - a_tr @ beta) ** 2))
        dof = float(np.trace(np.linalg.solve(mat, gram)))
        gcv = n * rss / max(n - dof, 1e-9) ** 2
        if best is None or gcv < best[0]:
            best = (gcv, beta)
    return a_te @ best[1]


# ----------------------------------------------------------------- t0

class _NonFiniteWatcher(logging.Handler):
    """Counts t0's sanitize warnings (copied from solarbench/forecasters.py)."""

    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self.count = 0

    def emit(self, record: logging.LogRecord) -> None:
        if "non-finite" in record.getMessage():
            self.count += 1


class T0:
    """Batched zero-shot t0 forecasts. ``model`` is a loaded t0 model (``solarbench.t0_pinned``)."""

    LEVELS = [0.1, 0.25, 0.5, 0.75, 0.9]

    def __init__(self, model, batch_size: int = 64):
        self.model, self.batch_size, self.sanitised, self.rows = model, batch_size, 0, 0

    def forecast(self, requests: list[tuple[np.ndarray, np.ndarray | None]]) -> list[np.ndarray]:
        """One 24-hour median forecast per (context, covariate block or None). Rows are batched by covariate
        count; context length must be equal within a call."""
        import torch

        out: list = [None] * len(requests)
        self.rows += len(requests)
        groups: dict = {}
        for i, (ctx, block) in enumerate(requests):
            groups.setdefault((len(ctx), 0 if block is None else block.shape[0]), []).append(i)
        logger = logging.getLogger("t0.model.model")
        for (_, k), idx in sorted(groups.items()):
            for s in range(0, len(idx), self.batch_size):
                part = idx[s:s + self.batch_size]
                ctx = torch.from_numpy(np.stack([requests[i][0] for i in part]).astype("float32"))
                kwargs = {"horizon": H, "quantiles": self.LEVELS}
                if k:
                    blocks = np.stack([requests[i][1] for i in part]).astype("float32")
                    kwargs["future_covariates"] = torch.from_numpy(blocks)
                watcher = _NonFiniteWatcher()
                logger.addHandler(watcher)
                try:
                    pred = self.model.predict(ctx, **kwargs)
                finally:
                    logger.removeHandler(watcher)
                self.sanitised += watcher.count
                med = pred.median.detach().cpu().numpy().astype("float64")
                for j, i in enumerate(part):
                    out[i] = med[j, :H]
        return out
