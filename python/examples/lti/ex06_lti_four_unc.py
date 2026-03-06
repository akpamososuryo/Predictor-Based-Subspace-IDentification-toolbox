from __future__ import annotations

import numpy as np
from _common import (
    format_metric,
    innovation_model,
    run_uncertainty_pipeline,
    simulate_system,
    state_space_model,
)
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

    rng = np.random.default_rng(106)
    n_samples = 4000
    r = rng.standard_normal((n_samples, 2))
    e = rng.standard_normal((n_samples, 2))

    ol = innovation_model(a, b, c, d, k)
    ol_nom = state_space_model(a, b, c, d)
    y0, _ = simulate_system(ol_nom, r)
    y, _ = simulate_system(ol, np.hstack((r, e)))

    print("[ex06-uncertainty]")
    print(f"SNR (dB): {format_metric(snr_db(y, y0))}")
    _ = run_uncertainty_pipeline(r, y, n=4, f=10, p=10, h=1.0)


if __name__ == "__main__":
    main()
