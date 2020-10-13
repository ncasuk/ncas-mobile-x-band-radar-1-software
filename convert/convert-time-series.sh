#!/bin/bash

# Load defaults
source raine_defaults.cfg

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

MIN_START=$START_DATE
MAX_END=$END_DATE
SCAN_TYPE=

# Parse command-line arguments
while getopts "s:e:t:" OPTION; do
    case $OPTION in
    s)
        START_DATE=$OPTARG
        [[ ${#START_DATE} -ne 8 ]] && [[ ! $START_DATE =~ /\d{8}/ ]] && {
            echo "[ERROR] Start date must be 8 digits"
            exit 1
        }
        ;;
    e)
        END_DATE=$OPTARG
        [[ ${#END_DATE} -ne 8 ]] && [[ ! $END_DATE =~ /\d{8}/ ]] && {
            echo "[ERROR] End date must be 8 digits"
            exit 1
        }
        ;;
    t)
        SCAN_TYPE=$OPTARG
        ;;
    *)
        echo "[ERROR] Incorrect options provided"
        exit 1
        ;;
    esac
done

# Check validity of range
if [[ $START_DATE -gt $END_DATE ]] || [[ $START_DATE -lt $MIN_START ]] || [[ $END_DATE -gt $MAX_END ]]; then
    echo "[ERROR] Please check date range. At least one date is out of range:"
    echo "        $START_DATE - $END_DATE"
    exit 1
fi

# Check scan type
if [[ ! $SCAN_TYPE =~ ^(vol|ele|azi)$ ]]; then
    echo "[ERROR] Scan type must be one of 'vol', 'ele', 'azi'."
    exit 1
fi


echo "[INFO] Running for period: $START_DATE - $END_DATE"

CURRENT_DATE=$START_DATE
while [[ $CURRENT_DATE -le $END_DATE ]]; do

    echo "[INFO] Running for: $CURRENT_DATE"

    script_cmd="$SCRIPT_DIR/convert-raine-x-band-day.sh -t $SCAN_TYPE -d $CURRENT_DATE"
    echo "[INFO] Running: $script_cmd"
    $script_cmd

    CURRENT_DATE=$(date '+%Y%m%d' -d "${CURRENT_DATE}+1 day")

done
exit 0;

