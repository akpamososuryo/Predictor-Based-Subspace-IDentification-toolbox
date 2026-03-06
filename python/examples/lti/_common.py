from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
from control import matlab as ml
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
StateSpace = Any


def _as_2d_float64(data: ArrayF64) -> ArrayF64:
    arr = np.asarray(data, dtype=np.float64)
    if arr.ndim == 1:
        return arr.reshape(-1, 1)
    if arr.ndim != 2:
        raise ValueError(f"Expected a 1D or 2D array, received shape {arr.shape}.")
    return arr


def _samples_first(data: ArrayF64) -> ArrayF64:
    arr = _as_2d_float64(data)
    if arr.shape[1] > arr.shape[0]:
        return arr.T
    return arr


def time_vector(n_samples: int, dt: float = 1.0) -> ArrayF64:
    return np.arange(n_samples, dtype=np.float64) * dt


def state_space_model(
    a: ArrayF64,
    b: ArrayF64,
    c: ArrayF64,
    d: ArrayF64,
    dt: float = 1.0,
) -> StateSpace:
    return ml.ss(a, b, c, d, dt)


def innovation_model(
    a: ArrayF64,
    b: ArrayF64,
    c: ArrayF64,
    d: ArrayF64,
    k: ArrayF64,
    dt: float = 1.0,
) -> StateSpace:
    l_out = c.shape[0]
    return ml.ss(a, np.hstack((b, k)), c, np.hstack((d, np.eye(l_out))), dt)


def feedback_model(plant: StateSpace, f_gain: ArrayF64) -> StateSpace:
    controller = ml.ss([], [], [], np.asarray(f_gain, dtype=np.float64), plant.dt)
    return ml.feedback(plant, controller, sign=-1)


def simulate_system(
    sys_model: StateSpace,
    u: ArrayF64,
    *,
    dt: float | None = None,
    x0: ArrayF64 | None = None,
) -> tuple[ArrayF64, ArrayF64]:
    u_2d = _as_2d_float64(u)
    sample_time = float(sys_model.dt if dt is None else dt)
    x0_use = (
        np.zeros((sys_model.nstates,), dtype=np.float64)
        if x0 is None
        else x0.astype(np.float64)
    )
    y, _, x = ml.lsim(
        sys_model,
        U=u_2d,
        T=time_vector(u_2d.shape[0], sample_time),
        X0=x0_use,
    )
    y = np.asarray(y, dtype=np.float64)
    x = np.asarray(x, dtype=np.float64)
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    return y, x


def frequency_response(sys_model: StateSpace, w: ArrayF64) -> ArrayF64:
    omega = np.asarray(w, dtype=np.float64)
    mag, phase, _ = ml.freqresp(sys_model, omega)
    mag_arr = np.asarray(mag, dtype=np.float64)
    phase_arr = np.asarray(phase, dtype=np.float64)
    response = mag_arr * np.exp(1j * phase_arr)
    if response.ndim == 1:
        response = response.reshape(1, 1, -1)
    return response


def format_metric(values: float | ArrayF64, precision: int = 2) -> str:
    arr = np.asarray(values, dtype=np.float64)
    if arr.ndim == 0:
        return f"{float(arr):.{precision}f}"
    return np.array2string(arr, precision=precision)


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
    u_2d = _as_2d_float64(u)
    if e is None and k is None:
        return simulate_system(state_space_model(a, b, c, d), u_2d, x0=x0)

    if k is None:
        raise ValueError("Noise samples require an innovation matrix k for combined simulation.")

    e_2d = (
        np.zeros((u_2d.shape[0], c.shape[0]), dtype=np.float64)
        if e is None
        else _as_2d_float64(e)
    )
    return simulate_system(innovation_model(a, b, c, d, k), np.hstack((u_2d, e_2d)), x0=x0)


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
    r_ref_2d = _as_2d_float64(r_ref)
    n_samples = r_ref_2d.shape[0]
    r_in = b.shape[1]
    l_out = c.shape[0]

    y = np.zeros((n_samples, l_out), dtype=np.float64)
    u = np.zeros((n_samples, r_in), dtype=np.float64)
    x = np.zeros((a.shape[0],), dtype=np.float64)
    e_use = np.zeros((n_samples, l_out), dtype=np.float64) if e is None else _as_2d_float64(e)

    for t in range(n_samples):
        # Match the MATLAB closed-loop example flow: compute the measured output first,
        # then form the current control input u[k] = r[k] - F y[k].
        y[t, :] = c @ x + e_use[t, :]
        u[t, :] = r_ref_2d[t, :] - f_gain @ y[t, :]
        x = (
            a @ x + b @ u[t, :]
            if k_noise is None
            else a @ x + b @ u[t, :] + k_noise @ e_use[t, :]
        )

    y_nom, _ = simulate_system(state_space_model(a, b, c, d), u)
    return u, y, y_nom


def estimate_varx_abcdk(
    u: ArrayF64,
    y: ArrayF64,
    n: int,
    f: int,
    p: int,
) -> tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64]:
    s, x, varx, u_proj, zps = dordvarx(u, y, f, p, reg="tikh", opt="gcv")
    x_n = dmodx(x, n)
    a, b, c, d, k = dx2abcdk(x_n, u, y, f, p, c="none", return_k=True)
    return s, a, b, c, d, k, varx, zps


def estimate_varmax_abcdk(
    u: ArrayF64,
    y: ArrayF64,
    n: int,
    f: int,
    p: int,
    *,
    method: str = "els",
    tol: float = 1e-6,
    reg: str = "tikh",
    opt: str | float = "gcv",
) -> tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64]:
    s, x, _, _ = dordvarmax(u, y, f, p, method=method, tol=tol, reg=reg, opt=opt)
    x_n = dmodx(x, n)
    return (s,) + dx2abcdk(x_n, u, y, f, p, c="none", return_k=True)


def estimate_fir_abcd(
    u: ArrayF64,
    y: ArrayF64,
    n: int,
    f: int,
    p: int,
    *,
    reg: str = "tikh",
    opt: str | float = "gcv",
) -> tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64]:
    s, x, _ = dordfir(u, y, f, p, reg=reg, opt=opt)
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


def print_case_summary(name: str, snr: ArrayF64, vaf_values: ArrayF64, a: ArrayF64) -> None:
    print(f"\n[{name}]")
    print(f"SNR (dB): {format_metric(snr)}")
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
