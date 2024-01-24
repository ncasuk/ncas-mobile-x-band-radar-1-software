# Project Choice
PROJ_NAME = 'woest'
SCAN_TYPE = 'bl_scans'
#SCAN_GEOM = 'sur'

# Maximum number of failures before convert_hour.py raises an error
EXIT_AFTER_N_FAILURES = 1000000

# Range in which there is data for the project
MIN_START_DATE = '20230501'
MAX_END_DATE = '20230930'

# LOTUS settings
QUEUE = 'short-serial-4hr --account=short4hr'
MAX_RUNTIME = '04:00:00'
EST_RUNTIME = '01:00:00'

# Where .out and .err files from LOTUS are output to
LOTUS_OUTPUT_PATH_BASE = f'/home/users/lbennett/logs/lotus-output/{PROJ_NAME}'
LOTUS_DIR = f'{LOTUS_OUTPUT_PATH_BASE}/cals/nxpol1/'

#LOCATION OF SCRIPTS
SCRIPT_DIR = f'/gws/pw/j07/ncas_obs_vol1/amf/software/ncas-mobile-x-band-radar-1/woest/apply_calc/'

#Location of uncalibrated files
INPUT_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-mobile-x-band-radar-1/{PROJ_NAME}/level1/'
#Location of calibrated/processed files
OUTPUT_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-mobile-x-band-radar-1/{PROJ_NAME}/level2/'

#Location of params files
PARAMS_FILE = f'/home/users/lbennett/lrose/ingest_params/{PROJ_NAME}/RadxConvert.nxpol1_{PROJ_NAME}_sur.level2' 
PARAMS_FILE_RHI = f'/home/users/lbennett/lrose/ingest_params/{PROJ_NAME}/RadxConvert.nxpol1_{PROJ_NAME}_rhi.level2' 

CHUNK_HOURS=6

