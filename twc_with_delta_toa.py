import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy import optimize as opt

def func(x, a, b, c):
    return a + b*x + c*x**2


def main():
    file_name = '2021-05-24_Array_Test_Results_B1P9_F11P9_B2P9_Beam_0524_F11HV220'
    
    read_data = pd.read_csv(file_name + '.txt', delimiter = '\s+', header=None)
    read_data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'toa',    'tot']
    read_raw_cal = pd.read_csv(file_name + '_cal_codes.txt', delimiter =    '\s+', header=None)
    read_raw_cal.columns = ['board', 'cal_code']
    print("Read data: Done")
    
    # Make array according to board
    b0_data = read_data.loc[read_data['board'] == 0]
    b0_data.reset_index(inplace=True, drop=True)
    b1_data = read_data.loc[read_data['board'] == 1]
    b1_data.reset_index(inplace=True, drop=True)
    b3_data = read_data.loc[read_data['board'] == 3]
    b3_data.reset_index(inplace=True,drop=True)

    # Make lists for cuts
    # toa_code lower, toa_code upper, tot_code lower, tot_code upper, cal_code lower
    # and cal_code upper limits
    b0_cuts = [150, 300, 55, 120, 100, 300]
    b1_cuts = [150, 300, 50, 100, 100, 300]
    b3_cuts = [150, 300, 70, 130, 100, 300]
    pd.options.mode.chained_assignment = None

    # Check toa, tot cut for events of each boards
    b0_data['bCut'] = (b0_data['toa_code'] > b0_cuts[0]) & (b0_data['toa_code'] < b0_cuts[1]) & (b0_data['tot_code'] > b0_cuts[2]) & (b0_data['tot_code'] < b0_cuts[3]) & (b0_data['cal_code'] > b0_cuts[4]) & (b0_data['cal_code'] < b0_cuts[5])
    b1_data['bCut'] = (b1_data['toa_code'] > b1_cuts[0]) & (b1_data['toa_code'] < b1_cuts[1]) & (b1_data['tot_code'] > b1_cuts[2]) & (b1_data['tot_code'] < b1_cuts[3]) & (b1_data['cal_code'] > b1_cuts[4]) & (b1_data['cal_code'] < b1_cuts[5])
    b3_data['bCut'] = (b3_data['toa_code'] > b3_cuts[0]) & (b3_data['toa_code'] < b3_cuts[1]) & (b3_data['tot_code'] > b3_cuts[2]) & (b3_data['tot_code'] < b3_cuts[3]) & (b3_data['cal_code'] > b3_cuts[4]) & (b3_data['cal_code'] < b3_cuts[5])

    
    # Find good twc events
    # Check event by event, all boards should pass their toa, tot cuts at the same time
    #b0_data['bDelta'] = b0_data['bCut']==True and b1_data['bCut']==True and b3_data['bCut']==True
    b0_data['bTwc'] = (b0_data['bCut']==True) & (b1_data['bCut']==True) & (b3_data['bCut']==True)
    b1_data['bTwc'] = (b0_data['bCut']==True) & (b1_data['bCut']==True) & (b3_data['bCut']==True)
    b3_data['bTwc'] = (b0_data['bCut']==True) & (b1_data['bCut']==True) & (b3_data['bCut']==True)

    #print(b1_data)
    #print(b3_data)
    
    b0_twc_delta_data = b0_data.loc[b0_data['bTwc'] == True][['toa','tot']]
    b1_twc_delta_data = b1_data.loc[b1_data['bTwc'] == True][['toa','tot']]
    b3_twc_delta_data = b3_data.loc[b3_data['bTwc'] == True][['toa','tot']]
    b0_twc_delta_data['delta_toa'] = (b1_twc_delta_data['toa'] + b3_twc_delta_data['toa'])*0.5 - b0_twc_delta_data['toa']
    b1_twc_delta_data['delta_toa'] = (b0_twc_delta_data['toa'] + b3_twc_delta_data['toa'])*0.5 - b1_twc_delta_data['toa']
    b3_twc_delta_data['delta_toa'] = (b0_twc_delta_data['toa'] + b1_twc_delta_data['toa'])*0.5 - b3_twc_delta_data['toa']
    
    #print(b0_twc_delta_data)
    #print(b1_twc_delta_data)
    #print(b3_twc_delta_data)
    
    
    popt1, _ = opt.curve_fit(func, b0_twc_delta_data['tot'].values, b0_twc_delta_data['delta_toa'].values)
    popt2, _ = opt.curve_fit(func, b1_twc_delta_data['tot'].values, b1_twc_delta_data['delta_toa'].values)
    popt3, _ = opt.curve_fit(func, b3_twc_delta_data['tot'].values, b3_twc_delta_data['delta_toa'].values)
    #plt.plot(b0_twc_delta_data['tot'].values, func(b0_twc_delta_data['tot'].values, *popt), 'g--', label='fit: a=%5.3f, b=%5.3f, c=%5.10f' % tuple(popt))
    #plt.hist2d(b0_twc_delta_data['tot'], b0_twc_delta_data['delta_toa'], cmin=1, bins=[500,500])
    #plt.xlabel('x')
    #plt.ylabel('y')
    #plt.legend()
    #plt.show()
    
    #b1
    #x-axis tot
    #y-axis (b0_toa + b3_toa)/2 - b1_toa
    
    b0_twc_delta_data['corr_toa'] = b0_twc_delta_data['toa'] + func(b0_twc_delta_data['tot'].values, *popt1)
    b1_twc_delta_data['corr_toa'] = b1_twc_delta_data['toa'] + func(b1_twc_delta_data['tot'].values, *popt2)
    b3_twc_delta_data['corr_toa'] = b3_twc_delta_data['toa'] + func(b3_twc_delta_data['tot'].values, *popt3)
    
    #print(b0_twc_delta_data)
    #print(b1_twc_delta_data)
    #print(b3_twc_delta_data)
    print(b3_twc_delta_data)
    b0_twc_delta_data.to_csv(file_name+'_b0_corr.txt', sep='\t', index=None, header=None)
    b1_twc_delta_data.to_csv(file_name+'_b1_corr.txt', sep='\t', index=None, header=None)
    b3_twc_delta_data.to_csv(file_name+'_b3_corr.txt', sep='\t', index=None, header=None)
    
    # TWC
    

if __name__ == '__main__':
    main()

