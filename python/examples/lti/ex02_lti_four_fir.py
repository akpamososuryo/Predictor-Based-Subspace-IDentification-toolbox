from __future__ import annotations

import numpy as np
from _common import (
    estimate_fir_abcd,
    estimate_varx_abcdk,
    print_case_summary,
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
    c = np.array(
        [[-0.3749, 0.0751, -0.5225, 0.583], [-0.8977, 0.7543, 0.1159, 0.0982]],
        dtype=np.float64,
    )
    d = np.zeros((2, 2), dtype=np.float64)

    n_samples = 4000
    rng = np.random.default_rng(102)
    t = np.arange(n_samples, dtype=np.float64)
    r = rng.standard_normal((n_samples, 2))
    e = rng.standard_normal((n_samples, 2))

    ol = ml.ss(a, b, c, d, 1.0)
    y0, _, _ = ml.lsim(ol, r, t)
    y0 = np.asarray(y0, dtype=np.float64)
    y = y0 + e

    n = 4
    f = 10
    p = 20

    _, ai, bi, ci, di = estimate_fir_abcd(r, y, n, f, p)
    _, av, bv, cv, dv, _, _, _ = estimate_varx_abcdk(r, y, n, f, p)

    yi, _, _ = ml.lsim(ml.ss(ai, bi, ci, di, 1.0), r, t)
    yv, _, _ = ml.lsim(ml.ss(av, bv, cv, dv, 1.0), r, t)
    yi = np.asarray(yi, dtype=np.float64)
    yv = np.asarray(yv, dtype=np.float64)

    print_case_summary("ex02-open-fir", snr_db(y, y0), vaf_percent(y0, yi), ai)
    print_case_summary("ex02-open-varx", snr_db(y, y0), vaf_percent(y0, yv), av)

    f_gain = np.diag([0.25, 0.25]).astype(np.float64)
    cl = ml.feedback(ol, ml.ss([], [], [], f_gain, 1.0), sign=-1)
    y_cl_nom, _, _ = ml.lsim(cl, r, t)
    y_cl_nom = np.asarray(y_cl_nom, dtype=np.float64)
    y_cl = y_cl_nom + 0.5 * e
    u_cl = r - y_cl @ f_gain.T
    y0_cl, _, _ = ml.lsim(ol, u_cl, t)
    y0_cl = np.asarray(y0_cl, dtype=np.float64)

    _, ai_cl, bi_cl, ci_cl, di_cl = estimate_fir_abcd(u_cl, y_cl, n, f, p)
    _, av_cl, bv_cl, cv_cl, dv_cl, _, _, _ = estimate_varx_abcdk(u_cl, y_cl, n, f, p)

    yi_cl, _, _ = ml.lsim(ml.ss(ai_cl, bi_cl, ci_cl, di_cl, 1.0), u_cl, t)
    yv_cl, _, _ = ml.lsim(ml.ss(av_cl, bv_cl, cv_cl, dv_cl, 1.0), u_cl, t)
    yi_cl = np.asarray(yi_cl, dtype=np.float64)
    yv_cl = np.asarray(yv_cl, dtype=np.float64)

    print_case_summary("ex02-closed-fir", snr_db(y_cl, y0_cl), vaf_percent(y0_cl, yi_cl), ai_cl)
    print_case_summary("ex02-closed-varx", snr_db(y_cl, y0_cl), vaf_percent(y0_cl, yv_cl), av_cl)


if __name__ == "__main__":
    main()
