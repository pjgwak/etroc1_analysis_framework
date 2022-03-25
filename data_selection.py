###############################################
# data processing
# 1. Exclude flag 0 signals
# 2. Check 0, 1, 3 pattern
# 3. Convert raw data codes to time in ns (raw data codes: ToA/ToT/CAL codes)
# 
# ### Convert formula ####
# fbin = 3.125 / 170 # 3.125 came from theory, 170 is fixed cal code from empirical experiences
# fToa = 12.5 - fToaCode * fbin; # 12.5 from TDC design
# fTot= (fTotCode*2 - np.floor(fTotCode/32.)) * fbin # 32 came from the TDC property of tot
###############################################

import os
import yaml
import numpy as np
import pandas as pd
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
from optparse import OptionParser
parser = OptionParser()
parser.add_option('-p', '--print', help='Print dataset during execution', action='store_true', default=True, dest='PRINT')
(options, args) = parser.parse_args()

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

codes_data = pd.read_csv(dir_path + '/' + file_name + '.txt', delimiter = '\s+', header=None, skiprows=1)
codes_data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'flag', 'dummy1', 'dummy2']
codes_data = codes_data.drop(['dummy1', 'dummy2'], axis=1)
print("Read data: Done")

if options.PRINT:
    print('============ Print loaded raw dataset ============')
    print(codes_data.head, '\n')

raw_cal_codes = codes_data[['board', 'cal_code']]
raw_cal_codes.to_csv(sub_file_dir+'/'+file_name+'_cal_codes.txt', sep='\t', index=None, header=None)
print("Save raw cal codes to txt")

selected_data = codes_data.loc[codes_data['flag'] >= 1]
selected_data.reset_index(inplace=True, drop=True)
print("Exclude flag 0 cases: Done")
if options.PRINT:
    print('============ Print dataset with hitflag = 1 ============')
    print(selected_data.head, '\n')

pattern = [0, 1, 3]
matched = selected_data.rolling(len(pattern)).apply(lambda x: all(np.equal(x, pattern)), raw=True)
# 'raw=True' -> Handle as numpy array instead of Pandas' DataFrame -> Much Faster
matched = matched.sum(axis = 1).astype(bool)   #Sum to perform boolean OR
idx_matched = np.where(matched)[0]
subset = [range(match-len(pattern)+1, match+1) for match in idx_matched]
selected_data = pd.concat([selected_data.iloc[subs,:] for subs in subset], axis = 0)
selected_data.reset_index(inplace=True, drop=True)
print("Check 0, 1, 3 patterns: Done")
if options.PRINT:
    print('============ Print selected good events (Board Id 0 1 3 aligned) in dataset ============')
    print(selected_data.head, '\n')

fbin = 3.125 / 170.
selected_data.drop(['flag'], axis=1, inplace = True)
selected_data['toa'] = 12.5 - selected_data['toa_code'] * fbin
selected_data['tot'] = (selected_data['tot_code'] * 2 - np.floor(selected_data['tot_code'] / 32.)) * fbin
if options.PRINT:
    print('============ Print converted ToA and ToT (ns) ============')
    print(selected_data.head, '\n')
print("Transform raw codes to time (ns): Done")

#  Save the selected events to txt file
selected_data.to_csv(sub_file_dir+'/'+file_name+'.txt', sep='\t', index=None, header=None)
print("Save the selected_data to txt")
