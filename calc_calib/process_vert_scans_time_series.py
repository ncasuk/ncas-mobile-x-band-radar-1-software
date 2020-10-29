import SETTINGS
import os
import glob
from datetime import date
import argparse
import dateutil.parser as dp

def arg_parse_all():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--start_date', nargs='1', required=True, 
                        default=SETTINGS.MIN_START_DATE, type=str, 
                        help=f'Start date string with format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-e', '--end_date', nargs='1', required=True, 
                        default=SETTINGS.MAX_END_DATE,type=str, 
                        help=f'End date string in format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    
    return parser.parse_args()

def loop_over_days()
 
    """ 
    Runs process_vert_scans.py for each day in the given time range
    
    :param args: (namespace) Namespace object built from arguments parsed from comandline
    """

    today = date.today().strftime("%Y-%m-%d")
    
    if not os.path.exists(os.path.join(SETTINGS.LOTUS_DIR,today)):
        os.makedirs(os.path.join(SETTINGS.LOTUS_DIR,today))
    
    dates = os.listdir(SETTINGS.DATA_DIR)
    dates.sort()
    
    current_directory = os.getcwd()  # get current working directory
    for day in dates:
        print(day)
    
    # command to submit to lotus
        sbatch_command = f"sbatch -p {SETTINGS.QUEUE} -t {SETTINGS.WALLCLOCK} -o " \
                           f"{SETTINGS.LOTUS_DIR}{today}/{day}.out -e {SETTINGS.LOTUS_DIR}{today}/{day}.err "\
                           f"--wrap=\"python {current_directory}/process_vert_scans.py {day} {SETTINGS.PLOT}\""
    
        #subprocess.call(sbatch_command, shell=True)
    
        print(f"running {sbatch_command}")
   
def main():
    """Runs script if called on command line"""

    args = arg_parse_all()
    loop_over_days(args)


if __name__ == '__main__':
    main() 
