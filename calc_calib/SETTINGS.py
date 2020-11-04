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
NO_RAYS_DIR = LOG_DIR+'no_rays/'

#Location for LOTUS output
LOTUS_DIR = '/gws/smf/j04/ncas_radar/lbennett/lotus-output/'+PROJ_NAME+'/cals/'

#Location of weather station text files with daily rain amounts
WXDIR = '/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-aws-2/incoming/'+PROJ_NAME+'/NOAA/'

#Location of vertical scans
VERT_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/cfradial/uncalib_v1/vert/'

#Location of volume scans
VOLUME_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/cfradial/uncalib_v1/sur/'

#Location of output of ZDR data for calibration
ZDR_CALIB_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/calibrations/ZDRcalib/'

#Location of output of Z data for calibration
Z_CALIB_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/calibrations/Zcalib/test/'

# Exclusions is a list of tuples (), where each tuple is a pair of 
# tuples.The first tuple of each pair is the start and stop elevation 
# of the segment to exclude. The second tuple contains the start and 
# stop azimuth of the segment to exclude.
EXCLUSIONS = [((0,90.1),(20,160)),((0,90.1),(201,207)),((0,0.51),(185,201.5))]
