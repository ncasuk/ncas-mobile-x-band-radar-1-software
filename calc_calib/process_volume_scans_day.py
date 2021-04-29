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
from abcunit_backend.database_handler import DataBaseHandler

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

    rh = DataBaseHandler(table_name="process_vol_scans")

    identifier = f'{date}'

    #If there is no success or a no_rays identifier, continue to process the data
    result=rh.get_result(identifier) 
    if rh.ran_successfully(identifier) or result=='no rays':
        print(f'[INFO] Already processed {date}')

    else:
        mlfile = f'{zdrdir}/{date}/hourly_ml_zdr.csv'
        if os.path.exists(mlfile):
            print("found ml file, processing data")
            ml_zdr = pd.read_csv(mlfile,index_col=0, parse_dates=True)
            raddir = os.path.join(inputdir, date)
            #print raddir, outdir, date
            if calib_functions.calibrate_day_att(raddir, outdir, date, ml_zdr):
                rh.insert_success(identifier)
                print("File successfully processed")
            else:
                rh.insert_failure(identifier, 'no suitable rays')
                print("No suitable rays")
        else:
            rh.insert_failure(identifier, 'no hourly ml file')
            print("No hourly ml file")

def main():
    """Runs script if called on command line"""

    args = arg_parse_day()
    process_volume_scans(args)

if __name__ == '__main__':
    main()
