import yaml
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy import optimize as opt


def quad_func(x, a, b, c):
    return a*x**2 + b*x + c


def draw_delta_toa_fit(board_number, input_data, popt, ax=None):
    if ax is not None:
        plt.sca(ax)
    plt.plot(input_data['tot'].values, quad_func(input_data['tot'].values, *popt), 'g--', label='fit: a=%5.3f, b=%5.3f, c=%5.10f' % tuple(popt))
    plt.hist2d(input_data['tot'], input_data['delta_toa'], bins=[100,100], cmap=plt.cm.jet, cmin=1)
    plt.title('Board ' + str(board_number) + ': ToT vs delta ToA w/o TWC')
    plt.xlabel('ToT')
    plt.ylabel('delta ToA w/o TWC')
    plt.colorbar()
    plt.legend()
    #plt.show()


def draw_delta_corr_toa_fit(board_number, input_data, popt, ax=None):
    if ax is not None:
        plt.sca(ax)
    plt.plot(input_data['tot'].values, quad_func(input_data['tot'].values, *popt), 'g--', label='fit: a=%5.3f, b=%5.3f, c=%5.10f' % tuple(popt))
    plt.hist2d(input_data['tot'], input_data['delta_corr_toa'], bins=[100,100], cmap=plt.cm.jet, cmin=1)
    plt.title('Board ' + str(board_number) + ': ToT vs delta ToA w/ TWC')
    plt.xlabel('ToT')
    plt.ylabel('delta ToA w/ TWC')
    plt.colorbar()
    plt.legend()
    #plt.show()
    

def draw_toa(ax, input_data, board_number):
    plt.sca(ax)
    plt.hist(input_data['toa'], bins=125, range=[0,12.5])
    plt.title('Board ' + str(board_number) + ': ToA w/ TWC')
    plt.xlabel('ToA (ns)')
    plt.ylabel('Counts')


def draw_tot(ax, input_data, board_number,bTdc=False):
    plt.sca(ax)
    plt.hist(input_data['tot'], bins=200, range=[0,20])
    plt.title('Board ' + str(board_number) + ': ToT w/ TWC')
    plt.xlabel('ToT (ns)')
    plt.ylabel('Counts')


def draw_tot_toa(ax, input_data, board_number):
    plt.sca(ax)
    plt.hist2d(input_data['tot'], input_data['toa'], cmap=plt.cm.jet, bins=[200,125], range=[[0,20],[0,12.5]], cmin=1)
    plt.colorbar()
    plt.title('Board ' + str(board_number) + ': ToT vs ToA w/ TWC')
    plt.xlabel('ToT (ns)')
    plt.ylabel('ToA (ns)')


def draw_board(board_number, input_data, popt, corr_popt, plot_dir):
    bDraw = False
    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    fig, ax = plt.subplots(2,3, constrained_layout=True, figsize=(1200*px, 600*px))
    
    draw_delta_toa_fit(board_number, input_data,popt, ax[0,0])
    draw_delta_corr_toa_fit(board_number, input_data,corr_popt, ax[0,1])
    
    draw_tot_toa(ax[1,0], input_data,board_number)
    draw_toa(ax[1,1], input_data,board_number)
    draw_tot(ax[1,2], input_data,board_number)

    plt.savefig(plot_dir + '/board'+ str(board_number) + '_plot2.png')
    
    


