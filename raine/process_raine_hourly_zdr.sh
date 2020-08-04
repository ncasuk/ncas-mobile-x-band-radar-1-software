#!/bin/bash

PYTHONDIR=/gws/smf/j04/ncas_radar/software/anaconda3/envs/Clustering_2_7_15/
logdir=/home/users/lbennett/logs/raine/cals

bsub -o $logdir/$TODAY/%J.log -e $logdir/$TODAY/%J.err -q short-serial -R "rusage[mem=5000]" -M 5000  -W 01:00 $PYTHONDIR/bin/python -W ignore process_raine_hourly_zdr.py

