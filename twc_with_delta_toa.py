import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy import optimize as opt

def draw_toa_code(ax, input_data, board_number):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist(data['toa_code'], bins=800, range=[0,800])
    plt.title('Board ' + str(board_number) + ': ToA codes')
    plt.xlabel('ToA codes')
    plt.ylabel('Counts')


def draw_tot_code(ax, input_data, board_number):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist(data['tot_code'], bins=300, range=[0,300])
    plt.title('Board ' + str(board_number) + ': ToT codes')
    plt.xlabel('ToT codes')
    plt.ylabel('Counts')


def draw_cal_code(ax, read_raw_cal, board_number):
    plt.sca(ax)
    data = read_raw_cal.loc[read_raw_cal['board'] == board_number]
    plt.hist(data['cal_code'], bins=40, range=[140,180])
    plt.title('Board ' + str(board_number) + ': cal codes')
    plt.xlabel('cal codes')
    plt.ylabel('Counts')


def draw_tot_toa_code(ax, input_data, board_number):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist2d(data['tot_code'], data['toa_code'], cmap=plt.cm.jet, bins=[300,300], range=[[0,300],[0,300]], cmin=1)
    plt.colorbar()
    plt.title('Board ' + str(board_number) + ': ToT vs ToA codes')
    plt.xlabel('ToT codes')
    plt.ylabel('ToA codes')


def draw_toa(ax, input_data, board_number, bTdc=False):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist(data['toa'], bins=125, range=[0,12.5])
    plt.title('Board ' + str(board_number) + ': ToA')
    plt.xlabel('ToA (ns)')
    plt.ylabel('Counts')


def draw_tot(ax, input_data, board_number,bTdc=False):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist(data['tot'], bins=200, range=[0,20])
    plt.title('Board ' + str(board_number) + ': ToT')
    plt.xlabel('ToT (ns)')
    plt.ylabel('Counts')


def draw_tot_toa(ax, input_data, board_number, bTdc=False):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist2d(data['tot'], data['toa'], cmap=plt.cm.jet, bins=[200,125], range=[[0,20],[0,12.5]], cmin=1)
    plt.colorbar()
    plt.title('Board ' + str(board_number) + ': ToT vs ToA')
    plt.xlabel('ToT (ns)')
    plt.ylabel('ToA (ns)')


# draw properties of a board
def draw_board(input_data, read_raw_cal):
    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    fig, ax = plt.subplots(4,3, constrained_layout=True, figsize=(1600*px, 1600*px))
    
    board_number = 0
    draw_tot_toa_code(ax[0,0], input_data,board_number)
    draw_toa_code(ax[0,1], input_data,board_number)
    draw_tot_code(ax[0,2], input_data,board_number)
    
    board_number = 1
    draw_tot_toa_code(ax[1,0], input_data,board_number)
    draw_toa_code(ax[1,1], input_data,board_number)
    draw_tot_code(ax[1,2], input_data,board_number)

    board_number = 3
    draw_tot_toa_code(ax[2,0], input_data,board_number)
    draw_toa_code(ax[2,1], input_data,board_number)
    draw_tot_code(ax[2,2], input_data,board_number)
    
    plt.savefig('plots/board'+ str(board_number) + '_properties.pdf')
    #plt.show()


def func(x, a, b, c):
    return a + b*x + c*x**2


def main():
    file_name = '2021-05-24_Array_Test_Results_B1P9_F11P9_B2P9_Beam_0524_F11HV210'
    
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

