from __future__ import annotations

import numpy as np
from _common import (
    estimate_varx_abcdk,
    print_case_summary,
    simulate_lti,
    stable_random_system,
    vaf_percent,
)


def main() -> None:
    # MATLAB ex04 uses wtsLTI; this Python port uses a deterministic
    # surrogate with matching I/O sizes.
    a, b, c, d, k = stable_random_system(n=7, r=2, l_out=3, seed=104)

    n_samples = 10000
    h = 0.1
    rng = np.random.default_rng(104)
    r_pitch = np.sign(rng.standard_normal(n_samples))
    r_torque = 1e3 * np.sign(rng.standard_normal(n_samples))
    u = np.column_stack((r_pitch, r_torque)).astype(np.float64)
    e = 0.03 * rng.standard_normal((n_samples, 3))

    y, _ = simulate_lti(a, b, c, d, u, k=k, e=e)
    y_nom, _ = simulate_lti(a, b, c, d, u)

    n = a.shape[0]
    p = 50
    f = 20

    _, ai, bi, ci, di, _, _, _ = estimate_varx_abcdk(u, y, n, f, p)
    yi, _ = simulate_lti(ai, bi, ci, di, u)

    print_case_summary("ex04-wts-surrogate", 0.0, vaf_percent(y_nom, yi), ai)
    print(f"Sample time used: {h}")


if __name__ == "__main__":
    main()
