import yaml
import pandas as pd
pd.options.mode.chained_assignment = None
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize as opt
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--pdf', action='store_true', default=False, dest='PDF')
parser.add_option('--code', action='store_true', help='Select events by code cuts', default=False, dest='CODE')
parser.add_option('--time', action='store_true', help='Select events by time cuts', default=False, dest='TIME')
parser.add_option('-p', '--print', help='Print dataset during execution', action='store_true', default=False, dest='PRINT')
(options, args) = parser.parse_args()

if not any([options.CODE, options.TIME]):
    raise ValueError('Please specify which cut do you want to use --code or --time')


def seperate_cal_code(board_number, data, plot_dir):
    index = len(data)
    # print(index, mod)
    step = int(index / 10)
    mod = index % 10
    lower = 0
    upper = step
    logy = True
    variable = 'cal_code'
    
    for idx in range(0, 10):
        if idx == 9:
            #print(lower, upper+mod)
            temp_data = data[variable][lower:upper+mod].values
        else:
            #print(lower, upper)
            temp_data = data[variable][lower:upper].values

        plt.hist(temp_data, bins=20, range=[120,140])
        #plt.set_xlabel('Cal code', fontsize=13)
        #plt.set_ylabel('# of events', fontsize=13)
        plt.legend(['Number of events: %d'%(temp_data.shape[0])])
        #if logy:
            #plt.set_yscale('log')
        print('{:.4f}'.format(temp_data.mean()))
        
        plt.savefig(plot_dir + '/board'+str(board_number)+'_part'+str(idx)+ '_TWC.png')
        #  plt.clf()
        lower = upper + 1
        upper += step
        

