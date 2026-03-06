from __future__ import annotations

from pathlib import Path

import numpy as np
from _common import (
    estimate_varx_abcdk,
    innovation_model,
    simulate_system,
    stable_random_system,
    state_space_model,
    vaf_percent,
)
from scipy.io import loadmat


def _load_or_synthesize(case: str) -> tuple[np.ndarray, np.ndarray, float, float]:
    repo_root = Path(__file__).resolve().parents[3]
    mat_path = repo_root / "examples" / f"smartrotor{case}.mat"
    if mat_path.exists():
        m = loadmat(mat_path, squeeze_me=False, struct_as_record=False)
        u = np.asarray(m["u"], dtype=np.float64)
        y = np.asarray(m["y"], dtype=np.float64)
        if u.shape[0] < u.shape[1]:
            u = u.T
        if y.shape[0] < y.shape[1]:
            y = y.T
        rpm = float(case)
        return u, y, 0.01, rpm

    rpm = float(case)
    ts = 0.01
    a, b, c, d, k = stable_random_system(n=12, r=2, l_out=2, seed=200 + int(case))
    n_samples = 6000
    rng = np.random.default_rng(200 + int(case))
    u = np.column_stack((rng.standard_normal(n_samples), rng.standard_normal(n_samples)))
    t = np.arange(n_samples, dtype=np.float64) * ts
    periodic = np.column_stack(
        (
            np.sin(2.0 * np.pi * rpm * t / 60.0),
            np.cos(2.0 * np.pi * rpm * t / 60.0),
        )
    )
    ol = innovation_model(a, b, c, d, k, ts)
    y, _ = simulate_system(ol, np.hstack((u, 0.03 * rng.standard_normal((n_samples, 2)))), dt=ts)
    y = y + 0.08 * periodic @ np.array([[1.0, 0.5], [-0.3, 0.9]], dtype=np.float64)
    return u, y, ts, rpm


def run_case(case: str) -> None:
    u, y, ts, rpm = _load_or_synthesize(case)
    t = np.arange(u.shape[0], dtype=np.float64) * ts

    harm = np.column_stack(
        (
            np.sin(2.0 * np.pi * rpm * t / 60.0),
            np.cos(2.0 * np.pi * rpm * t / 60.0),
            np.sin(4.0 * np.pi * rpm * t / 60.0),
            np.cos(4.0 * np.pi * rpm * t / 60.0),
        )
    )
    u_aug = np.hstack((u, harm))

    n = 12
    f = 20
    p = 20

    _, a_plain, b_plain, c_plain, d_plain, _, _, _ = estimate_varx_abcdk(u, y, n, f, p)
    _, a_aug, b_aug, c_aug, d_aug, _, _, _ = estimate_varx_abcdk(u_aug, y, n, f, p)

    y_plain, _ = simulate_system(
        state_space_model(a_plain, b_plain, c_plain, d_plain, ts), u, dt=ts
    )
    y_aug, _ = simulate_system(
        state_space_model(a_aug, b_aug, c_aug, d_aug, ts), u_aug, dt=ts
    )

    print(f"\n[ex09-RPM-{int(rpm)}]")
    print(f"VAF plain (%): {np.array2string(vaf_percent(y, y_plain), precision=2)}")
    print(f"VAF periodic-aug (%): {np.array2string(vaf_percent(y, y_aug), precision=2)}")


def main() -> None:
    run_case("370")
    run_case("430")


if __name__ == "__main__":
    main()
