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
    Loops through the horizontal ZDR files, concatenates the data and 
    make a plot of the time series of bias
    
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

    outdir = os.path.join(SETTINGS.ZDR_CALIB_DIR,'horz/')
    all_data=pd.DataFrame()
    
    filelist = glob.glob(outdir + '*.csv')
    filelist.sort()
    for f in range(0,len(filelist)):
        file = filelist[f]
        data = pd.read_csv(file,index_col=0, parse_dates=True)
        all_data = pd.concat([all_data, data])
    
    median_bias=np.nanmedian(all_data.loc[start_date_dt:end_date_dt]['ZDR'])
    print('Median Bias for whole period = ',median_bias)
    zdr_med = all_data.resample('D').median()
    zdr_std = all_data.resample('D').std()

    plt.figure(figsize=(15,8))
    plt.errorbar(zdr_med.index,zdr_med['ZDR'],yerr=zdr_std['ZDR'],color='black',fmt='o',
                 markersize='6', elinewidth=2,capsize=4)
    plt.yticks(size=12)
    plt.xticks(size=12)
    plt.grid()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.xticks(rotation=90)
    plt.ylim([-0.5, 1])
    plt.xlim([start_date_dt,end_date_dt])
    
    plt.ylabel('Horizontal ZDR Bias (dB)', fontsize=18)
    plt.xlabel('Date', fontsize=18)
    
    plt.tight_layout()

    img_dir=os.path.join(outdir,'images')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    #Save plot
    if plot==1:
        img_name = f'{img_dir}/{start_date}_{end_date}_horz_zdr.png'
        plt.savefig(img_name,dpi=150)
        plt.close()

def main():
    """Runs script if called on command line"""

    args = arg_parse()
    plot_zdr(args)


if __name__ == '__main__':
    main()     
