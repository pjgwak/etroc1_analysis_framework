import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from optparse import OptionParser


def main():
    # create the file to gather data (Always overwrite)
    with open('test.txt', 'w+') as f:
        print('gathering file is created')

    # Make file list -> Use config file?
    folder_path = '2022-03-10_SinglePixel_Test_Results/Jitter_Performance_P16_QInj=1M25_internal_QInj_PhaseAdjScan_FS19_DiscriOff_QInjEnable_PreBuffOff_DAC250'
    file_list = glob.glob(folder_path + '/*.dat')
    DAC_range = [100, 200]
    DAC_value = DAC_range[0]
    
    result_list = []

    for filename in file_list:
        # is file empty?
        if os.stat(filename).st_size == 0:
            # DAC, TOA code mean, TOT code mean, Cal code mean, TOA rms
            sub_list = [DAC_value, 0, 0, 0, 0]
            result_list.append(sub_list)
            DAC_value += 2
        else:
            data = pd.read_csv(filename, delimiter = '\s+', header=None)
            data.columns = ['toa_code', 'tot_code', 'cal_code', 'hit_flag']

            # add column for  DAC or PhaseAdj number
            TOA_code_mean = data['toa_code'].mean()
            TOT_code_mean = data['tot_code'].mean()
            Cal_code_mean = data['cal_code'].mean()

            fbins = 3.125 / Cal_code_mean
            TOA_mean = 12.5 - data['toa_code'] * fbins
            data['tot'] = (data['tot_code']*2 - np.floor(data['tot_code']/32.)) * fbins
            data['toa_rms'] = np.sqrt(np.mean(data['toa']**2))
            TOA_rms = data['TOA_code'].mean()

            print(TOA_code_mean)
            print(TOT_code_mean)
            print(Cal_code_mean)
            print(TOA_rms)
            exit(1)

            sub_list = [DAC_value, TOA_code_mean, TOT_code_mean, Cal_code_mean, TOA_rms]
            DAC_value += 2


if __name__ == '__main__':
    main()





'''
data = pd.read_csv('test.txt', delimiter = '\s+', header=None)
data.columns = ['toa_code', 'tot_code', 'cal_code', 'hit_flag', 'toa', 'tot', 'toa_rms', 'DAC/Phase']
print(data)

#  k = data.groupby('DAC/Phase')['toa_rms'].agg(**{'mean':'mean'}).reset_index()
k = data.groupby('DAC/Phase').count().reset_index();

#  ['toa_rms'].agg(**{'mean':'mean'}).reset_index()
print(k)


plt.plot(k['DAC/Phase'], k['toa_code'], linestyle='--', marker='o', color='b', label='line with marker')
plt.yscale('log')
plt.ylim(None, None)
plt.show()
'''
