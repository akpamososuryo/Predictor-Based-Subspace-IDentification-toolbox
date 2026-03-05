from __future__ import annotations

import numpy as np
from _common import estimate_varx_abcdk, simulate_lti, stable_random_system, vaf_percent


def main() -> None:
    a, b, c, d, k = stable_random_system(n=7, r=2, l_out=3, seed=107)

    n_samples = 4000
    mcs = 20
    rng = np.random.default_rng(107)
    vaf_store = np.zeros((mcs, 3), dtype=np.float64)
    pole_store = np.zeros((mcs, a.shape[0]), dtype=np.complex128)

    for i in range(mcs):
        u = np.column_stack(
            (
                np.sign(rng.standard_normal(n_samples)),
                1e3 * np.sign(rng.standard_normal(n_samples)),
            )
        ).astype(np.float64)
        y, _ = simulate_lti(a, b, c, d, u, k=k, e=0.03 * rng.standard_normal((n_samples, 3)))
        y_nom, _ = simulate_lti(a, b, c, d, u)

        _, ai, bi, ci, di, _, _, _ = estimate_varx_abcdk(u, y, n=a.shape[0], f=20, p=50)
        yi, _ = simulate_lti(ai, bi, ci, di, u)

        vaf_store[i, :] = vaf_percent(y_nom, yi)
        pole_store[i, :] = np.linalg.eigvals(ai)

    print("[ex07-monte-carlo]")
    print(f"VAF mean (%): {np.array2string(np.mean(vaf_store, axis=0), precision=2)}")
    print(f"VAF std  (%): {np.array2string(np.std(vaf_store, axis=0), precision=2)}")
    print(
        f"Mean pole magnitudes: {np.array2string(np.mean(np.abs(pole_store), axis=0), precision=4)}"
    )


if __name__ == "__main__":
    main()
