import os
import glob
import yaml
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

def process_data(Q_value, dir_path, DAC_value):
    sub_file_dir = dir_path + '/sub_file'
    file_list = glob.glob(dir_path + '/*_LaserAttenuation=' + str(Q_value) + '_*.dat')
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
    with open(sub_file_dir + '/q' + str(Q_value) + '.txt', 'w+') as f:
        for sub_list in result_list:
            for ele in sub_list:
                f.write(str(ele))
                f.write('\t')
            f.write('\n')

class Painter:
    def __init__(self):
        pass
    
    def set_path(self, plot_dir, sub_file_dir, board, pixel):
        self.plot_dir = plot_dir
        self.sub_file_dir = sub_file_dir
        self.board = board
        self.pixel = pixel
        
    def read_data_files(self):
        self.data_Q5 = pd.read_csv(self.sub_file_dir + '/q8500.txt', delimiter = '\s+', header=None)
        self.data_Q10 = pd.read_csv(self.sub_file_dir + '/q8550.txt', delimiter = '\s+', header=None)
        self.data_Q15 = pd.read_csv(self.sub_file_dir + '/q8600.txt', delimiter = '\s+', header=None)
        self.data_Q20 = pd.read_csv(self.sub_file_dir + '/q8650.txt', delimiter = '\s+', header=None)
        #self.data_Q25 = pd.read_csv(self.sub_file_dir + '/q25.txt', delimiter = '\s+', header=None)
        #self.data_Q30 = pd.read_csv(self.sub_file_dir + '/q30.txt', delimiter = '\s+', header=None)
        self.data_Q5.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
        self.data_Q10.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
        self.data_Q15.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
        self.data_Q20.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
        #self.data_Q25.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']
        #self.data_Q30.columns = ['DAC_value', 'nHit', 'TOA_code_mean', 'TOT_code_mean', 'Cal_code_mean', 'TOA_rms']


    def draw_S_curve(self):
        # Draw DAC-Hits
        DAC_range = [self.data_Q10['DAC_value'].min(), self.data_Q10['DAC_value'].max()]
        nBin = self.data_Q10['DAC_value'].max() - self.data_Q10['DAC_value'].min() + 1
        #  plt.plot(self.data_Q5['DAC_value'], self.data_Q5['nHit'])
        '''
        plt.plot(self.data_Q5['DAC_value'], self.data_Q5['nHit'], 'ro--', \
                self.data_Q10['DAC_value'], self.data_Q10['nHit'], 'bs--', \
                self.data_Q15['DAC_value'], self.data_Q15['nHit'], 'y^--', \
                self.data_Q20['DAC_value'], self.data_Q20['nHit'], 'g*--', \
                self.data_Q25['DAC_value'], self.data_Q25['nHit'], 'o--',\
                self.data_Q30['DAC_value'], self.data_Q30['nHit'], 'p--'
                )
        '''
        plt.title(self.board + 'P' + str(self.pixel) + ' S curve')
        plt.xlabel('DAC')
        plt.ylabel('# of hits')
        plt.plot(self.data_Q5['DAC_value'], self.data_Q50['nHit'], 'g--', \
                self.data_Q10['DAC_value'], self.data_Q10['nHit'], 'ro--', \
                self.data_Q15['DAC_value'], self.data_Q15['nHit'], 'y^--', \
                self.data_Q20['DAC_value'], self.data_Q20['nHit'], 'bs--'
                )
        plt.savefig(self.plot_dir + '/pixel'+ str(self.pixel) + '_S_curve.png', dpi=300)
        #plt.show()
    
    def find_noise_region(self):
        plt.clf()
        data = self.data_Q5.diff()
        peak1 = data['nHit'].nlargest(1).index.values
        peak2 = data['nHit'].nsmallest(1).index.values
        self.first_peak_DAC = self.data_Q5['DAC_value'][peak1[0]]
        self.second_peak_DAC = self.data_Q5['DAC_value'][peak2[0]]
        plt.plot(self.data_Q5['DAC_value'], data['nHit'], 'ro--')
        plt.title(self.board + 'P' + str(self.pixel) + ' noise check')
        plt.xlabel('DAC')
        plt.ylabel('Difference # of hits')
        plt.savefig(self.plot_dir + '/pixel'+ str(self.pixel) + '_noise.png', dpi=300)
        #plt.show()

    def draw_DAC_line(self):
        plt.clf()
        # Find last point of signal
        # Get maximum DAC_value which has non-zero nHit
        last_Q5 = self.data_Q5['DAC_value'].loc[self.data_Q5['nHit'] != 0].max()
        last_Q10 = self.data_Q10['DAC_value'].loc[self.data_Q10['nHit'] != 0].max()
        last_Q15 = self.data_Q15['DAC_value'].loc[self.data_Q15['nHit'] != 0].max()
        last_Q20 = self.data_Q20['DAC_value'].loc[self.data_Q20['nHit'] != 0].max()
        #last_Q25 = self.data_Q25['DAC_value'].loc[self.data_Q25['nHit'] != 0].max()
        #last_Q30 = self.data_Q30['DAC_value'].loc[self.data_Q30['nHit'] != 0].max()
        #last_points = np.asarray([last_Q5, last_Q10, last_Q15, last_Q20, last_Q25, last_Q30])
        #q_list = np.asarray([5, 10, 15, 20, 25, 30])
        #last_points = np.asarray([last_Q15, last_Q20, last_Q25, last_Q30])
        #q_list = np.asarray([15, 20, 25, 30])
        last_points = np.asarray([last_Q5, last_Q10, last_Q15, last_Q20])
        q_list = np.asarray([85, 85.5, 86, 86.5])
        qx_temp = np.arange(0,100,1)
        #  print(last_Q5)

        # Fit and draw S curve
        popt, _ = opt.curve_fit(poly1, q_list, last_points)
        plt.plot(qx_temp, poly1(qx_temp, *popt), 'r--', label='fit: a=%.3f, b=%.3f' % tuple(popt))
    
        plt.plot(q_list, last_points, 'bo')
        plt.xlim(0,100)
        #plt.ylim(self.first_peak_DAC-10, last_points[-1]+20)
        plt.fill([0,0,100,100],[self.first_peak_DAC, self.second_peak_DAC, self.second_peak_DAC, self.first_peak_DAC], color='lightgray', alpha=0.8)
        plt.text(10,(self.second_peak_DAC+self.first_peak_DAC)/2, 'Noise: {:} - {:}'.format(self.first_peak_DAC, self.second_peak_DAC))
        plt.legend()
        plt.title(self.board + 'P' + str(self.pixel) + ' DAC scan')
        plt.xlabel('Attenuation (%)')
        plt.ylabel('DAC')
        plt.savefig(self.plot_dir + '/pixel'+ str(self.pixel) + 'DAC_scan.png', dpi=300)
        #plt.show()
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
    with open('config.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    dir_path = conf['dir_path']
    DAC_value = conf['DAC_value']
    pixel = conf['pixel']
    board = conf['board']
    plot_dir = dir_path + '/plot'
    sub_file_dir = dir_path + '/sub_file'
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
        
        
    #for charge in [5, 10, 15, 20, 25, 30]:
    for charge in [8500, 8550, 8600, 8650]:
        process_data(charge, dir_path, DAC_value)

    my_painter = Painter()
    my_painter.set_path(plot_dir, sub_file_dir, board, pixel)
    my_painter.read_data_files()
    my_painter.draw_S_curve()
    my_painter.find_noise_region()
    my_painter.draw_DAC_line()


if __name__ == '__main__':
    main()
