#!/bin/bash

# Load defaults
source raine_defaults.cfg

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

SCAN_TYPE=

# Parse command-line arguments
while getopts "t:" OPTION; do
    case $OPTION in
    t)
        SCAN_TYPE=$OPTARG
        ;;
    *)
        echo "[ERROR] Incorrect options provided"
        exit 1
        ;;
    esac
done
shift "$(($OPTIND -1))"

# Check scan type
if [[ ! $SCAN_TYPE =~ ^(vol|ele|azi)$ ]]; then
    echo "[ERROR] Scan type must be one of 'vol', 'ele', 'azi'."
    exit 1
fi

# Parse command-line arguments
DATE_HOURS=$@

if [ ! "$DATE_HOURS" ]; then
    echo "[ERROR] Date/hour must be 10 digit."
    exit 1
fi

for dh in $DATE_HOURS; do
    if [[ ${#dh} -ne 10 ]] && [[ ! $dh =~ /\d{10}/ ]]; then
        echo "[ERROR] Date/hour must be 10 digits, not: '$dh'"
        exit 1
    fi
done

YYYY=$(echo $DATE_HOURS | cut -c1-4)
MM=$(echo $DATE_HOURS | cut -c5-6)
DD=$(echo $DATE_HOURS | cut -c7-8)
DATE=$YYYY$MM$DD

success_dir=$LOG_BASEDIR/raine/success/$YYYY/$MM/$DD
failure_dir=$LOG_BASEDIR/raine/failure/$YYYY/$MM/$DD
bad_num_dir=$LOG_BASEDIR/raine/bad_num/$YYYY/$MM/$DD

mkdir -p $success_dir $failure_dir $bad_num_dir

# Keep track of failure count so we can exit if many failing
failure_count=0

# Map scan type for output checks
mapped_scan_type=$($SCRIPT_DIR/map-scan-type.py $SCAN_TYPE)


for dh in $DATE_HOURS; do

    echo "[INFO] Processing: $dh"
    
    # Get input files
    input_files=$($SCRIPT_DIR/get-raine-input-files.sh $dh $SCAN_TYPE | sort -u)
    
    for dbz_file in $input_files; do 

        # Test if too many failures have happened and if so, exit
        if [ $failure_count -ge $EXIT_AFTER_N_FAILURES ]; then
            echo "[WARN] Exiting after failure count reaches limit: $EXIT_AFTER_N_FAILURES"
            exit 1
        fi

        input_dir=$(dirname $dbz_file)
        fname=$(basename $dbz_file)
        success_file=$success_dir/${fname}
	echo $success_file
        failure_file=$failure_dir/${fname}
        bad_num_file=$bad_num_dir/${fname}
        
        if [ -f $success_file ]; then 
            echo "[INFO] Already ran: $dbz_file"
            echo "       Success file found: $success_file"
            continue
        fi

        # Remove previous error files (if present)
        rm -f $failure_file $bad_num_file
        
        cd $input_dir/
        fname_base=$(echo $fname | cut -c1-16)
        time_digits=$(echo $fname | cut -c9-14)
        
        # Get expected variables as a single space-delimited string
        expected_vars_with_newlines=$(ls ${fname_base}*.${SCAN_TYPE} | cut -c17- | sed "s/\.${SCAN_TYPE}\$//g;" | sort)
        expected_vars="${expected_vars_with_newlines//[$'\t\r\n ']/ }"
        n_vars=$(echo $expected_vars | wc -w)
        
        # Process the uncalibrated data
        source $SCRIPT_DIR/setup-env.sh
        script_cmd="RadxConvert -v -params $PARAMS_FILE_RAINE -f $dbz_file"
        echo "[INFO] Running: $script_cmd"
        $script_cmd
        
        # NOTE: output written to whatever is specified in params file
	# /work/scratch-nopw/lbennett/raine/uncalib_v1/

        # Define required dir name based on scan type
        if [ $mapped_scan_type == "VER" ]; then
            scan_dir_name=vert
        else
            scan_dir_name=$(echo $mapped_scan_type | tr '[:upper:]' '[:lower:]')
        fi

#writing to scratch
        expected_file=$RAINE_SCR_DIR/uncalib_v1/${scan_dir_name}/$DATE/ncas-mobile-x-band-radar-1_sandwith_${DATE}-${time_digits}_${mapped_scan_type}_v1.nc
#        expected_file=/work/scratch-pw/lbennett/raine/uncalib_v1/${scan_dir_name}/$DATE/ncas-mobile-x-band-radar-1_sandwith_${DATE}-${time_digits}_${mapped_scan_type}_v1.nc
        
        echo "[INFO] Checking that the output file has been produced."

        if [ ! -f $expected_file ]; then
            echo "[ERROR] Failed to generate output file: $expected_file"
            let failure_count+=1
            touch $failure_file
            continue
        else
            echo "[INFO] Found expected file: $expected_file"
        fi 
        
        found_vars=$(ncdump -h $expected_file | grep -P "\(time, range\)" | cut -d\( -f1 | cut -d' ' -f2 | sort)
        found_vars="${found_vars//[$'\t\r\n ']/ }"
        echo "[INFO] Checking that the output variables match those in the input files."
#        echo "       Expected: $expected_vars"
#        echo "       Found:    $found_vars"
        
        if [ "$found_vars" != "$expected_vars" ]; then
            echo "[ERROR] Output variables are NOT the same as input files: $found_vars != $expected_vars"
            let failure_count+=1
            touch $bad_num_file
            continue
        else
            echo "[INFO] All expected variables were found: $expected_vars"
        fi 
       
	#Move cfradial file to gws
	gws_location=$RAINE_GWS_DIR/uncalib_v1/${scan_dir_name}/$DATE/
	mkdir -p $gws_location 
	cp $expected_file $gws_location
	echo "[INFO] Output file moved to gws"

        # If we got here then we have success - Create success file
        touch $success_file
 
    done

done
exit 0;

