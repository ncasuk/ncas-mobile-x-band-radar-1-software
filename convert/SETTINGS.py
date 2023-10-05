# Project Choice
PROJ_NAME = 'woest'

#Radar name
RADAR = 'nxpol1'

#Radar long name
RADAR_LONG = 'ncas-mobile-x-band-radar-1'

#Platform name
PLATFORM = 'lyneham'

# Maximum number of failures before convert_hour.py raises an error
EXIT_AFTER_N_FAILURES = 1000000

# Range in which there is data for the project
MIN_START_DATE = '20230501'
MAX_END_DATE = '20230930'

# LOTUS settings
QUEUE = 'short-serial-4hr --account=short4hr'
MAX_RUNTIME = '04:00:00'
EST_RUNTIME = '01:00:00'

# Number of hours passed to convert_hour.py at a time
CHUNK_SIZE = 6

# Radx convert params file
PARAMS_FILE=f'/home/users/lbennett/lrose/ingest_params/{PROJ_NAME}/RadxConvert.{RADAR}_{PROJ_NAME}.uncalib'
# WHILE TESTING
# PARAMS_FILE = '/home/users/jhaigh0/work/abcunit-radar/ncas-mobile-x-band-radar-1-software/convert/test/RadxConvert.raine.uncalib'

# Where .out and .err files from LOTUS are output to
LOTUS_OUTPUT_PATH_BASE = f'/home/users/lbennett/logs/lotus-output/{PROJ_NAME}'
# WHILE TESTING
# LOTUS_OUTPUT_PATH_BASE = '/home/users/jhaigh0/work/abcunit-radar/ncas-mobile-x-band-radar-1-software/convert/test/test_lotus_out'
LOTUS_OUTPUT_PATH = LOTUS_OUTPUT_PATH_BASE + "/{year}/{month}/{day}"

# choice for success / failure output handling
BACKEND = 'db' #'db' or 'file'

# Top level directory for raw data
INPUT_DIR = '/gws/smf/j07/ncas_radar/data/ncas-mobile-x-band-radar-1/woest/raw_data/'

# Output directory for netcdf files (specified in the params file)
OUTPUT_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-mobile-x-band-radar-1/{PROJ_NAME}/cfradial/uncalib_v1'

