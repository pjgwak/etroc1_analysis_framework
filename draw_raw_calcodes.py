import yaml
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
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

def drawPlots(board_number, read_data, plot_dir):
    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    fig, ax = plt.subplots(constrained_layout=True, figsize=(800*px, 450*px))
    hist1d(ax, read_data, board_number, 'cal_code', 1000, (0,1000), 'Board '+str(board_number), 'CAL code', 'Number of hits', logy=True)

    plt.savefig(plot_dir + '/board'+ str(board_number) + '_rawCALcode.png')
    if options.PDF:
        outfile = plot_dir + '/board'+ str(board_number) + '_rawCALcode.pdf'
        plt.savefig(outfile)

def main():
    with open('config.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    dir_path = conf['dir_path']
    file_name = conf['file_name']
    plot_dir = dir_path + '/' + file_name + '_plot'
    sub_file_dir = dir_path + '/' + file_name + '_sub_file'

    read_data = pd.read_csv(sub_file_dir+'/'+file_name+'_cal_codes.txt', delimiter = '\s+', header=None)
    read_data.columns = ['board', 'cal_code']
    print("Read data: Done")

    for board_number in [0, 1, 3]:
        drawPlots(board_number, read_data, plot_dir)


if __name__ == '__main__':
    main()