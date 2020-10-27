import pyart
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticks 
from datetime import date
from datetime import time
from datetime import timedelta
import pandas as pd
from functions import moving_average

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

#---------------------------------------------------------------------------------------
#Extract ML, ZDR from vertical scans and save to day_ml_zdr.csv'

def process_zdr_scans(outdir,raddir,date,file,plot):
 
    filelist = glob.glob(raddir+date+'/*.nc')
    filelist.sort()    
    
    ML=np.zeros(300)*np.nan;
    nvals=np.zeros(300)*np.nan;
    mean_zdr=np.zeros(300)*np.nan;
    med_zdr=np.zeros(300)*np.nan;
    std_zdr=np.zeros(300)*np.nan;
    std_err=np.zeros(300)*np.nan;
    T=np.zeros(300)*np.nan;
    fileindex=np.zeros(300)*np.nan;

    #Loop through files for a given day
    for F in range (0,len(filelist)):
    #for F in range (203,205):
        print F
	#print filelist[F]
        #Read file
        rad=pyart.io.read(filelist[F])

        el = copy.deepcopy(rad.elevation['data'])
        el = el[::360]
        radh = copy.deepcopy(rad.altitude['data'])
        az = copy.deepcopy(rad.azimuth['data'])
        rg = copy.deepcopy(rad.range['data']/1000)
        rg_sp = rg[1]-rg[0]
        max_gate = rg.size
        
	try:
	    rhohv = copy.deepcopy(rad.fields['RhoHV']['data'])
	    uzh = copy.deepcopy(rad.fields['dBuZ']['data'])
            zdru = copy.deepcopy(rad.fields['ZDRu']['data'])
            v = copy.deepcopy(rad.fields['Vu']['data'])
            v2 = copy.deepcopy(rad.fields['Vu']['data'])

    	except:
            print "Couldn't load all variables"    
            continue

        #Create time array
        time = rad.metadata['start_datetime']
        hh = float(time[11:13])
        mm = float(time[14:16])
        ss = float(time[17:19])
        T[F] = hh + mm/60.0 + ss/3600.0
        daystr = time[0:4]+time[5:7]+time[8:10]
        
        if hh<10:
            if mm<10:
                timestr = '0' + str(int(hh)) + '0' + str(int(mm))
            else:
                timestr = '0' + str(int(hh)) + str(int(mm))
        elif mm<10:
            timestr = str(int(hh)) + '0' + str(int(mm))
        else:
            timestr = str(int(hh)) + str(int(mm))
       
        img_name = os.path.join(outdir,date,'vert_profs_' + daystr + '_' + timestr + '.png') 
        if os.path.exists(img_name):
            continue

	ind = v>6.0
        v2[ind] = -7.9725 - (7.9725-v[ind])

        rhv_prof = np.nanmean(rhohv,axis=0)
        uzh_prof = np.nanmean(uzh,axis=0)
        v_prof = np.nanmean(v2,axis=0)
        zdru_prof = np.nanmean(zdru,axis=0)

        ind = np.logical_and(rhv_prof > 0.99, np.logical_and(uzh_prof > 0,  v_prof <- 2))

        #Check if any of the data fit the criteria

        #If no, skip to next iteration of the loop i.e. next file
        if np.sum(ind==True)==0:
            continue

        #Find index of good data
        i = np.where(ind==True)
        
        #Find starting point, lowest rain gate
        ind2 = i[0][0]
        if rg[ind2]>1.0:
            print 'lowest point is above 1km'
            continue       
 
        #Find bottom of the melting layer, i.e. top of the rain by finding gaps in the good data
        #First check if there are any gaps
	#Find data gaps greater than 8 points. If size==0 then there arent any gaps, so use the top point of the selected data
        if np.where(np.diff(i[0])>8)[0].size == 0:
            ind3=i[0][-1]            
        else:
            ind3 = i[0][np.where(np.diff(i[0])>8)[0][0]]+1                        
        
        #If the section of data is less than 0.48km (16*0.03) then skip to next volume
        if ind3-ind2<16:
            continue

        #Count the number of data points
        nvals[F] = ind3-ind2+1


	grad_v = np.gradient(v_prof)
    	grad_rhv = np.gradient(rhv_prof)

	max_grad_v_ind = np.where(grad_v==np.max(grad_v[ind3:ind3+17]))[0][0]
    	max_grad_v = grad_v[max_grad_v_ind]
    	#print 'max grad_v = ', max_grad_v, ' at height of ', rg[max_grad_v_ind]
    
    	min_grad_rhv_ind = np.where(grad_rhv==np.min(grad_rhv[ind3:ind3+17]))[0][0]
    	min_grad_rhv = grad_rhv[min_grad_rhv_ind]
    	#print 'max_grad_rhv = ', max_grad_rhv, 'at height of ', rg[max_grad_rhv_ind]
	
	if np.logical_or(np.logical_and(np.logical_and(max_grad_v_ind > ind3, 0.15 <= max_grad_v < 0.25), min_grad_rhv <-0.015),\
            np.logical_and(max_grad_v_ind > ind3, max_grad_v >0.25)):

            #Define Melting Level height as the height at the top of the valid data i.e. first rain point 
            #Need to add on radar height to get height above sea level
            fileindex[F] = F
            ML[F] = rg[ind3] + (radh /1000)
            med_zdr[F] = np.median(zdru_prof[ind2:ind3])
            std_zdr[F] = np.std(zdru_prof[ind2:ind3])


            if plot==1:
                print 'graph plotted' 
        	fig = plt.figure(figsize=(10,7))    
                ax1 = fig.add_subplot(141)
                ax1.plot(rhv_prof,rg,'kx-')
                ax1.plot(rhv_prof[ind2:ind3],rg[ind2:ind3],'bx')
                ax1.set_ylim([0, 6])
                ax1.set_xlim(0.9,1)
                ax1.set_xlabel('RhoHV')
                ax2 = fig.add_subplot(142)
                ax2.plot(uzh_prof,rg,'kx-')
                ax2.plot(uzh_prof[ind2:ind3],rg[ind2:ind3],'bx')
                ax2.set_ylim([0, 6])
                ax2.set_xlabel('dBuZ')
                ax3 = fig.add_subplot(143)
                ax3.plot(v_prof,rg,'kx-')
                ax3.plot(v_prof[ind2:ind3],rg[ind2:ind3],'bx')
                ax3.set_ylim([0, 6])
                ax3.set_xlabel('V')
                ax4 = fig.add_subplot(144)
                ax4.plot(zdru_prof,rg,'kx-')
                ax4.plot(zdru_prof[ind2:ind3],rg[ind2:ind3],'bx')
                ax4.set_ylim([0, 6])
                ax4.set_xlabel('ZDRu')
                if mm<10:
                #   timestr = str(int(hh)) + '0' + str(int(mm))
                    fig.suptitle(timestr)
                else:
                #   timestr = str(int(hh)) + str(int(mm))
                    fig.suptitle(timestr)
           
                #plt.tight_layout()
                #file_name = os.path.join(outdir,date,'vert_profs_' + daystr + '_' + timestr + '.png') 
                #print file_name
                #file_path = os.path.join(outdir,date,file_name)
                
                if not os.path.exists(os.path.join(outdir,date)):
                    os.makedirs(os.path.join(outdir,date))
    
                plt.savefig(img_name,dpi=150)
                plt.close()
                plt.clf()
    	    
            data_array = np.stack([zdru_prof, rhv_prof, uzh_prof, v_prof],axis=1)
            np.savetxt(os.path.join(outdir, date, 'vert_profs_' + daystr + '_' + timestr + '.txt'), data_array, delimiter=',')
            print 'data file saved'

	del rad
	del zdru, rhohv, uzh, v 
	gc.collect()

    if np.isfinite(ML).any() or np.isfinite(med_zdr).any():

        if not os.path.exists(outdir + date):
            os.makedirs(outdir + date)

        T2 = pd.to_datetime(date) + pd.to_timedelta(T, unit='h')
        output = pd.DataFrame({'ZDR' : med_zdr, 'ML' : ML}, index=T2)
        output.to_csv(file)
	return True

    else:
	return False
#        output = pd.DataFrame()
#        output.to_csv(file)

