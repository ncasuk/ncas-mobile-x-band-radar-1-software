QUEUE='short-serial'
WALLCLOCK = '01:00:00'
PROJ_NAME = 'raine'
LOG_DIR = '/gws/smf/j04/ncas_radar/lbennett/logs/'+PROJ_NAME+'/cals/'
SUCCESS_DIR = LOG_DIR+'success/'
NO_RAIN_DIR = LOG_DIR+'no_rain/'
LOTUS_DIR = '/gws/smf/j04/ncas_radar/lbennett/lotus_output/'+PROJ_NAME+'/cals/'
DATA_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/cfradial/uncalib_v1/vert/'

CALIB_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/calibrations/ZDRcalib/'

#Location of weather station text files with daily rain amounts
wxdir = '/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-aws-2/incoming/'+PROJ_NAME+'/NOAA/'

#Set this to 0 or 1. 0 if you don't want the script to make plots for each good vertical profile, or 1 if you do.
PLOT = 0 
