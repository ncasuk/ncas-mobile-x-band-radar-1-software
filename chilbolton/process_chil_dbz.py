import pyart
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticks 
plt.switch_backend('agg')
from datetime import date
from datetime import time
from datetime import timedelta
import pandas as pd

import warnings
import fileinput
import glob
import gc
import copy
import os
import sys
import scipy as scipy

sys.path.append("/home/users/lbennett/lindsay/bin/")
import calib_functions

warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

zdr_dir = '/gws/nopw/j04/ncas_radar_vol2/data/xband/chilbolton/calibrations/ZDRcalib_2020/'
if not os.path.exists(zdr_dir):
    print "zdr_dir does not exist"
datadir = '/gws/nopw/j04/ncas_radar_vol2/data/xband/chilbolton/cfradial/uncalib_v1/sur/'
if not os.path.exists(datadir):
    print "datadir does not exist"
outdir = '/gws/nopw/j04/ncas_radar_vol2/data/xband/chilbolton/calibrations/Zcalib_2020/phi_files/110620_att/'
#outdir = '/gws/nopw/j04/ncas_radar_vol2/data/xband/chilbolton/calibrations/Zcalib_2020/phi_files/080620_norm/'
if not os.path.exists(outdir):
    os.makedirs(outdir)

#Directory for logs
logdir = '/gws/nopw/j04/ncas_radar_vol2/data/xband/chilbolton/calibrations/Zcalib_2020/logs'
success_dir = os.path.join(logdir,'success_att')
no_rays_dir = os.path.join(logdir,'no_rays_att')
#success_dir = os.path.join(logdir,'success_norm')
#no_rays_dir = os.path.join(logdir,'no_rays_norm')

if not os.path.exists(logdir):
    os.makedirs(logdir)
if not os.path.exists(success_dir):
    os.makedirs(success_dir)
if not os.path.exists(no_rays_dir):
    os.makedirs(no_rays_dir)

date = sys.argv[1]
print date
success_file = os.path.join(success_dir, date+'.txt')
no_rays_file = os.path.join(no_rays_dir, date+'.txt')

#If there is a success file or a no_rays file, write out to log file
if os.path.exists(success_file):
    print "already processed, success file found"
elif os.path.exists(no_rays_file):
    print "already processed, no_rays file found"

#If there is no 'success' file and no 'no_rays' file, then nothing has been processed, so carry on to process the data
if not os.path.exists(success_file) and not os.path.exists(no_rays_file):
    print "no success or no_rays file found"
    mlfile = os.path.join(zdr_dir, date, 'hourly_ml_zdr.csv')
    if os.path.exists(mlfile):
        print "found ml_file, processing data"
        ml_zdr = pd.read_csv(mlfile,index_col=0, parse_dates=True)
        raddir = os.path.join(datadir, date)
        #print raddir, outdir, date
        #if calib_functions.calibrate_day_norm(raddir, outdir, date, ml_zdr):
        if calib_functions.calibrate_day_att(raddir, outdir, date, ml_zdr):
        #if calib_functions.calibrate_day_norm(raddir, outdir, date, ml_zdr):
            f=open(success_file,'w')
	    f.write("")
	    f.close()
            print "written success file"
	else:
	    f=open(no_rays_file,'w')
	    f.write("")
	    f.close()
            print "written no_rays file"
    else:
	f=open(no_rays_file,'w')
	f.write("")
	f.close()
        print "no hourly ml file, nothing to process"
