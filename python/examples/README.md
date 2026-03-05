# Python Examples

This folder contains Python scripts that mirror the MATLAB workflows in `../examples/`.

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

## Running

From `python/`:

```powershell
python examples/lti/ex01_lti_four.py
python examples/lti/ex02_lti_four_fir.py
python examples/lti/ex03_lti_duct.py
```

Each script prints identification metrics (SNR, VAF, poles, and uncertainty dimensions).
Some MATLAB-specific parts (for example `pem` and specific Simulink models) are replaced with a
Python-port equivalent demonstration using the currently implemented `pbsid.lti` API.
