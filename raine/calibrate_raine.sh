#!/bin/bash
#apply calibration offsets to uncalibrated cfradials

#Load defaults
SCRIPT_DIR=/home/users/lbennett/lrose/ncas-radar-lotus-processor/src/
source $SCRIPT_DIR/raine_defaults.cfg

opts=("$@")
scan_type=${opts[0]}
params_index=${opts[1]}
chunk_index=${opts[2]}
files=${opts[@]:3}

#echo $scan_type
#echo $params_index
#echo $chunk_index
#echo $files

YYYY=$(date +%Y)
MM=$(date +%m)
DD=$(date +%d)
HH=$(date +%H)
NN=$(date +%M)
SS=$(date +%S)

lotus_outdir=$LOTUS_OUTPUTS_BASEDIR/raine/$YYYY/$MM/$DD

mkdir -p $lotus_outdir

wallclock="04:00:00"

logfile=$YYYY$MM$DD\_$HH$NN\_$(printf %03d ${chunk_index})

ARGS="$scan_type ${params_index} $files"


#output info not including big list of arguments
print_cmd="sbatch -p $QUEUE -t $wallclock -o $lotus_outdir/${logfile}.out -e $lotus_outdir/${logfile}.err --wrap=\"time $SCRIPT_DIR/calibrate_raine_chunk.sh\""
echo "[INFO] Running: $print_cmd"

script_cmd=$(sbatch -p $QUEUE -t $wallclock -o $lotus_outdir/${logfile}.out -e $lotus_outdir/${logfile}.err --wrap="time $SCRIPT_DIR/calibrate_raine_chunk.sh ${ARGS}")
echo $script_cmd

exit 0; 
