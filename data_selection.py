import numpy as np
import pandas as pd
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt


codes_data = pd.read_csv("2021-05-24_Array_Test_Results/B1P9_F11P9_B2P9_Beam_0524_F11HV210.txt", delimiter = '\s+', header=None)
file_name = '2021-05-24_Array_Test_Results_B1P9_F11P9_B2P9_Beam_0524_F11HV210'

# codes_data = pd.read_csv("txt", delimiter = '\s+', header=None)
codes_data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'flag']
print("Read data: Done")

# print test
# print(codes_data.head)
# print(codes_data.shape)

# data processing
# 1. exclude flag 0 signals
# 2. check 0, 1, 3 pattern
raw_cal_codes = codes_data[['board', 'cal_code']]
raw_cal_codes.to_csv(file_name+'_cal_codes.txt', sep='\t', index=None, header=None)
print("Save raw cal codes to txt")

selected_data = codes_data.loc[codes_data['flag'] >= 1]
selected_data.reset_index(inplace=True, drop=True)
print("Exclude flag 0 cases: Done")
#  print(selected_data)

pattern = [0, 1, 3]
matched = selected_data.rolling(len(pattern)).apply(lambda x: all(np.equal(x, pattern)), raw=True)  
# 'raw=True' -> Handle as numpy array instead of Pandas' DataFrame -> Much Faster
matched = matched.sum(axis = 1).astype(bool)   #Sum to perform boolean OR
idx_matched = np.where(matched)[0]
subset = [range(match-len(pattern)+1, match+1) for match in idx_matched]
selected_data = pd.concat([selected_data.iloc[subs,:] for subs in subset], axis = 0)
selected_data.reset_index(inplace=True, drop=True)
#  print(selected_data)
print("Check 0, 1, 3 patterns: Done")


# calculate time value from raw data (called toa/tot/cal codes)
# the result is time (ns)
#### Calculation fomular ###
# fbin = 3.125 / 170 # 3.125 came from theory, 170 is fixed cal code from empirical experiences
# fToa = 12.5 - fToaCode * fbin; # 12.5 from toa's property(?)
# fTot= (fTotCode*2 - np.floor(fTotCode/32.)) * fbin # 32 came from hardware property of tot
### End ###

fbin = 3.125 / 170.
selected_data.drop(['flag'], axis=1, inplace = True)
selected_data['toa'] = 12.5 - selected_data['toa_code'] * fbin
selected_data['tot'] = (selected_data['tot_code'] * 2 - np.floor(selected_data['tot_code'] / 32.)) * fbin
print(selected_data)
print("Transform raw codes to time (ns): Done")

#  Save the selected events to txt file
selected_data.to_csv(file_name+'.txt', sep='\t', index=None, header=None)
print("Save the selected_data to txt")

#a[a.loc[codes_data['board']==3]['toa']]
