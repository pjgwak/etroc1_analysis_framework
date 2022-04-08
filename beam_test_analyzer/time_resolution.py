import yaml
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy import optimize as opt
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--pdf', action='store_true', default=False, dest='PDF')
(options, args) = parser.parse_args()

def gaussianFit(delta_toa, board_number, plot_dir, twc=False):

    def gauss(x, a, x0, sigma):
        return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))
    # Make bin width 0.02 ns
    my_bins = int((delta_toa.max()-delta_toa.min())/0.02)
    bins, edges = np.histogram(delta_toa.values, my_bins, density=False)
    centers = edges[:-1] + np.diff(edges) / 2
    par, _ = opt.curve_fit(gauss, centers, bins)

    fig, ax = plt.subplots(constrained_layout=True, figsize=(8, 6))
    fit_y = gauss(centers, *par)
    ax.plot(centers, bins, 'o', label='data')
    ax.plot(centers, fit_y, '-', label='fit: mean=%.3f, sigma=%.3f' % (par[1], abs(par[2])))
    ax.set_xlabel('ToA (ns)')
    ax.set_ylabel('Counts')
    ax.set_xlim(par[1]-0.5, par[1]+0.5)
    ax.legend()
    if twc:
        ax.set_title('Board ' + str(board_number) + r': $\Delta$ ToA w/ TWC')
        fig.savefig(plot_dir+'/gaussianFit_Board_wTWC'+str(board_number)+'.png')
        if options.PDF:
            fig.savefig(plot_dir+'/gaussianFit_Board_wTWC'+str(board_number)+'.pdf')
    else:
        ax.set_title('Board ' + str(board_number) + r': $\Delta$ ToA w/o TWC')
        fig.savefig(plot_dir+'/gaussianFit_Board_noTWC'+str(board_number)+'.png')
        if options.PDF:
            fig.savefig(plot_dir+'/gaussianFit_Board_noTWC'+str(board_number)+'.pdf')

    return par

def main():
    with open('config.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    dir_path = conf['dir_path']
    file_name = conf['file_name']
    plot_dir = dir_path + '/' + file_name + '_plot'
    sub_file_dir = dir_path + '/' + file_name + '_sub_file'

    b0_corr = pd.read_csv(sub_file_dir + '/' + file_name + '_b0_corr.txt', delimiter = '\s+', header=None)
    b0_corr.columns = ['toa', 'tot', 'cal_code', 'delta_toa', 'corr_toa']
    b1_corr = pd.read_csv(sub_file_dir + '/' + file_name + '_b1_corr.txt', delimiter = '\s+', header=None)
    b1_corr.columns = ['toa', 'tot', 'cal_code', 'delta_toa', 'corr_toa']
    b3_corr = pd.read_csv(sub_file_dir + '/' + file_name + '_b3_corr.txt', delimiter = '\s+', header=None)
    b3_corr.columns = ['toa', 'tot', 'cal_code', 'delta_toa', 'corr_toa']
    print("Read data: Done")

    #1. Gaus delta
    b0_corr['delta_toa_gauss'] = b1_corr['corr_toa'] - b3_corr['corr_toa']
    b1_corr['delta_toa_gauss'] = b0_corr['corr_toa'] - b3_corr['corr_toa']
    b3_corr['delta_toa_gauss'] = b0_corr['corr_toa'] - b1_corr['corr_toa']

    #### Get Delta TOA of each board w/o TWC ####
    # [0]: Norm, [1]: Mean,  [2]: Sigma
    par0 = gaussianFit(b1_corr['toa'] - b3_corr['toa'], 0, plot_dir)
    par1 = gaussianFit(b0_corr['toa'] - b3_corr['toa'], 1, plot_dir)
    par3 = gaussianFit(b0_corr['toa'] - b1_corr['toa'], 3, plot_dir)
    print('========== \u0394 ToA w/o TWC ==========')
    print('b0: %.4f'%(abs(par0[2])))
    print('b1: %.4f'%(abs(par1[2])))
    print('b3: %.4f'%(abs(par3[2])), '\n')

    #### Get Delta TOA of each board w/ TWC ####
    # [0]: Norm, [1]: Mean,  [2]: Sigma
    par0 = gaussianFit(b0_corr['delta_toa_gauss'], 0, plot_dir, True)
    par1 = gaussianFit(b1_corr['delta_toa_gauss'], 1, plot_dir, True)
    par3 = gaussianFit(b3_corr['delta_toa_gauss'], 3, plot_dir, True)
    print('========== \u0394 ToA w/ TWC ==========')
    print('b0: %.4f'%(abs(par0[2])))
    print('b1: %.4f'%(abs(par1[2])))
    print('b3: %.4f'%(abs(par3[2])), '\n')

    # Get time resoultions
    # Ex) b0 time resolution
    # a = b1_sigma^2 + b3_sigma^2 - b0_sigma^2
    # b = a * 0.5
    # b0_resolution = sqrt(b)
    b0_res = np.sqrt((par1[2]**2 + par3[2]**2 - par0[2]**2)*0.5)
    b1_res = np.sqrt((par0[2]**2 + par3[2]**2 - par1[2]**2)*0.5)
    b3_res = np.sqrt((par0[2]**2 + par1[2]**2 - par3[2]**2)*0.5)

    print('========== ETROC1 time resolution ==========')
    print('b0: %.2f ps'%(b0_res*1000))
    print('b1: %.2f ps'%(b1_res*1000))
    print('b3: %.2f ps'%(b3_res*1000))

if __name__ == '__main__':
    main()
