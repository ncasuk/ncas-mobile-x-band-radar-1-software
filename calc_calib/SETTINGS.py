QUEUE='short-serial-4hr'
WALLCLOCK = '01:00:00'
PROJ_NAME = 'WOEST'

# Range in which there is data for the project
MIN_START_DATE = '20230501'
MAX_END_DATE = '20230930'

#Location for output files
#LOG_DIR = '/gws/smf/j04/ncas_radar/lbennett/logs/'+PROJ_NAME+'/cals/'
#SUCCESS_DIR = LOG_DIR+'success/'
#NO_RAIN_DIR = LOG_DIR+'no_rain/'
#NO_RAYS_DIR = LOG_DIR+'no_rays/'

#LOCATION OF SCRIPTS
SCRIPT_DIR = f'/gws/pw/j07/ncas_obs_vol1/amf/software/ncas-mobile-x-band-radar-1/calc_calib/'

#Location for LOTUS output
LOTUS_OUTPUT_PATH_BASE = f'/home/users/lbennett/logs/lotus-output/{PROJ_NAME}'
LOTUS_DIR = f'{LOTUS_OUTPUT_PATH_BASE}/cals/'

#Location of weather station text files with daily rain amounts
#WXDIR = f'/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-aws-2/incoming/{PROJ_NAME}/NOAA/'
WXDIR= f'/gws/nopw/j04/ncas_radar_vol2/data/xband/woest/wow_obs/'

#Location of vertical scans
#VERT_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/cfradial/uncalib_v1/vert/'
#INPUT_DIR = f'/gws/smf/j07/ncas_radar/data/xband/{PROJ_NAME}/cfradial/uncalib_v1/vert/'
INPUT_DIR = f'/gws/nopw/j04/ncas_radar_vol2/data/xband/woest/cfradial/uncalib_v1/vert/'

#Location of volume scans
#VOLUME_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/cfradial/uncalib_v1/sur/'
VOLUME_DIR = f'/gws/smf/j07/ncas_radar/data/xband/{PROJ_NAME}/cfradial/uncalib_v1/sur/'

#Location of output of ZDR data for calibration
#ZDR_CALIB_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/calibrations/ZDRcalib/'
ZDR_CALIB_DIR = f'/gws/smf/j07/ncas_radar/data/xband/{PROJ_NAME}/calibrations/ZDRcalib/'

#Location of output of Z data for calibration
#Z_CALIB_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/calibrations/Zcalib/'
Z_CALIB_DIR = f'/gws/smf/j07/ncas_radar/data/xband/{PROJ_NAME}/calibrations/Zcalib/'

#Location of phi files 
PHI_DIR = Z_CALIB_DIR+'phi_files/'

# Exclusions is a list of tuples (), where each tuple is a pair of 
# tuples.The first tuple of each pair is the start and stop elevation 
# of the segment to exclude. The second tuple contains the start and 
# stop azimuth of the segment to exclude.
EXCLUSIONS = [((0,90.1),(20,160)),((0,90.1),(201,207)),((0,0.51),(185,201.5))]
