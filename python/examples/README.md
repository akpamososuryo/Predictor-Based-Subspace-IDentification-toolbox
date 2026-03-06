# Python Examples

This folder contains Python scripts and notebooks that mirror the MATLAB workflows in
`../examples/`.

## LTI examples

The `lti/` subfolder maps directly to MATLAB files:
- `ex01_lti_four.py`
- `ex02_lti_four_fir.py`
- `ex03_lti_duct.py`
- `ex04_lti_wts.py`
- `ex05_lti_wts_batch.py`
- `ex06_lti_four_unc.py`
- `ex07_lti_wts_mcs.py`
- `ex08_lti_wts_bootstrap.py`
- `ex09_lti_plus_periodic_rotor.py`

Each script also has a notebook counterpart with MATLAB-style section comments:
- `ex01_lti_four.ipynb`
- `ex02_lti_four_fir.ipynb`
- `ex03_lti_duct.ipynb`
- `ex04_lti_wts.ipynb`
- `ex05_lti_wts_batch.ipynb`
- `ex06_lti_four_unc.ipynb`
- `ex07_lti_wts_mcs.ipynb`
- `ex08_lti_wts_bootstrap.ipynb`
- `ex09_lti_plus_periodic_rotor.ipynb`

## Example Porting Notes

- Prefer direct `control.matlab` calls in control-oriented example code whenever practical so the
	Python flow stays close to the MATLAB `ss` / `feedback` / `lsim` style.
- Use direct `control` calls only when the matlab-style API is not a practical fit for the example.
- When a MATLAB utility exists as its own file, port it into its own Python file as well instead of
	placing the implementation inside `_common.py` or another shared helper.
- Treat `_common.py` as example glue only; direct MATLAB function ports should remain individually
	importable modules.
- Use helper functions only when they remain thin mappings onto `control.matlab` behavior instead of
	adding an extra abstraction layer.
- When validating an example port, compare it against both the MATLAB source in `../examples/*.m`
	and the published MATLAB output pages in `../examples/html/*.html`.
- Use the HTML pages to compare printed metrics and the key figures shown there, especially singular
	values, pole plots, and Bode or frequency-response plots.
- For unseeded MATLAB example runs, use the HTML outputs as a structural reference; exact numeric
	agreement in printed SNR / VAF values is not expected unless the input data are matched.

## Running

From `python/`:

```powershell
python examples/lti/ex01_lti_four.py
python examples/lti/ex02_lti_four_fir.py
python examples/lti/ex03_lti_duct.py
```

In VS Code, open any notebook in `python/examples/lti/*.ipynb` and run cells with the
selected Python kernel.

Each script prints identification metrics (SNR, VAF, poles, and uncertainty dimensions).
Some MATLAB-specific parts (for example `pem` and specific Simulink models) are replaced with a
Python-port equivalent demonstration using the currently implemented `pbsid.lti` API.

On this Windows setup, `conda run -n pbsid-py ...` is the more reliable way to run example
validation commands when `control` / `control.matlab` is involved.