#---------------------------------------------------------------------------------------------
#Calculate hourly median values of ML heights to use for Z calibration

def calc_hourly_ML(outdir,date):        
   
    hourly_ml_zdr = pd.DataFrame() 
    file1 = os.path.join(outdir, date, 'day_ml_zdr.csv')
    file2 = os.path.join(outdir, date, 'hourly_ml_zdr.csv')

    #if os.path.exists(file1):
    data = pd.read_csv(file1,index_col=0, parse_dates=True)

    if data.empty==False:

        hourly_ml = np.zeros(24)*np.nan
        hourly_zdr = np.zeros(24)*np.nan
    
        for hh in range(0,24):
            beg=time(hh,0,0)
            if hh==23:
                end=time(23,59,0)            
            else:
                end=time(hh+1,0,0)
    
            #Find values of ML and Median ZDR between each hourly period
            ml_zdr=data[['ML','ZDR']].between_time(beg,end,include_end=False)
        
            #If there are less than 3 (out of 9) valid values, set all to NaN and continue
            if ml_zdr['ML'].count()<3:
                hourly_ml[hh]=float('nan')
                hourly_zdr[hh]=float('nan')
                continue
            else:
                M=ml_zdr.median()
        
                #Median Absolute Deviation
                mad=1.4826*(abs(ml_zdr-M)).median()
                out=mad*2.5
                ind = np.logical_or(ml_zdr <= M-out, ml_zdr >= M+out)
        
                ml_zdr[ind==True]=np.nan
      
                hourly_ml[hh]=ml_zdr['ML'].median()
                hourly_zdr[hh]=ml_zdr['ZDR'].median()
           
        if np.isfinite(hourly_ml).any():      
        
            #Construct time array for hourly medians i.e. 00:30, 01:30
            hourly_T = pd.to_datetime(date) + pd.timedelta_range('00:30:00','23:30:00',freq='1H')
            hourly_ml_zdr = pd.DataFrame({'H_ML' : hourly_ml, 'H_ZDR' : hourly_zdr}, index=hourly_T)
            #print 'here'
        
            hourly_ml_zdr = hourly_ml_zdr.dropna()
            #print median_ML
            hourly_ml_zdr.to_csv(file2)
        
            return True        
        else:
            return False

#------------------------------------------------------------------------------------------------------
def extract_ml_zdr(time, ml_zdr):

#Extract ML and ZDR values corresponding to radar file time
#ml_zdr is the dataframe
#ft = radar file time   
    ft = pd.to_datetime(time)
    ft=ft.tz_convert(None)

#Index of nearest values to ft
    indf = ml_zdr.index.get_loc(ft, method='nearest')
    #print ft, ml_zdr.index[indf] 
#If radar file time is earlier than first index of ml_zdr, set ml and zdr to first value in file
    if ft >= ml_zdr.index[-1]:

        mlh=ml_zdr['H_ML'][-1]
        zdr_bias=ml_zdr['H_ZDR'][-1]

#If radar file time is later than last index of ml_zdr, set ml and zdr to last value in file
    elif ft <= ml_zdr.index[0]:

        mlh=ml_zdr['H_ML'][0]
        zdr_bias=ml_zdr['H_ZDR'][0]

#If radar file time equals an index of ml_zdr, set ml and zdr to those values.
    elif ft == ml_zdr.index[indf]:

        mlh=ml_zdr['H_ML'][indf]
        zdr_bias=ml_zdr['H_ZDR'][indf]
   
#Else find time indices either side of file time and linearly interpolate between them               
    else:
        if ft > ml_zdr.index[indf]:

            st = indf
            fn = indf+1

        elif ft < ml_zdr.index[indf]:

            st = indf-1
            fn = indf

        t2 = (abs(ft - ml_zdr.index[st])).seconds
        t3 = (abs(ml_zdr.index[fn]-ml_zdr.index[st])).seconds
        t4 = float(t2) / float(t3)

        #Melting layer height interpolated linearly between hourly values
        mlh = ml_zdr['H_ML'][st] + (ml_zdr['H_ML'][fn] - ml_zdr['H_ML'][st]) * t4

        #ZDR interpolated linearly between hourly values
        zdr_bias = ml_zdr['H_ZDR'][st] + (ml_zdr['H_ZDR'][fn] - ml_zdr['H_ZDR'][st]) * t4

    return mlh, zdr_bias

