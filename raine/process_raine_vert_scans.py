import warnings
import pyart
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticks 
from datetime import date
from datetime import time
from datetime import timedelta
import pandas as pd

import glob
import gc
import copy
import os
import scipy as scipy
import sys

warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=FutureWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

sys.path.append("/home/users/lbennett/lindsay/bin/")
import calib_functions

plt.switch_backend('agg')

#Location of weather station text files with daily rain amounts
wxdir = '/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-aws-2/incoming/raine/NOAA/'

#Directory for radar data
raddir = '/gws/nopw/j04/ncas_radar_vol2/data/xband/raine/cfradial/uncalib_v1_new/vert/'
dates = os.listdir(raddir)
dates.sort()

#Directory for processed data
outdir = '/gws/nopw/j04/ncas_radar_vol2/data/xband/raine/calibrations/ZDRcalib/'

#Directory for logs
logdir = '/gws/nopw/j04/ncas_radar_vol2/data/xband/raine/calibrations/ZDRcalib/logs'
success_dir = os.path.join(logdir,'success')
no_rain_dir = os.path.join(logdir,'no_rain')

if not os.path.exists(logdir):
    os.makedirs(logdir)
if not os.path.exists(success_dir):
    os.makedirs(success_dir)
if not os.path.exists(no_rain_dir):
    os.makedirs(no_rain_dir)

#For each day of radar data, look to see if rain was observed by the weather station at the site. 
#If yes, then process the vertical scans to calculate a value of ZDR and an estimate of the height of the melting layer. 
#Save melting layer height and zdr values to file. Save a success file. 

date = sys.argv[1]
print date
plot = int(sys.argv[2])

file = os.path.join(outdir, date, 'day_ml_zdr.csv')

success_file = os.path.join(success_dir, date+'_ml_zdr.txt')
no_rain_file = os.path.join(no_rain_dir, date+'_no_rain.txt')
#print success_file, no_rain_file

#If there is no success file and no no_rain file, then nothing has been processed, so carry on script to process the data

if not os.path.exists(success_file) and not os.path.exists(no_rain_file):
         
    #Construct the NOAA filename based on the date
    nfile = [wxdir + 'NOAA-' + date[0:4] + '-' + date[4:6] + '.txt']
    #print nfile
    #extract the day
    day = date[6:8]
    
    #Use pandas read_table to read the text file into a table to extract the rain amount
    data = pd.read_table(nfile[0], sep='\s+', header=6)
    #Set the index column
    data2 = data.set_index("DAY")
    #Extract rain amount for the current day
    rain = data2.loc[day,"RAIN"]
    
    #If there was less than 1mm of rain, go to the next day
    if rain < 1.0 or np.isfinite(rain)==False:
	f=open(no_rain_file,'w')
	f.write("")
	f.close()
    #Otherwise process the day's data
    else:
        if calib_functions.process_zdr_scans(outdir,raddir,date,file,plot):       
	    f=open(success_file,'w')
	    f.write("")
	    f.close()
	    print date+' succesfully processed'		
        else:
	    f=open(no_rain_file,'w')
            f.write("")
            f.close()
            print date+'not enough data to process'	
