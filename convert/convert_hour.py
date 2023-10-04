#!/usr/bin/env python

import argparse
import dateutil.parser as dp
import glob
import os
import pyart
import re
import subprocess

from netCDF4 import Dataset
#imports the databasehandler module
from abcunit_backend.database_handler import DataBaseHandler
#from convert import SETTINGS
import SETTINGS


def arg_parse_hour():
    """
    Parses arguments given at the command line

    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()
    type_choices = ['vol', 'ele', 'azi']

    parser.add_argument('-t', '--scan_type',  nargs=1, type=str,
                        choices=type_choices, required=True,
                        help=f'Type of scan, one of: {type_choices}',
                        metavar='')
    # Not sure if this will work along side having a tagged parameter
    parser.add_argument('hours', nargs='+', type=str, help='The hours you want '
                        'to run in the format YYYYMMDDHH', metavar='')

    parser.add_argument('-n', '--table_name', nargs=1, type=str, required=True,metavar='')

    return parser.parse_args()


def _map_scan_type(type):
    """
    Converts (two way) between <> scan names and <> scan names.

    :param type: (str) Scan type in either <> or <> format

    :return: (str) Converted scan type
    """

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
    """
    Finds raw input files from SETTINGS.INPUT_DIR

    :param hour: (str) Hour of the data in the format YYYYMMDDHH
    :param scan_type: (str) Type of scan, one of 'vol', 'ele', or 'azi'

    :return: Sorted list of raw input file paths
    """

    # Probably needs a try round it to format check
    date_dir = None
    try:
        date_dir = dp.isoparse(hour[:-2]).strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError('[ERROR] DateHour format is incorrect, '
                         'should be YYYYMMDDHH')

    files_path = SETTINGS.INPUT_DIR
    # They're all dirs but feels good to check
    dirs = [name for name in os.listdir(files_path) if os.path.isdir(os.path.join(files_path, name))]

    """ if scan_type == 'vol':
        pattern = re.compile(f"^{SETTINGS.PROJ_NAME}.*_.*.vol$")
    elif scan_type == 'ele':
        pattern = re.compile(f"^{SETTINGS.PROJ_NAME}_.*.ele$")
    elif scan_type == 'azi':
        pattern = re.compile(f"^{SETTINGS.PROJ_NAME}.*.azi$") """

    # Pattern to find data folders (anything that has an underscore .scan_type)
    pattern = re.compile(f"^.*_.*.{scan_type}$")

    filtered_dirs = [os.path.join(files_path, name) for name in dirs if pattern.match(name)]
    #print(filtered_dirs) 
    dbz_files = []

    for dr in filtered_dirs:
        target_dir = f'{dr}/{date_dir}'
        #print(target_dir)
        if os.path.exists(target_dir):
            #print(target_dir)
            files = os.listdir(target_dir)
            pattern = re.compile(f"^{hour}.*dBZv.{scan_type}$")
            dbz_files.extend([os.path.join(target_dir, fname) for fname in files if pattern.match(fname)])
    return sorted(set(dbz_files))


#def _get_results_handler(n_facets, sep):
#    """
#    Returns a result handler which either uses a database or the file system
#    depending on the SETTING.BACKEND.
#    If using a database make sure there is an environment variable called
#    $ABCUNIT_DB_SETTINGS which is set to "dbname=<db_name> user=<user_name>
#    host=<host_name> password=<password>".
#
#    :param n_facets: (int) Number of facets used to define a result.
#    :param sep: (str) Delimeter for facet separation in identifier.
#    :param error_types: (list) List of the string names of the types of
#    errors that can occur.
#    """
#
## This function is not really needed because we are always going to be using db in the future.
## For the moment it is useful to keep it in, just in case we want to revert to the file system method. 
#
#    if SETTINGS.BACKEND == 'db':
#        return DataBaseHandler(table_name="convert_results")
#    elif SETTINGS.BACKEND == 'file':
#        base_path = '/home/users/jhaigh0/work/abcunit-radar/ncas-mobile-x-band-radar-1-software/convert/test/test_result_out'
#        return FileSystemHandler(base_path, n_facets, sep, error_types)
#    else:
#        raise ValueError('SETTINGS.BACKEND is not set properly')
#

