from glob import glob
import time
from optparse import OptionParser
import os
import shutil

#####################
### Configure options
parser = OptionParser()
parser.add_option('-d', '--directory', help='directory', dest='directory')
parser.add_option('-u', '--user', help='username', dest='USER')
parser.add_option('-r', '--restart', action='store_true', default=False, dest='RESTART')
parser.add_option('-c', '--count', dest='COUNT')
parser.add_option('-n', '--name', default='TDC_Data_PhaseAdj0_F9P5_QSel0_DAC543_F11P5_QSel0_DAC536_F5P5_QSel0_DAC560', help='name', dest='NAME')
(options, args) = parser.parse_args()
#####################
#####################

ListcopiedRawFiles = []
count = 0
#savedir = '/home/daq/ETROC1/E1Array/1tbHDD/ETROC1/ETROC1_Array_Test_Software_20220228'

if not os.path.exists('temp'):
    os.mkdir('temp')

if options.RESTART:
    cmd = 'ls -v temp/ | tail -n 1'
    var = os.popen(cmd).read()
    num = int(var.split('.')[0].split('_')[-1])
    ListcopiedRawFiles = [n for n in range(num+1)]

if options.COUNT:
    count = int(options.COUNT)

while True:
    ListRawFiles = [x.split('/')[1].split('.')[0].split('_')[-1] for x in glob(options.directory+'/*')]
    #print(ListRawFiles)
    SetRawFiles = set(map(int, ListRawFiles))
    #print(SetRawFiles)
    copiedRawFiles = set(map(int, ListcopiedRawFiles))

    files_to_process = SetRawFiles - copiedRawFiles

    dname = 'dataset_%d'%(count)
    destination = '/uscms_data/d1/'+options.USER+'/ETROC/2022-04-09_Array_Test_Results_F9P5_F11P5_F5P5_HV220/'+dname

    if len(files_to_process) == 0:
        print('No file to copy')
        print('Sleep 1 minutes \n')
        time.sleep(60)
        continue
    else:
        print('\n=============================')
        print('Which dataset?', dname)
        print('=============================')
        for run in files_to_process:
            fname = '%s_%i.dat' % (options.NAME, run)
            cmd = 'scp -p %s/%s %s@cmslpc-sl7.fnal.gov:%s/%s' % (options.directory, fname, options.USER, destination, fname) ## -p option to preserve created time
            #print(cmd)
            os.system(cmd)
            ListcopiedRawFiles.append(run)

        ListcopiedRawFiles = sorted(ListcopiedRawFiles)
        #### Copy the last copied file
        shutil.copy('%s/%s_%i.dat'%(options.directory, options.NAME, ListcopiedRawFiles[-1]), 'temp/')

    count += 1

    #break
    print('\n=========== Sleep 3 minutes ===========')
    print('If you want to stop, please press CTRL + C at this point')
    print('Otherwise the process will be messed up')
    print('========================================\n\n')
    time.sleep(180) ### 3 mins sleep
