import argparse
import dateutil
import dateutil.parser as dp
import glob
from netCDF4 import Dataset
import os
from .output_handler.database_handler import DataBaseHandler
from .output_handler.file_system_handler import FileSystemHandler
import re
import SETTINGS
import subprocess

def arg_parse_hour():
    """
    Parses arguments given at the command line

    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()
    type_choices = ['vol','ele','azi']

    parser.add_argument('-t', '--scan_type',  nargs=1, type=str, choices=type_choices, required=True,
                        help=f'Type of scan, one of: {type_choices}', metavar='')
    # Not sure if this will work along side having a tagged parameter
    parser.add_argument('hours', nargs='+', type=str, required=True, help='The hours you want to run'
                        'in the format YYYYMMDDHH', metavar='')
         
    return parser.parse_args()


def map_scan_type(type):

    scan_dict = {
        'vol': 'SUR',
        'ele': 'RHI',
        'azi': 'VER',
        'SUR': 'vol',
        'RHI': 'ele',
        'VER': 'azi'
    }

    if type in scan_dict:
        return scan_dict[type]
    
    raise KeyError(f'Cannot match scan type {type}')


def _get_input_files(hour, scan_type):

    # Probably needs a try round it to format check
    date_dir = None
    try:
        date_dir = dp.isoparse(hour[:-2]).strftime("%Y-%m-%d")
    except ValueError as err:
        raise ValueError('[ERROR] DateHour format is incorect, should be YYYYMMDDHH')

    files_path = SETTINGS.INPUT_DIR
    # They're all dirs but feels good to check
    dirs = [name for name in os.listdir(files_path) if os.path.isdir(os.path.join(files_path, name))]

    if scan_type == 'vol':
        pattern = re.compile(f"^{SETTINGS.PROJ_NAME}.*_.*.vol$")
    elif scan_type == 'ele':
        pattern = re.compile(f"^{SETTINGS.PROJ_NAME}_.*.ele$")
    elif scan_type == 'azi':
        pattern = re.compile(f"^{SETTINGS.PROJ_NAME}.*.azi$")

    filtered_dirs = [os.path.join(files_path, name) for name in dirs if pattern.match(name)]
    dbz_files = []

    for dr in filtered_dirs:
        target_dir = f'{dr}/{date_dir}'
        files = os.listdir(target_dir)
        pattern = re.compile(f"^{hour}.*dBZv.{scan_type}$")
        dbz_files.extend([os.path.join(target_dir, fname) for fname in files if pattern.match(fname)])

    return sorted(set(dbz_files))


def _get_results_handler(n_facests, sep, error_types):

    if SETTINGS.BACKEND == 'db':
        constring = os.environ.get("ABCUNIT_DB_SETTINGS")
        if not constring:
            raise KeyError('Please create environment variable ABCUNI_DB_SETTINGS'
                            'in for format of "dbname=<db_name> user=<user_name>'
                            'host=<host_name> password=<password>"')
        return DataBaseHandler(constring, error_types)
    elif SETTINGS.BACKEND == 'file':
        return FileSystemHandler(n_facets, sep, error_types)
    else:
        raise ValueError('SETTINGS.BACKEND is not set properly')


def loop_over_hours(args):

    scan_type = args.scan_type
    hours = args.hours
    
    # THIS IS ALL TO CHANGE
    rh = _get_results_handler(4,'.',['bad_num', 'failure', 'bad_output'])

    failure_count = 0
    mapped_scan_type = map_scan_type(scan_type)

    for hour in hours:

        print(f'[INFO] Processing: {hour}')

        input_files = _get_input_files(hour, scan_type)

        year, month, day = hour[:4], hour[4:6], hour[6:8]

        for dbz_file in input_files:

            if failure_count >= SETTINGS.EXIT_AFTER_N_FAILURES:
                raise ValueError('[WARN] Exiting after failure count reaches limit: '
                                f'{SETTINGS.EXIT_AFTER_N_FAILURES}')
            
            fname = os.path.basename(dbz_file)
            input_dir = os.path.dirname(dbz_file)

            identifier = f'{year}.{month}.{day}.{os.path.splittext(fname)[0]}'

            # Check if allready successful
            if rh.ran_succesfully(identifier):
                print(f'[INFO] Already ran {dbz_file} sucessfully')
                continue

            # Remove eroneous runs
            rh.delete_result(identifier)

            # Get expected variables 
            fname_base = fname[:16]
            time_digits = fname[9:14]

            pattern = f'{input_dir}/{fname_base}*.{scan_type}'
            expected_vars = set([os.path.splitext(name[17:])[0] for name in glob.glob(pattern)])

            # 'Process the uncalibrated data' (where output is generated)
            script_cmd = f"RadxConvert -v -params {SETTINGS.PARAMS_FILE} -f {dbz_file}"
            print(f'[INFO] Running: {script_cmd}')
            if subprocess.call(script_cmd, shell=True) != 0:
                print('[ERROR] RadexConvert call resulted in an error')
                rh.insert_failure(identifier, 'failure')
                failure_count += 1
                continue

            # Check for expected netcdf output
            scan_dir_name = None

            if mapped_scan_type == 'VER':
                scan_dir_name = 'vert'
            else:
                scan_dir_name = mapped_scan_type.lower()

            # This should probably be a default path that is formatted
            expected_file = f'{SETTINGS.OUTPUT_DIR}/{scan_dir_name}/{date}/' \ 
                            f'ncas-mobile-x-band-radar-1_sandwith_{date}-{time_digits}_{mapped_scan_type}_v1.nc

            # Get found_vars from the .nc file 
            found_vars = None
            try:
                ds = Dataset(expected_file, 'r', format="NETCDF4")
                found_vars = set(ds.variables.keys())
                ds.close()
            except FileNotFoundError as err:
                print(f'[ERROR] Expected file {expected_file} not found')
                rh.insert_failure(identifier, 'bad_output')
                failure_count += 1
                continue

            print('[INFO] Checking that the output variables match those in the input files')

            if found_vars != expected_vars:
                print('[ERROR] Output variables are not the same as input files'
                      f'{found_vars} != {expected_vars}')
                failure_count += 1
                rh.insert_failure(identifier, 'bad_num')
                continue
            else:
                print(f'[INFO] All expected variable were found: {expected_vars}') 

            #output a success
            rh.insert_success(identifier)


def main():
    """Runs script if called on command line"""

    args = arg_parse_hour()
    loop_over_hours(args)


if __name__ == '__main__':
    main()