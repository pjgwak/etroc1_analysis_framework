import os
import glob
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from optparse import OptionParser
from scipy.optimize import curve_fit
import scipy.stats as stats

parser = OptionParser()
parser.add_option("--dac", help="DAC value", dest="dac", default="418")
parser.add_option("--laser", help="laser", dest="laser", default="15")
parser.add_option("--cut", help="CAL code cut", dest="cut", action="store_true")
(options, args) = parser.parse_args()

def poly3(x, a, b, c, d):
    return a*x**3 + b*x**2 + c*x + d

def process_data(Q_value, dir_path, DAC_value):
    sub_file_dir = dir_path + '/sub_file'
    file_list = glob.glob(dir_path + '/*_LaserAttenuation=' + str(Q_value) + '_*.dat')
    file_list.sort()

    result_list = []

    for filename in file_list:

        fsize = os.stat(filename).st_size
        #if (fsize < 42000 or fsize > 44000):
        if (fsize < 21000 or fsize > 23000):
            continue
        dac = filename.split('=')[9].split('_')[0]
        charge = filename.split('=')[3].split('_')[0]
        #print(charge, dac)

        data = pd.read_csv(filename, delimiter = '\s+', header=None)
        data.columns = ['toa_code', 'tot_code', 'cal_code', 'hit_flag']
        cal = data['cal_code'].to_numpy()
        mVal = np.bincount(cal).argmax() ## Find most frequent value
        data = data.loc[(data['cal_code'] >= mVal-10) & (data['cal_code'] <= mVal+10)]
        data.reset_index(inplace=True, drop=True)

        if options.cut:
            ## +- 2 cal code window
            data = data.loc[(data['cal_code'] >= mVal-2) & (data['cal_code'] <= mVal+2)]
            data.reset_index(inplace=True, drop=True)

        Cal_code_mean = data['cal_code'].mean()

        fbins = 3.125 / Cal_code_mean
        data['tot'] = (data['tot_code']*2 - np.floor(data['tot_code']/32.)) * fbins
        data['toa']= 12.5 - data['toa_code'] * fbins

        ## Do time walk correction
        ## Temporary
        popt, pcov = curve_fit(poly3, data['tot'], data['toa'])
        data['corrToa'] = data['toa'] - poly3(data['tot'], *popt)

        ## Let's make simple, drop unused columns
        ## create the file to gather data (Always overwrite)
        data = data.drop(['hit_flag'], axis=1)
        data.to_csv(sub_file_dir + '/laser' + str(Q_value) + '_DAC' + str(dac) + '_time.txt', sep='\t', index=None, header=None)