###------------------------------------------------------------------------------------------------------
##def calibrate_day_v2(raddir, outdir, day, ml_zdr):
##
##    ZDRmax = 2.0
##    min_path = 15
##    filelist = glob.glob(os.path.join(raddir,'*.nc'))
##    filelist.sort()
##    nfiles=len(filelist)
##    print nfiles
##
##    #raine 10 elevations: 0.5, 1, 1.5, 2, 3, 4.5, 6, 7.5, 10, 20 
##    ss=3600
##
##    #create empty array for calibration offsets
##    delta_all=np.zeros((nfiles,ss))*np.nan
##    #create empty array for PhiEst and PhiObs
##    phiest_all=np.zeros((nfiles,ss))*np.nan
##    phiobs_all=np.zeros((nfiles,ss))*np.nan
##    startphi_all=np.zeros((nfiles,ss))*np.nan
##    #create empty array for Time
##    T = np.zeros((nfiles))*np.nan
##    #create empty array for number of good rays in each volume
##    good_rays = np.zeros((nfiles))*np.nan
##    #Create empty array for good ray index
##    ray_index = np.zeros((nfiles,ss))*np.nan
##    ray_az = np.zeros((nfiles,ss))*np.nan
##    ray_el = np.zeros((nfiles,ss))*np.nan
##
##
##    for file in range(nfiles):
##    #for file in (30,):
##        print file
##
##        #Read file
##        rad=pyart.io.read(filelist[file])
##
##        #Create time array
##        time = rad.metadata['start_datetime']
##        hh = float(time[11:13])
##        mm = float(time[14:16])
##        ss = float(time[17:19])
##        T[file] = hh + mm/60.0 + ss/3600.0
##
##        #Extract dimensions
##        Rdim = rad.ngates
##        Edim = rad.nsweeps
##        Tdim = rad.nrays
##        Adim = Tdim/Edim
##
##        #Extract data
##        try:
##            rg = copy.deepcopy(rad.range['data']/1000)
##            rg_sp = rg[1]-rg[0]
##            max_gate = rg.size
##            el = copy.deepcopy(rad.elevation['data'])
##            el = el[::360]
##            radh = copy.deepcopy(rad.altitude['data'])
##            az = copy.deepcopy(rad.azimuth['data'])
##            uzh = copy.deepcopy(rad.fields['dBuZ']['data'])
##            zdr = copy.deepcopy(rad.fields['ZDR']['data'])
##            rhohv = copy.deepcopy(rad.fields['RhoHV']['data'])
##            kdp = copy.deepcopy(rad.fields['KDP']['data'])
##
##            phidp = copy.deepcopy(rad.fields['PhiDP']['data'])
##            ind = phidp > 180
##            phidp[ind] = phidp[ind] - 360
##            ind = phidp < -180
##            phidp[ind] = phidp[ind] + 360
##
##	    uphidp = copy.deepcopy(rad.fields['uPhiDP']['data'])
##            #Set invalid values (-9e33) to nans
##            ind = uphidp.mask==True
##            uphidp[ind]=np.nan
##
##        except:
##            print "Couldn't load all variables"    
##            continue
##
##        #Calculate height of every range gate
##        beam_height = np.empty((Tdim,Rdim))
##        for j in np.arange(0,Edim):
##            for i in np.arange(0,Adim):
##                beam_height[(360*j)+i,:] = radh/1000 + np.sin(np.deg2rad(el[j]))*rg + np.sqrt(rg**2 + (6371*4/3.0)**2) - (6371*4/3.0);
##
##        mlh, zdr_bias = extract_ml_zdr(time, ml_zdr)
##
##        zind = beam_height > mlh   
##        uzh[zind==True] = np.nan
##        #zind = beam_height < 0.5    
##        #uzh[zind==True] = np.nan
##
##        zdr[zind==True] = np.nan
##        phidp[zind==True] = np.nan
##        uphidp[zind==True] = np.nan
##        kdp[zind==True] = np.nan
##        rhohv[zind==True] = np.nan
##
##        #Get rid of first 2km
##        n=13
##        uzh = uzh[:,n:]
##        zdr = zdr[:,n:]
##        phidp = phidp[:,n:]
##        uphidp = uphidp[:,n:]
##        kdp = kdp[:,n:] 
##        rhohv = rhohv[:,n:]
##
##        rg = rg[n:]
##
##        #Create empty arrays for observed and calculated PhiDP
##        phiobs = np.zeros([Tdim])*np.nan
##        phiest = np.zeros([Tdim])*np.nan        
##        startphi = np.zeros([Tdim])*np.nan        
##
##        c=0
##
### Exclusions is a list of tuples (), where each tuple is a pair of tuples.
### The first tuple of each pair is the start and stop elevation of the segment to exclude
### and the second tuple contains the start and stop azimuth of the segment to exclude.
### This "one-liner" builds a generator from the list of tuples so each tuple defines a binary array which is True
### where the segment occurs and false elsewhere. All conditions must be met, so between start and stop in both
### azimuth and elevation. These are then combined to a single array using np.any to create a single exclude binary array which is True where
### any of the segments are found and False in non-excluded places
##
##    	exclusions = [((0,90.1),(20,160)),((0,90.1),(201,207)),((0,0.51),(185,201.5))]
##        exclude_radials = np.any([np.all([rad.elevation['data']>=ele[0],
##                                  rad.elevation['data']<ele[1],
##                                  rad.azimuth['data']>=azi[0],
##                                  rad.azimuth['data']<azi[1]],axis=0) for ele, azi in exclusions],axis=0)
##	az_index = np.where(~exclude_radials)[0]
##
##        for i in az_index:
##        #for i in (778,):
##
##            #Extract ray
##            phidp_f = phidp[i,:]
##            uphidp_f = uphidp[i,:]
##            #uphidp_sm_f = uphidp_sm[i,:]
##            uzh_f = uzh[i,:]
##            zdr_f = zdr[i,:] - zdr_bias
##            rhohv_f = rhohv[i,:]
##
##            #attenuation correction
##            #phidp_att = copy.deepcopy(phidp_f)
##            phidp_att = phidp_f - phidp_f[0]
##
##            PA = np.maximum.accumulate(phidp_att) 
##            uzh_att = uzh_f + 0.28*PA
##            zdr_att = zdr_f + 0.04*PA
##
##            #Check for all-nan array, go to next iteration of loop if so
##            if np.sum(np.isfinite(phidp_att)==True)==0:
##                continue
##
###            #Find minimum value of PhiDP and shift ray to start at that value
###            phi1_valid = (np.nonzero(np.isfinite(phidp_f)))[0]
###            if phi1_valid.size != 0:
###                phi1 = phi1_valid[0]
###                phidp_f=phidp_f-phidp_f[phi1]
##
##            #Find minimum value of PhiDP
##            phi1_valid = np.where(np.isfinite(phidp_att))[0]
##            if phi1_valid.size != 0:
##                phi1 = phi1_valid[0]
##            else:
##                continue
###            #Find indices where PhiDP is between 4 and 6 degs    
###            ind = np.where(np.logical_and(phidp_f > 4, phidp_f < 6))[0]
##
##            #Find indices where PhiDP has increased to between 4 and 6 degs    
##            ind = np.where(np.logical_and(phidp_att > 4, phidp_att < 6))[0]
##            #print 'ind.size = ', ind.size
##            #If values exist, 
##            if ind.size != 0:
##                #Find the index of the maximum value of PhiDP between 4 and 6
##                ib = np.where(phidp_att==max(phidp_att[ind]))[0][0]
##                #print '1. index and value of maximum phidp_f between 4&6=', ib, phidp_f[ib]
##
##                pdpmax = phidp_att[ib]
###                path_len = (np.sum(np.isfinite(uzh_f[0:ib+1])==True))*rg_sp
##                #path_len = (np.sum(np.isfinite(uzh_f[phi1:ib+1])==True))*rg_sp
##                path_len = rg[ib]
##                #print '2. maxmimum phidp=', pdpmax, 'Path length=', path_len
##
##                #if path of significant returns exceeds min_path
##                #if np.logical_and(path_len > min_path, pdpmax > 4):
##                if path_len > min_path:
##                    #print '3.', con1
##                    #print "step1"
##                    #plt.plot(zdr_f[0:ib+1])
##
##                    #exclude rays with any bad pixels (heavy rain (mie-scattering))
###                    ind = zdr_f[0:ib+1] > ZDRmax
##                    ind = zdr_att[phi1:ib+1] > ZDRmax
##                    #print '4.', np.sum(ind) < 1
##
##                    if np.sum(ind) < 1:
##                        #plt.plot(rhohv_f[0:ib+1])
##                        #print "step2"
##
##                        #exclude rays where 3 or more values of RhoHV are less than 0.98, i.e. not rain
##                        #ind = rhohv_f[0:ib+1] < 0.98
##                        ind = np.logical_and(rhohv_f > 0.0, rhohv_f < 0.98)
##                        #print '5.', np.sum(ind) < 3
##                        #print uzh_f[0:10]
##                        #print uzh_f_all[0,0:10]
##                        #if np.sum(ind) < 3:   
##
###                        if np.sum(ind[0:ib+1]) < 3:   
##                        if np.sum(ind[phi1:ib+1]) < 3:   
##                            #print i
##                            #index of good rays (value from 0 to 4320)
##                            ray_index[file,i] = i
##                            ray_az[file,i] = rad.azimuth['data'][i]
##                            ray_el[file,i] = rad.elevation['data'][i]
##
##                            #print i
##                            uzh_att[ind] = np.nan
##                            zdr_att[ind] = np.nan
##                            #phidp_f[ind] = np.nan
##                            #uphidp_sm_f[ind] = np.nan
##			    #uphidp_sm_f.mask[ind] = np.nan
##                            #rhohv_f[ind] = np.nan
##
##                            startphi[i] = np.nanmedian(uphidp_f[phi1:phi1+10])
##
##                            phiobs[i] = pdpmax
##                            #phiobs_all[file,:] = phiobs
##
##                            #kdpest = 1e-05 * (11.74 - 4.020*zdr_f - 0.140*zdr_f**2 + 0.130*zdr_f**3)*10 ** (uzh_f/10)
##                            kdpest = 1e-05 * (11.74 - 4.020*zdr_att - 0.140*zdr_att**2 + 0.130*zdr_att**3)*10 ** (uzh_att/10)
##
##                            tmpphi = np.nancumsum(kdpest)*rg_sp*2
##                            #phiest[c] = tmpphi[ib]
##                            phiest[i] = tmpphi[ib]
##                            print 'phiest = ', phiest[i] 
##                            c = c + 1
##
##        #phiest is a function of ray, phiest(4320)
##        #phiest_all is a function of volume and ray, phiest_all(289,4320)
##        #delta is a function of ray, delta(4320)
##        #delta_all is a function of volume and ray, delta_all(289,4320)
##
##    	phiobs_all[file,0:Tdim] = phiobs
##    	phiest_all[file,0:Tdim] = phiest
##    	startphi_all[file,0:Tdim] = startphi
##
##    	good_rays[file] = c-1;
##	print 'file=',file,'rays=',str(c)
##    	del rad
##    	del zdr, rhohv, kdp, phidp, uzh, uphidp
##    	gc.collect()
##                    
##        #print phiobs.shape   
##        #delta = ((phiest-phiobs)/phiobs)*100
##        #print delta.shape
##        #print file
##        #delta_all[file,:] = delta
##        #print 'end'    
##        #filename = outdir + 'file%03.d_phiest_phiobs_delta' %(file)
##        #data_save=np.vstack((phiest,phiobs,delta))
##        #np.save(filename,data_save)          
##
##    #filename = outdir + 'good_rays'     
##    #np.save(filename,good_rays)
##    print np.sum(np.isfinite(phiest_all.flatten()))
##    if np.sum(np.isfinite(phiest_all.flatten())) !=0:
##        print "phiest and phiobs values exist"
##        phiest_filename = os.path.join(outdir, 'phiest_all_att_' + day)
##        np.save(phiest_filename,phiest_all)
##        phiobs_filename = os.path.join(outdir, 'phiobs_all_att_' + day)
##        np.save(phiobs_filename,phiobs_all)
##        startphi_filename = os.path.join(outdir, 'startphi_all_' + day)
##        np.save(startphi_filename,startphi_all)
##        return True
##    else:
##        return False
##
##
###------------------------------------------------------------------------------------------------------
##def calibrate_day(raddir, outdir, day, ml_zdr):
##
##    ZDRmax = 2.0
##    min_path = 15
##    filelist = glob.glob(os.path.join(raddir,'*.nc'))
##    filelist.sort()
##    nfiles=len(filelist)
##    print nfiles
##
##    #chilbolton
##    #ss=4680
##    #raine 10 elevations: 0.5, 1, 1.5, 2, 3, 4.5, 6, 7.5, 10, 20 
##    ss=3600
##
##    #create empty array for calibration offsets
##    delta_all=np.zeros((nfiles,ss))*np.nan
##    #create empty array for PhiEst and PhiObs
##    phiest_all=np.zeros((nfiles,ss))*np.nan
##    phiobs_all=np.zeros((nfiles,ss))*np.nan
##    startphi_all=np.zeros((nfiles,ss))*np.nan
##    #create empty array for Time
##    T = np.zeros((nfiles))*np.nan
##    #create empty array for number of good rays in each volume
##    good_rays = np.zeros((nfiles))*np.nan
##    #Create empty array for good ray index
##    ray_index = np.zeros((nfiles,ss))*np.nan
##    ray_az = np.zeros((nfiles,ss))*np.nan
##    ray_el = np.zeros((nfiles,ss))*np.nan
##
##
##    for file in range(nfiles):
##    #for file in (181,):
##
##        #print filelist[file]
##        print file
##        #if file < 59:
##        #    continue
##
##        #Read file
##        rad=pyart.io.read(filelist[file])
##
##        #Create time array
##        time = rad.metadata['start_datetime']
##        hh = float(time[11:13])
##        mm = float(time[14:16])
##        ss = float(time[17:19])
##        T[file] = hh + mm/60.0 + ss/3600.0
##
##        #Extract dimensions
##        Rdim = rad.ngates
##        Edim = rad.nsweeps
##        Tdim = rad.nrays
##        Adim = Tdim/Edim
##
##        #Extract data
##        try:
##            rg = copy.deepcopy(rad.range['data']/1000)
##            rg_sp = rg[1]-rg[0]
##            max_gate = rg.size
##            el = copy.deepcopy(rad.elevation['data'])
##            el = el[::360]
##            radh = copy.deepcopy(rad.altitude['data'])
##            az = copy.deepcopy(rad.azimuth['data'])
##            #print 'elevation, azimuth, range array sizes=', el.shape, az.shape, rg.shape
##            uzh = copy.deepcopy(rad.fields['dBuZ']['data'])#[rad.sweep_start_ray_index['data'][0]]
##            #print 'variable sizes=', uzh.shape
##            zdr = copy.deepcopy(rad.fields['ZDR']['data'])
##            rhohv = copy.deepcopy(rad.fields['RhoHV']['data'])
##            kdp = copy.deepcopy(rad.fields['KDP']['data'])
##
##            phidp = copy.deepcopy(rad.fields['PhiDP']['data'])
##            ind = phidp > 180
##            phidp[ind] = phidp[ind] - 360
##            ind = phidp < -180
##            phidp[ind] = phidp[ind] + 360
##
##	    uphidp = copy.deepcopy(rad.fields['uPhiDP']['data'])
##            #Set invalid values (-9e33) to nans
##            ind = uphidp.mask==True
##            uphidp[ind]=np.nan
##
##        except:
##            print "Couldn't load all variables"    
##            continue
##
##        #Calculate height of every range gate
##        beam_height = np.empty((Tdim,Rdim))
##        for j in np.arange(0,Edim):
##            for i in np.arange(0,Adim):
##                beam_height[(360*j)+i,:] = radh/1000 + np.sin(np.deg2rad(el[j]))*rg + np.sqrt(rg**2 + (6371*4/3.0)**2) - (6371*4/3.0);
##
##        mlh, zdr_bias = extract_ml_zdr(time, ml_zdr)
##
##        zind = beam_height > mlh   
##        uzh[zind==True] = np.nan
##        #zind = beam_height < 0.5    
##        #uzh[zind==True] = np.nan
##
##        zdr[zind==True] = np.nan
##        phidp[zind==True] = np.nan
##        uphidp[zind==True] = np.nan
##        kdp[zind==True] = np.nan
##        rhohv[zind==True] = np.nan
##
###       Remove first 2km of data
##        n=13
##        uzh = uzh[:,n:]
##        zdr = zdr[:,n:]
##        phidp = phidp[:,n:]
##        uphidp = uphidp[:,n:]
##        kdp = kdp[:,n:] 
##        rhohv = rhohv[:,n:]
##        rg = rg[n:] - rg[n]
##
##        #Set first 2km to NaN
###        uzh[:,0:n] = np.nan
###        zdr[:,0:n] = np.nan
###        phidp[:,0:n] = np.nan
###        phidp[:,0:n].mask = True
###        uphidp[:,0:n] = np.nan
###        uphidp[:,0:n].mask = True
###        kdp[:,0:n] = np.nan
###        rhohv[:,0:n] = np.nan
##
##
##        #a1 = rhohv.shape[0]
##        #a2 = rhohv.shape[1]
##        #print a1, a2
##
##        #Create empty arrays for observed and calculated PhiDP
##        phiobs = np.zeros([Tdim])*np.nan
##        phiest = np.zeros([Tdim])*np.nan        
##        startphi = np.zeros([Tdim])*np.nan        
##
##        c=0
##        #Loop through every ray in the volume
##        #for i in range(0,Tdim):
##        #only use elevations 2 to 10 (i.e. 1 deg to 10 degs)
##
###chilbolton
###	az_index = np.where( np.all([rad.elevation['data']>1.0,rad.elevation['data']<8.5,
###                   rad.azimuth['data']>0,rad.azimuth['data']<49],axis=0) | 
###           	   np.all([rad.elevation['data']>1.0,rad.elevation['data']<8.5,                 
###                   rad.azimuth['data']>190,rad.azimuth['data']<360],axis=0) |
###           	   np.all([rad.elevation['data']>1.0,rad.elevation['data']<8.5,                 
###                   rad.azimuth['data']>90,rad.azimuth['data']<130],axis=0))[0]
##
###RAIN-E
###	az_index = np.where( np.all([rad.elevation['data']>0.5,rad.elevation['data']<10,
###                   rad.azimuth['data']>0,rad.azimuth['data']<20],axis=0) | 
###           	   np.all([rad.elevation['data']>0.5,rad.elevation['data']<10,                 
###                   rad.azimuth['data']>160,rad.azimuth['data']<360],axis=0))[0]
##
###	az_index = np.where(np.all([rad.azimuth['data']>0,rad.azimuth['data']<20],axis=0) | 
###           	   np.all([rad.azimuth['data']>160,rad.azimuth['data']<360],axis=0))[0]
##
### Exclusions is a list of tuples (), where each tuple is a pair of tuples.
### The first tuple of each pair is the start and stop elevation of the segment to exclude
### and the second tuple contains the start and stop azimuth of the segment to exclude.
### This "one-liner" builds a generator from the list of tuples so each tuple defines a binary array which is True
### where the segment occurs and false elsewhere. All conditions must be met, so between start and stop in both
### azimuth and elevation. These are then combined to a single array using np.any to create a single exclude binary array which is True where
### any of the segments are found and False in non-excluded places
##
##    	exclusions = [((0,90.1),(20,160)),((0,90.1),(201,207)),((0,0.51),(185,201.5))]
##        exclude_radials = np.any([np.all([rad.elevation['data']>=ele[0],
##                                  rad.elevation['data']<ele[1],
##                                  rad.azimuth['data']>=azi[0],
##                                  rad.azimuth['data']<azi[1]],axis=0) for ele, azi in exclusions],axis=0)
##	az_index = np.where(~exclude_radials)[0]
##
##        for i in az_index:
##
##            #Extract ray
##            phidp_f1 = phidp[i,:]
##            uphidp_f = uphidp[i,:]
##            #uphidp_sm_f = uphidp_sm[i,:]
##            uzh_f = uzh[i,:]
##            zdr_f = zdr[i,:] - zdr_bias
##            rhohv_f = rhohv[i,:]
##
##
##            #Check for all-nan array, go to next iteration of loop if so
##            if np.sum(np.isfinite(phidp_f)==True)==0:
##                continue
##            
##            phidp_f = phidp_f1 - phidp_f1[0]
##
##            #Find minimum value of PhiDP
##            phi1_valid = (np.nonzero(np.isfinite(phidp_f)))[0]
##            if phi1_valid.size != 0:
##                phi1 = phi1_valid[0]
##            else:
##                continue
###            #Find indices where PhiDP is between 4 and 6 degs    
###            ind = np.where(np.logical_and(phidp_f > 4, phidp_f < 6))[0]
##
##            #Find indices where PhiDP has increased to between 4 and 6 degs    
##            ind = np.where(np.logical_and(phidp_f > 4, phidp_f < 6))[0]
##
##            #If values exist, 
##            if ind.size != 0:
##                #Find the index of the maximum value of PhiDP between 4 and 6
##                ib = np.where(phidp_f==max(phidp_f[ind]))[0][0]
##                #print '1. index and value of maximum phidp_f between 4&6=', ib, phidp_f[ib]
##
##                pdpmax = phidp_f[ib]
###                path_len = (np.sum(np.isfinite(uzh_f[0:ib+1])==True))*rg_sp
###                path_len = (np.sum(np.isfinite(uzh_f[phi1:ib+1])==True))*rg_sp
##                path_len = rg[ib]
##                #print '2. maxmimum phidp=', pdpmax, 'Path length=', path_len
##
##                #if path of significant returns exceeds min_path
##                #if np.logical_and(path_len > min_path, pdpmax > 4):
##                if path_len > min_path:
##                    #print '3.', con1
##                    #print "step1"
##                    #plt.plot(zdr_f[0:ib+1])
##
##                    #exclude rays with any bad pixels (heavy rain (mie-scattering))
###                    ind = zdr_f[0:ib+1] > ZDRmax
##                    ind = zdr_f[phi1:ib+1] > ZDRmax
##                    #print '4.', np.sum(ind) < 1
##
##                    if np.sum(ind) < 1:
##                        #plt.plot(rhohv_f[0:ib+1])
##                        #print "step2"
##
##                        #exclude rays where 3 or more values of RhoHV are less than 0.98, i.e. not rain
##                        #ind = rhohv_f[0:ib+1] < 0.98
##
##                        ind = np.logical_and(rhohv_f > 0.0, rhohv_f < 0.98)
##                        #ind = rhohv_f < 0.98
##
##                        #print '5.', np.sum(ind) < 3
##                        #print uzh_f[0:10]
##                        #print uzh_f_all[0,0:10]
##                        #if np.sum(ind) < 3:   
##
###                        if np.sum(ind[0:ib+1]) < 3:   
##                        if np.sum(ind[phi1:ib+1]) < 3:   
##                            #print i
##                            #index of good rays (value from 0 to 4320)
##                            ray_index[file,i] = i
##                            ray_az[file,i] = rad.azimuth['data'][i]
##                            ray_el[file,i] = rad.elevation['data'][i]
##
##                            #print i
##                            uzh_f[ind] = np.nan
##                            zdr_f[ind] = np.nan
##                            #phidp_f[ind] = np.nan
##                            #uphidp_sm_f[ind] = np.nan
##			    #uphidp_sm_f.mask[ind] = np.nan
##                            #rhohv_f[ind] = np.nan
##
##                            startphi[i] = np.nanmedian(uphidp_f[phi1:phi1+10])
##
##                            phiobs[i] = pdpmax
##                            #phiobs_all[file,:] = phiobs
##
##                            #kdpest = 1e-05 * (11.74 - 4.020*zdr_f - 0.140*zdr_f**2 + 0.130*zdr_f**3)*10 ** (uzh_f/10)
##                            kdpest = 1e-05 * (11.74 - 4.020*zdr_f[phi1:] - 0.140*zdr_f[phi1:]**2 + 0.130*zdr_f[phi1:]**3)*10 ** (uzh_f[phi1:]/10)
##
##                            tmpphi = np.nancumsum(kdpest)*rg_sp*2
##                            phiest[c] = tmpphi[ib]
##                            #phiest[i] = tmpphi[ib-phi1]
##
##                            c = c + 1
##
##        #phiest is a function of ray, phiest(4320)
##        #phiest_all is a function of volume and ray, phiest_all(289,4320)
##        #delta is a function of ray, delta(4320)
##        #delta_all is a function of volume and ray, delta_all(289,4320)
##
##    	phiobs_all[file,0:Tdim] = phiobs
##    	phiest_all[file,0:Tdim] = phiest
##    	startphi_all[file,0:Tdim] = startphi
##
##    	good_rays[file] = c-1;
##	print 'file=',file,'rays=',str(c)
##    	del rad
##    	del zdr, rhohv, kdp, phidp, uzh, uphidp
##    	gc.collect()
##                    
##        #print phiobs.shape   
##        #delta = ((phiest-phiobs)/phiobs)*100
##        #print delta.shape
##        #print file
##        #delta_all[file,:] = delta
##        #print 'end'    
##        #filename = outdir + 'file%03.d_phiest_phiobs_delta' %(file)
##        #data_save=np.vstack((phiest,phiobs,delta))
##        #np.save(filename,data_save)          
##
##    #filename = outdir + 'good_rays'     
##    #np.save(filename,good_rays)
##    print np.sum(np.isfinite(phiest_all.flatten()))
##    if np.sum(np.isfinite(phiest_all.flatten())) !=0:
##        print "phiest and phiobs values exist"
##        phiest_filename = os.path.join(outdir, 'phiest_all_' + day)
##        np.save(phiest_filename,phiest_all)
##        phiobs_filename = os.path.join(outdir, 'phiobs_all_' + day)
##        np.save(phiobs_filename,phiobs_all)
##        startphi_filename = os.path.join(outdir, 'startphi_all_' + day)
##        np.save(startphi_filename,startphi_all)
##        return True
##    else:
##        return False
##

