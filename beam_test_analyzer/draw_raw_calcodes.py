import os
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--pdf', action='store_true', default=False, dest='PDF')
parser.add_option('--argmax', action='store_true', default=False, dest='ARGMAX')
parser.add_option('--zoom', help='range to zoom in', dest='ZOOM')
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
    if options.ZOOM:
        ax.set_xlim(int(options.ZOOM)-10, int(options.ZOOM)+10)
        ax.set_xticks(np.arange(int(options.ZOOM)-10, int(options.ZOOM)+10, 1))
        ax.grid(axis='x')

def drawPlots(board_number, read_data, plot_dir):
    fig, ax = plt.subplots(constrained_layout=True, figsize=(12, 8))
    hist1d(ax, read_data, board_number, 'cal_code', 1000, (0,1000), 'Board '+str(board_number), 'CAL code', 'Number of hits', logy=True)
    
    if options.ZOOM:
        plt.savefig(plot_dir + '/board'+ str(board_number) + '_rawCALcode_zoom.png')
    else:
        plt.savefig(plot_dir + '/board'+ str(board_number) + '_rawCALcode.png')
    
    if options.PDF:
        outfile = plot_dir + '/board'+ str(board_number) + '_rawCALcode.pdf'
        plt.savefig(outfile)

def printArgMax(board_number, input_data):
    data = input_data.loc[input_data['board'] == board_number]
    bins, _ = np.histogram(data['cal_code'], bins=1000, range=(0,1000))
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

    read_data = pd.read_csv(dir_path + '/' + file_name + '.txt', delimiter = '\s+', header=None, skiprows=1)
    read_data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'flag', 'dummy1', 'dummy2']
    read_data = read_data.drop(['toa_code', 'tot_code', 'flag', 'dummy1', 'dummy2'], axis=1)
    print("Read data: Done")

    for board_number in [0, 1, 3]:
        drawPlots(board_number, read_data, plot_dir)
        if options.ARGMAX:
            printArgMax(board_number, read_data)


if __name__ == '__main__':
    main()
