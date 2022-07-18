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
(options, args) = parser.parse_args()

def poly3(x, a, b, c, d):
    return a*x**3 + b*x**2 + c*x + d

class Painter:
    def __init__(self):
        pass

    def set_path(self, plot_dir, sub_file_dir, pixel):
        self.plot_dir = plot_dir
        self.sub_file_dir = sub_file_dir
        self.pixel = pixel

    def read_data_files(self):
        li = []

        file_list = glob.glob(self.sub_file_dir + '/*DAC'+str(options.dac)+'*_time.txt')
        file_list.sort()

        for ifile in file_list:
            print('Read file: %s' % (ifile.split('/')[2]))
            df = pd.read_csv(ifile, sep='\t', header=None, usecols=[3,4])
            li.append(df)

        frame = pd.concat(li, axis=0, ignore_index=True)
        frame.columns=['tot', 'toa']
        self.frame = frame

    def timewalk(self):
        fig, ax = plt.subplots(figsize=(8, 8), constrained_layout=True)
        hh = ax.hist2d(self.frame['tot'], self.frame['toa'], bins=[50,16], range=[[1.5,4.0],[8.2,9.0]], cmin=1)
        ax.set_xlabel('TOT (ns)', fontsize=13)
        ax.set_ylabel('TOA (ns)', fontsize=13)
        ax.grid()
        fig.colorbar(hh[3], ax=ax)

        popt, _ = curve_fit(poly3, self.frame['tot'], self.frame['toa'])
        x = np.linspace(2.0, 3.5, num=150)
        ax.plot(x, poly3(x, *popt), 'r--')

        fig.savefig(self.plot_dir + '/pixel'+ str(self.pixel) + '_DAC' + str(options.dac) + '_TWC_fullDataSet_2Dfit.png', dpi=300)

        return popt

    def compareTOA(self, popt):
        file_list = glob.glob(self.sub_file_dir + '/*DAC'+str(options.dac)+'*_time.txt')
        file_list.sort()

        q = [15, 20, 25, 30]

        fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9), constrained_layout=True)
        for cnt, ifile in enumerate(file_list):
            print('Read file: %s for draw TOA' % (ifile.split('/')[2]))
            df = pd.read_csv(ifile, sep='\t', header=None, usecols=[3,4])
            df.columns=['tot', 'toa']
            df['corrToa'] = df['toa'] - poly3(df['tot'], *popt)

            mean1, std1 = df['toa'].mean(), df['toa'].std()
            mean2, std2 = df['corrToa'].mean(), df['corrToa'].std()

            ax1.hist(df['toa'], bins=75, range=(8.0, 9.5), histtype='step', label='mean = %.3g\nstd = %.3g'%(mean1,std1))
            ax1.set_xlabel('TOA before TWC (ns)', fontsize=13)
            ax1.legend(loc='best')

            ax2.hist(df['corrToa'], bins=50, range=(-0.5, 0.5), histtype='step', label='mean = %.3g\nstd = %.3g'%(mean2,std2))
            ax2.set_xlabel('TOA after TWC (ns)', fontsize=13)
            ax2.legend(loc='best')

            fig1.savefig(self.plot_dir + '/pixel'+ str(self.pixel) + '_q' + str(q[cnt]) + '_DAC' + str(options.dac) + '_TWC_TOA_fullDataset.png', dpi=300)

            ax1.cla()
            ax2.cla()

def main():

    with open('config.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    dir_path = conf['dir_path']
    DAC_value = conf['DAC_value']
    pixel = conf['pixel']
    plot_dir = dir_path + '/plot'
    sub_file_dir = dir_path + '/sub_file'

    my_painter = Painter()
    my_painter.set_path(plot_dir, sub_file_dir, pixel)
    my_painter.read_data_files()
    popt = my_painter.timewalk()
    my_painter.compareTOA(popt)

if __name__ == '__main__':
    main()
