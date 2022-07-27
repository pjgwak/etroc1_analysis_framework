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

if not os.path.exists('rawData'):
    os.makedirs('rawData')
    os.makedirs('rawData/a')
    os.makedirs('rawData/b')
    os.makedirs('files')
    os.makedirs('plots')

charge_cut = [8, 10, 10]

in_names = ['TDC_Data_PhaseAdj0_F5P5_QSel%i_DAC586_F17P5_QSel20_DAC559_B2P5_QSel20_DAC539_Split*',
            'TDC_Data_PhaseAdj0_F5P5_QSel20_DAC586_F17P5_QSel%i_DAC559_B2P5_QSel20_DAC539_Split*',
            'TDC_Data_PhaseAdj0_F5P5_QSel20_DAC586_F17P5_QSel20_DAC559_B2P5_QSel%i_DAC539_Split*'
           ]

out_names = ['files/TDC_Data_PhaseAdj0_F5P5_QSel%i_DAC586_F17P5_QSel20_DAC559_B2P5_QSel20_DAC539.txt',
             'files/TDC_Data_PhaseAdj0_F5P5_QSel20_DAC586_F17P5_QSel%i_DAC559_B2P5_QSel20_DAC539.txt',
             'files/TDC_Data_PhaseAdj0_F5P5_QSel20_DAC586_F17P5_QSel20_DAC559_B2P5_QSel%i_DAC539.txt'
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

print('======== plotting ========')
for i in range(3):
    fig3, axes3 = plt.subplots(figsize=(10, 8), constrained_layout=True, sharey=True)
    #x = np.arange(9, 32, 1)
    if i == 0:
        x = np.arange(9, 32, 1)
    else:
        x = np.arange(11, 32, 1)
    y = np.zeros(x.size)
    
    for iq in Qsel:
        if iq <= charge_cut[i]:
            continue
        f = out_names[i] % iq
        data = pd.read_csv(f, delimiter = '\s+', header=None)
        data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'flag']
        selected_data = data.loc[data['flag'] == 1]
        selected_data.reset_index(inplace=True, drop=True)
        selected_data = selected_data.loc[selected_data['board'] == bID[i]]
        selected_data.reset_index(inplace=True, drop=True)
        
        #### Draw Raw data when hitflag = 1 ####
        #fig1, axes1 = plt.subplots(figsize=(12,8), constrained_layout=True, sharey=True)
        plt.hist(data['cal_code'], bins=70, alpha=0.5, range=[100,800], histtype='step', label=iq)


        # Cosmetic part
        #axes1.set_xlabel('CAL code', fontsize=13)
        #step = 70
        #axes1.set_xticks(np.arange(range[0], range[1], step))
        #axes1.grid(axis='x')        
    plt.legend(loc='upper left')
    #plt.show()
    plt.suptitle('Board'+str(bID[i]), fontsize=16)
    plt.savefig('rawData/b/board'+str(bID[i])+'cal_code.png')
print('======== Done ========')