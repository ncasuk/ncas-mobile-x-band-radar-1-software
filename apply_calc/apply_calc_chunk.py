# vim: et ts=4
import sys
import glob
import os
import SETTINGS
import argparse
import dateutil.parser as dp

#input file has this form
#/gws/nopw/j04/ncas_radar_vol2/data/xband/raine/cfradial/uncalib_v1/sur/20181101/ncas-mobile-x-band-radar-1_sandwith_20181101-090356_SUR_v1.nc

def arg_parse_chunk():

    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()
    type_choices = ['sur', 'rhi']

    parser.add_argument('-p', '--params_file', nargs=1, required=True, type=str, 
                        help=f'Index for params file given as an integer', metavar='')
    parser.add_argument('-f', '--files', nargs='*', required=True, type=str, 
                        help=f'List of files to process', metavar='')
    parser.add_argument('-t', '--scan_type', nargs=1, type=str,
                        choices=type_choices, required=True,
                        help=f'Type of scan, one of: {type_choices}',metavar='')
    
    return parser.parse_args()


def loop_over_files(args):

    params_file = args.params_file[0]
    input_files = args.files
    print("input_files= ",input_files)
    scan_type = args.scan_type[0]

    failure_count=0

    for ncfile in input_files:
        print("ncfile= ",ncfile)
        ncdate = os.path.basename(ncfile).split('_')[2].replace('-','')
    
        YYYY=ncdate[0:4]
        MM=ncdate[4:6]
        DD=ncdate[6:8]
        date=ncdate[0:8]

        failure_dir=os.path.join(SETTINGS.FAILURE_DIR,YYYY,MM,DD)
        success_dir=os.path.join(SETTINGS.SUCCESS_DIR,YYYY,MM,DD)
        if not os.path.exists(failure_dir):
            os.makedirs(failure_dir)
        if not os.path.exists(success_dir):
            os.makedirs(success_dir)
    
        # Test if too many failures have happened and if so, exit
        #if [ $failure_count -ge $EXIT_AFTER_N_FAILURES ]; then
        #    echo "[WARN] Exiting after failure count reaches limit: $EXIT_AFTER_N_FAILURES"
        #    exit 1
        #fi
    
        fname=os.path.basename(ncfile)
        success_file=os.path.join(success_dir,fname)
        failure_file=os.path.join(failure_dir,fname)
    
        # Remove previous error files (if present)
        if os.path.exists(failure_file):
            os.remove(failure_file)
    
        if os.path.exists(success_file):
            print("[INFO] Already ran: ", ncfile)
            print("Success file found: ", success_file)
            continue
    
        # Process the data
        script_cmd = f"RadxConvert -v -params {params_file} -f {ncfile}"
        print(f'[INFO] Running: {script_cmd}')
        #if subprocess.call(script_cmd, shell=True) != 0:
        #    print('[ERROR] RadxConvert call resulted in an error')
        #    #rh.insert_failure(identifier, 'failure')
        #    failure_count += 1
        #    continue
    
        #this line looks for the file generated from uncalib_v1 in calib_v1.
        output_dir=os.path.join(SETTINGS.OUTPUT_DIR,scan_type,date)
        expected_file=os.path.join(output_dir,fname)
    
        #print expected_file
        print("[INFO] Checking that the output file has been produced.")
    
        if not os.path.exists(expected_file):
            print("[ERROR] Failed to generate output file: ", expected_file)
            failure_count += 1
            f=open(failure_file,'w')
            f.write("")
            f.close()
            print("written failure file")
            continue
        else:
            print("[INFO] Found expected file: ", expected_file)
            f=open(success_file,'w')
            f.write("")
            f.close()
            print("written success file")

def main():
    """Runs script if called on command line"""

    args = arg_parse_chunk()
    loop_over_files(args)

if __name__ == '__main__':
    main() 
