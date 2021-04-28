import numpy as np
import warnings
import os
import SETTINGS
import utilities
from utilities import calib_functions
import re
from abcunit_backend.database_handler import DataBaseHandler

warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

def make_hourly_files():

    rh = DataBaseHandler(table_name="process_hourly_zdr")

    #list only date directories
    inputdir = SETTINGS.ZDR_CALIB_DIR
    outdir = SETTINGS.ZDR_CALIB_DIR

    pattern = re.compile(r'(\d{8})')
    proc_dates = [x for x in os.listdir(inputdir) if pattern.match(x)]
    proc_dates.sort()

    #For each date where the vertical scans have already been processed, 
    #we now want to calculate hourly values of melting layer height and ZDR

    for date in proc_dates[0:]:
        print(date)
        identifier = f'{date}'
        result=rh.get_result(identifier)
        #If there is no 'success' identifier and no 'not enough_rain' identifier, then the file hasn't been processed, so carry on to process the data
        if rh.ran_successfully(identifier) or result=='not enough rain':
            print(f'[INFO] Already processed {date}')
        else:   
            if calib_functions.calc_hourly_ML(outdir,date):
                rh.insert_success(identifier)
            else:
                rh.insert_failure(identifier, 'not enough rain')

def main():
    """Runs script if called on command line"""

    make_hourly_files()

if __name__ == '__main__':
    main() 