def main():
    with open('config.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    dir_path = conf['dir_path']
    file_name = conf['file_name']
    plot_dir = dir_path + '/' + file_name + '_plot'
    sub_file_dir = dir_path + '/' + file_name + '_sub_file'

    read_data = pd.read_csv(sub_file_dir+'/'+file_name+'.txt', delimiter = '\s+', header=None)
    read_data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'toa', 'tot']
    print("Read data: Done")

    # Make array according to board
    b0_data = read_data.loc[read_data['board'] == 0]
    b0_data.reset_index(inplace=True, drop=True)
    b1_data = read_data.loc[read_data['board'] == 1]
    b1_data.reset_index(inplace=True, drop=True)
    b3_data = read_data.loc[read_data['board'] == 3]
    b3_data.reset_index(inplace=True,drop=True)

    # Make lists for cuts
    # toa_code lower, toa_code upper, tot_code lower, tot_code upper, cal_code lower
    # and cal_code upper limits
    b0v, _ = np.histogram(b0_data['tot_code'], bins=300, range=(0,300))
    b1v, _ = np.histogram(b1_data['tot_code'], bins=300, range=(0,300))
    b3v, _ = np.histogram(b3_data['tot_code'], bins=300, range=(0,300))
    #print(np.argmax(b0v), np.argmax(b1v), np.argmax(b3v))
    # TOA 7 ns = 228, 8 ns = 187, 9 ns = 145, 10 ns = 104
    # Only if Cal code is 130
    b0_cuts = [104, 228, np.argmax(b0v)-22, np.argmax(b0v)+22, 120, 140]
    b1_cuts = [104, 228, np.argmax(b1v)-22, np.argmax(b1v)+22, 120, 140]
    b3_cuts = [104, 228, np.argmax(b3v)-22, np.argmax(b3v)+22, 120, 140]


    ####  ####

    b0v, _ = np.histogram(b0_data['tot'], bins=200, range=(0,20))
    b1v, _ = np.histogram(b1_data['tot'], bins=200, range=(0,20))
    b3v, _ = np.histogram(b3_data['tot'], bins=200, range=(0,20))

    # Check toa, tot cut for events of each boards
    if options.CODE:
        print('============= Select events with code cuts =============')
        b0_data['bCut'] = (b0_data['toa_code'] >= b0_cuts[0]) & (b0_data['toa_code'] <= b0_cuts[1]) & (b0_data['tot_code'] >= b0_cuts[2]) & (b0_data['tot_code'] <= b0_cuts[3]) & (b0_data['cal_code'] >= b0_cuts[4]) & (b0_data['cal_code'] <= b0_cuts[5])
        b1_data['bCut'] = (b1_data['toa_code'] >= b1_cuts[0]) & (b1_data['toa_code'] <= b1_cuts[1]) & (b1_data['tot_code'] >= b1_cuts[2]) & (b1_data['tot_code'] <= b1_cuts[3]) & (b1_data['cal_code'] >= b1_cuts[4]) & (b1_data['cal_code'] <= b1_cuts[5])
        b3_data['bCut'] = (b3_data['toa_code'] >= b3_cuts[0]) & (b3_data['toa_code'] <= b3_cuts[1]) & (b3_data['tot_code'] >= b3_cuts[2]) & (b3_data['tot_code'] <= b3_cuts[3]) & (b3_data['cal_code'] >= b3_cuts[4]) & (b3_data['cal_code'] <= b3_cuts[5])
    elif options.TIME:
        print('============= Select events with time cuts =============')
        print('TOA cuts for the B0 board:', b0_tcuts[:2])
        print('TOA cuts for the B1 board:', b1_tcuts[:2])
        print('TOA cuts for the B3 board:', b3_tcuts[:2], '\n')
        b0_data['bCut'] = (b0_data['toa'] >= b0_tcuts[0]) & (b0_data['toa'] <= b0_tcuts[1]) & (b0_data['tot'] >= b0_tcuts[2]) & (b0_data['tot'] <= b0_tcuts[3]) & (b0_data['cal_code'] >= b0_tcuts[4]) & (b0_data['cal_code'] <= b0_tcuts[5])
        b1_data['bCut'] = (b1_data['toa'] >= b1_tcuts[0]) & (b1_data['toa'] <= b1_tcuts[1]) & (b1_data['tot'] >= b1_tcuts[2]) & (b1_data['tot'] <= b1_tcuts[3]) & (b1_data['cal_code'] >= b1_tcuts[4]) & (b1_data['cal_code'] <= b1_tcuts[5])
        b3_data['bCut'] = (b3_data['toa'] >= b3_tcuts[0]) & (b3_data['toa'] <= b3_tcuts[1]) & (b3_data['tot'] >= b3_tcuts[2]) & (b3_data['tot'] <= b3_tcuts[3]) & (b3_data['cal_code'] >= b3_tcuts[4]) & (b3_data['cal_code'] <= b3_tcuts[5])

    if options.PRINT:
        print(b0_data.loc[b0_data['bCut'] == True])
        print(b1_data.loc[b1_data['bCut'] == True])
        print(b1_data.loc[b3_data['bCut'] == True], '\n')

    # Find good twc events
    # Check event by event, all boards should pass their toa, tot cuts at the same time
    #b0_data['bDelta'] = b0_data['bCut']==True and b1_data['bCut']==True and b3_data['bCut']==True
    b0_data['bTwc'] = (b0_data['bCut']==True) & (b1_data['bCut']==True) & (b3_data['bCut']==True)
    b1_data['bTwc'] = (b0_data['bCut']==True) & (b1_data['bCut']==True) & (b3_data['bCut']==True)
    b3_data['bTwc'] = (b0_data['bCut']==True) & (b1_data['bCut']==True) & (b3_data['bCut']==True)

    if options.PRINT:
        print(b0_data.loc[b0_data['bTwc'] == True])
        print(b1_data.loc[b1_data['bTwc'] == True])
        print(b3_data.loc[b3_data['bTwc'] == True], '\n')

    b0_twc_delta_data = b0_data.loc[b0_data['bTwc'] == True][['toa','tot','cal_code']]
    b1_twc_delta_data = b1_data.loc[b1_data['bTwc'] == True][['toa','tot','cal_code']]
    b3_twc_delta_data = b3_data.loc[b3_data['bTwc'] == True][['toa','tot','cal_code']]

    #seperate_cal_code(0, b0_twc_delta_data, plot_dir)
    seperate_cal_code(1, b1_twc_delta_data, plot_dir)
    #seperate_cal_code(3, b3_twc_delta_data, plot_dir)
    

if __name__ == '__main__':
    main()
