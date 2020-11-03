# Conversion Scripts #

These scripts convert raw files (.vol, .ele, .azi) to netcdf files. Its structured into three tiers to help break up processing:

 * Time Series
 * Day
 * Hour

## Time series ##

``` 
convert_time_series.py -t <scan_type> -s <start_date> -e <end_date> 
```

Where <scan_type> can be one of `vol`, `ele`, or `azi`, and the dates are in the format YYYYMMDD.

Example:

```
convert_time_series.py -t vol -s 20191005 -e 20200615 
```

This script calls `convert_day.py` for each day in the time series.

## Day ##

``` 
convert_day.py -t <scan_type> -d <date> 
```

Where <scan_type> can be one of `vol`, `ele`, or `azi`, and <date> is in the format YYYYMMDD.

Example:

``` 
convert_day.py -t ele -d 20201012 
```

This script calls LOTUS with the `convert_hour.py` script which is passes `SETTINGS.CHUNK_SIZE` number of hours.

## Hour ##

``` 
convert_hour.py -t <scan_type> <hour_1> ... <hour_n> 
```

Where <scan_type> can be one of `vol`, `ele`, or `azi`, and <hour_n> is in the format YYYYMMDDHH.

Example:

``` 
convert_hour.py -t azi 2020101207 2020101208 2020101209 2020101210 2020101211 2020101212 
```

## Settings ##

All values in `SETTINGS.py` are explained in the file but there are some important values that must be changed if you're a new user:

 * `LOTUS_OUTPUT_PATH` - Where .out and .err files from LOTUS are output to
 * `PARAMS_FILE` - Location of your params file for RadexConvert