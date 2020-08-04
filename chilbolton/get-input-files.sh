#!/bin/bash

#DIRS="/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-mobile-x-band-radar-1/data/chilbolton/chilbolton03_data.vol"

# Load defaults
source chil_defaults.cfg

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Parse command-line arguments
DATE_HOUR=$1
SCAN_TYPE=$2

if [[ ! $DATE_HOUR ]] || [[ ${#DATE_HOUR} -ne 10 ]] && [[ ! $DATE_HOUR =~ /\d{10}/ ]]; then
    echo "[ERROR] Date/hour must be 10 digits, not: '$DATE_HOUR'"
    exit 1
fi

YYYY=$(echo $DATE_HOUR | cut -c1-4)
MM=$(echo $DATE_HOUR | cut -c5-6)
DD=$(echo $DATE_HOUR | cut -c7-8)
DATE_DIR="${YYYY}-${MM}-${DD}"

if [ $SCAN_TYPE = 'vol' ]; then
    DIRS=$(ls -d /gws/nopw/j04/ncas_obs/amf/raw_data/ncas-mobile-x-band-radar-1/data/chilbolton/chilbolton*_*.vol)
elif [ $SCAN_TYPE = 'ele' ]; then
    DIRS=$(ls -d /gws/nopw/j04/ncas_obs/amf/raw_data/ncas-mobile-x-band-radar-1/data/chilbolton/chilbolton_*.ele)
elif [ $SCAN_TYPE = 'azi' ]; then
    DIRS=$(ls -d /gws/nopw/j04/ncas_obs/amf/raw_data/ncas-mobile-x-band-radar-1/data/chilbolton/chilbolton*.azi)
fi


for dr in $DIRS; do

    ls $dr/$DATE_DIR/${DATE_HOUR}*dBZv.$SCAN_TYPE 

done
