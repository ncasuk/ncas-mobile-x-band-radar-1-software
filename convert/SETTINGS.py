# Project Choice
PROJ_NAME = 'raine' # raine or chilbolton

EXIT_AFTER_N_FAILURES = 1000000
MIN_START_DATE = '20181025'
MAX_END_DATE = '20201230'

# lotus settings
QUEUE = 'short-serial'
CHUNK_SIZE = 6 # in hours

LOTUS_OUTPUT_PATH = f'/home/users/lbennett/logs/lotus-output/{PROJ_NAME}/{year}/{month}/{day}/{scan_type}'

# Radex convert params file
PARAMS_FILE=f'/home/users/lbennett/lrose/ingest_params/{PROJ_NAME}/RadxConvert.{PROJ_NAME}.uncalib'

# choice for success / failure output handling
BACKEND = 'db' #'db' or 'file'

# input dirs
CHIL_DIR = '/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-mobile-x-band-radar-1/data/chilbolton'
RAINE_DIR = '/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-mobile-x-band-radar-1/incoming/raine'

INPUT_DIR = '/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-mobile-x-band-radar-1/incoming/raine'

# output dirs (for netcdf)
OUTPUT_DIR=f'/gws/nopw/j04/ncas_radar_vol2/data/xband/{PROJ_NAME}/cfradial/uncalib_v1'

