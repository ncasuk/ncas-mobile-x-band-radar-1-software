QUEUE='short-serial'
WALLCLOCK = '01:00:00'
PROJ_NAME = 'raine'

# Range in which there is data for the project
MIN_START_DATE = '20181001'
MAX_END_DATE = '20210331'

#Location for output files
LOG_DIR = '/gws/smf/j04/ncas_radar/lbennett/logs/'+PROJ_NAME+'/cals/'
SUCCESS_DIR = LOG_DIR+'success/'
NO_RAIN_DIR = LOG_DIR+'no_rain/'

#Location for LOTUS output
LOTUS_DIR = '/gws/smf/j04/ncas_radar/lbennett/lotus-output/'+PROJ_NAME+'/cals/'

#Location of vertical scans
DATA_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/cfradial/uncalib_v1/vert/'

#Location of output of ZDR data for calibration
CALIB_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/calibrations/ZDRcalib/'

#Location of weather station text files with daily rain amounts
WXDIR = '/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-aws-2/incoming/'+PROJ_NAME+'/NOAA/'

