#!/bin/bash

PYTHONDIR=/gws/smf/j04/ncas_radar/software/anaconda3/envs/Clustering_2_7_15/
zdr_dir=/gws/nopw/j04/ncas_radar_vol2/data/xband/chilbolton/calibrations/ZDRcalib_2020/
logdir=/home/users/lbennett/logs/chilbolton/cals
mkdir -p $logdir/$TODAY/

for day in $(find $zdr_dir  -maxdepth 1 -name "20*" -type d -execdir basename {} ';')
#for day in 20200518 20200519 
#for day in 20161112 
do
echo $day

#bsub -o $logdir/$TODAY/$day'_norm.log' -e $logdir/$TODAY/$day'_norm.err' -q short-serial -R "rusage[mem=5000]" -W 02:00 $PYTHONDIR/bin/python -W ignore process_chil_dbz.py $day
bsub -o $logdir/$TODAY/$day'_att.log' -e $logdir/$TODAY/$day'_att.err' -q short-serial -R "rusage[mem=5000]" -W 02:00 $PYTHONDIR/bin/python -W ignore process_chil_dbz.py $day
done

