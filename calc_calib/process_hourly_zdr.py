import numpy as np
import warnings
import os
import SETTINGS
import utilities
from utilities import calib_functions
import re

warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

def make_hourly_files():

    #Directory for logs
    logdir = SETTINGS.LOG_DIR
    success_dir = SETTINGS.SUCCESS_DIR
    no_rain_dir = SETTINGS.NO_RAIN_DIR

    if not os.path.exists(logdir):
        os.makedirs(logdir)
    if not os.path.exists(success_dir):
        os.makedirs(success_dir)
    if not os.path.exists(no_rain_dir):
        os.makedirs(no_rain_dir)

    #list only date directories
    inputdir = SETTINGS.CALIB_DIR
    outdir = SETTINGS.CALIB_DIR

    pattern = re.compile(r'(\d{8})')
    proc_dates = [x for x in os.listdir(inputdir) if pattern.match(x)]
    proc_dates.sort()

    #For each date where the vertical scans have already been processed, 
    #we now want to calculate hourly values of melting layer height and ZDR

    for date in proc_dates[0:]:
        print(date)
        success_file = os.path.join(success_dir, date+'_hourly_ml_zdr.txt')
        no_rain_file = os.path.join(no_rain_dir, date+'_no_hourly_rain.txt')

        #If there is no 'success' file and no 'no_rain' file, then nothing has been processed, so carry on to process the data
        if not os.path.exists(success_file) and not os.path.exists(no_rain_file):

            if calib_functions.calc_hourly_ML(outdir,date):
       	        f=open(success_file,'w')
                f.write("")
                f.close()
            else:
                f=open(no_rain_file,'w')
                f.write("")
                f.close()

def main():
    """Runs script if called on command line"""

    make_hourly_files()

if __name__ == '__main__':
    main() 
