import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from glob import glob
from optparse import OptionParser
import os
from natsort import natsorted
from scipy.optimize import curve_fit

#####################
### Configure options
parser = OptionParser()
parser.add_option('-f', '--fit', action="store_true", dest='fit')
parser.add_option('-p', '--plot', action="store_true", dest='plotting')
(options, args) = parser.parse_args()
#####################
#####################

def hist1d(ax, data, variable='toa_code', num_bins=100, range_hist=[0,100], xtitle=''):
    if ax is not None:
        plt.sca(ax)
    ax.hist(data[variable], bins=num_bins, range=range_hist)
    ax.set_xlabel(xtitle, fontsize=13)
    step = 10
    ax.set_xticks(np.arange(range_hist[0], range_hist[1], step))
    ax.grid(axis='x')

def hist2d(fig, ax, data, v1='tot_code', v2='toa_code', num_bins=[200,200], range_hist=[[0,600],[0,600]], xtitle='', ytitle='', step=10):
    if ax is not None:
        plt.sca(ax)
    h = ax.hist2d(data[v1], data[v2], cmap=plt.cm.jet, bins=num_bins, range=range_hist, cmin=1)
    fig.colorbar(h[3], ax=ax)
    ax.set_xlabel(xtitle, fontsize=13)
    ax.set_xticks(np.arange(range_hist[0][0], range_hist[0][1], step))
    ax.set_ylabel(ytitle, fontsize=13)
    ax.set_yticks(np.arange(range_hist[1][0], range_hist[1][1], step))
    ax.grid()
    ax.plot(np.NaN, np.NaN, '-', color='none', label='') ## only for legend
    ax.legend(['TOT mean: %.3f, TOA mean %.3f'%(np.mean(data[v1]), np.mean(data[v2]))], loc='lower right', fontsize=13)

txt_names = ['files/TDC_Data_PhaseAdj0_F5P5_QSel%i_DAC583.txt',
             'files/TDC_Data_PhaseAdj0_F17P5_QSel%i_DAC435.txt',
             'files/TDC_Data_PhaseAdj0_B2P5_QSel%i_DAC541.txt'
            ]

bID = [0, 1, 3]
Qsel = np.arange(8, 32, 1)
charge_cut = [8, 10, 10]

def gaus(x,a,x0,sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))

if not os.path.exists('plots'):
    os.makedirs('plots')

##### Draw charge vs. mean TOT #####
#for i in range(3):
for i in [0,1,2]:
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    x = np.arange(8, 32, 1)
    y = np.zeros(x.size)
    yerr = np.zeros(x.size)
    charge_list = []
    value_list = []
    for iq in Qsel:
        if iq <= charge_cut[i]:
            y[iq-8] = np.NaN
            yerr[iq-8] = np.NaN
            continue
        #print('Which board %d and what charge %d?' %(i, iq))
        f = txt_names[i] % iq
        fig1, axes = plt.subplots(ncols=2, figsize=(16,9))


        data = pd.read_csv(f, delimiter = '\s+', header=None)
        data.columns = ['toa_code', 'tot_code', 'cal_code', 'toa', 'tot']

        if options.plotting:
            hist2d(fig1, axes[0], data, 'tot', 'toa', [50, 50], [[0,5],[6,11]], 'TOT (ns)', 'TOA (ns)', 1)
            #hist2d(fig1, axes[1], data, 'tot_code', 'toa_code', [70, 60], [[20,90],[150,210]], 'TOT code', 'TOA code', 10)
            hist2d(fig1, axes[1], data, 'tot_code', 'toa_code', [120, 240], [[0,120],[60,300]], 'TOT code', 'TOA code', 10)
            fig1.suptitle('Board'+str(bID[i])+'_'+str(iq)+'fC_TOTvsTOA', fontsize=15)
            fig1.savefig('plots/Board'+str(bID[i])+'_'+str(iq)+'fC_TOAvsTOA.png')
        if options.fit:
            print('Do Gaussian fit')
            num_bins = 40
            bins, edges = np.histogram(data['tot'], num_bins, range=(0.0, 4.0), density=False)
            centers = 0.5*(edges[1:] + edges[:-1])
            mean, sigma = np.mean(data['tot']), np.std(data['tot'], ddof=1)
            try:
                popt, _ = curve_fit(gaus, centers, bins, p0=[100, mean, sigma])
                y[iq-8] = popt[1]
                yerr[iq-8] = popt[2]
                charge_list.append(iq)
                value_list.append(y[iq-8])
                #fc0 = gaus(3.353, *popt)
                #fc1 = gaus(3.747, *popt)
                #fc3 = gaus(2.818, *popt)
                #print(fc0, fc1, fc3)
                #if options.plotting:
                #    ax1.hist(data['tot'], num_bins, range=(0.0, 4.0), density=False)
                #    ax1.plot(centers, gaus(centers, *popt), color='red', lw=2)
                #    ax1.set_title('Board'+str(bID[i])+'_'+str(iq)+'fC', fontsize=15)
                #    ax1.set_xlabel('TOT (ns)', fontsize=15)
                #    fig1.savefig('plots/Board'+str(bID[i])+'_'+str(iq)+'fC'+'_gaussianFit.png')
            except:
                print('Gaussian fit failed!!')
                y[iq-8] = np.mean(data['tot'])
                yerr[iq-8] = np.std(data['tot'], ddof=1)
                charge_list.append(iq)
                value_list.append(y[iq-8])
                #if options.plotting:
                #    ax1.hist(data['tot'], num_bins, range=(0.0, 4.0), density=False)
                #    ax1.set_title('Board'+str(bID[i])+'_'+str(iq)+'fC', fontsize=15)
                #    ax1.set_xlabel('TOT (ns)', fontsize=15)
                #    fig1.savefig('plots/Board'+str(bID[i])+'_'+str(iq)+'fC'+'_gaussianFit.png')
        else:
            y[iq-8] = np.mean(data['tot'])
            yerr[iq-8] = np.std(data['tot'], ddof=1)
            charge_list.append(iq)
            value_list.append(y[iq-8])

    def poly2(x,a,b,c):
        return a*x**2 + b*x + c
    popt1, _ = curve_fit(poly2, value_list, charge_list)
    #print(charge_list)
    #print(value_list)
    #a1 = np.polyfit(np.log(value_list), charge_list, 1)
    print(popt1)
    a = poly2(3.530, *popt1)
    #a = poly2(3.747, *popt1)
    #a = poly2(2.818, *popt1)
    #print(a)

    ax2.errorbar(x, y, yerr=yerr, marker='o', ms=5, mfc='black', mew=0, elinewidth=2)
    ax2.set_title('Board '+str(bID[i]), fontsize=15)
    ax2.set_xlabel('Charge (fC)', fontsize=15)
    ax2.set_xticks(np.arange(8, 33, 1))
    ax2.set_ylabel('Mean TOT (ns)', fontsize=15)
    ax2.set_ylim(0, 4.5)
    ax2.grid()
    fig2.savefig('plots/b'+str(bID[i])+'chargeVStot.png')