#--------------------------------------------------------------------------------------------------------------------------

def calibrate_day_norm(raddir, outdir, day, ml_zdr):

    ZDRmax = 2.0
    min_path = 15
    filelist = glob.glob(os.path.join(raddir,'*.nc'))
    filelist.sort()
    nfiles=len(filelist)
    print nfiles
    #chilbolton 
    ss=4680
    #raine 10 elevations: 0.5, 1, 1.5, 2, 3, 4.5, 6, 7.5, 10, 20 
    #ss=3600

    #create empty array for calibration offsets
    delta_all=np.zeros((nfiles,ss))*np.nan
    #create empty array for PhiEst and PhiObs
    phiest_all=np.zeros((nfiles,ss))*np.nan
    phiobs_all=np.zeros((nfiles,ss))*np.nan
    startphi_all=np.zeros((nfiles,ss))*np.nan
    #create empty array for Time
    T = np.zeros((nfiles))*np.nan
    #create empty array for number of good rays in each volume
    good_rays = np.zeros((nfiles))*np.nan
    #Create empty array for good ray index
    ray_index = np.zeros((nfiles,ss))*np.nan
    ray_az = np.zeros((nfiles,ss))*np.nan
    ray_el = np.zeros((nfiles,ss))*np.nan


    for file in range(nfiles):
    #for file in (181,):
        print file

        #Read file
        rad=pyart.io.read(filelist[file])

        #Create time array
        time = rad.metadata['start_datetime']
        hh = float(time[11:13])
        mm = float(time[14:16])
        ss = float(time[17:19])
        T[file] = hh + mm/60.0 + ss/3600.0

        #Extract dimensions
        Rdim = rad.ngates
        Edim = rad.nsweeps
        Tdim = rad.nrays
        Adim = Tdim/Edim

        #Extract data
        try:
            rg = copy.deepcopy(rad.range['data']/1000)
            rg_sp = rg[1]-rg[0]
            max_gate = rg.size
            el = copy.deepcopy(rad.elevation['data'])
            el = el[::360]
            radh = copy.deepcopy(rad.altitude['data'])
            az = copy.deepcopy(rad.azimuth['data'])
            uzh = copy.deepcopy(rad.fields['dBuZ']['data'])
            zdr = copy.deepcopy(rad.fields['ZDR']['data'])
            rhohv = copy.deepcopy(rad.fields['RhoHV']['data'])
            kdp = copy.deepcopy(rad.fields['KDP']['data'])

            phidp = copy.deepcopy(rad.fields['PhiDP']['data'])
            ind = phidp > 180
            phidp[ind] = phidp[ind] - 360
            ind = phidp < -180
            phidp[ind] = phidp[ind] + 360

	    uphidp = copy.deepcopy(rad.fields['uPhiDP']['data'])
            #Set invalid values (-9e33) to nans
            ind = uphidp.mask==True
            uphidp[ind]=np.nan

        except:
            print "Couldn't load all variables"    
            continue

        #Calculate height of every range gate
        beam_height = np.empty((Tdim,Rdim))
        for j in np.arange(0,Edim):
            for i in np.arange(0,Adim):
                beam_height[(360*j)+i,:] = radh/1000 + np.sin(np.deg2rad(el[j]))*rg + np.sqrt(rg**2 + (6371*4/3.0)**2) - (6371*4/3.0);

        mlh, zdr_bias = extract_ml_zdr(time, ml_zdr)

        zind = beam_height > mlh   
        uzh[zind==True] = np.nan
        #zind = beam_height < 0.5    
        #uzh[zind==True] = np.nan

        zdr[zind==True] = np.nan
        phidp[zind==True] = np.nan
        uphidp[zind==True] = np.nan
        kdp[zind==True] = np.nan
        rhohv[zind==True] = np.nan

