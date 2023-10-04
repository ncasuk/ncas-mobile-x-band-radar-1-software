import SETTINGS
import os
import argparse
import dateutil.parser as dp
from datetime import date
import subprocess

def arg_parse_all():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--start_date', nargs=1, required=True, 
                        default=SETTINGS.MIN_START_DATE, type=str, 
                        help=f'Start date string with format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-e', '--end_date', nargs=1, required=True, 
                        default=SETTINGS.MAX_END_DATE,type=str, 
                        help=f'End date string in format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-p','--make_plots',nargs=1, required=True, default=0, type=int,
                        help=f'Make plots of the profiles if p is set to 1',metavar='')
    
    return parser.parse_args()

def loop_over_days(args):
 
    """ 
    Runs process_vert_scans.py for each day in the given time range
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """

    today = date.today().strftime("%Y-%m-%d")
    #Set up directory for Lotus output files based on today's date
    if not os.path.exists(os.path.join(SETTINGS.LOTUS_DIR,today)):
        os.makedirs(os.path.join(SETTINGS.LOTUS_DIR,today))

    start_date = args.start_date[0]
    end_date = args.end_date[0]
    plot = args.make_plots[0]

    start_date_dt = dp.parse(start_date) 
    end_date_dt = dp.parse(end_date) 
  
    min_date = dp.parse(SETTINGS.MIN_START_DATE)
    max_date = dp.parse(SETTINGS.MAX_END_DATE)
 
    if start_date_dt < min_date or end_date_dt > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - {SETTINGS.MAX_END_DATE}')
 
    proc_dates = os.listdir(SETTINGS.INPUT_DIR)
    proc_dates.sort()
    
    current_directory = os.getcwd()  # get current working directory

    for day in proc_dates:
        day_dt=dp.parse(day);
        if day_dt >= start_date_dt and day_dt <= end_date_dt:
    
            print(day)
    
            # command to submit to lotus
            sbatch_command = f"sbatch -p {SETTINGS.QUEUE} --account=short4hr -t {SETTINGS.WALLCLOCK} -o " \
                             f"{SETTINGS.LOTUS_DIR}{today}/{day}.out -e {SETTINGS.LOTUS_DIR}{today}/{day}.err "\
                             f"--wrap=\"python {SETTINGS.SCRIPT_DIR}/process_vert_scans_day.py -d {day} -p {plot}\""
    
            subprocess.call(sbatch_command, shell=True)
    
            print(f"running {sbatch_command}")
   
def main():
    """Runs script if called on command line"""

    args = arg_parse_all()
    loop_over_days(args)


if __name__ == '__main__':
    main() 
