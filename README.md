# etroc1_analysis_framework

### Workflow
1. data_selection.py
- Read experimental data and select good event (hit flag 1 and board numbers are 0, 1, 3 sequentially)
- Command: `python data_selection.py`
- If you want to print data frame, add `--p` option behind the command.

2. draw_codes_distributions.py
- Draw raw data distributions e.g. ToA, ToT, CAL codes etc...
- Command: `python draw_codes_distributions.py`
- If you also want to save as pdf format, add `--pdf` option behind the command.

3. twc_with_delta_toa.py
- Get toa with TWC (Time Work Correction) from delta_toa
- Command: `python twc_with_delta_toa.py --code or --time`
- If you also want to save as pdf format, add `--pdf` option behind the command.

4. time_resolution.py
- Calculate time resolutions of boards
- Command: `python time_resolution.py`
