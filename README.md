# etroc1_analysis_framework

### Workflow
1. data_selection.py
- Read experimental data and select good event (hit flag 1 and board numbers are 0, 1, 3 sequentially)
- Chage a path for 'codes_data' variable.
- Change a 'file_name' variable. It is used for every codes below

2. draw_codes_distributions.py
- Draw distributionss of toa_codes, tot_codes and cal_code according to boards
- Result plot is saved into 'plots' folder (please make this folder or change a path for saving)
- Change a 'file_name' as the one of 'data_selection.py'
- You have to see the plot and decide proper cut ranges by yourself

3. twc_with_delta_toa.py
- Get toa with TWC (Time Work Correction) from delta_toa
- Change a 'file_name' as the one of 'data_selection.py'
- Fill out b0_cuts, b1_cuts and b3_cuts with cuts from 'draw_codes_distributions.py'

4. time_resolution.py
- Calculate time resolutions of boards
- Change a 'file_name' as the one of 'data_selection.py'
- You can see the delta_toa gauss distribution by running the code with '--ploting' option
- Ex) python time_resolution.py --plotting
