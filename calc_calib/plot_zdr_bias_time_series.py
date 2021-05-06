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
import os
import re
import SETTINGS

import utilities
from utilities import calib_functions

plt.switch_backend('agg')
warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

def arg_parse():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--start_date', nargs='?', default=SETTINGS.MIN_START_DATE, 
                        type=str, help=f'Start date string in format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-e', '--end_date', nargs='?', default=SETTINGS.MAX_END_DATE,
                        type=str, help=f'End date string in format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-p','--make_plots',nargs=1, required=True, default=0, type=int,
                        help=f'Make plots of the profiles if p is set to 1',metavar='')
    
    return parser.parse_args()

def plot_zdr(args):
    """
    Loops through the ZDRcalib files, concatenates the data and 
    make a plot of the time series of ZDR bias
    
    :param args: (namespace) Namespace object built from attributes 
    parsed from command line
    """

    plot=args.make_plots[0]
    start_date = args.start_date
    end_date = args.end_date

    start_date_dt = dp.parse(start_date) 
    end_date_dt = dp.parse(end_date) 
  
    min_date = dp.parse(SETTINGS.MIN_START_DATE)
    max_date = dp.parse(SETTINGS.MAX_END_DATE)
 
    if start_date_dt < min_date or end_date_dt > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - {SETTINGS.MAX_END_DATE}')

    outdir = SETTINGS.ZDR_CALIB_DIR
    
    all_hourly_data=pd.DataFrame()
    all_data=pd.DataFrame()
    
    pattern = re.compile(r'(\d{8})')
    proc_dates = [x for x in os.listdir(outdir) if pattern.match(x)]
    proc_dates.sort()
    
    for date in proc_dates:
        date_dt=dp.parse(date);
        if date_dt >= start_date_dt and date_dt <= end_date_dt:
    
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
   
    median_bias=np.nanmedian(all_hourly_data.loc[start_date_dt:end_date_dt]['H_ZDR']) 
    print('Median Bias for whole period = ',median_bias) 
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
    
    plt.xlim([start_date_dt,end_date_dt])
    
    monthyearFmt = mdates.DateFormatter('%d-%m-%y')
    ax1.xaxis.set_major_formatter(monthyearFmt)

    plt.plot([start_date_dt, end_date_dt],[median_bias,median_bias],'r-',
                      label="Median Bias = %s" % round(median_bias,2))
    
    if not os.path.exists(os.path.join(outdir,'images')):
        os.makedirs(os.path.join(outdir,'images'))
    
    #Save plot
    if plot==1:
        img_name = f'{outdir}/images/{start_date}_{end_date}_zdr.png'
        print(img_name)
        plt.savefig(img_name,dpi=150)
        plt.close()

def main():
    """Runs script if called on command line"""

    args = arg_parse()
    plot_zdr(args)


if __name__ == '__main__':
    main()    
