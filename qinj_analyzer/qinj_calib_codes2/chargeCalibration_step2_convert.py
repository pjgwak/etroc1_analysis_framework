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

out_names = ['files/TDC_Data_PhaseAdj0_F5P5_QSel%i_DAC586_F17P5_QSel20_DAC559_B2P5_QSel20_DAC539.txt',
             'files/TDC_Data_PhaseAdj0_F5P5_QSel20_DAC586_F17P5_QSel%i_DAC559_B2P5_QSel20_DAC539.txt',
             'files/TDC_Data_PhaseAdj0_F5P5_QSel20_DAC586_F17P5_QSel20_DAC559_B2P5_QSel%i_DAC539.txt'
            ]
            
txt_names = ['files/TDC_Data_PhaseAdj0_F5P5_QSel%i_DAC586.txt',
             'files/TDC_Data_PhaseAdj0_F17P5_QSel%i_DAC559.txt',
             'files/TDC_Data_PhaseAdj0_B2P5_QSel%i_DAC539.txt'
            ]

bID = [0, 1, 3]
Qsel = np.arange(8, 32, 1)

#cal_code_cut = [[127, 129], [129, 131], [126, 128]] ## Apr 10 data (F9, F11, F5)
#cal_code_cut = [[138, 140], [138, 140], [137, 139]] ## Apr 28 data (F9, F15, F5)
cal_code_cut = [[144, 151], [144, 150], [138, 145]]
cal_peak = [144, 143, 137]
charge_cut = [8, 10, 10]

##### Convert to time #####
for i in range(3):
    for iq in Qsel:
        if iq <= charge_cut[i]:
            continue
        print('Board %i with charge %ifC' %(bID[i], iq))
        f = out_names[i] % iq
        output = txt_names[i] %iq
        #if not os.path.exists(output):
        data = pd.read_csv(f, delimiter = '\s+', header=None)
        data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'flag']
        selected_data = data.loc[data['flag'] == 1]
        selected_data.reset_index(inplace=True, drop=True)
        selected_data = selected_data.loc[selected_data['board'] == bID[i]]
        selected_data.reset_index(inplace=True, drop=True)
        selected_data = selected_data.loc[(selected_data['cal_code'] >= cal_code_cut[i][0]) & (selected_data['cal_code'] <= cal_code_cut[i][1])]
        selected_data.reset_index(inplace=True, drop=True)
        # TOA = 12.5 - TOA_code*n_bin
        # -> TOA_code = (TOA - 12.5) / n_bin
        #TOA_code_upper = np.abs(5.5) / n_bin
        #TOA_code_lower = np.abs(2.5) / n_bin
        # TOT = (TOT_code*2 - np.floor(TOT_code/32)) * n_bin
        # -> TOT_code ((TOT / n_bin) + np.floor(TOT_code/32))/2
        # -> TOT_code (TOT / n_bin)/2
        # Be care equation above
        # n_bin = 3.125 / cal_peak
        #TOT_code_upper = (3 / n_bin) / 2
        #TOT_code_lower = 0
        #### TOA code ####
        bins, _ = np.histogram(selected_data['toa_code'], bins=100, range=(130, 230))
        if i == 0:
            n_bin = 3.125 / cal_peak[0]
            TOA_code_upper = np.abs(5.5) / n_bin
            TOA_code_lower = np.abs(2.5) / n_bin
            selected_data = selected_data.loc[(selected_data['toa_code'] > TOA_code_lower) & (selected_data['toa_code'] < TOA_code_upper)]
            #selected_data = selected_data.loc[(selected_data['toa_code'] >= np.argmax(bins)+127) & (selected_data['toa_code'] <= np.argmax(bins)+133)]
            selected_data.reset_index(inplace=True, drop=True)
            #elif i == 1:
            #    n_bin = 3.125 / cal_peak[1] 
            #    TOA_code_upper = np.abs(5.5) / n_bin
            #    TOA_code_lower = np.abs(2.5) / n_bin
            #    selected_data = selected_data.loc[(selected_data['toa_code'] > TOA_code_lower) & (selected_data['toa_code'] < TOA_code_upper)]
            #    selected_data.reset_index(inplace=True, drop=True)
        else:
            TOA_code_upper = 2000 # Any big number -> No cut
            TOA_code_lower = 0
            selected_data = selected_data.loc[(selected_data['toa_code'] > TOA_code_lower) & (selected_data['toa_code'] < TOA_code_upper)]
            selected_data.reset_index(inplace=True, drop=True)
        
        
        #### TOT code ####
        bins, _ = np.histogram(selected_data['tot_code'], bins=100, range=(0, 100))
        '''
        TOT_code_upper = 257 # 11 ns
        TOT_code_lower = 0
        selected_data = selected_data.loc[(selected_data['tot_code'] >=TOT_code_lower) & (selected_data['tot_code'] <= TOT_code_upper)]
        selected_data.reset_index(inplace=True, drop=True)
        '''
        if i == 0:
            #TOT_code_upper = 77
            #TOT_code_lower = 0
            TOT_code_upper = 140
            TOT_code_lower = 77
            selected_data = selected_data.loc[(selected_data['tot_code'] >= TOT_code_lower) & (selected_data['tot_code'] <= TOT_code_upper)]
            #selected_data = selected_data.loc[(selected_data['toa_code'] >= np.argmax(bins)+127) & (selected_data['toa_code'] <= np.argmax(bins)+133)]
            selected_data.reset_index(inplace=True, drop=True)
        elif i == 1:
            # No TOT cut
            TOT_code_upper = 1000 # Any big number passing everything
            TOT_code_lower = 0
            selected_data = selected_data.loc[(selected_data['tot_code'] >= TOT_code_lower) & (selected_data['tot_code'] <= TOT_code_upper)]
            selected_data.reset_index(inplace=True, drop=True)
        else:
            #TOT_code_upper = 66
            #TOT_code_lower = 0
            TOT_code_upper = 134
            TOT_code_lower = 68
            selected_data = selected_data.loc[(selected_data['tot_code'] >=TOT_code_lower) & (selected_data['tot_code'] <= TOT_code_upper)]
            selected_data.reset_index(inplace=True, drop=True)
        #selected_data = selected_data.loc[(selected_data['tot_code'] >= np.argmax(bins)-2) & (selected_data['tot_code'] <= np.argmax(bins)+2)]
        #selected_data.reset_index(inplace=True, drop=True)
        fbin = 3.125/selected_data['cal_code']
        #fbin = 3.125/np.mean(selected_data['cal_code'])
        selected_data['toa'] = 12.5 - selected_data['toa_code'] * fbin
        selected_data['tot'] = (selected_data['tot_code'] * 2 - np.floor(selected_data['tot_code'] / 32.)) * fbin
        selected_data = selected_data.drop(['board', 'flag'], axis=1)
        if selected_data.empty:
            print('Selected %s is empty!!' % f)
        else:
            selected_data.to_csv(output, sep='\t', index=None, header=None, mode='w')