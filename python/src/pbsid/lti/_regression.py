from __future__ import annotations

from typing import cast

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import fminbound

type ArrayF64 = NDArray[np.float64]


def _sorted_eigh_desc(mat: ArrayF64) -> tuple[ArrayF64, ArrayF64]:
    eigvals, eigvecs = np.linalg.eigh(mat)
    order = np.argsort(np.abs(eigvals))[::-1]
    eigvals_sorted = np.abs(eigvals[order]).astype(np.float64)
    eigvecs_sorted = np.real(eigvecs[:, order]).astype(np.float64)
    return eigvecs_sorted, eigvals_sorted


def _reggcv_tikh(yp: ArrayF64, eigvecs: ArrayF64, eigvals: ArrayF64) -> float:
    beta = eigvecs.T @ yp
    s = np.sqrt(eigvals)
    smin_ratio = 16.0 * np.finfo(np.float64).eps
    reg_param = np.zeros((200,), dtype=np.float64)
    reg_param[-1] = max(s[-1], s[0] * smin_ratio)
    ratio = (s[0] / reg_param[-1]) ** (1.0 / (reg_param.size - 1))
    for i in range(reg_param.size - 2, -1, -1):
        reg_param[i] = ratio * reg_param[i + 1]

    def gcv_fun(lam: float) -> float:
        filt = (lam**2) / (eigvals + lam**2)
        numer = np.linalg.norm((filt[:, np.newaxis]) * beta, ord="fro") ** 2
        denom = float(np.sum(filt) ** 2)
        return float(numer / max(denom, 1e-300))

    g_vals = np.array([gcv_fun(lam) for lam in reg_param], dtype=np.float64)
    min_idx = int(np.argmin(g_vals))
    lo = reg_param[min(min_idx + 1, reg_param.size - 1)]
    hi = reg_param[max(min_idx - 1, 0)]
    left = min(lo, hi)
    right = max(lo, hi)
    if np.isclose(left, right):
        return float(reg_param[min_idx])
    return float(fminbound(gcv_fun, left, right, xtol=1e-8, maxfun=500))


def _resolve_tikh_regularization(
    yp: ArrayF64,
    eigvecs: ArrayF64,
    eigvals: ArrayF64,
    opt: str | float,
) -> float:
    if np.isscalar(opt) and not isinstance(opt, str):
        return float(cast(float, opt))

    opt_l = str(opt).lower()
    if opt_l == "gcv":
        return _reggcv_tikh(yp, eigvecs, eigvals)
    if opt_l == "lcurve":
        raise NotImplementedError(
            "Tikhonov lcurve selection is not yet supported in the Python port."
        )
    raise ValueError("Unsupported Tikhonov regularization option.")


def regress_matrix(
    y: ArrayF64,
    p: ArrayF64,
    reg: str,
    opt: str | float,
    x0: ArrayF64 | None = None,
) -> tuple[ArrayF64, float, ArrayF64]:
    reg_l = str(reg).lower()
    if reg_l == "none":
        zps = np.asarray(np.linalg.pinv(p), dtype=np.float64)
        if x0 is None:
            return y @ zps, 0.0, zps
        return x0 + (y - x0 @ p) @ zps, 0.0, zps

    if reg_l != "tikh":
        raise NotImplementedError(
            "Only reg='none' and reg='tikh' are currently supported."
        )

    n_cols = y.shape[1]
    cov = (p @ p.T) / float(n_cols)
    eigvecs, eigvals = _sorted_eigh_desc(cov)
    y_res = y if x0 is None else y - x0 @ p
    yp = ((y_res @ p.T) / float(n_cols)).T
    reg_raw = _resolve_tikh_regularization(yp, eigvecs, eigvals, opt)
    denom = eigvals**2 + reg_raw**2
    filt = np.divide(eigvals, denom, out=np.zeros_like(eigvals), where=denom > 0.0)
    zps = (eigvecs @ np.diag(filt) @ eigvecs.T @ (p / float(n_cols))).T
    x = y @ zps if x0 is None else x0 + y_res @ zps
    return (
        np.asarray(x, dtype=np.float64),
        float(reg_raw * n_cols),
        np.asarray(zps, dtype=np.float64),
    )