#       Remove first 2km of data
        n=13
        uzh = uzh[:,n:]
        zdr = zdr[:,n:]
        phidp = phidp[:,n:]
        uphidp = uphidp[:,n:]
        kdp = kdp[:,n:] 
        rhohv = rhohv[:,n:]
        rg = rg[n:] - rg[n]

        #Create empty arrays for observed and calculated PhiDP
        phiobs = np.zeros([Tdim])*np.nan
        phiest = np.zeros([Tdim])*np.nan        
        startphi = np.zeros([Tdim])*np.nan        

#        c=0

# Exclusions is a list of tuples (), where each tuple is a pair of tuples.
# The first tuple of each pair is the start and stop elevation of the segment to exclude
# and the second tuple contains the start and stop azimuth of the segment to exclude.
# This "one-liner" builds a generator from the list of tuples so each tuple defines a binary array which is True
# where the segment occurs and false elsewhere. All conditions must be met, so between start and stop in both
# azimuth and elevation. These are then combined to a single array using np.any to create a single exclude binary array which is True where
# any of the segments are found and False in non-excluded places

    	#raine exclusions = [((0,90.1),(20,160)),((0,90.1),(201,207)),((0,0.51),(185,201.5))]
    	exclusions = [((0,90.1),(49,90)),((0,90.1),(130,190)),((0,1.01),(0,360))]
        exclude_radials = np.any([np.all([rad.elevation['data']>=ele[0],
                                  rad.elevation['data']<ele[1],
                                  rad.azimuth['data']>=azi[0],
                                  rad.azimuth['data']<azi[1]],axis=0) for ele, azi in exclusions],axis=0)
	az_index = np.where(~exclude_radials)[0]

        for i in az_index:


            #Extract ray
            phidp_f1 = phidp[i,:]
            uphidp_f = uphidp[i,:]
            #uphidp_sm_f = uphidp_sm[i,:]
            uzh_f = uzh[i,:]
            zdr_f = zdr[i,:] - zdr_bias
            rhohv_f = rhohv[i,:]
