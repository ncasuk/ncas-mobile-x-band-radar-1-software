import pyart
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticks
from datetime import date
from datetime import time
from datetime import timedelta
import pandas as pd

import warnings
import glob
import gc
import copy
import os
import scipy as scipy

plt.switch_backend('agg')

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

def moving_average(data, size):
    """
    Run a moving window masked average along
    each ray of a data array (rays, gates), with size indicating the number
    of gates either side of the point to survey in the average.
    Parameters
    ----------
    data
    size
    Returns
    -------
    """
    out = np.ma.zeros(data.shape)  # Create the output array
    assert type(data) == np.ma.masked_array, 'Input data is not a masked array, use an alternative function or ' \
                                             'convert input to masked array before use'
    for ran in range(data.shape[1]):  # for each range gate
        # Normal condition
        if ran >= size:
            window = data[:, ran - size:ran + size]
       	    out[:, ran] = np.ma.average(window,
                                        axis=1)
            out[:, ran] = np.where(out[:, ran].mask == True,
                                   np.nan,
                                   out[:, ran])

        # Shortened window at start of the array
        else:
            out[:,ran] = np.nan
    return out

def moving_linear_masked_average(data, size, weights=False, weight_data=None):
    """
    Run a moving window masked average along
    each ray of a data array (rays, gates), with size indicating the number
    of gates either side of the point to survey in the average.
    Parameters
    ----------
    data
    size
    weights
    weight_data
    Returns
    -------
    """
    out = np.ma.zeros(data.shape)  # Create the output array
    assert type(data) == np.ma.masked_array, 'Input data is not a masked array, use an alternative function or ' \
                                             'convert input to masked array before use'
    for ran in range(data.shape[1]):  # for each range gate
        # Normal condition
        if ran >= size:
            window = data[:, ran - size:ran + size + 1]

            if weights:
                weight_window = weight_data[:, ran - size:ran + size + 1]
        # Shortened window at start of the array
        else:
            window = data[:, :ran + size + 1]
            if weights:
                weight_window = weight_data[:, :ran + size + 1]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            if weights:
                out[:, ran] = np.ma.average(window,
                                            weights=weight_window,
                                            axis=1)
                out[:, ran] = np.where(out[:, ran].mask == True,
                                       np.nan,
                                       out[:, ran])
            else:
                out[:, ran] = np.ma.average(window,
                                            axis=1)
                out[:, ran] = np.where(out[:, ran].mask == True,
                                       np.nan,
                                       out[:, ran])
    return out



def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    np.hanning, np.hamming, np.bartlett, np.blackman, np.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y

#Simple running average smooth
def simple_smooth(data,size):
    data_sm = np.zeros(data.shape)
#    first_valid_point = np.isfinite(data)
    for val in range(data.shape[1]): #0 to 999
        #print 'val=' , val
        if size <= val < data.shape[1]-size:
        #   print 'window = ', val-size , ' to ', val+size
            window = data[:, val - size:val + size]
            data_sm[:,val] = np.nanmedian(window,axis=1)            
        else:
            data_sm[:,val] = np.nan
    return data_sm     


def extract_phase(zdrdir,datadir,date,outdir):

    filelist = glob.glob(datadir+date+'/*.nc')
    if len(filelist)>0:
        ml_file = os.path.join(zdrdir,date,'day_ml_zdr.csv')
        ml_data = pd.read_csv(ml_file,index_col=0, parse_dates=True)
        rain_index = np.where(ml_data['ML'].notnull())[0]
        all_phase = []
        time = []
        for file in rain_index[0:10]:
            print(filelist[file])
            rad=pyart.io.read(filelist[file],delay_field_loading=True)                
            try:
                IP = pyart.correct.phase_proc.det_sys_phase(rad, ncp_lev=0.4, rhohv_lev=0.6, ncp_field='SQI', rhv_field='RhoHV', phidp_field='uPhiDP')
                all_phase.append(IP)
                time_of_file = filelist[file][120:135]
                time.append(time_of_file)                
            except:
                print(date, 'no uphidp')
                return False

    pdtime = pd.to_datetime(time,format = '%Y%m%d-%H%M%S')
    data = pd.DataFrame({'Initial Phase' : all_phase}, index=pdtime)
    phase_file = os.path.join(outdir,'initial_phase_'+date+'.csv')
    data.to_csv(phase_file)
    return True 
