export PYART_QUIET=True
export LD_LIBRARY_PATH=/gws/smf/j04/ncas_radar/software/LROSE/lib:/gws/smf/j04/ncas_radar/software/anaconda3/lib:${LD_LIBRARY_PATH}
export PATH=/gws/smf/j04/ncas_radar/software/LROSE/bin:$PATH

#export PROJ_DIR=/gws/nopw/j04/ncas_radar_vol1/lindsay/projDir
#export DATA_DIR=/gws/nopw/j04/ncas_radar_vol1/ag/output
export DATA_DIR=/gws/nopw/j04/ncas_radar_vol2/data/xband

export RAINE_DIR=/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-mobile-x-band-radar-1/incoming/raine
export CHIL_DIR=/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-mobile-x-band-radar-1/data/chilbolton

export DATA_HOST=localhost
export RAP_DATA_DIR=$DATA_DIR

export PROCMAP_HOST=localhost
export DATA_MAPPER_ACTIVE=true

export LDATA_FMQ_ACTIVE=true
export ERRORS_LOG_DIR=$DATA_DIR/logs/status

export RESTART_LOG_DIR=$DATA_DIR/logs/restart
export DS_COMM_TIMEOUT_MSECS=60000

export TODAY=$(date '+%Y-%m-%d')