#
#
#
            phidp_f = phidp_f1 - phidp_f1[0]
#
#
#
#
#
            #Check for all-nan array, go to next iteration of loop if so
            if np.sum(np.isfinite(phidp_f)==True)==0:
                continue
            
            #Find minimum value of PhiDP
            phi1_valid = (np.nonzero(np.isfinite(phidp_f)))[0]
            if phi1_valid.size != 0:
                phi1 = phi1_valid[0]
            else:
                continue
#            #Find indices where PhiDP is between 4 and 6 degs    
            ind = np.where(np.logical_and(phidp_f > 4, phidp_f < 6))[0]

            #If values exist, 
            if ind.size != 0:
                #Find the index of the maximum value of PhiDP between 4 and 6
                ib = np.where(phidp_f==max(phidp_f[ind]))[0][0]
                #print '1. index and value of maximum phidp_f between 4&6=', ib, phidp_f[ib]

                pdpmax = phidp_f[ib]
#                path_len = (np.sum(np.isfinite(uzh_f[0:ib+1])==True))*rg_sp
#                path_len = (np.sum(np.isfinite(uzh_f[phi1:ib+1])==True))*rg_sp
                path_len = rg[ib]
                #print '2. maxmimum phidp=', pdpmax, 'Path length=', path_len

                #if path of significant returns exceeds min_path
                #if np.logical_and(path_len > min_path, pdpmax > 4):
                if path_len > min_path:
                    #print '3.', con1
                    #print "step1"
                    #plt.plot(zdr_f[0:ib+1])

                    #exclude rays with any bad pixels (heavy rain (mie-scattering))
#                    ind = zdr_f[0:ib+1] > ZDRmax
                    ind = zdr_f[phi1:ib+1] > ZDRmax
                    #print '4.', np.sum(ind) < 1

                    if np.sum(ind) < 1:
                        #plt.plot(rhohv_f[0:ib+1])
                        #print "step2"

                        #exclude rays where 3 or more values of RhoHV are less than 0.98, i.e. not rain
                        #ind = rhohv_f[0:ib+1] < 0.98
                        ind = np.logical_and(rhohv_f > 0.0, rhohv_f < 0.98)
                        #print '5.', np.sum(ind) < 3
                        #print uzh_f[0:10]
                        #print uzh_f_all[0,0:10]
                        #if np.sum(ind) < 3:   

#                        if np.sum(ind[0:ib+1]) < 3:   
                        if np.sum(ind[phi1:ib+1]) < 3:   
                            #print i
                            #index of good rays (value from 0 to 4320)
                            ray_index[file,i] = i
                            ray_az[file,i] = rad.azimuth['data'][i]
                            ray_el[file,i] = rad.elevation['data'][i]

                            #print i
                            uzh_f[ind] = np.nan
                            zdr_f[ind] = np.nan
                            #phidp_f[ind] = np.nan
                            #uphidp_sm_f[ind] = np.nan
			    #uphidp_sm_f.mask[ind] = np.nan
                            #rhohv_f[ind] = np.nan

                            startphi[i] = np.nanmedian(uphidp_f[phi1:phi1+10])

                            phiobs[i] = pdpmax
                            #phiobs_all[file,:] = phiobs

                            #kdpest = 1e-05 * (11.74 - 4.020*zdr_f - 0.140*zdr_f**2 + 0.130*zdr_f**3)*10 ** (uzh_f/10)
                            kdpest = 1e-05 * (11.74 - 4.020*zdr_f[phi1:] - 0.140*zdr_f[phi1:]**2 + 0.130*zdr_f[phi1:]**3)*10 ** (uzh_f[phi1:]/10)

                            tmpphi = np.nancumsum(kdpest)*rg_sp*2

                            phiest[i] = tmpphi[ib]
                            #phiest[i] = tmpphi[ib-phi1]

        #phiest is a function of ray, phiest(4320)
        #phiest_all is a function of volume and ray, phiest_all(289,4320)
        #delta is a function of ray, delta(4320)
        #delta_all is a function of volume and ray, delta_all(289,4320)

    	phiobs_all[file,0:Tdim] = phiobs
    	phiest_all[file,0:Tdim] = phiest
    	startphi_all[file,0:Tdim] = startphi

    	good_rays = np.sum(np.isfinite(phiest))
    	print 'file=',file,'rays=',str(good_rays)
    	del rad
    	del zdr, rhohv, kdp, phidp, uzh, uphidp
    	gc.collect()
                    
        #print phiobs.shape   
        #delta = ((phiest-phiobs)/phiobs)*100
        #print delta.shape
        #print file
        #delta_all[file,:] = delta
        #print 'end'    
        #filename = outdir + 'file%03.d_phiest_phiobs_delta' %(file)
        #data_save=np.vstack((phiest,phiobs,delta))
        #np.save(filename,data_save)          

    #filename = outdir + 'good_rays'     
    #np.save(filename,good_rays)
    print "total rays = ", np.sum(np.isfinite(phiest_all.flatten()))
    if np.sum(np.isfinite(phiest_all.flatten())) !=0:
        print "phiest and phiobs values exist"
        phiest_filename = os.path.join(outdir, 'phiest_all_' + day)
        np.save(phiest_filename,phiest_all)
        phiobs_filename = os.path.join(outdir, 'phiobs_all_' + day)
        np.save(phiobs_filename,phiobs_all)
        startphi_filename = os.path.join(outdir, 'startphi_all_' + day)
        np.save(startphi_filename,startphi_all)
        return True
    else:
        return False

