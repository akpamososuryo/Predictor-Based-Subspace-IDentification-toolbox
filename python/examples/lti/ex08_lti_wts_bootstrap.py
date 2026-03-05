from __future__ import annotations

import numpy as np
from _common import estimate_varx_abcdk, simulate_lti, stable_random_system, vaf_percent


def main() -> None:
    a, b, c, d, k = stable_random_system(n=7, r=2, l_out=3, seed=108)

    n_samples = 5000
    bootstrap_runs = 20
    rng = np.random.default_rng(108)

    u = np.column_stack(
        (np.sign(rng.standard_normal(n_samples)), 1e3 * np.sign(rng.standard_normal(n_samples)))
    ).astype(np.float64)
    y, _ = simulate_lti(a, b, c, d, u, k=k, e=0.03 * rng.standard_normal((n_samples, 3)))
    y_nom, _ = simulate_lti(a, b, c, d, u)

    _, ai0, bi0, ci0, di0, _, _, _ = estimate_varx_abcdk(u, y, n=a.shape[0], f=20, p=50)
    y_hat0, _ = simulate_lti(ai0, bi0, ci0, di0, u)
    resid0 = y - y_hat0

    vaf_runs = np.zeros((bootstrap_runs, y.shape[1]), dtype=np.float64)
    for i in range(bootstrap_runs):
        idx = rng.integers(0, n_samples, size=n_samples)
        y_boot = y_hat0 + resid0[idx, :]
        _, ai, bi, ci, di, _, _, _ = estimate_varx_abcdk(u, y_boot, n=a.shape[0], f=20, p=50)
        y_hat, _ = simulate_lti(ai, bi, ci, di, u)
        vaf_runs[i, :] = vaf_percent(y_nom, y_hat)

    print("[ex08-bootstrap]")
    print(f"Reference VAF (%): {np.array2string(vaf_percent(y_nom, y_hat0), precision=2)}")
    print(f"Bootstrap mean VAF (%): {np.array2string(np.mean(vaf_runs, axis=0), precision=2)}")
    print(f"Bootstrap std VAF  (%): {np.array2string(np.std(vaf_runs, axis=0), precision=2)}")


if __name__ == "__main__":
    main()
