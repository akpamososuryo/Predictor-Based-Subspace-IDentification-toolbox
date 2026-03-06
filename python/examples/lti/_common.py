from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

PY_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PY_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pbsid.lti import (  # noqa: E402
    dmodx,
    dordfir,
    dordvarmax,
    dordvarx,
    dvar2eig,
    dvar2frd,
    dvar4abcdk,
    dvar4varx,
    dx2abcd,
    dx2abcdk,
)

ArrayF64 = NDArray[np.float64]


def snr_db(y: ArrayF64, y_ref: ArrayF64) -> float:
    num = float(np.sum(np.square(y_ref)))
    den = float(np.sum(np.square(y - y_ref)))
    den = max(den, 1e-12)
    return 10.0 * np.log10(num / den)


def vaf_percent(y: ArrayF64, y_hat: ArrayF64) -> ArrayF64:
    err = y - y_hat
    var_y = np.var(y, axis=0)
    var_e = np.var(err, axis=0)
    return (1.0 - (var_e / np.maximum(var_y, 1e-12))) * 100.0


def simulate_lti(
    a: ArrayF64,
    b: ArrayF64,
    c: ArrayF64,
    d: ArrayF64,
    u: ArrayF64,
    *,
    k: ArrayF64 | None = None,
    e: ArrayF64 | None = None,
    x0: ArrayF64 | None = None,
) -> tuple[ArrayF64, ArrayF64]:
    n_samples = u.shape[0]
    n = a.shape[0]
    l_out = c.shape[0]

    x = np.zeros((n,), dtype=np.float64) if x0 is None else x0.astype(np.float64).copy()
    y = np.zeros((n_samples, l_out), dtype=np.float64)
    x_hist = np.zeros((n_samples + 1, n), dtype=np.float64)
    x_hist[0, :] = x

    e_use = np.zeros((n_samples, l_out), dtype=np.float64) if e is None else e

    for t in range(n_samples):
        ut = u[t, :]
        et = e_use[t, :]
        y[t, :] = c @ x + d @ ut + et
        x = a @ x + b @ ut if k is None else a @ x + b @ ut + k @ et
        x_hist[t + 1, :] = x

    return y, x_hist


def simulate_closed_loop(
    a: ArrayF64,
    b: ArrayF64,
    c: ArrayF64,
    d: ArrayF64,
    k_noise: ArrayF64 | None,
    f_gain: ArrayF64,
    r_ref: ArrayF64,
    *,
    e: ArrayF64 | None = None,
) -> tuple[ArrayF64, ArrayF64, ArrayF64]:
    n_samples = r_ref.shape[0]
    r_in = b.shape[1]
    l_out = c.shape[0]

    y = np.zeros((n_samples, l_out), dtype=np.float64)
    u = np.zeros((n_samples, r_in), dtype=np.float64)
    x = np.zeros((a.shape[0],), dtype=np.float64)
    e_use = np.zeros((n_samples, l_out), dtype=np.float64) if e is None else e

    for t in range(n_samples):
        u[t, :] = r_ref[t, :] - f_gain @ y[t - 1, :] if t > 0 else r_ref[t, :]
        y[t, :] = c @ x + d @ u[t, :] + e_use[t, :]
        x = (
            a @ x + b @ u[t, :]
            if k_noise is None
            else a @ x + b @ u[t, :] + k_noise @ e_use[t, :]
        )

    y_nom, _ = simulate_lti(a, b, c, d, u)
    return u, y, y_nom


def estimate_varx_abcdk(
    u: ArrayF64,
    y: ArrayF64,
    n: int,
    f: int,
    p: int,
) -> tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64]:
    # MATLAB ex01-ex09 typically use tikh/gcv regularization here.
    # The current Python port only exposes the reg="none" path.
    s, x, varx, u_proj, zps = dordvarx(u, y, f, p, reg="none", opt="gcv")
    x_n = dmodx(x, n)
    a, b, c, d, k = dx2abcdk(x_n, u, y, f, p, c="none", return_k=True)
    return s, a, b, c, d, k, varx, zps


def estimate_varmax_abcdk(
    u: ArrayF64,
    y: ArrayF64,
    n: int,
    f: int,
    p: int,
) -> tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64]:
    # MATLAB examples use the ELS path together with tikh/gcv.
    # Only the no-regularization variant is currently ported, but ELS is closer
    # to the intended MATLAB workflow than the gradient fallback.
    s, x, _, _ = dordvarmax(u, y, f, p, method="els", tol=1e-6, reg="none")
    x_n = dmodx(x, n)
    return (s,) + dx2abcdk(x_n, u, y, f, p, c="none", return_k=True)


def estimate_fir_abcd(
    u: ArrayF64,
    y: ArrayF64,
    n: int,
    f: int,
    p: int,
) -> tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64]:
    s, x, _ = dordfir(u, y, f, p, reg="none", opt="gcv")
    x_n = dmodx(x, n)
    a, b, c, d = dx2abcd(x_n, u, y, f, p, c="none")
    return s, a, b, c, d


def stable_random_system(
    *, n: int, r: int, l_out: int, seed: int
) -> tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64]:
    rng = np.random.default_rng(seed)
    q, _ = np.linalg.qr(rng.standard_normal((n, n)))
    eigs = np.linspace(0.65, 0.95, n)
    a = q @ np.diag(eigs) @ np.linalg.inv(q)
    b = 0.25 * rng.standard_normal((n, r))
    c = 0.35 * rng.standard_normal((l_out, n))
    d = 0.05 * rng.standard_normal((l_out, r))
    k = 0.08 * rng.standard_normal((n, l_out))
    return (
        a.astype(np.float64),
        b.astype(np.float64),
        c.astype(np.float64),
        d.astype(np.float64),
        k.astype(np.float64),
    )


def print_case_summary(name: str, snr: float, vaf_values: ArrayF64, a: ArrayF64) -> None:
    print(f"\n[{name}]")
    print(f"SNR (dB): {snr:.2f}")
    print(f"VAF (%): {np.array2string(vaf_values, precision=2)}")
    print(f"Estimated poles: {np.array2string(np.linalg.eigvals(a), precision=4)}")


def run_uncertainty_pipeline(
    u: ArrayF64,
    y: ArrayF64,
    n: int,
    f: int,
    p: int,
    h: float,
) -> tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64]:
    s, x, varx, u_proj, zps = dordvarx(u, y, f, p, reg="none", opt="gcv")
    x_n = dmodx(x, n)
    a, b, c, d, k = dx2abcdk(x_n, u, y, f, p, c="none", return_k=True)

    p_varx, _ = dvar4varx(u, y, p, varx, zps)
    w = np.logspace(-2, np.log10(np.pi), 300)
    g_varx, cov_varx = dvar2frd(p_varx, w, h, p, varx)

    p_abcdk, _ = dvar4abcdk(x_n, u, y, f, p, a, b, c, d, k, u_proj, zps)
    g_abcdk, cov_abcdk = dvar2frd(p_abcdk, w, h, a, b, c, d, k)
    eigs, cov_eigs = dvar2eig(p_abcdk, a)

    print(f"Uncertainty run: S size={s.shape}, eig count={eigs.size}")
    print(f"VARX FRD shape={g_varx.shape}, cov shape={cov_varx.shape}")
    print(f"ABCDK FRD shape={g_abcdk.shape}, cov shape={cov_abcdk.shape}")
    print(f"Eigen covariance shape={cov_eigs.shape}")

    return s, g_abcdk, cov_abcdk, eigs
