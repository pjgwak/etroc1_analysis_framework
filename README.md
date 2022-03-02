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
- Use --plot0 options to pop up distributions of board0 one by one. You can zoom in the plot to decide cut range
- --plot1 and --plot3 work same way like --plot0 for board 1 and 3 respectively
- To save summary plot add --plotSum option
- Ex) To check distirbution of board 0 and 3 and to save summary plot, you can use command below   
- python draw_codes_distributions.py --plot0 --plot3 --plotSum

3. twc_with_delta_toa.py
- Get toa with TWC (Time Work Correction) from delta_toa
- Change a 'file_name' as the one of 'data_selection.py'
- Fill out b0_cuts, b1_cuts and b3_cuts with cut ranges from 'draw_codes_distributions.py'

4. time_resolution.py
- Calculate time resolutions of boards
- Change a 'file_name' as the one of 'data_selection.py'
- You can see the delta_toa gauss distributions by running the code with '--plotting' option
- Ex) python time_resolution.py --plotting
