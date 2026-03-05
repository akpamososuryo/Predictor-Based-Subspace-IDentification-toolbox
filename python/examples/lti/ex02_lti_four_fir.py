from __future__ import annotations

import numpy as np
from _common import (
    estimate_fir_abcd,
    estimate_varx_abcdk,
    print_case_summary,
    simulate_closed_loop,
    simulate_lti,
    snr_db,
    vaf_percent,
)


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
    r = rng.standard_normal((n_samples, 2))
    e = rng.standard_normal((n_samples, 2))

    y0, _ = simulate_lti(a, b, c, d, r)
    y = y0 + e

    n = 4
    f = 10
    p = 20

    _, ai, bi, ci, di = estimate_fir_abcd(r, y, n, f, p)
    _, av, bv, cv, dv, _, _, _ = estimate_varx_abcdk(r, y, n, f, p)

    yi, _ = simulate_lti(ai, bi, ci, di, r)
    yv, _ = simulate_lti(av, bv, cv, dv, r)

    print_case_summary("ex02-open-fir", snr_db(y, y0), vaf_percent(y0, yi), ai)
    print_case_summary("ex02-open-varx", snr_db(y, y0), vaf_percent(y0, yv), av)

    f_gain = np.diag([0.25, 0.25]).astype(np.float64)
    u_cl, y_cl_nom, y0_cl = simulate_closed_loop(a, b, c, d, None, f_gain, r)
    y_cl = y_cl_nom + 0.5 * e

    _, ai_cl, bi_cl, ci_cl, di_cl = estimate_fir_abcd(u_cl, y_cl, n, f, p)
    _, av_cl, bv_cl, cv_cl, dv_cl, _, _, _ = estimate_varx_abcdk(u_cl, y_cl, n, f, p)

    yi_cl, _ = simulate_lti(ai_cl, bi_cl, ci_cl, di_cl, u_cl)
    yv_cl, _ = simulate_lti(av_cl, bv_cl, cv_cl, dv_cl, u_cl)

    print_case_summary("ex02-closed-fir", snr_db(y_cl, y0_cl), vaf_percent(y0_cl, yi_cl), ai_cl)
    print_case_summary("ex02-closed-varx", snr_db(y_cl, y0_cl), vaf_percent(y0_cl, yv_cl), av_cl)


if __name__ == "__main__":
    main()
