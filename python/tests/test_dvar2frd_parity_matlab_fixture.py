from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from pbsid.lti.dvar2frd import dvar2frd
from pbsid.parity_report_utils import write_parity_report

ATOL_G = 1e-12
RTOL_G = 1e-9
ATOL_COV = 1e-13
RTOL_COV = 1e-10

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "fixtures" / "matlab_reference" / "dvar2frd_fixture.mat"
)


def _max_abs_rel(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    diff = np.abs(a - b)
    denom = np.maximum(np.abs(b), 1e-12)
    return float(np.max(diff)), float(np.max(diff / denom))


def _assert_close(name: str, got: np.ndarray, ref: np.ndarray, atol: float, rtol: float) -> None:
    max_abs, max_rel = _max_abs_rel(got, ref)
    assert np.allclose(got, ref, atol=atol, rtol=rtol), (
        f"{name} mismatch: max_abs={max_abs:.3e}, max_rel={max_rel:.3e}, "
        f"shape_got={got.shape}, shape_ref={ref.shape}"
    )


def _load_case_count(m: dict[str, np.ndarray], generator_name: str) -> int:
    n_cases = int(np.asarray(m.get("n_cases", [[1]])).item())
    if n_cases < 3:
        pytest.skip(
            f"Fixture has fewer than 3 cases. Regenerate with: testutils.{generator_name}"
        )
    return n_cases


@pytest.mark.parity
def test_dvar2frd_parity_varx_fixture() -> None:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "Missing MATLAB fixture. Generate with: testutils.generateDvar2frdFixture in MATLAB."
        )

    m = loadmat(FIXTURE_PATH, squeeze_me=False, struct_as_record=False)
    n_cases = _load_case_count(m, "generateDvar2frdFixture")
    rows: list[dict[str, str | float | int | bool]] = []

    for i in range(n_cases):
        case_label = f"case_{i + 1}"
        p_cov = np.asarray(m["P_varx_cases"][..., i], dtype=np.float64)
        w = np.asarray(m["w_varx_cases"][..., i], dtype=np.float64).reshape(-1)
        h = float(np.asarray(m["h_varx_cases"][..., i]).item())
        p = int(np.asarray(m["p_varx_cases"][..., i]).item())
        varx = np.asarray(m["VARX_cases"][..., i], dtype=np.float64)

        g_py, cov_g_py = dvar2frd(p_cov, w, h, p, varx)
        g_ref = np.asarray(m["G_varx_cases"][..., i], dtype=np.complex128)
        cov_g_ref = np.asarray(m["covG_varx_cases"][..., i], dtype=np.float64)

        max_abs_g, max_rel_g = _max_abs_rel(g_py, g_ref)
        g_ok = np.allclose(g_py, g_ref, atol=ATOL_G, rtol=RTOL_G)
        rows.append(
            {
                "function": "dvar2frd",
                "case": case_label,
                "metric": "G_varx",
                "max_abs": max_abs_g,
                "max_rel": max_rel_g,
                "atol": ATOL_G,
                "rtol": RTOL_G,
                "pass": bool(g_ok),
            }
        )
        _assert_close(f"G_varx_{case_label}", g_py, g_ref, atol=ATOL_G, rtol=RTOL_G)

        max_abs_cov, max_rel_cov = _max_abs_rel(cov_g_py, cov_g_ref)
        cov_ok = np.allclose(cov_g_py, cov_g_ref, atol=ATOL_COV, rtol=RTOL_COV)
        rows.append(
            {
                "function": "dvar2frd",
                "case": case_label,
                "metric": "covG_varx",
                "max_abs": max_abs_cov,
                "max_rel": max_rel_cov,
                "atol": ATOL_COV,
                "rtol": RTOL_COV,
                "pass": bool(cov_ok),
            }
        )
        _assert_close(f"covG_varx_{case_label}", cov_g_py, cov_g_ref, atol=ATOL_COV, rtol=RTOL_COV)

    write_parity_report("dvar2frd_varx_parity_report", rows)


