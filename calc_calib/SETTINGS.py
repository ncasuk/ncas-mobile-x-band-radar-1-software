QUEUE='short-serial'
WALLCLOCK = '01:00:00'
PROJ_NAME = 'raine'

#Location for output files
LOG_DIR = '/gws/smf/j04/ncas_radar/lbennett/logs/'+PROJ_NAME+'/cals/'
SUCCESS_DIR = LOG_DIR+'success/'
NO_RAIN_DIR = LOG_DIR+'no_rain/'

#Location for LOTUS output
LOTUS_DIR = '/gws/smf/j04/ncas_radar/lbennett/lotus-output/'+PROJ_NAME+'/cals/'

#Location of vertical scans
DATA_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/cfradial/uncalib_v1/vert/'

#Location of output of ZDR data for calibration
CALIB_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/calibrations/ZDRcalib/test/'

#Location of weather station text files with daily rain amounts
wxdir = '/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-aws-2/incoming/'+PROJ_NAME+'/NOAA/'

#Set this to 0 or 1. Script for processing vertical scans will make plots if set to 1. Set to 0 otherwise.
PLOT = 0 
