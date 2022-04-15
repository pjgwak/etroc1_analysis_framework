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
    folder_path = '2022-04-14_Array_Test_Results/Jitter_Performance_P5_QInj=1M25_external_PhaseAdj0_F27_DiscriOn_QInjEnable_PreBuffOff_DACScan'
    DAC_value = 320 # Start value of DAC
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

class Painter:
    def __init__(self):
        self.read_data_files()
    
    def read_data_files(self):
        self.data_Q5 = pd.read_csv('q5_test.txt', delimiter = '\s+', header=None)
        self.data_Q10 = pd.read_csv('q10_test.txt', delimiter = '\s+', header=None)
        self.data_Q15 = pd.read_csv('q15_test.txt', delimiter = '\s+', header=None)
        self.data_Q20 = pd.read_csv('q20_test.txt', delimiter = '\s+', header=None)
        self.data_Q25 = pd.read_csv('q25_test.txt', delimiter = '\s+', header=None)
        self.data_Q30 = pd.read_csv('q30_test.txt', delimiter = '\s+', header=None)
        self.data_Q5.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
        self.data_Q10.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
        self.data_Q15.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
        self.data_Q20.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
        self.data_Q25.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
        self.data_Q30.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']


    def draw_DAC_hit(self):
        # Draw DAC-Hits
        DAC_range = [self.data_Q5['DAC_value'].min(), self.data_Q5['DAC_value'].max()]
        nBin = self.data_Q5['DAC_value'].max() - self.data_Q5['DAC_value'].min() + 1
        #  plt.plot(self.data_Q5['DAC_value'], self.data_Q5['nHit'])
        plt.plot(self.data_Q5['DAC_value'], self.data_Q5['nHit'], 'ro--', \
                self.data_Q10['DAC_value'], self.data_Q10['nHit'], 'bs--', \
                self.data_Q15['DAC_value'], self.data_Q15['nHit'], 'y^--', \
                self.data_Q20['DAC_value'], self.data_Q20['nHit'], 'g*--', \
                self.data_Q25['DAC_value'], self.data_Q25['nHit'], 'o--',\
                self.data_Q30['DAC_value'], self.data_Q30['nHit'], 'p--'
                )
        plt.show()
    
    def find_noise_region(self):
        data = self.data_Q5.diff()
        peak_idx = data['nHit'].nlargest(2).index.values
        self.first_peak_DAC = self.data_Q5['DAC_value'][peak_idx[0]]
        self.second_peak_DAC = self.data_Q5['DAC_value'][peak_idx[1]]
        plt.plot(self.data_Q5['DAC_value'], data['nHit'], 'ro--')
        plt.show()

    def draw_S_curve(self):
        # Find last point of signal
        # Get maximum DAC_value which has non-zero nHit
        last_Q5 = self.data_Q5['DAC_value'].loc[self.data_Q5['nHit'] != 0].max()
        last_Q10 = self.data_Q10['DAC_value'].loc[self.data_Q10['nHit'] != 0].max()
        last_Q15 = self.data_Q15['DAC_value'].loc[self.data_Q15['nHit'] != 0].max()
        last_Q20 = self.data_Q20['DAC_value'].loc[self.data_Q20['nHit'] != 0].max()
        last_Q25 = self.data_Q25['DAC_value'].loc[self.data_Q25['nHit'] != 0].max()
        last_Q30 = self.data_Q30['DAC_value'].loc[self.data_Q30['nHit'] != 0].max()
        last_points = np.asarray([last_Q5, last_Q10, last_Q15, last_Q20, last_Q25, last_Q30])
        q_list = np.asarray([5, 10, 15, 20, 25, 30])
        qx_temp = np.arange(0,33,1)
        #  print(last_Q5)

        # Fit and draw S curve
        popt, _ = opt.curve_fit(poly1, q_list, last_points)
        plt.plot(qx_temp, poly1(qx_temp, *popt), 'r--', label='fit: a=%.3f, b=%.3f' % tuple(popt))
    
        plt.plot(q_list, last_points, 'bo')
        plt.xlim(0,33)
        plt.ylim(self.first_peak_DAC-10, last_points[-1]+20)
        plt.fill([0,0,33,33],[self.first_peak_DAC, self.second_peak_DAC, self.second_peak_DAC, self.first_peak_DAC], color='lightgray', alpha=0.8)
        plt.legend()
        plt.show()
        #plt.clf()
        

    def draw_DAC_TOA_rms(self):
        '''
        # Draw DAC-TOA rms
        y_rms = self.data_Q5['TOA_rms'].values
        y_rms[y_rms == 0] = np.nan
        plt.plot(self.data_Q5['DAC_value'], y_rms, 'ro')
        #  plt.show()
        #  print(self.data_Q5['TOA_rms'])
        '''
        pass
        

def main():
    for charge in [5, 10, 15, 20, 25, 30]:
        process_data(charge)
    my_painter = Painter()
    my_painter.draw_DAC_hit()
    my_painter.find_noise_region()
    my_painter.draw_S_curve()
    


if __name__ == '__main__':
    main()