def main():
    with open('config.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    dir_path = conf['dir_path']
    file_name = conf['file_name']
    plot_dir = dir_path + '/' + file_name + '_plot'
    sub_file_dir = dir_path + '/' + file_name + '_sub_file'
    
    read_data = pd.read_csv(sub_file_dir+'/'+file_name+'.txt', delimiter = '\s+', header=None)
    read_data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'toa',    'tot']
    read_raw_cal = pd.read_csv(sub_file_dir+'/'+file_name+'_cal_codes.txt', delimiter = '\s+', header=None)
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
    b0_cuts = [150, 300, 40, 70, 120, 140]
    b1_cuts = [150, 300, 50, 80, 120, 140]
    b3_cuts = [150, 300, 60, 80, 120, 140]
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
    
    
    popt0, _ = opt.curve_fit(quad_func, b0_twc_delta_data['tot'].values, b0_twc_delta_data['delta_toa'].values)
    popt1, _ = opt.curve_fit(quad_func, b1_twc_delta_data['tot'].values, b1_twc_delta_data['delta_toa'].values)
    popt3, _ = opt.curve_fit(quad_func, b3_twc_delta_data['tot'].values, b3_twc_delta_data['delta_toa'].values)
    #draw_delta_toa_fit(b0_twc_delta_data, popt0)
    
    # Calculate toa w/ TWC
    #x-axis ToT
    #y-axis B1 TOA: (b0_toa + b3_toa)/2 - b1_toa
    b0_twc_delta_data['corr_toa'] = b0_twc_delta_data['toa'] + quad_func(b0_twc_delta_data['tot'].values, *popt0)
    b1_twc_delta_data['corr_toa'] = b1_twc_delta_data['toa'] + quad_func(b1_twc_delta_data['tot'].values, *popt1)
    b3_twc_delta_data['corr_toa'] = b3_twc_delta_data['toa'] + quad_func(b3_twc_delta_data['tot'].values, *popt3)
    
    #print(b0_twc_delta_data)
    #print(b1_twc_delta_data)
    #print(b3_twc_delta_data)
    b0_twc_delta_data.to_csv(sub_file_dir+'/'+file_name+'_b0_corr.txt', sep='\t', index=None, header=None)
    b1_twc_delta_data.to_csv(sub_file_dir+'/'+file_name+'_b1_corr.txt', sep='\t', index=None, header=None)
    b3_twc_delta_data.to_csv(sub_file_dir+'/'+file_name+'_b3_corr.txt', sep='\t', index=None, header=None)


    # To draw delta ToA with corrected ToA.
    # Don't need to save.
    b0_twc_delta_data['delta_corr_toa'] = (b1_twc_delta_data['corr_toa'] + b3_twc_delta_data['corr_toa'])*0.5 - b0_twc_delta_data['corr_toa']
    b1_twc_delta_data['delta_corr_toa'] = (b0_twc_delta_data['corr_toa'] + b3_twc_delta_data['corr_toa'])*0.5 - b1_twc_delta_data['corr_toa']
    b3_twc_delta_data['delta_corr_toa'] = (b0_twc_delta_data['corr_toa'] + b1_twc_delta_data['corr_toa'])*0.5 - b3_twc_delta_data['corr_toa']
    
    corr_popt0, _ = opt.curve_fit(quad_func, b0_twc_delta_data['tot'].values, b0_twc_delta_data['delta_corr_toa'].values)
    corr_popt1, _ = opt.curve_fit(quad_func, b1_twc_delta_data['tot'].values, b1_twc_delta_data['delta_corr_toa'].values)
    corr_popt3, _ = opt.curve_fit(quad_func, b3_twc_delta_data['tot'].values, b3_twc_delta_data['delta_corr_toa'].values)
    
    
    # Draw plots
    draw_board(0, b0_twc_delta_data, popt0, corr_popt0, plot_dir)
    draw_board(1, b1_twc_delta_data, popt1, corr_popt1, plot_dir)
    draw_board(3, b3_twc_delta_data, popt3, corr_popt3, plot_dir)
    
    
    

if __name__ == '__main__':
    main()



#fit_y = gauss(centers, norm, mean, sigma)
#plt.plot(centers, contents, 'o', label='data')
#plt.plot(centers, fit_y, '-', label='fit')
#plt.title('Board ' + str(board_number) + ': delta_ToAs')
#plt.xlabel('delta ToA (ns)')
#plt.ylabel('Counts')
#plt.legend()
#print('Board ', board_number, ': ', 'norm: ', norm, 'mean: ', mean, ', sigma: ', sigma)
#plt.show()
