from glob import glob
import time
from optparse import OptionParser
import os
import shutil
from natsort import natsorted

#####################
### Configure options
parser = OptionParser()
parser.add_option('-d', '--directory', help='directory', dest='directory')
parser.add_option('-n', '--name', default='TDC_Data_PhaseAdj0_F9P5_QSel0_DAC543_F11P5_QSel0_DAC536_F5P5_QSel0_DAC560', help='name', dest='NAME')
(options, args) = parser.parse_args()
#####################
#####################

cwd = os.getcwd()
count = 0
finishedDirs = []

#2022-03-29_Array_Test_Results_F9P5_F11P5_F5P5/dataset_46

while True:
    print('Base directory is %s'%(cwd))
    ListDirs = [x.split('/')[-1].split('_')[-1] for x in glob(options.directory+'/*_*[!.txt]')]
    print(ListDirs)
    setListDirs = set(map(int, ListDirs))
    setDoneDirs = set(map(int, finishedDirs))
    dirs_to_process = setListDirs - setDoneDirs
    print(dirs_to_process, '\n')
    for idir in dirs_to_process:

        targetDir = '%s/dataset_%d'%(options.directory, idir)

        ### Copy converting script into the directory
        shutil.copy('Data_Analyze1.0.flex.timestemp.py', targetDir+'/')
        #print('Copy Data_Analyze1.0.flex.timestemp.py %s/' %(targetDir))

        ListFiles = [f for f in os.listdir(targetDir)]
        ListFiles = natsorted(ListFiles, key=lambda y: y.lower())
        #print(ListFiles[1], ListFiles[-1])
        if '.py' in ListFiles[0]:
            minIdx, maxIdx = ListFiles[1].split('.')[0].split('_')[-1], ListFiles[-1].split('.')[0].split('_')[-1]
        else:
            minIdx, maxIdx = ListFiles[0].split('.')[0].split('_')[-1], ListFiles[-1].split('.')[0].split('_')[-1]
        print('Min:', minIdx, 'Max:', maxIdx)

        #### Move to the directory where the actual code will run
        os.chdir(targetDir)
        print('I am here! %s'%(os.getcwd()))

        cmd = 'python3 Data_Analyze1.0.flex.timestemp.py %s %s %s > ../F9P5_F11P5_F5P5_Beam_%i.txt'%(minIdx, maxIdx, options.NAME, count)
        print(cmd)
        tic = time.time()
        os.system(cmd)
        dt = dt = time.time() - tic
        print('total time: ',dt/60, '\n')
        finishedDirs.append(idir)

        #### Back to base dir
        os.chdir(cwd)
        count += 1

    #break
    time.sleep(600) ### 10 mins sleep
