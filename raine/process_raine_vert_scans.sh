#!/bin/bash

PYTHONDIR=/gws/smf/j04/ncas_radar/software/anaconda3/envs/Clustering_2_7_15/
datadir=/gws/nopw/j04/ncas_radar_vol2/data/xband/raine/cfradial/uncalib_v1_new/vert
logdir=/home/users/lbennett/logs/raine/cals
mkdir -p $logdir/$TODAY/

#Set this to 0 or 1. 0 if you don't want the script to make plots for each good vertical profile, or 1 if you do.
plot=1

for day in $(find $datadir/20* -type d -execdir basename {} ';')
#for day in 20181031
do

bsub -o $logdir/$TODAY/$day.log -e $logdir/$TODAY/$day.err -q short-serial -R "rusage[mem=5000]" -W 01:00 $PYTHONDIR/bin/python -W ignore process_raine_vert_scans.py $day $plot

done

