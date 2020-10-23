import argparse
from datetime import timedelta
import dateutil
import dateutil.parser as dp
import os
import SETTINGS
import subprocess

def arg_parse_all():
    """
    Parses arguments given at the command line

    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()

    type_choices = ['vol','ele','azi']

    parser.add_argument('-t', '--scan_type', nargs=1, type=str, choices=type_choices, required=True,
                        help=f'Type of scan, one of: {type_choices}', metavar='')
    parser.add_argument('-s', '--start', nargs=1, type=str, required=True, default=SETTINGS.MIN_START_DATE,
                        help=f'Start date in the format YYYYMMDD, {SETTINGS.MIN_START_DATE} at the earliest'
                        metavar='')
    parser.add_argument('-e', '--end', nargs=1, type=str, required=True, default=SETTINGS.MAX_END_DATE,
                        help=f'End date in the format YYYYMMDD, {SETTINGS.MAX_END_DATE} at the latest'
                        metavar='')

    return parser.parse_args()

def loop_over_days(args):
    """ 
    Runs convert_rainte_x_band_day.py for each day in the given time range
    
    :param args: (namespace) Namespace object built from arguments parsed from comandline
    """

    # import pdb; pdb.set_trace(), or add breakpoint if doesn't work
    scan_type = args.scan_type
    start_date = args.start
    end_date = args.end

    #validate dates
    try:
        start_date_time = dp.isoparse(start_date)
        end_date_time = dp.isoparse(end_date)
    except ValueError as err:
        raise ValueError('[ERROR] Date format is incorect, should be YYYYMMDD')

    if start_date_time > end_date_time:
        raise ValueError('Start date must be before end date')

    current_date_time = start_date_time
    script_directory = os.path.dirname(os.path.abspath(__file__))

    while current_date_time <= end_date_time:

        current_date = current_date_time.strftime("%Y%m%d")
        print(f"[INFO] Running for: {current_date}")

        cmd = f"{script_directory}/convert_day.py -t {scan_type} -d {current_date}"
        print(f"[INFO] Running: {cmd}")
        subprocess.call(cmd, shell=True)

        current_date_time += timedelta(days=1)


def main():
    """Runs script if called on command line"""

    args = arg_parse_all()
    loop_over_days(args)


if __name__ == '__main__':
    main()
