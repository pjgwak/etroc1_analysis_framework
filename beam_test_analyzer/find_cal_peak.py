import os
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
pd.options.mode.chained_assignment = None
from matplotlib.backends.backend_pdf import PdfPages
from optparse import OptionParser
from scipy import optimize as opt
parser = OptionParser()
parser.add_option('--pdf', action='store_true', default=False, dest='PDF')
parser.add_option('--argmax', action='store_true', default=False, dest='ARGMAX')
parser.add_option('--zoom', help='range to zoom in', dest='ZOOM')
(options, args) = parser.parse_args()

def gaussianFit(delta_toa, board_number, plot_dir, twc=False):
    def gauss(x, a, x0, sigma):
        return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))
    bins, edges = np.histogram(delta_toa.values, 10, density=False)
    centers = edges[:-1] + np.diff(edges) / 2
    par, _ = opt.curve_fit(gauss, centers, bins)

    fig, ax = plt.subplots(constrained_layout=True, figsize=(8, 6))
    fit_y = gauss(centers, *par)
    ax.plot(centers, bins, 'r*', label='data')
    ax.plot(centers, fit_y, 'r--', label='fit: mean=%.3f, sigma=%.3f' % (par[1], abs(par[2])))

    
def hist1d(ax, input_data, board_number, variable='toa_code', num_bins=100, range_hist=(0,100), title='', xtitle='', ytitle='', logy=False):
    if ax is not None:
        plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    ax.hist(data[variable], bins=num_bins, range=range_hist)
    ax.set_title(title)
    ax.set_xlabel(xtitle, fontsize=13)
    ax.set_ylabel(ytitle, fontsize=13)
    ax.legend(['Number of events: %d'%(data[variable].shape[0])])
    if logy:
        ax.set_yscale('log')
    if options.ZOOM:
        ax.set_xlim(int(options.ZOOM)-10, int(options.ZOOM)+10)
        ax.set_xticks(np.arange(int(options.ZOOM)-10, int(options.ZOOM)+10, 1))
        ax.grid(axis='x')

def drawPlots(board_number, raw_data, plot_dir):
    fig, ax = plt.subplots(constrained_layout=True, figsize=(12, 8))
    hist1d(ax, raw_data, board_number, 'cal_code', 100, (0,200), 'Board '+str(board_number), 'CAL code', 'Number of hits', logy=True)
    
    if options.ZOOM:
        plt.savefig(plot_dir + '/board'+ str(board_number) + '_rawCALcode_zoom.png')
    else:
        plt.savefig(plot_dir + '/board'+ str(board_number) + '_rawCALcode.png')
    
    if options.PDF:
        outfile = plot_dir + '/board'+ str(board_number) + '_rawCALcode.pdf'
        plt.savefig(outfile)

def printArgMax(board_number, input_data):
    data = input_data.loc[input_data['board'] == board_number]
    bins, _ = np.histogram(data['cal_code'], bins=100, range=(100,200))
    print('Board '+str(board_number)+' : '+str(np.argmax(bins)))


def main():
    with open('config.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    dir_path = conf['dir_path']
    file_name = conf['file_name']
    plot_dir = dir_path + '/' + file_name + '_plot'
    sub_file_dir = dir_path + '/' + file_name + '_sub_file'
    try:
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
    except OSError:
        print('Error: Cannot creat plot directory')

    try:
        if not os.path.exists(sub_file_dir):
            os.makedirs(sub_file_dir)
    except OSError:
        print('Error: Cannot creat sub file directory')

    raw_data = pd.read_csv(dir_path + '/' + file_name + '.txt', delimiter = '\s+', header=None, skiprows=1)
    raw_data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'flag', 'dummy1', 'dummy2']
    raw_data = raw_data.drop(['toa_code', 'tot_code', 'flag', 'dummy1', 'dummy2'], axis=1)
    print("Read data: Done")
    
    
    cal_cuts = [145, 150, 145, 149, 139, 144]
    b0_data = raw_data.loc[raw_data['board']==0]
    b1_data = raw_data.loc[raw_data['board']==1]
    b3_data = raw_data.loc[raw_data['board']==3]
    
    b0_data['bCut'] = (b0_data['cal_code'] >= cal_cuts[0]) & (b0_data['cal_code'] <= cal_cuts[1])
    b1_data['bCut'] = (b1_data['cal_code'] >= cal_cuts[2]) & (b1_data['cal_code'] <= cal_cuts[3])
    b3_data['bCut'] = (b3_data['cal_code'] >= cal_cuts[4]) & (b3_data['cal_code'] <= cal_cuts[5])
    #print(b3_data)
    #exit(1)
    #print('Mean with noise: ', b0_data['cal_code'].mean())
    print('B0\'s mean w/o noise: ', b0_data['cal_code'].loc[b0_data['bCut']==True].mean())
    print('B1\'s mean w/o noise: ', b1_data['cal_code'].loc[b1_data['bCut']==True].mean())
    print('B3\'s mean w/o noise: ', b3_data['cal_code'].loc[b3_data['bCut']==True].mean())
    
    
    #def gauss(x, a, x0, sigma):
    #    return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))
    #
    #bins, edges = np.histogram(b0_data['cal_code'].loc[b0_data['bCut']==True].values, 12, density=False)
    ##bins, edges = np.histogram(b1_data['cal_code'].values, 1000, density=False)
    #centers = edges[:-1] + np.diff(edges) / 2
    #par, _ = opt.curve_fit(gauss, centers, bins, maxfev=50000)
    #print('Fit parameters: ', par)
    #
    #plt.plot(centers, bins, 'bo', label='data')
    #fit_y = gauss(centers, *par)
    #plt.plot(centers, fit_y, 'r--', label='fit: mean=%.3f, sigma=%.3f' % (par[1], abs(par[2])))
    #plt.show()
        
    #for board_number, data in [(0,b0_data), (1,b1_data), (3,b3_data)]:
    #    drawPlots(board_number, data.loc[data['bCut']==True], plot_dir)
    #    if options.ARGMAX:
    #        printArgMax(board_number, raw_data)


if __name__ == '__main__':
    main()
