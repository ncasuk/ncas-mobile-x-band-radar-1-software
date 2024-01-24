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

    parser.add_argument('-d', '--date', nargs='?', default=SETTINGS.MIN_START_DATE, 
                        type=str, help=f'Date string in format YYYYMMDD', metavar='')
    parser.add_argument('-p','--make_plots',nargs=1, required=True, default=0, type=int,
                        help=f'Make a plot if p is set to 1',metavar='')
    
    return parser.parse_args()

def plot_zdr(args):
    """
    Loads the data file for the day, plots the time series of ZDR bias    
    :param args: (namespace) Namespace object built from attributes 
    parsed from command line
    """

    plot=args.make_plots[0]
    date = args.date

    date_dt = dp.parse(date) 
  
    min_date = dp.parse(SETTINGS.MIN_START_DATE)
    max_date = dp.parse(SETTINGS.MAX_END_DATE)
 
    if date_dt < min_date or date_dt > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - {SETTINGS.MAX_END_DATE}')

    outdir = SETTINGS.ZDR_CALIB_DIR
    
    all_hourly_data=pd.DataFrame()
    all_data=pd.DataFrame()
    
    file1 = os.path.join(outdir,date,'day_ml_zdr.csv')
    if os.path.exists(file1):
        data1 = pd.read_csv(file1,index_col=0, parse_dates=True)
    #(3) Make a plot showing time series of ZDR for chosen period
    
    fig,ax1=plt.subplots(figsize=(15,8))
    plt.plot(data1.index,data1['ZDR'], 'kx-',markersize='6',linewidth=2)
    plt.yticks(size=16)
    plt.xticks(size=16)
    plt.grid()
    
    plt.ylabel('ZDR Bias (dB)', fontsize=18)
    plt.xlabel('Time (UTC)', fontsize=18)
    
    timeFmt = mdates.DateFormatter('%H-%M')
    ax1.xaxis.set_major_formatter(timeFmt)

    if not os.path.exists(os.path.join(outdir,'images')):
        os.makedirs(os.path.join(outdir,'images'))
    
    #Save plot
    if plot==1:
        img_name = f'{outdir}/images/{date}_zdr.png'
        print(img_name)
        plt.savefig(img_name,dpi=150)
        plt.close()

def main():
    """Runs script if called on command line"""

    args = arg_parse()
    plot_zdr(args)


if __name__ == '__main__':
    main()    
