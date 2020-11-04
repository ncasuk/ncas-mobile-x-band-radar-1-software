import numpy as np
import pandas as pd
import warnings
import os
import argparse
import dateutil.parser as dp
import re
import SETTINGS
from utilities import calib_functions

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

def process_volume_scans(args):

    """ 
    Processes the volume scans for each day with rain present, 
    to calculate horizontal ZDR bias
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """

    date=args.date[0]
    print('Processing ',date)
    day_dt = dp.parse(date)
    min_date = dp.parse(SETTINGS.MIN_START_DATE)
    max_date = dp.parse(SETTINGS.MAX_END_DATE)

    if day_dt < min_date or day_dt > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - {SETTINGS.MAX_END_DATE}')

    #Volume scans data to process
    inputdir = SETTINGS.VOLUME_DIR
    #But only using dates in the ZDR directory, which are ones we know have rain
    zdr_dir = SETTINGS.ZDR_CALIB_DIR
    #Create subdirectory of ZDR directory for output data
    outdir = os.path.join(zdr_dir,'horz/')
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    zcorr = 0.0

    ml_file = os.path.join(zdr_dir,date,'hourly_ml_zdr.csv')

    if os.path.exists(ml_file):
        data = pd.read_csv(ml_file,index_col=0, parse_dates=True)
    
        if data.empty==False:
            var = data.resample('D').mean()
            mlh = var['H_ML'][0]
    
            T, medZDR18 = calib_functions.horiz_zdr(datadir, date, outdir, mlh, zcorr)
            T2 = pd.to_datetime(T)
            T2=T2.tz_convert(None)
            output = pd.DataFrame({'ZDR' : medZDR18}, index=T2)
            filename = os.path.join(outdir,date,'_horz_zdr.csv')
            output.to_csv(filename)

def main():
    """Runs script if called on command line"""

    args = arg_parse_day()
    process_volume_scans(args)

if __name__ == '__main__':
    main()
