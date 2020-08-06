# vim: et ts=4
#!/bin/bash

#Load defaults
SCRIPT_DIR=/home/users/lbennett/lrose/ncas-radar-lotus-processor/src/
source $SCRIPT_DIR/raine_defaults.cfg

#input file has this form
#/gws/nopw/j04/ncas_radar_vol2/data/xband/raine/cfradial/uncalib_v1/sur/20181101/ncas-mobile-x-band-radar-1_sandwith_20181101-090356_SUR_v1.nc

#parse arguments from calibrate_raine.sh
opts=("$@")
scan_type=${opts[0]}
params_index=${opts[1]}
input_files=${opts[@]:2}

params_file=/home/users/lbennett/lrose/ingest_params/raine/RadxConvert.raine.calib.0$params_index

failure_count=0

for ncfile in $input_files; do

    ncdate=${ncfile:71:8}
    YYYY=${ncdate:0:4}
    MM=${ncdate:4:2}
    DD=${ncdate:6:2}
    DATE=$YYYY$MM$DD

    failure_dir=$LOG_BASEDIR/raine/failure/$YYYY/$MM/$DD
    success_dir=$LOG_BASEDIR/raine/success/$YYYY/$MM/$DD
    mkdir -p $success_dir $failure_dir

    # Test if too many failures have happened and if so, exit
    if [ $failure_count -ge $EXIT_AFTER_N_FAILURES ]; then
        echo "[WARN] Exiting after failure count reaches limit: $EXIT_AFTER_N_FAILURES"
        exit 1
    fi

    fname=$(basename $ncfile)
    success_file=$success_dir/${fname}
    failure_file=$failure_dir/${fname}

    # Remove previous error files (if present)
    rm -f $failure_file

    if [ -f $success_file ]; then 
        echo "[INFO] Already ran: $ncfile"
        echo "       Success file found: $success_file"
        continue
    fi

    # Process the data
	script_cmd="RadxConvert -v -params ${params_file} -f $ncfile"
    echo "[INFO] Running: $script_cmd"
    $script_cmd

    #this line looks for the file generated from uncalib_v1 in calib_v1.
	#expected_file=${ncfile:0:61}${ncfile:64 -1}

    #as we're writing to scratch we need to change this line.
    #output directory needs to reflect what is specified in the params file.
    output_dir=$RAINE_SCR_DIR/calib_v1/$scan_type/$DATE
	expected_file=$output_dir/$fname

    #echo $expected_file
    echo "[INFO] Checking that the output file has been produced."

	if [ ! -f $expected_file ]; then
	    echo "[ERROR] Failed to generate output file: $expected_file"
        let failure_count+=1
        touch $failure_file
        continue
    else
        echo "[INFO] Found expected file: $expected_file"
    fi 

	#Copy cfradial file to gws
	gws_location=$RAINE_GWS_DIR/calib_v1/${scan_type}/$DATE/
	mkdir -p $gws_location 
	cp $expected_file $gws_location
	echo "[INFO] Output file moved to gws"

    gws_file=$gws_location/$fname

	if [ ! -f $gws_file ]; then
	    echo "[ERROR] Failed to copy file to gws: $gws_file"
#        let failure_count+=1
#        touch $failure_file
        continue
    else
        echo "[INFO] Found gws file: $gws_file"
        touch $success_file
    fi 


done

exit 0;
