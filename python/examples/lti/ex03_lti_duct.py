from __future__ import annotations

import numpy as np
from _common import (
    estimate_varmax_abcdk,
    estimate_varx_abcdk,
    print_case_summary,
    snr_db,
    vaf_percent,
)
from scipy.signal import lfilter


def main() -> None:
    ts = 0.001
    a_den = np.array(
        [
            1.0,
            -1.8937219532483,
            0.92020408176247,
            8.4317527635809e-13,
            -6.9870644340972e-13,
            3.2703011891141e-13,
            -2.8053825784320e-14,
            -4.8518619047975e-13,
            9.0515016323085e-13,
            -8.9573340462955e-13,
            6.2104932381850e-13,
            -4.0655443037130e-13,
            3.8448359402553e-13,
            -4.9321540807220e-13,
            5.3571245452629e-13,
            -6.7043859898372e-13,
            6.5050860651120e-13,
            0.66499999999978,
            -1.2593250989101,
            0.61193571437226,
        ],
        dtype=np.float64,
    )
    b_u = np.array(
        [
            0.0,
            -5.6534330123106e-6,
            5.6870704280702e-6,
            7.7870811926239e-3,
            1.3389477125431e-3,
            -9.1260667240191e-3,
            1.4435759589218e-8,
            -1.2021568096247e-8,
            -2.2746529807395e-9,
            6.3067990166664e-9,
            9.1305924779895e-10,
            -7.5200613526843e-9,
            1.9549739577695e-9,
            1.3891832078608e-8,
            -1.6372496840947e-8,
            9.0003511972213e-3,
            -1.9333235957678e-3,
            -7.0669966879457e-3,
            -3.7850561971775e-6,
            3.7590122810601e-6,
        ],
        dtype=np.float64,
    )
    b_e = np.array(
        [
            0.0,
            -5.65645330123106e-6,
            5.345344280702e-6,
            7.45341926239e-3,
            2.3389477125431e-3,
            -9.5480667240191e-3,
            1.545435759589218e-8,
            -1.2343468096247e-8,
            -2.534549807395e-9,
            4.454930166664e-9,
            9.342424779895e-10,
            -7.2342313526843e-9,
            1.9549739577695e-9,
            1.564565078608e-8,
            -3.1272496840947e-8,
            9.345511972213e-3,
            -1.876875957678e-3,
            -6.0669966879457e-3,
            -3.54561971775e-6,
            3.7590122810601e-6,
        ],
        dtype=np.float64,
    )

    n_samples = 5000
    rng = np.random.default_rng(103)
    r = np.sign(rng.standard_normal(n_samples)).astype(np.float64)
    e = 0.1 * rng.standard_normal(n_samples)

    y0 = lfilter(b_u, a_den, r)
    y = y0 + lfilter(b_e, a_den, e)

    n = 19
    f = 30
    p = 30

    u2 = r.reshape(-1, 1)
    y2 = y.reshape(-1, 1)
    y0_2 = y0.reshape(-1, 1)

    _, ai, bi, ci, di, _, _, _ = estimate_varx_abcdk(u2, y2, n, f, p)
    _, av, bv, cv, dv, _ = estimate_varmax_abcdk(u2, y2, n, f, p)

    yi = np.zeros_like(y0_2)
    yv = np.zeros_like(y0_2)
    x_i = np.zeros((n,), dtype=np.float64)
    x_v = np.zeros((n,), dtype=np.float64)
    for t in range(n_samples):
        yi[t, 0] = ci @ x_i + di @ u2[t, :]
        yv[t, 0] = cv @ x_v + dv @ u2[t, :]
        x_i = ai @ x_i + bi @ u2[t, :]
        x_v = av @ x_v + bv @ u2[t, :]

    print_case_summary("ex03-high-order-varx", snr_db(y2, y0_2), vaf_percent(y0_2, yi), ai)
    print_case_summary("ex03-high-order-varmax", snr_db(y2, y0_2), vaf_percent(y0_2, yv), av)
    print(f"Sample time used: {ts}")


if __name__ == "__main__":
    main()