@pytest.mark.parity
def test_dvar2frd_parity_abck_fixture() -> None:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "Missing MATLAB fixture. Generate with: testutils.generateDvar2frdFixture in MATLAB."
        )

    m = loadmat(FIXTURE_PATH, squeeze_me=False, struct_as_record=False)
    required = {
        "P_abck_cases",
        "A_abck_cases",
        "B_abck_cases",
        "C_abck_cases",
        "K_abck_cases",
        "G_abck_cases",
        "covG_abck_cases",
    }
    if not required.issubset(set(m.keys())):
        pytest.skip(
            "Fixture missing ABCK fields. Regenerate with: testutils.generateDvar2frdFixture"
        )

    n_cases = _load_case_count(m, "generateDvar2frdFixture")
    rows: list[dict[str, str | float | int | bool]] = []

    for i in range(n_cases):
        case_label = f"case_{i + 1}"
        p_cov = np.asarray(m["P_abck_cases"][..., i], dtype=np.float64)
        w = np.asarray(m["w_abck_cases"][..., i], dtype=np.float64).reshape(-1)
        h = float(np.asarray(m["h_abck_cases"][..., i]).item())
        a = np.asarray(m["A_abck_cases"][..., i], dtype=np.float64)
        b = np.asarray(m["B_abck_cases"][..., i], dtype=np.float64)
        c = np.asarray(m["C_abck_cases"][..., i], dtype=np.float64)
        k = np.asarray(m["K_abck_cases"][..., i], dtype=np.float64)

        g_py, cov_g_py = dvar2frd(p_cov, w, h, a, b, c, k)
        g_ref = np.asarray(m["G_abck_cases"][..., i], dtype=np.complex128)
        cov_g_ref = np.asarray(m["covG_abck_cases"][..., i], dtype=np.float64)

        max_abs_g, max_rel_g = _max_abs_rel(g_py, g_ref)
        rows.append(
            {
                "function": "dvar2frd",
                "case": case_label,
                "metric": "G_abck",
                "max_abs": max_abs_g,
                "max_rel": max_rel_g,
                "atol": ATOL_G,
                "rtol": RTOL_G,
                "pass": bool(np.allclose(g_py, g_ref, atol=ATOL_G, rtol=RTOL_G)),
            }
        )
        _assert_close(f"G_abck_{case_label}", g_py, g_ref, atol=ATOL_G, rtol=RTOL_G)

        max_abs_cov, max_rel_cov = _max_abs_rel(cov_g_py, cov_g_ref)
        rows.append(
            {
                "function": "dvar2frd",
                "case": case_label,
                "metric": "covG_abck",
                "max_abs": max_abs_cov,
                "max_rel": max_rel_cov,
                "atol": ATOL_COV,
                "rtol": RTOL_COV,
                "pass": bool(
                    np.allclose(cov_g_py, cov_g_ref, atol=ATOL_COV, rtol=RTOL_COV)
                ),
            }
        )
        _assert_close(
            f"covG_abck_{case_label}", cov_g_py, cov_g_ref, atol=ATOL_COV, rtol=RTOL_COV
        )

    write_parity_report("dvar2frd_abck_parity_report", rows)


@pytest.mark.parity
def test_dvar2frd_parity_abcdk_fixture() -> None:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "Missing MATLAB fixture. Generate with: testutils.generateDvar2frdFixture in MATLAB."
        )

    m = loadmat(FIXTURE_PATH, squeeze_me=False, struct_as_record=False)
    required = {
        "P_abcdk_cases",
        "A_abcdk_cases",
        "B_abcdk_cases",
        "C_abcdk_cases",
        "D_abcdk_cases",
        "K_abcdk_cases",
        "G_abcdk_cases",
        "covG_abcdk_cases",
    }
    if not required.issubset(set(m.keys())):
        pytest.skip(
            "Fixture missing ABCDK fields. Regenerate with: testutils.generateDvar2frdFixture"
        )

    n_cases = _load_case_count(m, "generateDvar2frdFixture")
    rows: list[dict[str, str | float | int | bool]] = []

    for i in range(n_cases):
        case_label = f"case_{i + 1}"
        p_cov = np.asarray(m["P_abcdk_cases"][..., i], dtype=np.float64)
        w = np.asarray(m["w_abcdk_cases"][..., i], dtype=np.float64).reshape(-1)
        h = float(np.asarray(m["h_abcdk_cases"][..., i]).item())
        a = np.asarray(m["A_abcdk_cases"][..., i], dtype=np.float64)
        b = np.asarray(m["B_abcdk_cases"][..., i], dtype=np.float64)
        c = np.asarray(m["C_abcdk_cases"][..., i], dtype=np.float64)
        d = np.asarray(m["D_abcdk_cases"][..., i], dtype=np.float64)
        k = np.asarray(m["K_abcdk_cases"][..., i], dtype=np.float64)

        g_py, cov_g_py = dvar2frd(p_cov, w, h, a, b, c, d, k)
        g_ref = np.asarray(m["G_abcdk_cases"][..., i], dtype=np.complex128)
        cov_g_ref = np.asarray(m["covG_abcdk_cases"][..., i], dtype=np.float64)

        max_abs_g, max_rel_g = _max_abs_rel(g_py, g_ref)
        rows.append(
            {
                "function": "dvar2frd",
                "case": case_label,
                "metric": "G_abcdk",
                "max_abs": max_abs_g,
                "max_rel": max_rel_g,
                "atol": ATOL_G,
                "rtol": RTOL_G,
                "pass": bool(np.allclose(g_py, g_ref, atol=ATOL_G, rtol=RTOL_G)),
            }
        )
        _assert_close(f"G_abcdk_{case_label}", g_py, g_ref, atol=ATOL_G, rtol=RTOL_G)

        max_abs_cov, max_rel_cov = _max_abs_rel(cov_g_py, cov_g_ref)
        rows.append(
            {
                "function": "dvar2frd",
                "case": case_label,
                "metric": "covG_abcdk",
                "max_abs": max_abs_cov,
                "max_rel": max_rel_cov,
                "atol": ATOL_COV,
                "rtol": RTOL_COV,
                "pass": bool(
                    np.allclose(cov_g_py, cov_g_ref, atol=ATOL_COV, rtol=RTOL_COV)
                ),
            }
        )
        _assert_close(
            f"covG_abcdk_{case_label}", cov_g_py, cov_g_ref, atol=ATOL_COV, rtol=RTOL_COV
        )

    write_parity_report("dvar2frd_abcdk_parity_report", rows)
