# vim: et ts=4
import sys
import glob
import os
import pyart
import SETTINGS
import argparse
import dateutil.parser as dp
import subprocess
from netCDF4 import Dataset
from abcunit_backend.database_handler import DataBaseHandler

#input file has this form
#/gws/smf/j07/ncas_radar/data/xband/raine/cfradial/uncalib_v1/sur/20181101/ncas-mobile-x-band-radar-1_sandwith_20181101-090356_SUR_v1.nc

def arg_parse_chunk():

    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()
    type_choices = ['sur', 'rhi']

    parser.add_argument('-p', '--params_index', nargs=1, required=True, type=str, 
                        help=f'Index for params file given as an integer', metavar='')
    parser.add_argument('-f', '--files', nargs='+', required=True,
                        help=f'List of files to process', metavar='')
    parser.add_argument('-t', '--scan_type', nargs=1, type=str,
                        choices=type_choices, required=True,
                        help=f'Type of scan, one of: {type_choices}',metavar='')
    
    return parser.parse_args()


def loop_over_files(args):

    params_index = args.params_index[0]
    params_file = f'{SETTINGS.PARAMS_FILE}{params_index}'
    input_files = args.files
    print("input_files= ",input_files)
    scan_type = args.scan_type[0]

    failure_count=0

    for ncfile in input_files:

        if failure_count >= SETTINGS.EXIT_AFTER_N_FAILURES:
            raise ValueError('[WARN] Exiting after failure count reaches limit: '
                                 f'{SETTINGS.EXIT_AFTER_N_FAILURES}')

        print("ncfile= ",ncfile)
        fname = os.path.basename(ncfile)
        ncdate = os.path.basename(ncfile).split('_')[2].replace('-','')
    
        YYYY=ncdate[0:4]
        MM=ncdate[4:6]
        DD=ncdate[6:8]
        date=ncdate[0:8]

        rh = DataBaseHandler(table_name="apply_calib_rhi")
        identifier = f'{ncdate}'

        #If there is a success identifier, continue to next file in the loop
        result=rh.get_result(identifier) 
        if rh.ran_successfully(identifier):
            print(f'[INFO] Already processed {ncdate} successfully')
            continue
        #If there is no success identifier then continue processing the file
        # Remove previous results for this file
        rh.delete_result(identifier)

        #Read input uncalibrated netcdf file and extract list of variables
        try:
            rad1=pyart.io.read(ncfile, delay_field_loading=True)
        except IOError:
            print('[ERROR] Could not open file, {ncfile}') 
            rh.insert_failure(identifier, 'failure')
        else: 
            input_vars=rad1.fields.keys() 
            #ds = Dataset(ncfile, 'r', format="NETCDF4")
            #input_vars = set(ds.variables.keys())
            #ds.close()

        # Process the data
        script_cmd = f"RadxConvert -v -params {params_file} -f {ncfile}"
        print(f'[INFO] Running: {script_cmd}')
        if subprocess.call(script_cmd, shell=True) != 0:
            print('[ERROR] RadxConvert call resulted in an error')
            rh.insert_failure(identifier, 'failure')
            failure_count += 1
            continue
    
        #this line looks for the file generated from uncalib_v1 in calib_v1.
        expected_file = f'{SETTINGS.OUTPUT_DIR}/{scan_type}/{date}/{fname}'
    
        #print expected_file
        print("[INFO] Checking that the output file has been produced.")
        #Read input uncalibrated netcdf file and extract list of variables
        try:
            rad2=pyart.io.read(expected_file, delay_field_loading=True)
        except IOError:
            print(f'[ERROR] Expected file {expected_file} not found')
            rh.insert_failure(identifier,'bad_output')
            failure_count += 1
            continue
        else:
            output_vars=rad2.fields.keys() 
        
        print(f'[INFO] Found expected file {expected_file}')

        print(f'[INFO] Checking that the output variables match those in the input files')
        #Checks that the variables in the calibrated nc file are identical to the variables in the uncalibrated input files
        #If not, create a failure identifier called bad_vars
        keys_not_found=[]
        for key in input_vars:
            if not key in output_vars:
                keys_not_found.append(key)
     
        if len(keys_not_found)>0:
            print('[ERROR] Output variables are not the same as input variables'
                      f'{output_vars} != {input_vars}')
            failure_count += 1
            rh.insert_failure(identifier, 'bad_vars')
            continue
        else:
            print(f'[INFO] All expected variable were found: {output_vars}')
 
        rh.insert_success(identifier)

    #rh.close()

def main():
    """Runs script if called on command line"""

    args = arg_parse_chunk()
    loop_over_files(args)

if __name__ == '__main__':
    main() 