#--------------------------------------------------------------------------------------------------------------------------
def calibrate_day_att(raddir, outdir, day, ml_zdr):

    ZDRmax = 2.0
    min_path = 15
    filelist = glob.glob(os.path.join(raddir,'*.nc'))
    filelist.sort()
    nfiles=len(filelist)
    print nfiles

    #raine 10 elevations: 0.5, 1, 1.5, 2, 3, 4.5, 6, 7.5, 10, 20 
    #ss=3600
    ss=4680

    #create empty array for calibration offsets
    delta_all=np.zeros((nfiles,ss))*np.nan
    #create empty array for PhiEst and PhiObs
    phiest_all=np.zeros((nfiles,ss))*np.nan
    phiobs_all=np.zeros((nfiles,ss))*np.nan
    startphi_all=np.zeros((nfiles,ss))*np.nan
    #create empty array for Time
    T = np.zeros((nfiles))*np.nan
    #create empty array for number of good rays in each volume
    good_rays = np.zeros((nfiles))*np.nan
    #Create empty array for good ray index
    ray_index = np.zeros((nfiles,ss))*np.nan
    ray_az = np.zeros((nfiles,ss))*np.nan
    ray_el = np.zeros((nfiles,ss))*np.nan


    for file in range(nfiles):
    #for file in (30,):
        print file

        #Read file
        rad=pyart.io.read(filelist[file])

        #Create time array
        time = rad.metadata['start_datetime']
        hh = float(time[11:13])
        mm = float(time[14:16])
        ss = float(time[17:19])
        T[file] = hh + mm/60.0 + ss/3600.0

        #Extract dimensions
        Rdim = rad.ngates
        Edim = rad.nsweeps
        Tdim = rad.nrays
        Adim = Tdim/Edim

        #Extract data
        try:
            rg = copy.deepcopy(rad.range['data']/1000)
            rg_sp = rg[1]-rg[0]
            max_gate = rg.size
            el = copy.deepcopy(rad.elevation['data'])
            el = el[::360]
            radh = copy.deepcopy(rad.altitude['data'])
            az = copy.deepcopy(rad.azimuth['data'])
            uzh = copy.deepcopy(rad.fields['dBuZ']['data'])
            zdr = copy.deepcopy(rad.fields['ZDR']['data'])
            rhohv = copy.deepcopy(rad.fields['RhoHV']['data'])
            kdp = copy.deepcopy(rad.fields['KDP']['data'])

            phidp = copy.deepcopy(rad.fields['PhiDP']['data'])
            ind = phidp > 180
            phidp[ind] = phidp[ind] - 360
            ind = phidp < -180
            phidp[ind] = phidp[ind] + 360

	    uphidp = copy.deepcopy(rad.fields['uPhiDP']['data'])
            #Set invalid values (-9e33) to nans
            ind = uphidp.mask==True
            uphidp[ind]=np.nan

        except:
            print "Couldn't load all variables"    
            continue

        #Calculate height of every range gate
        beam_height = np.empty((Tdim,Rdim))
        for j in np.arange(0,Edim):
            for i in np.arange(0,Adim):
                beam_height[(360*j)+i,:] = radh/1000 + np.sin(np.deg2rad(el[j]))*rg + np.sqrt(rg**2 + (6371*4/3.0)**2) - (6371*4/3.0);

        mlh, zdr_bias = extract_ml_zdr(time, ml_zdr)

        zind = beam_height > mlh   
        uzh[zind==True] = np.nan
        #zind = beam_height < 0.5    
        #uzh[zind==True] = np.nan

        zdr[zind==True] = np.nan
        phidp[zind==True] = np.nan
        uphidp[zind==True] = np.nan
        kdp[zind==True] = np.nan
        rhohv[zind==True] = np.nan

        #Get rid of first 2km
        n=13
        uzh = uzh[:,n:]
        zdr = zdr[:,n:]
        phidp = phidp[:,n:]
        uphidp = uphidp[:,n:]
        kdp = kdp[:,n:] 
        rhohv = rhohv[:,n:]
        rg = rg[n:] - rg[n]

        #Create empty arrays for observed and calculated PhiDP
        phiobs = np.zeros([Tdim])*np.nan
        phiest = np.zeros([Tdim])*np.nan        
        startphi = np.zeros([Tdim])*np.nan        

#        c=0

# Exclusions is a list of tuples (), where each tuple is a pair of tuples.
# The first tuple of each pair is the start and stop elevation of the segment to exclude
# and the second tuple contains the start and stop azimuth of the segment to exclude.
# This "one-liner" builds a generator from the list of tuples so each tuple defines a binary array which is True
# where the segment occurs and false elsewhere. All conditions must be met, so between start and stop in both
# azimuth and elevation. These are then combined to a single array using np.any to create a single exclude binary array which is True where
# any of the segments are found and False in non-excluded places

    	# raine exclusions = [((0,90.1),(20,160)),((0,90.1),(201,207)),((0,0.51),(185,201.5))]
    	#080620_att exclusions = [((0,90.1),(49,90)),((0,90.1),(130,190)),((0,1.01),(0,360))]
    	exclusions = [((0,90.1),(49,90)),((0,90.1),(130,190)),((0,0.6),(0,360)),((0.6,1.01),(190,211)),((0.6,1.01),(324,335))]
        exclude_radials = np.any([np.all([rad.elevation['data']>=ele[0],
                                  rad.elevation['data']<ele[1],
                                  rad.azimuth['data']>=azi[0],
                                  rad.azimuth['data']<azi[1]],axis=0) for ele, azi in exclusions],axis=0)

	az_index = np.where(~exclude_radials)[0]

        for i in az_index:
        #for i in (778,):

            #Extract ray
            phidp_f = phidp[i,:]
            uphidp_f = uphidp[i,:]
            #uphidp_sm_f = uphidp_sm[i,:]
            uzh_f = uzh[i,:]
            zdr_f = zdr[i,:] - zdr_bias
            rhohv_f = rhohv[i,:]

            #attenuation correction
            #phidp_att = copy.deepcopy(phidp_f)
            phidp_att = phidp_f - phidp_f[0]

            PA = np.maximum.accumulate(phidp_att) 
            uzh_att = uzh_f + 0.28*PA
            zdr_att = zdr_f + 0.04*PA

            #Check for all-nan array, go to next iteration of loop if so
            if np.sum(np.isfinite(phidp_att)==True)==0:
                continue

            #Find minimum value of PhiDP
            phi1_valid = np.where(np.isfinite(phidp_att))[0]
            if phi1_valid.size != 0:
                phi1 = phi1_valid[0]
            else:
                continue
#            #Find indices where PhiDP is between 4 and 6 degs    
            ind = np.where(np.logical_and(phidp_att > 4, phidp_att < 6))[0]

            #If values exist, 
            if ind.size != 0:
                #Find the index of the maximum value of PhiDP between 4 and 6
                ib = np.where(phidp_att==max(phidp_att[ind]))[0][0]
                #print '1. index and value of maximum phidp_f between 4&6=', ib, phidp_f[ib]

                pdpmax = phidp_att[ib]
