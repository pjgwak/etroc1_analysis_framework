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
#parser = OptionParser()
#parser.add_option('-p', '--plot', help='plotting raw data distributions', action="store_true", dest='plotting')
#(options, args) = parser.parse_args()
#####################
#####################

def hist1d(ax, data, variable='toa_code', num_bins=100, range_hist=[0,100], xtitle=''):
    if ax is not None:
        plt.sca(ax)
    ax.hist(data[variable], bins=num_bins, range=range_hist)
    ax.set_xlabel(xtitle, fontsize=13)
    step = 5
    ax.set_xticks(np.arange(range_hist[0], range_hist[1], step))
    ax.grid(axis='x')

def hist2d(ax, data, v1='tot_code', v2='toa_code', num_bins=[100,100], range_hist=[[0,300],[0,300]], xtitle='', ytitle=''):
    if ax is not None:
        plt.sca(ax)
    h = ax.hist2d(data[v1], data[v2], cmap=plt.cm.jet, bins=num_bins, range=range_hist, cmin=1)
    fig2.colorbar(h[3], ax=ax)
    ax.set_xlabel(xtitle, fontsize=13)
    step = 10
    ax.set_xticks(np.arange(range_hist[0][0], range_hist[0][1], step))
    ax.set_ylabel(ytitle, fontsize=13)
    ax.set_yticks(np.arange(range_hist[1][0], range_hist[1][1], step))
    ax.grid()

in_names = ['files/TDC_Data_PhaseAdj0_F9P5_QSel%i_DAC551_F15P5_QSel20_DAC542_F5P5_QSel20_DAC566_Split*',
            'files/TDC_Data_PhaseAdj0_F9P5_QSel20_DAC551_F15P5_QSel%i_DAC542_F5P5_QSel20_DAC566_Split*',
            'files/TDC_Data_PhaseAdj0_F9P5_QSel20_DAC551_F15P5_QSel20_DAC542_F5P5_QSel%i_DAC566_Split*'
           ]

out_names = ['files/TDC_Data_PhaseAdj0_F9P5_QSel%i_DAC551_F15P5_QSel20_DAC542_F5P5_QSel20_DAC566.txt',
             'files/TDC_Data_PhaseAdj0_F9P5_QSel20_DAC551_F15P5_QSel%i_DAC542_F5P5_QSel20_DAC566.txt',
             'files/TDC_Data_PhaseAdj0_F9P5_QSel20_DAC551_F15P5_QSel20_DAC542_F5P5_QSel%i_DAC566.txt'
            ]

bID = [0, 1, 3]
Qsel = np.arange(8, 32, 1)

print('======== Merge ========')
##### Merge output #####
for i in range(3):
    for iq in Qsel:
        print('Board %i with charge %ifC' %(bID[i], iq))
        f = in_names[i] % iq
        output = out_names[i] %iq
        if not os.path.exists(output):
            Listfiles = [x for x in glob(f)]
            Listfiles = natsorted(Listfiles, key=lambda y: y.lower())
            argus = str(' '.join(Listfiles))
            cmd = 'cat %s > %s'%(argus, output)
            #print(cmd)
            os.system(cmd)
print('======== Done ========')

if not os.path.exists('rawData'):
    os.makedirs('rawData')

charge_cut = [8, 8, 8]

print('======== plotting ========')
for i in range(3):
    fig3, axes3 = plt.subplots(figsize=(10, 8), constrained_layout=True, sharey=True)
    x = np.arange(9, 32, 1)
    y = np.zeros(x.size)
    for iq in Qsel:
        if iq <= charge_cut[i]:
            continue
        print('Board %i with charge %ifC' %(bID[i], iq))
        f = out_names[i] % iq
        data = pd.read_csv(f, delimiter = '\s+', header=None)
        data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'flag']
        selected_data = data.loc[data['flag'] == 1]
        selected_data.reset_index(inplace=True, drop=True)
        selected_data = selected_data.loc[selected_data['board'] == bID[i]]
        selected_data.reset_index(inplace=True, drop=True)

        #### Draw Raw data when hitflag = 1 ####
        fig1, axes1 = plt.subplots(figsize=(12,8), constrained_layout=True, sharey=True)
        hist1d(axes1, selected_data, variable='cal_code', num_bins=40, range_hist=[120,160], xtitle='CAL code')
        fig1.suptitle('Board'+str(bID[i])+'_'+str(iq)+'fC', fontsize=16)
        fig1.savefig('rawData/Board'+str(bID[i])+'_'+str(iq)+'fC_rawData.png')

        fig2, axes2 = plt.subplots(figsize=(12,8), constrained_layout=True, sharey=True)
        hist2d(axes2, selected_data, 'tot_code', 'toa_code', num_bins=[100, 100], range_hist=[[0, 100], [130, 230]], xtitle='TOT code', ytitle='TOA code')
        fig2.suptitle('Board'+str(bID[i])+'_'+str(iq)+'fC', fontsize=16)
        fig2.savefig('rawData/Board'+str(bID[i])+'_'+str(iq)+'fC_rawData_TOTvsTOA.png')

        #### CAL code mean and standard deviation ####
        y[iq-9] = np.mean(selected_data['cal_code'])

    axes3.plot(x, y, marker='o', ms=5, mfc='black')
    axes3.set_title('Board '+str(bID[i]), fontsize=15)
    axes3.set_xlabel('Charge (fC)', fontsize=15)
    axes3.set_xticks(np.arange(9, 33, 1))
    axes3.set_yticks(np.arange(130, 160, 5))
    axes3.set_ylabel('Mean CAL code', fontsize=15)
    axes3.grid()
    fig3.savefig('rawData/board'+str(bID[i])+'chargeVScalcode.png')
print('======== Done ========')
