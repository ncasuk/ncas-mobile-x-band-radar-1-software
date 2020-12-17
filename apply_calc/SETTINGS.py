QUEUE='short-serial-4hr'
WALLCLOCK = '01:00:00'
PROJ_NAME = 'raine'

# Range in which there is data for the project
MIN_START_DATE = '20181001'
MAX_END_DATE = '20210331'

#Location for output files
LOG_DIR = '/gws/smf/j04/ncas_radar/lbennett/logs/'+PROJ_NAME+'/cals/'
FAILURE_DIR = LOG_DIR+'failure/'
SUCCESS_DIR = LOG_DIR+'success/'

#Location for LOTUS output
LOTUS_DIR = '/gws/smf/j04/ncas_radar/lbennett/lotus-output/'+PROJ_NAME+'/cals/'

#Location of uncalibrated files
INPUT_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/cfradial/uncalib_v1/'
OUTPUT_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/cfradial/calib_v1/'

#Location of params files
PARAMS_FILE = '/home/users/lbennett/lrose/ingest_params/'+PROJ_NAME+'/'+'RadxConvert.'+PROJ_NAME+'.calib.' 

CHUNK_HOURS=6

