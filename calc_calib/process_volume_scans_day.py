import numpy as np
import pandas as pd
import warnings
import os
import argparse
import dateutil.parser as dp
import re
import utilities
from utilities import calib_functions
import SETTINGS

warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

def arg_parse_day():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--date', nargs=1, required=True, type=str, 
                        help=f'Date string with format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    
    return parser.parse_args()

def process_volume_files(args):

    """ 
    Processes the volume scans for each day with rain present, to calculate Z bias
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """

    date=args.date[0]
    print('Processing ',date)
    day_dt = dp.parse(date)
    min_date = dp.parse(SETTINGS.MIN_START_DATE)
    max_date = dp.parse(SETTINGS.MAX_END_DATE)

    if day_dt < min_date or day_dt > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - {SETTINGS.MAX_END_DATE}')

    #Directory for input radar data
    inputdir=SETTINGS.VOLUME_DIR

    #Directory for zdr_ml data
    zdrdir=SETTINGS.ZDR_CALIB_DIR

    #Directory for output calibration data
    outdir=SETTINGS.Z_CALIB_DIR
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    #Directory for logs
    logdir = SETTINGS.LOG_DIR
    success_dir = SETTINGS.SUCCESS_DIR
    no_rays_dir = SETTINGS.NO_RAYS_DIR

    if not os.path.exists(logdir):
        os.makedirs(logdir)
    if not os.path.exists(success_dir):
        os.makedirs(success_dir)
    if not os.path.exists(no_rays_dir):
        os.makedirs(no_rays_dir)

    #print(date)
    success_file = os.path.join(success_dir, date+'_Z.txt')
    no_rays_file = os.path.join(no_rays_dir, date+'_Z.txt')

    #If there is a success file or a no_rays file, write out to log file
    if os.path.exists(success_file):
        print("already processed, success file found")
    elif os.path.exists(no_rays_file):
        print("already processed, no_rays file found")

    #If there is no 'success' file and no 'no_rays' file, then nothing has been processed, so carry on to process the data
    if not os.path.exists(success_file) and not os.path.exists(no_rays_file):
        print("no success or no_rays file found")
        mlfile = os.path.join(zdrdir, date, 'hourly_ml_zdr.csv')
        if os.path.exists(mlfile):
            print("found ml_file, processing data")
            ml_zdr = pd.read_csv(mlfile,index_col=0, parse_dates=True)
            raddir = os.path.join(inputdir, date)
            #print raddir, outdir, date
            if calib_functions.calibrate_day_att(raddir, outdir, date, ml_zdr):
                f=open(success_file,'w')
                f.write("")
                f.close()
                print("written success file")
            else:
                f=open(no_rays_file,'w')
                f.write("")
                f.close()
                print("written no_rays file")
        else:
            f=open(no_rays_file,'w')
            f.write("")
            f.close()
            print("no hourly ml file, nothing to process")

def main():
    """Runs script if called on command line"""

    args = arg_parse_day()
    loop_over_days(args)

if __name__ == '__main__':
    main()
