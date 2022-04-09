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
parser.add_option('-o', '--output', default='', help='output name', dest='OUTPUT')
(options, args) = parser.parse_args()
#####################
#####################

cwd = os.getcwd()
#2022-03-29_Array_Test_Results_F9P5_F11P5_F5P5/dataset_46

if not options.OUTPUT:
    raise ValueError('Clarifiy the output name')

if not options.directory:
    raise ValueError('Specifiy the input directory')

print('Base directory is %s'%(cwd))
ListDirs = [x.split('/')[-1].split('_')[-1] for x in glob(options.directory+'/*_*[!.txt]')]
setListDirs = set(map(int, ListDirs))
print(setListDirs, '\n')

for idir in setListDirs:
    output = '%s_%i.txt' %(options.OUTPUT, idir)

    if os.path.exists('%s/%s'%(options.directory, output)):
        print('The directory has already processed, skip %s/dataset_%i' % (options.directory, idir))
        continue

    else:
        targetDir = '%s/dataset_%d'%(options.directory, idir)

        ### Copy converting script into the directory
        shutil.copy('Data_Analyze1.1.flex.timestemp.py', targetDir+'/')
        #print('Copy Data_Analyze1.1.flex.timestemp.py %s/' %(targetDir))

        ListFiles = [f for f in os.listdir(targetDir) if not "Split" in f]

        if len(ListFiles) == 0:
            print('Empty directory !!!!')
            break

        ListFiles = natsorted(ListFiles, key=lambda y: y.lower())
        if '.py' in ListFiles[0]:
            minIdx, maxIdx = ListFiles[1].split('.')[0].split('_')[-1], ListFiles[-1].split('.')[0].split('_')[-1]
        else:
            minIdx, maxIdx = ListFiles[0].split('.')[0].split('_')[-1], ListFiles[-1].split('.')[0].split('_')[-1]
        print('Min:', minIdx, 'Max:', maxIdx, 'how many files will be processed?', int(maxIdx)-int(minIdx)+1)

        #### Move to the directory where the actual code will run
        os.chdir(targetDir)
        print('I am here! %s'%(os.getcwd()))

        cmd = 'python3 Data_Analyze1.1.flex.timestemp.py %s %s %s > ../%s'%(minIdx, maxIdx, options.NAME, output)
        print(cmd)
        tic = time.time()
        os.system(cmd)
        dt = time.time() - tic
        print('Elapsed time: %.3f mins \n' %(dt/60))

    #### Back to base dir
    os.chdir(cwd)

    print('=========== Sleep 5:00 minutes ===========')
    print('If you want to stop, please press CTRL + C at this point')
    print('Otherwise the process will be messed up')
    print('========================================\n\n')
    time.sleep(300)
