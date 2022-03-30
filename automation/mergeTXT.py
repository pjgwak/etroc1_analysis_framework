from glob import glob
from optparse import OptionParser
import os
from natsort import natsorted

#####################
### Configure options
parser = OptionParser()
parser.add_option('-d', '--directory', help='directory', dest='directory')
(options, args) = parser.parse_args()
#####################
#####################

cwd = os.getcwd()
count = 0
finishedDirs = []

ListFiles = [x for x in glob(options.directory+'/*[!revised].txt')]
ListFiles = natsorted(ListFiles, key=lambda y: y.lower())
print(ListFiles)

### Remove first line of each file and save it
for itxt in ListFiles:
    fname = '%s/%s_revised.txt' % (itxt.split('/')[0], itxt.split('/')[1].split('.')[0])
    #print(fname)
    if not os.path.exists(fname):
        cmd = 'tail -n +2 %s > %s' % (itxt, fname)
        print(cmd)
        os.system(cmd)
    else:
        continue

newListFiles = [x for x in glob(options.directory+'/*revised.txt')]
newListFiles = natsorted(newListFiles, key=lambda y: y.lower())
print(newListFiles)

argus = str(' '.join(newListFiles))

cmd = 'cat %s > %s/F9P5_F11P5_F5P5_Beam.txt'%(argus, options.directory)
print(cmd)
os.system(cmd)
