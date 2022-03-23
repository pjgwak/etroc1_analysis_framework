import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy import optimize as opt
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--plotting', action='store_true', dest='plotting')
(options, args) = parser.parse_args()


def gauss(x, a, x0, sigma):
    return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))


def draw_fit_plot(board_number, centers, contents, norm, mean, sigma, ax=None):
    if ax is not None:
        plt.sca(ax)
    #plt.hist(contents, bins=len(centers), range=[min(contents), max(contents)])
    fit_y = gauss(centers, norm, mean, sigma)
    plt.plot(centers, contents, 'o', label='data')
    plt.plot(centers, fit_y, '-', label='fit')
    plt.title('Board ' + str(board_number) + ': delta_ToA')
    plt.xlabel('ToA (ns)')
    plt.ylabel('Counts')
    plt.legend()
    print('Board ', board_number, ': ', 'norm: ', norm, 'mean: ', mean, ', sigma: ', sigma)
    #plt.show()


def draw_board(board_lst, center_lst, content_lst, norm_lst, mean_lst, sigma_lst):
    bDraw = False
    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    fig, ax = plt.subplots(1,4, constrained_layout=True, figsize=(1600*px, 300*px))
    
    draw_fit_plot(board_lst[0], center_lst[0], content_lst[0], norm_lst[0], mean_lst[0], sigma_lst[0], ax[0])
    draw_fit_plot(board_lst[1], center_lst[1], content_lst[1], norm_lst[1], mean_lst[1], sigma_lst[0], ax[1])
    draw_fit_plot(board_lst[2], center_lst[2], content_lst[2], norm_lst[2], mean_lst[2], sigma_lst[0], ax[2])

    plt.savefig('plots/resolution.png')


def main():
    file_name = '2021-05-24_Array_Test_Results_B1P9_F11P9_B2P9_Beam_0524_F11HV220'
    b0_corr = pd.read_csv(file_name + '_b0_corr.txt', delimiter = '\s+', header=None)
    b0_corr.columns = ['toa', 'tot', 'delta_toa', 'corr_toa']
    b1_corr = pd.read_csv(file_name + '_b1_corr.txt', delimiter = '\s+', header=None)
    b1_corr.columns = ['toa', 'tot', 'delta_toa', 'corr_toa']
    b3_corr = pd.read_csv(file_name + '_b3_corr.txt', delimiter = '\s+', header=None)
    b3_corr.columns = ['toa', 'tot', 'delta_toa', 'corr_toa']
    print("Read data: Done")
    
    #1. Gaus delta
    #b0
    #(b1corr_toa+b3_cprr_ta)/2 - b0_corr_toa -> delta_toa for gauss fitting
    b0_corr['delta_toa_gauss'] = (b1_corr['corr_toa'] + b3_corr['corr_toa'])*0.5 - b0_corr['corr_toa']
    b1_corr['delta_toa_gauss'] = (b0_corr['corr_toa'] + b3_corr['corr_toa'])*0.5 - b1_corr['corr_toa']
    b3_corr['delta_toa_gauss'] = (b0_corr['corr_toa'] + b1_corr['corr_toa'])*0.5 - b3_corr['corr_toa']
    #print(b0_corr)
    #print(b1_corr)
    
    # Get sigmas
    bins0, edges0 = np.histogram(b0_corr['delta_toa_gauss'].values, 100, density=False)
    centers0 = edges0[:-1] + np.diff(edges0) / 2
    par0, _ = opt.curve_fit(gauss, centers0, bins0)
    norm0 = par0[0]
    mean0 = par0[1]
    sigma0 = par0[2]
    
    bins1, edges1 = np.histogram(b1_corr['delta_toa_gauss'].values, 100, density=False)
    centers1 = edges1[:-1] + np.diff(edges1) / 2
    par1, _ = opt.curve_fit(gauss, centers1, bins1)
    norm1 = par1[0]
    mean1 = par1[1]
    sigma1 = par1[2]

    bins3, edges3 = np.histogram(b3_corr['delta_toa_gauss'].values, 100, density=False)
    centers3 = edges3[:-1] + np.diff(edges3) / 2
    par3, _ = opt.curve_fit(gauss, centers3, bins3)
    norm3 = par3[0]
    mean3 = par3[1]
    sigma3 = par3[2]
    
    if options.plotting:
        draw_fit_plot(0, centers0, bins0, norm0, mean0, sigma0)
        draw_fit_plot(1, centers1, bins1, norm1, mean1, sigma1)
        draw_fit_plot(3, centers3, bins3, norm3, mean3, sigma3)

    board_lst = [0,1,3]
    center_lst = [centers0,centers1,centers3]
    bin_lst = [bins0,bins1,bins3]
    norm_lst = [norm0,norm1,norm3]
    mean_lst = [mean0,mean1,mean3]
    sigma_lst = [sigma0,sigma1,sigma3]

    draw_board(board_lst, center_lst, bin_lst, norm_lst, mean_lst, sigma_lst)
    
    # Get time resoultions
    # Ex) b0 time resolution
    # a = b1_sigma^2 + b3_sigma^2 - b0_sigma^2
    # b = a * 0.5
    # b0_resolution = sqrt(b)
    b0_res = np.sqrt((sigma1**2 + sigma3**2 - sigma0**2)*0.5)
    b1_res = np.sqrt((sigma0**2 + sigma3**2 - sigma1**2)*0.5)
    b3_res = np.sqrt((sigma0**2 + sigma1**2 - sigma3**2)*0.5)
    
    print('=== ETROC1 time resolution (ps) ===')
    print('b0: ', b0_res*1000)
    print('b1: ', b1_res*1000)
    print('b3: ', b3_res*1000)
    


if __name__ == '__main__':
    main()

