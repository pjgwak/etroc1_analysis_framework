import yaml
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--pdf', action='store_true', default=False, dest='PDF')
(options, args) = parser.parse_args()

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

def hist2d(ax, input_data, board_number, v1='tot_code', v2='toa_code', num_bins=[100,100], range_hist=[[0,300],[0,300]], title='', xtitle='', ytitle=''):
    if ax is not None:
        plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist2d(data[v1], data[v2], cmap=plt.cm.jet, bins=num_bins, range=range_hist, cmin=1)
    plt.colorbar()
    ax.set_title(title)
    ax.set_xlabel(xtitle, fontsize=13)
    ax.set_ylabel(ytitle, fontsize=13)

def drawPlots(board_number, read_data, plot_dir):
    fig, ax = plt.subplots(2,4, constrained_layout=True, figsize=(16, 9))

    ax[0,0].text(0.5, 0.5, "Board "+str(board_number)+"\nraw data plots", fontsize=20, horizontalalignment='center', verticalalignment='center')
    ax[0,0].axis('off')
    hist1d(ax[0,1], read_data, board_number, 'toa_code', 800, (0,800), '', 'TOA code', 'Number of events')
    hist1d(ax[0,2], read_data, board_number, 'tot_code', 300, (0,300), '', 'TOT code', '')
    hist2d(ax[0,3], read_data, board_number, 'tot_code', 'toa_code', 200, [[0,300],[0,800]], '', 'ToT code', 'ToA code')

    hist1d(ax[1,0], read_data, board_number, 'cal_code', 1000, (0,1000), '', 'CAL code', 'Number of events', logy=True)
    hist1d(ax[1,1], read_data, board_number, 'toa', 125, (0,12.5), '', 'TOA (ns)', '')
    hist1d(ax[1,2], read_data, board_number, 'tot', 200, (0,20), '', 'TOT (ns)', '')
    hist2d(ax[1,3], read_data, board_number, 'tot', 'toa', [200,125], [[0,20],[0,12.5]], '', 'ToT (ns)', 'ToA (ns)')

    plt.savefig(plot_dir + '/board'+ str(board_number) + '_rawData.png')
    if options.PDF:
        outfile = plot_dir + '/board'+ str(board_number) + '_rawData.pdf'
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

    for board_number in [0, 1, 3]:
        drawPlots(board_number, read_data, plot_dir)

if __name__ == '__main__':
    main()