class Painter:
    def __init__(self):
        pass

    def set_path(self, plot_dir, sub_file_dir, pixel):
        self.plot_dir = plot_dir
        self.sub_file_dir = sub_file_dir
        self.pixel = pixel

    def read_data_files(self):
        self.data = pd.read_csv(self.sub_file_dir + '/laser' + str(options.laser) + '_DAC'+ str(options.dac) +'_time.txt', sep='\t', header=None)
        self.data.columns = ['toaCode', 'totCode', 'cal', 'tot', 'toa', 'corrToa']

    def draw_distribution(self):

        ## TOA plots
        ## ax1: code, ax2: time
        fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9), constrained_layout=True)
        mean1, std1 = self.data['toaCode'].mean(), self.data['toaCode'].std()
        mean2, std2 = self.data['toa'].mean(), self.data['toa'].std()

        ax1.hist(self.data['toaCode'], bins=100, range=(80, 180), histtype='step', label='mean = %.3g\nstd = %.3g'%(mean1,std1))
        ax1.set_xlabel('TOA Code', fontsize=13)
        ax1.legend(loc='best')

        ax2.hist(self.data['toa'], bins=75, range=(9.5, 11.0), histtype='step', label='mean = %.3g\nstd = %.3g'%(mean2,std2))
        ax2.set_xlabel('TOA before TWC (ns)', fontsize=13)
        ax2.legend(loc='best')

        fig1.savefig(self.plot_dir + '/pixel'+ str(self.pixel) + '_laser' + str(options.laser) + '_DAC' + str(options.dac) + '_TOA.png', dpi=300)

        ## Clear axes
        ax1.cla()
        ax2.cla()

        ## TOT plot
        ## ax1: code, ax2: time
        mean1, std1 = self.data['totCode'].mean(), self.data['totCode'].std()
        mean2, std2 = self.data['tot'].mean(), self.data['tot'].std()

        ax1.hist(self.data['totCode'], bins=100, range=(50, 150), histtype='step', label='mean = %.3g\nstd = %.3g'%(mean1,std1))
        ax1.set_xlabel('TOT Code', fontsize=13)
        ax1.legend(loc='best')

        ax2.hist(self.data['tot'], bins=100, range=(1.5, 5.5), histtype='step', label='mean = %.3g\nstd = %.3g'%(mean2,std2))
        ax2.set_xlabel('TOT (ns)', fontsize=13)
        ax2.legend(loc='best')

        fig1.savefig(self.plot_dir + '/pixel'+ str(self.pixel) + '_laser' + str(options.laser) + '_DAC' + str(options.dac) + '_TOT.png', dpi=300)

        ## CAL plot
        fig2, ax3 = plt.subplots(figsize=(8, 8), constrained_layout=True)
        min3, max3 = self.data['cal'].min()-4, self.data['cal'].max()+4
        mean3, std3 = self.data['cal'].mean(), self.data['cal'].std()
        ax3.hist(self.data['cal'], bins=(max3-min3+2), range=(min3-1, max3+1), histtype='step', label='mean = %.3g\nsigma = %.3g'%(mean3,std3))
        ax3.set_xlim(min3, max3)
        ax3.set_xlabel('CAL code', fontsize=13)
        ax3.legend(loc='best')
        fig2.savefig(self.plot_dir + '/pixel'+ str(self.pixel) + '_laser' + str(options.laser) + '_DAC' + str(options.dac) + '_CAL.png', dpi=300)

    def timewalk_plot(self):
        fig, ax = plt.subplots(figsize=(8, 8), constrained_layout=True)
        hh = ax.hist2d(self.data['tot'], self.data['toa'], bins=[16,12], range=[[1.8,2.6],[8.4,9.0]], cmin=1)
        ax.set_xlabel('TOT (ns)', fontsize=13)
        ax.set_ylabel('TOA (ns)', fontsize=13)
        ax.grid()
        fig.colorbar(hh[3], ax=ax)

        popt, _ = curve_fit(poly3, self.data['tot'], self.data['toa'])
        #ax.plot(self.data['tot'], poly3(self.data['tot'], *popt), 'r--')
        x = np.linspace(1.8, 2.6, num=120)
        ax.plot(x, poly3(x, *popt), 'r--')
        #min2, max2 = self.data['corrToa'].min()-0.1, self.data['corrToa'].max()+0.1
        #mean2, std2 = self.data['corrToa'].mean(), self.data['corrToa'].std()
        #ax2.hist(self.data['corrToa'], bins=10, histtype='step', label='mean = %.3g\nsigma = %.3g'%(mean2,std2))
        #ax2.set_xlim(min2, max2)
        #ax2.set_xlabel('corrected TOA (ns)', fontsize=13)
        #ax2.legend(loc='best')

        #popt, pcov = curve_fit(poly3, self.data['tot'], self.data['toa'])

        fig.savefig(self.plot_dir + '/pixel'+ str(self.pixel) + '_DAC' + str(options.dac) + '_TDC_2Dfit.png', dpi=300)

    def compareTOA(self):
        fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9), constrained_layout=True)
        mean1, std1 = self.data['toa'].mean(), self.data['toa'].std()
        mean2, std2 = self.data['corrToa'].mean(), self.data['corrToa'].std()

        ax1.hist(self.data['toa'], bins=75, range=(8.0, 9.5), histtype='step', label='mean = %.3g\nstd = %.3g'%(mean1,std1))
        ax1.set_xlabel('TOA before TWC (ns)', fontsize=13)
        ax1.legend(loc='best')

        ax2.hist(self.data['corrToa'], bins=50, range=(-0.5, 0.5), histtype='step', label='mean = %.3g\nstd = %.3g'%(mean2,std2))
        ax2.set_xlabel('TOA after TWC (ns)', fontsize=13)
        ax2.legend(loc='best')

        fig1.savefig(self.plot_dir + '/pixel'+ str(self.pixel) + '_laser' + str(options.laser) + '_DAC' + str(options.dac) + '_TWC_TOA.png', dpi=300)

def main():
    with open('config.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    dir_path = conf['dir_path']
    DAC_value = conf['DAC_value']
    pixel = conf['pixel']
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


    for charge in [8500, 8550, 8600, 8650, 8700]:
        if os.path.exists(sub_file_dir + '/laser' + str(charge) + '_DAC' + str(options.dac) + '_time.txt'):
            print('File (Laser=%s, DAC=%s) already exists' %(str(charge), str(options.dac)))
            continue
        process_data(charge, dir_path, DAC_value)

    my_painter = Painter()
    my_painter.set_path(plot_dir, sub_file_dir, pixel)
    my_painter.read_data_files()
    my_painter.draw_distribution()
    #my_painter.timewalk_plot()
    #my_painter.compareTOA()

if __name__ == '__main__':
    main()
