#!/bin/bash

source /cvmfs/sft.cern.ch/lcg/views/LCG_96python3/x86_64-centos7-gcc8-opt/setup.sh
export PYTHONPATH=~/.local/lib/python3.6/site-packages:$PYTHONPATH
export PYTHONPATH=$PWD/analysis:$PYTHONPATH
export PYTHONWARNINGS="ignore"
