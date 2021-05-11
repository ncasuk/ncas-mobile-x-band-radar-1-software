# Project Choice
PROJ_NAME = 'raine'

# Maximum number of failures before convert_hour.py raises an error
EXIT_AFTER_N_FAILURES = 1000000

# Range in which there is data for the project
MIN_START_DATE = '20181025'
MAX_END_DATE = '20201231'

# LOTUS settings
QUEUE='short-serial-4hr'
WALLCLOCK = '01:00:00'

# Where .out and .err files from LOTUS are output to
LOTUS_OUTPUT_PATH_BASE = f'/home/users/lbennett/logs/lotus-output/{PROJ_NAME}'
LOTUS_DIR = f'{LOTUS_OUTPUT_PATH_BASE}/cals/'

#LOCATION OF SCRIPTS
SCRIPT_DIR = f'/gws/nopw/j04/ncas_obs/amf/software/ncas-mobile-x-band-radar-1/apply_calc/'

#Location of uncalibrated files
INPUT_DIR = f'/gws/smf/j07/ncas_radar/data/xband/{PROJ_NAME}/cfradial/uncalib_v1/'
OUTPUT_DIR = f'/gws/smf/j07/ncas_radar/data/xband/{PROJ_NAME}/cfradial/calib_v1/'

#Location of params files
PARAMS_FILE = f'/home/users/lbennett/lrose/ingest_params/{PROJ_NAME}/RadxConvert.{PROJ_NAME}.calib.0' 

CHUNK_HOURS=6

