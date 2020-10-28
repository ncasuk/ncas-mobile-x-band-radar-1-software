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

sys.path.append("/gws/nopw/j04/ncas_obs/amf/software/ncas-mobile-x-band-radar-1/utilities/")

import calib_functions
import SETTINGS

plt.switch_backend('agg')

warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

outdir = SETTINGS.CALIB_DIR

proc_dates = os.listdir(outdir)]
proc_dates.sort()

all_hourly_data=pd.DataFrame()
all_data=pd.DataFrame()

for date in proc_dates[0:]:
    file1 = os.path.join(outdir,date,'day_ml_zdr.csv')
    file2 = os.path.join(outdir,date,'hourly_ml_zdr.csv')
    if os.path.exists(file1):
        data1 = pd.read_csv(file1,index_col=0, parse_dates=True)
        all_data = pd.concat([all_data, data1])
        zdr_day_avg1 = all_data.resample('D').mean()
        zdr_std1 = all_data.resample('D').std()
    if os.path.exists(file2):
        data2 = pd.read_csv(file2,index_col=0, parse_dates=True)
        all_hourly_data = pd.concat([all_hourly_data, data2])
        zdr_day_avg2 = all_hourly_data.resample('D').mean()
        zdr_std2 = all_hourly_data.resample('D').std()

#(3) Make a plot showing time series of ZDR for chosen period

fig,ax1=plt.subplots(figsize=(15,8))
plt.errorbar(zdr_day_avg1.index,zdr_day_avg1['ZDR'],
    yerr=zdr_std1['ZDR'],color='black',fmt='o', markersize='6', 
    elinewidth=2,capsize=4)
plt.yticks(size=16)
plt.xticks(size=16)
plt.grid()

plt.ylabel('ZDR Bias (dB)', fontsize=18)
plt.xlabel('Date', fontsize=18)

monthyearFmt = mdates.DateFormatter('%d-%m-%y')
ax1.xaxis.set_major_formatter(monthyearFmt)

if not os.path.exists(os.path.join(outdir,'images'))
    os.makedirs(os.path.join(outdir,'images'))

#Save plot
img_name = os.path.join(outdir,'images','full_zdr.png')
plt.savefig(img_name,dpi=150)
plt.close()

#(4) Make plot of all melting layers across whole period
#plt.figure(figsize=(15,8))
#plt.plot_date(all_hourly_data.index,all_hourly_data['H_ML'],'kx')

#plt.yticks(size=16)
#plt.xticks(size=16)
#plt.grid()

#plt.ylabel('Melting Layer (km)', fontsize=18)
#plt.xlabel('Date', fontsize=18)

#Save plot
#plt.savefig(os.path.join(outdir,'images','full_raine_ml.png'))
#plt.close()
