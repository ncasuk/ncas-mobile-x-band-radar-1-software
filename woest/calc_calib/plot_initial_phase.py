import pyart
import numpy as np
import matplotlib.pyplot as plt
import warnings
import glob
import copy
import os
import datetime
import scipy
import pandas as pd
import matplotlib.dates as mdates
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

np.set_printoptions(threshold=np.inf)

plt.switch_backend('agg')
warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

datadir= '/gws/smf/j07/ncas_radar/data/xband/raine/calibrations/Zcalib/phase_files/'

os.chdir(datadir)
filelist = glob.glob("startphi*")
filelist.sort()
ndays=len(filelist)
print(ndays)
startphi=np.zeros((ndays,290,3600))*np.nan

dates=[]
for d in range(len(filelist)):
    day = filelist[d]
    dates.append(day[13:21])
    startphi1 = np.load(datadir + day)
    [a,b] = startphi1.shape
    startphi[d,0:a,0:b] = startphi1

all_phi=[]

for d in range(len(filelist)):
    daily_median_phi = np.nanmedian(startphi[d].flatten())
    all_phi.append(daily_median_phi)

time = pd.to_datetime(dates, format = '%Y%m%d')
data = pd.DataFrame({'phi' : all_phi}, index=time)

fig, ax1 = plt.subplots(figsize=(15,8)) 
plt.plot(data.index,data['phi'],'kx')
#plt.plot([pd.to_datetime('20190427'), pd.to_datetime('20190427')],[40, 120],'b--')        
#plt.plot([pd.to_datetime('20191029'), pd.to_datetime('20191029')],[40, 120],'b--')     
#plt.plot([pd.to_datetime('20191105'), pd.to_datetime('20191105')],[40, 120],'b--')     
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.xlim(pd.to_datetime('20181030'),pd.to_datetime('20201218'))
plt.xticks(rotation=90)
plt.yticks(size=18)
plt.xticks(size=18)
plt.grid()
plt.xlabel('Date',{'fontsize':18})    
plt.ylabel('Initial Phase (degs)',{'fontsize':18})
fig.set_facecolor('white')
plt.tight_layout()
plt.savefig(datadir+'initial_phase2.png',dpi=150)
