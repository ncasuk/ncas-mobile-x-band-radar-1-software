import pyart
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticks 
from datetime import date
from datetime import time
from datetime import timedelta
import pandas as pd

import warnings
import glob
import gc
import copy
import os
import scipy as scipy

import sys

sys.path.append("/gws/nopw/j04/ncas_radar_vol1/lindsay/bin/")

import calib_functions

plt.switch_backend('agg')

warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

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

#list only date directories
proc_dates = [os.path.basename(x) for x in glob.glob(outdir+'20*')]

#For each date where the vertical scans have already been processed (i.e. each day with suitable amount of rain), we now want to calculate hourly values of melting layer height (and hourly ZDR)
for date in proc_dates[0:]:
    print date
    success_file = os.path.join(success_dir, date+'_hourly_ml_zdr.txt')
    no_rain_file = os.path.join(no_rain_dir, date+'_no_hourly_rain.txt')

#If there is no 'success' file and no 'no_rain' file, then nothing has been processed, so carry on to process the data
    if not os.path.exists(success_file) and not os.path.exists(no_rain_file):

        if calib_functions.calc_hourly_ML(outdir,date):
 	    f=open(success_file,'w')
	    f.write("")
	    f.close()
	else:
            f=open(no_rain_file,'w')
	    f.write("")
	    f.close()