def loop_over_hours(args):
    """
    Processes each file for each hour passed in the comand line arguments.

    :param args: (namespace) Namespace object built from attributes parsed
    from command line
    """

    scan_type = args.scan_type[0]
    hours = args.hours
    table = args.table_name[0]

# error types are bad_num (different number of variables in raw vs nc)
# failure (RadxConvert doesnt complete) and bad_output (no output file found)
    #rh = _get_results_handler(4, '.')
    #rh = DataBaseHandler(table_name=table)
    rh = DataBaseHandler(table_name=table)

    failure_count = 0
    mapped_scan_type = _map_scan_type(scan_type)

    for hour in hours:

        print(f'[INFO] Processing: {hour}')

        input_files = _get_input_files(hour, scan_type)

        year, month, day = hour[:4], hour[4:6], hour[6:8]
        date = year + month + day

        for dbz_file in input_files:

            if failure_count >= SETTINGS.EXIT_AFTER_N_FAILURES:
                raise ValueError('[WARN] Exiting after failure count reaches limit: '
                                 f'{SETTINGS.EXIT_AFTER_N_FAILURES}')

            fname = os.path.basename(dbz_file)
            input_dir = os.path.dirname(dbz_file)
            
            #This is the file identifier used in the database
            identifier = f'{year}.{month}.{day}.{os.path.splitext(fname)[0]}'

            # Check if this file has already been processed successfully
            #If yes, then go to the next iteration of the loop, i.e. next file
            if rh.ran_successfully(identifier):
                print(f'[INFO] Already ran {dbz_file} successfully')
                continue

            #If there is no success identifier then continue processing the file
            # Remove previous results for this file
            rh.delete_result(identifier)

            # Get expected variables
            fname_base = fname[:16]
            time_digits = fname[8:14]

            pattern = f'{input_dir}/{fname_base}*.{scan_type}'
            expected_vars = set([os.path.splitext(os.path.basename(name)[16:])[0] for name in glob.glob(pattern)])

            # 'Process the uncalibrated data' (where output is generated)
            script_cmd = f"RadxConvert -v -params {SETTINGS.PARAMS_FILE} -f {dbz_file}"
            print(f'[INFO] Running: {script_cmd}')
            #If RadxConvert fails, create a failure outcome in the database 
            if subprocess.call(script_cmd, shell=True) != 0:
                print('[ERROR] RadxConvert call resulted in an error')
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
                            f'{SETTINGS.RADAR_LONG}_{SETTINGS.PLATFORM}_{date}-{time_digits}_{mapped_scan_type}_v1.nc'

            # Read netcdf file to find variables
            # If the file can't be found, create a bad_output failure identifier
            #found_vars = None
            try:
                 rad2=pyart.io.read(expected_file, delay_field_loading=True)
#                ds = Dataset(expected_file, 'r', format="NETCDF4")
#                found_vars = set(ds.variables.keys())
#                ds.close()
            except FileNotFoundError:
                print(f'[ERROR] Expected file {expected_file} not found')
                rh.insert_failure(identifier, 'bad_output')
                failure_count += 1
                continue
            else:
                output_vars=set(rad2.fields.keys())

            print('[INFO] Checking that the output variables match those in the input files')
            #print('expected vars = ', expected_vars)
            #print('output_vars = ', output_vars)

            #Checks that the variables in the nc file are identical to the variables in the input files
            #If not, create a failure identifier called bad_num
            if not expected_vars.issubset(output_vars):
                print('[ERROR] Output variables are not the same as input files'
                      f'{output_vars} != {expected_vars}')
                failure_count += 1
                rh.insert_failure(identifier, 'bad_num')
                continue
            else:
                print(f'[INFO] All expected variable were found: {expected_vars}')

            # If all of the above is succesful, create a success identifier
            rh.insert_success(identifier)

    #rh.close()


def main():
    """Runs script if called on command line"""

    args = arg_parse_hour()
    loop_over_hours(args)


if __name__ == '__main__':
    main()
