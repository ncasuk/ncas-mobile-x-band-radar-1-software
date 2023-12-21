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
                        help=f'Make plots of the day or time series if p is set to 1 or 2, or a plot of every time step if p is 3',metavar='')
    
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
    if not os.path.exists(os.path.join(outdir,'images')):
        os.makedirs(os.path.join(outdir,'images'))
    
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
                zdr_day_avg1 = data1.resample('D').median()
                zdr_std1 = data1.resample('D').std()

                if plot==1: 
                    fig,ax1=plt.subplots(figsize=(15,8))
                    plt.plot(data1.index,data1['ZDR'], 'kx-',markersize='6',linewidth=2)
                    plt.yticks(size=16)
                    plt.xticks(size=16)
                    plt.xlim(pd.to_datetime(date),pd.to_datetime(date) + pd.to_timedelta(24, unit='h'))
                    plt.ylim(-0.5,0.5)
                    plt.grid()
                    plt.ylabel('ZDR Bias (dB)', fontsize=18)
                    plt.xlabel('Time (UTC)', fontsize=18)
                    plt.title('Median ZDR ', zdr_day_avg1['ZDR'][0],' +/- ', zdr_std1['ZDR'][0])
                    timeFmt = mdates.DateFormatter('%H')
                    ax1.xaxis.set_major_formatter(timeFmt)
                    img_name = f'{outdir}/images/{date}_zdr.png'
                    print('Saving ', img_name)
                    plt.savefig(img_name,dpi=150)
                    plt.close()

                all_data = pd.concat([all_data, data1])

            if os.path.exists(file2):
                data2 = pd.read_csv(file2,index_col=0, parse_dates=True)
                all_hourly_data = pd.concat([all_hourly_data, data2])
                zdr_day_avg2 = all_hourly_data.resample('D').mean()
                zdr_std2 = all_hourly_data.resample('D').std()

          
    median_bias=np.nanmedian(all_hourly_data.loc[start_date_dt:end_date_dt]['H_ZDR']) 
    print('Median Bias for whole period (from hourly data) = ',median_bias) 
    #(3) Make a plot showing time series of ZDR for chosen period
    
    if plot==2:    
        fig,ax1=plt.subplots(figsize=(15,8))
    #plt.errorbar(zdr_day_avg1.index,zdr_day_avg1['ZDR'],
    #    yerr=zdr_std1['ZDR'],color='black',fmt='o', markersize='6', 
    #    elinewidth=2,capsize=4)
        plt.errorbar(zdr_day_avg2.index,zdr_day_avg2['H_ZDR'],
            yerr=zdr_std2['H_ZDR'],color='black',fmt='o', markersize='6', 
            elinewidth=2,capsize=4)

        for a in range(len(zdr_day_avg2.index)):
            Z=zdr_day_avg2['H_ZDR'][a]
            if np.isfinite(Z):
                T=zdr_day_avg2.index[a]
                D=zdr_day_avg2.index[a].date().strftime('%d%m')
                #print(T), print(D), print(Z)
                plt.text(T,Z,' ' + D)

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
        img_name = f'{outdir}/images/{start_date}_{end_date}_zdr.png'
        print('Saving ',img_name)
        plt.savefig(img_name,dpi=150)
        plt.close()
   
    #make plot of all ZDR values i.e. every timestep
    if plot==3:

        all_data_mean=all_data.resample('D').mean()
        all_data_median=all_data.resample('D').median()
        all_data_std=all_data.resample('D').std()

        all_data_overall_median=np.nanmedian(all_data.loc[start_date_dt:end_date_dt]['ZDR']) 
        all_data_overall_mean=np.nanmean(all_data.loc[start_date_dt:end_date_dt]['ZDR']) 
        all_data_overall_std=np.nanstd(all_data.loc[start_date_dt:end_date_dt]['ZDR']) 

        fig,ax1=plt.subplots(figsize=(15,8))
        plt.plot(all_data.index,all_data['ZDR'],'kx')
        plt.plot(all_data_mean.index,all_data_mean['ZDR'],'ro')
        plt.plot(all_data_median.index,all_data_median['ZDR'],'go')

        plt.plot([start_date_dt,end_date_dt],[all_data_overall_mean['ZDR'],all_data_overall_mean['ZDR']],'g-')


        plt.yticks(size=16)
        plt.xticks(size=16)
        plt.grid()
        plt.ylabel('ZDR Bias (dB)', fontsize=18)
        plt.xlabel('Date', fontsize=18)
        plt.xlim([start_date_dt,end_date_dt])
        monthyearFmt = mdates.DateFormatter('%d-%m-%y')
        ax1.xaxis.set_major_formatter(monthyearFmt)
        img_name = f'{outdir}/images/{start_date}_{end_date}_every_zdr.png'
        print('Saving ',img_name)
        plt.savefig(img_name,dpi=150)
        plt.close()

 
def main():
    """Runs script if called on command line"""

    args = arg_parse()
    plot_zdr(args)


if __name__ == '__main__':
    main()    
