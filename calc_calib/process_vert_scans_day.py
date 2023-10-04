import warnings
import numpy as np
import pandas as pd
import os
import argparse
import dateutil.parser as dp
import SETTINGS
import sys

warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=FutureWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

#sys.path.append('/gws/nopw/j04/ncas_obs/amf/software/ncas-mobile-x-band-radar-1/utilities/')

#import utilities
from utilities import calib_functions
#import calib_functions
from abcunit_backend.database_handler import DataBaseHandler

def arg_parse_day():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--date', nargs=1, required=True, type=str, 
                        help=f'Date string with format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-p','--make_plots',nargs=1, required=True, default=0, type=int,
                        help=f'Make plots of the profiles if p is set to 1',metavar='')
    
    return parser.parse_args()

def process_vert_scans(args):

    """ 
    Processes all vertical scans for given day to extract values of ZDR bias and melting layer height
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """

    plot=args.make_plots[0]
    day=args.date[0]
    #print(day)
    YYYY, MM, DD = day[:4], day[4:6], day[6:8]
    day_dt = dp.parse(day)
    #print('day_dt = ', day_dt)
    min_date = dp.parse(SETTINGS.MIN_START_DATE)
    max_date = dp.parse(SETTINGS.MAX_END_DATE)

    if day_dt < min_date or day_dt > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - {SETTINGS.MAX_END_DATE}')

    #Directory for input radar data
    raddir = SETTINGS.INPUT_DIR
    
    #Directory for weather station data
    wxdir = SETTINGS.WXDIR
    
    #Directory for processed data
    outdir = SETTINGS.ZDR_CALIB_DIR
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    rh = DataBaseHandler(table_name="process_vert_scans")
    
    #For given day of radar data, look to see if rain was observed by the weather station at the site. 
    #If yes, then process the vertical scans to calculate a value of ZDR and an estimate of the height of the melting layer. 
    #Save melting layer height and zdr values to file. Save a success file. 
    
    expected_file = f'{outdir}/{day}/day_ml_zdr.csv'
   
    identifier = f'{YYYY}.{MM}.{DD}'
 
    #If the file hasn't already been processed, or there is no rain or insufficient data, then carry on script to process the data
   
    result=rh.get_result(identifier) 
    if rh.ran_successfully(identifier) or result in ('no rain', 'insufficient data'):
        print(f'[INFO] Already processed {day}')
     
    else:
#        #Construct the NOAA filename based on the date
#        nfile = f'{wxdir}NOAA-{YYYY}-{MM}.txt'
        
        #Construct the AWS filename based on the date
        nfile = f'{wxdir}{YYYY}-{MM}_rain.csv'
            
#        #Use pandas read_table to read the text file into a table to extract the rain amount
#        data = pd.read_table(nfile, sep='\s+', header=6)
        data=pd.read_csv(nfile,parse_dates=True,index_col=0, dayfirst=True)       
 
        #Set the index column
#        data2 = data.set_index("DAY")
        #Extract rain amount for the current day
#        rain = data2.loc[DD,"RAIN"]
        dateP = day[0:4]+'-'+day[4:6]+'-'+day[6:8]
        #print(dateP)
        rain = data.loc[dateP,"RAIN"]
        #print(rain)    
        #If there was less than 1mm of rain, go to the next day
        if rain < 1.0 or np.isfinite(rain)==False:
            print('no rain')
            rh.insert_failure(identifier, 'no rain')
            #Otherwise process the day's data
        else:
            print('processing day ',day)
            if calib_functions.process_zdr_scans(outdir,raddir,day,expected_file,plot):       
                rh.insert_success(identifier)
            else:
                rh.insert_failure(identifier, 'insufficient data')
    
def main():
    """Runs script if called on command line"""

    args = arg_parse_day()
    process_vert_scans(args)

if __name__ == '__main__':
    main() 
