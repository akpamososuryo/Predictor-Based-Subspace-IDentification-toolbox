from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from pbsid.lti.dmodx import dmodx
from pbsid.parity_report_utils import write_parity_report

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "matlab_reference"
    / "dmodx_fixture.mat"
)


def _cell_entry(cell: np.ndarray, index: int) -> np.ndarray:
    return np.asarray(cell[0, index], dtype=np.float64)


def _max_abs_rel(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    diff = np.abs(a - b)
    denom = np.maximum(np.abs(b), 1e-12)
    return float(np.max(diff)), float(np.max(diff / denom))


def _record_metric(
    *,
    rows: list[dict[str, str | float | int | bool]],
    case: str,
    metric: str,
    got: np.ndarray,
    ref: np.ndarray,
    atol: float,
    rtol: float,
) -> None:
    max_abs, max_rel = _max_abs_rel(got, ref)
    ok = np.allclose(got, ref, atol=atol, rtol=rtol)
    rows.append(
        {
            "function": "dmodx",
            "case": case,
            "metric": metric,
            "max_abs": max_abs,
            "max_rel": max_rel,
            "atol": atol,
            "rtol": rtol,
            "pass": bool(ok),
        }
    )
    assert ok, (
        f"{metric}_{case} mismatch: max_abs={max_abs:.3e}, max_rel={max_rel:.3e}, "
        f"shape_got={got.shape}, shape_ref={ref.shape}"
    )


@pytest.mark.parity
def test_dmodx_parity_single_and_batch_fixture() -> None:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "Missing MATLAB fixture. Generate with: testutils.generateDmodxFixture in MATLAB."
        )

    m = loadmat(FIXTURE_PATH, squeeze_me=False, struct_as_record=False)
    n_cases = int(np.asarray(m.get("n_cases", [[1]])).item())
    if n_cases < 3:
        pytest.skip(
            "Fixture has fewer than 3 cases. Regenerate with: testutils.generateDmodxFixture"
        )

    rows: list[dict[str, str | float | int | bool]] = []

    for i in range(n_cases):
        case_label = f"c{i + 1}"

        x_single = np.asarray(m[f"X_single_{case_label}"], dtype=np.float64)
        n_single = int(np.asarray(m[f"n_single_{case_label}"]).item())
        ref_single = np.asarray(m[f"X_single_out_{case_label}"], dtype=np.float64)

        got_single = dmodx(x_single, n_single)
        assert not isinstance(got_single, list)
        _record_metric(
            rows=rows,
            case=f"single_{case_label}",
            metric="X",
            got=got_single,
            ref=ref_single,
            atol=1e-12,
            rtol=1e-10,
        )

        x_batch_cell = np.asarray(m[f"X_batch_{case_label}"])
        n_batch = int(np.asarray(m[f"n_batch_{case_label}"]).item())
        ref_batch_cell = np.asarray(m[f"X_batch_out_{case_label}"])

        x_batch = [_cell_entry(x_batch_cell, 0), _cell_entry(x_batch_cell, 1)]
        got_batch = dmodx(x_batch, n_batch)
        assert isinstance(got_batch, list)

        ref_1 = _cell_entry(ref_batch_cell, 0)
        ref_2 = _cell_entry(ref_batch_cell, 1)
        _record_metric(
            rows=rows,
            case=f"batch1_{case_label}",
            metric="X",
            got=got_batch[0],
            ref=ref_1,
            atol=1e-12,
            rtol=1e-10,
        )
        _record_metric(
            rows=rows,
            case=f"batch2_{case_label}",
            metric="X",
            got=got_batch[1],
            ref=ref_2,
            atol=1e-12,
            rtol=1e-10,
        )

    write_parity_report("dmodx_parity_report", rows)