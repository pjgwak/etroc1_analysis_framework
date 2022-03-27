import yaml
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize as opt
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--pdf', action='store_true', default=False, dest='PDF')
parser.add_option('--code', action='store_true', help='Select events by code cuts', default=False, dest='CODE')
parser.add_option('--time', action='store_true', help='Select events by time cuts', default=False, dest='TIME')
(options, args) = parser.parse_args()

if not any([options.CODE, options.TIME]):
    raise ValueError('Please specify which cut do you want to use --code or --time')

def quad_func(x, a, b, c):
    return a*x**2 + b*x + c

def hist1d(ax, data, variable='toa', num_bins=125, range_hist=[0,12.5], title='', xtitle='', ytitle='', logy=False):
    if ax is not None:
        plt.sca(ax)
    ax.hist(data[variable], bins=num_bins, range=range_hist)
    ax.set_title(title)
    ax.set_xlabel(xtitle, fontsize=13)
    ax.set_ylabel(ytitle, fontsize=13)
    ax.legend(['Number of events: %d'%(data[variable].shape[0])])
    if logy:
        ax.set_yscale('log')

def hist2d(ax, data, v1='tot', v2='toa', num_bins=[200,125], range_hist=[[0,20.0],[0,12.5]], title='', xtitle='', ytitle=''):
    if ax is not None:
        plt.sca(ax)
    plt.hist2d(data[v1], data[v2], cmap=plt.cm.jet, bins=num_bins, range=range_hist, cmin=1)
    plt.colorbar()
    ax.set_title(title)
    ax.set_xlabel(xtitle, fontsize=13)
    ax.set_ylabel(ytitle, fontsize=13)

def plotFit(ax, data, v1, v2, popt, title, xtitle, ytitle):
    if ax is not None:
        plt.sca(ax)
    ax.plot(data[v1].values, quad_func(data[v1].values, *popt), 'g--', label='fit: a=%.3f, b=%.3f, c=%.3f' % tuple(popt))
    plt.hist2d(data[v1], data[v2], bins=[100,100], cmap=plt.cm.jet, cmin=1)
    ax.set_title(title)
    ax.set_xlabel(xtitle, fontsize=13)
    ax.set_ylabel(ytitle, fontsize=13)
    plt.colorbar()
    ax.legend()

def draw_board(board_number, input_data, popt, corr_popt, plot_dir):
    bDraw = False
    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    fig, ax = plt.subplots(2,3, constrained_layout=True, figsize=(1200*px, 600*px))

    ax[0,0].text(0.5, 0.5, "Board "+str(board_number)+"\nTime Walk Correction plots", fontsize=18, horizontalalignment='center', verticalalignment='center')
    ax[0,0].axis('off')
    plotFit(ax[0,1], input_data, 'tot', 'delta_toa', popt, '', 'ToT (ns)', r'$\Delta$ ToA w/o TWC')
    plotFit(ax[0,2], input_data, 'tot', 'delta_corr_toa', corr_popt, '', 'ToT (ns)', r'$\Delta$ ToA w/ TWC')

    hist1d(ax[1,0], input_data, 'toa', 125, [0, 12.5], '', 'ToA (ns)', 'Number of events')
    hist1d(ax[1,1], input_data, 'tot', 200, [0, 20.0], '', 'ToT (ns)', 'Number of events')
    hist2d(ax[1,2], input_data, 'tot', 'toa', [200,125], [[0,20.0],[0,12.5]], '', 'ToT (ns)', 'ToA (ns)')

    extraArg = ''
    if options.CODE:
        extraArg = 'byCode'
    elif options.TIME:
        extraArg = 'byTime'

    plt.savefig(plot_dir + '/board'+str(board_number)+'_'+extraArg+ '_TimeWalkCorrection.png')
    if options.PDF:
        outfile = plot_dir + '/board'+str(board_number)+'_'+extraArg+ '_TimeWalkCorrection.pdf'
        plt.savefig(outfile)

