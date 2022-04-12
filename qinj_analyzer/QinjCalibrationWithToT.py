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
parser = OptionParser()
parser.add_option('-f', '--fit', action="store_true", dest='fit')
(options, args) = parser.parse_args()
#####################
#####################

Qsel = np.arange(5, 32, 1)

def gaus(x,a,x0,sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))

in_names = ['files/TDC_Data_PhaseAdj0_F9P5_QSel%i_DAC543_F11P5_QSel20_DAC536_F5P5_QSel20_DAC560_Split*',
            'files/TDC_Data_PhaseAdj0_F9P5_QSel20_DAC543_F11P5_QSel%i_DAC536_F5P5_QSel20_DAC560_Split*',
            'files/TDC_Data_PhaseAdj0_F9P5_QSel20_DAC543_F11P5_QSel20_DAC536_F5P5_QSel%i_DAC560_Split*'
           ]

out_names = ['files/TDC_Data_PhaseAdj0_F9P5_QSel%i_DAC543_F11P5_QSel20_DAC536_F5P5_QSel20_DAC560.dat',
             'files/TDC_Data_PhaseAdj0_F9P5_QSel20_DAC543_F11P5_QSel%i_DAC536_F5P5_QSel20_DAC560.dat',
             'files/TDC_Data_PhaseAdj0_F9P5_QSel20_DAC543_F11P5_QSel20_DAC536_F5P5_QSel%i_DAC560.dat'
            ]

txt_names = ['files/TDC_Data_PhaseAdj0_F9P5_QSel%i_DAC543.txt',
             'files/TDC_Data_PhaseAdj0_F11P5_QSel%i_DAC536.txt',
             'files/TDC_Data_PhaseAdj0_F5P5_QSel%i_DAC560.txt'
            ]

bID = [0, 1, 3]

##### Merge output #####
for i in range(3):
    for iq in Qsel:
        f = in_names[i] % iq
        output = out_names[i] %iq
        if not os.path.exists(output):
            Listfiles = [x for x in glob(f)]
            Listfiles = natsorted(Listfiles, key=lambda y: y.lower())
            argus = str(' '.join(Listfiles))
            cmd = 'cat %s > %s'%(argus, output)
            print(cmd)
            os.system(cmd)

##### Find patterns and convert to time #####
for i in range(3):
    for iq in Qsel:
        f = out_names[i] % iq
        output = txt_names[i] %iq
        if not os.path.exists(output):
            data = pd.read_csv(f, delimiter = '\s+', header=None)
            data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'flag']
            selected_data = data.loc[data['flag'] == 1]
            selected_data.reset_index(inplace=True, drop=True)
            selected_data = selected_data.loc[selected_data['board'] != bID[i]]
            selected_data.reset_index(inplace=True, drop=True)
            selected_data = selected_data.loc[(selected_data['cal_code'] > 120) & (data['cal_code'] < 140)]
            selected_data.reset_index(inplace=True, drop=True)
            selected_data['tot'] = (selected_data['tot_code'] * 2 - np.floor(selected_data['tot_code'] / 32.)) * (3.125/selected_data['cal_code'])
            selected_data = selected_data.drop(['toa_code', 'tot_code', 'cal_code', 'flag'], axis=1)
            if selected_data.empty:
                print('Selected %s is empty!!' % f)
            else:
                selected_data.to_csv(output, sep='\t', index=None, header=None)


def expoFit(x, a, b, c):
    return a*np.exp(b*x) + c

def poly3(x, a, b, c, d):
    return a*x**3 + b*x**2 + c*x + d

def poly2(x, a, b, c):
    return a*x**2 + b*x**1 + c

##### Draw charge vs. mean TOT #####
for i in range(3):
    fig, ax = plt.subplots(figsize=(10, 8))
    x = np.arange(5, 32, 1)
    y = np.zeros(x.size)
    yerr = np.zeros(x.size)
    for iq in Qsel:
        f = txt_names[i] % iq
        fig1, ax1 = plt.subplots(figsize=(8,8))

        if iq < 9:
            y[iq-5] = np.NaN
            yerr[iq-5] = np.NaN
            continue

        if not os.path.exists(f):
            print('File is not existed')
            print('Use mean value = 0')
            y[iq-5] = np.NaN
            yerr[iq-5] = np.NaN
            continue
        else:
            data = pd.read_csv(f, delimiter = '\s+', header=None)
            data.columns = ['board', 'tot']
            if data.size < 100:
                print('Not enough of number events for fit')
                print('Ignore this point')
                y[iq-5] = np.mean(data['tot'])
                yerr[iq-5] = np.std(data['tot'], ddof=1)
                continue
            if options.fit:
                print('Do Gaussian fit')
                num_bins = 40
                bins, edges = np.histogram(data['tot'], num_bins, range=(0.0, 4.0), density=False)
                centers = 0.5*(edges[1:] + edges[:-1])
                mean, sigma = np.mean(data['tot']), np.std(data['tot'], ddof=1)
                try:
                    popt, _ = curve_fit(gaus, centers, bins, p0=[100, mean, sigma])
                    y[iq-5] = popt[1]
                    yerr[iq-5] = popt[2]
                    ax1.hist(data['tot'], num_bins, range=(0.0, 4.0), density=False)
                    ax1.plot(centers, gaus(centers, *popt), color='red', lw=2)
                    ax1.set_title('Board'+str(bID[i])+'_'+str(iq)+'fC', fontsize=15)
                    ax1.set_xlabel('TOT (ns)', fontsize=15)
                    fig1.savefig('Board'+str(bID[i])+'_'+str(iq)+'fC'+'_gaussianFit.png')
                except:
                    print('Gaussian fit failed!!')
                    y[iq-5] = np.mean(data['tot'])
                    yerr[iq-5] = np.std(data['tot'], ddof=1)
                    ax1.hist(data['tot'], num_bins, range=(0.0, 4.0), density=False)
                    ax1.set_title('Board'+str(bID[i])+'_'+str(iq)+'fC', fontsize=15)
                    ax1.set_xlabel('TOT (ns)', fontsize=15)
                    fig1.savefig('Board'+str(bID[i])+'_'+str(iq)+'fC'+'_gaussianFit.png')
            else:
                if iq < 12:
                    y[iq-5] = np.NaN
                    yerr[iq-5] = np.NaN
                else:
                    y[iq-5] = np.mean(data['tot'])
                    yerr[iq-5] = np.std(data['tot'], ddof=1)

    #try:
    #    popt, _ = curve_fit(expoFit, x[7:] , y[7:])
    #    ax.plot(x[7:], expoFit(x[7:], *popt), color='red', lw=2)
    #except:
    #    print("Fit doesn't work!!")
    ax.errorbar(x, y, yerr=yerr, marker='o', ms=5, mfc='black', mew=0, elinewidth=2)
    ax.set_title('Board '+str(bID[i]), fontsize=15)
    ax.set_xlabel('Charge (fC)', fontsize=15)
    ax.set_xticks(np.arange(5, 33, 1))
    ax.set_ylabel('Mean TOT (ns)', fontsize=15)
    ax.set_ylim(0, 4.5)
    ax.grid()
    fig.savefig('b'+str(bID[i])+'chargeVStot.png')
