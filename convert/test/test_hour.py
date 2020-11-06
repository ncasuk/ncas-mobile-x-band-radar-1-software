from argparse import Namespace
from convert import convert_hour
import os
import pytest
import subprocess
from convert import SETTINGS

def test_RadxConvert():
    # Could maybe check more in-depth into netcfd output
    example_file = f'{SETTINGS.INPUT_DIR}/sandwith01_data.vol/2020-04-07/2020040713415800dBZv.vol'
    cmd = f'RadxConvert -v -params {SETTINGS.PARAMS_FILE} -f {example_file}'
    return_code = subprocess.call(cmd, shell=True)

    example_expected = f'{SETTINGS.OUTPUT_DIR}/sur/20200407/ncas-mobile-x-band-radar-1_sandwith_20200407-134158_SUR_v1.nc'

    assert(return_code == 0)
    assert(os.path.exists(example_expected))

def test_output_one_hour():
    example_hour = '2020040705'
    example_scan_type = 'vol'
    example_args = Namespace(scan_type=[example_scan_type], hours=[example_hour])

    convert_hour.loop_over_hours(example_args)

    """
    Files that should be found

    2020040705045800dBZv.vol
    2020040705105400dBZv.vol
    2020040705165000dBZv.vol
    2020040705224400dBZv.vol
    2020040705284000dBZv.vol
    2020040705344900dBZv.vol
    2020040705404200dBZv.vol
    2020040705463700dBZv.vol
    2020040705523200dBZv.vol
    2020040705582800dBZv.vol
    """

    # If file isn't produced then that should be seen in the results handler but can check manually here

    example_expected_files = ['2020040705045800dBZv.vol', '2020040705105400dBZv.vol', '2020040705165000dBZv.vol'
                              '2020040705224400dBZv.vol', '2020040705284000dBZv.vol', '2020040705344900dBZv.vol'
                              '2020040705404200dBZv.vol', '2020040705463700dBZv.vol', '2020040705523200dBZv.vol'
                              '2020040705582800dBZv.vol']

    for fname in example_expected_files:
        expected_path = f'{SETTINGS.OUTPUT_DIR}/sur/20200407/' \
                        f'ncas-mobile-x-band-radar-1_sandwith_20200407-{fname[8:14]}_SUR_v1.nc'
        assert(os.path.exists(expected_path))

