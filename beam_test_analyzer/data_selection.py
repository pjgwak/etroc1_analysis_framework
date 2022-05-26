###############################################
# data processing
# 1. Exclude flag 0 signals
# 2. Check 0, 1, 3 pattern
# 3. Convert raw data codes to time in ns (raw data codes: ToA/ToT/CAL codes)
# 
# ### Convert formula ####
# fbin = 3.125 / 170 # 3.125 came from theory, 170 is fixed cal code from peak of Cal code distribution
# fToa = 12.5 - fToaCode * fbin; # 12.5 from TDC design
# fTot= (fTotCode*2 - np.floor(fTotCode/32.)) * fbin # 32 came from the TDC property of tot
###############################################

import os
import yaml
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
from optparse import OptionParser
parser = OptionParser()
parser.add_option('-p', '--print', help='Print dataset during execution', action='store_true', default=False, dest='PRINT')
(options, args) = parser.parse_args()


def code_to_time(data, cal0 = 130, cal1 = 130, cal3 = 130):
    fbin0 = 3.125 / cal0
    fbin1 = 3.125 / cal1
    fbin3 = 3.125 / cal3
    
    data['toa'] = None
    data['tot'] = None
    
    data['toa'].loc[data['board']==0] = 12.5 - data['toa_code'].loc[data['board']==0] * fbin0
    data['tot'].loc[data['board']==0] = (data['tot_code'].loc[data['board']==0] * 2 - np.floor(data['tot_code'].loc[data['board']==0]  / 32.)) * fbin0
    
    data['toa'].loc[data['board']==1] = 12.5 - data['toa_code'].loc[data['board']==1] * fbin1
    data['tot'].loc[data['board']==1] = (data['tot_code'].loc[data['board']==1] * 2 - np.floor(data['tot_code'].loc[data['board']==1]  / 32.)) * fbin1
    
    data['toa'].loc[data['board']==3] = 12.5 - data['toa_code'].loc[data['board']==3] * fbin3
    data['tot'].loc[data['board']==3] = (data['tot_code'].loc[data['board']==3] * 2 - np.floor(data['tot_code'].loc[data['board']==3]  / 32.)) * fbin3
    
    if options.PRINT:
        print('============ Print converted ToA and ToT (ns) ============')
        print(aligned_data.head, '\n')
    print("Transform raw codes to time (ns): Done")

    
def main():
    with open('config.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    dir_path = conf['dir_path']
    file_name = conf['file_name']
    plot_dir = dir_path + '/' + file_name + '_plot'
    sub_file_dir = dir_path + '/' + file_name + '_sub_file'
    
    #try:
    #    if not os.path.exists(plot_dir):
    #        os.makedirs(plot_dir)
    #except OSError:
    #    print('Error: Cannot creat plot directory')
    
    raw_data = pd.read_csv(dir_path + '/' + file_name + '.txt', delimiter = '\s+',    header=None, skiprows=1)
    raw_data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'flag', 'day', 'time']
    raw_data = raw_data.drop(['day', 'time'], axis=1)
    print("Read data: Done")
    
    if options.PRINT:
        print('============ Print loaded raw dataset ============')
        print(raw_data.head, '\n')
    
    raw_cal_codes = raw_data[['board', 'cal_code']]
    raw_cal_codes.to_csv(sub_file_dir+'/'+file_name+'_cal_codes.txt', sep='\t', index=None,     header=None)
    print("Save raw cal codes to txt")
    
    aligned_data = raw_data.loc[raw_data['flag'] >= 1]
    aligned_data.reset_index(inplace=True, drop=True)
    print("Exclude flag 0 cases: Done")
    if options.PRINT:
        print('============ Print dataset with hitflag = 1 ============')
        print(aligned_data.head, '\n')
    
    pattern = [0, 1, 3]
    matched = aligned_data.rolling(len(pattern)).apply(lambda x: all(np.equal(x, pattern)),    raw=True)
    # 'raw=True' -> Handle as numpy array instead of Pandas' DataFrame -> Much Faster
    matched = matched.sum(axis = 1).astype(bool)   #Sum to perform boolean OR
    idx_matched = np.where(matched)[0]
    subset = [range(match-len(pattern)+1, match+1) for match in idx_matched]
    aligned_data = pd.concat([aligned_data.iloc[subs,:] for subs in subset], axis = 0)
    aligned_data.reset_index(inplace=True, drop=True)
    print("Check 0, 1, 3 patterns: Done")
    if options.PRINT:
        print('============ Print selected good events (Board Id 0 1 3 aligned) in dataset  ============')
        print(aligned_data.head, '\n')
    aligned_data.drop(['flag'], axis=1, inplace = True)
    
    code_to_time(aligned_data, 146.9, 146.4, 140.7)

    #  Save the selected events to txt file
    aligned_data.to_csv(sub_file_dir+'/'+file_name+'_aligned.txt', sep='\t', index=None,   header=None)
    print("Save the aligend events to txt")


if __name__ == '__main__':
    main()
