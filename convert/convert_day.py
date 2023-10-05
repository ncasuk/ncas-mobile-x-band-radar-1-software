import argparse
from datetime import timedelta
import dateutil.parser as dp
import os
#import convert
#from convert import SETTINGS
import SETTINGS
import subprocess


def arg_parse_day():
    """
    Parses arguments given at the command line

    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()
    type_choices = ['vol', 'ele', 'azi']

    parser.add_argument('-t', '--scan_type', nargs=1, type=str,
                        choices=type_choices, required=True,
                        help=f'Type of scan, one of: {type_choices}',
                        metavar='')
    parser.add_argument('-d', '--date', nargs=1, type=str, required=True,
                        help=f'Date to find scans from, fromat YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}',
                        metavar='')
    parser.add_argument('-n', '--table_name', nargs=1, type=str, required=True,metavar='')

    return parser.parse_args()


def loop_over_chunks(args):
    """
    Loops through a day in hour chunks of size SETTINGS.CHUNK_SIZE and submits
    those times to convert_hour.py

    :param args: (namespace) Namespace object built from attributes parsed
    from the command line
    """

    scan_type = args.scan_type[0]
    date = args.date[0]
    table = args.table_name[0]

    try:
        day_date_time = dp.isoparse(date)
    except ValueError:
        raise ValueError('[ERROR] Date format is incorrect, should be YYYYMMDD')

    min_date = dp.isoparse(SETTINGS.MIN_START_DATE)
    max_date = dp.isoparse(SETTINGS.MAX_END_DATE)

    if day_date_time < min_date or day_date_time > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - '
                         f'{SETTINGS.MAX_END_DATE}')

    if 24 % SETTINGS.CHUNK_SIZE != 0:
        raise ValueError(f'Chunk size ({SETTINGS.CHUNK_SIZE}) does not divide '
                         'evenly into 24')

    n_chunks = 24 / SETTINGS.CHUNK_SIZE

    if n_chunks < 1:
        raise ValueError('SETTINGS.CHUNK_SIZE must be 24 or less')

    start_day = day_date_time.day
    current_day_date_time = day_date_time
    script_directory = os.path.dirname(os.path.abspath(__file__))

    while current_day_date_time.day == start_day:

        hours = []

        for hour in [current_day_date_time + timedelta(hours=x) for x in range(SETTINGS.CHUNK_SIZE)]:
            hour_str = hour.strftime("%Y%m%d%H")
            hours.append(hour_str)

        current_day_date_time += timedelta(hours=SETTINGS.CHUNK_SIZE)

        print(f"[INFO] Running for {hours}")

        hour_range = hours[0][-2:] + '-' + hours[-1][-2:]
        output_base = SETTINGS.LOTUS_OUTPUT_PATH.format(year=day_date_time.year,
                                                        month=day_date_time.month,
                                                        day=day_date_time.day)

        if not os.path.exists(output_base):
            os.makedirs(output_base)

        output_base += f'/{hour_range}-{scan_type}'

#        slurm_command = f"sbatch -p {SETTINGS.QUEUE} -t {SETTINGS.WALL_CLOCK} -o {output_base}.out " \
#                        f"-e {output_base}.err {script_directory}/convert_hour.py " \
#                        f"-t {scan_type} {' '.join(hours)}"
        slurm_command = f"sbatch -p {SETTINGS.QUEUE} -t {SETTINGS.MAX_RUNTIME}" \
                        f" -o {output_base}.out" \
                        f" -e {output_base}.err" \
                        f" --wrap=\"python {script_directory}/convert_hour.py \
                           -t {scan_type} {' '.join(hours)} -n {table}\""
        print(f"[INFO] Running: {slurm_command}")
        subprocess.call(slurm_command, shell=True)


def main():
    """Runs script if called on command line"""

    args = arg_parse_day()
    loop_over_chunks(args)


if __name__ == '__main__':
    main()