#                path_len = (np.sum(np.isfinite(uzh_f[0:ib+1])==True))*rg_sp
                #path_len = (np.sum(np.isfinite(uzh_f[phi1:ib+1])==True))*rg_sp
                path_len = rg[ib]
                #print '2. maxmimum phidp=', pdpmax, 'Path length=', path_len

                #if path of significant returns exceeds min_path
                #if np.logical_and(path_len > min_path, pdpmax > 4):
                if path_len > min_path:
                    #print '3.', con1
                    #print "step1"
                    #plt.plot(zdr_f[0:ib+1])

                    #exclude rays with any bad pixels (heavy rain (mie-scattering))
#                    ind = zdr_f[0:ib+1] > ZDRmax
                    ind = zdr_att[phi1:ib+1] > ZDRmax
                    #print '4.', np.sum(ind) < 1

                    if np.sum(ind) < 1:
                        #plt.plot(rhohv_f[0:ib+1])
                        #print "step2"

                        #exclude rays where 3 or more values of RhoHV are less than 0.98, i.e. not rain
                        #ind = rhohv_f[0:ib+1] < 0.98
                        ind = np.logical_and(rhohv_f > 0.0, rhohv_f < 0.98)
                        #print '5.', np.sum(ind) < 3
                        #print uzh_f[0:10]
                        #print uzh_f_all[0,0:10]
                        #if np.sum(ind) < 3:   

#                        if np.sum(ind[0:ib+1]) < 3:   
                        if np.sum(ind[phi1:ib+1]) < 3:   
                            #print i
                            #index of good rays (value from 0 to 4320)
                            ray_index[file,i] = i
                            ray_az[file,i] = rad.azimuth['data'][i]
                            ray_el[file,i] = rad.elevation['data'][i]

                            #print i
                            uzh_att[ind] = np.nan
                            zdr_att[ind] = np.nan
                            #phidp_f[ind] = np.nan
                            #uphidp_sm_f[ind] = np.nan
			    #uphidp_sm_f.mask[ind] = np.nan
                            #rhohv_f[ind] = np.nan

                            startphi[i] = np.nanmedian(uphidp_f[phi1:phi1+10])

                            phiobs[i] = pdpmax
                            #phiobs_all[file,:] = phiobs

                            #kdpest = 1e-05 * (11.74 - 4.020*zdr_f - 0.140*zdr_f**2 + 0.130*zdr_f**3)*10 ** (uzh_f/10)
                            kdpest = 1e-05 * (11.74 - 4.020*zdr_att[phi1:] - 0.140*zdr_att[phi1:]**2 + 0.130*zdr_att[phi1:]**3)*10 ** (uzh_att[phi1:]/10)

                            tmpphi = np.nancumsum(kdpest)*rg_sp*2
                            #phiest[c] = tmpphi[ib]
                            phiest[i] = tmpphi[ib]
#                           print 'phiest = ', phiest[i] 

        #phiest is a function of ray, phiest(4320)
        #phiest_all is a function of volume and ray, phiest_all(289,4320)
        #delta is a function of ray, delta(4320)
        #delta_all is a function of volume and ray, delta_all(289,4320)

    	phiobs_all[file,0:Tdim] = phiobs
    	phiest_all[file,0:Tdim] = phiest
    	startphi_all[file,0:Tdim] = startphi

   	good_rays = np.sum(np.isfinite(phiest_all));
	print 'file=',file,'rays=',str(good_rays)
    	del rad
    	del zdr, rhohv, kdp, phidp, uzh, uphidp
    	gc.collect()
                    
        #print phiobs.shape   
        #delta = ((phiest-phiobs)/phiobs)*100
        #print delta.shape
        #print file
        #delta_all[file,:] = delta
        #print 'end'    
        #filename = outdir + 'file%03.d_phiest_phiobs_delta' %(file)
        #data_save=np.vstack((phiest,phiobs,delta))
        #np.save(filename,data_save)          

    #filename = outdir + 'good_rays'     
    #np.save(filename,good_rays)
    print "total rays = ", np.sum(np.isfinite(phiest_all.flatten()))
    if np.sum(np.isfinite(phiest_all.flatten())) !=0:
        print "phiest and phiobs values exist"
        phiest_filename = os.path.join(outdir, 'phiest_all_att_' + day)
        np.save(phiest_filename,phiest_all)
        phiobs_filename = os.path.join(outdir, 'phiobs_all_att_' + day)
        np.save(phiobs_filename,phiobs_all)
        startphi_filename = os.path.join(outdir, 'startphi_all_' + day)
        np.save(startphi_filename,startphi_all)
        return True
    else:
        return False



#--------------------------------------------------------------------------------------------------------------------------
def horiz_zdr(datadir, date, outdir, mlh, zcorr):
    
    filelist = glob.glob(datadir + date + '/*.nc')
    filelist.sort()
    nfiles=len(filelist)
    
#   T = np.zeros((nfiles))*np.nan
#   num18 = np.zeros(nfiles)*np.nan
#   stdZDR18  = np.zeros(nfiles)*np.nan
    medZDR18  = np.zeros(nfiles)*np.nan
    T_arr = []

    
    for file in range(0,nfiles):
        #print filelist[file]
        print file
        rad=pyart.io.read(filelist[file])

        #Create time array
        time = rad.metadata['start_datetime']
        hh = float(time[11:13])
        mm = float(time[14:16])
        ss = float(time[17:19])
#        T[file] = hh + mm/60.0 + ss/3600.0

	T_arr.append(time)

        #Extract dimensions
        Rdim = rad.ngates
        Edim = rad.nsweeps
        Tdim = rad.nrays
        Adim = Tdim/Edim
        
   	#raine exclusions = [((0,90.1),(20,160)),((0,90.1),(201,207)),((0,0.51),(185,201.5))]
    	exclusions = [((0,90.1),(49,90)),((0,90.1),(130,190)),((0,1.01),(0,360))]
        exclude_radials = np.any([np.all([rad.elevation['data']>=ele[0],
                                  rad.elevation['data']<ele[1],
                                  rad.azimuth['data']>=azi[0],
                                  rad.azimuth['data']<azi[1]],axis=0) for ele, azi in exclusions],axis=0)
	az_index = np.where(~exclude_radials)[0]

        #Extract data
        try:
            rg = copy.deepcopy(rad.range['data']/1000)
            rg_sp = rg[1]-rg[0]
            max_gate = rg.size
            el = copy.deepcopy(rad.elevation['data'])
            el = el[::360]
            radh = copy.deepcopy(rad.altitude['data'])
            az = copy.deepcopy(rad.azimuth['data'])

            uzh = copy.deepcopy(rad.fields['dBuZ']['data'][az_index,:])#[rad.sweep_start_ray_index['data'][0]]
            uzh = uzh + zcorr
            zdr = copy.deepcopy(rad.fields['ZDR']['data'][az_index,:])
            rhohv = copy.deepcopy(rad.fields['RhoHV']['data'][az_index,:])
            phidp = copy.deepcopy(rad.fields['PhiDP']['data'][az_index,:])
            ind = phidp > 180
            phidp[ind] = phidp[ind] - 360
            ind = phidp < -180
            phidp[ind] = phidp[ind] + 360
        except:
            print "Couldn't load all variables"    
            continue

        beam_height = np.empty((Tdim,Rdim))
        for j in np.arange(0,Edim):
            for i in np.arange(0,Adim):
                beam_height[(Adim*j)+i,:] = radh/1000 + np.sin(np.deg2rad(el[j]))*rg + np.sqrt(rg**2 + (6371*4/3.0)**2) - (6371*4/3.0);

        beam_height = beam_height[az_index,:]

        zind = beam_height > mlh   
        uzh[zind==True] = np.nan    
        zdr[zind==True] = np.nan
        phidp[zind==True] = np.nan
        rhohv[zind==True] = np.nan

        #Set first three range gates to NaN
        uzh[:,0:3] = np.nan
        zdr[:,0:3] = np.nan
        phidp[:,0:3] = np.nan
        rhohv[:,0:3] = np.nan

        ind=np.all([rhohv>0.99, phidp>0, phidp<6, uzh>15, uzh<=18],axis=0)
        if ind.sum() >0:
#           num18[file] = np.sum(ind==True)
#           stdZDR18[file] = np.nanstd(zdr[ind==True])
            medZDR18[file] = np.nanmedian(zdr[ind==True])

	del rad
        del zdr, rhohv, uzh, phidp
        gc.collect()
    
    return T_arr, medZDR18

