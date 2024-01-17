import numpy as np
import argparse
import pyart
import warnings
import glob
import os
import gc
import shutil
import sys
sys.path.insert(1, '/gws/pw/j07/ncas_obs_vol1/amf/software/ncas-mobile-x-band-radar-1/calc_calib/')
import SETTINGS

basedir = '/gws/smf/j07/ncas_radar/data/ncas-mobile-x-band-radar-1/woest/cfradial/processed_v1/sur/'

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

def move_files(args):

    """ 
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """

    day=args.date[0]
    print('Processing ',day)

    filelist = [os.path.basename(x) for x in glob.glob(f'{basedir}{day}/*.nc')]
    filelist.sort()
    for f in filelist:
        print('f=',f)
        src=f'{basedir}{day}/{f}'
#        print('src=',src)
        rad = pyart.io.read(src,delay_field_loading = True)
        pw=rad.instrument_parameters['pulse_width']['data'][0]
        pw=pw*1000000
        #print(pw)
        if round(pw)==2:
            dst=f'{basedir}{day}/bl_scans/{f}'
 #           print('dst=',dst)
            bldir=f'{basedir}{day}/bl_scans'
            if not os.path.exists(bldir):
                os.makedirs(bldir)
            print('moving ',src,' to ',dst)
            shutil.move(src,dst)
        elif round(pw)==0:
            dst=f'{basedir}{day}/cloud_scans/{f}'
  #          print('dst=',dst)
            cldir=f'{basedir}{day}/cloud_scans'
            if not os.path.exists(cldir):
                os.makedirs(cldir)
            print('moving ',src,' to ',dst)
            shutil.move(src,dst)
        del rad
        gc.collect()
 
def main():
    """Runs script if called on command line"""

    args = arg_parse_day()
    move_files(args)

if __name__ == '__main__':
    main()
