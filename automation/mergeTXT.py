from glob import glob
from optparse import OptionParser
import os
from natsort import natsorted

#####################
### Configure options
parser = OptionParser()
parser.add_option('-d', '--directory', help='directory', dest='directory')
parser.add_option('-o', '--output', default='', help='output name', dest='OUTPUT')
(options, args) = parser.parse_args()
#####################
#####################

if not options.OUTPUT:
    raise ValueError('Clarifiy the output name')

if not options.directory:
    raise ValueError('Specifiy the input directory')

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

cmd = 'cat %s > %s/%s.txt'%(argus, options.directory, options.OUTPUT)
print(cmd)
os.system(cmd)
