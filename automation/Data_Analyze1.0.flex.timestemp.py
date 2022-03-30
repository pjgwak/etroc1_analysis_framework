#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import copy
import time
#import visa
import struct
import socket
#import winsound
import datetime
#import heartrate
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import subprocess
#---------------------------------------------------------------------------------#

min, max = int(sys.argv[1]), int(sys.argv[2])
fileNameString = sys.argv[3]
print("min file index: %.0f, max file index: %.0f"%(min, max))

def runCmdP(cmd, PrinterMode, Nindent=0):
    indent = ""
    for i in range(Nindent):
        indent += "\t"
    #print (indent+">>> "+cmd+"\n")
    if PrinterMode is False :
        popen = subprocess.Popen(cmd.split( ), stdout=subprocess.PIPE)
        return popen

## define main function
def main():
    #for data in range(12400, 12500, 1):
    # 0 to 43817
    for data in range(min, max+1, 1):
        #file_name = "TDC_Data_PhaseAdj0_B1P5_QSel0_DAC518_C0P5_QSel0_DAC541_B2P9_QSel0_DAC556_%d.dat"%data
        file_name = "%s_%d.dat"%(fileNameString, data)
        cmdForTimeStemp = "ls --time-style=full-iso -al %s"%(file_name)
        cmdOut = runCmdP(cmdForTimeStemp, False, 0)
        for line in iter(cmdOut.stdout.readline, ''):
            if (len(line)>0):
                #line = lines.rstrip()
                l = str(line)
                TimeStemp = l[l.find("2022-"):l.find("2022-")+len("2022-02-18 20:47:46")]
                break
        hitFlagCounter = 0
        with open(file_name,'r') as infile, open('%s_Split.%s'%(file_name.split('.')[0], file_name.split('.')[1]), 'w') as outfile:
            for line in infile.readlines():
                TDC_data = []
                for j in range(32):
                    TDC_data += [((int(line.split()[0]) >> j) & 0x1)]
                ID = TDC_data[31] << 1 | TDC_data[30]
                hitFlag = TDC_data[0]
                TOT_Code1 = TDC_data[29] << 8 | TDC_data[28] << 7 | TDC_data[27] << 6 | TDC_data[26] << 5 | TDC_data[25] << 4 | TDC_data[24] << 3 | TDC_data[23] << 2 | TDC_data[22] << 1 | TDC_data[21]
                TOA_Code1 = TDC_data[20] << 9 | TDC_data[19] << 8 | TDC_data[18] << 7 | TDC_data[17] << 6 | TDC_data[16] << 5 | TDC_data[15] << 4 | TDC_data[14] << 3 | TDC_data[13] << 2 | TDC_data[12] << 1 | TDC_data[11]
                Cal_Code1 = TDC_data[10] << 9 | TDC_data[9] << 8 | TDC_data[8] << 7 | TDC_data[7] << 6 | TDC_data[6] << 5 | TDC_data[5] << 4 | TDC_data[4] << 3 | TDC_data[3] << 2 | TDC_data[2] << 1 | TDC_data[1]

                if hitFlag==1 and ID!=2:
                    hitFlagCounter = hitFlagCounter+hitFlag
                    #print("HitFlagCounter: ", hitFlagCounter)
                    print(ID, TOA_Code1, TOT_Code1, Cal_Code1, hitFlag, TimeStemp)
                    #print(TOA_Code1, TOT_Code1, Cal_Code1, hitFlag)
                if ID!=0 or TOA_Code1!=0 or TOT_Code1 !=0 or Cal_Code1!=0 or hitFlag!=0:
                    if ID!=2:
                        outfile.write("%2d %3d %3d %3d %d\n"%(ID, TOA_Code1, TOT_Code1, Cal_Code1,hitFlag))
#---------------------------------------------------------------------------------#
if __name__ == "__main__":
    main() 
