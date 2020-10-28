import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticks 
import pandas as pd
import dateutil
import dateutil.parser as dp
import argparse

import warnings
import glob
import gc
import os
import sys

start_date = str(sys.argv[1])
end_date = str(sys.argv[2])

sdate_dt = dp.parse(start_date) 
edate_dt = dp.parse(end_date) 

sys.path.append("/gws/nopw/j04/ncas_obs/amf/software/ncas-mobile-x-band-radar-1/utilities/")

import calib_functions
import SETTINGS

plt.switch_backend('agg')

warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

outdir = SETTINGS.CALIB_DIR

proc_dates = [os.path.basename(x) for x in glob.glob(outdir+'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]')]
proc_dates_np = np.array(proc_dates)

#ind = np.where((proc_dates_np >= start_date_dt) & (proc_dates_np <= end_date_dt))

all_hourly_data=pd.DataFrame()
all_data=pd.DataFrame()

for date in proc_dates:
    date_dt=dp.parse(date);
    if date_dt >= sdate_dt and date_dt <= edate_dt:

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
#plt.errorbar(zdr_day_avg1.index,zdr_day_avg1['ZDR'],
#    yerr=zdr_std1['ZDR'],color='black',fmt='o', markersize='6', 
#    elinewidth=2,capsize=4)
plt.errorbar(zdr_day_avg2.index,zdr_day_avg2['H_ZDR'],
    yerr=zdr_std2['H_ZDR'],color='black',fmt='o', markersize='6', 
    elinewidth=2,capsize=4)
plt.yticks(size=16)
plt.xticks(size=16)
plt.grid()

plt.ylabel('ZDR Bias (dB)', fontsize=18)
plt.xlabel('Date', fontsize=18)

plt.xlim([sdate_dt,edate_dt])

monthyearFmt = mdates.DateFormatter('%d-%m-%y')
ax1.xaxis.set_major_formatter(monthyearFmt)

if not os.path.exists(os.path.join(outdir,'images')):
    os.makedirs(os.path.join(outdir,'images'))

#Save plot
img_name = os.path.join(outdir,'images','full_zdr.png')
plt.savefig(img_name,dpi=150)
plt.close()

