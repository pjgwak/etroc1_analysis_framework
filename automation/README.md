# Half-automation for post-processing the raw data 

**You have to use LPC server for this framework.**

### How to use the command
First, you need to setup the python3 environment.  
`source setup.sh`   

To copy raw data to LPC,  
`python3 scpRawDataToLPC.py -d <input dir> -u <username> -n <filename>`  
For example,   
`python3 scpRawDataToLPC.py -d test1 -u jongho -n TDC_Data_PhaseAdj0_F9P5_QSel0_DAC543_F11P5_QSel0_DAC536_F5P9_QSel0_DAC595`  



Sometimes the job can be stopped by an unknown reason, you can restart the job by giving two more options:  
`-r`: restart flag  
`-c <number>`: specify the number where files will be copied  
For example,  
`python3 scpRawDataToLPC.py -d test1 -u jongho -n TDC_Data_PhaseAdj0_F9P5_QSel0_DAC543_F11P5_QSel0_DAC536_F5P9_QSel0_DAC595 -r -c 2`



To convert raw ascii data to readable data, the following command is needed:  
`python3 convertRawDataAutomatic.py -d <input dir> -o <output name>`  
For example,  
`python3 convertRawDataAutomatic.py -d 2022-03-30_Array_Test_Results_F9P5_F11P5_F5P5 -o F9P5_F11P5_F5P5_Beam`  
Even if the job has been killed by an unknown reason, you can put the same command to rerun this script.  




At the end, you need to merge individual output file to one text file.  
`python3 mergeTXT.py -d <input dir> -o <output name>`  
For example,  
`python3 mergeTXT.py -d 2022-03-29_Array_Test_Results_F9P5_F11P5_F5P5 -o F9P5_F11P5_F5P5_Beam`
