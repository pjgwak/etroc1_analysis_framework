import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from optparse import OptionParser
from scipy import optimize as opt

def cut_date(data):
    '''
    On development
    '''
    return 0

def poly1(x, a, b):
    return a*x + b

#  def

def process_data(Q_value = 5):
    # Make file list -> Use config file?
    folder_path = '2021-06-09_SinglePixel_Test_Results/Jitter_Performance_P16_QInj=1M25_internal_DAC_PreampOutOn'
    DAC_range = [260, 360]
    DAC_value = DAC_range[0]
    file_list = glob.glob(folder_path + '/*_QSel=' + str(Q_value) + '_*.dat')
    file_list.sort()
   
    result_list = []

    for filename in file_list:
        # is file empty?
        if os.stat(filename).st_size == 0:
            nHit = 0
            TOA_code_mean = 0 
            TOT_code_mean = 0
            Cal_code_mean = 0
            TOA_rms = 0

            sub_list = [DAC_value, nHit, TOA_code_mean, TOT_code_mean, Cal_code_mean, TOA_rms]
            result_list.append(sub_list)
            DAC_value += 2
        else:
            data = pd.read_csv(filename, delimiter = '\s+', header=None)
            data.columns = ['toa_code', 'tot_code', 'cal_code', 'hit_flag']
            nHit = len(data.index)
            TOA_code_mean = data['toa_code'].mean()
            TOT_code_mean = data['tot_code'].mean()
            Cal_code_mean = data['cal_code'].mean()

            #  fbins = 3.125 / Cal_code_mean
            #  data['fbins'] = 3.125 / data['cal_code']
            #  data['toa'] = 12.5 - data['toa_code'] * data['fbins']
            fbins = 3.125 / Cal_code_mean
            data['toa'] = 12.5 - data['toa_code'] * fbins
            #  data['tot'] = (data['tot_code']*2 - np.floor(data['tot_code']/32.)) * fbins
            TOA_rms = data['toa'].std()

            #  TOA_rms = np.sqrt(np.mean((TOA_mean-data['toa'])**2))
            #  print(TOA_code_mean)
            #  print(TOT_code_mean)
            #  print(Cal_code_mean)
            #  print(TOA_rms)

            sub_list = [DAC_value, nHit, TOA_code_mean, TOT_code_mean, Cal_code_mean, TOA_rms]
            result_list.append(sub_list)
            DAC_value += 2

    # create the file to gather data (Always overwrite)
    with open('q' + str(Q_value) + '_test.txt', 'w+') as f:
        for sub_list in result_list:
            for ele in sub_list:
                f.write(str(ele))
                f.write('\t')
            f.write('\n')

def draw_plots():
    data_Q5 = pd.read_csv('q5_test.txt', delimiter = '\s+', header=None)
    data_Q10 = pd.read_csv('q10_test.txt', delimiter = '\s+', header=None)
    data_Q15 = pd.read_csv('q15_test.txt', delimiter = '\s+', header=None)
    data_Q20 = pd.read_csv('q20_test.txt', delimiter = '\s+', header=None)
    data_Q5.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
    data_Q10.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
    data_Q15.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
    data_Q20.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
    
    # Draw DAC-Hits 
    DAC_range = [data_Q5['DAC_value'].min(), data_Q5['DAC_value'].max()]
    nBin = data_Q5['DAC_value'].max() - data_Q5['DAC_value'].min() + 1
    #  plt.plot(data_Q5['DAC_value'], data_Q5['nHit'])
    plt.plot(data_Q5['DAC_value'], data_Q5['nHit'], 'r--', \
            data_Q10['DAC_value'], data_Q10['nHit'], 'b--', \
            data_Q15['DAC_value'], data_Q15['nHit'], 'y--', \
            data_Q20['DAC_value'], data_Q20['nHit'], 'g--')
    plt.show()
    plt.clf()


    # Find noise peak
    # Get inddex of maximun of nHit
    # And get corresponding DAC_value
    peak_Q5 = data_Q5['DAC_value'][data_Q5['nHit'].idxmax()]
    peak_Q10 = data_Q10['DAC_value'][data_Q10['nHit'].idxmax()]
    #  print(data_Q5['DAC_value'][data_Q5['nHit'].idxmax()])

    # Find last point of signal
    # Get maximum DAC_value which has non-zero nHit
    last_Q5 = data_Q5['DAC_value'].loc[data_Q5['nHit'] != 0].max()
    last_Q10 = data_Q10['DAC_value'].loc[data_Q10['nHit'] != 0].max()
    last_Q15 = data_Q15['DAC_value'].loc[data_Q15['nHit'] != 0].max()
    last_Q20 = data_Q20['DAC_value'].loc[data_Q20['nHit'] != 0].max()
    last_points = np.asarray([last_Q5, last_Q10, last_Q15, last_Q20])
    q_list = np.asarray([5, 10, 15, 20])
    qx_temp = np.arange(0,25,1)
    #  print(last_Q5)
    
    '''
    # Find noise region
    # Use 5 fC case (closest to noise level)
    peak_idx = data_Q5['nHit'].idxmax()
    def gauss(x, a, x0, sigma):
        return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))
    gauss_x = data_Q5['DAC_value'][peak_idx-5:peak_idx+10].values
    gauss_x = gauss_x.astype(float)
    gauss_y = data_Q5['nHit'][peak_idx-5:peak_idx+10].values
    gauss_y = gauss_y.astype(float)
    print(gauss_x)
    print(gauss_y)
    par, _ = opt.curve_fit(gauss, gauss_x, gauss_y, x0=peak_Q5)
    print(par)
    '''

    # Fit and draw S curve
    popt, _ = opt.curve_fit(poly1, q_list, last_points)
    plt.plot(qx_temp, poly1(qx_temp, *popt), 'r--', label='fit: a=%.3f, b=%.3f' % tuple(popt))

    plt.plot(q_list, last_points, 'bo')
    plt.xlim(0,25)
    plt.ylim(last_points[0]-20, last_points[-1]+20)
    plt.fill([0,0,25,25],[peak_Q5, peak_Q10, peak_Q10, peak_Q5], color='lightgray', alpha=0.8)
    plt.legend()
    #  plt.show()
    plt.clf()


    # Draw DAC-TOA rms
    y_rms = data_Q5['TOA_rms'].values
    y_rms[y_rms == 0] = np.nan
    plt.plot(data_Q5['DAC_value'], y_rms, 'ro')
    #  plt.show()
    #  print(data_Q5['TOA_rms'])


def main():
    for charge in [5, 10, 15, 20]:
        process_data(charge)
    draw_plots() 


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
