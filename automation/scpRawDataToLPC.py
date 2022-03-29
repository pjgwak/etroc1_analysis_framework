from glob import glob
import time
from optparse import OptionParser
import os

#####################
### Configure options
parser = OptionParser()
parser.add_option('-d', '--directory', help='directory', dest='directory')
parser.add_option('-u', '--user', help='username', dest='USER')
(options, args) = parser.parse_args()
#####################
#####################

ListcopiedRawFiles = []
count = 0
#savedir = '/home/daq/ETROC1/E1Array/1tbHDD/ETROC1/ETROC1_Array_Test_Software_20220228'

while True:
    ListRawFiles = [x.split('/')[1].split('.')[0].split('_')[-1] for x in glob(options.directory+'/*')]
    #print(ListRawFiles)
    SetRawFiles = set(map(int, ListRawFiles))
    #print(SetRawFiles)
    copiedRawFiles = set(map(int, ListcopiedRawFiles))

    files_to_process = SetRawFiles - copiedRawFiles

    dname = 'dataset%d'%(count)
    destination = '/uscms_data/d1/'+options.USER+'/ETROC/2022-03-28_Array_Test_Results/'+dname
    for run in files_to_process:
        fname = 'TDC_Data_PhaseAdj0_F9P5_QSel0_DAC543_F11P5_QSel0_DAC536_F5P9_QSel0_DAC595_%i.dat' % run
        cmd = 'scp %s/%s %s@cmslpc-sl7.fnal.gov:%s/%s' % (dname, fname, options.USER, destination, fname)
        #print(cmd)
        os.system(cmd)
        ListcopiedRawFiles.append(run)

    count += 1

    #break
    time.sleep(1800) ### 30 mins sleep
