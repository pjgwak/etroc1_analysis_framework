import pandas as pd
import matplotlib.pyplot as plt

def draw_toa_code(ax, input_data, board_number):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist(data['toa_code'], bins=800, range=[0,800])
    plt.title('Board ' + str(board_number) + ': ToA codes')
    plt.xlabel('ToA codes')
    plt.ylabel('Counts')


def draw_tot_code(ax, input_data, board_number):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist(data['tot_code'], bins=300, range=[0,300])
    plt.title('Board ' + str(board_number) + ': ToT codes')
    plt.xlabel('ToT codes')
    plt.ylabel('Counts')


def draw_cal_code(ax, read_raw_cal, board_number):
    plt.sca(ax)
    data = read_raw_cal.loc[read_raw_cal['board'] == board_number]
    plt.hist(data['cal_code'], bins=40, range=[140,180])
    plt.title('Board ' + str(board_number) + ': cal codes')
    plt.xlabel('cal codes')
    plt.ylabel('Counts')


def draw_tot_toa_code(ax, input_data, board_number):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist2d(data['tot_code'], data['toa_code'], cmap=plt.cm.jet, bins=[300,300], range=[[0,300],[0,300]], cmin=1)
    plt.colorbar()
    plt.title('Board ' + str(board_number) + ': ToT vs ToA codes')
    plt.xlabel('ToT codes')
    plt.ylabel('ToA codes')


def draw_toa(ax, input_data, board_number, bTdc=False):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist(data['toa'], bins=125, range=[0,12.5])
    plt.title('Board ' + str(board_number) + ': ToA')
    plt.xlabel('ToA (ns)')
    plt.ylabel('Counts')


def draw_tot(ax, input_data, board_number,bTdc=False):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist(data['tot'], bins=200, range=[0,20])
    plt.title('Board ' + str(board_number) + ': ToT')
    plt.xlabel('ToT (ns)')
    plt.ylabel('Counts')


def draw_tot_toa(ax, input_data, board_number, bTdc=False):
    plt.sca(ax)
    data = input_data.loc[input_data['board'] == board_number]
    plt.hist2d(data['tot'], data['toa'], cmap=plt.cm.jet, bins=[200,125], range=[[0,20],[0,12.5]], cmin=1)
    plt.colorbar()
    plt.title('Board ' + str(board_number) + ': ToT vs ToA')
    plt.xlabel('ToT (ns)')
    plt.ylabel('ToA (ns)')


# draw properties of a board
def draw_board(input_data, read_raw_cal):
    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    fig, ax = plt.subplots(4,3, constrained_layout=True, figsize=(1600*px, 1600*px))
    
    board_number = 0
    draw_tot_toa_code(ax[0,0], input_data,board_number)
    draw_toa_code(ax[0,1], input_data,board_number)
    draw_tot_code(ax[0,2], input_data,board_number)
    
    board_number = 1
    draw_tot_toa_code(ax[1,0], input_data,board_number)
    draw_toa_code(ax[1,1], input_data,board_number)
    draw_tot_code(ax[1,2], input_data,board_number)

    board_number = 3
    draw_tot_toa_code(ax[2,0], input_data,board_number)
    draw_toa_code(ax[2,1], input_data,board_number)
    draw_tot_code(ax[2,2], input_data,board_number)
    
    plt.savefig('plots/board'+ str(board_number) + '_properties.pdf')
    #plt.show()


def main():
    file_name =     '2021-05-24_Array_Test_Results_B1P9_F11P9_B2P9_Beam_0524_F11HV210'
    
    read_data = pd.read_csv(file_name + '.txt', delimiter = '\s+', header=None)
    read_data.columns = ['board', 'toa_code', 'tot_code', 'cal_code', 'toa',    'tot']
    read_raw_cal = pd.read_csv(file_name + '_cal_codes.txt', delimiter =    '\s+', header=None)
    read_raw_cal.columns = ['board', 'cal_code']
    print("Read data: Done")
    
    draw_board(read_data, read_raw_cal)
    

if __name__ == '__main__':
    main()