def main():
    with open('config.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    dir_path = conf['dir_path']
    file_name = conf['file_name']
    plot_dir = dir_path + '/' + file_name + '_plot'
    sub_file_dir = dir_path + '/' + file_name + '_sub_file'

    read_data = pd.read_csv(sub_file_dir+'/'+file_name+'.txt', delimiter = '\s+', header=None)
    read_data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'toa', 'tot']
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
    b0v, _ = np.histogram(b0_data['tot_code'], bins=300, range=(0,300))
    b1v, _ = np.histogram(b1_data['tot_code'], bins=300, range=(0,300))
    b3v, _ = np.histogram(b3_data['tot_code'], bins=300, range=(0,300))
    #print(np.argmax(b0v), np.argmax(b1v), np.argmax(b3v))
    b0_cuts = [100, 250, np.argmax(b0v)-22, np.argmax(b0v)+22, 120, 140]
    b1_cuts = [100, 250, np.argmax(b1v)-22, np.argmax(b1v)+22,120, 140]
    b3_cuts = [100, 250, np.argmax(b3v)-22, np.argmax(b3v)+22,120, 140]
    pd.options.mode.chained_assignment = None

    b0v, _ = np.histogram(b0_data['tot'], bins=200, range=(0,20))
    b1v, _ = np.histogram(b1_data['tot'], bins=200, range=(0,20))
    b3v, _ = np.histogram(b3_data['tot'], bins=200, range=(0,20))
    #print(np.argmax(b0v)*0.1, np.argmax(b1v)*0.1, np.argmax(b3v)*0.1)
    b0_tcuts = [7, 10, np.argmax(b0v)*0.1-1.5, np.argmax(b0v)*0.1+1.5, 120, 140]
    b1_tcuts = [7, 10, np.argmax(b1v)*0.1-1.5, np.argmax(b1v)*0.1+1.5, 120, 140]
    b3_tcuts = [7, 10, np.argmax(b3v)*0.1-1.5, np.argmax(b3v)*0.1+1.5, 120, 140]

    # Check toa, tot cut for events of each boards
    if options.CODE:
        print('============= Select events with code cuts =============')
        b0_data['bCut'] = (b0_data['toa_code'] > b0_cuts[0]) & (b0_data['toa_code'] < b0_cuts[1]) & (b0_data['tot_code'] > b0_cuts[2]) & (b0_data['tot_code'] < b0_cuts[3]) & (b0_data['cal_code'] > b0_cuts[4]) & (b0_data['cal_code'] < b0_cuts[5])
        b1_data['bCut'] = (b1_data['toa_code'] > b1_cuts[0]) & (b1_data['toa_code'] < b1_cuts[1]) & (b1_data['tot_code'] > b1_cuts[2]) & (b1_data['tot_code'] < b1_cuts[3]) & (b1_data['cal_code'] > b1_cuts[4]) & (b1_data['cal_code'] < b1_cuts[5])
        b3_data['bCut'] = (b3_data['toa_code'] > b3_cuts[0]) & (b3_data['toa_code'] < b3_cuts[1]) & (b3_data['tot_code'] > b3_cuts[2]) & (b3_data['tot_code'] < b3_cuts[3]) & (b3_data['cal_code'] > b3_cuts[4]) & (b3_data['cal_code'] < b3_cuts[5])
    elif options.TIME:
        print('============= Select events with time cuts =============')
        b0_data['bCut'] = (b0_data['toa'] > b0_tcuts[0]) & (b0_data['toa'] < b0_tcuts[1]) & (b0_data['tot'] > b0_tcuts[2]) & (b0_data['tot'] < b0_tcuts[3]) & (b0_data['cal_code'] > b0_tcuts[4]) & (b0_data['cal_code'] < b0_tcuts[5])
        b1_data['bCut'] = (b1_data['toa'] > b1_tcuts[0]) & (b1_data['toa'] < b1_tcuts[1]) & (b1_data['tot'] > b1_tcuts[2]) & (b1_data['tot'] < b1_tcuts[3]) & (b1_data['cal_code'] > b1_tcuts[4]) & (b1_data['cal_code'] < b1_tcuts[5])
        b3_data['bCut'] = (b3_data['toa'] > b3_tcuts[0]) & (b3_data['toa'] < b3_tcuts[1]) & (b3_data['tot'] > b3_tcuts[2]) & (b3_data['tot'] < b3_tcuts[3]) & (b3_data['cal_code'] > b3_tcuts[4]) & (b3_data['cal_code'] < b3_tcuts[5])

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
