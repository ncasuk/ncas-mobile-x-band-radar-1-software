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
PARAMS_FILE=f'/home/users/lbennett/lrose/ingest_params/{PROJ_NAME}/RadxConvert.{PROJ_NAME}.uncalib'

# Where .out and .err files from LOTUS are output to
LOTUS_OUTPUT_PATH = f'/home/users/lbennett/logs/lotus-output/{PROJ_NAME}/{year}/{month}/{day}/{scan_type}'

# choice for success / failure output handling
BACKEND = 'db' #'db' or 'file'

# Top level directory for raw data
INPUT_DIR = '/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-mobile-x-band-radar-1/incoming/raine'

# Output directory for netcdf files (specified in the params file)
OUTPUT_DIR=f'/gws/nopw/j04/ncas_radar_vol2/data/xband/{PROJ_NAME}/cfradial/uncalib_v1'

