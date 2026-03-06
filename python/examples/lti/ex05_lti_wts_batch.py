from __future__ import annotations

import numpy as np
from _common import (
    dmodx,
    dordvarx,
    dx2abcdk,
    innovation_model,
    simulate_system,
    stable_random_system,
    state_space_model,
    vaf_percent,
)


def main() -> None:
    a, b, c, d, k = stable_random_system(n=7, r=2, l_out=3, seed=105)
    n_samples = 12000
    rng = np.random.default_rng(105)

    u_full = np.column_stack(
        (np.sign(rng.standard_normal(n_samples)), 1e3 * np.sign(rng.standard_normal(n_samples)))
    ).astype(np.float64)
    ol = innovation_model(a, b, c, d, k)
    ol_nom = state_space_model(a, b, c, d)
    e_full = 0.03 * rng.standard_normal((n_samples, 3))
    y_full, _ = simulate_system(ol, np.hstack((u_full, e_full)))
    y_nom, _ = simulate_system(ol_nom, u_full)

    u_batches = [u_full[:4000, :], u_full[5000:8000, :], u_full[9000:12000, :]]
    y_batches = [y_full[:4000, :], y_full[5000:8000, :], y_full[9000:12000, :]]

    f = 20
    p = 50
    s, x_batch, _, _, _ = dordvarx(u_batches, y_batches, f, p, reg="tikh", opt="gcv")
    x_n = dmodx(x_batch, a.shape[0])
    ai, bi, ci, di, _ = dx2abcdk(x_n, u_batches, y_batches, f, p, c="none", return_k=True)

    yi, _ = simulate_system(state_space_model(ai, bi, ci, di), u_full)
    print("[ex05-batch]")
    print(f"Singular values shape: {s.shape}")
    print(f"VAF (%): {np.array2string(vaf_percent(y_nom, yi), precision=2)}")
    print(f"Estimated poles: {np.array2string(np.linalg.eigvals(ai), precision=4)}")


if __name__ == "__main__":
    main()
