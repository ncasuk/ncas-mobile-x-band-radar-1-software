#!/bin/bash

PYTHONDIR=/gws/smf/j04/ncas_radar/software/anaconda3/envs/Clustering_2_7_15/
datadir=/gws/nopw/j04/ncas_radar_vol2/data/xband/chilbolton/cfradial/uncalib_v1/vert
logdir=/home/users/lbennett/logs/chilbolton/cals
mkdir -p $logdir/$TODAY/

#find number of days of radar data
#numdays=`find $datadir/20* -type d |wc -l`
#returns just the directory names (days) without the paths
#day=`find $datadir/20* -type d -execdir basename {} ';'`

plot=1

#start=20161122

for day in $(find $datadir/2018* -type d -execdir basename {} ';')
do
#if [ $(date -d $day +%s) -gt $(date -d $start +%s) ]
#then
bsub -o $logdir/$TODAY/$day.log -e $logdir/$TODAY/$day.err -q short-serial -R "rusage[mem=5000]" -W 01:00 $PYTHONDIR/bin/python -W ignore process_chil_vert_scans.py $day $plot
#fi
done

