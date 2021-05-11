# vim: et ts=4
import sys
import glob
import os
import SETTINGS
import argparse
import dateutil
import dateutil.parser as dp
from datetime import date
import re
import subprocess

def arg_parse_all():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()
    type_choices = ['sur', 'rhi']

    parser.add_argument('-s', '--start_date', nargs=1, required=True, 
                        default=SETTINGS.MIN_START_DATE, type=str, 
                        help=f'Start date string with format YYYYMMDDHHNNSS, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-e', '--end_date', nargs=1, required=True, 
                        default=SETTINGS.MAX_END_DATE,type=str, 
                        help=f'End date string in format YYYYMMDDHHNNSS, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-p', '--params_index', nargs=1, required=True, type=str, 
                        help=f'Index for params file given as a 2-digit string e.g. 00, 01, 02', metavar='')

    parser.add_argument('-t', '--scan_type', nargs=1, type=str,
                        choices=type_choices, required=True,
                        help=f'Type of scan, one of: {type_choices}',
                        metavar='')
    
    return parser.parse_args()

def loop_over_days(args): 

    """ 
    Runs .py for each day in the given time range
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """
    today = date.today().strftime("%Y-%m-%d")
    print('today= ',today)
    script_dir=SETTINGS.SCRIPT_DIR

    scan_type = args.scan_type[0]
    params_index = args.params_index[0]
    input_dir = os.path.join(SETTINGS.INPUT_DIR, scan_type) 
    #params_file = f'{SETTINGS.PARAMS_FILE}{params_index}'

    #How many files to process in each chunk. Approx 10 files each hour.   
    chunk_hours=SETTINGS.CHUNK_HOURS
    chunk_size=10*chunk_hours

    start_date=args.start_date[0]
    end_date=args.end_date[0]
    
    start_date_dt = dp.parse(start_date) 
    end_date_dt = dp.parse(end_date) 
    
    start_day_dt = dp.parse(start_date[0:8])
    end_day_dt = dp.parse(end_date[0:8])
    
    min_date = dp.parse(SETTINGS.MIN_START_DATE)
    max_date = dp.parse(SETTINGS.MAX_END_DATE)
     
    if start_date_dt < min_date or end_date_dt > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - {SETTINGS.MAX_END_DATE}')
    
    daydir=os.listdir(input_dir)
    daydir.sort()
    
    files = []
    for day in daydir:
        day_dt=dp.parse(day);
        if day_dt >= start_day_dt and day_dt <= end_day_dt:
            for each in glob.glob(input_dir + '/' + day + '/*.nc'):
                filetime = os.path.basename(each).split('_')[2].replace('-','')
                filetime_dt=dp.parse(filetime)
                if start_date_dt <= filetime_dt and end_date_dt >= filetime_dt:
                    files.append(each)
    print('number of files = ', len(files))
    files.sort()
    #print(files)
    
    lotus_logs=f'{SETTINGS.LOTUS_DIR}{today}'    
    if not os.path.exists(lotus_logs):
        os.makedirs(lotus_logs)

    chunk_index=0

    for file_chunk in chunks(files,chunk_size):
        file_list=' '.join(file_chunk)
        first_file = file_chunk[0]
        D=os.path.basename(first_file).split('_')[2]
        # command to submit to lotus
        sbatch_command = f"sbatch -p {SETTINGS.QUEUE} -t {SETTINGS.WALLCLOCK}" \
                         f" -o {lotus_logs}/{D}_{chunk_index}.out" \
                         f" -e {lotus_logs}/{D}_{chunk_index}.err" \
                         f" --wrap=\"python {script_dir}/apply_calc_chunk.py \
                                -p {params_index} -f {file_list} -t {scan_type}\""

        #print(file_list)
        #py_command = f"python {script_dir}/apply_calc_chunk.py -p {params_file} -f {file_list} -t {scan_type}"
    
        print(f"running {chunk_index}")
        #print(f"running {sbatch_command}")
        subprocess.call(sbatch_command, shell=True)

        #print(f"running {py_command}")
        #subprocess.call(py_command, shell=True)
    
        chunk_index=chunk_index+1
        
def chunks(l, n):

    """Yield successive n-sized chunks from l."""

    for i in range(0, len(l), n):
        yield l[i:i + n]

def main():
    """Runs script if called on command line"""

    args = arg_parse_all()
    loop_over_days(args)

if __name__ == '__main__':
    main() 
