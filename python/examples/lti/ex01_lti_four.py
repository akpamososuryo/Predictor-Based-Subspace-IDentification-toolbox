from __future__ import annotations

import numpy as np
from _common import (
    estimate_varmax_abcdk,
    estimate_varx_abcdk,
    print_case_summary,
    simulate_closed_loop,
    vaf_percent,
)
from control import matlab as ml
from snr import snr_db


def main() -> None:
    a = np.array(
        [
            [0.67, 0.67, 0.0, 0.0],
            [-0.67, 0.67, 0.0, 0.0],
            [0.0, 0.0, -0.67, -0.67],
            [0.0, 0.0, 0.67, -0.67],
        ],
        dtype=np.float64,
    )
    b = np.array(
        [[0.6598, -0.5256], [1.9698, 0.4845], [4.3171, -0.4879], [-2.6436, -0.3416]],
        dtype=np.float64,
    )
    k = np.array(
        [[-0.6968, -0.1474], [0.1722, 0.5646], [0.6484, -0.4660], [-0.94, 0.1032]],
        dtype=np.float64,
    )
    c = np.array(
        [[-0.3749, 0.0751, -0.5225, 0.583], [-0.8977, 0.7543, 0.1159, 0.0982]],
        dtype=np.float64,
    )
    d = np.zeros((2, 2), dtype=np.float64)

    n_samples = 4000
    rng = np.random.default_rng(101)
    t = np.arange(n_samples, dtype=np.float64)
    r = rng.standard_normal((n_samples, 2))
    e = rng.standard_normal((n_samples, 2))

    ol = ml.ss(a, np.hstack((b, k)), c, np.hstack((d, np.eye(c.shape[0]))), 1.0)
    ol_nom = ml.ss(a, b, c, d, 1.0)
    y, _, _ = ml.lsim(ol, np.hstack((r, e)), t)
    y0, _, _ = ml.lsim(ol_nom, r, t)
    y = np.asarray(y, dtype=np.float64)
    y0 = np.asarray(y0, dtype=np.float64)

    n = 4
    f = 10
    p = 10

    _, ai, bi, ci, di, _, _, _ = estimate_varx_abcdk(r, y, n, f, p)
    varmax_ok = True
    try:
        _, av, bv, cv, dv, _ = estimate_varmax_abcdk(r, y, n, f, p)
    except (np.linalg.LinAlgError, ValueError, FloatingPointError) as exc:
        varmax_ok = False
        print(f"[ex01-open-varmax] skipped due to numerical issue: {exc}")

    yi, _, _ = ml.lsim(ml.ss(ai, bi, ci, di, 1.0), r, t)
    yi = np.asarray(yi, dtype=np.float64)
    if varmax_ok:
        yv, _, _ = ml.lsim(ml.ss(av, bv, cv, dv, 1.0), r, t)
        yv = np.asarray(yv, dtype=np.float64)

    print_case_summary("ex01-open-varx", snr_db(y, y0), vaf_percent(y0, yi), ai)
    if varmax_ok:
        print_case_summary("ex01-open-varmax", snr_db(y, y0), vaf_percent(y0, yv), av)

    f_gain = np.diag([0.25, 0.25]).astype(np.float64)
    u_cl, y_cl, y0_cl = simulate_closed_loop(a, b, c, d, k, f_gain, r, e=0.7 * e)

    _, ai_cl, bi_cl, ci_cl, di_cl, _, _, _ = estimate_varx_abcdk(u_cl, y_cl, n, f, p)
    varmax_cl_ok = True
    try:
        _, av_cl, bv_cl, cv_cl, dv_cl, _ = estimate_varmax_abcdk(u_cl, y_cl, n, f, p)
    except (np.linalg.LinAlgError, ValueError, FloatingPointError) as exc:
        varmax_cl_ok = False
        print(f"[ex01-closed-varmax] skipped due to numerical issue: {exc}")

    yi_cl, _, _ = ml.lsim(ml.ss(ai_cl, bi_cl, ci_cl, di_cl, 1.0), u_cl, t)
    yi_cl = np.asarray(yi_cl, dtype=np.float64)
    if varmax_cl_ok:
        yv_cl, _, _ = ml.lsim(ml.ss(av_cl, bv_cl, cv_cl, dv_cl, 1.0), u_cl, t)
        yv_cl = np.asarray(yv_cl, dtype=np.float64)

    print_case_summary(
        "ex01-closed-varx", snr_db(y_cl, y0_cl), vaf_percent(y0_cl, yi_cl), ai_cl
    )
    if varmax_cl_ok:
        print_case_summary(
            "ex01-closed-varmax",
            snr_db(y_cl, y0_cl),
            vaf_percent(y0_cl, yv_cl),
            av_cl,
        )


if __name__ == "__main__":
    main()
