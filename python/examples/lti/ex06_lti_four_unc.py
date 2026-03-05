from __future__ import annotations

import numpy as np
from _common import run_uncertainty_pipeline, simulate_lti, snr_db


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

    y0, _ = simulate_lti(a, b, c, d, r)
    y, _ = simulate_lti(a, b, c, d, r, k=k, e=e)

    print("[ex06-uncertainty]")
    print(f"SNR (dB): {snr_db(y, y0):.2f}")
    _ = run_uncertainty_pipeline(r, y, n=4, f=10, p=10, h=1.0)


if __name__ == "__main__":
    main()
