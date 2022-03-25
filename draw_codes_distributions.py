import yaml
import pandas as pd
import matplotlib.pyplot as plt
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--plot0', action='store_true', default=False, dest='plotting0')
parser.add_option('--plot1', action='store_true', default=False, dest='plotting1')
parser.add_option('--plot3', action='store_true', default=False, dest='plotting3')
parser.add_option('--plotSum', action='store_true', default=False, dest='plot_summary')
parser.add_option('--plotLimit', action='store_true', default=False, dest='plot_limits')
(options, args) = parser.parse_args()

if not any([options.plotting0, options.plotting1, options.plotting1, options.plotting3, options.plot_summary]):
    error_message = ('\n================================\n'+'Please add at least one option\n'+'--plot0, --plot1, --plot3 or --plotSum\n'+'================================')
    raise ValueError(error_message)
    

def draw_toa_code(ax, input_data, board_number, bDraw=False):
    if ax is not None:
        plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist(data['toa_code'], bins=800, range=[0,800])
    plt.title('Board ' + str(board_number) + ': ToA codes')
    plt.xlabel('ToA codes')
    plt.ylabel('Counts')
    if bDraw:
        plt.show()


def draw_tot_code(ax, input_data, board_number, bDraw=False):
    if ax is not None:
        plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist(data['tot_code'], bins=300, range=[0,300])
    plt.title('Board ' + str(board_number) + ': ToT codes')
    plt.xlabel('ToT codes')
    plt.ylabel('Counts')
    if bDraw:
        plt.show()


def draw_cal_code(ax, read_raw_cal, board_number, bDraw=False):
    if ax is not None:
        plt.sca(ax)
    data = read_raw_cal.loc[read_raw_cal['board'] == board_number]
    plt.hist(data['cal_code'], bins=1000, range=[0,1000], log=True)
    plt.title('Board ' + str(board_number) + ': cal codes')
    plt.xlabel('cal codes')
    plt.ylabel('Counts')
    if bDraw:
        plt.show()


def draw_tot_toa_code(ax, input_data, board_number):
    if ax is not None:
        plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist2d(data['tot_code'], data['toa_code'], cmap=plt.cm.jet, bins=[300,300], range=[[0,300],[0,300]], cmin=1)
    plt.colorbar()
    plt.title('Board ' + str(board_number) + ': ToT vs ToA codes')
    plt.xlabel('ToT codes')
    plt.ylabel('ToA codes')


def draw_toa(ax, input_data, board_number):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist(data['toa'], bins=125, range=[0,12.5])
    plt.title('Board ' + str(board_number) + ': ToA w/o TWC')
    plt.xlabel('ToA (ns)')
    plt.ylabel('Counts')


def draw_tot(ax, input_data, board_number,bTdc=False):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist(data['tot'], bins=200, range=[0,20])
    plt.title('Board ' + str(board_number) + ': ToT w/o TWC')
    plt.xlabel('ToT (ns)')
    plt.ylabel('Counts')


def draw_tot_toa(ax, input_data, board_number):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist2d(data['tot'], data['toa'], cmap=plt.cm.jet, bins=[200,125], range=[[0,20],[0,12.5]], cmin=1)
    plt.colorbar()
    plt.title('Board ' + str(board_number) + ': ToT vs ToA w/o TWC')
    plt.xlabel('ToT (ns)')
    plt.ylabel('ToA (ns)')


# draw properties of three boards
#def draw_boards(input_data, read_raw_cal):
#    bDraw = False
#    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
#    fig, ax = plt.subplots(3,4, constrained_layout=True, figsize=(1800*px, 1200*px))
#
#    board_number = 0
#    draw_tot_toa_code(ax[0,0], input_data,board_number)
#    draw_toa_code(ax[0,1], input_data,board_number, bDraw)
#    draw_tot_code(ax[0,2], input_data,board_number, bDraw)
#    draw_cal_code(ax[0,3], input_data,board_number, bDraw)
#
#    board_number = 1
#    draw_tot_toa_code(ax[1,0], input_data,board_number, bDraw)
#    draw_toa_code(ax[1,1], input_data,board_number, bDraw)
#    draw_tot_code(ax[1,2], input_data,board_number, bDraw)
#    draw_cal_code(ax[1,3], input_data,board_number, bDraw)
#
#    board_number = 3
#    draw_tot_toa_code(ax[2,0], input_data,board_number, bDraw)
#    draw_toa_code(ax[2,1], input_data,board_number, bDraw)
#    draw_tot_code(ax[2,2], input_data,board_number, bDraw)
#    draw_cal_code(ax[2,3], input_data,board_number, bDraw)
#    #plt.savefig('plots/board'+ str(board_number) + '_properties.png')
#    plt.savefig('plots/raw_codes_summary.png')


def draw_board(board_number, input_data, read_raw_cal, plot_dir):
    bDraw = False
    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    fig, ax = plt.subplots(2,4, constrained_layout=True, figsize=(1600*px, 800*px))
    
    draw_tot_toa_code(ax[0,0], input_data,board_number)
    draw_toa_code(ax[0,1], input_data,board_number, bDraw)
    draw_tot_code(ax[0,2], input_data,board_number, bDraw)
    # cal codes passing hit flag 1
    draw_cal_code(ax[0,3], read_raw_cal,board_number, bDraw)
    
    draw_tot_toa(ax[1,0], input_data,board_number)
    draw_toa(ax[1,1], input_data,board_number)
    draw_tot(ax[1,2], input_data,board_number)
    # cal code passign hit flag1 and 0, 1 and 3 pattern
    #draw_cal_code(ax[1,3], input_data,board_number)

    plt.savefig(plot_dir + '/board'+ str(board_number) + '_plot1.png')


def main():
    with open('config.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    dir_path = conf['dir_path']
    file_name = conf['file_name']
    plot_dir = dir_path + '/' + file_name + '_plot'
    sub_file_dir = dir_path + '/' + file_name + '_sub_file'
    
    read_data = pd.read_csv(sub_file_dir+'/'+file_name+'.txt', delimiter = '\s+', header=None)
    read_data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'toa', 'tot']
    read_raw_cal = pd.read_csv(sub_file_dir+'/'+file_name+'_cal_codes.txt', delimiter = '\s+', header=None)
    read_raw_cal.columns = ['board', 'cal_code']
    print("Read data: Done")
    
    if options.plotting0:
        draw_toa_code(None, read_data, 0, True)
        draw_tot_code(None, read_data, 0, True)
        draw_cal_code(None, read_raw_cal, 0, True)
        
    if options.plotting1:
        draw_toa_code(None, read_data, 1, True)
        draw_tot_code(None, read_data, 1, True)
        draw_cal_code(None, read_raw_cal, 1, True)
        
    if options.plotting3:
        draw_toa_code(None, read_data, 3, True)
        draw_tot_code(None, read_data, 3, True)
        draw_cal_code(None, read_raw_cal, 3, True)
    
    if options.plot_summary:
        for board_number in [0, 1, 3]:
            draw_board(board_number, read_data, read_raw_cal, plot_dir)
    

if __name__ == '__main__':
    main()
