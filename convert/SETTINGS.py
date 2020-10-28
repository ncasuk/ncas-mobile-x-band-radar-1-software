# Project Choice
PROJ_NAME = 'raine'

# Maximum number of failures before convert_hour.py raises an error
EXIT_AFTER_N_FAILURES = 1000000

# Range in which there is data for the project
MIN_START_DATE = '20181025'
MAX_END_DATE = '20201230'

# LOTUS settings
QUEUE = 'short-serial'

# choice for success / failure output handling
BACKEND = 'db' #'db' or 'file'

# Number of hours passed to convert_hour.py at a time
CHUNK_SIZE = 6

# Radex convert params file
# PARAMS_FILE=f'/home/users/lbennett/lrose/ingest_params/{PROJ_NAME}/RadxConvert.{PROJ_NAME}.uncalib'
# WHILE TESTING
PARAMS_FILE = '/home/users/jhaigh0/work/abcunit-radar/ncas-mobile-x-band-radar-1-software/convert/test/RadxConvert.raine.uncalib'

# Where .out and .err files from LOTUS are output to
# LOTUS_OUTPUT_PATH_BASE = f'/home/users/lbennett/logs/lotus-output/{PROJ_NAME}'
# WHILE TESTING
LOTUS_OUTPUT_PATH_BASE = '/home/users/jhaigh0/work/abcunit-radar/ncas-mobile-x-band-radar-1-software/convert/test/test_lotus_out'
LOTUS_OUTPUT_PATH = LOTUS_OUTPUT_PATH_BASE + "/{year}/{month}/{day}/{hours}-{scan_type}"

# choice for success / failure output handling
BACKEND = 'file' #'db' or 'file'

SUCCESS_DIR = '/home/users/jhaigh0/work/abcunit-radar/ncas-mobile-x-band-radar-1-software/convert/test/test_result_out/success'
FAILURE_DIR = '/home/users/jhaigh0/work/abcunit-radar/ncas-mobile-x-band-radar-1-software/convert/test/test_result_out/failure'

# Top level directory for raw data
INPUT_DIR = '/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-mobile-x-band-radar-1/incoming/raine'

# Output directory for netcdf files (specified in the params file)
# OUTPUT_DIR = f'/gws/nopw/j04/ncas_radar_vol2/data/xband/{PROJ_NAME}/cfradial/uncalib_v1'
# WHILE TESTING
OUTPUT_DIR = '/home/users/jhaigh0/work/abcunit-radar/ncas-mobile-x-band-radar-1-software/convert/test/test_radex_out'
