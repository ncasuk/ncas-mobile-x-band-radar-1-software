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

datadir = '/gws/nopw/j04/ncas_radar_vol2/data/xband/raine/cfradial/uncalib_v1_new/sur/'
zdr_dir = '/gws/nopw/j04/ncas_radar_vol2/data/xband/raine/calibrations/ZDRcalib/'
outdir = zdr_dir + 'horz/'
if not os.path.exists(outdir):
    os.makedirs(outdir)

#raindays = [name for name in os.listdir(zdr_dir) if os.path.isdir(os.path.join(zdr_dir, name))]
#raindays.sort()

zcorr = 0.0

#date=raindays[kkkk]
date=sys.argv[1]

ml_file = zdr_dir + date + '/' + 'hourly_ml_zdr.csv'


if os.path.exists(ml_file):
    data = pd.read_csv(ml_file,index_col=0, parse_dates=True)

    if data.empty==False:
        var = data.resample('D').mean()
        mlh = var['H_ML'][0]

        T, medZDR18 = calib_functions.horiz_zdr(datadir, date, outdir, mlh, zcorr)
	T2 = pd.to_datetime(T)
        T2=T2.tz_convert(None)
        output = pd.DataFrame({'ZDR' : medZDR18}, index=T2)
        filename = outdir + date + '_horz_zdr.csv'
#            print filename
#        np.save(filename, [T, medZDR18])
	output.to_csv(filename)

